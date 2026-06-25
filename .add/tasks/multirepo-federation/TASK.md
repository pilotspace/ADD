# TASK: Multirepo Federation

slug: multirepo-federation · created: 2026-06-25 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project `auto`: method-defining — adds a new `federate` command that reads an external repo's file + writes a local snapshot. Bounded fail-loud transport + a human verify guard the blast radius. -->
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
  - `add-method/tooling/add.py:_contracts`/`_contract_snapshot` (task 3) — the contract registry + the local snapshot path. Federation lands a REMOTE producer repo's snapshot at the SAME local `.add/contracts/<id>.json`, so tasks 3/4 then treat mono + multi-repo identically.
  - `add-method/tooling/add.py:_atomic_write` (L217) — the design-for-failure write for the landed snapshot.
  - `add-method/tooling/add.py` CLI registration (`sub.add_parser(...)` ~L6517) + `cmd_check` — register a new `federate` command; surface a federation finding at check.
Context (working folder):
  - NEW manifest section `[federation.<id>]` in `.add/components.toml` (source path + optional pin); NEW `cmd_federate`; NEW test `add-method/tooling/test_multirepo_federation.py`. 3-tree parity + re-pin.
Honors (patterns / conventions):
  - INVARIANT (MILESTONE): mono vs multi-repo differ ONLY in state-location + snapshot-transport — federation transports the IMMUTABLE frozen snapshot; each repo's state.json stays git-native + independent.
  - INVARIANT: designed-for-failure — a missing / unreadable / id-mismatched / version-mismatched source HARD-STOPS the pull (never lands a guessed shape, never builds blind).
  - INVARIANT: opt-in — no `[federation.*]` ⇒ nothing changes; `federate` is an explicit operator command.
  - ENGINE INVARIANT: no code execution — federation reads a JSON file + writes a JSON file.
  - red/green TDD · 3-tree parity · atomic write.
Anchors the contract cites: `cmd_federate` · `_federation` · `_contract_snapshot` · `_atomic_write`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Multi-repo federation — a consumer repo PULLS a producer repo's published, immutable contract snapshot by id (fail-loud), landing it locally so the rest of ADD treats mono + multi-repo the same
Framings weighed: pull-by-manifest — the consumer declares a `[federation.<id>]` source path + an explicit `add.py federate pull` (chosen — operator-driven, no network, fail-loud, lands the snapshot where tasks 3/4 already look) · a daemon/auto-sync that watches producer repos (out of scope, stateful) · a shared mutable registry across repos (rejected by the milestone Out-list)
Must:
<must>
  - A consumer repo DECLARES `[federation.<id>]` in `.add/components.toml` with `source = "<path to the producer repo's .add/contracts/<id>.json>"` (relative to the project root) and an OPTIONAL `pin = "vN"` (the version it expects).
  - `add.py federate pull <id>` reads the source snapshot and LANDS it at the local `.add/contracts/<id>.json` (atomic write, `contracts/` created if absent). The producer's snapshot is the published artifact (immutable — task 3 wrote it on the producer's freeze).
  - designed-for-failure / fail-loud: `<id>` not in the manifest -> `federation_unknown`; source unreadable/absent -> `federation_source_missing`; source not valid JSON / wrong id / no hash -> `federation_snapshot_invalid`; `pin` set and source `version` ≠ pin -> `federation_version_mismatch`. Every failure HARD-STOPS and lands NOTHING.
  - after a successful pull the local snapshot equals the producer's, so a `consumes: <id>` task then holds/pins via tasks 3/4 exactly as in a monorepo.
  - `cmd_check`: a declared `[federation.<id>]` whose source is unreadable surfaces `federation_source_unreadable` (WARN), so a broken join is visible before a pull.
  - OPT-IN: no `[federation.*]` ⇒ `check` + every other path byte-identical; `federate` only acts when invoked.
</must>
Reject:
<reject>
  - `federate pull <id>` where `<id>` has no `[federation.<id>]` -> "federation_unknown"
  - source path unreadable / absent -> "federation_source_missing"
  - source not valid JSON, or its `id` ≠ `<id>`, or it has no `hash` -> "federation_snapshot_invalid"
  - manifest `pin = vN` but source `version` ≠ vN -> "federation_version_mismatch"
</reject>
After:
<after>
  - The consumer repo holds a byte-copy of the producer's frozen snapshot at `.add/contracts/<id>.json`; a missing/mismatched source hard-stopped rather than landing a guess.
  - No-federation project: byte-identical to today.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a LOCAL FILESYSTEM PATH source (a sibling checkout) is enough transport for MVP — lowest confidence because real federation often spans CI/remote repos (git URL, artifact registry); if wrong: the manifest source grammar needs a fetch scheme. Mitigation: the `source` is opaque to the lander (just a readable path); a future scheme can resolve URL→local-temp before the same validate+land path, so the fail-loud core is reused.
  - [x] the producer's `.add/contracts/<id>.json` IS the publish artifact (no separate `publish` command) — CONFIRMED (lead): task 3 already writes the immutable snapshot on freeze; "publish" = expose that file (commit it), not a new engine write. Keeps the surface minimal.
  - [x] pull OVERWRITES the local snapshot unconditionally on success — CONFIRMED (lead): the producer is the source of truth for the seam; the consumer's `contract_consumer_stale` (task 3) then flags any consumer that had pinned an older hash.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Pull lands the producer's published snapshot
  Given `[federation.gateway-api]` declares source = a sibling repo's frozen `.add/contracts/gateway-api.json`
  When the operator runs `add.py federate pull gateway-api`
  Then the local `.add/contracts/gateway-api.json` byte-equals the producer's snapshot
  And the command prints the landed version + hash

Scenario: Unknown contract is refused
  Given no `[federation.nope]` in the manifest
  When `add.py federate pull nope`
  Then it fails "federation_unknown"
  And nothing is written under `.add/contracts/`

Scenario: Missing source hard-stops
  Given `[federation.gateway-api]` whose source path does not exist
  When `add.py federate pull gateway-api`
  Then it fails "federation_source_missing"
  And no local snapshot is created

Scenario: Invalid source snapshot hard-stops
  Given a source file that is not valid JSON, or whose id ≠ gateway-api, or has no hash
  When `add.py federate pull gateway-api`
  Then it fails "federation_snapshot_invalid"
  And no local snapshot is written

Scenario: Pinned version mismatch hard-stops
  Given `[federation.gateway-api]` with pin = "v2" but the source snapshot version is "v1"
  When `add.py federate pull gateway-api`
  Then it fails "federation_version_mismatch"
  And no local snapshot is written

Scenario: check surfaces a broken join
  Given `[federation.gateway-api]` whose source is unreadable
  When `add.py check`
  Then it WARNs "federation_source_unreadable" (never red on its own)

Scenario: No federation is byte-identical
  Given a project with no `[federation.*]`
  When `add.py check`
  Then output is byte-identical to today
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine API — add-method/tooling/add.py · builds on task 3's _contracts/_contract_snapshot/_atomic_write

Manifest (.add/components.toml):
  [federation.<id>]
  source = "<path to producer repo's .add/contracts/<id>.json, relative to project root>"
  pin    = "vN"        # OPTIONAL — the version the consumer expects

_federation(root) -> dict[str, dict]                 # NEW, pure, degrade-safe
  parses [federation.<id>] -> {id: {"source": str, "pin": str|None}}; any read error -> {}

cmd_federate(args)  (args.action == "pull", args.id)  # NEW command: federate pull <id>
  fed = _federation(root)
  if id not in fed                          -> _die("federation_unknown: ...")
  src = (root.parent / fed[id]["source"])              # resolved under the project root
  raw = read(src)        # OSError                     -> _die("federation_source_missing: ...")
  snap = json.loads(raw) # ValueError, or snap["id"] != id, or not snap.get("hash")
                                                       -> _die("federation_snapshot_invalid: ...")
  if fed[id]["pin"] and snap.get("version") != fed[id]["pin"]
                                                       -> _die("federation_version_mismatch: ...")
  _atomic_write(_contract_snapshot(root, id), raw)     # land the byte-copy (mkdir contracts/)
  print("federated '<id>' <version> <hash> from <source>")
  # EVERY failure HARD-STOPS and writes nothing (designed-for-failure / never build blind).

cmd_check(root)                                        # EXTENDED
  for each declared [federation.<id>] whose source is unreadable
      -> WARN "federation_source_unreadable: ..."      # surfaces a broken join, never red alone

opt-in:  no [federation.*]  ->  check + every path BYTE-IDENTICAL to today
```

Least-sure flag surfaced at freeze: [contract] the `source` is a LOCAL filesystem path (a sibling checkout) — real federation often spans remote/CI repos (git URL, artifact registry). Why/cost: if a fetch scheme is needed sooner than expected, the manifest `source` grammar widens; the cost is bounded because `source` is opaque to the lander — a future scheme resolves URL→local-temp then reuses the SAME validate+atomic-land core, so the fail-loud guarantee is preserved.
Status: FROZEN @ v1 — approved by Tin Dang (AUTO MODE: project-lead decision), 2026-06-25. Both open assumptions confirmed.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of cmd_federate's branches + the check finding.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - pull-lands (byte-equal + printed version/hash) · unknown-refused (nothing written) · missing-source-hardstop · invalid-source-hardstop (×3: bad-json / wrong-id / no-hash) · version-mismatch-hardstop · check-surfaces-unreadable · no-federation-byte-identical
</test_plan>

Tests live in: `add-method/tooling/test_multirepo_federation.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py`
Strategy (ordered batches): 1. RED — `add-method/tooling/test_multirepo_federation.py` (the scenarios) · 2. add `_federation` reader + `cmd_federate` (pull: lookup→read→validate→version-pin→atomic land, every failure HARD-STOPS) + register the `federate` CLI command + the `cmd_check` WARN · 3. GREEN; propagate to 2 mirrors + re-pin.
Safety rule (feature-specific): validate-before-write — `_atomic_write` lands the snapshot ONLY after every check passes; a failure writes nothing. Reads are degrade-safe (`_federation` never raises).
Code lives in: `add-method/tooling/add.py` (+ mirrors)
Constraints: do NOT change any test or the contract; stdlib only (tomllib + json + the existing `_atomic_write`); ask if unclear. Re-cross tests→build after declaring §5. `.add/` is pruned by `_scope_walk` so the gate-enforced token is `add-method/`.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 1733/0; task suite test_multirepo_federation.py 11/11.
- [x] coverage did not decrease — +11 federation tests (incl. the exact-byte-copy CRLF case + a tightened no-contracts-dir reject assert added during the self-heal). +1 LIFECYCLE entry in test_min_pillar (a new subcommand MUST register there — the meta-test's own contract).
- [x] no test or contract was altered during build to weaken it — §3 v1 untouched. The refute-read drove a self-heal: I phased BACK to tests (re-anchoring the tripwire), STRENGTHENED the suite (added the CRLF byte-copy test + tightened the unknown-id reject), re-crossed to build, then fixed the impl. test_min_pillar's LIFECYCLE update is required by its own self-maintaining contract ("a new subcommand fails here until added"), not a weakening.
- [x] the green was EARNED — refute-read v1 returned GREEN-NOT-EARNED on a determinative MINOR: the frozen §3 promises a BYTE-COPY but the impl landed via text-mode `_atomic_write` (CRLF→LF translation) and the test was overfit to a `json.dumps` (\n-only) fixture. SELF-HEALED faithfully to the frozen contract: new `_atomic_write_bytes` lands the raw source bytes unchanged; a new CRLF test proves the exact copy (was RED on the old impl, now GREEN). Finding 2 (weak absent-file assert) tightened to "no contracts/ dir"; Finding 3 (tomllib<3.11 degradation) documented. Findings 4 + path-trust + pin-coercion were confirmed ACCEPTABLE by the reviewer (operator-authored manifest; validate-gates guard a stray read).
- [x] concurrency / timing safe — the land is a temp-then-`os.replace` atomic write (crash-safe, no orphan temp via `finally`); every failure HARD-STOPS before the write, so nothing partial lands.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (tomllib/json + the new binary atomic write). `source` is an operator-authored manifest path; a stray/absolute/traversal path can only land a file that ALSO validates as JSON with the matching id + a hash — never a guessed shape. Trust boundary documented as a §7 delta.
- [x] layering & dependencies follow CONVENTIONS.md — `cmd_federate` sits beside `cmd_check`; `_federation` beside `_contracts`; `_atomic_write_bytes` beside `_atomic_write`; the `federate` parser beside `check`.
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] After `federate pull gateway-api`, the local contracts snapshot byte-equals the producer's source file — `test_pull_lands_producer_snapshot` + `test_pull_is_an_exact_byte_copy` (CRLF source lands unchanged via `_atomic_write_bytes`).
- [x] Each of unknown / missing-source / invalid-source(×3) / version-mismatch HARD-STOPS with its own code AND leaves no local snapshot — the reject tests assert both the code AND the absent file (`test_unknown` now asserts no `contracts/` dir at all).
- [x] `check` WARNs `federation_source_unreadable` for a broken join (`test_check_warns_unreadable_source`) and is byte-identical with no federation declared (`test_no_federation_clean` + full suite green).
- [x] 3-tree parity (md5 unique=1) + ENGINE_MD5 re-pinned (`2669f273…`) — parity/pin tests green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_federate` is wired via the `federate`→`pull` subparser (`set_defaults(func=cmd_federate)`); it calls `_federation`, `_contract_snapshot`, `_atomic_write_bytes`. `_federation` is also called in `cmd_check` (the WARN). `_atomic_write_bytes` is referenced by `cmd_federate`. All reachable.
- [x] DEAD-CODE (code) — no orphans; every new symbol (`_federation`, `cmd_federate`, `_atomic_write_bytes`) has a caller proven by the suite.
- [x] SEMANTIC — re-read the refute-read + the self-heal: the byte-copy contract is now honored literally (binary land + a CRLF test that was red on the old impl). The two open §7 deltas (remote-source scheme; manifest path-trust) are bounded + disclosed, not blockers.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): federate-pull reject rate (which code) · stale-pull frequency (`contract_consumer_stale` after a pull).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] federation `source` is a LOCAL filesystem path only — a remote scheme (git URL / artifact registry, resolve→local-temp→reuse the validate+land core) would cover CI/cross-machine federation (evidence: §3 least-sure flag; real multi-repo often spans machines).
- [SPEC · open] the manifest `source` is unsanitized (absolute / `../` traversal resolves) — acceptable for an operator-authored manifest, but a path-confinement guard (source must resolve under a sibling-repo allowlist) would harden it (evidence: refute-read path-safety note; the validate-gates already prevent landing a non-contract file).
- [SPEC · open] no `federate publish` command — the producer's `.add/contracts/<id>.json` IS the artifact today; an explicit publish-to-a-shared-location verb may help when repos don't share a parent dir (evidence: §1 assumption confirmed for MVP).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a byte-equality claim needs a fixture that can actually DIFFER in bytes — a `json.dumps` (\n-only) fixture made the byte-copy assert vacuous; the CRLF case exposed the text-mode-translation bug (evidence: refute-read Finding 1; red→green after `_atomic_write_bytes`). [folded foundation-version 50]
