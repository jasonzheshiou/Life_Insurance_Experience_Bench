# Zero-shot probe — run xam_20260831_opt
model=Qwen3.8-Flash-Next endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=3
sampling: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0} · max_tokens: not sent · stateless per-call context
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (782 files verified, seal match: True)

## sc-042304  (3/3 runs ok)
## sc-137901  (3/3 runs ok)
## sc-14cdd9  (3/3 runs ok)
## sc-17d82f  (2/3 runs ok)
## sc-2d248f  (3/3 runs ok)
## sc-314eca  (3/3 runs ok)
## sc-3c83fd  (3/3 runs ok)
## sc-409000  (3/3 runs ok)
## sc-48351f  (3/3 runs ok)
## sc-4a7f9e  (3/3 runs ok)
## sc-5e376b  (3/3 runs ok)
## sc-63f1c7  (3/3 runs ok)
## sc-6e2478  (3/3 runs ok)
## sc-8a9fa1  (3/3 runs ok)
## sc-8d3b47  (3/3 runs ok)
## sc-9372cd  (3/3 runs ok)
## sc-9660b9  (3/3 runs ok)
## sc-abbec4  (3/3 runs ok)
## sc-bba653  (3/3 runs ok)
## sc-d72b95  (3/3 runs ok)
## sc-da1123  (3/3 runs ok)
## sc-f520e5  (3/3 runs ok)
## sc-f69eea  (3/3 runs ok)

## Ground truth (scorer-only — copied for the experimenter, NEVER sent to the model)
Manifest files copied to zero_shot/truth/ (keyed by the opaque scenario id; see truth/id_map.csv for the descriptive name). Open a manifest and a `<scenario>_runNN.json` side by side and check: benefit, years, pattern type, direction, magnitude. (Automated scoring arrives with milestone M0 scoring.py / M3 Stage 1.)

## SWEEP ABORTED

endpoint unavailable

Re-run with `--skip-existing` to resume without re-spending the calls that already succeeded.

## Failures
- sc-17d82f run 3: endpoint unavailable (wait-for-endpoint expired)
