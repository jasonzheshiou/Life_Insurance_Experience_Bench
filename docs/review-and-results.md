# Review & Results — Data Pipeline Arena

The test plan, the current project status, and where measured results land.
The authoritative test plan is §12 of the
[implementation guide](../BENCHMARK_IMPLEMENTATION_GUIDE.md); this page tracks
what has been done and what the runs produce.

---

## 1. Current status

| Milestone | Scope | Status |
|---|---|---|
| Plan | `BENCHMARK_IMPLEMENTATION_GUIDE.md` (locked decisions, schemas, guards) | ✅ Done |
| **Dataset (Stage 0)** | Scenario registry (47 scenarios), `generate_scenarios.py`, sanity gate, split/manifests/hashes | ✅ Done — see [Dataset usage](dataset-usage.md) |
| **M0** | Skeleton + deterministic core: `manifest.py`, `verdict.py`, `datasets.py`, `scoring.py`, classical detector, stub "model", `report.py` | ⬜ Not started (recommended next) |
| **M1** | Sandboxed runner (`runner.py` Tier 1) + one real LLM emitting Stage-2 code against the optimization set | ⬜ Not started |
| **M2** | N×K + heldout + leaderboard (freeze/hash, execution variance, `leaderboard.json`) | ⬜ Not started |
| **M3** | Stage-1 zero-shot baseline + Stage-3 report generation + human-review queue/annotations | ⬜ Not started |
| **M4** | Multi-model runs, cost/effort metrics, docs polish | ⬜ Not started |

The dataset (47 scenarios: 23 optimization / 24 heldout, families none/drift/
shock/volatility/noise_trap/recovery/mixed/systemic) is generated at `full`
scale (250k policies) with per-scenario sanity checks; the model-facing eval
workspace (`data/eval/`, **opaque scenario ids**) and scorer-only truth store
(`data/truth/`: manifests, id map, sealed) are written only when every check
passes **and** the byte-level leak scan (`scripts/leakcheck.py`) is clean.

### Ad-hoc zero-shot probe (experimental, not a milestone)

A Stage-1-style "give the LLM the data and ask for insights" probe
(`scripts/run_zero_shot.py`, see [zero-shot-experiment.md](zero-shot-experiment.md))
is ready and pointed at the local LM Studio endpoint
(`http://192.168.1.59:1234/v1`). It builds prompts from model-facing artifacts
only and **enforces it at runtime**: a preflight gate (opaque-layout check,
leak scan of the selected scenarios, banned-token scan of the assembled
prompt, file-hash + seal verification) refuses any API call unless
everything is clean. Supports N runs per scenario and can copy the
scorer-only manifests to the experimenter's disk for side-by-side comparison.
**Status: tooling ready (v0.2.0 with enforcement), no run executed yet.**
Results will land in `results/<run-id>/zero_shot/` when a run is made.

---

## 2. Test plan (acceptance criteria)

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
Two model configs pointed at the same run receive **byte-identical**
model-facing inputs (assert content hashes equal).

### Baseline sanity
The classical control-chart detector must detect `drift` and `shock` scenarios
(recall ≥ 1 on the canonical set) and must **not** fire on
`baseline`/`noop` — this proves the signal is present and the detector floor is
sane.

---

## 3. Where results land

| Artifact | Path | Contents |
|---|---|---|
| Verdicts | `results/<run-id>/verdicts.jsonl` | every model verdict per scenario |
| Scores | `results/<run-id>/scores.json` | per-cell detection + window/type/magnitude metrics |
| Leaderboard | `results/<run-id>/leaderboard.json` | heldout-only scores, median + spread, sandbox tier |
| Reports | `results/<run-id>/reports/*.md` | deterministic Stage-3 reports (ground truth revealed) |
| Review queue | `human_review/queue.jsonl` | anomalies queued for blind human review |
| Annotations | `human_review/annotations.jsonl` | TP/FP/boundary/missed labels + notes (feeds the golden set) |

Every run records its fingerprint (config hash + data hashes + model + time) so
any number in the leaderboard can be reproduced.

---

## 4. Known risks (from the plan)

| Risk | Mitigation |
|---|---|
| Arbitrary code executes harmfully | Container + `--network none`, resource caps, non-root, no host mounts |
| Model overfits/cheats via leakage | Strict optimization/heldout split, scorer-only manifests, hash audit |
| LLM non-determinism | N runs × K execs, fixed temperature/seed where possible, median + spread |
| Cost explosion | Iteration + token caps, classical-baseline gate before expensive runs |
| Unfair comparison | Identical inputs (hashed), one scoring rubric, same sandbox tier |
| Sandbox weaker on macOS/Windows | Default to container tier; record tier in results |
