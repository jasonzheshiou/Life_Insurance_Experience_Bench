# Reviewer notes — sc-6e2478 (volatility_death_sigma_02, volatility)

> SCORER-SIDE — ground truth. Companion to `sc-6e2478_behavior.md`.

## Headline
Truth: Death volatility σ=0.2, 2015–2024. Valid runs **2/2 strict**
(run2: Death/volatility/dispersion [2016,2024] c0.90; run3: [2015,2024]
c0.78; FP=0). Score shows 2/3 with badjson=1 because **run1 was an EMPTY
GENERATION** — a new runner-level failure mode (below). Effective
detection on valid samples: 100%.

## New failure mode: silent empty completion
`sc-6e2478_run01.json` (rerun, 08:50–10:32 window): stream completed with
`attempts_ok=1`, no error, wall 270 s, but **content 0 chars,
finish_reason null, usage empty**. The SSE stream closed without any
delta — runner recorded success-with-nothing. Consequence: `--skip-existing`
does NOT protect against this pattern being counted as "attempted" by the
chain's ok-status (run_zero_shot counts a call OK if no exception), so the
chain declared rerun_ok while a stub survived. Follow-up (deferred): runner
should treat empty-content-no-error as a failed call (retryable). To
regenerate this single run later: delete the stub file, re-run the wrapper
(only the missing/stub run is spent).

## Notes
- The weaker run3 window (c0.78, but correct) and run2 offset start year
  show σ=0.2 is near the model's materiality threshold — it still
  diagnosed dispersion correctly, just with less conviction than σ=0.3
  (sc-2d248f, c0.95–0.97) or σ=0.35 (sc-8a9fa1, c0.88–0.95).
- Wall (valid runs): 606/513 s; completion 9,373/9,311. Canonical settings.
