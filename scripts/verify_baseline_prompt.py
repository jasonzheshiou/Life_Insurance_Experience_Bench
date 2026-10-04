#!/usr/bin/env python3
"""Verify that a baseline run would send EXACTLY the archived baseline prompts.

Compares, for every scenario in both splits, the prompt that the pinned-baseline
runner would build against the per-run record stored in an archived corpus
(default: results/xam_v5, the Qwen3.8-27B baseline):

    sha256(system + NUL + user)  ==  record["prompt"]["sha256"]
    len(system) == record["prompt"]["system_chars"]
    len(user)   == record["prompt"]["user_chars"]

Exit 0 only if every scenario matches. No API calls.

    python3 scripts/verify_baseline_prompt.py            # vs xam_v5
    python3 scripts/verify_baseline_prompt.py --corpus xam_v4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_zero_shot as runner  # noqa: E402

PROMPT_FILE = HERE.parent / "data" / "prompts" / "system_v2_baseline.txt"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="xam_v5", help="archived corpus to compare against")
    ap.add_argument("--runs", type=int, default=1, help="which archived run to read")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if not PROMPT_FILE.is_file():
        print(f"missing pinned prompt: {PROMPT_FILE}", file=sys.stderr)
        return 2
    runner.SYSTEM_PROMPT = PROMPT_FILE.read_text()

    same = diff = missing = 0
    for split in ("optimization", "heldout"):
        for sdir in sorted((Path("data/eval") / split).glob("sc-*")):
            if not sdir.is_dir():
                continue
            sid = sdir.name
            sys_txt, user_txt = runner.build_prompt(sid, sdir, "full", "pooled")
            sha = hashlib.sha256((sys_txt + "\x00" + user_txt).encode()).hexdigest()
            rec_p = Path("results") / a.corpus / "zero_shot" / f"{sid}_run{a.runs:02d}.json"
            if not rec_p.exists():
                missing += 1
                continue
            rec = json.loads(rec_p.read_text())["prompt"]
            rec_rev = rec.get("revision", "(pre-v2 corpus: no revision field)")
            ok = (sha == rec["sha256"]
                  and len(sys_txt) == rec["system_chars"]
                  and len(user_txt) == rec["user_chars"]
                  and runner.PROMPT_REVISION == rec_rev)
            if ok:
                same += 1
            else:
                diff += 1
                print(f"  MISMATCH {sid}: sha {sha[:12]} vs {rec['sha256'][:12]}, "
                      f"system {len(sys_txt)} vs {rec['system_chars']}, "
                      f"user {len(user_txt)} vs {rec['user_chars']}, "
                      f"rev {runner.PROMPT_REVISION} vs {rec_rev}")
    total = same + diff
    print(f"baseline prompt check vs results/{a.corpus}: "
          f"{same}/{total} identical, {diff} different, {missing} not in that corpus")
    if not a.quiet and diff == 0:
        sys_txt, user_txt = runner.build_prompt(
            sorted((Path('data/eval/optimization')).glob('sc-*'))[0].name,
            sorted((Path('data/eval/optimization')).glob('sc-*'))[0], "full", "pooled")
        print(f"  system prompt: {len(sys_txt)} chars  sha256 {hashlib.sha256(sys_txt.encode()).hexdigest()[:16]}")
        print(f"  user prompt:   {len(user_txt)} chars (scenario data; scenario-specific)")
    return 0 if diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
