#!/usr/bin/env bash
# ============================================================================
# harness_pass_run.sh — run the WHOLE remaining optimization pass unattended.
#
# Difference from harness_opt_step.sh (one scenario per invocation, stops for
# a harness edit between scenarios): this one walks every optimization
# scenario that lacks a valid run, back to back, and CONTINUES past failures
# (retrying each scenario up to RETRIES times with a pause) so an overnight
# run survives server restarts. Use it when the harness is frozen for the
# pass; use harness_opt_step.sh while still iterating on the harness.
#
#   bash scripts/harness_pass_run.sh              # continue/complete pass 1
#   PASS=2 bash scripts/harness_pass_run.sh       # second pass (fresh corpus)
#   bash scripts/harness_pass_run.sh --status     # progress only
#
# Resume-safe: re-run the same command after any interruption; completed
# scenarios are skipped, failed ones re-spent. Status:
#   results/logs/harness_pass_status.txt   |  per-scenario diffs:
#   results/logs/harness_opt_loop.md
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

PASS="${PASS:-1}"
# Corpus name; overridable so a different MODEL can run the same pass structure
# into its own corpus (e.g. OUT=harness_q36_p1 MODEL=Qwen3.6-27B). Default
# unchanged, so every archived pass keeps the name it was run under.
OUT="${OUT:-harness_opt_p${PASS}}"
RUNS="${RUNS:-1}"
TOOL_CALLS="${TOOL_CALLS:-4}"
RETRIES="${RETRIES:-3}"
MODEL="${MODEL:-Qwen3.8-27B-Q8_0}"
BASE_URL="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
# How long ONE attempt waits for the LLM endpoint to come back before giving up
# (the runner then fails fast and the loop retries the scenario). Lower it, e.g.
# WAIT_ENDPOINT=300, if the server is flaky and you would rather burn retries
# than sit in a 30-minute wait per attempt.
WAIT_ENDPOINT="${WAIT_ENDPOINT:-1800}"
ZERO="results/$OUT/zero_shot"
LOGF="results/logs/harness_pass_run.log"
LOOP="results/logs/harness_opt_loop.md"
STATUS="results/logs/harness_pass_status.txt"
LOCKF="results/logs/harness_opt_step.lock"     # shared with the step script
mkdir -p results/logs "$ZERO"

opt_sids() {
  # SIDS lets the per-scenario improvement loop run ONE wrong book without
  # touching the whole split: SIDS=sc-48351f,sc-3c83fd bash scripts/harness_pass_run.sh
  # Everything else (snapshot, retries, per-book diff, re-score) still happens,
  # so a probe is recorded exactly like a pass.
  if [ -n "${SIDS:-}" ]; then
    echo "$SIDS" | tr ',' '\n' | tr -d ' ' | grep -E '^sc-[0-9a-f]{6}$'
    return
  fi
  ls data/eval/optimization | grep -E '^sc-[0-9a-f]{6}$' | sort
}
banked() { python3 scripts/sweep_status.py --zero "$ZERO" --runs "$RUNS" \
             --count-sid "$1" 2>/dev/null || echo 0; }
# Count how many scenarios have their full complement of valid runs.
scenarios_done() {
  local _done=0 _sid
  for _sid in $(opt_sids); do
    [ "$(banked "$_sid")" -ge "$RUNS" ] && _done=$((_done + 1))
  done
  echo "$_done"
}

write_status() {  # $1 state ; $2 current ; $3 extra
  local _done _total
  _total=$(opt_sids | wc -l)
  _done=$(scenarios_done)
  {
    echo "==== harness optimization pass $PASS — unattended run ===="
    echo "state:    $1"
    echo "updated:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "corpus:   results/$OUT  (model=$MODEL, runs/scenario=$RUNS, harness=h1)"
    echo "SCENARIOS FINISHED: $_done/$_total"
    [ -n "${2:-}" ] && echo "current:  $2"
    [ -n "${3:-}" ] && echo "note:     $3"
    echo "log:      $LOGF"
    echo "resume:   bash scripts/harness_pass_run.sh"
  } > "$STATUS"
}

exec 9>"$LOCKF"
if [ "${1:-}" = "--status" ]; then
  # Only label the pass IDLE when nothing holds the shared lock; otherwise the
  # file belongs to the live run and must not be overwritten.
  flock -n 9 && write_status IDLE
  cat "$STATUS"; exit 0
fi
flock -n 9 || { echo "another harness run holds $LOCKF — not starting a second"; exit 1; }

# ---- snapshot the harness this pass will use ------------------------------
# The harness is edited in place between passes, and this project is not under
# version control, so without this copy the exact code behind a pass's numbers
# is unrecoverable (it happened: v1.3's source is gone). The held-out script has
# always done this; now every pass does too.
SNAP="results/$OUT/harness_snapshot"
if [ ! -f "$SNAP/MANIFEST.txt" ]; then
  mkdir -p "$SNAP"
  cp scripts/stats_pack.py scripts/run_zero_shot.py "$SNAP/"
  {
    echo "harness snapshot for pass $PASS — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "model=$MODEL  runs/scenario=$RUNS  tool_calls=$TOOL_CALLS"
    for f in stats_pack.py run_zero_shot.py; do
      printf '%s  %s\n' "$(sha256sum "$SNAP/$f" | cut -c1-64)" "$f"
    done
    # Snapshot the system prompt text too — code+prompt are both needed to
    # reproduce a question, so leaving the prompt outside the snapshot makes the
    # pass unreproducible. PINNED_PROMPT_FILE names the file when the runner is
    # run_zero_shot_baseline_v2.py (a model evolving its own prompt without
    # editing run_zero_shot.py). When that variable is NOT exported we must fall
    # back to the wrapper's own default rather than skipping the copy: pass 1 of
    # the 3.6 campaign skipped it exactly that way, and the prompt had to be
    # added to the snapshot by hand afterwards.
    _prompt="${PINNED_PROMPT_FILE:-data/prompts/system_v2_baseline.txt}"
    if [ -f "$_prompt" ]; then
      cp "$_prompt" "$SNAP/system_prompt.txt"
      printf '%s  %s\n' "$(sha256sum "$SNAP/system_prompt.txt" | cut -c1-64)" \
        "system_prompt.txt (from $_prompt${PINNED_PROMPT_FILE:+; PINNED_PROMPT_FILE})"
    else
      printf 'WARNING: system prompt file not found (%s) — snapshot has code only\n' \
        "$_prompt"
    fi
  } > "$SNAP/MANIFEST.txt"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) harness snapshot -> $SNAP" >>"$LOGF"
fi

echo "==== pass $PASS start $(date -u +%Y-%m-%dT%H:%M:%SZ) model=$MODEL ====" >>"$LOGF"
failed=""
for SID in $(opt_sids); do
  if [ "$(banked "$SID")" -ge "$RUNS" ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) SKIP $SID (already banked)" >>"$LOGF"
    continue
  fi
  ok=0
  for TRY in $(seq 1 "$RETRIES"); do
    write_status RUNNING "$SID (attempt $TRY/$RETRIES)"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) RUN $SID try $TRY" >>"$LOGF"
    ${RUNNER:-python3 scripts/run_zero_shot.py} --scenarios "$SID" --split optimization \
      --detail full --termination-mean pooled \
      --base-url "$BASE_URL" --model "$MODEL" \
      --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
      --presence-penalty 0.0 --repetition-penalty 1.0 \
      --timeout 3600 --runs "$RUNS" --stream \
      --wait-for-endpoint "$WAIT_ENDPOINT" --max-consecutive-failures 5 \
      --skip-existing --harness full --tool-calls "$TOOL_CALLS" \
      --out "$OUT" >>"$LOGF" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ] && [ "$(banked "$SID")" -ge "$RUNS" ]; then ok=1; break; fi
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FAIL $SID rc=$rc (try $TRY)" >>"$LOGF"
    sleep "${RETRY_SLEEP:-120}"
  done
  {
    echo; echo "## $(date -u +%Y-%m-%dT%H:%M:%SZ)  $SID (pass $PASS, unattended)"
    echo '```'
    python3 scripts/harness_diff.py "$SID" --out "$OUT" 2>&1 | head -40
    echo '```'
  } >>"$LOOP"
  python3 scripts/score_xam.py "$ZERO" --json-out "results/$OUT/scores.json" \
    > "results/$OUT/scoreboard.txt" 2>&1 || true
  [ "$ok" -eq 1 ] || failed="$failed $SID"
  sleep "${SLEEP_BETWEEN:-10}"
done

# ---- completion is VERIFIED against the corpus, never assumed -------------
missing=""
for SID in $(opt_sids); do
  [ "$(banked "$SID")" -ge "$RUNS" ] || missing="$missing $SID"
done
if [ -n "$missing" ]; then
  write_status PASS_INCOMPLETE "still missing:$missing" "failures:${failed:- none} — re-run to retry"
else
  write_status PASS_COMPLETE "all $(opt_sids | wc -l) optimization scenarios have a valid run"
fi
echo "==== pass $PASS end $(date -u +%Y-%m-%dT%H:%M:%SZ) failures:${failed:- none} ====" >>"$LOGF"
grep -E "TOTALS|CLEAN-data honesty|DRIFT-WINDOW STRATA" "results/$OUT/scoreboard.txt" 2>/dev/null
