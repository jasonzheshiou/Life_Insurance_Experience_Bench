#!/usr/bin/env bash
# Re-runs the FIVE problem books once each under harness v1.6d (profile/onset
# agreement + direction-symmetric taxonomy), then scores the corpus.
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena || exit 1
LOG=results/logs/p7_fix5.log
for sid in sc-137901 sc-3c83fd sc-9372cd sc-bba653 sc-d72b95; do
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ)  $sid" >>"$LOG"
  PASS=7 bash scripts/harness_opt_step.sh "$sid" >>"$LOG" 2>&1
  echo "=== $sid exit=$? $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
done
python3 scripts/score_xam.py results/harness_opt_p7/zero_shot \
  --json-out results/harness_opt_p7/scores.json > results/harness_opt_p7/scoreboard.txt 2>&1
echo "FIVE DONE — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
