# MILESTONE: Ceremony token anatomy — attribute ADD's cache-read cost by category

goal: A deterministic per-turn, per-category token-anatomy harness over run transcripts (method-docs · engine-output · build-work · conversation-history) that quantifies which surfaces drive ADD's cache-read cost, so ceremony optimization targets real drivers with data, not guesses
stage: mvp · status: active · created: 2026-07-15T06:32:08+00:00 · lane: tiny
release: pending

> Tiny plan — small scope, one approval. Keep it to a handful of lines; if it
> outgrows this shape, recreate without --tiny (the full SDD scaffold).

Why: the honest-fidelity-meter benchmark showed ADD costs ~3.6× spec-kit, and the token
anatomy traced it to cache-reads of carried context (98% of tokens; output negligible) driven
by two factors — 3.3× more turns and 1.5× bigger per-turn context (PROJECT.md ~13.7k resident).
Before optimizing (a heavily-trodden area), MEASURE which surfaces actually drive the cost.
This harness reads transcripts only — it does NOT touch the ADD engine (no ENGINE_MD5 repin).

## Plan
- **anatomy-core** (fast): `token_anatomy(transcript_path) -> {category: cache_read_tokens}` — walk
  the JSONL messages in order, size each message's content, categorize it (method-doc read ·
  engine-output · build-work · conversation), and attribute each message's cache-read cost as
  `size × (# later turns it stays resident)`. Deterministic; attributes ≥95% of the transcript's
  cache_read to a named category (residual reported).
- **anatomy-report** (fast): render the attribution as markdown (per-category tokens + %) + a
  cross-arm compare (ADD vs spec-kit) isolating the ceremony delta (method-doc + engine-output
  share) + a `python -m benchmark.anatomy <transcript>` CLI.

## Done when
- [ ] `token_anatomy` attributes ≥95% of a real transcript's cache_read to categories (residual <5%), deterministic on a fixed transcript — verified by `benchmark/tests/test_token_anatomy.py`.
- [ ] on `add-v2meter-r0/wm1` the harness prints the method-docs vs conversation-history vs engine-output vs build-work split with concrete token numbers — verified live + pinned by a test on a fixture transcript.
- [ ] the cross-arm compare quantifies ADD's ceremony overhead vs spec-kit (the removable-vs-inherent split) — verified by a test asserting the compare surfaces both arms' category shares.
- [ ] read-only over transcripts, no `add-method/` engine change; full `benchmark/tests/` suite green.
