# Zero-shot probe — run harness_opt_p7
model=Qwen3.8-27B-Q8_0 endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=1
sampling: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0} · max_tokens: not sent · stateless per-call context
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (34 files verified, seal match: True)

## sc-9660b9  (1/1 runs ok)
