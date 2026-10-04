#!/usr/bin/env python3
"""harness_gate.py — the freeze gate for the harness optimization campaign.

The campaign rule (agreed up front, so the stopping decision is not a matter of
taste afterwards):

    FREEZE the harness only if ALL of these hold on the optimization split
      1. strict recall        >= 80 %
      2. false positives/run  <= 1.0
      3. clean-data honesty   == 0 clean runs where an anomaly was claimed
      4. data integrity       == 0 unparseable answers, 0 errored runs
      5. no regression on the two drift strata vs the zero-shot reference
    and the whole campaign is capped at 3 passes over the 23 scenarios.

Criterion 5 is the one that stops the harness from "winning" by trading a real
capability for a proxy: a version may not buy overall recall by getting worse at
bounded-then-reverting drifts, which is the control type the zero-shot model
handles worst (2/51 at baseline).

Usage
    python3 scripts/harness_gate.py results/harness_opt_p3/zero_shot
    python3 scripts/harness_gate.py results/harness_opt_p3/zero_shot \
        --reference results/xam_v5/zero_shot --label "harness v1.4 (pass 3)"
    python3 scripts/harness_gate.py results/harness_opt_p3/zero_shot --json-out gate.json

Exit status: 0 = FREEZE, 1 = DO NOT FREEZE.  Nothing here calls the LLM.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_xam  # noqa: E402  (reuse the canonical scorer, never a copy of it)

MIN_STRICT = 0.80
MAX_FP_PER_RUN = 1.0


def split_ids(split: str, eval_root: Path = Path("data/eval")) -> set[str] | None:
    """Scenario ids belonging to a split; None means 'do not filter'."""
    if split in ("", "all"):
        return None
    return {p.name for p in (eval_root / split).glob("sc-*") if p.is_dir()}


def aggregate(run_dir: Path, truth: Path, keep: set[str] | None = None,
              max_run: int | None = None) -> dict:
    """Same aggregation as score_xam.main(), returned as data.

    `keep`/`max_run` matter for honesty: the gate compares the candidate corpus
    against a reference corpus, and that comparison is only meaningful when both
    sides cover the SAME scenarios with the SAME number of runs. The zero-shot
    corpus holds all 47 scenarios x 3 runs, so it must be narrowed to the
    optimization split and run 1 before its numbers may be compared.
    """
    id_map = {}
    p = truth / "id_map.csv"
    if p.is_file():
        import csv
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                id_map[r["eval_id"]] = r

    rows: dict[str, list] = defaultdict(list)
    drift = []          # (sid, bounded, strict, loose)
    for f in sorted(run_dir.glob("*_run*.json")):
        rec = score_xam.load_json(f)
        if not rec:
            continue
        sid, run = rec["scenario_id"], rec.get("run")
        if keep is not None and sid not in keep:
            continue
        if max_run is not None and (run or 0) > max_run:
            continue
        man = score_xam.load_json(truth / "manifests" / f"{sid}.json")
        if man is None:
            continue
        status, findings, overall = score_xam.parse_findings(rec.get("content"))
        s = score_xam.score_run(man, findings)
        clean = bool(man.get("no_op")) or not (man.get("controls") or [])
        rows[sid].append({
            "run": run, "json": status, "overall": overall, "clean": clean,
            "family": (id_map.get(sid) or {}).get("family"),
            "n_controls": s.get("n_controls", 0),
            "strict": s.get("strict", 0), "loose": s.get("loose", 0),
            "fp": s.get("fp", 0), "error": rec.get("error"),
        })
        for bounded, st_, lo_ in s.get("_drift_units", []):
            drift.append((sid, bounded, st_, lo_))

    agg = defaultdict(int)
    fams: dict[str, dict] = defaultdict(lambda: {"strict": 0, "loose": 0, "controls": 0,
                                                 "fp": 0, "runs": 0})
    for sid, runs in sorted(rows.items()):
        clean = bool(runs and runs[0]["clean"])
        fam = "CLEAN" if clean else str(runs[0]["family"])
        for r in runs:
            agg["n_runs"] += 1
            agg["fp"] += r["fp"]
            if r["json"] != "valid":
                agg["badjson"] += 1
            if r["error"]:
                agg["err"] += 1
            if clean:
                agg["clean_runs"] += 1
                if r["overall"] == "anomalies":
                    agg["clean_false_claims"] += 1
            else:
                agg["controls"] += r["n_controls"]
                agg["strict"] += r["strict"]
                agg["loose"] += r["loose"]
                fams[fam]["controls"] += r["n_controls"]
                fams[fam]["strict"] += r["strict"]
                fams[fam]["loose"] += r["loose"]
            fams[fam]["runs"] += 1
            fams[fam]["fp"] += r["fp"]

    n_p = sum(1 for _, b, _, _ in drift if not b)
    s_p = sum(st for _, b, st, _ in drift if not b)
    l_p = sum(lo for _, b, _, lo in drift if not b)
    n_b = sum(1 for _, b, _, _ in drift if b)
    s_b = sum(st for _, b, st, _ in drift if b)
    l_b = sum(lo for _, b, _, lo in drift if b)
    denom = agg["controls"] or 1
    return {
        "run_dir": str(run_dir),
        "split": None,
        "runs_per_scenario": max_run,
        "n_runs": agg["n_runs"],
        "strict": agg["strict"], "controls": agg["controls"],
        "strict_pct": agg["strict"] / denom,
        "loose": agg["loose"], "loose_pct": agg["loose"] / denom,
        "fp": agg["fp"], "fp_per_run": agg["fp"] / (agg["n_runs"] or 1),
        "badjson": agg["badjson"], "errors": agg["err"],
        "clean_runs": agg["clean_runs"],
        "clean_false_claims": agg["clean_false_claims"],
        "persistent": {"hit": s_p, "n": n_p, "loose": l_p},
        "bounded": {"hit": s_b, "n": n_b, "loose": l_b},
        "families": {k: dict(v) for k, v in sorted(fams.items())},
    }


def evaluate(a: dict, ref: dict | None, min_strict: float, max_fp: float) -> list[dict]:
    checks = [
        {"name": "strict recall >= %.0f%%" % (min_strict * 100),
         "ok": a["strict_pct"] >= min_strict,
         "detail": f"{a['strict']}/{a['controls']} = {a['strict_pct']:.1%}"},
        {"name": "false positives per run <= %.1f" % max_fp,
         "ok": a["fp_per_run"] <= max_fp,
         "detail": f"{a['fp']}/{a['n_runs']} = {a['fp_per_run']:.2f}"},
        {"name": "clean data never called anomalous",
         "ok": a["clean_false_claims"] == 0,
         "detail": f"claimed an anomaly on {a['clean_false_claims']}/{a['clean_runs']} "
                   f"clean run(s)"},
        {"name": "no unparseable answers and no errored runs",
         "ok": a["badjson"] == 0 and a["errors"] == 0,
         "detail": f"badjson={a['badjson']} errors={a['errors']}"},
    ]
    if ref is not None:
        for key, label in (("persistent", "persistent-to-horizon"),
                           ("bounded", "bounded-then-reverting")):
            new, old = a[key], ref[key]
            ok = new["hit"] >= old["hit"]
            if ok:
                detail = (f"{new['hit']}/{new['n']} vs {old['hit']}/{old['n']} at "
                          f"zero-shot (no regression)")
            else:
                detail = (f"REGRESSION {new['hit']}/{new['n']} vs {old['hit']}/{old['n']} "
                          f"at zero-shot")
            checks.append({"name": f"drift stratum not worse: {label}", "ok": ok,
                           "detail": detail})
    return checks


def report(a: dict, checks: list[dict], ref: dict | None, label: str,
           split: str = "optimization") -> bool:
    width = 74
    print("=" * width)
    print(f"FREEZE GATE — {label}")
    print(f"corpus: {a['run_dir']}   ({a['n_runs']} run(s), {split} split, "
          f"run 1..{a['runs_per_scenario']})")
    print("=" * width)
    for c in checks:
        print(f"  [{'PASS' if c['ok'] else 'FAIL'}] {c['name']:<44} {c['detail']}")
    print("-" * width)
    print("  per-family strict recall (strict/controls, fp):")
    for fam, v in a["families"].items():
        if fam == "CLEAN":
            print(f"    {fam:<22} clean — false anomaly claims "
                  f"{a['clean_false_claims']}/{v['runs']}, fp={v['fp']}")
        else:
            pct = (v["strict"] / v["controls"]) if v["controls"] else 0.0
            print(f"    {fam:<22} {v['strict']:>2}/{v['controls']:<2} = {pct:>5.1%}  "
                  f"loose {v['loose']}/{v['controls']}  fp={v['fp']}")
    print("-" * width)
    if ref is not None:
        print(f"  reference (zero-shot, same design): {ref['strict']}/{ref['controls']} = "
              f"{ref['strict_pct']:.1%} strict, fp/run {ref['fp_per_run']:.2f}")
    failed = [c["name"] for c in checks if not c["ok"]]
    verdict = not failed
    print(f"  VERDICT: {'FREEZE — all criteria met' if verdict else 'DO NOT FREEZE'}")
    if failed:
        print(f"  not met: {'; '.join(failed)}")
    print("=" * width)
    return verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", help="e.g. results/harness_opt_p3/zero_shot")
    ap.add_argument("--truth", default="data/truth")
    ap.add_argument("--reference", default="results/xam_v5/zero_shot",
                    help="corpus to compare drift strata against ('' disables)")
    ap.add_argument("--split", default="optimization",
                    choices=["optimization", "heldout", "all"],
                    help="scenario set the gate applies to; the reference is "
                         "narrowed to it so the comparison is like-for-like")
    ap.add_argument("--runs", type=int, default=1,
                    help="how many runs per scenario to count (the zero-shot "
                         "reference holds 3; pass corpora hold 1)")
    ap.add_argument("--label", default="")
    ap.add_argument("--min-strict", type=float, default=MIN_STRICT)
    ap.add_argument("--max-fp", type=float, default=MAX_FP_PER_RUN)
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args(argv)

    truth = Path(a.truth)
    run_dir = Path(a.run_dir)
    if not run_dir.is_dir():
        print(f"no such run dir: {run_dir}", file=sys.stderr)
        return 2
    keep = split_ids(a.split)
    agg = aggregate(run_dir, truth, keep=keep, max_run=a.runs)
    agg["split"] = a.split
    ref = None
    if a.reference:
        ref_dir = Path(a.reference)
        if ref_dir.is_dir():
            ref = aggregate(ref_dir, truth, keep=keep, max_run=a.runs)
            ref["split"] = a.split
        else:
            print(f"(reference {ref_dir} missing — strata comparison skipped)",
                  file=sys.stderr)
    checks = evaluate(agg, ref, a.min_strict, a.max_fp)
    verdict = report(agg, checks, ref, a.label or run_dir.name, a.split)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(
            {"corpus": agg, "reference": ref, "checks": checks, "freeze": verdict},
            indent=2, default=str))
        print(f"wrote {a.json_out}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
