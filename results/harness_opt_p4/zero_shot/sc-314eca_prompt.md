# Prompt — sc-314eca

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

Scenario: sc-314eca

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
      "overall_ae": 1.0302,
      "claims": 5151
    },
    "CI": {
      "overall_ae": 1.0026,
      "claims": 12031
    },
    "TPD": {
      "overall_ae": 1.0014,
      "claims": 8011
    },
    "IP": {
      "overall_ae": 1.005,
      "claims": 15075,
      "overall_termination_ae": 0.9964
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=230  Expected=240  AE=0.960
  2016: Actual=304  Expected=290  AE=1.049
  2017: Actual=303  Expected=337  AE=0.898
  2018: Actual=379  Expected=390  AE=0.973
  2019: Actual=494  Expected=447  AE=1.106
  2020: Actual=590  Expected=508  AE=1.160
  2021: Actual=738  Expected=576  AE=1.282
  2022: Actual=640  Expected=652  AE=0.981
  2023: Actual=678  Expected=735  AE=0.922
  2024: Actual=795  Expected=826  AE=0.962

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=616  Expected=596  AE=1.033
  2016: Actual=644  Expected=720  AE=0.894
  2017: Actual=770  Expected=837  AE=0.920
  2018: Actual=867  Expected=963  AE=0.900
  2019: Actual=1,265  Expected=1,097  AE=1.153
  2020: Actual=1,692  Expected=1,239  AE=1.365
  2021: Actual=1,275  Expected=1,386  AE=0.920
  2022: Actual=1,482  Expected=1,548  AE=0.957
  2023: Actual=1,639  Expected=1,719  AE=0.953
  2024: Actual=1,781  Expected=1,893  AE=0.941

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=469  Expected=487  AE=0.963
  2016: Actual=599  Expected=562  AE=1.066
  2017: Actual=649  Expected=625  AE=1.039
  2018: Actual=753  Expected=690  AE=1.091
  2019: Actual=1,039  Expected=757  AE=1.372
  2020: Actual=772  Expected=826  AE=0.934
  2021: Actual=516  Expected=897  AE=0.575
  2022: Actual=965  Expected=974  AE=0.991
  2023: Actual=1,089  Expected=1,052  AE=1.035
  2024: Actual=1,160  Expected=1,130  AE=1.026

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,056  Expected=1,013  AE=1.043
  2016: Actual=1,159  Expected=1,142  AE=1.015
  2017: Actual=1,185  Expected=1,241  AE=0.955
  2018: Actual=1,289  Expected=1,342  AE=0.961
  2019: Actual=1,848  Expected=1,441  AE=1.283
  2020: Actual=1,409  Expected=1,545  AE=0.912
  2021: Actual=1,617  Expected=1,653  AE=0.978
  2022: Actual=1,693  Expected=1,768  AE=0.957
  2023: Actual=1,834  Expected=1,876  AE=0.977
  2024: Actual=1,985  Expected=1,980  AE=1.003

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.996
  Cardiovascular: 0.986
  Injury/Accident: 1.031
  Mental Health: 0.993
  Musculoskeletal: 0.998
  Other: 0.972

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.03 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0032/yr, R2 0.01, total 0.029
  step: -0.109 at 2023 (score 2.2)
  excursions (windows whose level differs from the rest, best first): 2019-2021 (3y) +0.219 score 4.0
  YoY sd: empirical 0.1446 vs Poisson 0.0477 -> overdispersion x3.03 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.37 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level)
  longest run: 5y up (+0.384) | max 1yr jump 0.3
  level at the END of the series: -0.053 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.227 over 2015-2022, fit R2 0.09 (gradient 0.0107/yr)
    MA series: 2015:0.97 2016:0.97 2017:0.99 2018:1.08 2019:1.18 2020:1.14 2021:1.06 2022:0.95
  yearly: 2015:0.96(z-0.6) 2016:1.05(z+0.8) 2017:0.90(z-1.9) 2018:0.97(z-0.5) 2019:1.11(z+2.2) 2020:1.16(z+3.6) 2021:1.28(z+6.8) 2022:0.98(z-0.5) 2023:0.92(z-2.1) 2024:0.96(z-1.1)

[CI] mean A/E 1.004 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient 0.0003/yr, R2 0.0, total 0.002
  step: +0.111 at 2019 (score 1.4)
  YoY sd: empirical 0.2026 vs Poisson 0.0305 -> overdispersion x6.64 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 1.39 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level)
  longest run: 3y up (+0.465) | max 1yr jump 0.445
  NOTE: this line is one of several taking unusually large swings in 2019-2020 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  smoothed 3y MA: amplitude 0.241 over 2015-2022, fit R2 0.02 (gradient 0.0057/yr)
    MA series: 2015:0.95 2016:0.91 2017:0.99 2018:1.14 2019:1.15 2020:1.08 2021:0.94 2022:0.95
  yearly: 2015:1.03(z+0.8) 2016:0.89(z-2.8) 2017:0.92(z-2.3) 2018:0.90(z-3.1) 2019:1.15(z+5.1) 2020:1.36(z+12.9) 2021:0.92(z-3.0) 2022:0.96(z-1.7) 2023:0.95(z-1.9) 2024:0.94(z-2.6)

[TPD] mean A/E 1.009 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient -0.0114/yr, R2 0.03, total -0.102
  step: -0.194 at 2020 (score 1.7)
  YoY sd: empirical 0.2709 vs Poisson 0.0364 -> overdispersion x7.44 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 1.98 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level)
  longest run: 3y up (+0.333) | max 1yr jump 0.437
  NOTE: this line is one of several taking unusually large swings in 2019-2020 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  level at the END of the series: -0.080 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.334 over 2015-2022, fit R2 0.3 (gradient -0.0262/yr)
    MA series: 2015:1.02 2016:1.07 2017:1.17 2018:1.13 2019:0.96 2020:0.83 2021:0.87 2022:1.02
  yearly: 2015:0.96(z-0.8) 2016:1.07(z+1.6) 2017:1.04(z+1.0) 2018:1.09(z+2.4) 2019:1.37(z+10.2) 2020:0.93(z-1.9) 2021:0.57(z-12.7) 2022:0.99(z-0.3) 2023:1.03(z+1.1) 2024:1.03(z+0.9)

[IP] mean A/E 1.008 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient -0.0056/yr, R2 0.03, total -0.051
  step: -0.086 at 2020 (score 1.4)
  YoY sd: empirical 0.1772 vs Poisson 0.0263 -> overdispersion x6.74 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 4.38 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level)
  longest run: 3y down (-0.088) | max 1yr jump 0.371
  NOTE: this line is one of several taking unusually large swings in 2019-2020 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  smoothed 3y MA: amplitude 0.117 over 2015-2022, fit R2 0.13 (gradient -0.0065/yr)
    MA series: 2015:1.00 2016:0.98 2017:1.07 2018:1.05 2019:1.06 2020:0.95 2021:0.97 2022:0.98
  yearly: 2015:1.04(z+1.4) 2016:1.01(z+0.5) 2017:0.95(z-1.6) 2018:0.96(z-1.4) 2019:1.28(z+10.7) 2020:0.91(z-3.5) 2021:0.98(z-0.9) 2022:0.96(z-1.8) 2023:0.98(z-1.0) 2024:1.00(z+0.1)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2015:1 2016:2 2017:1 2018:2 2019:2 2020:2 2021:1 2022:1
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:1 2019:3 2020:3 2021:2 2022:2
  -> 3 of 4 lines swing together in 2019-2020: a COORDINATED dispersion event is plausible — if that is your reading, report it for EACH affected line with the shared years

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.996 (z -0.1, expected 1268) -> clean
  Cardiovascular: pooled A/E 0.986 (z -0.4, expected 927) -> clean
  Injury/Accident: pooled A/E 1.031 (z +1.1, expected 1362) -> clean
  Mental Health: pooled A/E 0.993 (z -0.5, expected 4520) -> clean
  Musculoskeletal: pooled A/E 0.998 (z -0.1, expected 3378) -> clean
  Other: pooled A/E 0.972 (z -1.0, expected 1212) -> clean

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
   the years. Do not tell four unrelated stories, and do not drop lines. This
   means one entry per affected line EVEN WHEN one line's own move is much
   smaller than the others, and even when you discuss the shared cause only once:
   an answer that names the largest line and merely mentions the others in prose
   is graded as having found only the largest line.

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

