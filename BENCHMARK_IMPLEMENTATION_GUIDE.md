# Anomaly-Detection Benchmark — Implementation Guide

> **Audience:** an LLM (or engineer) implementing this from scratch in a NEW folder.
>
> **Purpose:** a controlled, repeatable sandbox that does three things. It lets different AI
> models build their own pipeline to detect trend anomalies in synthetic life-insurance
> experience data. It compares models and architectures on an objective leaderboard. And it
> produces a Markdown report a human can validate.
>
> **Source data:** the "Synthetic Life Insurance Experience Data Generator" repo
> — [jasonzheshiou/Synthetic_Life_Insurance_Data_Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)
> (pure-Python, deterministic, seed=42). This benchmark is a separate project that consumes
> that generator's outputs.

---

## 0·A Status of this guide — read this before implementing anything

**This is the plan as written before the first experiment ran.** The plan is kept as it was,
with status notes added rather than rewrites, so you can still see the gap between intention
and outcome. For what was built and what was measured, read
[README.md](README.md) (purpose and status),
[docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md) (everything, with paths) and
[docs/REPORT_qwen36_vs_qwen38.md](docs/REPORT_qwen36_vs_qwen38.md) (the findings).

**Built, and used for every published number**

| guide section | what shipped |
|---|---|
| §1 domain background | correct as written — A/E ≈ 1.0 baseline, four benefit lines, Poisson noise ~ 1/√target |
| §2.4 strict split, §5.2 ZONE A / ZONE B | exactly as specified: opaque ids in `data/eval/`, manifests in `data/truth/`, `dataset.json` + `seal.json`, `scripts/leakcheck.py` |
| §2.3 structured verdict, malformed = miss | `findings` JSON + scorer v3 strict matching; added `strict=False` tolerance for raw control characters |
| §2.7 reproducibility pins | stronger than specified: every corpus carries `harness_snapshot/` + `MANIFEST.txt` with the full sha256 of pack, runner and prompt |
| §8 scoring | accuracy (strict hits / units) + FP/claim, on a unit = control × run ledger, with book-wide controls expanded per benefit line |

**Built differently than specified**

| guide section | specified | what was built |
|---|---|---|
| §6–7 Stage 1 + Stage 2 | multi-turn free-code pipeline building, ≤5 iterations, frozen submission | **one turn**, with up to 4 sandboxed python *analysis* calls and a deterministic evidence pack. Multi-turn pipeline construction was never built. |
| §3, §10 packaging | `src/abench/` package + `abench` CLI + `pyproject.toml` | flat `scripts/` modules. No package, no CLI, no install step. |
| §4.1–4.2 schemas | pydantic `ScenarioManifest` / `Verdict` classes | JSON manifests + a plain-dict scorer; pydantic is not in the loop |
| §5.3 starter set | 6 canonical scenarios + heldout variants | 47 books in 8 families (`config/scenarios.yaml`), see [docs/scenario-catalog.md](docs/scenario-catalog.md) |
| §7.4 iteration feedback | scores fed back to the *subject* model on the optimization set | feedback consumed by the **operator-side harness author** instead. The subject gets one cold turn per book. |
| §8.3 effort metrics | tokens, wall-clock, iterations, code length, human interventions | tokens and wall-clock per run. Iteration and human-intervention counters never existed. |

**Never built**: §7.3 sandbox tiers (what runs is `python -I -c`, 10 s, 4 000-char cap —
**no rlimits, no network block, no filesystem jail**: advisory only); §8.2 window IoU and
magnitude error; §2.5 N×K median + spread (runs were summed, not summarised); §8.4 the
classical control-chart baseline; §9 Stage-3 report and blind human validation; §12
acceptance tests beyond the registry invariants.

### What the study found, and what it does to the thesis

The answer to the thesis in §0 ("does the best architecture around a model change as the
model changes?") is **yes** — and the evidence is cleaner than expected, because both
subjects had the same size and architecture and differed only in behaviour learned by
reinforcement:

- Each model did best with the harness tuned **for it**: 3.8 got 71.2 % on its own harness
  and 70.3 % on 3.6's; 3.6 got 65.8 % on its own and 64.9 % on 3.8's. A harness is
  per-model equipment, not portable equipment.
- The same harness gave 3.8 **+23.8 points of precision** (34.3 % → 58.1 %) and 3.6
  **+1.3 points** (60.0 % → 61.3 %). The models fail differently: 3.8 claims too much (31
  of 69 false alarms were invented rather than mislabelled), 3.6 holds back.
- Behaviour decided whether a harness feature existed at all. The offered tool was used in
  about 24 % of 3.8's runs and **0 of 144** of 3.6's.
- The optimization-vs-heldout gap that §7.4 predicted came out at **about 30 points for
  both models** (3.8: 97.7 → 69.1; 3.6: 95.5 → 64.2, both on the full held-out split).
- §0 asked for **cost recorded beside accuracy**. Wall-clock and tokens were, iterations and
  human interventions were not. It changed the conclusion instead of decorating it: 3.6
  reached about 93 % of 3.8's held-out accuracy at about a third of the time and tokens,
  with better precision, so cost is part of the ranking argument.

If you implement this from scratch today, treat §11 and §5.2 as the parts that earned their
cost, and treat Stage 2 as an open extension rather than a task.

---

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

> **Answer, as measured (see §0·A).** Yes — and the effect survives holding architecture
> constant. Both subjects are 27 B models on one endpoint with identical samplers; the
> difference between them is behaviour learned by reinforcement, not design. Each model
> scored best with the harness tuned for it, and the same harness bought one model
> +23.8 points of precision and the other +1.3. The orchestration-vs-autonomous axis
> itself was never tested (Stage 2 was dropped); what was tested instead was narrower and
> more useful: **harness transfer between models with different behaviours.**

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

> **What actually shipped.** Each published book (`data/eval/<split>/<sc-xxxxxx>/`) holds
> 34 files, 29 of them in the repo:
> `artifacts/ae_<benefit>_by_year.csv|.png`,
> `artifacts/ae_<benefit>_age_gender.csv|.png`, `artifacts/ae_<benefit>.csv`,
> `artifacts/ae_ip_termination.csv`, `artifacts/ae_ip_termination_by_month.csv|.png`,
> `artifacts/summary.json`, `artifacts/scenario_id.txt`, top-level `<Benefit>.csv`
> per benefit, plus the excluded bulk files (`exposure.csv`, `<benefit>_claims.csv`). The raw
> store keeps **both** `.csv` and `.parquet` per table plus `metadata.json`, in
> `data/raw/<id>/store/` alongside `run_info.json` — none of it published. Note that the
> model-facing prompt **lists every file in the scenario directory**, so which files exist
> is part of the prompt (see the clone caveat in the README).

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

> **What actually shipped.** No pydantic model was built. The contract is written as prose in
> the pinned system prompt, and asks for this shape:
>
> ```json
> {"scenario_id": "<given id>",
>  "overall_assessment": "clean" | "anomalies",
>  "findings": [{"benefit": "Death|CI|TPD|IP",
>                "years": [start, end] | null,
>                "pattern": "drift|shock|volatility|recovery|other",
>                "direction": "increase|decrease|dispersion",
>                "magnitude": "free text", "confidence": 0.0-1.0,
>                "evidence": ["checkable pointers"],
>                "recommended_action": "what to do next"}]}
> ```
>
> Two differences from the design are worth keeping. `overall_assessment` forces an explicit
> `clean` answer, and `recommended_action` asks for the actuarial follow-up — that is what
> makes the answer an *insight* instead of a labelled pattern. The scorer ignores
> `recommended_action` and `confidence`.
>
> Unparseable JSON scores as a miss, with one tolerated exception: the parser uses
> `json.loads(..., strict=False)`, so a raw newline inside a string does not throw away an
> otherwise correct answer.

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

> **What was done.** Option 2, through `scripts/generate_scenarios.py`. It imports the
> generator as a library from a **sibling directory** named
> `Life_insurance_data_generator_new`, hard-coded as `GEN_ROOT` with no override flag. Clone
> [Synthetic_Life_Insurance_Data_Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)
> under that directory name. Scale presets live in `config/scenarios.yaml`. The published
> corpus is `--scale full` (250 000 policies, seed 42, generator commit `66a73d0`).
> Step-by-step instructions:
> [README § Where the data comes from](README.md#-where-the-data-comes-from-and-how-to-generate-it-yourself).

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

> ⚠️ **Status: not implemented as written.** What runs today is
> `run_sandboxed_python()` in `scripts/run_zero_shot.py`: `python -I -c <code>`, `cwd` set to
> the scenario's `artifacts/`, a 10 s timeout and a 4 000-char output cap. There is **no
> `setrlimit`, no network block and no filesystem jail** — not Tier 1, not Tier 2. This was
> tested directly: model-authored code could read files outside the workspace and list the
> truth manifests. All 97 tool calls recorded in the two campaigns stayed inside
> `artifacts/`, but that was the model choosing to. "Never read outside `artifacts/`" is a
> line in the rules text, not a control. If you build this for real, implement this section
> before running anything you do not trust.

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

> **Status: this file was never created.** Configuration ended up split three ways: the
> scenario registry in `config/scenarios.yaml` (scale presets, 47 books, split); sampler and
> endpoint settings as command-line flags to `scripts/run_zero_shot.py` and
> `run_zero_shot_baseline_v2.py`; harness behaviour fixed in code plus a pinned system-prompt
> file in `data/prompts/`. The block below is the original design, kept for reference. For
> what actually ran in a given corpus, read that corpus's `harness_snapshot/MANIFEST.txt`.

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

What actually produced every published number:

- **Subjects**: `Qwen3.6-27B` and `Qwen3.8-27B-Q8_0`, served by **llama.cpp** at
  `http://192.168.1.59:8080/v1`, **one slot** (one generation at a time).
- **Sampling**: temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, streaming, and
  `max_tokens` never set.
- **Harness author**: neither subject. The operator-side agent that built the harness ran on
  DeepSeek V4.1 Flash, a third model, so no subject tuned the exam it sat.

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

> **Status:** one item from this plan has an automated test — split generation, in
> `tests/test_registry.py` (split disjointness, manifest contract, scale presets; all
> passing). `stats_pack.py`, `score_xam.py`, `harness_gate.py` and `leakcheck.py` have **no
> unit tests**. Their correctness rests on the runtime preflight gate, the freeze gate, and
> diffing all 23 regenerated optimization packs after any change. The sandbox,
> integration-smoke and baseline-sanity tests below were never written, and the classical
> detector they depend on does not exist.

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

> **Status: no milestone was delivered as packaged.** Work arrived out of order and as flat
> scripts. The deterministic data + split + scoring core was built first (the substance of
> M0) and then bypassed: Stage 2 (M1–M2) was dropped in favour of a single-turn evidence-pack
> harness, and the M3 report/validation loop and M0 packaging were never done. The campaigns
> then invented something this guide did not plan for, and it deserves its own milestone:
> **an agent that iterates the harness against optimization-set evidence.** Read the table
> as history plus intent; read the "actual" column as what you can reuse.

| Milestone | Planned | Actual |
|---|---|---|
| **M0** skeleton + deterministic core, no LLM/sandbox | `manifest.py`, `verdict.py`, `datasets.py`, `scoring.py`, classical detector, stub model, `report.py` | ✅ substance, no packaging: `generate_scenarios.py` + `score_xam.py` + registry + tests. ❌ classical detector, stub model, `report.py` |
| **M1** sandboxed runner + one real LLM writing code | `runner.py` Tier 1, Stage 2 against optimization | ⚠️ replaced: `run_sandboxed_python()` (advisory, §7.3) used for *analysis*, not pipeline construction |
| **M2** N×K + heldout + leaderboard | freeze/hash, execution variance, `leaderboard.json` | ⚠️ partial: freeze/hash is strong (`harness_snapshot/`) and the held-out split was used exactly once; ❌ median+spread, `leaderboard.json` |
| **M3** Stage 1 baseline + Stage 3 validation | zero-shot prompt, report, human-review queue | ✅ Stage 1 is the entire measured surface (`xam_*` corpora). ❌ reports, human review |
| **M4** multi-model + architecture axis + polish | ≥2 models, two topologies, cost metrics, docs | ✅ exceeded in substance: two models × two harnesses on one endpoint, cost analysis in the report, four docs. ❌ the orchestrated-vs-autonomous topology axis |

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

> **Status: illustrative. These are not the prompts that ran.** The real ones are archived
> as artifacts and are far longer than these sketches:
>
> - the system prompt is a file in `data/prompts/` — 3 053 characters for the baseline line,
>   3 866 for the harness-era line;
> - the taxonomy and discipline clauses live in `HARNESS_RULES` inside
>   `scripts/run_zero_shot.py`;
> - the model also receives a deterministic evidence pack for each book.
>
> The exact bytes behind any published number are in that corpus's `harness_snapshot/`, and
> `results/<corpus>/prompts/*.md` holds one fully rendered prompt per scenario.

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
