# Harness growth — a plain-language record of what we built, why, and what happened

*Living document. Every version below was forced by a measured failure and
checked against ground truth on the **optimization split only**; the held-out
split stays untouched until the final test. Last updated: 2026-09-11 (pass 3
running — the final permitted pass).*

---

# PART 0 — If you know nothing about AI, read this first

**The job we gave the AI.** An insurance company's claims come in above or below
what the actuary expected. The ratio *actual ÷ expected* is called **A/E**: 1.00
means "exactly as expected", 1.20 means "20 % more claims than expected". The AI
receives ten years of these ratios for four insurance lines (life/Death,
critical illness/CI, disability/TPD, income protection/IP) and must answer: *is
something unusual going on, and if so, where, what kind, how big, how sure am I,
and what would you do about it?*

**Why it's hard.** Ten years of four lines is ~40 numbers per book, each wobbling
with random noise. Human actuaries use statistics. The AI reads the numbers and
reasons in its head — and that's where it goes wrong: it mistakes noise for
signal, or labels a slow multi-year trend as a sudden jolt.

**What "the harness" means.** Think of the AI as a very well-read analyst who
cannot use a calculator and cannot open a spreadsheet, working only from what
you paste into the chat. A **harness** is everything we build *around* that
analyst: the briefing we give them, the calculator we hand them, the rulebook
about when to speak up, and the filing system that records what they said. The
AI model itself is never retrained or modified in this campaign — only the
harness around it grows.

**How we know whether it worked.** For every test book, we know what was
actually planted in the data (it was generated that way). That hidden answer
sheet is called the **ground truth**. We never show it to the AI. We only use it
afterwards to mark the AI's answer, exactly like an exam.

**The one number that matters most.** *Recall* — of the real planted problems,
how many did the AI find and describe correctly? The second number is
*false alarms* — how many things did it report that were not planted?

---

# PART 1 — The starting point: two finished experiments

Two complete experiments existed before this campaign, each with 141 AI answers
(47 books × 3 repeats):

| experiment | AI model | what it was told | correct | false alarms per answer |
|---|---|---|---|---|
| `xam_v4` | Qwen3.8-Flash-Next | original briefing | 63.1 % | 1.05 |
| `xam_v5` | Qwen3.8-27B | briefing revised once | 65.5 % | 1.93 |

Marking those 282 answers taught us **exactly where the AI's weaknesses were** —
and that is what the harness had to attack:

```
 WHAT THE AI DID WELL                         WHAT IT GOT WRONG
 ─────────────────────────────────────        ──────────────────────────────────────
 · sudden jolts ("shock")      92 %           · slow multi-year trends that stop
 · year-to-year unsteadiness                  before the last year of data:
   ("volatility")             100 %             only 3.9 % correct in xam_v4
 · recovery-rate changes      100 %             (it kept calling them "sudden jolts")
 · not inventing facts      141/141           · "false alarms": ~2 per answer,
                                                e.g. calling ordinary noise a problem
                                              · trusting a statistical test whose
                                                assumptions the data violated
                                              · on completely clean books it still
                                                reported problems in 4 of 6 checks
```

Those four weaknesses became the four things the harness had to fix:
**characterising** (what kind of problem, over which years), **calibrating**
(is the statistical test even valid here), **restraint** (say "nothing unusual"
when that's the truth), and **investigating** (go and check before asserting).

---

# PART 2 — How the improvement loop works

One book at a time, never in parallel (the server has a single slot — two
requests at once would crash it):

```
        ┌─────────────────────────────────────────────────────────────────────┐
        │ 1. pick the next book from the OPTIMIZATION set (23 books)          │
        │                                                                     │
        │ 2. THE HARNESS prepares the question:                               │
        │      original data tables                                           │
        │    + EVIDENCE PACK (statistics computed from those same tables)     │
        │    + RULEBOOK (how to interpret the numbers, when to stay silent)   │
        │                                                                     │
        │ 3. THE AI reads it and answers with a structured list of findings   │
        │    (it may ask the harness to run small calculations for it — the   │
        │     "tool", at most 4 times, then it must answer)                   │
        │                                                                     │
        │ 4. THE MARKER compares the answer with the hidden ground truth      │
        │      → correct / missed / wrong kind / false alarm                  │
        │                                                                     │
        │ 5. DIAGNOSIS: which of the four weaknesses let it down this time?   │
        │                                                                     │
        │ 6. EDIT THE HARNESS (evidence, rulebook, or the machinery)          │
        │    → the edit is only kept if it survives the evidence: any idea    │
        │      that doesn't separate the cases is thrown away                 │
        │                                                                     │
        │ 7. repeat from step 1 ── the harness is now slightly "grown"        │
        └─────────────────────────────────────────────────────────────────────┘
```

Two modes of running that loop:

* `scripts/harness_opt_step.sh` — one book per command, stopping in between so a
  human (or the agent) can edit the harness. Used while the harness is changing.
* `scripts/harness_pass_run.sh` — walks every remaining book unattended, retries
  failures, skips finished ones and can be safely re-run after any crash.
  Used once the harness is frozen for a whole pass.

Rules that keep it a fair experiment (not "teaching to the test"):

* The ground truth **never** enters the question put to the AI. An automatic
  gate re-checks every question before it is sent and refuses to run if a
  forbidden word or answer-bearing phrase appears.
* All thresholds were tuned on the optimization books only; the held-out books
  are touched exactly once, at the end.
* Every book, including failures, is kept on disk (`results/…`) with the full
  transcript, so nothing is quietly dropped.

---

# PART 2b — One book at a time first, the whole set only to measure

The two modes above are not interchangeable, and mixing them up wastes hours or
flatters the numbers. The rule the project settled on:

```
   ┌──────────────────────────────────────────────────────────────────────────┐
   │  GROW THE HARNESS — work ONE book at a time (the "individual node")      │
   │                                                                          │
   │   pick a book the marker says is WRONG                                   │
   │        │                                                                 │
   │        ▼                                                                 │
   │   run THAT book alone (one call, ~10-40 min)                             │
   │        │                                                                 │
   │        ├── now correct ──────────► move to the NEXT wrong book           │
   │        │                                                                 │
   │        └── still wrong ──► MEASURE why (offline, no calls)               │
   │                            └─► grow the harness (pack / rulebook / code) │
   │                                 └─► run the SAME book again ──┐          │
   │                                                               │          │
   │                                        (repeat until it passes)◄─────────┘
   └──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼  only when the wrong books are handled
   ┌──────────────────────────────────────────────────────────────────────────┐
   │  MEASURE — run the WHOLE optimization set once (23 books, 8-12 h)        │
   │  → score → freeze gate (strict >= 80 %, false alarms <= 1.0, clean book  │
   │    untouched, no unreadable answers, drift strata not worse)             │
   │  → only if it passes: the HELD-OUT exam (24 unseen books x 3 answers)    │
   └──────────────────────────────────────────────────────────────────────────┘
```

**Why one book at a time while growing.** A wrong book is the unit of work: its
failure mode ("the right window with the wrong pattern word", "a jolt read as
erraticness") points at one specific defect, and a single-book run returns in
minutes. Running all 23 after every edit would cost 8-12 hours per idea and would
report only an aggregate — the diagnosis would be lost, and most edits would be
judged on noise.

**Why the whole set is still required to measure anything.** A set of books
chosen *because* they are hard is not a sample of the benchmark. In the v1.6
loop the five hardest books finished at 93 % of their units but **1.4 false
alarms per answer** — above the 1.0 ceiling the gate applies. The other eighteen
books sat at 0-1 false alarms each before, so the split-wide number should pass,
but that is an *inference*; only a full run turns it into a measurement. The same
logic constrains every claim in this document: per-book results are diagnostics,
split-wide results are evidence.

**The order actually used, and why it is cheap.** Wrong books first, because each
one is a defect to repair; then the never-run books, because they test whether the
repairs generalise or quietly broke something; then the books that were run under
an *earlier* version of the harness, because a corpus stitched from several
versions measures a harness that never existed. That last re-run is the price of
iterating in place, and it is small (5 books) compared with the tuning it bought.

---

# PART 3 — The growth history, version by version

## v1.0 — the evidence pack (give the analyst a calculator)

**What we saw.** In `xam_v5` the AI mislabelled slow trends as jolts (only half
the "bounded" trends right), quoted statistical significance computed under an
assumption the data broke, and produced about two false alarms per answer.

**Why we thought so.** Reading its written reasoning showed it doing arithmetic
in its head — ten years × four lines — and losing track. It never computed
year-to-year variability or fitted a trend; it eyeballed.

**What we changed.** A program (`scripts/stats_pack.py`) now runs *before* the
question is sent, reading only the same tables the AI already gets, and appends a
compact computed summary — the **evidence pack**. For each insurance line:

| evidence item | plain-language meaning |
|---|---|
| yearly table with z-score | each year's A/E plus "how far from expectation, in units of ordinary noise" |
| trend gradient + R² | how steep the long-run movement is, and how well a straight line describes it (1.00 = perfect) |
| best "step" | the single point where the average level jumps most |
| best "excursion" | the stretch of years whose average level differs most from the rest |
| overdispersion factor | how much wilder the year-to-year swings are than pure chance allows |
| longest run | the longest unbroken string of years moving the same way, and how far it went |
| smoothed 3-year average | the wobble removed, so slow drifts become visible as a gentle ramp |
| IP termination table | recovery-rate evidence per diagnosis (pooled across durations) |

**What happened.** First live test (book sc-042304): the AI found the right
problem — but produced **4 false alarms**, because it promoted the pack's own
"overdispersion x2.2" numbers into findings. Growth created a new failure. That
is normal, and it is why the loop measures after every change.

## v1.1 — the rulebook (teach restraint)

**What we saw.** v1.0's four false alarms were all lines the pack described as
having *no strong signal* — the AI had simply amplified the pack's raw numbers.

**What we changed.**
* The pack now states an **evidence profile** — a description of the shape of
  the evidence, never a claim that something is wrong.
* Each overdispersion number is labelled with what it *means for the test*:
  "test assumptions valid" / "indicative only" / "test invalid here".
* Two discipline rules went into the rulebook: *a merely uneven line is normal
  texture, not a finding*; *small subgroups (few expected claims) produce
  extreme ratios by chance and are never evidence on their own*.
* All decision thresholds were re-derived from the **optimization books only**.

**What happened.** Same book re-run: **1/1 correct, 0 false alarms.** Measured
offline across the optimization set: lines that are genuinely clean were being
given an "anomaly-shaped" profile 24 times before this change, **0 times** after.

## v1.2 — the smoothed level (make a slow ramp visible)

**What we saw.** On book sc-137901 the AI answered "sudden jolt, 2022–2023" for
two lines whose real answer was a slow trend across 2019–2023. It scored **0/2**.

**Why we thought so.** We read the pack the AI had been given, and it was **our
own text that misled it**: it described the movement as an "abrupt excursion over
2 years … short/absent ramp". The pack had been fooled by noise into choosing the
two steepest years and calling that the whole story.

**What we changed.** The pack now also prints the **3-year moving average** as a
series, and the profile says: read where the smoothed level leaves and returns to
its own baseline, and report *that* span. The moving average removes the
year-to-year wobble, and the ramp appears:
`0.93 0.91 0.93 0.95 0.98 1.05 1.12 1.09`.

**What happened.** The same book re-run: **2/2 correct**, with the exact years
the answer sheet used ([2019, 2023]). It also became 3.5× faster and used 60 %
fewer tokens (1,643 s → 472 s; 38k → 15k tokens) — a correct harness also stops
the AI second-guessing itself.

## the tool loop (let the analyst go and look)

Shipped alongside v1.0, proven useful later: the AI may ask the harness to run a
small Python calculation inside that book's own data folder (maximum 4 requests,
10 seconds each). Observed uses: it inspected the age-band tables behind a false
alarm and then *declined* to report it; on a deliberately clean book it looked
around and still answered "nothing unusual".

## v1.3 — four targeted repairs after pass 1

Pass 1 finished all 23 optimization books and was marked. The verdict was
split — much better restraint, no better recall — and the five failures each had
a *specific*, fixable cause:

| failure | what the AI did | why (root cause) | v1.3 fix |
|---|---|---|---|
| sc-314eca | 2-hour answer, unreadable output, and it was *saved as a success* | the AI used its own native "<tool_call>" format that our machinery didn't recognise, and a faulty safety line then cleared the error flag | machinery fixed: native format is now understood and executed; a content failure can never again be marked as success |
| sc-9660b9 | five separate per-line stories | **our pack only ever looked at one line at a time**, so a book-wide event looked like four unrelated problems | new CROSS-LINE section: counts how many lines move together each year |
| sc-6e2478 | answered "nothing unusual" | the pack said "no strong signal" although the line's swings were 5× wilder than chance | new **scatter-dominant** profile |
| sc-8a9fa1 | called a wobbly line a "trend" | same gap as above | same fix |
| sc-5e376b | called a flat-topped 3-year jolt a "trend" | *our own wording* invited "2–3 year sustained move" | new **onset sharpness** statistic: does the change arrive in one year (a jolt) or build up year by year (a trend)? |

Two of the v1.3 additions deserve a sentence of explanation:

* **Onset sharpness** = the biggest single-year move ÷ the size of the whole
  excursion. If the change arrives in one go, that ratio is about 1.0; if it
  builds up over years, the ratio is well below 1; if the line swings around
  without holding a new level, the ratio is above 1.3. Calibrated on the
  optimization books: jolts sit at ~1.1, build-ups mostly below 0.9, swinging
  lines at ~1.8.
* **Cross-line coordination** = each year, how many of the four lines sit away
  from their own baseline, plus how many take an unusually large swing. A claim
  of coordination requires **at least two consecutive years with three or more
  lines**. Verified to fire on the two book-wide cases and to stay silent on a
  single-line jolt and on a clean book.

Pass 2 (all 23 books again, with v1.3) is running now.

## v1.4 — three repairs after pass 2 (the final permitted pass)

Pass 2 finished all 23 books with **72.7 % correct** (up from 61.4 %) and
**0.78 false alarms per answer** (baseline 1.61) — but it also introduced one
regression and left three structural gaps:

| what we saw | why (root cause) | v1.4 fix |
|---|---|---|
| sc-137901 went **2/2 → 0/2**: two slow trends again reported as sudden jolts | our new "onset sharpness" rule was checked *before* the smoothed-ramp evidence, so a genuine ramp that happens to contain one big year was labelled a jolt | the smoothed-ramp evidence now takes precedence: if the 3-year average rises steadily, it is a build-up, whatever any single year did |
| sc-d72b95: the AI found the two jolts but missed two trends that continue to the last year of data | the pack reported only the single best-matching window, which happened to be an *early* dip — the later rise was invisible | the pack now lists **up to three non-overlapping windows** plus a "level at the END of the series versus its own baseline" figure (clean books never exceed 0.008, so this is a very clean signal) |
| sc-9660b9 and sc-314eca: book-wide erraticness still told as separate per-line stories (0–1 of 4) | the cross-line warning existed once, at the end of the pack, and each line's own story was more persuasive | every affected line now carries its own note — *"this line is one of several taking unusually large swings in 2020-2022 — the book became erratic as a whole"* |

Measured effect so far on the two books we can already check: sc-137901's two
trends are again described as build-ups covering the right years, and
sc-d72b95's hidden 2019-2024 rise is now listed
(`2019-2024 (6y) +0.185`).

**Pass 3 finished all 23 books with no failures: 75.0 % correct (33 of 44),
0.52 false alarms per answer, no unreadable answers.** Both repairs above landed
where they were aimed, and the price is visible too:

| book | pass 2 (v1.3) | pass 3 (v1.4) | likely cause — *inference, not proof* |
|---|---|---|---|
| sc-137901 (systemic) | 0/2, 3 false alarms | **1/2, 1** | the ramp evidence now outranks the single big year — this book was the fix's target |
| sc-d72b95 (systemic) | 2/4 | 2/4 *(unchanged)* | it still reports the two 2020 jolts and still misses the two 2021-2024 rises, although the pack now lists that window |
| sc-314eca (systemic) | 1/4, 4 false alarms | **3/4, 1** | per-line "the whole book became erratic" notes |
| sc-9660b9 (trap) | 0/4, 5 false alarms | **1/4, 3** | same, partially |
| sc-bba653 (systemic) | 4/4, 3 false alarms | 4/4, **0** | the per-line notes stopped it inventing extra findings |
| sc-da1123 (systemic) | 4/4, 0 | **3/4, 1** | one trend now read as a jolt — the reverse of the sc-137901 trade |
| sc-6e2478 (erratic) | 1/1 | **0/1** | the smoothed-ramp precedence let a genuinely erratic line be told as a slow move |
| sc-8a9fa1 (trap) | 1/1 | **0/1, 1 false alarm** | same cause |
| sc-2d248f (erratic) | 1/1, 0 | 1/1, **2** | found the erratic line but added two more findings around it |
| sc-f69eea (trend) | 1/1, 1 false alarm | 1/1, **0** | end-of-series level figure |

Net: **+1 correct finding and −0.26 false alarms per answer** versus pass 2, but
one slow-trend family unit moved the wrong way (persistent-to-horizon 8/10 →
7/10) and the trap books remain the weakest family (1/5 = 20 %).

**How much of this is signal?** One answer per book, so a one-unit change on a
single book is *not* established as caused by the edit that was aimed at it. The
measured spread of the unharnessed model across three identical runs was about
±3 units on 44 — the same order as several rows above. The two rows the edits
were explicitly designed to move (sc-137901 and the per-line trap notes) moved in
the intended direction; the rest of the table is recorded as observation, and
the causes listed are the most plausible reading, not measurement.

---

## v1.5 — the round after the gate said no (pass 4)

The three-pass cap was a rule we set, and the human running the project chose to
lift it rather than spend the held-out exam on a version that had not reached the
bar. That is legitimate as long as one thing stays true: **the 24 held-out books
remain unread**. Extra passes on the 23 practice books cost accuracy on nothing —
they only make the tuning set more familiar, which is exactly why the held-out
exam exists.

Work started from the eleven control-units still missed, and the first job was to
find out *why* each was missed rather than guess. That measurement changed the
plan:

| what looked like the problem | what the measurement said | what was done |
|---|---|---|
| "the pack suppresses dispersion" — our rulebook says ignore scatter below ×6, while the true unsteadiness units sit at ×3.0–22.7 | lowering that floor would fire on **28 lines of which only 4 are the right ones**, and 16 of the others are *jolts* the model currently gets right 15/15. Relabelling those would trade a real skill for a proxy | **nothing.** A fourth attempt to separate planted unsteadiness from an ordinary noisy line, and a fourth failure — recorded in Part 4 with the numbers |
| "maybe a jolt is one big swing and unsteadiness is several" | backwards: the *trend* lines are the ones with two or more big swings (7 of 13); the unsteadiness lines have 0–1 | **nothing**, same reason |
| the pack calls a late slow rise "no strong signal" because an earlier jolt cancels the whole-window fit | a **tail segment** statistic (the final three years' gradient, fit quality and level versus the years before) fires on **11 lines, every one a real movement, and on none of the clean book's four lines** (clean \|gradient\| ≤ 0.013, real ones 0.036–0.113) | **added to the pack.** It makes `sc-d72b95`'s and `sc-da1123`'s late rises visible — the two units that were missed for this reason |
| `sc-137901`: the model's own prose said the move was "coordinated with IP", but it emitted an entry for TPD only | a rule-following failure, not a knowledge failure | **rule 3c sharpened**: one entry per affected line even when one line's move is smaller, and mentioning a line only in prose counts as not finding it |

Expected effect, stated before the pass ran so it cannot be rationalised later:
the two repairs should recover **2–3 of the 11** missed units (79.5–81.8 %), with
false alarms roughly unchanged, because both repairs add information about
movements the model *already detects* rather than loosening a threshold. The
unsteadiness units (7 of 11) are **not** expected to move: three separate
discriminators were measured and all three failed, and the trap books plant their
scatter across sibling lines that have no planted control at all — so any rule
that claims the right line also claims the innocent ones. That part of the
benchmark is hard by design and is left honestly unreached rather than gamed.

**What actually happened (pass 4, 23 books, no failures): 81.8 % correct, 0.91
false alarms per answer, clean-book honesty intact, and the freeze gate passed on
all six criteria.** The honest attribution is narrower than that headline:

| change | units gained | evidence |
|---|---|---|
| the cross-line rule | **+1** | `sc-137901` 1/2 → 2/2, the IP entry recovered, false alarms unchanged. Aimed at exactly this failure |
| the TAIL block | **net 0** | worked where predicted (`sc-da1123` TPD and `sc-d72b95` CI both recovered — the tail reads +0.080/yr, fit R2 0.96 on that CI line), but on the same `sc-d72b95` it cost both 2020 jolt units, because the model now reads that line as a drift "2016-2020" instead of a jolt. Two recovered, two lost |
| sampling luck | **+2** | `sc-6e2478` and `sc-8a9fa1` both recovered, and the TAIL block does not fire on either line; `sc-6e2478`'s previous answer was an empty 83-character response. The temperature-1.0 lottery, not the edits |

And one prediction **failed**: false alarms did *not* stay flat — 0.52 → **0.91**.
The cause is our own wording. The TAIL instruction says to report the tail "even
when an earlier event on the same line is bigger and already reported", so the
model now emits *two* findings on lines where the tail fires (8 findings on
`sc-bba653` for a 4-line jolt, 8 on `sc-da1123` for 4 trends). The second entry
often carries the wrong pattern name for that line's control, so it counts as a
false alarm: +9 in total, concentrated in those two books. For context, 0.91 is
still 44 % fewer false alarms than the unharnessed model's 1.61.

The better wording — "extend the same finding's window into the tail" instead of
"add a second finding" — is recorded as a known improvement and **deliberately
not applied**. The gate passed on rules fixed in advance, and editing again right
after passing, to improve the very number the gate just accepted, is how a tuning
set gets overfit. It belongs in a future round with a fresh tuning split.

---

## v1.6 — the round that ended with a frozen harness (passes 5-7)

The human owner asked for more improvement before the held-out exam, so the cap
was lifted again. The condition that keeps this honest does not change: **the 24
held-out books stay unread**, and one tempting fix was rejected precisely because
of them (below).

Pass 4 left 8 missed units and 21 false alarms. Both were traced to named causes:

**The recall defect — the harness contradicted itself.** On `sc-9660b9` the model
returned the *exact right window on all four lines* and the wrong word on three:

```
Death [2020,2022] "sustained move"   → counted as a false alarm
CI    [2020,2022] "sustained move"   → counted as a false alarm
TPD   [2020,2022] "dispersion"       → correct
IP    [2020,2022] "one-off change"   → counted as a false alarm
```

Its own evidence text quotes the pack saying the line *"oscillates rather than
holding a new level"* — and then it wrote a sustained move anyway, citing the
system prompt verbatim: *"prefer drift per 'rises YoY before peaking' rule"*.
That clause was overriding the pack. Five units were being lost to a **word
choice on windows the model already found**.

**The false alarms — three of the four kinds are self-inflicted.** Enumerating all
21: three are the same Death-2016 wobble appearing in three different books
(identical numbers, because the generator shares that series — a real feature the
answer sheet does not include); three are favourable deviations the model listed
without claiming them; five are second entries describing a movement it had
already reported; three are the wrong-word problem above; and seven are genuinely
distinct movements the answer sheet simply does not cover.

**The fix that was rejected.** `sc-da1123`'s five "same movement twice" points
look *exactly* like the two genuine units of a **held-out** book (`sc-c9d78b`: a
drift followed by a jolt on the same line). A rule against two findings per line
would very likely delete real held-out units, so it was not made. That is the
tuning set arguing against the exam, and the exam wins.

**v1.6 changes four things**, three of which can only remove false alarms:

| change | expected effect | measured basis |
|---|---|---|
| the "rises year over year → prefer a sustained move" clause now yields to the pack's oscillation note, and the book-wide case is stated explicitly | recall | five pass-4 units lost to this contradiction; the model's own text quotes both sides |
| a new book-wide line in the pack for "3+ lines swinging together across 2+ consecutive years" | recall | fires on **exactly 2 of 23 books**, both the book-wide unsteadiness books, never on the clean book; the six other coordinated-swing books all have a single-year span |
| a one-year wobble needs Poisson \|z\| ≥ ~4.5 to be claimed | fewer false alarms | the shared noise wobble sits at z +2.8; every genuine one-year planted jolt measures z +5.6 to +12.2 |
| observations that are not claims must not be listed, and a movement must not be described twice | fewer false alarms | 8 of the 21 pass-4 false alarms are exactly these two habits |

Predictions were registered before the pass ran: recall 40/44 = 90.9 %, false
alarms ~0.61-0.70 per answer, clean book intact, strata unchanged — and the note
that **if recall climbs while false alarms breach 1.0 per answer, the pass fails**
under the pre-agreed gate, and will be reported as a failure.

**The full sweep was stopped after one book** and replaced, on the owner's
instruction, by a one-book-at-a-time loop: run a book that was wrong, and if it is
still wrong, change the harness and run *that same book* again before moving on.
Four wrong books, worked in order:

| book | before | after | how it got there |
|---|---|---|---|
| `sc-042304` (control) | 1/1, FP 0 | **1/1, FP 0** | untouched — proof the new rules do not cause over-reporting |
| `sc-9660b9` | 1/4, FP 3 | **4/4, FP 3** | the pack now names the book-wide erratic stretch and says which pattern word to use for every line |
| `sc-314eca` | 3/4, FP 1 | **4/4, FP 0** | 3/4 on the first attempt (the pack flagged only three swinging lines, the truth covers four) → rule grown to include the quieter fourth line → passed |
| `sc-f520e5` | 1/2, FP 3 | **2/2, FP 2** | 1/2 on the first attempt: the oscillation fix won one line and lost its twin. Both lines are statistically identical, so the rule now asks for **both readings** on such a line → retry matched both, for one extra false alarm |
| `sc-d72b95` | 1/4, FP 2 | **3/4, FP 2** | two retries. A new "give-back" note (a one-year jump that is immediately undone is a one-off change, not an erratic stretch) won both 2020 jolts; its first version named the *down* year instead of the *up* year, so the model reported a decrease — correcting the year turned that into a match |

Those same five books scored **47 % (7/15) with 9 false alarms** before and
**93 % (14/15) with 7 false alarms** now.

**The fifth line of that table is also the honest limit.** `sc-d72b95`'s last
missed unit is a drift of +0.05/yr whose computed final-years gradient is
**+0.017/yr with fit R² 0.08** — noise by every statistic in the pack. The two
retries matched *different* three-of-four units, which is the signature of a coin
flip rather than a fixable gap, so the loop stops there instead of tuning further.

**Two things this round cost, stated plainly.** First, each book now spends
20–40 minutes reasoning (20,000–37,000 reasoning tokens) against ~10 minutes
before — so a full sweep is ~8–12 hours and the held-out exam ~24–36 hours.
Second, on these five hardest books the false-alarm rate is 1.4 per answer, which
is **above the 1.0 ceiling** the gate applies split-wide. The other eighteen books
sat at 0–1 false alarms each before, so the split-wide number should still pass —
but that is now an assumption rather than a measurement, and only a full sweep can
settle it. It did not pass — see below.

### v1.6b, measured: best recall yet, and the gate says no

The full 23-book sweep finished on 2026-09-13: **88.6 % correct (39/44)** — the
best of any version — but **1.26 false alarms per answer** against a ceiling of
1.0, and the bounded-then-reverting drift stratum fell to **2/5** from 5/5.
**The gate failed, so v1.6b was not frozen.** What was gained and lost:

```
 gained:  sc-9660b9 1/4→4/4 (+3)   sc-d72b95 1/4→3/4 (+2)
          sc-314eca 3/4→4/4 (+1)   sc-f520e5 1/2→2/2 (+1)
 lost:    sc-137901 2/2→1/2   sc-3c83fd 1/1→0/1
          sc-9372cd 1/1→0/1   sc-bba653 4/4→3/4
 false alarms: +8, concentrated on the jolt books (one book alone: +5)
```

Reading the answers rather than guessing gave three causes, two of them mine:

1. On the jolt books the model was adding a dispersion entry beside every correct
   jolt entry. My own new system-prompt wording invited that "whenever the
   CROSS-LINE block reports several lines swinging together" — and that block
   always prints swing counts, including several lines swinging in a **single**
   year, which is precisely what a book-wide jolt looks like. A false lead created
   by the very rule that fixed the erraticness books.
2. The dual-reading note asked for a level-change entry but never said **which
   shape**, so on two books the model offered a one-off change where the truth is
   a sustained move — both bounded drifts, which is why that stratum collapsed.
3. One loss (`sc-3c83fd`) is plain model variation: it reported a single eight-year
   "shock" for a drift, and no rule of ours points there.

**v1.6c repairs both by narrowing rather than adding:** the system-prompt rule now
demands *consecutive* years and says outright that a single-year coordinated swing
is a jolt; the pack adds that clarification on the six books where lines swing
together in one year (verified by a firing test) while the multi-year instruction
still fires on exactly the two erraticness books; and the dual note now names the
shape its second entry should take. Leak preflight passed on all 47 books, and a
fresh sweep was launched so that all 23 books are measured under **one** version —
the previous corpus was stitched from three intermediate variants, which is the
price of editing in place and is why that re-run is not optional.

**If v1.6c also fails the gate, the fallback is v1.5** (pass 4) — the only version
that has passed it: 81.8 %, 0.91 false alarms, strata 9/10 and 5/5.

---

# PART 4 — Ideas we tested and threw away

Growth is not just addition. Four plausible ideas were implemented, measured on
the optimization books, and **discarded** because they did not actually tell the
cases apart:

| idea | what it measured | why it was rejected |
|---|---|---|
| year-to-year "ramp ratio" | biggest move ÷ average move | trends 1.68, jolts 1.89, clean 1.94 — useless |
| excursion on the smoothed line | best stretch of the smoothed series | kept choosing the *mirror-image* window (the opposite direction) |
| rise/flat/fall shape of the smoothed line | how the smoothed line rises and falls | trends and jolts overlapped completely (a 1-year jolt smears into a 3-year rise) |
| dispersion vs sibling lines | a line's wildness relative to the book's other lines | book-wide events put every line at the same level, so the ratio collapses |
| **a dispersion floor low enough to catch the unsteadiness books** (v1.5 round) | whether a scatter threshold can point at the planted line | it fires on 28 lines and only **4** are the right ones, while 16 of the others are *jolts* the model already gets right 15/15 — relabelling those would trade a real skill for a proxy. Our ×6 rule was measured and deliberately left alone |
| **"one big swing = jolt, several swings = unsteadiness"** (v1.5 round) | how many separate large excursions a line has | exactly backwards: the *trend* lines are the ones with two or more (7 of 13); the unsteadiness lines have 0-1 |
| **"a swing that returns to where it started = unsteadiness"** (v1.5 round) | the shape of the largest excursion | fires on a genuine *trend* unit and misses three of the four unsteadiness units. Written as a rule, tested against the recorded clean-book numbers, and deleted again before any pass was run |

The honest, useful conclusion: **"deliberately planted unsteadiness" cannot be
separated from "a naturally noisy line" using per-line statistics** — that is
precisely why those books are traps. The harness therefore presents the numbers
with their meaning and lets the AI decide, rather than pretending to know. Three
further discriminators were tried in the v1.5 round (last three rows) and all
three failed the same way; the trap books also spread their scatter across
sibling lines that have **no planted problem at all**, so a rule sharp enough to
catch the real line also accuses the innocent ones.

---

# PART 5 — Incidents and repairs (why the machinery matters)

| when | what happened | repair |
|---|---|---|
| early | the server restarted mid-answer; half a JSON answer was saved as a *successful* run | a "dead stream" is now a retryable failure: no proper finish marker, unreadable answer, or an answer that is still asking for a tool = retry, never save |
| pass 1 | the AI answered in its own tool format; that raw text was marked as a normal answer | the native format is now recognised and executed |
| pass 1 | after all retries failed for *content* reasons, a safety line still cleared the error flag, so a broken answer counted as good | error-clearing now ignores content failures |
| during tuning | a forbidden word ("volatility") slipped into the rulebook; the leak gate refused to start the run | wording fixed; a 10-second no-API pre-flight script now checks the full question for all 47 books before any run |
| unattended run | the runner kept re-running one book and then falsely reported "complete" | the script's internal variable was being overwritten by its own status helper (a shell-script trap); completion is now *recounted from the files on disk*, never asserted |
| unattended run | one book spent 2 hours spiralling | the rulebook now caps tool use at two calls for easy books |
| pass 3 | the LLM server went down for ~4.5 h mid-pass; 12 attempts failed | each failure is written to disk flagged as an error and is *not* counted as an answer, so nothing was corrupted; the loop waited, then resumed by itself and the four books that exhausted their retries were re-spent by re-running the same command |
| pass 3 → freeze | **the v1.3 source no longer exists**: the harness is edited in place, the project is not under version control, and nobody snapshotted the code when pass 2 ran | each pass now copies the two harness files with sha256 into `results/<pass>/harness_snapshot/` before its first call — the same protection the held-out exam already had. Consequence for the record: only **v1.4 is freezable**, because v1.3 cannot be restored. The 23 recorded `pack_text` fields of pass 2 preserve *what the AI was shown*, but not the code that produced it |

---

# PART 6 — Scoreboards

**Same 23 optimization books, same AI, one answer each — with and without the
harness:**

| metric | harness OFF (`xam_v5`, answer 1) | pass 1 (v1.2) | pass 2 (v1.3) | pass 3 (v1.4) | pass 4 (v1.5) | **v1.6e — FROZEN** |
|---|---|---|---|---|---|---|
| correct findings (strict) | 63.6 % | 61.4 % | 72.7 % | 75.0 % | 81.8 % | **97.7 %** |
| correct or nearly (loose) | 63.6 % | 63.6 % | 75.0 % | 75.0 % | 84.1 % | **97.7 %** |
| false alarms per answer | 1.61 | **0.52** | 0.78 | **0.52** | 0.91 | 0.96 |
| slow trends that stop early | 3/5 | 5/5 | 3/5 | 4/5 | 5/5 | **5/5** |
| slow trends running to the end | 8/10 | 8/10 | 8/10 | 7/10 | 9/10 | **9/10** |
| trap books | 2/5 | 0/5 | 2/5 | 1/5 | 2/5 | **5/5** |
| unreadable answers | 0 | 1 | **0** | **0** | **0** | **0** |
| honesty on clean books | intact | intact | intact | intact | intact | intact |

The final column is the frozen harness. Read it together with the attribution
tables in the version sections: the recall figure is a full-sweep measurement of
23 answers, and the corpus was verified to be consistent with the frozen files
(they rebuild all 23 recorded questions byte-for-byte). **One unit of 44 is still
missed anywhere in the split** — `sc-d72b95`'s Death drift, whose signature is
+0.017/yr at fit R² 0.08.

Read the pass-4 column together with the attribution table in the v1.5 section:
of the +3 units over pass 3, **one** is cleanly due to a rule change, the TAIL
block nets zero (two recovered, two lost), and two are sampling luck. False alarms
rose from 0.52 to 0.91 there — still 44 % below the unharnessed model, but they
rose, and the cause was our own instruction.

Books fixed by v1.3 (pass 1 → pass 2): the flat-topped jolt it had called a
trend (0/1 → 1/1), both missed erratic lines (0/1 → 1/1 each), one systemic book
(2/4 → 4/4) and one mixed book (1/2 → 2/4). Per-family in pass 4 (strict /
controls): jolts 4/4, trends 3/3, recovery 2/2, systemic 20/24, mixed 3/4,
erratic 2/2, trap books 2/5 — the traps remain the weakest family by a wide
margin, and every book each version changed is itemised in the version sections
above.

Running history inside the loop (the honest, warts-and-all view):

```
 v1.0  sc-042304   correct 1/1   false alarms 4   ← the pack's numbers were over-amplified
 v1.1  sc-042304   correct 1/1   false alarms 0   ← restraint rules
 v1.1  sc-137901   correct 0/2   false alarms 2   ← our own wording misled it
 v1.2  sc-137901   correct 2/2   false alarms 0   ← smoothed level, exact years
 v1.2  sc-14cdd9   "nothing unusual", 0 findings  ← honesty held on a clean book
 v1.2  pass 1 complete: 23 books, no failures  → 61.4 % correct, 0.52 false alarms
 v1.3  pass 2 complete: 23 books, no failures  → 72.7 % correct, 0.78 false alarms,
                                                  0 unreadable answers, 1 regression
 v1.4  pass 3 complete: 23 books, no failures  → 75.0 % correct, 0.52 false alarms,
                                                  0 unreadable answers, trap books 1/5
 v1.4  gate applied: NOT MET — 75.0 % against a target of 80 %, and the three-pass
                   cap was spent; the cap was then lifted by the human owner
 v1.5  pass 4 complete: 23 books, no failures  → 81.8 % correct, 0.91 false alarms,
                                                  0 unreadable answers, trap books 2/5
 v1.5  gate applied: ALL SIX CRITERIA PASS  →  FROZEN
 v1.6  one-book loop on the four wrong books: 47 % → 93 % of their units
 v1.6b full sweep: 88.6 %, false alarms 1.26  →  gate FAILED (over-reporting)
 v1.6c repairs by narrowing; v1.6d adds profile/onset agreement and a
       direction-symmetric drift clause
 v1.6d full sweep: 97.7 %, false alarms 1.26, both strata pass  →  gate FAILED
       on false alarms alone (24 of the 29 were the deliberate "other reading")
 v1.6e removes one clause that invited a redundant paired entry on the two
       book-wide books → 97.7 %, false alarms 0.96
 v1.6e gate applied: ALL SIX CRITERIA PASS  →  FROZEN (verified: the frozen
       files rebuild all 23 recorded questions byte-for-byte)
```

**Freeze gate — final result.** The gate was fixed in
advance so the stopping decision could not be talked into a better answer
afterwards. It is a script rather than a paragraph —
`python3 scripts/harness_gate.py results/harness_opt_p4/zero_shot` (exit 0 =
freeze, 1 = do not freeze):

| criterion | target | pass 1 (v1.2) | pass 2 (v1.3) | pass 3 (v1.4) | pass 4 (v1.5) | **v1.6e (frozen)** |
|---|---|---|---|---|---|---|
| correct findings | ≥ 80 % | 61.4 % ✗ | 72.7 % ✗ | 75.0 % ✗ | 81.8 % ✓ | **97.7 % ✓** |
| false alarms per answer | ≤ 1.0 | 0.52 ✓ | 0.78 ✓ | 0.52 ✓ | 0.91 ✓ | **0.96 ✓** |
| clean books never called anomalous | 0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| no unreadable / errored answers | 0 | 1 ✗ | ✓ | ✓ | ✓ | ✓ |
| slow trends to the end | not below baseline (8/10) | 8/10 ✓ | 8/10 ✓ | 7/10 ✗ | 9/10 ✓ | **9/10 ✓** |
| slow trends that revert | not below baseline (3/5) | 5/5 ✓ | 3/5 ✓ | 4/5 ✓ | 5/5 ✓ | **5/5 ✓** |

**Verdict: FREEZE (exit 0) — all six criteria met.** The frozen harness is
snapshotted with sha256, and it was **verified rather than assumed** that the
corpus matches it: the frozen files rebuild all 23 recorded questions
byte-for-byte, so the reported answers are answers to exactly the questions the
frozen harness asks.

Four caveats travel with that verdict, and they belong next to the headline:

1. The bottom two rows were **added on the day the gate first became a script**;
   before that the agreed gate was the top four rows. Nobody tuned against them,
   but they are not pre-registered in the same sense as the 80 % target.
2. False alarms are **0.96 against a ceiling of 1.0** — the thinnest margin of any
   criterion, with 22 spread across fourteen books. Most of them are the
   deliberate "report both readings" hedge on ambiguous lines, which is precisely
   what buys the recall. A harness that hedged less would trade recall for
   precision; the gate was set to prefer recall, and it is worth saying plainly
   that this is a choice rather than a free win.
3. The route from 81.8 % to 97.7 % ran through **two further gate failures in two
   days** (v1.6b, and v1.6d's near-miss on false alarms alone), each diagnosed
   from the answers rather than guessed, and each fixed by *narrowing* a rule
   rather than adding machinery. The single unit still missed anywhere in the
   split — `sc-d72b95`'s Death drift at +0.017/yr, fit R² 0.08 — is documented as
   statistically invisible rather than quietly dropped.
4. Everything above is the **optimization split**, now used for tuning many times
   over. The number that has never been tuned against is the held-out exam, and
   that is the next step. With three answers per book it is also the first
   measurement in this project whose differences are larger than the
   temperature-1.0 lottery.

---

# PART 6b — The held-out exam: the number that counts

**Run 2026-09-13 → 2026-09-15: 24 never-tuned books × 3 answers = 72 calls with the
frozen harness, followed by the full workspace leak check (CLEAN — 1,599 files, 0
hits).** This is the only measurement in the project that was never tuned against,
and the only one with three answers per book, so its differences are larger than
the temperature-1.0 lottery.

| metric | harness OFF (same 24 books × 3) | frozen harness | change |
|---|---|---|---|
| correct findings (strict) | 79/123 = 64.2 % | **85/123 = 69.1 %** | **+4.9 points** |
| false alarms per answer | 2.00 | **0.96** | **halved** |
| clean book (1 book × 3 answers) | claimed anomalies in **2 of 3** | **0 of 3 — correctly silent** | fixed |
| slow trends running to the end | 6/6 | 6/6 | tie |
| slow trends that revert | 17/36 = 47 % | 11/36 = **31 %** | **−17 points (worse)** |
| unreadable / errored answers | 0 | 0 | — |

Per family (harness OFF → frozen harness):

```
 shock        8/12 = 67 %  →  12/12 = 100 %     recovery    9/9  →  9/9
 mixed       12/15 = 80 %  →  13/15 =  87 %     volatility  6/6  →  6/6
 drift        6/9  = 67 %  →   6/9  =  67 %     noise traps 1/6  →  3/6  (17 % → 50 %)
 systemic    37/66 = 56 %  →  36/66 =  55 %   ← the largest family, essentially flat
```

Per book: **5 improved** (by +4, +3, +2, +1, +1 units), **3 got worse** (−2, −2, −1),
16 unchanged.

## What this says, including the unflattering part

**The harness helps on unseen books, but far less than the practice books
suggested.** The optimization split ended at 97.7 %; the held-out split scores
69.1 %. That ~29-point gap is the signature of fitting — a good part of the polish
on the practice books was learned from those particular books rather than from
reasoning that transfers.

What genuinely transferred:

* **the clean book.** The unharnessed model accused a book with nothing planted in
  it in 2 of its 3 answers. The harness never did — not in any version, not on any
  book, at any point in the project. The clearest behavioural change produced here.
* **false alarms halved** (2.00 → 0.96) *while* recall rose — not a trade, an
  improvement on both axes at once.
* **one-off events: 67 % → 100 %**, and the trap books 17 % → 50 %, though both
  remain the weakest family in absolute terms.

What did **not** transfer:

* **slow trends that revert** — the stratum the harness was explicitly taught to
  respect regressed from 47 % to 31 % on unseen books. Something in the tuned rules
  (most likely the oscillation hedge, added to win the trap books) is actively
  harmful when the book is new.
* three systemic books got worse, and the largest family (systemic, 66 control-runs)
  is flat — which is where most of the remaining headroom sits.

## The honest verdict against the pre-agreed bar

Applied to the held-out split, the gate's thresholds are **not met**: 69.1 %
against 80 %, with one stratum worse than the unharnessed baseline. The gate exists
to stop exactly the mistake of quoting a tuned number as the result, and it has
done its job. The number to carry forward is therefore:

> **On 24 unseen books, three answers each: 69.1 % of planted problems correctly
> identified (unharnessed baseline 64.2 %), 0.96 false alarms per answer (baseline
> 2.00), and no false alarm on the clean book (baseline: 2 of 3 answers). The 80 %
> target was not reached, and reverted slow trends became worse than the
> unharnessed model.**

Everything reported about the optimization split remains true and is labelled as
what it is — the tuning set. The gap between the two columns is the honest measure
of how much of that polish was learning and how much was fitting.

---

# PART 7 — What happens next

1. ~~Pass 2 finishes → scored → gate applied.~~ **Done** (72.7 %, gate not met).
2. ~~If the gate is met: freeze and run the held-out test. If not: one more
   targeted round of edits, pass 3 being the cap.~~ **The third pass is spent and
   the gate is still not met** (75.0 % against a target of 80 %). The remaining
   decision is therefore not "shall we keep tuning?" — by the campaign's own rule
   we may not — but **which version to freeze for the held-out exam**:

   | | pass 2 (v1.3) | pass 3 (v1.4) |
   |---|---|---|
   | correct findings | 32/44 = 72.7 % | **33/44 = 75.0 %** |
   | false alarms per answer | 0.78 | **0.52** |
   | clean-book honesty | intact | intact |
   | slow trends to the end | 8/10 | 7/10 |
   | slow trends that revert | 3/5 | **4/5** |
   | failed gate criteria | 1 (the 80 % bar) | 2 (the bar, and one slow-trend unit) |

   On the metric the exercise is actually about, v1.4 is ahead by one correct
   finding and a quarter of a false alarm per answer; v1.3 is ahead on one
   slow-trend unit, which is the criterion added after the fact. In practice the
   choice was never open: see the last row of Part 5 — **the v1.3 source was never
   snapshotted and cannot be restored**, so v1.4 is the only freezable version of
   the three. The table is kept because it is the honest comparison, and because
   the missing snapshot is itself a result worth stating.

   **The human running the project then lifted the three-pass cap** and asked for
   one more round before the held-out exam. That is allowed, on one condition
   that has been kept: the 24 held-out books stay unread. See the v1.5 section in
   Part 3 for what was changed and what was measured before changing it. A fourth
   pass (23 more answers) is the cost; the tuning set becoming more familiar is
   the price, and the held-out exam is what prices it.
3. **The held-out exam is now the open step** — 24 books never used for tuning,
   3 answers each = 72 calls, harness snapshotted with sha256 first:
   `bash scripts/harness_final_heldout.sh`. Compare against the unharnessed model
   on the same 24 books × 3 answers, which already exists (`xam_v5`), so the
   baseline side of that comparison costs no extra calls. This is the first
   measurement in the project with three answers per book, i.e. the first whose
   differences are larger than the sampling lottery. Whatever it says — including
   if it says the harness does not transfer — it gets reported as it comes out.
4. **Optional, separate track — actually training the AI.** Everything above
   changes the surroundings, not the model. Because the data generator knows
   exactly what it planted, unlimited perfectly-labelled practice books can be
   minted, which makes both supervised fine-tuning and reward-based training
   (using the marker itself as the reward signal) feasible. That would be a new
   project with its own hardware needs and its own risks (chiefly: learning the
   generator's habits rather than real statistical reasoning). Not started.

---

# PART 8 — Glossary for non-specialists

| term | meaning |
|---|---|
| **A/E** | actual claims ÷ expected claims. 1.00 = as expected; 1.20 = 20 % more claims than expected. |
| **expected claims** | what the actuarial assumptions predict for that year. |
| **noise** | the unavoidable randomness of claims; it makes every ratio wobble even when nothing is wrong. |
| **drift (trend)** | a slow, multi-year movement — like a tide coming in. |
| **shock (jolt)** | an abrupt change that then holds or reverts — like a wave. |
| **volatility (dispersion)** | the line becomes erratic year to year without settling at a new level — like choppy water. |
| **recovery (IP termination)** | how quickly income-protection claimants return to work; a change here is its own kind of finding. |
| **clean book** | nothing was planted; the correct answer is "nothing unusual". |
| **ground truth / answer sheet** | the record of what was actually planted. Never shown to the AI. |
| **false alarm** | reporting a problem that was not planted. |
| **recall** | the share of real planted problems that were correctly described. |
| **prompt** | the text sent to the AI — the question plus all instructions. |
| **system prompt** | the standing instructions that come before the data. |
| **evidence pack** | our computed statistics, appended to the question. |
| **rulebook (harness rules)** | how to read the evidence, and when to stay silent. |
| **tool / tool call** | the AI asking the harness to run a small calculation on its behalf. |
| **sandbox** | the restricted space where that calculation runs (only that book's own folder, 10-second limit). |
| **token** | the unit AI text is measured in — roughly ¾ of a word. |
| **context window** | the maximum amount of text the AI can hold at once (this model: 260,096 tokens). |
| **quantisation (Q8_0)** | storing the model's numbers at slightly lower precision so it fits on one machine; 8-bit here, i.e. near-original quality. |
| **llama.cpp / GGUF** | the program and file format that run this model locally on a normal machine. |
| **streaming** | receiving the answer word-by-word as it is written, instead of waiting for the end. |
| **seed / temperature** | the dials that make the AI's random choices reproducible (fixed at 1234 / 1.0 here). |
| **optimization split** | the 23 practice books used for tuning. |
| **held-out split** | the 24 books kept untouched for the final exam. |
| **leak** | any hint of the answer sheet reaching the AI. Prevented by an automatic gate on every question. |
| **harness** | everything around the AI: the question, the evidence, the tools, the rules, and the record-keeping. |

---

# PART 9 — Where things live (so anyone can check)

| path | what it is |
|---|---|
| `results/logs/harness_opt_loop.md` | the running diary: every book, what the AI said, what the truth was, what we changed and why |
| `results/logs/harness_pass_status.txt` | live progress: `SCENARIOS FINISHED: n/23`, current book |
| `results/logs/harness_pass_run.log` | detailed machinery log (including generation heartbeats) |
| `results/harness_opt_p1/` | all answers of pass 1 (v1.2), with the exact evidence text each answer was based on |
| `results/harness_opt_p2/` | pass 2 (v1.3) — 23/23 books, `scoreboard.txt` + `scores.json` |
| `results/harness_opt_p3/` | pass 3 (v1.4) — 23/23 books, `scoreboard.txt` + `scores.json` |
| `results/harness_opt_p4/` | pass 4 (v1.5) — 23/23 books, `scoreboard.txt` + `scores.json` + `gate.json` |
| `results/harness_opt_p5/` | the first book of the v1.6 sweep (halted by choice in favour of the one-book loop) |
| `results/harness_opt_p6/` | the v1.6 corpus: the five books worked in the one-book loop, then the remaining eighteen |
| `results/harness_opt_p1/quarantine/` | answers that failed for technical reasons, kept for the record but excluded from scoring |
| `results/xam_v4/`, `results/xam_v5/` | the two earlier complete experiments (untouched) |
| `scripts/stats_pack.py` | the evidence pack: all statistics described in Part 3 |
| `scripts/run_zero_shot.py` | the runner: builds the question, runs the tool loop, records everything (`--harness full` switches the harness on) |
| `scripts/harness_opt_step.sh` / `harness_pass_run.sh` | the two ways of running the improvement loop |
| `scripts/harness_diff.py` | the marker's side-by-side view: AI's findings vs the answer sheet |
| `scripts/harness_preflight.sh` | 10-second check that a question passes the leak gate — no API calls |
| `scripts/harness_gate.py` | the freeze gate as code: recomputes the scoreboard and says FREEZE / DO NOT FREEZE against the pre-agreed criteria (exit 0 / 1). Compares like-for-like (same split, same number of answers), which is why the zero-shot reference is narrowed to the optimization books before its slow-trend numbers are used |
| `scripts/harness_final_heldout.sh` | the final held-out exam with the frozen harness |

**To check progress yourself at any time:**

```bash
cat results/logs/harness_pass_status.txt
grep '^## ' results/logs/harness_opt_loop.md | tail -20
tail -3 results/logs/harness_pass_run.log
```

---

# PART 10 — What we have done so far, on one page

Written while the eighteen never-run books are being measured, so the state below
is the state before that sweep finishes.

## The question

A local AI (Qwen3.8-27B, 8-bit, one machine, one request at a time) is shown a
synthetic life-insurance book — four benefit lines, A/E ratios by year — and must
report what was planted in it. A hidden answer sheet scores every claim: correct,
missed, or false alarm. The harness is everything wrapped around the model: the
evidence it is given, the rules it follows, the tools it may call, and the record
kept. **The model is never changed. Only its surroundings are.**

## The campaign in one table

| version | what was added | what it fixed | measured result (23 books) |
|---|---|---|---|
| baseline | nothing — the raw question | — | 63.6 % correct, 1.61 false alarms |
| v1.0 | computed evidence pack | the model was doing mental arithmetic on a table | 1 book: 1/1 but 4 false alarms |
| v1.1 | restraint rules | over-reporting; clean lines described as anomalies | 1 book: 0 false alarms |
| v1.2 | smoothed 3-year level | a slow ramp was invisible; exact years wrong | pass 1: 61.4 %, 0.52 false alarms |
| v1.3 | onset sharpness, scatter view, cross-line view | four diagnosed failures from pass 1 | pass 2: 72.7 %, 0.78 false alarms |
| v1.4 | gradual evidence takes precedence; three excursion windows; end-of-series level | a regression and three structural gaps | pass 3: 75.0 %, 0.52 → **gate not met** (bar 80 %) |
| v1.5 | final-years (tail) segment; cross-line completeness rule | a late rise hidden by an earlier jolt; a coordinated event reported for one line only | pass 4: **81.8 %**, 0.91 false alarms → **gate PASSED** |
| v1.6 | book-wide erratic stretch named; one-year wobble size gate; no unclaimed observations; no double-describing; **both readings on ambiguous lines**; give-back one-off note | five control units lost to a *word choice* on windows the model already found; false alarms from three self-inflicted habits | one-book loop on the four wrong books: 47 % → **93 %** of their units |
| v1.6b | the give-back note now names the correct year | the model reported the year the spike *ended* instead of the year it happened | `sc-d72b95` 1/4 → 3/4 |

## What the growth was actually worth

* correct findings on the practice books: **63.6 % → 81.8 %** (last full sweep),
  and **93 %** on the five hardest books after the one-book loop
* false alarms per answer: **1.61 → 0.91** (last full sweep)
* honesty on the clean book: intact throughout, in every version
* the model's own readings were often right while the *label* was wrong — a large
  part of the last gain came from naming the shapes it had already found

## What repeatedly failed, and is therefore not attempted again

Four separate attempts to tell deliberately planted *unsteadiness* from an
ordinary noisy line were built, measured and discarded (Part 4). The honest
conclusion stands: per-line statistics cannot separate them, and the trap books
spread their scatter across innocent sibling lines. The final harness therefore
reports *both* readings on a line whose evidence is ambiguous, instead of
pretending to know which one is true.

## What is honest to claim, and what is not

* The **held-out books have never been read**. Every threshold in the harness comes
  from the 23 practice books.
* The 81.8 % figure is a **full-sweep** measurement, so it is evidence. The 93 %
  figure is five hand-picked hard books, so it is a **diagnostic**, not a score.
* The v1.6 corpus is currently **stitched from more than one harness version** —
  the price of editing in place. A short re-run of the five affected books is
  needed before the corpus can be quoted as a single version's result.
* The harness costs the model a lot of thinking time: 20–40 minutes per book
  against ~10 before, and the reason is that the rulebook is ~2,500 characters
  longer. That is a real cost of the growth, not a footnote.
