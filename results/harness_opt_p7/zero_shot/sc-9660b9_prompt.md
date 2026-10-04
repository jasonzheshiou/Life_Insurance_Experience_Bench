# Prompt — sc-9660b9

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
    flat-topped or single-year excursions. If the excursion moves year over year
    in ONE direction before it peaks or reverts — rising OR falling — prefer
    drift — UNLESS the computed evidence says the biggest single-year move
    EXCEEDS the net excursion of that window, which means the line is swinging
    around instead of holding a level: then the pattern is volatility, not drift.
  * volatility: an increase in year-to-year dispersion with an unchanged level.
    Use this whenever a line's own evidence says its swing exceeds its net level
    change, or when the CROSS-LINE block reports several lines swinging together
    across CONSECUTIVE years. A single-year coordinated swing is NOT this — that
    is what a book-wide shock looks like, so read it in the level rows instead.
    In the multi-year case report it for EVERY affected line over the shared
    years, and if you also believe that line shows a level change, give that a
    separate entry of its own rather than dropping either reading.
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

Scenario: sc-9660b9

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
      "overall_termination_ae": 0.9951
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=224  Expected=240  AE=0.935
  2016: Actual=250  Expected=290  AE=0.863
  2017: Actual=301  Expected=337  AE=0.892
  2018: Actual=359  Expected=390  AE=0.921
  2019: Actual=426  Expected=447  AE=0.954
  2020: Actual=589  Expected=508  AE=1.158
  2021: Actual=703  Expected=576  AE=1.221
  2022: Actual=924  Expected=652  AE=1.417
  2023: Actual=660  Expected=735  AE=0.898
  2024: Actual=715  Expected=826  AE=0.866

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=531  Expected=596  AE=0.890
  2016: Actual=619  Expected=720  AE=0.860
  2017: Actual=750  Expected=837  AE=0.896
  2018: Actual=859  Expected=963  AE=0.892
  2019: Actual=974  Expected=1,097  AE=0.888
  2020: Actual=1,545  Expected=1,239  AE=1.247
  2021: Actual=2,051  Expected=1,386  AE=1.480
  2022: Actual=1,331  Expected=1,548  AE=0.860
  2023: Actual=1,606  Expected=1,719  AE=0.934
  2024: Actual=1,765  Expected=1,893  AE=0.932

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=485  Expected=487  AE=0.996
  2016: Actual=626  Expected=562  AE=1.114
  2017: Actual=645  Expected=625  AE=1.033
  2018: Actual=683  Expected=690  AE=0.990
  2019: Actual=803  Expected=757  AE=1.060
  2020: Actual=1,289  Expected=826  AE=1.560
  2021: Actual=771  Expected=897  AE=0.860
  2022: Actual=381  Expected=974  AE=0.391
  2023: Actual=1,104  Expected=1,052  AE=1.049
  2024: Actual=1,224  Expected=1,130  AE=1.083

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=992  Expected=1,013  AE=0.980
  2016: Actual=1,033  Expected=1,142  AE=0.905
  2017: Actual=1,251  Expected=1,241  AE=1.008
  2018: Actual=1,283  Expected=1,342  AE=0.956
  2019: Actual=1,444  Expected=1,441  AE=1.002
  2020: Actual=2,115  Expected=1,545  AE=1.369
  2021: Actual=1,361  Expected=1,653  AE=0.823
  2022: Actual=1,831  Expected=1,768  AE=1.035
  2023: Actual=1,886  Expected=1,876  AE=1.005
  2024: Actual=1,879  Expected=1,980  AE=0.949

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 0.996
  Cardiovascular: 0.983
  Injury/Accident: 1.034
  Mental Health: 0.988
  Musculoskeletal: 1.004
  Other: 0.961

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.

---
COMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)
Reading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.

[DEATH] mean A/E 1.013 | evidence profile: sustained-move candidate: long same-direction run — check the yearly table; fits may be weak if the move is bounded
  trend: gradient 0.0203/yr, R2 0.11, total 0.182
  step: -0.164 at 2023 (score 2.3)
  excursions (windows whose level differs from the rest, best first): 2020-2022 (3y) +0.361 score 4.6
  YoY sd: empirical 0.2127 vs Poisson 0.0477 -> overdispersion x4.46 (mild overdispersion — z-scores indicative only; this alone is NOT an anomaly)
  onset: max 1yr move / excursion size = 1.44 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 7y up (+0.554) | max 1yr jump 0.519
  NOTE: this line is one of several taking unusually large swings in 2020-2022 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  level at the END of the series: +0.059 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.373 over 2015-2022, fit R2 0.62 (gradient 0.0441/yr)
    MA series: 2015:0.90 2016:0.89 2017:0.92 2018:1.01 2019:1.11 2020:1.27 2021:1.18 2022:1.06
  yearly: 2015:0.94(z-1.0) 2016:0.86(z-2.3) 2017:0.89(z-2.0) 2018:0.92(z-1.6) 2019:0.95(z-1.0) 2020:1.16(z+3.6) 2021:1.22(z+5.3) 2022:1.42(z+10.6) 2023:0.90(z-2.8) 2024:0.87(z-3.9)

[CI] mean A/E 0.988 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient 0.0172/yr, R2 0.06, total 0.155
  step: +0.141 at 2017 (score 1.7)
  excursions (windows whose level differs from the rest, best first): 2020-2021 (2y) +0.469 score 4.0
  YoY sd: empirical 0.2683 vs Poisson 0.0305 -> overdispersion x8.79 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 1.32 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y down (-0.008) | max 1yr jump 0.62
  NOTE: this line is one of several taking unusually large swings in 2020-2022 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  smoothed 3y MA: amplitude 0.323 over 2015-2022, fit R2 0.24 (gradient 0.0278/yr)
    MA series: 2015:0.88 2016:0.88 2017:0.89 2018:1.01 2019:1.21 2020:1.20 2021:1.09 2022:0.91
  yearly: 2015:0.89(z-2.7) 2016:0.86(z-3.8) 2017:0.90(z-3.0) 2018:0.89(z-3.4) 2019:0.89(z-3.7) 2020:1.25(z+8.7) 2021:1.48(z+17.9) 2022:0.86(z-5.5) 2023:0.93(z-2.7) 2024:0.93(z-3.0)

[TPD] mean A/E 1.014 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient -0.0168/yr, R2 0.03, total -0.151
  step: -0.280 at 2021 (score 1.5)
  YoY sd: empirical 0.4214 vs Poisson 0.0364 -> overdispersion x11.58 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 1.44 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y down (-0.125) | max 1yr jump 0.7
  NOTE: this line is one of several taking unusually large swings in 2020-2022 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  level at the END of the series: -0.242 versus this line's own baseline (calibration: clean lines stay within 0.008) — the movement does NOT return to where it started
  smoothed 3y MA: amplitude 0.436 over 2015-2022, fit R2 0.38 (gradient -0.0375/yr)
    MA series: 2015:1.05 2016:1.05 2017:1.03 2018:1.20 2019:1.16 2020:0.94 2021:0.77 2022:0.84
  yearly: 2015:1.00(z-0.1) 2016:1.11(z+2.7) 2017:1.03(z+0.8) 2018:0.99(z-0.3) 2019:1.06(z+1.7) 2020:1.56(z+16.1) 2021:0.86(z-4.2) 2022:0.39(z-19.0) 2023:1.05(z+1.6) 2024:1.08(z+2.8)

[IP] mean A/E 1.003 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation — Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated
  trend: gradient 0.0032/yr, R2 0.0, total 0.029
  step: +0.076 at 2017 (score 1.1)
  YoY sd: empirical 0.2505 vs Poisson 0.0263 -> overdispersion x9.53 (Poisson null INVALID on this line)
  onset: max 1yr move / excursion size = 4.06 (the biggest single-year move EXCEEDS the net excursion — the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change — the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))
  longest run: 3y up (+0.413) | max 1yr jump 0.545
  NOTE: this line is one of several taking unusually large swings in 2020-2022 — the book became erratic as a whole; weigh a book-wide dispersion reading (and still report it for every affected line)
  smoothed 3y MA: amplitude 0.154 over 2015-2022, fit R2 0.04 (gradient 0.0052/yr)
    MA series: 2015:0.96 2016:0.96 2017:0.99 2018:1.11 2019:1.06 2020:1.08 2021:0.95 2022:1.00
  yearly: 2015:0.98(z-0.7) 2016:0.91(z-3.2) 2017:1.01(z+0.3) 2018:0.96(z-1.6) 2019:1.00(z+0.1) 2020:1.37(z+14.5) 2021:0.82(z-7.2) 2022:1.03(z+1.5) 2023:1.00(z+0.2) 2024:0.95(z-2.3)

[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2015:2 2016:2 2017:2 2018:2 2019:2 2020:3 2021:3 2022:2
  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2020:4 2021:3 2022:4 2023:2
  -> 4 of 4 lines swing together in 2020-2022: a COORDINATED dispersion event is plausible — if that is your reading, report it for EACH affected line with the shared years
     This swing spans 3 consecutive years (2020-2022) across 4 lines — a book-wide erratic stretch rather than a one-off jolt, which is the shape the schema calls dispersion: give ALL FOUR benefit lines one entry using that pattern with direction `dispersion` and these years. A line that swings less over that stretch is still part of the same book-wide event — include it unless its own movement ends away from its own baseline, which would make it a level change instead; a swing that returns to baseline is this event itself. For this stretch exactly one dispersion entry per line is the whole answer — do NOT also add a level-change entry covering these years (measured: those paired entries are false alarms on lines whose movement returns to baseline). A genuinely separate move AFTER this stretch, one that ends away from the line's own baseline, is a different finding and does get its own entry
  -> 3 of 4 lines move together in 2020-2021: a COORDINATED move, so weigh one systemic explanation and report it for EACH affected line (the answer schema has no 'all' benefit) rather than four unrelated stories

[IP TERMINATION by diagnosis — pooled, no year dimension] (for recovery patterns)
  Cancer: pooled A/E 0.996 (z -0.1, expected 1259) -> clean
  Cardiovascular: pooled A/E 0.983 (z -0.5, expected 922) -> clean
  Injury/Accident: pooled A/E 1.034 (z +1.3, expected 1373) -> clean
  Mental Health: pooled A/E 0.988 (z -0.8, expected 4543) -> clean
  Musculoskeletal: pooled A/E 1.004 (z +0.3, expected 3374) -> clean
  Other: pooled A/E 0.961 (z -1.4, expected 1242) -> clean

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

