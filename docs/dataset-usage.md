# Dataset Usage — Data Pipeline Arena

How to generate, extend, and consume the arena's scenario dataset. This is the
living guide: it documents **every** feature of the current pipeline and the
conventions that future scenarios must follow.

**Related docs:** [architecture](architecture.md) (design) ·
[assumptions-reference](assumptions-reference.md) (ground-truth schema) ·
[review-and-results](review-and-results.md) (test plan) ·
[implementation guide](../BENCHMARK_IMPLEMENTATION_GUIDE.md) (arena plan)

---

## 1. What this pipeline produces

For each scenario in the registry (`config/scenarios.yaml` + optional
`config/scenarios.d/*.yaml`), the generator:

1. builds a deterministic `Assumptions` object (seeded, default `42`) with the
   scenario's control segments (drift / shock / volatility / IP recovery),
2. runs the sibling generator's pipeline once (250k policies at `full` scale),
3. saves the complete store under `data/raw/<scenario_id>/` — *our* copy,
   including `metadata.json` which embeds the full assumptions (ground truth),
4. runs **sanity checks** on the observable signature of every control,
5. assembles the **model-facing eval workspace** `data/eval/` (ZONE A) — CSVs
   and charts only, under **opaque scenario ids** (`sc-<6hex>`); ground truth
   and every descriptive scenario name stay out **by construction**,
6. writes the **scorer-only truth store** `data/truth/` (ZONE B): the frozen
   id map, manifests keyed by opaque id, the sanity-check report, and a sha256
   **seal** committing to all of it,
7. runs a mandatory **byte-level leak scan** (`scripts/leakcheck.py`) over the
   whole eval workspace — any answer-bearing token **fails the build**.

Layout:

```
data/
├── raw/<descriptive_id>/           # full store (generator outputs + metadata.json) — lab view
│   ├── store/                      # exposure + claim frames (CSV + parquet), benchmarks/, metadata.json
│   ├── artifacts/                  # A/E charts (PNG), per-benefit A/E CSVs, summary.json
│   └── run_info.json               # scale, seed, targets, generator commit
├── eval/                           # ZONE A — the ONLY folder ever shipped to a model/agent
│   ├── optimization/sc-<6hex>/     # TRAINING: model-facing artifacts, opaque dir name
│   ├── heldout/sc-<6hex>/          # TESTING:  model-facing artifacts, opaque dir name
│   └── dataset.json                # file inventory + sha256 (opaque paths) + truth seal
└── truth/                          # ZONE B — scorer-only, NEVER ships with data/eval/
    ├── id_key.json                 # random seed behind the opaque id derivation
    ├── id_map.csv                  # sc-<6hex> → descriptive name, family, split (FROZEN)
    ├── manifests/sc-<6hex>.json    # GROUND TRUTH — scorer only, keyed by opaque id
    ├── scenario_summary.json       # statuses, check details, fingerprint, id map copy
    └── seal.json                   # sha256(id_map + all manifests) — sealed commitment
```

Each model-facing scenario directory contains: the raw exposure/claim CSVs, the
per-benefit A/E CSVs and charts, `summary.json`, and a `scenario_id.txt`.
`metadata.json` (which contains the injected controls) and parquet files are
**excluded** by design.

---

## 2. Quick start

```bash
# One-off smoke pass at reduced scale (seconds per scenario)
python scripts/generate_scenarios.py --scale tiny --only baseline,drift_death_up_2018_2024

# The canonical dataset (250k policies, all 47 scenarios; ~1 hour)
python scripts/generate_scenarios.py --scale full

# Regenerate everything from scratch
python scripts/generate_scenarios.py --scale full --force

# Rebuild the split from existing raw stores (no regeneration)
python scripts/generate_scenarios.py --scale full --split-only
```

Use the interpreter that has the generator's dependencies:

```bash
../Life_insurance_data_generator_new/.venv/bin/python scripts/generate_scenarios.py --scale full
```

---

## 3. CLI reference

```
usage: generate_scenarios.py [-h] [--config PATH] [--scale NAME] [--only id1,id2]
                             [--force] [--split-only] [--no-checks] [--force-split]

--config PATH     scenario registry YAML (default config/scenarios.yaml)
--scale NAME      tiny | medium | full  (default: config's default_scale)
--only id1,id2    generate/assemble only these scenario ids
--force           regenerate raw stores even if they exist
--split-only      skip generation; rebuild split from existing raw stores
--no-checks       skip the sanity checks
--force-split     assemble the split even if sanity checks fail (deliberate override)
```

Exit codes: `0` success (split assembled and all checks passed), `1` on error
or failed sanity checks (split **not** written).

---

## 4. The registry — the single source of truth

**`config/scenarios.yaml`** defines every scenario. The script contains no
scenario definitions — it only executes the registry. Extra files dropped into
**`config/scenarios.d/`** (any `*.yaml` with a `scenarios:` list) are merged at
load time, so future scenario batches can live in their own files.

### 4.1 Top-level keys

```yaml
scales:            # named scale presets
  tiny:   {n_policies: 5000,   target_factor: 0.02}   # ~100/240/160/300 claims
  medium: {n_policies: 25000,  target_factor: 0.1}    # ~500/1200/800/1500
  full:   {n_policies: 250000, target_factor: 1.0}    # 5000/12000/8000/15000
default_scale: medium          # change this or pass --scale
seed: 42                       # deterministic reproducibility
study: {start: "2015-01-01", end: "2024-12-31"}
base_targets: {Death: 5000, CI: 12000, TPD: 8000, IP: 15000}

scenarios:
  - id: <unique-id>
    family: none|drift|shock|volatility|noise_trap|recovery|mixed|systemic
    split: optimization|heldout
    no_op: true|false          # baseline/neutral scenarios only
    neutral: true              # optional: all controls at neutral values (exact no-op)
    controls: [ ... ]
```

### 4.2 Control shapes

| type | fields | generator segment |
|---|---|---|
| `drift` | `benefit` (or `all`), `window: [y0, y1]`, `slope` | `DriftSegment` |
| `shock` | `name`, `window`, `factors: {Benefit: float}` | `ShockSegment` |
| `volatility` | `benefit` (or `all`), `window`, `sigma` | `VolatilitySegment` |
| `ip_recovery` | `window`, `factors: {Diagnosis: float}` | `RecoverySegment` |

Diagnosis names (exact): `Musculoskeletal`, `Mental Health`, `Cancer`,
`Cardiovascular`, `Neurological`, `Injury/Accident`, `Other`.

Validated ranges (the generator enforces them): drift slope ∈ [−0.9, 5.0],
sigma ∈ [0, 1.0], all factors > 0. Windows are inclusive years; a control with
`benefit: all` (or no benefit) applies to every benefit. Multi-control
scenarios (family `mixed` / `systemic`) simply list several controls.

### 4.3 The disjointness rule (hard requirement)

`optimization` and `heldout` must be **disjoint by
(benefit set × control type × window × factor)**. The script verifies this
before generating anything and aborts on any overlap. When you add heldout
scenarios, use windows, magnitudes, or benefits that do not appear in any
optimization scenario — a model must never be able to answer a heldout case by
memorising a training case.

---

## 5. Adding scenarios later (future-proofing)

1. Append an entry (or drop a file into `config/scenarios.d/`) with a unique id.
   Family prefixes are conventional: `drift_*`, `shock_*`, `vol_*`,
   `rec_*`/`ip_recovery_*`, `trap_*` (noise traps), `mix_*`/`mixed_*`,
   `sys_*` (systemic / correlated), `baseline`, `noop_*`.
2. Run `python scripts/generate_scenarios.py --scale full --only <new-id>` to
   generate just that scenario's raw store.
3. Reassemble the split with `--split-only` (existing stores are reused; the
   split is rebuilt to include the new scenario). The disjointness check runs
   again and will catch any training/test overlap.

Nothing else changes: manifests, hashes, and the summary are all derived from
the registry.

---

## 6. Scales and regeneration policy

- **Scales** are presets in the registry; add your own or edit `target_factor`
  freely. The effective `n_policies` and per-benefit targets are recorded in
  every manifest and `run_info.json`.
- **Scale mixing is forbidden**: if a raw store exists at a different scale than
  requested, the script refuses to proceed (train/test must never mix scales)
  unless `--force` overwrites it.
- **Reuse**: an existing raw store matching the requested scale is reused
  (checks still run against it); `--force` regenerates.
- **Determinism**: same registry + same scale ⇒ byte-identical stores (fixed
  seed). `run_info.json` records the generator commit for provenance.
- **Split rebuilds** wipe and recreate `data/eval/{optimization,heldout}` and
  `data/truth/manifests` each time, so the eval workspace always reflects
  exactly the current registry + available raw stores. Opaque ids are FROZEN
  in `data/truth/id_map.csv` and never churn; new scenarios extend the map.
- **Pandas-free rebuild**: `--split-only --no-checks` only relabels/copies and
  scans — it runs on a bare stdlib+PyYAML interpreter (no generator package).

---

## 7. Sanity checks

Each scenario's observable signature is checked before the split is written
(the gate: a failing scenario blocks the whole split unless `--force-split`):

| family | checks |
|---|---|
| `none` baseline | overall A/E ≈ 1 for all benefits (5σ band of Poisson noise) |
| `none` neutral | claims/exposure/termination A/E bit-identical to baseline |
| `drift` | in-window A/E vs reference period: sign matches slope, magnitude ≥ 1.5σ |
| `shock` | in-window A/E vs 1.0: sign matches factor, magnitude ≥ 0.7·|factor−1| |
| `volatility`, `noise_trap` | in-window std ratio vs baseline ≥ 1.5; level unchanged |
| `recovery` | per-diagnosis mean duration moves with the factor; unaffected diagnoses flat |
| `mixed` / `systemic` | per-control checks above, each control independently |

Weak detections (correct direction, small magnitude) are reported as `weak`,
not failures — at reduced scales small effects are statistically underpowered.
The full-scale run is the authoritative gate.

---

## 8. Manifests (scorer-only ground truth)

`data/truth/manifests/<sc-id>.json` (scorer-only; keyed by the **opaque** id):

```json
{
  "schema_version": 1,
  "eval_id": "sc-f69eea",
  "descriptive_id": "drift_death_up_2018_2024",
  "scenario_id": "drift_death_up_2018_2024",
  "family": "drift",
  "split": "optimization",
  "scale": "full",
  "seed": 42,
  "n_policies": 250000,
  "targets": {"Death": 5000, "CI": 12000, "TPD": 8000, "IP": 15000},
  "study_window": [2015, 2024],
  "no_op": false,
  "controls": [
    {"type": "drift", "benefit": "Death", "window": [2018, 2024],
     "factor": 0.15, "signature": {"direction": "increase", "magnitude": "+0.15/yr"}}
  ],
  "benefit_lines_untouched": ["CI", "TPD", "IP"],
  "primary": { ... }            // for single-control scenarios: the arena's
                                // ScenarioManifest-compatible flattened form
}
```

Multi-control scenarios (`mixed`, `systemic`) list every injected control in
`controls`; `primary` is `null` and `benefit_lines_untouched` is computed over
all controls. This is the documented extension of the arena's single-control
`ScenarioManifest` (guide §4.1) — the scorer matches claims greedily against
the `controls` list.

---

## 9. Fairness & reproducibility

- `data/eval/dataset.json`: sha256 of every file under `optimization/` and
  `heldout/` (keyed by **opaque** relative paths) — proves all models saw
  byte-identical inputs and audits the workspace.
- `data/truth/seal.json`: sha256 over `id_map.csv` + all manifests. Publish
  the seal **before** model runs to prove the ground truth was not edited
  afterwards. `run_zero_shot.py` records it in every `meta.json`.
- `data/truth/scenario_summary.json`: per-scenario statuses + check details,
  counts, scale, seed, generator commit, and a **fingerprint** = sha256 over
  the sorted manifest set. Pin any arena run to this fingerprint.
- Ground truth lives **only** in `data/truth/` (+ `data/raw/`); the eval
  workspace contains CSVs, PNGs, and `scenario_id.txt` (opaque id) — never
  `metadata.json` (it embeds the controls), never a descriptive scenario name.

---

## 10. FAQ

- **Why did a check say `weak`?** The effect is present but small relative to
  Poisson noise at this scale. Re-run at `full` for the authoritative result.
- **I changed a scenario's parameters — what happens to old stores?** The raw
  store is keyed by `scenario_id` only. Regenerate with `--force` for that id,
  then `--split-only` to rebuild the split.
- **Can I add a whole new control type?** Yes — add the segment builder in
  `build_assumptions`, the YAML shape in §4.2, and a check in
  `check_scenario`; the manifest and disjointness logic are already generic.
- **Where do parquet files go?** They stay in `data/raw/` (our copy). The
  model-facing split is CSV-only for portability.
