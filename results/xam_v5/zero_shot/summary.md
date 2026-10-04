# Zero-shot probe — run xam_v5
model=Qwen3.8-27B-Q8_0 endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=3
sampling: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0} · max_tokens: not sent · stateless per-call context
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (34 files verified, seal match: True)

## sc-f916b9  (3/3 runs ok)

## Ground truth (scorer-only — copied for the experimenter, NEVER sent to the model)
Manifest files copied to zero_shot/truth/ (keyed by the opaque scenario id; see truth/id_map.csv for the descriptive name). Open a manifest and a `<scenario>_runNN.json` side by side and check: benefit, years, pattern type, direction, magnitude. (Automated scoring arrives with milestone M0 scoring.py / M3 Stage 1.)
