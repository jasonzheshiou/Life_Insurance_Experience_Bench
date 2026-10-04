#!/usr/bin/env python3
"""probe_tool_call.py — minimal test: can Qwen3.6-27B be made to emit a tool call?

WHY THIS EXISTS
---------------
Across three full harness passes (69 runs) Qwen3.6-27B made ZERO python tool
calls, even after the rules block was rewritten to ask for one. Its reasoning
traces show it is not blind to the offer: 23/23 runs quote the evidence pack and
22/23 the cross-line block, but only one run ever says the word "tool", and that
one says:

    "No tool calls needed as the evidence pack already gives z=-20.4 for Cancer"

That is clause 3b's own escape hatch ("if the pack answers the question, answer
immediately without any tool call") being quoted back as a reason to decline.
Hypothesis: the escape hatch does not merely permit skipping the tool, it hands
the model a ready-made justification for skipping it, and this model takes it
every time.

This script isolates that variable on a tiny task, so the test costs seconds of
prompt instead of a 17 KB harness prompt. It is NOT part of the benchmark: no
truth, no scoring, nothing written into results/ corpora.

    python3 scripts/probe_tool_call.py --variant escape
    python3 scripts/probe_tool_call.py --variant noescape --task easy

Variants (the ONLY difference between them is the closing clause):
    escape     the live clause-3b wording: answer immediately if you can
    noescape   efficiency asked for, but no permission to skip the tool
    mandatory  the tool call is required before answering
    none       no clause at all
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from run_zero_shot import extract_tool_request  # noqa: E402

BASE_URL = "http://192.168.1.59:8080/v1"
MODEL = "Qwen3.6-27B"

# 30 values, deliberately tedious to summarise by hand but trivial with a tool.
HARD = [1.02, 0.97, 1.11, 0.88, 1.31, 0.94, 1.07, 0.83, 1.19, 0.91,
        1.04, 0.99, 1.27, 0.86, 1.12, 0.95, 1.08, 0.81, 1.23, 0.93,
        1.01, 0.96, 1.15, 0.89, 1.29, 0.92, 1.06, 0.84, 1.21, 0.90]
EASY = [1.0, 2.0, 3.0, 4.0, 5.0]

CLAUSES = {
    "escape": ("Work efficiently: if the values above already answer the "
               "question, answer immediately without any tool call."),
    "noescape": ("Work efficiently and never spend more turns than the problem "
                 "needs."),
    "mandatory": ("Before answering you MUST use the tool at least once. Do not "
                  "answer from mental arithmetic."),
    "none": "",
}


def _build_core(variant: str, task: str) -> str:
    vals = HARD if task in ("hard", "provided") else EASY
    clause = CLAUSES[variant]
    if task == "provided":
        # Mirrors the real harness: the arithmetic is ALREADY done for the model,
        # exactly as the evidence pack does it. This is the condition clause 3b
        # names ("if the pack answers the question").
        sd = _population_sd(HARD)
        pack = (f"\nCOMPUTED EVIDENCE PACK (deterministic, from the values above; "
                f"trust over mental math)\n"
                f"  population standard deviation: {sd:.4f}\n"
                f"  mean: {sum(HARD)/len(HARD):.4f},  n: {len(HARD)}\n")
        q = ("Confirm or override the pack's population standard deviation. "
             "Give it rounded to 4 decimal places.")
        return (
            f"A small dataset is given below.\n\nvalues = {vals}\n\n{q}\n"
            f"{pack}\n"
            f"HARNESS MODE\n"
            f"1) You may compute anything else you need. To use the tool, reply "
            f"with ONLY a JSON object (no other text):\n"
            f'     {{"tool": "python", "code": "<python source as one JSON string>"}}\n'
            f"   The code runs with plain stdlib Python; its output is returned "
            f"verbatim. You get at most 4 tool calls.\n"
            f"2) When done - with or without tools - reply with ONLY the final "
            f"JSON:\n"
            f'     {{"answer": <number>}}\n'
            + (f"\n{clause}\n" if clause else "")
        )
    q = ("Compute the population standard deviation of these values and round "
         "it to 4 decimal places." if task == "hard"
         else "Compute the mean of these values.")
    return (
        f"A small dataset is given below.\n\n"
        f"values = {vals}\n\n"
        f"{q}\n\n"
        f"HARNESS MODE\n"
        f"1) You may compute anything you need. To use the tool, reply with ONLY "
        f"a JSON object (no other text):\n"
        f'     {{"tool": "python", "code": "<python source as one JSON string>"}}\n'
        f"   The code runs with plain stdlib Python; its output is returned "
        f"verbatim. You get at most 4 tool calls.\n"
        f"2) When done - with or without tools - reply with ONLY the final JSON:\n"
        f'     {{"answer": <number>}}\n'
        + (f"\n{clause}\n" if clause else "")
    )


def build_prompt(variant: str, task: str, pad: int = 0) -> str:
    """Core prompt, optionally padded with synthetic pack rows inserted between the
    task/pack and the HARNESS MODE block - the real layout, at the real size."""
    base = _build_core(variant, task)
    if pad <= 0:
        return base
    marker = "HARNESS MODE"
    i = base.find(marker)
    if i == -1:
        return base + _filler_pack(pad)
    return base[:i] + _filler_pack(pad) + "\n" + base[i:]


def _population_sd(xs) -> float:
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


def _filler_pack(n_lines: int) -> str:
    """Synthetic per-line statistics rows, shaped like the real evidence pack, to
    test whether prompt SIZE alone is what stops the model reaching for the tool.
    The real harness prompt is 17-18 KB with the pack sitting between the task and
    the HARNESS MODE block; this reproduces that layout without the real data."""
    out = ["", "PER-LINE EVIDENCE PROFILES (deterministic)"]
    for i in range(n_lines):
        out.append(
            f"\n[SYNTHETIC LINE {i:02d}] mean A/E 1.0{i % 10}3 | evidence profile: "
            f"no strong signal - judge from the yearly table and null-validity "
            f"columns\n"
            f"  trend: gradient {0.001 * i:+.4f}/yr, R2 0.{i % 9}7, total "
            f"{0.01 * i:+.3f}\n"
            f"  step: {0.02 * (i % 7):+.3f} at {2015 + i % 8} "
            f"(score {1.0 + 0.1 * (i % 20):.1f})\n"
            f"  YoY sd: empirical 0.0{100 + i % 800} vs Poisson 0.0305 -> "
            f"overdispersion x{1.0 + 0.01 * i:.2f} (Poisson null approximately "
            f"valid)\n"
            f"  longest run: {2 + i % 5}y up ({0.01 * i:+.3f}) | max 1yr jump "
            f"{0.05 + 0.001 * i:.3f}\n"
            f"  yearly: 2015:1.0{i % 9} 2016:0.9{i % 9} 2017:1.0{i % 9} "
            f"2018:0.9{i % 9} 2019:1.0{i % 9} 2020:0.9{i % 9} 2021:1.0{i % 9} "
            f"2022:0.9{i % 9} 2023:1.0{i % 9} 2024:0.9{i % 9}")
    return "\n".join(out) + "\n"


def load_prompt_md(path: str) -> tuple[str, str]:
    """Parse results/<corpus>/zero_shot/<sid>_prompt.md into (system, user).

    Lets the probe replay the REAL harness prompt for a book the model failed, so
    the failure can be reproduced in a single 5-minute call and then bisected -
    instead of guessing from a toy prompt."""
    import re
    t = Path(path).read_text()
    m = re.search(r"^## system\s*\n(.*?)^## user\s*\n(.*)\Z", t, re.S | re.M)
    if not m:
        raise SystemExit(f"could not parse system/user sections from {path}")
    return m.group(1).strip(), m.group(2).strip()


def call(prompt: str, timeout: int = 1800, system: str | None = None) -> dict:
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = json.dumps({
        "model": MODEL,
        "messages": msgs,
        "temperature": 1.0, "top_p": 0.95, "top_k": 20, "min_p": 0.0,
        "presence_penalty": 0.0, "repetition_penalty": 1.0,
        "stream": True,
    }).encode()
    req = urllib.request.Request(
        BASE_URL + "/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    content, reasoning, finish = [], [], None
    with urllib.request.urlopen(req, timeout=timeout) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue
            for ch in chunk.get("choices") or []:
                delta = ch.get("delta") or {}
                if delta.get("content"):
                    content.append(delta["content"])
                if delta.get("reasoning_content"):
                    reasoning.append(delta["reasoning_content"])
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
    text = "".join(content)
    return {"content": text, "reasoning": "".join(reasoning),
            "finish_reason": finish,
            "tool_request": extract_tool_request(text)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--variant", required=True, choices=sorted(CLAUSES))
    ap.add_argument("--task", default="hard", choices=["hard", "easy", "provided"])
    ap.add_argument("--pad", type=int, default=0, help="insert N synthetic pack blocks before HARNESS MODE")
    ap.add_argument("--prompt-md", default=None,
                    help="replay a real harness prompt: results/<corpus>/zero_shot/<sid>_prompt.md")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args(argv)

    system = None
    if a.prompt_md:
        system, prompt = load_prompt_md(a.prompt_md)
    else:
        prompt = build_prompt(a.variant, a.task, a.pad)
    out = call(prompt, system=system)
    req = out["tool_request"]
    reasoned = out["reasoning"].lower()
    print(f"variant={a.variant:<10} task={a.task:<5} prompt_chars={len(prompt)}")
    print(f"  finish_reason     : {out['finish_reason']}")
    print(f"  TOOL CALL EMITTED : {'YES' if req else 'no'}")
    if req:
        print(f"  code              : {req['code'][:160]!r}")
    print(f"  reasoning chars   : {len(out['reasoning'])}")
    print(f"  reasoning mentions 'tool': {'tool' in reasoned}   'python': {'python' in reasoned}")
    print(f"  content head      : {out['content'].strip()[:160]!r}")
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(
            {"variant": a.variant, "task": a.task, "prompt": prompt,
             "content": out["content"], "reasoning": out["reasoning"],
             "finish_reason": out["finish_reason"],
             "tool_call_emitted": bool(req)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
