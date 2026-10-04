#!/usr/bin/env python3
"""Byte-level leakage scanner for the model-facing eval workspace.

The eval workspace (data/eval/) must reveal NOTHING about which anomaly a
scenario contains. Every naming channel is a leak: folder names, the
scenario_id.txt content, strings embedded in CSVs/JSONs, PNG text metadata.

Scans three channels:
  * layout  — root must contain only optimization/, heldout/, dataset.json;
              every scenario directory must be a bare opaque token sc-<6 hex>
  * paths   — no banned token may appear in any path component
  * content — raw bytes of every text file, and the uncompressed metadata
              chunks (tEXt/iTXt/zTXt) of every PNG, searched case-
              insensitively for banned tokens (chunked, overlap-safe)

Banned tokens:
  * the anomaly-family vocabulary below
  * every descriptive scenario id CONTAINING "_" from the truth id map
    (single-word ids like "baseline" are innocent English words that occur
    legitimately in data content, so they are banned in PATHS only)

NOTE: "recovery" and "baseline" are deliberately NOT content-banned — they are
legitimate actuarial values ("Recovery/Return to Work" claim outcomes). Their
full scenario ids (ip_recovery_* etc.) remain banned verbatim.

Usage::

    python3 scripts/leakcheck.py                                  # data/eval + data/truth
    python3 scripts/leakcheck.py --root other/dir --id-map x.csv  # custom

Exit status: 0 clean · 1 leaks found · 2 usage error.
"""
from __future__ import annotations

import argparse
import csv
import re
import struct
import sys
from pathlib import Path

SCENARIO_ID_RE = re.compile(r"^sc-[0-9a-f]{6}$")
ALLOWED_ROOT = {"optimization", "heldout", "dataset.json"}

BANNED_WORDS = [
    # anomaly families / answer-bearing vocabulary
    "drift", "shock", "volatil", "noop", "no_op", "trap", "lookalike",
    "crisis", "covid", "cascade", "inverse", "aging", "diverge", "macro",
    "neutral", "sigma", "slope",
    # scorer-side artifacts must never appear inside the eval workspace
    "ground truth", "truth", "manifest", "scorer", "controls", "descriptive_id",
    "assumptions",
]


def _banned_tokens(descriptive_ids: list[str], include_single_word_ids: bool) -> list[str]:
    tokens = list(BANNED_WORDS)
    for sid in descriptive_ids:
        sid = sid.strip().lower()
        if not sid:
            continue
        if "_" in sid or include_single_word_ids:
            tokens.append(sid)
    return sorted(set(tokens))


def _png_meta_bytes(path: Path) -> bytes:
    """Return only the uncompressed metadata chunks of a PNG (skip IDAT: compressed
    image bytes are indistinguishable from noise and would beg for false hits)."""
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return data  # mislabeled file: scan it all
    out = bytearray()
    i = 8
    while i + 8 <= len(data):
        (length,) = struct.unpack(">I", data[i:i + 4])
        ctype = data[i + 4:i + 8]
        if ctype in (b"tEXt", b"iTXt", b"zTXt"):
            out += data[i + 8:i + 8 + length]
        if ctype == b"IEND":
            break
        i += 12 + length
    return bytes(out)


def _scan_bytes(haystack_lower: bytes, tokens: list[str]) -> list[str]:
    return [t for t in tokens if t.encode() in haystack_lower]


def load_descriptive_ids(id_map_path: Path) -> list[str]:
    """Descriptive scenario ids from a truth id_map.csv ([] when unavailable)."""
    if not Path(id_map_path).is_file():
        return []
    with open(id_map_path, newline="", encoding="utf-8") as fh:
        return [row["scenario_id"] for row in csv.DictReader(fh)]


def scan_text(text: str, descriptive_ids: list[str]) -> list[str]:
    """Banned tokens found in a text payload (e.g. a fully-built model prompt)."""
    hay = text.lower().encode("utf-8", "replace")
    return _scan_bytes(hay, _banned_tokens(descriptive_ids, include_single_word_ids=False))


def scan_eval(root: Path, descriptive_ids: list[str],
              scenarios: list[str] | None = None) -> list[tuple[str, str]]:
    """Return [(location, token), ...]. Empty list == clean.

    scenarios: optional list of scenario dirs RELATIVE to root
    (e.g. ["heldout/sc-1a2b3c"]) — restricts the (expensive) path+content scan
    to those subtrees; the layout check always covers the whole root.
    """
    hits: list[tuple[str, str]] = []
    content_tokens = _banned_tokens(descriptive_ids, include_single_word_ids=False)
    path_tokens = _banned_tokens(descriptive_ids, include_single_word_ids=True)

    if not root.is_dir():
        return [(str(root), "<missing root>")]

    # --- layout ---------------------------------------------------------- #
    for child in sorted(root.iterdir()):
        if child.name not in ALLOWED_ROOT:
            hits.append((child.name, "<unexpected root entry>"))
    for split_dir in (root / "optimization", root / "heldout"):
        if not split_dir.is_dir():
            hits.append((str(split_dir.relative_to(root)), "<missing split dir>"))
            continue
        for scen in sorted(split_dir.iterdir()):
            if not scen.is_dir():
                hits.append((str(scen.relative_to(root)), "<stray file in split dir>"))
            elif not SCENARIO_ID_RE.match(scen.name):
                hits.append((str(scen.relative_to(root)), "<non-opaque scenario dir>"))

    if scenarios is None:
        files = [f for f in sorted(root.rglob("*")) if f.is_file()]
    else:
        files = []
        for rel in scenarios:
            sub = root / rel
            if not sub.is_dir():
                hits.append((f"SCENARIO {rel}", "<scenario dir missing>"))
                continue
            files.extend(f for f in sorted(sub.rglob("*")) if f.is_file())

    # --- paths ------------------------------------------------------------ #
    for f in files:
        rel = f.relative_to(root).as_posix().lower()
        for tok in _scan_bytes(rel.encode(), path_tokens):
            hits.append((f"PATH {rel}", tok))

    # --- content ----------------------------------------------------------- #
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(root).as_posix()
        try:
            if f.suffix.lower() == ".png":
                for tok in _scan_bytes(_png_meta_bytes(f).lower(), content_tokens):
                    hits.append((f"CONTENT {rel}", tok))
                continue
            # chunked read with carry-over so tokens never split across chunks
            carry = b""
            with open(f, "rb") as fh:
                while True:
                    block = fh.read(1 << 20)
                    if not block:
                        break
                    hay = (carry + block).lower()
                    for tok in _scan_bytes(hay, content_tokens):
                        hits.append((f"CONTENT {rel}", tok))
                    carry = hay[-64:]
        except OSError as e:
            hits.append((f"READ {rel}", f"<unreadable: {e}>"))
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="data/eval", help="eval workspace to scan")
    ap.add_argument("--id-map", default="data/truth/id_map.csv",
                    help="truth id map csv providing descriptive scenario ids")
    args = ap.parse_args(argv)

    root = Path(args.root)
    id_map = Path(args.id_map)
    ids = load_descriptive_ids(id_map)
    if not ids and not root.is_dir():
        print(f"error: neither {root} nor {id_map} exists", file=sys.stderr)
        return 2

    hits = scan_eval(root, ids)
    if hits:
        print(f"LEAK CHECK FAILED: {len(hits)} hit(s) under {root}", file=sys.stderr)
        for where, tok in hits:
            print(f"  {where}: '{tok}'", file=sys.stderr)
        return 1
    n_files = sum(1 for f in root.rglob("*") if f.is_file())
    print(f"leak check: CLEAN — {n_files} files, 0 hits under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
