# Prompt — sc-0ce4d6

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
