# Zero-shot probe — run harness_q36_regress
model=Qwen3.6-27B endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=3
sampling: {"top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 0.0, "repetition_penalty": 1.0} · max_tokens: not sent · stateless per-call context
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (136 files verified, seal match: True)

## sc-4a7f9e  (3/3 runs ok)
## sc-5e376b  (3/3 runs ok)
## sc-abbec4  (3/3 runs ok)
## sc-bba653  (3/3 runs ok)
