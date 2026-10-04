# Prompt — sc-2d248f

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

Scenario: sc-2d248f

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
      "overall_ae": 1.001,
      "claims": 5005
    },
    "CI": {
      "overall_ae": 1.0193,
      "claims": 12232
    },
    "TPD": {
      "overall_ae": 1.0051,
      "claims": 8041
    },
    "IP": {
      "overall_ae": 0.9995,
      "claims": 14993,
      "overall_termination_ae": 1.0001
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=225  Expected=240  AE=0.939
  2016: Actual=336  Expected=290  AE=1.160
  2017: Actual=325  Expected=337  AE=0.963
  2018: Actual=378  Expected=390  AE=0.970
  2019: Actual=450  Expected=447  AE=1.008
  2020: Actual=506  Expected=508  AE=0.995
  2021: Actual=563  Expected=576  AE=0.978
  2022: Actual=661  Expected=652  AE=1.014
  2023: Actual=745  Expected=735  AE=1.014
  2024: Actual=816  Expected=826  AE=0.988

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=601  Expected=596  AE=1.008
  2016: Actual=728  Expected=720  AE=1.011
  2017: Actual=816  Expected=837  AE=0.975
  2018: Actual=1,016  Expected=963  AE=1.055
  2019: Actual=1,127  Expected=1,097  AE=1.027
  2020: Actual=1,276  Expected=1,239  AE=1.030
  2021: Actual=1,350  Expected=1,386  AE=0.974
  2022: Actual=1,624  Expected=1,548  AE=1.049
  2023: Actual=1,750  Expected=1,719  AE=1.018
  2024: Actual=1,944  Expected=1,893  AE=1.027

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=486  Expected=487  AE=0.998
  2016: Actual=582  Expected=562  AE=1.036
  2017: Actual=633  Expected=625  AE=1.014
  2018: Actual=727  Expected=690  AE=1.053
  2019: Actual=762  Expected=757  AE=1.006
  2020: Actual=798  Expected=826  AE=0.966
  2021: Actual=911  Expected=897  AE=1.016
  2022: Actual=978  Expected=974  AE=1.004
  2023: Actual=1,061  Expected=1,052  AE=1.009
  2024: Actual=1,103  Expected=1,130  AE=0.976

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=418  Expected=1,013  AE=0.413
  2016: Actual=1,888  Expected=1,142  AE=1.654
  2017: Actual=1,334  Expected=1,241  AE=1.075
  2018: Actual=1,249  Expected=1,342  AE=0.931
  2019: Actual=1,359  Expected=1,441  AE=0.943
  2020: Actual=2,491  Expected=1,545  AE=1.612
  2021: Actual=1,546  Expected=1,653  AE=0.935
  2022: Actual=1,308  Expected=1,768  AE=0.740
  2023: Actual=1,490  Expected=1,876  AE=0.794
  2024: Actual=1,910  Expected=1,980  AE=0.965

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.036
  Cardiovascular: 1.029
  Injury/Accident: 0.951
  Mental Health: 0.993
  Musculoskeletal: 1.002
  Other: 1.023

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.003 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.002/yr, R2 0.01, total -0.018
  step: -0.058 at 2017 (score 0.5)
  YoY sd: empirical 0.1066 vs Poisson 0.0477 -> overdispersion x2.23 (Poisson null approximately valid)
  longest run: 3y up (+0.044) | max 1yr jump 0.221
  smoothed 3y MA: amplitude 0.051 over 2015-2022, fit R2 0.14 (gradient -0.0025/yr)
    MA series: 2015:1.02 2016:1.03 2017:0.98 2018:0.99 2019:0.99 2020:1.00 2021:1.00 2022:1.00
  yearly: 2015:0.94(z-0.9) 2016:1.16(z+2.7) 2017:0.96(z-0.7) 2018:0.97(z-0.6) 2019:1.01(z+0.2) 2020:0.99(z-0.1) 2021:0.98(z-0.5) 2022:1.01(z+0.3) 2023:1.01(z+0.4) 2024:0.99(z-0.4)

[CI] mean A/E 1.017 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0021/yr, R2 0.06, total 0.019
  step: +0.028 at 2018 (score 1.8)
  YoY sd: empirical 0.0477 vs Poisson 0.0305 -> overdispersion x1.56 (Poisson null approximately valid)
  longest run: 2y up (+0.003) | max 1yr jump 0.08
  smoothed 3y MA: amplitude 0.039 over 2015-2022, fit R2 0.24 (gradient 0.0024/yr)
    MA series: 2015:1.00 2016:1.01 2017:1.02 2018:1.04 2019:1.01 2020:1.02 2021:1.01 2022:1.03
  yearly: 2015:1.01(z+0.2) 2016:1.01(z+0.3) 2017:0.97(z-0.7) 2018:1.05(z+1.7) 2019:1.03(z+0.9) 2020:1.03(z+1.0) 2021:0.97(z-1.0) 2022:1.05(z+1.9) 2023:1.02(z+0.7) 2024:1.03(z+1.2)

[TPD] mean A/E 1.008 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0036/yr, R2 0.18, total -0.032
  step: -0.029 at 2019 (score 2.0)
  YoY sd: empirical 0.0373 vs Poisson 0.0364 -> overdispersion x1.02 (Poisson null approximately valid)
  longest run: 3y down (-0.088) | max 1yr jump 0.05
  smoothed 3y MA: amplitude 0.039 over 2015-2022, fit R2 0.54 (gradient -0.0043/yr)
    MA series: 2015:1.02 2016:1.03 2017:1.02 2018:1.01 2019:1.00 2020:0.99 2021:1.01 2022:1.00
  yearly: 2015:1.00(z-0.0) 2016:1.04(z+0.9) 2017:1.01(z+0.3) 2018:1.05(z+1.4) 2019:1.01(z+0.2) 2020:0.97(z-1.0) 2021:1.02(z+0.5) 2022:1.00(z+0.1) 2023:1.01(z+0.3) 2024:0.98(z-0.8)

[IP] mean A/E 1.006 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient -0.0124/yr, R2 0.01, total -0.111
  step: -0.248 at 2022 (score 1.4)
  YoY sd: empirical 0.5956 vs Poisson 0.0263 -> overdispersion x22.66 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 2.68 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level)
  longest run: 3y down (-0.723) | max 1yr jump 1.241
  level at the END of the series: -0.268 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  TAIL: in the FINAL years 2022-2024 the line moves steadily up (+0.113/yr, fit R2 0.92), ending -0.248 against the years before that (values 2022:0.74 2023:0.79 2024:0.96). Calibration: clean lines never reach this block (|gradient| <= 0.013), while genuine slow movements do — a steady final-years move that leaves the level away from its earlier value is a sustained move in its own right, so report it with THESE years even when an earlier event on the same line is bigger and already reported
  smoothed 3y MA: amplitude 0.397 over 2015-2022, fit R2 0.37 (gradient -0.0374/yr)
    MA series: 2015:1.05 2016:1.22 2017:0.98 2018:1.16 2019:1.16 2020:1.10 2021:0.82 2022:0.83
  yearly: 2015:0.41(z-18.7) 2016:1.65(z+22.1) 2017:1.07(z+2.7) 2018:0.93(z-2.5) 2019:0.94(z-2.2) 2020:1.61(z+24.1) 2021:0.94(z-2.6) 2022:0.74(z-10.9) 2023:0.79(z-8.9) 2024:0.96(z-1.6)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2016:1 2017:1 2021:1 2022:1
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:2 2017:2 2018:1 2020:1 2021:1

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 1.036 (z +1.3, expected 1248) -> clean
  Cardiovascular: pooled A/E 1.029 (z +0.8, expected 875) -> clean
  Injury/Accident: pooled A/E 0.951 (z -1.9, expected 1472) -> clean
  Mental Health: pooled A/E 0.993 (z -0.5, expected 4483) -> clean
  Musculoskeletal: pooled A/E 1.002 (z +0.1, expected 3374) -> clean
  Other: pooled A/E 1.023 (z +0.8, expected 1192) -> clean

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

