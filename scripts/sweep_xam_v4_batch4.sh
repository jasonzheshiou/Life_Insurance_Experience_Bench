#!/usr/bin/env bash
# Batch 4: finish optimization (sc-f69eea, #23) + first 5 heldout scenarios,
# strictly sequentially (1-slot server).
#
# Resume-safe via the runner's --skip-existing: runs that already have content
# and no error are NOT re-spent. Re-run the SAME command after interruption.
# Single-instance lock: a second concurrent launch exits immediately instead
# of racing the first one on the same run files (batch-3 race guard).
set -uo pipefail
cd "$(dirname "$0")/.."

LOCK="results/logs/sweep_xam_v4_batch4.lock"
mkdir -p results/logs
exec 9>"$LOCK"
flock -n 9 || { echo "sweep_xam_v4_batch4 is already running — refusing to double-launch"; exit 1; }

STATUS="results/logs/sweep_xam_v4_batch4.status"
echo "sweep start: $(date -u +%FT%TZ)  sids: sc-f69eea sc-0ce4d6 sc-11135c sc-12be68 sc-21b383 sc-3411b2" | tee "$STATUS"

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

SIDS="sc-f69eea sc-0ce4d6 sc-11135c sc-12be68 sc-21b383 sc-3411b2"

for SID in $SIDS; do
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
echo "sweep complete: $(date -u +%FT%TZ)" | tee -a "$STATUS"
