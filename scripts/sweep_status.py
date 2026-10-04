#!/usr/bin/env python3
"""Human-readable progress tracker for a model-sweep corpus.

A run counts as FINISHED here exactly as run_zero_shot.py --skip-existing
defines it: the file <zero-dir>/<sid>_runNN.json exists and holds non-empty
content with no error. Scans every scenario dir under data/eval/{optimization,
heldout}, so it always reports against the full 47-scenario denominator.

Prints the status to stdout and (with --status-file) writes the same text to
the tracking txt. Used by scripts/sweep_qwen27b.sh after every scenario, but
works for any corpus:

    python3 scripts/sweep_status.py --zero results/xam_v5/zero_shot --runs 3 \
        --model Qwen3.8-27b --out xam_v5 --state RUNNING \
        --status-file results/logs/qwen27b.status.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SPLITS = ["optimization", "heldout"]


def all_scenarios(eval_root: Path, splits: list[str] | None = None) -> list[tuple[str, str]]:
    """(split, sid) pairs in sweep launch order."""
    out = []
    for split in (splits or SPLITS):
        base = eval_root / split
        if not base.is_dir():
            continue
        for d in sorted(base.glob("sc-*")):
            if d.is_dir():
                out.append((split, d.name))
    return out


def banked_runs(zero_dir: Path, sid: str, runs: int) -> int:
    """How many of sid's runs are valid (same rule as --skip-existing)."""
    k = 0
    for n in range(1, runs + 1):
        f = zero_dir / f"{sid}_run{n:02d}.json"
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if rec.get("content") and not rec.get("error"):
            k += 1
    return k


def build_status(a: argparse.Namespace) -> str:
    eval_root = Path(a.eval_root)
    zero_dir = Path(a.zero)
    splits = None if a.split == "all" else [a.split]
    sids = all_scenarios(eval_root, splits)
    total_runs = len(sids) * a.runs

    counts = [(sp, sid, banked_runs(zero_dir, sid, a.runs)) for sp, sid in sids]
    done_runs = sum(c for _, _, c in counts)
    done_scen = sum(1 for _, _, c in counts if c == a.runs)
    remaining = [(sp, sid, c) for sp, sid, c in counts if c < a.runs]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pct = (100.0 * done_runs / total_runs) if total_runs else 0.0
    L = [
        f"================ {a.model} full sweep — status ================",
        f"corpus:   results/{a.out}/zero_shot  (prompt rev v2, {a.runs} runs/scenario)",
        f"state:    {a.state}",
        f"updated:  {now}",
        "",
        f"RUNS FINISHED: {done_runs}/{total_runs}  ({pct:.1f}%)",
        f"SCENARIOS COMPLETE: {done_scen}/{len(sids)}",
        "",
    ]
    if a.current:
        L.append(f"current:   {a.current}")
    if a.last:
        L.append(f"last done: {a.last}")
    if a.current or a.last:
        L.append("")
    L.append(f"remaining scenarios ({len(remaining)}):")
    if remaining:
        for sp, sid, c in remaining:
            L.append(f"  {sid}  ({sp}, {c}/{a.runs} banked)")
    else:
        L.append("  none — every scenario has its full complement of valid runs")
    L += [
        "",
        "resume after any crash with the SAME command:",
        f"  {a.resume_hint}",
    ]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--zero", required=True, help="results/<out>/zero_shot dir")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--model", default="model")
    p.add_argument("--out", default="xam_v5")
    p.add_argument("--eval-root", default="data/eval")
    p.add_argument("--split", choices=["all", "optimization", "heldout"], default="all",
                   help="which split(s) count toward the totals (default all = 47)")
    p.add_argument("--state", default="IDLE",
                   help="free-form state label: RUNNING/WAITING_FOR_MODEL/STOPPED/DONE…")
    p.add_argument("--current", default="", help="scenario in progress line")
    p.add_argument("--last", default="", help="last completed line")
    p.add_argument("--status-file", default=None,
                   help="also write the rendered status to this txt")
    p.add_argument("--resume-hint", default="bash scripts/sweep_qwen27b.sh",
                   help="command shown as the resume instruction in the txt")
    p.add_argument("--count-sid", default=None,
                   help="machine mode: print only '<k>' (valid runs banked for "
                        "this scenario id, 0-<runs>) and exit — used by the "
                        "sweep wrapper to skip finished scenarios")
    a = p.parse_args(argv)

    if a.count_sid:
        print(banked_runs(Path(a.zero), a.count_sid, a.runs))
        return 0

    text = build_status(a)
    sys.stdout.write(text)
    if a.status_file:
        sf = Path(a.status_file)
        sf.parent.mkdir(parents=True, exist_ok=True)
        sf.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
