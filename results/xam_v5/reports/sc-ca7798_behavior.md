# Behavioural dossier — scenario `sc-ca7798`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 12 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on CI [2020, 2024] (+0.05/yr); volatility on IP [2015, 2024] (sigma=0.15); ip_recovery on ['Mental Health'] [2015, 2024] (Mental Health x1.5).
**What the model said:**
- run 1: CI / drift / increase (confidence 0.75) — TRUE POSITIVE
- run 1: IP / volatility / dispersion (confidence 0.9) — FALSE POSITIVE
- run 1: IP / recovery / increase (confidence 0.85) — FALSE POSITIVE
- run 1: Death / other / dispersion (confidence 0.8) — FALSE POSITIVE
- run 1: TPD / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 2: CI / drift / decrease (confidence 0.7) — FALSE POSITIVE
- run 2: CI / drift / increase (confidence 0.9) — TRUE POSITIVE
- run 2: IP / volatility / dispersion (confidence 0.85) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — mixed_triple_ci_ip_mh (mixed family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on CI [2020, 2024] (+0.05/yr); volatility on IP [2015, 2024] (sigma=0.15); ip_recovery on ['Mental Health'] [2015, 2024] (Mental Health x1.5).

**Diagnosis to trust:** the injected irregularity was named correctly (drift on CI [2020, 2024] (+0.05/yr); volatility on IP [2015, 2024] (sigma=0.15); ip_recovery on ['Mental Health'] [2015, 2024] (Mental Health x1.5)).

Confidence stated on the correct finding: 0.75, 0.9, 0.85.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4031 chars, sha256 `43bd0d0dab0123b81542d6e804a18441418344a7f7a77e3998a49767083f6387`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-ca7798_prompt.md`
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
| 1 | 1234 | 1098s | 17842 | 2729 | stop | 3559 | 50171 | ok |
| 2 | 1235 | 928s | 16227 | 2729 | stop | 4699 | 36784 | ok |
| 3 | 1236 | 1022s | 16146 | 2729 | stop | 4698 | 45132 | ok |

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
    2015: A/E=0.939  (≈-0.9σ from 1.0)  
    2016: A/E=1.160  (≈+2.7σ from 1.0)  <== +2.7 sigma
    2017: A/E=0.963  (≈-0.7σ from 1.0)  
    2018: A/E=0.970  (≈-0.6σ from 1.0)  
    2019: A/E=1.008  (≈+0.2σ from 1.0)  
    2020: A/E=0.995  (≈-0.1σ from 1.0)  
    2021: A/E=0.978  (≈-0.5σ from 1.0)  
    2022: A/E=1.014  (≈+0.3σ from 1.0)  
    2023: A/E=1.014  (≈+0.4σ from 1.0)  
    2024: A/E=0.988  (≈-0.4σ from 1.0)  
**CI** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=1.026  (≈+0.6σ from 1.0)  
    2016: A/E=0.969  (≈-0.8σ from 1.0)  
    2017: A/E=0.928  (≈-2.1σ from 1.0)  <== -2.1 sigma
    2018: A/E=0.887  (≈-3.5σ from 1.0)  <== -3.5 sigma **
    2019: A/E=0.926  (≈-2.5σ from 1.0)  <== -2.5 sigma
    2020: A/E=0.931  (≈-2.4σ from 1.0)  <== -2.4 sigma
    2021: A/E=0.984  (≈-0.6σ from 1.0)  
    2022: A/E=1.045  (≈+1.8σ from 1.0)  
    2023: A/E=1.114  (≈+4.7σ from 1.0)  <== +4.7 sigma **
    2024: A/E=1.175  (≈+7.6σ from 1.0)  <== +7.6 sigma **
**TPD** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.998  (≈-0.0σ from 1.0)  
    2016: A/E=1.036  (≈+0.9σ from 1.0)  
    2017: A/E=1.014  (≈+0.3σ from 1.0)  
    2018: A/E=1.053  (≈+1.4σ from 1.0)  
    2019: A/E=1.006  (≈+0.2σ from 1.0)  
    2020: A/E=0.966  (≈-1.0σ from 1.0)  
    2021: A/E=1.016  (≈+0.5σ from 1.0)  
    2022: A/E=1.004  (≈+0.1σ from 1.0)  
    2023: A/E=1.009  (≈+0.3σ from 1.0)  
    2024: A/E=0.976  (≈-0.8σ from 1.0)  
**IP** — yearly A/E with Poisson noise band (σ ≈ 1/√expected):
    2015: A/E=0.744  (≈-8.2σ from 1.0)  <== -8.2 sigma **
    2016: A/E=1.301  (≈+10.2σ from 1.0)  <== +10.2 sigma **
    2017: A/E=1.067  (≈+2.4σ from 1.0)  <== +2.4 sigma
    2018: A/E=0.943  (≈-2.1σ from 1.0)  <== -2.1 sigma
    2019: A/E=1.004  (≈+0.2σ from 1.0)  
    2020: A/E=1.278  (≈+10.9σ from 1.0)  <== +10.9 sigma **
    2021: A/E=0.947  (≈-2.1σ from 1.0)  <== -2.1 sigma
    2022: A/E=0.875  (≈-5.3σ from 1.0)  <== -5.3 sigma **
    2023: A/E=0.911  (≈-3.9σ from 1.0)  <== -3.9 sigma **
    2024: A/E=0.971  (≈-1.3σ from 1.0)  

**IP termination A/E per diagnosis (pooled):**
    Cancer: 1.023
    Cardiovascular: 1.037
    Injury/Accident: 0.966
    Mental Health: 1.466  <== deviates
    Musculoskeletal: 1.002
    Other: 1.019

### Ground truth (scorer-side)

- descriptive id: `mixed_triple_ci_ip_mh` (family `mixed`)
- controls: drift on CI [2020, 2024] (+0.05/yr); volatility on IP [2015, 2024] (sigma=0.15); ip_recovery on ['Mental Health'] [2015, 2024] (Mental Health x1.5)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 12
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-ca7798` · run dir `results/xam_v5/zero_shot`_