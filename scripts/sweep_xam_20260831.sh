#!/usr/bin/env bash
# Cross-examination sweep v2: every scenario, 3 independent stateless runs each.
#  - sampler settings per experiment spec; NO max_tokens; 1 h per-call timeout
#  - --skip-existing  : resumption-safe (survives WSL VM reclaim)
#  - --wait-for-endpoint: rides out a server reload instead of burning calls
#  - --max-consecutive-failures 5: circuit breaker
# Log lives INSIDE the repo (/tmp is wiped when the WSL VM is reclaimed).
set -uo pipefail
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena

BASE=http://192.168.1.59:8080/v1
MODEL=Qwen3.8-Flash-Next
COMMON=(--base-url "$BASE" --model "$MODEL"
        --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0
        --presence-penalty 0.0 --repetition-penalty 1.0
        --timeout 3600 --runs 3 --detail full --show-truth
        --skip-existing --wait-for-endpoint 1800
        --max-consecutive-failures 5)

for pass in 1 2 3 4 5 6 7 8; do
  echo "=== PASS $pass $(date -u +%FT%TZ) ==="
  rc_opt=0; rc_held=0
  echo "--- optimization $(date -u +%FT%TZ) ---"
  python3 scripts/run_zero_shot.py --scenarios all --split optimization \
      "${COMMON[@]}" --out xam_20260831_opt || rc_opt=$?
  echo "optimization rc=$rc_opt"
  echo "--- heldout $(date -u +%FT%TZ) ---"
  python3 scripts/run_zero_shot.py --scenarios all --split heldout \
      "${COMMON[@]}" --out xam_20260831_held || rc_held=$?
  echo "heldout rc=$rc_held"

  good_n=$(grep -l '"error": null' results/xam_20260831_opt/zero_shot/*_run*.json \
      results/xam_20260831_held/zero_shot/*_run*.json 2>/dev/null | wc -l)
  echo "=== PASS $pass done $(date -u +%FT%TZ): good=$good_n / 141 ==="
  if [ "$good_n" -ge 141 ]; then echo "=== SWEEP COMPLETE ==="; break; fi
  sleep 20
done
