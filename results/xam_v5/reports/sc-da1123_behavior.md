# Behavioural dossier — scenario `sc-da1123`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 13 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (+0.04/yr); drift on TPD [2018, 2024] (+0.03/yr); drift on IP [2018, 2024] (+0.02/yr).
**What the model said:**
- run 1: Death / drift / decrease (confidence 0.75) — TRUE POSITIVE
- run 1: Death / drift / increase (confidence 0.85) — TRUE POSITIVE
- run 1: CI / shock / increase (confidence 0.7) — FALSE POSITIVE
- run 1: CI / drift / increase (confidence 0.6) — FALSE POSITIVE
- run 1: TPD / drift / increase (confidence 0.55) — FALSE POSITIVE
- run 1: IP / recovery / decrease (confidence 0.35) — FALSE POSITIVE
- run 2: Death / drift / decrease (confidence 0.85) — TRUE POSITIVE
- run 2: Death / drift / increase (confidence 0.8) — TRUE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_drift_aging_2018_2024 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (+0.04/yr); drift on TPD [2018, 2024] (+0.03/yr); drift on IP [2018, 2024] (+0.02/yr).

**Diagnosis to trust:** the injected irregularity was named correctly (drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (+0.04/yr); drift on TPD [2018, 2024] (+0.03/yr); drift on IP [2018, 2024] (+0.02/yr)).

Confidence stated on the correct finding: 0.75, 0.85, 0.85, 0.8, 0.85, 0.6.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4031 chars, sha256 `264045c38bccbd20f015b10b0b7dc78c938ad7907b4b93c6c7f545634dd8a012`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-da1123_prompt.md`
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
| 1 | 1234 | 1599s | 25510 | 2729 | stop | 4378 | 69084 | ok |
| 2 | 1235 | 1361s | 24013 | 2729 | stop | 6399 | 52512 | ok |
| 3 | 1236 | 1644s | 25916 | 2729 | stop | 5083 | 71447 | ok |

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


### Ground truth (scorer-side)

- descriptive id: `sys_drift_aging_2018_2024` (family `systemic`)
- controls: drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (+0.04/yr); drift on TPD [2018, 2024] (+0.03/yr); drift on IP [2018, 2024] (+0.02/yr)

### Scorer verdict summary

- TRUE POSITIVE findings: 6
- other / false-positive findings: 13
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-da1123` · run dir `results/xam_v5/zero_shot`_