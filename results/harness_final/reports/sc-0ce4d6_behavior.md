# Behavioural dossier — scenario `sc-0ce4d6`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 3 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** volatility on CI [2017, 2023] (sigma=0.3).
**What the model said:**
- run 1: CI / shock / increase (confidence 0.9) — FALSE POSITIVE
- run 1: CI / volatility / dispersion (confidence 0.7) — TRUE POSITIVE
- run 2: CI / shock / increase (confidence 0.9) — FALSE POSITIVE
- run 2: CI / volatility / dispersion (confidence 0.8) — TRUE POSITIVE
- run 3: CI / shock / increase (confidence 0.85) — FALSE POSITIVE
- run 3: CI / volatility / dispersion (confidence 0.7) — TRUE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — trap_noise_drift_lookalike_b (noise_trap family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: volatility on CI [2017, 2023] (sigma=0.3).

**Diagnosis to trust:** the injected irregularity was named correctly (volatility on CI [2017, 2023] (sigma=0.3)).

Confidence stated on the correct finding: 0.7, 0.8, 0.7.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 14205 chars, sha256 `389ecff43dd828d31d95d997ffc78fde85283fc83c98adf90bce628223a931f5`
- the exact prompt text is archived at `results/harness_final/zero_shot/sc-0ce4d6_prompt.md`
- samplers: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0}
- `max_tokens`: **not sent** · `stream`: `True` · termination aggregation: `pooled`
- files shown: listing only; contents of `summary.json` and the per-benefit yearly A/E + IP termination tables

### What was sent (verbatim request body, redacted messages)

```json
{
  "model": "Qwen3.8-27B-Q8_0",
  "temperature": 1.0,
  "seed": 1234,
  "multi_turn": true,
  "initial_messages": [
    {
      "role": "system",
      "content": "You are an actuary reviewing synthetic life-insurance experience data for a\nsingle book. The data covers four benefit lines: Death, CI (critical illness),\nTPD (total permanent disability), and IP (income protection).\n\nKey facts about this data:\n- A/E = Actual claims / Expected claims. A clean (baseline) A/E is approximately\n  1.0, with sampling noise of order 1/sqrt(expected claim count) per year.\n- Anomalies, when present, are one of:\n  * drift: a sustained year-over-year move in A/E over 2+ years. A drift does\n    NOT have to continue to the last data year: a trend confined to a sub-window\n    that later reverts toward baseline is STILL drift \u2014 a reversion at the end is\n    not evidence against the trend that came before it. When reporting drift,\n    set years to the FULL window of the trend INCLUDING the gentle early ramp\n    years, and note the reversion (if any) in the evidence.\n  * shock: an abrupt level change (spike or drop) WITHOUT a gradual build-up \u2014\n    flat-topped or single-year excursions. If the excursion moves year over year\n    in ONE direction before it peaks or reverts \u2014 rising OR falling \u2014 prefer\n    drift \u2014 UNLESS the computed evidence says the biggest single-year move\n    EXCEEDS the net excursion of that window, which means the line is swinging\n    around instead of holding a level: then the pattern is volatility, not drift.\n  * volatility: an increase in year-to-year dispersion with an unchanged level.\n    Use this whenever a line's own evidence says its swing exceeds its net level\n    change, or when the CROSS-LINE block reports several lines swinging together\n    across CONSECUTIVE years. A single-year coordinated swing is NOT this \u2014 that\n    is what a book-wide shock looks like, so read it in the level rows instead.\n    In the multi-year case report it for EVERY affected line over the shared\n    years, and if you also believe that line shows a level change, give that a\n    separate entry of its own rather than dropping either reading.\n  * recovery: a change in IP termination/recovery rates for a specific diagnosis.\n- Statistical discipline: before quoting any z-score or sigma computed under a\n  Poisson (1/sqrt(E)) null for a benefit line, compare that line's empirical\n  year-to-year standard deviation of A/E against the Poisson expectation. If the\n  data is overdispersed (empirical SD materially larger), the Poisson null is\n  invalid: describe the anomaly as volatility/dispersion rather than flagging\n  individual years against the Poisson null, and never re-apply Poisson z-scores\n  inside a window you have already identified as volatile.\n- Random noise can LOOK like a trend or a spike. Be conservative: do not invent\n  anomalies just to appear useful. If the data is consistent with noise, say so.\n\nYour task:\n1. Identify any anomalies or notable insights in the data you are given.\n2. For each finding, say WHERE it is (benefit line, which years), WHAT kind of\n   pattern it is, the direction and rough magnitude, how confident you are, the\n   evidence you are relying on, and WHAT ACTION you would recommend\n   (investigation steps, assumption review, pricing/valuation follow-up).\n3. If you see nothing anomalous, say so explicitly.\n\nRespond with ONLY a JSON object matching this shape (no prose outside it):\n\n{\n  \"scenario_id\": \"<the scenario id you were given>\",\n  \"overall_assessment\": \"clean\" | \"anomalies\",\n  \"findings\": [\n    {\n      \"benefit\": \"Death\" | \"CI\" | \"TPD\" | \"IP\",\n      \"years\": [start_year, end_year] | null,\n      \"pattern\": \"drift\" | \"shock\" | \"volatility\" | \"recovery\" | \"other\",\n      \"direction\": \"increase\" | \"decrease\" | \"dispersion\",\n      \"magnitude\": \"free text, e.g. ~+0.10/yr, x1.5, sigma=0.3\",\n      \"confidence\": 0.0-1.0,\n      \"evidence\": [\"short, checkable: which file/rows support this\"],\n      \"recommended_action\": \"what you would do next\"\n    }\n  ]\n}"
    },
    {
      "role": "user",
      "content": "Scenario: sc-0ce4d6\n\nFiles available (paths are relative to the scenario folder):\n  - artifacts/ae_ci.csv\n  - artifacts/ae_ci_age_gender.csv\n  - artifacts/ae_ci_age_gender.png\n  - artifacts/ae_ci_by_year.csv\n  - artifacts/ae_ci_by_year.png\n  - artifacts/ae_death.csv\n  - artifacts/ae_death_age_gender.csv\n  - artifacts/ae_death_age_gender.png\n  - artifacts/ae_death_by_year.csv\n  - artifacts/ae_death_by_year.png\n  - artifacts/ae_ip.csv\n  - artifacts/ae_ip_age_gender.csv\n  - artifacts/ae_ip_age_gender.png\n  - artifacts/ae_ip_by_year.csv\n  - artifacts/ae_ip_by_year.png\n  - artifacts/ae_ip_termination.csv\n  - artifacts/ae_ip_termination_by_month.csv\n  - artifacts/ae_ip_termination_by_month.png\n  - artifacts/ae_tpd.csv\n  - artifacts/ae_tpd_age_gender.csv\n  - artifacts/ae_tpd_age_gender.png\n  - artifacts/ae_tpd_by_year.csv\n  - artifacts/ae_tpd_by_year.png\n  - artifacts/summary.json\n  - benchmarks/CI.csv\n  - benchmarks/Death.csv\n  - benchmarks/IP.csv\n  - benchmarks/TPD.csv\n  - ci_claims.csv\n  - death_claims.csv\n  - exposure.csv\n  - ip_claims.csv\n  - scenario_id.txt\n  - tpd_claims.csv\n\nsummary.json (overall A/E per benefit, claim counts):\n{\n  \"benefits\": {\n    \"Death\": {\n      \"overall_ae\": 0.9972,\n      \"claims\": 4986\n    },\n    \"CI\": {\n      \"overall_ae\": 1.0029,\n      \"claims\": 12035\n    },\n    \"TPD\": {\n      \"overall_ae\": 0.9945,\n      \"claims\": 7956\n    },\n    \"IP\": {\n      \"overall_ae\": 1.0005,\n      \"claims\": 15008,\n      \"overall_termination_ae\": 0.9941\n    }\n  }\n}\n\nartifacts/ae_death_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=224  Expected=240  AE=0.935\n  2016: Actual=332  Expected=290  AE=1.146\n  2017: Actual=324  Expected=337  AE=0.961\n  2018: Actual=378  Expected=390  AE=0.970\n  2019: Actual=447  Expected=447  AE=1.001\n  2020: Actual=502  Expected=508  AE=0.987\n  2021: Actual=562  Expected=576  AE=0.976\n  2022: Actual=658  Expected=652  AE=1.009\n  2023: Actual=746  Expected=735  AE=1.015\n  2024: Actual=813  Expected=826  AE=0.984\n\nartifacts/ae_ci_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=543  Expected=596  AE=0.910\n  2016: Actual=654  Expected=720  AE=0.908\n  2017: Actual=793  Expected=837  AE=0.947\n  2018: Actual=788  Expected=963  AE=0.818\n  2019: Actual=1,015  Expected=1,097  AE=0.925\n  2020: Actual=1,021  Expected=1,239  AE=0.824\n  2021: Actual=1,222  Expected=1,386  AE=0.882\n  2022: Actual=2,186  Expected=1,548  AE=1.412\n  2023: Actual=2,126  Expected=1,719  AE=1.237\n  2024: Actual=1,687  Expected=1,893  AE=0.891\n\nartifacts/ae_tpd_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=476  Expected=487  AE=0.977\n  2016: Actual=569  Expected=562  AE=1.013\n  2017: Actual=628  Expected=625  AE=1.006\n  2018: Actual=705  Expected=690  AE=1.022\n  2019: Actual=761  Expected=757  AE=1.005\n  2020: Actual=777  Expected=826  AE=0.940\n  2021: Actual=913  Expected=897  AE=1.018\n  2022: Actual=961  Expected=974  AE=0.987\n  2023: Actual=1,061  Expected=1,052  AE=1.009\n  2024: Actual=1,105  Expected=1,130  AE=0.977\n\nartifacts/ae_ip_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=1,016  Expected=1,013  AE=1.003\n  2016: Actual=1,183  Expected=1,142  AE=1.036\n  2017: Actual=1,279  Expected=1,241  AE=1.031\n  2018: Actual=1,329  Expected=1,342  AE=0.990\n  2019: Actual=1,436  Expected=1,441  AE=0.997\n  2020: Actual=1,528  Expected=1,545  AE=0.989\n  2021: Actual=1,592  Expected=1,653  AE=0.963\n  2022: Actual=1,770  Expected=1,768  AE=1.001\n  2023: Actual=1,887  Expected=1,876  AE=1.006\n  2024: Actual=1,988  Expected=1,980  AE=1.004\n\nartifacts/ae_ip_termination.csv \u2014 termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):\n  Cancer: 1.005\n  Cardiovascular: 1.007\n  Injury/Accident: 0.992\n  Mental Health: 0.972\n  Musculoskeletal: 1.005\n  Other: 1.029\n\nNow analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.\n\n---\nCOMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)\nReading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.\n\n[DEATH] mean A/E 0.998 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0014/yr, R2 0.01, total -0.013\n  step: -0.053 at 2017 (score 0.5)\n  YoY sd: empirical 0.1013 vs Poisson 0.0477 -> overdispersion x2.12 (Poisson null approximately valid)\n  longest run: 3y up (+0.040) | max 1yr jump 0.211\n  smoothed 3y MA: amplitude 0.048 over 2015-2022, fit R2 0.09 (gradient -0.0019/yr)\n    MA series: 2015:1.01 2016:1.03 2017:0.98 2018:0.99 2019:0.99 2020:0.99 2021:1.00 2022:1.00\n  yearly: 2015:0.94(z-1.0) 2016:1.15(z+2.5) 2017:0.96(z-0.7) 2018:0.97(z-0.6) 2019:1.00(z+0.0) 2020:0.99(z-0.3) 2021:0.98(z-0.6) 2022:1.01(z+0.2) 2023:1.01(z+0.4) 2024:0.98(z-0.5)\n\n[CI] mean A/E 0.975 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation \u2014 Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated\n  trend: gradient 0.0275/yr, R2 0.19, total 0.247\n  step: +0.292 at 2022 (score 1.9)\n  excursions (windows whose level differs from the rest, best first): 2022-2023 (2y) +0.436 score 4.9\n  YoY sd: empirical 0.2435 vs Poisson 0.0305 -> overdispersion x7.97 (Poisson null INVALID on this line)\n  onset: max 1yr move / excursion size = 1.22 (essentially the whole excursion arrives in ONE year, then holds \u2014 a one-off level change, not a build-up)\n  longest run: 3y up (+0.588) | max 1yr jump 0.53\n  level at the END of the series: +0.256 versus this line's own baseline (calibration: clean lines stay within 0.008) \u2014 the movement does NOT return to where it started\n  TAIL: in the FINAL years 2022-2024 the line moves steadily down (-0.260/yr, fit R2 0.97), ending +0.292 against the years before that (values 2022:1.41 2023:1.24 2024:0.89). Calibration: clean lines never reach this block (|gradient| <= 0.013), while genuine slow movements do \u2014 a steady final-years move that leaves the level away from its earlier value is a sustained move in its own right, so report it with THESE years even when an earlier event on the same line is bigger and already reported\n  smoothed 3y MA: amplitude 0.324 over 2015-2022, fit R2 0.64 (gradient 0.0438/yr)\n    MA series: 2015:0.92 2016:0.89 2017:0.90 2018:0.86 2019:0.88 2020:1.04 2021:1.18 2022:1.18\n  yearly: 2015:0.91(z-2.2) 2016:0.91(z-2.5) 2017:0.95(z-1.5) 2018:0.82(z-5.6) 2019:0.93(z-2.5) 2020:0.82(z-6.2) 2021:0.88(z-4.4) 2022:1.41(z+16.2) 2023:1.24(z+9.8) 2024:0.89(z-4.7)\n\n[TPD] mean A/E 0.995 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0012/yr, R2 0.02, total -0.011\n  step: -0.018 at 2020 (score 1.2)\n  YoY sd: empirical 0.0426 vs Poisson 0.0364 -> overdispersion x1.17 (Poisson null approximately valid)\n  longest run: 3y down (-0.081) | max 1yr jump 0.078\n  smoothed 3y MA: amplitude 0.031 over 2015-2022, fit R2 0.22 (gradient -0.0022/yr)\n    MA series: 2015:1.00 2016:1.01 2017:1.01 2018:0.99 2019:0.99 2020:0.98 2021:1.00 2022:0.99\n  yearly: 2015:0.98(z-0.5) 2016:1.01(z+0.3) 2017:1.01(z+0.1) 2018:1.02(z+0.6) 2019:1.00(z+0.1) 2020:0.94(z-1.7) 2021:1.02(z+0.5) 2022:0.99(z-0.4) 2023:1.01(z+0.3) 2024:0.98(z-0.8)\n\n[IP] mean A/E 1.002 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0027/yr, R2 0.15, total -0.024\n  step: -0.031 at 2018 (score 2.6)\n  excursions (windows whose level differs from the rest, best first): 2016-2017 (2y) +0.039 score 7.0\n  YoY sd: empirical 0.0249 vs Poisson 0.0263 -> overdispersion x0.95 (Poisson null approximately valid)\n  longest run: 3y down (-0.046) | max 1yr jump 0.041\n  smoothed 3y MA: amplitude 0.041 over 2015-2022, fit R2 0.46 (gradient -0.0043/yr)\n    MA series: 2015:1.02 2016:1.02 2017:1.01 2018:0.99 2019:0.98 2020:0.98 2021:0.99 2022:1.00\n  yearly: 2015:1.00(z+0.1) 2016:1.04(z+1.2) 2017:1.03(z+1.1) 2018:0.99(z-0.4) 2019:1.00(z-0.1) 2020:0.99(z-0.4) 2021:0.96(z-1.5) 2022:1.00(z+0.0) 2023:1.01(z+0.2) 2024:1.00(z+0.2)\n\n[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2020:1 2021:1 2022:1\n  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:2 2017:1 2018:1 2021:2 2022:2 2024:1\n\n[IP TERMINATION by diagnosis \u2014 pooled, no year dimension] (for recovery patterns)\n  Cancer: pooled A/E 1.005 (z +0.2, expected 1259) -> clean\n  Cardiovascular: pooled A/E 1.007 (z +0.2, expected 899) -> clean\n  Injury/Accident: pooled A/E 0.992 (z -0.3, expected 1428) -> clean\n  Mental Health: pooled A/E 0.972 (z -1.9, expected 4505) -> clean\n  Musculoskeletal: pooled A/E 1.005 (z +0.3, expected 3334) -> clean\n  Other: pooled A/E 1.029 (z +1.0, expected 1169) -> clean\n\nHARNESS MODE \u2014 you are not limited to eyeballing the tables above.\n\n1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact\n   CSVs) is appended at the end of this message. Trust its arithmetic over\n   mental math, but the final judgement is yours: confirm or override its\n   per-line heuristic verdicts.\n\n2) You may compute anything else you need. To use the tool, reply with ONLY a\n   JSON object (no other text, no <tool_call> tags, no function-call syntax):\n     {\"tool\": \"python\", \"code\": \"<python source as one JSON string>\"}\n   The code runs with the scenario's artifacts/ directory as cwd (open files\n   by relative path, e.g. open(\"ae_death_by_year.csv\")); plain stdlib Python\n   (csv, math, statistics); 10 s limit; output is returned verbatim.\n   You get at most 4 tool calls. NEVER write files or read outside artifacts/.\n\n3) When done \u2014 with or without tools \u2014 reply with ONLY the final JSON object\n   in the required shape. Do not put tool requests inside that final JSON.\n\n3b) Work efficiently: the evidence pack already contains the arithmetic. At most\n   TWO tool calls, and if the pack answers the question, answer immediately\n   without any tool call. Never spend more turns than the problem needs.\n\n3c) Books where several lines move together: when the CROSS-LINE block reports a\n   coordinated move or coordinated swings over a run of consecutive years, treat\n   it as ONE underlying event but report it for EVERY affected line \u2014 the output\n   schema has no \"all\" benefit, so a four-line event needs four entries sharing\n   the years. Do not tell four unrelated stories, and do not drop lines. This\n   means one entry per affected line EVEN WHEN one line's own move is much\n   smaller than the others, and even when you discuss the shared cause only once:\n   an answer that names the largest line and merely mentions the others in prose\n   is graded as having found only the largest line.\n\n4) Discipline (these are scored):\n   * Overdispersion is NOT a finding by itself. Report a dispersion\n     finding only when the elevated year-to-year scatter is the material\n     anomaly for that line (roughly x6 or more versus the Poisson expectation,\n     with a level that stays flat). Mild overdispersion, and any line whose\n     evidence profile says \"no strong signal\", must NOT be reported as a\n     finding merely because its scatter is above Poisson. The one exception is\n     the book-wide case: when the CROSS-LINE block reports several lines\n     swinging together across consecutive years, that shared evidence stands on\n     its own, and every affected line gets its dispersion entry even if that\n     line's own ratio is below the x6 guide.\n   * Use the pattern the evidence actually describes. A single-year deviation\n     that reverts is a one-off change; a movement that builds and then flattens\n     or runs on is a sustained move; a stretch where the line swings around\n     without ever settling at a new level is dispersion. The schema's taxonomy\n     above defines each pattern word. When a per-line note says the biggest\n     single-year move EXCEEDS the net excursion, the evidence cannot separate a\n     give-back ramp from an erratic stretch: give that line a dispersion entry\n     AND keep the level-change reading as an entry of its own, so both readings\n     are on the record (one entry of each kind per line, never two of the same).\n   * A one-year wobble is only a finding if the year is genuinely extreme:\n     require a Poisson z of about 4.5 or more for that year (A/E alone is\n     misleading when the expected count is small). A single-year excursion\n     around z 3 is the kind of thing ordinary books produce, so leave it out.\n     Where a line's own scatter already exceeds Poisson, per-year z-scores are\n     unreliable \u2014 then require a larger move, or describe the stretch as\n     dispersion instead of claiming a one-off change.\n   * Every entry in \"findings\" is a claim that something material happened and\n     should be investigated. A favourable deviation (A/E materially BELOW\n     expectation), a movement you have decided is ordinary, and any observation\n     you are not claiming must not appear as its own entry \u2014 mention it in the\n     evidence text of a finding you ARE making, or leave it out entirely.\n     Listing an observation you are not claiming is scored as a false alarm.\n   * Do not describe the same movement twice. If a line's final years reverse a\n     movement you have already reported for that line, that reversal is part of\n     the earlier event: say so inside that finding rather than adding a second\n     entry for the same line.\n   * Small cells are not evidence: age-band or duration-month A/E values rest\n     on tiny expected counts and go extreme by chance. Never report a\n     book-level anomaly from such a cell unless the same effect is visible in\n     the by-year series or the pooled line.\n   * Findings you considered and rejected for these reasons do not appear in\n     the \"findings\" array at all.\n"
    }
  ]
}
```

### Per-run facts

| run | seed | wall time | completion tok | prompt tok | finish | answer chars | reasoning chars | error |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1234 | 890s | 15955 | 6617 | stop | 2759 | 43235 | ok |
| 2 | 1235 | 981s | 15554 | 6617 | stop | 1928 | 46680 | ok |
| 3 | 1236 | 2340s | 39503 | 14705 | stop | 2107 | 62136 | ok |

### Tool use (did it do anything besides read the text?)

| check | result |
|---|---|
| tools offered in request | `False` |
| tool calls in response | `False` |
| code fences in output | `False` |
| python code / file reads in output | `False` |
| asked to inspect files | `True` |

The runner offers no tools (`tools`/`function_call` keys never appear in the request) and the server returned none. The model answered from the text alone.

### The data it saw (for replaying its reasoning)

**Death** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.935  (≈-1.0σ from 1.0)  
    2016: A/E=1.146  (≈+2.5σ from 1.0)  <== +2.5 sigma
    2017: A/E=0.961  (≈-0.7σ from 1.0)  
    2018: A/E=0.970  (≈-0.6σ from 1.0)  
    2019: A/E=1.001  (≈+0.0σ from 1.0)  
    2020: A/E=0.987  (≈-0.3σ from 1.0)  
    2021: A/E=0.976  (≈-0.6σ from 1.0)  
    2022: A/E=1.009  (≈+0.2σ from 1.0)  
    2023: A/E=1.015  (≈+0.4σ from 1.0)  
    2024: A/E=0.984  (≈-0.5σ from 1.0)  
**CI** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.910  (≈-2.2σ from 1.0)  <== -2.2 sigma
    2016: A/E=0.908  (≈-2.5σ from 1.0)  <== -2.5 sigma
    2017: A/E=0.947  (≈-1.5σ from 1.0)  
    2018: A/E=0.818  (≈-5.6σ from 1.0)  <== -5.6 sigma **
    2019: A/E=0.925  (≈-2.5σ from 1.0)  <== -2.5 sigma
    2020: A/E=0.824  (≈-6.2σ from 1.0)  <== -6.2 sigma **
    2021: A/E=0.882  (≈-4.4σ from 1.0)  <== -4.4 sigma **
    2022: A/E=1.412  (≈+16.2σ from 1.0)  <== +16.2 sigma **
    2023: A/E=1.237  (≈+9.8σ from 1.0)  <== +9.8 sigma **
    2024: A/E=0.891  (≈-4.7σ from 1.0)  <== -4.7 sigma **
**TPD** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.977  (≈-0.5σ from 1.0)  
    2016: A/E=1.013  (≈+0.3σ from 1.0)  
    2017: A/E=1.006  (≈+0.1σ from 1.0)  
    2018: A/E=1.022  (≈+0.6σ from 1.0)  
    2019: A/E=1.005  (≈+0.1σ from 1.0)  
    2020: A/E=0.940  (≈-1.7σ from 1.0)  
    2021: A/E=1.018  (≈+0.5σ from 1.0)  
    2022: A/E=0.987  (≈-0.4σ from 1.0)  
    2023: A/E=1.009  (≈+0.3σ from 1.0)  
    2024: A/E=0.977  (≈-0.8σ from 1.0)  
**IP** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.003  (≈+0.1σ from 1.0)  
    2016: A/E=1.036  (≈+1.2σ from 1.0)  
    2017: A/E=1.031  (≈+1.1σ from 1.0)  
    2018: A/E=0.990  (≈-0.4σ from 1.0)  
    2019: A/E=0.997  (≈-0.1σ from 1.0)  
    2020: A/E=0.989  (≈-0.4σ from 1.0)  
    2021: A/E=0.963  (≈-1.5σ from 1.0)  
    2022: A/E=1.001  (≈+0.0σ from 1.0)  
    2023: A/E=1.006  (≈+0.2σ from 1.0)  
    2024: A/E=1.004  (≈+0.2σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 1.005
    Cardiovascular: 1.007
    Injury/Accident: 0.992
    Mental Health: 0.972
    Musculoskeletal: 1.005
    Other: 1.029

### Ground truth (scorer-side)

- descriptive id: `trap_noise_drift_lookalike_b` (family `noise_trap`)
- controls: volatility on CI [2017, 2023] (sigma=0.3)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 3
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-0ce4d6` · run dir `results/harness_final/zero_shot`_