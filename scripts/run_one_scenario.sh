#!/usr/bin/env bash
# Run ONE scenario with the canonical cross-examination settings.
# Usage:  bash scripts/run_one_scenario.sh <sc-id> [RUNID] [--dry-run]
# Example: bash scripts/run_one_scenario.sh sc-137901
#          bash scripts/run_one_scenario.sh sc-137901 xam_v4   (default run id)
#          bash scripts/run_one_scenario.sh sc-137901 xam_v4 --dry-run  (no API)
set -euo pipefail
cd "$(dirname "$0")/.."

SID="${1:?usage: bash scripts/run_one_scenario.sh <sc-id> [RUNID] [--dry-run]}"
OUT="${2:-xam_v4}"
EXTRA=""
[ "${3:-}" = "--dry-run" ] && EXTRA="--dry-run"

# Resolve split automatically from the truth id map.
SPLIT=$(python3 -c "
import csv
sid='$SID'
with open('data/truth/id_map.csv', newline='') as f:
    for r in csv.DictReader(f):
        if r['eval_id']==sid:
            print(r['split']); break
" )
[ -n "$SPLIT" ] || { echo "unknown scenario id: $SID"; exit 2; }

echo "==> scenario $SID (split=$SPLIT) -> results/$OUT/zero_shot"

python3 scripts/run_zero_shot.py \
  --scenarios "$SID" --split "$SPLIT" \
  --detail full --termination-mean pooled --show-truth \
  --base-url http://192.168.1.59:8080/v1 --model Qwen3.8-Flash-Next \
  --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 \
  --timeout 3600 --runs 3 --stream \
  --wait-for-endpoint 1800 --max-consecutive-failures 5 \
  --out "$OUT" $EXTRA

echo
echo "==> results -> results/$OUT/zero_shot/${SID}_runNN.json (+ prompt + truth)"
