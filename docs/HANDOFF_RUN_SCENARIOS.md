# HANDOFF — Run Remaining Zero-Shot Scenarios (Data Pipeline Arena)

> **✅ STUDY COMPLETE (2026-09-05): 47/47 scenarios × 3 runs = 141/141 valid
> generations in `results/xam_v4/`.** Final analysis: `results/xam_v4/reports/
> STUDY_SUMMARY.md` (+ `COMPUTE_AND_META.md` for tokens/runtime and the
> grader-awareness audit). Scorer upgraded to **v3** and runner to **v0.4.2**
> (see §6). Raw v2 scores preserved at `results/xam_v4/scores_v2_snapshot.json`.
> The operating manual below is retained for any future re-run / model swap.

> **🔄 MODEL-SWAP CAMPAIGN (2026-09-07): `Qwen3.8-27b` on all 47 scenarios × 3
> runs → separate corpus `results/xam_v5/`.** Run (and re-run to resume) with
> **`bash scripts/sweep_qwen27b.sh`** — resume-safe (`--skip-existing`,
> per-scenario skip of banked runs), flock-guarded against double-launch; live
> progress in **`results/logs/qwen27b_status.txt`** (`RUNS FINISHED: n/141`,
> rewritten after every scenario; also anytime via `scripts/sweep_status.py`).
> The xam_v4 corpus is untouched — `run_zero_shot.py` writes only inside
> `results/<--out>/`. ⚠️ Prompt caveat: runner **v0.4.3** ships the revised
> prompt (revision **v2** = former patch P2: bounded-drift definition +
> Poisson-overdispersion discipline) as its ONLY system prompt, so xam_v5
> differs from xam_v4 in model **and** prompt revision, not model alone.

> 📖 **Plain-language record of the harness work (what, why, measured effect,
> glossary for non-specialists): `docs/HARNESS_GROWTH.md` — kept up to date as
> the campaign runs.**
>
> **🔧 HARNESS CAMPAIGN (2026-09-09): grow the simplest tool-harness that
> lifts Qwen3.8-27B.** Runner **v0.5.0** adds opt-in `--harness full` (default
> `off` keeps the zero-shot protocol that produced xam_v4/xam_v5 unchanged).
> Harness h1 = (a) deterministic **evidence pack** (`scripts/stats_pack.py`,
> thresholds calibrated against all 47 truth manifests; appended to the user
> prompt and leak-scanned clean) + (b) **sandboxed python tool loop**
> (cwd=scenario artifacts, 10 s/call, ≤4 calls, full transcript recorded;
> truth can never reach the pack or the sandbox). Improvement loop on the
> **optimization split only**: `bash scripts/harness_opt_step.sh` — ONE
> scenario per invocation (1 run), scores vs truth, appends the truth-diff
> (`scripts/harness_diff.py`) to `results/logs/harness_opt_loop.md`, stops for
> a harness edit, re-run same command advances/resumes; live counters in
> `results/logs/harness_opt_status.txt`. Passes `PASS=1..3` → corpora
> `results/harness_opt_p<N>/`. Freeze gate: optimization strict ≥ ~80 %,
> FP/run ≤ 1.0, zero CLEAN regressions → final test on heldout, then leakcheck.
> ⚠️ New hosting (unsloth-studio) answers 401 without a real token —
> `export ABENCH_API_KEY=<token>` before any live run.

This document is the complete operating manual for continuing the experiment.
A prior session already did scenario 1 of 47. Everything needed to run the
remaining 46 is here. Read it fully before doing anything.

**Repo root:** `/mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena`
(working dir of the agent; every command below is run from there).

---

## 0. TL;DR checklist for the next scenario

For each scenario, in order:

1. `bash scripts/run_one_scenario.sh <sc-id>` (defaults to run dir `xam_v4`)
2. When it finishes: `python3 scripts/score_xam.py results/xam_v4/zero_shot`
3. `python3 scripts/report_xam.py results/xam_v4/zero_shot`
4. **Read the results and the dossier, then STOP and present to the user**:
   Tier-1 executive summary → Tier-2 actuary view → Tier-3 methodology.
   Do NOT start the next scenario without user sign-off ("go").
5. Leak checks are automatic (preflight gate refuses to run on any leak).
   After finishing all scenarios, run the full workspace scan once more
   (section 5).

All 47 scenarios are DONE. Batch sweeps for the tail ran through
`scripts/sweep_xam_v4_heldout.sh` (resume-safe, flock-guarded; `--list` shows
anything outstanding). The opt-in **prompt patch P2** (bounded-drift labelling +
Poisson-overdispersion discipline) was ADOPTED as the only system prompt in
runner v0.4.3 (`PROMPT_REVISION = "v2"`); the `--prompt-patch` flag no longer
exists. The xam_v4 corpus (141/141) was generated under revision **v1** — its
exact prompt text survives in `results/xam_v4/zero_shot/*_prompt.md` and in
every run record's `prompt.sha256`.

---

## 1. What this experiment is

- **Task:** zero-shot "insights" probe for a synthetic life-insurance benchmark
  (Data Pipeline Arena). An LLM is given ONLY the model-facing data of one
  scenario (A/E experience tables) and asked to identify anomalies: where,
  what kind (drift / shock / volatility / recovery), direction, magnitude,
  confidence, evidence, recommended action — as a strict JSON object.
- **Ground truth lives in `data/truth/manifests/<sc-id>.json`** (scorer-side).
  It is NEVER sent to the model. The model sees only the opaque scenario
  directory `data/eval/<split>/<sc-id>/` (opaque ids `sc-<6hex>`, no
  descriptive names anywhere).
- **Leakage is enforced at runtime** by `scripts/run_zero_shot.py` before any
  API call: opaque-layout check, byte scan of scenario files (paths + content
  + PNG text chunks) for banned vocabulary and every descriptive scenario id,
  a scan of the exact prompt to be sent, and file-hash/seal integrity vs
  `data/eval/dataset.json` + `data/truth/seal.json`. Any hit → refuses to run.
- 47 scenarios: 24 heldout (never tuned on) + 23 optimization. Each scenario
  has one injected control (or is a clean/noise-trap control).

## 2. The model endpoint (fixed settings — do not change)

- **Endpoint:** `http://192.168.1.59:8080/v1` — llama.cpp server, **1 slot**
  (requests serialize), `n_ctx = 260096`, `default max_tokens = -1` (unlimited).
- **Model:** `Qwen3.8-Flash-Next` (hybrid reasoning model, ~176B Q4_K-M).
- **Samplers (exact):** `temperature=1.0, top_p=0.95, top_k=20, min_p=0.0,
  presence_penalty=0.0, repetition_penalty=1.0`.
- **No `max_tokens` is ever sent** — the completion is bounded only by the
  260k context window. This is deliberate (user requirement).
- **`stream=true` always** — needed because single generations take 10–30 min
  and a silent socket invites connection resets. `stream_options.include_usage`
  is set so token counts come back.
- **Stateless:** each call = exactly one system turn + one user turn. No
  history. Proven empirically: `prompt_tokens` identical across runs,
  `cached_tokens: 0`.
- **No tools:** the request never contains `tools`/`function_call`, the server
  returns no `tool_calls`, and outputs contain no code. The model answers from
  the numbers alone. (Verified for scenario 1.)

### Why outputs are huge (do not "fix" this)
The model is a hybrid reasoner with thinking ON by default. 94–97% of every
generation is hidden chain-of-thought (`reasoning_content`), typically
40k–95k chars, before the ~3k-char JSON answer. `finish_reason: stop` —
nothing is truncated. This is expected behaviour, recorded as-is. Mean cost
per call: ~11–30k completion tokens, ~10–30 min wall time (scenario 1:
21/9.4/13 min).

## 3. Runner — `scripts/run_zero_shot.py` (v0.4.0)

Stdlib-only (urllib). Key flags used by the wrapper (section 4):

- `--runs 3` — 3 independent runs per scenario (seeds 1234/1235/1236)
- `--detail full --termination-mean pooled` — includes IP termination table,
  **pooled** aggregation (see section 6 — this was a bug fix)
- `--stream` — SSE streaming
- `--timeout 3600` — 1 h per API call
- `--wait-for-endpoint 1800` — if the server is reloading (it refuses
  connections for minutes), poll up to 30 min before spending a call
- `--max-consecutive-failures 5` — circuit breaker: abort the sweep instead
  of burning calls against a dead endpoint
- `--skip-existing` — resume: keeps any run file that already has content
- `--show-truth` — copies scorer-only manifests into the results dir for the
  experimenter's review; **never sent to the model**
- `--out <run-id>` → writes to `results/<run-id>/zero_shot/`
- `--dry-run` — prints the prompts and runs the full preflight gate but writes
  NOTHING to disk (it cannot clobber a live pool's meta.json; fixed in v0.4.1)

Outputs per scenario: `<sc-id>_prompt.md`, `<sc-id>_runNN.json` (contains
`content`, `reasoning_content`, `raw_response`, `usage`, `finish_reason`,
`request` verbatim payload, `wall_seconds`, timestamps, prompt sha256),
`summary.md`, `meta.json` (provenance + leak verdict). Note: `meta.json`
and `summary.md` are rewritten by the *most recent* runner invocation
(one scenario per wrapper call); the cumulative pool truth is the
`*_runNN.json` records + `reports/index.md` + `score_xam.py` output.
Manual per-scenario review notes live in `reports/<sc-id>_notes.md`
(never regenerated by tooling — the permanent record of reasoning quotes,
rubric artifacts and behavioral observations).

## 4. Run ONE scenario (the wrapper)

```bash
bash scripts/run_one_scenario.sh sc-137901            # split auto-detected
# optional second arg overrides run dir:  ... sc-137901 xam_v4
```

That single command does the preflight gate + 3 streamed calls. Each run
takes 10–30 min; the whole scenario ~45–90 min. Run it in the background
(e.g. the agent's `run_in_background: true`) and check on it — do not block.

### After it finishes

```bash
python3 scripts/score_xam.py results/xam_v4/zero_shot   # recall / FP vs truth
python3 scripts/report_xam.py results/xam_v4/zero_shot  # 3-tier dossier
```

The dossier lands at `results/xam_v4/reports/<sc-id>_behavior.md` (plus
`index.md`). It has three tiers: **Tier 1 executive summary** (general
reader), **Tier 2 for the actuary** (domain view), **Tier 3 methodology &
outcomes** (settings, per-run timing/tokens, tool-use evidence, the data with
σ-bands, ground truth, verdicts).

**Then STOP.** Present to the user, in this shape:

1. **Executive summary** (plain language): what the model concluded, whether
   it matches the hidden anomaly, did it cheat (it cannot — say so with the
   evidence), confidence, false positives.
2. **For the actuary:** trust diagnosis, magnitude check, what to be careful
   about.
3. **Methodology & outcomes:** settings used, run time, token counts, prompt
   archive path, what was recorded.

Wait for user approval before the next scenario.

## 5. Verification / hygiene (run whenever unsure)

```bash
curl -s -m 15 http://192.168.1.59:8080/v1/models          # endpoint alive?
curl -s -m 15 http://192.168.1.59:8080/slots               # is_processing?
python3 scripts/leakcheck.py          # full workspace byte scan (~2-3 min)
```

- Leak rules: **never** copy anything from `data/truth/` or
  `results/*/reports/` into `data/eval/` or into any prompt. The dossiers
  contain ground truth — they live under `results/` only, and
  `report_xam.py` refuses to write under `data/eval/`.
- If the endpoint is down: wait; the runner's `--wait-for-endpoint` handles
  it. IMPORTANT: `wait-for-endpoint expired` does NOT prove the server is
  dead — a llama.cpp slot busy with an ORPHANED generation (from a broken
  stream) stays unavailable while still generating. Confirm via
  `GET /slots` (`is_processing`) before concluding an outage. If a run file
  exists with empty content or an `error` field, it is a stub: re-running
  the same wrapper re-spends ONLY those stubs (`--skip-existing` skips only
  records with content and no error). If the WSL VM was reclaimed (uptime resets, `/tmp` wiped), just re-run
  the same wrapper — `--skip-existing` resumes; nothing already answered is
  re-spent. Never keep logs only in `/tmp`.
- Connection-refused stubs are recorded as `"error": ...` in run files; a run
  with `content` and no `error` is good.

## 6. Known defects & decisions (carry these forward)

1. **Termination aggregation bug (FIXED).** As-shipped, `--detail full` sent
   an UNWEIGHTED mean over 108 duration months (98 tiny-exposure cells),
   which manufactured a phantom "recovery" anomaly (Injury/Accident 1.544)
   in every scenario — verified: exposure-weighted truth is 1.001. Fix:
   `--termination-mean pooled` = `sum(Recovered)/sum(Exposed*AssumedRate)`,
   which reproduces the dataset's own published `overall_termination_ae` to
   4 dp. Effect measured on scenario 1: false positives 2.33/run → 0.33/run,
   recall unchanged (3/3), cost −32%. `--termination-mean unweighted` exists
   only to reproduce the old behaviour.
2. **Truth-side direction label is lossy.** `generate_scenarios.py:575`
   collapses a mixed-direction control (e.g. Death ×1.4 AND CI ×0.6) into one
   `signature.direction` ("decrease" if ANY factor < 1.0). A correct model
   answer would be scored wrong on direction against that label. `score_xam.py`
   compares per-benefit factors instead. Do not "fix" the manifests.
3. **Scoring rubric nuance.** The model sometimes reports a statistically
   real observation that is not the injected control (scenario 1: "CI ≈0.93
   excluding the spike" — true, verified). That counts as a false positive by
   the rubric but is not a hallucination. Note it in the dossier, don't hide
   it.
4. **Prior aborted sweeps (ignore).** `results/xam_20260831_*` contain 135
   connection-refused stubs from an earlier run against a dead server — not
   data. `results/xam_v3` is scenario 1 with the OLD (unweighted) prompt —
   keep for comparison, do not extend. The live pool is **`results/xam_v4`**
   (pooled prompt + streaming): contains scenario 1 (`sc-042304`).
6. **Scorer volatility/drift-direction bugs (FIXED 2026-09-02).** Two
   related defects in `score_xam.py`: volatility controls carry σ in
   `factor` (e.g. 0.3), and drift controls carry a SIGNED PER-YEAR RATE
   (e.g. +0.08); both were misread as A/E ratios (`<1.0 → "decrease"`),
   so the model's CORRECT "dispersion"/"increase" answers failed strict
   on direction. Fixed: volatility→`dispersion`, drift→sign of rate
   (matching the manifest's own `signature.direction`). Effects:
   sc-2d248f 0/3→3/3, sc-314eca 0/3→2/3, sc-63f1c7 3/6→6/6,
   sc-8d3b47 3/6→6/6 (pre-fix numbers live in the per-scenario
   `*_notes.md`). Three further FP-inflating artifacts are DOCUMENTED
   BUT NOT FIXED (deferred until the pool completes, to keep
   comparability): (a) `matched_idx` marks only one finding per
   multi-benefit control, so correctly finding BOTH benefits scores the
   second as FP (sc-4a7f9e, sc-48351f); (b) model "no material anomaly"
   statements filed in `findings` (`pattern:"other"`) count as FP; (c)
   `years:null` on full-period controls fails strict window overlap
   (recovery family — see sc-17d82f/sc-409000 notes).
7. **Empty-generation failure mode (FIXED in runner v0.4.2).** `sc-6e2478_run01`
   (rerun, batch 2): SSE stream closed cleanly (`attempts_ok=1`, no exception)
   with ZERO content, null finish_reason. v0.4.1 counted this as OK, so chains
   could report rerun_ok with a stub surviving. v0.4.2 raises `EmptyGeneration`
   (retried in-call; if it persists it is recorded as a real error so
   `--skip-existing` re-spends it), and the over-broad "recovered run is OK →
   error=None" line now also requires non-empty content. v0.4.2 additionally
   logs `prompt.patch` per record and adds `--prompt-patch {none,p2}` (P2 =
   bounded-drift + overdispersion schema patch, default off = byte-identical
   corpus). **v0.4.3 update:** that flag was removed — P2 is now the sole
   system prompt; records log `prompt.revision` ("v2") instead of
   `prompt.patch`. Scorer **v3** (post-pool) fixed the three FP-inflating artifacts of
   item 6 (per-benefit units, no-anomaly statements excluded, null-window =
   full-period hit) and made the ip_recovery direction check live; v2 scores
   frozen at `results/xam_v4/scores_v2_snapshot.json`. v3 totals: strict
   56.1%→63.1%, FP/run 1.54→1.05, recovery 1/15→15/15. Details:
   `reports/COMPUTE_AND_META.md`.
8. **User requirements honored:** no max_tokens; 1 h per-call timeout;
   ≥3 independent stateless runs per scenario; one scenario at a time with a
   stop-and-review; every run recorded verbatim (prompt, reasoning, answer,
   request, usage, timing).

## 7. Environment facts

- Python 3.14.4; everything stdlib-only.
- Repo layout: `scripts/` (runner, leakcheck, score_xam, report_xam,
  generate_scenarios), `data/eval/` (model-facing), `data/truth/`
  (scorer-side), `results/` (experiment outputs + dossiers), `docs/`,
  `config/scenarios.yaml`, `BENCHMARK_IMPLEMENTATION_GUIDE.md`.
- Files authored by the previous session:
  - `scripts/run_zero_shot.py` v0.4.0 (patched: samplers, streaming,
    pooled termination, circuit breaker, resume, payload capture)
  - `scripts/score_xam.py` (truth-comparison scorer)
  - `scripts/report_xam.py` (dossier generator, leak-safe)
  - `scripts/run_one_scenario.sh` (wrapper)
  - `scripts/sweep_xam_20260831.sh` (bulk sweep harness — obsolete; the
    one-at-a-time flow is now the norm)
- **Incident log:** scenario-1 raw run files under `results/xam_v4/zero_shot/`
  were accidentally deleted during handoff prep and re-generated by re-running
  the identical command (same fixed seeds 1234/1235/1236 → near-identical
  outputs). The dossier `results/xam_v4/reports/sc-042304_behavior.md`
  survived the whole time. If a raw run file is missing, re-running the same
  wrapper command with the same run id restores it without touching other
  scenarios.
- **Incident (2026-09-02, batch 2):** the llama.cpp server process DIED at
  ~04:52 UTC mid-stream (connections refused, ~2.7 h, recovered ~07:31 UTC —
  external restart; NOT reproducible from our side, possibly OOM after
  >38k-token generations at 260k ctx). It wiped sc-5e376b/63f1c7/6e2478/
  8a9fa1/8d3b47 (error stubs only); a resume chain re-ran all five
  successfully (08:50–11:42 UTC) — same seeds, everything documented.
  Distinguish the two failure signatures: `URLError(ConnectionRefused)` =
  process down (wait for restart); `wait-for-endpoint expired` with the
  port alive = slot busy/orphaned generation draining (see §5).
- Sandbox: file policy `danger-full-access`; approval prompts disabled —
  never request sandbox escalation.

## 8. Scenario order (truth names for review only — NEVER into prompts)

Optimization split (23) — next is #17:

```
 1. sc-042304 shock_ci_2021_2022            shock        DONE (results/xam_v4)
 2. sc-137901 sys_trend_tpd_ip_2019_2023    systemic     DONE (strict 0/6: found TPD+IP increase, labeled shock/volatility — see notes)
 3. sc-14cdd9 baseline                      none         DONE (clean 3/3, FP 0)
 4. sc-17d82f ip_recovery_cancer_x05        recovery     DONE (loose 3/3, strict 0/3 on years:null — see notes)
 5. sc-2d248f volatility_ip_sigma_03        volatility   DONE (strict 3/3 post-scorer-fix; exact)
 6. sc-314eca sys_vol_macro_2019_2021       systemic     DONE (strict 2/3 post-fix; decomposed per benefit)
 7. sc-3c83fd drift_ci_down_2016_2019       drift        DONE (0/3: labeled dispersion — bounded-drift ambiguity)
 8. sc-409000 ip_recovery_mental_health_x2  recovery     DONE (loose 3/3, A/E 1.990 vs x2.0; strict 1/3 on years:null)
 9. sc-48351f shock_tpd_ip_2023             shock        DONE (strict 3/3; rerun after orphaned-slot timeout)
10. sc-4a7f9e sys_shock_inverse_2021_2022   systemic     DONE (strict 3/3 mixed-direction, both sides; rerun)
11. sc-5e376b shock_covid_2020_2022         shock        DONE (strict 3/3, Death x1.5 nailed; first pass killed by server crash, rerun)
12. sc-63f1c7 mixed_drift_death_shock_ci    mixed        DONE (strict 6/6 post-scorer-fix; FIRST correct "drift" labels 3/3)
13. sc-6e2478 volatility_death_sigma_02     volatility   DONE (2/2 valid runs strict; run1 = empty-generation, see notes + §6.7)
14. sc-8a9fa1 trap_noise_drift_lookalike    noise_trap   DONE (strict 3/3; resisted the drift-lookalike bait)
15. sc-8d3b47 sys_drift_diverge_2018_2024   systemic     DONE (strict 6/6 post-fix; both drifts, both directions, 3/3 runs)
16. sc-9372cd drift_tpd_up_2019_2021        drift        DONE (0/3: bounded drift read as 2021 shock — 3rd bounded-drift miss, see table in notes)
17. sc-9660b9 trap_noise_spike_lookalike    noise_trap   <-- NEXT
17. sc-9660b9 trap_noise_spike_lookalike    noise_trap
18. sc-abbec4 sys_shock_tpd_ip_2021_2022    systemic
19. sc-bba653 sys_shock_crisis_2020_2022    systemic
20. sc-d72b95 sys_cascade_shock_drift_2020  systemic
21. sc-da1123 sys_drift_aging_2018_2024     systemic
22. sc-f520e5 mixed_drift_ip_vol_death      mixed
23. sc-f69eea drift_death_up_2018_2024      drift
```

Heldout split (24), then in this order:

```
sc-0ce4d6 trap_noise_drift_lookalike_b   noise_trap
sc-11135c ip_recovery_cardio_x04         recovery
sc-12be68 noop_neutral_controls          none
sc-21b383 sys_drift_diverge_2020_2023    systemic
sc-3411b2 sys_shock_inverse_2017_2019    systemic
sc-3627d2 sys_trend_tpd_ip_2015_2018     systemic
sc-62c222 volatility_ci_sigma_015        volatility
sc-696b93 shock_death_2016               shock
sc-6fe297 sys_shock_tpd_ip_2022          systemic
sc-73fd27 sys_drift_aging_2016_2019      systemic
sc-7e3a65 shock_ip_2018_2019             shock
sc-87e6e7 drift_ci_up_2021_2023          drift
sc-88fa33 volatility_tpd_sigma_04        volatility
sc-90a5be drift_ip_down_2020_2024        drift
sc-9db072 ip_recovery_mh_msk             recovery
sc-a15166 trap_noise_spike_lookalike_b   noise_trap
sc-a3e6a6 sys_shock_crisis_2015_2016     systemic
sc-c9d78b sys_cascade_drift_shock_2018   systemic
sc-ca7798 mixed_triple_ci_ip_mh          mixed
sc-e28a00 mixed_shock_tpd_drift_death    mixed
sc-e549ad ip_recovery_injury_x15         recovery
sc-e6ffa4 sys_vol_macro_2020_2024        systemic
sc-f19bae shock_ci_tpd_2015_2016         shock
sc-f916b9 drift_death_up_2015_2017       drift
```

## 9. Expected results reference (scenario 1, for calibration)

- Truth: shock on CI [2021,2022] ×1.4 (increase).
- Model (3/3 runs): CI / [2021,2022] / shock / increase, conf 0.95–0.97,
  magnitude ~+27–30% (~835 excess claims). Strict recall 3/3.
- False positives after fix: 0 in the current restored runs (an earlier
  generation had 1/3 — a factually true but non-control observation;
  sampling variation at temp 1.0). Before fix: 7 (5 phantom recoveries).
- Mean 13,660 completion tokens/run; prompt 2,479 tokens; all
  `finish_reason: stop`; leak gate clean; statelessness proven.
