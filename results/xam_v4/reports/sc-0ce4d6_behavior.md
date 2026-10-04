# Behavioural dossier — scenario `sc-0ce4d6`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 8 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** volatility on CI [2017, 2023] (sigma=0.3).
**What the model said:**
- run 1: CI / volatility / dispersion (confidence 0.85) — TRUE POSITIVE
- run 1: Death / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 1: TPD / other / dispersion (confidence 0.92) — FALSE POSITIVE
- run 1: IP / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 2: CI / shock / increase (confidence 0.97) — FALSE POSITIVE
- run 2: CI / other / decrease (confidence 0.8) — FALSE POSITIVE
- run 3: CI / shock / increase (confidence 0.98) — FALSE POSITIVE
- run 3: CI / other / decrease (confidence 0.9) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — trap_noise_drift_lookalike_b (noise_trap family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: volatility on CI [2017, 2023] (sigma=0.3).

**Diagnosis to trust:** the injected irregularity was named correctly (volatility on CI [2017, 2023] (sigma=0.3)).

Confidence stated on the correct finding: 0.85.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-Flash-Next`
- prompt: system + user turns, 4034 chars, sha256 `698eacd4e8edffe07f338980bdf6298d46609c26c509d09cb355eaf58749567c`
- the exact prompt text is archived at `results/xam_v4/zero_shot/sc-0ce4d6_prompt.md`
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
| 1 | 1234 | 1441s | 23392 | 2479 | stop | 3072 | 74962 | ok |
| 2 | 1235 | 834s | 14664 | 2479 | stop | 2536 | 45263 | ok |
| 3 | 1236 | 870s | 15248 | 2479 | stop | 3111 | 45839 | ok |

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

- TRUE POSITIVE findings: 1
- other / false-positive findings: 8
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-0ce4d6` · run dir `results/xam_v4/zero_shot`_