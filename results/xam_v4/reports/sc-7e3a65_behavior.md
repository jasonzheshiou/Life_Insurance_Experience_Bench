# Behavioural dossier — scenario `sc-7e3a65`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 3 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** shock on ['IP'] [2018, 2019] (IP x1.5).
**What the model said:**
- run 1: IP / shock / increase (confidence 0.97) — TRUE POSITIVE
- run 1: IP / other / decrease (confidence 0.85) — FALSE POSITIVE
- run 2: IP / shock / increase (confidence 0.97) — TRUE POSITIVE
- run 2: IP / other / decrease (confidence 0.75) — FALSE POSITIVE
- run 3: IP / shock / increase (confidence 0.98) — TRUE POSITIVE
- run 3: IP / other / decrease (confidence 0.7) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — shock_ip_2018_2019 (shock family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: shock on ['IP'] [2018, 2019] (IP x1.5).

**Diagnosis to trust:** the injected irregularity was named correctly (shock on ['IP'] [2018, 2019] (IP x1.5)).

Confidence stated on the correct finding: 0.97, 0.97, 0.98.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-Flash-Next`
- prompt: system + user turns, 4033 chars, sha256 `c5580ea4e30ef321cd6c5a070232f161226188933d46036f8199bad46ff4f575`
- the exact prompt text is archived at `results/xam_v4/zero_shot/sc-7e3a65_prompt.md`
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
| 1 | 1234 | 1109s | 18573 | 2479 | stop | 2512 | 61034 | ok |
| 2 | 1235 | 1481s | 23960 | 2479 | stop | 2404 | 81623 | ok |
| 3 | 1236 | 779s | 13672 | 2479 | stop | 2029 | 44451 | ok |

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
    2015: A/E=0.885  (≈-3.7σ from 1.0)  <== -3.7 sigma **
    2016: A/E=0.933  (≈-2.3σ from 1.0)  <== -2.3 sigma
    2017: A/E=0.929  (≈-2.5σ from 1.0)  <== -2.5 sigma
    2018: A/E=1.329  (≈+12.0σ from 1.0)  <== +12.0 sigma **
    2019: A/E=1.438  (≈+16.6σ from 1.0)  <== +16.6 sigma **
    2020: A/E=0.914  (≈-3.4σ from 1.0)  <== -3.4 sigma
    2021: A/E=0.903  (≈-4.0σ from 1.0)  <== -4.0 sigma **
    2022: A/E=0.915  (≈-3.6σ from 1.0)  <== -3.6 sigma **
    2023: A/E=0.901  (≈-4.3σ from 1.0)  <== -4.3 sigma **
    2024: A/E=0.937  (≈-2.8σ from 1.0)  <== -2.8 sigma

**IP termination A/E per diagnosis (pooled):**
    Cancer: 0.995
    Cardiovascular: 1.015
    Injury/Accident: 0.959
    Mental Health: 1.008
    Musculoskeletal: 1.006
    Other: 0.977

### Ground truth (scorer-side)

- descriptive id: `shock_ip_2018_2019` (family `shock`)
- controls: shock on ['IP'] [2018, 2019] (IP x1.5)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 3
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-7e3a65` · run dir `results/xam_v4/zero_shot`_