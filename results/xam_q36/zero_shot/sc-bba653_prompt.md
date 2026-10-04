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
