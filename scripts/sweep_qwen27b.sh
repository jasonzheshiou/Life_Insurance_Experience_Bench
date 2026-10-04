#!/usr/bin/env bash
# ============================================================================
# Qwen3.8-27b full cross-examination — ALL 47 scenarios × 3 runs, into its own
# corpus results/xam_v5/. The finished xam_v4 corpus is NEVER touched:
# run_zero_shot.py only ever writes inside results/<--out>/, and xam_v5 does
# not exist yet. (Prompt note: run_zero_shot.py v0.4.3 ships the revised v2
# system prompt — the former "patch P2" text — as its only prompt.)
#
# RESUME DESIGN — this command is safe to re-run as often as you like, after a
# crash, a Ctrl-C, or a server outage:
#   * the runner's --skip-existing reuses every run file that already holds a
#     non-empty, error-free answer (API calls are spent only on missing/failed
#     runs);
#   * this wrapper additionally skips scenarios that already have all 3 valid
#     runs, so a resume pass is near-instant until it reaches real work;
#   * a flock guard kills a second concurrent copy (single-slot server).
#
# STATUS — a human-readable txt is rewritten after every scenario and always
# shows "RUNS FINISHED: n/141":
#       results/logs/qwen27b_status.txt
#   Watch it live in another terminal:
#       tail -f results/logs/qwen27b_status.txt
#
# Usage:
#   bash scripts/sweep_qwen27b.sh              # run or resume (do this)
#   python3 scripts/sweep_status.py --zero results/xam_v5/zero_shot \
#       --model Qwen3.8-27b --out xam_v5       # print status anytime (no write)
#
# Before starting, load Qwen3.8-27b in LM Studio at 192.168.1.59:8080 — the
# runner treats "model not found" as a wait-and-retry condition, so launching
# early is safe (it polls for up to 30 min per call window), but loading it
# first saves idle time.
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

MODEL="${MODEL:-Qwen3.8-27B-Q8_0}"
OUT="${OUT:-xam_v5}"
RUNS="${RUNS:-3}"
BASE_URL="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
ZERO_DIR="results/$OUT/zero_shot"
LOG="results/logs/sweep_qwen27b.log"
STATUS="results/logs/qwen27b_status.txt"
LOCK="results/logs/sweep_qwen27b.lock"

mkdir -p results/logs "$ZERO_DIR"
mkdir -p "results/$OUT/reports"

# ---- single-instance guard -------------------------------------------------
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "another sweep_qwen27b instance holds $LOCK — exiting (no double-launch)" | tee -a "$LOG"
  exit 1
fi

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# status <STATE> [current-line] — regenerate the tracking txt (never hides errors)
status() {
  python3 scripts/sweep_status.py --zero "$ZERO_DIR" --runs "$RUNS" \
      --model "$MODEL" --out "$OUT" --state "$1" ${2:+--current "$2"} \
      --status-file "$STATUS" >/dev/null 2>&1 || true
}

trap 'status ABORTED "interrupted by user at $(ts)"' INT TERM

echo "==== sweep_qwen27b started $(ts) model=$MODEL out=$OUT runs=$RUNS ====" >>"$LOG"
status RUNNING "starting sweep"

for split in optimization heldout; do
  for sid in $(ls "data/eval/$split" | grep -E '^sc-[0-9a-f]{6}$' | sort); do
    # Skip scenarios that already have the full complement of valid runs.
    banked=$(python3 scripts/sweep_status.py --zero "$ZERO_DIR" --runs "$RUNS" \
               --count-sid "$sid" 2>/dev/null || echo 0)
    if [ "$banked" -ge "$RUNS" ]; then
      echo "$(ts) SKIP $sid ($split): $banked/$RUNS valid runs already banked" >>"$LOG"
      continue
    fi

    status RUNNING "now: $sid ($split) — $banked/$RUNS banked, spending new calls"
    echo "$(ts) RUN  $sid ($split) banked=$banked" >>"$LOG"

    # Canonical experiment settings: temp=1.0 top_p=0.95 top_k=20 min_p=0
    # presence=0 repetition=1, seed=1234 base, 1h per call, streaming, NO
    # max_tokens ever, opaque eval artifacts only, truth copied scorer-side.
    # ${RUNNER:+...} lets tests substitute a fake runner; leave unset in prod.
    ${RUNNER:-python3 scripts/run_zero_shot.py} \
      --scenarios "$sid" --split "$split" \
      --detail full --termination-mean pooled --show-truth \
      --base-url "$BASE_URL" --model "$MODEL" \
      --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
      --presence-penalty 0.0 --repetition-penalty 1.0 \
      --timeout 3600 --runs "$RUNS" --stream \
      --wait-for-endpoint 1800 --max-consecutive-failures 5 \
      --skip-existing --out "$OUT" >>"$LOG" 2>&1
    rc=$?

    if [ $rc -ne 0 ]; then
      status STOPPED "runner exited rc=$rc on $sid ($split) at $(ts) — server issue?"
      echo "$(ts) FAIL $sid ($split) rc=$rc — stopping; progress is banked" >>"$LOG"
      echo
      echo "STOPPED on $sid (rc=$rc). Finished runs are kept."
      echo "Fix the server (or just wait), then re-run the SAME command to resume:"
      echo "  bash scripts/sweep_qwen27b.sh"
      echo "Status file: $STATUS   Log: $LOG"
      exit 1
    fi

    banked=$(python3 scripts/sweep_status.py --zero "$ZERO_DIR" --runs "$RUNS" \
               --count-sid "$sid" 2>/dev/null || echo 0)
    echo "$(ts) DONE $sid ($split): $banked/$RUNS valid" >>"$LOG"
    status RUNNING "$sid ($split) complete ($banked/$RUNS)"
    sleep "${SLEEP_BETWEEN:-15}"   # let the endpoint settle between scenarios
  done
done

# ---- all 47 scenarios complete: score, report, leak-check -------------------
status SCORING "all scenarios complete — scoring"
python3 scripts/score_xam.py "$ZERO_DIR" \
  --json-out "results/$OUT/scores.json" > "results/$OUT/reports/scoreboard.txt" 2>&1 || true
python3 scripts/report_xam.py "$ZERO_DIR" >>"$LOG" 2>&1 || true
python3 scripts/leakcheck.py >>"$LOG" 2>&1 || true   # full-workspace gate, ~2-4 min

status DONE "corpus complete — board in results/$OUT/reports/scoreboard.txt"
echo "$(ts) ALL SCENARIOS COMPLETE — corpus results/$OUT" >>"$LOG"
python3 scripts/sweep_status.py --zero "$ZERO_DIR" --runs "$RUNS" \
  --model "$MODEL" --out "$OUT" --state DONE
