#!/usr/bin/env bash
# ============================================================================
# harness_exam_retry.sh — run a held-out exam to completion over a flaky server.
#
# WHY: harness_final_heldout.sh STOPS on the first failed scenario (it does not
# retry, unlike harness_pass_run.sh). A 72-call exam takes ~6 h, and the
# inference server blipped twice during the 3.6 campaign — once killing Exam A
# at 5/72. Without a wrapper, an overnight exam dies and waits for a human.
#
# This re-invokes the exam script until every run is banked. The exam script is
# resume-safe (--skip-existing + a banked-count check that ignores errored
# placeholders), so each pass continues where the last one stopped.
#
#   OUT=harness_q36_final bash scripts/harness_exam_retry.sh
#
# Env is passed straight through to the exam script: OUT, RUNS, MODEL, RUNNER,
# PINNED_PROMPT_FILE, LOGF, STATUS, WAIT_ENDPOINT.
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

OUT="${OUT:?set OUT, e.g. OUT=harness_q36_final}"
RUNS="${RUNS:-3}"
ZERO="results/$OUT/zero_shot"
ATTEMPTS="${ATTEMPTS:-40}"
PAUSE="${PAUSE:-90}"

# Count only USABLE records: a crashed attempt banks a 0-char placeholder with an
# error string, and counting those would end the loop early with a corpus full of
# holes.
valid_runs() {
  python3 - "$ZERO" <<'PY'
import glob, json, sys
n = 0
for f in glob.glob(sys.argv[1] + "/*_run*.json"):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if d.get("content") and not d.get("error"):
        n += 1
print(n)
PY
}

target=$(( $(ls data/eval/heldout | grep -cE '^sc-[0-9a-f]{6}$') * RUNS ))

for attempt in $(seq 1 "$ATTEMPTS"); do
  n=$(valid_runs)
  echo "=== attempt $attempt/$ATTEMPTS — $n/$target usable runs banked ==="
  if [ "$n" -ge "$target" ]; then
    echo "EXAM COMPLETE: $n/$target  corpus=results/$OUT"
    exit 0
  fi
  bash scripts/harness_final_heldout.sh || true
  n=$(valid_runs)
  if [ "$n" -ge "$target" ]; then
    echo "EXAM COMPLETE: $n/$target  corpus=results/$OUT"
    exit 0
  fi
  echo "--- attempt $attempt stopped at $n/$target; sleeping ${PAUSE}s ---"
  sleep "$PAUSE"
done

echo "EXAM INCOMPLETE after $ATTEMPTS attempts: $(valid_runs)/$target usable runs"
exit 1
