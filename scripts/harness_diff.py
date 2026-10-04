#!/usr/bin/env python3
"""harness_diff.py — per-scenario outcome diff for the harness improvement loop.

EXPERIMENTER SIDE ONLY: reads ground truth (data/truth/manifests/) and one run
record and prints what the model found vs what the truth says, per control,
plus false positives and the tool transcript. This output must NEVER be pasted
into a model prompt; it exists so the harness (stats_pack verdicts, rules)
can be tuned on the OPTIMIZATION split between scenarios.

    python3 scripts/harness_diff.py sc-042304 --out harness_opt_p1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import score_xam as sc  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sid")
    ap.add_argument("--out", default="harness_opt_p1", help="results/<out>/zero_shot")
    ap.add_argument("--run", type=int, default=1)
    a = ap.parse_args(argv)

    run_p = Path("results") / a.out / "zero_shot" / f"{a.sid}_run{a.run:02d}.json"
    rec = sc.load_json(run_p)
    if not rec:
        print(f"no valid run record at {run_p}")
        return 1
    man = sc.load_json(Path("data/truth/manifests") / f"{a.sid}.json")
    if not man:
        print(f"no truth manifest for {a.sid}")
        return 1

    status, findings, overall = sc.parse_findings(rec.get("content"))
    s = sc.score_run(man, findings)
    matched = set(s.get("matched_idx") or [])
    supp = set(s.get("supp_idx") or [])

    ctrl = man.get("controls") or []
    print(f"scenario {a.sid}  json={status}  overall_says={overall}  "
          f"error={rec.get('error')}  wall={rec.get('wall_seconds')}s")
    har = rec.get("harness") or {}
    print(f"harness: tool_calls={har.get('tool_calls')}  "
          f"pack_sha={(har.get('pack_sha') or '')[:12]}")
    print("TRUTH CONTROLS:")
    if not ctrl:
        print("  (none — clean scenario; any anomaly claim is a FP)")
    for c in ctrl:
        print(f"  {c.get('benefit')} | {c.get('type')} | window {c.get('window') or c.get('years')}"
              f" | factor {c.get('factor')}")
    print("MODEL FINDINGS:")
    if not findings:
        print("  (none)")
    for i, f in enumerate(findings):
        tag = "MATCH" if i in matched else ("supp" if i in supp else "FP")
        print(f"  [{i}] {tag:5s} {f.get('benefit')} | {f.get('pattern')} | "
              f"{f.get('direction')} | {f.get('years')} | conf {f.get('confidence')} | "
              f"mag {str(f.get('magnitude'))[:40]}")
    # Use the scorer's own unit count: a control whose benefit is "all" expands
    # into one unit per benefit line (4), so counting raw controls printed a
    # misleading "strict 4/1" for the book-wide traps.
    n_units = s.get("n_controls") or len(ctrl)
    n_fp = len([i for i in range(len(findings)) if i not in matched and i not in supp])
    print(f"SCORE: strict {s.get('strict')}/{n_units}  loose {s.get('loose')}/{n_units}  "
          f"FP {s.get('fp', n_fp)}")
    tr = har.get("transcript") or []
    if tr:
        print(f"TOOL TRANSCRIPT ({len(tr)} call(s)):")
        for j, t in enumerate(tr):
            code = (t.get("code") or "").strip().replace("\n", " ⏎ ")
            print(f"  [{j}] run: {code[:160]}")
            print(f"      -> {(t.get('result') or '').strip()[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
