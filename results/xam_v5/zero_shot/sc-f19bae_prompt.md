# Prompt — sc-f19bae

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

Scenario: sc-f19bae

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
  2015: Actual=721  Expected=596  AE=1.209
  2016: Actual=851  Expected=720  AE=1.182
  2017: Actual=844  Expected=837  AE=1.008
  2018: Actual=986  Expected=963  AE=1.024
  2019: Actual=1,085  Expected=1,097  AE=0.989
  2020: Actual=1,229  Expected=1,239  AE=0.992
  2021: Actual=1,318  Expected=1,386  AE=0.951
  2022: Actual=1,535  Expected=1,548  AE=0.991
  2023: Actual=1,708  Expected=1,719  AE=0.994
  2024: Actual=1,894  Expected=1,893  AE=1.000

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=665  Expected=487  AE=1.366
  2016: Actual=727  Expected=562  AE=1.294
  2017: Actual=608  Expected=625  AE=0.973
  2018: Actual=633  Expected=690  AE=0.917
  2019: Actual=750  Expected=757  AE=0.990
  2020: Actual=772  Expected=826  AE=0.934
  2021: Actual=886  Expected=897  AE=0.988
  2022: Actual=906  Expected=974  AE=0.930
  2023: Actual=1,036  Expected=1,052  AE=0.985
  2024: Actual=1,067  Expected=1,130  AE=0.944

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
