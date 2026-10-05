# EXPERIMENT INDEX — Data Pipeline Arena, Qwen3.6-27B vs Qwen3.8-27B

**Start here.** This file is the master index: the benchmark, the harness, both model
campaigns, every result corpus, and the replication commands. It assumes no prior context.
You should be able to work out what was done, why, and where the evidence lives.

Last updated: end of the Qwen3.6-27B campaign and the cross-model harness matrix.

**Why these two campaigns exist.** Short version; the full argument is in
[README § The Study Behind It](../README.md#-the-study-behind-it--four-questions-this-has-to-answer).

0. **Govern the model and its pipeline.** How good is the model at experience-study work,
   what does it cost, and is the pipeline around it right or in need of updating?
1. **Measure the model's eye.** Can an LLM find an actuarial insight in A/E data?
2. **Measure the harness.** What is it worth, and does it transfer? Qwen3.6 and Qwen3.8
   have the same size and architecture, so everything that differs between them is
   behaviour learned by reinforcement — exactly the thing that decides what a harness has
   to do.
3. **Record a reusable method** for building a harness from model evidence.

Sections 2–6 hold the evidence for 1 and 2. Section 3 and the runbooks hold the method
for 3.

---

## 1. What the benchmark is

A synthetic life-insurance experience-analysis task. Each **scenario** ("book") is a
set of CSVs of actual-vs-expected claim counts across four benefit lines — **Death,
CI (critical illness), TPD (total permanent disability), IP (income protection)** —
over 2015-2024. Anomalies are planted by construction, and the model must report them
as structured JSON:

```json
{"scenario_id": "...", "overall_assessment": "anomalies"|"clean",
 "findings": [{"benefit","years","pattern","direction","magnitude","confidence",...}]}
```

**47 scenarios total: 23 optimization + 24 held-out.** The optimization split is for
tuning; the held-out split is the exam and must not be tuned against.

**Scenario families** (the "question type"), and what each plants:

| family | what is planted | held-out count |
|---|---|---|
| `drift` | sustained multi-year movement | 3 |
| `shock` | abrupt single-year (or few-year) level change | 3 |
| `volatility` | increased year-to-year dispersion, flat level | 2 |
| `recovery` | IP termination-rate recovery | 3 |
| `systemic` | coordinated multi-line event (2-4 lines together) | 8 |
| `mixed` | two or more different events in one book | 2 |
| `noise_trap` | a *lookalike* — the line looks like drift/spike but the truth is volatility | 2 |
| `CLEAN` | nothing planted; any claim is a false alarm | 1 |

**Scenario ids are opaque** (`sc-<6hex>`). Truth lives only in
`data/truth/manifests/<sc-id>.json` and is **experimenter-side only — it must never
appear in a prompt.** Note the manifest's `scenario_id` field holds the *descriptive*
name (`shock_death_2016`); the opaque id is the **filename**. Key by filename.

### How the data were generated

A separate public project generates every book:
**[Synthetic_Life_Insurance_Data_Generator](https://github.com/jasonzheshiou/Synthetic_Life_Insurance_Data_Generator)**.
`scripts/generate_scenarios.py` drives it from the registry `config/scenarios.yaml`, one
deterministic run per book. Published pins: scale `full` (250 000 policies), seed 42,
generator commit **`66a73d0`**. To regenerate it yourself, use
[README § Where the data comes from](../README.md#-where-the-data-comes-from-and-how-to-generate-it-yourself).

The truth manifest records what was planted: `controls[]` with `benefit`, `type`,
`window`, `factor`, and `signature.direction`. A book-wide control has `benefit: "all"`,
which the scorer expands to **one unit per benefit line (4 units)**.

The split is fixed and must not change: every corpus in `results/` was scored against
these same 47 books with these same planted controls.

---

## 2. How scoring works

`scripts/score_xam.py` (scorer v3) computes, per run:

* **unit** = one (run, control-or-expanded-benefit) pair. `units = controls × runs`.
* **hits (strict)** = findings matching a unit on **benefit + pattern + window
  overlap + direction**.
* **loose** = benefit + pattern only. A unit counts as a hit **only if strict**.
* **FP (false positive / false alarm)** = any finding that does not strictly match a
  unit — including near-misses and pattern mismatches.
* `PATTERN_EQUIV` is **exact**: drift↔drift, shock↔shock, volatility↔volatility,
  recovery↔recovery. One wrong pattern word turns a hit into a miss **and** an FP.

### Reporting standard (adopted late in the campaign — use it)

| metric | formula | denominator | answers |
|---|---|---|---|
| **accuracy (recall)** | strict hits / units | units = controls × runs | did it find what was there? |
| **FP/claim** | FPs / claims emitted | claims = hits + FPs | is it trustworthy when it speaks? |
| precision | hits / claims | = 1 − FP/claim | |

Secondary, keep as diagnostics only: `FP/run` (FPs ÷ runs) and `FP/unit` (FPs ÷ units).

**Why FP/claim and not FP/run:** a model can flood claims to inflate recall; `FP/run`
shows the absolute noise but not that the noise now dominates the output. FP/claim is
normalised by what the model actually said. Do **not** convert FP/unit or FP/claim to
percentages of each other — accuracy and FP/claim have different denominators and
never sum to 100 %. Within the *units* ledger, `accuracy + miss-rate = 100 %`; within
the *findings* ledger, `precision + FP/claim = 100 %`.

---

## 3. The harness

"Harness" = everything wrapped around the model. Three components:

1. **Evidence pack** — `scripts/stats_pack.py`. Deterministic statistics computed from
   the scenario CSVs (per-line trend, step, excursions, onset ratio, overdispersion,
   longest run, smoothed 3-yr MA, tail segment, cross-line swings). Appended to the
   user turn. Leak-gated: it must not contain the taxonomy words or truth.
2. **Rules block** — `HARNESS_RULES` inside `scripts/run_zero_shot.py`. Defines the
   taxonomy (drift / shock / volatility / recovery), the output schema, discipline
   clauses, and offers ≤4 sandboxed Python tool calls.
3. **Prompt** — the system message. In this campaign it is a **file**, injected by
   `scripts/run_zero_shot_baseline_v2.py` via `PINNED_PROMPT_FILE`, so a model can
   evolve its own prompt without editing the runner.

### Who builds the harness

Neither subject wrote its own harness. An operator-side agent built both lineages, running
on **DeepSeek V4.1 Flash** — a third model, deliberately not one of the two subjects, so no
model tuned the exam it later sat. Each pass:

1. Run the frozen harness over all 23 **optimization** books.
2. Score it, then read the evidence per unit — recorded prompt, answer, tool log, the
   scorer's per-control diff — and say why each miss missed.
3. Turn that into **one** hypothesis and **one** edit: `stats_pack.py`, `HARNESS_RULES`, or
   a new pinned prompt file.
4. Test it on the affected books in a scratch corpus (`harness_q36_step*`), then re-check
   the neighbours it could have disturbed (`harness_q36_regress`).
5. Keep or revert. Snapshot code **and** prompt into
   `results/<corpus>/harness_snapshot/`.
6. Never read a held-out result before deciding an edit, and never feed one back.

The corpus names in section 5 are this loop: `harness_opt_p1..p7` and `harness_q36_p1..p4`
are harness passes; `harness_q36_step*` are single-book tests of one hypothesis each; the
two `*_final*` corpora are the exams after the tuning.

Two limits: a human chose which failures to pursue, and the frozen record proves which
harness **bytes** produced which numbers (`MANIFEST.txt`), not which model wrote each line.

### Harness versions

Qwen3.8's line: **v1.0 → v1.1 → v1.2 → v1.3 → v1.4 → v1.5 → v1.6e**, built over 7
optimization passes plus **307 per-scenario diary entries** (268 involving a harness
review/edit). Every pass p3→p7 changed **both** harness files. `stats_pack.py` grew
27,229 → 38,490 bytes in that span.

**v1.6e is the frozen 3.8 harness.** Its exact bytes are preserved in:
* `results/harness_opt_p7/harness_snapshot/` — `stats_pack.py` `16e53e0ef0b097ab`,
  `run_zero_shot.py` `a4b967de975625f9`
* `results/harness_final/harness_snapshot/` — identical

### Harness file hashes seen in this campaign

| file | hash prefix | meaning |
|---|---|---|
| `stats_pack.py` | `16e53e0ef0b097ab` | v1.6e (frozen 3.8 pack) |
| `stats_pack.py` | `feababaf9eb5ebaa` | v1.6e + cross-line wording fix |
| `stats_pack.py` | `8bd4c07be285bf51` | **current** — v1.6e + 3.6 edits (smoothed-window, cross-line, onset caution + coordination guard) |
| `run_zero_shot.py` | `a4b967de975625f9` | v1.6e (frozen 3.8 runner) |
| `run_zero_shot.py` | `98411194093cdd0c` | **current** — v1.6e + `strict=False` parser tolerance |

---

## 4. Models and serving

| | |
|---|---|
| models | `Qwen3.8-27B-Q8_0` (also advertised as `Qwen3.8-27B`), `Qwen3.6-27B` |
| endpoint | `http://192.168.1.59:8080/v1` (llama.cpp, build `b10802-d1a92352c`) |
| slots | **1** — one generation at a time. Never run two clients concurrently |
| samplers | temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence 0.0, repetition 1.0 |
| other | stream always; **never** set max_tokens; per-call timeout 3600 s; `WAIT_ENDPOINT=1800` |

**Hidden behaviour worth knowing:** Qwen3.6-27B **never uses the tool** — 0 calls in
144 held-out runs. Its tool loop is dormant. Qwen3.8-27B uses tools in ~24 % of runs.
This asymmetry drives several results below.

---

## 5. Result corpora — where everything is

All corpora follow `results/<name>/zero_shot/<sid>_runNN.json` (plus `scores.json`,
`scoreboard.txt`, `prompts/*.md`, and `harness_snapshot/`). "runs" = records.

### Baselines (no harness, prompt 3053 chars)

| corpus | model | books × runs | note |
|---|---|---|---|
| `results/xam_v5/` | 3.8 | 47 × 3 = 141 | 3.8 zero-shot baseline |
| `results/xam_q36/` | 3.6 | 47 × 3 = 141 | 3.6 zero-shot baseline |
| `results/xam_v4/` | 3.8-Flash-Next | 141 | earlier model, prompt v1 |
| `results/xam_v3/`, `xam_20260831_*`, `zs_20260830_150341/` | misc | — | earlier exploratory runs |

### Qwen3.8 harness campaign

| corpus | books | strict | note |
|---|---|---|---|
| `harness_opt_p1` | 23 | 27/44 = 61.4 % | first harness |
| `harness_opt_p2` | 23 | 32/44 = 72.7 % | |
| `harness_opt_p3` | 23 | 33/44 = 75.0 % | |
| `harness_opt_p4` | 23 | 36/44 = 81.8 % | |
| `harness_opt_p5` | **1** | 1/1 | the campaign's only single-book pass |
| `harness_opt_p6` | 23 | 39/44 = 88.6 % | |
| `harness_opt_p7` | 23 | **43/44 = 97.7 %** | frozen v1.6e |
| `harness_final` | 24 held-out × 3 = 72 | **85/123 = 69.1 %** | the 3.8 held-out exam |

Diary of the 3.8 loop: `results/logs/harness_opt_loop.md` (4,750 lines).

### Qwen3.6 harness campaign

| corpus | books × runs | accuracy | FP/claim | note |
|---|---|---|---|---|
| `harness_q36_p1` | 23 × 1 | 39/44 = 88.6 % | — | v1.6e straight |
| `harness_q36_p2` | 23 × 1 | 42/44 = 95.5 % | — | + smoothed-window fix |
| `harness_q36_p3` | 23 × 1 | 40/44 = 90.9 % | — | + clause-3b text (**reverted**, inert) |
| `harness_q36_p4` | 23 × 1 | 41/44 = 93.2 % | — | + cross-line wording |
| `harness_q36_final` | 24 × 3 = 72 | **79/123 = 64.2 %** | 38.8 % | **Exam A** — 3.6 + own tuned harness (3053 prompt) |
| `harness_q36_final_v16e` | 24 × 3 = 72 | **78/123 = 63.4 %** | 44.7 % | **Exam B** — 3.6 + 3.8's exact harness (v1.6e + 3866 prompt) |

### Cross-model matrix

**Like-for-like: every cell below covers the same 23 books × 3 runs = 69 records = 111
units.** Units outnumber records because a book-wide control expands to one unit per benefit
line. `sc-e6ffa4` is out of every cell; it never completed under 3.8 + the 3.6 harness
(section 8). The per-campaign rows above do include it, so they report `/123` — do not mix
the two.

| model + harness | records | accuracy | FP/claim |
|---|---|---|---|
| 3.8 + own (v1.6e + 3866) | 23 × 3 | **71.2 %** (79/111) | 41.9 % |
| 3.8 + 3.6's (tuned + 3053) | 23 × 3 | 70.3 % (78/111) | 43.1 % |
| 3.6 + 3.8's (v1.6e + 3866) | 23 × 3 | 64.9 % (72/111) | 43.3 % |
| 3.6 + own (tuned + 3053) | 23 × 3 | 65.8 % (73/111) | **38.7 %** |

Count `sc-e6ffa4` as the zero it is (24 books, 123 units) and the same four cells read: 3.8
own **69.1 %**, 3.6 own 64.2 %, 3.6 + 3.8's 63.4 %. The 3.8 + 3.6's cell does not move
(70.3 %), because that run never contained the book.

`harness_q38_tuned` is **incomplete by design**: `sc-e6ffa4` is a recorded failure
(section 8). Reported as **23/24** — see section 7 for both treatments.

### Per-scenario loop corpora (the improvement method)

| corpus | purpose |
|---|---|
| `harness_q36_step` | 3-run baseline for `sc-3c83fd` **before** the fix (0/3) |
| `harness_q36_step2` | same book **after** the fix (**3/3**) |
| `harness_q36_step3` | baseline for `sc-d72b95` |
| `harness_q36_step4` | GIVE-BACK edit test — failed, reverted |
| `harness_q36_step5` | baseline for `sc-f520e5` |
| `harness_q36_step6` | TAIL guard test — failed, reverted |
| `harness_q36_step7` | onset fix **with** coordination guard — verified |
| `harness_q36_regress` | regression check of the 4 books the onset fix touched |

### Logs, gates, status

* `results/logs/harness_q36_next_steps.md` — **the campaign runbook** (1,876 lines).
  Sections 1-37: pass results, the four-cell matrix, the reporting-standard change,
  identifiability audits, the `sc-e6ffa4` diagnosis and the declined-fix decision.
* `results/logs/harness_opt_loop.md` — the 3.8 per-scenario diary.
* `results/logs/*_gate.json` — freeze-gate read-outs.
* `results/logs/*_status.txt` — per-corpus completion status.

---

## 6. Key results

**All figures below are on the held-out split. Cell = accuracy | FP/claim.**

### Table A — 23 books, `sc-e6ffa4` excluded for every model (like-for-like)

| family | 3.8 own | 3.8+3.6h | 3.6+3.8h | 3.6 own | 3.6 zero | 3.8 zero |
|---|---|---|---|---|---|---|
| systemic | 56 \| 51 | **63 \| 46** | 44 \| 57 | 44 \| 51 | 41 \| 52 | 54 \| 66 |
| shock | 100 \| 8 | 75 \| 36 | 100 \| 20 | 100 \| 8 | 75 \| 25 | 67 \| 72 |
| drift | 67 \| 40 | 67 \| 40 | 67 \| 33 | 67 \| 33 | 67 \| 25 | 67 \| 70 |
| mixed | 87 \| 28 | 80 \| 29 | 80 \| 25 | 87 \| 24 | **93 \| 7** | 80 \| 48 |
| recovery | 100 \| 0 | 100 \| 0 | 100 \| 0 | 100 \| 0 | 100 \| 0 | 100 \| 55 |
| volatility | 100 \| 60 | 100 \| 62 | 100 \| 62 | 100 \| 57 | **100 \| 0** | 100 \| 60 |
| noise_trap | 50 \| 70 | 33 \| 75 | 50 \| 50 | 50 \| 62 | **0 \| 100** | 17 \| 92 |
| **TOTAL** | 71 \| 42 | 70 \| 43 | 65 \| 43 | 66 \| **39** | 59 \| 40 | 64 \| 66 |

### Table B — 24 books, the failure counted (0/12 for the config that failed it)

| family | 3.8 own | 3.8+3.6h | 3.6+3.8h | 3.6 own | 3.6 zero | 3.8 zero |
|---|---|---|---|---|---|---|
| systemic | 55 \| 54 | **52 \| 46** | 45 \| 57 | 45 \| 49 | 38 \| 49 | 56 \| 63 |
| (other rows identical to Table A) | | | | | | |
| **TOTAL** | **69 \| 45** | **63 \| 43** | 63 \| 45 | 64 \| **39** | 56 \| 39 | 64 \| 65 |

### Conclusions

1. **3.8 leads on recall, 3.6 leads on precision.** 71 % vs 66 % accuracy; 39 % vs
   42 % FP/claim (3.6 better). Holds in both tables and every sample size (9 → 24).
2. **Each model does best with its OWN harness.** 3.8: 71 % own vs 70 % on 3.6's.
   3.6: 66 % own vs 65 % on 3.8's. The "harness transfers between models" effect was
   **+8.3 points at 9 books and decayed to −1 by 23** — withdrawn.
3. **3.8 unaided is a precision disaster.** 65-66 % FP/claim, **34 % precision**. The
   harness lifts it to ~58 % precision. Most robust finding in the dataset.
4. **The harness buys 3.6 almost nothing on precision** (60 % unaided vs 61 %).
5. **`systemic` is the only family where recall varies.** Drift/recovery/volatility
   are saturated at 100 % for every harnessed config; `noise_trap` is poor for
   everyone (0-50 %). The models differ almost entirely on systemic.
6. **Over-claiming decomposition:** `FPs − misses` isolates false alarms *not*
   explained by a mislabel. 3.8 own harness: +31 of 69 FPs invented; 3.6 tuned: +6 of
   50. 3.8 both mislabels and over-claims; 3.6 almost purely mislabels.
7. **Optimism gap ~30 points for both models.** 3.6: 95.5 % opt → 63.4 % held-out.
   3.8: 97.7 % → 69.1 %. Optimization-split numbers rank models; they do not predict
   held-out performance.

---

## 7. How to replicate

### One book, no harness (baseline)

```bash
python3 scripts/run_zero_shot.py --scenarios sc-042304 --split optimization \
  --detail full --termination-mean pooled --base-url http://192.168.1.59:8080/v1 \
  --model Qwen3.6-27B --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 --timeout 3600 --runs 3 --stream \
  --wait-for-endpoint 1800 --max-consecutive-failures 5 --skip-existing --out my_run
```

### One book, harness on, pinned prompt (the 3.6 configuration)

```bash
python3 scripts/run_zero_shot_baseline_v2.py --scenarios sc-3c83fd \
  --split optimization --detail full --termination-mean pooled \
  --base-url http://192.168.1.59:8080/v1 --model Qwen3.6-27B \
  --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 --timeout 3600 --runs 3 --stream \
  --wait-for-endpoint 1800 --max-consecutive-failures 5 --skip-existing \
  --harness full --tool-calls 4 --out my_run
```

`PINNED_PROMPT_FILE=data/prompts/<file>.txt` overrides the system prompt (default:
`data/prompts/system_v2_baseline.txt`, 3053 chars).

### A full optimization pass (23 books, unattended, resume-safe)

```bash
setsid nohup env MODEL=Qwen3.6-27B OUT=my_pass PASS=1 RUNS=1 WAIT_ENDPOINT=1800 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  bash scripts/harness_pass_run.sh > results/logs/my_pass.log 2>&1 </dev/null &
```

Snapshots the harness (code **and** prompt) into `results/<OUT>/harness_snapshot/`
before the first call. **Always check that snapshot afterwards** — it is the only
proof of what actually ran.

### A held-out exam (24 books × 3 runs), with retry wrapper

```bash
setsid nohup env OUT=my_exam RUNS=3 MODEL=Qwen3.6-27B WAIT_ENDPOINT=1800 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  PINNED_PROMPT_FILE=data/prompts/system_v2_baseline.txt \
  LOGF=results/logs/my_exam.log STATUS=results/logs/my_exam_status.txt \
  bash scripts/harness_exam_retry.sh > results/logs/my_exam_retry.log 2>&1 </dev/null &
```

Omit `RUNNER` and `PINNED_PROMPT_FILE` to reproduce 3.8's configuration exactly
(`run_zero_shot.py` native, 3866-char harness-era prompt).

### Score, diagnose, gate

```bash
python3 scripts/score_xam.py results/my_run/zero_shot --json-out results/my_run/scores.json
python3 scripts/harness_diff.py sc-3c83fd --out my_run        # EXPERIMENTER-SIDE, prints truth
python3 scripts/harness_gate.py results/my_run/zero_shot --split optimization --runs 1 \
  --reference results/xam_q36/zero_shot --json-out /tmp/gate.json
```

### Safety checks (run after ANY harness edit)

```bash
bash scripts/harness_preflight.sh     # leak scan: pack refs + rules blocks, no API calls
bash -n scripts/<edited>.sh           # bash syntax
python3 -c "import ast;ast.parse(open('scripts/stats_pack.py').read())"
```

---

## 8. Known failures and limitations

### `sc-e6ffa4` — recorded failure, do NOT patch silently

`sys_vol_macro_2020_2024` (all four lines volatile). Under **3.8 + the 3.6 harness**
it never completed: 6+ attempts, one of 2 h 25 min, **0 usable runs**. It completes
**9/9 under the three other configurations.**

Three things had to go wrong together. None of them was enough on its own:

1. the 3053 prompt lacks ~800 chars of volatility guidance present in the 3866 one
   (a 546-char block describing exactly this book: several lines swinging together
   across consecutive years, report for EVERY affected line);
2. a model that uses tools — 3.8 ~24 % of runs, **3.6 0 of 144**;
3. a malformed tool request — the embedded Python had an invalid JSON escape
   (`Invalid \escape`), so `extract_tool_request` could not parse it, the tool never
   ran (`tool_calls=0`), the answer validator also failed, and the run retried
   **forever**.

The control that proves (1) is not the cause: **3.6 in the identical harness (tuned
pack + 3053 prompt) passes 3/3**. `strict=False` does not fix this case.

**Decision (section 36 of the runbook): the escape-repair is deliberately NOT
applied.** A defect documented as a failure stays auditable; one patched away becomes
a silent gap. `run_zero_shot.py` must remain at `98411194093cdd0c` unless that
decision is revisited.

**Impact:** the missing book is 12 units. Table A (exclude) 70.3 %; Table B (count as
0/12) 63.4 %. Most likely true value ≈ 68 % (6/12, its rate under 3.8's own harness).
FP/claim is unaffected — the aborted runs made no claims.

### `sc-696b93` — fixed, for contrast

Failed identically (`TruncatedStream`) because 3.8 emitted a **raw newline inside a
JSON string** (`"Poiss\non"`). Fixed by `json.loads(..., strict=False)` in both
`score_xam.parse_findings` and `run_zero_shot.answer_parses_as_json`. That fix **is**
applied. Impact on existing results: **zero** — all reference corpora have 0
unparseable answers.

### Other limitations

* **Tool loop dormant in 3.6** — 0 calls in 144 held-out runs, despite the tool being
  offered. Two attempts to activate it (clause-3b rewrite; mandatory wording) failed.
  The model correctly judges the pack answers the question.
* **Two prompt revisions in `harness_q38_tuned`** — the first 63 runs parsed strictly,
  the last 9 leniently. Affects only answers with raw control characters.
* **Unidentifiable units.** `sc-d72b95`'s Death drift is statistically undetectable
  (fitted +0.0253/yr, SE 0.0251, t = 1.01; minimum detectable slope +0.088 vs planted
  0.05). `sc-f520e5` is genuinely ambiguous (volatility F = 17.1 *and* a real level
  excursion), so its drift reading is defensible. Neither is a harness defect.
* **`sc-e6ffa4` recovery is possible** but requires revisiting the declined fix.

---

## 9. Folder layout and conventions

```
data/
  eval/{optimization,heldout}/<sc-id>/artifacts/   # the scenario CSVs
  truth/manifests/<sc-id>.json                     # planted controls — NEVER in a prompt
  prompts/                                         # system prompt files
scripts/                                           # runners, scorers, harness, tooling
results/<corpus>/{zero_shot,scores.json,scoreboard.txt,harness_snapshot/}
results/logs/                                      # diaries, gate read-outs, status
docs/                                              # background and handover documents
tests/
```

**Naming conventions in `results/`:**

| prefix | meaning |
|---|---|
| `xam_*` | zero-shot corpora, no harness (`xam_v5` = 3.8, `xam_q36` = 3.6) |
| `harness_opt_p1..p7` | 3.8 optimization passes |
| `harness_final` | 3.8 held-out exam |
| `harness_q36_p1..p4` | 3.6 optimization passes |
| `harness_q36_final` | 3.6 Exam A (own tuned harness) |
| `harness_q36_final_v16e` | 3.6 Exam B (3.8's exact harness) |
| `harness_q38_tuned` | 3.8 on 3.6's harness (23/24 — see section 8) |
| `harness_q36_step*` | per-scenario improvement loop |
| `harness_q36_regress` | regression check |

**Do not move or rename corpora** — every script resolves fixed paths such as
`results/harness_opt_p7/zero_shot`. Relocating them breaks replication. Organisation
is achieved through *this index*, not by restructuring the tree.

**Operational rules learned the hard way:**

* one generation at a time (server has 1 slot); two concurrent clients cause
  spurious connection errors;
* the user launches API-touching runs; log everything to `results/logs/`;
* **never edit a bash script while it is running** — bash re-reads the file and can
  execute garbage. Stop first, patch, relaunch;
* `pkill -f` patterns self-match the calling shell. Build patterns at runtime
  (`A="run_zero"; A="${A}_shot"; pkill -f "$A"`) and match on the leading fragment —
  the runner is `run_zero_shot_baseline_v2.py`, which `pkill -f "run_zero_shot.py"`
  silently misses;
* a killed driver can leave its child holding `results/logs/harness_final.lock`. Find
  it with `ls -l /proc/*/fd 2>/dev/null | grep harness_final.lock`;
* `answer_parses_as_json` failing produces a retry loop, not a skipped run — bound it
  with `--max-consecutive-failures 1` when probing a suspect book.

---

## 10. Where to look first, by question

| question | go to |
|---|---|
| Why does this benchmark exist, and who is it for? | [README § The Study Behind It](../README.md#-the-study-behind-it--four-questions-this-has-to-answer) |
| How do I regenerate the 47 books? | [README § Where the data comes from](../README.md#-where-the-data-comes-from-and-how-to-generate-it-yourself) |
| What was done and why, in order? | `results/logs/harness_q36_next_steps.md` |
| How was the 3.8 harness built? | `results/logs/harness_opt_loop.md`, `docs/HARNESS_GROWTH.md` |
| What are the final numbers? | section 6 above; `results/*/scores.json` |
| Why did a book fail? | section 8 above; runbook sections 35-37 |
| How do I reproduce a result? | section 7 above; the corpus's `harness_snapshot/` |
| What is the benchmark? | `docs/scenario-catalog.md`, `docs/architecture.md`, `README.md` |

---

## 11. Formal report

A standalone, self-contained write-up of this work — executive summary, method,
results by model and by family, the `sc-e6ffa4` failure and its impact, cost
analysis (run time, tokens, throughput), and conclusions — is at:

**`docs/REPORT_qwen36_vs_qwen38.md`**

Read that if you want the findings without the operational detail; read this index
if you need to locate a corpus or reproduce a number.
