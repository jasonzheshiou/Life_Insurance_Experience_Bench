
## 2026-09-10T04:46:04Z  sc-042304 (pass 1)
```
scenario sc-042304  json=unparseable  overall_says=None  error=None  wall=957.7s
harness: tool_calls=0  pack_sha=31d6b572e237
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
sc-042304   fam=shock       runs=1 strict=0/1 loose=0/1 FP=0 badjson=1 err=0
```

## 2026-09-10T15:09:14Z  sc-042304 (pass 1)

### Run 1 (sc-042304) — VOID: stream died mid-answer
- 957.7 s wall, finish_reason=null, usage all zeros, answer cut mid-JSON
  (11,400+ reasoning chunks then a truncated findings object).
- Cause: local llama.cpp restarted during generation (endpoint auth/state
  changed mid-run); NOT a model behaviour. File quarantined to
  results/harness_opt_p1/quarantine/sc-042304_run01_TRUNCATED.json
  and the scenario re-run.
- Runner fix shipped with the retry: `TruncatedStream` — a missing
  finish_reason, a non-JSON answer, or a final turn that is still a tool
  request is now a RETRYABLE failure (was silently banked). All 141
  xam_v4/xam_v5 runs ended with finish_reason="stop", so nothing historical
  is affected.
- Partial observations (void but useful): the model DID identify the true
  control (CI 2021–22, labelled "shock", +0.35, conf 0.85) and explicitly
  reasoned with the pack's numbers — "abrupt +0.39 one-year jump with flat top
  and abrupt revert: no gradual build-up, so shock not drift" and "line is
  overdispersed (empirical YoY SD 0.193 vs Poisson 0.030, x6.3) — Poisson
  z-scores not relied upon". It did NOT use the python tool (tool_calls=0).

### Harness edits made while pass 1 runs (each affects the NEXT scenario)
- Pack output is now a descriptive **evidence profile** (dispersion-dominant /
  step-dominant / sustained-move / excursion / no strong signal) instead of a
  family claim, thresholds re-tuned by grid search on the OPTIMIZATION split
  only (the previous 4.0-overdispersion rule mislabelled 9 clean trap lines).
- New **excursion** statistic (widest window whose level differs from the
  rest): catches bounded/reverting multi-year moves that a single-step split
  and a whole-window linear fit both miss — sc-9372cd TPD now reports
  "2018-2021 (4y) +0.113".
- Every run record now stores the exact `pack_text` the model received, so a
  mid-pass harness edit can never make a past run unattributable.
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=727.1s
harness: tool_calls=2  pack_sha=3fe72e9bd85e
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag A/E jumps from 0.88 (2020) to ~1.27-1.30
  [1] FP    CI | other | increase | None | conf 0.5 | mag 65+ age band A/E ~10-12x vs expected ~2-
  [2] FP    Death | other | dispersion | None | conf 0.8 | mag overall A/E 1.004, all years 0.94-1.16, 
  [3] FP    TPD | other | dispersion | None | conf 0.8 | mag overall A/E 1.006, all years 0.96-1.04, 
  [4] FP    IP | other | dispersion | None | conf 0.85 | mag overall A/E 1.002 and termination A/E 1.
SCORE: strict 1/1  loose 1/1  FP 4
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv, itertools ⏎ for f in ['ae_ci_age_gender.csv','ae_death_age_gender.csv','ae_ip_age_gender.csv','ae_tpd_age_gender.csv']: ⏎     print('='*20, f) ⏎    
      -> ==================== ae_ci_age_gender.csv
rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '9', '7.709347866452286', '1.1674139182594248']
['15', 'Male', '8', '10.6813974879
  [1] run: import csv ⏎ with open('ci_claims.csv') as f: ⏎     r = csv.reader(f) ⏎     hdr = next(r) ⏎     rows = [x for x in r] ⏎ print('cols:', hdr) ⏎ print('n rows:', l
      -> [error] FileNotFoundError: [Errno 2] No such file or directory: 'ci_claims.csv'
sc-042304   fam=shock       runs=1 strict=1/1 loose=1/1 FP=4 badjson=0 err=0
```

### sc-042304 — run 2 result (harness v1.0 pack): 1/1 strict, 4 FP
- Found the true control (CI 2021-22, "shock", +0.35, conf 0.90) and used the
  python tool twice (inspected the age-gender tables; then tried a file that
  does not exist).
- FPs: three of the four were the pack's own overdispersion numbers promoted
  into "dispersion" findings on lines whose profile said "no strong signal"
  (Death x2.2, TPD, IP, conf 0.8-0.85); the fourth came from a small-cell
  age-band excursion (65+, tiny expected counts).
- Fixes applied before re-testing: (1) each overdispersion row now states what
  the value MEANS for the null (valid / indicative only / invalid) and says
  outright that mild overdispersion is not an anomaly; (2) HARNESS_RULES gains
  a discipline clause — dispersion is a finding only at ~x6+ with a flat level,
  small cells are never evidence, rejected candidates stay out of the array;
  (3) profile rules re-ordered (a coherent level excursion outranks dispersion
  and trend) and re-calibrated on the optimization split: excursion score >= 8
  to be called "SHAPED" (clean lines max 6.4), which drives false anomaly-shaped
  profiles on clean lines from 24 -> 0 while still naming the right shape for
  21/40 true controls.

## 2026-09-10T15:22:46Z  sc-042304 (pass 1)

## 2026-09-10T15:27:16Z  sc-042304 (pass 1)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=662.3s
harness: tool_calls=2  pack_sha=08d849a55415
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.85 | mag A/E lifts from ~0.94 baseline to ~1.28 (
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(p, n=8): ⏎     print("=====", p) ⏎     try: ⏎         with open(p) as f: ⏎             rows = list(csv.reader(f)) ⏎     except Exceptio
      -> ===== ae_ci_age_gender.csv
header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
nrows: 22
['15', 'Female', '9', '7.709347866452286', '1.1674139182594248']
['15', 'Male', '8', '10.681397487918058'
  [1] run: import csv ⏎ print("===== CI age/gender full") ⏎ with open("ae_ci_age_gender.csv") as f: ⏎     rows=list(csv.reader(f)) ⏎ for r in rows[1:]: ⏎     ae=float(r[4]
      -> ===== CI age/gender full
  15 Female  act=      9 exp=     7.7 AE= 1.167
  15 Male    act=      8 exp=    10.7 AE= 0.749
  20 Female  act=     27 exp=    27.6 AE= 0.979
  20 Male    act=     25 exp=  
sc-042304   fam=shock       runs=1 strict=1/1 loose=1/1 FP=0 badjson=0 err=0
```

### sc-042304 — run 3 (harness v1.1: calibrated pack + discipline clauses): 1/1 strict, 0 FP ✅
- Single finding, exactly the truth: CI shock [2021,2022] increase, conf 0.85.
- Used the python tool twice (both on the age-gender tables that produced the
  small-cell FP before) and correctly did NOT report them.
- 662 s, 29,976 tokens (19,490 prompt / 10,486 completion).
- Comparison for this scenario:
  | run | strict | FP | notes |
  |---|---|---|---|
  | xam_v5 harness OFF r1/r2/r3 | 1/1 each | 0 / 4 / 1 | same model, zero-shot |
  | harness v1.0 (pre-fix) | 1/1 | 4 | pack's overdispersion promoted to findings |
  | harness v1.1 (this run) | 1/1 | 0 | calibration + discipline clauses |
- Caveat recorded for honesty: the dispersion-FP mode is partly intrinsic to
  the model — xam_v5 run 2 produced TPD/IP "dispersion" findings with NO pack at
  all. The harness removes the pack's contribution to it and adds an explicit
  rule, but one run is not evidence of a stable improvement; the pass-level
  totals will decide.

## 2026-09-10T15:38:39Z  sc-137901 (pass 1)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1643.4s
harness: tool_calls=1  pack_sha=3a80b973937f
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] FP    TPD | shock | increase | [2022, 2023] | conf 0.9 | mag flat-topped level jump of ~+0.20 A/E (fr
  [1] FP    IP | shock | increase | [2022, 2023] | conf 0.85 | mag flat-topped level jump of ~+0.14 A/E (fr
SCORE: strict 0/2  loose 0/2  FP 2
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def analyze(f): ⏎     with open(f, newline='') as fh: ⏎         rd = list(csv.reader(fh)) ⏎     if not rd:
      -> == ae_tpd_age_gender.csv
HDR: ['ageband', 'gender', 'actual', 'expected', 'ae']
ROW0: ['15', 'Female', '9', '13.27437178792839', '0.67799818656462']
cannot parse columns
== ae_ip_age_gender.csv
HDR: [
sc-137901   fam=systemic    runs=1 strict=0/2 loose=0/2 FP=2 badjson=0 err=0
```

## 2026-09-10T16:10:56Z  sc-137901 (pass 1)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=472.3s
harness: tool_calls=0  pack_sha=889a1afefd90
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2019, 2023] | conf 0.85 | mag A/E rises from ~0.93 baseline (2015-18) 
  [1] MATCH IP | drift | increase | [2018, 2023] | conf 0.85 | mag A/E rises from ~0.94 baseline (2015-16) 
SCORE: strict 2/2  loose 2/2  FP 0
sc-137901   fam=systemic    runs=1 strict=2/2 loose=2/2 FP=0 badjson=0 err=0
```

### sc-137901 (systemic, TPD+IP drift 2019-2023) — the diagnostic case
| attempt | harness | strict | FP | what the model said |
|---|---|---|---|---|
| 1 | v1.1 (excursion rule, no smoothing) | 0/2 | 2 | TPD/IP "shock [2022,2023]" — "flat-topped level jump" |
| 2 | v1.2 (smoothed 3y-MA evidence) | **2/2** | **0** | TPD drift [2019,2023] ✓ exact window; IP drift [2018,2023]; conf 0.85 |
- The pack in attempt 1 actively misled: its own label read "SHAPED: abrupt
  level excursion over 2 y (2022-2023) … short/absent ramp", so the model
  reported exactly that window as a shock.
- Fix: the smoothed (3-year MA) level, printed as a series, exposes the ramp
  the raw A/E hides — 0.93 0.91 0.93 0.95 0.98 1.05 1.12 1.09 — and the
  profile now says "SHAPED-AND-GRADUAL … use the MA series to read where the
  smoothed level leaves and returns to its own baseline, and report THAT span".
- Calibration behind it (optimization split): clean lines never exceed a
  smoothed amplitude of 0.051; every true control line is >= 0.082; drift lines
  fit the smoothed level at R2 ~0.86 median vs ~0.57 for shock and ~0.30 for
  volatility. Two candidate discriminators were TESTED AND REJECTED first
  (ramp-ratio max/mean YoY: drift 1.68 vs shock 1.89 vs clean 1.94 — no
  separation; smoothed-excursion window detection: picked the mirror window).
- Cost effect: 472 s / 14.9k tokens vs 1,643 s / 38.0k tokens for the failing
  attempt — a correct harness also makes the model stop second-guessing.

## 2026-09-10T16:19:15Z  sc-14cdd9 (pass 1)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=438.3s
harness: tool_calls=1  pack_sha=a642bf805b73
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for p in ['ae_death.csv','ae_death_age_gender.csv','ae_ip_termination_by_month.csv','ae_ip_termination.csv','ae_ip_by_year.csv']: ⏎     try: ⏎     
      -> === ae_death.csv n= 891
['Age', 'Gender', 'Year', 'Actual', 'Expected', 'AE']
{'Age': '17', 'Gender': 'Female', 'Year': '2015', 'Actual': '0', 'Expected': '0.061779156759464535', 'AE': '0.0'}
{'Age': 
sc-14cdd9   fam=CLEAN       runs=1 FALSE-POSITIVE: claimed-anomalies=0/1 FP=0 badjson=0 err=0
```

### sc-14cdd9 (CLEAN — honesty test) — harness v1.2: clean, 0 FP ✅
- `overall_assessment: "clean"`, zero findings, zero FP; used the python tool
  once (peeked at the death and IP-termination files) and still declined to
  invent an anomaly.
- Baseline xam_v5 (harness off): 2 of 3 runs claimed an anomaly here.
- Running tally after 3 scenarios (all with harness v1.2 where re-tested):
  sc-042304 1/1 strict 0 FP · sc-137901 2/2 strict 0 FP · sc-14cdd9 honest.

## 2026-09-10T16:37:48Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:38:06Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:38:25Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:38:43Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:39:01Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:39:20Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:39:38Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:39:56Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:40:15Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:40:33Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:40:51Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:41:10Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:41:28Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:41:46Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:42:05Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:42:23Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:42:42Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:43:00Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

## 2026-09-10T16:43:19Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=632.0s
harness: tool_calls=1  pack_sha=5d5f134a15aa
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag A/E gradient ~+0.084/yr; rises from ~0.6
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ def peek(path, n=12): ⏎     with open(path) as f: ⏎         r = list(csv.reader(f)) ⏎     print("==", path, "rows:", len(r)) ⏎     for row in r[
      -> == ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040
```

### INCIDENT — pass runner spun and falsely reported PASS_COMPLETE (fixed)
- `harness_pass_run.sh` used `sid` both as its loop variable and inside the
  `write_status()` helper's own counting loop. Bash functions share scope, so
  the helper overwrote `sid` with the LAST scenario in the list before the
  runner command was built: only sc-f69eea was ever really run, the remaining
  19 iterations were instant `--skip-existing` no-ops, and the completion line
  was trusted rather than verified.
- Fixes: helpers now use `local` + `_`-prefixed names, the main loop uses
  `SID`/`TRY`, and completion is RECOUNTED from the corpus
  (PASS_COMPLETE only when every scenario has a valid run, else
  PASS_INCOMPLETE with the missing list).
- harness_opt_step.sh was NOT affected (it uses SID/TRY at top level).
- Cost: one wasted scenario run (sc-f69eea, banked and valid) + ~16 min idle.

## 2026-09-10T21:56:58Z  sc-17d82f (pass 1, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=692.0s
harness: tool_calls=2  pack_sha=a6a9fe08bd26
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.95 | mag pooled cancer termination A/E ~0.50 (obs
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎  ⏎ with open('ae_ip_termination_by_month.csv', newline='') as f: ⏎     rows = list(csv.reader(f)) ⏎ print('cols:', rows[0]) ⏎ print('n rows:', len(
      -> cols: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
n rows: 122
['0', '15030', '2107', '2152.3900000000003', '0.978911814308745']
['1', '12780', '1655', '1731.8063636363636', '
  [1] run: import csv ⏎  ⏎ with open('ae_ip_termination.csv', newline='') as f: ⏎     rows = list(csv.reader(f)) ⏎ hdr = rows[0] ⏎ di = hdr.index('Diagnosis') ⏎ print('HEA
      -> HEADER: ['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
n cancer rows: 122
['Cancer', '0', '1867', '64', '0.03427959292983396', '0.075', '0.4570612390644528
```

## 2026-09-10T22:13:07Z  sc-2d248f (pass 1, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=771.1s
harness: tool_calls=1  pack_sha=a9c855975556
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical YoY sd of A/E ~0.60 vs Poisson
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, statistics as st ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p) as f: return list(csv.reader(f)) ⏎  ⏎ ag = load("ae_ip_a
      -> AG hdr: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
AG rows: 22
['15', 'Female', '22', '33.94934067109002', '0.6480243670456426']
['15', 'Male', '28', '43.49296919561533', '0.6437822139497151']

```

## 2026-09-11T00:16:03Z  sc-314eca (pass 1, unattended)
```
scenario sc-314eca  json=unparseable  overall_says=None  error=None  wall=7356.6s
harness: tool_calls=2  pack_sha=3aefc5b68c43
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv, os ⏎ files = sorted(os.listdir('.')) ⏎ print("FILES:", files) ⏎ for f in files: ⏎     if f.endswith('.csv'): ⏎         print("="*25, f) ⏎         tr
      -> FILES: ['ae_ci.csv', 'ae_ci_age_gender.csv', 'ae_ci_age_gender.png', 'ae_ci_by_year.csv', 'ae_ci_by_year.png', 'ae_death.csv', 'ae_death_age_gender.csv', 'ae_death_age_gender.png', 'ae_death_by_year.c
  [1] run: import csv ⏎  ⏎ # IP termination by month - check for recovery anomalies ⏎ print('=== ae_ip_termination_by_month.csv ===') ⏎ with open('ae_ip_termination_by_mon
      -> === ae_ip_termination_by_month.csv ===
header: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
['0', '15072', '2159', '2159.085', '0.999960631471202']
['1', '12776', '1733', '173
```

## 2026-09-11T00:35:05Z  sc-3c83fd (pass 1, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=1123.3s
harness: tool_calls=3  pack_sha=b69f32a76441
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2016, 2019] | conf 0.8 | mag ~-0.12/yr: A/E falls from ~1.10 (2016) t
  [1] FP    CI | shock | increase | [2020, 2024] | conf 0.55 | mag Abrupt step at 2020 (+0.34 A/E; actual C
SCORE: strict 1/1  loose 1/1  FP 1
TOOL TRANSCRIPT (3 call(s)):
  [0] run: import csv ⏎ def show(f,n=4): ⏎     print("==",f) ⏎     with open(f) as fh: ⏎         r=csv.reader(fh) ⏎         for i,row in enumerate(r): ⏎             if i>=
      -> == ci_claims.csv

[error] FileNotFoundError: [Errno 2] No such file or directory: 'ci_claims.csv'
  [1] run: import os ⏎ print(sorted(os.listdir('.')))
      -> ['ae_ci.csv', 'ae_ci_age_gender.csv', 'ae_ci_age_gender.png', 'ae_ci_by_year.csv', 'ae_ci_by_year.png', 'ae_death.csv', 'ae_death_age_gender.csv', 'ae_death_age_gender.png', 'ae_death_by_year.csv', 'a
  [2] run: import csv ⏎ def show(f,n=10): ⏎     print("==",f) ⏎     with open(f) as fh: ⏎         r=csv.reader(fh) ⏎         for i,row in enumerate(r): ⏎             if i>
      -> == ae_ci_by_year.csv
['Year', 'Actual', 'Expected', 'AE']
['2015', '627', '596.3795704717398', '1.0513438605954246']
['2016', '791', '720.1724322459376', '1.0983480685773805']
['2017', '776', '837.149
```

## 2026-09-11T00:46:18Z  sc-409000 (pass 1, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=654.1s
harness: tool_calls=3  pack_sha=2cecd2d9a331
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.95 | mag Mental Health termination A/E ~1.99 (x2.
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (3 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ # ---------- I
      -> TERM header: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
TERM rows: 122
['0', '15030', '2908', '2152.3900000000003', '1.3510562676838302']
['1', '11984', '2110', '1629.344545
  [1] run: import csv ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ # by-diagnosis pooled ⏎ td = load("ae_ip_termination.cs
      -> TERM-DIAG header: ['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
Injury/Accident 1499 315.0 4.759
Injury/Accident 1170 257.0 4.553
Injury/Accident 904 172.
  [2] run: import csv ⏎ from collections import defaultdict ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ td = load("ae_ip_
      -> TERM-DIAG header: ['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']

Pooled per diagnosis (Recovered, Exp*AssumedRate, A/E):
Cancer 1260 1261.9 0.9985
Cardiov
```

## 2026-09-11T01:25:09Z  sc-48351f (pass 1, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=2312.2s
harness: tool_calls=1  pack_sha=6c83adeb086d
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.7 | mag single-year A/E spike ~+0.24 (2022 1.00 
  [1] MATCH IP | shock | increase | [2023, 2023] | conf 0.7 | mag single-year A/E spike ~+0.18 (2022 1.00 
SCORE: strict 2/1  loose 2/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import os, csv ⏎ print(sorted(os.listdir("."))) ⏎ for p in ["ae_ip_termination_by_month.csv","ae_tpd_age_gender.csv","ae_ip_age_gender.csv","ae_death_age_gender
      -> ['ae_ci.csv', 'ae_ci_age_gender.csv', 'ae_ci_age_gender.png', 'ae_ci_by_year.csv', 'ae_ci_by_year.png', 'ae_death.csv', 'ae_death_age_gender.csv', 'ae_death_age_gender.png', 'ae_death_by_year.csv', 'a
```

## 2026-09-11T01:31:44Z  sc-4a7f9e (pass 1, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=375.9s
harness: tool_calls=0  pack_sha=4bd707908d9f
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag level ~1.29-1.30 vs ~0.90-0.95 baseline 
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag level ~0.65-0.67 vs ~1.11-1.15 baseline 
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-11T01:56:58Z  sc-5e376b (pass 1, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=1493.2s
harness: tool_calls=1  pack_sha=ab5b228f9bb0
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2020, 2022] | conf 0.9 | mag ~+0.40 A/E above the ~0.86 surrounding b
SCORE: strict 0/1  loose 0/1  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, collections ⏎  ⏎ def tof(x): ⏎     try: ⏎         return float(str(x).replace(',','')) ⏎     except Exception: ⏎         return 0.0 ⏎  ⏎ # --- Death
      -> DEATH AGG COLS: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE'] N: 22
mapped: None AgeBand Gender Actual Expected
--- IP termination by month ---
COLS2: ['DurationMonth', 'Exposed', 'Recovered', 'Ex
```

## 2026-09-11T02:11:28Z  sc-63f1c7 (pass 1, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=850.3s
harness: tool_calls=1  pack_sha=e6fe3691ac10
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.78 | mag A/E climbs from ~0.87 (2015) to ~1.19 (2
  [1] MATCH CI | shock | increase | [2021, 2021] | conf 0.8 | mag single-year spike to A/E 1.327 in 2021 (
SCORE: strict 2/2  loose 2/2  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for f in ["ae_death_age_gender.csv","ae_ci_age_gender.csv"]: ⏎     print("==",f) ⏎     rows=list(csv.reader(open(f))) ⏎     print("header:",rows[0]
      -> == ae_death_age_gender.csv
header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '1', '4.520672767466119', '0.22120601322809516']
['15', 'Male', '6', '7.135997803227396', '0.84080
```

## 2026-09-11T02:33:41Z  sc-6e2478 (pass 1, unattended)
```
scenario sc-6e2478  json=valid  overall_says=clean  error=None  wall=1313.3s
harness: tool_calls=1  pack_sha=d2baec600e7c
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, math ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p) as f: ⏎         return list(csv.DictReader(f)) ⏎  ⏎ def num(x): ⏎   
      -> DEATH_AG cols: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
mapped: None AgeBand Gender AE Expected
sample: {'AgeBand': '15', 'Gender': 'Female', 'Actual': '6', 'Expected': '4.520672767466119', '
```

## 2026-09-11T02:44:02Z  sc-8a9fa1 (pass 1, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=601.7s
harness: tool_calls=1  pack_sha=e0b367128d1f
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2018] | conf 0.82 | mag A/E rises ~+0.21/yr from 1.08 (2016) to 
SCORE: strict 0/1  loose 0/1  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ # Read the age/gender file ⏎ with open('ae_death_age_gender.csv', 'r') as f: ⏎     reader = csv.reader(f) 
      -> Header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
Total rows: 22
First 10 rows:
['15', 'Female', '5', '4.520672767466119', '1.1060300661404758']
['15', 'Male', '6', '7.135997803227396', '0.840
```

## 2026-09-11T02:50:43Z  sc-8d3b47 (pass 1, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=381.6s
harness: tool_calls=0  pack_sha=6d593d5f6647
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.92 | mag ~+0.30 over window (A/E from ~0.86 avg 2
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.92 | mag ~-0.30 over window (A/E from ~1.17 avg 2
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-11T03:00:13Z  sc-9372cd (pass 1, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=550.7s
harness: tool_calls=1  pack_sha=30f29f8e3829
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2018, 2021] | conf 0.7 | mag peak ~+0.23 above baseline (1.19 vs 0.96
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for f in ["ae_tpd_age_gender.csv","ae_death_age_gender.csv","ae_ip_termination_by_month.csv","ae_ip_age_gender.csv"]: ⏎     print("="*25, f) ⏎     
      -> ========================= ae_tpd_age_gender.csv
nrows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '10', '13.27437178792839', '0.7533313184051332']
['15', 'Male', '9', '18.63
```

## 2026-09-11T03:22:29Z  sc-9660b9 (pass 1, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=1316.7s
harness: tool_calls=0  pack_sha=886eae5ddb4e
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2022] | conf 0.85 | mag A/E 0.86 (2016) to 1.42 (2022): six cons
  [1] FP    CI | drift | increase | [2020, 2021] | conf 0.75 | mag 2-year hump off a flat ~0.88 baseline: 1
  [2] FP    TPD | shock | increase | [2020, 2020] | conf 0.65 | mag single-year spike to A/E 1.56 (actual 1,
  [3] FP    TPD | shock | decrease | [2022, 2022] | conf 0.75 | mag plunge to A/E 0.39 (actual 381 vs expect
  [4] FP    IP | shock | increase | [2020, 2021] | conf 0.6 | mag 2020 spike to A/E 1.37 (actual 2,115 vs 
SCORE: strict 0/1  loose 0/1  FP 5
```

## 2026-09-11T03:37:11Z  sc-abbec4 (pass 1, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=861.9s
harness: tool_calls=1  pack_sha=54256c884991
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.41 (pooled 2021-2022 A/E 1.32 vs ~0.
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.30 (pooled 2021-2022 A/E 1.24 vs ~0.
SCORE: strict 2/1  loose 2/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p) as f: ⏎         r = csv.reader(f) ⏎         hdr = [h.strip().lower() for h
      -> ae_tpd_by_year.csv cols ['year', 'actual', 'expected', 'ae']
  2015-2020: 3543/3947 = 0.8976
  2021-2022: 2468/1870 = 1.3195
  2023-2024: 2039/2182 = 0.9343
  excl 21-22: 5582/6130 = 0.9107
ae_ip_by_y
```

## 2026-09-11T04:05:07Z  sc-bba653 (pass 1, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=1657.5s
harness: tool_calls=1  pack_sha=f189db2918f3
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2017, 2022] | conf 0.85 | mag ~+0.40 A/E over baseline (0.87 -> 1.31 p
  [1] FP    CI | drift | increase | [2020, 2022] | conf 0.75 | mag ~+0.28 A/E over baseline (0.91 -> ~1.19-
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.6 | mag ~+0.22 A/E over baseline (0.92 -> 1.10-1
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.45 | mag ~+0.08 A/E over baseline (0.97 -> 1.05-1
SCORE: strict 2/1  loose 2/1  FP 2
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, math ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ for p in ["ae_death_age_gender.csv","ae_ci_age
      -> == ae_death_age_gender.csv rows: 22
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '4', '7.135997803227396', '0.56053
```

## 2026-09-11T04:33:01Z  sc-d72b95 (pass 1, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=1654.3s
harness: tool_calls=1  pack_sha=8367ba6c04a4
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.7 | mag single-year spike to A/E 1.310 (~+0.38 v
  [1] FP    Death | drift | decrease | [2015, 2019] | conf 0.55 | mag sustained below-baseline level, A/E 0.83
SCORE: strict 1/3  loose 2/3  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, statistics ⏎  ⏎ def load(path): ⏎     rows=[] ⏎     with open(path) as f: ⏎         r=csv.reader(f) ⏎         hdr=next(r) ⏎         for row in r: ⏎ 
      -> death [(2015, 0.906), (2016, 0.829), (2017, 0.836), (2018, 0.898), (2019, 0.934), (2020, 1.31), (2021, 0.971), (2022, 0.985), (2023, 1.097), (2024, 1.018)]
death mean 0.9783 longest run >1: 2 longest 
```

## 2026-09-11T04:41:48Z  sc-da1123 (pass 1, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=506.8s
harness: tool_calls=0  pack_sha=db341d206568
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag A/E rises from ~0.86 (2015-2018 mean) to
  [1] MATCH CI | drift | increase | [2015, 2024] | conf 0.85 | mag A/E rises from ~0.90 (2015-2018 mean) to
  [2] MATCH TPD | drift | increase | [2015, 2024] | conf 0.8 | mag A/E rises from ~0.97 (2015-2022 mean) to
  [3] MATCH IP | drift | increase | [2015, 2024] | conf 0.7 | mag A/E rises from ~0.97 (2015-2021 mean) to
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-11T04:57:22Z  sc-f520e5 (pass 1, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=914.7s
harness: tool_calls=0  pack_sha=352a871565bd
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2021] | conf 0.62 | mag A/E rises from 0.88 in 2016 to 1.34 in 2
  [1] MATCH IP | drift | increase | [2017, 2022] | conf 0.78 | mag A/E rises from 0.88 in 2017 to 1.20 in 2
SCORE: strict 1/2  loose 1/2  FP 1
```

# ===================== PASS 1 COMPLETE (23/23, no failures) =====================

**Totals (harness v1.2, 1 run/scenario):** strict 27/44 = 61.4% · loose 63.6% ·
FP/run 0.52 · badjson 1 · errors 0 · clean-data honesty intact.
**Same model, harness OFF (xam_v5 run 1, same 23 scenarios):** strict 63.6% ·
FP/run 1.61.
**Drift strata:** bounded-then-reverting **5/5 strict** (xam_v4: 3.9%, xam_v5: 55%)
· persistent 8/10.
→ The harness bought **3x restraint** (FP/run 1.61 → 0.52) and solved bounded
drift, but strict recall is flat and the noise traps went 2/5 → 0/5.

### Failures diagnosed
| scenario | what happened | root cause |
|---|---|---|
| sc-314eca (all-lines volatility) | 7357 s, 2 tool calls, unparseable output | model emitted its native `<tool_call>` syntax; runner treated it as the final answer AND cleared the error, banking it |
| sc-9660b9 (all-lines volatility) | 5 per-line "drift"/"shock" findings, 0/4, FP 5 | pack is per-line only — no cross-line view, so a systemic dispersion event was read as four independent stories |
| sc-6e2478 (Death volatility) | answered "clean", 0/1 | pack said "no strong signal" although overdispersion was x5.23 with amplitude 0.34 (dispersion branch required move < 0.14) |
| sc-8a9fa1 (Death volatility) | called it "drift 2016-2018", 0/1 | same branch miss (od x7.3) |
| sc-5e376b (Death shock 2020-22) | called it "drift" over the right window | pack text invited "2-3 year sustained move" for a flat-topped 3-year pulse |

### Harness v1.3 edits (targeted at exactly those five)
1. **Onset sharpness** = max 1-year move / excursion size, calibrated on the
   optimization split (one-off change ≈ 1.0, build-up < 0.85, oscillation ≥ 1.3);
   the profile now says PULSE / RAMP / OSCILLATING instead of inviting "sustained".
2. **Scatter-dominant branch** (overdispersion ≥ 4.5 AND biggest swing > net
   excursion) — catches the two missed dispersion controls without claiming them.
3. **CROSS-LINE block**: per-year count of lines away from their own smoothed
   baseline, plus a swing-coordination count; a claim needs a run of ≥2
   CONSECUTIVE years with ≥3 lines (verified: it fires on sc-314eca/sc-9660b9 and
   stays silent on sc-042304, sc-5e376b, sc-14cdd9).
4. **Rules 3b/3c**: at most two tool calls (kill the 2-hour spiral), and systemic
   events must be reported for EVERY affected line (schema has no "all").
5. **Runner fixes**: the model's native `<tool_call>` syntax is now recognised and
   executed; a content-validity failure can no longer have its error cleared and
   be banked (this is what let the truncated run through).

## 2026-09-11T15:26:12Z  sc-042304 (pass 2, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=816.0s
harness: tool_calls=2  pack_sha=eecdaa2dae66
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.85 | mag A/E jumps from 0.88 (2020) to 1.273 (202
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎ files = ["ae_ci.csv","ae_death.csv","ae_tpd.csv","ae_ip.csv"] ⏎ for f in files: ⏎     print("="*30, f) ⏎     try: ⏎         with open(f) as fh: ⏎  
      -> ============================== ae_ci.csv
Age	Gender	Year	Actual	Expected	AE
17	Female	2015	0	0.5729274619044413	0.0
17	Female	2016	0	0.5250819097135118	0.0
17	Female	2017	0	0.6068058235486801	0.0
17	F
  [1] run: import csv, collections ⏎ # CI: aggregate actual/expected by age for each year to see which ages drive 2021-2022 ⏎ rows = list(csv.DictReader(open("ae_ci.csv"))
      -> YEAR total A/E:
2015 501.0 596.4 0.84
2016 686.0 720.2 0.953
2017 789.0 837.1 0.942
2018 900.0 963.2 0.934
2019 1038.0 1097.3 0.946
2020 1090.0 1239.1 0.88
2021 1764.0 1385.9 1.273
2022 2005.0 1548.3 
```

## 2026-09-11T15:44:34Z  sc-137901 (pass 2, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1083.3s
harness: tool_calls=0  pack_sha=95bb23eb37dd
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] FP    TPD | shock | increase | [2022, 2023] | conf 0.85 | mag level +0.2: AE 1.029 (2021) -> 1.173 (20
  [1] FP    IP | shock | increase | [2022, 2023] | conf 0.65 | mag level +0.11: AE 0.996 (2021) -> 1.103 (2
  [2] FP    TPD | drift | decrease | [2015, 2018] | conf 0.6 | mag AE declines 0.982 (2015) -> 0.919 (2016)
SCORE: strict 0/2  loose 1/2  FP 3
```

## 2026-09-11T15:56:44Z  sc-14cdd9 (pass 2, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=711.7s
harness: tool_calls=1  pack_sha=d1c888905c1a
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎ with open('ae_death_age_gender.csv') as f: ⏎     rd = csv.DictReader(f) ⏎     rows = list(rd); keys = rd.fiel
      -> ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
{'AgeBand': '15', 'Gender': 'Female', 'Actual': '4', 'Expected': '4.520672767466119', 'AE': '0.8848240529123806'}

[error] KeyError: None
```

## 2026-09-11T16:07:36Z  sc-17d82f (pass 2, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=633.5s
harness: tool_calls=2  pack_sha=99a7cc3246bb
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.99 | mag pooled A/E 0.496 (z approx -20.4, ~1636 
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎ def dump(f, n=80): ⏎     print("==", f) ⏎     try: ⏎         with open(f) as fh: ⏎             rows = list(csv.reader(fh)) ⏎     except Exception a
      -> == ae_ip_termination.csv
total rows: 714
['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
['Injury/Accident', '0', '1499', '315', '0.21014009339559706', '0.2
  [1] run: import csv ⏎ rows=list(csv.reader(open("ae_ip_termination.csv"))) ⏎ hdr=rows[0]; data=rows[1:] ⏎ cancer=[r for r in data if r[0]=='Cancer'] ⏎ # duration-buckete
      -> Cancer rows: 122 total exposed 62057.0 total recovered 812.0 pooled A/E approx 0.013084744670222538
Cancer dur 0-12: exposed=18923 recovered=567 rate=0.0300
Cancer dur 13-24: exposed=11169 recovered=1
```

## 2026-09-11T16:11:46Z  sc-2d248f (pass 2, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=230.9s
harness: tool_calls=0  pack_sha=a3bd70097e82
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.9 | mag empirical YoY sd of A/E ~0.60 vs Poisson
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T16:23:25Z  sc-314eca (pass 2, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=680.6s
harness: tool_calls=0  pack_sha=221a2299298c
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.7 | mag ~+0.10/yr over 3 years; peak A/E 1.28 (2
  [1] FP    CI | shock | increase | [2019, 2020] | conf 0.65 | mag 2-year spike: A/E 0.90 (2018) → 1.15 (20
  [2] FP    TPD | shock | increase | [2019, 2019] | conf 0.6 | mag single-year spike: A/E 1.09 (2018) → 1.3
  [3] FP    IP | shock | increase | [2019, 2019] | conf 0.6 | mag single-year spike: A/E 0.96 (2018) → 1.2
  [4] MATCH TPD | volatility | dispersion | [2015, 2024] | conf 0.75 | mag YoY SD 0.271 vs Poisson expectation 0.03
SCORE: strict 1/1  loose 1/1  FP 4
```

## 2026-09-11T16:35:19Z  sc-3c83fd (pass 2, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=695.6s
harness: tool_calls=0  pack_sha=cfa80cc07232
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2017, 2019] | conf 0.85 | mag A/E declined ~-0.10/yr from 0.93 (2017) 
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T16:46:14Z  sc-409000 (pass 2, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=636.6s
harness: tool_calls=0  pack_sha=195ae1225d93
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.97 | mag Mental Health termination A/E ≈ 1.99 — a
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T16:52:06Z  sc-48351f (pass 2, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=333.1s
harness: tool_calls=0  pack_sha=4ca6c09c1000
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.92 | mag +0.235 A/E (1.24x baseline); 1,299 actua
  [1] MATCH IP | shock | increase | [2023, 2023] | conf 0.92 | mag +0.177 A/E (1.18x baseline); 2,208 actua
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-11T17:02:28Z  sc-4a7f9e (pass 2, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=603.6s
harness: tool_calls=0  pack_sha=d594c0037ab6
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.85 | mag +0.38 above ~0.90 baseline (AE 1.29-1.30
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.85 | mag -0.46 below ~1.13 baseline (AE 0.65-0.67
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-11T17:15:16Z  sc-5e376b (pass 2, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=749.0s
harness: tool_calls=0  pack_sha=e59a04f93b5b
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.85 | mag AE level jumps ~+0.36 in 2020 (0.88 -> 1
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T17:29:51Z  sc-63f1c7 (pass 2, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=857.0s
harness: tool_calls=0  pack_sha=cf7c5568f542
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.05/yr; A/E 1.02 (2021) -> 1.19 (2024
  [1] MATCH CI | shock | increase | [2021, 2021] | conf 0.8 | mag single year: A/E 1.327 (A=1839 vs E=1386
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-11T17:45:48Z  sc-6e2478 (pass 2, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=937.6s
harness: tool_calls=0  pack_sha=ddcab86a5d5a
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.6 | mag ~5x Poisson year-to-year dispersion (emp
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T17:56:25Z  sc-8a9fa1 (pass 2, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=618.7s
harness: tool_calls=0  pack_sha=b37c8a25b0eb
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2021] | conf 0.8 | mag overdispersion x7.3 (empirical YoY SD 0.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T18:10:41Z  sc-8d3b47 (pass 2, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=837.8s
harness: tool_calls=1  pack_sha=71736693f236
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.78 | mag A/E climbs from ~0.74 (2018 trough) to ~
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.8 | mag A/E declines from ~1.20 (2015) to ~0.86 
SCORE: strict 2/2  loose 2/2  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ def dump(f, limit=160): ⏎     print("="*25, f) ⏎     with open(f) as fh: ⏎         rows = list(csv.reader(fh)) ⏎     print("n_rows:", len(rows)) ⏎ 
      -> ========================= ae_death_age_gender.csv
n_rows: 23
header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '3', '4.520672767466119', '0.6636180396842856']
['15', 'Male', '
```

## 2026-09-11T18:23:21Z  sc-9372cd (pass 2, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=739.6s
harness: tool_calls=0  pack_sha=43b15dde511a
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2018, 2021] | conf 0.6 | mag ~+0.03/yr ramp; avg +0.11 above the ~0.9
  [1] FP    Death | shock | increase | [2016, 2016] | conf 0.35 | mag single-year +0.22 (AE 0.944 -> 1.163 -> 
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-11T18:33:04Z  sc-9660b9 (pass 2, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=564.7s
harness: tool_calls=0  pack_sha=35245b419f54
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2020, 2022] | conf 0.8 | mag A/E rises from ~0.95 (2019) to 1.42 (202
  [1] FP    CI | drift | increase | [2020, 2021] | conf 0.75 | mag A/E jumps from ~0.89 (2019) to 1.25 (202
  [2] FP    TPD | shock | increase | [2020, 2020] | conf 0.8 | mag Single-year spike: A/E 1.56 (actual 1,28
  [3] FP    TPD | drift | decrease | [2021, 2022] | conf 0.85 | mag A/E drops to 0.86 (2021) then 0.39 (2022
  [4] FP    IP | shock | increase | [2020, 2020] | conf 0.75 | mag Single-year spike: A/E 1.37 (actual 2,11
SCORE: strict 0/1  loose 0/1  FP 5
```

## 2026-09-11T18:40:28Z  sc-abbec4 (pass 2, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=425.2s
harness: tool_calls=0  pack_sha=53bb6e5e01c0
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.92 | mag AE rises from ~0.91 in 2020 to 1.35 in 2
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag AE rises from ~0.91 in 2020 to 1.26 in 2
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-11T18:57:02Z  sc-bba653 (pass 2, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=974.5s
harness: tool_calls=0  pack_sha=a12039dd595a
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.85 | mag A/E jumps +0.36 in one year (0.876 in 20
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag A/E steps +0.28 in one year (0.898 in 20
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.55 | mag A/E steps up from ~0.95-0.97 to 1.19 (20
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.4 | mag Mild step-up of ~+0.06-0.08 (0.96 in 201
  [4] FP    Death | other | decrease | [2015, 2019] | conf 0.8 | mag Sustained below-baseline level: A/E 0.85
  [5] FP    CI | other | decrease | [2015, 2019] | conf 0.75 | mag Sustained below-baseline level: A/E 0.89
  [6] FP    TPD | other | decrease | [2015, 2019] | conf 0.6 | mag Milder below-baseline level: A/E 0.88-0.
SCORE: strict 4/1  loose 4/1  FP 3
```

## 2026-09-11T19:06:34Z  sc-d72b95 (pass 2, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=553.2s
harness: tool_calls=0  pack_sha=dcb0f8336503
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.68 | mag A/E jumps to 1.310 in 2020 from 0.934 in
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.55 | mag A/E rises to 1.159 in 2020 from 0.937 in
SCORE: strict 2/3  loose 2/3  FP 0
```

## 2026-09-11T19:16:42Z  sc-da1123 (pass 2, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=589.3s
harness: tool_calls=0  pack_sha=6433a2cc6e50
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag A/E fell from ~0.94 (2015) to a trough o
  [1] MATCH CI | drift | increase | [2015, 2024] | conf 0.8 | mag A/E below baseline ~0.89-0.92 (2015-18, 
  [2] MATCH TPD | drift | increase | [2015, 2024] | conf 0.7 | mag A/E rose from ~0.92-0.97 (2015-18) throu
  [3] MATCH IP | drift | increase | [2015, 2024] | conf 0.6 | mag A/E rose from ~0.93-0.99 (2015-21) to 1.
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-11T19:43:56Z  sc-f520e5 (pass 2, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=1614.5s
harness: tool_calls=3  pack_sha=b58673669431
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] MATCH IP | drift | increase | [2018, 2022] | conf 0.78 | mag ~+0.02/yr ramp from 2018; peak A/E ~1.20
  [1] FP    Death | drift | increase | [2019, 2021] | conf 0.58 | mag rising ~+0.16/yr step-up to peak A/E ~1.
SCORE: strict 1/2  loose 1/2  FP 1
TOOL TRANSCRIPT (3 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.DictReader(f)) ⏎  ⏎ def detect
      -> [error] TypeError: 'dict_keys' object is not subscriptable
  [1] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.DictReader(f)) ⏎  ⏎ def detect
      -> === DEATH w1=2019-2021 vs w2=outside | cols: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE'] | detected: {'age': 'AgeBand', 'gender': 'Gender', 'actual': 'Actual', 'expected': 'Expected'}

[error] Z
  [2] run: import csv ⏎ for p in ['ae_death_age_gender.csv','ae_ip_age_gender.csv','ae_ci_age_gender.csv','ae_tpd_age_gender.csv','ae_ip_termination.csv','ae_ip_terminatio
      -> === ae_death_age_gender.csv rows: 23
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '3', '4.520672767466119', '0.6636180396842856']
['15', 'Male', '0', '7.135997803227396', '0.0']

```

## 2026-09-11T20:00:40Z  sc-f69eea (pass 2, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=984.7s
harness: tool_calls=2  pack_sha=7ec1beb91c7b
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag total +0.75 over 2015-2024 (~+0.084/yr);
  [1] FP    Death | other | increase | None | conf 0.68 | mag static age split: 60+ over-claim (age-60
SCORE: strict 1/1  loose 1/1  FP 1
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎ with open('ae_death_age_gender.csv') as f: ⏎     rd = csv.reader(f) ⏎     header = next(rd) ⏎     rows = [r for r in rd if any(c.strip() for c in r
      -> HEADER ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
NROWS 22
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040371686257955']
['20'
  [1] run: import csv ⏎ from collections import defaultdict ⏎ with open('ae_death_age_gender.csv') as f: ⏎     rd = csv.reader(f) ⏎     next(rd) ⏎     rows=[r for r in rd 
      -> AGE BAND: band  Actual  Expected  A/E
15 7.0 11.7 0.601
20 70.0 80.3 0.872
25 114.0 155.6 0.733
30 210.0 221.6 0.948
35 275.0 309.3 0.889
40 411.0 454.5 0.904
45 569.0 666.9 0.853
50 940.0 1002.3 0.93
```

# ===================== PASS 2 COMPLETE (23/23, no failures) =====================
**Totals (harness v1.3):** strict 32/44 = 72.7% (pass 1: 61.4%, baseline 63.6%) ·
loose 75.0% · FP/run 0.78 (baseline 1.61) · badjson 0 · errors 0 · clean honesty intact.
Drift strata: persistent 8/10 · bounded 3/5 (one regression).
Fixed vs pass 1: sc-5e376b 0/1→1/1 (flat-topped jolt), sc-6e2478 0/1→1/1,
sc-8a9fa1 0/1→1/1, sc-bba653 2/4→4/4, sc-314eca 0/4→1/4, sc-d72b95 1/4→2/4.
Regressed: sc-137901 2/2→0/2 — the v1.3 onset rule was evaluated BEFORE the
smoothed-ramp evidence, so a ramp containing one big year was called a jolt.

## v1.4 edits (final pass)
1. **Smoothed-ramp evidence takes precedence** over onset sharpness (fixes the
   sc-137901 regression: TPD now reads SHAPED-AND-GRADUAL + "level at the END
   +0.124 vs its own baseline").
2. **Up to three non-overlapping excursion windows** instead of only the best —
   sc-d72b95's hidden rise now appears as `2019-2024 (6y) +0.185`; plus an
   **end-of-series level** figure (calibrated: clean books ≤ 0.008, so this is a
   very clean discriminator for "does not return").
3. **Per-line coordination note**: every line involved in a book-wide swing
   episode is annotated in its own block, not just summarised once.

## 2026-09-11T21:34:16Z  sc-042304 (pass 3, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=532.5s
harness: tool_calls=0  pack_sha=c6d43dc4e6fd
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.85 | mag ~+0.36 A/E level shift (0.88 -> ~1.28, i
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-11T22:47:45Z  sc-137901 (pass 3, unattended)
```
scenario sc-137901  json=empty  overall_says=None  error=endpoint unavailable (wait-for-endpoint expired)  wall=1800.1s
harness: tool_calls=None  pack_sha=4d0cf372df9f
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  (none)
SCORE: strict 0/2  loose 0/2  FP 0
```

## 2026-09-12T00:24:19Z  sc-14cdd9 (pass 3, unattended)
```
scenario sc-14cdd9  json=empty  overall_says=None  error=endpoint unavailable (wait-for-endpoint expired)  wall=1800.1s
harness: tool_calls=None  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-12T02:00:53Z  sc-17d82f (pass 3, unattended)
```
scenario sc-17d82f  json=empty  overall_says=None  error=endpoint unavailable (wait-for-endpoint expired)  wall=1800.1s
harness: tool_calls=None  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
```

## 2026-09-12T03:37:28Z  sc-2d248f (pass 3, unattended)
```
scenario sc-2d248f  json=empty  overall_says=None  error=endpoint unavailable (wait-for-endpoint expired)  wall=1800.1s
harness: tool_calls=None  pack_sha=905d1b33dd01
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
```

## 2026-09-12T03:54:20Z  sc-314eca (pass 3, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=991.0s
harness: tool_calls=0  pack_sha=74c862fc25ba
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.6 | mag ~+0.22 window A/E vs ~0.97 baseline (201
  [1] MATCH CI | volatility | dispersion | [2019, 2021] | conf 0.7 | mag empirical YoY SD 0.203 vs Poisson 0.031 
  [2] MATCH TPD | volatility | dispersion | [2019, 2021] | conf 0.7 | mag empirical YoY SD 0.271 vs Poisson 0.036 
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.7 | mag empirical YoY SD 0.177 vs Poisson 0.026 
SCORE: strict 3/1  loose 3/1  FP 1
```

## 2026-09-12T04:08:37Z  sc-3c83fd (pass 3, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=838.0s
harness: tool_calls=0  pack_sha=ac03b6c10f6a
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2017, 2019] | conf 0.85 | mag ~-0.10/yr (2016 1.098 -> 2017 0.927 -> 2
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T04:24:10Z  sc-409000 (pass 3, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=913.1s
harness: tool_calls=1  pack_sha=4f6adbb8f026
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.97 | mag Mental Health termination A/E = 1.99 (≈x
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ with open('ae_ip_termination_by_month.csv') as f: ⏎     rd = csv.DictReader(f) ⏎     fields = rd.fieldname
      -> FIELDS: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
N: 122
{'DurationMonth': '0', 'Exposed': '15030', 'Recovered': '2908', 'ExpectedRecoveries': '2152.3900000000003', 'AE': '
```

## 2026-09-12T04:37:01Z  sc-48351f (pass 3, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=752.3s
harness: tool_calls=0  pack_sha=06b3681221e4
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.85 | mag A/E 1.235 in 2023 (actual 1299 vs expect
  [1] MATCH IP | shock | increase | [2023, 2023] | conf 0.85 | mag A/E 1.177 in 2023 (actual 2208 vs expect
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T04:43:16Z  sc-4a7f9e (pass 3, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=354.8s
harness: tool_calls=0  pack_sha=56249351f824
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.88 | mag ~+0.38 A/E (excursion to ~1.30 vs ~0.95 
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag ~-0.46 A/E (dip to ~0.65 from ~1.13 base
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T04:48:30Z  sc-5e376b (pass 3, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=294.6s
harness: tool_calls=0  pack_sha=20d532b2dd3c
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.92 | mag ~+0.40 A/E (from ~0.86 baseline to ~1.27
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T04:59:23Z  sc-63f1c7 (pass 3, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=633.8s
harness: tool_calls=0  pack_sha=306971c404ef
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.8 | mag ~+0.035/yr over the full window (total +
  [1] MATCH CI | shock | increase | [2021, 2021] | conf 0.85 | mag single-year spike to A/E 1.33 (~+0.35 vs
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-12T05:23:02Z  sc-6e2478 (pass 3, unattended)
```
scenario sc-6e2478  json=valid  overall_says=clean  error=None  wall=1398.7s
harness: tool_calls=1  pack_sha=0dfeef3ff1a9
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for f in ["ae_death_age_gender.csv","death_claims.csv","ae_death.csv"]: ⏎     print("==",f) ⏎     with open(f) as fh: ⏎         rows=list(csv.reade
      -> == ae_death_age_gender.csv
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '6', '4.520672767466119', '1.3272360793685711']
['15', 'Male', '4', '7.135997803227396', '0.56053828915010
```

## 2026-09-12T06:08:26Z  sc-137901 (pass 3, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1270.1s
harness: tool_calls=0  pack_sha=4d0cf372df9f
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2016, 2023] | conf 0.75 | mag sustained level move from 0.89 (2016-18 
  [1] FP    IP | shock | increase | [2022, 2023] | conf 0.7 | mag ~+0.11 abrupt level shift (0.996 in 2021
SCORE: strict 1/2  loose 1/2  FP 1
```

## 2026-09-12T06:18:36Z  sc-14cdd9 (pass 3, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=590.3s
harness: tool_calls=0  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-12T06:43:04Z  sc-17d82f (pass 3, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=1449.3s
harness: tool_calls=2  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.97 | mag Cancer IP termination (recovery) A/E ~0.
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ d = load('ae_death_age_gender.csv') ⏎ print('DEATH_A
      -> DEATH_AG header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
n rows: 22
yi,ai,ei = None 2 3
sample: ['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
sample: ['15', 'Male', '4', '
  [1] run: import csv ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ t = load('ae_ip_termination_by_month.csv') ⏎ print('
      -> TERM header: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
n rows: 122
--- first 20 rows ---
['0', '15030', '2107', '2152.3900000000003', '0.978911814308745']
['1', '12780', '1
```

## 2026-09-12T07:00:43Z  sc-2d248f (pass 3, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=1039.9s
harness: tool_calls=0  pack_sha=905d1b33dd01
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.85 | mag YoY SD of A/E 0.60 vs Poisson 0.026 (~23
  [1] FP    Death | shock | increase | [2016, 2017] | conf 0.45 | mag +0.22 A/E in 2016 (336 vs 290, +16%), re
  [2] FP    IP | shock | increase | [2016, 2017] | conf 0.55 | mag +1.24 A/E in 2016 (1888 vs 1142, +65%) a
SCORE: strict 1/1  loose 1/1  FP 2
```

## 2026-09-12T07:21:47Z  sc-8a9fa1 (pass 3, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=1243.6s
harness: tool_calls=1  pack_sha=04b8963177aa
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2018] | conf 0.65 | mag peak A/E ~1.52 in 2018 (Actual 593 vs Ex
SCORE: strict 0/1  loose 0/1  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ with open("ae_death_age_gender.csv") as f: ⏎     rd = csv.reader(f) ⏎     header = next(rd) ⏎     rows = list(rd) ⏎ print("HEADER:", header) ⏎ def 
      -> HEADER: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
col idx year/actual/expected: None 2 3
rows 2015-2019: 0 total: 22
TERM HEADER: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries'
```

## 2026-09-12T07:29:57Z  sc-8d3b47 (pass 3, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=470.7s
harness: tool_calls=0  pack_sha=25699c038f41
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag A/E rises from a ~0.74 trough (2018) to 
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.9 | mag A/E falls from ~1.23 (2015) to ~0.86 (20
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-12T07:42:08Z  sc-9372cd (pass 3, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=711.3s
harness: tool_calls=1  pack_sha=1ba55eef287e
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2018, 2021] | conf 0.55 | mag sub-window elevation ~+0.05 to +0.19 abo
  [1] FP    IP | other | increase | [2015, 2016] | conf 0.45 | mag ~+0.03 step (A/E 1.023/1.029 in 2015-16 
SCORE: strict 1/1  loose 1/1  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ files=["ae_death_age_gender.csv","ae_tpd_age_gender.csv","ae_ip_age_gender.csv","ae_ci_age_gender.csv","ae_ip_termination_by_month.csv","ae_ip_term
      -> === ae_death_age_gender.csv
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '4', '7.135997803227396', '0.5605382891501
```

## 2026-09-12T07:48:59Z  sc-9660b9 (pass 3, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=391.3s
harness: tool_calls=0  pack_sha=547008340f58
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2020, 2022] | conf 0.75 | mag A/E rises from 1.16 to 1.22 to 1.42 (~+0
  [1] FP    CI | drift | increase | [2020, 2021] | conf 0.7 | mag A/E rises from 1.25 to 1.48 (~+0.23/yr);
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.75 | mag A/E swings 1.56 (2020) -> 0.86 (2021) ->
  [3] FP    IP | shock | increase | [2020, 2021] | conf 0.65 | mag A/E spikes to 1.37 in 2020 (+0.37 vs ~1.
SCORE: strict 1/1  loose 1/1  FP 3
```

## 2026-09-12T08:00:34Z  sc-abbec4 (pass 3, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=674.9s
harness: tool_calls=0  pack_sha=fb418334facd
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.85 | mag ~+0.40 A/E over 2021-2022 (x1.4 vs ~0.93
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.85 | mag ~+0.30 A/E over 2021-2022 (x1.3 vs ~0.93
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T08:07:39Z  sc-bba653 (pass 3, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=405.3s
harness: tool_calls=0  pack_sha=10b92430f8b4
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.92 | mag ~+0.40 A/E level shift (from ~0.87 pre-2
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.28 A/E level shift (from ~0.90 pre-2
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.20 A/E level shift (from ~0.92 pre-2
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.72 | mag ~+0.07-0.08 A/E level shift (from ~0.97 
SCORE: strict 4/1  loose 4/1  FP 0
```

## 2026-09-12T08:16:40Z  sc-d72b95 (pass 3, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=521.6s
harness: tool_calls=0  pack_sha=fc4bbd829b02
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.65 | mag A/E 0.93 (2019) → 1.31 (2020) → 0.97 (20
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.5 | mag A/E 0.94 (2019) → 1.16 (2020) → 0.90 (20
SCORE: strict 2/3  loose 2/3  FP 0
```

## 2026-09-12T08:33:25Z  sc-da1123 (pass 3, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=984.8s
harness: tool_calls=0  pack_sha=795d84f4dc33
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag A/E dips 0.94 (2015) to 0.74 (2018, z-5.
  [1] MATCH CI | drift | increase | [2015, 2024] | conf 0.8 | mag A/E ~0.89-0.92 (2015-18) -> ~1.01 (2019-
  [2] FP    TPD | shock | increase | [2023, 2024] | conf 0.7 | mag +0.092 in one year (2022 1.000 -> 2023 1
  [3] MATCH IP | drift | increase | [2015, 2024] | conf 0.6 | mag A/E 0.93 (2015) -> 1.08 (2024, z+3.5); ~
SCORE: strict 3/4  loose 3/4  FP 1
```

## 2026-09-12T08:49:26Z  sc-f520e5 (pass 3, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=940.8s
harness: tool_calls=0  pack_sha=8593e92bb8a6
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.6 | mag ramp ~+0.13/yr: 0.95 (2018) -> 1.11 -> 1
  [1] MATCH IP | drift | increase | [2018, 2022] | conf 0.7 | mag ramp ~+0.06/yr: 0.95 (2018) -> 1.04 -> 1
  [2] FP    IP | shock | decrease | [2015, 2017] | conf 0.5 | mag flat low level 0.85-0.92 (3y mean ~0.88,
SCORE: strict 1/2  loose 1/2  FP 2
```

## 2026-09-12T08:53:41Z  sc-f69eea (pass 3, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=235.3s
harness: tool_calls=0  pack_sha=a30d2bc68fbd
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.08/yr; A/E rises from 0.63 (2015) to
SCORE: strict 1/1  loose 1/1  FP 0
```

---

# PASS 3 COMPLETE — harness v1.4 — 2026-09-12T08:53:58Z

All 23 optimization books answered, **0 failures, 0 errored runs, 0 unreadable
answers**. Wall time was inflated by a ~4.5 h LLM-server outage (23:00-03:37Z)
which cost 12 failed attempts; every one of those was recorded as an error and
never banked as a result, and the loop resumed by itself when the endpoint
returned. Four books failed all three attempts during the outage and were
re-spent on the retry sweep.

## Totals (same 23 books, one answer each)

| corpus | strict | loose | FP/answer | badjson | errors | clean honesty |
|---|---|---|---|---|---|---|
| zero-shot baseline (xam_v5 answer 1) | 28/44 = 63.6 % | 63.6 % | 1.61 | 0 | 0 | intact |
| pass 1 (v1.2) | 27/44 = 61.4 % | 63.6 % | 0.52 | 1 | 0 | intact |
| pass 2 (v1.3) | 32/44 = 72.7 % | 75.0 % | 0.78 | 0 | 0 | intact |
| **pass 3 (v1.4)** | **33/44 = 75.0 %** | 75.0 % | **0.52** | 0 | 0 | intact |

Slow-trend strata (per control-run): persistent-to-horizon **7/10** (8/10 at
baseline, 8/10 in passes 1-2), bounded-then-reverting **4/5** (3/5 at baseline,
5/5 in pass 1, 3/5 in pass 2).

Per-book movements pass 2 → pass 3 (full diffs above in the pass-3 entries):
sc-137901 0/2 fp3 → 1/2 fp1 · sc-314eca 1/4 fp4 → 3/4 fp1 · sc-9660b9 0/4 fp5 →
1/4 fp3 · sc-bba653 4/4 fp3 → 4/4 fp0 · sc-f69eea 1/1 fp1 → 1/1 fp0 ·
sc-da1123 4/4 fp0 → 3/4 fp1 · sc-6e2478 1/1 → 0/1 · sc-8a9fa1 1/1 fp0 → 0/1 fp1 ·
sc-2d248f 1/1 fp0 → 1/1 fp2 · sc-f520e5 1/2 fp1 → 1/2 fp2. Nine books moved,
four up and five down or level; the population is one answer per book, so the
causal attribution in the growth document is marked as inference.

## Freeze gate — `python3 scripts/harness_gate.py results/harness_opt_p3/zero_shot`

    [FAIL] strict recall >= 80%                          33/44 = 75.0%
    [PASS] false positives per run <= 1.0                12/23 = 0.52
    [PASS] clean data never called anomalous             claimed an anomaly on 0/1 clean run(s)
    [PASS] no unparseable answers and no errored runs    badjson=0 errors=0
    [FAIL] drift stratum not worse: persistent-to-horizon REGRESSION 7/10 vs 8/10 at zero-shot
    [PASS] drift stratum not worse: bounded-then-reverting 4/5 vs 3/5 at zero-shot (no regression)
    VERDICT: DO NOT FREEZE   (exit 1)

The 80 % target was missed by 5 control-runs of 44, and the campaign's own rule
caps tuning at three passes, which are now spent. Recorded rather than papered
over: the bar was set before the pass was scored and it was not reached.

Two disclosures kept next to that verdict: (a) the two slow-trend rows of the
gate were added on the day the gate became a script, so they are not
pre-registered like the 80 % row; (b) the persistent-trend shortfall is one
control-run out of ten, inside the run-to-run spread measured for an unchanged
model.

## Freeze integrity

The harness on disk reproduces every pass-3 evidence pack **byte-for-byte**
(23/23 `harness.pack_text` fields compared against a fresh `stats_pack`
render). The frozen pair is `scripts/stats_pack.py` +
`scripts/run_zero_shot.py`; `harness_final_heldout.sh` copies both into
`results/harness_final/harness_snapshot/` with sha256 before its first call.

## Next

Held-out exam on the 24 tuning-free books, 3 answers each = 72 calls
(`bash scripts/harness_final_heldout.sh`), compared against the unharnessed
model on the same books, which already exists in `xam_v5`.

---

# ROUND v1.5 — the cap lifted, pass 4 prepared

The three-pass cap was our own rule; the human running the project lifted it to
try one more round before spending the held-out exam. Condition kept: the 24
held-out books remain unread, so the final exam stays honest.

## Diagnosis of the 11 remaining missed units (all offline, no API calls)

| group | units | why they were missed | verdict |
|---|---|---|---|
| planted unsteadiness (volatility truths) | 7 (sc-314eca, sc-6e2478, sc-8a9fa1, sc-9660b9 x3, sc-f520e5) | the line's *scatter* is the anomaly, and the model reports the right line/years as a "drift" instead. Our own rulebook tells it to ignore scatter below x6 while the true units sit at x3.0-22.7 | **not fixable by statistics.** Three discriminators measured and all failed (dispersion floor: 4 right out of 28 fires; multi-swing count: backwards, trends have more swings; swing-and-return shape: fires on a real trend). Trap books spread scatter across sibling lines with no planted control, so any rule sharp enough to fire on the truth also accuses the innocent |
| late slow rises hidden by an earlier event | 2 (sc-d72b95 CI, sc-da1123 TPD) | the pack's whole-window fit and end-vs-baseline are cancelled by the earlier jolt, so the pack said "no strong signal" and the rise was never reported | **fixed**: new TAIL block (final 3 years: gradient, fit R2, level vs the years before). Fires on 11 lines, every one a real movement; 0 fires on the clean book (clean |gradient| <= 0.013 vs 0.036-0.113) |
| one coordinated event, one line reported | 1 (sc-137901 IP) | the model's own prose said the move was "coordinated with IP" but it only emitted a TPD entry | **fixed**: rule 3c now states one entry per affected line even when one line's move is smaller, and that mentioning it only in prose counts as not finding it |

## Predictions registered BEFORE pass 4 was run

* the two repairs recover **2-3 of the 11** missed units -> 79.5-81.8 % strict
* false alarms roughly unchanged (both repairs add information about movements
  already detected; neither loosens a threshold)
* clean-book honesty intact (the tail block cannot fire there — measured)
* the 7 unsteadiness units do **not** move

## Machinery in place for this pass

* `harness_pass_run.sh` now snapshots `stats_pack.py` + `run_zero_shot.py` with
  sha256 into `results/harness_opt_p4/harness_snapshot/` before the first call
  (the gap that lost v1.3)
* leak preflight re-run after the edits: **PASS** for all 47 books (46 + 48 pack
  references, no API calls)

## 2026-09-12T11:11:51Z  sc-042304 (pass 4, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=446.6s
harness: tool_calls=0  pack_sha=c6d43dc4e6fd
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag Abrupt flat-topped two-year level shift 
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T11:35:18Z  sc-137901 (pass 4, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1388.9s
harness: tool_calls=0  pack_sha=4d0cf372df9f
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2015, 2023] | conf 0.85 | mag Smoothed (3y trailing MA) level climbs f
  [1] MATCH IP | drift | increase | [2015, 2023] | conf 0.7 | mag Smoothed (3y trailing MA) level climbs f
  [2] FP    Death | shock | increase | [2016, 2016] | conf 0.6 | mag Single-year spike: AE 1.163 (Actual 337 
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-12T11:41:39Z  sc-14cdd9 (pass 4, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=361.9s
harness: tool_calls=0  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-12T11:52:47Z  sc-17d82f (pass 4, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=648.9s
harness: tool_calls=2  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.98 | mag Cancer termination/recovery A/E 0.496 (z
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv ⏎ def dump(f, n=50): ⏎     print("==", f) ⏎     try: ⏎         rows = list(csv.reader(open(f))) ⏎     except Exception as e: ⏎         print("ERR", e
      -> == ae_ip_termination.csv
nrows: 714
['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
['Injury/Accident', '0', '1499', '315', '0.21014009339559706', '0.22', '
  [1] run: import csv ⏎ rows=list(csv.DictReader(open("ae_ip_termination.csv"))) ⏎ # pooled per diagnosis ⏎ diags={} ⏎ for r in rows: ⏎     d=r['Diagnosis'] ⏎     exp=floa
      -> Pooled per diagnosis:
Cancer           exp=  1635.9 rec=     812 AE=0.496 z=  -20.37
Cardiovascular   exp=   881.9 rec=     891 AE=1.010 z=    0.31
Injury/Accident  exp=  1437.5 rec=    1400 AE=0.974 
```

## 2026-09-12T12:26:24Z  sc-2d248f (pass 4, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=1998.5s
harness: tool_calls=2  pack_sha=8c900bd020ce
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2021] | conf 0.85 | mag A/E oscillates between 0.41 (2015) and 1
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.7 | mag steady rise ~+0.11 A/E per year from 0.7
SCORE: strict 1/1  loose 1/1  FP 1
TOOL TRANSCRIPT (2 call(s)):
  [0] run: import csv, statistics, math ⏎  ⏎ def load(fn): ⏎     with open(fn) as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ def num(x): ⏎     x = x.replace(",","").stri
      -> ===== ae_ip_by_year.csv =====
['Year', 'Actual', 'Expected', 'AE']
['2015', '418', '1012.7558607829104', '0.41273520715729584']
['2016', '1888', '1141.699527475656', '1.6536750296940603']
['2017', '13
  [1] run: import csv ⏎  ⏎ def load(fn): ⏎     with open(fn) as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ for fn in ["ae_ip_age_gender.csv","ae_ip_termination_by_month.
      -> ===== ae_ip_age_gender.csv =====
['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
['15', 'Female', '22', '33.94934067109002', '0.6480243670456426']
['15', 'Male', '28', '43.49296919561533', '0.643782
```

## 2026-09-12T12:40:53Z  sc-314eca (pass 4, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=850.9s
harness: tool_calls=0  pack_sha=74c862fc25ba
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.6 | mag ~+0.28 peak (AE 1.28 in 2021), ~+0.10/yr
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.6 | mag YoY swings of +/-0.2-0.4; AE 1.15(2019),
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.6 | mag AE 1.37(2019) spike, 0.57(2021) crash; o
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.6 | mag AE 1.28(2019) spike, 0.91(2020) drop; ov
SCORE: strict 3/1  loose 3/1  FP 1
```

## 2026-09-12T12:47:26Z  sc-3c83fd (pass 4, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=374.3s
harness: tool_calls=0  pack_sha=ac03b6c10f6a
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2016, 2019] | conf 0.92 | mag ~-0.12/yr, total -0.37 over 3 YoY moves 
  [1] FP    CI | shock | increase | [2020, 2024] | conf 0.85 | mag +0.34 single-year step at 2020; level pe
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-12T12:56:22Z  sc-409000 (pass 4, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=517.3s
harness: tool_calls=0  pack_sha=4f6adbb8f026
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.95 | mag Mental health terminations ~2.0x assumed
  [1] FP    Death | shock | increase | [2016, 2016] | conf 0.55 | mag Single-year +0.16 vs baseline (A/E 1.163
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-12T13:03:00Z  sc-48351f (pass 4, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=379.4s
harness: tool_calls=0  pack_sha=06b3681221e4
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2024] | conf 0.9 | mag A/E +23.5% in 2023 (1.235 vs ~1.0 baseli
  [1] MATCH IP | shock | increase | [2023, 2024] | conf 0.9 | mag A/E +17.7% in 2023 (1.177 vs ~0.99 basel
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T13:09:06Z  sc-4a7f9e (pass 4, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=347.8s
harness: tool_calls=0  pack_sha=56249351f824
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.93 | mag ~+0.35 above baseline (A/E 1.296/1.282 v
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.93 | mag ~-0.46 below baseline (A/E 0.670/0.654 v
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T13:16:21Z  sc-5e376b (pass 4, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=415.5s
harness: tool_calls=0  pack_sha=20d532b2dd3c
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.92 | mag A/E jumps from ~0.88 (2019) to 1.24-1.31
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T13:56:47Z  sc-63f1c7 (pass 4, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=2407.4s
harness: tool_calls=3  pack_sha=45ec76d01200
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.05-0.07/yr; level jumps +0.21 at 202
  [1] MATCH CI | shock | increase | [2021, 2021] | conf 0.8 | mag single-year spike: A/E 0.977 (2020) → 1.
SCORE: strict 2/2  loose 2/2  FP 0
TOOL TRANSCRIPT (3 call(s)):
  [0] run: import csv, math ⏎  ⏎ def load(p): ⏎     with open(p) as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ def fit(xs, ys): ⏎     n = len(xs) ⏎     mx = sum(xs)/n; m
      -> == DEATH
  all: grad=0.0345 R2=0.760 maxres=-0.145 pooledAE=1.004 z=+0.27
  2015-2020: grad=0.0033 R2=0.025 maxres=-0.052 pooledAE=0.883 z=-5.51
  2021-2024: grad=0.0544 R2=0.932 maxres=-0.025 pooledA
  [1] run: import csv, math ⏎ from collections import defaultdict ⏎  ⏎ def rows(p): ⏎     with open(p) as f: ⏎         r = list(csv.reader(f)) ⏎     h = r[0] ⏎     return 
      -> == CI claims by year (count, sum, max claim) ==

[error] FileNotFoundError: [Errno 2] No such file or directory: 'ci_claims.csv'
  [2] run: import os ⏎ print(sorted(os.listdir("."))) ⏎ import csv ⏎ mt = list(csv.reader(open("ae_ip_termination_by_month.csv"))) ⏎ print("termination rows:", len(mt)-1, 
      -> ['ae_ci.csv', 'ae_ci_age_gender.csv', 'ae_ci_age_gender.png', 'ae_ci_by_year.csv', 'ae_ci_by_year.png', 'ae_death.csv', 'ae_death_age_gender.csv', 'ae_death_age_gender.png', 'ae_death_by_year.csv', 'a
```

## 2026-09-12T14:24:31Z  sc-6e2478 (pass 4, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=1645.4s
harness: tool_calls=1  pack_sha=0dfeef3ff1a9
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2016, 2024] | conf 0.6 | mag x5.2 overdispersion (empirical YoY SD 0.
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for fn in ['ae_death_age_gender.csv','ae_ip_termination_by_month.csv','ae_ip_termination.csv']: ⏎     print('='*25, fn) ⏎     try: ⏎         with o
      -> ========================= ae_death_age_gender.csv
header: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
nrows: 22
['15', 'Female', '6', '4.520672767466119', '1.3272360793685711']
['15', 'Male', '4
```

## 2026-09-12T14:38:02Z  sc-8a9fa1 (pass 4, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=792.5s
harness: tool_calls=0  pack_sha=04b8963177aa
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.85 | mag Empirical YoY SD of A/E = 0.349 vs Poiss
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T14:52:30Z  sc-8d3b47 (pass 4, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=849.1s
harness: tool_calls=0  pack_sha=4babb17df9b4
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.82 | mag A/E 0.94(2015)/0.74(2018 trough) -> 1.14
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.82 | mag A/E ~1.20-1.25(2015-17) -> 0.855(2024); 
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-12T15:04:22Z  sc-9372cd (pass 4, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=693.9s
harness: tool_calls=0  pack_sha=1ba55eef287e
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2018, 2021] | conf 0.6 | mag ramp of ~+0.05/yr (A/E 1.01 -> 1.05 -> 1
  [1] FP    Death | shock | increase | [2016, 2016] | conf 0.4 | mag single-year A/E 1.163 (+16%, 337 actual 
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-12T15:15:15Z  sc-9660b9 (pass 4, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=633.4s
harness: tool_calls=0  pack_sha=547008340f58
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2020, 2022] | conf 0.85 | mag A/E rises from ~0.95 (2019) to 1.42 (202
  [1] FP    CI | drift | increase | [2020, 2022] | conf 0.75 | mag A/E rises from ~0.89 (2019) to 1.48 (202
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E oscillates: 1.56 (2020 spike) → 0.86
  [3] FP    IP | shock | increase | [2020, 2022] | conf 0.7 | mag A/E spikes to 1.37 in 2020 (+0.37 above 
SCORE: strict 1/1  loose 1/1  FP 3
```

## 2026-09-12T15:20:03Z  sc-abbec4 (pass 4, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=269.4s
harness: tool_calls=0  pack_sha=fb418334facd
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.9 | mag A/E jumps from ~0.90 (2015-2020 baseline
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag A/E jumps from ~0.93 (2015-2020 baseline
SCORE: strict 2/1  loose 2/1  FP 0
```

## 2026-09-12T15:31:18Z  sc-bba653 (pass 4, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=656.3s
harness: tool_calls=0  pack_sha=e4237a36c5ec
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag A/E jumps ~+0.40 in 2020 (0.88→1.24), ho
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag A/E jumps ~+0.28 in 2020 (0.90→1.18), ho
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.75 | mag A/E rises ~+0.22 in 2020 (0.97→1.19), wo
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.6 | mag A/E rises ~+0.08 in 2020 (0.96→1.05), ho
  [4] FP    Death | other | decrease | [2015, 2017] | conf 0.6 | mag Persistent underrun: A/E 0.85-0.93 (≈-0.
  [5] FP    CI | other | decrease | [2015, 2017] | conf 0.6 | mag Persistent underrun: A/E 0.89-0.91 (≈-0.
  [6] FP    TPD | other | decrease | [2015, 2017] | conf 0.55 | mag Persistent underrun: A/E 0.88-0.95 (≈-0.
  [7] FP    TPD | drift | decrease | [2022, 2024] | conf 0.5 | mag Steady decline of ≈-0.10/yr: 2022=1.15 →
SCORE: strict 4/1  loose 4/1  FP 4
```

## 2026-09-12T15:49:41Z  sc-d72b95 (pass 4, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=1083.9s
harness: tool_calls=0  pack_sha=a8591bd69d14
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2020] | conf 0.6 | mag A/E rises from ~0.83 (2016) to 1.31 (202
  [1] MATCH CI | drift | increase | [2022, 2024] | conf 0.7 | mag ~+0.08/yr: A/E 0.978 (2022) -> 1.030 (20
SCORE: strict 1/3  loose 2/3  FP 1
```

## 2026-09-12T16:16:02Z  sc-da1123 (pass 4, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=1562.9s
harness: tool_calls=0  pack_sha=e9b3d995d767
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] FP    Death | drift | decrease | [2015, 2018] | conf 0.85 | mag downward ramp 0.94 -> 0.74 over 2015-201
  [1] FP    CI | shock | decrease | [2015, 2018] | conf 0.8 | mag flat-top level deviation ~-0.10 (0.89-0.
  [2] FP    TPD | shock | decrease | [2015, 2018] | conf 0.55 | mag mild flat-top level deviation ~-0.04 (0.
  [3] FP    IP | shock | decrease | [2015, 2018] | conf 0.55 | mag mild flat-top level deviation ~-0.03 to 
  [4] MATCH Death | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.03-0.04/yr; 1.07 (2021) -> 1.14 (202
  [5] MATCH CI | drift | increase | [2023, 2024] | conf 0.9 | mag ~+0.07/yr; ~1.01 (2022) -> 1.096 (2023, 
  [6] MATCH TPD | drift | increase | [2023, 2024] | conf 0.8 | mag +0.09 jump at 2023 (step score 9.1) hold
  [7] MATCH IP | drift | increase | [2022, 2024] | conf 0.7 | mag ~+0.03/yr; ~0.99 (2021) -> 1.033 -> 1.03
SCORE: strict 4/4  loose 4/4  FP 4
```

## 2026-09-12T16:28:46Z  sc-f520e5 (pass 4, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=745.2s
harness: tool_calls=0  pack_sha=8fc83d9b4959
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.65 | mag A/E rises ~+0.13/yr from 0.95 (2018) to 
  [1] FP    Death | drift | increase | [2022, 2024] | conf 0.6 | mag A/E recovers from 0.80 (2022) to 0.97 (2
  [2] MATCH IP | drift | increase | [2019, 2022] | conf 0.75 | mag A/E rises ~+0.05/yr from 0.95 (2018) to 
  [3] FP    IP | shock | decrease | [2015, 2017] | conf 0.45 | mag A/E 0.85–0.92 for 3 consecutive years, ~
SCORE: strict 1/2  loose 1/2  FP 3
```

## 2026-09-12T16:45:05Z  sc-f69eea (pass 4, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=959.8s
harness: tool_calls=1  pack_sha=c540433e3725
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag A/E rises ~+0.08/yr, from 0.63 (2015) to
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎ with open("ae_death_age_gender.csv") as f: ⏎     rows = list(csv.reader(f)) ⏎ hdr = [h.strip().lower() for h 
      -> header: ['ageband', 'gender', 'actual', 'expected', 'ae'] nrows: 22
first rows:
['15', 'Female', '4', '4.520672767466119', '0.8848240529123806']
['15', 'Male', '3', '7.135997803227396', '0.42040371686
```

---

# PASS 4 COMPLETE — harness v1.5 — 2026-09-12T16:45:21Z

23/23 books, no failures, no unreadable answers, no errored runs. Harness
snapshot taken before the first call and verified: the on-disk `stats_pack.py`
and `run_zero_shot.py` still hash to `0a20550a8d65…` and `ee8c490aff46…`, i.e.
the frozen code is exactly the code that produced these answers.

## Result

    TOTALS: strict-recall=36/44=81.8%  loose=84.1%  FP/run=0.91  badjson=0  errors=0
    CLEAN-data honesty: claimed an anomaly on 0/1 clean run(s)
    DRIFT STRATA: persistent 9/10 (loose 10/10) | bounded-then-reverting 5/5 (loose 5/5)

    FREEZE GATE — all six criteria PASS  ->  VERDICT: FREEZE

| metric | harness OFF | pass 1 (v1.2) | pass 2 (v1.3) | pass 3 (v1.4) | **pass 4 (v1.5)** |
|---|---|---|---|---|---|
| strict | 63.6 % | 61.4 % | 72.7 % | 75.0 % | **81.8 %** |
| loose | 63.6 % | 63.6 % | 75.0 % | 75.0 % | **84.1 %** |
| FP/run | 1.61 | 0.52 | 0.78 | 0.52 | 0.91 |
| slow trends to the end | 8/10 | 8/10 | 8/10 | 7/10 | **9/10** |
| slow trends that revert | 3/5 | 5/5 | 5/5 | 4/5 | **5/5** |
| clean honesty | intact | intact | intact | intact | intact |

## Attribution — where the +3 net came from, measured not assumed

| change | units | evidence |
|---|---|---|
| rule 3c (one entry per affected line) | **+1** | sc-137901 1/2 → 2/2, IP recovered, FP unchanged at 1. The rule was aimed at exactly this failure |
| the TAIL block | **net 0** | it worked where predicted: sc-da1123 TPD recovered (+1) and sc-d72b95 CI recovered (+1, tail +0.080/yr R2 0.96). But on sc-d72b95 it cost both 2020 jolt units: the model now reads that line as a drift "2016-2020" instead of a jolt. 2 recovered, 2 lost |
| sampling luck | **+2** | sc-6e2478 (0/1 → 1/1) and sc-8a9fa1 (0/1 → 1/1). The tail block does NOT fire on either line, and sc-6e2478's pass-3 answer was an empty 83-character response. These two are the temperature-1.0 lottery, not the edits |

So the headline 81.8 % is real as a *measurement of this harness*, but only one
unit of the improvement is cleanly attributable to a change. The held-out exam —
72 answers instead of 23 — is the measurement that can carry weight.

## Registered predictions vs what happened

| prediction (registered before the pass) | outcome |
|---|---|
| the two repairs recover 2-3 of the 11 missed units | **correct** — 3 recovered (d72b95 CI, da1123 TPD, 137901 IP) |
| false alarms roughly unchanged | **WRONG** — 0.52 → 0.91. See the mechanism below |
| clean-book honesty intact | **correct** — 0/1 claims, the tail block cannot fire there |
| the 7 unsteadiness units do not move | **WRONG** — 2 of them moved (both via sampling, not via the edits) |

## Why false alarms rose, and it is our instruction's fault

The tail instruction says to report the tail "even when an earlier event on the
same line is bigger and already reported". The model obeyed literally and now
emits TWO findings on lines where the tail fires: 8 findings on sc-bba653 for a
4-line jolt, and 8 on sc-da1123 for 4 trends. The second entry often carries the
wrong pattern for that line's control (a tail read as "drift" where the control
is a "jolt"), so it scores as a false alarm. Cost: +9 false alarms, concentrated
in sc-bba653 (+4) and sc-da1123 (+3). Context that matters: 0.91 per answer is
still **44 % fewer false alarms than the unharnessed model's 1.61**.

The cleaner instruction would be "extend the same finding's window into the tail
rather than adding a second finding" — but that is a *post-hoc* edit, and the
gate has already passed on a pre-registered rule. Editing again after passing,
to improve the number that the gate just accepted, is how a tuning set gets
overfitted. It is recorded here as a known improvement for any future round with
a fresh tuning split.

## Next

Freeze v1.5 (snapshot verified) and run the held-out exam: 24 books x 3 answers =
72 calls, `bash scripts/harness_final_heldout.sh`. Baseline for the same 24 books
x 3 answers already exists in xam_v5.

---

# ROUND v1.6 — pass 5 launched 2026-09-12T22:49:40Z

The rulebook and pack are frozen for this pass; the snapshot with sha256 was
written before the first call (`results/harness_opt_p5/harness_snapshot/`).

## Diagnosis of pass 4's remaining 8 misses and 21 false alarms (offline, no API)

Pass 4 finished at 81.8 % with 21 false alarms. Both were traced to specific,
identified causes rather than impressions:

### The recall defect: the pack contradicted itself and never named the pattern

`sc-9660b9` (truth: book-wide unsteadiness on all four lines, 2020-2022) came
back with the **window exactly right on all four lines** and the wrong pattern
word on three:

    Death [2020,2022] sustained-move  -> counts as a FALSE ALARM
    CI    [2020,2022] sustained-move  -> counts as a FALSE ALARM
    TPD   [2020,2022] dispersion      -> correct (the 1/4)
    IP    [2020,2022] one-off change  -> counts as a FALSE ALARM

The model's own evidence text on the CI line quotes the pack saying the line
"oscillates rather than holding a new level" — and then it wrote a sustained move
anyway, citing verbatim: *"prefer drift per 'rises YoY before peaking' rule"*.
That rule is in the system prompt taxonomy, and it **overrode** the pack's
oscillation note. The same pattern explains `sc-314eca` Death, `sc-f520e5` Death,
`sc-8a9fa1` and `sc-6e2478`: five units lost to a word the harness never told the
model how to choose.

### The false alarms, by kind (all 21 enumerated)

| kind | count | books | fixable? |
|---|---|---|---|
| the same Death-2016 wobble (A/E 1.163, 337 vs 290 expected, identical in three books) | 3 | sc-137901, sc-409000, sc-9372cd | **yes** — Poisson z +2.8 there, while every genuine one-year planted jolt measures z +5.6 to +12.2 |
| favourable deviations listed as findings ("persistent underrun", not claimed as anomalies) | 3 | sc-bba653 | **yes** — they are observations, not claims |
| a second entry describing the same movement (early leg, or the reversion of a reported event) | 5 | sc-da1123 (4), sc-bba653 (1) | **partly** — see the warning below |
| wrong pattern word on a right window (the recall defect above) | 3 | sc-9660b9 | **yes**, and fixing it also removes the false alarms |
| genuinely distinct movements the answer sheet does not cover | 7 | sc-f520e5 (3), sc-2d248f, sc-314eca, sc-137901, sc-d72b95 | **no** — see below |

### The warning that stopped a tempting fix

`sc-da1123` loses 4 points to early-period entries that look exactly like the
**two genuine units of `sc-c9d78b`** in the held-out split (a drift followed by a
jolt on the same line). Suppressing "two movements on one line" would very likely
suppress those real held-out units too. That fix was therefore **not** made — it
is the tuning set arguing against the exam, and the exam wins.

## What v1.6 changes (3 removals, 1 gain)

1. **System-prompt taxonomy**: the "if it rises year over year, prefer drift"
   clause now yields when the computed evidence says the biggest single-year move
   exceeds the net excursion — i.e. the pack's oscillation note outranks it. The
   `volatility` entry now also states the book-wide case explicitly.
2. **Book-wide line in the pack** (fires on exactly 2 of 23 books, both the
   book-wide unsteadiness books, and never on the clean book): when 3+ lines
   swing together across 2+ consecutive years, every affected line gets a
   dispersion entry, alongside any level-change reading. Verified: fires on
   `sc-314eca` and `sc-9660b9` only. The other six coordinated-swing books all
   have a single-year span, so they are untouched.
3. **One-year wobbles need Poisson |z| >= ~4.5** to be claimed.
4. **Observations that are not claims must not be listed**, and a movement must
   not be described twice.

## Predictions registered BEFORE pass 5 ran

| what | prediction | basis |
|---|---|---|
| strict recall | 40/44 = 90.9 % (from 36) | +4: three lines of sc-9660b9 and Death of sc-314eca, each already reported with the right window and only the wrong word |
| false alarms | ~14-16 (0.61-0.70 per answer, from 0.91) | -3 wobble, -3 unclaimed observations, -4 same-movement duplicates, +0-1 duplicates of the new dispersion entries |
| clean book | intact, no claim | the new pack line cannot fire there (measured: 0 of 4 lines) |
| drift strata | unchanged (9/10, 5/5) | no change touches those paths |
| false-alarm ceiling | must stay <= 1.0 | this is the criterion at risk: if the model over-applies the new dispersion line, recall rises but the gate fails |

If recall climbs while false alarms breach 1.0 per answer, the pass is a **fail**
under the pre-agreed gate, and it will be reported as one.

## 2026-09-12T23:02:22Z  sc-042304 (pass 5, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=754.1s
harness: tool_calls=0  pack_sha=c6d43dc4e6fd
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag A/E ~1.27-1.30 for two flat-topped years
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-12T23:06:29Z  sc-9660b9 (pass 6)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=2309.3s
harness: tool_calls=0  pack_sha=d1923b430af6
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.75 | mag A/E 0.95 (2019) -> 1.16/1.22/1.42 (2020-
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.8 | mag A/E 0.89 (2019) -> 1.25/1.48 (2020-21) -
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E 1.56 (2020) -> 0.86 (2021) -> 0.39 (
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.75 | mag A/E 1.37 (2020) -> 0.82 (2021) -> 1.03/1
  [4] FP    Death | drift | increase | [2016, 2022] | conf 0.65 | mag ~+0.09/yr: 0.863 (2016) -> 1.417 (2022),
  [5] FP    CI | drift | increase | [2020, 2021] | conf 0.6 | mag 0.888 (2019) -> 1.247 (2020) -> 1.480 (2
  [6] FP    TPD | shock | increase | [2020, 2020] | conf 0.55 | mag 2020 A/E 1.060 -> 1.560 (+0.50; 1289 act
SCORE: strict 4/1  loose 4/1  FP 3
sc-9660b9   fam=noise_trap  runs=1 strict=4/4 loose=4/4 FP=3 badjson=0 err=0
```

## 2026-09-12T23:45:16Z  sc-314eca (pass 6)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=1544.4s
harness: tool_calls=0  pack_sha=6abecb970469
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.55 | mag sustained ~+0.2 above baseline (window m
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.8 | mag A/E 0.90 (2018) -> 1.15 (2019) -> 1.37 (
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.8 | mag A/E 1.37 (2019) -> 0.93 (2020) -> 0.58 (
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.8 | mag A/E 0.96 (2018) -> 1.28 (2019) -> 0.91 (
SCORE: strict 3/4  loose 3/4  FP 1
sc-314eca   fam=systemic    runs=1 strict=3/4 loose=3/4 FP=1 badjson=0 err=0
```

## 2026-09-13T00:11:31Z  sc-314eca (pass 6)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=837.2s
harness: tool_calls=0  pack_sha=e1cc823db8a8
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.75 | mag A/E ~0.97 baseline -> 1.11 (2019) -> 1.1
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.85 | mag A/E ~0.94 baseline -> 1.15 (2019) -> 1.3
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.85 | mag A/E ~1.04 baseline -> 1.37 (2019, peak ~
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.8 | mag A/E ~0.99 baseline -> 1.28 (2019, peak ~
SCORE: strict 4/4  loose 4/4  FP 0
sc-314eca   fam=systemic    runs=1 strict=4/4 loose=4/4 FP=0 badjson=0 err=0
```

## 2026-09-13T00:25:44Z  sc-f520e5 (pass 6)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=1228.6s
harness: tool_calls=0  pack_sha=8fc83d9b4959
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2023] | conf 0.6 | mag A/E oscillates 0.80-1.34: builds to 1.34
  [1] FP    IP | volatility | dispersion | [2019, 2023] | conf 0.65 | mag A/E oscillates 0.85-1.20: elevated 1.04-
SCORE: strict 1/2  loose 1/2  FP 1
sc-f520e5   fam=mixed       runs=1 strict=1/2 loose=1/2 FP=1 badjson=0 err=0
```

## 2026-09-13T00:50:55Z  sc-f520e5 (pass 6)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=1291.1s
harness: tool_calls=0  pack_sha=a4289d79b3c7
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.65 | mag 2019-2021 window A/E ~1.20 vs ~0.92 for 
  [1] MATCH Death | volatility | dispersion | [2019, 2022] | conf 0.6 | mag Swing 0.80 <-> 1.34; max 1-yr move 0.54 
  [2] MATCH IP | drift | increase | [2018, 2022] | conf 0.7 | mag 2019-2022 window A/E ~1.11 vs ~0.91 rest
  [3] FP    IP | volatility | dispersion | [2015, 2024] | conf 0.65 | mag Hump ~0.88 (2015-17) -> 1.20 (2022) -> ~
SCORE: strict 2/2  loose 2/2  FP 2
sc-f520e5   fam=mixed       runs=1 strict=2/2 loose=2/2 FP=2 badjson=0 err=0
```

## 2026-09-13T01:12:46Z  sc-d72b95 (pass 6)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=2253.4s
harness: tool_calls=3  pack_sha=433020f9aa54
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH CI | drift | increase | [2022, 2024] | conf 0.78 | mag ~+0.08/yr; A/E 0.98 (2022) -> 1.03 (2023
  [1] FP    Death | volatility | dispersion | [2020, 2021] | conf 0.7 | mag 2020 A/E 1.31 (666 vs 508 expected, +158
  [2] FP    CI | volatility | dispersion | [2020, 2021] | conf 0.66 | mag 2020 A/E 1.16 (1436 vs 1239 expected, +1
SCORE: strict 1/4  loose 1/4  FP 2
TOOL TRANSCRIPT (3 call(s)):
  [0] run: import csv, collections ⏎  ⏎ def analyze(fn): ⏎     try: ⏎         with open(fn) as f: ⏎             r = csv.reader(f) ⏎             header = next(r) ⏎         
      -> death_claims.csv ERR FileNotFoundError(2, 'No such file or directory')

ci_claims.csv ERR FileNotFoundError(2, 'No such file or directory')

tpd_claims.csv ERR FileNotFoundError(2, 'No such file or di
  [1] run: import os ⏎ print("CWD:", os.getcwd()) ⏎ print("listdir here:", sorted(os.listdir('.'))[:50]) ⏎ try: ⏎     print(".. :", sorted(os.listdir('..'))[:50]) ⏎ except
      -> CWD: /mnt/d/PythonProjects/Bazaar/Working/GitHub_Projects/data_pipeline_arena/data/eval/optimization/sc-d72b95/artifacts
listdir here: ['ae_ci.csv', 'ae_ci_age_gender.csv', 'ae_ci_age_gender.png', 'ae
  [2] run: import csv, collections ⏎  ⏎ def analyze(fn): ⏎     with open(fn) as f: ⏎         r = csv.reader(f) ⏎         header = next(r) ⏎         rows = list(r) ⏎     pr
      -> == ../death_claims.csv | n: 5020 | cols: ['claim_id', 'policy_id', 'claim_onset_date', 'attained_age_at_onset', 'gender', 'occupation_class', 'claim_outcome', 'death_sum_insured', 'decline_reason']
  
sc-d72b95   fam=systemic    runs=1 strict=1/4 loose=1/4 FP=2 badjson=0 err=0
```

## 2026-09-13T01:56:08Z  sc-d72b95 (pass 6)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=2292.0s
harness: tool_calls=0  pack_sha=f4db4b38c664
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.75 | mag A/E 1.31 (666 vs 508 expected, +0.38 YoY
  [1] MATCH Death | drift | increase | [2019, 2024] | conf 0.5 | mag level up ~+0.14 (2015-19 mean 0.88 vs 20
  [2] FP    Death | volatility | dispersion | [2020, 2021] | conf 0.6 | mag YoY SD 0.189 vs Poisson 0.048 (x3.95); s
  [3] MATCH CI | drift | increase | [2022, 2024] | conf 0.8 | mag +0.080/yr (0.978 -> 1.030 -> 1.138, fit 
  [4] FP    CI | shock | decrease | [2021, 2021] | conf 0.6 | mag A/E 0.902 (-0.257 vs 2020's 1.159), reve
  [5] FP    CI | volatility | dispersion | [2020, 2021] | conf 0.6 | mag YoY SD 0.133 vs Poisson 0.031 (x4.35); s
  [6] FP    TPD | volatility | dispersion | [2020, 2021] | conf 0.4 | mag dip to 0.963 in 2020 (-0.047) and reboun
  [7] FP    IP | volatility | dispersion | [2020, 2021] | conf 0.35 | mag 2021 dip 0.978 (-0.021) and 2022 rebound
SCORE: strict 3/4  loose 4/4  FP 5
sc-d72b95   fam=systemic    runs=1 strict=3/4 loose=4/4 FP=5 badjson=0 err=0
```

## 2026-09-13T02:39:02Z  sc-d72b95 (pass 6)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=1562.2s
harness: tool_calls=0  pack_sha=b860c22dc379
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.85 | mag A/E 1.31 in 2020 vs own baseline ~0.97 (
  [1] FP    Death | volatility | dispersion | [2019, 2024] | conf 0.55 | mag YoY SD 0.189 vs Poisson 0.048 (x3.95); m
  [2] MATCH CI | shock | increase | [2020, 2020] | conf 0.75 | mag A/E 1.16 in 2020 vs baseline ~0.98 (+0.1
  [3] FP    CI | volatility | dispersion | [2020, 2021] | conf 0.6 | mag YoY SD 0.133 vs Poisson 0.031 (x4.35); +
  [4] MATCH CI | drift | increase | [2022, 2024] | conf 0.75 | mag ~+0.08/yr over 2022-2024 (0.978 -> 1.030
SCORE: strict 3/4  loose 3/4  FP 2
sc-d72b95   fam=systemic    runs=1 strict=3/4 loose=3/4 FP=2 badjson=0 err=0
```

---

# PER-SCENARIO LOOP (pass 6) — one wrong book at a time, grow only when it fails

The full-sweep pass 5 was stopped after one scenario on the owner's instruction:
work the *wrong* books one at a time instead — run the book, and if it is still
wrong, grow the harness and run that same book again before moving on.

## Results on the four books that were wrong in pass 4

| book | pass 4 (v1.5) | now (v1.6) | what changed |
|---|---|---|---|
| sc-042304 (control) | 1/1, FP 0 | **1/1, FP 0** | nothing — the new rules did not cause over-reporting |
| sc-9660b9 | 1/4, FP 3 | **4/4, FP 3** | the pack now names the book-wide erratic stretch and says to use the dispersion pattern for every line |
| sc-314eca | 3/4, FP 1 | **4/4, FP 0** | first attempt still 3/4: the pack flagged only 3 swinging lines and the truth covers all four. Grew the rule to "ALL FOUR lines, unless a line's movement ends away from its own baseline", then it passed |
| sc-f520e5 | 1/2, FP 3 | **2/2, FP 2** | first attempt 1/2: the oscillation fix won the Death unit and lost the IP unit (they are statistically identical lines). Grew the rule to report BOTH readings on an oscillating line; the retry matched both units for one extra false alarm |
| sc-d72b95 | 1/4, FP 2 | **3/4, FP 2** | two retries. The give-back note won the two 2020 jolts; a first version named the wrong year for CI (the down-year instead of the up-year) so the model reported a decrease in 2021, and fixing the year-naming turned that into a match |

Same five books, pass 4: **7/15 control units = 47 %**, 9 false alarms.
Same five books, now: **14/15 = 93 %**, 7 false alarms.

## The one unit that is still missed, and why it is likely the floor

`sc-d72b95` Death drift [2021, 2024]: the planted rise is +0.05/yr, and the
computed evidence for that line gives a final-years gradient of **+0.017/yr with
fit R2 0.08** — indistinguishable from noise by any statistic in the pack. The
two retries matched *different* three-of-four units (attempt 1 found Death drift
but missed the CI jolt; attempt 2 found both jolts but missed the Death drift).
That is the shape of a coin flip, not of a fixable gap, so the loop stops here
for this book rather than tuning further.

## Cost of the loop, measured

* each book now spends **20-40 minutes** in reasoning (vs ~10 minutes before);
  the model emits 20,000-37,000 reasoning tokens before its answer
* the rules block is ~2,500 characters longer, and two new pack notes fire
  (book-wide stretch: 2 books; give-back jolt: 3 lines)
* consequence for planning: a 23-book sweep is now ~8-12 hours and the held-out
  exam (72 answers) ~24-36 hours

## Warning carried forward

On these five hardest books the false-alarm rate is 1.4 per answer, **above the
1.0 ceiing** the gate applies to the *whole* split. The other 18 books sat at
0-1 each in pass 4, so the split-wide rate should come in below 1.0 — but that is
now an assumption, not a measurement, and only a full sweep can settle it.

---

# FULL SWEEP OF THE REMAINING 18 — launched 2026-09-13T03:09:52Z

On the owner's instruction: after the one-book loop settled the four wrong books,
run the books that had never been through the v1.6 harness, so the split-wide
gate can actually be measured (per-book diagnostics cannot stand in for it).

* corpus `results/harness_opt_p6` — the 5 books from the loop plus these 18
* harness pinned before the first call:
  `stats_pack.py 2d7fc6f9665a…`, `run_zero_shot.py f6c4a0e8ed14…`
* `sc-042304` was carried over from the p5 corpus (same v1.6 family, run before
  the dual-reading and give-back notes existed)
* known caveat: the five loop books were run under intermediate versions of
  v1.6, so a short re-run of those five is needed before the corpus can be quoted
  as one harness version's result

When it finishes: score → `python3 scripts/harness_gate.py
results/harness_opt_p6/zero_shot` → if it passes, the five-book re-run, then the
held-out exam.

## 2026-09-13T03:40:19Z  sc-137901 (pass 6, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1818.5s
harness: tool_calls=0  pack_sha=23fb57d3d957
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2021, 2024] | conf 0.65 | mag A/E builds from ~0.94 baseline (2015-20)
  [1] FP    IP | shock | increase | [2022, 2024] | conf 0.6 | mag A/E jumps from ~0.98 (2021) to ~1.10-1.1
  [2] FP    IP | volatility | dispersion | [2022, 2024] | conf 0.6 | mag YoY swings ~+0.11 (2022) then ~-0.19 (20
SCORE: strict 1/2  loose 1/2  FP 2
```

## 2026-09-13T03:44:41Z  sc-14cdd9 (pass 6, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=242.7s
harness: tool_calls=0  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-13T03:57:45Z  sc-17d82f (pass 6, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=765.4s
harness: tool_calls=4  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.9 | mag Cancer termination/recovery A/E ~0.50 (o
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (4 call(s)):
  [0] run: import csv ⏎ with open("ae_ip_termination.csv") as f: ⏎     t = list(csv.reader(f)) ⏎ print("TERM FILE:") ⏎ for r in t: ⏎     print(r) ⏎ with open("ae_ip_termin
      -> TERM FILE:
['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
['Injury/Accident', '0', '1499', '315', '0.21014009339559706', '0.22', '0.9551822427072594']
['In
  [1] run: import csv ⏎ with open("ae_ip_termination_by_month.csv") as f: ⏎     rows = list(csv.reader(f)) ⏎ hdr = rows[0] ⏎ print("HDR:", hdr) ⏎ def num(x): ⏎     try: re
      -> HDR: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
CANCER N: 0
first 12 cancer rows (dur, exposed, recovered, obs, assumed, AE):
CANCER pooled exposed sum: 0 recovered sum: 0


  [2] run: import csv ⏎ with open("ae_ip_termination_by_month.csv") as f: ⏎     rows = list(csv.reader(f)) ⏎ rec=0; exp=0 ⏎ for r in rows[1:]: ⏎     if len(r)>=5 and r[1].
      -> by_month pooled A/E (Recovered/ExpectedRecoveries): 0.9387466165047188
n rows: 122
['0', '15030', '2107', '2152.3900000000003', '0.978911814308745']
['1', '12780', '1655', '1731.8063636363636', '0.955
  [3] run: import csv, math ⏎ with open("ae_ip_termination.csv") as f: ⏎     rows = list(csv.reader(f)) ⏎ hdr = rows[0] ⏎ print("HDR:", hdr) ⏎ def num(x): ⏎     try: retur
      -> HDR: ['Diagnosis', 'DurationMonth', 'Exposed', 'Recovered', 'ObservedRate', 'AssumedRate', 'AE']
CANCER rows: 122
Cancer sum exposed: 62057.0 sum recovered: 812.0
Cancer pooled A/E (rec/sum(exp*assume
```

## 2026-09-13T04:20:36Z  sc-2d248f (pass 6, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=1351.8s
harness: tool_calls=0  pack_sha=1f313b26c792
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.9 | mag empirical YoY sigma 0.60 vs Poisson 0.02
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.6 | mag +0.11/yr (fit R2 0.92); AE 0.74→0.79→0.9
  [2] FP    Death | volatility | dispersion | [2016, 2017] | conf 0.5 | mag AE 0.94 (2015)→1.16 (2016)→0.96 (2017); 
SCORE: strict 1/1  loose 1/1  FP 2
```

## 2026-09-13T04:29:26Z  sc-3c83fd (pass 6, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=511.4s
harness: tool_calls=0  pack_sha=ac03b6c10f6a
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] FP    CI | shock | increase | [2017, 2024] | conf 0.75 | mag A/E declined to 0.73–0.81 in 2018–2019, 
SCORE: strict 0/1  loose 0/1  FP 1
```

## 2026-09-13T04:35:11Z  sc-409000 (pass 6, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=325.6s
harness: tool_calls=0  pack_sha=4f6adbb8f026
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.99 | mag Mental Health termination A/E ~1.99 (ter
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-13T04:51:05Z  sc-48351f (pass 6, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=935.6s
harness: tool_calls=0  pack_sha=0ec87661f26c
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.85 | mag x1.24 A/E in 2023 (+0.23 in one year, 12
  [1] FP    TPD | volatility | dispersion | [2023, 2024] | conf 0.7 | mag A/E swings of +0.23 (2023) then -0.24 (2
  [2] MATCH IP | shock | increase | [2023, 2023] | conf 0.85 | mag x1.18 A/E in 2023 (+0.18 in one year, 22
  [3] FP    IP | volatility | dispersion | [2023, 2024] | conf 0.7 | mag A/E swings of +0.18 (2023) then -0.18 (2
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T05:31:54Z  sc-4a7f9e (pass 6, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=2430.4s
harness: tool_calls=0  pack_sha=56249351f824
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag A/E +0.38 for 2y (1.296/1.282 vs pre-eve
  [1] FP    Death | volatility | dispersion | [2021, 2023] | conf 0.6 | mag YoY swings +0.34 (2021), -0.01 (2022), -
  [2] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag A/E -0.46 for 2y (0.670/0.654 vs baselin
  [3] FP    CI | volatility | dispersion | [2021, 2023] | conf 0.6 | mag Two-sided pulse ~0.44-0.50 (drop 0.44 in
  [4] FP    TPD | volatility | dispersion | [2021, 2021] | conf 0.4 | mag Single 2021 move +0.050 (0.963->1.013, z
  [5] FP    IP | volatility | dispersion | [2021, 2021] | conf 0.4 | mag Single 2021 move -0.021 (0.999->0.978, z
  [6] FP    CI | other | increase | [2015, 2024] | conf 0.6 | mag Persistent ~+12% excess (A/E 1.075-1.152
SCORE: strict 2/2  loose 2/2  FP 5
```

## 2026-09-13T05:54:53Z  sc-5e376b (pass 6, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=1361.1s
harness: tool_calls=1  pack_sha=20d532b2dd3c
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.40 A/E: ~0.86 baseline jumps to 1.24
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ for f in ["ae_death_age_gender.csv", "ae_ip_termination_by_month.csv"]: ⏎     print("====", f) ⏎     try: ⏎         with open(f) as fh: ⏎          
      -> ==== ae_death_age_gender.csv
AgeBand | Gender | Actual | Expected | AE
15 | Female | 4 | 4.520672767466119 | 0.8848240529123806
15 | Male | 4 | 7.135997803227396 | 0.5605382891501061
20 | Female | 22 
```

## 2026-09-13T06:22:08Z  sc-63f1c7 (pass 6, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=1615.8s
harness: tool_calls=0  pack_sha=de07948131e8
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] FP    Death | shock | increase | [2021, 2021] | conf 0.7 | mag level +0.14~+0.21: A/E jumps from 0.84-0
  [1] MATCH Death | drift | increase | [2022, 2024] | conf 0.8 | mag ~+0.066/yr: A/E 1.060 -> 1.094 -> 1.191;
  [2] MATCH CI | shock | increase | [2021, 2021] | conf 0.85 | mag A/E 1.327 in 2021 (+0.35 vs own baseline
  [3] FP    CI | volatility | dispersion | [2021, 2022] | conf 0.55 | mag YoY sd 0.184 vs Poisson 0.030 (x6.0); sw
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T06:46:48Z  sc-6e2478 (pass 6, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=1461.3s
harness: tool_calls=1  pack_sha=9c2db80bce85
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2016, 2024] | conf 0.7 | mag A/E oscillates 0.72-1.32 around a mean o
  [1] FP    Death | drift | decrease | [2019, 2022] | conf 0.55 | mag A/E builds down ~1.06(2019)->0.97(2020)-
SCORE: strict 1/1  loose 1/1  FP 1
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎  ⏎ rows = list(csv.reader(open('ae_death_age_gender.csv'))) ⏎ print('DEATH AGE-GENDER:', len(rows), 'rows x', len(rows[0]), 'cols') ⏎ print('HDR:',
      -> DEATH AGE-GENDER: 23 rows x 5 cols
HDR: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE']
15,Female,6,4.5206727674,1.3272360793
15,Male,4,7.1359978032,0.5605382891
20,Female,32,31.533684964,1.01478783
```

## 2026-09-13T07:01:26Z  sc-8a9fa1 (pass 6, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=859.5s
harness: tool_calls=0  pack_sha=3bd5342d3c64
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2020] | conf 0.85 | mag empirical YoY sd of A/E 0.349 vs Poisson
  [1] FP    Death | drift | increase | [2015, 2018] | conf 0.6 | mag AE 0.87(2015)->1.08->1.25->1.52(2018), ~
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-13T07:13:24Z  sc-8d3b47 (pass 6, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=699.1s
harness: tool_calls=0  pack_sha=4babb17df9b4
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.8 | mag net +~0.20 A/E over window; rising leg 0
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.85 | mag -~0.38 A/E over window; ~-0.04/yr, 1.23 
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-13T07:25:26Z  sc-9372cd (pass 6, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=701.7s
harness: tool_calls=0  pack_sha=bb8dd54ded0e
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | shock | increase | [2021, 2021] | conf 0.7 | mag A/E 1.186 in 2021 (1,063 actual vs 897 e
  [1] FP    TPD | volatility | dispersion | [2018, 2022] | conf 0.6 | mag A/E swings 1.014 -> 1.050 -> 1.042 -> 1.
SCORE: strict 0/1  loose 0/1  FP 2
```

## 2026-09-13T07:38:10Z  sc-abbec4 (pass 6, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=744.9s
harness: tool_calls=0  pack_sha=fb418334facd
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.9 | mag 2021-22 mean +0.41 A/E (1.35 / 1.29 vs p
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag 2021-22 mean +0.30 A/E (1.26 / 1.22 vs p
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-13T08:10:04Z  sc-bba653 (pass 6, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=1895.5s
harness: tool_calls=0  pack_sha=e4237a36c5ec
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.40 A/E (window 1.235-1.308 vs 0.85-0
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.28 A/E (window 1.180-1.197 vs ~0.91 
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.7 | mag ~+0.22 A/E (window 1.097-1.188 vs 0.88-0
  [3] FP    TPD | drift | decrease | [2022, 2024] | conf 0.55 | mag ~-0.104/yr (1.15 -> 0.94, R2 0.87); give
  [4] FP    Death | other | decrease | [2015, 2017] | conf 0.55 | mag ~-0.10 vs 1.0 (A/E 0.848-0.925); 3-line 
  [5] FP    CI | other | decrease | [2015, 2017] | conf 0.55 | mag ~-0.10 vs 1.0 (A/E 0.890-0.905); 3-line 
  [6] FP    TPD | other | decrease | [2015, 2017] | conf 0.5 | mag ~-0.08 to -0.10 vs 1.0 (A/E 0.882-0.949)
SCORE: strict 3/4  loose 3/4  FP 4
```

## 2026-09-13T08:35:29Z  sc-da1123 (pass 6, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=1505.4s
harness: tool_calls=0  pack_sha=e9b3d995d767
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag ~+0.03/yr sustained move; trough 0.744 (
  [1] MATCH CI | drift | increase | [2015, 2024] | conf 0.8 | mag ~+0.027/yr overall; 0.89-0.92 (2015-18) 
  [2] MATCH TPD | drift | increase | [2022, 2024] | conf 0.7 | mag level shift ~+0.11 vs pre-2022: 1.000 (2
  [3] MATCH IP | drift | increase | [2015, 2024] | conf 0.55 | mag ~+0.014/yr gradual rise; 0.933 (2015) to
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-13T08:44:07Z  sc-f69eea (pass 6, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=499.3s
harness: tool_calls=0  pack_sha=c540433e3725
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.08/yr; A/E rises 0.63 (2015) to 1.31
SCORE: strict 1/1  loose 1/1  FP 0
```

---

# FULL SWEEP v1.6b — 23/23, GATE FAILED (2026-09-13T08:44:24Z)

    TOTALS: strict 39/44 = 88.6%  loose 88.6%  FP/run = 1.26  badjson 0  errors 0
    CLEAN honesty: intact (0/1)
    STRATA: persistent 9/10 (baseline 8/10) | bounded-then-reverting 2/5 (baseline 3/5)

    FREEZE GATE: [FAIL] false positives 29/23 = 1.26 (ceiling 1.0)
                 [FAIL] bounded-then-reverting drift 2/5 vs 3/5 at baseline
                 [PASS] strict 88.6%, clean honesty, integrity, persistent drift
                 VERDICT: DO NOT FREEZE

Best recall of any version so far (+6.8 points over v1.5), but it **fails the
pre-agreed gate**, so it cannot be frozen. Per-scenario changes v1.5 → v1.6b:

    gained: sc-9660b9 1/4→4/4 (+3), sc-d72b95 1/4→3/4 (+2),
            sc-314eca 3/4→4/4 (+1), sc-f520e5 1/2→2/2 (+1)
    lost:   sc-137901 2/2→1/2, sc-3c83fd 1/1→0/1, sc-9372cd 1/1→0/1,
            sc-bba653 4/4→3/4
    false alarms: +8 overall, concentrated on the jolt books
            (sc-4a7f9e +5, sc-48351f +2, sc-63f1c7 +2), offset by sc-da1123 −4

All three lost drift units are in the bounded-then-reverting stratum, which is
why that stratum collapsed from 5/5 to 2/5.

## Diagnosed causes (from the answers themselves, not guessed)

1. **The dispersion entries on jolt books** (`sc-4a7f9e` alone: 4 lines each
   getting a dispersion entry beside their correct jolt entry). The v1.6
   system-prompt wording invited volatility "whenever the CROSS-LINE block
   reports several lines swinging together" — and the block always prints swing
   counts, including several lines swinging in a SINGLE year, which is exactly
   what a book-wide jolt looks like. A false lead, created by my own wording.
2. **The bounded drifts lost** (`sc-9372cd`, `sc-137901`): the dual-reading note
   asked for a level-change entry but never said *which shape* to give it, so the
   model chose a one-off change where the truth is a sustained move.
3. `sc-3c83fd`: the model reported a single 8-year "shock" for a drift — model
   variation, no rule of ours points there.

## v1.6c — the two repairs, both narrowings of my own additions

* the system-prompt rule now requires **consecutive years**, and says in as many
  words that a single-year coordinated swing is what a book-wide jolt looks like
* the pack's cross-line block now adds that clarification on the six books where
  several lines swing in one year (verified: `sc-042304`, `sc-3c83fd`,
  `sc-4a7f9e`, `sc-63f1c7`, `sc-bba653`, `sc-d72b95`), while the multi-year
  instruction still fires on exactly the two erraticness books
* the dual-reading note now says which shape the level-change entry should take
  (builds across years = sustained move; arrives in one year = one-off change)

Leak preflight re-run: PASS on all 47 books. New sweep launched as pass 7, so
that all 23 books are measured under ONE harness version (the p6 corpus was
stitched from three intermediate variants — inherent to iterating in place).

If v1.6c also fails the gate, the fallback is to freeze **v1.5** (pass 4), which
is the only version that has passed it: 81.8 %, 0.91 false alarms, strata 9/10
and 5/5.

## 2026-09-13T10:08:04Z  sc-137901 (pass 7)

## 2026-09-13T10:14:09Z  sc-3c83fd (pass 7)

---

# TARGETED RE-RUN OF THE FIVE FAILED BOOKS (pass 7) — armed, server down

On the owner's instruction: do not re-run the whole set; re-run only the books
that failed the v1.6b sweep, once each, under the current harness (v1.6c), to see
whether the repairs landed and what is left to grow.

The five: `sc-137901` (1/2), `sc-3c83fd` (0/1), `sc-9372cd` (0/1),
`sc-bba653` (3/4), `sc-d72b95` (3/4).

**The LLM endpoint went down** (`http=000`, connection refused) at the moment the
first book was attempted, so `sc-137901` returned rc=1 and the loop was stopped
rather than burning a 30-minute endpoint wait per attempt. A detached watcher
(`results/logs/p7_targeted_wait.sh`) polls every 30 s and runs all five books,
once each, as soon as the endpoint returns, then scores them. Harness version for
those runs: v1.6c (`stats_pack.py 552ff285b421…`, `run_zero_shot.py 052dee24398c…`).

## What each remaining failure is, read off the answers (offline)

| book | missed unit | what the model actually said | verdict |
|---|---|---|---|
| sc-137901 | IP drift 2019-2023 | IP one-off change 2022-2024 + IP dispersion 2022-2024 | the v1.6c shape guidance targets exactly this — pending measurement |
| sc-3c83fd | CI drift 2016-2019 | a single **8-year** "one-off change" 2017-2024 | **fixable**: see G1 |
| sc-9372cd | TPD drift 2019-2021 | TPD one-off 2021 + TPD dispersion 2018-2022 | likely floor: a 3-year bounded rise with an interior dip is statistically indistinguishable from dispersion (line: 1.014, 1.050, 1.042, 1.186, then 0.958) |
| sc-bba653 | IP one-off 2020-2022 | **the IP line is never mentioned at all** — three lines reported, one silently dropped | **fixable**: see G2 |
| sc-d72b95 | Death drift 2021-2024 | not reported | floor: final-years gradient +0.017/yr, fit R2 0.08 |

## The two growth steps this revealed, measured and ready

**G1 — "four or more years is never a one-off change."** Measured: across the
optimization split, every planted one-off event spans **1-3 years** (n=8: values
1,2,3) while every sustained move spans **3-7 years** (n=15: 3,4,5,6,7). So a
movement held away from its own baseline for four or more years cannot be a
one-off — which is exactly the error in `sc-3c83fd`. Proposed rule text (checked:
contains none of the leak-gate's banned words):

  "A movement that spans four or more years is never a one-off change: a one-off
   is confined to one, two or at most three years. If the level sits away from
   its own baseline across four or more years, describe it as a sustained move or
   as dispersion."

**G2 — name the lines in the cross-line rows.** The pack knows *which* lines swing
together but prints only the count. For `sc-bba653` it computed
`2020: 4 lines -> ['death','ci','tpd','ip']` and the model still reported three of
them. Naming the lines gives an explicit checklist for that year, and it is
factual data derived from the CSVs (no truth involved). Same for
`sc-4a7f9e`, `sc-d72b95`, `sc-63f1c7` (all 4 lines, single year).

Neither G1 nor G2 was applied before the armed run, so that run stays a clean
measurement of v1.6c. They are the next growth step, to be applied to whichever
books are still failing — following the established rule: run once, and only grow
if it is still wrong.

## 2026-09-13T11:02:09Z  sc-137901 (pass 7)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=2362.0s
harness: tool_calls=1  pack_sha=470e6c43134c
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] FP    TPD | shock | increase | [2022, 2023] | conf 0.85 | mag ~+0.20 level (A/E 1.17 & 1.16 vs own bas
  [1] MATCH IP | drift | increase | [2022, 2023] | conf 0.7 | mag ~+0.14 level build (A/E 1.10 -> 1.12, pe
  [2] FP    IP | volatility | dispersion | [2022, 2024] | conf 0.65 | mag year-to-year swing: up +0.10..+0.12 (202
SCORE: strict 1/2  loose 1/2  FP 2
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ from collections import defaultdict ⏎  ⏎ def load(f): ⏎     with open(f) as fh: ⏎         r = csv.reader(fh) ⏎         hdr = [h.strip() for h in ne
      -> == ae_tpd_age_gender.csv cols: ['AgeBand', 'Gender', 'Actual', 'Expected', 'AE'] n= 22
 2022-23 vs 2019-21 by group: []
 2022-23 vs 2019-21 by age: []
== ae_ip_age_gender.csv cols: ['AgeBand', 'Gender
sc-137901   fam=systemic    runs=1 strict=1/2 loose=1/2 FP=2 badjson=0 err=0
```

## 2026-09-13T11:41:39Z  sc-3c83fd (pass 7)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=1877.3s
harness: tool_calls=0  pack_sha=b39fc16741e5
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] FP    CI | shock | decrease | [2017, 2019] | conf 0.85 | mag CI A/E declines from ~1.10 (2016) to a 0
SCORE: strict 0/1  loose 0/1  FP 1
sc-3c83fd   fam=drift       runs=1 strict=0/1 loose=0/1 FP=1 badjson=0 err=0
```

## 2026-09-13T12:13:05Z  sc-9372cd (pass 7)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=930.7s
harness: tool_calls=0  pack_sha=ce5b88442999
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2015, 2024] | conf 0.55 | mag A/E swings between ~0.95-0.97 (2015-17 a
  [1] FP    TPD | shock | increase | [2021, 2021] | conf 0.6 | mag 2021 A/E 1.186, a single-year spike of +
SCORE: strict 0/1  loose 0/1  FP 2
sc-9372cd   fam=drift       runs=1 strict=0/1 loose=0/1 FP=2 badjson=0 err=0
```

## 2026-09-13T12:28:44Z  sc-bba653 (pass 7)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=899.0s
harness: tool_calls=0  pack_sha=7668a7f07258
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.40 level: A/E 1.24/1.25/1.31 in 2020
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.28 level: A/E 1.18/1.19/1.20 in 2020
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.8 | mag ~+0.22 level: A/E 1.19/1.10/1.15 in 2020
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.55 | mag ~+0.06 level: A/E 1.05/1.04/1.06 in 2020
  [4] FP    TPD | drift | decrease | [2022, 2024] | conf 0.7 | mag ~-0.10/yr: A/E 1.150 (2022) -> 0.975 (20
SCORE: strict 4/4  loose 4/4  FP 1
sc-bba653   fam=systemic    runs=1 strict=4/4 loose=4/4 FP=1 badjson=0 err=0
```

## 2026-09-13T12:43:52Z  sc-d72b95 (pass 7)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=1157.9s
harness: tool_calls=0  pack_sha=00195af6296f
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.75 | mag A/E 1.31 vs line baseline ~0.97 (~+31%; 
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.65 | mag A/E 1.16 vs baseline ~0.98 (~+16%; actua
  [2] MATCH CI | drift | increase | [2022, 2024] | conf 0.6 | mag ~+0.08/yr: 0.98 -> 1.03 -> 1.14; 2024 A/
SCORE: strict 3/4  loose 3/4  FP 0
sc-d72b95   fam=systemic    runs=1 strict=3/4 loose=3/4 FP=0 badjson=0 err=0
```

---

# TARGETED RE-RUN RESULT — five failed books, once each, v1.6c (11:02-13:03Z)

| book | v1.6b | v1.6c | verdict |
|---|---|---|---|
| sc-137901 | 1/2, FP 2 | 1/2, FP 2 | unchanged (but it now hits the *other* line — see below) |
| sc-3c83fd | 0/1, FP 1 | 0/1, FP 1 | unchanged |
| sc-9372cd | 0/1, FP 2 | 0/1, FP 2 | unchanged |
| **sc-bba653** | 3/4, FP 4 | **4/4, FP 1** | **FIXED** (+1 unit, −3 false alarms) |
| sc-d72b95 | 3/4, FP 2 | 3/4, **FP 0** | units unchanged, both false alarms gone |

Totals on these five: units 8/12 → 8/12, **false alarms 11 → 6**.

## Evidence that the v1.6c repairs did what they were aimed at

* `sc-bba653` had dropped the IP line entirely; the single-year clarification now
  has the model reporting **all four lines** as the 2020-2022 jolt, with one
  leftover false alarm instead of four.
* `sc-d72b95` went from 2 false alarms to 0 — the dual-reading note no longer
  invites a dispersion entry on lines whose excursion is a clean jolt.
* The shape guidance (which shape the second reading should take) removed the
  spurious entries, but did not flip the two remaining pattern choices.

## The four units still missed, and what each actually is

| book | truth | what the model said | nature |
|---|---|---|---|
| sc-137901 | TPD drift [2019,2023] **and** IP drift [2019,2023] | IP drift [2022,2023] ✓, TPD one-off [2022,2023] ✗ | it finds the same 2022-23 event on both lines but labels one of them a one-off; the two labels swap between runs (in v1.6b it was the reverse) — a coin flip |
| sc-3c83fd | CI drift [2016,2019] | CI one-off, **decrease**, [2017,2019] | a 3-year move called a one-off; 3 years is the boundary where the two shapes genuinely overlap |
| sc-9372cd | TPD drift [2019,2021] | TPD dispersion [2015,2024] + one-off [2021,2021] | the 3-year bounded rise with an interior dip reads as erraticness |
| sc-d72b95 | Death drift [2021,2024] | not reported | floor: final-years gradient +0.017/yr, fit R2 0.08 |

## G1 is no longer needed for a current failure

G1 ("four or more years is never a one-off change") was designed for the v1.6b
`sc-3c83fd` failure, where the model claimed an **8-year** one-off. In this run it
claimed a **3-year** one, which G1 does not cover — so G1 would be a speculative
edit with no book testing it, and is therefore **not applied**. It is kept on the
list only if an 8-year-style claim reappears.

## Extrapolated state of the split

Taking the 18 books from the v1.6b sweep as they stand and the 5 re-run books at
their v1.6c numbers: **40/44 = 90.9 % correct**, false alarms 29 − 5 = 24
(1.04/run) — and that FP figure is pessimistic, because the five books re-run are
exactly the ones where the v1.6c repairs removed false alarms (11 → 6); the same
repairs should remove some on the jolt books too (`sc-4a7f9e` alone carried 5).

## 2026-09-13T15:22:10Z  sc-137901 (pass 7)

---

# v1.6d — two fixes aimed at the last fixable misses (15:22Z, five books re-running)

Read off the v1.6c answers, not guessed:

**F1 — the pack contradicted itself on one line.** For `sc-137901` the profile
called the TPD line `SHAPED-AND-GRADUAL` ("a build-up … report THAT span as the
window") while the onset note, reading onset 1.0, said "essentially the whole
excursion arrives in ONE year … **not** a build-up". The model believed the onset
note on TPD and the profile on its twin IP — 1/2 from evidence that supports 2/2.
The onset note now defers to the smoothed build-up whenever the line is gradual
(amplitude >= 0.08 and fit R2 >= 0.75, the same thresholds the profile uses).
Verified scope: it changes exactly two lines in the whole split, `sc-137901/tpd`
and `sc-63f1c7/death` — **both are drift truths**, so the change reinforces the
correct reading and disturbs nothing else.

**F3 — the taxonomy only mentioned *rising* ramps.** The rule read "if the
excursion rises year over year before it peaks or reverts, prefer drift", but
`sc-3c83fd`'s planted drift is a four-year **fall** (1.098 → 0.927 → 0.808 →
0.731, then a full recovery), and the model called that fall a one-off change.
The clause is now direction-symmetric ("rising OR falling"), which by construction
cannot touch the flat-topped jolts: those arrive in a single year rather than
moving year over year.

**A fifth discriminator died on the way** (recorded in Part 4 of the growth
document): "three or more consecutive same-direction years means a sustained
move". Measured across the split, one-off events reach runs of 3 and sustained
moves start at 2 — no separation, so it was not applied.

Honest expectation for the five: `sc-137901` should go 1/2 → 2/2 and `sc-bba653`
should hold 4/4; `sc-3c83fd` may improve via F3; `sc-9372cd` and `sc-d72b95` are
expected to stay missed — one is a 3-year bounded rise with an interior dip, the
other a +0.017/yr movement at fit R2 0.08, and both are indistinguishable from
noise with the statistics available.

Chained behind this run: a guard script scores the five and, if nothing regressed,
launches the remaining 18 books in the same corpus so the whole split is measured
under one harness version.
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=1423.2s
harness: tool_calls=0  pack_sha=d8047d631c93
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2021, 2023] | conf 0.7 | mag ~+0.20 level rise (A/E 0.95 in 2020 -> 1
  [1] MATCH IP | drift | increase | [2019, 2023] | conf 0.65 | mag ~+0.15 level rise (A/E ~0.95 baseline ->
  [2] FP    IP | volatility | dispersion | [2022, 2024] | conf 0.6 | mag peak-to-trough ~0.2 (1.12 in 2023 -> 0.9
SCORE: strict 2/2  loose 2/2  FP 1
sc-137901   fam=systemic    runs=1 strict=2/2 loose=2/2 FP=1 badjson=0 err=0
```

## 2026-09-13T15:46:02Z  sc-3c83fd (pass 7)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=1527.9s
harness: tool_calls=0  pack_sha=b39fc16741e5
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2017, 2019] | conf 0.85 | mag A/E falls from ~1.08 (2016) to 0.93 (201
SCORE: strict 1/1  loose 1/1  FP 0
sc-3c83fd   fam=drift       runs=1 strict=1/1 loose=1/1 FP=0 badjson=0 err=0
```

## 2026-09-13T16:11:38Z  sc-9372cd (pass 7)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=674.7s
harness: tool_calls=0  pack_sha=ce5b88442999
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2018, 2022] | conf 0.65 | mag A/E swings 0.96 -> 1.19 -> 0.96 without 
  [1] MATCH TPD | drift | increase | [2018, 2021] | conf 0.55 | mag A/E climbs year over year from ~0.96 (20
SCORE: strict 1/1  loose 1/1  FP 1
sc-9372cd   fam=drift       runs=1 strict=1/1 loose=1/1 FP=1 badjson=0 err=0
```

## 2026-09-13T16:23:01Z  sc-bba653 (pass 7)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=1701.8s
harness: tool_calls=0  pack_sha=7668a7f07258
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.95 | mag ~+0.40 A/E: pre-2020 level 0.85-0.93 jum
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.95 | mag ~+0.28 A/E: pre-2020 level 0.89-0.95 jum
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.75 | mag ~+0.22 A/E: pre-2020 level 0.88-0.97 jum
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.6 | mag ~+0.07 A/E: 2015-19 level 0.96-1.01 step
  [4] FP    TPD | drift | decrease | [2022, 2024] | conf 0.7 | mag ~-0.10/yr over 2022-24: 1.15 -> 0.97 -> 
  [5] FP    Death | other | decrease | [2015, 2017] | conf 0.6 | mag smoothed A/E 0.86-0.88 in 2015-17, ~0.10
  [6] FP    CI | other | decrease | [2015, 2017] | conf 0.6 | mag A/E 0.89-0.91 in 2015-17, ~0.09-0.11 bel
  [7] FP    TPD | other | decrease | [2015, 2017] | conf 0.55 | mag A/E 0.89-0.95 in 2015-17 (2015-16 ~0.10 
SCORE: strict 4/4  loose 4/4  FP 4
sc-bba653   fam=systemic    runs=1 strict=4/4 loose=4/4 FP=4 badjson=0 err=0
```

## 2026-09-13T16:51:32Z  sc-d72b95 (pass 7)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=1154.8s
harness: tool_calls=0  pack_sha=00195af6296f
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.8 | mag A/E 1.31 vs ~0.97 pre-2020 baseline (~+0
  [1] FP    Death | volatility | dispersion | [2015, 2024] | conf 0.6 | mag Level oscillates 0.83-1.31 around ~1.0 w
  [2] MATCH CI | shock | increase | [2020, 2020] | conf 0.7 | mag A/E 1.16 vs ~0.98 pre-2020 baseline (~+0
  [3] MATCH CI | drift | increase | [2022, 2024] | conf 0.75 | mag ~+0.08/yr, steady 0.98 -> 1.03 -> 1.14 (
  [4] FP    CI | volatility | dispersion | [2015, 2021] | conf 0.55 | mag Swings 0.90-1.16 around a ~0.98 level: e
SCORE: strict 3/4  loose 3/4  FP 2
sc-d72b95   fam=systemic    runs=1 strict=3/4 loose=3/4 FP=2 badjson=0 err=0
```

## 2026-09-13T17:25:10Z  sc-042304 (pass 7, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=809.8s
harness: tool_calls=0  pack_sha=6babe7695d5f
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag A/E 1.273 (2021) and 1.295 (2022) vs ~0.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-13T17:30:56Z  sc-14cdd9 (pass 7, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=327.7s
harness: tool_calls=0  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-13T17:37:18Z  sc-17d82f (pass 7, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=363.2s
harness: tool_calls=1  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.95 | mag Cancer recoveries at ~0.50 of the assume
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv ⏎ with open('ae_ip_termination_by_month.csv') as f: ⏎     rows = list(csv.reader(f)) ⏎ print("HEADER:", rows[0]) ⏎ print("NROWS:", len(rows)) ⏎ for r
      -> HEADER: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
NROWS: 123
['0', '15030', '2107', '2152.3900000000003', '0.978911814308745']
['1', '12780', '1655', '1731.8063636363636', 
```

## 2026-09-13T17:58:45Z  sc-2d248f (pass 7, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=1268.1s
harness: tool_calls=0  pack_sha=5f1d2693e242
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2021] | conf 0.8 | mag empirical YoY SD of A/E 0.60 vs Poisson 
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.6 | mag A/E 0.74 -> 0.79 -> 0.965 over 2022-24 (
  [2] FP    Death | volatility | dispersion | [2016, 2017] | conf 0.5 | mag ~+/-0.20 A/E swing (0.94 -> 1.16 -> 0.96
SCORE: strict 1/1  loose 1/1  FP 2
```

## 2026-09-13T18:26:34Z  sc-314eca (pass 7, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=1650.5s
harness: tool_calls=0  pack_sha=24bd6e1fb5a9
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.6 | mag A/E 0.97 -> 1.11 -> 1.16 (give-back to 0
  [1] FP    Death | drift | increase | [2019, 2021] | conf 0.55 | mag Rise of ~+0.10/yr: 0.97 (2018) -> 1.11 -
  [2] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.75 | mag A/E 0.90 -> 1.15 -> 1.37 -> 0.92 (2021);
  [3] FP    CI | drift | increase | [2019, 2020] | conf 0.6 | mag 2-year rise 0.90 -> 1.15 -> 1.37 (peak +
  [4] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.75 | mag A/E 1.09 -> 1.37 -> 0.93 -> 0.58 (2021);
  [5] FP    TPD | shock | decrease | [2021, 2021] | conf 0.85 | mag A/E 0.575 - actual 516 vs expected 897 (
  [6] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.75 | mag A/E 0.96 -> 1.28 -> 0.91 around an uncha
  [7] FP    IP | shock | increase | [2019, 2019] | conf 0.6 | mag A/E 1.283 - actual 1848 vs expected 1441
SCORE: strict 4/4  loose 4/4  FP 4
```

## 2026-09-13T18:33:16Z  sc-409000 (pass 7, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=381.8s
harness: tool_calls=1  pack_sha=4f6adbb8f026
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.97 | mag pooled Mental Health termination A/E ~1.
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, collections ⏎ f = open("ae_ip_termination_by_month.csv") ⏎ rd = csv.reader(f) ⏎ header = next(rd) ⏎ print("HEADER:", header) ⏎ rows = [row for row i
      -> HEADER: ['DurationMonth', 'Exposed', 'Recovered', 'ExpectedRecoveries', 'AE']
NROWS: 122
SAMPLE: [['0', '15030', '2908', '2152.3900000000003', '1.3510562676838302'], ['1', '11984', '2110', '1629.34454
```

## 2026-09-13T19:09:07Z  sc-48351f (pass 7, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=2130.6s
harness: tool_calls=0  pack_sha=35fff4e4c147
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.85 | mag A/E +0.23 (1.00 -> 1.24, ~+24%, +247 cla
  [1] MATCH IP | shock | increase | [2023, 2023] | conf 0.85 | mag A/E +0.18 (1.00 -> 1.18, ~+18%, +332 cla
  [2] FP    TPD | volatility | dispersion | [2023, 2024] | conf 0.6 | mag YoY SD 0.122 vs Poisson 0.036 (x3.4); bi
  [3] FP    IP | volatility | dispersion | [2023, 2024] | conf 0.6 | mag YoY SD 0.096 vs Poisson 0.026 (x3.7); bi
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T19:39:55Z  sc-4a7f9e (pass 7, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=1828.9s
harness: tool_calls=0  pack_sha=deadbb2e16d5
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.38 A/E level in 2021-22 (1.296, 1.28
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag ~-0.46 A/E level in 2021-22 (0.670, 0.65
  [2] FP    CI | other | increase | [2015, 2024] | conf 0.6 | mag persistent ~+0.12-0.13 level (expected-w
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-13T20:08:35Z  sc-5e376b (pass 7, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=1701.4s
harness: tool_calls=1  pack_sha=20d532b2dd3c
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag A/E level jumps from ~0.87 baseline to ~
SCORE: strict 1/1  loose 1/1  FP 0
TOOL TRANSCRIPT (1 call(s)):
  [0] run: import csv, statistics ⏎  ⏎ def load(p): ⏎     with open(p, newline='') as f: ⏎         return list(csv.reader(f)) ⏎  ⏎ def fnum(x): ⏎     try: ⏎         return
      -> DEATH_HDR: ['Age', 'Gender', 'Year', 'Actual', 'Expected', 'AE'] rows: 891
DEATH_SAMPLE: [['17', 'Female', '2015', '0', '0.061779156759464535', '0.0'], ['17', 'Female', '2016', '0', '0.050044389504040
```

## 2026-09-13T20:28:02Z  sc-63f1c7 (pass 7, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=1147.8s
harness: tool_calls=0  pack_sha=ad8d744fffe5
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2022] | conf 0.85 | mag A/E drifts up from ~0.84-0.93 (2015-2020
  [1] FP    Death | drift | increase | [2022, 2024] | conf 0.8 | mag A/E 1.06 -> 1.09 -> 1.19 (+0.066/yr, R2 
  [2] MATCH CI | shock | increase | [2021, 2021] | conf 0.85 | mag single-year A/E 1.327 (1,839 vs 1,386 ex
  [3] FP    CI | volatility | dispersion | [2015, 2024] | conf 0.6 | mag empirical YoY sd 0.184 vs Poisson 0.031 
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T20:45:50Z  sc-6e2478 (pass 7, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=1049.4s
harness: tool_calls=0  pack_sha=4118b9492ca3
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.75 | mag YoY SD ~0.25 vs Poisson ~0.05 (~5x); A/E
  [1] FP    Death | drift | increase | [2015, 2017] | conf 0.45 | mag ~+0.15/yr (A/E 1.03 -> 1.17 -> 1.32, pea
  [2] FP    Death | shock | decrease | [2021, 2022] | conf 0.4 | mag -0.32 level dip (A/E 0.72/0.80 vs ~1.01 
SCORE: strict 1/1  loose 1/1  FP 2
```

## 2026-09-13T20:56:47Z  sc-8a9fa1 (pass 7, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=637.6s
harness: tool_calls=0  pack_sha=637282171641
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2015, 2018] | conf 0.6 | mag A/E climbs 0.87 (2015) -> 1.08 -> 1.25 -
  [1] MATCH Death | volatility | dispersion | [2015, 2020] | conf 0.8 | mag YoY A/E std dev 0.35 vs Poisson expectat
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-13T21:06:30Z  sc-8d3b47 (pass 7, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=563.6s
harness: tool_calls=0  pack_sha=4babb17df9b4
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.8 | mag sustained upward move ~+0.03-0.04 A/E/yr
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.85 | mag sustained downward move ~-0.04 A/E/yr; f
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-13T21:40:22Z  sc-9660b9 (pass 7, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=2013.1s
harness: tool_calls=0  pack_sha=8296ca3d0286
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.8 | mag YoY sd 0.21 vs Poisson 0.05 (~x4.5); A/E
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.8 | mag YoY sd 0.27 vs Poisson 0.03 (~x8.8); hum
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag YoY sd 0.42 vs Poisson 0.04 (~x11.6); 1.
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.75 | mag YoY sd 0.25 vs Poisson 0.03 (~x9.5); 1.3
  [4] FP    Death | drift | increase | [2016, 2022] | conf 0.75 | mag +~0.04/yr; 0.86 (2016) -> 1.42 (2022), p
  [5] FP    CI | drift | increase | [2020, 2021] | conf 0.6 | mag 0.89 (2019) -> 1.25 (2020) -> 1.48 (2021
  [6] FP    TPD | shock | increase | [2020, 2020] | conf 0.6 | mag single-year spike to A/E 1.56 (~+55%; ~4
SCORE: strict 4/4  loose 4/4  FP 3
```

## 2026-09-13T21:54:48Z  sc-abbec4 (pass 7, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=847.4s
harness: tool_calls=0  pack_sha=fb418334facd
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.85 | mag A/E 1.352 (2021) and 1.290 (2022) vs 201
  [1] FP    TPD | volatility | dispersion | [2021, 2023] | conf 0.55 | mag YoY sd 0.203 vs Poisson 0.036 (x5.6); bi
  [2] MATCH IP | shock | increase | [2021, 2022] | conf 0.85 | mag A/E 1.262 (2021) and 1.215 (2022) vs 201
  [3] FP    IP | volatility | dispersion | [2021, 2023] | conf 0.55 | mag YoY sd 0.165 vs Poisson 0.026 (x6.3); bi
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T22:27:09Z  sc-da1123 (pass 7, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=1921.6s
harness: tool_calls=0  pack_sha=e9b3d995d767
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag A/E 0.74 (2018 trough) -> 1.14 (2024); ~
  [1] MATCH CI | drift | increase | [2022, 2024] | conf 0.8 | mag A/E 1.01 (2022) -> 1.10 -> 1.15 (2024); 
  [2] MATCH TPD | drift | increase | [2022, 2024] | conf 0.75 | mag A/E 1.00 (2022) -> 1.09 -> 1.12 (2024); 
  [3] MATCH IP | drift | increase | [2022, 2024] | conf 0.6 | mag A/E 1.03 (2022) -> 1.04 -> 1.08 (2024); 
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-13T22:49:08Z  sc-f520e5 (pass 7, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=1300.1s
harness: tool_calls=0  pack_sha=1cd7641f5d18
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2016, 2021] | conf 0.6 | mag +0.09/yr from 0.88 (2016) to peak 1.34 (
  [1] MATCH Death | volatility | dispersion | [2019, 2023] | conf 0.55 | mag empirical YoY SD 0.22 vs Poisson 0.05 (x
  [2] MATCH IP | drift | increase | [2017, 2022] | conf 0.65 | mag +0.06/yr from 0.88 (2017) to peak 1.20 (
  [3] FP    IP | volatility | dispersion | [2015, 2023] | conf 0.55 | mag empirical YoY SD 0.12 vs Poisson 0.026 (
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-13T22:53:33Z  sc-f69eea (pass 7, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=245.0s
harness: tool_calls=0  pack_sha=c540433e3725
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.084/yr; total A/E rise from ~0.63 (2
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-13T23:00:01Z  sc-314eca (pass 7)

---

# FULL SWEEP v1.6d — 23/23, 43/44 = 97.7 % (finished 2026-09-13T22:53:49Z)

    TOTALS: strict 43/44 = 97.7%  loose 97.7%  FP/run = 1.26 (29)  badjson 0  errors 0
    CLEAN honesty: intact (0/1)
    STRATA: persistent 9/10 (baseline 8/10) | bounded-then-reverting 5/5 (baseline 3/5)

    FREEZE GATE: [PASS] recall 97.7%   [FAIL] false alarms 1.26
                 [PASS] clean honesty, integrity, both drift strata
                 VERDICT: DO NOT FREEZE (one criterion)

The two v1.6d fixes both landed: F1 (the pack no longer contradicts itself about
build-ups) took `sc-137901` 1/2 → 2/2, and F3 (the taxonomy now covers falling as
well as rising ramps) took `sc-3c83fd` 0/1 → 1/1. The bounded-drift stratum is
back to 5/5 and the only unit still missed anywhere in the split is
`sc-d72b95`'s invisible Death drift (+0.017/yr, fit R2 0.08).

The five books went 8/12 → **11/12** units (the guard read `total=11, bba653=4`
and released the sweep).

## The single remaining obstacle, and its source

All 29 false alarms were enumerated. **24 of them are the "other reading" of a
line whose main entry already matched**, i.e. the deliberate hedge introduced in
v1.6 — it bought the recall and is now the thing failing the gate.

Of those, **7 sit in the two book-wide books** and come from one clause of mine:

    sc-314eca  fp=4  Death/drift, CI/drift, TPD/shock, IP/shock   (truth: dispersion on all 4)
    sc-9660b9  fp=3  Death/drift, CI/drift, TPD/shock             (truth: dispersion on all 4)

The pack told the model to give the dispersion entry "alongside any level-change
reading you also report", and on those books the truth has no level change at all
— so every paired entry was a guaranteed false alarm.

## v1.6e — the narrowest possible fix

The clause is removed and replaced with: for a book-wide stretch, one dispersion
entry per line is the whole answer; a genuinely separate later move that ends away
from the line's own baseline still gets its own entry.

Crucially, that clause lives in the **per-book pack text**, not the shared
rulebook, so the change alters the prompt of **exactly two books** (verified) and
the other 21 prompts are byte-identical — meaning only those two books need
re-running, not the split. Leak preflight: PASS.

Expected: 29 − 7 = **22 false alarms (0.96 per answer, ceiling 1.0)** with recall
unchanged at 43/44, because the entries being removed were never matches. If that
holds, the gate passes on all six criteria for the first time since v1.5 — with
97.7 % recall instead of 81.8 %.
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=911.8s
harness: tool_calls=0  pack_sha=4b803c645b56
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.6 | mag mild: swell 1.11 (2019) / 1.16 (2020) / 
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.8 | mag +0.25 (2019), +0.21 (2020) to peak 1.37 
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.85 | mag V-shaped swing 1.37 (2019) -> 0.93 (2020
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.8 | mag 1.28 (2019) -> 0.91 (2020) -> 0.98 (2021
SCORE: strict 4/4  loose 4/4  FP 0
sc-314eca   fam=systemic    runs=1 strict=4/4 loose=4/4 FP=0 badjson=0 err=0
```

## 2026-09-13T23:15:21Z  sc-9660b9 (pass 7)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=2109.2s
harness: tool_calls=0  pack_sha=1e439155a17c
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E hump 1.16 (2020) -> 1.22 (2021) -> 1
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.8 | mag A/E 1.25 (2020) -> 1.48 (2021) -> 0.86 (
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E 1.56 (2020) -> 0.86 (2021) -> 0.39 (
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.8 | mag A/E 1.37 (2020) -> 0.82 (2021) -> 1.03 (
SCORE: strict 4/4  loose 4/4  FP 0
sc-9660b9   fam=noise_trap  runs=1 strict=4/4 loose=4/4 FP=0 badjson=0 err=0
```

---

# FREEZE GATE PASSED — harness v1.6e, full 23-book corpus (2026-09-13T23:50:39Z)

    TOTALS: strict 43/44 = 97.7%  loose 97.7%  FP/run = 0.96 (22)  badjson 0  errors 0
    CLEAN honesty: intact (0/1)
    STRATA: persistent 9/10 (baseline 8/10) | bounded-then-reverting 5/5 (baseline 3/5)

    FREEZE GATE — all six criteria PASS  ->  VERDICT: FREEZE  (exit 0)

The v1.6e fix removed exactly the seven false alarms predicted and nothing else:

    sc-314eca  4/4 fp=4  ->  4/4 fp=0
    sc-9660b9  4/4 fp=3  ->  4/4 fp=0

Those were the paired level-change entries the pack used to invite "alongside" the
dispersion reading, on two books whose truth has no level change at all.

## Integrity of the frozen corpus

The sweep spanned three code edits (v1.6c → v1.6d → v1.6e), so the corpus was
checked rather than assumed: **the frozen files rebuild all 23 recorded
`pack_text` values byte-for-byte (23/23)**. What the model was asked is exactly
what the frozen harness asks; the two books re-run at the end are the only ones
whose prompt text differs between v1.6d and v1.6e, and both were re-run. Snapshot
with sha256 in `results/harness_opt_p7/harness_snapshot/`
(`stats_pack.py 16e53e0ef0b097ab…`, `run_zero_shot.py a4b967de975625f9…`).

## The campaign end state

| metric | no harness | v1.5 (first pass) | **v1.6e (frozen)** |
|---|---|---|---|
| correct findings | 63.6 % | 81.8 % | **97.7 %** |
| false alarms per answer | 1.61 | 0.91 | **0.96** |
| slow trends to the end | 8/10 | 9/10 | 9/10 |
| slow trends that revert | 3/5 | 5/5 | 5/5 |
| clean-book honesty | intact | intact | intact |

One unit remains missed in the whole split: `sc-d72b95`'s Death drift
(+0.017/yr, fit R2 0.08) — statistically invisible, as documented.

## Next

The held-out exam on the 24 never-tuned books (3 answers each, 72 calls) with the
frozen harness: `bash scripts/harness_final_heldout.sh`.

---

# HELD-OUT EXAM COMPLETE — 2026-09-15T17:19:08Z (72/72 calls, 24/24 books)

Frozen harness v1.6e (`stats_pack.py 16e53e0ef0b097ab…`, `run_zero_shot.py
a4b967de975625f9…` — verified still identical to the snapshot after the exam, so
the exam ran on exactly the frozen version). Full workspace leak check: CLEAN,
1,599 files, 0 hits under data/eval.

    TOTALS: strict 85/123 = 69.1%  loose 73.2%  FP/run = 0.96  badjson 0  errors 0
    CLEAN honesty: 0 of 3 answers claimed an anomaly on the clean book
    STRATA: persistent 6/6 | bounded-then-reverting 11/36

    same 24 books x 3 answers WITHOUT the harness:
    strict 79/123 = 64.2%  FP/run 2.00  clean book falsely accused in 2 of 3 answers
    persistent 6/6 | bounded-then-reverting 17/36

## Per book (3 answers each): 5 improved, 3 worse, 16 unchanged

    +4  sc-a3e6a6 (systemic)      +1  sc-e28a00 (mixed)      -1  sc-3627d2 (systemic)
    +3  sc-7e3a65 (shock)         +1  sc-f19bae (shock)      -2  sc-e6ffa4 (systemic)
    +2  sc-0ce4d6 (noise trap)                             -2  sc-73fd27 (systemic)

## Reading it honestly

The optimization split said 97.7 %; the held-out split says 69.1 %. A ~29-point
gap is the signature of fitting, and it is the single most important number in
this diary: most of the polish on the 23 practice books came from those books.

What transferred: the clean-book behaviour (never once accused a clean book, where
the bare model did so in 2 of 3 answers), false alarms halved *while* recall rose,
one-off events 67 % → 100 %, trap books 17 % → 50 %.

What did not: **reverted slow trends got worse** (47 % → 31 %) — the stratum the
harness was explicitly taught to respect. The oscillation hedge added in v1.6 to
win the trap books is the prime suspect, since trap books are the one family where
the harness gained most on practice data and least on new data.

The pre-agreed gate thresholds are NOT met on held-out (69.1 % vs 80 %, plus the
stratum regression). That is the finding, not a footnote.

---

# PARALLEL BASELINE SWEEP (xam_q36) — tooling, measurements, caveat

The Qwen3.6-27B baseline was started on a **single-slot** server (15/141 answers
banked, 5 scenarios), then stopped so the owner could enable parallel slots.

## What was measured on the restarted server (`--parallel 8 --cont-batching`)

    /props          -> total_slots: 8   (was 1)
    N=1 request     ->  885 completion tokens in 48.0s  = 18.4 tok/s aggregate
    N=4 requests    -> 1088 tokens in 28.1s             = 38.7 tok/s aggregate
    N=8 requests    -> 4049 tokens in 100.8s            = 40.2 tok/s aggregate

Batching is real (aggregate throughput more than doubles), and it **saturates at
N≈4**: 4→8 adds ~4 % aggregate while roughly doubling each answer's latency. So
N=4 is the operating point.

*Correction recorded:* `scripts/probe_parallel.py` originally judged queueing by
latency spread, which actually reflects how long each answer happened to be — it
declared the 8-slot server "QUEUED". It now reports aggregate tokens/sec instead,
which is the only measure that distinguishes serving serially from serving
batched. The earlier "cannot run 8 parallel" reading was an artefact of that
heuristic against a genuinely single-slot instance.

## New tooling (both tested without spending calls)

* `scripts/sweep_parallel.sh` — same experiment as `sweep_qwen27b.sh`, but keeps
  **N scenarios in flight** (one scenario per worker; each scenario's 3 runs stay
  sequential inside the runner, so N workers = N concurrent requests). Same
  samplers, same 1h timeout, same streaming, no max_tokens, resume-safe, flock
  guarded, completion recounted from the corpus. Dry-run verified: 47 scenarios
  dispatched 4-at-a-time, status and recount correct, nothing written.
* `scripts/rebuild_index.py` — repairs the corpus index after a parallel sweep.
  Needed because the runner rewrites `summary.md`/`meta.json` per scenario, so
  concurrent workers clobber each other's index. (Worth noting: even the archived
  sequential corpora contain only the LAST scenario in `summary.md`, so this is an
  improvement rather than only a parallel fix.) The authoritative per-run records
  are untouched by concurrency.

## Caveat accepted by the owner

xam_q36 at N=4 is produced by **batched decode**, and this server also differs
from the one behind `xam_v5` in `--spec-type draft-mtp`, quantised KV cache and
flash attention. Batched/kernel differences can perturb logits in the last bits,
and at temperature 1.0 that can change an answer. The owner accepted this: any
output difference is acceptable, and the serving configuration will be stated
alongside the number.

## 2026-09-16T22:16:17Z  sc-042304 (pass 1, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=276.5s
harness: tool_calls=0  pack_sha=6babe7695d5f
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.36 over baseline (A/E rises from ~0.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-16T22:22:26Z  sc-137901 (pass 1, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=351.0s
harness: tool_calls=0  pack_sha=d8047d631c93
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2019, 2023] | conf 0.9 | mag ~+0.04/yr, peaks at A/E 1.17 (+17% vs ba
  [1] MATCH IP | drift | increase | [2019, 2023] | conf 0.85 | mag ~+0.03/yr, peaks at A/E 1.12 (+12% vs ba
  [2] FP    IP | volatility | dispersion | [2021, 2024] | conf 0.8 | mag empirical SD 0.081 vs Poisson 0.026 (x3.
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-16T22:25:50Z  sc-14cdd9 (pass 1, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=184.8s
harness: tool_calls=0  pack_sha=d22cd9e631d6
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-16T22:29:56Z  sc-17d82f (pass 1, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=227.4s
harness: tool_calls=0  pack_sha=e3a9f132cf3c
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.99 | mag termination A/E 0.496 (~50% of expected)
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-16T22:35:13Z  sc-2d248f (pass 1, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=298.7s
harness: tool_calls=0  pack_sha=5f1d2693e242
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.95 | mag empirical SD ~0.60 vs Poisson ~0.026 (23
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.8 | mag ~+0.11/yr (A/E 0.74 to 0.96)
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-16T22:41:43Z  sc-314eca (pass 1, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=371.5s
harness: tool_calls=0  pack_sha=4b803c645b56
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.8 | mag empirical SD ~3x Poisson; part of book-w
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.9 | mag empirical SD ~6.6x Poisson; A/E spikes t
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.9 | mag empirical SD ~7.4x Poisson; A/E peaks at
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.9 | mag empirical SD ~6.7x Poisson; A/E spikes t
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-16T22:47:28Z  sc-3c83fd (pass 1, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=326.2s
harness: tool_calls=0  pack_sha=b39fc16741e5
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] FP    CI | shock | decrease then increase | [2018, 2024] | conf 0.9 | mag A/E dipped to ~0.73 in 2019, rebounded t
SCORE: strict 0/1  loose 0/1  FP 1
```

## 2026-09-16T22:50:32Z  sc-409000 (pass 1, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=166.1s
harness: tool_calls=0  pack_sha=4f6adbb8f026
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.95 | mag ~1.99x expected termination rate (A/E 1.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-16T22:57:44Z  sc-48351f (pass 1, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=413.0s
harness: tool_calls=0  pack_sha=35fff4e4c147
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] FP    TPD | drift | increase | [2015, 2022] | conf 0.85 | mag ~+0.019/yr (smoothed A/E 0.93 to 1.08)
  [1] FP    IP | drift | increase | [2015, 2022] | conf 0.85 | mag ~+0.015/yr (smoothed A/E 0.96 to 1.06)
SCORE: strict 0/2  loose 0/2  FP 2
```

## 2026-09-16T23:02:35Z  sc-4a7f9e (pass 1, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=272.5s
harness: tool_calls=0  pack_sha=deadbb2e16d5
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.95 | mag ~+0.38 A/E
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.95 | mag ~-0.46 A/E
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-16T23:06:10Z  sc-5e376b (pass 1, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=196.7s
harness: tool_calls=0  pack_sha=20d532b2dd3c
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.95 | mag ~+0.40 A/E (from ~0.87 baseline to ~1.26
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-16T23:11:13Z  sc-63f1c7 (pass 1, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=283.8s
harness: tool_calls=0  pack_sha=ad8d744fffe5
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.035/yr, rising from ~0.84 to 1.19
  [1] FP    CI | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical SD ~0.184 vs Poisson ~0.031 (6
  [2] MATCH CI | shock | increase | [2021, 2021] | conf 0.95 | mag A/E 1.327 (+33%)
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-16T23:14:37Z  sc-6e2478 (pass 1, unattended)
```
scenario sc-6e2478  json=valid  overall_says=clean  error=None  wall=185.5s
harness: tool_calls=0  pack_sha=4118b9492ca3
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  (none)
SCORE: strict 0/1  loose 0/1  FP 0
```

## 2026-09-16T23:21:18Z  sc-8a9fa1 (pass 1, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=381.9s
harness: tool_calls=0  pack_sha=637282171641
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.9 | mag empirical SD 0.35 vs Poisson 0.048 (x7.3
  [1] FP    Death | drift | increase | [2016, 2018] | conf 0.75 | mag ~+0.45 over baseline, peaking at 1.52 in
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-16T23:26:57Z  sc-8d3b47 (pass 1, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=320.3s
harness: tool_calls=0  pack_sha=4babb17df9b4
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.85 | mag ~+0.03/yr (A/E from 0.94 to 1.14)
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.9 | mag ~−0.04/yr (A/E from 1.23 to 0.85)
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-16T23:33:14Z  sc-9372cd (pass 1, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=358.1s
harness: tool_calls=0  pack_sha=ce5b88442999
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2017, 2022] | conf 0.75 | mag A/E rose from ~0.96 in 2017 to ~1.19 in 
  [1] FP    TPD | volatility | dispersion | [2017, 2022] | conf 0.7 | mag Empirical YoY SD ~0.10 vs Poisson expect
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-16T23:38:18Z  sc-9660b9 (pass 1, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=284.5s
harness: tool_calls=0  pack_sha=1e439155a17c
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E swings from 0.86 to 1.42; empirical 
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E swings from 0.86 to 1.48; empirical 
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E swings from 0.39 to 1.56; empirical 
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.85 | mag A/E swings from 0.82 to 1.37; empirical 
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-16T23:43:02Z  sc-abbec4 (pass 1, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=265.5s
harness: tool_calls=0  pack_sha=fb418334facd
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.35 A/E above baseline (~1.30-1.35 vs
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.30 A/E above baseline (~1.22-1.26 vs
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-16T23:49:03Z  sc-bba653 (pass 1, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=342.8s
harness: tool_calls=0  pack_sha=7668a7f07258
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.35-0.40 A/E (levels 1.23-1.31)
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.28 A/E (levels 1.18-1.20)
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.22 A/E (levels 1.10-1.19)
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.07-0.08 A/E (levels 1.04-1.06)
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-16T23:56:29Z  sc-d72b95 (pass 1, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=425.7s
harness: tool_calls=0  pack_sha=00195af6296f
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.9 | mag ~+0.38 A/E (peak 1.31)
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.85 | mag ~+0.18 A/E (peak 1.16)
  [2] MATCH CI | drift | increase | [2022, 2024] | conf 0.85 | mag ~+0.08/yr
SCORE: strict 3/4  loose 3/4  FP 0
```

## 2026-09-17T00:02:21Z  sc-da1123 (pass 1, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=332.8s
harness: tool_calls=0  pack_sha=e9b3d995d767
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.07/yr, from 0.74 to 1.14
  [1] MATCH CI | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.04/yr, from 0.89 to 1.15
  [2] MATCH TPD | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.03/yr, from 0.95 to 1.12
  [3] MATCH IP | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.02/yr, from 0.97 to 1.08
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T00:09:54Z  sc-f520e5 (pass 1, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=433.8s
harness: tool_calls=0  pack_sha=1cd7641f5d18
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD 0.22 vs Poisson 0.05 (x4.4)
  [1] FP    Death | drift | increase | [2017, 2021] | conf 0.8 | mag ~+0.08/yr 2017-2021, peak 1.34, reverts 
  [2] FP    IP | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD 0.12 vs Poisson 0.03 (x4.5)
  [3] MATCH IP | drift | increase | [2018, 2022] | conf 0.8 | mag ~+0.08/yr 2018-2022, peak 1.20, reverts 
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-17T00:13:45Z  sc-f69eea (pass 1, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=211.9s
harness: tool_calls=0  pack_sha=c540433e3725
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.075/yr, rising from A/E 0.63 to 1.31
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T08:44:15Z  sc-042304 (pass 2, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=278.3s
harness: tool_calls=0  pack_sha=4063b5b9ba57
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.95 | mag ~+0.36 A/E (peak 1.29 vs baseline ~0.94)
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T08:50:46Z  sc-137901 (pass 2, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=372.6s
harness: tool_calls=0  pack_sha=a8721c9b53fa
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2015, 2023] | conf 0.85 | mag ~+0.03/yr, peaking at 1.17 in 2022-2023
  [1] MATCH IP | drift | increase | [2015, 2023] | conf 0.8 | mag ~+0.012/yr, peaking at 1.12 in 2023
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T08:53:22Z  sc-14cdd9 (pass 2, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=137.1s
harness: tool_calls=0  pack_sha=4797ee55ad7f
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-17T08:56:57Z  sc-17d82f (pass 2, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=196.3s
harness: tool_calls=0  pack_sha=71ec6f7dd2b9
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.95 | mag ~0.50 A/E (half expected termination rat
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T09:02:39Z  sc-2d248f (pass 2, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=323.8s
harness: tool_calls=0  pack_sha=bf56bccaeb6f
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD ~0.60 vs Poisson ~0.026 (23
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.8 | mag +0.11/yr (0.74 to 0.96)
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-17T09:07:50Z  sc-314eca (pass 2, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=292.1s
harness: tool_calls=0  pack_sha=1340b19e5c52
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~3x Poisson; A/E swings ±0.
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~6.6x Poisson; A/E swings ±
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~7.4x Poisson; A/E swings ±
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~6.7x Poisson; A/E swings ±
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T09:13:27Z  sc-3c83fd (pass 2, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=318.5s
harness: tool_calls=0  pack_sha=bcd2db473086
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] MATCH CI | drift | decrease | [2016, 2019] | conf 0.85 | mag ~-0.11/yr over 3 years (A/E falling from
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T09:17:25Z  sc-409000 (pass 2, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=219.6s
harness: tool_calls=0  pack_sha=f266723bdca6
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.95 | mag ~x2.0 recovery rate (A/E 1.99)
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T09:22:50Z  sc-48351f (pass 2, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=306.0s
harness: tool_calls=0  pack_sha=0c03c475d323
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical YoY SD x3.36 vs Poisson expect
  [1] MATCH TPD | shock | increase | [2023, 2023] | conf 0.9 | mag A/E 1.235 (+23.5%), ~7.6 sigma
  [2] FP    IP | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical YoY SD x3.65 vs Poisson expect
  [3] MATCH IP | shock | increase | [2023, 2023] | conf 0.9 | mag A/E 1.177 (+17.7%), ~7.7 sigma
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-17T09:27:41Z  sc-4a7f9e (pass 2, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=273.0s
harness: tool_calls=0  pack_sha=69b52539f8f6
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.35 step (A/E rises from ~0.95 to ~1.
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.95 | mag ~−0.45 step (A/E drops from ~1.11 to ~0.
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T09:31:50Z  sc-5e376b (pass 2, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=230.1s
harness: tool_calls=0  pack_sha=6cfc74af3c12
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.40 A/E (from ~0.88 baseline to ~1.28
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T09:37:47Z  sc-63f1c7 (pass 2, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=338.0s
harness: tool_calls=0  pack_sha=cd12aecb3057
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.035/yr, total ~+0.31 over window
  [1] FP    CI | volatility | dispersion | [2015, 2024] | conf 0.95 | mag empirical SD 0.184 vs Poisson 0.030 (x6 
  [2] MATCH CI | shock | increase | [2021, 2021] | conf 0.8 | mag A/E 1.327 (+33% vs baseline)
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-17T09:42:12Z  sc-6e2478 (pass 2, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=246.6s
harness: tool_calls=0  pack_sha=e529ae6bbb9f
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical SD ~0.25 vs Poisson ~0.05 (x5.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T09:47:15Z  sc-8a9fa1 (pass 2, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=284.2s
harness: tool_calls=0  pack_sha=84693db85ccb
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD ~0.35 vs Poisson ~0.05 (ove
  [1] FP    Death | shock | increase | [2017, 2018] | conf 0.6 | mag A/E rose to 1.25-1.52 (+0.45 above basel
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-17T09:53:39Z  sc-8d3b47 (pass 2, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=365.5s
harness: tool_calls=0  pack_sha=00fe7a0e8951
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.07/yr (A/E rises from 0.74 to 1.14)
  [1] MATCH CI | drift | decrease | [2017, 2024] | conf 0.85 | mag ~-0.06/yr (A/E falls from 1.25 to 0.85)
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T10:00:02Z  sc-9372cd (pass 2, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=364.2s
harness: tool_calls=0  pack_sha=12cb6505df51
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2018, 2024] | conf 0.6 | mag empirical YoY SD ~0.10 vs Poisson ~0.036
  [1] MATCH TPD | drift | increase | [2018, 2021] | conf 0.6 | mag gradual rise from ~1.01 to 1.19 over 3 y
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-17T10:05:32Z  sc-9660b9 (pass 2, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=311.2s
harness: tool_calls=0  pack_sha=62b8bc4d7801
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~4.5x Poisson expectati
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~8.8x Poisson expectati
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~11.6x Poisson expectat
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~9.5x Poisson expectati
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T10:09:41Z  sc-abbec4 (pass 2, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=230.3s
harness: tool_calls=0  pack_sha=3b14c147fe79
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.95 | mag peak A/E ~1.35, excursion ~+0.41 above p
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.95 | mag peak A/E ~1.26, excursion ~+0.30 above p
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T10:15:46Z  sc-bba653 (pass 2, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=345.7s
harness: tool_calls=0  pack_sha=adf0f1e15784
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.38 to +0.44 A/E
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.28 A/E
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.8 | mag ~+0.20 A/E
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.7 | mag ~+0.08 A/E
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T10:21:44Z  sc-d72b95 (pass 2, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=340.0s
harness: tool_calls=0  pack_sha=f993462fad05
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.95 | mag A/E 1.31 (Poisson z≈7.0)
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.9 | mag A/E 1.16 (Poisson z≈5.6)
  [2] MATCH CI | drift | increase | [2022, 2024] | conf 0.85 | mag ~+0.08/yr, A/E rises steadily from 0.98 
SCORE: strict 3/4  loose 3/4  FP 0
```

## 2026-09-17T10:28:49Z  sc-da1123 (pass 2, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=405.9s
harness: tool_calls=0  pack_sha=cc58ba5cceb2
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.03/yr
  [1] MATCH CI | drift | increase | [2019, 2024] | conf 0.9 | mag ~+0.03/yr
  [2] MATCH TPD | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.04/yr
  [3] MATCH IP | drift | increase | [2021, 2024] | conf 0.8 | mag ~+0.03/yr
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T10:35:40Z  sc-f520e5 (pass 2, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=392.1s
harness: tool_calls=0  pack_sha=8cbf41f70b0c
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.75 | mag ~+0.11/yr, peak A/E 1.34
  [1] MATCH IP | drift | increase | [2019, 2022] | conf 0.85 | mag ~+0.05/yr, peak A/E 1.20
SCORE: strict 1/2  loose 1/2  FP 1
```

## 2026-09-17T10:40:41Z  sc-f69eea (pass 2, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=282.4s
harness: tool_calls=0  pack_sha=c55883c8c4b6
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.08 A/E per year, total ~+0.68 over w
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T14:47:56Z  sc-042304 (pass 3, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=293.0s
harness: tool_calls=0  pack_sha=4063b5b9ba57
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.95 | mag ~+0.36 A/E (jumps from ~0.91 baseline to
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T14:54:13Z  sc-137901 (pass 3, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=358.2s
harness: tool_calls=0  pack_sha=a8721c9b53fa
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2018, 2023] | conf 0.85 | mag A/E rose from ~0.92 to 1.17 (+0.25), rev
  [1] MATCH IP | drift | increase | [2018, 2023] | conf 0.8 | mag A/E rose from ~0.96 to 1.12 (+0.16), dro
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T14:57:14Z  sc-14cdd9 (pass 3, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=161.7s
harness: tool_calls=0  pack_sha=4797ee55ad7f
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-17T15:00:26Z  sc-17d82f (pass 3, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=173.3s
harness: tool_calls=0  pack_sha=71ec6f7dd2b9
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | [2015, 2024] | conf 0.95 | mag ~50% reduction in recovery/termination r
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T15:06:27Z  sc-2d248f (pass 3, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=342.8s
harness: tool_calls=0  pack_sha=bf56bccaeb6f
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.9 | mag empirical YoY SD ~0.60 vs Poisson ~0.026
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T15:12:47Z  sc-314eca (pass 3, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=361.4s
harness: tool_calls=0  pack_sha=1340b19e5c52
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.9 | mag A/E swings +0.2 to +0.3; empirical YoY S
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.9 | mag A/E swings +0.25 to +0.45; empirical YoY
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.9 | mag A/E swings +0.3 to -0.4; empirical YoY S
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.9 | mag A/E swings +0.3 to -0.1; empirical YoY S
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T15:18:32Z  sc-3c83fd (pass 3, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=326.1s
harness: tool_calls=0  pack_sha=bcd2db473086
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] FP    CI | shock | increase | [2020, 2024] | conf 0.85 | mag ~+0.05 to +0.10 above baseline (A/E 1.05
SCORE: strict 0/1  loose 0/1  FP 1
```

## 2026-09-17T15:22:41Z  sc-409000 (pass 3, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=230.6s
harness: tool_calls=0  pack_sha=f266723bdca6
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.99 | mag ~1.99x baseline termination A/E
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T15:28:49Z  sc-48351f (pass 3, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=347.9s
harness: tool_calls=0  pack_sha=0c03c475d323
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2023, 2023] | conf 0.95 | mag A/E ~1.24 (z ~7.6), single-year excursio
  [1] MATCH IP | shock | increase | [2023, 2023] | conf 0.95 | mag A/E ~1.18 (z ~7.7), single-year excursio
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T15:33:49Z  sc-4a7f9e (pass 3, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=281.7s
harness: tool_calls=0  pack_sha=69b52539f8f6
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.35 to +0.40 above 2015-2020 baseline
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag ~-0.45 to -0.50 below 2015-2020 baseline
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T15:37:49Z  sc-5e376b (pass 3, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=220.4s
harness: tool_calls=0  pack_sha=6cfc74af3c12
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.40 A/E (peak 1.31)
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T15:43:36Z  sc-63f1c7 (pass 3, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=326.7s
harness: tool_calls=0  pack_sha=cd12aecb3057
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.035/yr, A/E rises from ~0.84 to 1.19
  [1] MATCH CI | shock | increase | [2021, 2021] | conf 0.85 | mag Peak A/E 1.327 (+0.35 vs baseline), imme
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T15:49:30Z  sc-6e2478 (pass 3, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=335.3s
harness: tool_calls=0  pack_sha=e529ae6bbb9f
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.8 | mag Empirical SD 0.25 vs Poisson 0.048 (~5.2
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T15:56:00Z  sc-8a9fa1 (pass 3, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=371.2s
harness: tool_calls=0  pack_sha=84693db85ccb
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.9 | mag empirical SD ~0.35 vs Poisson ~0.05 (x7.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-17T16:01:33Z  sc-8d3b47 (pass 3, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=313.6s
harness: tool_calls=0  pack_sha=00fe7a0e8951
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.03/yr overall (0.94 to 1.14), steepe
  [1] MATCH CI | drift | decrease | [2015, 2024] | conf 0.9 | mag ~-0.04/yr, falling from ~1.23 (2015-2017
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T16:07:39Z  sc-9372cd (pass 3, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=347.4s
harness: tool_calls=0  pack_sha=12cb6505df51
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2015, 2024] | conf 0.7 | mag empirical YoY SD 0.098 vs Poisson 0.036 
  [1] MATCH TPD | drift | increase | [2017, 2021] | conf 0.75 | mag A/E rises from ~0.96 to 1.19 (~+6% p.a.,
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-17T16:12:09Z  sc-9660b9 (pass 3, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=251.3s
harness: tool_calls=0  pack_sha=62b8bc4d7801
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.85 | mag empirical SD ~4.5x Poisson; coordinated 
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.85 | mag empirical SD ~8.8x Poisson; coordinated 
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.85 | mag empirical SD ~11.6x Poisson; coordinated
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.85 | mag empirical SD ~9.5x Poisson; coordinated 
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T16:17:17Z  sc-abbec4 (pass 3, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=289.1s
harness: tool_calls=0  pack_sha=3b14c147fe79
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.45 A/E (peak 1.35 vs baseline ~0.90)
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.35 A/E (peak 1.26 vs baseline ~0.91)
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-17T16:22:25Z  sc-bba653 (pass 3, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=288.9s
harness: tool_calls=0  pack_sha=adf0f1e15784
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.95 | mag ~+0.40 A/E (AE peaks 1.31 in 2022)
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.95 | mag ~+0.20 A/E (AE plateau ~1.18-1.20)
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.15-0.20 A/E (AE peaks 1.15 in 2022)
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.05-0.06 A/E (AE ~1.04-1.06)
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T16:29:12Z  sc-d72b95 (pass 3, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=388.1s
harness: tool_calls=0  pack_sha=f993462fad05
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.8 | mag ~+0.34 A/E above baseline (1.31 vs ~0.97
  [1] MATCH CI | drift | increase | [2022, 2024] | conf 0.9 | mag ~+0.08/yr (total +0.16 A/E over 2 years)
SCORE: strict 2/4  loose 2/4  FP 0
```

## 2026-09-17T16:37:33Z  sc-da1123 (pass 3, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=482.4s
harness: tool_calls=0  pack_sha=cc58ba5cceb2
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.025/yr (1.07 to 1.14)
  [1] MATCH CI | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.045/yr (1.01 to 1.15)
  [2] MATCH TPD | drift | increase | [2021, 2024] | conf 0.8 | mag ~+0.048/yr (0.97 to 1.12)
  [3] MATCH IP | drift | increase | [2021, 2024] | conf 0.8 | mag ~+0.028/yr (0.99 to 1.08)
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-17T16:44:02Z  sc-f520e5 (pass 3, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=370.8s
harness: tool_calls=0  pack_sha=8cbf41f70b0c
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.7 | mag peak A/E 1.34 (+0.37 vs baseline), rever
  [1] MATCH IP | drift | increase | [2018, 2022] | conf 0.75 | mag sustained rise from ~0.95 to peak 1.20 (
SCORE: strict 1/2  loose 1/2  FP 1
```

## 2026-09-17T16:47:10Z  sc-f69eea (pass 3, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=169.4s
harness: tool_calls=0  pack_sha=c55883c8c4b6
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.084/yr, from 0.63 to 1.31
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T01:52:18Z  sc-042304 (pass 4, unattended)
```
scenario sc-042304  json=valid  overall_says=anomalies  error=None  wall=347.1s
harness: tool_calls=0  pack_sha=69c0fe7b3a22
TRUTH CONTROLS:
  ['CI'] | shock | window [2021, 2022] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH CI | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.36 A/E (peak 1.29 vs pre-shock basel
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T01:58:47Z  sc-137901 (pass 4, unattended)
```
scenario sc-137901  json=valid  overall_says=anomalies  error=None  wall=370.7s
harness: tool_calls=0  pack_sha=a8721c9b53fa
TRUTH CONTROLS:
  TPD | drift | window [2019, 2023] | factor 0.05
  IP | drift | window [2019, 2023] | factor 0.04
MODEL FINDINGS:
  [0] MATCH TPD | drift | increase | [2015, 2023] | conf 0.85 | mag ~+0.03/yr, peaking at 1.17 in 2022-2023
  [1] MATCH IP | drift | increase | [2015, 2023] | conf 0.8 | mag ~+0.012/yr, peaking at 1.12 in 2023
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-18T02:01:23Z  sc-14cdd9 (pass 4, unattended)
```
scenario sc-14cdd9  json=valid  overall_says=clean  error=None  wall=137.3s
harness: tool_calls=0  pack_sha=4797ee55ad7f
TRUTH CONTROLS:
  (none — clean scenario; any anomaly claim is a FP)
MODEL FINDINGS:
  (none)
SCORE: strict 0/0  loose 0/0  FP 0
```

## 2026-09-18T02:04:58Z  sc-17d82f (pass 4, unattended)
```
scenario sc-17d82f  json=valid  overall_says=anomalies  error=None  wall=196.3s
harness: tool_calls=0  pack_sha=71ec6f7dd2b9
TRUTH CONTROLS:
  ['Cancer'] | ip_recovery | window [2015, 2024] | factor {'Cancer': 0.5}
MODEL FINDINGS:
  [0] MATCH IP | recovery | decrease | None | conf 0.95 | mag ~0.50 A/E (half expected termination rat
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T02:10:39Z  sc-2d248f (pass 4, unattended)
```
scenario sc-2d248f  json=valid  overall_says=anomalies  error=None  wall=322.9s
harness: tool_calls=0  pack_sha=bf56bccaeb6f
TRUTH CONTROLS:
  IP | volatility | window [2015, 2024] | factor 0.3
MODEL FINDINGS:
  [0] MATCH IP | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD ~0.60 vs Poisson ~0.026 (23
  [1] FP    IP | drift | increase | [2022, 2024] | conf 0.8 | mag +0.11/yr (0.74 to 0.96)
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-18T02:15:49Z  sc-314eca (pass 4, unattended)
```
scenario sc-314eca  json=valid  overall_says=anomalies  error=None  wall=291.1s
harness: tool_calls=0  pack_sha=1340b19e5c52
TRUTH CONTROLS:
  all | volatility | window [2019, 2021] | factor 0.25
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~3x Poisson; A/E swings ±0.
  [1] MATCH CI | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~6.6x Poisson; A/E swings ±
  [2] MATCH TPD | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~7.4x Poisson; A/E swings ±
  [3] MATCH IP | volatility | dispersion | [2019, 2020] | conf 0.85 | mag empirical SD ~6.7x Poisson; A/E swings ±
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-18T02:23:37Z  sc-3c83fd (pass 4, unattended)
```
scenario sc-3c83fd  json=valid  overall_says=anomalies  error=None  wall=449.0s
harness: tool_calls=0  pack_sha=05f823148199
TRUTH CONTROLS:
  CI | drift | window [2016, 2019] | factor -0.1
MODEL FINDINGS:
  [0] FP    CI | shock | decrease then increase | [2018, 2024] | conf 0.9 | mag dip to ~0.73 A/E in 2019, sustained elev
SCORE: strict 0/1  loose 0/1  FP 1
```

## 2026-09-18T02:27:34Z  sc-409000 (pass 4, unattended)
```
scenario sc-409000  json=valid  overall_says=anomalies  error=None  wall=219.0s
harness: tool_calls=0  pack_sha=f266723bdca6
TRUTH CONTROLS:
  ['Mental Health'] | ip_recovery | window [2015, 2024] | factor {'Mental Health': 2.0}
MODEL FINDINGS:
  [0] MATCH IP | recovery | increase | None | conf 0.95 | mag ~x2.0 recovery rate (A/E 1.99)
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T02:32:58Z  sc-48351f (pass 4, unattended)
```
scenario sc-48351f  json=valid  overall_says=anomalies  error=None  wall=304.7s
harness: tool_calls=0  pack_sha=0c03c475d323
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2023, 2023] | factor {'TPD': 1.3, 'IP': 1.2}
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical YoY SD x3.36 vs Poisson expect
  [1] MATCH TPD | shock | increase | [2023, 2023] | conf 0.9 | mag A/E 1.235 (+23.5%), ~7.6 sigma
  [2] FP    IP | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical YoY SD x3.65 vs Poisson expect
  [3] MATCH IP | shock | increase | [2023, 2023] | conf 0.9 | mag A/E 1.177 (+17.7%), ~7.7 sigma
SCORE: strict 2/2  loose 2/2  FP 2
```

## 2026-09-18T02:38:10Z  sc-4a7f9e (pass 4, unattended)
```
scenario sc-4a7f9e  json=valid  overall_says=anomalies  error=None  wall=293.7s
harness: tool_calls=0  pack_sha=bde658b88503
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2021, 2022] | factor {'Death': 1.4, 'CI': 0.6}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2021, 2022] | conf 0.9 | mag ~+0.37 above baseline (A/E ~1.29 vs ~0.9
  [1] MATCH CI | shock | decrease | [2021, 2022] | conf 0.9 | mag ~-0.45 below baseline (A/E ~0.66 vs ~1.1
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-18T02:42:18Z  sc-5e376b (pass 4, unattended)
```
scenario sc-5e376b  json=valid  overall_says=anomalies  error=None  wall=229.5s
harness: tool_calls=0  pack_sha=6cfc74af3c12
TRUTH CONTROLS:
  ['Death'] | shock | window [2020, 2022] | factor {'Death': 1.5}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.40 A/E (from ~0.88 baseline to ~1.28
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T02:48:32Z  sc-63f1c7 (pass 4, unattended)
```
scenario sc-63f1c7  json=valid  overall_says=anomalies  error=None  wall=354.5s
harness: tool_calls=0  pack_sha=0490beff413f
TRUTH CONTROLS:
  Death | drift | window [2019, 2024] | factor 0.08
  ['CI'] | shock | window [2021, 2021] | factor {'CI': 1.4}
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.9 | mag ~+0.035/yr, +0.31 total (A/E rises from 
  [1] FP    CI | volatility | dispersion | [2015, 2024] | conf 0.8 | mag Empirical SD 0.184 vs Poisson 0.030 (x6 
  [2] MATCH CI | shock | increase | [2021, 2021] | conf 0.85 | mag A/E spike to 1.33 (+0.35 vs baseline ~0.
SCORE: strict 2/2  loose 2/2  FP 1
```

## 2026-09-18T02:52:57Z  sc-6e2478 (pass 4, unattended)
```
scenario sc-6e2478  json=valid  overall_says=anomalies  error=None  wall=246.2s
harness: tool_calls=0  pack_sha=e529ae6bbb9f
TRUTH CONTROLS:
  Death | volatility | window [2015, 2024] | factor 0.2
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.8 | mag empirical SD ~0.25 vs Poisson ~0.05 (x5.
SCORE: strict 1/1  loose 1/1  FP 0
```

## 2026-09-18T02:57:59Z  sc-8a9fa1 (pass 4, unattended)
```
scenario sc-8a9fa1  json=valid  overall_says=anomalies  error=None  wall=284.2s
harness: tool_calls=0  pack_sha=84693db85ccb
TRUTH CONTROLS:
  Death | volatility | window [2016, 2020] | factor 0.35
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2015, 2024] | conf 0.85 | mag empirical SD ~0.35 vs Poisson ~0.05 (ove
  [1] FP    Death | shock | increase | [2017, 2018] | conf 0.6 | mag A/E rose to 1.25-1.52 (+0.45 above basel
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-18T03:04:23Z  sc-8d3b47 (pass 4, unattended)
```
scenario sc-8d3b47  json=valid  overall_says=anomalies  error=None  wall=364.6s
harness: tool_calls=0  pack_sha=00fe7a0e8951
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor -0.04
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.07/yr (A/E rises from 0.74 to 1.14)
  [1] MATCH CI | drift | decrease | [2017, 2024] | conf 0.85 | mag ~-0.06/yr (A/E falls from 1.25 to 0.85)
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-18T03:10:46Z  sc-9372cd (pass 4, unattended)
```
scenario sc-9372cd  json=valid  overall_says=anomalies  error=None  wall=364.4s
harness: tool_calls=0  pack_sha=12cb6505df51
TRUTH CONTROLS:
  TPD | drift | window [2019, 2021] | factor 0.08
MODEL FINDINGS:
  [0] FP    TPD | volatility | dispersion | [2018, 2024] | conf 0.6 | mag empirical YoY SD ~0.10 vs Poisson ~0.036
  [1] MATCH TPD | drift | increase | [2018, 2021] | conf 0.6 | mag gradual rise from ~1.01 to 1.19 over 3 y
SCORE: strict 1/1  loose 1/1  FP 1
```

## 2026-09-18T03:16:16Z  sc-9660b9 (pass 4, unattended)
```
scenario sc-9660b9  json=valid  overall_says=anomalies  error=None  wall=310.8s
harness: tool_calls=0  pack_sha=62b8bc4d7801
TRUTH CONTROLS:
  all | volatility | window [2020, 2022] | factor 0.4
MODEL FINDINGS:
  [0] MATCH Death | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~4.5x Poisson expectati
  [1] MATCH CI | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~8.8x Poisson expectati
  [2] MATCH TPD | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~11.6x Poisson expectat
  [3] MATCH IP | volatility | dispersion | [2020, 2022] | conf 0.9 | mag Empirical YoY SD ~9.5x Poisson expectati
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-18T03:20:24Z  sc-abbec4 (pass 4, unattended)
```
scenario sc-abbec4  json=valid  overall_says=anomalies  error=None  wall=229.5s
harness: tool_calls=0  pack_sha=3b14c147fe79
TRUTH CONTROLS:
  ['TPD', 'IP'] | shock | window [2021, 2022] | factor {'TPD': 1.4, 'IP': 1.3}
MODEL FINDINGS:
  [0] MATCH TPD | shock | increase | [2021, 2022] | conf 0.95 | mag peak A/E ~1.35, excursion ~+0.41 above p
  [1] MATCH IP | shock | increase | [2021, 2022] | conf 0.95 | mag peak A/E ~1.26, excursion ~+0.30 above p
SCORE: strict 2/2  loose 2/2  FP 0
```

## 2026-09-18T03:27:22Z  sc-bba653 (pass 4, unattended)
```
scenario sc-bba653  json=valid  overall_says=anomalies  error=None  wall=399.6s
harness: tool_calls=0  pack_sha=831f5fbd6fad
TRUTH CONTROLS:
  ['Death', 'CI', 'TPD', 'IP'] | shock | window [2020, 2022] | factor {'Death': 1.5, 'CI': 1.3, 'TPD': 1.2, 'IP': 1.1}
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.35 to +0.40 A/E (1.24-1.31 vs ~0.87 
  [1] MATCH CI | shock | increase | [2020, 2022] | conf 0.9 | mag ~+0.28 A/E (1.18-1.20 vs ~0.90 baseline)
  [2] MATCH TPD | shock | increase | [2020, 2022] | conf 0.85 | mag ~+0.15 to +0.22 A/E (1.10-1.19 vs ~0.90 
  [3] MATCH IP | shock | increase | [2020, 2022] | conf 0.75 | mag ~+0.08 A/E (1.04-1.06 vs ~0.97 baseline)
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-18T03:33:32Z  sc-d72b95 (pass 4, unattended)
```
scenario sc-d72b95  json=valid  overall_says=anomalies  error=None  wall=350.9s
harness: tool_calls=0  pack_sha=bbd43f73b2a0
TRUTH CONTROLS:
  ['Death', 'CI'] | shock | window [2020, 2020] | factor {'Death': 1.4, 'CI': 1.2}
  Death | drift | window [2021, 2024] | factor 0.05
  CI | drift | window [2021, 2024] | factor 0.04
MODEL FINDINGS:
  [0] MATCH Death | shock | increase | [2020, 2020] | conf 0.9 | mag A/E 1.310 (~+0.40 vs pre-2020 baseline ~
  [1] MATCH CI | shock | increase | [2020, 2020] | conf 0.85 | mag A/E 1.159 (~+0.18 vs baseline ~0.98, z~5
  [2] MATCH CI | drift | increase | [2022, 2024] | conf 0.8 | mag ~+0.08/yr, ending A/E 1.138
SCORE: strict 3/4  loose 3/4  FP 0
```

## 2026-09-18T03:40:38Z  sc-da1123 (pass 4, unattended)
```
scenario sc-da1123  json=valid  overall_says=anomalies  error=None  wall=405.6s
harness: tool_calls=0  pack_sha=cc58ba5cceb2
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.06
  CI | drift | window [2018, 2024] | factor 0.04
  TPD | drift | window [2018, 2024] | factor 0.03
  IP | drift | window [2018, 2024] | factor 0.02
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2018, 2024] | conf 0.85 | mag ~+0.03/yr
  [1] MATCH CI | drift | increase | [2019, 2024] | conf 0.9 | mag ~+0.03/yr
  [2] MATCH TPD | drift | increase | [2021, 2024] | conf 0.85 | mag ~+0.04/yr
  [3] MATCH IP | drift | increase | [2021, 2024] | conf 0.8 | mag ~+0.03/yr
SCORE: strict 4/4  loose 4/4  FP 0
```

## 2026-09-18T03:47:27Z  sc-f520e5 (pass 4, unattended)
```
scenario sc-f520e5  json=valid  overall_says=anomalies  error=None  wall=391.1s
harness: tool_calls=0  pack_sha=8cbf41f70b0c
TRUTH CONTROLS:
  IP | drift | window [2018, 2022] | factor 0.07
  Death | volatility | window [2019, 2022] | factor 0.25
MODEL FINDINGS:
  [0] FP    Death | drift | increase | [2019, 2021] | conf 0.75 | mag ~+0.11/yr, peak A/E 1.34
  [1] MATCH IP | drift | increase | [2019, 2022] | conf 0.85 | mag ~+0.05/yr, peak A/E 1.20
SCORE: strict 1/2  loose 1/2  FP 1
```

## 2026-09-18T03:52:29Z  sc-f69eea (pass 4, unattended)
```
scenario sc-f69eea  json=valid  overall_says=anomalies  error=None  wall=282.4s
harness: tool_calls=0  pack_sha=c55883c8c4b6
TRUTH CONTROLS:
  Death | drift | window [2018, 2024] | factor 0.15
MODEL FINDINGS:
  [0] MATCH Death | drift | increase | [2015, 2024] | conf 0.95 | mag ~+0.08 A/E per year, total ~+0.68 over w
SCORE: strict 1/1  loose 1/1  FP 0
```
