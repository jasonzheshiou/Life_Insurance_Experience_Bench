# Prompt — sc-9660b9

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
