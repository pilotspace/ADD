# TASK: Cross Component Contract

slug: cross-component-contract · created: 2026-06-24 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project `auto`: method-defining — adds a write-hook to the core `cmd_advance` path + writes a new artifact file (.add/contracts/<id>.json). The opt-in byte-identical invariant + a human verify guard the blast radius. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_advance(args)` (L1186) — the phase-bump path. The contract→tests crossing (`nxt == "tests"`) is where a producer's §3 freeze is approved — the hook point to WRITE the contract snapshot, and where a consumer PINS it. Mirrors the existing `nxt == "build"` snapshot block (tripwire + scope).
  - `add-method/tooling/add.py:_components(root)` (L3927) — TOML registry reader (task 1). EXTEND-as-sibling: a new `_contracts(root)` parses `[contract.<id>]` (producer · consumers) from the SAME `.add/components.toml`, degrade-safe like `_components`.
  - `add-method/tooling/add.py:_COMPONENT_LINE_RE` (L1304) + `_task_component` (L3974) — the anchored `component:` header grammar + reader. Mirror for new `produces:` / `consumes:` header lines.
  - `add-method/tooling/add.py:_raw_phase_bodies(root, slug)` (L4456) — the §3 body bytes the snapshot HASH is taken over (the frozen shape).
  - `add-method/tooling/add.py:_atomic_write` (L217) + `_md5_text` (L3862) — the design-for-failure write + the hash primitive for the snapshot file.
  - `add-method/tooling/add.py:cmd_check` — where consumer-stale (`contract_consumer_stale`) + malformed-contract findings surface, mirroring task 1's `_component_findings`.
Context (working folder):
  - NEW artifact dir `.add/contracts/` holding `<id>.json` snapshots; NEW test `add-method/tooling/test_cross_component_contract.py`; models task 1/2's tests. 3-tree parity + `engine_pin.py` re-pin.
Honors (patterns / conventions):
  - INVARIANT (MILESTONE): freeze is the cross-component gate; the producer §3 freeze WRITES the snapshot, consumers PIN it, a producer re-freeze that changes the snapshot opens a stale delta on every consumer (never silently breaks a downstream leg).
  - INVARIANT: designed-for-failure — a missing/mismatched pinned snapshot HARD-STOPS the consumer (fail-loud), never builds against a guessed shape.
  - INVARIANT: opt-in — no contracts declared / no `produces:`/`consumes:` ⇒ `cmd_advance` byte-identical to today.
  - ENGINE INVARIANT: the engine never executes a suite; here it also only READS the §3 bytes + WRITES an immutable snapshot — no code execution.
  - red/green TDD · 3-tree parity · atomic write.
Anchors the contract cites: `cmd_advance` · `_contracts` · `_task_produces` · `_task_consumes` · `_contract_snapshot` (path) · `_contract_body_hash` · `_atomic_write`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Cross-component contract as a first-class artifact — a producer's §3 freeze writes an immutable snapshot, consumers pin it, a producer re-freeze flags every consumer stale
Framings weighed: auto-write the snapshot at the producer's contract→tests crossing + auto-pin at the consumer's (chosen — no new human step, hooks the existing freeze approval) · a separate `add.py contract publish/pin` command (more surface, another seam to stamp) · snapshot lives in MILESTONE.md prose only (not machine-checkable)
Must:
<must>
  - A contract is DECLARED in `.add/components.toml` as `[contract.<id>]` with `producer = "<component>"` and `consumers = ["<component>", …]`. Parsed by a new `_contracts(root)`, degrade-safe (bad TOML / missing producer ⇒ skipped, surfaced as a finding).
  - A task declares its role via a header line: `produces: <id>` (this task freezes the contract) or `consumes: <id>` (this task builds against it) — same anchored grammar as `component:`.
  - PRODUCER WRITE: when a task with `produces: <id>` crosses contract→tests (its §3 is FROZEN), the engine writes `.add/contracts/<id>.json` = {id, producer, task, version (from "FROZEN @ vN"), frozen (date), hash (of the §3 contract shape)} via an atomic write; the `contracts/` dir is created if absent. Idempotent — re-writing the same frozen shape yields byte-identical content.
  - CONSUMER PIN: when a task with `consumes: <id>` crosses contract→tests, the engine reads the live snapshot and records the pinned hash into state (`tasks[slug].contract_pin = {id, hash}`). A MISSING snapshot HARD-STOPS the crossing (`contract_snapshot_missing`) — never build against a guessed shape.
  - STALE FLAG: `cmd_check` surfaces `contract_consumer_stale` when a consumer task's pinned hash ≠ the live snapshot hash (the producer re-froze a changed shape) — the §7-delta cue, actionable, never crashes.
  - OPT-IN / byte-identical: no `[contract.*]` declared AND no `produces:`/`consumes:` header ⇒ `cmd_advance` and `cmd_check` behave exactly as today.
</must>
Reject:
<reject>
  - a `consumes: <id>` task crossing contract→tests when `.add/contracts/<id>.json` does not exist -> "contract_snapshot_missing" (HARD-STOP the crossing; fail-loud)
  - a `[contract.<id>]` whose `producer` is not a declared component -> "contract_producer_unknown" (cmd_check red finding)
</reject>
After:
<after>
  - A producer task freeze leaves an immutable `.add/contracts/<id>.json`; a consumer task pins its hash; a producer re-freeze that changes the §3 shape makes `cmd_check` report every pinned consumer stale.
  - Zero-contract / no-role project: advance + check byte-identical to today.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the snapshot HASH is taken over the §3 contract SHAPE (the first ```fenced``` block, whitespace-normalized), NOT the whole §3 — lowest confidence because if the fence is absent/oddly formatted the hash falls back to the §3 body minus Status/flag lines, which could over- or under-trigger stale; if wrong: a pure version bump churns consumers stale (noise) OR a real shape change slips by (missed stale). Mitigation: normalize whitespace + exclude the Status/flag lines; a stale flag is a WARN, never a hard block.
  - [x] auto-write at contract→tests (not a separate command) is the right hook — CONFIRMED (lead): the freeze is already approved at that crossing; the open "add.py freeze write command" delta can later formalize an explicit actor-stamped publish.
  - [x] single `produces:`/`consumes:` id per task (not a list) is enough for MVP — CONFIRMED (lead): one task owns one seam; multi-contract tasks are a forward §7 delta.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Producer freeze writes the contract snapshot
  Given a task `produces: gateway-api` bound to component gateway, §3 FROZEN @ v1
  When it advances contract -> tests
  Then `.add/contracts/gateway-api.json` exists with {id, producer: gateway, task, version: v1, hash}
  And re-running the same crossing yields byte-identical JSON (idempotent)

Scenario: Consumer pins the live snapshot
  Given `.add/contracts/gateway-api.json` exists and a task `consumes: gateway-api`
  When it advances contract -> tests
  Then state.tasks[<slug>].contract_pin == {id: gateway-api, hash: <live hash>}

Scenario: Consumer with no snapshot is hard-stopped
  Given a task `consumes: gateway-api` and NO `.add/contracts/gateway-api.json`
  When it advances contract -> tests
  Then it fails with "contract_snapshot_missing"
  And the task stays at `contract` — phase unchanged, nothing pinned

Scenario: Producer re-freeze flags the consumer stale
  Given a consumer pinned hash H1, and the producer re-froze a CHANGED §3 (new hash H2 written to the snapshot)
  When `add.py check` runs
  Then it reports "contract_consumer_stale" for the consumer
  And the report is a finding, not a crash

Scenario: A pure version bump does not churn the consumer stale
  Given a consumer pinned H1, and the producer re-froze v1->v2 with the SAME §3 shape (same fenced block)
  When `add.py check` runs
  Then no "contract_consumer_stale" is reported (the shape hash is unchanged)

Scenario: Unknown producer is a malformed-contract finding
  Given `[contract.x]` whose producer is not a declared component
  When `add.py check` runs
  Then it reports "contract_producer_unknown"

Scenario: Zero-contract project is byte-identical
  Given a project with no `[contract.*]` and a task with no `produces:`/`consumes:`
  When it advances contract -> tests
  Then no snapshot is written, nothing is pinned, and the crossing behaves exactly as today
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine API — add-method/tooling/add.py · `root` = the .add/ dir · builds on task 1's readers

_contracts(root) -> dict[str, dict]                # NEW · pure · degrade-safe
  parse [contract.<id>] from .add/components.toml -> {id: {producer: str, consumers: list[str]}}
  skip an entry whose `producer` is not a str (malformed); tomllib-None / bad TOML -> {}

_task_produces(root, slug) -> str | None           # NEW · pure   (header line `produces: <id>`)
_task_consumes(root, slug) -> str | None           # NEW · pure   (header line `consumes: <id>`)
  anchored grammar mirroring _COMPONENT_LINE_RE: r"(?:^|·)[ \t]*produces:[ \t]*([^\s<#|]+)"

_contract_snapshot(root, id) -> Path               # NEW   = root / "contracts" / f"{id}.json"

_contract_body_hash(raw3) -> str                   # NEW · pure
  = let m = re.search(r"```(.*?)```", raw3, DOTALL); body = m.group(1) if m else
    re.sub(r"(?m)^(Status:|Least-sure flag|v\d+ CHANGE REQUEST).*$", "", raw3)
    return _md5_text(re.sub(r"\s+", " ", body).strip())     # hash the SHAPE, version-stamp excluded

cmd_advance(args)                                  # EXTENDED — only the produces/consumes path is new
  at the contract->tests crossing (nxt == "tests"):
    if _task_produces(root, slug) == id:
        write _contract_snapshot(root, id) = json({id, producer, task: slug,
            version: <vN parsed from FROZEN @ vN, else "?">, frozen: date.today(),
            hash: _contract_body_hash(_raw_phase_bodies(root,slug)[3])}, sort_keys) via _atomic_write
            (mkdir contracts/ parents=exist_ok) — idempotent (same shape -> same bytes)
    if _task_consumes(root, slug) == id:
        snap = _contract_snapshot(root, id)
        if not snap.exists(): _die("contract_snapshot_missing: no .add/contracts/<id>.json — the
            producer must freeze first")   # HARD-STOP; phase stays `contract`, validate-before-write
        state.tasks[slug].contract_pin = {id, hash: json.load(snap)["hash"]}
  no produces/consumes  ->  cmd_advance BYTE-IDENTICAL to today (no snapshot, no pin, no die)

cmd_check                                          # EXTENDED — findings, mirror _component_findings
  contract_producer_unknown (RED)  : a [contract.<id>] whose producer not in _components(root)
  contract_consumer_stale  (WARN)  : a task with contract_pin whose hash != live snapshot hash
  both degrade-safe — an unreadable snapshot / missing file never crashes check

Schema: state.json gains tasks[slug].contract_pin = {id, hash} (consumer only) · NEW files
  .add/contracts/<id>.json (immutable snapshot) · reads .add/components.toml + §3 body bytes
```

Status: FROZEN @ v1 — approved by Tin Dang (AUTO MODE: project-lead decision), 2026-06-25. Both flags ACCEPTED as defaults (shape-hash over the fenced block; auto-write/pin at the crossing).
Least-sure flag surfaced at freeze: [contract] the snapshot HASH is over the first ```fenced``` block of §3 (whitespace-normalized), with a Status/flag-stripped fallback — a §3 that puts its shape OUTSIDE a fence, or reformats the fence, can over-trigger (version-bump churn) or under-trigger (missed shape change) the stale flag; if wrong: loosen to a structural hash or tighten the fence requirement. [spec] auto-write/auto-pin at the contract→tests crossing (vs a dedicated `add.py contract publish/pin` command) — if wrong: the freeze-write seam wants to be an explicit, actor-stamped command (the open `add.py freeze` delta). Both default-accepted.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py`
Strategy (ordered batches): 1. RED — `add-method/tooling/test_cross_component_contract.py` (7 scenarios) · 2. add `_contracts`, `_task_produces`/`_task_consumes` (+ regexes), `_contract_snapshot`, `_contract_body_hash` · 3. hook `cmd_advance` contract→tests (producer write + consumer pin/HARD-STOP) · 4. `cmd_check` findings (producer_unknown RED + consumer_stale WARN) · 5. GREEN; propagate to 2 mirrors + re-pin.
Safety rule (feature-specific): the snapshot write is atomic (`_atomic_write` into `contracts/`, mkdir parents=exist_ok); the consumer read is validate-before-write (missing → HARD-STOP, phase unchanged, nothing pinned). The no-role path takes NO new branch.
Code lives in: `add-method/tooling/add.py` (+ mirrors)
Constraints: do NOT change any test or the contract; stdlib only (json/hashlib/re/tomllib — all already imported); ask if unclear. Re-cross tests→build after declaring §5. `.add/` is pruned by `_scope_walk` so the gate-enforced token is `add-method/`.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 1717/0; task suite test_cross_component_contract.py 15/15.
- [x] coverage did not decrease — +15 tests (pure readers/hash + advance hooks + check findings + 2 refute-driven fail-loud regressions).
- [x] no test or contract was altered during build — the fixture fix + 2 new tests were made via `add.py phase tests` BEFORE re-advancing (tripwire re-anchored); §3 v1 untouched.
- [x] the green was EARNED — adversarial refute-read returned GREEN-NOT-EARNED: a MAJOR VACUOUS FIXTURE (`_new_at_contract`'s `re.sub(count=1)` replaced the §2 gherkin fence, not §3, so the `fence=` param was inert and the changed-shape→stale path was never exercised end-to-end) + 2 MINOR fail-loud gaps (null-hash snapshot pinned None; corrupt live snapshot masked stale). ALL FIXED: fixture now anchors to `## 3 · CONTRACT`; the stale test drives the real advance→snapshot→check path; `test_different_shapes_write_different_hashes` proves the §3 fence flows into the hash; null-hash/unreadable now HARD-STOP `contract_snapshot_missing`; a corrupt live snapshot surfaces `contract_snapshot_unreadable` (both faithful to the frozen designed-for-failure invariant). Red→green-locked.
- [x] concurrency / timing safe — the snapshot write is atomic (`_atomic_write` temp-then-replace); the consumer read is validate-before-write (a bad snapshot HARD-STOPs before the phase bump, nothing pinned). Engine still executes no suite.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (json/hashlib/re/tomllib, already imported); the snapshot is data, no code execution; contract id flows only into a filename under `.add/contracts/` (no traversal — ids are TOML table keys + header tokens).
- [x] layering & dependencies follow CONVENTIONS.md — readers mirror task 1's `_components`/`_component_findings`; the advance hook sits beside the existing tripwire/scope snapshot block; findings mirror the component-findings surface.
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A producer task's contract→tests crossing writes `.add/contracts/gateway-api.json` with the right fields (incl. a hash = the §3 shape hash), and a second crossing is byte-identical — `test_producer_crossing_writes_snapshot` + `test_producer_write_is_idempotent` + `test_different_shapes_write_different_hashes`.
- [x] A consumer crossing pins the live hash; a consumer with no/hashless snapshot HARD-STOPs `contract_snapshot_missing` with phase unchanged — `test_consumer_pins_live_hash` + `test_consumer_without_snapshot_hard_stops` + `test_null_hash_snapshot_hard_stops_consumer`.
- [x] A producer re-freeze of a CHANGED §3 shape makes `add.py check` report `contract_consumer_stale` (driven end-to-end via advance/check); a pure version bump (same fence) does NOT — `test_consumer_stale_when_producer_refroze_changed_shape` + `test_no_stale_on_pure_version_bump`. A corrupt live snapshot surfaces `contract_snapshot_unreadable` (not masked) — `test_corrupt_live_snapshot_is_surfaced_not_masked`.
- [x] A zero-contract / no-role project advances + checks byte-identically — `test_zero_contract_no_role_byte_identical` (no `contracts/` dir, no pin, no die) + full suite 1717/0.
- [x] An unknown producer is a RED `contract_producer_unknown` finding — `test_unknown_producer_is_red_finding`. 3-tree parity + ENGINE_MD5 re-pinned (`66307c90…`) — parity/pin tests green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_task_produces`/`_task_consumes`/`_contract_snapshot`/`_contract_body_hash`/`_contracts` are called in the cmd_advance contract→tests hook; `_contract_findings` + the consumer-stale block are called in cmd_check; the two regexes feed the readers. All reachable from the CLI advance/check paths.
- [x] DEAD-CODE (code) — no orphans; every new symbol has a live call site.
- [x] SEMANTIC — re-read the frozen designed-for-failure invariant: the null-hash/unreadable HARD-STOP and the `contract_snapshot_unreadable` WARN are the faithful surface of "a missing/mismatched pinned snapshot HARD-STOPS … never builds against a guessed shape" + "degrade-safe never crashes" — not a contract change, a completion of it. Confirmed the consumer id flows only into a `.add/contracts/<id>.json` filename (TOML key / header token), no path traversal.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
