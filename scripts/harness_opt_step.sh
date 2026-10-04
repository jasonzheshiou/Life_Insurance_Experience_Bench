#!/usr/bin/env bash
# ============================================================================
# harness_opt_step.sh — ONE optimization-split scenario per invocation, with
# the harness ON. This is the improvement loop from the experiment plan:
#
#   "run each scenario once, compare to truth, make changes, then next"
#
# Each invocation runs exactly ONE not-yet-run optimization scenario (1 run,
# canonical samplers, --harness full), scores it against truth, appends the
# truth-diff to the loop log, and STOPS. Between invocations the harness
# (scripts/stats_pack.py verdicts/thresholds, HARNESS_RULES in
# run_zero_shot.py) is reviewed and edited. Re-run the SAME command to move
# to the next scenario — it always picks the first scenario without a valid
# run in the current pass, so a crash mid-run resumes automatically
# (--skip-existing re-spends only missing/failed runs).
#
#   PASS=1  bash scripts/harness_opt_step.sh     # pass 1, next scenario
#   bash scripts/harness_opt_step.sh sc-14cdd9   # force a specific scenario
#   bash scripts/harness_opt_step.sh --status    # progress only, no API call
#
# Corpus: results/harness_opt_p$PASS/ (separate from xam_v4 / xam_v5).
# The model NEVER sees truth; this script only prints truth for the
# experimenter log (results/logs/harness_opt_loop.md).
# Gate to freeze the harness: optimization strict >= ~80%, FP/run <= 1.0,
# zero CLEAN regressions, hard cap 3 passes -> then run heldout final.
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

PASS="${PASS:-1}"
OUT="harness_opt_p${PASS}"
RUNS="${RUNS:-1}"
MODEL="${MODEL:-Qwen3.8-27B-Q8_0}"
BASE_URL="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
ZERO="results/$OUT/zero_shot"
LOGF="results/logs/harness_opt_step.log"
LOOP="results/logs/harness_opt_loop.md"
STATUS="results/logs/harness_opt_status.txt"
LOCKF="results/logs/harness_opt_step.lock"
mkdir -p results/logs "$ZERO"

# --- helpers ---------------------------------------------------------------
valid_run() {  # $1 sid -> 0 if a good run exists
  python3 - "$ZERO" "$1" "$RUNS" <<'PY'
import json, sys
from pathlib import Path
zero, sid, runs = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
k = 0
for n in range(1, runs + 1):
    f = zero / f"{sid}_run{n:02d}.json"
    try:
        r = json.loads(f.read_text())
    except Exception:
        continue
    if r.get("content") and not r.get("error"):
        k += 1
sys.exit(0 if k >= runs else 1)
PY
}

opt_sids() { ls data/eval/optimization | grep -E '^sc-[0-9a-f]{6}$' | sort; }

write_status() {  # $1 state  [$2 current-line]
  local done=0 total; total=$(opt_sids | wc -l)
  for sid in $(opt_sids); do valid_run "$sid" && done=$((done + 1)); done
  {
    echo "==== harness optimization loop (pass $PASS) — status ===="
    echo "state:    $1"
    echo "updated:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "corpus:   results/$OUT  (model=$MODEL, harness=h1, runs/scenario=$RUNS)"
    echo "SCENARIOS FINISHED: $done/$total"
    [ -n "${2:-}" ] && echo "last:     $2"
    echo "loop log: results/logs/harness_opt_loop.md"
    echo "next:     bash scripts/harness_opt_step.sh"
  } > "$STATUS"
  cat "$STATUS"
}

if [ "${1:-}" = "--status" ]; then write_status IDLE; exit 0; fi

exec 9>"$LOCKF"
flock -n 9 || { echo "another harness_opt_step is running — not starting a second"; exit 1; }

# --- pick the scenario ------------------------------------------------------
SID="${1:-}"
if [ -z "$SID" ]; then
  for sid in $(opt_sids); do
    valid_run "$sid" || { SID="$sid"; break; }
  done
fi
if [ -z "$SID" ]; then
  write_status PASS_COMPLETE "all optimization scenarios done for pass $PASS — score & apply the freeze gate"
  python3 scripts/score_xam.py "$ZERO" --json-out "results/$OUT/scores.json" \
    > "results/$OUT/scoreboard.txt" 2>&1 || true
  echo; echo "PASS COMPLETE — run the freeze gate, then the heldout final test."; exit 0
fi

write_status RUNNING "now: $SID"
{ echo; echo "## $(date -u +%Y-%m-%dT%H:%M:%SZ)  $SID (pass $PASS)"; } >> "$LOOP"

# --- run -------------------------------------------------------------------
# ${RUNNER:-...} allows offline dry-testing (RUNNER=true); leave unset in prod.
${RUNNER:-python3 scripts/run_zero_shot.py} --scenarios "$SID" --split optimization \
  --detail full --termination-mean pooled \
  --base-url "$BASE_URL" --model "$MODEL" \
  --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 \
  --timeout 3600 --runs "$RUNS" --stream \
  --wait-for-endpoint 1800 --max-consecutive-failures 5 \
  --skip-existing --harness full --tool-calls "${TOOL_CALLS:-4}" \
  ${DRY:+--dry-run} --out "$OUT" >> "$LOGF" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  write_status STOPPED "runner rc=$rc on $SID (see $LOGF) — fix and re-run SAME command"
  exit 1
fi

# --- score + truth diff (experimenter side) --------------------------------
python3 scripts/score_xam.py "$ZERO" --json-out "results/$OUT/scores.json" \
  > "results/$OUT/scoreboard.txt" 2>&1 || true
{
  echo '```'
  python3 scripts/harness_diff.py "$SID" --out "$OUT" 2>&1
  grep "$SID" "results/$OUT/scoreboard.txt" 2>/dev/null | head -1 || true
  echo '```'
} >> "$LOOP"

write_status STEP_DONE "$SID done — review results/logs/harness_opt_loop.md, edit the harness, re-run this command"
echo
echo "STEP DONE: $SID  (diff appended to $LOOP)"
echo "Review the truth-diff, adjust the harness, then:  bash scripts/harness_opt_step.sh"
