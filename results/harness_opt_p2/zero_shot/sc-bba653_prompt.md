# Prompt — sc-bba653

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

Scenario: sc-bba653

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
      "overall_termination_ae": 1.0045
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=207  Expected=240  AE=0.864
  2016: Actual=268  Expected=290  AE=0.925
  2017: Actual=286  Expected=337  AE=0.848
  2018: Actual=335  Expected=390  AE=0.860
  2019: Actual=391  Expected=447  AE=0.876
  2020: Actual=628  Expected=508  AE=1.235
  2021: Actual=722  Expected=576  AE=1.254
  2022: Actual=853  Expected=652  AE=1.308
  2023: Actual=629  Expected=735  AE=0.856
  2024: Actual=701  Expected=826  AE=0.849

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=531  Expected=596  AE=0.890
  2016: Actual=652  Expected=720  AE=0.905
  2017: Actual=757  Expected=837  AE=0.904
  2018: Actual=910  Expected=963  AE=0.945
  2019: Actual=985  Expected=1,097  AE=0.898
  2020: Actual=1,462  Expected=1,239  AE=1.180
  2021: Actual=1,655  Expected=1,386  AE=1.194
  2022: Actual=1,853  Expected=1,548  AE=1.197
  2023: Actual=1,592  Expected=1,719  AE=0.926
  2024: Actual=1,774  Expected=1,893  AE=0.937

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=435  Expected=487  AE=0.893
  2016: Actual=500  Expected=562  AE=0.890
  2017: Actual=593  Expected=625  AE=0.949
  2018: Actual=609  Expected=690  AE=0.882
  2019: Actual=736  Expected=757  AE=0.972
  2020: Actual=982  Expected=826  AE=1.188
  2021: Actual=984  Expected=897  AE=1.097
  2022: Actual=1,120  Expected=974  AE=1.150
  2023: Actual=1,026  Expected=1,052  AE=0.975
  2024: Actual=1,065  Expected=1,130  AE=0.942

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=973  Expected=1,013  AE=0.961
  2016: Actual=1,111  Expected=1,142  AE=0.973
  2017: Actual=1,190  Expected=1,241  AE=0.959
  2018: Actual=1,351  Expected=1,342  AE=1.007
  2019: Actual=1,385  Expected=1,441  AE=0.961
  2020: Actual=1,618  Expected=1,545  AE=1.047
  2021: Actual=1,724  Expected=1,653  AE=1.043
  2022: Actual=1,882  Expected=1,768  AE=1.064
  2023: Actual=1,881  Expected=1,876  AE=1.002
  2024: Actual=1,920  Expected=1,980  AE=0.970

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.019
  Cardiovascular: 1.025
  Injury/Accident: 0.966
  Mental Health: 1.013
  Musculoskeletal: 1.008
  Other: 0.983

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 0.987 | evidence profile: SHAPED-PULSE: the whole excursion (2020-2022, 3 y, +0.398) arrives in essentially ONE year and then holds flat (onset 1.14) — an abrupt one-off level change, however many years it lasts; report the span it covers and note that it is not a gradual build-up
  trend: gradient 0.0195/yr, R2 0.09, total 0.176
  step: -0.169 at 2023 (score 2.3)
  excursion: 2020-2022 (3y) +0.398 (score 16.5)
  YoY sd: empirical 0.2084 vs Poisson 0.0477 -> overdispersion x4.36 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.14 (essentially the whole excursion arrives in ONE year, then holds — a one-off level change, not a build-up)
  longest run: 6y up (+0.460) | max 1yr jump 0.452
  smoothed 3y MA: amplitude 0.405 over 2015-2022, fit R2 0.49 (gradient 0.042/yr)
    MA series: 2015:0.88 2016:0.88 2017:0.86 2018:0.99 2019:1.12 2020:1.27 2021:1.14 2022:1.00
  yearly: 2015:0.86(z-2.1) 2016:0.93(z-1.3) 2017:0.85(z-2.8) 2018:0.86(z-2.8) 2019:0.88(z-2.6) 2020:1.24(z+5.3) 2021:1.25(z+6.1) 2022:1.31(z+7.9) 2023:0.86(z-3.9) 2024:0.85(z-4.4)

[CI] mean A/E 0.998 | evidence profile: SHAPED-PULSE: the whole excursion (2020-2022, 3 y, +0.275) arrives in essentially ONE year and then holds flat (onset 1.03) — an abrupt one-off level change, however many years it lasts; report the span it covers and note that it is not a gradual build-up
  trend: gradient 0.0185/yr, R2 0.18, total 0.167
  step: +0.178 at 2020 (score 2.8)
  excursion: 2020-2022 (3y) +0.275 (score 29.1)
  YoY sd: empirical 0.1401 vs Poisson 0.0305 -> overdispersion x4.59 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.03 (essentially the whole excursion arrives in ONE year, then holds — a one-off level change, not a build-up)
  longest run: 4y up (+0.299) | max 1yr jump 0.282
  smoothed 3y MA: amplitude 0.29 over 2015-2022, fit R2 0.56 (gradient 0.032/yr)
    MA series: 2015:0.90 2016:0.92 2017:0.92 2018:1.01 2019:1.09 2020:1.19 2021:1.11 2022:1.02
  yearly: 2015:0.89(z-2.7) 2016:0.91(z-2.5) 2017:0.90(z-2.8) 2018:0.94(z-1.7) 2019:0.90(z-3.4) 2020:1.18(z+6.3) 2021:1.19(z+7.2) 2022:1.20(z+7.7) 2023:0.93(z-3.1) 2024:0.94(z-2.7)

[TPD] mean A/E 0.994 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0176/yr, R2 0.23, total 0.158
  step: +0.150 at 2019 (score 3.3)
  excursion: 2020-2022 (3y) +0.216 (score 7.1)
  YoY sd: empirical 0.1148 vs Poisson 0.0364 -> overdispersion x3.15 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.0 (essentially the whole excursion arrives in ONE year, then holds — a one-off level change, not a build-up)
  longest run: 3y up (+0.306) | max 1yr jump 0.217
  smoothed 3y MA: amplitude 0.238 over 2015-2022, fit R2 0.59 (gradient 0.0276/yr)
    MA series: 2015:0.91 2016:0.91 2017:0.94 2018:1.01 2019:1.09 2020:1.15 2021:1.07 2022:1.02
  yearly: 2015:0.89(z-2.4) 2016:0.89(z-2.6) 2017:0.95(z-1.3) 2018:0.88(z-3.1) 2019:0.97(z-0.8) 2020:1.19(z+5.4) 2021:1.10(z+2.9) 2022:1.15(z+4.7) 2023:0.97(z-0.8) 2024:0.94(z-1.9)

[IP] mean A/E 0.999 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0061/yr, R2 0.21, total 0.055
  step: +0.049 at 2018 (score 3.2)
  excursion: 2020-2022 (3y) +0.075 (score 7.5)
  YoY sd: empirical 0.0466 vs Poisson 0.0263 -> overdispersion x1.77 (Poisson null approximately valid)
  onset: max 1yr move / excursion size = 1.14 (essentially the whole excursion arrives in ONE year, then holds — a one-off level change, not a build-up)
  longest run: 3y down (-0.094) | max 1yr jump 0.086
  smoothed 3y MA: amplitude 0.087 over 2015-2022, fit R2 0.67 (gradient 0.0102/yr)
    MA series: 2015:0.96 2016:0.98 2017:0.98 2018:1.00 2019:1.02 2020:1.05 2021:1.04 2022:1.01
  yearly: 2015:0.96(z-1.2) 2016:0.97(z-0.9) 2017:0.96(z-1.4) 2018:1.01(z+0.2) 2019:0.96(z-1.5) 2020:1.05(z+1.9) 2021:1.04(z+1.8) 2022:1.06(z+2.7) 2023:1.00(z+0.1) 2024:0.97(z-1.3)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2015:3 2016:3 2017:3 2019:1 2020:3 2021:2
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2018:1 2019:1 2020:4 2023:3
  -> 3 of 4 lines move together in 2015-2017: a COORDINATED move, so weigh one systemic explanation and report it for EACH affected line (the answer schema has no 'all' benefit) rather than four unrelated stories

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 1.019 (z +0.7, expected 1246) -> clean
  Cardiovascular: pooled A/E 1.025 (z +0.7, expected 885) -> clean
  Injury/Accident: pooled A/E 0.966 (z -1.3, expected 1441) -> clean
  Mental Health: pooled A/E 1.013 (z +0.8, expected 4458) -> clean
  Musculoskeletal: pooled A/E 1.008 (z +0.4, expected 3318) -> clean
  Other: pooled A/E 0.983 (z -0.6, expected 1224) -> clean

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

