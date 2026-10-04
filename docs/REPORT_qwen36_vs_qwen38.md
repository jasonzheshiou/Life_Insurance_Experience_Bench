# Cross-Model Evaluation Report
## Qwen3.6-27B vs Qwen3.8-27B on the Data Pipeline Arena anomaly-detection benchmark

**Scope:** held-out split, 24 scenarios, 3 runs each, single-slot inference.
**Status:** complete except one recorded failure (`sc-e6ffa4` — see §1.6 and §2.7).

---

# PART 1 — EXECUTIVE SUMMARY

## 1.1 Purpose

To determine whether two language models, **Qwen3.6-27B** and **Qwen3.8-27B**, differ
in their ability to find planted anomalies in synthetic life-insurance experience
data, and specifically **whether a similar level of harness optimisation produces a
similar result for both**. The benchmark exists because actuarial anomaly detection
is a task where a model must do more than read a table: it must decide *whether* an
anomaly exists, *which* pattern it is, *which years* it covers, and *which benefit
lines* it affects — and where a confident wrong answer is worse than no answer.

## 1.2 Method, in brief

Each model answers the same 24 unseen books, 3 times each, at temperature 1.0, with
no truth visible to it. Answers are scored against planted ground truth. Two
experimental factors are crossed:

* **model** — Qwen3.6-27B vs Qwen3.8-27B;
* **harness** — *none* (raw scenario data + task prompt), or a **harness**: a
  deterministic evidence pack computed from the data, plus a rules block defining
  the anomaly taxonomy and output schema, plus optional sandboxed Python tool calls.

Qwen3.8's harness was built over seven optimisation passes (v1.0 → v1.6e, 307
per-scenario iterations). Qwen3.6 received that finished harness as a starting point
and then four optimisation passes plus a targeted per-scenario repair loop.

## 1.3 Definitions — the two metrics used throughout

**Accuracy (recall)** — *did the model find what was there?*

```
accuracy = strict hits / units        units = planted controls × runs
```

A **unit** is one (run, control) pair. A planted control is matched **strictly** only
if the finding agrees on **benefit line + pattern type + window overlap + direction**.
Pattern agreement is exact: a *drift* reported as a *shock* does **not** match.

**FP/claim (false alarm rate)** — *is the model trustworthy when it speaks?*

```
FP/claim = false positives / claims emitted
         = false positives / (strict hits + false positives)
precision = 1 − FP/claim
```

A **false positive** is any reported finding that does not strictly match a planted
control. This includes near-misses, and includes findings on CLEAN books (which have
no controls at all, so any claim is a false alarm).

**Why both, and why FP/claim specifically.** Accuracy alone can be gamed: a model
that floods plausible claims raises recall while degrading the output. `FP/run`
(the older diagnostic, false alarms per answer) shows absolute noise but not that the
noise has come to dominate. FP/claim is normalised by what the model actually said,
so it cannot be inflated that way. The two metrics also have **different
denominators** (opportunities vs claims) and therefore do **not** sum — accuracy +
FP/claim above 100 % is not an error.

**A note on cost of error.** One wrongly-labelled pattern costs *twice*: the control
is missed **and** the wrong claim is a false alarm. This is why the two metrics move
together for mislabels but independently for omissions (a missed control with no
claim) and inventions (a claim with no corresponding control).

## 1.4 Headline results — accuracy and false alarms by model and harness

All figures on the **same 23 books** (the one book that failed is treated separately
in §1.6, so every row is like-for-like). **Cell = accuracy | FP/claim.**

| # | configuration | accuracy | FP/claim | precision |
|---|---|---|---|---|
| 1 | **Qwen3.6-27B, no harness** | 59.5 % | **40.0 %** | 60.0 % |
| 2 | **Qwen3.8-27B, no harness** | 64.0 % | **65.7 %** | 34.3 % |
| 3 | Qwen3.6-27B + Qwen3.8's harness | 64.9 % | 43.3 % | 56.7 % |
| 4 | **Qwen3.6-27B + own harness** | **65.8 %** | **38.7 %** | **61.3 %** |
| 5 | Qwen3.8-27B + Qwen3.6's harness | 70.3 % | 43.1 % | 56.9 % |
| 6 | **Qwen3.8-27B + own harness** | **71.2 %** | 41.9 % | 58.1 % |

**Reading the progression:**

* **Without a harness, 3.8 finds more but is far less reliable.** It leads 3.6 on
  accuracy (64.0 % vs 59.5 %) but emits false alarms at **65.7 %** — meaning **almost
  two thirds of everything it says without a harness is wrong.** 3.6 sits at 40.0 %.
* **The harness helps 3.8 enormously on trustworthiness and 3.6 on recall.** For 3.8
  it cuts FP/claim 65.7 % → 41.9 % (precision 34.3 % → 58.1 %) while adding only ~7
  points of accuracy. For 3.6 it adds ~6 points of accuracy (59.5 % → 65.8 %) and
  improves FP/claim only marginally (40.0 % → 38.7 %).
* **Each model performs best on its own harness.** 3.8: 71.2 % own vs 70.3 % on
  3.6's. 3.6: 65.8 % own vs 64.9 % on 3.8's. The harness does **not** transfer
  between models.
* **The final ranking is a trade, not a win.** 3.8 leads on **recall** (71.2 % vs
  65.8 %, a 5.4-point gap); 3.6 leads on **precision** (61.3 % vs 58.1 %, a 3.2-point
  gap). Which model is "better" depends on whether a missed anomaly or a false alarm
  costs more in the intended deployment.

**A striking individual result:** 3.8 *without* a harness (64.0 % accuracy) is nearly
as accurate as 3.6 *with* a full harness (65.8 %) — but at **34.3 % precision versus
61.3 %**. Comparable recall, radically different trustworthiness.

## 1.5 Results by scenario family

The same six configurations, broken down by the type of anomaly planted. Families
are the benchmark's "question types": **drift** (sustained multi-year move), **shock**
(abrupt single-year change), **volatility** (dispersion with flat level), **recovery**
(IP termination recovery), **systemic** (coordinated multi-line event), **mixed**,
**noise_trap** (a lookalike — the line *looks* like drift/spike but the truth is
volatility), and **CLEAN** (nothing planted).

**Cell = accuracy | FP/claim.**

| family | 3.6 no harness | 3.8 no harness | 3.6 + own | 3.8 + own |
|---|---|---|---|---|
| **systemic** | 41 \| 52 | 54 \| 66 | 44 \| 51 | **56 \| 51** |
| **shock** | 75 \| 25 | 67 \| 72 | **100 \| 8** | **100 \| 8** |
| **drift** | 67 \| 25 | 67 \| 70 | 67 \| 33 | 67 \| 40 |
| **mixed** | **93 \| 7** | 80 \| 48 | 87 \| 24 | 87 \| 28 |
| **recovery** | 100 \| 0 | 100 \| 55 | **100 \| 0** | **100 \| 0** |
| **volatility** | **100 \| 0** | 100 \| 60 | 100 \| 57 | 100 \| 60 |
| **noise_trap** | 0 \| 100 | 17 \| 92 | **50 \| 62** | 50 \| 70 |
| **CLEAN** | silent ✓ | **falsely accused** | silent ✓ | silent ✓ |

**The four findings that matter:**

1. **`systemic` is the only family where recall genuinely varies.** Three families
   (drift, recovery, volatility) sit at 100 % accuracy for every harnessed
   configuration — both models find everything there. The entire recall difference
   between the models lives in systemic (44 % vs 56 %) and noise_trap (both 50 %).
   **The benchmark's discriminating power is concentrated in a minority of families.**

2. **The models' character difference is sharpest in `systemic` and `volatility`.**
   On systemic, 3.8 finds 12 points more; on mixed, 3.6 actually leads (93 % vs 80 %).
   There is no family where one model dominates on both metrics.

3. **`noise_trap` is the hardest family for both.** Best case 50 % accuracy. Without a
   harness, 3.6 scores **0 % accuracy with 100 % FP/claim** — it claimed anomalies and
   got every one wrong. The trap works: the planted truth is *volatility* while the
   line contains a lookalike spike or drift, and models report the lookalike.

4. **CLEAN honesty separates the models without a harness.** With a harness, both
   correctly stay silent on the clean book. Without one, **3.8 falsely accused it**,
   while 3.6 did not.

## 1.6 The failed scenario `sc-e6ffa4` and its effect on the data

**What happened.** `sc-e6ffa4` is `sys_vol_macro_2020_2024` — **all four benefit lines
volatile 2020-2024**. Under **Qwen3.8-27B running Qwen3.6's harness** it produced
**no usable run at all**: six or more attempts, one lasting **2 hours 25 minutes**,
every one failing. Under the three *other* configurations it completes 3/3 every
time (§2.7 gives the full diagnosis). It is therefore a genuine failure of that one
configuration, not a missing data point.

**How it affects the data.** The book contributes **12 units** (4 benefit lines × 3
runs). Two treatments are reported, and **they must not be confused**:

| treatment | what it means | accuracy | FP/claim |
|---|---|---|---|
| **Exclude** (23 books) | "how did it do on what it attempted?" | **70.3 %** | 43.1 % |
| **Count as failure** (24 books) | the book scores 0/12 | **63.4 %** | 43.1 % |

**The failure costs 6.9 accuracy points and leaves FP/claim untouched.** That
asymmetry is substantive, not arithmetic: the aborted runs emitted **no claims at
all**, so the book adds 12 to the denominator of accuracy and nothing to either side
of the FP/claim fraction. A book that cannot answer is penalised as a total miss, not
as noise.

**Effect on conclusions: none.** The reference point is what 3.8 scored on this book
under its own harness — **6/12** — which would put the true figure near **68 %**,
between the two bounds. Every conclusion in §1.4 has a margin far larger than
±7 points: the recall gap is 5.4, the precision gap 3.2, and 3.8's unharnessed
precision sits 24 points below its harnessed figure. None of them move.

**Decision recorded:** the underlying parser defect was **deliberately not patched**.
A defect that exists only as a documented failure remains auditable; one that has
been patched away becomes a silent gap. `sc-e6ffa4` must always be reported as
**failed**, never as absent or excluded.

## 1.7 Conclusions from the entire research

1. **The two models are differently shaped, not ranked.** 3.8 is the higher-recall
   model (+5.4 points); 3.6 is the more precise one (+3.2 points precision). Neither
   dominates. The choice depends on the relative cost of a missed anomaly versus a
   false alarm in the intended use.

2. **Without a harness, Qwen3.8-27B is not usable for this task.** 65.7 % of its
   claims are false alarms — precision 34.3 %. This is the single most robust finding
   in the study and holds at every sample size measured. The harness is worth **~24
   points of precision** to it.

3. **Qwen3.6-27B is already well-behaved without a harness** (40.0 % FP/claim, 60.0 %
   precision) and never falsely accused the clean book. Its deficiency is recall.

4. **Harness optimisation does not transfer between models.** The effect of swapping
   harnesses between models was **+8.3 accuracy points at 9 books and decayed to −1 by
   23 books** — i.e. zero. Each model's best result came from its own harness. This
   was tested directly and is reported as a negative result.

5. **The optimisation split badly overstates held-out performance — by ~30 points for
   both models.** 3.6: 95.5 % optimising → 63.4 % held-out. 3.8: 97.7 % → 69.1 %.
   Optimisation-split numbers rank models; they do **not** predict unseen
   performance. Any future tuning on this benchmark should be treated as a ranking
   tool only.

6. **The task's difficulty is concentrated.** Four of eight families are saturated
   (everything found) and two carry nearly all the signal (`systemic`, `noise_trap`).
   A benchmark revision should add discriminating scenarios in those families, since
   the current split cannot separate models elsewhere.

7. **Errors are mostly mislabelling and over-claiming, not blindness.** The models
   generally see the right lines and the right movement, then choose the wrong
   taxonomy word, or add a spurious second finding on top of a correct one. Decomposing
   false alarms as `FP − misses` shows 3.8 invents 31 of its 69 false alarms (the rest
   are mislabels), while 3.6 invents only 6 of 50 — 3.6's errors are almost purely
   nomenclature.

8. **Two of the "failures" are not model failures at all.** `sc-d72b95`'s missing unit
   is **statistically undetectable** (fitted slope +0.0253/yr, standard error 0.0251,
   t = 1.01; minimum detectable slope at 80 % power is +0.088 against a planted 0.05),
   and `sc-f520e5` is **genuinely ambiguous** (the line carries both real volatility
   and a real level excursion, so its alternative reading is defensible). These should
   be reclassified as bad units rather than counted against the models.

---

# PART 2 — BODY

## 2.1 Purpose and background

Actuarial experience analysis asks whether observed claims deviate from expected, and
if so *how*. The hard part is not arithmetic but **classification**: distinguishing a
sustained multi-year drift from a single-year shock from elevated dispersion, deciding
which years the event covers, and recognising when *several lines are moving together*
because of one shared cause rather than several unrelated ones.

The benchmark was built to test exactly that, on data where the answer is known by
construction but **not visible to the model** — no truth markers, no labels, opaque
scenario ids, and files that never state what was planted. The model receives only
the CSVs and the task framing.

The research question: **do Qwen3.6-27B and Qwen3.8-27B differ on this task, and does
a similar level of harness optimisation close any gap between them?**

## 2.2 How the data were generated

`scripts/generate_scenarios.py` builds each book from a fixed seed and a scenario
specification. A book covers four benefit lines — **Death, CI (critical illness),
**TPD (total permanent disability)**, **IP (income protection)** — over 2015-2024,
as actual and expected claim counts per year (and, for some lines, by age band,
gender and duration month).

Anomalies are planted by applying a **factor** to a line over a **window**, producing
one of the patterns:

| pattern | how it is planted |
|---|---|
| **drift** | a sustained year-over-year movement across consecutive years (positive or negative) |
| **shock** | an abrupt level change in one year (or a short run), flat-topped |
| **volatility** | increased year-to-year dispersion with the level left unchanged |
| **recovery** | an IP termination-rate recovery |
| **systemic** | the same event applied to 2-4 lines simultaneously |
| **noise_trap** | a line that *looks* like drift or a spike, but the planted truth is volatility |

The **truth manifest** for each book (`data/truth/manifests/<sc-id>.json`) records
`controls[]`: benefit, type, window, factor, and signature direction. A book-wide
control uses `benefit: "all"`, which the scorer expands to one unit per benefit line
(4 units). **These manifests are experimenter-side only and must never enter a
prompt.**

Three safeguards protect the benchmark's integrity:

* **opaque ids** — scenarios are `sc-<6hex>`, unrelated to their content;
* **fixed split** — 23 optimization books for tuning, 24 held-out books that must not
  be tuned against;
* **leak gating** — `scripts/harness_preflight.sh` scans every generated prompt for
  truth tokens and for the taxonomy vocabulary leaking into the evidence pack, and
  must pass before any pass is run.

## 2.3 Methodology

### 2.3.1 Zero-shot baselines

Each model first answered all 47 books three times with **no harness** — raw scenario
data plus the task prompt and output schema. These are the baselines
(`results/xam_v5/` for 3.8, `results/xam_q36/` for 3.6) and establish each model's
unaided ability. They are the reference against which the harness is measured.

### 2.3.2 Harness growth methodology

The harness has three components:

1. **Evidence pack** (`scripts/stats_pack.py`) — deterministic statistics computed
   directly from the CSVs and appended to the prompt: per-line trend, step,
   excursions, onset sharpness, overdispersion, longest run, smoothed 3-year moving
   average, tail segment, and cross-line swing coordination. It presents *evidence*,
   not verdicts, and is explicitly labelled as such.
2. **Rules block** (`HARNESS_RULES` in `scripts/run_zero_shot.py`) — defines the
   anomaly taxonomy, the output schema, discipline clauses about what is *not* an
   anomaly, and offers up to 4 sandboxed Python tool calls.
3. **System prompt** — supplied as a file, so a model can evolve its own prompt
   without editing the runner (`PINNED_PROMPT_FILE`).

Growth proceeded by **two alternating methods**:

* **Full optimisation passes** — re-run all 23 optimization books under an edited
  harness, score, and compare. Seven passes were run for 3.8 and four for 3.6.
* **The per-scenario loop** — the more productive method. Run **one** wrong book
  three times to establish a baseline, diagnose the failure from the evidence pack
  and the model's answer, make **one targeted edit**, validate it offline across all
  23 books, then re-run that book three times. Keep the edit only if it clears a
  pre-registered bar; otherwise revert.

Every edit was validated in three ways before spending a single API call:
regenerate all 23 packs and inspect which books changed; confirm the CLEAN book and
the other previously-solved books are unaffected; run the leak preflight. Every pass
snapshots its harness bytes — code **and** prompt — into
`results/<corpus>/harness_snapshot/`, so the exact configuration behind any number is
recoverable.

**Discipline observed throughout:** an edit that fails its bar is reverted rather
than kept; a negative result is reported as such; a failure is recorded rather than
worked around. Three edits were reverted during the 3.6 campaign on this basis.

### 2.3.3 Evaluation protocol

* 24 held-out books × 3 runs = 72 calls per exam.
* Canonical samplers (temperature 1.0, top_p 0.95, top_k 20), streaming, no
  `max_tokens`, 3600 s per-call timeout, one generation at a time (the server has a
  single slot).
* Three runs are essential: they separate a *consistent* failure from an unlucky one.
  This study found books scoring 0/3 and 3/3 across configurations, and a single run
  would have shown only "a shock" or "a drift" with no way to tell which was typical.
* Every corpus is scored with the same scorer (`score_xam.py`, v3) against the same
  fixed truth manifests.

## 2.4 Detailed results

### 2.4.1 Headline table

See §1.4. Tables there are on the common 23 books so all rows are like-for-like.

### 2.4.2 Full held-out results (24 books, where available)

| configuration | accuracy | FP/claim | precision | FP/run |
|---|---|---|---|---|
| 3.8 + own harness (v1.6e + 3866 prompt) | **69.1 %** | 44.8 % | 55.2 % | 0.96 |
| 3.6 + own harness (tuned + 3053 prompt) | 64.2 % | **38.8 %** | **61.2 %** | 0.69 |
| 3.6 + 3.8's harness (v1.6e + 3866 prompt) | 63.4 % | 44.7 % | 55.3 % | 0.88 |

### 2.4.3 The controlled cross-model comparison

Exam B gave Qwen3.6-27B **exactly** Qwen3.8-27B's instrument: identical harness bytes
(`stats_pack.py 16e53e0ef0b097ab`, `run_zero_shot.py a4b967de975625f9`), identical
3866-character system prompt, identical books, runs and samplers. This is the only
fully controlled comparison in the study.

| | accuracy | FP/claim | precision |
|---|---|---|---|
| Qwen3.6-27B | 78/123 = **63.4 %** | 44.7 % | 55.3 % |
| Qwen3.8-27B | 85/123 = **69.1 %** | 44.8 % | 55.2 % |
| **difference** | **7 units = 5.7 points** | −0.1 | +0.1 |

**With an identical instrument, 3.8 is 5.7 points more accurate and the two are
indistinguishable on precision.** The recall gap is real; the reliability difference
disappears once both models are harnessed.

### 2.4.4 Optimisation split vs held-out — the optimism gap

| model | best optimisation | held-out | gap |
|---|---|---|---|
| Qwen3.6-27B | 42/44 = 95.5 % | 63.4 % | **−32.1** |
| Qwen3.8-27B | 43/44 = 97.7 % | 69.1 % | **−28.6** |

Both models lose roughly **30 points** moving from the 23 books they were tuned on to
24 unseen books. This is a property of the benchmark and harness, not of either
model, and it is the single most important methodological finding: **optimisation-split
scores are a ranking device and must never be quoted as expected performance.**

### 2.4.5 Precision, false alarms and over-claiming

False alarms decompose into two kinds:

```
false positives = mislabels (a miss occurred) + over-claims (no miss occurred)
                = min(FP, misses)             + max(0, FP − misses)
```

| configuration | units | hits | misses | FPs | **over-claims** |
|---|---|---|---|---|---|
| 3.8 own harness | 123 | 85 | 38 | 69 | **+31** |
| 3.6 Exam B (same harness) | 123 | 78 | 45 | 63 | +18 |
| 3.6 own harness | 123 | 79 | 44 | 50 | **+6** |

**3.8 emits 154 claims for 123 truths — 25 % more claims than there is truth** — and
31 of its false alarms have no corresponding miss at all: they are pure invention.
3.6 emits 129 claims for 123 truths, and only 6 of its false alarms are inventions;
its errors are almost entirely *mislabels*, meaning it sees the right line and picks
the wrong word.

**Practical consequence:** the two profiles need different remedies. Over-claiming
needs discipline ("do not report what is not there"); mislabelling needs vocabulary
work. Applying precision-suppression to 3.6 would be the wrong medicine, and this was
confirmed experimentally — the 3.6-specific pattern-vocabulary edits worked, while
attempts to make 3.6 report *less* did not.

### 2.4.6 Cost — run time, tokens, throughput

Measured on the same hardware and server throughout.

| configuration | median wall per book | median reasoning | median completion tokens |
|---|---|---|---|
| 3.8 no harness | 16.4 min | 43,056 chars | 16,227 |
| 3.8, optimisation p7 | 19.1 min | 46,705 chars | 18,928 |
| 3.8 held-out | 13.5 min | 33,921 chars | 13,763 |
| **3.6 no harness** | **5.4 min** | — | — |
| 3.6 optimisation p2 | 5.1 min | — | — |
| **3.6 held-out** | **4.8 min** | 15,586 chars | 5,719 |

**Qwen3.6-27B is roughly 3× cheaper per answer.** It reasons ~2.2× less
(15.6 K vs 33.9 K characters) and emits ~2.4× fewer completion tokens. Aggregate
throughput is ~17.5 tokens/second on a single slot, so a 23-book optimisation pass
costs **~2 hours** for 3.6 and **~4-5 hours** for 3.8, and a 72-call held-out exam
costs **~6 hours** for 3.6 and **~16 hours** for 3.8.

Cost therefore matters to the conclusions: **3.6 achieves 93 % of 3.8's held-out
accuracy at roughly one third of the time and tokens**, with better precision.

### 2.4.7 Tool use

The harness offers up to 4 sandboxed Python calls per run.

| model | tool-using runs |
|---|---|
| Qwen3.8-27B | ~24 % (17 of 72 held-out; 10 of 64 in the tuned corpus) |
| **Qwen3.6-27B** | **0 of 144 — never** |

3.6's tool loop is entirely dormant despite the tool being offered and two dedicated
attempts to activate it (a rewritten efficiency clause, and mandatory-use wording).
It correctly judges that the evidence pack already contains the arithmetic. **This
asymmetry is not a defect but it is a robustness advantage**: the one hard failure in
this study (§2.7) was a malformed tool request, which 3.6 cannot produce.

## 2.5 What the harness changed, edit by edit

| edit | target | outcome |
|---|---|---|
| smoothed-window labelling (the 3-yr MA labelled its windows one-sidedly, so a smoothed shape appeared to stop two years before the data did) | `sc-3c83fd` drift read as shock | **kept** — part of the +4 unit gain at pass 2 |
| cross-line note over-claim removed ("not a multi-year erratic stretch") | over-suppression of multi-year readings | **kept** — wording correction only |
| onset caution (names a competing sustained-run reading when the onset ratio is measured against too narrow a window) | `sc-3c83fd` | **kept with guard** — 0/3 → 3/3 |
| coordination guard (suppresses that caution when several lines move together, where a "long run" is the shared event) | `sc-bba653` regression caused by the caution | **kept with the caution** — 4/4 → 11/12, pack byte-identical to the pre-edit state |
| clause-3b efficiency rewrite | activate 3.6's tool loop | **reverted** — inert, 0 tool calls before and after |
| GIVE-BACK scoping | `sc-d72b95` missing drift | **reverted** — no change (9/12 both sides); the unit is undetectable |
| TAIL rebound guard | `sc-f520e5` volatility read as drift | **reverted** — made it worse (3/6 vs 4/6) |

The per-scenario loop fixed more in 25 minutes than four full optimisation passes had
managed, because a 23-book sweep moves three units of noise while a single-book loop
isolates one cause.

## 2.6 Identifiability — not every miss is a model failure

Two apparent 3.6 failures were audited statistically:

**`sc-d72b95`** — the missing unit is a Death drift planted at factor 0.05 over
2021-2024. Fitted from the data: slope **+0.0253/yr**, standard error **0.0251**,
**t = 1.01** (needs |t| > 3.18 at 2 degrees of freedom). The 95 % confidence interval
**[−0.083, +0.133]** contains zero *and* the planted value. **Minimum detectable slope
at 80 % power: +0.088/yr** — the planted effect is roughly half of what four annual
observations can resolve. **This unit is not identifiable**, and 3.6 in fact finds all
three *identifiable* controls in that book: it is at ceiling on the units the data
support.

**`sc-f520e5`** — the volatility is real (variance ratio **F = 17.1** against a
critical 5.41), but the same line also carries a genuine level excursion
(0.95 → 1.34 → 0.80, mean 1.102 inside the window against 0.943 outside). The model's
alternative "drift" reading is **defensible from the data**; the truth merely prefers
the volatility label. Attempts to push the model toward the truth made the score
*worse*, because they asked it to ignore a real feature.

## 2.7 The `sc-e6ffa4` failure — full diagnosis

`sc-e6ffa4` (`sys_vol_macro_2020_2024`, all four lines volatile) produced **zero
usable runs** under 3.8 + 3.6's harness, across six or more attempts, one running
2 h 25 min.

**The saved record is a tool request, not a final answer:**

```
{"tool": "python", "code": "import csv\nfrom collections import defaultdict\n..."}
parse error: Invalid \escape: line 1 column 2108 (char 2107)
```

The embedded Python contained an invalid JSON escape, so `extract_tool_request` could
not parse it — **the tool never executed** (`tool_calls=0` confirms it) — and the
answer validator failed too. The run was marked with a misleading `TruncatedStream`
label and retried, reproducing the same slip indefinitely.

**It requires three conditions together, none sufficient alone:**

| model | pack | prompt | volatility guidance? | `sc-e6ffa4` |
|---|---|---|---|---|
| 3.8 | v1.6e | 3866 | yes | 3/3 OK (~32 min) |
| **3.8** | **tuned** | **3053** | **no** | **0/3 — FAILED** |
| 3.6 | v1.6e | 3866 | yes | 3/3 OK |
| **3.6** | **tuned** | **3053** | **no** | **3/3 OK** |

Rows 2 and 4 have the **identical harness** and differ only by model, so the prompt
gap cannot be the cause. What it explains is the **routing**: the 3866 prompt carries
~800 characters of volatility guidance absent from the 3053 one, including a 546-char
block that describes this book exactly ("several lines swinging together across
CONSECUTIVE years … report it for EVERY affected line"). Under-instructed, 3.8 falls
back to computation; 3.6 never uses tools, so it simply answers.

**Impact:** 12 units, counted as a total miss. 70.3 % (exclude) vs 63.4 % (count).
FP/claim unchanged. **No conclusion in this report moves.**

## 2.8 Conclusion

**On the research question:** a similar level of harness optimisation does produce
different results for the two models, and the difference is a **shape, not a rank**.
Qwen3.8-27B finds more anomalies; Qwen3.6-27B makes fewer false ones. Under an
identical instrument the gap is **5.7 points of accuracy and nothing on precision**.

**On harness design:** the harness is not a neutral wrapper. For Qwen3.8-27B — which
without it produces false alarms at 65.7 % — it is worth **~24 points of precision**
and is the difference between usable and unusable output. For Qwen3.6-27B, already
well-behaved unaided, it is worth **~6 points of accuracy**. **The same harness
produces a different benefit for each model, and does not transfer between them.**

**On method:** three lessons worth carrying forward.

1. **Three runs, not one.** Single runs cannot distinguish a consistent failure from
   an unlucky one, and several conclusions in this study reversed when the sample
   grew from 9 to 23 books.
2. **Report accuracy *and* FP/claim.** A model that floods claims raises recall while
   degrading output; FP/claim is the only rate normalised by what the model actually
   said. Adopting it mid-campaign overturned an earlier conclusion that 3.8 was
   simply "the better scorer".
3. **Separate the model from the instrument before concluding.** An apparent
   "+8.3 point harness transfer" decayed to −1 as the sample grew, and the reported
   "97.7 %" optimisation figure accompanies a **69.1 %** held-out figure. Both are
   real; only the second predicts performance.

**On the benchmark itself:** four of eight families are saturated for both models and
two carry nearly all the discriminating power. The split should be extended in
`systemic`, `noise_trap` and `mixed` before it is used to rank further models, and
the two unidentifiable units identified in §2.6 should be reclassified rather than
counted against any model.
