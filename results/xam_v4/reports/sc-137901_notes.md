# Reviewer notes — sc-137901 (sys_trend_tpd_ip_2019_2023, systemic)

> SCORER-SIDE — contains ground truth. Companion to the auto-generated
> `sc-137901_behavior.md` (which is regenerated on each report run; this
> file is manual and permanent).

## Headline

Strict recall **0/6** (2 controls × 3 runs), FP 6, but this is a *near
miss on label*, not a detection failure. All 3 runs found **TPD and IP**
(the two controlled benefits) with the right **direction (increase)** and
the right **magnitude**; all 3 runs mislabeled the pattern.

## What the truth was

Two simultaneous bounded drifts, 2019→2023: TPD +0.05/yr, IP +0.04/yr.
Cumulative effect lands in the tail of the window: observed within-window
A/E slope fit = **+6.1%/yr (TPD)** and **+3.1%/yr (IP)** vs injected
+5 / +4 — i.e. the drift is statistically visible and roughly at strength.
Pre-window means: TPD 0.926, IP 0.947 → window means 1.056 / 1.048.

## What the model did (3/3 runs identical structure)

- Run 1: TPD+IP, "shock", years [2022,2023], +0.16–0.17 / +0.10–0.12 A/E,
  conf 0.88/0.86.
- Run 2: TPD+IP, **volatility/dispersion** (variability ~3× Poisson noise),
  conf 0.86/0.86.
- Run 3: TPD+IP, "shock", [2022,2023], +0.16 / +0.10–0.12 A/E,
  conf 0.91/0.90.

## Why it missed — smoking-gun reasoning evidence

The model **explicitly considered drift and rejected it**, naming nearly
the correct hypothesis (run 1, reasoning):

> "Maybe the generator injects a gradual trend in one line across all
> years: e.g. TPD/IP true A/E drift from 0.9 to 1.1. … This could be a
> drift. But …" (run 1: 50 mentions of "drift", 48k chars of reasoning)

Rejection argument (run 2):

> "Drift gradual; here abrupt 2022-23. Shock."

The deciding datum was **2024**: TPD 0.942, IP 0.927 — a sharp reversion
below baseline. Under a *persistent* drift 2024 should be highest year;
the control's window ending at 2023 is benchmark knowledge the model
cannot have. Given its assumptions the inference was rational: bounded
drift vs shock are only distinguishable at the boundary year, and the
boundary year points away from the truth.

Second factor: the model read raw yearly A/E (z per year) instead of
fitting a within-window trend; early-window years (2019–21) sit at
0.95–1.03 because the cumulative drift is still small, so "abrupt at
2022" is what the unsmoothed eye sees. Run 2 additionally counted 2016
(−2.75σ) and 2024 (−3.24σ) as evidence for volatility.

## Scoring note (rubric nuance, per handoff §6.3)

The 6 "FPs" are the *same real signal* mislabeled, not hallucinations.
No invented numbers: every figure quoted in evidence strings matches the
CSVs (checked: 1142/974/1.173 for TPD 2022 etc.). Benefits not mentioned
at all: Death, CI — correctly left alone.

## Difficulty read-out

First systemic/trend case in the pool. Pattern-name vocabulary is doing
hard work here: "drift" in this benchmark means *bounded* multiplicative
trend inside a window that snaps back after the window; a careful
statistician without the generator's manual reasonably reads that as
"shock, then recovery". Expect the same failure mode on other bounded
trend scenarios (sc-3c83fd, sc-9372cd, sc-f69eea, sc-da1123…).

## Numbers for the record

- Runs: 3/3 OK, finish_reason=stop, no errors, leak gate clean, stateless.
- Wall: 1022s / 1653s / 1245s (17/27.5/21 min). Completion tokens:
  17,389 / 25,889 / 20,304 (94–97% reasoning_content). Prompt 2,460 tokens
  identical across runs.
- Seeds 1234/1235/1236, samplers as canonical, no max_tokens, stream=true.
