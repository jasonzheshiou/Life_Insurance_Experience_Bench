# Reviewer notes — sc-8d3b47 (sys_drift_diverge_2018_2024, systemic)

> SCORER-SIDE — ground truth. Companion to `sc-8d3b47_behavior.md`.

## Headline
Truth: TWO co-migrating drifts [2018,2024] — Death +0.06/yr (increase),
CI −0.04/yr (decrease). Model **6/6 strict (post scorer-fix), 6/6 loose**:
every run named both benefits, both patterns "drift", BOTH directions
correct (Death/increase c0.85–0.92; CI/decrease c0.85–0.95). FP=2: the
"other — no material anomaly" notes on TPD/IP (run1). Best systemic-family
result in the pool — same long-drift conditions as sc-63f1c7 (6-year
persistent trends, cumulative ~+40%/−25%).

## Interpretation
When boundedness doesn't bite (window extends to the last year of data,
no post-window snap-back), this model handles exactly the scenario type
that broke sc-137901 — divergent simultaneous drifts, correctly signed.
Reinforces the pool-level conclusion: **the drift misses are a
boundary-ambiguity problem, not a trend-detection problem.**

## Scorer correction (material)
Death-drift answers were failed pre-fix by the drift-direction bug
(+0.06 rate read as ratio<1 ⇒ "decrease" expected); fixed 2026-09-02
(handoff §6.5): strict 3/6 → **6/6**. CI side passed pre-fix only because
a negative rate coincidentally compares <1.0.

## Numbers
3/3 OK, finish=stop. Wall 838/599/666 s; completion 14,606/10,898/11,965.
Canonical settings, seeds 1234/1235/1236.
