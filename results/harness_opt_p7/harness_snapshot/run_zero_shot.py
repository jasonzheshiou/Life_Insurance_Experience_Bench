#!/usr/bin/env python3
"""Ad-hoc zero-shot "insights" experiment runner for the Data Pipeline Arena.

Stage-1-style probe (BENCHMARK_IMPLEMENTATION_GUIDE.md §6), run manually before
M3 formalizes it: give an LLM ONLY the model-facing scenario artifacts and a goal,
and ask it to identify anomalies — where they are, what kind, and what to do.

Hard rules:
  * The prompt is built EXCLUSIVELY from the model-facing scenario dir
    (data/eval/<split>/<sc-id>/). Scenario dirs carry OPAQUE ids (sc-<6hex>):
    descriptive scenario names, ground truth (data/truth/manifests/,
    metadata.json) NEVER enter the prompt — by construction, not by convention.
  * No code execution, no sandbox: this is a plain chat-completions call to any
    OpenAI-compatible endpoint (default: local LM Studio).

Leakage is ENFORCED at runtime, not merely by layout. Before any API call a
preflight gate checks (scoped to the selected scenarios):
  1. opaque layout — every scenario dir must be sc-<6hex> and the workspace
     must carry dataset.json; the old descriptive data/split-style layout is
     refused outright;
  2. byte scan — scripts/leakcheck.py over the selected scenario subtrees:
     banned anomaly-family vocabulary and every descriptive scenario id from
     the truth id_map, in paths AND file contents (PNG text chunks included);
  3. prompt scan — the fully-built user prompt is itself scanned for banned
     tokens, guaranteeing what is SENT cannot name the answer;
  4. integrity — every file of the selected scenarios is re-hashed against
     data/eval/dataset.json, and its seal is compared against the sealed
     truth store (data/truth/seal.json). --no-verify skips only this step;
     the leak scan itself cannot be disabled.
Any problem aborts the run (exit 1) before touching the API; the verdict is
recorded in meta.json ("leak_check") and in summary.md.

Outputs land in results/<run-id>/zero_shot/:
  * <scenario>_runNN.json   raw API response per (scenario x run)
  * <scenario>_prompt.md    the exact prompt sent (once per scenario)
  * summary.md              run index + statuses (+ truth comparison with --show-truth)
  * meta.json               provenance: model, endpoint, seed, truth seal,
                            leak-check + integrity verdicts

Only stdlib is used (urllib + the stdlib-only sibling leakcheck.py), so it
runs on any Python >= 3.11.

EXAMPLES
--------
Full 47-scenario cross-examination (run the two splits in turn; there is no
--split all). --skip-existing makes the SAME command re-runnable: completed
runs (non-empty content, no error) are never re-sent to the API, so
re-running after any crash resumes exactly where the corpus stopped. Each
scenario gets --runs attempts at fresh seeds and --timeout bounds each call::

    python3 scripts/run_zero_shot.py --scenarios all --split optimization --detail full --termination-mean pooled --show-truth --base-url http://192.168.1.59:8080/v1 --model "Qwen3.8-27b" --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repetition-penalty 1.0 --timeout 3600 --runs 3 --stream --wait-for-endpoint 1800 --max-consecutive-failures 5 --skip-existing --out xam_v5
    python3 scripts/run_zero_shot.py --scenarios all --split heldout      --detail full --termination-mean pooled --show-truth --base-url http://192.168.1.59:8080/v1 --model "Qwen3.8-27b" --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repetition-penalty 1.0 --timeout 3600 --runs 3 --stream --wait-for-endpoint 1800 --max-consecutive-failures 5 --skip-existing --out xam_v5

Single scenario, prompt preview only (no API call)::

    python3 scripts/run_zero_shot.py --scenarios sc-00a3cb --detail full --dry-run

    v0.4.1 — the circuit breaker no longer trips on 404 model_not_found during
    model-swap windows.
    v0.4.2 — finish_reason=null / empty-content stream results are treated as
    retryable EmptyGeneration failures (in-call retry, recorded as error, and
    re-spent by --skip-existing) instead of silently saved as success stubs.
    v0.4.3 — the opt-in P2 schema patch (bounded-drift definition + Poisson
    overdispersion discipline) is ADOPTED as the only system prompt;
    PROMPT_REVISION ("v2") is recorded in meta.json and every run record, and
    the --prompt-patch flag is removed. Revision v1 (the entire xam_v4 corpus)
    survives only in results/xam_v4/prompts.
    v0.5.0 — HARNESS h1 (opt-in --harness full, default off = byte-identical
    zero-shot protocol): appends the deterministic evidence pack
    (scripts/stats_pack.py, leak-gated) to the user prompt and lets the model
    spend up to --tool-calls sandboxed python turns (cwd=artifacts/, stdlib,
    10 s cap) before answering. Full tool transcript recorded per run; usage
    summed across turns. xam_v4/xam_v5 corpora were produced with the harness
    OFF.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import leakcheck  # noqa: E402  stdlib-only sibling scanner

VERSION = "0.5.0"


class EmptyGeneration(RuntimeError):
    """Server closed the stream cleanly but produced no answer content.

    Observed repeatedly on the xam_v4 corpus (finish_reason=null, attempts_ok=1,
    error=None — a SILENT stub the runner used to count as OK). Treated as a
    retryable failure so the attempt loop retries it and a final empty result is
    recorded as an error (and re-spent by --skip-existing on resume)."""


class TruncatedStream(RuntimeError):
    """Stream ended without a proper finish_reason, or the answer is not JSON.

    Observed 2026-09-10 on the harness corpus: the local server restarted
    mid-generation, the SSE stream closed after ~11k reasoning chunks with
    finish_reason=null and zero usage, and the half-written JSON was banked as a
    successful run. All 141 xam_v4/xam_v5 runs ended with finish_reason="stop",
    so a missing finish_reason (or an unparseable answer) is an infrastructure
    failure, not model behaviour — retry it instead of saving it."""

BENEFITS = ["Death", "CI", "TPD", "IP"]
HARNESS_VERSION = "h1"   # evidence pack + sandboxed python tool loop (see --harness)
DEFAULT_BASE_URL = "http://192.168.1.59:8080/v1"   # local LM Studio
DEFAULT_MODEL = "Qwen3.8-27B"                       # override with --model
DEFAULT_SEED = 1234
DEFAULT_RUNS = 3
DEFAULT_TEMPERATURE = 1.0
DEFAULT_TIMEOUT = 180  # seconds per API call

SYSTEM_PROMPT = """You are an actuary reviewing synthetic life-insurance experience data for a
single book. The data covers four benefit lines: Death, CI (critical illness),
TPD (total permanent disability), and IP (income protection).

Key facts about this data:
- A/E = Actual claims / Expected claims. A clean (baseline) A/E is approximately
  1.0, with sampling noise of order 1/sqrt(expected claim count) per year.
- Anomalies, when present, are one of:
  * drift: a sustained year-over-year move in A/E over 2+ years. A drift does
    NOT have to continue to the last data year: a trend confined to a sub-window
    that later reverts toward baseline is STILL drift — a reversion at the end is
    not evidence against the trend that came before it. When reporting drift,
    set years to the FULL window of the trend INCLUDING the gentle early ramp
    years, and note the reversion (if any) in the evidence.
  * shock: an abrupt level change (spike or drop) WITHOUT a gradual build-up —
    flat-topped or single-year excursions. If the excursion moves year over year
    in ONE direction before it peaks or reverts — rising OR falling — prefer
    drift — UNLESS the computed evidence says the biggest single-year move
    EXCEEDS the net excursion of that window, which means the line is swinging
    around instead of holding a level: then the pattern is volatility, not drift.
  * volatility: an increase in year-to-year dispersion with an unchanged level.
    Use this whenever a line's own evidence says its swing exceeds its net level
    change, or when the CROSS-LINE block reports several lines swinging together
    across CONSECUTIVE years. A single-year coordinated swing is NOT this — that
    is what a book-wide shock looks like, so read it in the level rows instead.
    In the multi-year case report it for EVERY affected line over the shared
    years, and if you also believe that line shows a level change, give that a
    separate entry of its own rather than dropping either reading.
  * recovery: a change in IP termination/recovery rates for a specific diagnosis.
- Statistical discipline: before quoting any z-score or sigma computed under a
  Poisson (1/sqrt(E)) null for a benefit line, compare that line's empirical
  year-to-year standard deviation of A/E against the Poisson expectation. If the
  data is overdispersed (empirical SD materially larger), the Poisson null is
  invalid: describe the anomaly as volatility/dispersion rather than flagging
  individual years against the Poisson null, and never re-apply Poisson z-scores
  inside a window you have already identified as volatile.
- Random noise can LOOK like a trend or a spike. Be conservative: do not invent
  anomalies just to appear useful. If the data is consistent with noise, say so.

Your task:
1. Identify any anomalies or notable insights in the data you are given.
2. For each finding, say WHERE it is (benefit line, which years), WHAT kind of
   pattern it is, the direction and rough magnitude, how confident you are, the
   evidence you are relying on, and WHAT ACTION you would recommend
   (investigation steps, assumption review, pricing/valuation follow-up).
3. If you see nothing anomalous, say so explicitly.

Respond with ONLY a JSON object matching this shape (no prose outside it):

{
  "scenario_id": "<the scenario id you were given>",
  "overall_assessment": "clean" | "anomalies",
  "findings": [
    {
      "benefit": "Death" | "CI" | "TPD" | "IP",
      "years": [start_year, end_year] | null,
      "pattern": "drift" | "shock" | "volatility" | "recovery" | "other",
      "direction": "increase" | "decrease" | "dispersion",
      "magnitude": "free text, e.g. ~+0.10/yr, x1.5, sigma=0.3",
      "confidence": 0.0-1.0,
      "evidence": ["short, checkable: which file/rows support this"],
      "recommended_action": "what you would do next"
    }
  ]
}"""

# Prompt provenance. The anomaly-taxonomy and statistical-discipline clauses
# below (formerly the opt-in "patch P2", adopted 2026-09-05 after the xam_v4
# study — see results/xam_v4/reports/STUDY_SUMMARY.md) are now the ONLY system
# prompt. Revision history:
#   v1 = original taxonomy (one-liner drift/shock/volatility/recovery, no
#        dispersion discipline) — used for the ENTIRE xam_v4 corpus (141 runs,
#        Qwen3.8-Flash-Next); its exact text survives in results/xam_v4/*/prompts
#        and results/xam_v4/zero_shot/*.json.
#   v2 = current text (bounded-drift definition + Poisson-overdispersion rule).
# New corpora (xam_v5 onward) are prompt revision v2.
PROMPT_REVISION = "v2"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--scenarios", required=True,
                   help="comma-separated scenario ids, 'all', or a path to a file "
                        "with one id per line")
    p.add_argument("--split", choices=["optimization", "heldout"], default="heldout")
    p.add_argument("--split-root", default="data/eval",
                   help="opaque model-facing eval workspace (ZONE A)")
    p.add_argument("--truth-root", default="data/truth",
                   help="scorer-only truth store (ZONE B); used by --show-truth")
    p.add_argument("--base-url", default=os_env("ABENCH_BASE_URL", DEFAULT_BASE_URL))
    p.add_argument("--api-key", default=os_env("ABENCH_API_KEY", "lm-studio"))
    p.add_argument("--model", default=os_env("ABENCH_MODEL", DEFAULT_MODEL))
    p.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    p.add_argument("--top-p", dest="top_p", type=float, default=None,
                   help="nucleus sampling; omitted from the payload when unset")
    p.add_argument("--top-k", dest="top_k", type=int, default=None,
                   help="top-k sampling (llama.cpp extension); omitted when unset")
    p.add_argument("--min-p", dest="min_p", type=float, default=None,
                   help="min-p sampling (llama.cpp extension); omitted when unset")
    p.add_argument("--presence-penalty", dest="presence_penalty", type=float, default=None,
                   help="presence penalty; omitted when unset")
    p.add_argument("--repetition-penalty", dest="repetition_penalty", type=float, default=None,
                   help="repetition penalty (llama.cpp extension); omitted when unset")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--stream", action=argparse.BooleanOptionalAction, default=True,
                   help="stream the completion over SSE (--stream / --no-stream); "
                        "keeps a multi-minute generation from sitting on a silent socket")
    p.add_argument("--skip-existing", action="store_true",
                   help="resume: keep any <scenario>_runNN.json that already holds "
                        "content with no error, instead of calling the API again")
    p.add_argument("--wait-for-endpoint", type=int, default=0,
                   help="seconds to keep polling the endpoint before/between calls "
                        "(0 = do not wait); survives a server restart mid-sweep")
    p.add_argument("--max-consecutive-failures", type=int, default=3,
                   help="circuit breaker: abort the sweep after this many consecutive "
                        "API failures instead of burning the remaining calls")
    p.add_argument("--detail", choices=["compact", "full"], default="compact",
                   help="compact: by-year A/E series only; full: also age-gender "
                        "and IP termination tables")
    p.add_argument("--termination-mean", dest="termination_mean",
                   choices=["pooled", "unweighted"], default="pooled",
                   help="how --detail full aggregates IP termination A/E per "
                        "diagnosis; 'unweighted' reproduces the original as-shipped "
                        "behaviour, which manufactures phantom anomalies")
    p.add_argument("--out", default=None,
                   help="results/<run-id>/zero_shot; defaults to zs_<timestamp>")
    p.add_argument("--show-truth", action="store_true",
                   help="copy the scorer-only manifests into the output and append "
                        "a truth comparison section to summary.md (experimenter "
                        "side only - never sent to the model)")
    p.add_argument("--no-verify", action="store_true",
                   help="skip integrity verification only (file hashes vs "
                        "dataset.json, seal vs truth store). The leak scan "
                        "itself CANNOT be disabled.")
    p.add_argument("--dry-run", action="store_true",
                   help="build and print the prompts without calling any API")
    p.add_argument("--list-models", action="store_true",
                   help="list models served by the endpoint and exit")
    p.add_argument("--harness", choices=["off", "full"], default="off",
                   help="h1 harness: append the deterministic evidence pack "
                        "(scripts/stats_pack.py) to the user prompt AND allow "
                        "up to --tool-calls sandboxed python turns per run. "
                        "'off' keeps the pure zero-shot protocol byte-identical.")
    p.add_argument("--tool-calls", type=int, default=4,
                   help="max sandboxed python tool turns per run (harness on)")
    return p.parse_args(argv)


def os_env(name: str, default: str) -> str:
    import os
    return os.environ.get(name, default)


def resolve_scenarios(spec: str, split_root: Path, split: str,
                      truth_root: Path | None = None) -> list[str]:
    """Resolve --scenarios to opaque scenario dir names.

    Accepts sc-<6hex> ids, 'all', or (via the truth id map) the descriptive
    names from the docs. Descriptive names are translated to opaque ids here,
    so they never reach the prompt or the per-run output files.
    """
    if spec == "all":
        raw = sorted(d.name for d in (split_root / split).iterdir() if d.is_dir())
    elif Path(spec).is_file():
        raw = [ln.strip() for ln in Path(spec).read_text().splitlines()
               if ln.strip() and not ln.strip().startswith("#")]
    else:
        raw = [s.strip() for s in spec.split(",") if s.strip()]

    # translate descriptive names -> opaque ids when a truth map is available
    desc_to_eval: dict[str, str] = {}
    if truth_root is not None:
        id_map = truth_root / "id_map.csv"
        if id_map.is_file():
            import csv as _csv
            with open(id_map, newline="", encoding="utf-8") as fh:
                desc_to_eval = {r["scenario_id"]: r["eval_id"]
                                for r in _csv.DictReader(fh)}
    ids = [desc_to_eval.get(x, x) for x in raw]

    missing = [x for x in ids if not (split_root / split / x).is_dir()]
    if missing:
        sys.exit(f"error: scenario dirs not found under {split_root}/{split}/: {missing} "
                 f"(use opaque sc- ids, descriptive names resolvable via the truth id map, "
                 f"or 'all')")
    return ids


def read_by_year(scenario_dir: Path, benefit: str) -> list[tuple[int, float, float, float]] | None:
    """Return [(year, actual, expected, ae)] from artifacts/ae_<b>_by_year.csv."""
    path = scenario_dir / "artifacts" / f"ae_{benefit.lower()}_by_year.csv"
    if not path.exists():
        return None
    rows = []
    with open(path) as f:
        f.readline()  # header: Year,Actual,Expected,AE
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


def summarize_termination(scenario_dir: Path, how: str = "pooled") -> dict[str, float] | None:
    """Per-diagnosis termination A/E from artifacts/ae_ip_termination.csv.

    how="pooled" (default)  sum(Recovered) / sum(Exposed * AssumedRate) — the
      statistic the dataset itself publishes as `overall_termination_ae`
      (verified to 4 dp against summary.json), so low-exposure late-duration
      months cannot dominate.
    how="unweighted"  the plain mean of the per-month AE column, kept only so
      the original as-shipped behaviour stays reproducible. It is a known
      defect: 98 of 108 duration months have tiny exposure, which inflates a
      ground-truth-clean scenario to 1.544 for Injury/Accident where the pooled
      figure is 1.001 — a phantom anomaly handed to the model on a plate.
    """
    path = scenario_dir / "artifacts" / "ae_ip_termination.csv"
    if not path.exists():
        return None
    agg: dict[str, list[tuple[float, float, float, float]]] = {}
    with open(path) as f:
        f.readline()  # header: Diagnosis,DurationMonth,Exposed,Recovered,ObservedRate,AssumedRate,AE
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 7:
                continue
            try:
                diag = parts[0]
                exposed, recovered = float(parts[2]), float(parts[3])
                assumed, ae = float(parts[5]), float(parts[6])
            except (ValueError, IndexError):
                continue
            agg.setdefault(diag, []).append((ae, exposed, recovered, assumed))
    out: dict[str, float] = {}
    for diag, rows in sorted(agg.items()):
        if how == "unweighted":
            out[diag] = round(sum(r[0] for r in rows) / len(rows), 3)
        else:
            num = sum(r[2] for r in rows)
            den = sum(r[1] * r[3] for r in rows)
            out[diag] = round(num / den, 3) if den else 0.0
    return out


def build_prompt(scenario_id: str, scenario_dir: Path, detail: str,
                 termination: str = "pooled") -> tuple[str, str]:
    """Return (system, user). Reads ONLY model-facing files - never manifests."""
    lines: list[str] = []
    lines.append(f"Scenario: {scenario_id}")
    lines.append("")
    lines.append("Files available (paths are relative to the scenario folder):")
    for rel in sorted(p.relative_to(scenario_dir).as_posix()
                      for p in scenario_dir.rglob("*") if p.is_file()):
        lines.append(f"  - {rel}")
    lines.append("")

    summary = scenario_dir / "artifacts" / "summary.json"
    if summary.exists():
        lines.append("summary.json (overall A/E per benefit, claim counts):")
        lines.append(json.dumps(json.load(open(summary)), indent=2))
        lines.append("")

    for benefit in BENEFITS:
        rows = read_by_year(scenario_dir, benefit)
        if not rows:
            continue
        lines.append(f"artifacts/ae_{benefit.lower()}_by_year.csv — yearly (Actual, Expected, AE):")
        for year, actual, expected, ae in rows:
            lines.append(f"  {year}: Actual={actual:,.0f}  Expected={expected:,.0f}  AE={ae:.3f}")
        lines.append("")

    if detail == "full":
        term = summarize_termination(scenario_dir, termination)
        if term:
            if termination == "unweighted":
                lines.append("artifacts/ae_ip_termination.csv — mean termination A/E per "
                             "diagnosis (unweighted mean over duration months; 1.0 = baseline):")
            else:
                lines.append("artifacts/ae_ip_termination.csv — termination A/E per diagnosis "
                             "(pooled over duration months: sum(Recovered)/sum(Exposed x "
                             "AssumedRate), so small late-duration cells carry little weight; "
                             "1.0 = baseline recovery rate):")
            for diag, mean_ae in term.items():
                lines.append(f"  {diag}: {mean_ae:.3f}")
            lines.append("")

    lines.append(
        "Now analyse the data above. Report every anomaly or notable insight you find, "
        "and explicitly state when the data looks clean. Return ONLY the JSON object."
    )
    return SYSTEM_PROMPT, "\n".join(lines)


# --------------------------------------------------------------------------- #
# API (stdlib urllib; OpenAI-compatible chat completions)
# --------------------------------------------------------------------------- #

def _post_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _post_stream(url: str, api_key: str, payload: dict, timeout: int,
                 heartbeat: int = 0) -> dict:
    """Streaming (SSE) chat-completions call, reassembled into a normal
    chat.completion-shaped dict.

    Streaming matters here for two reasons: a single answer can take >15 min,
    and a silent 15-minute socket invites idle timeouts / connection resets;
    tokens flowing keep the connection honest. It also lets us report progress.
    `usage` is requested explicitly via stream_options.include_usage, otherwise
    SSE would never tell us the token counts.
    """
    hdrs = {"Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=hdrs, method="POST")
    content: list[str] = []
    reasoning: list[str] = []
    finish = None
    usage = None
    extra: dict = {}
    chunks = 0
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        ctype = (resp.headers.get("Content-Type") or "").lower()
        if "text/event-stream" not in ctype:      # server ignored `stream`
            body = json.load(resp)
            body["streamed"] = False
            return body
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line or line.startswith(":"):   # SSE keep-alive comment
                continue
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                ev = json.loads(data)
            except json.JSONDecodeError:
                continue
            chunks += 1
            if ev.get("usage"):
                usage = ev["usage"]
            for k in ("id", "model", "system_fingerprint", "timings", "created"):
                if ev.get(k) is not None:
                    extra[k] = ev[k]
            for ch in ev.get("choices") or []:
                delta = ch.get("delta") or {}
                if delta.get("content"):
                    content.append(delta["content"])
                rc = delta.get("reasoning_content")
                if rc:
                    reasoning.append(rc)
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
            if heartbeat and chunks % heartbeat == 0:
                print(f"    ... {chunks} chunks | content "
                      f"{sum(len(c) for c in content)} chars | "
                      f"{time.time() - t0:.0f}s", flush=True)
    out = {
        "id": extra.get("id"),
        "object": "chat.completion",
        "created": extra.get("created"),
        "model": extra.get("model"),
        "system_fingerprint": extra.get("system_fingerprint"),
        "choices": [{"index": 0,
                     "message": {"role": "assistant",
                                 "content": "".join(content),
                                 "reasoning_content": "".join(reasoning) or None},
                     "finish_reason": finish}],
        "usage": usage,
        "streamed": True,
        "sse_chunks": chunks,
    }
    if extra.get("timings"):
        out["timings"] = extra["timings"]
    return out


def list_models(base_url: str, api_key: str) -> None:
    url = base_url.rstrip("/") + "/models"
    data = _get_json(url, api_key, 30)
    for m in data.get("data", []):
        print(m.get("id"))


def _get_json(url: str, api_key: str, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def server_context_window(base_url: str, api_key: str) -> dict:
    """Read the server's declared context window for provenance.

    /props lives at the server root, not under /v1, so derive the root. The
    point of recording this is the "no token cap" guarantee: with no
    max_tokens sent, n_ctx is the only bound on completion length.
    """
    from urllib.parse import urlsplit
    parts = urlsplit(base_url)
    root = f"{parts.scheme}://{parts.netloc}"
    out: dict = {"n_ctx": None, "props_url": root + "/props"}
    for url in (root + "/props", base_url.rstrip("/") + "/props"):
        try:
            d = _get_json(url, api_key, 15)
            params = (d.get("default_generation_settings", {}) or {}).get("params", {})
            out["n_ctx"] = d.get("n_ctx") or params.get("n_ctx")
            out["default_max_tokens"] = params.get("max_tokens", params.get("n_predict"))
            out["total_slots"] = d.get("total_slots")
            break
        except Exception as e:
            out["error"] = repr(e)
    if out.get("n_ctx") is None:            # fall back to /slots
        try:
            s = _get_json(root + "/slots", api_key, 15)
            if isinstance(s, list) and s:
                out["n_ctx"] = s[0].get("n_ctx")
        except Exception as e:
            out.setdefault("slots_error", repr(e))
    if out.get("n_ctx") is not None:
        out.pop("error", None)
    return out


def wait_for_endpoint(base_url: str, api_key: str, wait_s: int,
                      log=print) -> bool:
    """Poll /models until the endpoint answers or the budget runs out.

    A llama.cpp server that is reloading a 100 GB GGUF refuses connections for
    minutes; without this the whole sweep burns its calls against a dead socket.
    """
    if wait_s <= 0:
        return True
    deadline = time.time() + wait_s
    attempt = 0
    while True:
        attempt += 1
        try:
            _get_json(base_url.rstrip("/") + "/models", api_key, 20)
            if attempt > 1:
                log(f"[endpoint] back after {attempt - 1} failed probe(s)")
            return True
        except Exception as e:
            if time.time() >= deadline:
                log(f"[endpoint] still down after {wait_s}s: {e!r}")
                return False
            time.sleep(min(30, max(5, deadline - time.time())))


def build_payload(model: str, messages: list[dict], temperature: float, seed: int,
                  sampling: dict | None = None, stream: bool = True) -> dict:
    """The exact JSON body sent to the model — built once so it can be recorded
    verbatim next to the answer (what we asked is as auditable as what we got).
    Deliberately NO max_tokens and NO tools/function-calling: the model is
    given text and nothing else — it cannot read files or run code.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
    }
    if sampling:
        payload.update({k: v for k, v in sampling.items() if v is not None})
        # llama.cpp spells the repetition penalty `repeat_penalty`; mirror the
        # caller's value under both spellings so the intent survives whichever
        # name the server honours (silently-unknown keys are ignored).
        if sampling.get("repetition_penalty") is not None:
            payload["repeat_penalty"] = sampling["repetition_penalty"]
    if stream:
        payload["stream"] = True
        # include_usage is what makes the final SSE event carry token counts;
        # nothing here caps the completion length.
        payload["stream_options"] = {"include_usage": True}
    return payload


def call_llm(base_url: str, api_key: str, model: str, messages: list[dict],
             temperature: float, seed: int, timeout: int,
             sampling: dict | None = None, stream: bool = True,
             payload_out: dict | None = None) -> dict:
    """One stateless chat-completions call.

    Isolation guarantees, in the order that matters:
      * exactly one system turn + one user turn — no conversation history is
        ever sent, so a run cannot see any earlier run or any outside session;
      * NO max_tokens / n_predict is ever sent, so the completion is bounded
        only by the server context window (n_ctx, see meta.json), not by us;
      * NO tools / function-calling is offered — the model gets numbers in
        text and cannot read files, run code, or call anything;
      * `stream` keeps tokens flowing for the whole (multi-minute) generation.

    `sampling` carries the optional sampler settings (top_p / top_k / min_p /
    presence_penalty / repetition_penalty); keys left unset are omitted so the
    server default applies rather than a value this script invented.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload = build_payload(model, messages, temperature, seed, sampling, stream)
    if payload_out is not None:
        payload_out.update(payload)
    if stream:
        return _post_stream(url, api_key, payload, timeout, heartbeat=200)
    return _post_json(url, api_key, payload, timeout)


def extract_content(response: dict) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return json.dumps(response)
    if isinstance(content, list):  # some servers return content parts
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part)
                       for part in content)
    return str(content)


# --------------------------------------------------------------------------- #
# harness h1: evidence pack + sandboxed python tool loop
# --------------------------------------------------------------------------- #

HARNESS_RULES = """
HARNESS MODE — you are not limited to eyeballing the tables above.

1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact
   CSVs) is appended at the end of this message. Trust its arithmetic over
   mental math, but the final judgement is yours: confirm or override its
   per-line heuristic verdicts.

2) You may compute anything else you need. To use the tool, reply with ONLY a
   JSON object (no other text, no <tool_call> tags, no function-call syntax):
     {"tool": "python", "code": "<python source as one JSON string>"}
   The code runs with the scenario's artifacts/ directory as cwd (open files
   by relative path, e.g. open("ae_death_by_year.csv")); plain stdlib Python
   (csv, math, statistics); 10 s limit; output is returned verbatim.
   You get at most 4 tool calls. NEVER write files or read outside artifacts/.

3) When done — with or without tools — reply with ONLY the final JSON object
   in the required shape. Do not put tool requests inside that final JSON.

3b) Work efficiently: the evidence pack already contains the arithmetic. At most
   TWO tool calls, and if the pack answers the question, answer immediately
   without any tool call. Never spend more turns than the problem needs.

3c) Books where several lines move together: when the CROSS-LINE block reports a
   coordinated move or coordinated swings over a run of consecutive years, treat
   it as ONE underlying event but report it for EVERY affected line — the output
   schema has no "all" benefit, so a four-line event needs four entries sharing
   the years. Do not tell four unrelated stories, and do not drop lines. This
   means one entry per affected line EVEN WHEN one line's own move is much
   smaller than the others, and even when you discuss the shared cause only once:
   an answer that names the largest line and merely mentions the others in prose
   is graded as having found only the largest line.

4) Discipline (these are scored):
   * Overdispersion is NOT a finding by itself. Report a dispersion
     finding only when the elevated year-to-year scatter is the material
     anomaly for that line (roughly x6 or more versus the Poisson expectation,
     with a level that stays flat). Mild overdispersion, and any line whose
     evidence profile says "no strong signal", must NOT be reported as a
     finding merely because its scatter is above Poisson. The one exception is
     the book-wide case: when the CROSS-LINE block reports several lines
     swinging together across consecutive years, that shared evidence stands on
     its own, and every affected line gets its dispersion entry even if that
     line's own ratio is below the x6 guide.
   * Use the pattern the evidence actually describes. A single-year deviation
     that reverts is a one-off change; a movement that builds and then flattens
     or runs on is a sustained move; a stretch where the line swings around
     without ever settling at a new level is dispersion. The schema's taxonomy
     above defines each pattern word. When a per-line note says the biggest
     single-year move EXCEEDS the net excursion, the evidence cannot separate a
     give-back ramp from an erratic stretch: give that line a dispersion entry
     AND keep the level-change reading as an entry of its own, so both readings
     are on the record (one entry of each kind per line, never two of the same).
   * A one-year wobble is only a finding if the year is genuinely extreme:
     require a Poisson z of about 4.5 or more for that year (A/E alone is
     misleading when the expected count is small). A single-year excursion
     around z 3 is the kind of thing ordinary books produce, so leave it out.
     Where a line's own scatter already exceeds Poisson, per-year z-scores are
     unreliable — then require a larger move, or describe the stretch as
     dispersion instead of claiming a one-off change.
   * Every entry in "findings" is a claim that something material happened and
     should be investigated. A favourable deviation (A/E materially BELOW
     expectation), a movement you have decided is ordinary, and any observation
     you are not claiming must not appear as its own entry — mention it in the
     evidence text of a finding you ARE making, or leave it out entirely.
     Listing an observation you are not claiming is scored as a false alarm.
   * Do not describe the same movement twice. If a line's final years reverse a
     movement you have already reported for that line, that reversal is part of
     the earlier event: say so inside that finding rather than adding a second
     entry for the same line.
   * Small cells are not evidence: age-band or duration-month A/E values rest
     on tiny expected counts and go extreme by chance. Never report a
     book-level anomaly from such a cell unless the same effect is visible in
     the by-year series or the pooled line.
   * Findings you considered and rejected for these reasons do not appear in
     the "findings" array at all.
"""


def extract_tool_request(text: str) -> dict | None:
    """Return {"code": ...} if the model's reply is a tool request, else None.

    Tolerant of code fences and surrounding prose: tries the whole reply first,
    then the outermost {...} slice. A reply is only treated as a tool request
    when it parses AND carries {"tool": "python", "code": <str>}, so a normal
    final answer (which also is JSON) is never mis-read as one.
    """
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1:]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    candidates = [t]
    a, b = t.find("{"), t.rfind("}")
    if 0 <= a < b:
        candidates.append(t[a:b + 1])
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("tool") == "python" \
                and isinstance(obj.get("code"), str):
            return {"code": obj["code"]}
    # The model sometimes answers in its own tool syntax, e.g.
    #   <tool_call> {"function": "code"} parameter= {"tool": "python", "code": "..."}
    # so a raw {"tool": "python"} is present but not as a standalone JSON object.
    # Recover the code string directly (it may be truncated — the caller still
    # gets a chance to run it).
    import re as _re
    m = _re.search(r'"tool"\s*:\s*"python".*?"code"\s*:\s*"((?:[^"\\]|\\.)*)"',
                   t, _re.S)
    if m:
        try:
            code = json.loads('"' + m.group(1) + '"')
        except Exception:
            code = None
        if code:
            return {"code": code}
    return None


def answer_parses_as_json(text: str) -> bool:
    """True when the reply is (or contains) a complete JSON object.

    Used to detect a stream that died mid-answer: the saved text looks like a
    finding but is cut off, and the scorer would call it `unparseable`."""
    if not text:
        return False
    t = text.strip()
    if t.startswith("```"):
        nl = t.find("\n")
        if nl != -1:
            t = t[nl + 1:]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    try:
        json.loads(t)
        return True
    except Exception:
        pass
    a, b = t.find("{"), t.rfind("}")
    if 0 <= a < b:
        try:
            json.loads(t[a:b + 1])
            return True
        except Exception:
            return False
    return False


def run_sandboxed_python(code: str, artifacts_dir: Path, timeout: int = 10) -> str:
    """Execute model-authored python with cwd=artifacts_dir, read-only intent,
    strict wall timeout. Output capped; never raises (returns text either way).
    """
    import subprocess
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            cwd=str(artifacts_dir), timeout=timeout,
            capture_output=True, text=True,
        )
        out = (proc.stdout or "")
        if proc.returncode != 0:
            err = (proc.stderr or "").strip().splitlines()
            out += "\n[error] " + (err[-1] if err else f"exit {proc.returncode}")
        if len(out) > 4000:
            out = out[:4000] + "\n[output truncated at 4000 chars]"
        return out or "[no output — print() something]"
    except subprocess.TimeoutExpired:
        return f"[error] code exceeded the {timeout}s limit"
    except Exception as e:  # never let the sandbox kill the run
        return f"[error] sandbox failure: {e!r}"


def run_harness_turns(base_url: str, api_key: str, model: str,
                      messages: list[dict], temperature: float, seed: int,
                      timeout: int, sampling: dict | None, stream: bool,
                      artifacts_dir: Path, max_tool_calls: int = 4) -> dict:
    """Harness h1 sequence: prompt (with evidence pack) -> model may request up
    to max_tool_calls sandboxed python turns -> final answer.

    Each turn is one chat-completions call with the full message list; the
    whole sequence is one experiment run (statelessness is preserved ACROSS
    runs, within a run the model legitimately holds a short working memory —
    that is what the harness is for). Returns the final response dict plus a
    turn log and summed usage.
    """
    msgs = [dict(m) for m in messages]
    turns, transcript, tool_calls = [], [], 0
    usage_sum = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    resp: dict = {}
    while True:
        resp = call_llm(base_url, api_key, model, msgs, temperature, seed, timeout,
                        sampling=sampling, stream=stream)
        content = extract_content(resp)
        u = resp.get("usage") or {}
        for k in usage_sum:
            usage_sum[k] += u.get(k) or 0
        req = extract_tool_request(content) if tool_calls < max_tool_calls else None
        turns.append({"role": "model", "chars": len(content),
                      "tool": bool(req),
                      "finish_reason": (resp.get("choices") or [{}])[0].get("finish_reason")})
        if not req:
            break
        tool_calls += 1
        result = run_sandboxed_python(req["code"], artifacts_dir)
        turns.append({"role": "tool", "code_chars": len(req["code"]),
                      "result_chars": len(result)})
        transcript.append({"model_asked": content[:4000], "code": req["code"],
                           "result": result})
        msgs.append({"role": "assistant", "content": content})
        msgs.append({"role": "user",
                     "content": "TOOL RESULT (python stdout/stderr):\n" + result +
                                "\n\nContinue: request another tool call (same JSON "
                                "form) or reply with ONLY the final JSON answer."})
    out = dict(resp)
    out["usage"] = usage_sum
    out["harness"] = {"version": HARNESS_VERSION, "tool_calls": tool_calls,
                      "turns": turns, "transcript": transcript}
    return out


def dataset_fingerprint(split_root: Path) -> str | None:
    """Truth seal from dataset.json (opaque layout); legacy summary fallback."""
    p = split_root / "dataset.json"
    if p.exists():
        try:
            return json.load(open(p)).get("seal")
        except Exception:
            return None
    p = split_root / "scenario_summary.json"  # legacy data/split layout
    if not p.exists():
        return None
    try:
        return json.load(open(p)).get("fingerprint")
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# preflight: leak scan + integrity gate
# --------------------------------------------------------------------------- #

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight_guards(args, scenarios: list[str],
                     prompts: dict[str, tuple[str, str]]) -> tuple[dict, list[str]]:
    """Run every leakage/integrity check BEFORE any API call.

    Returns (verdict_for_meta, problems). Non-empty problems -> the caller MUST
    refuse to run. Checks are scoped to the selected scenarios; only the
    (cheap) layout sweep covers the whole workspace.
    """
    split_root = Path(args.split_root)
    truth_root = Path(args.truth_root)
    problems: list[str] = []
    ids = leakcheck.load_descriptive_ids(truth_root / "id_map.csv")

    # 1) opaque layout: reject the old descriptive-style workspace outright
    for sid in scenarios:
        if not leakcheck.SCENARIO_ID_RE.match(sid):
            problems.append(
                f"{sid}: scenario dir is not an opaque sc-<6hex> id — this looks "
                f"like a leaky layout; rebuild with scripts/generate_scenarios.py")
    dataset_p = split_root / "dataset.json"
    if not dataset_p.exists():
        problems.append(f"{dataset_p}: missing — not an opaque eval workspace (ZONE A)")

    # 2) byte scan of the selected scenario subtrees (paths + content + PNG meta)
    rel = [f"{args.split}/{sid}" for sid in scenarios]
    for where, tok in leakcheck.scan_eval(split_root, ids, scenarios=rel):
        problems.append(f"{where}: '{tok}'")

    # 3) prompt self-check: scan EXACTLY what would be sent to the model
    for sid, (_system, user) in prompts.items():
        for tok in leakcheck.scan_text(user, ids):
            problems.append(f"prompt[{sid}] would leak banned token '{tok}'")

    # 4) integrity: re-hash selected files vs dataset.json; seal vs truth store
    integrity: dict = {"status": "skipped (--no-verify)",
                       "files_verified": 0, "seal_match": None}
    if not args.no_verify and dataset_p.exists() and not problems:
        try:
            dataset = json.load(open(dataset_p))
        except Exception as e:
            dataset = None
            integrity["status"] = f"FAILED (dataset.json unreadable: {e!r})"
        if dataset is not None:
            bad: list[str] = []
            n = 0
            for sid in scenarios:
                sdir = split_root / args.split / sid
                for f in sorted(sdir.rglob("*")):
                    if not f.is_file():
                        continue
                    relp = f"{args.split}/{sid}/{f.relative_to(sdir).as_posix()}"
                    expected = dataset.get("files", {}).get(relp)
                    if expected is None:
                        bad.append(f"{relp}: not listed in dataset.json "
                                   f"(file added after sealing)")
                    elif sha256_file(f) != expected:
                        bad.append(f"{relp}: sha256 mismatch vs dataset.json "
                                   f"(tampered or stale copy)")
                    n += 1
            integrity["files_verified"] = n
            seal_truth_p = truth_root / "seal.json"
            if seal_truth_p.exists():
                try:
                    seal_truth = json.load(open(seal_truth_p)).get("sha256")
                except Exception:
                    seal_truth = None
                integrity["seal_match"] = bool(dataset.get("seal")) and \
                    dataset.get("seal") == seal_truth
                if not integrity["seal_match"]:
                    problems.append(
                        "dataset.json seal does not match the sealed truth store "
                        f"({seal_truth_p}) — data/eval was modified after sealing")
            else:
                integrity["seal_match"] = None  # truth store not present; nothing to compare
            problems += bad
            integrity["status"] = "ok" if not bad else "FAILED"
    elif not args.no_verify and problems:
        integrity["status"] = "not run (leak problems already found)"

    verdict = {
        "status": "clean" if not problems else "FAILED",
        "leak_scan_scenarios": len(scenarios),
        "descriptive_ids_from": str(truth_root / "id_map.csv") if ids
                                else "unavailable (truth store missing — family-vocab scan only)",
        "integrity": integrity,
    }
    return verdict, problems


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    args = parse_args(argv)
    split_root = Path(args.split_root)

    if args.list_models:
        list_models(args.base_url, args.api_key)
        return 0

    scenarios = resolve_scenarios(args.scenarios, split_root, args.split,
                                  Path(args.truth_root))
    prompts = {sid: build_prompt(sid, split_root / args.split / sid, args.detail,
                                 args.termination_mean)
               for sid in scenarios}
    harness_packs: dict[str, str] = {}
    harness_pack_texts: dict[str, str] = {}
    if args.harness == "full":
        # Evidence pack + rules appended to the USER turn before anything else
        # looks at the prompt: sha256, leak scan and payload all reflect it.
        import stats_pack
        for sid, (sys_txt, user_txt) in prompts.items():
            sdir = split_root / args.split / sid
            pack = stats_pack.render_text(stats_pack.build_pack(sdir))
            harness_packs[sid] = hashlib.sha256(pack.encode()).hexdigest()[:16]
            harness_pack_texts[sid] = pack
            prompts[sid] = (sys_txt, user_txt + "\n\n---\n" + pack + "\n" + HARNESS_RULES)

    sampling = {"top_p": args.top_p, "top_k": args.top_k, "min_p": args.min_p,
                "presence_penalty": args.presence_penalty,
                "repetition_penalty": args.repetition_penalty}

    # ---- preflight: leak scan + integrity gate — NO API CALL BEFORE THIS --- #
    guards, problems = preflight_guards(args, scenarios, prompts)

    run_id = args.out or ("zs_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    out_dir = Path("results") / run_id / "zero_shot"
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "script_version": VERSION,
        "prompt_revision": PROMPT_REVISION,
        "split": args.split,
        "scenarios": scenarios,
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "sampling": {k: v for k, v in sampling.items() if v is not None},
        "max_tokens": None,          # never sent — completion is bounded only by n_ctx
        "stream": args.stream,
        "context": server_context_window(args.base_url, args.api_key),
        "stateless_calls": True,     # one system + one user turn per call, no history
        "seed": args.seed,
        "runs": args.runs,
        "detail": args.detail,
        "termination_mean": args.termination_mean,
        "dataset_fingerprint": dataset_fingerprint(split_root),
        "leak_check": guards,
    }
    if args.harness != "off":
        meta["harness"] = {"version": HARNESS_VERSION, "mode": args.harness,
                           "tool_calls_max": args.tool_calls,
                           "pack_sha": harness_packs}
    # Only a real run (or a refused one) records meta.json; a --dry-run never
    # writes into the output dir, so it cannot clobber a live pool's meta.json.
    if not args.dry_run:
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    if problems:
        print(f"REFUSING TO RUN: preflight gate failed ({len(problems)} problem(s)); "
              "no API call was made. Fix the workspace (rebuild with "
              "scripts/generate_scenarios.py); full verdict in "
              f"{out_dir / 'meta.json'}", file=sys.stderr)
        for p in problems[:40]:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # ---- dry run: print prompts, no API call ------------------------------ #
    if args.dry_run:
        integ = guards["integrity"]
        for sid in scenarios:
            system, user = prompts[sid]
            print("=" * 78)
            print(f"SCENARIO {sid}  (split={args.split}, prompt chars: {len(user)})")
            print("=" * 78)
            print("[system]\n" + system)
            print("[user]\n" + user)
        print(f"\n[preflight] leak scan CLEAN · integrity: {integ['status']} "
              f"({integ['files_verified']} files verified, "
              f"seal match: {integ['seal_match']})")
        print(f"[dry-run] prompts written to stdout only; no API call was made. "
              f"nothing was written under {out_dir}")
        return 0

    # ---- real run ---------------------------------------------------------- #
    integ = guards["integrity"]
    summary_lines = [f"# Zero-shot probe — run {run_id}",
                     f"model={args.model} endpoint={args.base_url} temp={args.temperature} "
                     f"seed={args.seed} runs={args.runs}",
                     f"sampling: {json.dumps({k: v for k, v in sampling.items() if v is not None}) or '{}'} "
                     f"· max_tokens: not sent · stateless per-call context",
                     f"dataset fingerprint: {meta['dataset_fingerprint']}",
                     f"preflight: leak check CLEAN · integrity {integ['status']} "
                     f"({integ['files_verified']} files verified, seal match: "
                     f"{integ['seal_match']})", ""]
    failures = []
    aborted = None
    consec = 0  # consecutive API failures -> circuit breaker

    for sid in scenarios:
        system, user = prompts[sid]
        (out_dir / f"{sid}_prompt.md").write_text(
            f"# Prompt — {sid}\n\n## system\n\n{system}\n\n## user\n\n{user}\n")
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": user}]

        for run in range(1, args.runs + 1):
            seed = args.seed + run - 1
            out_p = out_dir / f"{sid}_run{run:02d}.json"

            if args.skip_existing and out_p.exists():
                prev = None
                try:
                    prev = json.loads(out_p.read_text())
                except Exception:
                    prev = None
                if prev and prev.get("content") and not prev.get("error"):
                    continue  # already have a good answer; do not re-spend the call

            record = {
                "scenario_id": sid,
                "run": run,
                "model": args.model,
                "temperature": args.temperature,
                "sampling": {k: v for k, v in sampling.items() if v is not None},
                "seed": seed,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "error": None,
                "attempts": [],
                "raw_response": None,
                "content": None,
                "reasoning_content": None,
                "prompt": {"system_chars": len(system), "user_chars": len(user),
                           "revision": PROMPT_REVISION,
                           "sha256": hashlib.sha256(
                               (system + "\x00" + user).encode()).hexdigest()},
                "request": None,   # exact payload sent, filled after the call
                "wall_seconds": None,
            }
            if args.harness != "off":
                record["harness"] = {"version": HARNESS_VERSION,
                                     "pack_sha": harness_packs.get(sid),
                                     "pack_text": harness_pack_texts.get(sid)}
            payload_sent: dict = {}
            t_start = time.time()
            # Do not spend an attempt against a socket we can see is dead.
            if not wait_for_endpoint(args.base_url, args.api_key,
                                     args.wait_for_endpoint):
                record["error"] = "endpoint unavailable (wait-for-endpoint expired)"
                failures.append((sid, run, record["error"]))
                record["wall_seconds"] = round(time.time() - t_start, 1)
                record["finished_at"] = datetime.now(timezone.utc).isoformat()
                out_p.write_text(json.dumps(record, indent=2, default=str))
                aborted = "endpoint unavailable"
                break

            invalid_content = False   # set when the failure is the answer itself
            for attempt in range(3):  # retry with backoff on transient errors
                try:
                    if args.harness == "full":
                        resp = run_harness_turns(
                            args.base_url, args.api_key, args.model, messages,
                            args.temperature, seed, args.timeout,
                            sampling=sampling, stream=args.stream,
                            artifacts_dir=split_root / args.split / sid / "artifacts",
                            max_tool_calls=args.tool_calls)
                        if record.get("harness") is not None:
                            record["harness"].update(resp.pop("harness", {}))
                        payload_sent.update({"model": args.model, "temperature": args.temperature,
                                             "seed": seed, "multi_turn": True,
                                             "initial_messages": messages})
                    else:
                        resp = call_llm(args.base_url, args.api_key, args.model,
                                        messages, args.temperature, seed, args.timeout,
                                        sampling=sampling, stream=args.stream,
                                        payload_out=payload_sent)
                    record["request"] = payload_sent
                    record["raw_response"] = resp
                    record["content"] = extract_content(resp)
                    try:
                        record["reasoning_content"] = (
                            resp["choices"][0]["message"].get("reasoning_content"))
                    except (KeyError, IndexError, TypeError, AttributeError):
                        pass
                    record["finish_reason"] = (resp.get("choices") or [{}])[0].get(
                        "finish_reason")
                    record["usage"] = resp.get("usage")
                    record["streamed"] = resp.get("streamed")
                    # A clean-but-empty completion is a failed call, not an OK
                    # run: it used to be recorded with content="" / error=None.
                    if not (record["content"] or "").strip():
                        invalid_content = True
                        raise EmptyGeneration(
                            f"empty completion (finish_reason="
                            f"{record.get('finish_reason')})")
                    # Infrastructure failure, not model behaviour: the stream
                    # died (server restart) — retry rather than bank half an
                    # answer. Historical corpora always ended with "stop".
                    if record.get("finish_reason") is None:
                        raise TruncatedStream(
                            f"stream ended without finish_reason "
                            f"({len(record.get('content') or '')} chars, "
                            f"usage={record.get('usage')})")
                    if not answer_parses_as_json(record["content"]):
                        invalid_content = True
                        raise TruncatedStream(
                            f"answer is not parseable JSON "
                            f"({len(record['content'])} chars saved)")
                    if extract_tool_request(record["content"]) is not None:
                        invalid_content = True
                        raise TruncatedStream(
                            "last turn is still a tool request — no final answer")
                    record["attempts_ok"] = attempt + 1
                    break  # success: leave record["error"] as None
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                        ConnectionError, json.JSONDecodeError, EmptyGeneration,
                        TruncatedStream) as e:
                    # NOTE: a later attempt may still succeed; `error` below is the
                    # FINAL verdict, so clear it on success instead of letting an
                    # early failed attempt masquerade as a failed run.
                    record["attempts"].append(f"attempt {attempt + 1}: {e!r}")
                    record["error"] = (f"all {attempt + 1} attempt(s) failed; last: "
                                       f"{e!r}")
                    time.sleep(2 * (attempt + 1))
            # A recovered run (content present) is an OK run; but do NOT clear the
            # error for an empty completion — that is the silent-stub bug (v0.4.1)
            # where content="" / error=None let --skip-existing skip a spent call.
            if (record.get("raw_response") is not None
                    and (record.get("content") or "").strip()
                    and not invalid_content):
                record["error"] = None
            record["wall_seconds"] = round(time.time() - t_start, 1)
            record["finished_at"] = datetime.now(timezone.utc).isoformat()
            out_p.write_text(json.dumps(record, indent=2, default=str))

            if record["error"]:
                failures.append((sid, run, record["error"]))
                consec += 1
                if consec >= args.max_consecutive_failures:
                    aborted = (f"circuit breaker: {consec} consecutive failures "
                               f"(last: {record['error']})")
                    break
            else:
                consec = 0
        if aborted:
            break

    for sid in scenarios:
        n_ok = args.runs - sum(1 for s, r, e in failures if s == sid)
        summary_lines.append(f"## {sid}  ({n_ok}/{args.runs} runs ok)")

    if args.show_truth:
        truth_root = Path(args.truth_root)
        truth_dir = out_dir / "truth"
        truth_dir.mkdir(exist_ok=True)
        id_map = truth_root / "id_map.csv"
        if id_map.exists():  # maps opaque sc- ids back to descriptive names
            (truth_dir / "id_map.csv").write_text(id_map.read_text())
        for sid in scenarios:  # sid is the opaque id; truth store keys on it
            src = truth_root / "manifests" / f"{sid}.json"
            if src.exists():
                (truth_dir / f"{sid}.json").write_text(src.read_text())
        summary_lines += [
            "",
            "## Ground truth (scorer-only — copied for the experimenter, NEVER sent to the model)",
            "Manifest files copied to zero_shot/truth/ (keyed by the opaque scenario "
            "id; see truth/id_map.csv for the descriptive name). Open a manifest and a "
            "`<scenario>_runNN.json` side by side and check: benefit, years, pattern "
            "type, direction, magnitude. (Automated scoring arrives with milestone M0 "
            "scoring.py / M3 Stage 1.)",
        ]

    summary_lines.append("")
    if aborted:
        summary_lines.append(f"## SWEEP ABORTED\n\n{aborted}\n\n"
                             "Re-run with `--skip-existing` to resume without "
                             "re-spending the calls that already succeeded.\n")
    if failures:
        summary_lines.append("## Failures")
        for sid, run, err in failures:
            summary_lines.append(f"- {sid} run {run}: {err}")
        summary_lines.append("")
    (out_dir / "summary.md").write_text("\n".join(summary_lines))

    meta["aborted"] = aborted
    meta["failed_calls"] = len(failures)
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    print(f"run {run_id} -> {out_dir}/")
    print(f"  {len(scenarios)} scenario(s) x {args.runs} run(s); "
          f"{len(failures)} failed call(s)")
    if aborted:
        print(f"  ABORTED: {aborted}", file=sys.stderr)
    return 1 if (failures or aborted) else 0


if __name__ == "__main__":
    sys.exit(main())
