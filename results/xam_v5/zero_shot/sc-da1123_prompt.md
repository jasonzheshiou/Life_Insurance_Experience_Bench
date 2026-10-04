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
