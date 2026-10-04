# Reviewer notes — sc-5e376b (shock_covid_2020_2022, shock)

> SCORER-SIDE — ground truth. Companion to `sc-5e376b_behavior.md`.

## Headline
Truth: Death ×1.5, [2020,2022]. Model **3/3 strict** — Death/shock/
increase/[2020,2022], conf 0.97–0.98, every run. Cleanest catch since the
pooled-termination fix (the "covid" shock is the biggest signal in the
pool so far). FP=2 are exclusion diagnostics: runs 1&3 also noted Death
"other/decrease" for the surrounding years (0.85 conf) — the rescaling
side-effect opposite the shock, real and correctly labeled "other".

## Sweep history
This scenario was the crash witness: its run1 stream was severed at
~04:52 UTC when the llama.cpp process died (see batch-2 sweep notes /
handoff §7 incident). Rerun 08:50 produced the valid 3/3 above.
Wall 874/605/715 s; completion 14,482/10,191/12,770. 3/3 finish=stop,
prompt identical ×3, no tools/code.
