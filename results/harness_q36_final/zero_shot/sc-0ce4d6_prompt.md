# Prompt — sc-0ce4d6

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

Scenario: sc-0ce4d6

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
      "overall_ae": 1.0029,
      "claims": 12035
    },
    "TPD": {
      "overall_ae": 0.9945,
      "claims": 7956
    },
    "IP": {
      "overall_ae": 1.0005,
      "claims": 15008,
      "overall_termination_ae": 0.9941
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=224  Expected=240  AE=0.935
  2016: Actual=332  Expected=290  AE=1.146
  2017: Actual=324  Expected=337  AE=0.961
  2018: Actual=378  Expected=390  AE=0.970
  2019: Actual=447  Expected=447  AE=1.001
  2020: Actual=502  Expected=508  AE=0.987
  2021: Actual=562  Expected=576  AE=0.976
  2022: Actual=658  Expected=652  AE=1.009
  2023: Actual=746  Expected=735  AE=1.015
  2024: Actual=813  Expected=826  AE=0.984

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=543  Expected=596  AE=0.910
  2016: Actual=654  Expected=720  AE=0.908
  2017: Actual=793  Expected=837  AE=0.947
  2018: Actual=788  Expected=963  AE=0.818
  2019: Actual=1,015  Expected=1,097  AE=0.925
  2020: Actual=1,021  Expected=1,239  AE=0.824
  2021: Actual=1,222  Expected=1,386  AE=0.882
  2022: Actual=2,186  Expected=1,548  AE=1.412
  2023: Actual=2,126  Expected=1,719  AE=1.237
  2024: Actual=1,687  Expected=1,893  AE=0.891

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=476  Expected=487  AE=0.977
  2016: Actual=569  Expected=562  AE=1.013
  2017: Actual=628  Expected=625  AE=1.006
  2018: Actual=705  Expected=690  AE=1.022
  2019: Actual=761  Expected=757  AE=1.005
  2020: Actual=777  Expected=826  AE=0.940
  2021: Actual=913  Expected=897  AE=1.018
  2022: Actual=961  Expected=974  AE=0.987
  2023: Actual=1,061  Expected=1,052  AE=1.009
  2024: Actual=1,105  Expected=1,130  AE=0.977

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,016  Expected=1,013  AE=1.003
  2016: Actual=1,183  Expected=1,142  AE=1.036
  2017: Actual=1,279  Expected=1,241  AE=1.031
  2018: Actual=1,329  Expected=1,342  AE=0.990
  2019: Actual=1,436  Expected=1,441  AE=0.997
  2020: Actual=1,528  Expected=1,545  AE=0.989
  2021: Actual=1,592  Expected=1,653  AE=0.963
  2022: Actual=1,770  Expected=1,768  AE=1.001
  2023: Actual=1,887  Expected=1,876  AE=1.006
  2024: Actual=1,988  Expected=1,980  AE=1.004

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.005
  Cardiovascular: 1.007
  Injury/Accident: 0.992
  Mental Health: 0.972
  Musculoskeletal: 1.005
  Other: 1.029

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 0.998 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0014/yr, R2 0.01, total -0.013
  step: -0.053 at 2017 (score 0.5)
  YoY sd: empirical 0.1013 vs Poisson 0.0477 -> overdispersion x2.12 (Poisson null approximately valid)
  longest run: 3y up (+0.040) | max 1yr jump 0.211
  smoothed 3y MA: amplitude 0.048 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.09 (gradient -0.0019/yr)
    MA series: 2015:1.01 2016:1.03 2017:0.98 2018:0.99 2019:0.99 2020:0.99 2021:1.00 2022:1.00
  yearly: 2015:0.94(z-1.0) 2016:1.15(z+2.5) 2017:0.96(z-0.7) 2018:0.97(z-0.6) 2019:1.00(z+0.0) 2020:0.99(z-0.3) 2021:0.98(z-0.6) 2022:1.01(z+0.2) 2023:1.01(z+0.4) 2024:0.98(z-0.5)

[CI] mean A/E 0.975 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient 0.0275/yr, R2 0.19, total 0.247
  step: +0.292 at 2022 (score 1.9)
  excursions (windows whose level differs from the rest, best first): 2022-2023 (2y) +0.436 score 4.9
  YoY sd: empirical 0.2435 vs Poisson 0.0305 -> overdispersion x7.97 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 1.22 (essentially the whole excursion arrives in ONE year, then holds — a one-off level change, not a build-up. CAUTION — this line ALSO carries a 3-year up run totalling +0.588, which is a sustained move in its own right; the ratio above is measured against the excursion window, not against that run, so weigh both readings and name the years you decide on rather than defaulting to the one-off one)
  longest run: 3y up (+0.588) | max 1yr jump 0.53
  level at the END of the series: +0.256 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  TAIL: in the FINAL years 2022-2024 the line moves steadily down (-0.260/yr, fit R2 0.97), ending +0.292 against the years before that (values 2022:1.41 2023:1.24 2024:0.89). Calibration: clean lines never reach this block (|gradient| <= 0.013), while genuine slow movements do — a steady final-years move that leaves the level away from its earlier value is a sustained move in its own right, so report it with THESE years even when an earlier event on the same line is bigger and already reported
  smoothed 3y MA: amplitude 0.324 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.64 (gradient 0.0438/yr)
    MA series: 2015:0.92 2016:0.89 2017:0.90 2018:0.86 2019:0.88 2020:1.04 2021:1.18 2022:1.18
  yearly: 2015:0.91(z-2.2) 2016:0.91(z-2.5) 2017:0.95(z-1.5) 2018:0.82(z-5.6) 2019:0.93(z-2.5) 2020:0.82(z-6.2) 2021:0.88(z-4.4) 2022:1.41(z+16.2) 2023:1.24(z+9.8) 2024:0.89(z-4.7)

[TPD] mean A/E 0.995 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0012/yr, R2 0.02, total -0.011
  step: -0.018 at 2020 (score 1.2)
  YoY sd: empirical 0.0426 vs Poisson 0.0364 -> overdispersion x1.17 (Poisson null approximately valid)
  longest run: 3y down (-0.081) | max 1yr jump 0.078
  smoothed 3y MA: amplitude 0.031 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.22 (gradient -0.0022/yr)
    MA series: 2015:1.00 2016:1.01 2017:1.01 2018:0.99 2019:0.99 2020:0.98 2021:1.00 2022:0.99
  yearly: 2015:0.98(z-0.5) 2016:1.01(z+0.3) 2017:1.01(z+0.1) 2018:1.02(z+0.6) 2019:1.00(z+0.1) 2020:0.94(z-1.7) 2021:1.02(z+0.5) 2022:0.99(z-0.4) 2023:1.01(z+0.3) 2024:0.98(z-0.8)

[IP] mean A/E 1.002 | evidence profile: no strong signal — judge from the yearly table and null-validity columns
  trend: gradient -0.0027/yr, R2 0.15, total -0.024
  step: -0.031 at 2018 (score 2.6)
  excursions (windows whose level differs from the rest, best first): 2016-2017 (2y) +0.039 score 7.0
  YoY sd: empirical 0.0249 vs Poisson 0.0263 -> overdispersion x0.95 (Poisson null approximately valid)
  longest run: 3y down (-0.046) | max 1yr jump 0.041
  smoothed 3y MA: amplitude 0.041 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.46 (gradient -0.0043/yr)
    MA series: 2015:1.02 2016:1.02 2017:1.01 2018:0.99 2019:0.98 2020:0.98 2021:0.99 2022:1.00
  yearly: 2015:1.00(z+0.1) 2016:1.04(z+1.2) 2017:1.03(z+1.1) 2018:0.99(z-0.4) 2019:1.00(z-0.1) 2020:0.99(z-0.4) 2021:0.96(z-1.5) 2022:1.00(z+0.0) 2023:1.01(z+0.2) 2024:1.00(z+0.2)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2020:1 2021:1 2022:1
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:2 2017:1 2018:1 2021:2 2022:2 2024:1

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 1.005 (z +0.2, expected 1259) -> clean
  Cardiovascular: pooled A/E 1.007 (z +0.2, expected 899) -> clean
  Injury/Accident: pooled A/E 0.992 (z -0.3, expected 1428) -> clean
  Mental Health: pooled A/E 0.972 (z -1.9, expected 4505) -> clean
  Musculoskeletal: pooled A/E 1.005 (z +0.3, expected 3334) -> clean
  Other: pooled A/E 1.029 (z +1.0, expected 1169) -> clean

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

