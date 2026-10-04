# Behavioural dossier — scenario `sc-63f1c7`

> **SCORER-SIDE DOCUMENT — contains ground truth.** For the experimenter's eyes only. Never feed this file to a model, never copy it under `data/eval/`, never let the prompt builder see it. The model that answered never saw any part of this file.

## Tier 1 · Executive summary (for a general reader)

This scenario hides a manufactured irregularity in synthetic insurance claims data. Asked three separate times (fresh context each time, no memory, no tools, no internet), the AI model found the anomaly every time but also raised 7 additional item(s). Overall it answered 'clean' in 0/3 runs.

**What was hidden:** drift on Death [2019, 2024] (+0.08/yr); shock on ['CI'] [2021, 2021] (CI x1.4).
**What the model said:**
- run 1: Death / drift / increase (confidence 0.9) — TRUE POSITIVE
- run 1: CI / shock / increase (confidence 0.98) — FALSE POSITIVE
- run 1: TPD / other / dispersion (confidence 0.92) — FALSE POSITIVE
- run 1: IP / other / dispersion (confidence 0.92) — FALSE POSITIVE
- run 2: Death / drift / increase (confidence 0.88) — TRUE POSITIVE
- run 2: CI / shock / increase (confidence 0.95) — FALSE POSITIVE
- run 3: Death / drift / increase (confidence 0.85) — TRUE POSITIVE
- run 3: CI / shock / increase (confidence 0.88) — FALSE POSITIVE

**Did it cheat?** No. It was given only the numbers, could not run code, open files, or use tools — and none of that was available in the conversation (see Tier 3 for the evidence).

## Tier 2 · For the actuary (what to make of the answer)

**The task.** The model was handed the A/E experience tables for this book — mixed_drift_death_shock_ci (mixed family) — exactly as a pricing analyst would see them, and asked: where are the anomalies, what kind, and what would you do? It had no knowledge of the injected control: drift on Death [2019, 2024] (+0.08/yr); shock on ['CI'] [2021, 2021] (CI x1.4).

**Diagnosis to trust:** the injected irregularity was named correctly (drift on Death [2019, 2024] (+0.08/yr); shock on ['CI'] [2021, 2021] (CI x1.4)).

Confidence stated on the correct finding: 0.9, 0.88, 0.85.
**Where it helps:** the evidence strings point at the exact rows it used, so you can replay its reasoning. The magnitudes it quotes are checkable against the A/E series.

**Where to be careful:**
- A finding does not equal an injected control. The model may raise genuine statistical anomalies (e.g. a −2.5σ year) that are noise, not the planted event.
- The termination table shown to the model is aggregated (pooled over duration months); that removes an artefact the old prompt had, but the aggregate can still hide small-cell noise.
- 'Clean' verdicts are only as good as the model's tolerance for 2–3σ excursions. On deliberately clean scenarios it should say clean; on noise-trap scenarios it should say nothing.

## Tier 3 · Methodology & outcomes (for the record)

### What the model was given

- endpoint/model: `http://192.168.1.59:8080/v1` / `Qwen3.8-Flash-Next`
- prompt: system + user turns, 4033 chars, sha256 `dd533ddb0ee2c47bb1251b32fb471511adf538a200e88468efd5288e9a27de5d`
- the exact prompt text is archived at `results/xam_v4/zero_shot/sc-63f1c7_prompt.md`
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
| 1 | 1234 | 863s | 14468 | 2479 | stop | 3783 | 40767 | ok |
| 2 | 1235 | 754s | 11440 | 2479 | stop | 2360 | 36535 | ok |
| 3 | 1236 | 910s | 14585 | 2479 | stop | 2968 | 43323 | ok |

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

- descriptive id: `mixed_drift_death_shock_ci` (family `mixed`)
- controls: drift on Death [2019, 2024] (+0.08/yr); shock on ['CI'] [2021, 2021] (CI x1.4)

### Scorer verdict summary

- TRUE POSITIVE findings: 3
- other / false-positive findings: 7
- runs: 3 · overall 'clean' verdicts: 0

---
_Generated by scripts/report_xam.py · scenario `sc-63f1c7` · run dir `results/xam_v4/zero_shot`_