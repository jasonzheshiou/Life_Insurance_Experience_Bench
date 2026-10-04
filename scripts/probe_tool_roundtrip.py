#!/usr/bin/env python3
"""probe_tool_roundtrip.py — prove the FULL tool loop works for Qwen3.6-27B.

What this tests, and what it deliberately does NOT do
-----------------------------------------------------
Earlier probes only proved the model can EMIT a tool request. This one proves the
whole production loop closes: request -> sandboxed execution -> result fed back ->
final answer. It calls the runner's own run_harness_turns(), so the code path,
message format and sandbox are exactly what the benchmark uses - nothing is
reimplemented here.

It does NOT change the harness and does NOT force tool use in it. The harness
keeps its own wording and 3.6 stays free to answer without tools, which is what it
chooses on the real prompts. This is a capability test only, on a small task where
the arithmetic is genuinely worth delegating.

    python3 scripts/probe_tool_roundtrip.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import run_zero_shot as rz  # noqa: E402

BASE_URL = "http://192.168.1.59:8080/v1"
MODEL = "Qwen3.6-27B"
SAMPLING = {"top_p": 0.95, "top_k": 20, "min_p": 0.0,
            "presence_penalty": 0.0, "repetition_penalty": 1.0}

# 30 values whose population sd is not a mental-arithmetic answer.
VALUES = [1.02, 0.97, 1.11, 0.88, 1.31, 0.94, 1.07, 0.83, 1.19, 0.91,
          1.04, 0.99, 1.27, 0.86, 1.12, 0.95, 1.08, 0.81, 1.23, 0.93,
          1.01, 0.96, 1.15, 0.89, 1.29, 0.92, 1.06, 0.84, 1.21, 0.90]


def true_sd(xs) -> float:
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


def build_messages() -> list[dict]:
    user = (
        f"values = {VALUES}\n\n"
        "Compute the population standard deviation of these values and round it "
        "to 4 decimal places.\n\n"
        "HARNESS MODE\n"
        "1) You may compute anything you need. To use the tool, reply with ONLY a "
        "JSON object (no other text):\n"
        '     {"tool": "python", "code": "<python source as one JSON string>"}\n'
        "   The code runs with plain stdlib Python; its output is returned "
        "verbatim. You get at most 4 tool calls.\n"
        "2) When done - with or without tools - reply with ONLY the final JSON:\n"
        '     {"answer": <number>}\n'
    )
    return [{"role": "user", "content": user}]


def main() -> int:
    target = true_sd(VALUES)
    # A real artifacts dir, so the sandbox behaves exactly as in a benchmark run.
    artifacts = _HERE.parent / "data" / "eval" / "optimization" / "sc-d72b95" / "artifacts"
    if not artifacts.is_dir():
        print(f"missing artifacts dir: {artifacts}", file=sys.stderr)
        return 2

    msgs = build_messages()
    print(f"task: population sd of {len(VALUES)} values   (true = {target:.4f})")
    print(f"sandbox cwd: {artifacts}")
    print("-" * 68)

    out = rz.run_harness_turns(
        base_url=BASE_URL, api_key="", model=MODEL, messages=msgs,
        temperature=1.0, seed=1234, timeout=1800, sampling=SAMPLING,
        stream=True, artifacts_dir=artifacts, max_tool_calls=2)

    h = out.get("harness") or {}
    print(f"TOOL CALLS MADE : {h.get('tool_calls')}")
    print(f"TURNS           : {[(t.get('role'), t.get('tool')) for t in h.get('turns') or []]}")
    for i, tr in enumerate(h.get("transcript") or []):
        print(f"\n--- tool call {i+1} ---")
        print("code   :", tr["code"].strip().replace("\n", " ")[:180])
        print("result :", tr["result"].strip()[:180])
    content = rz.extract_content(out)
    print("\nFINAL ANSWER:")
    print(" ", content.strip()[:300])
    print("-" * 68)

    ok = False
    try:
        ans = json.loads(content.strip())
        got = float(ans.get("answer"))
        ok = abs(got - target) < 5e-4
        print(f"parsed answer = {got}   expected = {round(target, 4)}   match = {ok}")
    except Exception as exc:  # noqa: BLE001
        print(f"could not parse a numeric answer: {exc}")

    loop_closed = (h.get("tool_calls") or 0) > 0 and bool((h.get("transcript") or []))
    print()
    print("LOOP CLOSED (request -> execute -> result -> final answer):",
          "YES" if loop_closed else "no")
    print("ANSWER CORRECT:", "YES" if ok else "no")
    Path("results/logs/toolprobe/roundtrip.json").parent.mkdir(
        parents=True, exist_ok=True)
    Path("results/logs/toolprobe/roundtrip.json").write_text(json.dumps(
        {"true_sd": round(target, 4), "harness": h, "final_content": content},
        indent=2, default=str))
    return 0 if (loop_closed and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
