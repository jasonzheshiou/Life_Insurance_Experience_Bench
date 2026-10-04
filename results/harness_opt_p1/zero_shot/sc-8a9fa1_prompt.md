# Prompt — sc-8a9fa1

## system

You are an actuary reviewing synthetic life-insurance experience data for a
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
    flat-topped or single-year excursions. If the excursion rises year over year
    before it peaks or reverts, prefer drift.
  * volatility: an increase in year-to-year dispersion with an unchanged level.
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
}

## user

Scenario: sc-8a9fa1

Files available (paths are relative to the scenario folder):
  - artifacts/ae_ci.csv
  - artifacts/ae_ci_age_gender.csv
  - artifacts/ae_ci_age_gender.png
  - artifacts/ae_ci_by_year.csv
  - artifacts/ae_ci_by_year.png
  - artifacts/ae_death.csv
  - artifacts/ae_death_age_gender.csv
  - artifacts/ae_death_age_gender.png
  - artifacts/ae_death_by_year.csv
  - artifacts/ae_death_by_year.png
  - artifacts/ae_ip.csv
  - artifacts/ae_ip_age_gender.csv
  - artifacts/ae_ip_age_gender.png
  - artifacts/ae_ip_by_year.csv
  - artifacts/ae_ip_by_year.png
  - artifacts/ae_ip_termination.csv
  - artifacts/ae_ip_termination_by_month.csv
  - artifacts/ae_ip_termination_by_month.png
  - artifacts/ae_tpd.csv
  - artifacts/ae_tpd_age_gender.csv
  - artifacts/ae_tpd_age_gender.png
  - artifacts/ae_tpd_by_year.csv
  - artifacts/ae_tpd_by_year.png
  - artifacts/summary.json
  - benchmarks/CI.csv
  - benchmarks/Death.csv
  - benchmarks/IP.csv
  - benchmarks/TPD.csv
  - ci_claims.csv
  - death_claims.csv
  - exposure.csv
  - ip_claims.csv
  - scenario_id.txt
  - tpd_claims.csv

summary.json (overall A/E per benefit, claim counts):
{
  "benefits": {
    "Death": {
      "overall_ae": 0.9972,
      "claims": 4986
    },
    "CI": {
      "overall_ae": 0.9989,
      "claims": 11987
    },
    "TPD": {
      "overall_ae": 0.9986,
      "claims": 7989
    },
    "IP": {
      "overall_ae": 1.0003,
      "claims": 15004,
      "overall_termination_ae": 1.0021
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=208  Expected=240  AE=0.868
  2016: Actual=314  Expected=290  AE=1.084
  2017: Actual=421  Expected=337  AE=1.248
  2018: Actual=593  Expected=390  AE=1.522
  2019: Actual=328  Expected=447  AE=0.734
  2020: Actual=578  Expected=508  AE=1.137
  2021: Actual=542  Expected=576  AE=0.942
  2022: Actual=592  Expected=652  AE=0.908
  2023: Actual=680  Expected=735  AE=0.925
  2024: Actual=730  Expected=826  AE=0.884

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=592  Expected=596  AE=0.993
  2016: Actual=710  Expected=720  AE=0.986
  2017: Actual=797  Expected=837  AE=0.952
  2018: Actual=982  Expected=963  AE=1.020
  2019: Actual=1,113  Expected=1,097  AE=1.014
  2020: Actual=1,258  Expected=1,239  AE=1.015
  2021: Actual=1,322  Expected=1,386  AE=0.954
  2022: Actual=1,598  Expected=1,548  AE=1.032
  2023: Actual=1,714  Expected=1,719  AE=0.997
  2024: Actual=1,901  Expected=1,893  AE=1.004

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=482  Expected=487  AE=0.990
  2016: Actual=569  Expected=562  AE=1.013
  2017: Actual=629  Expected=625  AE=1.007
  2018: Actual=702  Expected=690  AE=1.017
  2019: Actual=778  Expected=757  AE=1.027
  2020: Actual=774  Expected=826  AE=0.937
  2021: Actual=915  Expected=897  AE=1.020
  2022: Actual=973  Expected=974  AE=0.999
  2023: Actual=1,060  Expected=1,052  AE=1.008
  2024: Actual=1,107  Expected=1,130  AE=0.979

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,016  Expected=1,013  AE=1.003
  2016: Actual=1,185  Expected=1,142  AE=1.038
  2017: Actual=1,278  Expected=1,241  AE=1.030
  2018: Actual=1,326  Expected=1,342  AE=0.988
  2019: Actual=1,437  Expected=1,441  AE=0.997
  2020: Actual=1,531  Expected=1,545  AE=0.991
  2021: Actual=1,591  Expected=1,653  AE=0.963
  2022: Actual=1,769  Expected=1,768  AE=1.000
  2023: Actual=1,884  Expected=1,876  AE=1.004
  2024: Actual=1,987  Expected=1,980  AE=1.004

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.993
  Cardiovascular: 0.992
  Injury/Accident: 0.984
  Mental Health: 1.018
  Musculoskeletal: 0.988
  Other: 1.022

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.025 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0243/yr, R2 0.1, total -0.219
  step: -0.259 at 2019 (score 1.8)
  excursion: 2017-2018 (2y) +0.450 (score 3.1)
  YoY sd: empirical 0.3485 vs Poisson 0.0477 -> overdispersion x7.3 (Poisson null INVALID on this line)
  longest run: 4y up (+0.654) | max 1yr jump 0.787
  smoothed 3y MA: amplitude 0.379 over 2015-2022, fit R2 0.62 (gradient -0.0433/yr)
    MA series: 2015:1.07 2016:1.28 2017:1.17 2018:1.13 2019:0.94 2020:0.99 2021:0.93 2022:0.91
  yearly: 2015:0.87(z-2.0) 2016:1.08(z+1.4) 2017:1.25(z+4.6) 2018:1.52(z+10.3) 2019:0.73(z-5.6) 2020:1.14(z+3.1) 2021:0.94(z-1.4) 2022:0.91(z-2.4) 2023:0.93(z-2.0) 2024:0.88(z-3.3)

[CI] mean A/E 0.997 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0023/yr, R2 0.07, total 0.021
  step: +0.028 at 2018 (score 1.8)
  excursion: 2018-2020 (3y) +0.028 (score 2.6)
  YoY sd: empirical 0.046 vs Poisson 0.0305 -> overdispersion x1.51 (Poisson null approximately valid)
  longest run: 3y down (-0.041) | max 1yr jump 0.078
  smoothed 3y MA: amplitude 0.04 over 2015-2022, fit R2 0.4 (gradient 0.0033/yr)
    MA series: 2015:0.98 2016:0.99 2017:0.99 2018:1.02 2019:0.99 2020:1.00 2021:0.99 2022:1.01
  yearly: 2015:0.99(z-0.2) 2016:0.99(z-0.4) 2017:0.95(z-1.4) 2018:1.02(z+0.6) 2019:1.01(z+0.5) 2020:1.01(z+0.5) 2021:0.95(z-1.7) 2022:1.03(z+1.3) 2023:1.00(z-0.1) 2024:1.00(z+0.2)

[TPD] mean A/E 1.0 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0015/yr, R2 0.03, total -0.014
  step: -0.022 at 2020 (score 1.4)
  excursion: 2018-2019 (2y) +0.028 (score 2.6)
  YoY sd: empirical 0.0465 vs Poisson 0.0364 -> overdispersion x1.28 (Poisson null approximately valid)
  longest run: 3y up (+0.020) | max 1yr jump 0.09
  smoothed 3y MA: amplitude 0.032 over 2015-2022, fit R2 0.2 (gradient -0.002/yr)
    MA series: 2015:1.00 2016:1.01 2017:1.02 2018:0.99 2019:0.99 2020:0.98 2021:1.01 2022:0.99
  yearly: 2015:0.99(z-0.2) 2016:1.01(z+0.3) 2017:1.01(z+0.2) 2018:1.02(z+0.5) 2019:1.03(z+0.7) 2020:0.94(z-1.8) 2021:1.02(z+0.6) 2022:1.00(z-0.0) 2023:1.01(z+0.2) 2024:0.98(z-0.7)

[IP] mean A/E 1.002 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0028/yr, R2 0.16, total -0.025
  step: -0.031 at 2018 (score 2.6)
  excursion: 2016-2017 (2y) +0.040 (score 6.4)
  YoY sd: empirical 0.026 vs Poisson 0.0263 -> overdispersion x0.99 (Poisson null approximately valid)
  longest run: 3y down (-0.050) | max 1yr jump 0.042
  smoothed 3y MA: amplitude 0.04 over 2015-2022, fit R2 0.49 (gradient -0.0044/yr)
    MA series: 2015:1.02 2016:1.02 2017:1.00 2018:0.99 2019:0.98 2020:0.98 2021:0.99 2022:1.00
  yearly: 2015:1.00(z+0.1) 2016:1.04(z+1.3) 2017:1.03(z+1.1) 2018:0.99(z-0.4) 2019:1.00(z-0.1) 2020:0.99(z-0.4) 2021:0.96(z-1.5) 2022:1.00(z+0.0) 2023:1.00(z+0.2) 2024:1.00(z+0.2)

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.993 (z -0.2, expected 1271) -> clean
  Cardiovascular: pooled A/E 0.992 (z -0.2, expected 899) -> clean
  Injury/Accident: pooled A/E 0.984 (z -0.6, expected 1446) -> clean
  Mental Health: pooled A/E 1.018 (z +1.2, expected 4360) -> clean
  Musculoskeletal: pooled A/E 0.988 (z -0.7, expected 3338) -> clean
  Other: pooled A/E 1.022 (z +0.7, expected 1168) -> clean

HARNESS MODE — you are not limited to eyeballing the tables above.

1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact
   CSVs) is appended at the end of this message. Trust its arithmetic over
   mental math, but the final judgement is yours: confirm or override its
   per-line heuristic verdicts.

2) You may compute anything else you need. To use the tool, reply with ONLY a
   JSON object (no other text):
     {"tool": "python", "code": "<python source as one JSON string>"}
   The code runs with the scenario's artifacts/ directory as cwd (open files
   by relative path, e.g. open("ae_death_by_year.csv")); plain stdlib Python
   (csv, math, statistics); 10 s limit; output is returned verbatim.
   You get at most 4 tool calls. NEVER write files or read outside artifacts/.

3) When done — with or without tools — reply with ONLY the final JSON object
   in the required shape. Do not put tool requests inside that final JSON.

4) Discipline (these are scored):
   * Overdispersion is NOT a finding by itself. Report a dispersion
     finding only when the elevated year-to-year scatter is the material
     anomaly for that line (roughly x6 or more versus the Poisson expectation,
     with a level that stays flat). Mild overdispersion, and any line whose
     evidence profile says "no strong signal", must NOT be reported as a
     finding merely because its scatter is above Poisson.
   * Small cells are not evidence: age-band or duration-month A/E values rest
     on tiny expected counts and go extreme by chance. Never report a
     book-level anomaly from such a cell unless the same effect is visible in
     the by-year series or the pooled line.
   * Findings you considered and rejected for these reasons do not appear in
     the "findings" array at all.

