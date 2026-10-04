# Behavioural dossier — scenario `sc-e6ffa4`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 4 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** volatility on all [2020, 2024] (sigma=0.15).
**What the model said:**
- run 1: Death / shock / increase (confidence 0.85) — FALSE POSITIVE
- run 1: CI / volatility / dispersion (confidence 0.9) — TRUE POSITIVE
- run 1: IP / volatility / dispersion (confidence 0.85) — TRUE POSITIVE
- run 2: Death / shock / increase (confidence 0.8) — FALSE POSITIVE
- run 2: CI / volatility / dispersion (confidence 0.9) — TRUE POSITIVE
- run 2: TPD / drift / decrease (confidence 0.8) — FALSE POSITIVE
- run 2: IP / volatility / dispersion (confidence 0.85) — TRUE POSITIVE
- run 3: Death / shock / increase (confidence 0.85) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_vol_macro_2020_2024 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: volatility on all [2020, 2024] (sigma=0.15).

**Diagnosis to trust:** the injected irregularity was named correctly (volatility on all [2020, 2024] (sigma=0.15)).

Confidence stated on the correct finding: 0.9, 0.85, 0.9, 0.85, 0.9, 0.9.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.6-27B`
- prompt: system + user turns, 18564 chars, sha256 `8369ec228fab7327dcda4ae29697600ff37b975327a310fb81d7ed5feface73a`
- the exact prompt text is archived at `results/harness_q36_final/zero_shot/sc-e6ffa4_prompt.md`
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
      "content": "Scenario: sc-e6ffa4\n\nFiles available (paths are relative to the scenario folder):\n  - artifacts/ae_ci.csv\n  - artifacts/ae_ci_age_gender.csv\n  - artifacts/ae_ci_age_gender.png\n  - artifacts/ae_ci_by_year.csv\n  - artifacts/ae_ci_by_year.png\n  - artifacts/ae_death.csv\n  - artifacts/ae_death_age_gender.csv\n  - artifacts/ae_death_age_gender.png\n  - artifacts/ae_death_by_year.csv\n  - artifacts/ae_death_by_year.png\n  - artifacts/ae_ip.csv\n  - artifacts/ae_ip_age_gender.csv\n  - artifacts/ae_ip_age_gender.png\n  - artifacts/ae_ip_by_year.csv\n  - artifacts/ae_ip_by_year.png\n  - artifacts/ae_ip_termination.csv\n  - artifacts/ae_ip_termination_by_month.csv\n  - artifacts/ae_ip_termination_by_month.png\n  - artifacts/ae_tpd.csv\n  - artifacts/ae_tpd_age_gender.csv\n  - artifacts/ae_tpd_age_gender.png\n  - artifacts/ae_tpd_by_year.csv\n  - artifacts/ae_tpd_by_year.png\n  - artifacts/summary.json\n  - benchmarks/CI.csv\n  - benchmarks/Death.csv\n  - benchmarks/IP.csv\n  - benchmarks/TPD.csv\n  - ci_claims.csv\n  - death_claims.csv\n  - exposure.csv\n  - ip_claims.csv\n  - scenario_id.txt\n  - tpd_claims.csv\n\nsummary.json (overall A/E per benefit, claim counts):\n{\n  \"benefits\": {\n    \"Death\": {\n      \"overall_ae\": 0.9872,\n      \"claims\": 4936\n    },\n    \"CI\": {\n      \"overall_ae\": 1.0038,\n      \"claims\": 12046\n    },\n    \"TPD\": {\n      \"overall_ae\": 1.0045,\n      \"claims\": 8036\n    },\n    \"IP\": {\n      \"overall_ae\": 1.0066,\n      \"claims\": 15099,\n      \"overall_termination_ae\": 0.9921\n    }\n  }\n}\n\nartifacts/ae_death_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=223  Expected=240  AE=0.931\n  2016: Actual=289  Expected=290  AE=0.998\n  2017: Actual=305  Expected=337  AE=0.904\n  2018: Actual=366  Expected=390  AE=0.939\n  2019: Actual=403  Expected=447  AE=0.902\n  2020: Actual=517  Expected=508  AE=1.017\n  2021: Actual=568  Expected=576  AE=0.987\n  2022: Actual=770  Expected=652  AE=1.181\n  2023: Actual=591  Expected=735  AE=0.804\n  2024: Actual=904  Expected=826  AE=1.094\n\nartifacts/ae_ci_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=619  Expected=596  AE=1.038\n  2016: Actual=669  Expected=720  AE=0.929\n  2017: Actual=826  Expected=837  AE=0.987\n  2018: Actual=950  Expected=963  AE=0.986\n  2019: Actual=1,059  Expected=1,097  AE=0.965\n  2020: Actual=1,443  Expected=1,239  AE=1.165\n  2021: Actual=1,332  Expected=1,386  AE=0.961\n  2022: Actual=2,088  Expected=1,548  AE=1.349\n  2023: Actual=1,909  Expected=1,719  AE=1.110\n  2024: Actual=1,151  Expected=1,893  AE=0.608\n\nartifacts/ae_tpd_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=495  Expected=487  AE=1.016\n  2016: Actual=605  Expected=562  AE=1.077\n  2017: Actual=612  Expected=625  AE=0.980\n  2018: Actual=738  Expected=690  AE=1.069\n  2019: Actual=742  Expected=757  AE=0.980\n  2020: Actual=1,014  Expected=826  AE=1.227\n  2021: Actual=909  Expected=897  AE=1.014\n  2022: Actual=884  Expected=974  AE=0.908\n  2023: Actual=965  Expected=1,052  AE=0.917\n  2024: Actual=1,072  Expected=1,130  AE=0.948\n\nartifacts/ae_ip_by_year.csv \u2014 yearly (Actual, Expected, AE):\n  2015: Actual=1,029  Expected=1,013  AE=1.016\n  2016: Actual=1,108  Expected=1,142  AE=0.970\n  2017: Actual=1,214  Expected=1,241  AE=0.979\n  2018: Actual=1,389  Expected=1,342  AE=1.035\n  2019: Actual=1,433  Expected=1,441  AE=0.995\n  2020: Actual=1,374  Expected=1,545  AE=0.889\n  2021: Actual=1,534  Expected=1,653  AE=0.928\n  2022: Actual=1,596  Expected=1,768  AE=0.903\n  2023: Actual=2,374  Expected=1,876  AE=1.265\n  2024: Actual=2,048  Expected=1,980  AE=1.035\n\nartifacts/ae_ip_termination.csv \u2014 termination A/E per diagnosis (pooled over duration months: sum(Recovered)/sum(Exposed x AssumedRate), so small late-duration cells carry little weight; 1.0 = baseline recovery rate):\n  Cancer: 0.978\n  Cardiovascular: 0.963\n  Injury/Accident: 1.010\n  Mental Health: 0.994\n  Musculoskeletal: 0.992\n  Other: 1.001\n\nNow analyse the data above. Report every anomaly or notable insight you find, and explicitly state when the data looks clean. Return ONLY the JSON object.\n\n---\nCOMPUTED EVIDENCE PACK (deterministic, from the CSVs; trust over mental math)\nReading guide: a profile describes EVIDENCE, it is not a finding. Mild overdispersion (x2.5-6.5) is the normal texture of this book and is never by itself an anomaly; small age/duration cells (tiny expected counts) are unreliable however extreme their A/E looks.\n\n[DEATH] mean A/E 0.976 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient 0.0106/yr, R2 0.09, total 0.096\n  step: +0.082 at 2020 (score 1.3)\n  YoY sd: empirical 0.1906 vs Poisson 0.0477 -> overdispersion x3.99 (mild overdispersion \u2014 z-scores indicative only; this alone is NOT an anomaly)\n  GIVE-BACK: in 2022 this line's level departs to 1.181 against its own baseline 0.987 (increase) and is back the following year (the move -0.377 is undone by +0.290, ratio 0.77) \u2014 that is the shape of a ONE-OFF change CONFINED TO 2022, not a slow build and not a multi-year erratic stretch. Name it as an entry of its own with that single year and direction; keep a dispersion entry as well if you believe the wider stretch is erratic (the two readings are not exclusive)\n  onset: max 1yr move / excursion size = 4.36 (the biggest single-year move EXCEEDS the net excursion \u2014 the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change \u2014 the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))\n  longest run: 2y up (+0.067) | max 1yr jump 0.377\n  smoothed 3y MA: amplitude 0.146 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.57 (gradient 0.0148/yr)\n    MA series: 2015:0.94 2016:0.95 2017:0.92 2018:0.95 2019:0.97 2020:1.06 2021:0.99 2022:1.03\n  yearly: 2015:0.93(z-1.1) 2016:1.00(z-0.0) 2017:0.90(z-1.8) 2018:0.94(z-1.2) 2019:0.90(z-2.1) 2020:1.02(z+0.4) 2021:0.99(z-0.3) 2022:1.18(z+4.6) 2023:0.80(z-5.3) 2024:1.09(z+2.7)\n\n[CI] mean A/E 1.01 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation \u2014 Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated\n  trend: gradient -0.004/yr, R2 0.0, total -0.036\n  step: -0.188 at 2023 (score 0.7)\n  YoY sd: empirical 0.2588 vs Poisson 0.0305 -> overdispersion x8.47 (Poisson null INVALID on this line)\n  onset: max 1yr move / excursion size = 2.21 (the biggest single-year move EXCEEDS the net excursion \u2014 the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change \u2014 the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))\n  longest run: 3y down (-0.022) | max 1yr jump 0.503\n  level at the END of the series: +0.051 versus this line's own baseline (calibration: clean lines stay within 0.008) \u2014 the movement does NOT return to where it started\n  smoothed 3y MA: amplitude 0.191 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.45 (gradient 0.0197/yr)\n    MA series: 2015:0.98 2016:0.97 2017:0.98 2018:1.04 2019:1.03 2020:1.16 2021:1.14 2022:1.02\n  yearly: 2015:1.04(z+0.9) 2016:0.93(z-1.9) 2017:0.99(z-0.4) 2018:0.99(z-0.4) 2019:0.96(z-1.2) 2020:1.17(z+5.8) 2021:0.96(z-1.4) 2022:1.35(z+13.7) 2023:1.11(z+4.6) 2024:0.61(z-17.1)\n\n[TPD] mean A/E 1.014 | evidence profile: no strong signal \u2014 judge from the yearly table and null-validity columns\n  trend: gradient -0.0122/yr, R2 0.15, total -0.11\n  step: -0.127 at 2022 (score 3.7)\n  excursions (windows whose level differs from the rest, best first): 2015-2021 (7y) +0.127 score 3.7; 2022-2023 (2y) -0.126 score 4.0\n  YoY sd: empirical 0.1359 vs Poisson 0.0364 -> overdispersion x3.73 (mild overdispersion \u2014 z-scores indicative only; this alone is NOT an anomaly)\n  onset: max 1yr move / excursion size = 1.96 (the biggest single-year move EXCEEDS the net excursion \u2014 the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change \u2014 the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))\n  longest run: 3y down (-0.319) | max 1yr jump 0.248\n  level at the END of the series: -0.107 versus this line's own baseline (calibration: clean lines stay within 0.008) \u2014 the movement does NOT return to where it started\n  smoothed 3y MA: amplitude 0.168 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.29 (gradient -0.0128/yr)\n    MA series: 2015:1.02 2016:1.04 2017:1.01 2018:1.09 2019:1.07 2020:1.05 2021:0.95 2022:0.92\n  yearly: 2015:1.02(z+0.4) 2016:1.08(z+1.8) 2017:0.98(z-0.5) 2018:1.07(z+1.8) 2019:0.98(z-0.6) 2020:1.23(z+6.5) 2021:1.01(z+0.4) 2022:0.91(z-2.9) 2023:0.92(z-2.7) 2024:0.95(z-1.7)\n\n[IP] mean A/E 1.001 | evidence profile: scatter-dominant: the largest single-year move exceeds the net level change and year-to-year scatter is far above the Poisson expectation \u2014 Poisson z-scores are INVALID here; if this scatter is the finding, say so for THIS line and give the years where it is elevated\n  trend: gradient 0.0086/yr, R2 0.06, total 0.078\n  step: +0.186 at 2023 (score 1.6)\n  excursions (windows whose level differs from the rest, best first): 2020-2022 (3y) -0.135 score 3.4\n  YoY sd: empirical 0.1601 vs Poisson 0.0263 -> overdispersion x6.09 (mild overdispersion \u2014 z-scores indicative only; this alone is NOT an anomaly)\n  onset: max 1yr move / excursion size = 2.68 (the biggest single-year move EXCEEDS the net excursion \u2014 the line oscillates rather than holding a new level, so the shape here is dispersion: give this line a dispersion entry over these years, and keep the level-change reading as an entry of its own too. Read that second reading's shape from this line's own evidence: a movement that climbs year over year before it peaks or gives back is a sustained move, while one that arrives in a single year and is gone is a one-off change \u2014 the evidence cannot separate a give-back ramp from an erratic stretch, so report both readings rather than guessing between them (one entry of each kind per line, never two of the same))\n  longest run: 3y up (+0.065) | max 1yr jump 0.363\n  level at the END of the series: +0.055 versus this line's own baseline (calibration: clean lines stay within 0.008) \u2014 the movement does NOT return to where it started\n  smoothed 3y MA: amplitude 0.161 covering 2015-2024 (points labelled 2015-2022; each point averages 3 years, so the last label covers the final 3), fit R2 0.06 (gradient 0.005/yr)\n    MA series: 2015:0.99 2016:0.99 2017:1.00 2018:0.97 2019:0.94 2020:0.91 2021:1.03 2022:1.07\n  yearly: 2015:1.02(z+0.5) 2016:0.97(z-1.0) 2017:0.98(z-0.8) 2018:1.03(z+1.3) 2019:0.99(z-0.2) 2020:0.89(z-4.4) 2021:0.93(z-2.9) 2022:0.90(z-4.1) 2023:1.26(z+11.5) 2024:1.03(z+1.5)\n\n[CROSS-LINE] lines whose smoothed level sits >0.08 from their own baseline, by year: 2020:3 2021:2 2022:1\n  lines taking an unusually large year-on-year swing (>2.5x their own median move), by year: 2020:1 2023:2 2024:3\n  -> 3 of 4 lines take their large swing in the SAME single year above; that is what a book-wide jolt looks like \u2014 read those lines in the level rows (step/excursion) rather than raising a dispersion reading on the strength of the swing counts alone. Note what this does and does not rule out: it rules out a multi-year ERRATIC stretch (dispersion), and it does NOT rule out a sustained move, so check each line's own longest-run row as well \u2014 a line that runs steadily in ONE direction for several consecutive years is a sustained move in its own right, even when other lines take a single-year jolt\n\n[IP TERMINATION by diagnosis \u2014 pooled, no year dimension] (for recovery patterns)\n  Cancer: pooled A/E 0.978 (z -0.8, expected 1255) -> clean\n  Cardiovascular: pooled A/E 0.963 (z -1.1, expected 920) -> clean\n  Injury/Accident: pooled A/E 1.01 (z +0.4, expected 1414) -> clean\n  Mental Health: pooled A/E 0.994 (z -0.4, expected 4469) -> clean\n  Musculoskeletal: pooled A/E 0.992 (z -0.5, expected 3382) -> clean\n  Other: pooled A/E 1.001 (z +0.0, expected 1192) -> clean\n\nHARNESS MODE \u2014 you are not limited to eyeballing the tables above.\n\n1) A COMPUTED EVIDENCE PACK (deterministic statistics computed from the exact\n   CSVs) is appended at the end of this message. Trust its arithmetic over\n   mental math, but the final judgement is yours: confirm or override its\n   per-line heuristic verdicts.\n\n2) You may compute anything else you need. To use the tool, reply with ONLY a\n   JSON object (no other text, no <tool_call> tags, no function-call syntax):\n     {\"tool\": \"python\", \"code\": \"<python source as one JSON string>\"}\n   The code runs with the scenario's artifacts/ directory as cwd (open files\n   by relative path, e.g. open(\"ae_death_by_year.csv\")); plain stdlib Python\n   (csv, math, statistics); 10 s limit; output is returned verbatim.\n   You get at most 4 tool calls. NEVER write files or read outside artifacts/.\n\n3) When done \u2014 with or without tools \u2014 reply with ONLY the final JSON object\n   in the required shape. Do not put tool requests inside that final JSON.\n\n3b) Work efficiently: the evidence pack already contains the arithmetic. At most\n   TWO tool calls, and if the pack answers the question, answer immediately\n   without any tool call. Never spend more turns than the problem needs.\n\n3c) Books where several lines move together: when the CROSS-LINE block reports a\n   coordinated move or coordinated swings over a run of consecutive years, treat\n   it as ONE underlying event but report it for EVERY affected line \u2014 the output\n   schema has no \"all\" benefit, so a four-line event needs four entries sharing\n   the years. Do not tell four unrelated stories, and do not drop lines. This\n   means one entry per affected line EVEN WHEN one line's own move is much\n   smaller than the others, and even when you discuss the shared cause only once:\n   an answer that names the largest line and merely mentions the others in prose\n   is graded as having found only the largest line.\n\n4) Discipline (these are scored):\n   * Overdispersion is NOT a finding by itself. Report a dispersion\n     finding only when the elevated year-to-year scatter is the material\n     anomaly for that line (roughly x6 or more versus the Poisson expectation,\n     with a level that stays flat). Mild overdispersion, and any line whose\n     evidence profile says \"no strong signal\", must NOT be reported as a\n     finding merely because its scatter is above Poisson. The one exception is\n     the book-wide case: when the CROSS-LINE block reports several lines\n     swinging together across consecutive years, that shared evidence stands on\n     its own, and every affected line gets its dispersion entry even if that\n     line's own ratio is below the x6 guide.\n   * Use the pattern the evidence actually describes. A single-year deviation\n     that reverts is a one-off change; a movement that builds and then flattens\n     or runs on is a sustained move; a stretch where the line swings around\n     without ever settling at a new level is dispersion. The schema's taxonomy\n     above defines each pattern word. When a per-line note says the biggest\n     single-year move EXCEEDS the net excursion, the evidence cannot separate a\n     give-back ramp from an erratic stretch: give that line a dispersion entry\n     AND keep the level-change reading as an entry of its own, so both readings\n     are on the record (one entry of each kind per line, never two of the same).\n   * A one-year wobble is only a finding if the year is genuinely extreme:\n     require a Poisson z of about 4.5 or more for that year (A/E alone is\n     misleading when the expected count is small). A single-year excursion\n     around z 3 is the kind of thing ordinary books produce, so leave it out.\n     Where a line's own scatter already exceeds Poisson, per-year z-scores are\n     unreliable \u2014 then require a larger move, or describe the stretch as\n     dispersion instead of claiming a one-off change.\n   * Every entry in \"findings\" is a claim that something material happened and\n     should be investigated. A favourable deviation (A/E materially BELOW\n     expectation), a movement you have decided is ordinary, and any observation\n     you are not claiming must not appear as its own entry \u2014 mention it in the\n     evidence text of a finding you ARE making, or leave it out entirely.\n     Listing an observation you are not claiming is scored as a false alarm.\n   * Do not describe the same movement twice. If a line's final years reverse a\n     movement you have already reported for that line, that reversal is part of\n     the earlier event: say so inside that finding rather than adding a second\n     entry for the same line.\n   * Small cells are not evidence: age-band or duration-month A/E values rest\n     on tiny expected counts and go extreme by chance. Never report a\n     book-level anomaly from such a cell unless the same effect is visible in\n     the by-year series or the pooled line.\n   * Findings you considered and rejected for these reasons do not appear in\n     the \"findings\" array at all.\n"
    }
  ]
}
```

### Per-run facts

| run | seed | wall time | completion tok | prompt tok | finish | answer chars | reasoning chars | error |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1234 | 402s | 7196 | 7405 | stop | 1939 | 22195 | ok |
| 2 | 1235 | 406s | 8238 | 7405 | stop | 2563 | 22333 | ok |
| 3 | 1236 | 376s | 7482 | 7405 | stop | 1931 | 22081 | ok |

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
    2015: A/E=0.931  (≈-1.1σ from 1.0)  
    2016: A/E=0.998  (≈-0.0σ from 1.0)  
    2017: A/E=0.904  (≈-1.8σ from 1.0)  
    2018: A/E=0.939  (≈-1.2σ from 1.0)  
    2019: A/E=0.902  (≈-2.1σ from 1.0)  <== -2.1 sigma
    2020: A/E=1.017  (≈+0.4σ from 1.0)  
    2021: A/E=0.987  (≈-0.3σ from 1.0)  
    2022: A/E=1.181  (≈+4.6σ from 1.0)  <== +4.6 sigma **
    2023: A/E=0.804  (≈-5.3σ from 1.0)  <== -5.3 sigma **
    2024: A/E=1.094  (≈+2.7σ from 1.0)  <== +2.7 sigma
**CI** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.038  (≈+0.9σ from 1.0)  
    2016: A/E=0.929  (≈-1.9σ from 1.0)  
    2017: A/E=0.987  (≈-0.4σ from 1.0)  
    2018: A/E=0.986  (≈-0.4σ from 1.0)  
    2019: A/E=0.965  (≈-1.2σ from 1.0)  
    2020: A/E=1.165  (≈+5.8σ from 1.0)  <== +5.8 sigma **
    2021: A/E=0.961  (≈-1.4σ from 1.0)  
    2022: A/E=1.349  (≈+13.7σ from 1.0)  <== +13.7 sigma **
    2023: A/E=1.110  (≈+4.6σ from 1.0)  <== +4.6 sigma **
    2024: A/E=0.608  (≈-17.1σ from 1.0)  <== -17.1 sigma **
**TPD** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.016  (≈+0.4σ from 1.0)  
    2016: A/E=1.077  (≈+1.8σ from 1.0)  
    2017: A/E=0.980  (≈-0.5σ from 1.0)  
    2018: A/E=1.069  (≈+1.8σ from 1.0)  
    2019: A/E=0.980  (≈-0.6σ from 1.0)  
    2020: A/E=1.227  (≈+6.5σ from 1.0)  <== +6.5 sigma **
    2021: A/E=1.014  (≈+0.4σ from 1.0)  
    2022: A/E=0.908  (≈-2.9σ from 1.0)  <== -2.9 sigma
    2023: A/E=0.917  (≈-2.7σ from 1.0)  <== -2.7 sigma
    2024: A/E=0.948  (≈-1.7σ from 1.0)  
**IP** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.016  (≈+0.5σ from 1.0)  
    2016: A/E=0.970  (≈-1.0σ from 1.0)  
    2017: A/E=0.979  (≈-0.8σ from 1.0)  
    2018: A/E=1.035  (≈+1.3σ from 1.0)  
    2019: A/E=0.995  (≈-0.2σ from 1.0)  
    2020: A/E=0.889  (≈-4.4σ from 1.0)  <== -4.4 sigma **
    2021: A/E=0.928  (≈-2.9σ from 1.0)  <== -2.9 sigma
    2022: A/E=0.903  (≈-4.1σ from 1.0)  <== -4.1 sigma **
    2023: A/E=1.265  (≈+11.5σ from 1.0)  <== +11.5 sigma **
    2024: A/E=1.035  (≈+1.5σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 0.978
    Cardiovascular: 0.963
    Injury/Accident: 1.010
    Mental Health: 0.994
    Musculoskeletal: 0.992
    Other: 1.001

### Ground truth (scorer-side)

- descriptive id: `sys_vol_macro_2020_2024` (family `systemic`)
- controls: volatility on all [2020, 2024] (sigma=0.15)

### Scorer verdict summary

- TRUE POSITIVE findings: 6
- other / false-positive findings: 4
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-e6ffa4` · run dir `results/harness_q36_final/zero_shot`_