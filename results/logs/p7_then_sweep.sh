#!/usr/bin/env bash
# Waits for the five-book v1.6d verification, checks it did not regress, and then
# runs the REMAINING 18 optimization books in the same corpus (pass 7) so the whole
# split ends up measured under one harness version. Guard: if the five-book strict
# total drops below the v1.6c baseline of 8, or sc-bba653 loses a unit, it stops
# for manual review instead of spending ~8 hours on the sweep.
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena || exit 1
LOG=results/logs/p7_then_sweep.log
echo "waiting for the five-book run — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
until grep -q "FIVE DONE" results/logs/p7_fix5.log 2>/dev/null; do sleep 60; done
sleep 5
python3 - <<'PY' >>"$LOG" 2>&1
import json
from pathlib import Path
p7=json.loads(Path('results/harness_opt_p7/scores.json').read_text())
r=list(p7.values())[0]
total=sum(r[s][0]['strict'] for s in r)
bba=r.get('sc-bba653',[{}])[0].get('strict',0)
print(f"five-book check: strict total {total} (v1.6c was 8), sc-bba653 {bba}/4")
ok = total >= 8 and bba == 4
Path('results/logs/p7_guard.txt').write_text(('GO' if ok else 'STOP') + f" total={total} bba653={bba}\n")
PY
GUARD=$(cat results/logs/p7_guard.txt 2>/dev/null)
echo "guard: $GUARD" >>"$LOG"
case "$GUARD" in
  GO*)
    echo "launching the remaining 18 — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
    PASS=7 WAIT_ENDPOINT=600 bash scripts/harness_pass_run.sh >>"$LOG" 2>&1
    echo "sweep finished — $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
    ;;
  *)
    echo "NOT launching the sweep — manual review needed ($GUARD)" >>"$LOG"
    ;;
esac
