#!/usr/bin/env python3
"""harness_probe.py — 20-second live check that the harness path works.

Instead of a real scenario (≈16 min), this sends a trivial tool-loop task
("compute the mean of data.csv") through the SAME code path the harness uses:
streaming call -> tool-request parsing -> sandboxed python -> second turn ->
final JSON. Use it after any change to the runner/sandbox/endpoint, before
spending a real scenario run.

    python3 scripts/harness_probe.py [--model Qwen3.8-27B-Q8_0] [--base-url ...]

Exit 0 = the whole loop closed correctly; 1 = something in the path is broken.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import run_zero_shot as rz  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="Qwen3.8-27B-Q8_0")
    ap.add_argument("--base-url", default="http://192.168.1.59:8080/v1")
    ap.add_argument("--api-key", default="lm-studio")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args(argv)

    art = Path(tempfile.mkdtemp(prefix="probe_"))
    (art / "data.csv").write_text("v\n1\n2\n3\n4\n")

    system = "You are a precise assistant. Follow the tool protocol exactly."
    user = ('Use the python tool to compute the mean of the v column in data.csv. '
            'Then reply with ONLY this JSON: {"mean": <value>}\n'
            'To use the tool reply with ONLY: {"tool": "python", "code": "<source>"}\n'
            + rz.HARNESS_RULES)

    resp = rz.run_harness_turns(
        a.base_url, a.api_key, a.model,
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=1.0, seed=1234, timeout=a.timeout,
        sampling={"top_p": 0.95, "top_k": 20}, stream=True,
        artifacts_dir=art, max_tool_calls=2)

    h = resp.pop("harness")
    final = rz.extract_content(resp)
    print(f"model={a.model}  tool_calls={h['tool_calls']}  turns={len(h['turns'])}")
    for t in h["transcript"]:
        print("  code  :", (t["code"] or "").strip().replace("\n", " ⏎ ")[:120])
        print("  result:", (t["result"] or "").strip().replace("\n", " ⏎ ")[:120])
    print("final answer:", repr(final[:200]))
    print("usage:", resp.get("usage"))

    ok = h["tool_calls"] >= 1 and "2.5" in final
    print("PROBE:", "PASS" if ok else "FAIL (no tool call or wrong answer)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
