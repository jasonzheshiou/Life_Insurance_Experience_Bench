#!/usr/bin/env bash
# Re-runs the two book-wide books whose pack text changed (v1.6e): the paired
# level-change entries the pack used to invite were 7 of the 29 false alarms.
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena || exit 1
LOG=results/logs/p7_fix2.log
for sid in sc-314eca sc-9660b9; do
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ)  $sid" >>"$LOG"
  PASS=7 bash scripts/harness_opt_step.sh "$sid" >>"$LOG" 2>&1
  echo "=== $sid exit=$? $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
done
python3 scripts/score_xam.py results/harness_opt_p7/zero_shot \
  --json-out results/harness_opt_p7/scores.json > results/harness_opt_p7/scoreboard.txt 2>&1
python3 scripts/harness_gate.py results/harness_opt_p7/zero_shot \
  --label "harness v1.6e — full 23-book corpus" --json-out results/harness_opt_p7/gate.json \
  > results/harness_opt_p7/gate.txt 2>&1
echo "GATE EXIT=$? — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
