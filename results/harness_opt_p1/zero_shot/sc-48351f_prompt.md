# Prompt — sc-48351f

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

Scenario: sc-48351f

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
      "overall_termination_ae": 0.9978
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=226  Expected=240  AE=0.944
  2016: Actual=337  Expected=290  AE=1.163
  2017: Actual=326  Expected=337  AE=0.966
  2018: Actual=379  Expected=390  AE=0.973
  2019: Actual=451  Expected=447  AE=1.010
  2020: Actual=508  Expected=508  AE=0.999
  2021: Actual=564  Expected=576  AE=0.980
  2022: Actual=662  Expected=652  AE=1.015
  2023: Actual=749  Expected=735  AE=1.019
  2024: Actual=818  Expected=826  AE=0.990

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=600  Expected=596  AE=1.006
  2016: Actual=723  Expected=720  AE=1.004
  2017: Actual=808  Expected=837  AE=0.965
  2018: Actual=1,009  Expected=963  AE=1.048
  2019: Actual=1,124  Expected=1,097  AE=1.024
  2020: Actual=1,269  Expected=1,239  AE=1.024
  2021: Actual=1,346  Expected=1,386  AE=0.971
  2022: Actual=1,618  Expected=1,548  AE=1.045
  2023: Actual=1,740  Expected=1,719  AE=1.012
  2024: Actual=1,934  Expected=1,893  AE=1.021

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=452  Expected=487  AE=0.928
  2016: Actual=509  Expected=562  AE=0.906
  2017: Actual=595  Expected=625  AE=0.953
  2018: Actual=678  Expected=690  AE=0.982
  2019: Actual=759  Expected=757  AE=1.002
  2020: Actual=776  Expected=826  AE=0.939
  2021: Actual=878  Expected=897  AE=0.979
  2022: Actual=977  Expected=974  AE=1.003
  2023: Actual=1,299  Expected=1,052  AE=1.235
  2024: Actual=1,127  Expected=1,130  AE=0.997

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=988  Expected=1,013  AE=0.976
  2016: Actual=1,075  Expected=1,142  AE=0.942
  2017: Actual=1,207  Expected=1,241  AE=0.973
  2018: Actual=1,248  Expected=1,342  AE=0.930
  2019: Actual=1,424  Expected=1,441  AE=0.988
  2020: Actual=1,510  Expected=1,545  AE=0.977
  2021: Actual=1,645  Expected=1,653  AE=0.995
  2022: Actual=1,765  Expected=1,768  AE=0.998
  2023: Actual=2,208  Expected=1,876  AE=1.177
  2024: Actual=1,965  Expected=1,980  AE=0.993

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.993
  Cardiovascular: 1.023
  Injury/Accident: 0.955
  Mental Health: 1.007
  Musculoskeletal: 1.009
  Other: 0.972

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.006 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.002/yr, R2 0.01, total -0.018
  step: -0.059 at 2017 (score 0.5)
  excursion: 2017-2018 (2y) -0.045 (score 2.0)
  YoY sd: empirical 0.1066 vs Poisson 0.0477 -> overdispersion x2.23 (Poisson null approximately valid)
  longest run: 3y up (+0.043) | max 1yr jump 0.22
  smoothed 3y MA: amplitude 0.051 over 2015-2022, fit R2 0.14 (gradient -0.0025/yr)
    MA series: 2015:1.02 2016:1.03 2017:0.98 2018:0.99 2019:1.00 2020:1.00 2021:1.00 2022:1.01
  yearly: 2015:0.94(z-0.9) 2016:1.16(z+2.8) 2017:0.97(z-0.6) 2018:0.97(z-0.5) 2019:1.01(z+0.2) 2020:1.00(z-0.0) 2021:0.98(z-0.5) 2022:1.01(z+0.4) 2023:1.02(z+0.5) 2024:0.99(z-0.3)

[CI] mean A/E 1.012 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0022/yr, R2 0.06, total 0.02
  step: +0.029 at 2018 (score 1.8)
  excursion: 2018-2020 (3y) +0.028 (score 2.2)
  YoY sd: empirical 0.0477 vs Poisson 0.0305 -> overdispersion x1.56 (Poisson null approximately valid)
  longest run: 4y down (-0.076) | max 1yr jump 0.082
  smoothed 3y MA: amplitude 0.04 over 2015-2022, fit R2 0.31 (gradient 0.0028/yr)
    MA series: 2015:0.99 2016:1.01 2017:1.01 2018:1.03 2019:1.01 2020:1.01 2021:1.01 2022:1.03
  yearly: 2015:1.01(z+0.1) 2016:1.00(z+0.1) 2017:0.96(z-1.0) 2018:1.05(z+1.5) 2019:1.02(z+0.8) 2020:1.02(z+0.8) 2021:0.97(z-1.1) 2022:1.04(z+1.8) 2023:1.01(z+0.5) 2024:1.02(z+0.9)

[TPD] mean A/E 0.992 | evidence profile: sustained-move (smoothed): the 3-year smoothed level rises/falls steadily from 2015 to 2022 (amplitude 0.149, fit R2 0.78) with a weak whole-window linear fit — report the smoothed span as the window and note whether it persists to the horizon or is confined/reverting
  trend: gradient 0.0188/yr, R2 0.39, total 0.169
  step: +0.094 at 2017 (score 2.7)
  excursion: 2015-2016 (2y) -0.094 (score 2.7)
  YoY sd: empirical 0.1223 vs Poisson 0.0364 -> overdispersion x3.36 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  longest run: 4y up (+0.096) | max 1yr jump 0.238
  smoothed 3y MA: amplitude 0.149 over 2015-2022, fit R2 0.78 (gradient 0.0197/yr)
    MA series: 2015:0.93 2016:0.95 2017:0.98 2018:0.97 2019:0.97 2020:0.97 2021:1.07 2022:1.08
  yearly: 2015:0.93(z-1.6) 2016:0.91(z-2.2) 2017:0.95(z-1.2) 2018:0.98(z-0.5) 2019:1.00(z+0.1) 2020:0.94(z-1.8) 2021:0.98(z-0.6) 2022:1.00(z+0.1) 2023:1.24(z+7.6) 2024:1.00(z-0.1)

[IP] mean A/E 0.995 | evidence profile: sustained-move (smoothed): the 3-year smoothed level rises/falls steadily from 2015 to 2022 (amplitude 0.109, fit R2 0.79) with a weak whole-window linear fit — report the smoothed span as the window and note whether it persists to the horizon or is confined/reverting
  trend: gradient 0.0128/yr, R2 0.33, total 0.115
  step: +0.066 at 2019 (score 2.0)
  excursion: 2016-2018 (3y) -0.067 (score 2.2)
  YoY sd: empirical 0.0959 vs Poisson 0.0263 -> overdispersion x3.65 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  longest run: 4y up (+0.200) | max 1yr jump 0.184
  smoothed 3y MA: amplitude 0.109 over 2015-2022, fit R2 0.79 (gradient 0.0154/yr)
    MA series: 2015:0.96 2016:0.95 2017:0.96 2018:0.96 2019:0.99 2020:0.99 2021:1.06 2022:1.06
  yearly: 2015:0.98(z-0.8) 2016:0.94(z-2.0) 2017:0.97(z-1.0) 2018:0.93(z-2.6) 2019:0.99(z-0.4) 2020:0.98(z-0.9) 2021:0.99(z-0.2) 2022:1.00(z-0.1) 2023:1.18(z+7.7) 2024:0.99(z-0.3)

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.993 (z -0.3, expected 1255) -> clean
  Cardiovascular: pooled A/E 1.023 (z +0.7, expected 902) -> clean
  Injury/Accident: pooled A/E 0.955 (z -1.7, expected 1453) -> clean
  Mental Health: pooled A/E 1.007 (z +0.5, expected 4445) -> clean
  Musculoskeletal: pooled A/E 1.009 (z +0.5, expected 3333) -> clean
  Other: pooled A/E 0.972 (z -1.0, expected 1196) -> clean

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

