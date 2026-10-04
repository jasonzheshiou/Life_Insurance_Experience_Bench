# Prompt — sc-e6ffa4

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

Scenario: sc-e6ffa4

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
      "overall_ae": 0.9872,
      "claims": 4936
    },
    "CI": {
      "overall_ae": 1.0038,
      "claims": 12046
    },
    "TPD": {
      "overall_ae": 1.0045,
      "claims": 8036
    },
    "IP": {
      "overall_ae": 1.0066,
      "claims": 15099,
      "overall_termination_ae": 0.9921
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=223  Expected=240  AE=0.931
  2016: Actual=289  Expected=290  AE=0.998
  2017: Actual=305  Expected=337  AE=0.904
  2018: Actual=366  Expected=390  AE=0.939
  2019: Actual=403  Expected=447  AE=0.902
  2020: Actual=517  Expected=508  AE=1.017
  2021: Actual=568  Expected=576  AE=0.987
  2022: Actual=770  Expected=652  AE=1.181
  2023: Actual=591  Expected=735  AE=0.804
  2024: Actual=904  Expected=826  AE=1.094

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=619  Expected=596  AE=1.038
  2016: Actual=669  Expected=720  AE=0.929
  2017: Actual=826  Expected=837  AE=0.987
  2018: Actual=950  Expected=963  AE=0.986
  2019: Actual=1,059  Expected=1,097  AE=0.965
  2020: Actual=1,443  Expected=1,239  AE=1.165
  2021: Actual=1,332  Expected=1,386  AE=0.961
  2022: Actual=2,088  Expected=1,548  AE=1.349
  2023: Actual=1,909  Expected=1,719  AE=1.110
  2024: Actual=1,151  Expected=1,893  AE=0.608

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=495  Expected=487  AE=1.016
  2016: Actual=605  Expected=562  AE=1.077
  2017: Actual=612  Expected=625  AE=0.980
  2018: Actual=738  Expected=690  AE=1.069
  2019: Actual=742  Expected=757  AE=0.980
  2020: Actual=1,014  Expected=826  AE=1.227
  2021: Actual=909  Expected=897  AE=1.014
  2022: Actual=884  Expected=974  AE=0.908
  2023: Actual=965  Expected=1,052  AE=0.917
  2024: Actual=1,072  Expected=1,130  AE=0.948

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,029  Expected=1,013  AE=1.016
  2016: Actual=1,108  Expected=1,142  AE=0.970
  2017: Actual=1,214  Expected=1,241  AE=0.979
  2018: Actual=1,389  Expected=1,342  AE=1.035
  2019: Actual=1,433  Expected=1,441  AE=0.995
  2020: Actual=1,374  Expected=1,545  AE=0.889
  2021: Actual=1,534  Expected=1,653  AE=0.928
  2022: Actual=1,596  Expected=1,768  AE=0.903
  2023: Actual=2,374  Expected=1,876  AE=1.265
  2024: Actual=2,048  Expected=1,980  AE=1.035

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.978
  Cardiovascular: 0.963
  Injury/Accident: 1.010
  Mental Health: 0.994
  Musculoskeletal: 0.992
  Other: 1.001

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 0.976 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient 0.0106/yr, R2 0.09, total 0.096
  step: +0.082 at 2020 (score 1.3)
  YoY sd: empirical 0.1906 vs Poisson 0.0477 -> overdispersion x3.99 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  GIVE-BACK: in 2022 this line's level departs to 1.181 against its own baseline 0.987 (increase) and is back the following year (the move -0.377 is undone by +0.290, ratio 0.77) — that is the shape of a ONE-OFF change CONFINED TO 2022, not a slow build and not a multi-year erratic stretch. Name it as an entry of its own with that single year and direction; keep a dispersion entry as well if you believe the wider stretch is erratic (the two readings are not exclusive)
  onset: max 1yr move / excursion size = 4.36 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 2y up (+0.067) | max 1yr jump 0.377
  smoothed 3y MA: amplitude 0.146 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.57 (gradient 0.0148/yr)
    MA series: 2015:0.94 2016:0.95 2017:0.92 2018:0.95 2019:0.97 2020:1.06 2021:0.99 2022:1.03
  yearly: 2015:0.93(z-1.1) 2016:1.00(z-0.0) 2017:0.90(z-1.8) 2018:0.94(z-1.2) 2019:0.90(z-2.1) 2020:1.02(z+0.4) 2021:0.99(z-0.3) 2022:1.18(z+4.6) 2023:0.80(z-5.3) 2024:1.09(z+2.7)

[CI] mean A/E 1.01 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient -0.004/yr, R2 0.0, total -0.036
  step: -0.188 at 2023 (score 0.7)
  YoY sd: empirical 0.2588 vs Poisson 0.0305 -> overdispersion x8.47 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 2.21 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y down (-0.022) | max 1yr jump 0.503
  level at the END of the series: +0.051 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.191 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.45 (gradient 0.0197/yr)
    MA series: 2015:0.98 2016:0.97 2017:0.98 2018:1.04 2019:1.03 2020:1.16 2021:1.14 2022:1.02
  yearly: 2015:1.04(z+0.9) 2016:0.93(z-1.9) 2017:0.99(z-0.4) 2018:0.99(z-0.4) 2019:0.96(z-1.2) 2020:1.17(z+5.8) 2021:0.96(z-1.4) 2022:1.35(z+13.7) 2023:1.11(z+4.6) 2024:0.61(z-17.1)

[TPD] mean A/E 1.014 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0122/yr, R2 0.15, total -0.11
  step: -0.127 at 2022 (score 3.7)
  excursions (windows whose level differs from the rest, best first): 2015-2021 (7y) +0.127 score 3.7; 2022-2023 (2y) -0.126 score 4.0
  YoY sd: empirical 0.1359 vs Poisson 0.0364 -> overdispersion x3.73 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.96 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y down (-0.319) | max 1yr jump 0.248
  level at the END of the series: -0.107 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.168 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.29 (gradient -0.0128/yr)
    MA series: 2015:1.02 2016:1.04 2017:1.01 2018:1.09 2019:1.07 2020:1.05 2021:0.95 2022:0.92
  yearly: 2015:1.02(z+0.4) 2016:1.08(z+1.8) 2017:0.98(z-0.5) 2018:1.07(z+1.8) 2019:0.98(z-0.6) 2020:1.23(z+6.5) 2021:1.01(z+0.4) 2022:0.91(z-2.9) 2023:0.92(z-2.7) 2024:0.95(z-1.7)

[IP] mean A/E 1.001 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient 0.0086/yr, R2 0.06, total 0.078
  step: +0.186 at 2023 (score 1.6)
  excursions (windows whose level differs from the rest, best first): 2020-2022 (3y) -0.135 score 3.4
  YoY sd: empirical 0.1601 vs Poisson 0.0263 -> overdispersion x6.09 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 2.68 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y up (+0.065) | max 1yr jump 0.363
  level at the END of the series: +0.055 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.161 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.06 (gradient 0.005/yr)
    MA series: 2015:0.99 2016:0.99 2017:1.00 2018:0.97 2019:0.94 2020:0.91 2021:1.03 2022:1.07
  yearly: 2015:1.02(z+0.5) 2016:0.97(z-1.0) 2017:0.98(z-0.8) 2018:1.03(z+1.3) 2019:0.99(z-0.2) 2020:0.89(z-4.4) 2021:0.93(z-2.9) 2022:0.90(z-4.1) 2023:1.26(z+11.5) 2024:1.03(z+1.5)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2020:3 2021:2 2022:1
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2020:1 2023:2 2024:3
  -> 3 of 4 lines take their large swing in the SAME single year above; that is what a book-wide jolt looks like — read those lines in the level rows (step/excursion) rather than raising a dispersion reading on the strength of the swing counts alone. Note what this does and does not rule out: it rules out a multi-year ERRATIC stretch (dispersion), and it does NOT rule out a sustained move, so check each line's own longest-run row as well — a line that runs steadily in ONE direction for several consecutive years is a sustained move in its own right, even when other lines take a single-year jolt

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.978 (z -0.8, expected 1255) -> clean
  Cardiovascular: pooled A/E 0.963 (z -1.1, expected 920) -> clean
  Injury/Accident: pooled A/E 1.01 (z +0.4, expected 1414) -> clean
  Mental Health: pooled A/E 0.994 (z -0.4, expected 4469) -> clean
  Musculoskeletal: pooled A/E 0.992 (z -0.5, expected 3382) -> clean
  Other: pooled A/E 1.001 (z +0.0, expected 1192) -> clean

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

