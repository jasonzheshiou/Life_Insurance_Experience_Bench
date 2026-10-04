#!/usr/bin/env python3
"""Baseline runner: the ordinary runner, pinned to the ORIGINAL system prompt.

WHY THIS EXISTS
---------------
During the harness campaign the anomaly taxonomy inside run_zero_shot.py was
edited twice (v1.6b: the shock/volatility wording; v1.6d: the drift clause made
direction-symmetric). Those edits also changed the BASE prompt, so a fresh
baseline run would not be comparable with the archived Qwen3.8 baselines
(`results/xam_v4`, `results/xam_v5`) even though nothing about the task changed.

This wrapper restores the exact baseline system text for BASELINE runs while
leaving `run_zero_shot.py` untouched, so the frozen harness provenance recorded
for the optimization passes and the held-out exam stays valid. It patches the
module global before `main()` runs; `build_prompt()` reads that global at call
time, so every prompt built by this process uses the pinned text.

THE PINNED TEXT IS VERIFIED, NOT RETYPED
----------------------------------------
`data/prompts/system_v2_baseline.txt` was recovered from the archived prompt
snapshots (`results/xam_v5/zero_shot/sc-*_prompt.md`) and checked against the
per-run hashes stored in those run records: sha256(system + NUL + user)
reproduces the archived value for all 47 scenarios. Use
`scripts/verify_baseline_prompt.py` to re-check at any time.

USAGE — identical to the ordinary runner, e.g.
    python3 scripts/run_zero_shot_baseline_v2.py --scenarios all \
        --split optimization --runs 3 ... --out xam_q36
or through the sweep wrapper:
    MODEL=Qwen3.6-27B OUT=xam_q36 RUNS=3 \
      RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
      bash scripts/sweep_qwen27b.sh

OPTIONAL USE FOR A CONTROLLED HARNESS A/B
-----------------------------------------
`--harness full` passes straight through, so this wrapper can produce a harness
question that keeps the pinned baseline system prompt — useful if you ever want to
attribute an effect to the pack/rules ALONE, with the prompt held fixed. It was
verified working for that purpose (system prompt byte-identical to `xam_q36`,
3053 chars, sha256 54d6d5c2bc742919; leak scan clean on all 23 books).

It is deliberately NOT used as the *permanent* harness runner. There, the system
prompt is part of the harness under construction — as it was for Qwen3.8-27B,
whose prompt was edited during harness building (v1.6b/v1.6d). The policy for the
Qwen3.6-27B campaign is therefore:

  * PASS 1 runs through this wrapper, so the prompt is byte-identical to the one
    `xam_q36` (the 3.6 baseline) used and the first harness measurement isolates
    the pack + rules;
  * LATER PASSES may evolve the prompt freely. To do that, point
    PINNED_PROMPT_FILE at a 3.6-specific prompt file instead of editing
    `run_zero_shot.py` — editing the runner would break the byte-identity of the
    frozen v1.6e files that the 3.8 held-out exam and gate refer to (their
    snapshots remain the record either way).

    PINNED_PROMPT_FILE=data/prompts/system_q36_v2.txt \
      python3 scripts/run_zero_shot_baseline_v2.py --harness full ...

  If PINNED_PROMPT_FILE is unset, the xam_q36 baseline prompt is used.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_zero_shot as runner  # noqa: E402

DEFAULT_PROMPT = HERE.parent / "data" / "prompts" / "system_v2_baseline.txt"


def main() -> int:
    # PINNED_PROMPT_FILE lets a later pass swap in a model-specific prompt
    # (e.g. data/prompts/system_q36_v2.txt) without editing run_zero_shot.py,
    # which must stay byte-identical to the frozen v1.6e harness.
    prompt_file = Path(os.environ.get("PINNED_PROMPT_FILE") or DEFAULT_PROMPT)
    if not prompt_file.is_file():
        print(f"missing pinned prompt file: {prompt_file}", file=sys.stderr)
        return 2
    text = prompt_file.read_text()
    runner.SYSTEM_PROMPT = text
    print(f"[pinned-prompt] {prompt_file} ({len(text)} chars) — recorded in each run "
          f"as prompt.system_chars", file=sys.stderr)
    return runner.main()


if __name__ == "__main__":
    sys.exit(main())
