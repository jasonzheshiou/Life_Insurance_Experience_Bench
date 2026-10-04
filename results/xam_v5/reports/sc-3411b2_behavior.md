# Behavioural dossier — scenario `sc-3411b2`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 3 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** shock on ['Death', 'IP'] [2017, 2019] (Death x1.3, IP x0.7).
**What the model said:**
- run 1: Death / shock / increase (confidence 0.8) — TRUE POSITIVE
- run 1: IP / shock / decrease (confidence 0.9) — TRUE POSITIVE
- run 2: Death / shock / increase (confidence 0.75) — TRUE POSITIVE
- run 2: IP / shock / decrease (confidence 0.85) — TRUE POSITIVE
- run 2: IP / recovery / decrease (confidence 0.3) — FALSE POSITIVE
- run 2: CI / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 2: TPD / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 3: Death / shock / increase (confidence 0.55) — TRUE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_shock_inverse_2017_2019 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: shock on ['Death', 'IP'] [2017, 2019] (Death x1.3, IP x0.7).

**Diagnosis to trust:** the injected irregularity was named correctly (shock on ['Death', 'IP'] [2017, 2019] (Death x1.3, IP x0.7)).

Confidence stated on the correct finding: 0.8, 0.9, 0.75, 0.85, 0.55, 0.75.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4033 chars, sha256 `a7c2e3605f110ee71c6063a8dc4a9fc4c705a6c9b498fd0def62359cf6d76461`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-3411b2_prompt.md`
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
| 1 | 1234 | 667s | 10676 | 2733 | stop | 2531 | 27234 | ok |
| 2 | 1235 | 1237s | 22008 | 2733 | stop | 4955 | 54753 | ok |
| 3 | 1236 | 1078s | 17506 | 2733 | stop | 2308 | 48162 | ok |

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
    2015: A/E=0.935  (≈-1.0σ from 1.0)  
    2016: A/E=0.863  (≈-2.3σ from 1.0)  <== -2.3 sigma
    2017: A/E=1.215  (≈+4.0σ from 1.0)  <== +4.0 sigma **
    2018: A/E=1.147  (≈+2.9σ from 1.0)  <== +2.9 sigma
    2019: A/E=1.216  (≈+4.6σ from 1.0)  <== +4.6 sigma **
    2020: A/E=0.940  (≈-1.3σ from 1.0)  
    2021: A/E=0.933  (≈-1.6σ from 1.0)  
    2022: A/E=0.988  (≈-0.3σ from 1.0)  
    2023: A/E=0.952  (≈-1.3σ from 1.0)  
    2024: A/E=0.953  (≈-1.4σ from 1.0)  
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
    2015: A/E=1.075  (≈+2.4σ from 1.0)  <== +2.4 sigma
    2016: A/E=1.156  (≈+5.3σ from 1.0)  <== +5.3 sigma **
    2017: A/E=0.769  (≈-8.1σ from 1.0)  <== -8.1 sigma **
    2018: A/E=0.756  (≈-8.9σ from 1.0)  <== -8.9 sigma **
    2019: A/E=0.741  (≈-9.8σ from 1.0)  <== -9.8 sigma **
    2020: A/E=1.074  (≈+2.9σ from 1.0)  <== +2.9 sigma
    2021: A/E=1.075  (≈+3.0σ from 1.0)  <== +3.0 sigma
    2022: A/E=1.103  (≈+4.3σ from 1.0)  <== +4.3 sigma **
    2023: A/E=1.102  (≈+4.4σ from 1.0)  <== +4.4 sigma **
    2024: A/E=1.079  (≈+3.5σ from 1.0)  <== +3.5 sigma **

**IP termination A/E per diagnosis (pooled):**
    Cancer: 1.005
    Cardiovascular: 1.019
    Injury/Accident: 0.962
    Mental Health: 1.012
    Musculoskeletal: 1.002
    Other: 0.957

### Ground truth (scorer-side)

- descriptive id: `sys_shock_inverse_2017_2019` (family `systemic`)
- controls: shock on ['Death', 'IP'] [2017, 2019] (Death x1.3, IP x0.7)

### Scorer verdict summary

- TRUE POSITIVE findings: 6
- other / false-positive findings: 3
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-3411b2` · run dir `results/xam_v5/zero_shot`_