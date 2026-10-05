# Model and Harness Evolution
## Two Qwen 27B models and the harnesses around them, measured on synthetic life-insurance A/E data

- **Platform:** [Life Insurance Experience Bench](../README.md) — generated A/E scenarios with a
  planted answer key.
- **Scope:** held-out split, 24 scenarios, 3 runs each, single-slot inference.
- **Status:** complete except one recorded failure (`sc-e6ffa4` — see §3.11).

---

---

---

---

# 1 · Executive summary

## 1.1 Purpose

The general question is whether a **harness has to evolve as the model underneath it
evolves**. A harness is the deterministic evidence pack, the rules block and the pinned
system prompt wrapped around a model before it is asked to work: when the model changes,
does the wrapper built for the old one still do its job?

This study answers it on two concrete subjects, **Qwen3.6-27B** and **Qwen3.8-27B**, and
specifically **whether, when you move from 3.6 to 3.8, the harness has to evolve with it.**
The two are the right pair for that question: they share the same underlying 27 B
architecture — parameter count, weight sizes, compute graph — and were served on the same
slot with the same sampler, so the only difference between them is training refinement and
post-training optimisation. Behaviour, not architecture.

## 1.2 Background

Suppose you want an LLM to help with experience studies: reading A/E tables, flagging
lines that need investigation, drafting experience commentary. Before anyone signs that
off, four questions have to be answered, and one convincing demo answers none of them.

- **How good is the model** at the task — how much of what is really in the data does it
  find?
- **What does it miss, and what does it invent?** A miss and an invention cost different
  things and are fixed differently, so they cannot be averaged into one score.
- **What does one answer cost**, in time and tokens, reported beside the result it bought?
- **Is the pipeline around the model right, or does it need updating — and on what
  evidence?** Who says the wrapper is still fit for purpose, and what would convince them.

**What you govern is the model and the harness together, not the model alone.** A vendor
notice saying "we upgraded the model" is not an assessment, and on its own it is not a
reason to re-assess. What changes between model versions is behaviour: how the model
reasons, how much it checks before asserting, whether it uses a tool at all. When behaviour
changes, re-measure the pair.

## 1.3 Methodology

Each model answers the same 24 unseen scenarios, three times each, at temperature 1.0,
with no truth visible to it. Answers are scored against the planted ground truth. Two
factors are crossed:

* **model** — Qwen3.6-27B vs Qwen3.8-27B;
* **harness** — *none* (scenario data plus the task prompt), or a **harness**: a
  deterministic evidence pack computed from the data, plus a rules block defining the
  anomaly taxonomy and the output schema, plus up to four sandboxed Python tool calls.

Two metrics are reported for every configuration and never blended:

- **accuracy** — how much of what was planted the model found. Matching is strict: a finding
  counts only if the benefit line, the pattern, the years and the direction all agree, so a
  vague or mislabelled answer scores nothing.
- **FP/claim** — how much of what the model said was wrong: false alarms divided by the
  findings it actually made. Its complement, **precision** (1 − FP/claim), is how far you can
  trust the model when it speaks.

Accuracy on its own can be raised by claiming generously, which is why both are always shown
together. Full definitions, formulas and worked arithmetic: §2.7.

## 1.4 Headline results

All figures are on the **same 23 scenarios**, three runs each, so every row is
like-for-like. The headline is the deployed configuration — each model on the harness tuned
for it — and the no-harness rows are what the harness was measured against.

| configuration | accuracy | FP/claim | precision |
|---|---|---|---|
| **Qwen3.8-27B + its own harness** | **71.2 %** | 41.9 % | 58.1 % |
| **Qwen3.6-27B + its own harness** | 65.8 % | **38.7 %** | **61.3 %** |
| Qwen3.8-27B, no harness | 64.0 % | 65.7 % | 34.3 % |
| Qwen3.6-27B, no harness | 59.5 % | 40.0 % | 60.0 % |

- **With its own harness 3.8 finds 71.2 % of what was planted and 3.6 finds 65.8 %**; 3.6 is
  the more reliable speaker, 61.3 % precision against 58.1 %. The ranking is a trade, not a
  win: which model is better depends on whether a miss or a false alarm costs more where you
  mean to use it.
- **The harness did a different job for each model** — about 24 points of precision for 3.8,
  about 6 points of accuracy for 3.6.
- **Each model does best on the harness tuned for it.** Handing one model the other's harness
  lost ground rather than gaining it (§3.2).
- **Cost is roughly 3× apart** for the same exam: about 4.8 min and 5.7k completion tokens per
  answer for 3.6, about 13.5 min and 13.8k for 3.8 (§3.8).

## 1.5 Conclusions

1. **A harness is part of the model's deployment, not neutral infrastructure.** Everything a
   harness compensates for — how eagerly the model asserts, how much it verifies, whether it
   reaches for a tool — is behaviour. Behaviour moves when a model is retrained even when the
   architecture does not.
2. **So yes: moving from 3.6 to 3.8 required the harness to evolve with it.** One harness,
   tuned twice, was worth about 24 points of precision to 3.8 and about 6 points of accuracy
   to 3.6. The same wrapper is worth different things to different models, because the models
   were short of different things (§3.2).
3. **A harness does not transfer.** Every cross-loaded cell scored below the tuned one, and an
   earlier claim of a positive transfer (+8.3 points at 9 scenarios) decayed to −1 at 23 and
   was withdrawn. A new model version inherits an unproven harness, not a working one (§3.2).
4. **Re-measure the pair, then re-tune the harness on recorded evidence.** Diagnose from the
   saved artifacts, take one hypothesis, make one edit, regression-check the neighbours, keep
   or revert. That loop is what turned a subject with 34.3 % precision into one at 58.1 %
   (§2.5).
5. **Whether a harness feature is worth building is an empirical question about the model in
   front of you.** Both subjects were offered four sandboxed tool calls: 3.8 used them in about
   a quarter of runs, 3.6 never once in 144 (§3.9).
6. **Never quote tuning scores as expected performance.** Both models lost about 30 points
   moving from the split they were tuned on to unseen scenarios, and every re-tune after a
   model change inherits that rule (§3.6).
7. **Governance wants a repeatable measurement, not a demo.** Because every corpus stores the
   exact harness bytes and prompt behind its numbers, a model change can be re-measured and
   audited instead of argued about (§2.8).
8. **Two caveats about this exam.** Discriminating power is concentrated in two of eight
   families, and two planted controls are not measurable at this sample size (§3.1, §3.10).

---

# 2 · Methodology

The task, how the data were made, what the harness is, how it was grown, how it was measured, and how the exam was kept honest.

## 2.1 The task and the research question

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

## 2.3 Zero-shot baselines

Each model first answered all 47 books three times with **no harness** — raw scenario
data plus the task prompt and output schema. These are the baselines
(`results/xam_v5/` for 3.8, `results/xam_q36/` for 3.6) and establish each model's
unaided ability. They are the reference against which the harness is measured.

## 2.4 The harness, in three parts

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

## 2.5 Growing the harness from evidence

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

The harness was not written in one sitting. **A model built it.** The operator-side agent
that ran the campaigns was driven by a third model, DeepSeek V4.1 Flash, deliberately not
one of the two subjects, so no subject tuned the exam it later took. It worked from
recorded artifacts, not impressions, in a fixed loop:

1. Run the frozen harness over all 23 **optimization** scenarios. Keep the corpus and the
   per-unit scorer output.
2. Read what actually happened: the recorded prompt, the answer, the tool log, and the
   scorer's per-unit diff. Say *why* each failed unit failed.
3. Form **one** hypothesis and make **one** edit — a new section in `stats_pack.py`, a
   discipline clause in `HARNESS_RULES`, or a new pinned system prompt.
4. Test it on the affected scenarios in a scratch corpus, then re-check the neighbouring scenarios
   the edit could have disturbed.
5. Keep or revert. Snapshot the harness bytes **and** the prompt into
   `results/<corpus>/harness_snapshot/` before the next run.
6. Never tune against `heldout`, and never let a held-out result influence an edit.

That produced seven harness versions for 3.8 (v1.0 → v1.6e), driven by **307
per-scenario diary entries**, 268 of which involved reviewing or editing the harness. For
3.6 it produced two kept edits from the same base. Both lineages are frozen here, so you
can inspect the method instead of taking it on trust — including the fix that was
**declined** (runbook §36), not just the ones kept.

**The method costs time, and that cost is part of the design.** On one llama.cpp slot, one
23-scenario optimization pass takes about **7 hours** for 3.8 and about **2 hours** for 3.6; a
72-call held-out exam takes about **16 hours** and about **6 hours**. Every harness version
costs a pass. That is why the loop allows one hypothesis per pass instead of searching the
prompt space — and it is also why the cheaper model's harness needed two edits, not seven.

Two limits of this method, stated plainly:

- A human chose which failures to chase. The model proposed and applied edits; it did not
  set the agenda.
- The frozen record proves **which harness bytes produced which numbers**
  (`harness_snapshot/MANIFEST.txt`). It does not prove which model wrote each line. The
  runbooks narrate that; it is not part of the evidence.

---

## 2.6 Evaluation protocol

* 24 held-out books × 3 runs = 72 calls per exam.
* Canonical samplers (temperature 1.0, top_p 0.95, top_k 20), streaming, no
  `max_tokens`, 3600 s per-call timeout, one generation at a time (the server has a
  single slot).
* Three runs are essential: they separate a *consistent* failure from an unlucky one.
  This study found books scoring 0/3 and 3/3 across configurations, and a single run
  would have shown only "a shock" or "a drift" with no way to tell which was typical.
* Every corpus is scored with the same scorer (`score_xam.py`, v3) against the same
  fixed truth manifests.

---

## 2.7 The two metrics in full

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

## 2.8 Keeping the exam honest

Two rules made the four background questions answerable, and both are kept visibly in
the repo.

- **The answer key is fixed and out of reach.** Truth is generated, never hand-labelled.
  The model sees only opaque `sc-<6hex>` ids; names and manifests live in a separate
  folder. A byte-level leak scan runs at build time and again before the first prompt.
  `dataset.json` hashes every model-facing file, so "both models saw the same exam" is
  provable rather than assumed.
- **Tuning must not touch the reported number.** Tuning used the 23-scenario optimization
  split; the reported number comes from the 24-scenario held-out split, scored once. The
  frozen harnesses scored **97.7 %** and **95.5 %** on tuning, and **69.1 %** and
  **64.2 %** on held-out data — an optimism gap of about 30 points for *both* models
  (§3.6). A sign-off based on tuning scores would have been wrong by that much. For the
  same reason, `sc-e6ffa4` is published as a **recorded failure** rather than quietly fixed.

The machinery behind those rules: `data/truth/seal.json` freezes the answer key, matching
is strict so a vague or mislabelled answer scores nothing, wall clock and token usage are
recorded on every run, and every corpus stores the exact harness bytes and prompt that
produced it (`results/<corpus>/harness_snapshot/`).

---

---

# 3 · Results

Everything behind the headline: what the models found, what the harness changed, and every table.

## 3.1 Can a model find the insight?

The campaigns answer **yes, with limits**. Harnessed, the two models recovered 65.8 % and 71.2 % of what was
planted on the held-out split, naming the line, the years and the pattern correctly. The
limits are shared rather than model-specific: `drift`, `recovery` and `volatility` saturate
for every harnessed configuration, `noise_trap` lookalikes are hard for all of them, and the
coordinated multi-line `systemic` scenarios are where the two separate (INDEX §6).

Two design notes carry beyond this dataset:

- `recommended_action` is part of the answer on purpose — the goal is a finding worth
  escalating, not a labelled time series. It is recorded in every corpus and, to be
  clear, **it is not scored**. Grading free-text advice is a separate unsolved problem.
- **Claims A/E is the first surface, not the limit.** The skill being tested is deciding
  whether a gap between actual and expected is signal. That is the same move in lapse and
  persistency, expense A/E, mortality and morbidity studies, and reserve-adequacy work.
  Extending to those means a new scenario family and a new section in `stats_pack.py`. It
  does not mean a new benchmark, a new scorer or a new governance argument.

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

## 3.2 What the harness is worth, and whether it transfers

This is the measurement the project exists to make. The two campaigns are the experiment
and the table below is its result: the held-out split, the same 23 scenarios in every row
(`sc-e6ffa4` excluded, since it never finished under one configuration — INDEX §8).
Definitions and arithmetic in README §3.

All figures on the **same 23 books** (the failed scenario is treated separately in §3.11,
so every row is like-for-like). **Cell = accuracy | FP/claim.**

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

Both subjects are 27 B models, on one llama.cpp slot, with identical samplers. The
difference between them is not architecture. It is behaviour that reinforcement learning
taught each model: how it reasons, how much it verifies, how eager it is to run code. The
harness has to compensate for that, and it compensates differently for each model:

- **3.8 without a harness finds a lot and says too much.** It found 64.0 % of what was
  there, but 65.7 % of its claims were wrong — 34.3 % precision. Its problem is not
  seeing; it is asserting. Its own harness moved it +7.2 points on recall and **+23.8
  points on precision** (34.3 % → 58.1 %).
- **3.6 without a harness fails the other way.** It found 59.5 % and was already 60.0 %
  precise. The same harness gave +6.3 recall and **+1.3** precision (60.0 % → 61.3 %),
  because 3.6 did not have 3.8's problem to fix.
- **Each model does best with the harness tuned for it**: 3.8 gets 71.2 own vs 70.3 on
  3.6's; 3.6 gets 65.8 own vs 64.9 on 3.8's. An earlier claim that a harness transfers
  (+8.3 points) rested on 9 scenarios; at 23 scenarios the same comparison gave −1, so the claim
  was withdrawn.
- **Behaviour decides whether a harness feature exists at all.** Both models were offered
  up to 4 sandboxed python calls. 3.8 used them in about 24 % of runs. **3.6 used them 0
  times in 144 runs**, after two separate attempts to get it to use them.
- **Over-claiming is a separate behaviour from mislabelling.** Splitting false alarms
  into "explained by a mislabel" and "invented from nothing": under 3.8's own harness, 31
  of 69 false alarms were invented; under 3.6's, 6 of 50.

The conclusion this repo exists to record: **harness requirements follow model behaviour,
not model weights.** A harness is not infrastructure you qualify once and reuse. It is
part of a model's deployment, and it has to be rebuilt when the behaviour under it
changes. That is why this repo publishes two harness lineages that started from the same
base and ended in different places.

## 3.3 What the harness changed, edit by edit

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

## 3.4 Full held-out results (24 books, where available)

§1.4 is on the common 23 books so every row is like-for-like. The table below is the full
24-book view, where a configuration completed the whole exam.

| configuration | accuracy | FP/claim | precision | FP/run |
|---|---|---|---|---|
| 3.8 + own harness (v1.6e + 3866 prompt) | **69.1 %** | 44.8 % | 55.2 % | 0.96 |
| 3.6 + own harness (tuned + 3053 prompt) | 64.2 % | **38.8 %** | **61.2 %** | 0.69 |
| 3.6 + 3.8's harness (v1.6e + 3866 prompt) | 63.4 % | 44.7 % | 55.3 % | 0.88 |

## 3.5 The controlled cross-model comparison

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

## 3.6 Optimisation split vs held-out — the optimism gap

| model | best optimisation | held-out | gap |
|---|---|---|---|
| Qwen3.6-27B | 42/44 = 95.5 % | 63.4 % | **−32.1** |
| Qwen3.8-27B | 43/44 = 97.7 % | 69.1 % | **−28.6** |

Both models lose roughly **30 points** moving from the 23 books they were tuned on to
24 unseen books. This is a property of the benchmark and harness, not of either
model, and it is the single most important methodological finding: **optimisation-split
scores are a ranking device and must never be quoted as expected performance.**

## 3.7 Precision, false alarms and over-claiming

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

## 3.8 Cost — run time, tokens, throughput

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

## 3.9 Tool use

The harness offers up to 4 sandboxed Python calls per run.

| model | tool-using runs |
|---|---|
| Qwen3.8-27B | ~24 % (17 of 72 held-out; 10 of 64 in the tuned corpus) |
| **Qwen3.6-27B** | **0 of 144 — never** |

3.6's tool loop is entirely dormant despite the tool being offered and two dedicated
attempts to activate it (a rewritten efficiency clause, and mandatory-use wording).
It correctly judges that the evidence pack already contains the arithmetic. **This
asymmetry is not a defect but it is a robustness advantage**: the one hard failure in
this study (§3.11) was a malformed tool request, which 3.6 cannot produce.

## 3.10 Identifiability — not every miss is a model failure

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

## 3.11 The `sc-e6ffa4` failure — full diagnosis

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
between the two bounds. Every conclusion in §1.5 has a margin far larger than
±7 points: the recall gap is 5.4, the precision gap 3.2, and 3.8's unharnessed
precision sits 24 points below its harnessed figure. None of them move.

**Decision recorded:** the underlying parser defect was **deliberately not patched**.
A defect that exists only as a documented failure remains auditable; one that has
been patched away becomes a silent gap. `sc-e6ffa4` must always be reported as
**failed**, never as absent or excluded.

---

---

# 4 · Conclusion

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
the two unidentifiable units identified in §3.10 should be reclassified rather than
counted against any model.
