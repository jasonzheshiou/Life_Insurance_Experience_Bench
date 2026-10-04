# Behavioural dossier — scenario `sc-a3e6a6`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 13 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** shock on ['Death', 'CI', 'IP'] [2015, 2016] (Death x1.4, CI x1.2, IP x1.1).
**What the model said:**
- run 1: Death / drift / increase (confidence 0.85) — FALSE POSITIVE
- run 1: CI / shock / increase (confidence 0.8) — TRUE POSITIVE
- run 1: IP / recovery / decrease (confidence 0.6) — FALSE POSITIVE
- run 1: TPD / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 2: Death / shock / decrease (confidence 0.7) — FALSE POSITIVE
- run 2: Death / drift / increase (confidence 0.6) — FALSE POSITIVE
- run 2: CI / shock / increase (confidence 0.6) — TRUE POSITIVE
- run 2: IP / other / increase (confidence 0.3) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_shock_crisis_2015_2016 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: shock on ['Death', 'CI', 'IP'] [2015, 2016] (Death x1.4, CI x1.2, IP x1.1).

**Diagnosis to trust:** the injected irregularity was named correctly (shock on ['Death', 'CI', 'IP'] [2015, 2016] (Death x1.4, CI x1.2, IP x1.1)).

Confidence stated on the correct finding: 0.8, 0.6, 0.7.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4032 chars, sha256 `24548c1919105d296df8788b3b45fc243316b5d2bd7d9781dfa7ccc790ac2c24`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-a3e6a6_prompt.md`
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
| 1 | 1234 | 1387s | 21551 | 2731 | stop | 4145 | 61584 | ok |
| 2 | 1235 | 1261s | 21808 | 2731 | stop | 5935 | 52170 | ok |
| 3 | 1236 | 1224s | 19582 | 2731 | stop | 5321 | 53895 | ok |

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
    2015: A/E=1.269  (≈+4.2σ from 1.0)  <== +4.2 sigma **
    2016: A/E=1.460  (≈+7.8σ from 1.0)  <== +7.8 sigma **
    2017: A/E=0.987  (≈-0.2σ from 1.0)  
    2018: A/E=1.006  (≈+0.1σ from 1.0)  
    2019: A/E=1.001  (≈+0.0σ from 1.0)  
    2020: A/E=0.903  (≈-2.2σ from 1.0)  <== -2.2 sigma
    2021: A/E=0.945  (≈-1.3σ from 1.0)  
    2022: A/E=0.951  (≈-1.3σ from 1.0)  
    2023: A/E=0.950  (≈-1.4σ from 1.0)  
    2024: A/E=0.968  (≈-0.9σ from 1.0)  
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
    2015: A/E=1.052  (≈+1.6σ from 1.0)  
    2016: A/E=1.086  (≈+2.9σ from 1.0)  <== +2.9 sigma
    2017: A/E=0.969  (≈-1.1σ from 1.0)  
    2018: A/E=0.954  (≈-1.7σ from 1.0)  
    2019: A/E=1.000  (≈+0.0σ from 1.0)  
    2020: A/E=1.004  (≈+0.2σ from 1.0)  
    2021: A/E=1.006  (≈+0.3σ from 1.0)  
    2022: A/E=1.002  (≈+0.1σ from 1.0)  
    2023: A/E=1.014  (≈+0.6σ from 1.0)  
    2024: A/E=0.969  (≈-1.4σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 1.003
    Cardiovascular: 1.011
    Injury/Accident: 0.959
    Mental Health: 1.010
    Musculoskeletal: 1.010
    Other: 0.983

### Ground truth (scorer-side)

- descriptive id: `sys_shock_crisis_2015_2016` (family `systemic`)
- controls: shock on ['Death', 'CI', 'IP'] [2015, 2016] (Death x1.4, CI x1.2, IP x1.1)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 13
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-a3e6a6` · run dir `results/xam_v5/zero_shot`_