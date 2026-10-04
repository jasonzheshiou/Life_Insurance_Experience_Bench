# Reviewer notes — sc-4a7f9e (sys_shock_inverse_2021_2022, systemic)

> SCORER-SIDE — contains ground truth. Companion to `sc-4a7f9e_behavior.md`.

## Headline

Truth: mixed-direction systemic shock [2021,2022]: Death ×1.4 (increase),
CI ×0.6 (decrease). Model **3/3 strict** — BOTH sides every run: Death
shock/increase [2021,2022] conf 0.88–0.98 AND CI shock/decrease [2021,2022]
conf 0.95–0.98, magnitudes near-exact (Death A/E 1.296/1.282, CI 0.670/0.654,
z up to −14, claim shortfalls −457/−535). The model handled the
mixed-direction control flawlessly — the very case where the manifest's
single `signature.direction` ("decrease") would have mis-scored it
(handoff §6.2; scorer's per-factor comparison vindicated).

## Beyond the control — "exclusion diagnostics" (notable behavior)

Runs 2–3 added findings stating what the data looks like **excluding the
spike**: Death ≈0.91 aggregate (−0.09), CI ≈1.13 (+0.13) — i.e. the model
noticed the surrounding years sit below/above expected opposite to the
shock (the generator's rescaling side-effect) and reported it explicitly
as "other". This is sophisticated analyst behavior, but it inflates FP:

## FP accounting — matched_idx artifact (systemic, fix candidate)

FP=9 (=3/run). Per run: the second true-benefit finding (CI) counts FP
because the scorer matches only ONE finding per multi-benefit control
(`matched_idx`, score_xam.py) — +2/run across runs; plus one "other"
finding/run. In run 1 the extra two were explicit **"No material
anomaly"** statements for TPD/IP that the model filed inside `findings`
(the schema has nowhere else to put reassurance). So of 9 "FPs": 6 are the
model correctly re-detecting the control's other benefit, 3 are no-anomaly
notes / exclusion diagnostics. **Zero hallucinations.**
Fix candidates (deferred, documented, NOT applied mid-experiment): match
one finding per (control, benefit) tuple; exclude `pattern:"other"` with
"no material anomaly" text from FP; treat `years:null` as window match for
full-period controls (sc-17d82f notes).

## Numbers for the record

3/3 OK, finish=stop, prompt ~2,480 ×3, no tools, no code.
Wall 2,664/1,953/2,223 s; completion 38,627/25,579/28,364 tokens — the
longest-running scenario type (systemic + mixed direction).
Canonical settings, seeds 1234/1235/1236. Rerun note: first pass died in
the same orphaned-slot timeout episode as sc-48351f; rerun clean.
