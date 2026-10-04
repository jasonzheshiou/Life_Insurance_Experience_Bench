#!/usr/bin/env bash
# ============================================================================
# harness_final_heldout.sh — FINAL test of the frozen harness on the HELDOUT
# split (24 scenarios). Run this only after the optimization loop has passed
# the freeze gate (strict >= ~80%, FP/run <= 1.0, no CLEAN regressions).
#
#  * The harness code is snapshotted (with sha256) into
#    results/<out>/harness_snapshot/ BEFORE the first call, so the exact
#    harness that produced the heldout numbers is preserved.
#  * Resume-safe: re-run the SAME command after any crash; --skip-existing
#    keeps every good run and re-spends only missing/failed ones.
#  * Status: results/logs/harness_final_status.txt   (RUNS FINISHED: n/72)
#
#   bash scripts/harness_final_heldout.sh              # 3 runs/scenario (protocol parity)
#   RUNS=1 bash scripts/harness_final_heldout.sh       # quick single-run look
#   bash scripts/harness_final_heldout.sh --status     # progress, no API call
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

OUT="${OUT:-harness_final}"
RUNS="${RUNS:-3}"
MODEL="${MODEL:-Qwen3.8-27B-Q8_0}"
BASE_URL="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
ZERO="results/$OUT/zero_shot"
LOGF="${LOGF:-results/logs/harness_final.log}"
STATUS="${STATUS:-results/logs/harness_final_status.txt}"
LOCKF="results/logs/harness_final.lock"
SNAP="results/$OUT/harness_snapshot"
mkdir -p results/logs "$ZERO"

write_status() {  # $1 state  [$2 current]
  python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" --model "$MODEL" \
    --out "$OUT" --split heldout --state "$1" ${2:+--current "$2"} \
    --resume-hint "bash scripts/harness_final_heldout.sh" \
    --status-file "$STATUS" >/dev/null 2>&1 || true
}

if [ "${1:-}" = "--status" ]; then
  python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" --model "$MODEL" \
    --out "$OUT" --split heldout --state IDLE \
    --resume-hint "bash scripts/harness_final_heldout.sh"
  exit 0
fi

exec 9>"$LOCKF"
flock -n 9 || { echo "another harness_final_heldout is running — exiting"; exit 1; }

# ---- snapshot the frozen harness before any call --------------------------
if [ ! -f "$SNAP/MANIFEST.txt" ]; then
  mkdir -p "$SNAP"
  cp scripts/stats_pack.py scripts/run_zero_shot.py "$SNAP/"
  { echo "harness snapshot (frozen) — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "model=$MODEL  runs/scenario=$RUNS  base_url=$BASE_URL"
    for f in stats_pack.py run_zero_shot.py; do
      printf '%s  %s\n' "$(sha256sum "$SNAP/$f" | cut -c1-64)" "$f"
    done
    # RUNNER may point at run_zero_shot_baseline_v2.py, which overrides the
    # system prompt from a FILE. When it does, the prompt is part of the harness
    # and must be snapshotted too, or the pass is not reproducible. Note which
    # runner produced these numbers as well: "same harness" for a cross-model
    # comparison means the same RUNNER, not just the same two code files.
    echo "runner=${RUNNER:-python3 scripts/run_zero_shot.py}"
    if [ -n "${PINNED_PROMPT_FILE:-}" ] && [ -f "${PINNED_PROMPT_FILE}" ]; then
      cp "$PINNED_PROMPT_FILE" "$SNAP/system_prompt.txt"
      printf '%s  %s\n' "$(sha256sum "$SNAP/system_prompt.txt" | cut -c1-64)" \
        "system_prompt.txt (from $PINNED_PROMPT_FILE)"
    fi
  } > "$SNAP/MANIFEST.txt"
  echo "frozen harness snapshot written to $SNAP"
fi

echo "==== harness FINAL heldout start $(date -u +%Y-%m-%dT%H:%M:%SZ) ====" >>"$LOGF"

for sid in $(ls data/eval/heldout | grep -E '^sc-[0-9a-f]{6}$' | sort); do
  banked=$(python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" \
             --count-sid "$sid" 2>/dev/null || echo 0)
  if [ "$banked" -ge "$RUNS" ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) SKIP $sid ($banked/$RUNS banked)" >>"$LOGF"
    continue
  fi
  write_status RUNNING "now: $sid (heldout) — $banked/$RUNS banked"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) RUN $sid ($banked/$RUNS banked)" >>"$LOGF"

  ${RUNNER:-python3 scripts/run_zero_shot.py} --scenarios "$sid" --split heldout \
    --detail full --termination-mean pooled \
    --base-url "$BASE_URL" --model "$MODEL" \
    --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --presence-penalty 0.0 --repetition-penalty 1.0 \
    --timeout 3600 --runs "$RUNS" --stream \
    --wait-for-endpoint "${WAIT_ENDPOINT:-1800}" --max-consecutive-failures 5 \
    --skip-existing --harness full --tool-calls "${TOOL_CALLS:-4}" \
    --out "$OUT" >>"$LOGF" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then
    write_status STOPPED "runner rc=$rc on $sid — fix and re-run the SAME command"
    echo "STOPPED on $sid (rc=$rc). Progress is banked; re-run: bash scripts/harness_final_heldout.sh"
    exit 1
  fi
  sleep "${SLEEP_BETWEEN:-15}"
done

# ---- final: score + dossiers + leak gate ----------------------------------
write_status SCORING "corpus complete — scoring"
python3 scripts/score_xam.py "$ZERO" --json-out "results/$OUT/scores.json" \
  > "results/$OUT/scoreboard.txt" 2>&1 || true
python3 scripts/report_xam.py "$ZERO" >>"$LOGF" 2>&1 || true
python3 scripts/leakcheck.py >>"$LOGF" 2>&1 || true      # full workspace gate
python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" --model "$MODEL" \
  --out "$OUT" --split heldout --state DONE \
  --resume-hint "bash scripts/harness_final_heldout.sh"
echo "HELDOUT FINAL COMPLETE — board: results/$OUT/reports/scoreboard.txt" | tee -a "$LOGF"
grep -E "TOTALS|CLEAN-data honesty|DRIFT-WINDOW STRATA" "results/$OUT/scoreboard.txt" 2>/dev/null
grep -E "^leak check" "$LOGF" | tail -1
