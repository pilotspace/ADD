# Fallback — graceful degradation for the docs-Q&A assistant

The per-failure-mode safe state for this RAG feature. A probabilistic system
without a declared fallback is unsafe by construction, so every failure mode
below names a concrete safe path — never "crash", never "hang". Each guardrail
declared in `io-contract.json` (`pii` · `injection` · `toxicity` · `refusal`)
has a wired line here; an unwired guardrail is red (`guardrail_without_fallback`).

## Timeout

If the model or retriever does not respond within `timeout_ms` (see Limits),
abandon the call and return the cached answer for an identical question when one
exists; otherwise return the canned "I couldn't reach the documentation service —
please retry shortly" message with `confidence: 0`. Never block the request
thread past the timeout.

## Error

On any exception (retriever down, model 5xx, malformed upstream payload), retry
within the bounded budget (see Limits); if retries are exhausted, degrade to the
canned unavailable message with `confidence: 0` and log the trace id. The caller
receives a schema-valid response, never a propagated stack trace.

## Low-confidence

When `confidence` is below the answer threshold (< 0.5), do not present the
answer as grounded. Return the hedged "I'm not confident the docs cover this —
here is the closest passage I found" response with the retrieved snippet, and
offer the human-handoff path (open a support ticket). Below-threshold output is
surfaced as uncertain, never asserted.

## Schema-invalid output

If the model's output fails validation against `io-contract.json`'s
`response_schema`, it takes this fallback path and never propagates. Attempt one
re-ask with a stricter format instruction; if it still fails, return the canned
unavailable message with `confidence: 0`. A schema-invalid output is treated as
no answer.

## Guardrail trip

- **injection** — a detected prompt-injection or indirect-injection attempt
  (including instructions embedded in retrieved chunks) hard-denies: return the
  fixed refusal "I can only answer questions grounded in the product
  documentation" with empty `relevant_chunk_ids`. A guardrail trip is a
  HARD-STOP class, never auto-passed.
- **pii** — if a candidate answer would emit PII to the response, redact the PII
  span before returning; if redaction cannot be confirmed, hard-deny with the
  refusal message. PII never leaves the boundary.
- **toxicity** — if the toxicity guardrail flags the generated answer, suppress
  it and return the refusal message rather than the flagged text.
- **refusal** — for out-of-scope or unsafe requests, the assistant refuses with
  the fixed refusal message and empty `relevant_chunk_ids`; this is the expected
  safe path, not an error.

## Empty retrieval

If retrieval returns no chunks above the relevance floor, do not let the model
answer from parametric memory (hallucination risk). Return the canned "I don't
see this in the documentation" response with empty `relevant_chunk_ids` and
`confidence: 0`, and offer the human-handoff path.

## Limits

- **timeout_ms** — 4000 (hard ceiling per request, retriever + generation
  combined).
- **retry** — bounded to 2 attempts with exponential backoff and jitter (matches
  `io-contract.json` `retry`); a circuit breaker opens after 5 consecutive
  failures within 60s and routes all traffic to the cached/canned path until it
  half-opens. No unbounded wait on a probabilistic dependency.
