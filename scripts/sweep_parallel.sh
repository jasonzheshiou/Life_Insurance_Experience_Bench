#!/usr/bin/env bash
# ============================================================================
# sweep_parallel.sh — the SAME experiment as sweep_qwen27b.sh, dispatched to N
# concurrent workers instead of one scenario at a time.
#
# Why a separate script: sweep_qwen27b.sh is deliberately sequential (it holds a
# flock for the whole sweep, because the archived corpora were produced with a
# single-slot server). When the server is started with `--parallel N`, the
# requests can genuinely overlap, so this driver keeps N scenarios in flight.
#
# What is identical to the sequential sweep (so results stay comparable):
#   * the runner, the canonical samplers, 1h timeout, streaming, NO max_tokens
#   * --runs 3 per scenario, --skip-existing (resume-safe), both splits
#   * the same corpus layout: results/<OUT>/zero_shot/sc-XXXX_runNN.json
#
# What differs, and is reported honestly:
#   * requests are BATCHED by the server (N sequences in one decode step), so the
#     serving configuration is not the same as a single-slot run. Batched decode
#     can perturb numerics in the last bits, and at temperature 1.0 that can
#     change an answer. Only compare against a baseline produced the same way,
#     unless an equivalence check has been run.
#   * meta.json / summary.md are rewritten by every worker (the runner does that
#     per scenario), so the LAST writer wins and the index would be partial. This
#     driver rebuilds a complete summary.md at the end via scripts/rebuild_index.py.
#
#   MODEL=Qwen3.6-27B OUT=xam_q36 RUNS=3 N=4 \
#     RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
#     bash scripts/sweep_parallel.sh
#   bash scripts/sweep_parallel.sh --status      # progress only, no API call
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

MODEL="${MODEL:-Qwen3.6-27B}"
OUT="${OUT:-xam_q36}"
RUNS="${RUNS:-3}"
N="${N:-4}"
RUNNER="${RUNNER:-python3 scripts/run_zero_shot.py}"
BASE_URL="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
ZERO="results/$OUT/zero_shot"
LOG="results/logs/sweep_parallel.log"
STATUS="results/logs/sweep_parallel_status.txt"
LOCK="results/logs/sweep_parallel.lock"
WORKLOGS="results/logs/parallel_workers"
mkdir -p results/logs "$ZERO" "results/$OUT/reports" "$WORKLOGS"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
banked() { python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" \
             --count-sid "$1" 2>/dev/null || echo 0; }
status() {  # $1 state  [$2 current]
  python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" --model "$MODEL" \
    --out "$OUT" --state "$1" ${2:+--current "$2"} \
    --status-file "$STATUS" >/dev/null 2>&1 || true
}

if [ "${1:-}" = "--status" ]; then
  python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" --model "$MODEL" \
    --out "$OUT" --state IDLE
  exit 0
fi

exec 9>"$LOCK"
flock -n 9 || { echo "another sweep_parallel holds $LOCK — not starting a second"; exit 1; }
trap 'status ABORTED "interrupted at $(ts)"' INT TERM

# ---- work list: every scenario that does not yet have RUNS valid answers ----
WORK=()
for split in optimization heldout; do
  for sid in $(ls "data/eval/$split" | grep -E '^sc-[0-9a-f]{6}$' | sort); do
    b=$(banked "$sid")
    [ "$b" -ge "$RUNS" ] && { echo "$(ts) SKIP $sid ($split) $b/$RUNS banked" >>"$LOG"; continue; }
    WORK+=("$split:$sid")
  done
done
echo "==== sweep_parallel start $(ts) model=$MODEL out=$OUT runs=$RUNS N=$N work=${#WORK[@]} ====" >>"$LOG"
status RUNNING "dispatching ${#WORK[@]} scenario(s) across $N workers"

run_one() {  # $1 = "split:sid"
  local item="$1" split="${1%%:*}" sid="${1##*:}"
  echo "$(ts) START $sid ($split)" >>"$LOG"
  $RUNNER --scenarios "$sid" --split "$split" \
    --detail full --termination-mean pooled --show-truth \
    --base-url "$BASE_URL" --model "$MODEL" \
    --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence-penalty 0.0 --repetition-penalty 1.0 \
    --timeout 3600 --runs "$RUNS" --stream \
    --wait-for-endpoint 1800 --max-consecutive-failures 5 \
    --skip-existing --out "$OUT" >>"$WORKLOGS/${sid}.log" 2>&1
  local rc=$?
  echo "$(ts) END   $sid ($split) rc=$rc banked=$(banked "$sid")/$RUNS" >>"$LOG"
  return $rc
}

# ---- dispatch, keeping exactly N workers busy ------------------------------
pids=()
launched=0
for item in "${WORK[@]}"; do
  while [ "${#pids[@]}" -ge "$N" ]; do
    wait -n 2>/dev/null || true
    alive=()
    for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive+=("$p"); done
    pids=("${alive[@]}")
    status RUNNING "$(( launched - ${#pids[@]} )) of ${#WORK[@]} done, ${#pids[@]} in flight"
  done
  run_one "$item" &
  pids+=($!)
  launched=$((launched+1))
done
wait

# ---- completion is VERIFIED from the corpus, never assumed ------------------
missing=""
for split in optimization heldout; do
  for sid in $(ls "data/eval/$split" | grep -E '^sc-[0-9a-f]{6}$' | sort); do
    [ "$(banked "$sid")" -ge "$RUNS" ] || missing="$missing $sid"
  done
done
python3 scripts/rebuild_index.py --out "$OUT" --runs "$RUNS" >>"$LOG" 2>&1 || true
python3 scripts/score_xam.py "$ZERO" --json-out "results/$OUT/scores.json" \
  > "results/$OUT/scoreboard.txt" 2>&1 || true
if [ -n "$missing" ]; then
  status INCOMPLETE "still missing:$missing — re-run this same command to retry"
  echo "$(ts) INCOMPLETE missing:$missing" >>"$LOG"
else
  status COMPLETE "every scenario has $RUNS valid answers"
  echo "$(ts) COMPLETE" >>"$LOG"
fi
grep -E "TOTALS|CLEAN-data honesty|DRIFT-WINDOW STRATA" "results/$OUT/scoreboard.txt" 2>/dev/null
