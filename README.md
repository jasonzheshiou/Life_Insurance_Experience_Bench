# ⚖️ Data Pipeline Arena — Anomaly Detection Benchmark

**A deterministic exam for LLM agents: can they build a real anomaly-detection
pipeline on synthetic life-insurance claims data?**

The full implementation plan lives in
[BENCHMARK_IMPLEMENTATION_GUIDE.md](BENCHMARK_IMPLEMENTATION_GUIDE.md) — every
locked design decision, schema, and guard is specified there. This README is the
front door; the guide is the single source of truth.

> **📊 For experiment results, start here:**
> [docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md) — the master index for the
> harness, both model campaigns (Qwen3.6-27B and Qwen3.8-27B), every result corpus
> and its location, the final tables, full replication commands, and the known
> failures. If you are asking "what was done, what were the results, how do I
> reproduce it", that is the document you want.

---

## ⚠️ In Development — Plan Stage

**This project is a work in progress.** You may encounter:

- Missing modules as milestones **M0–M4** land (see the Testing section below)
- Schema or CLI changes between revisions
- A sandbox and scoring stack that is still being hardened

**This is intentional** — the project is a benchmark for agentic coding on a
security-relevant task (model-written code runs inside a sandbox), so rough
edges are part of the experiment. **Feedback and comments are welcome.**

---

## 🤖 Why This Project Exists

The arena measures what **agentic coding** can and cannot do on a hard,
security-relevant task. A model is handed synthetic claims data and must detect
*injected* trend anomalies — drift, shock, volatility, and IP-recovery changes —
by writing and running its own code inside a sandbox, iterating **only** on
optimization-set feedback, and being scored exactly once on a heldout set.

### What This Proves
| Capability | Status |
|-----------|--------|
| Deterministic scenario generation + strict split (no LLM) | 📐 Specified (M0) |
| Pydantic-validated verdict contract | 📐 Specified (M0) |
| Sandboxed free-code runner (subprocess + container tiers) | 📐 Specified (M1) |
| Scoring: precision/recall, window IoU, type & magnitude error | 📐 Specified (M0) |
| N×K runs with median + spread reporting, frozen & hashed pipelines | 📐 Specified (M2) |
| Stage-3 report + blind human validation, golden set | 📐 Specified (M3) |
| Multi-model runs, cost/effort metrics, docs | 📐 Specified (M4) |

---

## 📋 Quick Navigation

<details>
<summary><strong>🚀 Quick Start</strong> — the planned workflow</summary>

```bash
pip install -e ".[dev]"        # pyproject lands with M0

abench init                    # scaffold config/ + data/ directories
abench generate                # Stage 0: mint scenarios + optimization/heldout split
abench run                     # Stage 1 zero-shot + Stage 2 free-code loop
abench score                   # match verdicts to manifests, build leaderboard
abench report                  # Stage 3: per-cell report.md + human-review queue
abench validate                # schema + split-separation self-checks
```

> The CLI above is the **planned** interface (guide §10). Nothing is wired up
> yet — start at milestone **M0** (deterministic hand-written "model" proving
> the split + scoring machinery before any LLM or sandbox is introduced).

</details>

<details>
<summary><strong>🧪 The Three Stages</strong> — what the arena runs</summary>

| Stage | What happens | Output |
|-------|--------------|--------|
| **Stage 0 — Data** | Deterministic scenario generation + disjoint `optimization`/`heldout` split (no LLM) | scenario stores, manifests (scorer-only) |
| **Stage 1 — Zero-shot** | Model returns a `Verdict` JSON from the artifacts alone — no code | `verdict.json` per scenario |
| **Stage 2 — Free-code** | Model writes & runs arbitrary code in the sandbox, iterates ≤ 3–5 times on optimization-set feedback only | frozen pipeline in `submissions/<hash>/` |
| **Stage 3 — Report** | Deterministic `report.md` + blind human validation | `reports/*.md`, `human_review/annotations.jsonl` |

**Locked guarantees** (guide §2): ground truth is always *generated*, never
hand-curated; the heldout set is mounted once, read-only, scored once, and never
fed back; malformed verdict JSON is scored as a miss; results are reported as
median + spread over N×K runs; two baselines — the classical control-chart
detector and the model's own Stage-1 verdict — are always shown.

</details>

<details>
<summary><strong>🎛️ Scenario Controls</strong> — what gets injected</summary>

| Control | Effect | Observable signature (starter set) |
|---------|--------|------------------------------------|
| **Drift** | Per-year slope on a benefit's A/E | `drift_death_up_2018_2024`: Death A/E ~0.74 → 1.30 in 2018–24 |
| **Shock** | One-off multiplier over a window | `shock_covid_2020_2022`: Death spike 1.31/1.34/1.25 in 2020–22 |
| **Volatility** | Per-year σ noise on claim counts | `volatility_ip_sigma_03`: IP count variance ×3, level unchanged |
| **IP recovery** | Termination-rate multiplier (IP) | `ip_recovery_mental_health_x2`: MH termination A/E ≈ 2.0, incidence untouched |
| **No-op** | All neutral | `noop_neutral_controls`: bit-identical to `baseline` |

Harder variants (smaller drift 0.05, shock ×1.2, narrower windows, σ=0.15, and
mixed-benefit scenarios) are specified in the guide §5.3.

</details>

<details>
<summary><strong>📐 Scoring Metrics</strong> — what "good" means</summary>

| Metric | Description |
|--------|-------------|
| **Precision / Recall / F1** | per-scenario claim matching against the manifest, aggregated |
| **Window IoU** | intersection/union of predicted vs true year window (penalizes vague "everything") |
| **Type accuracy** | fraction of claims with the correct control type |
| **Magnitude error** | normalized error vs the injected factor |
| **False-positive rate** | spurious claims on no-op/baseline scenarios |
| **No-op correctness** | correctly identifying clean scenarios |
| **Effort metrics** | tokens, wall-clock, iteration count, code length, human interventions |

Baselines always shown: the classical control chart (z-score + CUSUM), the same
model's Stage-1 zero-shot, and trivial random / all-baseline for calibration.

</details>

<details>
<summary><strong>📁 Project Structure</strong></summary>

```
data_pipeline_arena/
├── README.md                           # this file
├── BENCHMARK_IMPLEMENTATION_GUIDE.md   # the plan — single source of truth
├── pyproject.toml                      # Python >= 3.11 (lands with M0)
├── config/
│   └── experiment.yaml                 # scenarios, models, N/K, split, limits
├── src/abench/
│   ├── manifest.py                     # ScenarioManifest (ground truth)
│   ├── verdict.py                      # Verdict + DetectResult schemas (pydantic)
│   ├── datasets.py                     # generate/load splits; strict separation
│   ├── detectors/                      # OPTIONAL importable registry (statistical, ml)
│   ├── scoring.py                      # precision/recall, window IoU, type/magnitude error
│   ├── runner.py                       # SANDBOXED arbitrary-code runner
│   ├── orchestrator.py                 # stages 1–3, N×K loop, freeze/hash
│   ├── llm_client.py                   # pluggable LLM adapter (OpenAI-compatible)
│   ├── report.py                       # Stage 3: charts + tables -> report.md
│   └── cli.py                          # abench <init|generate|run|score|report|validate>
├── data/
│   ├── raw/                            # generated scenario stores (gitignored)
│   └── split/
│       ├── optimization/               # data handed to models for iteration
│       ├── heldout/                    # data mounted ONCE for final scoring
│       └── manifests/                  # ground truth — ONLY the scorer reads this
├── submissions/                        # frozen model pipelines (content-hashed)
├── results/<run-id>/                   # verdicts.jsonl, scores.json, leaderboard.json, reports/
└── human_review/                       # queue.jsonl + annotations.jsonl
```

</details>

<details>
<summary><strong>🛡️ Sandbox & Fairness</strong> — guards that must not be skipped</summary>

- **Tier 1 (subprocess, works everywhere):** fresh temp cwd,
  `resource.setrlimit` for CPU time / address space / file size, wall-clock
  watchdog, read-only data + write-only output, network blocked
  (`unshare -n` on Linux; weaker on macOS/Windows — documented).
- **Tier 2 (container, recommended for real runs):** Docker/Podman with
  `--network none`, read-only data volume, `--cpus` / `--memory` /
  `--pids-limit`, non-root user.
- **Hard limits to start with:** 120 s timeout, 2 GB memory, 1 CPU, 10 MB output.
- **Leakage guard:** feedback to the model may contain *only* optimization-set
  results; the heldout set is generated before any model runs, never referenced
  in any prompt, mounted at freeze time, and scored once. The
  optimization-vs-heldout score gap is itself a reported metric — the
  overfitting/autonomy-danger signal.
- **Fairness audit:** content hash of every model-facing input proves all models
  saw byte-identical data.

</details>

<details>
<summary><strong>⚠️ Limitations & Assumptions</strong></summary>

- **Plan stage for the arena core** — the benchmark harness modules (scorer,
  sandbox, orchestrator) are specified, not yet shipped; the **scenario dataset
  pipeline is implemented and generating** (`scripts/generate_scenarios.py`).
- Synthetic claims data from the life-insurance generator; no real policyholder
  or company data.
- Anomalies are *injected by design* — detection means recovering a known signal
  (from the manifest), not discovering unknown ones.
- Sandbox Tier 1 is weaker on macOS/Windows; the leaderboard must state the tier
  used for each run.
- LLM non-determinism is controlled, not eliminated: N×K runs, fixed
  temperature/seed where possible, median + spread reporting.
- `scikit-learn` is an optional extra (ML detector registry only); the core runs
  without it.

</details>

<details>
<summary><strong>📊 Dataset</strong> — the generated arena scenarios</summary>

The arena's input data is generated from the sibling
`Life_insurance_data_generator_new` project by
[`scripts/generate_scenarios.py`](scripts/generate_scenarios.py), driven by the
scenario registry [`config/scenarios.yaml`](config/scenarios.yaml).

| Property | Value |
|---|---|
| Scenarios | 47 (23 optimization / 24 heldout) |
| Families | none, drift, shock, volatility, noise_trap, recovery, mixed, systemic |
| Split discipline | disjoint by (benefit × control type × window × factor) |
| Scale | `tiny` / `medium` / `full` (default `medium`; one-line switch) |
| Model-facing (ZONE A) | `data/eval/` — opaque scenario ids (`sc-<6hex>`), no answer-bearing names; `dataset.json` hashes + seal |
| Ground truth (ZONE B) | `data/truth/manifests/` (scorer-only, sealed via `seal.json`) — never ships with `data/eval/` |
| Leak enforcement | byte-level scan at build time + at run time (`scripts/leakcheck.py`) |

Regenerate or extend with:

```bash
python scripts/generate_scenarios.py --scale full      # canonical 250k-policy dataset
python scripts/generate_scenarios.py --scale tiny      # fast smoke pass
```

See the [Dataset usage guide](docs/dataset-usage.md) for the full CLI, the
registry format, and how to add scenarios; the [architecture](docs/architecture.md)
documents the design.

</details>

<details>
<summary><strong>📚 Documentation</strong></summary>

- [Implementation guide](BENCHMARK_IMPLEMENTATION_GUIDE.md) — the plan: locked
  design decisions, schemas, stages, sandbox, scoring (single source of truth)
- [Usage guide](docs/usage.md) — install, CLI, experiment config, and the
  milestone roadmap
- [Dataset usage](docs/dataset-usage.md) — generate/extend the scenario
  dataset; registry format; CLI reference; manifests
- [Architecture](docs/architecture.md) — dataset pipeline design, invariants,
  and extension points
- [Scenario catalog](docs/scenario-catalog.md) — all 47 scenarios, families,
  splits, and injected controls (auto-generated from the registry)
- [Assumptions reference](docs/assumptions-reference.md) — scenario manifest,
  verdict contract, scoring rubric, split and sandbox rules
- [Review & results](docs/review-and-results.md) — the test plan, current
  status, and where measured results land

</details>

<details>
<summary><strong>🧪 Testing</strong></summary>

```bash
pytest tests/            # registry + invariant tests (dataset pipeline)
abench validate          # schema + split-separation + sandbox self-checks (lands with M0)
```

**Current test status**: the dataset pipeline's registry invariants
(disjointness, manifest contract, scale presets) are covered by
[`tests/test_registry.py`](tests/test_registry.py) — all passing. The generator
also runs per-scenario sanity checks with a hard gate before `data/eval/` is
written, and every assembly must pass the byte-level leak scan
([`scripts/leakcheck.py`](scripts/leakcheck.py)) — the build fails on any hit.
The remaining acceptance test plan (end-to-end smoke, fairness,
baseline-sanity for the arena core) is specified in
[Review & results](docs/review-and-results.md).

</details>

<details>
<summary><strong>📄 License</strong></summary>

This project is licensed under the MIT License — see the LICENSE file for
details (to be added with M0).

The scenario data is **synthetic** and provided for research, learning, and
testing only.

**Acknowledgments**: the Life Insurance Data Generator project (scenario
source), the pytest / pydantic / Streamlit communities.

</details>

---

*Last updated: 2026 | Project status: dataset pipeline implemented (47 scenarios) — arena core starts at milestone M0*
