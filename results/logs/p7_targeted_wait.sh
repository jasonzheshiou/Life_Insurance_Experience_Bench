#!/usr/bin/env bash
# Waits for the LLM endpoint to come back, then runs the FIVE books that failed
# the v1.6b sweep once each under the current harness (v1.6c). One run per book,
# no growth in between — this is a measurement, not an iteration.
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena || exit 1
EP="${ABENCH_BASE_URL:-http://192.168.1.59:8080/v1}"
LOG=results/logs/p7_targeted_wait.log
echo "waiting for $EP — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
until curl -s -o /dev/null --max-time 5 "$EP/models"; do sleep 30; done
echo "endpoint is back — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
for sid in sc-137901 sc-3c83fd sc-9372cd sc-bba653 sc-d72b95; do
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ)  $sid" >>"$LOG"
  PASS=7 bash scripts/harness_opt_step.sh "$sid" >>"$LOG" 2>&1
  echo "=== $sid exit=$? $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
done
python3 scripts/score_xam.py results/harness_opt_p7/zero_shot \
  --json-out results/harness_opt_p7/scores.json > results/harness_opt_p7/scoreboard.txt 2>&1
echo "ALL FIVE DONE — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
