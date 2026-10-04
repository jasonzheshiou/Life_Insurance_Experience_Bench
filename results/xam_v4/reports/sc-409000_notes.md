# Reviewer notes — sc-409000 (ip_recovery_mental_health_x2, recovery)

> SCORER-SIDE — contains ground truth. Companion to `sc-409000_behavior.md`.

## Headline

Truth: IP termination (recovery) table, Mental Health segment, A/E ×2.0,
2015–2024. Model 3/3: IP / recovery / increase, Mental Health termination
A/E = **1.990 vs ×2.0 injected** (0.5% error), aggregate 1.237 quoted with
correct share-explanation, conf 0.95. Second consecutive magnitude-perfect
recovery catch (after sc-17d82f). Strict 1/3 — run 3 volunteered
`years:[2015,2024]` and passed; runs 1–2 used the schema-legal `null` for
a whole-period effect and strict window-overlap failed them (same artifact
as sc-17d82f — see proposed rule there).

## Observations

- Runs got progressively shorter (397→273→217 s) and leaner
  (7,167→5,192→4,072 tokens) — seed 1236 reached the same verdict with
  43% less deliberation than seed 1234; verdict identical throughout.
- FP=2 are the two `years:null` findings themselves (rubric fall-through),
  not invented content. Zero hallucinations.
- Cumulative across both recovery scenarios: 2/2 segment A/E quoted within
  1% of injected factor (0.496 vs 0.5; 1.990 vs 2.0) — termination-table
  reading is this model's strongest skill in the pool.

## Numbers for the record

3/3 OK, finish=stop, prompt 2,481 ×3, no tools, no code.
Wall 397/273/217 s; completion 7,167/5,192/4,072 tokens.
Canonical settings, seeds 1234/1235/1236.
