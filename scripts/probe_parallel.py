#!/usr/bin/env python3
"""probe_parallel.py — what does the LLM server do with CONCURRENT requests?

Fires N simultaneous chat completions and reports, per request, the HTTP status,
the wall time and how much text came back. That distinguishes the three possible
server behaviours:

  * all 200, times ≈ serial          -> requests are QUEUED (one slot, fair queue)
  * some 503 / "server is busy"      -> CONCURRENT SLOTS ARE NOT ENABLED
  * all 200, times ≈ parallel        -> N slots are live (llama.cpp --parallel N)

No sampling tricks, no max_tokens: each request asks for one short sentence and
is left to finish. Nothing in this script touches the benchmark corpora.

    python3 scripts/probe_parallel.py            # 2 concurrent requests
    python3 scripts/probe_parallel.py --n 4      # 4 concurrent requests
    python3 scripts/probe_parallel.py --n 2 --url http://host:port/v1
"""
from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.error
import urllib.request

RESULTS: dict[int, dict] = {}


def one(i: int, url: str, model: str, same: bool = False) -> None:
    text = ("Reply with one short sentence." if same
            else f"Request number {i}. Reply with one short sentence.")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": 1.0, "top_p": 0.95, "top_k": 20, "min_p": 0.0,
        "presence_penalty": 0.0, "repetition_penalty": 1.0,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{url.rstrip('/')}/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = r.read().decode()
        el = time.time() - t0
        try:
            d = json.loads(raw)
            msg = (d.get("choices") or [{}])[0].get("message", {}) or {}
            txt = msg.get("content") or ""
            reason = msg.get("reasoning_content") or ""
            usage = d.get("usage") or {}
            usage["_reason_chars"] = len(reason)
        except Exception:
            txt, usage = "", {}
        RESULTS[i] = {"status": 200, "seconds": el, "chars": len(txt.strip()),
                      "text": txt.strip()[:60], "usage": usage}
    except urllib.error.HTTPError as e:
        RESULTS[i] = {"status": e.code, "seconds": time.time() - t0, "chars": 0,
                      "text": e.read().decode()[:120].replace("\n", " "), "usage": {}}
    except Exception as e:
        RESULTS[i] = {"status": "ERR", "seconds": time.time() - t0, "chars": 0,
                      "text": f"{type(e).__name__}: {e}", "usage": {}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--url", default="http://192.168.1.59:8080/v1")
    ap.add_argument("--model", default="Qwen3.6-27B")
    ap.add_argument("--same", action="store_true",
                    help="send the IDENTICAL prompt in every request (isolates queueing "
                         "from reasoning-length variance)")
    a = ap.parse_args()

    try:
        with urllib.request.urlopen(f"{a.url.rstrip('/')}/models", timeout=10) as r:
            served = [m.get("id") for m in (json.loads(r.read().decode()).get("data") or [])]
        print(f"server serves: {served}")
    except Exception as e:
        print(f"cannot reach {a.url}: {e}")
        return 2

    print(f"firing {a.n} requests simultaneously against {a.url} …")
    t0 = time.time()
    threads = [threading.Thread(target=one, args=(i, a.url, a.model, a.same))
               for i in range(1, a.n + 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.time() - t0

    print(f"\n{'req':<5}{'status':<8}{'seconds':>9}{'chars':>7}  text")
    for i in sorted(RESULTS):
        r = RESULTS[i]
        print(f"{i:<5}{str(r['status']):<8}{r['seconds']:>9.1f}{r['chars']:>7}  {r['text']}")
    ok = [r for r in RESULTS.values() if r["status"] == 200]
    toks = sum((r["usage"] or {}).get("completion_tokens") or 0 for r in ok)
    print(f"\ntotal wall time for {a.n} request(s): {total:.1f}s   succeeded: {len(ok)}/{a.n}"
          f"   completion tokens: {toks if toks else 'not reported by server'}")
    if toks:
        print(f"AGGREGATE THROUGHPUT: {toks / total:.1f} completion tokens/sec "
              f"(this is the number that matters — compare runs with different --n)")
    if len(ok) == a.n and len(ok) > 1:
        lat = sorted(r["seconds"] for r in ok)
        print(f"latency spread (slowest/fastest): {lat[-1] / lat[0]:.1f}x   "
              f"[{', '.join(f'{x:.1f}s' for x in lat)}]")
        print("NOTE: latency spread reflects how long each answer happened to be, not "
              "queueing. Compare AGGREGATE THROUGHPUT across --n values instead: if it "
              "rises with --n, the slots are genuinely batched; if it stays flat while "
              "wall time doubles, requests are being serialised.")
    elif len(ok) != a.n:
        print("-> some requests were REJECTED: concurrent slots are likely off")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
