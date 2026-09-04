---
type: Task
title: One pinned JSON payload serves both read verbs, and is byte-stable across runs
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
depends_on:
  - /tasks/show-verb.md
  - /tasks/search-structured-filters.md
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/.add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/docs/13-command-reference.md
  - add-method/tests/engine
gives:
  - S1 add.read_payload(verb, request, ok, note, results, edges) — the ONE envelope every machine read emits, and the only place its keys are named
  - S2 add.show_payload(root, ref, expand) — the adapter that fills that envelope from what `show` returned, beside the exit code its refusal earned
  - S3 add.search_payload(root, query, filters) — the adapter that fills the same envelope from what `search` returned
  - S4 add.as_json(payload) — the one serializer: sorted keys, two-space indent, a single trailing newline, no clock and no absolute path
  - S5 the `--json` flag on the two read verbs in cli.py — the shipped surface a script actually calls
  - S6 FORMAT.md's pinned schema section — the document a consumer reads before parsing the payload
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:5961032504e73058", binding: "sha256:7dfe44a235b0cad0" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:8caaad9b13a38caa" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:5961032504e73058", binding: "sha256:7dfe44a235b0cad0" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/json-emission.d/runs/1.md }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:e1a531518fbbf08e" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/json-emission.d/runs/2.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:84baefb0424388c1", binding: "sha256:7dfe44a235b0cad0" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ae74a102e8061c2c" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/json-emission.d/runs/3.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/json-emission.d/runs/3.md, brief: "sha256:ae74a102e8061c2c" }
---
## CARD
goal: one JSON payload schema serves both read verbs, survives a refusal, and is byte-identical across runs over an unchanged bundle.
why: `show` and `search` are the two doors a machine reads this bundle through, and both answer only in prose today. A consumer that has to parse the human render is coupled to wording no test pins. The milestone's whole point is a bundle a tool can walk, so the walk needs a stable machine surface — and ONE, because two payload shapes for two read verbs is the same drift X4 just cost us a task to undo.
beat: done · next: add status

## RULES
<must>
- M1 `show --json` and `search --json` emit the SAME envelope keys, built by one function neither verb bypasses
- M2 two runs of the same command over an unchanged bundle emit byte-identical stdout
- M3 a refusal emits the envelope too, with `ok: false` and the refusal text (its `next:` line included) in `note`
- M4 a refusal keeps the exit code it earned; `--json` never turns a refusal into a success
- M5 `--json` writes the payload and nothing else to stdout — no banner, no human render alongside it
- M6 FORMAT.md pins the schema: every envelope key, what fills it per verb, and the stability guarantee
- M7 the envelope carries a SCHEMA version, never the engine version — a payload must not change bytes because a release did
</must>
<reject>
- R:TWOSHAPES the two verbs must not each name the envelope's keys; one builder or the schema drifts -> "TWOSHAPES"
- R:FALSESUCCESS a refusal rendered as JSON must never exit 0 — a caller that checks the status code would read a refusal as an answer -> "FALSESUCCESS"
- R:UNSTABLE nothing in the payload may vary run to run — no clock, no absolute path, no set or dict iteration order -> "UNSTABLE"
- R:DIRTYSTDOUT prose must not share stdout with the payload; a consumer pipes it straight into a parser -> "DIRTYSTDOUT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 S4 S5 S6 · n/a · a read-only emission over data the two verbs already return; no stamp, no floor, no new capability, and no write path reaches any of it
- A2 [which] covers: S1 · the request does not say what the shared envelope IS; taking `results[] + edges[]` — `show` is one node plus its walk, `search` is N hits and no walk, so the same two lists hold both and a later verb returning both fits without a third shape -> if wrong, the envelope needs a verb-shaped branch and M1 is decorative
- A3 [which] covers: S2 S5 · the request does not say which parts map where, nor which verbs get the flag; taking `fm` to a result's fields, the body to its text and the walk rows to `edges`, and the flag on the two READ verbs only — `deltas` and `status` are separate asks -> if wrong, the flag spreads to verbs whose payload nothing here designed
- A4 [which] covers: S3 · the request does not say what a search hit's `cid` is; taking `address` minus its `#fragment`, because `search` already returns the address and one-address-per-concept just made the node and delta doors build it the same way · found: `search()` returns `(address, kind, text)` triples and every address is a cid or `cid#fragment` -> if wrong, the adapter recomputes a cid the verb already knew and the two can disagree
- A5 [which] covers: S4 S6 · the request does not say which serializer settings or which document; taking `sort_keys · indent=2 · ensure_ascii=False · one trailing newline`, pinned in a FORMAT.md section beside the neighbourhood walk, because that is where a consumer already reads what the bundle guarantees -> if wrong, the guarantee lives only in code and a consumer pins bytes nobody promised
- A6 [when] covers: S1 S5 · the request does not say when the schema string changes; taking ONLY a schema change — the engine version is deliberately absent, so a release cannot move the bytes (M7) -> if wrong, every release breaks a consumer's byte pin for no semantic reason
- A7 [when] covers: S2 S3 S4 · the request does not say when the payload is built; taking AFTER the verb answers, from what it returned, and serialized exactly once — never a second traversal, so the JSON and the prose can never describe different reads -> if wrong, two reads race and the machine surface disagrees with the human one
- A8 [when] covers: S6 · the request does not say when the document must move; taking WITH the builder, in the same change — a schema section that lags the code is worse than none, because it is believed -> if wrong, the pinned section documents a payload the engine stopped emitting
- A9 [absent] covers: S2 S3 · the request does not say what an absent frontmatter field is; taking OMITTED, not `null` — the frontmatter is copied as it stands, so a key present in the payload means a key present in the file · probe: `show`'s view already carries `fm` as read -> if wrong, a consumer cannot tell an unauthored slot from an authored empty one
- A10 [absent] covers: S1 S4 · the request does not say what `edges` holds for `search`; taking the EMPTY LIST, never a missing key, and the serializer strips nothing — a consumer indexes one shape or the schema is not one schema -> if wrong, every consumer writes the `.get("edges", [])` the envelope was supposed to spare it
- A11 [absent] covers: S5 S6 · the request does not say what happens without the flag; taking today's prose EXACTLY, byte for byte — this task adds a second render and changes neither the first one nor its tests -> if wrong, a machine surface silently rewords the human one
- A12 [order] covers: S1 S4 · the request does not say what makes the bytes stable; taking sorted keys plus the two verbs' existing total orders — `neighborhood()` already emits a deterministic order and `search` orders by tier · probe: run the same command twice and compare bytes -> if wrong, dict insertion order leaks and M2 fails intermittently, which is the worst way to fail
- A13 [order] covers: S2 S3 · the request does not say what orders `results`; taking the VERB's order, unchanged — an adapter that re-sorts makes the two renders disagree about what came first -> if wrong, the prose and the payload rank the same hits differently
- A14 [order] covers: S5 S6 · the request does not say whether flag order matters; taking argparse's own handling — `--json` is a store_true that commutes with every other flag, and the FORMAT section documents keys alphabetically because that is the order they are emitted in -> if wrong, the document and the payload list the same keys in two orders
- A15 [experience] covers: S5 S6 · the receiver is a script piping stdout into a parser; what would make it hard is prose on the same stream or a refusal that exits 0, so the payload is alone on stdout and the exit code is untouched -> if wrong, the surface works in a terminal and fails in a pipeline
- A16 [experience] covers: S1 S2 S3 S4 · the receiver is the next author adding a third read verb; taking a NAMED builder they call rather than a schema they re-type, the shape one-address-per-concept just cost a task to establish -> if wrong, verb three names the keys itself and the schema drifts on its first day

## PLAN
contract: `read_payload(verb, request, ok, note, results, edges)` returns the envelope — `schema · verb · ok · request · results · edges · note`. `as_json(payload)` serializes it with `sort_keys=True`, `indent=2`, `ensure_ascii=False` and one trailing newline. `show_payload` and `search_payload` call the verb, map its return into `results`/`edges`, and hand back `(payload, exit_code)`. `cli.py` grows `--json` on both verbs: print `as_json(payload)`, exit with the code the adapter returned. FORMAT.md gains the pinned schema section.
strategy: write the byte-stability check and the refusal-exit-code check FIRST — R:UNSTABLE and R:FALSESUCCESS are the two failures a happy-path test would never see.

## EDGES
- E1 a refusal (`--expand 9`, an unresolvable ref, a query-less filter-less search) emits the envelope, `ok: false`, and its own non-zero exit
- E2 a search with zero hits is a SUCCESS with an empty `results` — not a refusal
- E3 a node whose body carries non-ASCII survives the round trip unescaped
- E4 `show` on an isolated node emits `edges: []`, never a missing key

## CHECKS
- test_both_verbs_emit_one_envelope · covers: M1, R:TWOSHAPES, A2, A10 · the two payloads carry the identical key set, and both adapters call `read_payload`, asserted from the source
- test_stdout_is_byte_stable_across_runs · covers: M2, R:UNSTABLE, A12 · the same command run twice over an unchanged bundle yields identical bytes
- test_a_refusal_is_a_payload_not_a_traceback · covers: M3, E1 · each refusal path emits the envelope with `ok` false and its `next:` line in `note`
- test_a_refusal_keeps_its_exit_code · covers: M4, R:FALSESUCCESS, E1, A15 · `--json` on a refusing invocation exits non-zero
- test_json_owns_stdout_alone · covers: M5, R:DIRTYSTDOUT · stdout parses whole as JSON, with no prose before or after it
- test_empty_result_is_not_a_refusal · covers: E2 · a zero-hit search exits 0 with `ok` true and `results: []`
- test_absent_fields_are_omitted_not_nulled · covers: A9, E3, E4 · a node with no `status:` has no `status` key, and unicode survives (E3)
- test_the_schema_is_pinned_in_format · covers: M6, M7, A5, A6 · FORMAT.md names every envelope key the builder emits, and the payload carries no engine version
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
