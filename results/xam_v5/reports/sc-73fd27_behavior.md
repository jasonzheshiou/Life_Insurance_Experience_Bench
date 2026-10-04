# Behavioural dossier — scenario `sc-73fd27`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model did not clearly identify the injected anomaly. Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on Death [2016, 2019] (+0.05/yr); drift on CI [2016, 2019] (+0.03/yr); drift on IP [2016, 2019] (+0.02/yr).
**What the model said:**
- run 1: Death / shock / increase (confidence 0.65) — FALSE POSITIVE
- run 1: CI / drift / increase (confidence 0.6) — FALSE POSITIVE
- run 1: IP / volatility / dispersion (confidence 0.55) — FALSE POSITIVE
- run 1: IP / recovery / decrease (confidence 0.35) — FALSE POSITIVE
- run 2: Death / shock / increase (confidence 0.75) — FALSE POSITIVE
- run 2: CI / shock / increase (confidence 0.8) — FALSE POSITIVE
- run 2: IP / shock / increase (confidence 0.7) — FALSE POSITIVE
- run 2: IP / recovery / decrease (confidence 0.35) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_drift_aging_2016_2019 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on Death [2016, 2019] (+0.05/yr); drift on CI [2016, 2019] (+0.03/yr); drift on IP [2016, 2019] (+0.02/yr).

**Diagnosis to trust:** the injected irregularity was NOT named.

Confidence stated on the correct finding: n/a.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4035 chars, sha256 `4fe33f94ef9297f967b01f08f0cf098d78ca1cba7550ed3d745001a269ab5c5d`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-73fd27_prompt.md`
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
| 1 | 1234 | 946s | 14649 | 2734 | stop | 4198 | 41105 | ok |
| 2 | 1235 | 1749s | 31036 | 2734 | stop | 5423 | 76204 | ok |
| 3 | 1236 | 1804s | 29167 | 2734 | stop | 3799 | 79054 | ok |

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
    2015: A/E=0.889  (≈-1.7σ from 1.0)  
    2016: A/E=0.998  (≈-0.0σ from 1.0)  
    2017: A/E=1.002  (≈+0.0σ from 1.0)  
    2018: A/E=1.150  (≈+3.0σ from 1.0)  <== +3.0 sigma
    2019: A/E=1.102  (≈+2.1σ from 1.0)  <== +2.1 sigma
    2020: A/E=1.040  (≈+0.9σ from 1.0)  
    2021: A/E=0.943  (≈-1.4σ from 1.0)  
    2022: A/E=0.986  (≈-0.4σ from 1.0)  
    2023: A/E=0.951  (≈-1.3σ from 1.0)  
    2024: A/E=1.000  (≈-0.0σ from 1.0)  
**CI** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.019  (≈+0.5σ from 1.0)  
    2016: A/E=0.959  (≈-1.1σ from 1.0)  
    2017: A/E=1.015  (≈+0.4σ from 1.0)  
    2018: A/E=1.099  (≈+3.1σ from 1.0)  <== +3.1 sigma
    2019: A/E=1.108  (≈+3.6σ from 1.0)  <== +3.6 sigma **
    2020: A/E=0.985  (≈-0.5σ from 1.0)  
    2021: A/E=1.022  (≈+0.8σ from 1.0)  
    2022: A/E=1.002  (≈+0.1σ from 1.0)  
    2023: A/E=0.987  (≈-0.5σ from 1.0)  
    2024: A/E=0.983  (≈-0.7σ from 1.0)  
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
    2015: A/E=1.025  (≈+0.8σ from 1.0)  
    2016: A/E=1.055  (≈+1.8σ from 1.0)  
    2017: A/E=1.027  (≈+0.9σ from 1.0)  
    2018: A/E=1.084  (≈+3.1σ from 1.0)  <== +3.1 sigma
    2019: A/E=1.046  (≈+1.7σ from 1.0)  
    2020: A/E=0.973  (≈-1.0σ from 1.0)  
    2021: A/E=0.935  (≈-2.6σ from 1.0)  <== -2.6 sigma
    2022: A/E=0.978  (≈-0.9σ from 1.0)  
    2023: A/E=0.992  (≈-0.4σ from 1.0)  
    2024: A/E=0.969  (≈-1.4σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 0.998
    Cardiovascular: 1.033
    Injury/Accident: 0.954
    Mental Health: 1.015
    Musculoskeletal: 1.016
    Other: 0.965

### Ground truth (scorer-side)

- descriptive id: `sys_drift_aging_2016_2019` (family `systemic`)
- controls: drift on Death [2016, 2019] (+0.05/yr); drift on CI [2016, 2019] (+0.03/yr); drift on IP [2016, 2019] (+0.02/yr)

### Scorer verdict summary

- TRUE POSITIVE findings: 0
- other / false-positive findings: 14
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-73fd27` · run dir `results/xam_v5/zero_shot`_