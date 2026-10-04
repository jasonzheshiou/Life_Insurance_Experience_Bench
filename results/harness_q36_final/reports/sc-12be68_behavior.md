# Behavioural dossier — scenario `sc-12be68`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model did not clearly identify the injected anomaly. Overall it answered 'clean' in 3/3 runs.

**What was hidden:** no injected control (clean / noise-only).
**What the model said:**

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — noop_neutral_controls (none family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: no injected control (clean / noise-only).

**Diagnosis to trust:** the injected irregularity was NOT named.

Confidence stated on the correct finding: n/a.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.6-27B`
- prompt: system + user turns, 13585 chars, sha256 `4ebe0a3a32cae3b03ab8edbc224eff15f679398dbd5290f92205505b5c35dbdf`
- the exact prompt text is archived at `results/harness_q36_final/zero_shot/sc-12be68_prompt.md`
- samplers: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0}
- `max_tokens`: **not sent** · `stream`: `True` · termination aggregation: `pooled`
- files shown: listing only; contents of `summary.json` and the per-benefit yearly A/E + IP termination tables

### What was sent (verbatim request body, redacted messages)

```json
{
  "model": "Qwen3.6-27B",
  "temperature": 1.0,
  "seed": 1234,
  "multi_turn": true,
  "initial_messages": [
    {
      "role": "system",
      "content": "You are an actuary reviewing synthetic life-insurance experience data for a\nsingle book. The data covers four benefit lines: Death, CI (critical illness),\nTPD (total permanent disability), and IP (income protection).\n\nKey facts about this data:\n- A/E = Actual claims / Expected claims. A clean (baseline) A/E is approximately\n  1.0, with sampling noise of order 1/sqrt(expected claim count) per year.\n- Anomalies, when present, are one of:\n  * drift: a sustained year-over-year move in A/E over 2+ years. A drift does\n    NOT have to continue to the last data year: a trend confined to a sub-window\n    that later reverts toward baseline is STILL drift \u2014 a reversion at the end is\n    not evidence against the trend that came before it. When reporting drift,\n    set years to the FULL window of the trend INCLUDING the gentle early ramp\n    years, and note the reversion (if any) in the evidence.\n  * shock: an abrupt level change (spike or drop) WITHOUT a gradual build-up \u2014\n    flat-topped or single-year excursions. If the excursion rises year over year\n    before it peaks or reverts, prefer drift.\n  * volatility: an increase in year-to-year dispersion with an unchanged level.\n  * recovery: a change in IP termination/recovery rates for a specific diagnosis.\n- Statistical discipline: before quoting any z-score or sigma computed under a\n  Poisson (1/sqrt(E)) null for a benefit line, compare that line's empirical\n  year-to-year standard deviation of A/E against the Poisson expectation. If the\n  data is overdispersed (empirical SD materially larger), the Poisson null is\n  invalid: describe the anomaly as volatility/dispersion rather than flagging\n  individual years against the Poisson null, and never re-apply Poisson z-scores\n  inside a window you have already identified as volatile.\n- Random noise can LOOK like a trend or a spike. Be conservative: do not invent\n  anomalies just to appear useful. If the data is consistent with noise, say so.\n\nYour task:\n1. Identify any anomalies or notable insights in the data you are given.\n2. For each finding, say WHERE it is (benefit line, which years), WHAT kind of\n   pattern it is, the direction and rough magnitude, how confident you are, the\n   evidence you are relying on, and WHAT ACTION you would recommend\n   (investigation steps, assumption review, pricing/valuation follow-up).\n3. If you see nothing anomalous, say so explicitly.\n\nRespond with ONLY a JSON object matching this shape (no prose outside it):\n\n{\n  \"scenario_id\": \"<the scenario id you were given>\",\n  \"overall_assessment\": \"clean\" | \"anomalies\",\n  \"findings\": [\n    {\n      \"benefit\": \"Death\" | \"CI\" | \"TPD\" | \"IP\",\n      \"years\": [start_year, end_year] | null,\n      \"pattern\": \"drift\" | \"shock\" | \"volatility\" | \"recovery\" | \"other\",\n      \"direction\": \"increase\" | \"decrease\" | \"dispersion\",\n      \"magnitude\": \"free text, e.g. ~+0.10/yr, x1.5, sigma=0.3\",\n      \"confidence\": 0.0-1.0,\n      \"evidence\": [\"short, checkable: which file/rows support this\"],\n      \"recommended_action\": \"what you would do next\"\n    }\n  ]\n}"
    },
    {
      "role": "user",
      "content": "Scenario: sc-12be68\n\nFiles available (paths are relative to the scenario folder):\n  - artifacts/ae_ci.csv\n  - artifacts/ae_ci_age_gender.csv\n  - artifacts/ae_ci_age_gender.png\n  - artifacts/ae_ci_by_year.csv\n  - artifacts/ae_ci_by_year.png\n  - artifacts/ae_death.csv\n  - artifacts/ae_death_age_gender.csv\n  - artifacts/ae_death_age_gender.png\n  - artifacts/ae_death_by_year.csv\n  - artifacts/ae_death_by_year.png\n  - artifacts/ae_ip.csv\n  - artifacts/ae_ip_age_gender.csv\n  - artifacts/ae_ip_age_gender.png\n  - artifacts/ae_ip_by_year.csv\n  - artifacts/ae_ip_by_year.png\n  - artifacts/ae_ip_termination.csv\n  - artifacts/ae_ip_termination_by_month.csv\n  - artifacts/ae_ip_termination_by_month.png\n  - artifacts/ae_tpd.csv\n  - artifacts/ae_tpd_age_gender.csv\n  - artifacts/ae_tpd_age_gender.png\n  - artifacts/ae_tpd_by_year.csv\n  - artifacts/ae_tpd_by_year.png\n  - artifacts/summary.json\n  - benchmarks/CI.csv\n  - benchmarks/Death.csv\n  - benchmarks/IP.csv\n  - benchmarks/TPD.csv\n  - ci_claims.csv\n  - death_claims.csv\n  - exposure.csv\n  - ip_claims.csv\n  - scenario_id.txt\n  - tpd_claims.csv\n\nsummary.json (overall A/E per benefit, claim counts):\n{\n  \"benefits\": {\n    \"Death\": {\n      \"overall_ae\": 1.004,\n      \"claims\": 5020\n    },\n    \"CI\": {\n      \"overall_ae\": 1.0143,\n      \"claims\": 12171\n    },\n    \"TPD\": {\n      \"overall_ae\": 1.0063,\n      \"claims\": 8050\n    },\n    \"IP\": {\n      \"overall_ae\": 1.0023,\n      \"claims\": 15035,\n      \"overall_termination_ae\": 1.0024\n    }\n  }\n}\n\nartifacts/ae_death_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=226  Expected=240  AE=0.944\n  2016: Actual=337  Expected=290  AE=1.163\n  2017: Actual=326  Expected=337  AE=0.966\n  2018: Actual=379  Expected=390  AE=0.973\n  2019: Actual=451  Expected=447  AE=1.010\n  2020: Actual=508  Expected=508  AE=0.999\n  2021: Actual=564  Expected=576  AE=0.980\n  2022: Actual=662  Expected=652  AE=1.015\n  2023: Actual=749  Expected=735  AE=1.019\n  2024: Actual=818  Expected=826  AE=0.990\n\nartifacts/ae_ci_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=600  Expected=596  AE=1.006\n  2016: Actual=723  Expected=720  AE=1.004\n  2017: Actual=808  Expected=837  AE=0.965\n  2018: Actual=1,009  Expected=963  AE=1.048\n  2019: Actual=1,124  Expected=1,097  AE=1.024\n  2020: Actual=1,269  Expected=1,239  AE=1.024\n  2021: Actual=1,346  Expected=1,386  AE=0.971\n  2022: Actual=1,618  Expected=1,548  AE=1.045\n  2023: Actual=1,740  Expected=1,719  AE=1.012\n  2024: Actual=1,934  Expected=1,893  AE=1.021\n\nartifacts/ae_tpd_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=480  Expected=487  AE=0.986\n  2016: Actual=585  Expected=562  AE=1.041\n  2017: Actual=640  Expected=625  AE=1.025\n  2018: Actual=710  Expected=690  AE=1.029\n  2019: Actual=765  Expected=757  AE=1.010\n  2020: Actual=796  Expected=826  AE=0.963\n  2021: Actual=908  Expected=897  AE=1.013\n  2022: Actual=981  Expected=974  AE=1.007\n  2023: Actual=1,071  Expected=1,052  AE=1.018\n  2024: Actual=1,114  Expected=1,130  AE=0.985\n\nartifacts/ae_ip_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=1,036  Expected=1,013  AE=1.023\n  2016: Actual=1,175  Expected=1,142  AE=1.029\n  2017: Actual=1,236  Expected=1,241  AE=0.996\n  2018: Actual=1,341  Expected=1,342  AE=0.999\n  2019: Actual=1,436  Expected=1,441  AE=0.997\n  2020: Actual=1,544  Expected=1,545  AE=0.999\n  2021: Actual=1,616  Expected=1,653  AE=0.978\n  2022: Actual=1,776  Expected=1,768  AE=1.004\n  2023: Actual=1,872  Expected=1,876  AE=0.998\n  2024: Actual=2,003  Expected=1,980  AE=1.012\n\nartifacts/ae_ip_termination.csv \u2014 termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):\n  Cancer: 0.999\n  Cardiovascular: 1.010\n  Injury/Accident: 0.974\n  Mental Health: 1.005\n  Musculoskeletal: 1.017\n  Other: 0.983\n\nNow analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.\n\n---\nCOMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)\nReading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.\n\n[DEATH] mean A/E 1.006 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.002/yr, R2 0.01, total -0.018\n  step: -0.059 at 2017 (score 0.5)\n  YoY sd: empirical 0.1066 vs Poisson 0.0477 -> overdispersion x2.23 (Poisson null approximately valid)\n  longest run: 3y up (+0.043) | max 1yr jump 0.22\n  smoothed 3y MA: amplitude 0.051 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.14 (gradient -0.0025/yr)\n    MA series: 2015:1.02 2016:1.03 2017:0.98 2018:0.99 2019:1.00 2020:1.00 2021:1.00 2022:1.01\n  yearly: 2015:0.94(z-0.9) 2016:1.16(z+2.8) 2017:0.97(z-0.6) 2018:0.97(z-0.5) 2019:1.01(z+0.2) 2020:1.00(z-0.0) 2021:0.98(z-0.5) 2022:1.01(z+0.4) 2023:1.02(z+0.5) 2024:0.99(z-0.3)\n\n[CI] mean A/E 1.012 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient 0.0022/yr, R2 0.06, total 0.02\n  step: +0.029 at 2018 (score 1.8)\n  YoY sd: empirical 0.0477 vs Poisson 0.0305 -> overdispersion x1.56 (Poisson null approximately valid)\n  longest run: 4y down (-0.076) | max 1yr jump 0.082\n  smoothed 3y MA: amplitude 0.04 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.31 (gradient 0.0028/yr)\n    MA series: 2015:0.99 2016:1.01 2017:1.01 2018:1.03 2019:1.01 2020:1.01 2021:1.01 2022:1.03\n  yearly: 2015:1.01(z+0.1) 2016:1.00(z+0.1) 2017:0.96(z-1.0) 2018:1.05(z+1.5) 2019:1.02(z+0.8) 2020:1.02(z+0.8) 2021:0.97(z-1.1) 2022:1.04(z+1.8) 2023:1.01(z+0.5) 2024:1.02(z+0.9)\n\n[TPD] mean A/E 1.008 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0021/yr, R2 0.07, total -0.019\n  step: -0.021 at 2020 (score 1.5)\n  excursions (windows whose level differs from the rest, best first): 2016-2018 (3y) +0.034 score 3.8\n  YoY sd: empirical 0.0346 vs Poisson 0.0364 -> overdispersion x0.95 (Poisson null approximately valid)\n  longest run: 3y down (-0.066) | max 1yr jump 0.056\n  smoothed 3y MA: amplitude 0.037 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.36 (gradient -0.0033/yr)\n    MA series: 2015:1.02 2016:1.03 2017:1.02 2018:1.00 2019:0.99 2020:0.99 2021:1.01 2022:1.00\n  yearly: 2015:0.99(z-0.3) 2016:1.04(z+1.0) 2017:1.02(z+0.6) 2018:1.03(z+0.8) 2019:1.01(z+0.3) 2020:0.96(z-1.1) 2021:1.01(z+0.4) 2022:1.01(z+0.2) 2023:1.02(z+0.6) 2024:0.98(z-0.5)\n\n[IP] mean A/E 1.004 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0021/yr, R2 0.18, total -0.019\n  step: -0.028 at 2017 (score 6.1)\n  excursions (windows whose level differs from the rest, best first): 2015-2016 (2y) +0.028 score 6.1; 2017-2023 (7y) -0.025 score 4.2\n  YoY sd: empirical 0.0178 vs Poisson 0.0263 -> overdispersion x0.68 (Poisson null approximately valid)\n  longest run: 2y up (+0.006) | max 1yr jump 0.033\n  smoothed 3y MA: amplitude 0.025 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.35 (gradient -0.0021/yr)\n    MA series: 2015:1.02 2016:1.01 2017:1.00 2018:1.00 2019:0.99 2020:0.99 2021:0.99 2022:1.00\n  yearly: 2015:1.02(z+0.7) 2016:1.03(z+1.0) 2017:1.00(z-0.1) 2018:1.00(z-0.0) 2019:1.00(z-0.1) 2020:1.00(z-0.0) 2021:0.98(z-0.9) 2022:1.00(z+0.2) 2023:1.00(z-0.1) 2024:1.01(z+0.5)\n\n[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: \n  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2016:2 2017:2 2018:1 2021:2 2022:1\n\n[IP TERMINATION by diagnosis \u2014 pooled, no year dimension] (for recovery patterns)\n  Cancer: pooled A/E 0.999 (z -0.1, expected 1262) -> clean\n  Cardiovascular: pooled A/E 1.01 (z +0.3, expected 882) -> clean\n  Injury/Accident: pooled A/E 0.974 (z -1.0, expected 1437) -> clean\n  Mental Health: pooled A/E 1.005 (z +0.4, expected 4458) -> clean\n  Musculoskeletal: pooled A/E 1.017 (z +1.0, expected 3306) -> clean\n  Other: pooled A/E 0.983 (z -0.6, expected 1212) -> clean\n\nHARNESS MODE \u2014 you are not limited to eyeballing the tables above.\n\n1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact\n   CSVs) is appended at the end of this message. Trust its arithmetic over\n   mental math, but the final judgement is yours: confirm or override its\n   per-line heuristic verdicts.\n\n2) You may compute anything else you need. To use the tool, reply with ONLY a\n   JSON object (no other text, no <tool_call> tags, no function-call syntax):\n     {\"tool\": \"python\", \"code\": \"<python source as one JSON string>\"}\n   The code runs with the scenario's artifacts/ directory as cwd (open files\n   by relative path, e.g. open(\"ae_death_by_year.csv\")); plain stdlib Python\n   (csv, math, statistics); 10 s limit; output is returned verbatim.\n   You get at most 4 tool calls. NEVER write files or read outside artifacts/.\n\n3) When done \u2014 with or without tools \u2014 reply with ONLY the final JSON object\n   in the required shape. Do not put tool requests inside that final JSON.\n\n3b) Work efficiently: the evidence pack already contains the arithmetic. At most\n   TWO tool calls, and if the pack answers the question, answer immediately\n   without any tool call. Never spend more turns than the problem needs.\n\n3c) Books where several lines move together: when the CROSS-LINE block reports a\n   coordinated move or coordinated swings over a run of consecutive years, treat\n   it as ONE underlying event but report it for EVERY affected line \u2014 the output\n   schema has no \"all\" benefit, so a four-line event needs four entries sharing\n   the years. Do not tell four unrelated stories, and do not drop lines. This\n   means one entry per affected line EVEN WHEN one line's own move is much\n   smaller than the others, and even when you discuss the shared cause only once:\n   an answer that names the largest line and merely mentions the others in prose\n   is graded as having found only the largest line.\n\n4) Discipline (these are scored):\n   * Overdispersion is NOT a finding by itself. Report a dispersion\n     finding only when the elevated year-to-year scatter is the material\n     anomaly for that line (roughly x6 or more versus the Poisson expectation,\n     with a level that stays flat). Mild overdispersion, and any line whose\n     evidence profile says \"no strong signal\", must NOT be reported as a\n     finding merely because its scatter is above Poisson. The one exception is\n     the book-wide case: when the CROSS-LINE block reports several lines\n     swinging together across consecutive years, that shared evidence stands on\n     its own, and every affected line gets its dispersion entry even if that\n     line's own ratio is below the x6 guide.\n   * Use the pattern the evidence actually describes. A single-year deviation\n     that reverts is a one-off change; a movement that builds and then flattens\n     or runs on is a sustained move; a stretch where the line swings around\n     without ever settling at a new level is dispersion. The schema's taxonomy\n     above defines each pattern word. When a per-line note says the biggest\n     single-year move EXCEEDS the net excursion, the evidence cannot separate a\n     give-back ramp from an erratic stretch: give that line a dispersion entry\n     AND keep the level-change reading as an entry of its own, so both readings\n     are on the record (one entry of each kind per line, never two of the same).\n   * A one-year wobble is only a finding if the year is genuinely extreme:\n     require a Poisson z of about 4.5 or more for that year (A/E alone is\n     misleading when the expected count is small). A single-year excursion\n     around z 3 is the kind of thing ordinary books produce, so leave it out.\n     Where a line's own scatter already exceeds Poisson, per-year z-scores are\n     unreliable \u2014 then require a larger move, or describe the stretch as\n     dispersion instead of claiming a one-off change.\n   * Every entry in \"findings\" is a claim that something material happened and\n     should be investigated. A favourable deviation (A/E materially BELOW\n     expectation), a movement you have decided is ordinary, and any observation\n     you are not claiming must not appear as its own entry \u2014 mention it in the\n     evidence text of a finding you ARE making, or leave it out entirely.\n     Listing an observation you are not claiming is scored as a false alarm.\n   * Do not describe the same movement twice. If a line's final years reverse a\n     movement you have already reported for that line, that reversal is part of\n     the earlier event: say so inside that finding rather than adding a second\n     entry for the same line.\n   * Small cells are not evidence: age-band or duration-month A/E values rest\n     on tiny expected counts and go extreme by chance. Never report a\n     book-level anomaly from such a cell unless the same effect is visible in\n     the by-year series or the pooled line.\n   * Findings you considered and rejected for these reasons do not appear in\n     the \"findings\" array at all.\n"
    }
  ]
}
```

### Per-run facts

| run | seed | wall time | completion tok | prompt tok | finish | answer chars | reasoning chars | error |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1234 | 178s | 3149 | 6226 | stop | 83 | 7825 | ok |
| 2 | 1235 | 159s | 3210 | 6226 | stop | 83 | 8914 | ok |
| 3 | 1236 | 83s | 1880 | 6226 | stop | 83 | 5218 | ok |

### Tool use (did it do anything besides read the text?)

| check | result |
|---|---|
| tools offered in request | `False` |
| tool calls in response | `False` |
| code fences in output | `True` |
| python code / file reads in output | `False` |
| asked to inspect files | `False` |

The runner offers no tools (`tools`/`function_call` keys never appear in the request) and the server returned none. The model answered from the text alone.

### The data it saw (for replaying its reasoning)

**Death** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.944  (≈-0.9σ from 1.0)  
    2016: A/E=1.163  (≈+2.8σ from 1.0)  <== +2.8 sigma
    2017: A/E=0.966  (≈-0.6σ from 1.0)  
    2018: A/E=0.973  (≈-0.5σ from 1.0)  
    2019: A/E=1.010  (≈+0.2σ from 1.0)  
    2020: A/E=0.999  (≈-0.0σ from 1.0)  
    2021: A/E=0.980  (≈-0.5σ from 1.0)  
    2022: A/E=1.015  (≈+0.4σ from 1.0)  
    2023: A/E=1.019  (≈+0.5σ from 1.0)  
    2024: A/E=0.990  (≈-0.3σ from 1.0)  
**CI** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.006  (≈+0.1σ from 1.0)  
    2016: A/E=1.004  (≈+0.1σ from 1.0)  
    2017: A/E=0.965  (≈-1.0σ from 1.0)  
    2018: A/E=1.048  (≈+1.5σ from 1.0)  
    2019: A/E=1.024  (≈+0.8σ from 1.0)  
    2020: A/E=1.024  (≈+0.8σ from 1.0)  
    2021: A/E=0.971  (≈-1.1σ from 1.0)  
    2022: A/E=1.045  (≈+1.8σ from 1.0)  
    2023: A/E=1.012  (≈+0.5σ from 1.0)  
    2024: A/E=1.021  (≈+0.9σ from 1.0)  
**TPD** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.986  (≈-0.3σ from 1.0)  
    2016: A/E=1.041  (≈+1.0σ from 1.0)  
    2017: A/E=1.025  (≈+0.6σ from 1.0)  
    2018: A/E=1.029  (≈+0.8σ from 1.0)  
    2019: A/E=1.010  (≈+0.3σ from 1.0)  
    2020: A/E=0.963  (≈-1.1σ from 1.0)  
    2021: A/E=1.013  (≈+0.4σ from 1.0)  
    2022: A/E=1.007  (≈+0.2σ from 1.0)  
    2023: A/E=1.018  (≈+0.6σ from 1.0)  
    2024: A/E=0.985  (≈-0.5σ from 1.0)  
**IP** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.023  (≈+0.7σ from 1.0)  
    2016: A/E=1.029  (≈+1.0σ from 1.0)  
    2017: A/E=0.996  (≈-0.1σ from 1.0)  
    2018: A/E=0.999  (≈-0.0σ from 1.0)  
    2019: A/E=0.997  (≈-0.1σ from 1.0)  
    2020: A/E=0.999  (≈-0.0σ from 1.0)  
    2021: A/E=0.978  (≈-0.9σ from 1.0)  
    2022: A/E=1.004  (≈+0.2σ from 1.0)  
    2023: A/E=0.998  (≈-0.1σ from 1.0)  
    2024: A/E=1.012  (≈+0.5σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 0.999
    Cardiovascular: 1.010
    Injury/Accident: 0.974
    Mental Health: 1.005
    Musculoskeletal: 1.017
    Other: 0.983

### Ground truth (scorer-side)

- descriptive id: `noop_neutral_controls` (family `none`)
- controls: no injected control (clean / noise-only)

### Scorer verdict summary

- TRUE POSITIVE findings: 0
- other / false-positive findings: 0
- runs: 3 · overall 'clean' verdicts: 3

---
_Generated by scripts/report_xam.py · scenario `sc-12be68` · run dir `results/harness_q36_final/zero_shot`_