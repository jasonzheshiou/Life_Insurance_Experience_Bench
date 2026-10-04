# Anomaly-Detection Benchmark — Implementation Guide

> **Audience:** an LLM (or engineer) implementing this from scratch in a NEW folder.
> **Purpose:** a controlled, repeatable sandbox that (1) lets different AI models
> build their own pipeline to detect trend anomalies in synthetic life-insurance
> experience data, (2) compares models/architectures on an objective leaderboard,
> and (3) produces a Markdown report a human can validate.
> **Source data:** the "Synthetic Life Insurance Experience Data Generator" repo
> (pure-Python, deterministic, seed=42). This benchmark is a separate project that
> consumes that generator's outputs.

---

## 0. Goals, non-goals, and the experiment thesis

### Goals
1. **Stage 1 — Zero-shot baseline.** Each model detects anomalies *without* a
   pipeline (a single structured answer from raw data). This measures whether a
   pipeline is even necessary for a given model.
2. **Stage 2 — Free-code pipeline.** Each model **writes and runs its own code**
   (any language/runtime the harness sandbox supports, default Python) to build,
   then iteratively improve, an anomaly-detection pipeline. This measures
   pipeline-building + optimization capability and long-horizon autonomy.
3. **Stage 3 — Human validation.** Results are summarized into a Markdown report
   (charts + tables) for a human to adjudicate (true positive / false positive /
   missed / boundary).

### Non-goals
- Not a production fraud/anomaly system.
- Not a polished UI (validation is a thin review loop over generated artifacts).
- Not concerned with generator internals — treat the generator as a black-box data
  source with a known, injected ground truth.

### The thesis to test
> As model capabilities change, does the optimal *architecture around the model*
> change too? (tightly-scoped orchestration vs. a single autonomous agent)

The benchmark must therefore record, per cell, not only **accuracy** but also
**autonomy/cost/effort** (tokens, wall-clock, iterations, human interventions), so
"does this model need the orchestration layer?" can be answered from data.

---

## 1. Domain background (what the data means)

You must understand this to write correct prompts, scorers, and detectors.

- **Benefits:** `Death`, `CI` (critical illness), `TPD` (total permanent
  disability), `IP` (income protection).
- **A/E analysis:** `Actuals` are generated from a base-rate model (Layer A) plus
  injected controls. `Expected` is computed from a separate actuarial-assumption
  model (Layer B). A/E = Actual / Expected. **Baseline A/E ≈ 1.0**, with Poisson
  sampling noise ~ `1/sqrt(target_claim_count)`.
- **Injected anomalies (the ground truth), all date-bounded and touching actuals
  only:**
  - `drift` — rate multiplier grows linearly over a window (e.g. Death +0.10/yr,
    2018–2024).
  - `shock` — step multiplier over a window (e.g. Death ×1.5, 2020–2022).
  - `volatility` — per-year multiplier ~ N(1, σ); **mean/level unchanged**, only
    dispersion increases (e.g. IP σ=0.3).
  - `ip_recovery` — termination/recovery-rate multiplier for a diagnosis in IP
    (e.g. Mental Health ×2.0). Observable in **termination A/E**, not incidence.
  - `none` / neutral — no-op control (all controls present at neutral values).

### What one scenario produces
For each scenario the generator writes a directory like `artifacts/scenario_verification/<scenario>/`:

| File | Contents |
|---|---|
| `ae_<benefit>_by_year.csv` | `Year, Actual, Expected, AE` per benefit (4 files) |
| `ae_<benefit>_age_gender.png` | incidence A/E by 5-year age band × gender |
| `ae_ip_termination_by_month.png` | IP termination A/E by duration month |
| `termination_ae_ip.csv` | `Diagnosis, DurationMonth, Exposed, Recovered, Rates, AE` |
| `summary.json` | per-benefit overall A/E, termination A/E, claim counts |

Optionally the raw store (`exposure` + one claims parquet per benefit) is produced
by `experience generate --out <dir>`; pipelines may use either the precomputed A/E
tables or the raw store. **Hand pipelines the raw store for the hardest version;
the A/E tables are the easier version.**

### Ground truth
The ground truth is the **scenario manifest** (which control, which benefit, which
window, what magnitude, what type). It is *generated*, never hand-curated, so the
exam can scale to hundreds of scenarios for free.

---

## 2. Locked design decisions

These are the decisions already made. Implement them exactly.

1. **Three stages.** Stage 1 = zero-shot verdict (no code). Stage 2 = free-code
   pipeline (Option A: the LLM writes/runs arbitrary code). Stage 3 = MD report +
   human validation.
2. **Arbitrary code in Stage 2.** The harness executes model-written code in an
   isolated sandbox. A detector registry is provided only as an *optional
   importable library* — it is NOT a constraint. The LLM may write anything.
3. **Strict structured output contract.** Every submission must emit a
   pydantic-validated `Verdict` JSON. Anything malformed is rejected and scored as
   a miss. No prose answers, no exceptions.
4. **Strict train/eval separation.** `optimization` set (models may run, see scores,
   and iterate) is fully disjoint from the `heldout` set (mounted once, read-only,
   scored once, never fed back).
5. **N×K runs.** Each cell runs the LLM N times with identical input (N=3–5), and
   the final frozen pipeline K times (K=3) on identical data. Report median +
   spread.
6. **Two cheap baselines always reported:** the classical control-chart detector and
   the same model's Stage-1 zero-shot verdict. These decompose "bad code" from "bad
   judgment".
7. **Reproducibility pins.** Record seed, generator commit, model id/version,
   temperature/seed, code hash, and a run fingerprint for every cell.

---

## 3. Recommended folder structure

```
anomaly-benchmark/
├── README.md
├── pyproject.toml                 # Python >=3.11
├── config/
│   └── experiment.yaml            # scenarios, models, N/K, split, limits
├── src/abench/
│   ├── __init__.py
│   ├── manifest.py                # ScenarioManifest (ground truth)
│   ├── verdict.py                 # Verdict + DetectResult schemas (pydantic)
│   ├── datasets.py                # generate/load splits; strict separation
│   ├── detectors/                 # OPTIONAL importable registry
│   │   ├── __init__.py            # registry + uniform detect() interface
│   │   ├── statistical.py         # control chart, CUSUM, change-point
│   │   └── ml.py                  # isolation forest, LOF, OCSVM, autoencoder
│   ├── scoring.py                 # precision/recall, window IoU, type acc, FP, magnitude err
│   ├── runner.py                  # SANDBOXED arbitrary-code runner
│   ├── orchestrator.py            # stages 1-3, N×K loop, iteration, freeze/hash
│   ├── llm_client.py              # pluggable LLM adapter (OpenAI-compatible)
│   ├── report.py                  # Stage 3: charts + tables -> report.md
│   └── cli.py                     # abench <init|generate|run|score|report|validate>
├── data/
│   ├── raw/                       # generated scenario stores (gitignored)
│   └── split/
│       ├── optimization/          # data handed to models for iteration
│       ├── heldout/               # data mounted ONCE for final scoring
│       └── manifests/             # ground truth — ONLY the scorer reads this
├── submissions/                   # frozen model pipelines (content-hashed)
├── results/
│   └── <run-id>/
│       ├── verdicts.jsonl
│       ├── scores.json
│       ├── leaderboard.json
│       └── reports/*.md
└── human_review/
    ├── queue.jsonl                # anomalies queued for human review
    └── annotations.jsonl          # human TP/FP/missed/boundary labels
```

Dependencies (keep minimal): `pydantic>=2`, `numpy`, `pandas`, `matplotlib`,
`pyyaml`. `scikit-learn` only for the optional `ml.py` registry — make it an
optional extra so the core runs without it.

---

## 4. Core schemas (implement first, exactly)

### 4.1 `ScenarioManifest` (ground truth — scorer-only)

```python
from pydantic import BaseModel, Field

class ControlType(str, Enum):
    DRIFT = "drift"
    SHOCK = "shock"
    VOLATILITY = "volatility"
    IP_RECOVERY = "ip_recovery"
    NONE = "none"

class ScenarioManifest(BaseModel):
    scenario_id: str
    benefit: str | None            # None when no_op / all-benefit noise
    control_type: ControlType
    window: tuple[int, int] | None # inclusive years; None for full-period/neutral
    factor: float                  # slope, multiplier, sigma, or recovery factor
    signature: dict                # {direction: "increase|decrease|none", magnitude: str}
    benefit_lines_untouched: list[str]   # benefits the control must NOT affect
    no_op: bool                    # True for baseline/neutral scenarios
```

### 4.2 `Verdict` (what every model/submission must emit)

```python
class AnomalyClaim(BaseModel):
    benefit: str
    metric: str                    # "A/E incidence" | "A/E termination" | "claim counts" | ...
    window: tuple[int, int] | None # years; None = full period
    direction: str                 # "increase" | "decrease" | "dispersion" | "none"
    magnitude: str                 # free-text but bounded, e.g. "~+0.10/yr"
    type: ControlType              # model's guess at the control type
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]            # short, human-checkable: "ae_death_by_year.csv 2018-2024 rising"

class Verdict(BaseModel):
    scenario_id: str
    anomalies: list[AnomalyClaim] = []
    no_op: bool = False            # model claims "no anomaly / baseline"
```

**Contract rules (enforced by the harness):**
- `scenario_id` must match the scenario being scored.
- `anomalies` must be deduplicated (no two claims for the same benefit+window+type).
- Empty `anomalies` requires `no_op=True`.
- Unknown enum value → validation error → scored as a miss (do not silently coerce).

### 4.3 `DetectResult` (uniform interface for the optional registry)

```python
class DetectResult(BaseModel):
    verdict: Verdict
    point_scores: list[dict] | None = None   # optional per-row scores for charting
```

The registry exposes one function per detector:
`detect(data_paths: dict, params: dict) -> DetectResult`.
The LLM may import and call these, or ignore them entirely.

---

## 5. Stage 0 — Data generation and split (no LLM)

### 5.1 Generate scenarios
Reuse the generator rather than reimplementing it:

- **Option 1 (preferred):** run the generator's CLI as a subprocess:
  `experience generate --preset <p> --out data/raw/<scenario>` or the full
  `python scripts/run_scenario_verification.py` for the 6 canonical scenarios.
- **Option 2:** import the generator as a library (`pip install -e <generator path>`)
  and call its pipeline API directly.

For the **heldout set**, mint NEW scenarios (new windows/magnitudes/seeds) that
did not appear in optimization, so a pipeline cannot have memorized them. The
generator's determinism means "same scenario id = same data"; "new scenario id" =
fresh, unseen data.

### 5.2 Split rules (hard requirements)
- `optimization` and `heldout` are disjoint by `scenario_id` **and** by
  (benefit × control window × factor) where possible.
- **Manifests live in the scorer-only truth store (`data/truth/manifests/`)
  only**, keyed by *opaque* scenario ids (`sc-<6hex>`, frozen in
  `data/truth/id_map.csv`). The model-facing eval workspace
  (`data/eval/{optimization,heldout}/`) contains only CSV/PNG artifacts under
  opaque dir names — never the manifest, never a descriptive scenario name.
- Record a content hash of every model-facing input so you can *prove* all models
  saw identical data (fairness audit): `data/eval/dataset.json`. `data/truth/seal.json`
  is a sha256 commitment to the whole truth store, published before runs, so answers
  provably cannot be edited after scoring.
- Assembly is gated by a byte-level leak scan (`scripts/leakcheck.py`): any
  answer-bearing token in the model-facing tree fails the build; experiment
  runners re-check before sending a single byte to a model.

### 5.3 Starter scenario set
At minimum ship these (from the canonical verification run) plus fresh heldout
variants:

| Scenario | Control | Expected observable signature |
|---|---|---|
| `baseline` | none | all A/E ≈ 1.0 (noise only) |
| `drift_death_up_2018_2024` | drift +0.10/yr | Death A/E rises ~0.74 → 1.30 in window |
| `shock_covid_2020_2022` | shock ×1.5 | Death A/E spike 1.31/1.34/1.25 exactly in 2020–22 |
| `volatility_ip_sigma_03` | volatility σ=0.3 | IP annual-count variance ×3, level unchanged |
| `ip_recovery_mental_health_x2` | ip_recovery ×2.0 | MH termination A/E ≈ 2.0, incidence untouched |
| `noop_neutral_controls` | all neutral | bit-identical to baseline |

Add harder variants: smaller drift (0.05), smaller shock (×1.2), narrower windows,
σ=0.15, and mixed-benefit scenarios (e.g. drift on Death + shock on CI).

---

## 6. Stage 1 — Zero-shot baseline (no code)

**Goal:** measure detection without a pipeline.

- **Input to the model:** the scenario's artifact paths + a prompt stating the task,
  the `Verdict` schema, and the scoring rubric. (Give summaries of CSV contents or
  the file paths — do NOT hand the raw parquet unless the model can read it.)
- **Output:** a `Verdict` JSON.
- **No code execution.** The harness only validates + scores the JSON.
- **N runs** with identical input; report median + spread.
- Score against **both** sets: optimization (for Stage-2 feedback) and heldout (for
  the leaderboard).

The Stage-1 verdict is also the **feedback seed** for Stage 2 ("here is what you
missed in your zero-shot attempt").

---

## 7. Stage 2 — Free-code pipeline (the core)

This is the heart of the benchmark and the riskiest part. Implement the loop below
**exactly**; every guard is there for a reason.

### 7.1 Per-cell execution loop

For each (model, scenario-set) cell, run the whole loop **N times** with a fresh
LLM context (same input):

1. **Prompt the model** with:
   - task spec ("build a detector pipeline for trend anomalies in claims experience
     data"),
   - the `Verdict` schema + scoring rubric,
   - the **optimization-set** data paths (no manifests),
   - the optional detector-registry import path,
   - its **Stage-1 misses** (optimization set only — never heldout),
   - a requirement to **declare a seed**.
2. **Model emits code** (a self-contained program; default Python, but the runner
   may allow any installed runtime).
3. **Harness executes** the code in the sandbox (Section 7.3) against the
   optimization set.
4. **Harness validates + scores** the emitted verdicts (Section 8).
5. **Model sees** the score + missed anomalies, and iterates (improve the code).
   **Cap iterations at 3–5** and record the iteration count as an effort metric.
6. **Freeze:** hash the final code (`submissions/<hash>/`), record the seed and
   provenance.
7. **Run the frozen pipeline K times** on the optimization set (execution-variance
   spread) and **exactly once** on the **heldout set** (mounted read-only, no
   feedback). The heldout score is the only number on the leaderboard.

### 7.2 Code contract for submissions

Every submission must:
- accept input paths via `argv` or env vars (the harness passes `DATA_DIR` and
  `OUT_DIR`),
- write **one `verdict.json` per scenario** (or a single `verdicts.jsonl`) to
  `OUT_DIR`,
- declare its RNG seed (recorded, not necessarily trusted),
- make **no network calls** (blocked anyway),
- terminate within the timeout.

The harness validates verdict JSON with the pydantic schema; malformed = miss.

### 7.3 Sandboxed runner (`runner.py`) — do not skip

Security and fairness require isolation. Implement in two tiers:

**Tier 1 (subprocess, works everywhere):**
- run in a fresh temp `cwd`,
- `resource.setrlimit` for CPU time, address space (memory), file size,
- wall-clock timeout via a watchdog,
- read-only mount of the data dir (chmod/ro + path check), write-only `OUT_DIR`,
- block network: on Linux use `unshare -n` (new network namespace with no device),
  or a thin socket-intercept; on macOS/Windows this is weaker — document it.

**Tier 2 (container, recommended for real runs):**
- Docker/Podman with `--network none`, read-only data volume, `--cpus`, `--memory`,
  `--pids-limit`, non-root user, no host mounts beyond the two data dirs.

Record which tier was used; the leaderboard must say so.

**Hard limits to start with:** 120 s timeout, 2 GB memory, 1 CPU, 10 MB output.

### 7.4 The "optimize based on what was missed" feedback (leakage guard)

The feedback to the model may contain **only optimization-set** results. The
heldout set is:
- generated before any model runs,
- never referenced in any prompt,
- mounted at freeze-time only,
- scored once and never re-scored for the same pipeline.

The **optimization-vs-heldout score gap is itself a reported metric** — it is your
overfitting/autonomy-danger signal.

---

## 8. Scoring (`scoring.py`)

### 8.1 Match verdict claims to ground truth
For each scenario:
- If `manifest.no_op` and `verdict.no_op` → correct no-op (1 point).
- Else, greedily match each `AnomalyClaim` to the manifest's injected anomaly by
  `benefit` + control-type + window overlap.

### 8.2 Metrics
- **Detection:** precision, recall, F1 (per scenario, aggregated).
- **Window IoU:** `intersection / union` of predicted vs true year window (penalizes
  vague "everything" windows).
- **Type accuracy:** fraction of claims with correct `control_type`.
- **Magnitude error:** normalized error vs `factor` (where comparable).
- **False-positive rate:** spurious claims on `no_op`/baseline scenarios.
- **No-op correctness:** rate of correctly identifying baseline scenarios.

### 8.3 Effort/autonomy metrics (for the thesis)
Record per cell: total tokens, wall-clock, iteration count, code length, and
**human interventions** (from Stage 3). Report these beside accuracy — a model that
matches the classical baseline only after 5 iterations + heavy orchestration is a
different result than one that matches it in one zero-shot pass.

### 8.4 Baselines always shown
- **Classical control-chart detector:** z-score on `AE` column with a known-noise
  threshold (~ `k / sqrt(target)`) + CUSUM for drift/shock. This is the honest floor.
- **Stage-1 zero-shot** of the same model.
- **Random / all-baseline** trivial baselines for calibration.

---

## 9. Stage 3 — Markdown report + human validation

### 9.1 Report generation (`report.py`)
For each (model × scenario × stage), produce a `report.md` containing:
- scenario name and control summary (ground truth revealed here),
- charts (matplotlib, from the generator's CSVs or the model's `point_scores`),
- the data table behind each chart,
- the model's verdict claims (with its stated `evidence`),
- the score vs ground truth,
- a clear **"Human review"** section per anomaly.

Use a deterministic template so reports are diffable across runs.

### 9.2 Human validation flow
1. **Blind pass:** a reviewer sees the report's charts + the model's claims, and
   labels each `AnomalyClaim` as `TP | FP | boundary`, and flags `missed` anomalies
   they notice. Ground truth is NOT shown during this pass (avoids anchoring).
2. **Adjudication:** reveal ground truth only for disagreements and boundaries; the
   reviewer records a final label + a short note.
3. **Storage:** write `human_review/annotations.jsonl` (one row per anomaly:
   scenario_id, model, claim index, label, note, reviewer id, timestamp).
4. **Golden set:** human-corrected labels accumulate into a curated evaluation set;
   over time you can measure model-vs-human agreement (and spot hallucinated
   "evidence").

Implementation: keep it a thin loop (CSV/JSON) first; a Streamlit page is an
optional later upgrade. Do NOT put validation UI in the benchmark core.

---

## 10. Configuration and CLI

### 10.1 `config/experiment.yaml`

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
  output_bytes: 10485760
  sandbox: subprocess    # or container

models:
  - id: deepseek-v4-flash
    provider: deepseek-official
    temperature: 0.0      # or a fixed value; record it
    seed: 1234            # per-run seed rotation
  - id: qwen3.8-27b
    provider: lm-studio
    base_url: http://192.168.1.59:1234/v1
```

### 10.2 CLI

```
abench init                  # write config + folder skeleton
abench generate              # stage 0: produce + split scenarios
abench run --stage 1 --model all
abench run --stage 2 --model deepseek-v4-flash
abench score --run-id <id>
abench report --run-id <id> # stage 3
abench validate              # schema + split-separation self-checks
```

`llm_client.py` should be a thin OpenAI-compatible adapter (same shape as the
generator's own LLM usage) so any OpenAI-compatible endpoint works; make it
swappable per model in config.

---

## 11. Reproducibility & fairness rules (checklist)

- [ ] Pin generator seed and record its commit/version.
- [ ] Record model id, provider, `temperature`, and per-run seed.
- [ ] Hash the frozen pipeline code; store in `submissions/<hash>/`.
- [ ] Record a run fingerprint (config hash + data hashes + model + time).
- [ ] Prove identical inputs across models via content hashes of model-facing dirs.
- [ ] Report N×K as median + spread (never a single best run).
- [ ] Never feed heldout results back to any model.
- [ ] State sandbox tier in the leaderboard.

---

## 12. Acceptance criteria / test plan

### Unit tests
- `Verdict` schema rejects malformed JSON (bad enum, no_op mismatch, duplicate claims).
- Scorer produces expected precision/recall/IoU on hand-built cases.
- Split generation guarantees no overlap between optimization and heldout.
- Sandbox: blocks network, enforces timeout, enforces read-only data / write-only out.

### Integration test (end-to-end smoke)
Run a 2-scenario, 1-model pipeline (a hand-written "model" that emits a fixed
verdict) and verify: scenarios generated → split created → verdicts validated →
scored → `report.md` produced → human-review queue written.

### Fairness test
Two model configs pointed at the same run receive **byte-identical** model-facing
inputs (assert content hashes equal).

### Baseline sanity
The classical control-chart detector must detect `drift` and `shock` scenarios
(recall ≥ 1 on the canonical set) and must NOT fire on `baseline`/`noop` — this
proves the signal is present and the detector floor is sane.

---

## 13. Milestones (implement in this order)

- **M0 — Skeleton + deterministic core (no LLM, no sandbox).** `manifest.py`,
  `verdict.py`, `datasets.py`, `scoring.py`, a hand-written classical detector, a
  stub "model" emitting fixed verdicts, `report.py`. Goal: full pipeline works
  end-to-end with zero LLM and zero arbitrary code.
- **M1 — Sandboxed runner.** `runner.py` Tier 1 + one real LLM emitting code for
  Stage 2 against the optimization set only.
- **M2 — N×K + heldout + leaderboard.** Freeze/hash, execution variance, disjoint
  heldout, `leaderboard.json`.
- **M3 — Stage 1 baseline + Stage 3 validation.** Zero-shot prompt, report
  generation, human-review queue + annotations.
- **M4 — Multi-model + architecture axis + polish.** Run ≥2 models, optionally two
  topologies (orchestrated vs autonomous), cost metrics, docs.

---

## 14. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Arbitrary code executes harmfully | Container + `--network none`, resource caps, non-root, no host mounts |
| Model overfits/cheats via leakage | Strict optimization/holdout split, scorer-only manifests, hash audit |
| LLM non-determinism | N runs × K execs, fixed temperature/seed where possible, median+spread |
| Cost explosion | Iteration + token caps, classical-baseline gate before expensive runs |
| Unfair comparison | Identical inputs (hashed), one scoring rubric, same sandbox tier |
| Sandbox weaker on macOS/Windows | Default to container tier; record tier in results |

---

## 15. Appendix — example prompts and artifacts

### 15.1 Stage-1 prompt (abridged)

```
You are an actuary. Given the scenario artifacts at {DATA_DIR}, produce a JSON
object matching this schema: {VERDICT_SCHEMA}. Detect trend anomalies (drift,
shock, volatility, recovery) in Death/CI/TPD/IP A/E experience. Baseline A/E is
1.0 with Poisson noise ~1/sqrt(target). Return ONLY the JSON. Do not write code.
```

### 15.2 Stage-2 prompt (abridged)

```
Build a detector pipeline. You may write and run any code. Inputs: {DATA_DIR}
(read-only). Output: write verdict.json per scenario to {OUT_DIR} matching
{VERDICT_SCHEMA}. You may import the optional registry at {REGISTRY}. Declare a
seed. You may iterate up to {MAX_ITER} times; after each run you will see your
score and missed anomalies on the OPTIMIZATION set only. Do not attempt network
access. Here is what your Stage-1 attempt missed: {STAGE1_MISSES}.
```

### 15.3 Example manifest / verdict pair

```json
// manifest (scorer-only)
{"scenario_id": "drift_death_up_2018_2024", "benefit": "Death",
 "control_type": "drift", "window": [2018, 2024], "factor": 0.10,
 "signature": {"direction": "increase", "magnitude": "~+0.10/yr"},
 "benefit_lines_untouched": ["CI", "TPD", "IP"], "no_op": false}

// verdict (model output)
{"scenario_id": "drift_death_up_2018_2024",
 "anomalies": [{"benefit": "Death", "metric": "A/E incidence",
   "window": [2018, 2024], "direction": "increase", "magnitude": "~+0.10/yr",
   "type": "drift", "confidence": 0.95,
   "evidence": ["ae_death_by_year.csv: AE rises 0.74 to 1.30 across 2018-2024"]}],
 "no_op": false}
```

---

*End of guide.* The M0 milestone is the recommended starting point — it proves the
scoring and split machinery with a deterministic, hand-written "model" before any
LLM or sandbox complexity is introduced.
