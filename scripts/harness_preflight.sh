#!/usr/bin/env bash
# ============================================================================
# harness_preflight.sh — validate the FULL harness prompt (pack + rules) for
# every scenario on BOTH splits, without spending a single API call.
#
# Run this after ANY edit to scripts/stats_pack.py, HARNESS_RULES in
# scripts/run_zero_shot.py, or the prompt builder. It assembles exactly the
# prompt the runner would send and runs the same leak/integrity gate the
# runner runs — so an edit that would trip the gate (e.g. answer vocabulary
# such as banned tokens leaking into the pack or the rules) is caught here in
# seconds instead of killing a loop iteration.
#
#   bash scripts/harness_preflight.sh          # both splits
#   bash scripts/harness_preflight.sh optimization
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 1

SPLITS="${1:-optimization heldout}"
fail=0
for split in $SPLITS; do
  out=$(python3 scripts/run_zero_shot.py --scenarios all --split "$split" \
        --detail full --termination-mean pooled --harness full --dry-run 2>&1)
  if echo "$out" | grep -q "REFUSING TO RUN"; then
    echo "[$split] REFUSED — the gate would block a live run:"
    echo "$out" | grep -E "leak banned|missing|integrity" | head -8
    fail=1
  else
    n=$(echo "$out" | grep -c '^SCENARIO sc-')
    pack=$(echo "$out" | grep -c 'COMPUTED EVIDENCE PACK')
    rules=$(echo "$out" | grep -c 'HARNESS MODE')
    echo "[$split] OK — $n scenarios; pack refs: $pack; rules blocks: $rules"
    [ "$n" -gt 0 ] && [ "$rules" -ge "$n" ] || { echo "  !! harness text missing from the prompt"; fail=1; }
  fi
done
[ "$fail" -eq 0 ] && echo "PREFLIGHT: PASS (no API calls made)" || echo "PREFLIGHT: FAIL"
exit "$fail"
