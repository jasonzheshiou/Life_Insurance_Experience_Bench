# Behavioural dossier — scenario `sc-c9d78b`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model did not clearly identify the injected anomaly. Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on Death [2016, 2019] (+0.05/yr); drift on IP [2016, 2019] (+0.03/yr); shock on ['Death', 'IP'] [2020, 2020] (Death x1.3, IP x1.2).
**What the model said:**
- run 1: Death / shock / increase (confidence 0.95) — FALSE POSITIVE
- run 1: IP / shock / increase (confidence 0.9) — FALSE POSITIVE
- run 2: Death / shock / increase (confidence 0.97) — FALSE POSITIVE
- run 2: IP / shock / increase (confidence 0.92) — FALSE POSITIVE
- run 2: IP / drift / decrease (confidence 0.65) — FALSE POSITIVE
- run 3: Death / shock / increase (confidence 0.95) — FALSE POSITIVE
- run 3: Death / shock / decrease (confidence 0.65) — FALSE POSITIVE
- run 3: IP / shock / increase (confidence 0.9) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_cascade_drift_shock_2018 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on Death [2016, 2019] (+0.05/yr); drift on IP [2016, 2019] (+0.03/yr); shock on ['Death', 'IP'] [2020, 2020] (Death x1.3, IP x1.2).

**Diagnosis to trust:** the injected irregularity was NOT named.

Confidence stated on the correct finding: n/a.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-Flash-Next`
- prompt: system + user turns, 4033 chars, sha256 `17cd1587b141f80cc7fc5dd22fa150e451f8637d81486f2686e95ed40dbce68a`
- the exact prompt text is archived at `results/xam_v4/zero_shot/sc-c9d78b_prompt.md`
- samplers: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0}
- `max_tokens`: **not sent** · `stream`: `True` · termination aggregation: `pooled`
- files shown: listing only; contents of `summary.json` and the per-benefit yearly A/E + IP termination tables

### What was sent (verbatim request body, redacted messages)

```json
{
  "model": "Qwen3.8-Flash-Next",
  "temperature": 1.0,
  "seed": 1234,
  "top_p": 0.95,
  "top_k": 20,
  "min_p": 0.0,
  "presence_penalty": 0.0,
  "repetition_penalty": 1.0,
  "repeat_penalty": 1.0,
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
```

### Per-run facts

| run | seed | wall time | completion tok | prompt tok | finish | answer chars | reasoning chars | error |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1234 | 1154s | 19356 | 2478 | stop | 2039 | 58040 | ok |
| 2 | 1235 | 1069s | 18203 | 2478 | stop | 3310 | 50902 | ok |
| 3 | 1236 | 1335s | 21851 | 2478 | stop | 3175 | 58888 | ok |

### Tool use (did it do anything besides read the text?)

| check | result |
|---|---|
| tools offered in request | `False` |
| tool calls in response | `False` |
| code fences in output | `False` |
| python code / file reads in output | `False` |
| asked to inspect files | `False` |

The runner offers no tools (`tools`/`function_call` keys never appear in the request) and the server returned none. The model answered from the text alone.

### The data it saw (for replaying its reasoning)

**Death** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.027  (≈+0.4σ from 1.0)  
    2016: A/E=0.925  (≈-1.3σ from 1.0)  
    2017: A/E=0.996  (≈-0.1σ from 1.0)  
    2018: A/E=1.070  (≈+1.4σ from 1.0)  
    2019: A/E=1.030  (≈+0.6σ from 1.0)  
    2020: A/E=1.294  (≈+6.6σ from 1.0)  <== +6.6 sigma **
    2021: A/E=1.009  (≈+0.2σ from 1.0)  
    2022: A/E=0.893  (≈-2.7σ from 1.0)  <== -2.7 sigma
    2023: A/E=0.913  (≈-2.4σ from 1.0)  <== -2.4 sigma
    2024: A/E=0.970  (≈-0.9σ from 1.0)  
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
    2015: A/E=0.979  (≈-0.7σ from 1.0)  
    2016: A/E=1.017  (≈+0.6σ from 1.0)  
    2017: A/E=1.020  (≈+0.7σ from 1.0)  
    2018: A/E=1.025  (≈+0.9σ from 1.0)  
    2019: A/E=1.045  (≈+1.7σ from 1.0)  
    2020: A/E=1.127  (≈+5.0σ from 1.0)  <== +5.0 sigma **
    2021: A/E=0.967  (≈-1.3σ from 1.0)  
    2022: A/E=0.965  (≈-1.5σ from 1.0)  
    2023: A/E=0.969  (≈-1.3σ from 1.0)  
    2024: A/E=0.946  (≈-2.4σ from 1.0)  <== -2.4 sigma

**IP termination A/E per diagnosis (pooled):**
    Cancer: 1.009
    Cardiovascular: 1.029
    Injury/Accident: 0.955
    Mental Health: 1.011
    Musculoskeletal: 1.007
    Other: 0.956

### Ground truth (scorer-side)

- descriptive id: `sys_cascade_drift_shock_2018` (family `systemic`)
- controls: drift on Death [2016, 2019] (+0.05/yr); drift on IP [2016, 2019] (+0.03/yr); shock on ['Death', 'IP'] [2020, 2020] (Death x1.3, IP x1.2)

### Scorer verdict summary

- TRUE POSITIVE findings: 0
- other / false-positive findings: 9
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-c9d78b` · run dir `results/xam_v4/zero_shot`_