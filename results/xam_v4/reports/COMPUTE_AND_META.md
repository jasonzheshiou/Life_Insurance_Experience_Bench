# Compute, Token Usage & Meta-Reasoning Report

Companion to `STUDY_SUMMARY.md`. Covers the two questions "is runtime/token
usage recorded?" (yes) and "how often does the model reason about the grader?"

## 1. Token & runtime accounting — recorded on every run (141/141)

Captured automatically by `run_zero_shot.py`: `usage` (prompt/completion/total
+ cached prompt tokens), `wall_seconds`, `started_at`/`finished_at`.
No `max_tokens` is ever sent, so completion length is model-chosen (bounded
only by n_ctx = 260,096). Figures below are the real xam_v4 corpus.

| Metric | min | median | mean | max | total |
|---|---|---|---|---|---|
| prompt_tokens | 2,473 | 2,479 | 2,479 | 2,484 | 349,566 |
| completion_tokens | 3,069 | 14,986 | 17,167 | 46,853 | 2,420,566 |
| total_tokens | 5,550 | 17,465 | 19,646 | 49,331 | 2,770,132 |
| cached prompt_tokens | 0 | 2,471 | 1,464 | 2,480 | 206,469 |
| wall_seconds | 161 | 974 | 1,155 | 7,159 | 162,826 (45.2 h) |
| reasoning_chars | 8,338 | 45,382 | 50,165 | 137,448 | 7.07 M |
| answer content_chars | 83 | 2,158 | 2,404 | 5,932 | 339 k |

- **Grand total: 2.77 M tokens** (0.35 M prompt + 2.42 M completion) over
  **45.2 h wall** across 141 runs (single 1-slot server, so wall ≈ sum).
- **Throughput ≈ 16.9 tok/s** completion (median).
- **Reasoning dominates output:** ~95% of completion tokens are the hidden
  chain-of-thought (median 45 k reasoning chars vs 2.2 k answer chars). This is
  a hybrid-reasoner; the answer JSON is the tip of the iceberg.
- **Prompt is ~fixed (~2.48 k tok)** and ~100 % prefix-cached on repeat calls
  (median cached 2,471 / 2,479) — prompt cost is negligible vs completion.

### Completion tokens by family (mean / total) — "thinking effort"

| family | mean | total | note |
|---|---|---|---|
| systemic | 22,567 | 1,083,204 | most compute (multi-anomaly deliberation) |
| mixed | 20,584 | 247,011 | |
| noise_trap | 18,731 | 224,773 | lots of deliberation, and where traps bite |
| shock | 14,944 | 269,001 | |
| none/clean | 15,156 | 90,936 | |
| drift | 12,898 | 232,163 | least deliberation — and where bounded drift fails silently |
| volatility | 12,456 | 149,466 | |
| recovery | 8,267 | 124,012 | cheapest; model is confidently correct (loose 15/15) |

Interesting: the two families that **fail** (systemic, drift) sit at the
extremes of compute — systemic over-deliberates across many signals; bounded
drift is under-deliberated and mislabeled quickly. Recovery is the cheapest and
the most reliably detected.

## 2. Grader-awareness / meta-reasoning audit

Scanned all 141 `reasoning_content` traces for speculation about the task
author's intent ("planted", "the designer expects", "ground truth", "they want").

- **Pervasive, not rare:** strict designer-intent phrasing appears in **all 47
  scenarios / 141 runs** (a few per trace; up to ~30 mentions in one trace).
  The model habitually models "what would a synthetic-data generator have
  planted here?" as part of its reasoning.
- **But it almost always resolves correctly:** the meta-reasoning is one
  *input* the model weighs against the statistics, and in 140/141 clean &
  anomaly runs it lands on the statistically-correct answer. The lone
  exception is the documented honesty breach (sc-12be68 run03):
  *"They might generate a spike … So likely scenario has Death shock. Need flag
  moderate confidence maybe 0.6"* — where the designer-prior **overrode** its own
  correct conclusion ("Death 2016 not >3" → flagged anyway at conf 0.6). The
  byte-identical control scenario sc-14cdd9 used the same meta-reasoning and
  correctly answered "clean" in all 3 runs — so it's a sampling-path coin-flip
  (T=1.0), not a data-driven bias.
- **Recommendation for evaluation design:** grader-awareness is a live
  confound on this model. Mitigations for a follow-up: (a) neutralize the
  framing (no "synthetic/benchmark" language — call it "a real book"), (b) add
  decoy spikes in *every* scenario so theorizing "there must be a planted
  anomaly" is never rewarded, (c) score a "resist-the-narrative" metric =
  correct-clean-rate vs number of designer-mentions.

## 3. What changed in the tooling this session (v0.4.2)

- **Runner (`run_zero_shot.py` v0.4.2):** empty clean-stream completion
  (`content=""`, `error=None`, `finish_reason=null` — the silent-stub that cost
  several re-spends in the batch sweeps) is now a retryable `EmptyGeneration`
  error: retried in-call, and if it persists recorded as a real failure so
  `--skip-existing` correctly re-spends it instead of skipping a wasted stub.
  The over-broad `if raw_response: error=None` recovery line now also requires
  non-empty content. New `--prompt-patch {none,p2}` flag (below); every record
  now logs `prompt.patch` and the prompt sha256 (P1 vs P2 is distinguishable
  post-hoc). Leak gate unchanged and passing.
- **Prompt P2 (opt-in, default `none` = byte-identical to the corpus):** two
  surgical additions targeting exactly the two systematic misclassification
  modes — (1) bounded/finite-window drift that reverts is *still drift*, and a
  horizon-adjacent reversion is not disproof of a prior trend; (2) before
  quoting a Poisson z/sigma, compare empirical year-to-year SD vs Poisson — if
  overdispersed, classify as dispersion and don't re-apply Poisson inside a
  volatile window. Validated: `--prompt-patch p2` produces the patched prompt,
  passes the leak/integrity gate, and default runs still contain zero patch text.
- **Scorer v3 (`score_xam.py`):** null-window treated as full-period hit (only
  when the control's truth window IS the study window); multi-benefit controls
  scored as per-benefit units (no more phantom FPs for listing all four
  benefits); "no material anomaly" statements excluded from the finding pool;
  ip_recovery direction check now live; new `DRIFT-WINDOW STRATA` summary line.
  Raw v2 scores preserved at `results/xam_v4/scores_v2_snapshot.json`
  (`scoreboard_v2.txt`); v3 at `scores_v3_snapshot.json` (`scoreboard_v3.txt`).

### v3 headline vs v2

- strict-recall 56.1% → **63.1%** (control-unit denominators differ slightly
  because multi-benefit controls now count per-benefit units: 189 → 255);
- FP/run **1.54 → 1.05** (artifacts removed);
- recovery family 1/15 → **15/15 strict** (pure artifact fix — the model was
  always right; the scorer's null-window rule was wrong);
- **drift-window strata (the one number that summarizes the study):**
  persistent-to-horizon drift **28/36 strict (78%)** vs bounded-then-reverting
  **2/51 strict (3.9%)**, 5/51 loose. The failure is 100 % about window shape.
