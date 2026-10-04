#!/usr/bin/env bash
# Batch 2: optimization scenarios #11-#16, strictly sequentially (1-slot server).
# Resume-safe: re-run the SAME command — --skip-existing inside
# run_one_scenario.sh re-spends only empty/error stubs, never finished runs.
set -uo pipefail
cd "$(dirname "$0")/.."

SIDS="sc-5e376b sc-63f1c7 sc-6e2478 sc-8a9fa1 sc-8d3b47 sc-9372cd"
STATUS="results/logs/sweep_xam_v4_batch2.status"
mkdir -p results/logs
echo "sweep start: $(date -u +%FT%TZ)  sids: $SIDS" | tee "$STATUS"

for SID in $SIDS; do
  echo
  echo "================ $SID  $(date -u +%FT%TZ) ================"
  if bash scripts/run_one_scenario.sh "$SID"; then
    RUNST=ok
  else
    RUNST="run_failed_rc$?"
    echo "!! $SID run step failed ($RUNST) — scoring what exists and continuing"
  fi
  python3 scripts/score_xam.py results/xam_v4/zero_shot | tail -3
  python3 scripts/report_xam.py results/xam_v4/zero_shot >/dev/null
  echo "$SID : $RUNST  $(date -u +%FT%TZ)" >> "$STATUS"
done

echo
echo "================ final workspace leakcheck ================"
python3 scripts/leakcheck.py || echo "!! leakcheck failed"
echo "sweep complete: $(date -u +%FT%TZ)" | tee -a "$STATUS"
