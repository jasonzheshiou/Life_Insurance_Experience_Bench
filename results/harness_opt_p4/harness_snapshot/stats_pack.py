#!/usr/bin/env python3
"""stats_pack.py — deterministic evidence pack for the Data Pipeline Arena harness.

Reads ONLY the model-facing artifacts of one scenario dir (data/eval/<split>/
<sid>/artifacts/*.csv) and prints a compact, computed statistics table for the
four benefit lines plus IP termination. This is the harness core: the model no
longer eyeballs 10 years x 4 lines by mental arithmetic — it gets computed
discriminators and reasons about THEM. Every number is derived from data the
model is already allowed to see, so this cannot leak truth.

Stdlib only (csv/math), matching the repo's no-dependency rule.

    python3 scripts/stats_pack.py data/eval/optimization/sc-042304

The output is designed to be APPENDED to the user prompt under a header that
tells the model to trust it over mental math. Key per-line evidence:

  * yearly A/E table with YoY change and correct-null z (Poisson on counts);
  * OLS trend slope + R^2 on A/E (drift candidate);
  * best single-year step change (mean before vs mean after) + t-like score
    (shock candidate), with the classic shift statistic argmax over splits;
  * volatility ratio: SD of YoY deltas in the second half vs first half, AND
    empirical SD vs Poisson-expected SD (overdispersion detector: ratio >> 1
    means Poisson z-scores are invalid and the right label is dispersion);
  * a descriptive evidence PROFILE per line (dispersion-dominant /
    step-dominant / sustained-move / no strong signal) — a statement about the
    shape of the evidence, never an anomaly claim; the model stays in charge and
    the pack just removes arithmetic errors.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

BENEFITS = ["death", "ci", "tpd", "ip"]


def _f(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def read_by_year(art: Path, benefit: str):
    """[(year, actual, expected, ae)] sorted by year, from ae_<b>_by_year.csv."""
    p = art / f"ae_{benefit}_by_year.csv"
    if not p.is_file():
        return []
    rows = []
    with open(p, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append((int(float(r["Year"])), _f(r["Actual"]), _f(r["Expected"]), _f(r["AE"])))
    return sorted(rows)


def read_termination(art: Path):
    """Per-diagnosis pooled termination evidence from ae_ip_termination.csv.

    NOTE: this file has NO year dimension (Diagnosis,DurationMonth,Exposed,
    Recovered,ObservedRate,AssumedRate,AE) — recovery findings legitimately
    carry years:null. Pooled A/E = sum(Recovered)/sum(Exposed*AssumedRate),
    the same statistic summary.json publishes (matches runner --termination-mean
    pooled). z is the Poisson z on pooled counts.
    """
    p = art / "ae_ip_termination.csv"
    if not p.is_file():
        return {}
    agg = {}
    with open(p, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                d = agg.setdefault(r["Diagnosis"], [0.0, 0.0])
                d[0] += float(r["Recovered"])
                d[1] += float(r["Exposed"]) * float(r["AssumedRate"])
            except (KeyError, ValueError):
                continue
    out = {}
    for diag, (rec, exp) in sorted(agg.items()):
        if exp <= 0:
            continue
        ae = rec / exp
        z = (rec - exp) / math.sqrt(exp)
        out[diag] = {
            "pooled_ae": round(ae, 3),
            "pooled_z": round(z, 1),
            "exposed_expected": round(exp, 0),
            "flag": "ANOMALOUS" if abs(z) >= 3 else ("watch" if abs(z) >= 2 else "clean"),
        }
    return out


def ols(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan"), float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return 0.0, float("nan")
    slope = sxy / sxx
    inter = my - slope * mx
    ss_res = sum((y - (slope * x + inter)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return slope, r2


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def sd(xs):
    n = len(xs)
    if n < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def best_step(rows):
    """Best split k: mean(ae[k:]) - mean(ae[:k]) as a step; returns (year_of_step,
    delta, score) where score = |delta| / pooled_sd * sqrt(effective_n)."""
    ae = [r[3] for r in rows]
    n = len(ae)
    best = (None, 0.0, 0.0)
    for k in range(2, n - 1):
        a, b = ae[:k], ae[k:]
        delta = mean(b) - mean(a)
        sa, sb = sd(a), sd(b)
        se = math.sqrt((sa * sa) / len(a) + (sb * sb) / len(b)) if sa == sa and sb == sb else float("nan")
        score = abs(delta) / se if se and se == se and se > 0 else 0.0
        if score > best[2]:
            best = (rows[k][0], delta, score)
    return best


def top_excursions(rows, k: int = 3, min_w: int = 2, floor: float = 3.0):
    """Up to k non-overlapping windows whose mean level differs from the rest.

    A line can carry more than one feature (e.g. a one-off jolt in 2020 and a
    separate drift from 2021); reporting only the single best-scoring window
    hides the others — observed on sc-d72b95."""
    ae = [r[3] for r in rows]
    n = len(ae)
    cands = []
    for i in range(n):
        for j in range(i + min_w - 1, n):
            inside, outside = ae[i:j + 1], ae[:i] + ae[j + 1:]
            if len(outside) < 3:
                continue
            d = mean(inside) - mean(outside)
            si, so = sd(inside), sd(outside)
            se = math.sqrt((si * si) / len(inside) + (so * so) / len(outside)) \
                if si == si and so == so else float("nan")
            score = abs(d) / se if se and se == se and se > 0 else 0.0
            cands.append((score, i, j, d))
    cands.sort(reverse=True)
    chosen = []
    for score, i, j, d in cands:
        if score < floor:
            break
        if any(not (j < ci or i > cj) for _, ci, cj, _ in chosen):
            continue                       # overlaps an already-chosen window
        chosen.append((score, i, j, d))
        if len(chosen) >= k:
            break
    return [(rows[i][0], rows[j][0], j - i + 1, round(d, 3), round(score, 1))
            for score, i, j, d in sorted(chosen, key=lambda x: x[1])]


def smooth_stats(rows, w: int = 3):
    """3-year centred moving average: noise-hiding ramps become visible levels.
    Returns (slope, r2, amplitude, [(year, ma)...]). Calibration on the
    OPTIMIZATION split: clean lines never exceed amplitude 0.051, every true
    control line is >= 0.082; drift lines fit the smoothed level with R2 ~0.86
    median (shock ~0.57, volatility ~0.30)."""
    ae = [r[3] for r in rows]
    yrs = [r[0] for r in rows]
    if len(ae) < w + 1:
        return None
    ma = [(yrs[i], sum(ae[i:i + w]) / w) for i in range(len(ae) - w + 1)]
    slope, r2 = ols([float(i) for i in range(len(ma))], [v for _, v in ma])
    amp = max(v for _, v in ma) - min(v for _, v in ma)
    return slope, r2, amp, ma


def best_excursion(rows, min_w: int = 2):
    """Widest/tightest window whose mean level differs from the rest of the
    series — the shape a bounded (confined, later-reverting) move makes, which
    a single-step split cannot see. Returns (from_year, to_year, width, delta,
    score) with score = |delta| / se(delta)."""
    ae = [r[3] for r in rows]
    n = len(ae)
    best = (None, None, 0, 0.0, 0.0)
    for i in range(n):
        for j in range(i + min_w - 1, n):
            inside, outside = ae[i:j + 1], ae[:i] + ae[j + 1:]
            if len(outside) < 3:
                continue
            d = mean(inside) - mean(outside)
            si, so = sd(inside), sd(outside)
            se = math.sqrt((si * si) / len(inside) + (so * so) / len(outside)) \
                if si == si and so == so else float("nan")
            score = abs(d) / se if se and se == se and se > 0 else 0.0
            width = j - i + 1
            better = score > best[4] + 1e-9 or (
                abs(score - best[4]) <= 1e-9 and width > best[2])
            if better:
                best = (rows[i][0], rows[j][0], width, d, score)
    return best


def yoy_stats(rows):
    """(empirical sd of YoY ae deltas, poisson-implied sd of those deltas).

    Poisson: Var(A/E) ~ 1/E per year, independent years -> Var(delta) ~ 1/E_t +
    1/E_{t-1}. Ratio >> 1 means the data is overdispersed vs Poisson."""
    ae = [r[3] for r in rows]
    exp_ = [r[2] for r in rows]
    deltas = [b - a for a, b in zip(ae, ae[1:])]
    emp = sd(deltas)
    pois = math.sqrt(mean([1 / e + 1 / p for e, p in zip(exp_[1:], exp_[:-1]) if e > 0 and p > 0]) / 2) if len(deltas) > 1 else float("nan")
    return emp, pois


def z_year(actual, expected):
    """Correct-null z under Poisson on counts (what a real analyst quotes)."""
    if expected > 0:
        return (actual - expected) / math.sqrt(expected)
    return float("nan")


def line_pack(rows):
    """Evidence dict for one benefit's by-year series."""
    if len(rows) < 4:
        return None
    years = [r[0] for r in rows]
    ae = [r[3] for r in rows]
    slope, r2 = ols([float(y) for y in years], ae)
    step_year, step_delta, step_score = best_step(rows)
    ex_from, ex_to, ex_w, ex_delta, ex_score = best_excursion(rows)
    ex_all = top_excursions(rows)
    sm = smooth_stats(rows)
    end_vs_base = None
    if sm:
        _vals = sorted(v for _, v in sm[3])
        _base = _vals[len(_vals) // 2]
        end_vs_base = sum(v for _, v in sm[3][-2:]) / 2 - _base
    emp_sd, pois_sd = yoy_stats(rows)
    disp = emp_sd / pois_sd if pois_sd and pois_sd == pois_sd and pois_sd > 0 else float("nan")
    # max consecutive same-direction YoY move (drift fingerprint)
    deltas = [b - a for a, b in zip(ae, ae[1:])]
    run = best_run = 0
    runsum = best_runsum = 0.0
    for d in deltas:
        if d > 0 and run >= 0:
            run += 1; runsum += d
        elif d < 0 and run <= 0:
            run -= 1; runsum += d
        else:
            run = 1 if d > 0 else -1; runsum = d
        if abs(run) > abs(best_run):
            best_run, best_runsum = run, runsum
    max_jump = max((abs(d) for d in deltas), default=0.0)
    mean_ae = mean(ae)
    # ---- TAIL SEGMENT (v1.5) ------------------------------------------------
    # What the line does in its FINAL years, compared with everything before.
    # Added because a large early event cancels the whole-window linear fit and
    # the end-vs-baseline figure: sc-d72b95 had a 2020 jolt plus a slow rise from
    # 2021 that reached the horizon, and the pack called that line "no strong
    # signal", so the rise was never reported. Calibrated on the OPTIMIZATION
    # split: this block fires on 11 lines, every one of them a real control whose
    # window reaches the horizon, and on none of the four lines of the clean book
    # (clean |gradient| <= 0.013 there, against 0.036-0.113 for the real ones).
    tail = None
    if len(rows) >= 6:
        k = 3
        tail_rows, prior_rows = rows[-k:], rows[:-k]
        t_slope, t_r2 = ols([float(r[0]) for r in tail_rows], [r[3] for r in tail_rows])
        t_mean = mean([r[3] for r in tail_rows])
        p_mean = mean([r[3] for r in prior_rows])
        level_vs_prior = t_mean - p_mean
        if (t_slope == t_slope and abs(t_slope) >= 0.03
                and t_r2 == t_r2 and t_r2 >= 0.80
                and abs(level_vs_prior) >= 0.03):
            tail = {
                "from": tail_rows[0][0],
                "to": tail_rows[-1][0],
                "gradient_per_yr": round(t_slope, 4),
                "r2": round(t_r2, 2),
                "level_vs_prior": round(level_vs_prior, 3),
                "direction": "up" if t_slope > 0 else "down",
                "values": [[r[0], round(r[3], 3)] for r in tail_rows],
            }
    return {
        "years": [years[0], years[-1]],
        "mean_ae": round(mean_ae, 3),
        "trend_gradient_per_yr": round(slope, 4) if slope == slope else None,
        "trend_r2": round(r2, 2) if r2 == r2 else None,
        "trend_total_move": round(slope * (years[-1] - years[0]), 3) if slope == slope else None,
        "best_step": {"at_year": step_year, "delta": round(step_delta, 3), "score": round(step_score, 1)} if step_year else None,
        "excursions": [{"from": a, "to": b, "width_years": w, "delta": d, "score": sc}
                       for a, b, w, d, sc in ex_all],
        "best_excursion": {"from": ex_from, "to": ex_to, "width_years": ex_w,
                           "delta": round(ex_delta, 3), "score": round(ex_score, 1)} if ex_from else None,
        "yoy_emp_sd": round(emp_sd, 4) if emp_sd == emp_sd else None,
        "yoy_poisson_sd": round(pois_sd, 4) if pois_sd == pois_sd else None,
        "overdispersion_ratio": round(disp, 2) if disp == disp else None,
        "longest_run": {"years": abs(best_run) + 1, "direction": "up" if best_run > 0 else "down", "total_move": round(best_runsum, 3)},
        "max_1yr_jump": round(max_jump, 3),
        "end_vs_baseline": round(end_vs_base, 3) if end_vs_base is not None else None,
        "tail_segment": tail,
        "onset_sharpness": (round(max_jump / abs(ex_delta), 2)
                            if ex_delta and abs(ex_delta) >= 0.05 else None),
        "smoothed": {
            "window": 3,
            "slope_per_yr": round(sm[0], 4) if sm else None,
            "r2": round(sm[1], 2) if sm else None,
            "amplitude": round(sm[2], 3) if sm else None,
            "from": sm[3][0][0] if sm else None,
            "to": sm[3][-1][0] if sm else None,
            "series": [[y, round(v, 3)] for y, v in sm[3]] if sm else None,
        } if sm else None,
        "per_year": [
            {"year": y, "ae": round(a, 3), "z_poisson": round(z, 1)}
            for (y, _, _, a), z in zip(rows, [z_year(r[1], r[2]) for r in rows])
        ],
    }


def profile(pk):
    """Descriptive evidence PROFILE for one line — never an anomaly claim.

    Factual by design: the pack states which *shape* dominates the evidence and
    the model decides whether that shape is a finding. Ordering matters — a
    coherent level excursion outranks everything else, because an excursion
    also inflates the dispersion ratio and can weaken a whole-window linear fit
    (the sc-042304 CI line: excursion score 20.1 at width 2, dispersion x6.3,
    trend R2 0.17 — an earlier rule order called that "no strong signal").

    Thresholds were tuned on the OPTIMIZATION split only; the heldout split
    never influenced them.
    """
    if not pk:
        return "insufficient-data"
    disp = pk.get("overdispersion_ratio") or 0
    move = abs(pk.get("trend_total_move") or 0)
    step = pk["best_step"]["score"] if pk.get("best_step") else 0
    r2 = pk.get("trend_r2") or 0
    run = (pk.get("longest_run") or {}).get("years") or 0
    runmv = abs((pk.get("longest_run") or {}).get("total_move") or 0)
    ex = pk.get("best_excursion") or {}
    ex_score, ex_w = ex.get("score") or 0, ex.get("width_years") or 0
    onset = pk.get("onset_sharpness")
    win = f"{ex.get('from')}-{ex.get('to')}"

    smd = pk.get("smoothed") or {}
    sm_amp, sm_r2 = smd.get("amplitude") or 0, smd.get("r2") or 0
    gradual = sm_amp >= 0.08 and sm_r2 >= 0.75      # calibrated: clean lines max amp 0.051
    if ex_score >= 8.0:   # optimization-split calibration: clean lines max 6.4
        if gradual:
            return (f"SHAPED-AND-GRADUAL: the smoothed (3y MA) level moves "
                    f"steadily (amplitude {sm_amp}, smoothed-fit R2 {sm_r2}) and the "
                    f"excursion accumulates across several years of small moves — a "
                    f"build-up. Use the MA series to read where the smoothed level "
                    f"leaves and returns to its own baseline, and report THAT span as "
                    f"the window; a move that builds over years and then "
                    f"flattens/reverts is a sustained move, not a one-off step")
        if onset is not None and onset >= 1.3:
            return (f"SHAPED-OSCILLATING: within {win} the biggest single-year move "
                    f"({pk.get('max_1yr_jump')}) is LARGER than the net excursion "
                    f"({ex.get('delta'):+.3f}) — the line swings around rather than "
                    f"holding a new level; weigh this as dispersion/scatter with a "
                    f"window, not as a level change")
        if onset is not None and onset >= 0.85:
            return (f"SHAPED-PULSE: the whole excursion ({win}, {ex_w} y, "
                    f"{ex.get('delta'):+.3f}) arrives in essentially ONE year and then "
                    f"holds flat (onset {onset}) — an abrupt one-off level change, "
                    f"however many years it lasts; report the span it covers and note "
                    f"that it is not a gradual build-up")
        return (f"SHAPED: level excursion over {ex_w} y ({win}, {ex.get('delta'):+.3f}, "
                f"score {ex_score}) — read the onset row and the yearly table to "
                f"decide between a build-up and a one-off change")
    if disp >= 4.5 and ex_score < 6.0 and (onset or 0) >= 1.2:
        return ("scatter-dominant: the largest single-year move exceeds the net level "
                "change and year-to-year scatter is far above the Poisson expectation "
                "— Poisson z-scores are INVALID here; if this scatter is the finding, "
                "say so for THIS line and give the years where it is elevated")
    if step >= 6.5 and r2 < 0.3:
        return ("step-dominant: one abrupt level change, weak linear fit over the "
                "whole window — check the yearly table for the break year(s)")
    if gradual and sm_amp >= 0.10:
        return (f"sustained-move (smoothed): the 3-year smoothed level rises/falls "
                f"steadily from {smd.get('from')} to {smd.get('to')} (amplitude "
                f"{sm_amp}, fit R2 {sm_r2}) with a weak whole-window linear fit — "
                f"report the smoothed span as the window and note whether it "
                f"persists to the horizon or is confined/reverting")
    if r2 >= 0.45 and move >= 0.12:
        return ("sustained-move: strong linear fit across the window — check whether "
                "it persists to the horizon or is confined/reverting")
    if run >= 6 and runmv >= 0.15:
        return ("sustained-move candidate: long same-direction run — check the yearly "
                "table; fits may be weak if the move is bounded")
    if ex_score >= 4.0 and ex_w >= 4:
        return (f"possible multi-year excursion ({win}, {ex_w} y, "
                f"{ex.get('delta'):+.3f}, score {ex_score}): not decisive on its own "
                f"— check the yearly table for whether the move builds up gradually "
                f"or jumps in one year")
    return "no strong signal — judge from the yearly table and null-validity columns"


def _longest_consecutive(years: list[int]) -> list[int]:
    """Longest run of consecutive years (a genuine episode, not scattered years)."""
    if not years:
        return []
    ys = sorted(years)
    best = cur = [ys[0]]
    for y in ys[1:]:
        if y == cur[-1] + 1:
            cur.append(y)
        else:
            cur = [y]
        if len(cur) > len(best):
            best = list(cur)
    return best


def build_pack(scenario_dir: Path) -> dict:
    art = scenario_dir / "artifacts"
    if not art.is_dir():
        art = scenario_dir  # tolerate flat layout
    pack = {"scenario": scenario_dir.name, "benefits": {}}
    for b in BENEFITS:
        pk = line_pack(read_by_year(art, b))
        if pk:
            pk["profile"] = profile(pk)
            pack["benefits"][b] = pk
    # ---- cross-line view: do several lines move together? -------------------
    # Calibrated on the optimization split: a clean line's smoothed level never
    # wanders more than ~0.05 from its own mean, so 0.08 marks real movement.
    per_year: dict[int, list[str]] = {}
    for b, pk in pack["benefits"].items():
        series = ((pk.get("smoothed") or {}).get("series")) or []
        if len(series) < 4:
            continue
        vals = sorted(v for _, v in series)
        m = vals[len(vals) // 2]          # median = robust baseline
        for y, v in series:
            if abs(v - m) > 0.08:
                per_year.setdefault(y, []).append(b)
    # A second, volatility-specific view: how many lines take an unusually big
    # year-on-year swing in the SAME year (a coordinated dispersion event raises
    # scatter without necessarily moving the level).
    swings: dict[int, list[str]] = {}
    for b, pk in pack["benefits"].items():
        rows = read_by_year(art, b)
        if len(rows) < 6:
            continue
        ae = {r[0]: r[3] for r in rows}
        ys = sorted(ae)
        deltas = [(ys[i], abs(ae[ys[i]] - ae[ys[i - 1]])) for i in range(1, len(ys))]
        typical = sorted(d for _, d in deltas)[len(deltas) // 2] or 1e-9
        for y, d in deltas:
            if d > 2.5 * typical:
                swings.setdefault(y, []).append(b)
    if swings:
        for b, pk in pack["benefits"].items():
            pass
    if per_year or swings:
        counts = {y: len(v) for y, v in sorted(per_year.items())}
        swing_counts = {y: len(v) for y, v in sorted(swings.items())}
        pack["cross_line"] = {
            "counts": counts,
            "swing_counts": swing_counts,
            "max_lines": max(counts.values() or [0]),
            "max_swings": max(swing_counts.values() or [0]),
            "coordinated_years": _longest_consecutive([y for y, c in counts.items() if c >= 3]),
            "coordinated_swings": _longest_consecutive([y for y, c in swing_counts.items() if c >= 3]),
        }

    # tell each affected line that it is part of a book-wide swing episode
    eps = _longest_consecutive([y for y, c in
                                {y: len(v) for y, v in sorted(swings.items())}.items() if c >= 3])
    if len(eps) >= 2:
        for y in eps:
            for b in swings.get(y, []):
                pack["benefits"][b]["coordinated_swing"] = [eps[0], eps[-1]]
    term = read_termination(art)
    if term:
        pack["ip_termination"] = term
    return pack


def render_text(pack: dict) -> str:
    L = ["COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)",
         "Reading guide: a profile describes EVIDENCE, it is not a finding. Mild "
         "overdispersion (x2.5-6.5) is the normal texture of this book and is never "
         "by itself an anomaly; small age/duration cells (tiny expected counts) are "
         "unreliable however extreme their A/E looks.", ""]
    for b, pk in pack["benefits"].items():
        L.append(f"[{b.upper()}] mean A/E {pk['mean_ae']} | evidence profile: {pk['profile']}")
        L.append(f"  trend: gradient {pk['trend_gradient_per_yr']}/yr, R2 {pk['trend_r2']}, total {pk['trend_total_move']}")
        if pk.get("best_step"):
            s = pk["best_step"]
            L.append(f"  step: {s['delta']:+.3f} at {s['at_year']} (score {s['score']})")
        exs = pk.get("excursions") or []
        if exs:
            L.append("  excursions (windows whose level differs from the rest, best first): "
                     + "; ".join(f"{e['from']}-{e['to']} ({e['width_years']}y) {e['delta']:+.3f} "
                                 f"score {e['score']}" for e in exs))
        od = pk["overdispersion_ratio"] or 0
        ex_s = (pk.get("best_excursion") or {}).get("score") or 0
        if od >= 6.5 and ex_s >= 6.0:
            tag = ("Poisson z INVALID, but the scatter is largely produced by the "
                   "excursion above — not an independent dispersion signal")
        elif od >= 6.5:
            tag = "Poisson null INVALID on this line"
        elif od >= 2.5:
            tag = ("mild overdispersion — z-scores indicative only; this alone is "
                   "NOT an anomaly")
        else:
            tag = "Poisson null approximately valid"
        L.append(f"  YoY sd: empirical {pk['yoy_emp_sd']} vs Poisson {pk['yoy_poisson_sd']} "
                 f"-> overdispersion x{od} ({tag})")
        onset = pk.get("onset_sharpness")
        if onset:
            if onset >= 1.3:
                otext = ("the biggest single-year move EXCEEDS the net excursion — the "
                         "line oscillates rather than holding a new level")
            elif onset >= 0.85:
                otext = ("essentially the whole excursion arrives in ONE year, then "
                         "holds — a one-off level change, not a build-up")
            else:
                otext = ("the excursion accumulates across several years of small "
                         "moves — a build-up, not a one-off jump")
            L.append(f"  onset: max 1yr move / excursion size = {onset} ({otext})")
        L.append(f"  longest run: {pk['longest_run']['years']}y {pk['longest_run']['direction']} ({pk['longest_run']['total_move']:+.3f}) | max 1yr jump {pk['max_1yr_jump']}")
        if pk.get("coordinated_swing"):
            L.append(f"  NOTE: this line is one of several taking unusually large swings in "
                     f"{pk['coordinated_swing'][0]}-{pk['coordinated_swing'][1]} — the book "
                     f"became erratic as a whole; weigh a book-wide dispersion reading "
                     f"(and still report it for every affected line)")
        evb = pk.get("end_vs_baseline")
        if evb is not None and abs(evb) >= 0.05:
            L.append(f"  level at the END of the series: {evb:+.3f} versus this line's own "
                     f"baseline (calibration: clean lines stay within 0.008) — the "
                     f"movement does NOT return to where it started")
        tail = pk.get("tail_segment")
        if tail:
            L.append(f"  TAIL: in the FINAL years {tail['from']}-{tail['to']} the line moves "
                     f"steadily {tail['direction']} ({tail['gradient_per_yr']:+.3f}/yr, fit "
                     f"R2 {tail['r2']}), ending {tail['level_vs_prior']:+.3f} against the "
                     f"years before that (values " +
                     " ".join(f"{y}:{v:.2f}" for y, v in tail["values"]) +
                     f"). Calibration: clean lines never reach this block (|gradient| <= "
                     f"0.013), while genuine slow movements do — a steady final-years move "
                     f"that leaves the level away from its earlier value is a sustained "
                     f"move in its own right, so report it with THESE years even when an "
                     f"earlier event on the same line is bigger and already reported")
        if pk.get("smoothed"):
            sm_ = pk["smoothed"]
            L.append(f"  smoothed 3y MA: amplitude {sm_['amplitude']} over "
                     f"{sm_['from']}-{sm_['to']}, fit R2 {sm_['r2']} "
                     f"(gradient {sm_['slope_per_yr']}/yr)")
            if sm_.get("series"):
                L.append("    MA series: " + " ".join(f"{y}:{v:.2f}"
                                                      for y, v in sm_["series"]))
        L.append("  yearly: " + " ".join(f"{p['year']}:{p['ae']:.2f}(z{p['z_poisson']:+.1f})" for p in pk["per_year"]))
        L.append("")
    cl = pack.get("cross_line")
    if cl:
        L.append(f"[CROSS-LINE] lines whose smoothed level sits >0.08 from their own "
                 f"baseline, by year: " +
                 " ".join(f"{y}:{c}" for y, c in cl["counts"].items()))
        L.append("  lines taking an unusually large year-on-year swing (>2.5x their "
                 "own median move), by year: " +
                 " ".join(f"{y}:{c}" for y, c in cl["swing_counts"].items()))
        if len(cl.get("coordinated_swings") or []) >= 2:
            ys = cl["coordinated_swings"]
            L.append(f"  -> {cl['max_swings']} of 4 lines swing together in "
                     f"{ys[0]}-{ys[-1]}: a COORDINATED dispersion event is plausible — "
                     f"if that is your reading, report it for EACH affected line with "
                     f"the shared years")
        if len(cl.get("coordinated_years") or []) >= 2:
            L.append(f"  -> {cl['max_lines']} of 4 lines move together in "
                     f"{cl['coordinated_years'][0]}-{cl['coordinated_years'][-1]}: a "
                     f"COORDINATED move, so weigh one systemic explanation and report "
                     f"it for EACH affected line (the answer schema has no 'all' "
                     f"benefit) rather than four unrelated stories")
        L.append("")
    if "ip_termination" in pack:
        L.append("[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)")
        for diag, t in pack["ip_termination"].items():
            L.append(f"  {diag}: pooled A/E {t['pooled_ae']} (z {t['pooled_z']:+.1f}, expected {t['exposed_expected']:.0f}) -> {t['flag']}")
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenario_dir", help="data/eval/<split>/<sc-id>")
    ap.add_argument("--text", action="store_true", help="render human-readable instead of JSON")
    a = ap.parse_args(argv)
    pack = build_pack(Path(a.scenario_dir))
    print(render_text(pack) if a.text else json.dumps(pack, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
