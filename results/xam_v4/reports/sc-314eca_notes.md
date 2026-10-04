# Reviewer notes — sc-314eca (sys_vol_macro_2019_2021, systemic volatility)

> SCORER-SIDE — contains ground truth. Companion to `sc-314eca_behavior.md`.

## Headline

Truth: ONE systemic control — volatility σ=0.25 on **all benefits**,
window [2019,2021]. The model, all 3 runs, correctly locked window
(2019–2021) and correctly found every line swung wildly, but *decomposed*
the single systemic control into per-benefit findings: Death "shock
increase", CI "shock increase", TPD volatility/dispersion (runs 1–2) or two
single-year TPD shocks (run 3), IP "shock increase". Correct z-magnitudes
throughout (e.g. CI 2020 1.365, z≈12.9).

**Scorer: strict 2/3 (corrected), 0/3 before the volatility-direction fix**
— the two loose hits carried a `volatility/dispersion` finding whose
direction was mis-expected from σ (see sc-2d248f notes fix note). Run 3
lost loose too because it named TPD as two shocks instead of volatility.

## Interpretation

- The model never produced the word "all benefits" — the systemic nature
  is visible (it independently flagged every line in the same window) but
  the JSON schema forces per-benefit entries, so the *systemic* family is
  almost unscoreable strictly unless one finding matches "all". The
  scorer's benefit rule (`all` → any benefit) lets a per-benefit volatility
  finding carry the hit; only runs that labeled it volatility got that.
- Decomposition is a legitimate analytic style — a real actuary WOULD
  report per-line shocks. The FP=11 headline is inflated by rubric
  mechanics (one control vs 4–5 findings; see sc-4a7f9e notes for the
  matched_idx artifact — same here: 3 of the per-benefit findings overlap
  the same single control).
- No fabricated numbers: all quoted A/E values and claim excesses match
  the CSVs (spot-checked CI 1.365/1.153, TPD 0.575, IP 1.283).

## Numbers for the record

3/3 OK, finish=stop, prompt 2,479 ×3, no tools, no code.
Wall 2,686/1,803/1,770 s; completion 38,259/28,001/27,684 tokens (systemic
scenarios provoke the longest reasoning). Seeds 1234/1235/1236, canonical
samplers, no max_tokens, stream=true.
