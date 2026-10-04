# Quarantined records — server fault, 2026-09-16

Between 01:24 and 05:10 UTC the LLM server (restarted with speculative-decoding
flags) intermittently returned HTTP 200 with `finish_reason=stop` and EMPTY
content, after cutting the model's thinking off mid-sentence. Roughly 3 in 4
requests were affected; a plain single request reproduced it, so it is a serving
fault, not a concurrency or runner problem.

* `errors/` — records the runner refused to bank (its EmptyGeneration guard).
  These are evidence of the fault, not answers: nothing here has content.
* `suspect_valid/` — answers that LOOK complete but were produced by that same
  misbehaving server, so they are moved out to be re-spent on a healthy server.

Both directories are outside `zero_shot/`, so the runner's --skip-existing will
re-spend every one of these run slots on the next resume. Nothing was deleted.
