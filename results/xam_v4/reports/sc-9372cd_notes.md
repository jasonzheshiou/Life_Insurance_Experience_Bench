# Reviewer notes — sc-9372cd (drift_tpd_up_2019_2021, drift)

> SCORER-SIDE — ground truth. Companion to `sc-9372cd_behavior.md`.

## Headline
Truth: TPD drift +0.08/yr, BOUNDED window [2019,2021] (cumulative ≈+26%
by 2021, then flat/reverts). Model **0/3 strict, 0/3 loose — third
bounded-drift miss**, 100% consistent: all 3 runs said
TPD/**shock**/increase/**[2021,2021]** (c0.85–0.95), i.e. it pinpointed
the peak year of the ramp and filed the whole drift as a one-year spike.
Right line, right direction, wrong pattern AND wrong window — window
still overlaps the truth so direction/pattern are what fail it.

## The pattern across the pool now (drift family, n=5 controls)
| scenario | drift shape | labeled drift? |
|---|---|---|
| sc-137901 | bounded 2019-23 (snap-back 2024) | never |
| sc-3c83fd  | bounded 2016-19 (overshoot after)   | never |
| sc-9372cd  | bounded 2019-21 (flat after)        | never |
| sc-63f1c7  | open-ended 2019-24                  | **3/3** |
| sc-8d3b47  | open-ended 2018-24 ×2               | **3/3** |

Zero-for-one on bounded drifts, 6-for-6 on open-ended ones. The model's
implicit definition of "drift" requires persistence to the horizon; a
trend that stops is read as a shock at its endpoint. This is a rational
semantic choice, not a perception error — the generator's bounded
windows are unknowable from the data.

## Numbers
3/3 OK, finish=stop. Wall 1,735/1,294/1,113 s; completion
7,634/8,443/18,816 (run1 ran 29 min of reasoning for a 7.6k-token answer
— heavy deliberation ending in the wrong label; worth a reasoning-trace
read in Tier 3 of the dossier). Canonical settings, seeds 1234/1235/1236.
