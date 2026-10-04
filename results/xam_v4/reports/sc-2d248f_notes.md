# Reviewer notes — sc-2d248f (volatility_ip_sigma_03, volatility)

> SCORER-SIDE — contains ground truth. Companion to `sc-2d248f_behavior.md`.

## Headline

**Best-performing scenario type in the pool: 3/3 exact detection** (benefit,
pattern, direction, full window, conf 0.95–0.97) — but auto-scored strict
0/3 due to a **scorer bug** (below). Model: IP, years [2015,2024],
volatility/dispersion, annual A/E range 0.413–1.654, sd ≈0.38 vs Poisson
noise ≈0.03 ("roughly 10× expected noise"), overall level unchanged ≈1.00.
Truth: volatility σ=0.3 on IP over 2015–2024. Everything matches.

## Scorer defect found here (FIXED in score_xam.py, documented)

Volatility controls carry `factor = sigma` (0.3), but `dir_from_factor()`
compared that float to 1.0 and derived expected direction "decrease".
The manifest's own `signature.direction` is `"dispersion"`. The model's
correct answer ("dispersion") was therefore failed on `direction_ok`.
Fix: volatility-type controls expect `dispersion` (tolerant of
increase/decrease wording), matching existing handling elsewhere.
**Old strict 0/3 → corrected strict 3/3.** Same bug also deflated
sc-314eca (sys_vol): old strict 0/3 → corrected 2/3. Applied 2026-09-02
after the 6-scenario sweep finished; totals in index/final table use the
fixed scorer, old numbers kept in each scenario's notes.

## Behavioral observations

- Run 1 quoted per-year sigma violations (2015 −18.7σ, 2016 +22σ) —
  correct Poisson reasoning at 1000-claim scale.
- Run 3 additionally hedged the familiar Death 2016 blip at conf 0.45
  (same honest borderline item as elsewhere; rubric FP, not a fabrication).
- Fastest confident non-recovery answers so far (~13 min/run): volatility
  is "easy" for this model when it's localized to one benefit line.

## Numbers for the record

3/3 OK, finish=stop, prompt 2,479 ×3 (statelessness), no tools, no code.
Wall 694/808/788 s; completion 12,011/11,304/11,831 tokens.
Seeds 1234/1235/1236, canonical samplers, no max_tokens, stream=true.
