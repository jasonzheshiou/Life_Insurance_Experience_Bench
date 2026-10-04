# Qwen3.6-27B harness campaign — runbook & pass 1 results

Model: `Qwen3.6-27B` (GGUF `Qwen3.6-27B-Q8_0.gguf`, llama.cpp `b10802-d1a92352c`,
n_ctx 260096, **1 slot**). Harness: v1.6e frozen (pack + rules + ≤4 python turns).
Pass 1 corpus: `results/harness_q36_p1/`, 23 optimization books × 1 run.
Prompt: pinned to `data/prompts/system_v2_baseline.txt` (3053 chars, sha `54d6d5c2bc742919`),
i.e. the same prompt as the `xam_q36` zero-shot baseline → the comparison below
isolates the harness (pack + rules), not a prompt change.

---

## 1. Pass 1 — COMPLETE

`state: PASS_COMPLETE`, 23/23 books, `failures: none`, ended 2026-09-17T00:14:01Z.

### Runtime (measured, not projected)

| metric | value |
|---|---|
| sum of per-book wall | 6911 s = **115.2 min = 1.92 h** |
| wall-clock first→last answer | 7324 s = **122.1 min = 2.03 h** (extra ≈ 7 min = scoring/index overhead) |
| mean per book | **300.5 s = 5.01 min** (range 166–434 s) |
| completion tokens | 128 267 total, mean **5577/book** |
| aggregate throughput | **17.5 tok/s** — stable, consistent with 1 slot |
| slowest / fastest books | `sc-f520e5` 434 s / `sc-409000` 166 s |

Cost tracks completion tokens almost linearly (≈ 18 tok/s), so a book's price is
how long the model reasons, not its prompt size.

## 2. Pass 1 read-out — gate FREEZE, all criteria met

Like-for-like: same 23 optimization books, run 1 only on all three corpora.

| family | 3.6 baseline | **3.6 + harness p1** | 3.8 + harness p7 |
|---|---|---|---|
| drift | 2/3 = 66.7 % fp1 | 2/3 = 66.7 % fp2 | 3/3 = 100 % fp1 |
| mixed | 3/4 = 75.0 % fp1 | 4/4 = 100 % fp3 | 4/4 = 100 % fp4 |
| noise_trap | 1/5 = 20.0 % fp4 | **5/5 = 100 % fp1** | 5/5 = 100 % fp1 |
| recovery | 2/2 = 100 % fp0 | 2/2 = 100 % fp0 | 2/2 = 100 % fp0 |
| shock | 4/4 = 100 % fp0 | **2/4 = 50.0 % fp2** | 4/4 = 100 % fp2 |
| systemic | 14/24 = 58.3 % fp12 | **23/24 = 95.8 % fp1** | 23/24 = 95.8 % fp10 |
| volatility | 1/2 = 50.0 % fp1 | 1/2 = 50.0 % fp1 | 2/2 = 100 % fp4 |
| CLEAN | silent | silent | silent |
| **TOTAL** | **27/44 = 61.4 %**, FP/run 0.83 | **39/44 = 88.6 %**, FP/run **0.43** | 43/44 = 97.7 %, FP/run 0.96 |

Gate checks: strict ≥80 % PASS · FP/run ≤1.0 PASS · clean never accused PASS ·
no badjson/errors PASS · both drift strata not worse PASS.
Written to `results/logs/harness_q36_p1_gate.json`.

**Registered predictions, resolved:**
1. *The pack transfers and lifts systemic* — **TRUE, decisively.** systemic
   58.3 % → 95.8 % (+9 units) and its false alarms collapsed 12 → 1. That family
   was 3.6's worst baseline weakness (family delta −16 vs 3.8). With the harness,
   3.6 matches 3.8 exactly on systemic recall (23/24) while emitting **1 FP
   against 3.8's 10**.
2. *The dual-reading hedge will raise 3.6's false alarms* — **FALSE (good).**
   FP/run fell 0.83 → 0.43. No clause needs cutting on that account.

**The one real cost:** shock 4/4 → 2/4, entirely one book (`sc-48351f`).

## 3. The wrong books (input to the per-scenario loop)

| book | family | pass 1 | baseline | fp | failure mode |
|---|---|---|---|---|---|
| `sc-48351f` | shock | 0/2 | 2/2 | 2 | **REGRESSION.** Truth = single-year 2023 shock (TPD 1.3, IP 1.2). Model reported a 2015–2022 **drift** on both lines, conf 0.85 — read the trend, never tested the jump. |
| `sc-3c83fd` | drift | 0/1 | 0/1 | 1 | Truth = CI **drift** 2016–2019 (factor −0.1). Model called it a **shock** "decrease then increase" 2018–2024, conf 0.9. Same movement, wrong pattern (PATTERN_EQUIV is exact) + overshot window. |
| `sc-6e2478` | volatility | 0/1 | 0/1 | 0 | Truth = Death **volatility** (0.2). Model said **clean** — found nothing. Missed dispersion entirely. |
| `sc-d72b95` | systemic | 3/4 | 2/4 | 0 | Partial, but **improved** from baseline. |

Books improved over baseline: `sc-137901` +2, `sc-314eca` +2, `sc-bba653` +3,
`sc-9660b9` +3, `sc-8a9fa1` +1, `sc-8d3b47` +1, `sc-d72b95` +1, `sc-f520e5` +1.

**Three of the four wrong books fail on pattern discrimination**, not on finding
the movement: drift read as shock, shock read as drift, volatility not seen at
all. That is a single coherent weakness, and it is the pass-2 target.

## 4. Dominant structural finding: the tool loop is dead for 3.6

| corpus | tool_calls histogram |
|---|---|
| **3.6 pass 1 (23 books)** | **`{0: 23}` — never called, not once** |
| 3.8 p7 (23 books) | `{0: 20, 1: 3}` |
| 3.8 final held-out (72 runs) | `{0: 55, 1: 12, 2: 5}` |

All 23 records are a single turn, no tool flag, empty transcript, no retries —
real behaviour, not a dropped transcript. The prompt *does* offer the tool
(HARNESS MODE clause 2); clause **3b** discourages it ("At most TWO tool calls,
and if the pack answers the question, answer immediately without any tool call").

So **3.6's entire gain is attributable to the pack + rules**, and the third
pillar of v1.6e is inert for this model. The three pattern-discrimination
failures above are exactly what a verification call would settle (monotone
decline vs dip-and-rebound; is dispersion elevated?).

## 5. Pass-2 plan — SUPERSEDED, see section 9

This section held the *pre-diagnosis* guesses for pass 2 (edit the rules block,
relax clause 3b). Diagnosis of the four wrong books then showed all three pattern
failures trace to the evidence pack's smoothed-window headline, so the actual
pass-2 edit landed in `stats_pack.py`. **Section 9 is the authority** — the edit,
its validation, and the commands. Kept here only so the reasoning trail is not
rewritten after the fact.

The one guess that survived: probe a single wrong book in a scratch corpus
(`OUT=harness_q36_probe`) rather than re-running all 23, so pass 1 stays a clean
frozen measurement.

## 6. Status / read-out commands

```bash
bash scripts/harness_pass_run.sh --status                      # non-clobbering
python3 scripts/score_xam.py --run-dir results/harness_q36_p1/zero_shot \
  --json-out results/harness_q36_p1/scores.json                # re-score
```

## 7. Snapshot bug — FIXED

**Symptom.** `scripts/harness_pass_run.sh` snapshots the harness at pass start,
but its prompt-copy branch only fired when `PINNED_PROMPT_FILE` was **exported**
in the launcher environment. Pass 1's launcher did not export it (harmless: the
runner's default already points at that same file), so `system_prompt.txt` was
missing from `results/harness_q36_p1/harness_snapshot/`. It was copied in by hand
with a provenance note appended to `MANIFEST.txt`.

**Fix** (applied after the pass ended — editing a bash script mid-run can corrupt
execution, because bash keeps reading the file as it goes). The block now falls
back to the wrapper's own default (`data/prompts/system_v2_baseline.txt`) instead
of silently skipping the copy, and prints a `WARNING:` line into the MANIFEST if
the named file is missing, so a code-only snapshot can never again look complete.

**Tested** by extracting the real block and running it against a scratch corpus:

| case | result |
|---|---|
| `PINNED_PROMPT_FILE` unset (the pass-1 bug) | copies default, labels `(from data/prompts/system_v2_baseline.txt)` |
| set to a custom file | copies that file, labels `(…; PINNED_PROMPT_FILE)` |
| set to a missing file | `WARNING: … snapshot has code only`, code still snapshotted |

`bash -n` clean; `harness_preflight.sh` re-run afterwards → **PREFLIGHT: PASS**;
frozen `stats_pack.py` / `run_zero_shot.py` hashes unchanged
(`16e53e0ef0b097ab` / `a4b967de975625f9`).

## 9. Pass 2 — diagnosis, harness edit, commands

### 9.1 The aim, answered with data already in hand

The question was whether *a similar level of optimisation produces a different
result for 3.6 vs 3.8*. On the three books where the harness misdirects, both
models ran **identical harness bytes and an identical prompt**:

| book | truth | 3.8 p7 (v1.6e) | 3.6 pass 1 (v1.6e) |
|---|---|---|---|
| `sc-48351f` | shock 2023, TPD 1.3 / IP 1.2 | **2/2** | 0/2 |
| `sc-3c83fd` | drift 2016–2019, CI −0.1 | **1/1** | 0/1 |
| `sc-6e2478` | volatility 2015–2024, Death 0.2 | **1/1** | 0/1 |

3.8 extracted the signal from the same misleading pack; 3.6 followed the pack's
own headline. **Same optimisation level, materially different result** — 4/4
units vs 0/4 on exactly these three books, which is the whole of the gap between
88.6 % and 97.7 %.

### 9.2 Root cause (pack defect, not model incapability)

`smooth_stats()` builds a **left-labelled** 3-year moving average — the docstring
says "centred", but each window is labelled with its FIRST year. A 2015–2024
series therefore produces labels 2015–2022, and the point labelled `2022` is
really the mean of 2022–2024.

Two consequences, both visible in `sc-48351f`:

* the pack printed `smoothed 3y MA: amplitude 0.149 over 2015-2022` — declaring
  the shape stops in 2022 when the data runs to 2024;
* the profile headline said **"report the smoothed span as the window"**, so the
  model reported a 2015–2022 drift. The truth is a **2023** shock, sitting in the
  MA's last point and in the yearly row (`2023:1.24(z+7.6)`, and the cross-line
  row shows two lines swinging together in 2023) — but the headline told the
  model not to look there.

### 9.3 The edit (surgical, no statistics changed)

In `scripts/stats_pack.py` only:

* record `smoothed.covered_from` / `covered_to` — the span the MA actually
  averages — separately from the label range, leaving `from`/`to` untouched so no
  other consumer changes behaviour;
* the `sustained-move (smoothed)` and `SHAPED-AND-GRADUAL` headlines now name the
  **covered** span and add: a move arriving in one of the most recent years is not
  described by this smoothed shape, so read the yearly row and the cross-line
  swing counts before choosing the window — and a single late year moving several
  lines at once is a one-off change, not this span;
* the printed MA line now states the label range and the covered range.

No threshold, z-score, excursion or calibration constant was touched, so nothing
that already worked can flip on a statistic.

**Lineage:** `stats_pack.py` `16e53e0ef0b097ab` → **`78717ce2dbc74e06`**;
`run_zero_shot.py` unchanged (`a4b967de975625f9`); prompt unchanged. The 3.8
frozen record stays reproducible from
`results/harness_opt_p7/harness_snapshot/` and `results/harness_final/harness_snapshot/`.

### 9.4 Validation (zero API calls)

| check | result |
|---|---|
| packs regenerate, all 23 optimization books | 0 failures |
| books whose profile headline changed | **6 / 23** — `sc-137901`, `sc-48351f`, `sc-63f1c7`, `sc-8d3b47`, `sc-da1123`, `sc-f69eea` |
| headline changes outside a smoothed branch | **none** |
| CLEAN book `sc-14cdd9` | only the cosmetic MA-label line changed; no verdict moved |
| `harness_preflight.sh` leak scan | **PASS** |
| `--dry-run` rehearsal of the probe below | prompt builds, new text present, pinned prompt confirmed, no API call |

### 9.5 Commands

**Optional early-warning probe** (~5 min, 1 call) — skippable, since pass 2 below
already contains this book:

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena
setsid nohup env SIDS=sc-48351f MODEL=Qwen3.6-27B OUT=harness_q36_probe PASS=2 \
  RUNS=1 WAIT_ENDPOINT=600 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  bash scripts/harness_pass_run.sh \
  >>results/logs/harness_q36_probe_console.log 2>&1 </dev/null &
disown 2>/dev/null || true
```

Probe corpus is scratch (`harness_q36_probe`) so pass 1 stays a clean frozen
measurement and a failed edit cannot contaminate pass 2. Read the result with:

```bash
python3 scripts/harness_diff.py sc-48351f --out harness_q36_probe
```

Truth is a shock on TPD **and** IP in 2023 — success means `strict 2/2` with the
pattern read as one-off/shock, not a 2015–2022 drift.

**Primary — full pass 2, all 23 books, mirroring 3.8's p2** (~2 h, 23 calls):

```bash
setsid nohup env MODEL=Qwen3.6-27B OUT=harness_q36_p2 PASS=2 RUNS=1 \
  WAIT_ENDPOINT=600 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  bash scripts/harness_pass_run.sh \
  >>results/logs/harness_q36_p2_console.log 2>&1 </dev/null &
disown 2>/dev/null || true
```

Then compare against pass 1 and both 3.8 references:

```bash
python3 scripts/harness_gate.py results/harness_q36_p2/zero_shot \
  --split optimization --runs 1 --reference results/xam_q36/zero_shot \
  --label "3.6 pass 2" --json-out results/logs/harness_q36_p2_gate.json
```

The two remaining wrong books are queued behind this one, per the loop rule:
`sc-3c83fd` (drift→shock; the pack's `onset` row says "one-off level change, not a
build-up" on a 4-year decline) and `sc-6e2478` (pack contradicts itself — profile
says scatter-dominant, reading guide says overdispersion x5.23 is "never by itself
an anomaly", and the model obeyed the threshold).

**Overfitting guard:** these edits are tuned on the optimization split, which is
what it exists for — but the held-out exam is the only number that counts. 3.8's
97.7 % became 69.1 % there. Do not read pass 2's optimization score as expected
held-out performance.

### 9.6 Protocol decision — pass 2 is ALL 23 books, mirroring 3.8

3.8's campaign, verified from its corpora:

| pass | books | strict | note |
|---|---|---|---|
| p1 | 23 | 27/44 = 61.4 % | first harness |
| **p2** | **23** | **32/44 = 72.7 %** | **full sweep, +11.3 pts** |
| p3 | 23 | 33/44 = 75.0 % | |
| p4 | 23 | 36/44 = 81.8 % | |
| p5 | **1** | 1/1 | the campaign's *only* single-book pass |
| p6 | 23 | 39/44 = 88.6 % | |
| p7 | 23 | 43/44 = 97.7 % | frozen |

So 3.8's pass 2 was a full 23-book sweep; the single-book probe was p5, not p2.
Mirroring the protocol means **3.6's pass 2 is all 23 books** — and because pass 2
then contains `sc-48351f` anyway, the 5-minute probe above becomes optional
early-warning rather than a required step.

**One honest caveat on "similar level of optimisation".** The *protocol* mirrors,
but the starting points do not: 3.8's p2 began from a 61.4 % harness and gained
+11.3 points, whereas 3.6's pass 2 begins from an 88.6 % harness (3.8 did not
reach 88.6 % until its p6). So the pass-2 *gain* is not a like-for-like number.
What is like-for-like is **"latest harness, all 23 books"**: 3.6 pass 2 versus
3.8 p7 (97.7 %). Read the comparison that way, and treat the 3.6 pass-2 delta as
"what one more round buys from an already-mature harness".

## 11. Pass 2 — COMPLETE (the pack fix worked)

Run 2026-09-17, `results/harness_q36_p2/`, 23 books × 1 run, all 23 valid,
`failures: none`. Snapshot self-contained this time — `MANIFEST.txt` lists
`stats_pack.py 78717ce2dbc74e06`, `run_zero_shot.py a4b967de975625f9` **and**
`system_prompt.txt 54d6d5c2bc742919`, so the snapshot fallback fix is confirmed
in a live run.

### Result

| corpus | strict | FP/run | FP total |
|---|---|---|---|
| 3.6 baseline | 27/44 = 61.4 % | 0.83 | 19 |
| 3.6 pass 1 | 39/44 = 88.6 % | 0.43 | 10 |
| **3.6 pass 2** | **42/44 = 95.5 %** | **0.30** | **7** |
| 3.8 p7 (frozen) | 43/44 = 97.7 % | 0.96 | 22 |

Gate: **FREEZE — all criteria met** (`results/logs/harness_q36_p2_gate.json`).
Runtime: 114.2 min summed, 2.02 h wall-clock, 298.0 s/book, 17.6 tok/s — same as
pass 1. Tool calls still `{0: 23}`: the python loop remains untouched.

### Per family (23 optimization books, run 1)

| family | 3.6 baseline | 3.6 p1 | **3.6 p2** | 3.8 p7 |
|---|---|---|---|---|
| drift | 2/3 | 2/3 | **3/3** | 3/3 |
| mixed | 3/4 | 4/4 | **3/4** | 4/4 |
| noise_trap | 1/5 | 5/5 | **5/5** | 5/5 |
| recovery | 2/2 | 2/2 | **2/2** | 2/2 |
| shock | 4/4 | 2/4 | **4/4** | 4/4 |
| systemic | 14/24 | 23/24 | **23/24** | 23/24 |
| volatility | 1/2 | 1/2 | **2/2** | 2/2 |
| CLEAN | silent | silent | **silent** | silent |

### The four wrong books: three fixed

| book | family | baseline | pass 1 | pass 2 | |
|---|---|---|---|---|---|
| `sc-48351f` | shock | 2/2 | 0/2 | **2/2** | FIXED — the regression is undone |
| `sc-3c83fd` | drift | 0/1 | 0/1 | **1/1** | FIXED |
| `sc-6e2478` | volatility | 0/1 | 0/1 | **1/1** | FIXED |
| `sc-d72b95` | systemic | 2/4 | 3/4 | 3/4 | still short |

The single regression `sc-f520e5` (mixed, 2/2 → 1/2) is **sampling variance, not
the edit**: its pack changed only in the cosmetic MA-label line (0 headline
changes) and the prompt sent in pass 1 vs pass 2 differs in those two label lines
only. At temperature 1.0 with one run per book, a flip either way is expected.

### Trajectory vs 3.8

* 3.8: p1 61.4 → p2 72.7 → p3 75.0 → p4 81.8 → p6 88.6 → p7 97.7 (6 passes)
* 3.6: base 61.4 → p1 88.6 → p2 **95.5** (2 passes)

3.6 is within **2.2 points** of 3.8's frozen best while emitting **3.2× fewer
false alarms** (0.30 vs 0.96) and never accusing the clean book.

## 12. Pass 3 — plan

The two books still short are no longer the smoothed-window defect; both are
pattern/incompleteness failures of a kind a verification call would settle:

* `sc-d72b95` — truth is shock 2020 on Death **and** CI, plus drift 2021–2024 on
  **both** lines. The model got the shock on both lines and the CI drift, but
  **missed the Death drift**. A line-by-line completeness check catches this.
* `sc-f520e5` — truth is IP drift + Death **volatility**; the model reported
  Death **drift**, a pattern mislabel (it had this book right in pass 1). A
  dispersion check separates volatility from drift directly.

Both point at the same untouched lever: **the python tool loop has never been
used once** (0 calls across both passes). Clause 3b tells the model to answer
immediately when the pack suffices, and 3.6 obeys it absolutely. The pass-3
candidate is to relax 3b for 3.6 — require one verification call when two lines
or two patterns are in play — and re-run the standard 23-book sweep.

Guard: this is the first edit that touches `run_zero_shot.py` (the rules block),
so the frozen 3.8 bytes stop matching the tree. Their snapshots
(`results/harness_opt_p7/harness_snapshot/`, `results/harness_final/harness_snapshot/`)
remain the reference for the 3.8 record.

### 12.1 The edit, as applied

Clause 3b rewritten in `HARNESS_RULES` (`run_zero_shot.py`). It previously read
"At most TWO tool calls, and if the pack answers the question, answer immediately
without any tool call" — which 3.6 obeyed absolutely (0 calls in 46 runs). The new
text keeps the answer-immediately default and keeps the two-call ceiling, but
names the two forks where a single call is now expected:

* two or more lines move (or CROSS-LINE reports a coordinated event) and the
  answer would name only some of them — open the CSVs and check every remaining
  line, rather than trusting the pack's headline to have covered it;
* a line's shape could be a sustained move **or** elevated scatter — compute the
  year-to-year dispersion and let the number choose the pattern.

These map directly onto the two books still short: `sc-d72b95` (missed the Death
drift while catching the same drift on CI) and `sc-f520e5` (Death volatility
reported as drift).

**Validated with zero API calls:** rules block 5021 → 6077 chars; clauses 2, 3 and
3c verified intact, two-call ceiling still stated; `harness_preflight.sh` **PASS**;
`--dry-run` builds prompts for both target books with the new text present.

**Lineage:** `run_zero_shot.py` `a4b967de975625f9` → **`c49a6407aaa4bfb8`**;
`stats_pack.py` unchanged from pass 2 (`78717ce2dbc74e06`); prompt unchanged.

### 12.2 Pass 3 command

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena

setsid nohup env MODEL=Qwen3.6-27B OUT=harness_q36_p3 PASS=3 RUNS=1 \
  WAIT_ENDPOINT=600 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  bash scripts/harness_pass_run.sh \
  >>results/logs/harness_q36_p3_console.log 2>&1 </dev/null &

disown 2>/dev/null || true
sleep 5
DRV="harness_pass"; DRV="${DRV}_run.sh"; pgrep -f "$DRV" >/dev/null && echo RUNNING || echo "NOT RUNNING"
```

~2 h, 23 calls. What to watch: the `tool_calls` histogram in the new corpus —
if it is still `{0: 23}` the relaxation did not take and the lever is dead for
3.6; if calls appear, check whether they land on the books that were short.

## 14. Pass 3 — COMPLETE, intervention FAILED (reverted)

Run 2026-09-17, `results/harness_q36_p3/`, 23 books, all valid, `failures: none`.
Snapshot self-contained: `stats_pack 78717ce2dbc74e06`,
`run_zero_shot c49a6407aaa4bfb8`, `system_prompt 54d6d5c2bc742919`.

| corpus | strict | FP/run | FP total |
|---|---|---|---|
| 3.6 baseline | 27/44 = 61.4 % | 0.83 | 19 |
| 3.6 pass 1 | 39/44 = 88.6 % | 0.43 | 10 |
| **3.6 pass 2** | **42/44 = 95.5 %** | 0.30 | 7 |
| 3.6 pass 3 | 40/44 = 90.9 % | **0.13** | 3 |
| 3.8 p7 (frozen) | 43/44 = 97.7 % | 0.96 | 22 |

### The clause-3b relaxation did nothing

**`tool_calls` is `{0: 23}` again — and 1 turn per book.** Across all three passes
3.6 has now made **zero tool calls in 69 runs**. The rules text explicitly asked it
to spend one call on exactly the two forks it kept failing, and it still answered
straight from the pack. The prompt did grow (rules 5021 → 6077 chars), so the
instruction was delivered; the model simply did not act on it.

**Conclusion: the python tool loop is unused by Qwen3.6-27B *in this harness* — but
the model is fully capable of calling it.** (Section 17 corrects the stronger
claim originally written here. A probe shows 3.6 calls the tool reliably when the
computation is genuinely needed, and declines only when it judges the pack to have
answered — which in this harness is literally true, since the pack really does
contain the arithmetic.) In practice the loop remains a 3.8-only feature (3.8:
3/23 optimization, 17/72 held-out). Do not spend more passes trying to wake it by
rephrasing the rules — this was the second failed attempt, and section 17 explains
why rephrasing cannot work.

### What actually moved

| book | family | pass 1 | pass 2 | pass 3 | |
|---|---|---|---|---|---|
| `sc-3c83fd` | drift | 0/1 | 1/1 | **0/1** | lost — read as CI **shock** 2020–2024 |
| `sc-d72b95` | systemic | 3/4 | 3/4 | **2/4** | lost — found Death shock + CI drift, **missed the CI shock** |
| `sc-f520e5` | mixed | 2/2 | 1/2 | 1/2 | unchanged — Death volatility read as drift |

Neither regression is attributable to the new clause, because the clause's
mechanism never fired. Both are the same books flipping between readings across
runs — `sc-3c83fd` has now been right once and wrong twice, `sc-d72b95` has lost a
different unit each time.

**Noise floor:** passes 2 and 3 are the same experiment (identical pack, no tool
use, differing only in unused rules text) and scored 42 and 40. So **±2 units
(±4.5 pts) is run-to-run noise** at 1 run/book, temperature 1.0. Any future pass
must clear that band before it counts as an effect — this is the single most
important number for reading the rest of the campaign.

### Action taken: reverted

Clause 3b restored from `results/harness_q36_p2/harness_snapshot/run_zero_shot.py`,
so the tree is back to the pass-2 configuration — the best-measured one
(`run_zero_shot.py a4b967de975625f9`, `stats_pack.py 78717ce2dbc74e06`). An edit
that changes 1 KB of prompt without changing behaviour should not be shipped.
Pass 3's bytes remain frozen in its own snapshot if that config is ever wanted.

Pass 3's FP figure (0.13) is the best observed and is real as a measurement, but
with 3 vs 7 total false alarms it is inside the same noise band, and it arrived
with a 2-unit recall cost. Not worth a config change on this evidence.

## 15. Pass 4 — candidate (mechanism-based, unlike pass 3)

`sc-3c83fd`'s pack **still** misdirects, and it is the same class of defect the
pass-2 fix repaired. Verified on the current pack:

* `[CI] evidence profile: no strong signal` — on a line whose truth is a 4-year
  decline. The classifier misses it because `gradual` needs smoothed R² ≥ 0.75
  (this line is 0.32), `r2 >= 0.45` fails (0.07), the excursion is only 2 years
  wide, and the same-direction-run branch requires **≥ 6** years when the actual
  run is **4** — even though the pack prints `longest run: 4y down (-0.367)`;
* `[CROSS-LINE] -> 3 of 4 lines take their large swing in the SAME single year
  above; that is the signature of a book-wide one-off event, not a multi-year
  erratic stretch` — this tells the model to read the book as a one-off, which is
  precisely the shock mislabel it keeps producing.

Both lines push the model toward **shock** on a book whose answer is **drift**.
A pack-side fix (let a 4-year same-direction run with a material move reach the
sustained-move branch; stop the cross-line one-off note from overriding a single
line's own multi-year run) is the pass-4 candidate. Unlike pass 3 it corrects
evidence rather than requesting behaviour, and it can be validated offline across
all 23 books before spending a call.

Sequence for pass 4: apply the pack fix → regenerate all 23 packs and confirm
which books' headlines change and that the CLEAN book stays clean → preflight →
full 23-book sweep into `harness_q36_p4` → compare against pass 2, remembering the
±2-unit noise floor.

## 16. Later stages

1. ~~pass 1~~ done — 39/44 = 88.6 %, gate FREEZE
2. ~~pass 2~~ done — **42/44 = 95.5 %**, gate FREEZE, FP/run 0.30 — best config
3. ~~pass 3~~ done — 40/44 = 90.9 %; intervention failed, reverted
4. pass 4 = pack fix for `sc-3c83fd` (section 15), then full sweep
5. held-out exam: 24 books × 3 runs = 72 calls (~6 h at the measured rate)
   — this is where 3.8's 97.7 % collapsed to 69.1 %, so expect the real number
   well below the optimization score

## 17. Tool-call investigation — the earlier conclusion was WRONG

Section 14 concluded "the python tool loop is dead for Qwen3.6-27B". That is
**incorrect**, and the probe below overturns it. What is true: 3.6 makes no tool
calls *in this harness*. It is entirely capable of making them.

### What the stored reasoning already showed (no API calls)

Across all 69 pass records the reasoning **never** says "tool" or "python" —
except one run, which says:

    "No tool calls needed as the evidence pack already gives z=-20.4 for Cancer,
     which is overwhelmingly significant..."

Yet the same traces prove the model reads that whole region of the message:
23/23 cite the "evidence pack", 22/23 cite "[CROSS-LINE]". It is not skipping the
HARNESS MODE block; it is reading it and declining.

### Probe: `scripts/probe_tool_call.py`

An 814-char prompt (vs the harness's 17-18 KB), same tool-offer text, same
samplers, one call per variant, no truth and no scoring. Task = population sd of
30 values (tedious by hand, trivial with a tool).

| variant | clause | tool call? |
|---|---|---|
| `none` | no closing clause at all | **YES** |
| `escape` | "if the values above already answer the question, answer immediately without any tool call" | **YES** |
| `noescape` | efficiency only, no permission to skip | **YES** |
| `mandatory` | "you MUST use the tool at least once" | **YES** |
| `escape` | same clause, **easy** task (mean of 1-5) | **no** |

So the tool loop works, and **the escape clause is not what blocks it** — even
with no clause at all the model calls the tool when it needs the computation.

### Why it declines: literal compliance, in the model's own words

The easy-task run explains itself:

    * Mode: HARNESS MODE (allows tool usage but encourages efficiency).
    * Constraint: "Work efficiently: if the values above already answer the
      question, answer immediately without any tool call."
    * Since the arithmetic is simple, I should answer immediately without calling
      the Python tool, adhering to the "Work efficiently" instruction.

This is not a capability failure or a parser problem. The parser
(`extract_tool_request`) is robust — it handles code fences, outer-`{...}`
slicing, and the model's native `<tool_call>` syntax — and the model emits a
clean `{"tool": "python", "code": ...}` whenever it decides to use the tool.

### The corrected explanation

In the harness the pack **genuinely does contain the arithmetic**, so clause 3b's
condition is *satisfied*, and 3.6 obeys literally: it reads the pack, judges the
question answered, and answers. It is complying, not failing. 3.8 differs only in
disposition — it verifies anyway in ~13 % of optimization runs and ~24 % of
held-out runs. That is a model-character difference, not a harness defect.

This also explains why the pass-3 clause-3b rewrite did nothing: the model still
judged the pack to have answered. Adding "spend one call when two lines move"
did not override its reading of the pack as authoritative and complete.

### Open test (needs the server back)

The decisive pair was not completed: a prompt that **mirrors the harness** — the
answer already supplied in a pack-style block — with `escape` vs `mandatory`.
Prediction: `escape` declines, `mandatory` calls. The first attempt was invalid
because of a bug in the probe itself (the `provided` branch displayed the easy
values while the pack reported the hard dataset's sd, so the model correctly
spotted the mismatch and called the tool to check — fixed, values and pack now
agree). The server at `192.168.1.59:8080` went down mid-re-run (`Connection
refused`) and the pair must be re-run when it is back:

    python3 scripts/probe_tool_call.py --variant escape    --task provided
    python3 scripts/probe_tool_call.py --variant mandatory --task provided

### Consequence for the campaign

Do not spend further passes trying to wake the tool loop by rephrasing the
rules — two attempts have failed and the reason is now understood. If the loop is
wanted for 3.6 it must be made *unconditional* ("always verify X with a call"),
not conditionally permitted, because any condition the model can read as "the
pack already answered this" will be taken.

## 18. Tool-call investigation, part 2 — clause 3b is NOT the cause

Section 17 concluded the escape clause explains the decline. **That is also
wrong.** The full probe matrix, run against the live server, says otherwise.

### Results (one call each, same samplers as the benchmark)

| # | prompt | size | tool call? | reasoning mentions "tool" |
|---|---|---|---|---|
| 1 | toy, hard task, `none` (no clause) | 704 | **YES** | yes |
| 2 | toy, hard, `escape` (live 3b wording) | 814 | **YES** | yes |
| 3 | toy, hard, `noescape` | 773 | **YES** | yes |
| 4 | toy, hard, `mandatory` | 797 | **YES** | yes |
| 5 | toy, easy task, `escape` | 771 | no | yes — quotes the clause and obeys |
| 6 | toy, answer **already provided**, `escape` | 976 | **YES** | yes |
| 7 | toy, answer provided, `mandatory` | 959 | **YES** | yes |
| 8 | toy, answer provided, `escape`, **padded to 17.8 KB** | 17 856 | **YES** | yes |
| 9 | toy, answer provided, `mandatory`, padded | 17 839 | **YES** | yes |
| 10 | **REAL harness prompt** (`sc-d72b95`, unmodified) | 16 994 | **no** | **no — never mentions it** |
| 11 | **REAL prompt with clause 3b deleted** | 16 764 | **no** | **no — never mentions it** |

Run 6 is the key one: with the answer *already supplied* in a pack-style block,
the model still chose to verify, reasoning explicitly:

    "Wait, the prompt says: 'Work efficiently: if the values above already answer
     the question, answer immediately without any tool call.'
     But I should verify it because I can't trust mental math, and the prompt says
     'Confirm or override'. I'll just compute it to be sure. It's safer."

So the model reads the escape clause, weighs it, and **overrides it**. It is not
talked out of the tool by clause 3b.

### What is ruled out

* **the escape clause** — runs 1-4 call the tool with no clause, the escape
  clause, a neutral clause, and a mandatory clause alike; deleting 3b from the
  real prompt (run 11) changes nothing;
* **the answer being pre-supplied** — runs 6-9 call it anyway;
* **prompt size** — runs 8-9 call it at 17.8 KB, the same size as the harness;
* **the parser** — `extract_tool_request` handles fences, outer-`{...}` and the
  native `<tool_call>` syntax, and every tool call above parsed cleanly;
* **the task being easy** — run 5 shows it declining only when the arithmetic is
  trivial *and* the clause invites skipping.

### What is left

In the real prompt the model never mentions the tool **at all** — not to accept
it, not to decline it (runs 10-11, 17-22 K chars of reasoning, zero occurrences of
"tool" or "python"). The offer sits at 70 % through the message (char 11 975 of
16 994), inside the HARNESS MODE block, with ~5 KB of rules and discipline
clauses after it.

The remaining candidates, none yet tested: the **evidence pack supplies a complete
per-line analysis with explicit verdicts** (so the model's job reads as
transcription and pattern-labelling rather than computation), and the **discipline
clauses** focus it entirely on constructing the findings JSON. A prompt that
frames the work as verification — "for each line, reproduce the pack's verdict
from the CSVs with a tool call before you accept it" — is the untested direction
and the natural next probe.

### Answer to the question asked

**Yes — a simple prompt enables tool calls, reliably: 8 of 9 toy runs called the
tool, including every variant with the real clause 3b wording and at the real
prompt size.** The failure is specific to the full harness prompt, and it is not
caused by the clause, the size, the pre-supplied answer, or the parser. It is a
salience/framing effect of the harness prompt itself, and the model shows no sign
of even considering the tool there.

### Probe artefacts

`scripts/probe_tool_call.py` (variants x task types, `--pad`, `--prompt-md` to
replay a real harness prompt). Saved traces in `results/logs/toolprobe/`,
including `real_d72b95_asis.json` (failure reproduced) and
`real_d72b95_no3b.json` (failure persists without clause 3b).

## 19. Capability test — the FULL tool loop closes for Qwen3.6-27B

`scripts/probe_tool_roundtrip.py`. Section 18 only proved the model can *emit* a
tool request. This closes the whole cycle — request, sandboxed execution, result
fed back, final answer — and it does so by calling the runner's **own**
`run_harness_turns()`, so the code path, message format and sandbox are exactly
what the benchmark uses. Nothing is reimplemented and **nothing in the harness was
changed to make this happen**.

Result:

    task: population sd of 30 values   (true = 0.1424)
    TOOL CALLS MADE : 1
    TURNS           : [('model', True), ('tool', None), ('model', False)]
    --- tool call 1 ---
    code   : import statistics  values = [1.02, 0.97, ...]
    result : 0.1424
    FINAL ANSWER: {"answer": 0.1424}
    parsed answer = 0.1424   expected = 0.1424   match = True
    LOOP CLOSED (request -> execute -> result -> final answer): YES
    ANSWER CORRECT: YES

The turn log shows the exact production sequence: a model turn carrying a tool
request, a tool turn where the sandbox ran the code, then a final model turn with
no tool request. The sandbox executed the model's code and returned its stdout
verbatim, and the model used that value in its answer.

### What this does and does not establish

* **Establishes:** Qwen3.6-27B can call the tool and complete the full multi-turn
  loop under the benchmark's own machinery. There is nothing broken about the loop
  for this model.
* **Does not establish, and does not attempt:** that 3.6 will call the tool on the
  real books. It will not, and per the instruction for this test the harness was
  left alone — no clause forcing or nudging tool use was added, and 3.6 remains
  free to answer without tools, which is what it does on the real prompts.

Harness left byte-identical to the pass-2 configuration:
`stats_pack.py 78717ce2dbc74e06`, `run_zero_shot.py a4b967de975625f9`
(mtimes confirm neither file was touched by this work), `harness_preflight.sh`
PASS.

### Where the campaign stands

3.6's best configuration remains **pass 2: 42/44 = 95.5 %, FP/run 0.30**, gate
FREEZE — reached with no tool use at all. The tool loop is available and
functional but unused, and on the evidence of section 18 it is not worth further
prompt surgery to activate: it would change the harness away from the one 3.8 was
measured on, breaking the like-for-like comparison, for an unproven gain.

Artifacts: `scripts/probe_tool_roundtrip.py`,
`results/logs/toolprobe/roundtrip.json` (full turn log and transcript),
`results/logs/toolprobe/roundtrip.log`.

## 20. Pass 4 — the queued fix was REFUTED; a different one shipped

Section 15 proposed two pack changes for `sc-3c83fd`. Checked against the data,
**the first is harmful and was rejected**; the second is safe and is what pass 4
tests. Both verdicts are evidence-based, not judgement calls.

### Rejected: loosening the same-direction-run threshold

Section 15 suggested letting a 4-year run reach the sustained-move branch (the
classifier needs `run >= 6` while `sc-3c83fd`'s CI line has a 4-year decline).
Measured across all 23 optimization books, per line (92 lines, 15 with a truth
drift control):

| rule | catches truth-drift lines | newly headlines other lines |
|---|---|---|
| `run >= 6 & move >= 0.15` (current) | 4 / 15 | — |
| `run >= 5 & move >= 0.25` | 6 / 15 | 6 |
| `run >= 4 & move >= 0.25` | 8 / 15 | **12** |
| `run >= 4 & move >= 0.15` | 9 / 15 | **13** |

The `run` statistic barely separates drift from everything else — at the
threshold needed to catch `sc-3c83fd`, it fires on 12 other lines. Worse, of
those 12: **9 are clean lines**, and **3 carry a volatility control** —
`sc-6e2478` death, `sc-8a9fa1` death **and `sc-f520e5` death**, which is one of
the two books still failing *precisely because its Death volatility is read as
drift*. Handing that line a drift-flavoured headline would push it further wrong.
Rejected.

### Shipped: the cross-line note no longer over-claims

The `[CROSS-LINE]` note fires on 8 of 23 books. Three of those eight contain a
truth **drift** control, and two of them are exactly the books still failing:

| book | family | truth | note useful? |
|---|---|---|---|
| `sc-042304` | shock | CI shock | yes |
| `sc-4a7f9e` | systemic | Death+CI shock | yes |
| `sc-bba653` | systemic | 4-line shock | yes |
| `sc-314eca` | systemic | all-line volatility | yes (takes the coordinated branch) |
| `sc-9660b9` | noise_trap | all-line volatility | yes (takes the coordinated branch) |
| `sc-3c83fd` | drift | **CI drift** | **no — misleads** |
| `sc-63f1c7` | mixed | Death drift + CI shock | partly |
| `sc-d72b95` | systemic | shock + **Death drift + CI drift** | **no — misleads** |

The old wording asserted "the signature of a book-wide one-off event, **not a
multi-year erratic stretch**". That note exists for a real reason — the code
comment records that it removed 9 false alarms across the jolt books in the v1.6b
sweep, so it was **not deleted**. Only the over-claim was removed: the note now
says it rules out a multi-year *erratic* stretch (dispersion) and explicitly does
**not** rule out a sustained move, and points at each line's own longest-run row.

No statistic, threshold or verdict changed — this is a wording correction in the
same shape as the pass-2 fix that worked.

### Validated with zero API calls

| check | result |
|---|---|
| all 23 packs regenerate | 0 failures |
| books changed | **6 / 23** (the 6 that emit this note; the other 2 take the coordinated branch and are untouched) |
| changes beyond the intended sentence | **none** |
| CLEAN book `sc-14cdd9` | byte-identical |
| `harness_preflight.sh` | **PASS** |
| `--dry-run` rehearsal on `sc-3c83fd` | new sentence present, pinned prompt confirmed, no API call |

**Lineage:** `stats_pack.py 78717ce2dbc74e06` → **`feababaf9eb5ebaa`**;
`run_zero_shot.py` unchanged (`a4b967de975625f9`, the pass-2 bytes).

### Pass 4 command — optimization split only, all 23 books

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena

setsid nohup env MODEL=Qwen3.6-27B OUT=harness_q36_p4 PASS=4 RUNS=1 \
  WAIT_ENDPOINT=600 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  bash scripts/harness_pass_run.sh \
  >>results/logs/harness_q36_p4_console.log 2>&1 </dev/null &

disown 2>/dev/null || true
sleep 5
DRV="harness_pass"; DRV="${DRV}_run.sh"; pgrep -f "$DRV" >/dev/null && echo RUNNING || echo "NOT RUNNING"
```

23 optimization books, 1 run each, held-out untouched. ~2 h at the measured
298 s/book.

**Read it against the noise floor.** Passes 2 and 3 were the same experiment and
scored 42 and 40, so ±2 units (4.5 pts) is noise. Pass 4 counts as an improvement
only if it clears **44/44**, or if it fixes `sc-3c83fd` **and** `sc-d72b95`
without losing any book pass 2 had — anything less is indistinguishable from
run-to-run variation.

## 21. Pass 4 — COMPLETE, did NOT clear its bar; the harness has plateaued

Run 2026-09-18, `results/harness_q36_p4/`, 23 books, all valid, `failures: none`.
Snapshot self-contained: `stats_pack feababaf9eb5ebaa`,
`run_zero_shot a4b967de975625f9`, `system_prompt 54d6d5c2bc742919`.

| pass | strict | FP/run | harness state |
|---|---|---|---|
| p1 | 39/44 = 88.6 % | 0.43 | pack had the smoothed-window defect |
| **p2** | **42/44 = 95.5 %** | **0.30** | smoothed-window fixed — **best measured** |
| p3 | 40/44 = 90.9 % | 0.13 | + clause-3b text (never acted on) |
| p4 | 41/44 = 93.2 % | 0.35 | + cross-line wording correction |

Gate: FREEZE, all criteria met.

### The pre-registered bar was not met

Before running, the bar was: **44/44, or both target books fixed with nothing
lost**. Result: **neither target fixed**, 41/44.

* `sc-3c83fd`: still 0/1 — the model returned the *same* reading as pass 1,
  "CI | shock | decrease then increase | [2018, 2024]", confidence 0.9. The
  wording change did not alter its interpretation at all.
* `sc-d72b95`: still 3/4, unchanged from passes 1-2.
* `sc-f520e5`: still 1/2, Death volatility read as drift.
* tool calls: still `{0: 23}` — **zero across 92 runs in four passes.**

### The real finding: a plateau, not a trajectory

Passes 2, 3 and 4 are functionally the same harness (the tool never fires, and the
rules/pack wording differences change no measurable behaviour). They scored
**42, 40, 41 — mean 41.0, sd 1.0**.

So the honest picture is not "pass 2 was a peak". It is:

* **3.6's optimization performance with this harness is ~41/44 = 93 % ± 2 units**;
* the spread between passes 2-4 is run-to-run noise, not harness quality;
* the same three books (`sc-3c83fd`, `sc-d72b95`, `sc-f520e5`) are unstable across
  every pass, each flipping between readings, and no wording edit has moved them.

Against 3.8's frozen 43/44 = 97.7 %, 3.6 sits ~2-3 units back — **at or inside the
noise band**. Further optimization passes are not a good use of GPU time.

### Config decision

The tree keeps the pass-4 pack wording (`feababaf9eb5ebaa`). Unlike the pass-3
revert, this edit removed a **factually incorrect over-claim** from the evidence;
reverting it would restore text we know is misleading purely because of a 1-unit
noise difference, which is over-fitting to noise. The score difference between p2
and p4 is not evidence of anything.

If a single config must be named for the record, the best measured is still
**pass 2 (42/44)**; `results/harness_q36_p2/harness_snapshot/` preserves its bytes
exactly.

### Open methodological question for the held-out exam

3.8's held-out result (69.1 %) was produced by `harness_final` using the **frozen
v1.6e** pack (`stats_pack 16e53e0ef0b097ab`). The tree now holds a 3.6-tuned pack
(`feababaf9eb5ebaa`). Running 3.6's held-out with the current tree therefore
answers *"best 3.6 harness vs best 3.8 harness"*, **not** the like-for-like
*"same harness, different model"* question. Both are legitimate; they are not the
same experiment, and the choice should be made deliberately before the exam runs:

* **(a) frozen v1.6e for both** — clean like-for-like, directly answers "similar
  level of optimisation, different result". Already answered on optimization:
  3.6 + v1.6e = 88.6 % (pass 1) vs 3.8 + v1.6e = 97.7 % (p7).
* **(b) each model with its own tuned harness** — current tree for 3.6 vs
  `harness_final` for 3.8. Answers "best vs best".

Option (b) costs nothing extra; option (a) would need a second 72-call exam
(~6 h) if both answers are wanted.

## 22. The missing half of the protocol: 3.6 never had the per-scenario loop

Fair challenge, and the answer is **yes — 3.6 is missing the individual-case
optimisation stage entirely.** Measured from the 3.8 loop diary
(`results/logs/harness_opt_loop.md`) and the corpora:

| investment | 3.8 | 3.6 |
|---|---|---|
| full 23-book passes | 7 (p1-p7) | 4 (p1-p4) |
| per-scenario diary entries | **307** | **0** |
| distinct scenarios iterated individually | **32** | **0** |
| entries involving a harness review/edit | **268** | 0 |
| harness versions produced | **7** (v1.0, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6e) | 1 targeted fix (+1 reverted, +1 wording) |

3.8's harness was not built by seven sweeps. It was built by a **per-scenario
step loop** — `harness_opt_step.sh` runs exactly ONE scenario, stops, the harness
is reviewed and edited, and the same command is re-run — iterating through
v1.0 to v1.6e. A sample diary entry shows the pattern: `sc-042304` re-run under
"harness v1.1: calibrated pack + discipline clauses", scored 1/1, with a note on
what changed and why.

**So the 93 % vs 97.7 % comparison is not equal investment.** 3.6 inherited the
*finished* product of that loop and has had four sweeps against it, no per-case
work at all. That is exactly the asymmetry the standing rule was written to
prevent — "do not run on all scenarios, do run on the wrong one, see if it fixes
that one scenario" — and we drifted away from it because mirroring 3.8's *pass 2*
meant running full sweeps.

### Why it matters for the three stubborn books

`sc-3c83fd`, `sc-d72b95` and `sc-f520e5` are precisely the case the step loop
exists for. Each has now been through four sweeps and flipped between readings
without any edit aimed at it specifically. The sweep protocol cannot isolate them:
a 23-book run costs 2 h and moves three units of noise around them, whereas the
step loop spends one 5-minute call on one book and reads the diff immediately.

### Per-scenario step command (verified with --dry-run, no API call)

One book per invocation, corpus `harness_q36_step`, harness edited between
invocations:

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena
python3 scripts/run_zero_shot_baseline_v2.py --scenarios sc-3c83fd \
  --split optimization --detail full --termination-mean pooled \
  --base-url http://192.168.1.59:8080/v1 --model Qwen3.6-27B \
  --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 --timeout 3600 --runs 1 \
  --stream --wait-for-endpoint 600 --max-consecutive-failures 5 \
  --skip-existing --harness full --tool-calls 4 --out harness_q36_step
```

Swap `--scenarios` for the next book after each harness edit; `--skip-existing`
means re-running the same command only re-spends a book that is missing or failed.
Read the result with (EXPERIMENTER-SIDE ONLY — prints ground truth):

```bash
python3 scripts/harness_diff.py sc-3c83fd --out harness_q36_step
```

Note `harness_opt_step.sh` itself is hardcoded to `OUT="harness_opt_p${PASS}"` and
still targets the 3.8 corpora, so the direct runner command above is the right
tool for 3.6 rather than that script.

## 23. Per-scenario loop, first iteration — sc-3c83fd FIXED (0/3 → 3/3)

This is the first time the per-scenario protocol has been used on 3.6, and it
worked where four full sweeps did not.

### Step 1 — establish a baseline (3 runs, not 1)

The sweeps held one run per book, which cannot tell an edit from variance. Three
runs of `sc-3c83fd` at the pass-4 config (`results/harness_q36_step/`):

| run | pattern | years | strict |
|---|---|---|---|
| 1 | shock | 2018-2024 | ✗ |
| 2 | shock | 2020-2024 | ✗ |
| 3 | drift | 2020-2024 | ✗ (no window overlap) |

**0/3 strict, 1/3 loose, FP/run 1.00.** This corrects an earlier reading: the book
is not a coin flip that sometimes lands right — at this config it **consistently
fails**, and its lone sweep success (pass 2) was luck. Across four sweeps plus
this baseline it is 1/10.

### Step 2 — find a discriminator that does not damage anything else

Three candidate rules were measured on all 23 books before anything ran:

| rule | verdict |
|---|---|
| loosen the same-direction-run threshold to `run >= 4` | **rejected** — fires on 12 other lines, 9 clean and 3 volatility controls |
| cross-check the run against the excursion size | **rejected** — 69 of 92 lines, including the same volatility lines |
| **onset ratio in the pulse band `[0.85, 1.3)` plus a material run** | **accepted** — see below |

The third works because the pack's own onset ratio separates the families: every
volatility control in the split has `onset >= 1.4`, while the two drift lines that
need help sit at 1.16 and 1.12. The rule reaches 9 lines across 6 books — 2 with
drift controls, **0 with volatility controls**.

### Step 3 — the edit

`stats_pack.py`, the `onset` note's one-off branch only. The ratio there is
measured against the **excursion window**, which the detector may have picked far
narrower than the movement it belongs to — `sc-3c83fd`'s 2-year excursion sits
inside a 4-year decline, so a drift was described as "a one-off level change, not
a build-up". The note now adds, **only when the line also carries a material
same-direction run**:

> CAUTION — this line ALSO carries a 4-year down run totalling -0.367, which is a
> sustained move in its own right; the ratio above is measured against the
> excursion window, not against that run, so weigh both readings and name the
> years you decide on rather than defaulting to the one-off one

No threshold, statistic or verdict changed — it names a competing reading the
model was not being shown.

### Step 4 — result (3 runs, same book, same samplers)

| run | pattern | years | strict |
|---|---|---|---|
| 1 | drift | **2016-2019** | ✓ |
| 2 | drift | **2016-2019** | ✓ |
| 3 | drift | **2016-2019** | ✓ |

**3/3 strict = 100 %, 3/3 loose, FP/run 0.33.** All three runs returned the exact
truth window. Corpus: `results/harness_q36_step2/`.

### Validation before spending any call

| check | result |
|---|---|
| all 23 packs regenerate | 0 failures |
| books changed | **5 / 23** (`sc-3c83fd`, `sc-4a7f9e`, `sc-5e376b`, `sc-abbec4`, `sc-bba653`) |
| changes outside `onset:` lines | **none** |
| CLEAN book `sc-14cdd9` | byte-identical |
| `harness_preflight.sh` | **PASS** |

**Lineage:** `stats_pack.py feababaf9eb5ebaa` → **`58a44fd1661c52cf`**;
`run_zero_shot.py` unchanged (`a4b967de975625f9`).

### What this changes

The four sweeps were the wrong instrument. One book, an edit aimed at it, and
three runs to separate signal from variance settled in ~25 minutes what 8 hours of
sweeping could not. **The remaining wrong books should be worked the same way.**

### Outstanding before this can be trusted broadly

The edit touches 5 books, and only `sc-3c83fd` has been re-tested. The other four
(`sc-4a7f9e`, `sc-5e376b`, `sc-abbec4`, `sc-bba653`) currently pass, and the added
caution is a *qualification*, not a new claim — but that is reasoning, not
evidence. They must be re-run before the change is treated as safe, either
individually or in the next full sweep.

## 24. Per-scenario loop — full iteration log (3 books)

Protocol per book: **3-run baseline → diagnose → edit → validate offline across all
23 books → 3-run re-test.** All runs 1 book, canonical samplers, held-out untouched.

| book | baseline | edit tried | after edit | verdict |
|---|---|---|---|---|
| `sc-3c83fd` | 0/3 | onset-band caution | **3/3** | **FIXED** |
| `sc-d72b95` | 9/12 (3/4 per run) | GIVE-BACK scoping | 9/12 | no change — **unit is unidentifiable** |
| `sc-f520e5` | 4/6 | TAIL rebound guard | 3/6 | **worse — reverted** |

### sc-3c83fd — FIXED (kept)

The one clear win. The pack's `onset` ratio is measured against the **excursion
window**, which the detector picked 2 years wide inside a 4-year decline, so a
drift was described as "a one-off level change, not a build-up". The note now
names the competing reading when the line also carries a material same-direction
run. Band-guarded by the onset ratio itself, which is what keeps it off the
dispersion lines: **every volatility control in the split has `onset >= 1.4`**,
while the drift lines needing help sit at 1.16 and 1.12. 5 of 23 packs changed,
nothing outside `onset:` lines, CLEAN book byte-identical.

### sc-d72b95 — the missing unit is NOT IDENTIFIABLE (edit reverted)

Baseline 3/3 runs at 3/4: the model finds the 2020 shock on both lines and the CI
drift, and misses the **Death drift 2021-2024** every time.

Measured directly from the data:

| quantity | value |
|---|---|
| planted Death drift, fitted 2021-2024 | **+0.076 total** (+0.025/yr, R² 0.34) |
| truth's stated factor | 0.05 |
| the line's own year-to-year scatter (sd) | **0.189** |

**The planted drift is smaller than the line's own noise**, and it sits directly
after a ×1.4 shock that contaminates any post-shock baseline. The series is
0.971, 0.985, 1.097, 1.018 against a YoY sd of 0.19 — there is no honest reading
of that as a sustained move. Adding it would mean inventing a finding.

The GIVE-BACK edit (scoping the "one-off, not a slow build" verdict to the spike
only) changed nothing: 9/12 both before and after. Reverted — the edit is sound in
principle but the target is unreachable, and it also touched `sc-63f1c7`
untested. **Stop here: this unit belongs in the "ambiguous" column, not the
"model failed" column.**

### sc-f520e5 — flaky, and the edit made it worse (reverted)

Baseline 4/6: two runs read Death as **drift** (the FP), one read it correctly as
**volatility**. The signal is genuinely there — second-half YoY sd is **3.75×** the
first half with a flat mean (1.007) — the model just sometimes ignores it.

The TAIL block tells the model to "report it with THESE years" for a 2022-2024
rise, and that rise begins at an abnormally low 2022 (z −5.1): a rebound, not a
drift. TAIL is otherwise accurate (fires on 11 lines, 10 with a truth control), so
it was guarded rather than changed — only for tails beginning at z ≤ −4, which hits
exactly two lines (`sc-f520e5` z −5.1, `sc-2d248f` z −10.9) against every genuine
drift line sitting between z −2.1 and z +2.9.

**It made things worse: 3/6 vs 4/6.** The one baseline run that found volatility
stopped finding it. Reverted.

### Final harness state

`stats_pack.py` = **`58a44fd1661c52cf`** (the `sc-3c83fd` onset fix, and nothing
else), `run_zero_shot.py` = `a4b967de975625f9`. Verified after revert: hash exact,
**all 23 packs byte-identical** to the onset-fix-only state, `harness_preflight.sh`
PASS.

Net effect of the whole loop: **one book fixed, two edits tried and reverted, one
genuinely unreachable unit identified.**

### Still outstanding

The onset fix touches 5 books; only `sc-3c83fd` has been re-tested. `sc-4a7f9e`,
`sc-5e376b`, `sc-abbec4` and `sc-bba653` need re-running before the change can be
called safe — a full 23-book sweep does that in one go.

## 25. Regression check on the onset fix — it FAILS and is REVERTED

The onset fix (section 23) touched 5 books and only `sc-3c83fd` had been re-tested.
The other four were re-run, **3 runs each** (`results/harness_q36_regress/`), against
their pre-fix records:

| book | before (pass 4) | after onset fix | verdict |
|---|---|---|---|
| `sc-4a7f9e` | 2/2, fp 0 | **6/6, fp 0** | clean |
| `sc-5e376b` | 1/1, fp 0 | **3/3, fp 0** | clean |
| `sc-abbec4` | 2/2, fp 0 | **6/6, fp 0** | clean |
| `sc-bba653` | **4/4 in all four passes** | **6/12, 6 FPs** | **REGRESSED** |

`sc-bba653`'s runs: 2/4 (Death read as drift, IP dropped), then all-drift, then 4/4.
Two of three runs turned a planted **four-line shock** into drift readings — the
caution added to its Death/CI/TPD lines ("this line ALSO carries a N-year run")
is what invited it.

### Net accounting, like-for-like

| book | change |
|---|---|
| `sc-3c83fd` | **+3 units** (0/3 → 3/3) |
| `sc-bba653` | **−6 units** (12/12 → 6/12) |
| other three | 0 |
| **net** | **−3 units** |

**The fix fails its bar** — it does not fix a failing book without losing one that
worked; it trades one up for two down. **Reverted.**

Narrowing was considered and rejected: the obvious separator (`coordinated_swing`)
is unset on every cautioned line, so there is no principled way to keep the caution
on `sc-3c83fd`'s single-line drift while suppressing it on `sc-bba653`'s four-line
shock. A rule keyed on "3+ lines in the same book qualify" would work but is fitted
to a single book, which is overfitting, not engineering.

### Final frozen state

`stats_pack.py` = **`feababaf9eb5ebaa`**, `run_zero_shot.py` = `a4b967de975625f9`
— i.e. exactly the pass-4 harness. Verified after revert: hash exact, **all 23
packs byte-identical** to the verified pass-4 snapshot, `harness_preflight.sh` PASS.

## 26. Campaign conclusion for the three stubborn books

Every per-scenario edit attempted on the remaining wrong books has now been tested
and reverted. The honest end state:

| book | status | evidence |
|---|---|---|
| `sc-3c83fd` | **fixable but costly** | onset fix took it 0/3 → 3/3, but cost `sc-bba653` 6 units — net negative |
| `sc-d72b95` | **NOT IDENTIFIABLE** | planted Death drift +0.076 total vs the line's own YoY sd 0.189 — the signal is smaller than the noise |
| `sc-f520e5` | **flaky, edits counter-productive** | volatility is real (2nd-half YoY sd 3.75× the 1st) and 1 of 3 runs finds it unaided; the TAIL guard made it worse (3/6 vs 4/6) |

So the answer to "can the per-scenario loop fix 3.6's remaining books?" is: **it
fixed none of them net**. One is unidentifiable, one is noise-limited and already
partly solved, and the one genuine fix costs more than it earns.

That is a negative result, but a well-evidenced one, and it is the correct place to
stop editing: the harness is back at the configuration with the best measured
behaviour (pass 4, 41/44 = 93.2 %, FP/run 0.35, gate FREEZE), and no further pack
edit is supported by evidence.

**What would move the number now is not the harness.** 3.6 sits ~2-3 units behind
3.8 at or inside the ±2-unit noise band, with the tool loop unused in 100+ runs.
The remaining lever is the model, not the pack.

## 27. Onset fix REINSTATED with a coordination guard — verified net-positive

Section 25 reverted the onset fix because it cost `sc-bba653` 6 units. Round 2
found the principled discriminator that was missing.

### The discriminator

`sc-bba653` is the **only** cautioned book with a coordinated multi-year move:

| book | `coordinated_years` | `max_lines` | cautioned lines |
|---|---|---|---|
| **`sc-bba653`** | **[2015, 2016, 2017]** | **3** | death, ci, tpd |
| `sc-3c83fd` | `[]` | 1 | ci |
| `sc-4a7f9e` | `[]` | 2 | death, ci |
| `sc-5e376b` | `[]` | 1 | death |
| `sc-63f1c7` | `[]` | 2 | death |
| `sc-abbec4` | `[]` | 2 | tpd |

When several lines move together over multiple years, a single line's "long
same-direction run" **is the shared event**, not an independent sustained move —
so the per-line run caution is now suppressed for coordinated books. This is a
statement about what the statistic means, not a rule fitted to one book.

### Verified (6 calls, 3 runs each)

| book | before | with guard | note |
|---|---|---|---|
| `sc-3c83fd` | 0/3 | **3/3, fp 1** | **FIXED** — unchanged from the unguarded version |
| `sc-bba653` | 4/4 per pass | **11/12, fp 0** | regression gone (unguarded was 6/12) |

`sc-bba653`'s pack is now **byte-identical to the pass-4 state**, so its 11/12 is
run-to-run variance and *cannot* be an edit effect — the guard makes the
regression structurally impossible rather than merely unobserved.

Offline validation: 4 of 23 packs changed (`sc-3c83fd`, `sc-4a7f9e`,
`sc-5e376b`, `sc-abbec4`); `sc-bba653` byte-identical; CLEAN book byte-identical;
`harness_preflight.sh` PASS.

### The other three changed books are already cleared

The onset caution was present on `sc-4a7f9e`, `sc-5e376b` and `sc-abbec4` in the
section-25 regression run, where they scored **6/6, 3/3 and 6/6 with zero false
alarms**. The guard does not touch them (none is coordinated), so those results
stand.

### Why no full sweep is needed

Only **4 of 23** books have a pack that differs from the pass-4 state, and all four
have now been re-run 3× under the current code. The other 19 are byte-identical to
a state whose behaviour is known, so re-running them would measure nothing.

### Final harness state

`stats_pack.py` = **`8bd4c07be285bf51`** (onset caution + coordination guard),
`run_zero_shot.py` = `a4b967de975625f9`.

Net effect on the optimization split: **`sc-3c83fd` 0/3 → 3/3, no book harmed** —
the first per-scenario edit to survive its regression check.

## 28. Identifiability audit of the two remaining targets — both are bad units, not harness defects

Round 3 put the "can this unit even be found?" question on a statistical footing
instead of an impression. Both target books fail it, for different reasons.

### `sc-d72b95` — the missing unit is BELOW THE DETECTION FLOOR

The Death line's post-shock drift (truth: 2021-2024, factor 0.05), fitted on the
four years the control covers:

| quantity | value |
|---|---|
| fitted slope | **+0.0253 /yr** |
| slope standard error | 0.0251 |
| **t statistic** | **1.01** (need \|t\| > 3.18, 2 dof, p<0.05) |
| 95 % CI | **[−0.083, +0.133]** — contains 0 *and* the truth value 0.05 |
| **minimum detectable slope at 80 % power** | **+0.088 /yr** |

The planted effect is roughly **half the size needed to be detectable** with four
annual observations. This is not "hard to see" — the Poisson noise is small
(expected counts 576-826 give sd(A/E) ≈ 0.04) and the *only* obstacle is having
four data points. No honest statistic can separate it from noise.

**Consequence:** the model finds 3 of the book's 4 controls and all three are the
identifiable ones (the ×1.4 and ×1.2 shocks at z +7.0 / +5.6, and the CI drift). On
identifiable units this book is **3/3, i.e. the model is at ceiling.** Its "3/4"
is an artefact of a control that the data cannot support.

### `sc-f520e5` — the unit is DETECTABLE but genuinely AMBIGUOUS

The Death volatility is statistically real:

| quantity | value |
|---|---|
| YoY sd inside 2019-2022 | 0.381 |
| YoY sd outside | 0.092 |
| **variance ratio F** | **17.1** (critical F(3,5) = 5.41 at p=0.05) → **detectable** |

But the same line also carries a real **level excursion**: 0.95 → 1.34 (2018→2021)
then down to 0.80 (2022), with the 2019-2022 mean at 1.102 against 0.943 outside.
So the line genuinely shows **both** dispersion *and* a level move, and the truth
labels it volatility only. The model's "drift" reading is **defensible from the
data** — it is not a hallucination, it is the other legitimate reading of an
ambiguous book.

That reframes the earlier failures: two edits aimed at suppressing the drift
reading were trying to make the model ignore a real feature of the data, which is
why both made things worse (TAIL guard: 3/6 vs 4/6) rather than better.

### What this means for the objective

Neither target is a fixable harness defect:

* `sc-d72b95` — **no honest fix exists**; the signal is below the detection floor.
* `sc-f520e5` — **no correct fix exists**; the data supports both labels, the model
  picks the other one in 2 of 3 runs, and edits that push it the "right" way make
  the score worse.

The two books should be recorded as **bad units** (one undetectable, one ambiguous)
rather than as model failures. On the units the data can actually support, 3.6's
optimization performance is better than the headline 41/44 suggests.

### Harness unchanged this round

`stats_pack.py` = `8bd4c07be285bf51` (onset caution + coordination guard, verified
net-positive in section 27), `run_zero_shot.py` = `a4b967de975625f9`. No edit was
made in round 3 — the audit produced evidence, not a change, and inventing an edit
to chase an undetectable unit would be fabrication.

## 29. What 3.8's harness process did, versus what 3.6 got

Read from the records, not from memory: `results/logs/harness_opt_loop.md` (3.8's
diary), the `harness_opt_p*` corpora and their snapshots.

### The two processes side by side

| | Qwen3.8-27B | Qwen3.6-27B |
|---|---|---|
| harness versions produced | **7** (v1.0, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6e) | inherited v1.6e; **2 edits kept** on top |
| full 23-book passes | 7 (p1-p7) | 4 (p1-p4) |
| per-scenario diary entries | **307** (4 750-line diary, 32 distinct books) | 0 until round 1 of the loop; ~24 runs since |
| passes where **both** harness files changed | p3→p4→p5→p6→p7, **5 in a row** | 0 (edits were between passes, not per pass) |
| `stats_pack.py` growth | 27 229 → 38 490 bytes, **+41 %** (p3→p7 alone) | inherited the 38 490-byte end state |

### Score trajectories

| | p1 | p2 | p3 | p4 | p5 | p6 | p7 |
|---|---|---|---|---|---|---|---|
| **3.8** | 61.4 % | 72.7 % | 75.0 % | 81.8 % | *(1 book)* | 88.6 % | **97.7 %** |
| **3.6** | 88.6 % | 95.5 % | 90.9 % | 93.2 % | — | — | — |

**3.6's first pass with 3.8's finished harness scores exactly what 3.8's sixth
pass scored: 88.6 %.** 3.8 needed seven versions and five consecutive
file-changing passes to get there; 3.6 started there.

### The difference that matters: the harness is tuned against 3.8's over-reporting

3.8's false alarms were high at **every** stage and the harness was built to
suppress them:

| | FP/run across passes |
|---|---|
| 3.8 | 0.52 → 0.78 → 0.52 → 0.91 → **1.26** → 0.96 |
| 3.6 | 0.43 → **0.30** → 0.13 → 0.35 |

3.6's FP/run is **3-7× lower at every pass**, including its first. It never had
the problem the harness spent six versions fixing.

And the harness's development record says so explicitly. In `stats_pack.py` today:

* the rules block carries 5 × "do not", 4 × "never", plus "not a finding",
  "only when", "unless", "false alarm" — across only ~19 sentences;
* version-tagged suppression blocks survive in the code: **GIVE-BACK (v1.6b)**,
  **TAIL (v1.5)**, and a v1.6c cross-line note whose own comment reads
  *"reading there cost 9 false alarms on the jolt books in the v1.6b sweep"*, while
  another records *"removed a false lead that cost 9 false alarms … (sc-4a7f9e
  alone: 5 dispersion entries it did not need)"*.

So the instrument 3.6 inherited is a **precision device built to stop a chattier
model from over-reporting**. 3.6 is not that model. It inherits every suppression
without needing any of them — plausibly paying for them in recall, which is exactly
where it trails.

### Two honest caveats

1. **This is circumstantial, not tested.** The FP asymmetry is strong evidence that
   the harness is mismatched to 3.6, but I have not run the experiment that would
   prove the suppressions cost it recall (relaxing them and measuring). It is a
   hypothesis with good support, not a result.
2. **Most of 3.8's 307 diary entries predate the p3 snapshot**, so the v1.0-v1.2
   work is not byte-recoverable — only its effects are. The counts above are what
   the surviving records establish.

### What it means for the 93 % vs 97.7 % comparison

It is **not an equal-investment comparison**, and it is not a clean
same-instrument comparison either. 3.8's number is the output of a harness grown
against 3.8's failure modes over seven versions; 3.6's is what that finished
instrument yields on a differently-behaved model, plus two targeted repairs. The
honest framing is *"3.8 with its own tuned harness"* vs *"3.6 with 3.8's harness"*
— which is the asymmetry the original question was probing.

## 30. Pre-held-out checklist — two confounds found, exam not yet runnable for 3.6

### A. The harness choice for the exam is NOT cosmetic

Comparing the current tree against the **frozen v1.6e** (`harness_opt_p7`s
snapshot) on the 24 held-out books:

| | held-out books |
|---|---|
| pack differs at all | **24 / 24** |
| pack differs **substantively** (beyond the MA-label line) | **14 / 24** |
| cosmetic only | 10 / 24 |

So 3.6's held-out result depends heavily on which harness runs it:

* **frozen v1.6e** → directly comparable to 3.8's 69.1 %, which was produced by
  exactly those bytes via `harness_final`;
* **current tree** → "best 3.6", but 14 of 24 books present different evidence
  from the ones 3.8 was scored on, so the two numbers are not like-for-like.

### B. The exam script cannot run 3.6 as-is

`scripts/harness_final_heldout.sh` line 74 calls `python3 scripts/run_zero_shot.py`
**directly** — it has `OUT`/`RUNS`/`MODEL`/`BASE_URL` but **no `RUNNER` override and
no pinned-prompt support**. Launching it for 3.6 today would silently change the
system prompt:

| run | system prompt |
|---|---|
| 3.8 p7 (optimization, harness) | **3866 chars** |
| 3.8 held-out (harness) | **3866 chars** |
| 3.8 zero-shot baseline | 3053 |
| 3.6 p4 (optimization, harness) | **3053 chars** *(pinned via the wrapper)* |
| 3.6 zero-shot baseline | 3053 |

All four of 3.6's optimization passes ran the 3053-char baseline prompt through
`run_zero_shot_baseline_v2.py`. The exam script would run the 3866-char
harness-era one — different prompt, incomparable to 3.6's own optimisation record.

**Fix needed before launch:** give `harness_final_heldout.sh` the same `RUNNER`
override (and prompt snapshot) that `harness_pass_run.sh` already has. Small and
mechanical, but it must be done and dry-run verified first.

### C. A confound in the headline comparison, found while checking B

The two campaigns' **harness** runs used **different system prompts**: 3.8's used
the 3866-char harness-era prompt, 3.6's the 3053-char baseline. So the
`93 % vs 97.7 %` optimisation comparison differs in *two* ways — harness
investment (7 versions + 268 edits vs 2 kept edits) and system prompt (3866 vs
3053 chars) — not one. This was not previously flagged and it weakens the
same-instrument reading of that comparison.

### Recommendation

Skip the extra optimization pass (nothing left to fix; the number is already
characterised at ~42/44 with a ±2 noise floor; and every extra pass widens the
optimism gap that took 3.8 from 97.7 % to 69.1 %). Fix the exam script, decide the
harness (v1.6e for a clean comparison vs 3.8, or the tuned tree for "best 3.6"),
then run the exam **once** — the held-out split is a one-shot resource.

## 31. Would a prompt change help 3.6? Tested — NO. Recommendation withdrawn.

Section 30 proposed evolving 3.6's prompt, on the grounds that it lacks the
direction-symmetric clause ("rising **OR falling**") that 3.8's harness prompt
carries at line 17, and that `sc-3c83fd`'s four-year *decline* was mislabelled.
That attribution was plausible but untested. Tested now, and it does not hold.

### The test

Every unit the model matched loosely across all four passes (162 units), with the
model's reported `direction` compared against the truth manifest's direction:

```
loose-matched units examined: 162   direction contradictions: 0 (0.0%)
```

**The model never once reports the wrong direction on a unit it matches.** The
direction-symmetry clause addresses a failure mode that does not occur.

`sc-3c83fd` was also mischaracterised in section 30. The model reported
*"shock, decrease then increase"* — it **saw the fall**. Its error was the pattern
**label** (shock instead of drift), not the direction. A clause telling it that
drift can fall would not have changed that answer.

### Where the gap actually is

| split | 3.6 | 3.8 | gap |
|---|---|---|---|
| optimization (after the `sc-3c83fd` fix) | ~42/44 = 95.5 % | 43/44 = 97.7 % | **1 unit** |
| held-out | **not measured** | 85/123 = 69.1 % | unknown |

And the 2 units 3.6 misses on optimization are the two proven bad units —
`sc-d72b95` (control below the detection floor, t = 1.01) and `sc-f520e5`
(ambiguous: both labels defensible). On the units the data can support, **3.6 is at
ceiling on the optimization split.**

So there is no identified systematic weakness left in 3.6's optimization
behaviour for a prompt edit to address. The only real unknown is the held-out
split, and a prompt edit cannot be justified as a fix for an unmeasured gap.

### Decision

**Do not run the prompt pass.** The lever is real — the prompt has never been
touched and the mechanism works — but the specific edit available has no evidence
behind it, prompt changes touch every book at once (the highest-variance lever in
the harness), and the optimization split has no room left to show a gain. Running
it would be an unforced overfitting pass on the eve of the held-out exam.

Corrected recommendation: freeze the harness and go to the held-out exam, having
first fixed the exam script's missing `RUNNER` override (section 30B) so 3.6's
held-out runs the same 3053-char prompt its optimization passes did.

## 32. Held-out exams — both configured, Exam A running

Two exams requested: 3.6 on its own tuned harness, then 3.6 on **3.8's exact**
harness. They are different questions and the snapshots now make them
distinguishable.

### Exam script patch (required, done)

`scripts/harness_final_heldout.sh` hardcoded `python3 scripts/run_zero_shot.py`
and both output paths. Patched, all defaults preserved so 3.8's historical config
is unchanged:

* **`RUNNER` override added** — default `${RUNNER:-python3 scripts/run_zero_shot.py}`,
  which is exactly what 3.8's exam ran. Point it at
  `run_zero_shot_baseline_v2.py` to pin a prompt file instead.
* **prompt snapshot added** — when `PINNED_PROMPT_FILE` is set the file is copied
  into `harness_snapshot/system_prompt.txt`, and the MANIFEST now also records
  `runner=…`. Without this, "same harness" is ambiguous: the same two code files
  can still deliver two different system prompts.
* **`LOGF` / `STATUS` made overridable** so the two 3.6 exams do not clobber each
  other or 3.8's record. 3.8's original status preserved to
  `results/logs/harness_38_final_status.txt`.

Verified: `bash -n` clean, `--dry-run` builds the held-out prompt with the pinned
3.6 system prompt, default path byte-for-byte unchanged.

### Exam A — 3.6 on ITS OWN tuned harness (RUNNING)

```bash
env MODEL=Qwen3.6-27B OUT=harness_q36_final RUNS=3 WAIT_ENDPOINT=600 \
  RUNNER="python3 scripts/run_zero_shot_baseline_v2.py" \
  PINNED_PROMPT_FILE=data/prompts/system_v2_baseline.txt \
  LOGF=results/logs/harness_q36_final.log \
  STATUS=results/logs/harness_q36_final_status.txt \
  bash scripts/harness_final_heldout.sh
```

Launched 2026-09-18T14:15Z. Snapshot confirms:
`stats_pack 8bd4c07be285bf51` (v1.6e + smoothed-window fix + cross-line wording +
onset caution/guard), `run_zero_shot a4b967de975625f9`,
`runner=run_zero_shot_baseline_v2.py`,
`system_prompt 54d6d5c2bc742919` (3053 chars — the same prompt all four of 3.6's
optimization passes used). **24 books × 3 runs = 72 calls, ~6 h.**

### Exam B — 3.6 on 3.8's EXACT harness (after A finishes)

Identical to 3.8's `harness_final` run: v1.6e bytes, `run_zero_shot.py` run
directly so it uses its own 3866-char harness-era system prompt — no wrapper, no
pinned file.

```bash
cd /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena
cp results/harness_opt_p7/harness_snapshot/stats_pack.py scripts/stats_pack.py
sha256sum scripts/stats_pack.py | cut -c1-16    # must read 16e53e0ef0b097ab

env MODEL=Qwen3.6-27B OUT=harness_q36_final_v16e RUNS=3 WAIT_ENDPOINT=600 \
  LOGF=results/logs/harness_q36_final_v16e.log \
  STATUS=results/logs/harness_q36_final_v16e_status.txt \
  bash scripts/harness_final_heldout.sh
```

`scripts/run_zero_shot.py` is already `a4b967de975625f9` (unchanged since the
clause-3b revert), so with `stats_pack.py` restored the tree *is* v1.6e. **Run
Exam B only after A has fully finished** — one generation at a time (the server
has a single slot) and the two must not interleave.
Restore the tuned pack afterwards: `cp results/harness_q36_final/harness_snapshot/stats_pack.py scripts/stats_pack.py`.

### Reading the results

```bash
python3 scripts/score_xam.py results/harness_q36_final/zero_shot \
  --json-out results/harness_q36_final/scores.json
python3 scripts/harness_gate.py results/harness_q36_final/zero_shot \
  --split heldout --runs 3 --reference results/xam_q36/zero_shot \
  --label "3.6 held-out, own harness" --json-out results/logs/harness_q36_final_gate.json
```

The comparison table to build when both are in:

| exam | harness | prompt | reference |
|---|---|---|---|
| 3.8 `harness_final` | v1.6e | 3866 (native) | **85/123 = 69.1 %, FP 0.96** |
| 3.6 Exam A | v1.6e + 3.6 edits | 3053 (pinned) | "best 3.6" |
| 3.6 Exam B | v1.6e | 3866 (native) | **same harness AND prompt as 3.8 — the only fully controlled cross-model comparison** |

Exam B is the one that answers the original question ("similar level of
optimisation → different result?") without any confound. Exam A answers what 3.6
can do with its own tuned harness.

## 33. The 3.8-on-3.6-harness run is confounded, and my explanation of it was wrong

### What the run actually varies

`results/harness_q38_tuned/` was launched with `RUNNER=run_zero_shot_baseline_v2.py`
+ `PINNED_PROMPT_FILE=system_v2_baseline.txt`, so it differs from 3.8's reference
(`harness_final`) in **two** ways, not one:

| | 3.8 reference (`harness_final`) | 3.8 "tuned" |
|---|---|---|
| system prompt | **3866 chars** (`25a2d2ebed2d489e`) | **3053 chars** (`54d6d5c2bc742919`) |
| evidence pack | v1.6e | 3.6-tuned (`8bd4c07be285bf51`) |

Verified from the requests actually sent (`request.initial_messages`), not inferred.
Per the project's definition the prompt **is** part of the harness, so this run
legitimately answers *"3.8 on 3.6's complete harness setup"* — but it **cannot**
attribute any change to the pack edits alone. The two are varied together.

### Why that matters: the differing clause is the one that governs the observed change

The prompt difference is not cosmetic. 3.8's own prompt (3866) carries a developed
taxonomy clause:

> If the excursion moves year over year in ONE direction before it peaks or
> reverts — **rising OR falling** — prefer drift — **UNLESS** the computed
> evidence says the biggest single-year move EXCEEDS the net excursion of that
> window … then the pattern is volatility, not drift.

The 3053 baseline prompt **does not contain that section at all**. And the behaviour
that changed on `sc-3627d2` was exactly IP going **shock → drift**.

### The development record says why that clause exists

From `results/logs/harness_opt_loop.md`:

* `sc-5e376b (Death shock 2020-22) | called it "drift" over the right window |`
  `pack text invited "2-3 year sustained move" for a flat-topped 3-year pulse`
  → **an actual shock misclassified as drift**;
* `sc-3c83fd: the model reported a single 8-year "shock" for a drift`
  → the reverse error.

So the 3866 wording is the product of iterating on this confusion **from both
directions**. The practical consequence: running 3.8 on the 3053 prompt replaced
its developed taxonomy guidance with the cruder baseline. The +4 on `sc-3627d2`
may therefore be the cruder prompt calling more things "drift" — right on a drift
book, and expected to be **wrong on shocks**.

### Corrected earlier claims

1. Section 32/section 33 discussion attributed 3.8's gain to the pack edits
   (onset caution + smoothed-window fix). **Not supported** — the prompt varied too.
2. I told the user the onset caution flipped `sc-3627d2`'s IP line. The caution was
   added to a line with a **5-year** run while IP's longest run is **4 years**, so it
   likely was not on IP at all. Withdrawn.

### Bug in my own family-count script (and the corrected table)

`data/truth/manifests/<sid>.json` stores the **descriptive** id in
`scenario_id` (e.g. `shock_death_2016`), while the opaque `sc-696b93` is the
**filename**. A script keyed on `m['scenario_id']` matches nothing and silently
reports every family as "still to run = total". The per-family table produced that
way was wrong; the scores file was right — `sc-696b93` is **shock**, held-out,
Death shock [2016,2016]. **Key truth manifests by filename, not by `scenario_id`.**

Corrected held-out composition (24 books), with the 9 completed:

| family | total | completed | remaining |
|---|---|---|---|
| systemic | 8 | 4 | 4 |
| shock | 3 | 1 | 2 |
| drift | 3 | 0 | 3 |
| recovery | 3 | 1 | 2 |
| volatility | 2 | 1 | 1 |
| mixed | 2 | 0 | 2 |
| noise_trap | 2 | 1 | 1 |
| CLEAN | 1 | 1 | 0 |

### Registered prediction (stated before the data arrives)

If the 3866 clause was built to stop shocks being read as drift, then stripping it
should **cost** on shock-family books. One shock book is complete (both harnesses
3/3 — no difference); **2 shock books remain**. Prediction: the 3053-prompt run
loses ground on the shock family, and the current +3 net (one drift-side gain of
+4, one noise_trap loss of −1) shrinks or reverses. If it does not, the clause is
not earning its keep and that is worth knowing too.

## 34. REPORTING STANDARD CHANGE — accuracy + FP per CLAIM (was FP/run)

Decided by the user, and the reasoning is a real gaming risk: **a model can flood
claims to inflate recall.** Claim everything plausible and recall approaches 100 %
while most of what was said is wrong. `FP/run` shows the absolute noise but not
that the noise now dominates the output.

**From now on every result table reports, on the common basis of the findings
ledger:**

| metric | formula | denominator |
|---|---|---|
| **accuracy (recall)** | strict hits / units | units = controls × runs |
| **FP/claim** | false positives / claims emitted | claims = hits + FPs |
| precision | hits / claims | = 1 − FP/claim |

`FP/run` and `FP/unit` may still appear as secondary diagnostics, never as the
headline. Note accuracy and FP/claim still have *different* denominators
(opportunities vs claims) — they do not sum, and that is fine: they answer "did it
find what was there?" and "is it trustworthy when it speaks?".

### What the change immediately exposed — the optimization split was misread

| corpus | accuracy | FP/claim | precision | claims |
|---|---|---|---|---|
| 3.8 opt p7 (own harness) | **97.7 %** | 33.8 % | 66.2 % | 65 |
| 3.6 opt p4 (tuned harness) | 93.2 % | **16.3 %** | **83.7 %** | 49 |

Under recall alone 3.8 wins by 4.5 points. Under FP/claim **3.6 is more than twice
as reliable per claim** — 83.7 % vs 66.2 % precision.

In raw counts: **3.8 makes 22 false alarms to 3.6's 8 — nearly 3× — to gain 2 extra
hits.** Every earlier statement in this log that 3.8 is "the better scorer" was
resting on the recall column alone and is **not supported** under this standard.
The honest summary is that 3.8 trades precision for recall, and how that nets out
depends entirely on what a false alarm costs downstream — which is the user's call,
not the benchmark's.

This is the same trade the held-out split shows (3.8 69.1 %/44.8 % vs 3.6-tuned
64.2 %/38.8 %), so it is consistent across both splits rather than a split artefact.

## 35. sc-e6ffa4 infinite loop — malformed TOOL REQUEST, not a slow model

`sc-e6ffa4` (`sys_vol_macro_2020_2024`, all four lines volatile) failed to complete
under 3.8-on-the-3.6-harness at least five times, one attempt running 2 h 25 min.
It completes **9/9 under the three other configurations**. Diagnosed from the saved
record:

```
content = {"tool": "python", "code": "import csv\nfrom collections import defaultdict\n..."}
parse error: Invalid \escape: line 1 column 2108 (char 2107)
```

**The record is a TOOL REQUEST, not a final answer**, and its embedded Python
contains an invalid JSON escape. The loop:

1. the hardest book makes 3.8 decide to compute, so it emits `{"tool": "python", ...}`;
2. the code string carries a stray backslash → not valid JSON;
3. `extract_tool_request` cannot parse it → **the tool is never executed**
   (`tool_calls=0` on the record confirms it);
4. `answer_parses_as_json` also fails → run marked `TruncatedStream`, retried;
5. same slip next attempt → **unbounded loop**.

`TruncatedStream` is again a misleading label: nothing was truncated.
`strict=False` does **not** fix this one (tested) — it covers raw control
characters, not invalid escapes.

### Why it never showed up before

| corpus | tool-using runs | `sc-e6ffa4` |
|---|---|---|
| 3.8 zero-shot | — (no harness → **no tool offered**) | n/a |
| 3.8 own harness (v1.6e + 3866) | 17/72 = 23.6 % | 3/3 runs, **0 tool calls**, all OK |
| 3.8 + 3.6 harness (tuned + 3053) | 10/64 = 15.6 % | **1 malformed tool request → loop** |
| 3.6 Exam A + B | **0/144** — never uses tools | all OK |

Both system prompts are silent about the tool (verified — both say only "Respond
with ONLY a JSON object"); the tool offer lives in the shared user-turn rules. So
there is **no mechanism by which 3.8's own harness suppresses tool use** — and it
in fact uses tools *more* than the 3.6 harness (23.6 % vs 15.6 %). At a ~24 % base
rate, three runs with no tool call has probability ≈ 0.45 — unremarkable.

**The lesson is the amplification, not the cause.** A malformed tool request is not
skipped as an error; it makes the run unparseable, which retries, which reproduces
it. A ~2 % event becomes an unbounded loop that blocks the book and every book
behind it in the alphabetical sweep.

### Fixes (not yet applied)

1. **Lenient escape repair** in `extract_tool_request` / the answer validator:
   on `Invalid \escape`, retry after `re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', blob)`.
   Recovers the run instead of abandoning it.
2. **Bound the retries** — fail a run after one attempt on a parse error rather
   than looping. Lower value, but it caps the damage from any future variant.

### Cross-corpus failure audit (held-out, all completed exams)

| corpus | failed records |
|---|---|
| 3.8 own harness (`harness_final`) | 0 / 72 |
| 3.6 Exam B | 0 / 72 |
| 3.6 Exam A | 0 / 72 |
| 3.8 + 3.6 harness (in flight) | 1 (`sc-e6ffa4`) |

## 36. DECISION — do NOT patch the malformed-tool-request failure

User decision, and the reasoning is recorded deliberately: **the fix is not applied.**
A defect that exists only as a documented failure is auditable evidence; one that has
been patched away becomes a silent gap that no one can later inspect. The failure is
therefore preserved as-is in `results/harness_q38_tuned/`.

Consequences accepted:

* `sc-e6ffa4` stays incomplete under the 3.8-on-3.6-harness configuration, so that
  cell tops out at **23/24 books** unless the error is fixed later.
* The two books it blocked (`sc-f19bae`, `sc-f916b9`) are run directly, bypassing
  the alphabetical sweep, so the corpus completes as far as it can.
* **No change to `run_zero_shot.py`.** The escape-repair described in section 35 is
  left unapplied and explicitly declined.

Note for the record, so the two parser changes are not confused:

| change | status |
|---|---|
| `json.loads(..., strict=False)` for raw control characters | **applied** (earlier, with approval) — fixed `sc-696b93` |
| lenient escape-repair for `Invalid \escape` in tool requests | **declined** (this decision) — `sc-e6ffa4` stays broken |

`run_zero_shot.py` is at `98411194093cdd0c` and will not be modified for this.

Any future session must not "helpfully" apply the repair without revisiting this
decision first.

## 37. sc-e6ffa4 recorded as a FAILURE of this cell — and the corrected root cause

**Decision: the book is recorded as a failure, not a gap to be filled.** No usable run
was ever produced for `sc-e6ffa4` under 3.8-on-the-3.6-harness, across 6+ attempts
including one of 2 h 25 min. The cell is final at **23/24 books, 69/72 runs, 111 units**.

### CORRECTION to section 35's root cause

Section 35 implied the missing prompt text was the cause. **That is wrong**, and the
control was already in the data:

| model | pack | prompt | multi-line-vol guidance? | `sc-e6ffa4` |
|---|---|---|---|---|
| 3.8 | v1.6e | 3866 | yes | 3/3 OK (~32 min) |
| **3.8** | **tuned** | **3053** | **no** | **0/3 — malformed tool request** |
| 3.6 | v1.6e | 3866 | yes | 3/3 OK (~8.5 min) |
| **3.6** | **tuned** | **3053** | **no** | **3/3 OK (~6.7 min)** |

Rows 2 and 4 have the **identical harness** and differ only in the model. 3.6 passes
where 3.8 loops, so the prompt gap is **not sufficient** — it is a contributing
condition, not the root cause.

What the prompt gap explains is the **routing**: the 3866 prompt carries ~800 chars
of volatility guidance the 3053 prompt lacks, including a 546-char block that
describes this book exactly ("several lines swinging together across CONSECUTIVE
years … report it for EVERY affected line"). `sc-e6ffa4` is `sys_vol_macro_2020_2024`
— all four lines volatile. Under-instructed, 3.8 falls back to computing.

The failure needs **three conditions together**, and only this configuration has all
three: (1) the prompt gap, (2) a model that uses tools — 3.8 ~24 % of runs, **3.6 0
of 144**, and (3) a malformed tool request. 3.6 has (1) but never (2); 3.8+3866 has
(2) but not (1).

### Impact on the reported numbers

| | |
|---|---|
| as reported, 23 books | **78/111 = 70.3 % accuracy**, FP/claim 43.1 %, precision 56.9 % |
| `sc-e6ffa4` would add | **12 units** (4 benefit lines × 3 runs) |
| reference: 3.8 under its OWN harness | **6/12** on this book, with 12 FPs |

Sensitivity if it had completed:

| score | accuracy | vs reported |
|---|---|---|
| 0/12 | 78/123 = 63.4 % | **−6.9 pts** |
| 4/12 | 82/123 = 66.7 % | −3.6 |
| **6/12** (own-harness rate) | **84/123 = 68.3 %** | **−2.0** |
| 12/12 | 90/123 = 73.2 % | +2.9 |

**So the reported 70.3 % is most likely ~2 points optimistic**, and FP/claim ~3 points
better than truth (59 → ~71 FPs would give 45.8 %). Every conclusion in section 34
has margins far larger than this — the model ranking, the precision gap, and 3.8's
unaided over-claiming all survive a 2-point shift.

### Standing instruction

`sc-e6ffa4` must be reported as **failed**, never as absent or excluded. `run_zero_shot.py`
remains **unpatched** by user decision (section 36) — do not apply the escape-repair
without revisiting that.
