# Prompt — sc-ca7798

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

Scenario: sc-ca7798

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
      "overall_termination_ae": 1.1395
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
  2015: Actual=612  Expected=596  AE=1.026
  2016: Actual=698  Expected=720  AE=0.969
  2017: Actual=777  Expected=837  AE=0.928
  2018: Actual=854  Expected=963  AE=0.887
  2019: Actual=1,016  Expected=1,097  AE=0.926
  2020: Actual=1,153  Expected=1,239  AE=0.931
  2021: Actual=1,364  Expected=1,386  AE=0.984
  2022: Actual=1,618  Expected=1,548  AE=1.045
  2023: Actual=1,915  Expected=1,719  AE=1.114
  2024: Actual=2,225  Expected=1,893  AE=1.175

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
  2015: Actual=753  Expected=1,013  AE=0.744
  2016: Actual=1,485  Expected=1,142  AE=1.301
  2017: Actual=1,324  Expected=1,241  AE=1.067
  2018: Actual=1,265  Expected=1,342  AE=0.943
  2019: Actual=1,447  Expected=1,441  AE=1.004
  2020: Actual=1,974  Expected=1,545  AE=1.278
  2021: Actual=1,566  Expected=1,653  AE=0.947
  2022: Actual=1,547  Expected=1,768  AE=0.875
  2023: Actual=1,709  Expected=1,876  AE=0.911
  2024: Actual=1,923  Expected=1,980  AE=0.971

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.023
  Cardiovascular: 1.037
  Injury/Accident: 0.966
  Mental Health: 1.466
  Musculoskeletal: 1.002
  Other: 1.019

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.
