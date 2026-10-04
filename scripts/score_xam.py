#!/usr/bin/env python3
"""Score zero-shot probe runs against the scorer-only truth manifests.

Usage:  python3 scripts/score_xam.py results/xam_20260831_opt/zero_shot [...]

Compares each <sc>_runNN.json finding list to data/truth/manifests/<sc>.json.
Reports, per scenario: control recall (strict = benefit+pattern+window+direction,
loose = benefit+pattern), false-positive claims, and JSON validity.

Direction is compared PER BENEFIT against the manifest's factor map, because
generate_scenarios.py collapses a mixed-direction control (e.g. Death x1.4 /
CI x0.6) into a single signature.direction ("decrease") — comparing against
that collapsed label would punish a correct answer. No truth text is ever
written into a prompt; this is scorer-side only.
"""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict
from pathlib import Path

BENEFITS = {"Death", "CI", "TPD", "IP"}
# truth control type -> pattern token the model was asked to emit
PATTERN_EQUIV = {
    "drift": {"drift"},
    "shock": {"shock"},
    "volatility": {"volatility"},
    "ip_recovery": {"recovery"},
}


def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def parse_findings(content: str | None):
    """Extract the JSON object the model was asked to return. Tolerant of
    prose or ``` fences around it; returns (status, list_of_findings)."""
    if not content or not content.strip():
        return "empty", [], None
    candidates = [content.strip()]
    if "{" in content and "}" in content:
        candidates.append(content[content.index("{"): content.rindex("}") + 1])
    for blob in candidates:
        try:
            # strict=False accepts RAW CONTROL CHARACTERS inside strings. The
            # model sometimes emits a literal newline mid-word ("Poiss\non"),
            # leaving otherwise-complete, balanced JSON. Rejecting it discards a
            # real answer over a formatting slip.
            obj = json.loads(blob, strict=False)
        except Exception:
            continue
        if isinstance(obj, dict):
            f = obj.get("findings")
            return "valid", (f if isinstance(f, list) else []), obj.get("overall_assessment")
    return "unparseable", [], None


def norm_years(f) -> tuple[int, int] | None:
    y = f.get("years")
    if isinstance(y, list) and len(y) == 2:
        try:
            return int(y[0]), int(y[1])
        except Exception:
            return None
    return None


def overlap(a, b) -> bool:
    if not a or not b:
        return False      # open-ended window does not count as a window hit
    return not (a[1] < b[0] or b[1] < a[0])


def benefit_matches(finding_benefit: str, control_benefit) -> bool:
    fb = str(finding_benefit or "").strip()
    if isinstance(control_benefit, list):
        return fb in {str(x) for x in control_benefit} or fb == "IP"
    if str(control_benefit) == "all":
        return fb in BENEFITS
    return fb == str(control_benefit)


def dir_from_factor(benefit: str, factor) -> str | None:
    """Expected direction for ONE benefit from the manifest factor(s)."""
    if isinstance(factor, dict):
        v = factor.get(benefit)
        if v is None:
            for k, kv in factor.items():          # diagnosis-keyed (ip_recovery)
                if str(k).lower() in str(benefit).lower():
                    v = kv
        if v is None:
            return None
        return "increase" if float(v) > 1.0 else "decrease"
    try:
        return "increase" if float(factor) > 1.0 else "decrease"
    except Exception:
        return None


def find_direction_issue(finding, control) -> bool:
    # (v3-D) ip_recovery controls carry a diagnosis-keyed factor dict; the
    # finding's benefit is always "IP", so dir_from_factor() could not resolve
    # it and silently skipped the check. Derive the expected direction from the
    # sign of the factor values instead (mixed signs -> no check).
    if str(control.get("type", "")) == "ip_recovery":
        fac = control.get("factor")
        if isinstance(fac, dict) and fac:
            vals = [float(v) for v in fac.values()]
            if all(v > 1.0 for v in vals):
                exp = "increase"
            elif all(v < 1.0 for v in vals):
                exp = "decrease"
            else:
                exp = None
        else:
            exp = None
        got = str(finding.get("direction", "")).lower()
        return exp is not None and bool(got) and got != exp
    # Volatility controls carry sigma in `factor` (e.g. 0.3 = σ multiplier),
    # NOT an A/E ratio — dir_from_factor() would misread it as "decrease".
    # The manifest's own signature.direction for these is "dispersion".
    if str(control.get("type", "")) == "volatility":
        exp = "dispersion"
    elif str(control.get("type", "")) == "drift":
        # Drift controls carry a signed per-year RATE (e.g. +0.08/yr), not
        # an A/E ratio; dir_from_factor() would read 0.08 as ratio<1 and
        # expect "decrease". Expected direction follows the rate's sign,
        # matching the manifest's own signature.direction.
        try:
            exp = "increase" if float(control.get("factor")) > 0 else "decrease"
        except (TypeError, ValueError):
            exp = None
    else:
        exp = dir_from_factor(finding.get("benefit", ""), control.get("factor"))
    got = str(finding.get("direction", "")).lower()
    if exp is None or not got:
        return False
    if exp == "dispersion":
        return got not in {"dispersion", "increase", "decrease"}
    return got != exp


def score_run(manifest: dict, findings: list[dict]):
    """Scorer v3.

    Artifact fixes over v2 (raw v2 snapshot kept at results/xam_v4/scores_v2_snapshot.json):
      A. years:null counts as a window hit IFF the control's truth window is the
         full study window (the model reports null when the data has no year
         dimension — e.g. pooled IP-termination file — which is honest, not wrong).
      B. Multi-benefit controls (benefit list / "all") are scored as one UNIT per
         expected benefit instead of a single hit-or-miss — listing all four
         affected benefits is no longer punished with 3 phantom FPs.
      C. "No material anomaly" bookkeeping statements (pattern=other + explicit
         no-anomaly text) are excluded from the finding pool entirely.
      D. ip_recovery direction is checked against the sign of the diagnosis
         factor dict (v2's dir_from_factor returned None -> silent no-op), and
         additional correct diagnosis findings are not counted as FPs.
    """
    controls = manifest.get("controls") or []
    swin = tuple(manifest.get("study_window")) if manifest.get("study_window") else None

    # (C) exclude no-anomaly statements; remember which indices survive
    keep = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            continue
        pat = str(f.get("pattern", "")).lower()
        text = f"{f.get('magnitude', '')} {' '.join(map(str, f.get('evidence') or []))}"
        if pat in {"other", "none", ""} and "no material anomaly" in text.lower():
            continue
        if pat in {"other", "none", ""} and str(f.get("direction", "")).lower() in {"none", ""} \
                and "no anomaly" in text.lower():
            continue
        keep.append((i, f))

    # (B) expand controls into scoring units: (control, expected_benefit|None)
    units = []
    for c in controls:
        cb = c.get("benefit")
        if str(c.get("type", "")) == "ip_recovery":          # diagnoses aren't a benefit line
            units.append((c, "IP"))
        elif isinstance(cb, list):
            units.extend((c, str(b)) for b in cb)
        elif str(cb) == "all":
            units.extend((c, b) for b in sorted(BENEFITS))
        else:
            units.append((c, str(cb)))

    res = {"n_controls": len(units), "strict": 0, "loose": 0,
           "per_control": [], "matched_idx": set(), "_drift_units": [], "supp_idx": set()}

    for c, eb in units:
        cwin = tuple(c["window"]) if c.get("window") else None
        hit = {"loose": False, "strict": False, "via": None}
        for i, f in keep:
            fb = str(f.get("benefit", "")).strip()
            if fb != eb:                       # unit_benefit is the exact expected benefit
                continue
            if str(f.get("pattern", "")).lower() not in PATTERN_EQUIV.get(c["type"], set()):
                continue
            hit["loose"] = True
            yrs = norm_years(f)
            # (A) null window == full-period claim: hit iff truth is full-period
            win_ok = overlap(yrs, cwin) or (yrs is None and cwin is not None
                                            and swin is not None and tuple(cwin) == tuple(swin))
            dir_ok = not find_direction_issue(f, c)
            if win_ok and dir_ok:
                hit["strict"] = True
                hit["via"] = {"finding_idx": i, "years": yrs, "want_years": cwin,
                              "direction": f.get("direction")}
                res["matched_idx"].add(i)
                # (D) ip_recovery: other correct-direction findings are supplementary, not FP
                if str(c.get("type", "")) == "ip_recovery":
                    for j, g in keep:
                        if str(g.get("pattern", "")).lower() == "recovery" \
                                and str(g.get("benefit", "")).strip() == "IP" \
                                and not find_direction_issue(g, c):
                            res["supp_idx"].add(j)
                break
            if hit["via"] is None:
                hit["via"] = {"finding_idx": i, "years": yrs, "want_years": cwin,
                              "direction": f.get("direction"),
                              "window_ok": win_ok, "direction_ok": dir_ok}
        res["per_control"].append({"type": c["type"], "benefit": c.get("benefit"),
                                   "unit_benefit": eb, "window": cwin, **hit})
        res["loose"] += hit["loose"]
        res["strict"] += hit["strict"]
        # difficulty strata: bounded (ends before study end) vs persistent drift controls
        if str(c.get("type", "")) == "drift":
            bounded = bool(cwin and swin and cwin[1] < swin[1])
            res["_drift_units"].append((bounded, hit["strict"], hit["loose"]))

    n_claim = len(keep)
    res["n_findings"] = n_claim
    res["fp"] = sum(1 for i, _ in keep
                    if i not in res["matched_idx"] and i not in res["supp_idx"])
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+")
    ap.add_argument("--truth", default="data/truth")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args(argv)

    truth = Path(a.truth)
    id_map = {}
    p = truth / "id_map.csv"
    if p.is_file():
        import csv
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                id_map[r["eval_id"]] = r

    out = {}
    for rd in a.run_dirs:
        rd = Path(rd)
        rows = defaultdict(list)
        drift_stats = []   # (sid, bounded, strict, loose) per drift control-run
        for f in sorted(rd.glob("*_run*.json")):
            rec = load_json(f)
            if not rec:
                continue
            sid, run = rec["scenario_id"], rec.get("run")
            man = load_json(truth / "manifests" / f"{sid}.json")
            status, findings, overall = parse_findings(rec.get("content"))
            if man is None:
                continue
            s = score_run(man, findings)
            clean_truth = bool(man.get("no_op")) or not (man.get("controls") or [])
            rows[sid].append({
                "run": run, "json": status, "overall": overall,
                "clean_truth": clean_truth, "family": id_map.get(sid, {}).get("family"),
                **s, "error": rec.get("error"),
                "completion_tokens": ((rec.get("raw_response") or {}).get("usage") or {})
                                     .get("completion_tokens"),
            })
            for bounded, st_, lo_ in s.get("_drift_units", []):
                drift_stats.append((sid, bounded, st_, lo_))

        print(f"\n{'='*100}\nRUN DIR: {rd}   [scorer v3: null-window=full-period, "
          f"per-benefit units, clean-statements excluded, ip_recovery direction live]\n{'='*100}")
        agg = defaultdict(int)
        for sid, runs in sorted(rows.items()):
            n = len(runs)
            strict = sum(r["strict"] for r in runs)
            n_ctrl = sum(r["n_controls"] for r in runs)
            is_clean = bool(runs and runs[0]["clean_truth"])
            # A clean scenario has NO control to recall; scoring it on recall is
            # meaningless — it is judged purely on false positives.
            ctr = n_ctrl if not is_clean else 0
            loose = sum(r["loose"] for r in runs)
            fps = sum(r["fp"] for r in runs)
            badjson = sum(1 for r in runs if r["json"] != "valid")
            errs = sum(1 for r in runs if r["error"])
            claim = sum(1 for r in runs if r["overall"] == "anomalies")
            if is_clean:
                print(f"{sid:<11} fam={'CLEAN':<11} runs={n} "
                      f"FALSE-POSITIVE: claimed-anomalies={claim}/{n} FP={fps} "
                      f"badjson={badjson} err={errs}")
            else:
                print(f"{sid:<11} fam={str(id_map.get(sid,{}).get('family')):<11} "
                      f"runs={n} strict={strict}/{ctr} loose={loose}/{ctr} "
                      f"FP={fps} badjson={badjson} err={errs}")
            agg["n_runs"] += n
            agg["strict"] += strict
            agg["controls"] += ctr
            agg["loose"] += loose
            agg["fp"] += fps
            agg["badjson"] += badjson
            agg["err"] += errs
            if is_clean:
                agg["clean_runs"] += n
                agg["clean_false_claims"] += claim
            out.setdefault(str(rd), {})[sid] = runs
        if agg["n_runs"]:
            denom = agg["controls"] or 1
            print(f"  TOTALS: runs={agg['n_runs']} "
                  f"strict-recall={agg['strict']}/{denom}="
                  f"{agg['strict']/denom:.1%} "
                  f"loose={agg['loose']/denom:.1%} "
                  f"FP/run={agg['fp']/agg['n_runs']:.2f} "
                  f"badjson={agg['badjson']} errors={agg['err']}")
            if agg.get("clean_runs"):
                print(f"  CLEAN-data honesty: claimed an anomaly on "
                      f"{agg['clean_false_claims']}/{agg['clean_runs']} clean run(s)")
            n_p = sum(1 for _, b, _, _ in drift_stats if not b)
            s_p = sum(st_ for _, b, st_, _ in drift_stats if not b)
            l_p = sum(lo_ for _, b, _, lo_ in drift_stats if not b)
            n_b = sum(1 for _, b, _, _ in drift_stats if b)
            s_b = sum(st_ for _, b, st_, _ in drift_stats if b)
            l_b = sum(lo_ for _, b, _, lo_ in drift_stats if b)
            if drift_stats:
                print(f"  DRIFT-WINDOW STRATA (per control-run): "
                      f"persistent-to-horizon strict {s_p}/{n_p}"
                      f" (loose {l_p}/{n_p}) | bounded-then-reverting strict {s_b}/{n_b}"
                      f" (loose {l_b}/{n_b})")
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(
            out, indent=2, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))
        print(f"\nwrote {a.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
