#!/usr/bin/env python3
"""rebuild_index.py — regenerate summary.md (and the scenario list in meta.json)
from the run records, after a PARALLEL sweep.

Why this is needed: the runner rewrites `zero_shot/summary.md` and
`zero_shot/meta.json` every time it finishes a scenario. With N workers running at
once the last writer wins, so the index would list only one scenario even though
every answer is on disk. The per-run records (`sc-XXXX_runNN.json`) are the
authoritative data — scoring reads those — and this script only repairs the
human-facing index on top of them.

    python3 scripts/rebuild_index.py --out xam_q36 --runs 3
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=3)
    a = ap.parse_args()

    zero = Path("results") / a.out / "zero_shot"
    runs: dict[str, list] = defaultdict(list)
    for f in sorted(glob.glob(str(zero / "sc-*_run*.json"))):
        try:
            r = json.loads(Path(f).read_text())
        except Exception:
            continue
        runs[r["scenario_id"]].append(r)
    if not runs:
        print(f"no run records under {zero} — nothing to rebuild")
        return 1

    # provenance from any one record (identical across workers by construction)
    any_rec = next(iter(runs.values()))[0]
    meta_p = zero / "meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.is_file() else {}
    valid = lambda r: bool(r.get("content")) and not r.get("error")  # noqa: E731

    lines = [
        f"# Zero-shot probe — run {a.out}  (index regenerated after a PARALLEL sweep)",
        f"model={any_rec.get('model')} endpoint={meta.get('base_url','')} "
        f"temp={any_rec.get('temperature')} seed={any_rec.get('seed')} runs={a.runs}",
        f"sampling: {json.dumps(any_rec.get('sampling'))} · max_tokens: not sent · "
        f"stateless per-call context",
        f"dataset fingerprint: {meta.get('dataset_fingerprint','')}",
        "",
        "note: this corpus was produced with CONCURRENT requests (batched decode). "
        "The serving configuration differs from a single-slot run; see the sweep log.",
        "",
    ]
    n_ok = n_err = 0
    for sid in sorted(runs):
        rs = runs[sid]
        ok = sum(1 for r in rs if valid(r))
        err = sum(1 for r in rs if r.get("error"))
        bad = sum(1 for r in rs if not valid(r) and not r.get("error"))
        n_ok += ok
        n_err += err
        flag = "" if ok >= a.runs else "   <-- INCOMPLETE"
        lines.append(f"## {sid}  ({ok}/{a.runs} runs ok"
                     + (f", {err} error, {bad} unusable" if (err or bad) else "")
                     + f"){flag}")
        lines.append("")
    lines.insert(6, f"TOTAL: {n_ok}/{len(runs) * a.runs} answers banked across "
                    f"{len(runs)} scenario(s); {n_err} errored record(s)")
    lines.insert(7, "")
    (zero / "summary.md").write_text("\n".join(lines))

    # meta.json keeps only the last scenario's name; restore the full list
    meta.setdefault("run_id", a.out)
    meta["scenarios"] = sorted(runs)
    meta["index_regenerated_by"] = "scripts/rebuild_index.py (parallel sweep)"
    meta_p.write_text(json.dumps(meta, indent=2))
    print(f"rebuilt {zero/'summary.md'} and meta.json scenario list: "
          f"{len(runs)} scenario(s), {n_ok}/{len(runs)*a.runs} answers banked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
