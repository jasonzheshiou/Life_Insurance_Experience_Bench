# Reviewer notes — sc-17d82f (ip_recovery_cancer_x05, recovery)

> SCORER-SIDE — contains ground truth. Companion to the auto-generated
> `sc-17d82f_behavior.md`.

## Headline

**Substantively 3/3 detection with near-perfect magnitude — the strict
score (0/3) is a field-filling artifact, not a perception failure.**
Truth: IP *termination (recovery)* table, Cancer diagnosis segment,
A/E ×0.5 across 2015–2024 (the whole table). Model, all 3 runs:
IP / recovery / decrease / conf 0.90–0.92, and quoted **Cancer
termination A/E = 0.496** — 0.8% off the injected ×0.5. Loose recall
3/3; strict lost **only** because the model returned `years: null`.

## Why strict=0/3 despite a perfect answer

- The effect is *omnipresent* (every year of the table). The prompt's
  schema says `"years": [start,end] | null` — null is legal for "no
  particular window". The model used it; the scorer's strict rule
  (score_xam.py: `overlap()` — "open-ended window does not count as a
  window hit") then can't pass. Arguably the model's read (constant
  effect, no window) is *more* accurate than a window claim would be.
- Benefit label: truth is diagnosis-level `["Cancer"]`; the model answered
  at table level (`IP`) with Cancer named explicitly in magnitude/evidence
  text. The scorer special-cases `IP == ip_recovery` so benefit matched
  (that's why loose=3/3).

## FP accounting — read carefully, rubric artifact

The FP=4 headline breaks down as:
- 3 × the recovery finding itself (counted FP because `matched_idx` only
  marks *strict* hits — the label-miss falls through to FP);
- 1 × genuinely extra: run 1's `Death 2016 / shock / increase`,
  A/E 1.163, "+47 claims, ~2.8σ", **confidence 0.35**. Same borderline
  year the model *correctly rejected* in the clean scenario (shared
  baseline data). Here it hedged instead of suppressing — low-confidence,
  statistically honest observation, not a fabrication.

Net hallucination count for this scenario: **0**.

## Behavioral observations

- Recovery signals are cheap to process: wall 354/514/702 s vs 900–1,600
  s on the trend/shock scenarios — the model locks onto a level shift
  immediately instead of oscillating over hypotheses.
- Run 1 quoted both segment (0.496) and aggregate (0.939) termination A/E
  — correctly noting the aggregate only moves −6% because Cancer is a
  small share of IP terminations. Exposure-weighted reasoning visible
  without prompting (consistent with the pooled-aggregation fix).
- 3/3 runs independently converged on identical structure and figures —
  no seed-to-seed wobbling on this scenario type.

## Numbers for the record

- Runs: 3/3 OK, finish_reason=stop, prompt 2,481 ×3 (statelessness),
  no tools, no code fences, leak gate clean.
- Wall: 354/514/702 s (6/8.5/12 min). Completion tokens: 5,650/7,412/
  10,928.
- Seeds 1234/1235/1236, canonical samplers, no max_tokens, stream=true.
- Suggested rubric follow-up (do NOT edit manifests): consider treating
  `years: null` as a window match when the control window spans the full
  observation period; otherwise recovery-family strict recall is
  systematically deflated.
