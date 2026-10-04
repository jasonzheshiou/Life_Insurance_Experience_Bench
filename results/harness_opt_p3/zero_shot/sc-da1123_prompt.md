# Prompt — sc-da1123

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

Scenario: sc-da1123

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
      "overall_termination_ae": 0.9991
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=226  Expected=240  AE=0.944
  2016: Actual=265  Expected=290  AE=0.915
  2017: Actual=281  Expected=337  AE=0.833
  2018: Actual=290  Expected=390  AE=0.744
  2019: Actual=400  Expected=447  AE=0.896
  2020: Actual=507  Expected=508  AE=0.997
  2021: Actual=615  Expected=576  AE=1.068
  2022: Actual=697  Expected=652  AE=1.069
  2023: Actual=796  Expected=735  AE=1.083
  2024: Actual=943  Expected=826  AE=1.142

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=531  Expected=596  AE=0.890
  2016: Actual=660  Expected=720  AE=0.916
  2017: Actual=755  Expected=837  AE=0.902
  2018: Actual=860  Expected=963  AE=0.893
  2019: Actual=1,112  Expected=1,097  AE=1.013
  2020: Actual=1,242  Expected=1,239  AE=1.002
  2021: Actual=1,398  Expected=1,386  AE=1.009
  2022: Actual=1,562  Expected=1,548  AE=1.009
  2023: Actual=1,884  Expected=1,719  AE=1.096
  2024: Actual=2,167  Expected=1,893  AE=1.145

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=449  Expected=487  AE=0.922
  2016: Actual=544  Expected=562  AE=0.968
  2017: Actual=579  Expected=625  AE=0.927
  2018: Actual=658  Expected=690  AE=0.953
  2019: Actual=754  Expected=757  AE=0.995
  2020: Actual=813  Expected=826  AE=0.984
  2021: Actual=870  Expected=897  AE=0.970
  2022: Actual=974  Expected=974  AE=1.000
  2023: Actual=1,149  Expected=1,052  AE=1.092
  2024: Actual=1,260  Expected=1,130  AE=1.115

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=945  Expected=1,013  AE=0.933
  2016: Actual=1,104  Expected=1,142  AE=0.967
  2017: Actual=1,176  Expected=1,241  AE=0.948
  2018: Actual=1,307  Expected=1,342  AE=0.974
  2019: Actual=1,433  Expected=1,441  AE=0.995
  2020: Actual=1,520  Expected=1,545  AE=0.984
  2021: Actual=1,643  Expected=1,653  AE=0.994
  2022: Actual=1,827  Expected=1,768  AE=1.033
  2023: Actual=1,946  Expected=1,876  AE=1.037
  2024: Actual=2,134  Expected=1,980  AE=1.078

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.996
  Cardiovascular: 1.027
  Injury/Accident: 0.955
  Mental Health: 1.003
  Musculoskeletal: 1.014
  Other: 0.978

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 0.969 | evidence profile: sustained-move (smoothed): the 3-year smoothed level rises/falls steadily from 2015 to 2022 (amplitude 0.273, fit R2 0.8) with a weak whole-window linear fit — report the smoothed span as the window and note whether it persists to the horizon or is confined/reverting
  trend: gradient 0.0316/yr, R2 0.58, total 0.284
  step: +0.202 at 2021 (score 5.0)
  excursions (windows whose level differs from the rest, best first): 2015-2020 (6y) -0.202 score 5.0; 2021-2024 (4y) +0.202 score 5.0
  YoY sd: empirical 0.0814 vs Poisson 0.0477 -> overdispersion x1.7 (Poisson null approximately valid)
  onset: max 1yr move / excursion size = 0.75 (the excursion accumulates across several years of small moves — a build-up, not a one-off jump)
  longest run: 7y up (+0.397) | max 1yr jump 0.151
  level at the END of the series: +0.099 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.273 over 2015-2022, fit R2 0.8 (gradient 0.0403/yr)
    MA series: 2015:0.90 2016:0.83 2017:0.82 2018:0.88 2019:0.99 2020:1.04 2021:1.07 2022:1.10
  yearly: 2015:0.94(z-0.9) 2016:0.92(z-1.4) 2017:0.83(z-3.1) 2018:0.74(z-5.0) 2019:0.90(z-2.2) 2020:1.00(z-0.1) 2021:1.07(z+1.6) 2022:1.07(z+1.8) 2023:1.08(z+2.3) 2024:1.14(z+4.1)

[CI] mean A/E 0.988 | evidence profile: sustained-move (smoothed): the 3-year smoothed level rises/falls steadily from 2015 to 2022 (amplitude 0.18, fit R2 0.97) with a weak whole-window linear fit — report the smoothed span as the window and note whether it persists to the horizon or is confined/reverting
  trend: gradient 0.0268/yr, R2 0.86, total 0.241
  step: +0.145 at 2019 (score 5.8)
  excursions (windows whose level differs from the rest, best first): 2015-2018 (4y) -0.145 score 5.8; 2019-2024 (6y) +0.145 score 5.8
  YoY sd: empirical 0.048 vs Poisson 0.0305 -> overdispersion x1.57 (Poisson null approximately valid)
  onset: max 1yr move / excursion size = 0.83 (the excursion accumulates across several years of small moves — a build-up, not a one-off jump)
  longest run: 5y up (+0.142) | max 1yr jump 0.121
  level at the END of the series: +0.054 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.18 over 2015-2022, fit R2 0.97 (gradient 0.026/yr)
    MA series: 2015:0.90 2016:0.90 2017:0.94 2018:0.97 2019:1.01 2020:1.01 2021:1.04 2022:1.08
  yearly: 2015:0.89(z-2.7) 2016:0.92(z-2.2) 2017:0.90(z-2.8) 2018:0.89(z-3.3) 2019:1.01(z+0.4) 2020:1.00(z+0.1) 2021:1.01(z+0.3) 2022:1.01(z+0.3) 2023:1.10(z+4.0) 2024:1.15(z+6.3)

[TPD] mean A/E 0.993 | evidence profile: SHAPED-AND-GRADUAL: the smoothed (3y MA) level moves steadily (amplitude 0.13, smoothed-fit R2 0.87) and the excursion accumulates across several years of small moves — a build-up. Use the MA series to read where the smoothed level leaves and returns to its own baseline, and report THAT span as the window; a move that builds over years and then flattens/reverts is a sustained move, not a one-off step
  trend: gradient 0.0182/yr, R2 0.74, total 0.164
  step: +0.138 at 2023 (score 9.1)
  excursions (windows whose level differs from the rest, best first): 2015-2018 (4y) -0.083 score 3.1; 2023-2024 (2y) +0.138 score 9.1
  YoY sd: empirical 0.0393 vs Poisson 0.0364 -> overdispersion x1.08 (Poisson null approximately valid)
  onset: max 1yr move / excursion size = 0.66 (the excursion accumulates across several years of small moves — a build-up, not a one-off jump)
  longest run: 4y up (+0.144) | max 1yr jump 0.092
  level at the END of the series: +0.062 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.13 over 2015-2022, fit R2 0.87 (gradient 0.0161/yr)
    MA series: 2015:0.94 2016:0.95 2017:0.96 2018:0.98 2019:0.98 2020:0.98 2021:1.02 2022:1.07
  yearly: 2015:0.92(z-1.7) 2016:0.97(z-0.7) 2017:0.93(z-1.8) 2018:0.95(z-1.2) 2019:0.99(z-0.1) 2020:0.98(z-0.5) 2021:0.97(z-0.9) 2022:1.00(z+0.0) 2023:1.09(z+3.0) 2024:1.11(z+3.9)

[IP] mean A/E 0.994 | evidence profile: sustained-move (smoothed): the 3-year smoothed level rises/falls steadily from 2015 to 2022 (amplitude 0.1, fit R2 0.96) with a weak whole-window linear fit — report the smoothed span as the window and note whether it persists to the horizon or is confined/reverting
  trend: gradient 0.0138/yr, R2 0.89, total 0.124
  step: +0.079 at 2022 (score 4.7)
  excursions (windows whose level differs from the rest, best first): 2015-2021 (7y) -0.079 score 4.7; 2022-2024 (3y) +0.079 score 4.7
  YoY sd: empirical 0.0216 vs Poisson 0.0263 -> overdispersion x0.82 (Poisson null approximately valid)
  onset: max 1yr move / excursion size = 0.52 (the excursion accumulates across several years of small moves — a build-up, not a one-off jump)
  longest run: 5y up (+0.094) | max 1yr jump 0.041
  smoothed 3y MA: amplitude 0.1 over 2015-2022, fit R2 0.96 (gradient 0.013/yr)
    MA series: 2015:0.95 2016:0.96 2017:0.97 2018:0.98 2019:0.99 2020:1.00 2021:1.02 2022:1.05
  yearly: 2015:0.93(z-2.1) 2016:0.97(z-1.1) 2017:0.95(z-1.8) 2018:0.97(z-1.0) 2019:0.99(z-0.2) 2020:0.98(z-0.6) 2021:0.99(z-0.2) 2022:1.03(z+1.4) 2023:1.04(z+1.6) 2024:1.08(z+3.5)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2015:2 2016:2 2017:1 2018:1 2021:1 2022:2
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2019:1 2023:2 2024:1

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.996 (z -0.2, expected 1264) -> clean
  Cardiovascular: pooled A/E 1.027 (z +0.8, expected 875) -> clean
  Injury/Accident: pooled A/E 0.955 (z -1.7, expected 1451) -> clean
  Mental Health: pooled A/E 1.003 (z +0.2, expected 4447) -> clean
  Musculoskeletal: pooled A/E 1.014 (z +0.8, expected 3306) -> clean
  Other: pooled A/E 0.978 (z -0.8, expected 1212) -> clean

HARNESS MODE — you are not limited to eyeballing the tables above.

1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact
   CSVs) is appended at the end of this message. Trust its arithmetic over
   mental math, but the final judgement is yours: confirm or override its
   per-line heuristic verdicts.

2) You may compute anything else you need. To use the tool, reply with ONLY a
   JSON object (no other text, no <tool_call> tags, no function-call syntax):
     {"tool": "python", "code": "<python source as one JSON string>"}
   The code runs with the scenario's artifacts/ directory as cwd (open files
   by relative path, e.g. open("ae_death_by_year.csv")); plain stdlib Python
   (csv, math, statistics); 10 s limit; output is returned verbatim.
   You get at most 4 tool calls. NEVER write files or read outside artifacts/.

3) When done — with or without tools — reply with ONLY the final JSON object
   in the required shape. Do not put tool requests inside that final JSON.

3b) Work efficiently: the evidence pack already contains the arithmetic. At most
   TWO tool calls, and if the pack answers the question, answer immediately
   without any tool call. Never spend more turns than the problem needs.

3c) Books where several lines move together: when the CROSS-LINE block reports a
   coordinated move or coordinated swings over a run of consecutive years, treat
   it as ONE underlying event but report it for EVERY affected line — the output
   schema has no "all" benefit, so a four-line event needs four entries sharing
   the years. Do not tell four unrelated stories, and do not drop lines.

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

