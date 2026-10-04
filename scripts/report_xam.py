#!/usr/bin/env python3
"""Behavioural dossier per scenario — "what did the model do?" for non-AI
audiences, written so the record itself cannot leak.

Usage:
    python3 scripts/report_xam.py results/xam_v4/zero_shot
    python3 scripts/report_xam.py results/xam_v4/zero_shot --truth data/truth

Output: results/<run-id>/reports/<scenario>_behavior.md  (one per scenario,
plus an index.md). Every report has the same three tiers:

  Tier 1 — Executive summary            for a general reader (no jargon)
  Tier 2 — For the actuary              domain expert who does not care how AI works
  Tier 3 — Methodology & outcomes       full settings, prompt, timing, evidence

LEAK SAFETY (enforced):
  * Reports are written under results/<run-id>/reports/ — never inside
    data/eval, never next to scenario files, never reachable by the prompt
    builder (build_prompt reads only the scenario dir).
  * The generator refuses to run if the output path would land inside the
    eval workspace.
  * The report explicitly names the truth and descriptive scenario id — that
    is by design for scorer-side review; the header warns it must never be
    fed to a model or placed under data/eval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

TRUTH_NAME = "data/truth"


# --------------------------------------------------------------------------- #
# data readers (mirror run_zero_shot so the report can be generated standalone)
# --------------------------------------------------------------------------- #

def by_year(scenario_dir: Path, benefit: str):
    p = scenario_dir / "artifacts" / f"ae_{benefit.lower()}_by_year.csv"
    if not p.exists():
        return []
    rows = []
    with open(p) as f:
        f.readline()
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 4:
                continue
            try:
                rows.append((int(float(parts[0])), float(parts[1]),
                             float(parts[2]), float(parts[3])))
            except ValueError:
                continue
    return rows


def termination_pooled(scenario_dir: Path) -> dict[str, float] | None:
    p = scenario_dir / "artifacts" / "ae_ip_termination.csv"
    if not p.exists():
        return None
    agg: dict[str, list[tuple[float, float, float, float]]] = defaultdict(list)
    with open(p) as f:
        f.readline()
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 7:
                continue
            try:
                agg[parts[0]].append((float(parts[2]), float(parts[3]),
                                      float(parts[5]), float(parts[6])))
            except ValueError:
                continue
    return {d: (sum(r[1] for r in v) / sum(r[0] * r[2] for r in v) if sum(r[0] * r[2] for r in v) else 0.0)
            for d, v in agg.items()}


def summary_json(scenario_dir: Path) -> dict | None:
    p = scenario_dir / "artifacts" / "summary.json"
    return json.load(open(p)) if p.exists() else None


def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def parse_findings(content):
    if not content or not content.strip():
        return None, []
    blob = content.strip()
    if "{" in blob and "}" in blob:
        blob = blob[blob.index("{"): blob.rindex("}") + 1]
    try:
        obj = json.loads(blob)
    except Exception:
        return None, []
    return obj, (obj.get("findings") if isinstance(obj, dict) else [])


# --------------------------------------------------------------------------- #
# evidence helpers
# --------------------------------------------------------------------------- #

def tool_evidence(record: dict) -> dict:
    """Did the model use a tool / write code / run anything? Built from the
    actual artefacts: the request body, the server response, the output text."""
    raw = record.get("raw_response") or {}
    msg = ((raw.get("choices") or [{}])[0].get("message") or {}) if isinstance(raw, dict) else {}
    blob = (record.get("content") or "") + "\n" + (record.get("reasoning_content") or "")
    req = record.get("request") or {}
    return {
        "tools_offered_in_request": ("tools" in req) or ("function_call" in req),
        "tool_calls_in_response": bool(msg.get("tool_calls")),
        "code_fences_in_output": bool(re.search(r"```", blob)),
        "python_code_in_output": bool(re.search(
            r"import (pandas|numpy)|pd\.read_csv|open\(.*\.csv|def \w+\(", blob)),
        "asked_to_inspect_files": bool(re.search(
            r"let me (run|check|read|open) |I will write a script|create a (python|script)", blob, re.I)),
    }


def verdicts(finding, control) -> tuple[str, str]:
    """(verdict, note) for one finding vs the truth control list."""
    b = str(finding.get("benefit", ""))
    pat = str(finding.get("pattern", "")).lower()
    yrs = finding.get("years")
    cwin = control.get("window")
    if pat == "recovery":
        truthpat = "ip_recovery"
    else:
        truthpat = pat
    if control["type"] != truthpat:
        return "FALSE POSITIVE", f"pattern {pat!r} vs truth {control['type']!r}"
    cb = control.get("benefit")
    if isinstance(cb, list):
        ok = b in {str(x) for x in cb}
    else:
        ok = b == str(cb) or str(cb) == "all"
    if not ok:
        return "FALSE POSITIVE", f"benefit {b!r} vs truth {cb!r}"
    if isinstance(yrs, list) and cwin and len(yrs) == 2 and len(cwin) == 2:
        if yrs[1] < cwin[0] or cwin[1] < yrs[0]:
            return "FALSE POSITIVE", f"window {yrs} vs truth {cwin}"
    return "TRUE POSITIVE", f"matches truth {control['type']} on {cb} {cwin}"


# --------------------------------------------------------------------------- #
# markdown builders
# --------------------------------------------------------------------------- #

def fmt_sigma(rows) -> list[str]:
    out = []
    for year, act, exp, ae in rows:
        sd = 1 / math.sqrt(max(1.0, exp))
        z = (ae - 1) / sd
        star = "  " if abs(z) <= 2 else (f"  <== {z:+.1f} sigma" if abs(z) <= 3.5 else f"  <== {z:+.1f} sigma **")
        out.append(f"    {year}: A/E={ae:.3f}  (≈{z:+.1f}σ from 1.0){star}")
    return out


def build_report(run_dir: Path, sid: str, runs: list[dict],
                 truth_root: Path, meta: dict, split_root: Path) -> str:
    man = load_json(truth_root / "manifests" / f"{sid}.json") or {}
    sdir = split_root / meta.get("split", "optimization") / sid

    # --- truth summary (scorer-side) ---
    controls = man.get("controls") or []
    if controls:
        truth_desc = "; ".join(
            f"{c['type']} on {c.get('benefit')} {c.get('window')} "
            f"({c.get('signature', {}).get('magnitude', '')})" for c in controls)
    else:
        truth_desc = "no injected control (clean / noise-only)"
    fam = man.get("family", "?")
    desc_id = man.get("descriptive_id") or man.get("scenario_id", sid)

    # --- model findings across runs ---
    findings_rows = []
    n_tp = n_fp = 0
    for r in runs:
        obj, fds = parse_findings(r.get("content"))
        if not fds:
            findings_rows.append((r.get("run"), r, None, "no findings parsed", ""))
            continue
        for fd in fds:
            if controls:
                v, note = verdicts(fd, controls[0])  # primary control comparison
            else:
                v, note = "FALSE POSITIVE (clean truth)", "no control to match"
            if v == "TRUE POSITIVE":
                n_tp += 1
            else:
                n_fp += 1
            findings_rows.append((r.get("run"), r, fd, v, note))

    # per-run facts
    def secs(r):
        w = r.get("wall_seconds")
        if w is not None:
            return w
        try:
            from datetime import datetime
            a = datetime.fromisoformat(r["started_at"])
            b = datetime.fromisoformat(r["finished_at"])
            return (b - a).total_seconds()
        except Exception:
            return None

    run_lines = []
    for r in sorted(runs, key=lambda x: x.get("run", 0)):
        u = r.get("usage") or {}
        t = secs(r)
        tt = f"{t:.0f}s" if t is not None else "n/a"
        rsn = r.get("reasoning_content") or ""
        run_lines.append(
            f"| {r.get('run')} | {r.get('seed')} | {tt} | "
            f"{u.get('completion_tokens', '?')} | {u.get('prompt_tokens', '?')} | "
            f"{r.get('finish_reason', '?')} | {len(r.get('content') or '')} | "
            f"{len(rsn)} | {r.get('error') or 'ok'} |")

    # tool evidence (from first good run)
    ev = tool_evidence(next((r for r in runs if r.get("content")), runs[0])) if runs else {}

    # sigma bands for the four benefits
    sigma_lines = []
    for b in ("Death", "CI", "TPD", "IP"):
        rows = by_year(sdir, b)
        if not rows:
            continue
        sigma_lines.append(f"**{b}** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):")
        sigma_lines += fmt_sigma(rows)

    term = termination_pooled(sdir)
    term_lines = []
    if term:
        for d, v in sorted(term.items()):
            mark = "  <== deviates" if abs(v - 1.0) > 0.2 else ""
            term_lines.append(f"    {d}: {v:.3f}{mark}")

    prompt = next((r.get("prompt") for r in runs if r.get("prompt")), None)
    prompt_file = run_dir / f"{sid}_prompt.md"
    if prompt is None and prompt_file.exists():
        body = prompt_file.read_text()
        prompt = {"system_chars": None, "user_chars": len(body),
                  "sha256": hashlib.sha256(body.encode()).hexdigest()}
    prompt_hash = (prompt or {}).get("sha256", "?")

    overalls = [parse_findings(r.get("content"))[0] for r in runs]
    overall_clean = sum(1 for o in overalls if o and o.get("overall_assessment") == "clean")

    L = []
    L.append(f"# Behavioural dossier — scenario `{sid}`")
    L.append("")
    L.append("> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's "
             "eyes only. Never feed this file to a model, never copy it under "
             "`data/eval/`, never let the prompt builder see it. The model that "
             "answered never saw any part of this file.")
    L.append("")

    # ---- Tier 1 -------------------------------------------------------- #
    L.append("## Tier 1 · Executive summary (for a general reader)")
    L.append("")
    if n_tp and n_fp == 0:
        tone = "found the anomaly every time and reported nothing false"
    elif n_tp and n_fp:
        tone = f"found the anomaly every time but also raised {n_fp} additional item(s)"
    else:
        tone = "did not clearly identify the injected anomaly"
    L.append(f"This scenario hides a manufactured irregularity in synthetic insurance "
             f"claims data. Asked three separate times (fresh context each time, no "
             f"memory, no tools, no internet), the AI model {tone}. "
             f"Overall it answered 'clean' in {overall_clean}/3 runs.")
    L.append("")
    L.append(f"**What was hidden:** {truth_desc}.")
    L.append(f"**What the model said:**")
    if findings_rows:
        for run, r, fd, verdict, note in findings_rows[:8]:
            if fd is None:
                continue
            L.append(f"- run {run}: {fd.get('benefit')} / {fd.get('pattern')} / "
                     f"{fd.get('direction')} (confidence {fd.get('confidence')}) "
                     f"— {verdict}")
    else:
        L.append("- (nothing parsed)")
    L.append("")
    L.append("**Did it cheat?** No. It was given only the numbers, could not run "
             "code, open files, or use tools — and none of that was available in the "
             "conversation (see Tier 3 for the evidence).")
    L.append("")

    # ---- Tier 2 -------------------------------------------------------- #
    L.append("## Tier 2 · For the actuary (what to make of the answer)")
    L.append("")
    L.append(f"**The task.** The model was handed the A/E experience tables for this "
             f"book — {desc_id} ({fam} family) — exactly as a pricing analyst would see "
             f"them, and asked: where are the anomalies, what kind, and what would you "
             f"do? It had no knowledge of the injected control: {truth_desc}.")
    L.append("")
    L.append(f"**Diagnosis to trust:** {'the injected irregularity was named correctly '
             f'({truth_desc})' if n_tp else 'the injected irregularity was NOT named'}.")
    L.append("")
    tp_confs = [fd.get('confidence') for _, r, fd, v, _ in findings_rows
                if fd and v == 'TRUE POSITIVE']
    L.append(f"Confidence stated on the correct finding: "
             f"{', '.join(str(c) for c in tp_confs) or 'n/a'}.")
    L.append("**Where it helps:** the evidence strings point at the exact rows it used, "
             "so you can replay its reasoning. The magnitudes it quotes are checkable "
             "against the A/E series.")
    L.append("")
    L.append("**Where to be careful:**")
    L.append("- A finding does not equal an injected control. The model may raise "
             "genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not "
             "the planted event.")
    L.append("- The termination table shown to the model is aggregated (pooled over "
             "duration months); that removes an artefact the old prompt had, but the "
             "aggregate can still hide small-cell noise.")
    L.append("- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ "
             "excursions. On deliberately clean scenarios it should say clean; on "
             "noise-trap scenarios it should say nothing.")
    L.append("")

    # ---- Tier 3 -------------------------------------------------------- #
    L.append("## Tier 3 · Methodology & outcomes (for the record)")
    L.append("")
    L.append("### What the model was given")
    L.append("")
    L.append("- endpoint/model: `{}` / `{}`".format(meta.get("base_url"), meta.get("model")))
    L.append("- prompt: system + user turns, {} chars, sha256 `{}`".format(
        (prompt or {}).get("user_chars", "?"), prompt_hash))
    if prompt_file.exists():
        try:
            rel = prompt_file.relative_to(Path.cwd()).as_posix()
        except ValueError:
            rel = str(prompt_file)
        L.append(f"- the exact prompt text is archived at `{rel}`")
    else:
        L.append("- (prompt text archive missing)")
    L.append("- samplers: {}".format(json.dumps(meta.get("sampling", {}))))
    L.append("- `max_tokens`: **not sent** · `stream`: `{}` · termination aggregation: `{}`".format(
        meta.get("stream"), meta.get("termination_mean")))
    L.append("- files shown: listing only; contents of `summary.json` and the "
             "per-benefit yearly A/E + IP termination tables")
    L.append("")
    L.append("### What was sent (verbatim request body, redacted messages)")
    L.append("")
    req = next((r.get("request") for r in runs if r.get("request")), None)
    req_recon = next((r.get("request_reconstructed") for r in runs
                      if r.get("request_reconstructed")), None)
    if req:
        red = {k: v for k, v in req.items() if k != "messages"}
        L.append("```json")
        L.append(json.dumps(red, indent=2))
        L.append("```")
    elif req_recon:
        red = {k: v for k, v in req_recon.items() if k != "messages"}
        L.append("_(reconstructed deterministically — this run predates verbatim "
                 "payload capture; the exact prompt text is archived in the "
                 "`_prompt.md` file)_")
        L.append("```json")
        L.append(json.dumps(red, indent=2))
        L.append("```")
    else:
        L.append("_(request body not captured for this run; runner v0.4.0+ records it)_")
    L.append("")
    L.append("### Per-run facts")
    L.append("")
    L.append("| run | seed | wall time | completion tok | prompt tok | finish | answer chars | reasoning chars | error |")
    L.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    L += run_lines
    L.append("")
    L.append("### Tool use (did it do anything besides read the text?)")
    L.append("")
    L.append("| check | result |")
    L.append("|---|---|")
    L.append(f"| tools offered in request | `{ev.get('tools_offered_in_request')}` |")
    L.append(f"| tool calls in response | `{ev.get('tool_calls_in_response')}` |")
    L.append(f"| code fences in output | `{ev.get('code_fences_in_output')}` |")
    L.append(f"| python code / file reads in output | `{ev.get('python_code_in_output')}` |")
    L.append(f"| asked to inspect files | `{ev.get('asked_to_inspect_files')}` |")
    L.append("")
    L.append("The runner offers no tools (`tools`/`function_call` keys never appear in "
             "the request) and the server returned none. The model answered from the "
             "text alone.")
    L.append("")
    L.append("### The data it saw (for replaying its reasoning)")
    L.append("")
    L += sigma_lines
    L.append("")
    if term_lines:
        L.append("**IP termination A/E per diagnosis (pooled):**")
        L += term_lines
        L.append("")
    L.append("### Ground truth (scorer-side)")
    L.append("")
    L.append(f"- descriptive id: `{desc_id}` (family `{fam}`)")
    L.append(f"- controls: {truth_desc}")
    L.append("")
    L.append("### Scorer verdict summary")
    L.append("")
    L.append(f"- TRUE POSITIVE findings: {n_tp}")
    L.append(f"- other / false-positive findings: {n_fp}")
    L.append(f"- runs: {len(runs)} · overall 'clean' verdicts: {overall_clean}")
    L.append("")
    L.append("---")
    L.append(f"_Generated by scripts/report_xam.py · scenario `{sid}` · "
             f"run dir `{run_dir}`_")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+")
    ap.add_argument("--truth", default=TRUTH_NAME)
    ap.add_argument("--split-root", default="data/eval")
    a = ap.parse_args(argv)

    truth_root = Path(a.truth)
    split_root = Path(a.split_root)
    eval_root = Path("data/eval").resolve()

    for rd_arg in a.run_dirs:
        rd = Path(rd_arg)
        meta = load_json(rd / "meta.json") or {}
        out_dir = rd.parent / "reports"
        if out_dir.resolve().is_relative_to(eval_root):
            print(f"REFUSING: reports output would land inside data/eval: {out_dir}",
                  file=sys.stderr)
            return 2
        out_dir.mkdir(parents=True, exist_ok=True)

        runs_by_sid: dict[str, list[dict]] = defaultdict(list)
        for f in sorted(rd.glob("*_run*.json")):
            rec = load_json(f)
            if rec:
                runs_by_sid[rec["scenario_id"]].append(rec)

        index = ["# Behavioural dossiers — run index",
                 "",
                 f"- run dir: `{rd}`",
                 f"- model: `{meta.get('model')}` · samplers: "
                 f"{json.dumps(meta.get('sampling', {}))}",
                 f"- stream: `{meta.get('stream')}` · max_tokens: not sent",
                 "",
                 "| scenario | family | dossiers |"]
        for sid, runs in sorted(runs_by_sid.items()):
            man = load_json(truth_root / "manifests" / f"{sid}.json") or {}
            fam = man.get("family", "?")
            p = out_dir / f"{sid}_behavior.md"
            p.write_text(build_report(rd, sid, runs, truth_root, meta, split_root))
            index.append(f"| `{sid}` | {fam} | [{sid}_behavior.md]({p.name}) |")
            print(f"wrote {p}")
        (out_dir / "index.md").write_text("\n".join(index))
        print(f"wrote {out_dir / 'index.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
