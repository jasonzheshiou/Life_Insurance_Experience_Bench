# Prompt — sc-d72b95

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

Scenario: sc-d72b95

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
      "overall_ae": 1.004,
      "claims": 5020
    },
    "CI": {
      "overall_ae": 1.0143,
      "claims": 12171
    },
    "TPD": {
      "overall_ae": 1.0063,
      "claims": 8050
    },
    "IP": {
      "overall_ae": 1.0023,
      "claims": 15035,
      "overall_termination_ae": 1.0024
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=217  Expected=240  AE=0.906
  2016: Actual=240  Expected=290  AE=0.829
  2017: Actual=282  Expected=337  AE=0.836
  2018: Actual=350  Expected=390  AE=0.898
  2019: Actual=417  Expected=447  AE=0.934
  2020: Actual=666  Expected=508  AE=1.310
  2021: Actual=559  Expected=576  AE=0.971
  2022: Actual=642  Expected=652  AE=0.985
  2023: Actual=806  Expected=735  AE=1.097
  2024: Actual=841  Expected=826  AE=1.018

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=574  Expected=596  AE=0.962
  2016: Actual=671  Expected=720  AE=0.932
  2017: Actual=843  Expected=837  AE=1.007
  2018: Actual=928  Expected=963  AE=0.963
  2019: Actual=1,028  Expected=1,097  AE=0.937
  2020: Actual=1,436  Expected=1,239  AE=1.159
  2021: Actual=1,250  Expected=1,386  AE=0.902
  2022: Actual=1,515  Expected=1,548  AE=0.978
  2023: Actual=1,771  Expected=1,719  AE=1.030
  2024: Actual=2,155  Expected=1,893  AE=1.138

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=480  Expected=487  AE=0.986
  2016: Actual=585  Expected=562  AE=1.041
  2017: Actual=640  Expected=625  AE=1.025
  2018: Actual=710  Expected=690  AE=1.029
  2019: Actual=765  Expected=757  AE=1.010
  2020: Actual=796  Expected=826  AE=0.963
  2021: Actual=908  Expected=897  AE=1.013
  2022: Actual=981  Expected=974  AE=1.007
  2023: Actual=1,071  Expected=1,052  AE=1.018
  2024: Actual=1,114  Expected=1,130  AE=0.985

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,036  Expected=1,013  AE=1.023
  2016: Actual=1,175  Expected=1,142  AE=1.029
  2017: Actual=1,236  Expected=1,241  AE=0.996
  2018: Actual=1,341  Expected=1,342  AE=0.999
  2019: Actual=1,436  Expected=1,441  AE=0.997
  2020: Actual=1,544  Expected=1,545  AE=0.999
  2021: Actual=1,616  Expected=1,653  AE=0.978
  2022: Actual=1,776  Expected=1,768  AE=1.004
  2023: Actual=1,872  Expected=1,876  AE=0.998
  2024: Actual=2,003  Expected=1,980  AE=1.012

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.999
  Cardiovascular: 1.010
  Injury/Accident: 0.974
  Mental Health: 1.005
  Musculoskeletal: 1.017
  Other: 0.983

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 0.978 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0256/yr, R2 0.3, total 0.23
  step: +0.185 at 2019 (score 3.1)
  excursion: 2016-2017 (2y) -0.182 (score 3.8)
  YoY sd: empirical 0.1888 vs Poisson 0.0477 -> overdispersion x3.95 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  longest run: 5y up (+0.481) | max 1yr jump 0.376
  smoothed 3y MA: amplitude 0.234 over 2015-2022, fit R2 0.62 (gradient 0.0318/yr)
    MA series: 2015:0.86 2016:0.85 2017:0.89 2018:1.05 2019:1.07 2020:1.09 2021:1.02 2022:1.03
  yearly: 2015:0.91(z-1.5) 2016:0.83(z-2.9) 2017:0.84(z-3.0) 2018:0.90(z-2.0) 2019:0.93(z-1.4) 2020:1.31(z+7.0) 2021:0.97(z-0.7) 2022:0.98(z-0.4) 2023:1.10(z+2.6) 2024:1.02(z+0.5)

[CI] mean A/E 1.001 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0131/yr, R2 0.21, total 0.118
  step: +0.067 at 2017 (score 1.9)
  excursion: 2015-2016 (2y) -0.067 (score 1.9)
  YoY sd: empirical 0.1329 vs Poisson 0.0305 -> overdispersion x4.35 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  longest run: 4y up (+0.236) | max 1yr jump 0.257
  smoothed 3y MA: amplitude 0.082 over 2015-2022, fit R2 0.43 (gradient 0.0083/yr)
    MA series: 2015:0.97 2016:0.97 2017:0.97 2018:1.02 2019:1.00 2020:1.01 2021:0.97 2022:1.05
  yearly: 2015:0.96(z-0.9) 2016:0.93(z-1.8) 2017:1.01(z+0.2) 2018:0.96(z-1.1) 2019:0.94(z-2.1) 2020:1.16(z+5.6) 2021:0.90(z-3.7) 2022:0.98(z-0.8) 2023:1.03(z+1.3) 2024:1.14(z+6.0)

[TPD] mean A/E 1.008 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0021/yr, R2 0.07, total -0.019
  step: -0.021 at 2020 (score 1.5)
  excursion: 2016-2018 (3y) +0.034 (score 3.8)
  YoY sd: empirical 0.0346 vs Poisson 0.0364 -> overdispersion x0.95 (Poisson null approximately valid)
  longest run: 3y down (-0.066) | max 1yr jump 0.056
  smoothed 3y MA: amplitude 0.037 over 2015-2022, fit R2 0.36 (gradient -0.0033/yr)
    MA series: 2015:1.02 2016:1.03 2017:1.02 2018:1.00 2019:0.99 2020:0.99 2021:1.01 2022:1.00
  yearly: 2015:0.99(z-0.3) 2016:1.04(z+1.0) 2017:1.02(z+0.6) 2018:1.03(z+0.8) 2019:1.01(z+0.3) 2020:0.96(z-1.1) 2021:1.01(z+0.4) 2022:1.01(z+0.2) 2023:1.02(z+0.6) 2024:0.98(z-0.5)

[IP] mean A/E 1.004 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0021/yr, R2 0.18, total -0.019
  step: -0.028 at 2017 (score 6.1)
  excursion: 2015-2016 (2y) +0.028 (score 6.1)
  YoY sd: empirical 0.0178 vs Poisson 0.0263 -> overdispersion x0.68 (Poisson null approximately valid)
  longest run: 2y up (+0.006) | max 1yr jump 0.033
  smoothed 3y MA: amplitude 0.025 over 2015-2022, fit R2 0.35 (gradient -0.0021/yr)
    MA series: 2015:1.02 2016:1.01 2017:1.00 2018:1.00 2019:0.99 2020:0.99 2021:0.99 2022:1.00
  yearly: 2015:1.02(z+0.7) 2016:1.03(z+1.0) 2017:1.00(z-0.1) 2018:1.00(z-0.0) 2019:1.00(z-0.1) 2020:1.00(z-0.0) 2021:0.98(z-0.9) 2022:1.00(z+0.2) 2023:1.00(z-0.1) 2024:1.01(z+0.5)

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.999 (z -0.1, expected 1262) -> clean
  Cardiovascular: pooled A/E 1.01 (z +0.3, expected 882) -> clean
  Injury/Accident: pooled A/E 0.974 (z -1.0, expected 1437) -> clean
  Mental Health: pooled A/E 1.005 (z +0.4, expected 4458) -> clean
  Musculoskeletal: pooled A/E 1.017 (z +1.0, expected 3306) -> clean
  Other: pooled A/E 0.983 (z -0.6, expected 1212) -> clean

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

