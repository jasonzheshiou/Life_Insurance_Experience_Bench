# Prompt — sc-a15166

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

Scenario: sc-a15166

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
      "overall_ae": 1.002,
      "claims": 5010
    },
    "CI": {
      "overall_ae": 1.0083,
      "claims": 12100
    },
    "TPD": {
      "overall_ae": 0.9975,
      "claims": 7980
    },
    "IP": {
      "overall_ae": 1.011,
      "claims": 15165,
      "overall_termination_ae": 1.0037
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=225  Expected=240  AE=0.939
  2016: Actual=335  Expected=290  AE=1.157
  2017: Actual=326  Expected=337  AE=0.966
  2018: Actual=379  Expected=390  AE=0.973
  2019: Actual=451  Expected=447  AE=1.010
  2020: Actual=505  Expected=508  AE=0.993
  2021: Actual=564  Expected=576  AE=0.980
  2022: Actual=661  Expected=652  AE=1.014
  2023: Actual=748  Expected=735  AE=1.018
  2024: Actual=816  Expected=826  AE=0.988

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=599  Expected=596  AE=1.004
  2016: Actual=719  Expected=720  AE=0.998
  2017: Actual=805  Expected=837  AE=0.962
  2018: Actual=998  Expected=963  AE=1.036
  2019: Actual=1,119  Expected=1,097  AE=1.020
  2020: Actual=1,267  Expected=1,239  AE=1.023
  2021: Actual=1,336  Expected=1,386  AE=0.964
  2022: Actual=1,604  Expected=1,548  AE=1.036
  2023: Actual=1,735  Expected=1,719  AE=1.009
  2024: Actual=1,918  Expected=1,893  AE=1.013

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=479  Expected=487  AE=0.984
  2016: Actual=571  Expected=562  AE=1.016
  2017: Actual=628  Expected=625  AE=1.006
  2018: Actual=702  Expected=690  AE=1.017
  2019: Actual=756  Expected=757  AE=0.998
  2020: Actual=778  Expected=826  AE=0.941
  2021: Actual=914  Expected=897  AE=1.019
  2022: Actual=968  Expected=974  AE=0.994
  2023: Actual=1,076  Expected=1,052  AE=1.023
  2024: Actual=1,108  Expected=1,130  AE=0.980

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,229  Expected=1,013  AE=1.214
  2016: Actual=1,362  Expected=1,142  AE=1.193
  2017: Actual=1,503  Expected=1,241  AE=1.211
  2018: Actual=1,092  Expected=1,342  AE=0.814
  2019: Actual=344  Expected=1,441  AE=0.239
  2020: Actual=551  Expected=1,545  AE=0.357
  2021: Actual=2,036  Expected=1,653  AE=1.232
  2022: Actual=2,206  Expected=1,768  AE=1.248
  2023: Actual=2,357  Expected=1,876  AE=1.256
  2024: Actual=2,485  Expected=1,980  AE=1.255

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.019
  Cardiovascular: 1.033
  Injury/Accident: 0.997
  Mental Health: 0.988
  Musculoskeletal: 1.018
  Other: 0.995

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.
