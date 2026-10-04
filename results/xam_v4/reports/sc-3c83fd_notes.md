# Reviewer notes — sc-3c83fd (drift_ci_down_2016_2019, drift)

> SCORER-SIDE — contains ground truth. Companion to `sc-3c83fd_behavior.md`.

## Headline

Truth: CI drift **−0.10/yr**, bounded window 2016–2019 (cumulative ≈ −30%;
observed A/E 0.927→0.808→0.731 by 2019, then post-window return to
1.05–1.10 in 2020–2024). Model: **strict 0/3, loose 0/3 — second genuine
drift-family miss** (same failure mode as sc-137901). It found the right
benefit (CI, 3/3) and the right low region (2017–2019, 3/3, with exact
figures), but labeled the pattern **volatility/dispersion** (runs 1,3) or
**shock/dispersion** (run 2) — never "drift".

## Why it missed — same bounded-drift ambiguity, amplified here

The windowed drift creates a V: years fall below expected through 2019,
then stand *above* expected after it. Because baseline A/E ≈0.95-ish,
post-window years read 1.05–1.10, so the whole series looks like a big
two-sided swing rather than a one-sided bounded decline. All 3 runs
described exactly that ("low 2017–2019 offset by 2020–2024 excess", sd
0.13 vs Poisson 0.03). Under "drift = persistent trend" semantics, the
reversion disqualifies drift — the model's inference is rational given
the benchmark's unstated boundedness (see sc-137901 notes; this is now a
pattern across ALL drift-family scenarios attempted so far: 0/9 control
runs detected as drift).

Note the model DID capture the drift's footprint: run 2 explicitly quoted
the monotone descent 0.927/0.808/0.731 — the shape of the injected trend —
and quantified the −540-claim shortfall; it just filed it under dispersion.

## FP accounting

FP=3: one per run, and each "FP" is the finding *itself* (pattern label
mismatch → falls through to FP). Zero hallucinated content; no other
benefit lines flagged (Death 2016 blip not mentioned this time).

## Numbers for the record

3/3 OK, finish=stop, prompt 2,476 ×3, no tools, no code.
Wall 1,124/680/1,673 s; completion 18,698/12,109/26,384 tokens.
Canonical settings, seeds 1234/1235/1236.
