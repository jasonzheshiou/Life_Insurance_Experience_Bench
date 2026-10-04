# Usage — Data Pipeline Arena

How to set up, configure, and run the benchmark. The design behind every
command is specified in the [implementation guide](../BENCHMARK_IMPLEMENTATION_GUIDE.md)
(§10); the command surface below is the **planned** interface that milestone
M0 wires up.

> **Generating the scenario dataset** (the arena's Stage-0 input) is already
> implemented — see the [Dataset usage guide](dataset-usage.md) for the CLI,
> the registry format, and how to add scenarios.

---

## 1. Installation

```bash
# Python >= 3.11
pip install -e ".[dev]"       # core: pydantic, numpy, pandas, matplotlib, pyyaml
pip install -e ".[ml]"        # optional: scikit-learn for the ML detector registry
```

Dependencies are intentionally minimal; `scikit-learn` is an extra so the core
runs without it.

## 2. Configuration — `config/experiment.yaml`

```yaml
generator:
  path: ../Life_insurance_data_generator   # or pip-installed
  seed: 42
  commit: ""                                # recorded for provenance

split:
  optimization_scenarios: 12
  heldout_scenarios: 8
  heldout_disjoint: true

runs:
  llm_samples: 3        # N
  exec_samples: 3       # K
  max_iterations: 4

limits:
  timeout_s: 120
  memory_mb: 2048
  cpu: 1
  output_bytes: 10485760   # 10 MB
```

## 3. CLI reference

```bash
abench init                    # scaffold config/ + data/ directories
abench generate                # Stage 0: mint scenarios + optimization/heldout split
abench run                     # Stage 1 zero-shot + Stage 2 free-code loop
abench score --run-id <id>     # match verdicts to manifests, build scores.json
abench report --run-id <id>    # Stage 3: deterministic report.md + review queue
abench validate                # schema + split-separation self-checks
```

`abench run` takes an OpenAI-compatible endpoint (model id, base URL, API key)
from config or env vars; the adapter in `src/abench/llm_client.py` is
deliberately thin so any compatible endpoint works.

## 4. Typical experiment flow

1. `abench init` — creates `config/`, `data/raw`, `data/eval`, `submissions/`,
   `results/`, `human_review/`.
2. `abench generate` — mints scenarios via the generator CLI and assembles the
   disjoint, **opaque-id** eval workspace `data/eval/{optimization,heldout}/`;
   manifests and the id map go to `data/truth/` (scorer-only, sealed).
3. `abench run` — for each model: Stage-1 zero-shot verdicts, then the Stage-2
   sandboxed free-code loop (≤ `max_iterations` iterations on optimization-set
   feedback only), then freeze/hash the final pipeline.
4. `abench score` — scores heldout exactly once; writes `scores.json` and
   `leaderboard.json` (median + spread, sandbox tier stated).
5. `abench report` — renders `report.md` per (model × scenario × stage) and
   queues anomalies for blind human review.

## 5. What you get per run

- `results/<run-id>/verdicts.jsonl` — every verdict
- `results/<run-id>/scores.json` — detection, window IoU, type accuracy,
  magnitude error, FP rate, no-op correctness, effort metrics
- `results/<run-id>/leaderboard.json` — heldout-only ranking
- `results/<run-id>/reports/*.md` — Stage-3 reports (ground truth revealed)
- `human_review/` — blind-review queue and accumulated annotations

See [Review & results](review-and-results.md) for the current milestone status
and the full acceptance test plan.
