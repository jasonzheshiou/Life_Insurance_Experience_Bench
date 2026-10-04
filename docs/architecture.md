# Architecture — Data Pipeline Arena Dataset

Design document for the scenario-dataset pipeline. It explains how the pieces
fit together, the invariants that must never be broken, and the extension
points for future work.

**Related docs:** [dataset-usage](dataset-usage.md) (operations) ·
[assumptions-reference](assumptions-reference.md) (schemas) ·
[implementation guide](../BENCHMARK_IMPLEMENTATION_GUIDE.md) (arena plan)

---

## 1. Goals and design principles

The dataset pipeline turns the sibling life-insurance generator into the arena's
Stage-0 input (guide §5):

1. **Registry-driven, not code-driven.** Every scenario is data
   (`config/scenarios.yaml` + `config/scenarios.d/*.yaml`). Adding a scenario
   later never requires editing the script.
2. **Deterministic.** Fixed seed (default 42); a scenario is a pure function of
   its registry entry. Re-running yields byte-identical stores.
3. **Strict train/test separation.** `optimization` (training) and `heldout`
   (testing) are disjoint by (benefit × control type × window × factor),
   enforced before any generation.
4. **No leakage.** Ground truth (manifests, `metadata.json` with the controls)
   is never copied into the model-facing split.
5. **A sanity gate.** The split is only written when every scenario's observable
   signature checks out, so a broken dataset never reaches the arena.
6. **Auditable.** Content hashes of every model-facing file + a dataset
   fingerprint pin any arena run to the exact data it saw.

---

## 2. Component diagram

```
                    config/scenarios.yaml (+ scenarios.d/*.yaml)
                              |
                              v
                     [registry loader]  --validates ids, disjointness
                              |
                              v
         [build_assumptions] --YAML control shapes---> generator segments
                              |                        (Drift/Shock/Volatility/Recovery)
                              v
              [run_pipeline]  (sibling generator, seed=42)
                              |
                 +------------+-------------+
                 v                          v
        data/raw/<id>/store          data/raw/<id>/artifacts
        (frames + metadata.json)     (A/E charts + CSVs + summary)
        + run_info.json
                 |
                 v
         [check_scenario]  --per-control sanity checks vs baseline--
                 |                (drift/shock/vol/recovery/mixed)
                 v
          all hard checks pass?
              | no  -> abort, split NOT written
              v yes
         [assemble_split]
              |
     +--------+--------+-------------+
     v                 v             v
 optimization/     heldout/      manifests/
 (model-facing)    (model-facing) (scorer-only)
     +-----------------+-------------+
                      v
              hashes.json  +  scenario_summary.json
              (fairness audit)   (fingerprint, statuses)
```

## 3. Data flow

1. **Registry** → scenario list with `split`, `family`, `controls`.
2. **Disjointness check** — collect a key per control
   `(type, benefit-set, window, factor)`; the intersection of optimization and
   heldout key sets must be empty, or the run aborts.
3. **Generation** — `build_assumptions` maps YAML controls onto the generator's
   typed segments; `run_pipeline` runs once per scenario; `save_store` writes
   the full store (CSV always, parquet when available). `run_info.json`
   records scale/seed/targets/commit.
4. **Checks** — each scenario is verified against the baseline scenario (same
   scale) with scale-aware thresholds: Poisson noise is `1/√target`, so every
   threshold derives from the effective targets. Failures block the split.
5. **Split assembly** — model-facing dirs get store CSVs + artifacts only;
   manifests are written per scenario; `hashes.json` and
   `scenario_summary.json` close the run.

## 4. Key invariants (must never be broken)

| Invariant | Enforced by |
|---|---|
| Optimization ∩ heldout control signatures = ∅ | `check_disjointness` (aborts) |
| Same scenario id = same data (determinism) | fixed seed; `Assumptions.fingerprint()` in metadata |
| Train/test never mix scales | `run_scenario` scale guard (aborts unless `--force`) |
| Ground truth never in model-facing dirs | `assemble_split` copies only CSVs/PNGs, never `metadata.json`/parquet |
| Split reflects only passing scenarios | sanity gate (aborts unless `--force-split`) |
| Auditability | `hashes.json` (sha256 per file) + `scenario_summary.json` fingerprint |

## 5. Scenario families and their ground-truth semantics

| family | control(s) | model must report | sanity check |
|---|---|---|---|
| `none` (baseline) | — | `no_op` | A/E ≈ 1 |
| `none` (neutral) | all-neutral | `no_op` | bit-identical to baseline |
| `drift` | 1 drift | drift + direction + window | in-window ΔA/E sign & magnitude |
| `shock` | 1 shock (1+ benefits) | shock + factor + window | in-window A/E vs 1.0 |
| `volatility` | 1 volatility | dispersion (σ) | std ratio vs baseline |
| `noise_trap` | 1 volatility (high σ) | dispersion only — **no trend/shock** | variance up, level flat |
| `recovery` | 1+ ip_recovery | recovery factor + diagnosis | mean duration moves |
| `mixed` | independent controls | each control separately | per-control checks |
| `systemic` | correlated controls | correlated set (joint truth) | per-control checks |

The noise-trap family exists specifically to test false positives: strong
random variance can *look like* a drift or a spike, and the correct answer is
"dispersion only".

## 6. Extension points

1. **New scenario** → append a registry entry (or `scenarios.d/*.yaml`); no
   code change. Re-run with `--only <id>` then `--split-only`.
2. **New scale** → add a `scales:` preset; `--scale` picks it. Targets are
   derived from `base_targets × target_factor`.
3. **New control type** → three touch points: a segment builder in
   `build_assumptions`, a YAML shape (dataset-usage §4.2), and a check branch
   in `check_scenario`; manifest/disjointness logic is already generic.
4. **New check** → add to `check_scenario`; it participates in the gate
   automatically. Thresholds are derived from targets (scale-aware).
5. **Future arena integration** → the arena's scorer consumes
   `manifests/<id>.json` (single-control scenarios map 1:1 onto the guide's
   `ScenarioManifest`; multi-control uses the documented `controls` extension),
   model-facing dirs are the Stage-1/2 inputs, `hashes.json` the fairness
   audit, and `scenario_summary.json` fingerprints the dataset.

## 7. Failure modes and guards

| Failure | Guard |
|---|---|
| Registry typo / unknown control type | load-time fatal error |
| Duplicate scenario id | load-time fatal error |
| Optimization/heldout overlap | disjointness abort |
| Scale mismatch between stores | scale guard abort (or `--force`) |
| Scenario signature not reproduced | sanity gate abort (or `--force-split`) |
| Missing raw store during split assembly | reported in summary as `missing` |
| Generator drift (commit changes) | `run_info.json` records `generator_commit` |

## 8. Complexity notes

- One full-scale scenario (250k policies, charts) ≈ 60–90 s; the full 47-scenario
  dataset ≈ 1 hour single-threaded. The pipeline is naturally parallelisable
  per scenario (each is an independent `run_pipeline` call) — a future
  `--jobs N` flag can fan out across scenarios.
- Storage: each full-scale scenario store ≈ tens of MB (CSV + parquet +
  charts); the model-facing split is CSV-only and smaller.
