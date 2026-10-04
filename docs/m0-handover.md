# M0 Handover Plan — Deterministic Arena Core

> **Audience:** the next LLM/engineer implementing milestone **M0** of
> `BENCHMARK_IMPLEMENTATION_GUIDE.md` (§13) in this repository.
> **Read this whole file first.** It pins the current state and the exact
> contracts; the guide is the strategy, this file is the tactical spec.

---

## 1. Current state (do NOT re-derive any of this)

- **Working dir:** `/mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena`
- **Sibling generator:** `../Life_insurance_data_generator_new` (do not modify it
  further; its interpreter has the data deps). Generator commit recorded in the
  data: **`66a73d0`**.
- **Python:** system `python3` = **3.14.4**; sibling venv
  `../Life_insurance_data_generator_new/.venv/bin/python` is also 3.14.4 and has
  `pydantic 2.13.4`, `numpy 2.5.2`, `pandas 3.0.5`, `matplotlib`, `pyyaml`.
  There is **no** `.venv`, `pyproject.toml`, or `src/` in this repo yet.
- **No git repo** at this folder (`git status` → "not a git repository"). Treat
  provenance as already captured inside the data files, not git.
- **The dataset is DONE (Stage 0).** Do not regenerate it unless asked.
  Rebuilt in the **leak-free layout** (opaque ids; old `data/split/` removed):
  - `data/eval/optimization/` — 23 scenario dirs `sc-<6hex>` (model-facing, ZONE A)
  - `data/eval/heldout/` — 24 scenario dirs `sc-<6hex>` (model-facing, ZONE A)
  - `data/eval/dataset.json` — sha256 of all 1598 model-facing files (opaque
    paths) + truth seal
  - `data/truth/manifests/` — 47 `sc-<6hex>.json` ground-truth files (ZONE B,
    scorer-only; contain `eval_id` + `descriptive_id`)
  - `data/truth/id_map.csv` — FROZEN opaque↔descriptive mapping (+family/split);
    `id_key.json` seeds the id derivation; `seal.json` commits to everything
    (current seal `2deda876…`)
  - `data/truth/scenario_summary.json` — statuses (45 pass / 2 warn / 0 fail),
    fingerprint **`648dc18cbd8f88d6`**
  - `data/raw/<descriptive_id>/` — 47 full stores (with `metadata.json` = the
    injected controls; `run_info.json` = scale/seed/targets/generator commit)
  - `python3 scripts/leakcheck.py` re-verifies ZONE A byte-for-byte at any time.
- **Model-facing scenario dir contents** (identical shape in both splits):
  `{death,ci,tpd,ip}_claims.csv`, `exposure.csv`, `scenario_id.txt` (holds the
  **opaque** id), `benchmarks/{Death,CI,TPD,IP}.csv`, and `artifacts/` with
  `ae_<benefit>.csv`, `ae_<benefit>_by_year.csv`, `ae_<benefit>_age_gender.csv`,
  `ae_<benefit>_by_year.png`, `ae_<benefit>_age_gender.png`,
  `ae_ip_termination.csv`, `ae_ip_termination_by_month.csv/.png`, `summary.json`.
- **A/E tables are the primary scoring surface.** `ae_<benefit>_by_year.csv` has
  columns `Year, Actual, Expected, AE`; baseline AE ≈ 1.0 with Poisson noise
  `~1/sqrt(target)`. `ae_ip_termination.csv` has
  `Diagnosis, DurationMonth, Exposed, Recovered, ObservedRate, AssumedRate, AE`.

---

## 2. Scope — exactly M0 (guide §13)

> "Skeleton + deterministic core (no LLM, no sandbox): `manifest.py`,
> `verdict.py`, `datasets.py`, `scoring.py`, a hand-written classical detector,
> a stub 'model' emitting fixed verdicts, `report.py`. Goal: full pipeline works
> end-to-end with zero LLM and zero arbitrary code."

**In scope:** package skeleton + pyproject + CLI; manifest loader; Verdict
schema + validation; split loader + fairness-hash check; scorer; classical
control-chart detector (z-score + CUSUM); a deterministic stub "model"; the
deterministic Markdown report; `config/experiment.yaml`; unit + integration +
baseline-sanity tests. Run everything against the **existing** `data/eval`
(+ `data/truth` for the scorer).

**Out of scope (later milestones):** any LLM call (`llm_client.py`), sandboxed
arbitrary-code runner (`runner.py`), N×K loop / freeze-hash / leaderboard
(`orchestrator.py`, M2), Stage-1 zero-shot + Stage-3 human review queue (M3),
multi-model + cost metrics (M4).

---

## 3. Target file tree (add, do not move existing files)

```
data_pipeline_arena/
├── pyproject.toml                  # [project] + [project.scripts] abench = abench.cli:main
├── config/
│   └── experiment.yaml             # NEW: runs/split/limits/models (guide §10.1)
├── src/abench/
│   ├── __init__.py
│   ├── manifest.py                 # ground-truth schema + loader (read data/truth/manifests)
│   ├── verdict.py                  # Verdict + AnomalyClaim + validation
│   ├── datasets.py                 # split discovery, load, fairness-hash verify
│   ├── scoring.py                  # match + metrics
│   ├── detectors/
│   │   ├── __init__.py             # registry: uniform detect(data_paths, params)->DetectResult
│   │   └── classical.py            # control chart (z-score) + CUSUM
│   ├── stub_model.py               # deterministic fixed-verdict "model"
│   ├── report.py                   # report.md per (model × scenario)
│   └── cli.py                      # abench <init|generate|run|score|report|validate>
├── results/<run-id>/               # verdicts.jsonl, scores.json, reports/*.md
├── tests/
│   ├── test_verdict.py
│   ├── test_manifest.py
│   ├── test_scoring.py
│   ├── test_datasets.py
│   └── test_classical_baseline.py
```

`detectors/__init__.py` exposes a registry: a dict `{"classical": classical.detect}`.
`DetectResult` lives in `verdict.py` (guide §4.3): `{verdict: Verdict,
point_scores: list[dict] | None}`.

---

## 4. Ground-truth manifest schema (authoritative)

The manifests are **already richer** than guide §4.1. Implement the loader
against the real files (schema_version **1**), not the guide's simplified
single-field schema. Exact shape (verified against all 47 files):

```jsonc
{
  "schema_version": 1,
  "scenario_id": "drift_death_up_2018_2024",
  "family": "drift",                  // none|drift|shock|volatility|noise_trap|recovery|mixed|systemic
  "split": "optimization",            // optimization|heldout
  "scale": "full", "seed": 42, "n_policies": 250000,
  "targets": {"Death":5000,"CI":12000,"TPD":8000,"IP":15000},
  "study_window": [2015, 2024],
  "no_op": false,
  "controls": [
    {"type":"drift","benefit":"Death","window":[2018,2024],"factor":0.15,
     "signature":{"direction":"increase","magnitude":"+0.15/yr"}}
  ],
  "benefit_lines_untouched": ["CI","TPD","IP"],
  "primary": { /* flattened single-control form, or null */ }
}
```

**Control `type` values:** `drift`, `shock`, `volatility`, `ip_recovery` only.
`no_op`/`baseline`/`noop_neutral_controls` have `controls: []` and `no_op: true`.
The guide's `NONE` enum value is never a real control type.

**Field quirks the loader MUST normalize** (these are where bugs happen):

1. **`benefit` is polymorphic:**
   - `drift`, `volatility`: a single benefit name string, or `"all"`.
   - `shock`: a **list** of benefit names (e.g. `["Death","CI"]`), with `factor`
     a **dict** `{Benefit: float}`.
   - `ip_recovery`: a **list of diagnosis names** (`["Mental Health"]`,
     `["Mental Health","Musculoskeletal"]`), with `factor` a **dict**
     `{Diagnosis: float}`. **Here `benefit` means "diagnosis", not benefit.**
2. **`factor` is polymorphic:** float for `drift`/`volatility`; dict for
   `shock`/`ip_recovery`.
3. **`window`** is always a 2-element inclusive year list; `ip_recovery` and most
   `volatility` use the full study window `[2015,2024]`. Never `null` in practice
   (the guide's "None for full-period" is conceptual).
4. **`signature.direction`** ∈ `increase` | `decrease` | `dispersion`.
   - `drift`/`shock`: `increase` if factor > 1 (slope > 0), `decrease` otherwise.
   - `volatility`: always `dispersion`.
   - `ip_recovery`: `increase` if factor > 1 (faster recovery, shorter duration),
     `decrease` if factor < 1 (slower recovery, longer duration). Verified:
     `mental_health_x2` → increase; `cancer_x05` → decrease.
5. **`primary`** is non-null only for single-control scenarios (one control that
   affects exactly one benefit, or a single-benefit drift/volatility). It is the
   flattened form matching guide §4.1 (`control_type`, `benefit`, `window`,
   `factor`, `signature`, `benefit_lines_untouched`). Multi-control
   (`mixed`/`systemic`) and multi-benefit shocks have `primary: null`. The scorer
   must **always** use `controls`, never `primary`.
6. **`benefit_lines_untouched`** for `ip_recovery` lists `["Death","CI","TPD","IP"]`
   (all incidence lines) because recovery touches termination, not incidence.

**Loader requirements:** pydantic models for `Control` and `ScenarioManifest`
that accept the JSON above verbatim; a `load_manifest(path)` / `load_all(dir)`
returning typed objects; reject unknown `type`/`family`/`direction` loudly.

---

## 5. Verdict contract (guide §4.2 + one extension)

Implement `AnomalyClaim` + `Verdict` **exactly** as guide §4.2, with **one
documented, backward-compatible addition** required to express recovery:

```python
class AnomalyClaim(BaseModel):
    benefit: str                      # Death|CI|TPD|IP  (recovery claims still set IP)
    metric: str                       # "A/E incidence" | "A/E termination" | "claim counts" | ...
    window: tuple[int, int] | None
    direction: str                    # increase|decrease|dispersion|none
    magnitude: str
    type: ControlType                 # drift|shock|volatility|ip_recovery (+ NONE unused)
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = []
    diagnosis: str | None = None      # EXTENSION: set for ip_recovery (the diagnosis name)
```

Rationale: `ip_recovery` anomalies are keyed by **diagnosis**, which has no slot
in the guide schema; without `diagnosis` a recovery claim cannot be matched.
`benefit` stays `"IP"` and `metric` stays `"A/E termination"` for recovery.

**Validation rules (enforced, not coerced):**
- `scenario_id` must equal the scenario being scored.
- dedup by `(benefit, type, window, diagnosis)`; duplicates rejected.
- empty `anomalies` requires `no_op=True` (and vice-versa: `no_op=True` requires
  empty `anomalies`).
- unknown enum / direction → **pydantic ValidationError → scored as a miss**.
- `direction` must be a valid value; `none` is allowed only for `no_op` verdicts.

`DetectResult` (guide §4.3): `{verdict: Verdict, point_scores: list[dict] | None}`.

---

## 6. Scoring algorithm (`scoring.py`)

### 6.1 Decompose ground truth into atomic units

The scorer matches claims against **atomic units**, not raw `controls`. Decompose:

```
for control in manifest.controls:
    if control.type in {drift, volatility}:
        benefits = [control.benefit] if benefit != "all" else [Death,CI,TPD,IP]
        for b in benefits:
            unit(benefit=b, diagnosis=None, type=control.type,
                 window=control.window, factor=control.factor,
                 direction=control.signature.direction)
    if control.type == "shock":
        for b, f in control.factor.items():
            unit(benefit=b, diagnosis=None, type="shock",
                 window=control.window, factor=f,
                 direction=increase if f>1 else decrease)
    if control.type == "ip_recovery":
        for diag, f in control.factor.items():
            unit(benefit=None, diagnosis=diag, type="ip_recovery",
                 window=control.window, factor=f,
                 direction=increase if f>1 else decrease)
```

A `no_op` manifest yields zero units. This decomposition gives **partial credit**:
catching `Death ×1.5` but missing `CI ×0.6` in `sys_shock_inverse_2021_2022`
scores TP + FN, not all-or-nothing.

### 6.2 Match a claim to a unit (greedy)

For a non-`no_op` scenario, for each claim, try to match an unmatched unit in
this precedence, **all conditions must hold**:

1. `claim.type == unit.type`
2. benefit/diagnosis agree:
   - drift/shock/volatility: `claim.benefit == unit.benefit`
   - ip_recovery: `claim.diagnosis == unit.diagnosis` **and**
     `claim.metric == "A/E termination"`
3. window overlap: `claim.window` intersects `unit.window` (full-period units
   overlap everything). `window=None` on a claim = "full period" = overlaps all.
4. direction consistency: `claim.direction` must equal `unit.direction`, except
   `claim.direction == "none"` is never a match (it is not a real anomaly).

Greedy: sort claims by `-confidence`, assign each to the first matching unmatched
unit. A claim with no matching unit = **FP**. An unmatched unit = **FN**.

*Special case — inverse shocks:* `Death ×1.4` + `CI ×0.6` share a window; benefit
already disambiguates, and direction is the final guard (a `Death/decrease` claim
matches nothing → FP, not a wrong-benefit TP).

### 6.3 Metrics

Per scenario: `tp`, `fp`, `fn`, then **precision** `tp/(tp+fp)`,
**recall** `tp/(tp+fn)`, **F1**. Plus:

- **Window IoU** (matched pairs only): `|a∩b| / |a∪b|` on year sets; mean over
  matched pairs.
- **Type accuracy:** fraction of matched claims whose `type` was correct (this
  equals 1.0 by construction given rule 1 — record it anyway for the later
  relaxation where a claim of the wrong type but right benefit/window is
  penalized rather than unmatched).
- **Magnitude error** (comparable types only — drift/shock/volatility): for
  matched pairs, normalize the claim's `magnitude` string where parseable
  (e.g. `~+0.10/yr` → 0.10; `×1.5` → 1.5; `sigma=0.3` → 0.3); else skip. Error
  = `|pred − true| / (1 + |true|)`.
- **No-op correctness:** on `no_op` manifests, verdict is correct iff
  `no_op=True and not anomalies`. A claim on a `no_op` scenario is a FP.
- **FP rate:** spurious claims across all `no_op`/baseline scenarios.

Aggregate **micro** (sum tp/fp/fn across scenarios) and **macro** (mean per-scenario
precision/recall/F1) — report **separately for optimization and heldout**. The
optimization-vs-heldout gap is a first-class metric (overfitting signal).

`scores.json` shape: `{run_id, split_level: {optimization: {...}, heldout: {...}},
per_scenario: {<id>: {tp,fp,fn,precision,recall,f1,iou,type_acc,magnitude_err}}}`.

---

## 7. Classical detector (`detectors/classical.py`)

Implements the honest floor (guide §8.4 / §12). Signature:
`detect(data_paths: dict, params: dict) -> DetectResult`, where `data_paths` has
`by_year_csv` (per-benefit `ae_<b>_by_year.csv` paths), `termination_csv`
(`ae_ip_termination.csv`), etc.

**Algorithm (deterministic, no randomness):**

1. **Control chart (shock):** per benefit, per year, `z = (AE − 1) / noise_sigma`
   where `noise_sigma = k / sqrt(target[benefit])` (targets from the manifest;
   default `k` ≈ 2.5). A contiguous run of years with `|z| > threshold` and a
   consistent sign → a `shock` claim (window = the run, direction from sign,
   magnitude ≈ mean AE − 1).
2. **CUSUM (drift):** per benefit, cumulative-sum statistic over the AE series
   for a positive and a negative drift; a monotone slope over ≥3 years that
   exceeds the decision interval → a `drift` claim (window, direction, slope ≈
   least-squares fit of AE on year).
3. **Dispersion (volatility):** per benefit, rolling std of annual AE vs the
   baseline-noise level; a window where observed std ≫ expected noise → a
   `volatility` claim with `direction="dispersion"`. (Lower priority than
   shock/drift so noise-traps are labelled "dispersion" not "drift".)
4. **Recovery:** out of scope for the classical floor (do not attempt in M0).
5. Emit `no_op=True` only if **no** benefit produced any claim.

**Required baseline sanity (guide §12 — this is a hard test):**
- recall **≥ 1** (detect the injected control) on `drift_death_up_2018_2024` and
  `shock_covid_2020_2022` (type + benefit + overlapping window + direction).
- **zero** claims (no_op=True) on `baseline` and `noop_neutral_controls`.

**Stretch (non-blocking):** on `trap_noise_spike_lookalike` /
`trap_noise_drift_lookalike`, any claim must be `volatility` (direction
`dispersion`), never `drift`/`shock`. Log the result; a FP here does not fail M0,
but report it because it is exactly the hallucination the noise-traps exist to
measure.

---

## 8. Stub model (`stub_model.py`)

A deterministic, hand-written "model" that emits **fixed** verdicts (no data
reading needed beyond loading the manifest-derived scenario id — but it MUST not
read manifests; it reads only `scenario_id.txt`). Used by the M0 smoke test and
as a second "always-baseline" calibration row. Two variants:
- `fixed_omniscient`: emits the correct verdict for a small hard-coded map (used
  only to prove the scoring machinery in tests, never as a leaderboard row).
- `always_noop`: emits `no_op=True` for every scenario (the "random/all-baseline"
  trivial baseline from guide §8.4).

It writes one `verdict.json` per scenario (or `verdicts.jsonl`) to `OUT_DIR`,
matching the Stage-2 code contract (`DATA_DIR`/`OUT_DIR` via env/argv) so M1 can
drop a real pipeline into the same slot.

---

## 9. Report (`report.py`)

Deterministic template → `results/<run-id>/reports/<scenario_id>.md`:
scenario id + family, ground-truth summary (revealed here), the `ae_*_by_year`
table (markdown), the generator's PNG embedded or linked, the model's claims with
its `evidence`, per-claim match result (TP/FP/FN), and the scenario score. Use a
fixed template string so reports diff cleanly across runs. (Stage-3 human-review
queue is **M3** — do not build it now.)

---

## 10. CLI + config

`config/experiment.yaml` (guide §10.1), seeded from the actual data:
```yaml
generator: {path: ../Life_insurance_data_generator_new, seed: 42, commit: "66a73d0"}
split:    {root: data/eval, optimization: optimization, heldout: heldout}
truth:    {root: data/truth, manifests: manifests, id_map: id_map.csv}   # scorer-only
runs:     {llm_samples: 3, exec_samples: 3, max_iterations: 4}
limits:   {timeout_s: 120, memory_mb: 2048, cpu: 1, output_bytes: 10485760, sandbox: subprocess}
```

`abench` subcommands for M0 (guide §10.2), each a small function:
- `abench init` — idempotent: create `results/`, `submissions/`, `human_review/`,
  and `config/experiment.yaml` if missing. Do **not** touch `data/`.
- `abench generate` — M0: verify `data/eval` + `data/truth` exist and are
  complete; do not regenerate (warn + point to
  `scripts/generate_scenarios.py` if absent).
- `abench run --model classical|stub --split optimization|heldout` — run the
  chosen detector over the split's scenario dirs, write `verdicts.jsonl`.
- `abench score --run-id <id>` — load verdicts + manifests, write `scores.json`.
- `abench report --run-id <id>` — render `reports/*.md`.
- `abench validate` — run the self-checks in §12 (manifest parse, split
  separation, hash match).

---

## 11. `datasets.py`

- `discover(eval_root)` → list of `(eval_id, dir)` for optimization/heldout,
  reading `scenario_id.txt` and cross-checking it against the opaque dir name
  (both must match `sc-<6hex>`). Descriptive names only via
  `data/truth/id_map.csv`, scorer-side.
- `load_manifests(truth_root)` → `dict[eval_id, ScenarioManifest]` from
  `data/truth/manifests/`.
- `verify_hashes(eval_root)` → recompute sha256 of every file under
  `optimization/` + `heldout/` and compare to `data/eval/dataset.json`; return
  list of mismatches (empty = byte-identical inputs proven). Also assert
  `dataset.json.seal == data/truth/seal.json.sha256` (truth not edited after
  sealing). This is the fairness test hook.
- **Separation invariant:** assert every scenario dir has a manifest, and no
  scenario dir contains a `metadata.json`/parquet file (leakage guard —
  re-assert it, cheap). Optionally shell out to `scripts/leakcheck.py` for the
  full byte-level scan.

---

## 12. Tests (map guide §12 to concrete cases)

| Guide criterion | Test |
|---|---|
| Verdict rejects malformed JSON | `test_verdict.py`: bad enum, `no_op` mismatch, duplicate claims, `confidence` out of range, empty anomalies without `no_op` |
| Scorer produces expected P/R/IoU | `test_scoring.py`: hand-built manifest+verdict pairs — exact TP, partial credit (2-of-2 units), FP, FN, window IoU (0/partial/1), inverse-shock direction guard, recovery diagnosis match |
| Split generation guarantees no overlap | `test_datasets.py`: optimization ∩ heldout scenario ids = ∅; control signatures disjoint (reuse the key from the dataset pipeline); no manifest/parquet leaks; `scripts/leakcheck.py` exits 0 on `data/eval` |
| Fairness (byte-identical inputs) | `test_datasets.py::test_verify_hashes` passes against the real `data/eval/dataset.json` (and its seal matches `data/truth/seal.json`) |
| Baseline sanity | `test_classical_baseline.py`: recall ≥1 on `drift_death_up_2018_2024` + `shock_covid_2020_2022`; zero claims on `baseline` + `noop_neutral_controls` |
| Integration smoke | one test that runs: load real split → classical detector → verdicts.jsonl → score → report.md exists |

`test_registry.py` (the existing dataset test) must keep passing.

---

## 13. Implementation order + definition of done

1. `pyproject.toml` + `src/abench/` skeleton + `.venv` (or reuse sibling venv).
2. `verdict.py` (schemas + validation) — no data deps.
3. `manifest.py` (schemas + loader) — validate against all 47 real files.
4. `datasets.py` (discover + manifests + hash verify).
5. `scoring.py` (decompose + greedy match + metrics).
6. `detectors/classical.py`.
7. `stub_model.py`.
8. `report.py`.
9. `cli.py` + `config/experiment.yaml`.
10. tests (order above), run `pytest tests/`.

**Definition of done (M0 complete when all true):**
- `pytest tests/` green (including the 9 existing `test_registry.py` cases).
- `abench run --model classical --split heldout` then `abench score` +
  `abench report` produce `scores.json` + `reports/*.md` from the real 47-scenario
  split, with **zero errors** and the classical detector achieving the §12
  baseline sanity numbers.
- `abench validate` exits 0 (manifests parse, splits disjoint, hashes match).
- `docs/review-and-results.md` M0 row flipped to ✅ with the measured baseline
  numbers, and this handover file kept (or a short note added) for the M1 agent.

---

## 14. Decisions to make (recommended defaults)

1. **Venv:** create a dedicated `.venv` (clean, `pip install -e ".[dev]"`). Fast
   path: reuse `../Life_insurance_data_generator_new/.venv/bin/python` (already
   has all core deps). Either is fine; record which in the README.
2. **`diagnosis` field on `AnomalyClaim`:** adopt the §5 extension (default
   recommended) — it is the minimal change that makes `ip_recovery` matchable.
   Do **not** overload `benefit` with diagnosis names.
3. **Volatility "all" claims:** models emit per-benefit `volatility` claims
   (benefit = a specific line). The classical detector emits up to 4. A claim
   with `benefit="all"` is treated as **not matchable** (FP) unless you
   explicitly add all-benefit matching later; keep it strict.
4. **`window=None`:** allowed on claims and interpreted as "full period"; it
   overlaps any unit. Record IoU accordingly (a `None` window vs a real window →
   IoU = 0 penalty, since it is "vague" — per guide §8.2 penalize vagueness).
5. **Magnitude error** is best-effort (parse the `magnitude` string); skip
   non-parseable magnitudes rather than guessing. Record `null` for those.

---

## 15. Non-goals for M0 (explicit)

No LLM adapter, no sandbox, no `runner.py`, no iteration loop, no freeze/hash of
submissions, no leaderboard, no human-review queue, no scikit-learn ML detectors.
Do not regenerate or modify `data/`. Do not edit the sibling generator.

---

## 16. Quick-start commands (for the next agent)

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena
# option A — dedicated venv
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
# option B — reuse sibling venv (no install needed for core deps)
PY=../Life_insurance_data_generator_new/.venv/bin/python
$PY -m pytest tests/ -q
$PY -m abench validate
$PY -m abench run --model classical --split heldout
$PY -m abench score --run-id <id>
$PY -m abench report --run-id <id>
```
