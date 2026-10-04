# Behavioural dossier — scenario `sc-f19bae`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 8 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** shock on ['CI', 'TPD'] [2015, 2016] (CI x1.2, TPD x1.4).
**What the model said:**
- run 1: CI / shock / increase (confidence 0.85) — TRUE POSITIVE
- run 1: TPD / shock / increase (confidence 0.85) — TRUE POSITIVE
- run 1: TPD / shock / decrease (confidence 0.6) — FALSE POSITIVE
- run 1: Death / other / increase (confidence 0.4) — FALSE POSITIVE
- run 1: IP / other / dispersion (confidence 0.85) — FALSE POSITIVE
- run 2: TPD / shock / increase (confidence 0.85) — TRUE POSITIVE
- run 2: CI / shock / increase (confidence 0.8) — TRUE POSITIVE
- run 2: TPD / volatility / dispersion (confidence 0.6) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — shock_ci_tpd_2015_2016 (shock family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: shock on ['CI', 'TPD'] [2015, 2016] (CI x1.2, TPD x1.4).

**Diagnosis to trust:** the injected irregularity was named correctly (shock on ['CI', 'TPD'] [2015, 2016] (CI x1.2, TPD x1.4)).

Confidence stated on the correct finding: 0.85, 0.85, 0.85, 0.8, 0.85.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4033 chars, sha256 `e2273df510979bbc574868aa24fdcd4726e117eeec3b72cf77340580b60b7f18`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-f19bae_prompt.md`
- samplers: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0}
- `max_tokens`: **not sent** · `stream`: `True` · termination aggregation: `pooled`
- files shown: listing only; contents of `summary.json` and the per-benefit yearly A/E + IP termination tables

### What was sent (verbatim request body, redacted messages)

```json
{
  "model": "Qwen3.8-27B-Q8_0",
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
| 1 | 1234 | 1298s | 20982 | 2731 | stop | 4079 | 54496 | ok |
| 2 | 1235 | 937s | 16367 | 2731 | stop | 6165 | 34266 | ok |
| 3 | 1236 | 1304s | 22138 | 2731 | stop | 2495 | 55869 | ok |

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
    2015: A/E=1.209  (≈+5.1σ from 1.0)  <== +5.1 sigma **
    2016: A/E=1.182  (≈+4.9σ from 1.0)  <== +4.9 sigma **
    2017: A/E=1.008  (≈+0.2σ from 1.0)  
    2018: A/E=1.024  (≈+0.7σ from 1.0)  
    2019: A/E=0.989  (≈-0.4σ from 1.0)  
    2020: A/E=0.992  (≈-0.3σ from 1.0)  
    2021: A/E=0.951  (≈-1.8σ from 1.0)  
    2022: A/E=0.991  (≈-0.3σ from 1.0)  
    2023: A/E=0.994  (≈-0.3σ from 1.0)  
    2024: A/E=1.000  (≈+0.0σ from 1.0)  
**TPD** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.366  (≈+8.1σ from 1.0)  <== +8.1 sigma **
    2016: A/E=1.294  (≈+7.0σ from 1.0)  <== +7.0 sigma **
    2017: A/E=0.973  (≈-0.7σ from 1.0)  
    2018: A/E=0.917  (≈-2.2σ from 1.0)  <== -2.2 sigma
    2019: A/E=0.990  (≈-0.3σ from 1.0)  
    2020: A/E=0.934  (≈-1.9σ from 1.0)  
    2021: A/E=0.988  (≈-0.4σ from 1.0)  
    2022: A/E=0.930  (≈-2.2σ from 1.0)  <== -2.2 sigma
    2023: A/E=0.985  (≈-0.5σ from 1.0)  
    2024: A/E=0.944  (≈-1.9σ from 1.0)  
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

- descriptive id: `shock_ci_tpd_2015_2016` (family `shock`)
- controls: shock on ['CI', 'TPD'] [2015, 2016] (CI x1.2, TPD x1.4)

### Scorer verdict summary

- TRUE POSITIVE findings: 5
- other / false-positive findings: 8
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-f19bae` · run dir `results/xam_v5/zero_shot`_