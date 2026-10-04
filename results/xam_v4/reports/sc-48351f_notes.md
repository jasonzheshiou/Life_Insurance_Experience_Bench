# Reviewer notes — sc-48351f (shock_tpd_ip_2023, shock)

> SCORER-SIDE — contains ground truth. Companion to `sc-48351f_behavior.md`.

## Headline

Truth: one control, two benefits — TPD ×1.3 and IP ×1.2, single year 2023.
Model **3/3 perfect**: TPD and IP, years [2023,2023], shock/increase,
conf 0.92–0.95, magnitudes to the claim (TPD 1,299 vs 1,052 = A/E 1.235,
z≈7.6; IP 2,208 vs 1,876 = 1.177, z≈7.7 — all tie to CSVs). Strict 3/3.
Cleanest multi-benefit catch in the pool.

## Sweep incident — this scenario twice; resolution + correction

First attempt (sweep pass 1): run1's HTTP stream died at 296 s; runs 2–3
then hit `wait-for-endpoint expired` (1,800 s). **Correction to the
contemporaneous reading ("server down"): the server was not down — it was
still generating orphaned work from the broken stream on its single slot,
so new requests could not start.** User correctly flagged this
("says request timeout but in reality it is still running"). Implication:
`wait-for-endpoint expired` means *slot unavailable*, not *server dead*;
the runner's 1,800 s wait gave up earlier than the orphan needed to drain.
Rerun (22:43 UTC) via `--skip-existing`: only empty/error stubs re-spent,
3/3 OK, 0 failed calls.

## FP accounting (artifact, see sc-4a7f9e notes)

FP=4 headline: the control has benefit `["TPD","IP"]` but the scorer marks
only ONE finding per control as matched — the model's (correct!) IP finding
was scored FP in every run (+1×3), plus run 2's low-confidence (0.55)
note on Injury/Accident pooled termination A/E 0.955 (+1). True
hallucinations: 0.

## Numbers for the record

3/3 OK, finish=stop, prompt ~2,480 ×3, no tools, no code.
Wall 1,227/1,146/1,072 s; completion 19,502/13,442/14,986 tokens.
Canonical settings, seeds 1234/1235/1236.
