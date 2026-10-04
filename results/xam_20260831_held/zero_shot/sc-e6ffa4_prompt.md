# Prompt — sc-e6ffa4

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

Scenario: sc-e6ffa4

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
      "overall_ae": 0.9872,
      "claims": 4936
    },
    "CI": {
      "overall_ae": 1.0038,
      "claims": 12046
    },
    "TPD": {
      "overall_ae": 1.0045,
      "claims": 8036
    },
    "IP": {
      "overall_ae": 1.0066,
      "claims": 15099,
      "overall_termination_ae": 0.9921
    }
  }
}

artifacts/ae_death_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=223  Expected=240  AE=0.931
  2016: Actual=289  Expected=290  AE=0.998
  2017: Actual=305  Expected=337  AE=0.904
  2018: Actual=366  Expected=390  AE=0.939
  2019: Actual=403  Expected=447  AE=0.902
  2020: Actual=517  Expected=508  AE=1.017
  2021: Actual=568  Expected=576  AE=0.987
  2022: Actual=770  Expected=652  AE=1.181
  2023: Actual=591  Expected=735  AE=0.804
  2024: Actual=904  Expected=826  AE=1.094

artifacts/ae_ci_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=619  Expected=596  AE=1.038
  2016: Actual=669  Expected=720  AE=0.929
  2017: Actual=826  Expected=837  AE=0.987
  2018: Actual=950  Expected=963  AE=0.986
  2019: Actual=1,059  Expected=1,097  AE=0.965
  2020: Actual=1,443  Expected=1,239  AE=1.165
  2021: Actual=1,332  Expected=1,386  AE=0.961
  2022: Actual=2,088  Expected=1,548  AE=1.349
  2023: Actual=1,909  Expected=1,719  AE=1.110
  2024: Actual=1,151  Expected=1,893  AE=0.608

artifacts/ae_tpd_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=495  Expected=487  AE=1.016
  2016: Actual=605  Expected=562  AE=1.077
  2017: Actual=612  Expected=625  AE=0.980
  2018: Actual=738  Expected=690  AE=1.069
  2019: Actual=742  Expected=757  AE=0.980
  2020: Actual=1,014  Expected=826  AE=1.227
  2021: Actual=909  Expected=897  AE=1.014
  2022: Actual=884  Expected=974  AE=0.908
  2023: Actual=965  Expected=1,052  AE=0.917
  2024: Actual=1,072  Expected=1,130  AE=0.948

artifacts/ae_ip_by_year.csv — yearly (Actual, Expected, AE):
  2015: Actual=1,029  Expected=1,013  AE=1.016
  2016: Actual=1,108  Expected=1,142  AE=0.970
  2017: Actual=1,214  Expected=1,241  AE=0.979
  2018: Actual=1,389  Expected=1,342  AE=1.035
  2019: Actual=1,433  Expected=1,441  AE=0.995
  2020: Actual=1,374  Expected=1,545  AE=0.889
  2021: Actual=1,534  Expected=1,653  AE=0.928
  2022: Actual=1,596  Expected=1,768  AE=0.903
  2023: Actual=2,374  Expected=1,876  AE=1.265
  2024: Actual=2,048  Expected=1,980  AE=1.035

artifacts/ae_ip_termination.csv — mean termination A/E per diagnosis (mean over duration months; 1.0 = baseline recovery rate):
  Cancer: 0.998
  Cardiovascular: 0.831
  Injury/Accident: 1.050
  Mental Health: 0.889
  Musculoskeletal: 0.736
  Other: 1.244

Now analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.
