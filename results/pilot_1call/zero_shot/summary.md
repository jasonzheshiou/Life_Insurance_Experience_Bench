# Zero-shot probe — run pilot_1call
model=Qwen3.8-Flash-Next endpoint=http://192.168.1.59:8080/v1 temp=1.0 seed=1234 runs=1
dataset fingerprint: 2deda8760407c9b270a1f443acbbeda641d225eb67d8afb6e8ca15afb01433a2
preflight: leak check CLEAN · integrity ok (34 files verified, seal match: True)

## sc-409000  (0/1 runs ok)

## Failures
- sc-409000 run 1: attempt 3: URLError(ConnectionRefusedError(111, 'Connection refused'))
