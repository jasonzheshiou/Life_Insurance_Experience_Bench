# Assumptions Reference — Data Pipeline Arena

Everything the benchmark *assumes* about ground truth, contracts, and scoring.
The [implementation guide](../BENCHMARK_IMPLEMENTATION_GUIDE.md) is the source
of truth; this page is the quick reference.

---

## 1. Control types (what can be injected)

| `ControlType` | Meaning | `factor` is … |
|---|---|---|
| `drift` | per-year slope on a benefit's A/E | slope per year (e.g. `+0.10/yr`) |
| `shock` | one-off multiplier over a window | multiplier (e.g. `×1.5`) |
| `volatility` | per-year σ noise on claim counts | sigma (e.g. `0.3`) |
| `ip_recovery` | termination-rate multiplier (IP only) | recovery factor (e.g. `×2.0`) |
| `none` | no anomaly | — |

## 2. `ScenarioManifest` — ground truth (scorer-only)

```python
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

**Where manifests live:** the scorer-only truth store `data/truth/manifests/`
*only*, keyed by the opaque scenario id (`sc-<6hex>`; `data/truth/id_map.csv`
maps them to descriptive names). The model-facing eval workspace
(`data/eval/{optimization,heldout}/`) contains only CSV/PNG artifacts —
never the manifest, never a descriptive name.

## 3. `Verdict` contract — what every submission must emit

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
- Unknown enum value → validation error → **scored as a miss** (never silently coerced).

## 4. Starter scenario set

| Scenario | Control | Expected observable signature |
|---|---|---|
| `baseline` | none | all A/E ≈ 1.0 (noise only) |
| `drift_death_up_2018_2024` | drift +0.10/yr | Death A/E rises ~0.74 → 1.30 in window |
| `shock_covid_2020_2022` | shock ×1.5 | Death A/E spike 1.31/1.34/1.25 exactly in 2020–22 |
| `volatility_ip_sigma_03` | volatility σ=0.3 | IP annual-count variance ×3, level unchanged |
| `ip_recovery_mental_health_x2` | ip_recovery ×2.0 | MH termination A/E ≈ 2.0, incidence untouched |
| `noop_neutral_controls` | all neutral | bit-identical to `baseline` |

Harder variants: smaller drift (0.05), smaller shock (×1.2), narrower windows,
σ=0.15, and mixed-benefit scenarios (e.g. drift on Death + shock on CI).

## 5. Split assumptions (hard requirements)

- `optimization` and `heldout` are disjoint by `scenario_id` **and** by
  (benefit × control window × factor) where possible.
- Heldout scenarios are *new* mints (new windows/magnitudes/seeds) so no
  pipeline can have memorized them — the generator's determinism means
  "new scenario id = fresh, unseen data".
- A content hash is recorded for every model-facing input (fairness audit).

## 6. Sandbox assumptions

- **Tier 1 (subprocess):** temp cwd, `resource.setrlimit` (CPU time, address
  space, file size), wall-clock watchdog, read-only data + write-only out,
  network blocked (`unshare -n` on Linux; weaker on macOS/Windows — documented).
- **Tier 2 (container, recommended):** Docker/Podman `--network none`,
  read-only data volume, `--cpus`/`--memory`/`--pids-limit`, non-root.
- **Hard limits:** 120 s timeout, 2 GB memory, 1 CPU, 10 MB output.
- The tier used is recorded in the leaderboard.

## 7. Reproducibility pins (per cell)

- Generator seed + commit/version
- Model id, provider, `temperature`, per-run seed
- Code hash of the frozen pipeline (`submissions/<hash>/`)
- Run fingerprint (config hash + data hashes + model + time)
- N×K: N = 3–5 identical-input runs, K = 3 frozen executions — reported as
  median + spread, never a single best run

## 8. Statistical assumptions

- Baseline A/E is 1.0 with Poisson noise ~ `1/sqrt(target)`.
- Classical baseline floor: z-score on `AE` with threshold ~ `k/sqrt(target)`
  + CUSUM for drift/shock.
- Iteration cap in Stage 2: 3–5, recorded as an effort metric.
- The optimization-vs-heldout score gap is a reported metric (overfitting
  signal).
