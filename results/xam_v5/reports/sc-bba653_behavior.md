# Behavioural dossier — scenario `sc-bba653`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 8 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** shock on ['Death', 'CI', 'TPD', 'IP'] [2020, 2022] (Death x1.5, CI x1.3, TPD x1.2, IP x1.1).
**What the model said:**
- run 1: Death / drift / increase (confidence 0.9) — FALSE POSITIVE
- run 1: CI / drift / increase (confidence 0.9) — FALSE POSITIVE
- run 1: TPD / shock / increase (confidence 0.75) — TRUE POSITIVE
- run 1: IP / other / dispersion (confidence 0.7) — FALSE POSITIVE
- run 2: Death / shock / increase (confidence 0.9) — TRUE POSITIVE
- run 2: CI / shock / increase (confidence 0.9) — TRUE POSITIVE
- run 2: TPD / shock / increase (confidence 0.75) — TRUE POSITIVE
- run 2: IP / shock / increase (confidence 0.5) — TRUE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_shock_crisis_2020_2022 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: shock on ['Death', 'CI', 'TPD', 'IP'] [2020, 2022] (Death x1.5, CI x1.3, TPD x1.2, IP x1.1).

**Diagnosis to trust:** the injected irregularity was named correctly (shock on ['Death', 'CI', 'TPD', 'IP'] [2020, 2022] (Death x1.5, CI x1.3, TPD x1.2, IP x1.1)).

Confidence stated on the correct finding: 0.75, 0.9, 0.9, 0.75, 0.5, 0.7.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-27B-Q8_0`
- prompt: system + user turns, 4031 chars, sha256 `1dad1ddf15c4ea85a7ecded5f0f0edf069db3b5b228287cb7f1fb0b4db3f0628`
- the exact prompt text is archived at `results/xam_v5/zero_shot/sc-bba653_prompt.md`
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
| 1 | 1234 | 1735s | 27046 | 2729 | stop | 4035 | 76128 | ok |
| 2 | 1235 | 1629s | 28768 | 2729 | stop | 6747 | 70184 | ok |
| 3 | 1236 | 949s | 15295 | 2729 | stop | 4051 | 43056 | ok |

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

- descriptive id: `sys_shock_crisis_2020_2022` (family `systemic`)
- controls: shock on ['Death', 'CI', 'TPD', 'IP'] [2020, 2022] (Death x1.5, CI x1.3, TPD x1.2, IP x1.1)

### Scorer verdict summary

- TRUE POSITIVE findings: 6
- other / false-positive findings: 8
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-bba653` · run dir `results/xam_v5/zero_shot`_