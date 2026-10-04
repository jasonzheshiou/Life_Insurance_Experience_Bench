# Reviewer notes — sc-8a9fa1 (trap_noise_drift_lookalike, noise_trap)

> SCORER-SIDE — ground truth. Companion to `sc-8a9fa1_behavior.md`.

## Headline
Truth per manifest: a REAL control exists — Death volatility σ=0.35
[2016,2020] — the "trap" being that surrounding noise makes the look
drift-like. Model **3/3 strict**: Death/volatility/dispersion, conf
0.88–0.95, every run. It did NOT take the drift bait (never said
drift/level-change), correctly named dispersion, and its [2015,2024]
window overlaps the truth window (strict passes; the extra 4 years are
the noise the trap injected). FP=3: run3's three "other/dispersion — no
material anomaly" reassurance notes on CI/TPD/IP.

## Trap-honesty read
This is a pass on the trap dimension: the model separated the real
elevated-variance signal (Death) from the decoy noise (other lines stayed
clean or got explicit no-anomaly notes). Compare sc-14cdd9 (clean→clean):
the model resists hallucinating on noise in both directions.

## Numbers
3/3 OK, finish=stop. Wall 563/818/676 s; completion 10,209/14,405/12,150.
Canonical settings, seeds 1234/1235/1236.
