# ⚖️ Life Insurance Experience Bench

*also known as **Data Pipeline Arena*** — an A/E experience-analysis benchmark for LLM agents

**Can an LLM spot what an actuary would spot in actual-versus-expected experience
data — and how much of what it finds is the model rather than the harness wrapped
around it?**

Two measured answers live here: the narrative write-up is
[docs/REPORT_qwen36_vs_qwen38.md](docs/REPORT_qwen36_vs_qwen38.md) and the full
locator, with every corpus and replication command, is
[docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md). The original design plan —
every locked decision, schema and guard, as written before any of it ran — is
[BENCHMARK_IMPLEMENTATION_GUIDE.md](BENCHMARK_IMPLEMENTATION_GUIDE.md).

---

## 🎯 Why This Project Exists — Four Purposes

This repo is not trying to win a leaderboard. It exists to answer a question that has
to be answerable before anyone lets a model near actuarial work: **what can it
actually see, what does it invent, and what do you have to build around it for the
result to be dependable?**

### 0 · Why this matters for governance

An A/E review is a control point. It sits between a book of experience and a pricing
or reserving decision, and it is exactly the judgement an auditor, an appointed
actuary or a regulator will ask about. If a model is going to sit anywhere near that
process — drafting experience commentary, flagging a line to investigate, triaging
forty portfolios a week — then "it usually looks right" is not a sign-off. Someone has
to be able to state, in writing, what it catches, what it misses, what it invents, and
how all three move when the model changes.

Every non-obvious design decision here follows from that requirement rather than from
convenience:

| Governance requirement | Mechanism in this repo |
|---|---|
| The answer key must be knowable | Ground truth is **generated**, never hand-labelled: every planted control is recorded in `data/truth/manifests/` |
| The answer key must not move after the exam | `data/eval/dataset.json` seals the model-facing tree; `data/truth/seal.json` is the sha256 commitment, written before any run and re-checked by the runner on every invocation |
| The model must not be able to read the answer | Opaque `sc-<6hex>` ids on the model-facing side; descriptive names and manifests live in a separate zone; a byte-level leak scan (`scripts/leakcheck.py`) runs at build time and again before the first prompt |
| Every model must sit the same exam | `dataset.json` hashes every model-facing file, so identical inputs are provable, not assumed |
| Tuning must not contaminate the reported number | `optimization` (23 books) and `heldout` (24 books) are disjoint by benefit × control × window × factor; the held-out split is mounted once and scored once |
| A score must be attributable to exact code | Every corpus ships `harness_snapshot/` + `MANIFEST.txt` with full sha256 of the pack, runner and prompt that produced it |
| Failures must stay visible | `sc-e6ffa4` is published as a **recorded failure** with a declined fix (INDEX §8), not patched into silence |

Governance is also why the unflattering numbers are in this README instead of a
footnote. The frozen harnesses scored **97.7 %** and **95.5 %** on the optimization
split; the same frozen harnesses on held-out data scored **69.1 %** and **64.2 %** — an
optimism gap of roughly 30 points for *both* models. Any sign-off taken from
tuning-set performance would have overshot by that much. A benchmark that only reports
its tuning set is not evidence.

### 1 · Measuring an LLM's ability to find insight in actuarial A/E data

Each of the 47 books is a set of A/E tables — actual versus expected claim counts by
benefit line (Death, CI, TPD, IP) and year, 2015–2024 — with patterns planted by
construction: drift, shock, volatility, a recovery-rate change, a lookalike that is
none of those, and clean books where any finding is a false alarm. The model must
return what an actuary would write up: **which line, which years, which pattern,
which direction, how large, how confident, on what evidence, and what action it
recommends** — as structured JSON, scored strictly (benefit + pattern + window overlap
+ direction must all agree; `PATTERN_EQUIV` is exact, so one wrong pattern word is both
a miss and a false alarm). The `recommended_action` field is deliberately part of the
answer: the point is the finding an actuary would escalate, not a labelled time series.
It is recorded in every corpus and, honestly, **not scored** — grading free-text advice
against a rubric is a separate, unsolved piece of this project.

**Claims A/E is the first surface, not the intended limit.** What is being tested is
the ability to look at an actual-versus-expected series over time and decide whether a
gap is signal — which is the same cognitive move in lapse and persistency A/E, expense
A/E, mortality and morbidity studies, and reserve-adequacy comparisons. Those surfaces
need a new scenario family and a new pack section in `stats_pack.py`; they do **not**
need a new benchmark, a new scorer, or a new governance argument. Scoring on
(insight recovered) and (insight invented) generalises as the surfaces do.

### 2 · Quantifying how much the harness is worth

This is the axis the project cares most about, and the two campaigns are the
experiment. Held-out split, 23 books like-for-like — **accuracy | FP/claim**, where
FP/claim is the share of everything the model said that was wrong, and
precision = 1 − FP/claim. `sc-e6ffa4` is excluded for *every* configuration because it
never completed under one of them (INDEX §8).

| model | no harness | own tuned harness | the *other* model's harness |
|---|---|---|---|
| Qwen3.6-27B | 59.5 \| 40.0 | **65.8 \| 38.7** | 64.9 \| 43.3 |
| Qwen3.8-27B | 64.0 \| 65.7 | **71.2 \| 41.9** | 70.3 \| 43.1 |

Read it as behaviour, not as a score race. Both subjects are 27 B models on one llama.cpp
slot with identical samplers. **The difference between Qwen3.6 and Qwen3.8 is not
architecture — it is what reinforcement learning taught each of them to do**: how they
reason, how much they verify before asserting, how eager they are to run code. The
harness is what has to compensate for that, and the numbers show it does so
differently:

- **3.8 unaided has excellent eyes and no restraint.** 64.0 % found but 65.7 % of its
  claims were false — **34 % precision**. Its failure is not seeing, it is saying.
  The harness moved it +7.2 points on recall and **+23.8 points on precision**.
- **3.6 unaided is the opposite failure.** 59.5 % found, already 60.0 % precision. Same
  harness, +6.3 recall and **+1.3** precision — because 3.6 did not have 3.8's problem
  to fix.
- **Each model finishes best with the harness tuned for it** (71.2 vs 70.3 for 3.8;
  65.8 vs 64.9 for 3.6). An earlier, prettier claim — that a harness tuned on one model
  transfers with +8.3 points — was measured at 9 books, decayed to −1 by 23, and was
  withdrawn.
- **Behaviour decides whether a harness feature even exists.** Both were offered up to
  4 sandboxed python calls. 3.8 used them in ~24 % of runs; **3.6 used them 0 times in
  144 held-out runs**, and two attempts to activate it failed. A capability you built
  for one model is decoration for the other.
- **Over-claiming is a separable behaviour.** Decomposing `FPs − misses` isolates false
  alarms not explained by a mislabel: +31 of 69 FPs invented under 3.8's own harness,
  +6 of 50 under 3.6's. 3.8 both mislabels and over-claims; 3.6 almost purely mislabels.

The conclusion the repo exists to record: **harness requirements evolve with model
behaviour, not with model weights.** A harness is not portable infrastructure you
qualify once and reuse; it is part of a model's deployment and has to be re-derived
whenever the behaviour underneath it changes. That is why this repo ships *two* harness
lineages that started from the same base and ended in different places, rather than one
blessed prompt.

### 3 · A first framework for building and testing the harness

The harness was not hand-written in one sitting. It was **built by a model** — the
operator-side agent that ran the campaigns was driven by a third model, DeepSeek
V4.1 Flash, deliberately **not** one of the two subjects, so no subject was grading its
own homework. It worked from artifacts rather than impressions, in a fixed loop:

1. run the frozen harness over all 23 **optimization** books → a corpus plus per-unit
   scorer output;
2. read what actually happened — the recorded prompt, the answer, the tool log, the
   scorer's per-unit diff — and name *why* each failed unit failed;
3. form **one** hypothesis, make **one** edit: a new section in `stats_pack.py`, a
   discipline clause in `HARNESS_RULES`, or a new pinned system prompt;
4. verify it on the affected books in a scratch corpus, then regression-check the
   neighbouring books the edit could have disturbed;
5. keep or revert, and snapshot the harness bytes **and** the prompt into
   `results/<corpus>/harness_snapshot/` before the next run;
6. never tune against `heldout`, and never feed a held-out result back into an edit.

What that produced: seven harness versions (v1.0 → v1.6e) driven by **307
per-scenario diary entries**, 268 of which involved a harness review or edit; and, for
the other subject, two kept edits from the same base. Both lineages are frozen in the
repo, so the framework can be inspected, not just described — and so a later reader can
see the edits that were *declined* (runbook §36) as well as the ones kept.

Two honest caveats. First, the loop was steered by a human who chose which failures to
pursue; the model proposed and applied edits, it did not set the agenda. Second, the
frozen record proves **which harness bytes produced which numbers**, not which model
wrote each edit — `harness_snapshot/MANIFEST.txt` is the provenance for the former and
the runbooks narrate the latter. Authorship attribution is not part of the evidence.

---

## ✅ Status — measured benchmark, unpackaged core

**What exists as code** is the experiment stack under [`scripts/`](scripts/):
the deterministic scenario generator, the evidence-pack harness
([`scripts/stats_pack.py`](scripts/stats_pack.py)), the runner with its
sandboxed python tool loop ([`scripts/run_zero_shot.py`](scripts/run_zero_shot.py)),
the scorer ([`scripts/score_xam.py`](scripts/score_xam.py)) and the freeze gate.
Two full model campaigns were run with that stack, and every published number
comes from it. If you want results and replication commands, open
[docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md) or
[docs/REPORT_qwen36_vs_qwen38.md](docs/REPORT_qwen36_vs_qwen38.md).

**What was never built** is the packaged arena core this README originally
announced: there is no `pyproject.toml`, no `src/abench/` package and no
`abench` CLI. The milestones **M0–M4** below describe a design that the
script-level implementation satisfied without being packaged. Those sections are
kept as design context, labelled as such, rather than rewritten after the fact.

---

## 📦 What ships in a clone, and what you regenerate

| content | size | note |
|---|---|---|
| code + docs + config + tests | ~0.6 MB | everything needed to run and score |
| `results/` corpora + `harness_snapshot/` | 102 MB | the only byte-exact provenance this project has |
| `data/eval/**/artifacts/` | 31 MB | what the prompt and `stats_pack` actually read |
| `data/truth/` | 236 KB | planted controls, so a third party can score |
| **clone total** | **~135 MB** | largest single file 0.41 MB |

Deliberately **excluded**, because they are regenerable and never read by the
prompt body: `data/eval/**/exposure.csv` (2.1 GB),
`data/eval/**/*_claims.csv` (239 MB) and `data/raw/` (2.9 GB). To rebuild them, see
**Where the data comes from** below.

**One reproduction caveat, stated up front:** `build_prompt()` lists every file in
a scenario directory, so a clone that lacks the excluded classes builds prompts
that differ byte-wise from the published corpora. The preflight integrity gate
still passes, because it only re-hashes files that exist — so a reduced clone
*runs*, and reproduces the published scores; do not chase a prompt-hash mismatch
until you have regenerated the full tree.

The published dataset was generated by generator commit **`66a73d0`** (recorded
per book in `data/raw/<id>/run_info.json`, which is local-only — that path is not
shipped).

---

## 🏭 Where the data comes from, and how to generate it yourself

Every book in this benchmark is produced by a **separate public project**:

> **[Synthetic_Life_Insurance_Data_Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)**
> — a deterministic, pure-Python generator of synthetic Australian life-insurance
> claims experience (Death, CI, TPD, IP) with Actual/Expected analysis built in. It is
> driven from a single typed assumptions object, so baseline A/E ≈ 1.0 by construction
> and every planted control is a date-bounded edit to the *actuals* only.

The two-repo split is deliberate: the generator is a data tool with its own release
cycle and its own docs; the arena is the exam built on top of it. The arena never
reimplements it — `scripts/generate_scenarios.py` imports the generator as a library
and calls its pipeline once per scenario.

### Step 1 — put the generator where the arena looks for it

`generate_scenarios.py` resolves the generator as a **sibling directory** with a fixed
name:

```python
GEN_ROOT = ARENA_ROOT.parent / "Life_insurance_data_generator_new"   # scripts/generate_scenarios.py
```

There is no flag or environment variable to override it, so clone it under that name:

```bash
cd data_pipeline_arena/..
git clone https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator.git \
    Life_insurance_data_generator_new
```

### Step 2 — dependencies

| what you run | needs |
|---|---|
| evidence pack, runner, scorer, gate, preflight, leak scan | **nothing** — stdlib only, Python ≥ 3.11 |
| `generate_scenarios.py` (reading the registry, `--split-only`) | `PyYAML ≥ 6` |
| `generate_scenarios.py` (actually generating) | `numpy ≥ 1.26`, `pandas ≥ 2.0`, `pydantic ≥ 2.5`, `PyYAML ≥ 6` — the generator's own dependencies, Python ≥ 3.11 |

The arena puts `<generator>/src` on `sys.path` itself, so `pip install -e` of the
generator is optional. What is **not** optional is running the script with an
interpreter that has those packages — the simplest correct invocation is the generator's
own environment:

```bash
../Life_insurance_data_generator_new/.venv/bin/python scripts/generate_scenarios.py --scale full
```

### Step 3 — generate

> ⚠️ **Read this before the first `--scale` you run on a fresh clone.** Assembly
> **deletes and rebuilds** the scenario directories under `data/eval/` and rewrites
> `data/truth/`. A published clone already contains the exact 47 books every number in
> this repo was measured on, so `--scale tiny` there replaces the real exam with a
> 5 000-policy one and re-seals the truth store. Recover with
> `git checkout -- data/eval data/truth`, or do experiments in a scratch clone. The scale
> guard in the script protects `data/raw/` from mixing scales; it cannot protect a clone
> that has no `data/raw/` yet, which is exactly the fresh-clone case.

```bash
python3 scripts/generate_scenarios.py --scale tiny      # 5k policies — registry smoke pass
python3 scripts/generate_scenarios.py --scale medium    # 25k policies — registry default
python3 scripts/generate_scenarios.py --scale full      # 250k policies — what is published, ~1 h
```

Useful flags: `--only <ids>` (subset), `--force` (regenerate raw stores that exist),
`--split-only` (skip generation, rebuild `data/eval` + `data/truth` from the raw stores
already on disk — this needs no pandas and no generator), `--no-checks`, `--force-split`.

Scale presets live in [`config/scenarios.yaml`](config/scenarios.yaml), which is the
**single source of truth** for the 47-book set: the script hard-codes no scenario, and
`config/scenarios.d/*.yaml` is merged in if present.

### Step 4 — what lands where

| path | role | shipped? |
|---|---|---|
| `data/raw/<descriptive_id>/` | the lab view — full store + `metadata.json` + `run_info.json` (scale, seed, targets, generator commit) | ❌ regenerable, 2.9 GB |
| `data/eval/{optimization,heldout}/<sc-xxxxxx>/` | **ZONE A**, model-facing, opaque ids | ✅ `artifacts/` yes, bulk CSVs no |
| `data/truth/` | **ZONE B** — `id_map.csv`, `id_key.json`, `manifests/`, `seal.json`; scorer-only | ✅ published so you can score |

Nothing reaches the model-facing tree without passing a per-scenario sanity gate *and*
a byte-level leak scan; the build fails on any hit, and the runner re-checks before its
first API call.

### Step 5 — reproducing the published corpus exactly

| pin | value |
|---|---|
| generator commit | **`66a73d0`** (recorded per book in `data/raw/<id>/run_info.json`) |
| seed | `42` (the generator is bit-deterministic: same scenario id ⇒ same bytes) |
| scale | `full` — 250 000 policies; claim targets 5000 / 12000 / 8000 / 15000 for Death / CI / TPD / IP |
| registry | `config/scenarios.yaml`, 47 books (23 optimization / 24 heldout) |

After regenerating, the checks that tell you the tree is sound:

```bash
pytest tests/                        # registry invariants: split disjointness, manifest contract, scale presets
bash scripts/harness_preflight.sh    # leak scan + integrity + seal match, zero API calls
```

### If you only cloned this repo

That is the normal case, and it is fully usable. The published `data/eval/**/artifacts/`
tree is exactly what the prompt and the evidence pack read, so scoring, gate, preflight
and pack-building all work offline with no generator installed. Only
`generate_scenarios.py` needs the sibling project. See the caveat in
**What ships** above about why a reduced clone builds byte-different prompts.

### Adding your own scenario

Append an entry to `config/scenarios.yaml` (or drop a file in `config/scenarios.d/`)
with controls inside the generator's validated ranges — drift slope ∈ [−0.9, 5.0],
volatility σ ∈ [0, 1.0], shock and recovery factors > 0 — then regenerate and re-run
`pytest tests/` plus the preflight. The split-disjointness check will refuse a
held-out book that overlaps an optimization book on benefit × control × window × factor,
which is the guard that keeps the exam honest as the catalog grows.

---

## 🧾 What the exam asks of a model

A subject gets one scenario directory of A/E CSVs and one turn. It may answer straight
from what it is shown, or spend up to four sandboxed python calls re-cutting the
numbers itself. It returns one JSON answer; the scorer expands each planted control to
a **unit** (a book-wide control becomes four units, one per benefit line) and a unit is
a hit only if benefit, pattern, window and direction all agree.

The campaign measured two things at once, and they need to be kept apart when reading
any number in this repo:

| axis | question | where it is answered |
|---|---|---|
| **subject** | can Qwen3.6-27B / Qwen3.8-27B find what was planted, without inventing? | [the report](docs/REPORT_qwen36_vs_qwen38.md), INDEX §6 |
| **harness** | how much of that is the evidence pack, the rules block and the prompt, and does it transfer? | purposes 2–3 above; INDEX §3, §5–6 |

The planned Stage-2 variant — the model writing and iterating its own *pipeline* over
many turns — was never built; what was built is the single-turn evidence-pack harness
described above. The design intent is preserved in the guide and summarised below.

### What This Proves

| Capability | Status |
|-----------|--------|
| Deterministic scenario generation + disjoint split, ground truth generated not curated | ✅ **built and used** — 47 books, sealed, leak-gated |
| Structured verdict contract, malformed = miss | ✅ **built and used** — JSON, `strict=False` parser tolerance |
| Evidence pack + rules block + pinned prompt, versioned and snapshotted | ✅ **built and used** — two lineages, frozen hashes |
| Strict scoring (benefit × pattern × window × direction) with FP accounting | ✅ **built and used** — scorer v3 |
| Frozen-pipeline provenance (hash the exact bytes that produced a number) | ✅ **built and used** — `harness_snapshot/` + `MANIFEST.txt` |
| Sandboxed free-code *pipeline construction* (Stage 2, ≤5 iterations, frozen submission) | 📐 Specified (M1/M2), **not built** — shipped harness is 1 turn + ≤4 analysis tool calls |
| Window IoU and magnitude-error scoring | 📐 Specified (M0), **not built** — scoring is strict hit/miss, no partial window credit |
| N×K median + spread reporting | 🟡 **partial** — runs × repetitions happen and are summed; median-of-N with spread was never wired up |
| Stage-3 report + blind human validation + golden set | 📐 Specified (M3), **not built** |
| Packaged `abench` CLI (`pyproject.toml`, `src/abench/`) | 📐 Specified (M0–M4), **not built** — `scripts/` only |

---

## 📋 Quick Navigation

<details>
<summary><strong>🚀 Quick Start</strong> — the commands that actually run</summary>

```bash
# No install step for the harness: pack, runner, scorer and gate are stdlib-only.
# (Only generate_scenarios.py needs PyYAML + the sibling generator project.)
bash scripts/harness_preflight.sh                       # leak + integrity gate, zero API calls
python3 scripts/stats_pack.py data/eval/optimization/<sc-id> --text   # print one evidence pack
python3 scripts/score_xam.py results/<corpus>/zero_shot --json-out /tmp/scores.json
python3 scripts/harness_gate.py results/<corpus>/zero_shot --split heldout --runs 3
```

> Point `--json-out` somewhere outside `results/` unless you mean to overwrite a
> published `scores.json`. **Do not run `generate_scenarios.py` on a fresh clone**
> without reading [Step 3](#step-3--generate) first: assembly rebuilds `data/eval/`
> and `data/truth/` in place, which replaces the published exam.

Anything that *answers* a scenario needs a live OpenAI-compatible endpoint
(`--base-url`); the scorer, gate, leak scan and pack builder all run offline.
Full replication commands — single book, unattended 23-book pass, held-out exam
with retry wrapper — are in [docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md) §7.

> A `pip install -e .` packaged CLI (`abench init|generate|run|score|report|validate`)
> remains the planned interface from guide §10 and was never wired up; see
> **Status** above.

</details>

<details>
<summary><strong>🧪 The Three Stages</strong> — the plan, and what actually ran</summary>

| Stage | What happens | Status |
|-------|--------------|--------|
| **Stage 0 — Data** | Deterministic scenario generation + disjoint `optimization`/`heldout` split (no LLM) | ✅ built — 47 sealed, leak-gated books |
| **Stage 1 — Zero-shot** | Model returns one JSON verdict from the artifacts alone — no pipeline | ✅ built, and this is what every published number comes from |
| **Stage 1+ — Evidence-pack harness** | *Not in the original plan.* Deterministic stats pack + rules block + pinned prompt + ≤4 sandboxed python calls, iterated by an operator-side agent over optimization passes | ✅ built — the axis the study is about |
| **Stage 2 — Free-code pipeline** | Model writes & iterates its own detector pipeline over 3–5 rounds on optimization-set feedback, then a frozen submission | 📐 Specified (M1/M2), **never built** |
| **Stage 3 — Report** | Deterministic `report.md` + blind human validation | 📐 Specified (M3), **never built** |

The shipped harness differs from planned Stage 1 in one way that matters for
governance: it is **one turn with up to four analysis tool calls**, not a multi-turn
agent that builds and refines a pipeline. Conclusions here are about how much a
static evidence pack + rules + prompt are worth, not about long-horizon autonomy.
**Locked guarantees** (guide §2) — and what happened to each of them in practice:

| guarantee | status |
|---|---|
| Ground truth is always *generated*, never hand-curated | ✅ honoured |
| Heldout set mounted once, scored once, never fed back | ✅ honoured — the held-out split is spent |
| Malformed verdict JSON is scored as a miss | ✅ honoured, with `strict=False` tolerance for raw control characters (INDEX §8) |
| Median + spread over N×K runs | ⚠️ **not built** — runs were summed into a single accuracy, so per-book variance is visible in `scores.json` but median/spread was never reported |
| Two cheap baselines always shown | ⚠️ **partial** — the no-harness zero-shot baseline of the same model exists (`xam_q36`, `xam_v5`); the classical control-chart / CUSUM detector was never implemented |

</details>

<details>
<summary><strong>🎛️ Scenario Controls</strong> — what gets planted</summary>

Four primitive controls, planted by the generator into the actuals only:

| Control | Effect | Observable signature (starter set from guide §5.3) |
|---------|--------|------------------------------------|
| **Drift** | Per-year slope on a benefit's A/E | `drift_death_up_2018_2024`: Death A/E ~0.74 → 1.30 in 2018–24 |
| **Shock** | One-off multiplier over a window | `shock_covid_2020_2022`: Death spike 1.31/1.34/1.25 in 2020–22 |
| **Volatility** | Per-year σ noise on claim counts | `volatility_ip_sigma_03`: IP count variance ×3, level unchanged |
| **IP recovery** | Termination-rate multiplier (IP) | `ip_recovery_mental_health_x2`: MH termination A/E ≈ 2.0, incidence untouched |
| **No-op** | All neutral | `noop_neutral_controls`: bit-identical to `baseline` |

The shipped 47-book catalog composes those primitives into eight **families**, and it is
the families the taxonomy of a *finding* keys on:

| family | what is planted | held-out count |
|---|---|---|
| `drift` | sustained multi-year movement | 3 |
| `shock` | abrupt single-year or few-year level change | 3 |
| `volatility` | increased year-to-year dispersion, flat level | 2 |
| `recovery` | IP termination-rate recovery | 3 |
| `systemic` | coordinated multi-line event, 2–4 lines at once | 8 |
| `mixed` | two or more different events in one book | 2 |
| `noise_trap` | a *lookalike* — reads as drift or a spike, the truth is volatility | 2 |
| `CLEAN` | nothing planted; any finding is a false alarm | 1 |

`systemic` is where the models actually differ; drift, recovery and volatility saturate
for every harnessed configuration, and `noise_trap` is hard for all of them
(INDEX §6). The full catalog is in [docs/scenario-catalog.md](docs/scenario-catalog.md).

</details>

<details>
<summary><strong>📐 Scoring Metrics</strong> — what "good" means</summary>

**What scorer v3 actually computes** (`scripts/score_xam.py`), and what the campaign
reports — a *unit* is one (control × run) pair, with a book-wide control expanded to
one unit per benefit line:

| Metric | Definition |
|--------|-------------|
| **accuracy (recall)** | strict hits / units — did it find what was there? |
| **FP/claim** | false positives / claims emitted — is it trustworthy when it speaks? |
| **precision** | hits / claims = 1 − FP/claim |
| **strict match** | benefit + pattern + window overlap + direction all agree; `PATTERN_EQUIV` is exact, so one wrong pattern word is a miss **and** a false alarm |
| **FP/run, FP/unit** | diagnostics only, deliberately not headline numbers |

Accuracy and FP/claim have different denominators and never sum to 100 %: within the
units ledger `accuracy + miss-rate = 100 %`, within the findings ledger
`precision + FP/claim = 100 %`.

**Planned but not built**: window IoU, magnitude error against the injected factor,
type accuracy as a separate axis (it is folded into strict matching), no-op correctness
as a named metric (it appears as the `CLEAN` family's FP count), and the effort metrics
(token and wall-clock counts are recorded per run, iteration count and human
interventions are not).

</details>

<details>
<summary><strong>📁 Project Structure</strong> — as it exists</summary>

This is the shipped tree. The guide's §10 layout (a packaged `src/abench/` with an
`abench` CLI) was never built; where that plan differed from reality, reality won.

```
data_pipeline_arena/
├── README.md                           # this file
├── BENCHMARK_IMPLEMENTATION_GUIDE.md   # the original plan, annotated plan-vs-built
├── config/
│   └── scenarios.yaml                  # the 47-book registry — single source of truth for the dataset
├── scripts/                            # 30 modules: generator driver, stats pack, runner, scorer, gate, drivers
├── docs/                               # EXPERIMENT_INDEX, REPORT, HARNESS_GROWTH, dataset + design refs
├── tests/test_registry.py              # registry + split-invariant tests (the only unit tests)
├── data/
│   ├── raw/                            # generated stores + run_info (local-only, regenerable)
│   ├── eval/                           # ZONE A: model-facing, opaque ids  [{optimization,heldout}/<sc-x>/]
│   └── truth/                          # ZONE B: manifests + id map + seal (scorer-only, published)
└── results/<corpus>/                   # zero_shot/, scores.json, scoreboard.txt, prompts/, harness_snapshot/

# from the guide's plan, never built:  pyproject.toml · src/abench/ · submissions/ · human_review/
```

</details>

<details>
<summary><strong>🛡️ Sandbox & Fairness</strong> — guards that must not be skipped</summary>

> **This section is the design, not the implementation.** What ships is neither
> Tier: `run_sandboxed_python()` is `python -I -c` with `cwd=artifacts/`, a 10 s
> wall timeout and a 4000-char output cap — no rlimits, no network block, no
> filesystem jail (see Limitations). The leakage guard below *is* implemented and
> runs on every invocation.

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

- **Not packaged, and single-purpose** — the scorer, gate and runner exist as
  `scripts/` modules wired for this benchmark, not as a reusable library or CLI.
  The **scenario dataset pipeline is implemented and generating**
  (`scripts/generate_scenarios.py`).
- **The sandbox is advisory, not enforced.** `run_sandboxed_python()` runs
  model-authored python as `python -I -c` with `cwd=artifacts/`, a 10 s timeout
  and a 4000-char output cap. There is no `setrlimit`, no network block and no
  filesystem jail, so "never read outside `artifacts/`" is a request in the rules
  text, not a control. All 97 recorded tool calls stayed inside the artifacts
  directory, but nothing prevented traversal — read the results with that in mind.
- Synthetic claims data from the
  [generator project](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator);
  no real policyholder or company data, and no real portfolio.
- Patterns are **planted by design** — a "hit" means recovering a known signal from the
  manifest, not discovering an unknown one. Real A/E review involves judgement calls with
  no answer key, and this benchmark cannot measure that.
- **Two seeds of evidence for the harness claim.** "Harness must be re-derived per model"
  is supported by a 2×2 matrix of two models × two harnesses on 23–24 books. That is a
  real signal and a real cost to reproduce, but it is n = 2 subjects on one serving
  stack — not a general theory of harness portability.
- **The held-out split is spent.** These 24 books are now published together with their
  answers, so they can no longer function as an unseen exam for any model that reads
  this repo. A new exam needs `generate_scenarios.py` with fresh controls.
- Two units are **not model failures** and are documented as benchmark artifacts:
  `sc-d72b95` plants a drift of +0.0253/yr with SE 0.0251 (t = 1.01; minimum detectable
  slope +0.088) and `sc-f520e5` is genuinely ambiguous (volatility F = 17.1 *and* a real
  level excursion).
- LLM non-determinism is **controlled, not eliminated**: temperature 1.0 sampling, three
  runs summed rather than median + spread, so run-to-run noise is folded into the totals
  rather than reported around them.

</details>

<details>
<summary><strong>📊 Dataset</strong> — the generated arena scenarios</summary>

The arena's input data is generated by the sibling project
**[Synthetic_Life_Insurance_Data_Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)**,
driven by [`scripts/generate_scenarios.py`](scripts/generate_scenarios.py) and the
scenario registry [`config/scenarios.yaml`](config/scenarios.yaml). Full instructions —
clone layout, dependencies, scales, reproducibility pins — are in
**[Where the data comes from](#-where-the-data-comes-from-and-how-to-generate-it-yourself)**.

| Property | Value |
|---|---|
| Scenarios | 47 (23 optimization / 24 heldout) |
| Families | none, drift, shock, volatility, noise_trap, recovery, mixed, systemic |
| Split discipline | disjoint by (benefit × control type × window × factor) |
| Scale | `tiny` 5k / `medium` 25k / `full` 250k policies — the published set is `full`, seed 42 |
| Model-facing (ZONE A) | `data/eval/` — opaque scenario ids (`sc-<6hex>`), no answer-bearing names; `dataset.json` hashes + seal |
| Ground truth (ZONE B) | `data/truth/manifests/` (scorer-only, sealed via `seal.json`) — published, so a third party can score |
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

**Results and evidence — read these:**

- [Experiment index](docs/EXPERIMENT_INDEX.md) — **the master locator**: benchmark,
  harness, both campaigns, every corpus and its path, final tables, replication
  commands, known failures
- [Cross-model report](docs/REPORT_qwen36_vs_qwen38.md) — the standalone write-up:
  method, results by model and family, the `sc-e6ffa4` failure, cost analysis
- [Harness growth diary](docs/HARNESS_GROWTH.md) — how Qwen3.8's harness grew,
  version by version
- [Campaign runbook](results/logs/harness_q36_next_steps.md) — §1–37 of the Qwen3.6
  campaign: every pass, decision and declined fix
- [3.8 optimization diary](results/logs/harness_opt_loop.md) — the per-scenario diary
  (4,750 lines) behind the seven harness versions

**Design and data reference:**

- [Implementation guide](BENCHMARK_IMPLEMENTATION_GUIDE.md) — the original plan:
  locked decisions, schemas, stages, sandbox and scoring design, with a
  plan-vs-built header
- [Dataset usage](docs/dataset-usage.md) — generate/extend the dataset; registry
  format; CLI reference; manifests
- [Scenario catalog](docs/scenario-catalog.md) — all 47 scenarios, families, splits,
  planted controls (lab-side: it prints the descriptive names)
- [Architecture](docs/architecture.md) — dataset pipeline design, invariants,
  extension points
- [Assumptions reference](docs/assumptions-reference.md) — manifest, verdict contract,
  scoring rubric, split and sandbox rules

**Historical / planning documents** (accurate as records, superseded as instructions):

- [Usage guide](docs/usage.md) — the *planned* `abench` CLI and `experiment.yaml`,
  never wired up
- [M0 handover](docs/m0-handover.md), [zero-shot experiment](docs/zero-shot-experiment.md),
  [handover: run scenarios](docs/HANDOFF_RUN_SCENARIOS.md),
  [review & results](docs/review-and-results.md)

</details>

<details>
<summary><strong>🧪 Testing</strong></summary>

```bash
pytest tests/                              # registry + invariant tests (dataset pipeline)
bash scripts/harness_preflight.sh          # leak + integrity gate, zero API calls
```

> `pytest` is the only test-time dependency, and it is not in a bare interpreter: on this
> machine the working invocation is
> `../Life_insurance_data_generator_new/.venv/bin/python -m pytest tests/` (9 tests, all
> passing). `harness_preflight.sh` is pure stdlib and needs nothing.

> `abench validate` (schema + split-separation self-checks) was planned for M0
> and never built; the runtime equivalent is the preflight gate above, which
> every run executes before its first API call.

**Current test status**: the dataset pipeline's registry invariants
(disjointness, manifest contract, scale presets) are covered by
[`tests/test_registry.py`](tests/test_registry.py) — all passing. The generator
also runs per-scenario sanity checks with a hard gate before `data/eval/` is
written, and every assembly must pass the byte-level leak scan
([`scripts/leakcheck.py`](scripts/leakcheck.py)) — the build fails on any hit.
The remaining acceptance test plan (end-to-end smoke, fairness,
baseline-sanity for the arena core) is specified in
[Review & results](docs/review-and-results.md).

**What is not tested:** `stats_pack.py`, `score_xam.py`, `harness_gate.py` and
`leakcheck.py` have no unit tests. Their correctness is carried by the runtime
preflight gate, the freeze gate, and the frozen corpora themselves — so any change
to those four files must be validated by regenerating all 23 optimization packs
and diffing them, as every campaign edit in `results/logs/` was.

</details>

<details>
<summary><strong>📄 License</strong></summary>

**No LICENSE file has been added to this repository yet.** The intention recorded in
the original plan is MIT, and this README says so, but until a `LICENSE` file is
committed treat all rights as reserved by the authors and ask before redistributing.
(Tracked as an outstanding item, not an oversight of the release.)

The scenario data is **synthetic** — generated, with no real policyholders or company
records — and is provided for research, learning and testing.

**Acknowledgments**: the
[Synthetic Life Insurance Data Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)
project, which produces every book in the arena.

</details>

---

## 📬 Feedback

Questions, corrections, and "your scorer is wrong about X" are welcome — the record of
every decision, including the fixes that were deliberately *not* applied, is in
[results/logs/harness_q36_next_steps.md](results/logs/harness_q36_next_steps.md) and
[docs/EXPERIMENT_INDEX.md](docs/EXPERIMENT_INDEX.md), so disagreements can be argued
against the evidence rather than against a summary.

---

*Last updated: 2026 | Status: 47-scenario dataset + script-level harness shipped and measured across two model campaigns (Qwen3.6-27B, Qwen3.8-27B); the packaged `abench` core of milestones M0–M4 was never built*
