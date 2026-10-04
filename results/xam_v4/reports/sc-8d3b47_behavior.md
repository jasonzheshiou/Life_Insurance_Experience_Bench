# Behavioural dossier — scenario `sc-8d3b47`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 5 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (-0.04/yr).
**What the model said:**
- run 1: Death / drift / increase (confidence 0.85) — TRUE POSITIVE
- run 1: CI / drift / decrease (confidence 0.85) — FALSE POSITIVE
- run 1: TPD / other / dispersion (confidence 0.9) — FALSE POSITIVE
- run 1: IP / other / dispersion (confidence 0.7) — FALSE POSITIVE
- run 2: Death / drift / increase (confidence 0.9) — TRUE POSITIVE
- run 2: CI / drift / decrease (confidence 0.95) — FALSE POSITIVE
- run 3: Death / drift / increase (confidence 0.92) — TRUE POSITIVE
- run 3: CI / drift / decrease (confidence 0.94) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — sys_drift_diverge_2018_2024 (systemic family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (-0.04/yr).

**Diagnosis to trust:** the injected irregularity was named correctly (drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (-0.04/yr)).

Confidence stated on the correct finding: 0.85, 0.9, 0.92.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-Flash-Next`
- prompt: system + user turns, 4037 chars, sha256 `05a32c0dc317a9897f8706dc1939fb4f3d68738ad30a508eaabd42a41e9ff902`
- the exact prompt text is archived at `results/xam_v4/zero_shot/sc-8d3b47_prompt.md`
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
| 1 | 1234 | 838s | 14606 | 2483 | stop | 3935 | 40129 | ok |
| 2 | 1235 | 599s | 10898 | 2483 | stop | 2050 | 28795 | ok |
| 3 | 1236 | 666s | 11965 | 2483 | stop | 2107 | 33059 | ok |

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

- descriptive id: `sys_drift_diverge_2018_2024` (family `systemic`)
- controls: drift on Death [2018, 2024] (+0.06/yr); drift on CI [2018, 2024] (-0.04/yr)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 5
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-8d3b47` · run dir `results/xam_v4/zero_shot`_