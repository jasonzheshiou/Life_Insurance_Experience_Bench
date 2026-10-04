# Prompt — sc-6fe297

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

Scenario: sc-6fe297

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
      "overall_termination_ae": 0.9972
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
  2015: Actual=600  Expected=596  AE=1.006
  2016: Actual=723  Expected=720  AE=1.004
  2017: Actual=808  Expected=837  AE=0.965
  2018: Actual=1,009  Expected=963  AE=1.048
  2019: Actual=1,124  Expected=1,097  AE=1.024
  2020: Actual=1,269  Expected=1,239  AE=1.024
  2021: Actual=1,346  Expected=1,386  AE=0.971
  2022: Actual=1,618  Expected=1,548  AE=1.045
  2023: Actual=1,740  Expected=1,719  AE=1.012
  2024: Actual=1,934  Expected=1,893  AE=1.021

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=457  Expected=487  AE=0.938
  2016: Actual=537  Expected=562  AE=0.956
  2017: Actual=629  Expected=625  AE=1.007
  2018: Actual=678  Expected=690  AE=0.982
  2019: Actual=757  Expected=757  AE=0.999
  2020: Actual=787  Expected=826  AE=0.952
  2021: Actual=857  Expected=897  AE=0.956
  2022: Actual=1,261  Expected=974  AE=1.295
  2023: Actual=1,013  Expected=1,052  AE=0.963
  2024: Actual=1,074  Expected=1,130  AE=0.950

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,006  Expected=1,013  AE=0.993
  2016: Actual=1,061  Expected=1,142  AE=0.929
  2017: Actual=1,218  Expected=1,241  AE=0.982
  2018: Actual=1,323  Expected=1,342  AE=0.986
  2019: Actual=1,426  Expected=1,441  AE=0.990
  2020: Actual=1,547  Expected=1,545  AE=1.001
  2021: Actual=1,604  Expected=1,653  AE=0.970
  2022: Actual=2,070  Expected=1,768  AE=1.171
  2023: Actual=1,865  Expected=1,876  AE=0.994
  2024: Actual=1,915  Expected=1,980  AE=0.967

artifacts/ae_ip_termination.csv — termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):
  Cancer: 1.002
  Cardiovascular: 1.019
  Injury/Accident: 0.956
  Mental Health: 1.008
  Musculoskeletal: 1.006
  Other: 0.960

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.
