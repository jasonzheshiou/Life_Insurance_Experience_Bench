#!/usr/bin/env python3
"""Generate the Data Pipeline Arena scenario dataset.

Reads the scenario registry (``config/scenarios.yaml`` + ``config/scenarios.d/*.yaml``),
runs the sibling Life_Insurance_data_generator pipeline once per scenario at a
chosen scale, sanity-checks each scenario's observable signature, then assembles
the LEAK-FREE eval workspace and the scorer-only truth store.

Anti-leakage layout (see also ``scripts/leakcheck.py``):

    data/raw/<descriptive_id>/     generator output incl. metadata.json — the
                                   lab view; descriptive names live here
    data/eval/                     ZONE A — the ONLY folder ever copied for an
                                   LLM/agent run. Scenario dirs carry opaque
                                   ids (sc-<6hex>); contains claims/exposure/
                                   benchmarks/artifacts + dataset.json
                                   (file inventory, hashes, truth seal).
                                   No descriptive names, no statuses.
    data/truth/                    ZONE B — scorer-only, never ships with the
                                   eval workspace: id_map.csv, manifests/,
                                   scenario_summary.json (statuses/checks),
                                   id_key.json, seal.json.

Ids are derived once from a random per-dataset seed (``truth/id_key.json``)
and FROZEN in ``truth/id_map.csv``: rebuilds never churn ids, new scenarios
extend the map. Assignment is shuffled, so alphabetical order of descriptive
ids does not survive into the eval layout.

Usage::

    python scripts/generate_scenarios.py                          # medium scale, all scenarios
    python scripts/generate_scenarios.py --scale tiny             # fast smoke pass
    python scripts/generate_scenarios.py --scale full             # canonical 250k-policy run
    python scripts/generate_scenarios.py --only baseline,drift_death_up_2018_2024
    python scripts/generate_scenarios.py --split-only             # rebuild data/eval + truth from raw stores
    python scripts/generate_scenarios.py --split-only --no-checks # ...without pandas (pure relabel/copy)
    python scripts/generate_scenarios.py --force                  # regenerate stores even if they exist

Determinism: the generator is seeded (default 42, from config) and every scenario
is a pure function of its registry entry, so re-running yields byte-identical
stores. Content hashes of the eval workspace are written to
``data/eval/dataset.json`` (opaque paths) and a sha256 commitment over the
truth store is written to ``data/truth/seal.json`` for the fairness audit.
Every assembly ends with a mandatory byte-level leak scan; the build FAILS on
any hit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import secrets
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# --- paths -------------------------------------------------------------------
ARENA_ROOT = Path(__file__).resolve().parents[1]
GEN_ROOT = ARENA_ROOT.parent / "Life_insurance_data_generator_new"
SCRIPT_DIR = Path(__file__).resolve().parent

DATA = ARENA_ROOT / "data"
RAW = DATA / "raw"       # generator output incl. ground truth — lab view, never shipped
EVAL = DATA / "eval"     # ZONE A: model-facing, opaque ids — the ONLY shipped folder
TRUTH = DATA / "truth"   # ZONE B: scorer-only — id map, manifests, checks, seal

BENEFIT_NAMES = ["Death", "CI", "TPD", "IP"]

# The generator package (pandas-dependent) is imported lazily so that a pure
# split rebuild (--split-only --no-checks) runs on a bare stdlib+PyYAML
# interpreter. Generation and sanity checks call _ensure_generator() first.
BENEFITS: dict[str, Any] | None = None
DIAGNOSES: dict[str, Any] | None = None


def _ensure_generator() -> None:
    """Import the sibling generator package and populate its names as globals."""
    global BENEFITS, DIAGNOSES
    if BENEFITS is not None:
        return
    sys.path.insert(0, str(GEN_ROOT / "src"))
    from experience.analysis.ae import compute_ae  # noqa: F401
    from experience.analysis.termination import compute_termination_ae  # noqa: F401
    from experience.application.orchestrator import PipelineResult, run_pipeline  # noqa: F401
    from experience.assumptions.controls import (  # noqa: F401
        DriftSegment,
        RecoverySegment,
        ShockSegment,
        VolatilitySegment,
    )
    from experience.assumptions.model import Assumptions  # noqa: F401
    from experience.domain.enums import BenefitType, DiagnosisCategory  # noqa: F401
    from experience.io.storage import (  # noqa: F401
        load_assumptions_from_store,
        load_store,
        save_store,
    )
    globals().update(
        compute_ae=compute_ae,
        compute_termination_ae=compute_termination_ae,
        PipelineResult=PipelineResult,
        run_pipeline=run_pipeline,
        DriftSegment=DriftSegment,
        RecoverySegment=RecoverySegment,
        ShockSegment=ShockSegment,
        VolatilitySegment=VolatilitySegment,
        Assumptions=Assumptions,
        BenefitType=BenefitType,
        DiagnosisCategory=DiagnosisCategory,
        load_assumptions_from_store=load_assumptions_from_store,
        load_store=load_store,
        save_store=save_store,
    )
    BENEFITS = {b.value: b for b in BenefitType}
    DIAGNOSES = {d.value: d for d in DiagnosisCategory}


# --- small helpers -----------------------------------------------------------
def _fatal(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def git_head(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- registry ----------------------------------------------------------------
def load_registry(config_path: Path) -> dict[str, Any]:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    scenarios = list(cfg.get("scenarios", []))
    d_dir = config_path.parent / "scenarios.d"
    if d_dir.is_dir():
        for extra in sorted(d_dir.glob("*.yaml")):
            scenarios.extend(yaml.safe_load(extra.read_text(encoding="utf-8")).get("scenarios", []))
    cfg["scenarios"] = scenarios
    return cfg


def resolve_scale(cfg: dict[str, Any], name: str) -> dict[str, Any]:
    scales = cfg["scales"]
    if name not in scales:
        _fatal(f"unknown scale {name!r}; choose from {sorted(scales)}")
    scale = dict(scales[name])
    scale["name"] = name
    targets = {b: int(round(t * scale["target_factor"])) for b, t in cfg["base_targets"].items()}
    for b, t in targets.items():
        if t <= 0:
            _fatal(f"scale {name} yields non-positive target for {b}")
    # plain benefit-name strings; converted to enums only at generator use-sites
    scale["targets"] = targets
    return scale


def _window(c: dict[str, Any]) -> tuple[date, date]:
    y0, y1 = c["window"]
    return date(y0, 1, 1), date(y1, 12, 31)


def _benefit(name: str | None):
    return None if name in (None, "all") else BENEFITS[name]


# --- opaque ids ---------------------------------------------------------------
def _load_or_init_id_map(specs: list[dict[str, Any]]) -> dict[str, str]:
    """descriptive id -> eval token, FROZEN in data/truth/id_map.csv.

    Tokens are derived from a random per-dataset seed (truth/id_key.json), so
    the alphabetical order of descriptive ids does not survive into the eval
    layout. Existing assignments are never re-derived; new scenarios extend
    the map deterministically.
    """
    TRUTH.mkdir(parents=True, exist_ok=True)
    key_path = TRUTH / "id_key.json"
    map_path = TRUTH / "id_map.csv"
    if key_path.exists():
        key = json.loads(key_path.read_text(encoding="utf-8"))
    else:
        key = {"seed_hex": secrets.token_hex(16),
               "created_at": datetime.now(timezone.utc).isoformat()}
        key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
    seed = key["seed_hex"]

    mapping: dict[str, str] = {}  # descriptive -> eval token
    if map_path.exists():
        with open(map_path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                mapping[row["scenario_id"]] = row["eval_id"]

    taken = set(mapping.values())

    def token_for(sid: str) -> str:
        salt = 0
        while True:
            tok = "sc-" + hashlib.sha256(f"{seed}|{sid}|{salt}".encode()).hexdigest()[:6]
            if tok not in taken:
                taken.add(tok)
                return tok
            salt += 1

    added = [sid for sid in (s["id"] for s in specs) if sid not in mapping]
    for sid in sorted(added):
        mapping[sid] = token_for(sid)
    if added or not map_path.exists():
        meta = {s["id"]: s for s in specs}
        with open(map_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["eval_id", "scenario_id", "family", "split"])
            for sid, eid in sorted(mapping.items(), key=lambda kv: kv[1]):
                s = meta.get(sid, {})
                w.writerow([eid, sid, s.get("family", ""), s.get("split", "")])
    return mapping


def _seal_truth() -> str:
    """sha256 commitment over id_map.csv + all manifests (sorted by name).

    Publishing the seal BEFORE model runs proves the ground truth was not
    edited after results were produced.
    """
    h = hashlib.sha256()
    idmap = TRUTH / "id_map.csv"
    if idmap.exists():
        h.update(b"id_map.csv\x00" + idmap.read_bytes())
    man_dir = TRUTH / "manifests"
    if man_dir.is_dir():
        for f in sorted(man_dir.glob("*.json")):
            h.update(f.name.encode("utf-8") + b"\x00" + f.read_bytes())
    return h.hexdigest()


# --- disjointness ------------------------------------------------------------
def control_keys(spec: dict[str, Any]) -> list[tuple[Any, ...]]:
    keys: list[tuple[Any, ...]] = []
    for c in spec.get("controls", []):
        ctype = c["type"]
        if ctype in ("drift", "volatility"):
            affected = frozenset({c.get("benefit") or "all"})
            factor = round(c.get("slope", c.get("sigma", 0.0)), 4)
        elif ctype in ("shock", "ip_recovery"):
            affected = frozenset(c["factors"])
            factor = frozenset(round(float(v), 4) for v in c["factors"].values())
        else:
            continue
        keys.append((ctype, affected, tuple(c["window"]), factor))
    return keys


def check_disjointness(cfg: dict[str, Any]) -> None:
    ids: set[str] = set()
    opt_keys: set[tuple[Any, ...]] = set()
    held_keys: set[tuple[Any, ...]] = set()
    for spec in cfg["scenarios"]:
        sid = spec["id"]
        if sid in ids:
            _fatal(f"duplicate scenario id {sid!r}")
        ids.add(sid)
        keys = control_keys(spec)
        if spec["split"] == "optimization":
            opt_keys.update(keys)
        else:
            held_keys.update(keys)
    overlap = held_keys & opt_keys
    if overlap:
        print("DISJOINTNESS VIOLATION: these control signatures appear in both splits:")
        for k in sorted(overlap, key=str):
            print(f"  - {k}")
        _fatal("optimization and heldout must be disjoint by (benefit x type x window x factor)")
    print(f"disjointness OK: {len(opt_keys)} optimization keys, {len(held_keys)} heldout keys, no overlap")


# --- generation --------------------------------------------------------------
def run_scenario(
    spec: dict[str, Any], cfg: dict[str, Any], scale: dict[str, Any], force: bool
) -> "PipelineResult":
    sid = spec["id"]
    raw = RAW / sid
    store_dir = raw / "store"
    run_info_path = raw / "run_info.json"

    def _reuse() -> "PipelineResult":
        assumptions = load_assumptions_from_store(store_dir)
        store = load_store(store_dir)
        ae = compute_ae(store, assumptions)
        termination_ae = compute_termination_ae(store, assumptions)
        return PipelineResult(store=store, ae=ae, termination_ae=termination_ae, summary={})

    if run_info_path.exists():
        info = json.loads(run_info_path.read_text(encoding="utf-8"))
        scale_match = info.get("scale") == scale["name"] and info.get("n_policies") == scale["n_policies"]
        if scale_match:
            if force:
                print(f"[{sid}] force: regenerating (scale {scale['name']})")
            else:
                print(f"[{sid}] reuse existing store (scale {scale['name']})")
                return _reuse()
        elif not force:
            _fatal(
                f"{sid}: raw store exists at scale {info.get('scale')} (n_policies={info.get('n_policies')}) "
                f"but requested {scale['name']} (n_policies={scale['n_policies']}). "
                f"Use --force to overwrite, or pick the matching scale. Train/test must never mix scales."
            )
        else:
            print(f"[{sid}] force: overwriting store at scale {info.get('scale')} with {scale['name']}")

    assumptions = build_assumptions(spec, cfg, scale)
    print(f"[{sid}] generating @ {scale['name']} (n_policies={scale['n_policies']}) ...", flush=True)
    result = run_pipeline(assumptions, report_dir=raw / "artifacts")
    save_store(result.store, store_dir)
    run_info = {
        "scenario_id": sid,
        "scale": scale["name"],
        "n_policies": scale["n_policies"],
        "targets": dict(scale["targets"]),
        "seed": cfg["seed"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": str(GEN_ROOT),
        "generator_commit": git_head(GEN_ROOT),
    }
    run_info_path.write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    return result


# --- sanity checks -----------------------------------------------------------
def yearly_ae(ae_table) -> dict[int, float]:
    """Per-year incidence A/E: Actual.sum() / Expected.sum() per calendar year."""
    out: dict[int, float] = {}
    g = ae_table.groupby("Year")
    for year, sub in g:
        exp = float(sub["Expected"].sum())
        out[int(year)] = float(sub["Actual"].sum() / exp) if exp > 0 else float("nan")
    return out


def _check(name: str, ok: bool, detail: str, status: str = "pass") -> dict[str, Any]:
    return {"name": name, "status": "fail" if not ok else status, "ok": ok, "detail": detail}


def check_scenario(
    spec: dict[str, Any],
    result: "PipelineResult",
    baseline: "PipelineResult | None",
    scale: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    targets = scale["targets"]

    def noise(benefit) -> float:
        return 1.0 / math.sqrt(targets[benefit.value])

    if spec.get("no_op") and not spec.get("controls") and not spec.get("neutral"):
        for b in BenefitType:
            ae = result.ae[b]
            exp = float(ae["Expected"].sum())
            overall = float(ae["Actual"].sum() / exp) if exp > 0 else float("nan")
            band = 5.0 * noise(b)
            ok = abs(overall - 1.0) <= band
            checks.append(
                _check(f"baseline_ae_{b.value.lower()}", ok, f"overall A/E {overall:.4f} within 1 ± {band:.4f}")
            )
        return checks

    if spec.get("neutral"):
        if baseline is None:
            checks.append(_check("noop_needs_baseline", False, "baseline result required for no-op check"))
            return checks
        for b in BenefitType:
            same = result.store.claims(b).equals(baseline.store.claims(b))
            checks.append(_check(f"noop_claims_{b.value.lower()}", same, f"{b.value} claims bit-identical"))
        same_exp = result.store.exposure.equals(baseline.store.exposure)
        checks.append(_check("noop_exposure", same_exp, "exposure bit-identical"))
        same_term = result.termination_ae.get(BenefitType.IP, None)
        base_term = baseline.termination_ae.get(BenefitType.IP, None)
        if same_term is not None and base_term is not None:
            checks.append(_check("noop_termination_ip", same_term.equals(base_term), "IP termination A/E bit-identical"))
        return checks

    # generic per-control checks (single or multiple controls)
    all_affected: set[str] = set()
    for c in spec.get("controls", []):
        ctype = c["type"]
        y0, y1 = c["window"]
        if ctype == "drift":
            benefit = BENEFITS[c["benefit"]] if c.get("benefit") != "all" else None
            for b in (list(BenefitType) if benefit is None else [benefit]):
                yearly = yearly_ae(result.ae[b])
                slope = c["slope"]
                # drift is a trend: fit a least-squares slope on the in-window
                # yearly A/E (a mean-vs-reference test is too sensitive to a
                # single noisy year at the window edge)
                in_win = sorted(
                    (y, v) for y, v in yearly.items() if y0 <= y <= y1 and not math.isnan(v)
                )
                if len(in_win) < 2:
                    checks.append(_check(f"drift_{b.value.lower()}", False, "need >=2 in-window years"))
                    continue
                xs = [y for y, _ in in_win]
                ys = [v for _, v in in_win]
                n = len(xs)
                mx = sum(xs) / n
                my = sum(ys) / n
                denom = sum((x - mx) ** 2 for x in xs)
                fit_slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else 0.0
                sign_ok = (fit_slope > 0) if slope > 0 else (fit_slope < 0)
                # threshold: the fitted slope must retain a meaningful fraction
                # of the injected slope (noise scales with 1/sqrt(target))
                thr = 0.4 * abs(slope)
                if sign_ok and abs(fit_slope) >= thr:
                    st = "pass"
                elif sign_ok:
                    st = "weak"
                else:
                    st = "fail"
                checks.append(
                    _check(
                        f"drift_{b.value.lower()}",
                        st != "fail",
                        f"fitted slope {fit_slope:+.4f}/yr over {n} yrs (injected {slope:+.2f}/yr, thr={thr:.3f})",
                        status=st,
                    )
                )
                all_affected.add(b.value)
        elif ctype == "shock":
            for bname, factor in c["factors"].items():
                b = BENEFITS[bname]
                yearly = yearly_ae(result.ae[b])
                in_win = [v for y, v in yearly.items() if y0 <= y <= y1 and not math.isnan(v)]
                if not in_win:
                    checks.append(_check(f"shock_{b.value.lower()}", False, "no in-window years"))
                    continue
                win_mean = sum(in_win) / len(in_win)
                sign_ok = (win_mean - 1.0 > 0) if factor > 1.0 else (win_mean - 1.0 < 0)
                # The generator's shock reallocates claims into the window, so
                # the observable in-window ratio is ~1 + 0.5*(factor-1) (the
                # canonical covid x1.5 shock lands at ~1.25). Calibrate the
                # threshold to that transfer, not the raw factor.
                if sign_ok and abs(win_mean - 1.0) >= 0.5 * abs(factor - 1.0):
                    st = "pass"
                elif sign_ok:
                    st = "weak"
                else:
                    st = "fail"
                checks.append(
                    _check(
                        f"shock_{b.value.lower()}",
                        st != "fail",
                        f"win_mean {win_mean:.3f} vs 1.0 (factor x{factor})",
                        status=st,
                    )
                )
                all_affected.add(b.value)
        elif ctype in ("volatility",):
            benefit = BENEFITS[c["benefit"]] if c.get("benefit") != "all" else None
            for b in (list(BenefitType) if benefit is None else [benefit]):
                yearly = yearly_ae(result.ae[b])
                base_yearly = yearly_ae(baseline.ae[b]) if baseline is not None else None
                in_win = [v for y, v in yearly.items() if y0 <= y <= y1 and not math.isnan(v)]
                base_win = (
                    [v for y, v in base_yearly.items() if y0 <= y <= y1 and not math.isnan(v)]
                    if base_yearly is not None
                    else None
                )
                if len(in_win) < 3 or base_win is None or len(base_win) < 3:
                    checks.append(_check(f"vol_{b.value.lower()}", False, "need >=3 in-window years and a baseline"))
                    continue
                std_ratio = (sum((v - sum(in_win) / len(in_win)) ** 2 for v in in_win) / (len(in_win) - 1)) ** 0.5 / (
                    (sum((v - sum(base_win) / len(base_win)) ** 2 for v in base_win) / (len(base_win) - 1)) ** 0.5
                )
                win_mean = sum(in_win) / len(in_win)
                if std_ratio >= 1.5:
                    st = "pass"
                elif std_ratio >= 1.2:
                    st = "weak"
                else:
                    st = "fail"
                # level tolerance: the mean of the in-window yearly A/E is
                # subject to the injected volatility itself (~ sigma/sqrt(n))
                # on top of Poisson noise, so the band must scale with sigma.
                level_thr = 4.0 * (c["sigma"] / math.sqrt(len(in_win)) + noise(b))
                level_ok = abs(win_mean - 1.0) <= level_thr
                checks.append(
                    _check(
                        f"vol_{b.value.lower()}",
                        st != "fail",
                        f"in-window std {std_ratio:.2f}x baseline std, mean {win_mean:.3f}",
                        status=st,
                    )
                )
                checks.append(_check(f"vol_level_{b.value.lower()}", level_ok, f"level unchanged ({win_mean:.3f})"))
                all_affected.add(b.value)
        elif ctype == "ip_recovery":
            ip_now = result.store.claims(BenefitType.IP)
            ip_base = baseline.store.claims(BenefitType.IP) if baseline is not None else None
            for dname, factor in c["factors"].items():
                diag = DIAGNOSES[dname]
                mask_now = ip_now["primary_diagnosis_category"] == diag.value
                if not mask_now.any():
                    checks.append(_check(f"recovery_{dname}", False, f"no {dname} claims in IP"))
                    continue
                dur_now = float(ip_now.loc[mask_now, "claim_duration_months"].mean())
                if ip_base is not None:
                    mask_base = ip_base["primary_diagnosis_category"] == diag.value
                    dur_base = float(ip_base.loc[mask_base, "claim_duration_months"].mean())
                else:
                    dur_base = dur_now
                if factor > 1.0:
                    ok = dur_now <= 0.9 * dur_base
                    st = "pass" if ok else ("weak" if dur_now < dur_base else "fail")
                else:
                    ok = dur_now >= 1.1 * dur_base
                    st = "pass" if ok else ("weak" if dur_now > dur_base else "fail")
                checks.append(
                    _check(
                        f"recovery_{dname}",
                        st != "fail",
                        f"{dname} mean duration {dur_now:.1f} vs baseline {dur_base:.1f} (factor x{factor})",
                        status=st,
                    )
                )
                all_affected.add("IP")

    # spillover: untouched benefits must stay at baseline (single-control scenarios only)
    if len(spec.get("controls", [])) == 1 and not spec.get("no_op"):
        for b in BenefitType:
            if b.value in all_affected:
                continue
            ae = result.ae[b]
            exp = float(ae["Expected"].sum())
            overall = float(ae["Actual"].sum() / exp) if exp > 0 else float("nan")
            band = 5.0 * noise(b)
            ok = abs(overall - 1.0) <= band
            checks.append(_check(f"spillover_{b.value.lower()}", ok, f"untouched {b.value} A/E {overall:.3f} within 1 ± {band:.3f}"))

    return checks


# --- manifest ------------------------------------------------------------------
def _manifest_for(spec: dict[str, Any], cfg: dict[str, Any], scale: dict[str, Any]) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []
    touched: set[str] = set()
    for c in spec.get("controls", []):
        ctype = c["type"]
        y0, y1 = c["window"]
        if ctype == "drift":
            affected = [c.get("benefit") or "all"]
            factor = c["slope"]
            direction = "increase" if c["slope"] > 0 else "decrease"
            magnitude = f"{c['slope']:+.2f}/yr"
        elif ctype == "shock":
            affected = list(c["factors"])
            factor = c["factors"]
            direction = "increase" if all(v > 1.0 for v in c["factors"].values()) else "decrease"
            magnitude = ", ".join(f"{k} x{v}" for k, v in c["factors"].items())
        elif ctype == "volatility":
            affected = [c.get("benefit") or "all"]
            factor = c["sigma"]
            direction = "dispersion"
            magnitude = f"sigma={c['sigma']}"
        else:  # ip_recovery
            affected = list(c["factors"])
            factor = c["factors"]
            direction = "increase" if all(v > 1.0 for v in c["factors"].values()) else "decrease"
            magnitude = ", ".join(f"{k} x{v}" for k, v in c["factors"].items())
        touched.update(affected)
        controls.append(
            {
                "type": ctype,
                "benefit": affected[0] if len(affected) == 1 and ctype != "shock" and ctype != "ip_recovery" else affected,
                "window": [y0, y1],
                "factor": factor,
                "signature": {"direction": direction, "magnitude": magnitude},
            }
        )

    untouched = [b for b in BENEFIT_NAMES if b not in touched]
    no_op = bool(spec.get("no_op"))
    manifest = {
        "schema_version": 1,
        "scenario_id": spec["id"],
        "family": spec.get("family", "none"),
        "split": spec["split"],
        "scale": scale["name"],
        "seed": cfg["seed"],
        "n_policies": scale["n_policies"],
        "targets": dict(scale["targets"]),
        "study_window": [int(cfg["study"]["start"][:4]), int(cfg["study"]["end"][:4])],
        "no_op": no_op,
        "controls": controls,
        "benefit_lines_untouched": untouched,
    }
    # primary: the arena-compatible flattened form. Only when exactly one
    # control exists AND it affects exactly one benefit (a multi-benefit shock
    # cannot flatten onto the arena's single-benefit ScenarioManifest).
    single_benefit = (
        len(controls) == 1
        and not isinstance(controls[0].get("benefit"), list)
        and (controls[0].get("benefit") or "all") != "all"
    )
    if single_benefit and not no_op:
        c = controls[0]
        manifest["primary"] = {
            "control_type": c["type"],
            "benefit": c["benefit"],
            "window": c["window"],
            "factor": c["factor"],
            "signature": c["signature"],
            "benefit_lines_untouched": untouched,
        }
    else:
        manifest["primary"] = None
    return manifest


# --- eval + truth assembly ------------------------------------------------------
def assemble_eval(
    cfg: dict[str, Any],
    scale: dict[str, Any],
    checks_by_id: dict[str, list[dict[str, Any]]],
    only: set[str] | None,
) -> tuple[bool, list[str], list[tuple[str, str]]]:
    """Assemble ZONE A (data/eval, opaque, model-facing) and ZONE B (data/truth).

    Zone A carries ONLY model-facing files — CSVs and PNGs plus a scenario_id.txt
    holding the OPAQUE id — under scenario dirs named sc-<6hex>. dataset.json
    holds the file inventory, per-file sha256 and the truth seal (a commitment
    that reveals nothing). Zone B holds the id map, manifests, sanity-check
    report and seal; it never ships with the eval workspace and is read only by
    validation/scoring. Assembly ends with a mandatory byte-level leak scan.
    """
    ok = True
    missing: list[str] = []
    opt_dir = EVAL / "optimization"
    held_dir = EVAL / "heldout"
    man_dir = TRUTH / "manifests"
    for d in (opt_dir, held_dir, man_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    id_map = _load_or_init_id_map(cfg["scenarios"])
    manifests: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}
    included: list[str] = []

    for spec in cfg["scenarios"]:
        sid = spec["id"]
        if only is not None and sid not in only:
            continue
        raw = RAW / sid
        if not (raw / "store").exists():
            missing.append(sid)
            continue
        run_info = json.loads((raw / "run_info.json").read_text(encoding="utf-8"))
        if run_info.get("scale") != scale["name"]:
            print(f"  [{sid}] skipped: raw store is at scale {run_info.get('scale')}, not {scale['name']}")
            missing.append(sid)
            continue

        eid = id_map[sid]
        split = spec["split"]
        dest = (opt_dir if split == "optimization" else held_dir) / eid
        dest.mkdir(parents=True)

        # raw store CSVs (never metadata.json — it embeds the assumptions; no parquet)
        for f in sorted((raw / "store").glob("*.csv")):
            shutil.copy2(f, dest / f.name)
        bench_src = raw / "store" / "benchmarks"
        if bench_src.is_dir():
            (dest / "benchmarks").mkdir(exist_ok=True)
            for f in sorted(bench_src.glob("*.csv")):
                shutil.copy2(f, dest / "benchmarks" / f.name)
        # A/E artifacts (charts + CSVs + summary.json)
        art_src = raw / "artifacts"
        if art_src.is_dir():
            (dest / "artifacts").mkdir(exist_ok=True)
            for f in sorted(art_src.iterdir()):
                if f.is_file():
                    shutil.copy2(f, dest / "artifacts" / f.name)
        # the id file carries the OPAQUE id — never the descriptive name
        (dest / "scenario_id.txt").write_text(eid + "\n", encoding="utf-8")

        manifest = _manifest_for(spec, cfg, scale)
        manifest = {"eval_id": eid, "descriptive_id": sid, **manifest}
        manifests[eid] = manifest
        (man_dir / f"{eid}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        checks = checks_by_id.get(sid, [])
        fails = [c for c in checks if c["status"] == "fail"]
        weaks = [c for c in checks if c["status"] == "weak"]
        if fails:
            statuses[sid] = "fail"
            ok = False
        elif weaks:
            statuses[sid] = "warn"
        else:
            statuses[sid] = "pass"
        included.append(sid)

    # --- ZONE B: seal + report ------------------------------------------------ #
    seal = _seal_truth()
    (TRUTH / "seal.json").write_text(
        json.dumps({"sealed_at": datetime.now(timezone.utc).isoformat(),
                    "sha256": seal, "n_manifests": len(manifests)}, indent=2),
        encoding="utf-8",
    )
    fingerprint = hashlib.sha256(
        json.dumps({eid: manifests[eid] for eid in sorted(manifests)}, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scale": scale["name"],
        "n_policies": scale["n_policies"],
        "seed": cfg["seed"],
        "counts": {
            "optimization": sum(1 for s in included if manifests[id_map[s]]["split"] == "optimization"),
            "heldout": sum(1 for s in included if manifests[id_map[s]]["split"] == "heldout"),
        },
        "statuses": {s: statuses[s] for s in sorted(statuses)},
        "checks": {s: checks_by_id.get(s, []) for s in sorted(statuses)},
        "eval_ids": {s: id_map[s] for s in sorted(included)},
        "fingerprint": fingerprint,
        "seal": seal,
        "missing": missing,
    }
    (TRUTH / "scenario_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # --- ZONE A: opaque inventory --------------------------------------------- #
    files: dict[str, str] = {}
    for base in (opt_dir, held_dir):
        for f in sorted(base.rglob("*")):
            if f.is_file():
                files[str(f.relative_to(EVAL)).replace("\\", "/")] = _sha256_file(f)
    dataset = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scale": scale["name"],
        "n_policies": scale["n_policies"],
        "counts": summary["counts"],
        "seal": seal,
        "files": files,
    }
    (EVAL / "dataset.json").write_text(json.dumps(dataset, indent=2, sort_keys=True), encoding="utf-8")

    # --- mandatory leak scan ---------------------------------------------------- #
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    import leakcheck

    leaks = leakcheck.scan_eval(EVAL, descriptive_ids=list(id_map.keys()))
    if leaks:
        print(f"LEAK CHECK FAILED: {len(leaks)} hit(s) in {EVAL} — do NOT run models against this:",
              file=sys.stderr)
        for where, tok in leaks[:40]:
            print(f"  {where}: '{tok}'", file=sys.stderr)
    else:
        print(f"leak check: CLEAN — {len(files)} files under {EVAL}")

    return ok, missing, leaks


# --- main --------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=ARENA_ROOT / "config" / "scenarios.yaml")
    ap.add_argument("--scale", default=None, help="tiny | medium | full (default: config default_scale)")
    ap.add_argument("--only", default=None, help="comma-separated scenario ids to generate")
    ap.add_argument("--force", action="store_true", help="regenerate raw stores even if present")
    ap.add_argument("--split-only", action="store_true", help="skip generation; rebuild data/eval + data/truth from raw stores")
    ap.add_argument("--no-checks", action="store_true",
                    help="skip sanity checks (--split-only --no-checks needs no pandas, just relabels/copies)")
    ap.add_argument("--force-split", action="store_true", help="assemble eval workspace even if checks fail")
    args = ap.parse_args()

    cfg = load_registry(args.config)
    scale = resolve_scale(cfg, args.scale or cfg.get("default_scale", "medium"))
    only = set(args.only.split(",")) if args.only else None

    print(f"registry: {len(cfg['scenarios'])} scenarios, scale={scale['name']}, "
          f"n_policies={scale['n_policies']}, targets={scale['targets']}")
    check_disjointness(cfg)

    selected = [s for s in cfg["scenarios"] if only is None or s["id"] in only]
    if only is not None:
        known = {s["id"] for s in cfg["scenarios"]}
        unknown = only - known
        if unknown:
            _fatal(f"unknown scenario ids: {sorted(unknown)}")
    if not selected:
        _fatal("no scenarios selected")

    # generation and sanity checks need the generator package (pandas);
    # a pure --split-only --no-checks rebuild is stdlib+yaml only.
    heavy = not (args.split_only and args.no_checks)
    if heavy:
        _ensure_generator()

    if not args.split_only:
        for spec in selected:
            run_scenario(spec, cfg, scale, args.force)
        print("generation complete")

    # load results for all scenarios with stores (needed for baseline + checks)
    loaded: dict[str, Any] = {}
    if heavy:
        for spec in cfg["scenarios"]:
            raw = RAW / spec["id"]
            if (raw / "store").exists() and (raw / "run_info.json").exists():
                info = json.loads((raw / "run_info.json").read_text(encoding="utf-8"))
                if info.get("scale") == scale["name"]:
                    assumptions = load_assumptions_from_store(raw / "store")
                    store = load_store(raw / "store")
                    loaded[spec["id"]] = PipelineResult(
                        store=store,
                        ae=compute_ae(store, assumptions),
                        termination_ae=compute_termination_ae(store, assumptions),
                        summary={},
                    )
    baseline = loaded.get("baseline")

    checks_by_id: dict[str, list[dict[str, Any]]] = {}
    for spec in selected:
        if args.no_checks:
            checks_by_id[spec["id"]] = []
            continue
        if spec["id"] not in loaded:
            continue
        checks_by_id[spec["id"]] = check_scenario(spec, loaded[spec["id"]], baseline, scale)

    if not args.split_only:
        n_fail = sum(1 for cs in checks_by_id.values() for c in cs if c["status"] == "fail")
        n_weak = sum(1 for cs in checks_by_id.values() for c in cs if c["status"] == "weak")
        print(f"checks: {n_fail} failed, {n_weak} weak")
        for sid in sorted(checks_by_id):
            for c in checks_by_id[sid]:
                mark = "OK " if c["status"] == "pass" else ("WEAK" if c["status"] == "weak" else "FAIL")
                print(f"  [{sid}] {mark} {c['name']}: {c['detail']}")

    hard_fail = any(c["status"] == "fail" for cs in checks_by_id.values() for c in cs)
    if hard_fail and not args.force_split:
        print("ERROR: sanity checks failed; data/eval was NOT written. "
              "Inspect the checks above, adjust the registry, then re-run "
              "(use --force-split only to override deliberately).", file=sys.stderr)
        return 1

    ok, missing, leaks = assemble_eval(cfg, scale, checks_by_id, only)
    print(f"eval workspace (ZONE A, ship this): {EVAL}")
    print(f"truth store   (ZONE B, scorer-only): {TRUTH}")
    print(f"truth seal: {_seal_truth()}")
    if missing:
        print(f"  missing (no raw store at {scale['name']} scale): {sorted(missing)}")
    if leaks:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
