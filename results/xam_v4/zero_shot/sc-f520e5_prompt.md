# Prompt — sc-f520e5

## system

You are an actuary reviewing synthetic life-insurance experience data for a
single book. The data covers four benefit lines: Death, CI (critical illness),
TPD (total permanent disability), and IP (income protection).

Key facts about this data:
- A/E = Actual claims / Expected claims. A clean (baseline) A/E is approximately
  1.0, with sampling noise of order 1/sqrt(expected claim count) per year.
- Anomalies, when present, are one of: a gradual TREND (drift), a one-off SPIKE
  or DROP over a few years (shock), an increase in year-to-year VOLATILITY with
  an unchanged level (dispersion), or a change in IP termination/recovery rates
  for a specific diagnosis (recovery).
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

Scenario: sc-f520e5

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
      "overall_ae": 1.0096,
      "claims": 5048
    },
    "CI": {
      "overall_ae": 0.9989,
      "claims": 11987
    },
    "TPD": {
      "overall_ae": 0.9969,
      "claims": 7975
    },
    "IP": {
      "overall_ae": 0.9962,
      "claims": 14943,
      "overall_termination_ae": 0.9993
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=233  Expected=240  AE=0.973
  2016: Actual=256  Expected=290  AE=0.884
  2017: Actual=316  Expected=337  AE=0.937
  2018: Actual=371  Expected=390  AE=0.952
  2019: Actual=496  Expected=447  AE=1.111
  2020: Actual=590  Expected=508  AE=1.160
  2021: Actual=770  Expected=576  AE=1.338
  2022: Actual=522  Expected=652  AE=0.801
  2023: Actual=696  Expected=735  AE=0.947
  2024: Actual=798  Expected=826  AE=0.966

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=591  Expected=596  AE=0.991
  2016: Actual=714  Expected=720  AE=0.991
  2017: Actual=799  Expected=837  AE=0.954
  2018: Actual=990  Expected=963  AE=1.028
  2019: Actual=1,113  Expected=1,097  AE=1.014
  2020: Actual=1,250  Expected=1,239  AE=1.009
  2021: Actual=1,324  Expected=1,386  AE=0.955
  2022: Actual=1,595  Expected=1,548  AE=1.030
  2023: Actual=1,713  Expected=1,719  AE=0.996
  2024: Actual=1,898  Expected=1,893  AE=1.002

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=478  Expected=487  AE=0.982
  2016: Actual=571  Expected=562  AE=1.016
  2017: Actual=628  Expected=625  AE=1.006
  2018: Actual=701  Expected=690  AE=1.016
  2019: Actual=766  Expected=757  AE=1.011
  2020: Actual=778  Expected=826  AE=0.941
  2021: Actual=915  Expected=897  AE=1.020
  2022: Actual=966  Expected=974  AE=0.992
  2023: Actual=1,060  Expected=1,052  AE=1.008
  2024: Actual=1,112  Expected=1,130  AE=0.984

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=857  Expected=1,013  AE=0.846
  2016: Actual=1,052  Expected=1,142  AE=0.921
  2017: Actual=1,087  Expected=1,241  AE=0.876
  2018: Actual=1,272  Expected=1,342  AE=0.948
  2019: Actual=1,497  Expected=1,441  AE=1.039
  2020: Actual=1,666  Expected=1,545  AE=1.078
  2021: Actual=1,827  Expected=1,653  AE=1.105
  2022: Actual=2,118  Expected=1,768  AE=1.198
  2023: Actual=1,714  Expected=1,876  AE=0.913
  2024: Actual=1,853  Expected=1,980  AE=0.936

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.037
  Cardiovascular: 1.010
  Injury/Accident: 1.021
  Mental Health: 0.985
  Musculoskeletal: 1.006
  Other: 0.961

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.
