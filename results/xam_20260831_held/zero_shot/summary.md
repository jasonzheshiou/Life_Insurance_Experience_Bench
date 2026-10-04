# Zero-shot probe — run xam_20260831_held
model=Qwen3.8-Flash-Next endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=3
sampling: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0} · max_tokens: not sent · stateless per-call context
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (816 files verified, seal match: True)

## sc-0ce4d6  (2/3 runs ok)
## sc-11135c  (3/3 runs ok)
## sc-12be68  (3/3 runs ok)
## sc-21b383  (3/3 runs ok)
## sc-3411b2  (3/3 runs ok)
## sc-3627d2  (3/3 runs ok)
## sc-62c222  (3/3 runs ok)
## sc-696b93  (3/3 runs ok)
## sc-6fe297  (3/3 runs ok)
## sc-73fd27  (3/3 runs ok)
## sc-7e3a65  (3/3 runs ok)
## sc-87e6e7  (3/3 runs ok)
## sc-88fa33  (3/3 runs ok)
## sc-90a5be  (3/3 runs ok)
## sc-9db072  (3/3 runs ok)
## sc-a15166  (3/3 runs ok)
## sc-a3e6a6  (3/3 runs ok)
## sc-c9d78b  (3/3 runs ok)
## sc-ca7798  (3/3 runs ok)
## sc-e28a00  (3/3 runs ok)
## sc-e549ad  (3/3 runs ok)
## sc-e6ffa4  (3/3 runs ok)
## sc-f19bae  (3/3 runs ok)
## sc-f916b9  (3/3 runs ok)

## Ground truth (scorer-only — copied for the experimenter, NEVER sent to the model)
Manifest files copied to zero_shot/truth/ (keyed by the opaque scenario id; see truth/id_map.csv for the descriptive name). Open a manifest and a `<scenario>_runNN.json` side by side and check: benefit, years, pattern type, direction, magnitude. (Automated scoring arrives with milestone M0 scoring.py / M3 Stage 1.)

## SWEEP ABORTED

endpoint unavailable

Re-run with `--skip-existing` to resume without re-spending the calls that already succeeded.

## Failures
- sc-0ce4d6 run 1: endpoint unavailable (wait-for-endpoint expired)
