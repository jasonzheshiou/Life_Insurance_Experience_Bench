# Reviewer notes — sc-63f1c7 (mixed_drift_death_shock_ci, mixed)

> SCORER-SIDE — ground truth. Companion to `sc-63f1c7_behavior.md`.

## Headline
Truth: TWO controls — Death drift +0.08/yr [2019,2024] AND CI shock ×1.4
[2021,2021]. Model: **6/6 strict (post scorer-fix), 6/6 loose** — the
first scenario where it named **"drift" correctly, all 3 runs** (Death/
drift/increase, conf 0.85–0.90) while simultaneously nailing the CI shock
(×1.4 single year, conf 0.88–0.98). FP=4: the "other/dispersion — no
material anomaly" statements for TPD/IP in runs 1&3 (schema artifact, see
sc-4a7f9e notes).

## Why drift worked here when sc-137901/3c83fd failed
This drift is LONG (6 years, +0.08/yr ⇒ ~+50% cumulative by 2024) and
never reverses within the table; the model saw a monotone climb it could
not explain as shock. The earlier drift misses were bounded/short
(2016-2019) or hidden under noise. Prediction: long persistent drifts are
detectable; bounded ones get mislabeled — consistent across the pool now.

## Scorer correction (material)
Before this run, the drift-family direction bug (drift `factor` = signed
per-year rate; `dir_from_factor()` read +0.08 as ratio<1 ⇒ expected
"decrease") silently failed the model's 3 correct Death-drift answers.
Fixed 2026-09-02 in `score_xam.py` (see handoff §6.5): strict for this
scenario was 3/6 → **6/6**. Loose (6/6) unaffected.

## Numbers
3/3 OK, finish=stop, wall 863/754/910 s, completion 14,468/11,440/14,585.
Canonical settings, seeds 1234/1235/1236, prompt identical ×3.
