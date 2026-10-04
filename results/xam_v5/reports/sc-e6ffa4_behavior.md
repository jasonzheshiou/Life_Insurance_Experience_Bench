# Behavioural dossier — scenario `sc-e6ffa4`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 8 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** volatility on all [2020, 2024] (sigma=0.15).
**What the model said:**
- run 1: Death / other / decrease (confidence 0.5) — FALSE POSITIVE
- run 1: Death / volatility / dispersion (confidence 0.7) — TRUE POSITIVE
- run 1: CI / volatility / dispersion (confidence 0.85) — TRUE POSITIVE
- run 1: TPD / drift / decrease (confidence 0.65) — FALSE POSITIVE
- run 1: IP / volatility / dispersion (confidence 0.75) — TRUE POSITIVE
- run 1: IP / other / dispersion (confidence 0.8) — FALSE POSITIVE
- run 2: CI / volatility / dispersion (confidence 0.85) — TRUE POSITIVE
- run 2: Death / volatility / dispersion (confidence 0.7) — TRUE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_vol_macro_2020_2024 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: volatility on all [2020, 2024] (sigma=0.15).

**Diagnosis to trust:** the injected irregularity was named correctly (volatility on all [2020, 2024] (sigma=0.15)).

Confidence stated on the correct finding: 0.7, 0.85, 0.75, 0.85, 0.7, 0.85, 0.7, 0.7.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4034 chars, sha256 `3334db5bbdc5a5fcbdc7855efcf5c439cd527372a02d15a34fc883ef5d20c4c2`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-e6ffa4_prompt.md`
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
| 1 | 1234 | 2163s | 33707 | 2731 | stop | 4485 | 89414 | ok |
| 2 | 1235 | 1256s | 25451 | 2731 | stop | 5437 | 51175 | ok |
| 3 | 1236 | 1569s | 25493 | 2731 | stop | 3955 | 64742 | ok |

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

- TRUE POSITIVE findings: 8
- other / false-positive findings: 8
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-e6ffa4` · run dir `results/xam_v5/zero_shot`_