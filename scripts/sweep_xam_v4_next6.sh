#!/usr/bin/env bash
# Sweep the next 6 optimization scenarios, strictly sequentially (1-slot server).
# Resume-safe: after any interruption re-run the SAME command — --skip-existing
# inside run_one_scenario.sh means already-answered runs are never re-spent.
# Chat-decoupled: no per-scenario human interaction; score + dossier regenerate
# after EVERY scenario so documentation is current at any point of death.
set -uo pipefail   # deliberately NOT -e: one failed scenario must not kill the sweep
cd "$(dirname "$0")/.."

SIDS="sc-2d248f sc-314eca sc-3c83fd sc-409000 sc-48351f sc-4a7f9e"
STATUS="results/logs/sweep_xam_v4_next6.status"
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
  python3 scripts/score_xam.py results/xam_v4/zero_shot || echo "!! score step failed after $SID"
  python3 scripts/report_xam.py results/xam_v4/zero_shot || echo "!! report step failed after $SID"
  echo "$SID : $RUNST  $(date -u +%FT%TZ)" >> "$STATUS"
  echo "-- status so far --"; cat "$STATUS"
done

echo
echo "================ final workspace leakcheck ================"
python3 scripts/leakcheck.py || echo "!! leakcheck failed"
echo "sweep complete: $(date -u +%FT%TZ)" | tee -a "$STATUS"
