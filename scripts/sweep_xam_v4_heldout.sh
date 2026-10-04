#!/usr/bin/env bash
# Heldout sweep (batches 5+): processes the NEXT N scenarios that still need
# work (default 6), strictly sequentially (1-slot server), then exits.
# Run the SAME command again for the following batch; pass a bigger N (or
# "all") to process more in one go.
#
# "Needs work" = any of run01..run03 missing, unreadable, carrying an error,
# or with empty content — exactly the runner's --skip-existing semantics, so
# finished runs are never re-spent. Order = id_map.csv order.
#
# Usage:
#   bash scripts/sweep_xam_v4_heldout.sh           # next 6
#   bash scripts/sweep_xam_v4_heldout.sh all       # every remaining scenario
#   bash scripts/sweep_xam_v4_heldout.sh --list    # preview, no API calls
set -uo pipefail
cd "$(dirname "$0")/.."

LOCK="results/logs/sweep_xam_v4_heldout.lock"
STATUS="results/logs/sweep_xam_v4_heldout.status"
mkdir -p results/logs
exec 9>"$LOCK"
flock -n 9 || { echo "another heldout sweep is already running — refusing to double-launch"; exit 1; }

ARG="${1:-6}"
[ "$ARG" = "all" ] && ARG=99

list_remaining () {   # sids (id_map order) that still need at least one run
  python3 - <<'EOF'
import csv, json, os
base = "results/xam_v4/zero_shot"
with open("data/truth/id_map.csv", newline="") as f:
    for r in csv.DictReader(f):
        sid = r["eval_id"]
        need = False
        for n in (1, 2, 3):
            p = os.path.join(base, f"{sid}_run0{n}.json")
            try:
                d = json.load(open(p))
                if d.get("error") or not (d.get("content") or "").strip():
                    need = True
            except Exception:
                need = True
            if need:
                break
        if need:
            print(sid)
EOF
}

mapfile -t ALL < <(list_remaining)
if [ "${#ALL[@]}" -eq 0 ]; then
  echo "nothing left to run — all scenarios complete"; exit 0
fi

if [ "${1:-6}" = "--list" ]; then
  echo "remaining scenarios (${#ALL[@]}):"; printf '  %s\n' "${ALL[@]}"; exit 0
fi

N=$(( ARG < ${#ALL[@]} ? ARG : ${#ALL[@]} ))
BATCH=( "${ALL[@]:0:N}" )
echo "================ batch start: $(date -u +%FT%TZ)  (${N}/${#ALL[@]} remaining): ${BATCH[*]} ================" | tee -a "$STATUS"

run_sid () {   # $1 = scenario id ; canonical settings + resume-safe skip-existing
  local SID="$1" SPLIT
  SPLIT=$(python3 -c "
import csv
with open('data/truth/id_map.csv', newline='') as f:
    for r in csv.DictReader(f):
        if r['eval_id']=='$SID':
            print(r['split']); break
")
  [ -n "$SPLIT" ] || { echo "unknown scenario id: $SID"; return 2; }
  python3 scripts/run_zero_shot.py \
    --scenarios "$SID" --split "$SPLIT" \
    --detail full --termination-mean pooled --show-truth \
    --base-url http://192.168.1.59:8080/v1 --model Qwen3.8-Flash-Next \
    --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence-penalty 0.0 --repetition-penalty 1.0 \
    --timeout 3600 --runs 3 --stream \
    --wait-for-endpoint 1800 --max-consecutive-failures 5 \
    --skip-existing \
    --out xam_v4
}

score_and_report () {
  python3 scripts/score_xam.py results/xam_v4/zero_shot | tail -3
  python3 scripts/report_xam.py results/xam_v4/zero_shot >/dev/null
}

for SID in "${BATCH[@]}"; do
  echo
  echo "================ $SID  $(date -u +%FT%TZ) ================"
  if run_sid "$SID"; then
    RUNST=ok
  else
    RUNST="run_failed_rc$?"
    echo "!! $SID run step failed ($RUNST) — scoring what exists and continuing"
  fi
  score_and_report
  echo "$SID : $RUNST  $(date -u +%FT%TZ)" >> "$STATUS"
done

echo
echo "================ final workspace leakcheck ================"
python3 scripts/leakcheck.py || echo "!! leakcheck failed"
LEFT=$(list_remaining | wc -l)
echo "================ batch complete: $(date -u +%FT%TZ)  remaining: $LEFT ================" | tee -a "$STATUS"
