# Zero-Shot "Insights" Experiment (ad-hoc)

An experiment you can run **today**, before milestone M0/M3 exist: hand an LLM
the raw scenario data, give it a goal, and see whether it can identify the
anomalies — where they are, what kind, and what to do about them.

This is the manual, open-ended version of **Stage 1** (guide §6). It uses only
chat completions: no code execution, no sandbox. When M3 lands, the same idea is
formalised with the strict `Verdict` schema and automatic scoring.

**Related docs:** [implementation guide §6](../BENCHMARK_IMPLEMENTATION_GUIDE.md) ·
[Dataset usage](dataset-usage.md) (the leak-free dataset layout) ·
[M0 handover plan](m0-handover.md) (where this becomes formal)

---

## 1. The one rule that must never break — and is now enforced

The model receives **only the model-facing scenario directory**
(`data/eval/<split>/sc-xxxxxx/`). Scenario dirs carry **opaque ids**
(`sc-<6hex>`): no folder name, file, or prompt can hint at which anomaly a
scenario contains. Ground truth lives in `data/truth/manifests/` (scorer-only)
and `data/raw/**/metadata.json` and is **never** part of the prompt.

Structural isolation is backed by a **runtime preflight gate** in
`scripts/run_zero_shot.py` — no API call happens unless all four checks pass
for the selected scenarios:

1. **opaque layout** — every scenario dir must be `sc-<6hex>` and the
   workspace must carry `dataset.json`; an old descriptive-style tree
   (`drift_death_up_…`) is refused outright;
2. **byte scan** — `scripts/leakcheck.py` sweeps the selected scenario
   subtrees (paths + file contents + PNG text chunks) for the banned
   anomaly-family vocabulary (`drift`, `shock`, `noop`, …) and for every
   descriptive scenario id in `data/truth/id_map.csv`;
3. **prompt scan** — the fully-built user prompt is itself scanned for banned
   tokens, so what is *sent* provably cannot name the answer;
4. **integrity** — every file of the selected scenarios is re-hashed against
   `data/eval/dataset.json`, whose `seal` must match the sealed truth store
   (`data/truth/seal.json`). A tampered or stale copy aborts the run.

Any hit prints `REFUSING TO RUN: preflight gate failed …` and exits 1 with no
API call; the verdict is recorded in `meta.json` (`leak_check`) and echoed in
`summary.md`. The leak scan cannot be disabled; only integrity verification
can (`--no-verify`, e.g. when running on a copy without the truth store).

## 2. What the runner does

Pre-flight gate passes (§1), then for each requested scenario and each run
(default 3 runs per scenario):

1. builds the prompt from the A/E tables (per-benefit yearly `Actual/Expected/AE`
   series, `summary.json`, and — in `--detail full` — the IP termination A/E by
   diagnosis),
2. calls the OpenAI-compatible endpoint (default: your local LM Studio at
   `http://192.168.1.59:1234/v1`) with a fixed system prompt asking for a
   structured JSON answer: overall assessment (`clean` | `anomalies`) and
   findings (benefit, years, pattern type, direction, magnitude, confidence,
   evidence, **recommended action**),
3. saves the raw response per run, plus the exact prompt, plus a summary.

Outputs: `results/<run-id>/zero_shot/`
(`<sc-id>_runNN.json`, `<sc-id>_prompt.md`, `summary.md`, `meta.json` with the
preflight verdict and truth seal).

## 3. Usage

Scenario ids are **opaque** (`sc-14cdd9`). For convenience the CLI also
accepts the descriptive names from the [scenario catalog](scenario-catalog.md)
and translates them via `data/truth/id_map.csv` — the descriptive name only
ever appears on your command line, never in a prompt or run output.

```bash
python3 scripts/run_zero_shot.py   # stdlib only (any python >= 3.11)

# what does your LM Studio serve right now?
python3 scripts/run_zero_shot.py --list-models

# preview the prompt for one scenario WITHOUT calling any API (gate still runs)
python3 scripts/run_zero_shot.py --scenarios baseline --split optimization --dry-run

# real probe: canonical easy cases + one noise trap + one clean baseline
python3 scripts/run_zero_shot.py \
    --scenarios drift_death_up_2018_2024,shock_covid_2020_2022,baseline \
    --split optimization \
    --model qwen3.8-27b \
    --runs 3 --show-truth

# heldout cases (never used for iteration; scored once)
python3 scripts/run_zero_shot.py --scenarios all --split heldout --runs 5 --show-truth

# different model on your endpoint, richer prompt
python3 scripts/run_zero_shot.py --scenarios all --split optimization \
    --model llama-3.1-8b --detail full --temperature 0.0 --runs 3
```

Environment overrides: `ABENCH_BASE_URL`, `ABENCH_MODEL`, `ABENCH_API_KEY`.
`--show-truth` copies the scorer-only manifests (keyed by the opaque id, plus
`id_map.csv`) into `results/<run-id>/zero_shot/truth/` **on the experimenter's
disk only** — the API call never sees them.

## 4. Good first scenario sets

Descriptive names below resolve automatically via the truth id map; their
opaque ids (from `data/truth/id_map.csv`) are given for reference.

| Set | Scenarios (descriptive → opaque) | What it tests |
|---|---|---|
| Easy positives | `drift_death_up_2018_2024`→`sc-f69eea`, `shock_covid_2020_2022`→`sc-5e376b`, `volatility_ip_sigma_03`→`sc-2d248f` | obvious trend, spike, dispersion |
| Clean negatives | `baseline`→`sc-14cdd9`, `noop_neutral_controls`→`sc-12be68` | false-positive tendency on clean data |
| Traps | `trap_noise_spike_lookalike`→`sc-9660b9`, `trap_noise_drift_lookalike`→`sc-8a9fa1` | does it hallucinate trend/spike from pure noise? correct answer is `volatility` only |
| Recovery | `ip_recovery_mental_health_x2`→`sc-409000` | is it looking at termination A/E, or missing it entirely? |
| Systemic | `sys_shock_inverse_2021_2022`→`sc-4a7f9e` | inverse directions (Death up ×1.4 / CI down ×0.6) in one window |
| Hard heldout | `trap_noise_spike_lookalike_b`→`sc-a15166`, `sys_cascade_drift_shock_2018`→`sc-c9d78b` | nasty cases, never seen before |

## 5. Judging the answers

Compare each `runNN.json`'s `findings` against the manifest in
`data/truth/manifests/<sc-id>.json` (or the copies under
`results/<run-id>/zero_shot/truth/` if you used `--show-truth`;
`id_map.csv` translates ids):

- **benefit** matches?
- **years** overlap the injected window?
- **pattern** equals the manifest's control type (`drift`/`shock`/`volatility`/
  `ip_recovery`)?
- **direction** matches `signature.direction`?
- on `baseline`/`noop`/noise-trap scenarios: did it claim anything at all?

That is a manual precision/recall; per guide §6, run **N times and look at the
median behaviour**, not one lucky answer. The `recommended_action` text is your
"what to do" layer — judge its quality qualitatively for now.

## 6. Current status & next steps

- **Status:** runner ready (`scripts/run_zero_shot.py`, v0.2.0, preflight
  enforcement included), pointed at LM Studio `192.168.1.59:1234`.
  **No run has been executed yet.**
- **Dataset:** leak-free layout (`data/eval` + `data/truth`) — see
  [Dataset usage](dataset-usage.md); run `python3 scripts/leakcheck.py` any
  time to re-verify the workspace byte-for-byte.
- **Next:** run the easy set above; then formalise as Stage 1 in M3 — same idea,
  but verdicts validate against the pydantic `Verdict` schema and score
  automatically against the manifests via M0's `scoring.py`.
