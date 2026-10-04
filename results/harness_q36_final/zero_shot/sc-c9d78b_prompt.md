# Prompt — sc-c9d78b

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

Scenario: sc-c9d78b

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
      "overall_termination_ae": 0.9992
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=246  Expected=240  AE=1.027
  2016: Actual=268  Expected=290  AE=0.925
  2017: Actual=336  Expected=337  AE=0.996
  2018: Actual=417  Expected=390  AE=1.070
  2019: Actual=460  Expected=447  AE=1.030
  2020: Actual=658  Expected=508  AE=1.294
  2021: Actual=581  Expected=576  AE=1.009
  2022: Actual=582  Expected=652  AE=0.893
  2023: Actual=671  Expected=735  AE=0.913
  2024: Actual=801  Expected=826  AE=0.970

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
  2015: Actual=991  Expected=1,013  AE=0.979
  2016: Actual=1,161  Expected=1,142  AE=1.017
  2017: Actual=1,266  Expected=1,241  AE=1.020
  2018: Actual=1,375  Expected=1,342  AE=1.025
  2019: Actual=1,505  Expected=1,441  AE=1.045
  2020: Actual=1,741  Expected=1,545  AE=1.127
  2021: Actual=1,599  Expected=1,653  AE=0.967
  2022: Actual=1,707  Expected=1,768  AE=0.965
  2023: Actual=1,818  Expected=1,876  AE=0.969
  2024: Actual=1,872  Expected=1,980  AE=0.946

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.009
  Cardiovascular: 1.029
  Injury/Accident: 0.955
  Mental Health: 1.011
  Musculoskeletal: 1.007
  Other: 0.956

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.013 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0063/yr, R2 0.03, total -0.057
  step: -0.125 at 2022 (score 2.5)
  excursions (windows whose level differs from the rest, best first): 2022-2023 (2y) -0.137 score 3.4
  YoY sd: empirical 0.1543 vs Poisson 0.0477 -> overdispersion x3.23 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  GIVE-BACK: in 2020 this line's level departs to 1.294 against its own baseline 1.009 (increase) and is back the following year (the move -0.285 is undone by +0.264, ratio 0.93) — that is the shape of a ONE-OFF change CONFINED TO 2020, not a slow build and not a multi-year erratic stretch. Name it as an entry of its own with that single year and direction; keep a dispersion entry as well if you believe the wider stretch is erratic (the two readings are not exclusive)
  onset: max 1yr move / excursion size = 2.07 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y up (+0.145) | max 1yr jump 0.285
  level at the END of the series: -0.100 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  TAIL: in the FINAL years 2022-2024 the line moves steadily up (+0.038/yr, fit R2 0.93), ending -0.125 against the years before that (values 2022:0.89 2023:0.91 2024:0.97). Calibration: clean lines never reach this block (|gradient| <= 0.013), while genuine slow movements do — a steady final-years move that leaves the level away from its earlier value is a sustained move in its own right, so report it with THESE years even when an earlier event on the same line is bigger and already reported
  smoothed 3y MA: amplitude 0.206 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.06 (gradient -0.0074/yr)
    MA series: 2015:0.98 2016:1.00 2017:1.03 2018:1.13 2019:1.11 2020:1.06 2021:0.94 2022:0.93
  yearly: 2015:1.03(z+0.4) 2016:0.93(z-1.3) 2017:1.00(z-0.1) 2018:1.07(z+1.4) 2019:1.03(z+0.6) 2020:1.29(z+6.6) 2021:1.01(z+0.2) 2022:0.89(z-2.7) 2023:0.91(z-2.4) 2024:0.97(z-0.9)

[CI] mean A/E 1.012 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0022/yr, R2 0.06, total 0.02
  step: +0.029 at 2018 (score 1.8)
  YoY sd: empirical 0.0477 vs Poisson 0.0305 -> overdispersion x1.56 (Poisson null approximately valid)
  longest run: 4y down (-0.076) | max 1yr jump 0.082
  smoothed 3y MA: amplitude 0.04 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.31 (gradient 0.0028/yr)
    MA series: 2015:0.99 2016:1.01 2017:1.01 2018:1.03 2019:1.01 2020:1.01 2021:1.01 2022:1.03
  yearly: 2015:1.01(z+0.1) 2016:1.00(z+0.1) 2017:0.96(z-1.0) 2018:1.05(z+1.5) 2019:1.02(z+0.8) 2020:1.02(z+0.8) 2021:0.97(z-1.1) 2022:1.04(z+1.8) 2023:1.01(z+0.5) 2024:1.02(z+0.9)

[TPD] mean A/E 1.008 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0021/yr, R2 0.07, total -0.019
  step: -0.021 at 2020 (score 1.5)
  excursions (windows whose level differs from the rest, best first): 2016-2018 (3y) +0.034 score 3.8
  YoY sd: empirical 0.0346 vs Poisson 0.0364 -> overdispersion x0.95 (Poisson null approximately valid)
  longest run: 3y down (-0.066) | max 1yr jump 0.056
  smoothed 3y MA: amplitude 0.037 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.36 (gradient -0.0033/yr)
    MA series: 2015:1.02 2016:1.03 2017:1.02 2018:1.00 2019:0.99 2020:0.99 2021:1.01 2022:1.00
  yearly: 2015:0.99(z-0.3) 2016:1.04(z+1.0) 2017:1.02(z+0.6) 2018:1.03(z+0.8) 2019:1.01(z+0.3) 2020:0.96(z-1.1) 2021:1.01(z+0.4) 2022:1.01(z+0.2) 2023:1.02(z+0.6) 2024:0.98(z-0.5)

[IP] mean A/E 1.006 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.006/yr, R2 0.12, total -0.054
  step: -0.073 at 2021 (score 3.5)
  excursions (windows whose level differs from the rest, best first): 2016-2020 (5y) +0.081 score 3.8; 2021-2024 (4y) -0.073 score 3.5
  YoY sd: empirical 0.0656 vs Poisson 0.0263 -> overdispersion x2.5 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.95 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 6y up (+0.148) | max 1yr jump 0.159
  level at the END of the series: -0.057 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.105 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.26 (gradient -0.0075/yr)
    MA series: 2015:1.00 2016:1.02 2017:1.03 2018:1.06 2019:1.05 2020:1.02 2021:0.97 2022:0.96
  yearly: 2015:0.98(z-0.7) 2016:1.02(z+0.6) 2017:1.02(z+0.7) 2018:1.02(z+0.9) 2019:1.04(z+1.7) 2020:1.13(z+5.0) 2021:0.97(z-1.3) 2022:0.96(z-1.5) 2023:0.97(z-1.3) 2024:0.95(z-2.4)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2018:1 2021:1 2022:1
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:1 2018:1 2020:2 2021:3
  -> 3 of 4 lines take their large swing in the SAME single year above; that is what a book-wide jolt looks like — read those lines in the level rows (step/excursion) rather than raising a dispersion reading on the strength of the swing counts alone. Note what this does and does not rule out: it rules out a multi-year ERRATIC stretch (dispersion), and it does NOT rule out a sustained move, so check each line's own longest-run row as well — a line that runs steadily in ONE direction for several consecutive years is a sustained move in its own right, even when other lines take a single-year jolt

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 1.009 (z +0.3, expected 1268) -> clean
  Cardiovascular: pooled A/E 1.029 (z +0.9, expected 884) -> clean
  Injury/Accident: pooled A/E 0.955 (z -1.7, expected 1461) -> clean
  Mental Health: pooled A/E 1.011 (z +0.7, expected 4465) -> clean
  Musculoskeletal: pooled A/E 1.007 (z +0.4, expected 3352) -> clean
  Other: pooled A/E 0.956 (z -1.5, expected 1229) -> clean

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
     finding merely because its scatter is above Poisson. The one exception is
     the book-wide case: when the CROSS-LINE block reports several lines
     swinging together across consecutive years, that shared evidence stands on
     its own, and every affected line gets its dispersion entry even if that
     line's own ratio is below the x6 guide.
   * Use the pattern the evidence actually describes. A single-year deviation
     that reverts is a one-off change; a movement that builds and then flattens
     or runs on is a sustained move; a stretch where the line swings around
     without ever settling at a new level is dispersion. The schema's taxonomy
     above defines each pattern word. When a per-line note says the biggest
     single-year move EXCEEDS the net excursion, the evidence cannot separate a
     give-back ramp from an erratic stretch: give that line a dispersion entry
     AND keep the level-change reading as an entry of its own, so both readings
     are on the record (one entry of each kind per line, never two of the same).
   * A one-year wobble is only a finding if the year is genuinely extreme:
     require a Poisson z of about 4.5 or more for that year (A/E alone is
     misleading when the expected count is small). A single-year excursion
     around z 3 is the kind of thing ordinary books produce, so leave it out.
     Where a line's own scatter already exceeds Poisson, per-year z-scores are
     unreliable — then require a larger move, or describe the stretch as
     dispersion instead of claiming a one-off change.
   * Every entry in "findings" is a claim that something material happened and
     should be investigated. A favourable deviation (A/E materially BELOW
     expectation), a movement you have decided is ordinary, and any observation
     you are not claiming must not appear as its own entry — mention it in the
     evidence text of a finding you ARE making, or leave it out entirely.
     Listing an observation you are not claiming is scored as a false alarm.
   * Do not describe the same movement twice. If a line's final years reverse a
     movement you have already reported for that line, that reversal is part of
     the earlier event: say so inside that finding rather than adding a second
     entry for the same line.
   * Small cells are not evidence: age-band or duration-month A/E values rest
     on tiny expected counts and go extreme by chance. Never report a
     book-level anomaly from such a cell unless the same effect is visible in
     the by-year series or the pooled line.
   * Findings you considered and rejected for these reasons do not appear in
     the "findings" array at all.

