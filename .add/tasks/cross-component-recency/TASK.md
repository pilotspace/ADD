# TASK: freeze-recency guard: a stale leftover snapshot must not admit a consumer into build

slug: cross-component-recency · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py` cmd_advance — the consumer HOLD at `nxt == "contract"` (L865-871): `if _cid and _cid in _cmap and not _contract_snapshot(root, _cid).exists(): _die("producer_contract_unfrozen")`. THE GAP: it gates on snapshot EXISTENCE only — a STALE LEFTOVER `.add/contracts/<cid>.json` (from a prior milestone, a producer that re-opened §3, or a hand-copied file) passes `.exists()` and RELEASES the hold, so the consumer writes §3 + pins (L909-920) against an out-of-date shape.
  - `add-method/tooling/add.py:cmd_phase` (L823-842) — the admin `phase <phase> <slug>` override runs `_build_entry` ONLY for `phase == "build"`; it does NOT run the `nxt == "contract"` consumer HOLD. So `add.py phase contract <consumer>` BYPASSES the producer-freeze hold entirely (the milestone's "cmd_phase HOLD bypass" to guard/document).
  - `add-method/tooling/add.py:_consumer_stale_guard` (L3963-3982) — the EXISTING completing-gate twin: HARD-STOPs `contract_consumer_stale` when the pinned hash drifted from live. It catches a producer re-freeze AFTER the consumer pinned — NOT a pre-existing stale leftover (a consistently-stale snapshot pins stale, matches stale-live, and sails through). This task closes the upstream hole.
  - `add-method/tooling/add.py` contract→tests crossing (L888-908) — the producer WRITES the snapshot `{id, producer, task, version, frozen(date), hash=_contract_body_hash(raw3c)}`; idempotent re-write only when hash/version changed. This is the recency source-of-truth: a CURRENT snapshot's hash == its producer task's live frozen §3 body-hash.
Context (working folder):
  - `add-method/tooling/test_cross_component.py` — the existing cross-component HOLD/pin suite (producer_contract_unfrozen · contract_snapshot_missing · the BE→FE ordering); the new recency tests live beside it. (confirm exact filename at tests.)
  - No `[contract.*]` / no `produces:`|`consumes:` in this repo (single-component) — tests build BE→FE fixtures in tmp projects.
  - `add-method/tooling/engine_pin.py` — ENGINE_MD5 re-pin after the tri-tree sync.
Honors (patterns / conventions):
  - OPT-IN + byte-identical-when-zero-components: no contracts / no produces|consumes → neither branch taken; single-component behavior is unchanged.
  - freeze = the cross-component gate (milestone shared decision): a consumer must never build against a guessed OR stale shape.
  - validate-then-write: the HARD-STOP precedes the phase bump (the task stays at `scenarios`); design-for-failure (reject before the state mutation).
  - admin-override-is-not-a-backdoor (phase-build-guard precedent, L831): `phase build` runs the SAME gate stack `advance` runs → `phase contract` should likewise run the consumer HOLD (consistency).
  - degrade-safe: an unreadable/absent producer §3 is NOT decided as stale (stays the existing existence HARD-STOP + a cmd_check warning); only a CONFIRMED hash mismatch / unfrozen producer blocks.
  - Tri-tree + pin: edit canonical `add-method/tooling/`, re-sync `.add/tooling/` + `_bundled/tooling/`, re-pin ENGINE_MD5.
Anchors the contract cites:
  - a recency rule at the consumer contract HOLD: snapshot EXISTS is necessary but not sufficient — if a LOCAL producer task backs the contract (`produces: <cid>`), its CURRENT §3 must be FROZEN with body-hash == the snapshot's hash; else STALE → HARD-STOP `producer_contract_stale`. No local producer (federation/external) → existence-only (recency is the producer repo's job via the federation version pin).
  - a shared hold helper (e.g. `_consumer_contract_hold(root, state, slug)`) called from BOTH cmd_advance (`nxt == "contract"`) and cmd_phase (`phase == "contract"`) — closes the bypass.
  - a cmd_check never-red WARN surfacing a consumer whose producer snapshot is stale/premature, early (consistent with `contract_consumer_stale`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: freeze-recency at the consumer contract HOLD — a stale leftover snapshot no longer admits a consumer; the `phase contract` admin override runs the same HOLD
Framings weighed: live-producer-hash-match (chosen — additive; existence-only stays for archived-producer/federation snapshots) · orphan-strict (block any snapshot with no live producer — too aggressive: breaks cross-milestone & federation consumes) · date/version-heuristic (compare `frozen` date / `version` — fragile vs the exact body-hash already recorded)
Must:
<must>
  - At the consumer contract HOLD (advancing scenarios->contract, AND the `phase contract <slug>` admin override), when a `consumes: <cid>` task targets a DECLARED contract whose snapshot EXISTS: if a LIVE producer task backs `<cid>` (a task whose §3 carries `produces: <cid>`), that producer's CURRENT §3 must be FROZEN with body-hash EQUAL to the snapshot's `hash`. Else HARD-STOP `producer_contract_stale` (the phase does not bump; nothing is pinned).
  - The HOLD logic is ONE shared helper called from BOTH cmd_advance (`nxt == "contract"`) and cmd_phase (`phase == "contract"`) — so the admin override is not a backdoor (mirrors the `phase build` → `_build_entry` precedent). The existing existence check (`producer_contract_unfrozen` when the snapshot is absent) is preserved inside the same helper.
  - No LIVE producer task backs `<cid>` (the producer was archived in a prior milestone, OR `<cid>` is a federation/external snapshot) -> EXISTENCE-ONLY, exactly as today (recency is the producer repo's responsibility via the federation version pin). A cross-milestone consume of a still-valid earlier-frozen contract is NOT blocked.
  - `check` surfaces a consumer whose live producer's §3 has drifted from the landed snapshot (or is no longer frozen) as a never-red WARN (`contract_producer_stale`), consistent with the existing `contract_consumer_stale` warning — measure, do not block.
  - OPT-IN + byte-identical-when-zero-components: no `[contract.*]` / no `produces:`|`consumes:` -> neither cmd_advance nor cmd_phase takes the branch; single-component behavior is unchanged.
  - Degrade-safe: an unreadable/missing producer §3 or snapshot is NOT decided as stale here (the absent-snapshot case stays the existing `producer_contract_unfrozen`/`contract_snapshot_missing` HARD-STOP); only a CONFIRMED hash mismatch or a confirmed-unfrozen live producer raises `producer_contract_stale`. The helper never raises on IO.
</must>
Reject:
<reject>
  - a consumer entering §3 against an EXISTING snapshot whose LIVE producer task has a drifted (≠) §3 body-hash, or whose live producer §3 is no longer FROZEN -> "producer_contract_stale"   (HARD-STOP at advance AND at `phase contract`; never-red WARN `contract_producer_stale` at check)
</reject>
After:
<after>
  - a stale leftover snapshot backed by a re-opened/drifted live producer HARD-STOPs the consumer at the contract boundary via EITHER `advance` or `phase contract`; the consumer stays at `scenarios`, nothing pinned.
  - a CURRENT snapshot (live producer frozen + hash matches) admits the consumer exactly as today; an archived-producer / federation / undeclared snapshot is existence-only as today.
  - `check` lists `contract_producer_stale` for a drifted consumer; silent when current.
  - the tri-tree stays byte-identical; ENGINE_MD5 re-pinned.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] recency = "a LIVE producer task's current frozen §3 body-hash must equal the snapshot hash"; a snapshot with NO live producer (archived-in-a-prior-milestone OR federation/external) stays EXISTENCE-ONLY — lowest confidence because the alternative ("any snapshot without a live producer is a stale leftover → block") is a defensible reading of the milestone wording but would BREAK two legitimate flows: a cross-milestone consumer of a contract frozen by a now-archived producer task, and every federation snapshot (which never has a local producer task). Live-producer-hash-match closes the real hole (a producer re-opening §3 mid-flight) WITHOUT those false-positives, and is purely additive (no existing test changes: `test_consumer_proceeds_once_snapshot_exists` uses a producerless hand-rolled snapshot → still existence-only → still green). If wrong (you want orphan-strict): add an orphan branch (snapshot with neither a live producer NOR a `[federation.<cid>]` entry → block) + migrate that existing test.
  - [ ] the `phase contract` override should ENFORCE the hold (consistency with `phase build`→`_build_entry`), not merely document it. If wrong (you want `phase` to stay a pure escape hatch): leave cmd_phase untouched, add only a glossary note + the cmd_check WARN.
  - [ ] staleness is a HARD-STOP at the hold (like `producer_contract_unfrozen`) + a never-red WARN at check. If wrong: make it WARN-only everywhere (no advance/phase block).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: stale leftover snapshot blocks the consumer at advance
  Given a live producer task `be` produces `gateway-api` and froze it (snapshot hash H1), then `be` re-opened §3 and edited it so its live body-hash drifted to H2 (snapshot still H1 on disk)
  When a consumer task `fe` (consumes: gateway-api) advances scenarios->contract
  Then it HARD-STOPs `producer_contract_stale`
  And `fe` stays at phase `scenarios` and pins nothing

Scenario: current snapshot admits the consumer
  Given a live producer `be` produced + froze `gateway-api` and its live §3 hash still equals the snapshot hash
  When `fe` (consumes: gateway-api) advances scenarios->contract
  Then it proceeds to `contract`
  And no error is raised

Scenario: no live producer is existence-only (archived-producer / federation)
  Given a snapshot `.add/contracts/gateway-api.json` exists but NO live task produces `gateway-api`
  When `fe` (consumes: gateway-api) advances scenarios->contract
  Then it proceeds to `contract` (recency is the producer repo's job)
  And behavior is byte-identical to today

Scenario: the phase-contract admin override runs the same hold
  Given a stale leftover snapshot whose live producer `be` drifted (as above)
  When an operator runs `add.py phase contract fe`
  Then it HARD-STOPs `producer_contract_stale` (the override is not a backdoor)
  And `fe`'s phase is unchanged

Scenario: phase-contract still enforces the absent-snapshot hold
  Given no snapshot exists for a declared `consumes: gateway-api`
  When an operator runs `add.py phase contract fe`
  Then it HARD-STOPs `producer_contract_unfrozen`
  And `fe`'s phase is unchanged

Scenario: check warns a drifted consumer, never red
  Given `fe` (consumes: gateway-api) and a live producer whose §3 drifted from the snapshot
  When `add.py check` runs
  Then it WARNs `contract_producer_stale` and exits 0
  And no FAIL line is added

Scenario: no role is byte-identical
  Given a task with no `consumes:` header
  When it advances scenarios->contract (or `phase contract`)
  Then it proceeds with no hold
  And single-component behavior is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Shared hold helper — called from BOTH cmd_advance (nxt=="contract") and cmd_phase (phase=="contract")
_consumer_contract_hold(root: Path, state: dict, slug: str) -> None
  # No `consumes:` header / undeclared cid -> return (byte-identical; a typo'd id is a cmd_check finding).
  # Let cid = _task_consumes(slug); require cid in _contracts(root).
  # snapshot = _contract_snapshot(root, cid)
  #   not snapshot.exists()            -> _die "producer_contract_unfrozen"          (PRESERVED)
  #   exists AND a live producer task backs cid AND it is STALE
  #                                    -> _die "producer_contract_stale"             (NEW)
  #   else (current | no live producer | federation/external) -> return (admit)
  # Validate-then-write: raises BEFORE the caller bumps the phase. Never raises on IO (degrade-safe).

# Recency predicate — pure, total
_producer_snapshot_stale(root: Path, cid: str, snap_hash: str|None) -> bool
  # True IFF a LIVE producer task backs cid (some task's §3 carries `produces: cid`) AND
  #   (that producer's live §3 is NOT FROZEN  OR  _contract_body_hash(its live §3) != snap_hash).
  # No live producer task -> False (archived-producer / federation/external = existence-only).
  # Unreadable/missing producer §3 or snap_hash None -> False (not confirmable -> not blocked here).
  # Reuses _task_produces scan + _raw_phase_bodies + the "FROZEN @ vN" marker + _contract_body_hash.

# cmd_advance:  if nxt == "contract": _consumer_contract_hold(root, state, slug)   # replaces the inline existence check
# cmd_phase:    if args.phase == "contract": _consumer_contract_hold(root, state, slug)   # closes the bypass (mirrors phase=="build" -> _build_entry)

# cmd_check (consumer loop): for each `consumes: cid` task whose snapshot exists and _producer_snapshot_stale(...) is True
#   -> warnings.append(("task '<slug>'", "contract_producer_stale — the live producer of '<cid>' changed/unfroze its §3 since the landed snapshot; re-cross the producer contract->tests, then re-enter")); never red.

Precedence at the hold: undeclared/no-consumes (return) -> snapshot absent (producer_contract_unfrozen) -> snapshot present + live producer stale (producer_contract_stale) -> admit.
Schema: reads .add/contracts/<cid>.json (the snapshot {id,producer,task,version,frozen,hash}) + each task's §3 body via _raw_phase_bodies; writes nothing in the helper. No new state fields.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
  ⚠ [contract] recency = "a LIVE producer task's current frozen §3 body-hash must equal the snapshot hash"; a snapshot with NO live producer task (archived-in-a-prior-milestone OR a federation/external pull) stays EXISTENCE-ONLY. WHY lowest-confidence: the milestone says "snapshot existence admits a stale leftover," which could be read as orphan-strict (block ANY snapshot with no live producer). I chose live-producer-hash-match because orphan-strict would BREAK a cross-milestone consumer of a still-valid earlier-frozen contract AND every federation snapshot (which never has a local producer task) — both legitimate. Live-producer-match closes the real hole (a producer re-opening §3 mid-flight) and is purely ADDITIVE (no existing test changes). COST if you want orphan-strict instead: add an orphan branch (no live producer AND no `[federation.<cid>]` entry -> block) + migrate `test_consumer_proceeds_once_snapshot_exists`. Also folded in: [contract] `phase contract` ENFORCES the hold (consistency with `phase build`), not just docs it.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject; 7 new tests (Recency class), 4 RED now for the right reason (stale-hold absent + `phase contract` bypasses both the stale AND the existence hold + the check WARN absent) + 3 GREEN pins (current admits · no-live-producer existence-only · no-role byte-identical). The existing Hold class (5 tests) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  Recency (test_cross_component_milestone.py):
  - test_stale_leftover_blocks_at_advance — producer drifted (live §3 hash ≠ snapshot) -> advance HARD-STOPs producer_contract_stale; fe stays scenarios
  - test_current_snapshot_admits_at_advance — GREEN PIN: live producer hash == snapshot -> advance to contract
  - test_no_live_producer_is_existence_only — GREEN PIN: hand-rolled snapshot, no producer task -> proceeds (cross-milestone/federation unbroken)
  - test_phase_contract_runs_stale_hold — `phase contract fe` on a drifted producer HARD-STOPs producer_contract_stale (bypass closed)
  - test_phase_contract_enforces_absent_hold — `phase contract fe` with no snapshot HARD-STOPs producer_contract_unfrozen
  - test_phase_contract_no_role_byte_identical — GREEN PIN: no-role task `phase contract` proceeds
  - test_check_warns_drifted_consumer_never_red — check WARNs contract_producer_stale, exit 0
</test_plan>

Tests live in: `add-method/tooling/test_cross_component_milestone.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_cross_component_milestone.py` `add-method/tooling/engine_pin.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. write red tests in test_cross_component_milestone.py (new Recency class) — RED (done). 2. add `_producer_snapshot_stale(root, cid, snap_hash)` pure predicate near `_task_produces` (scan root/tasks/* for a live producer; FROZEN + body-hash match). 3. add `_consumer_contract_hold(root, state, slug)` (existence + recency; preserves producer_contract_unfrozen) near the other completing guards. 4. cmd_advance: replace the inline `nxt=="contract"` existence check with the helper call. 5. cmd_phase: call the helper when `args.phase == "contract"`. 6. cmd_check consumer loop: add the never-red `contract_producer_stale` WARN. 7. green the suite (existing Hold class unchanged). 8. re-sync `.add/tooling/` + `_bundled/tooling/`, re-pin ENGINE_MD5.
Known-problem fixes: existence-vs-recency → keep the existence HARD-STOP, ADD a recency branch (snapshot present + live producer drifted) so the 3 green pins stay green · bypass → ONE shared helper from both cmd_advance and cmd_phase (the phase-build precedent) · false-positive → no-live-producer returns False (archived/federation existence-only); only a CONFIRMED frozen-hash-mismatch or unfrozen-live-producer blocks · degrade-safe → snap_hash None / unreadable producer §3 → False (not confirmable, not blocked) · validate-then-write → the helper `_die`s BEFORE the caller bumps the phase · tri-tree drift → re-sync all three + re-pin.
Strategy actually used: as planned, all 8 batches, no deviation. `_producer_snapshot_stale` scans `root/tasks/*` for a live `produces: <cid>` task (archived → moved out → existence-only, which is the intended rule); `_consumer_contract_hold` preserves the existing `producer_contract_unfrozen` existence HARD-STOP and adds the recency branch; both call sites (cmd_advance `nxt=="contract"` + cmd_phase `phase=="contract"`) share the helper, closing the override bypass exactly like the `phase build`→`_build_entry` precedent. Verified by an independent refute-read (EARNED) + a live BE→FE CLI repro (drift → advance HARD-STOP + phase-contract HARD-STOP + check WARN). One disclosed degrade-safe residual (R1: a hash-less snapshot is existence-only — frozen behavior, forward delta).
Safety rule (feature-specific): the recency predicate is PURE + TOTAL (never raises on IO); a stale HARD-STOP fires only on a CONFIRMED mismatch, never on a degraded read.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2215/0; dogfood `check` 459/0; `audit` exit 0
- [x] coverage did not decrease — +7 Recency tests; the existing Hold class (5) + the whole suite stay green
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the only test edit (the Recency class) was made in the TESTS phase before crossing
- [x] the green was EARNED — independent refute-read (agent affb3fcd) verdict EARNED: 4/7 tests discriminating (fail if reverted), 3 legitimate regression guards, the drift fixture faithfully models a stale leftover; byte-identical confirmed for the real repo
- [⚠] concurrency / timing — synchronous file reads, no concurrency residue. NOTE: this is a TRUST-LAYER gate change (tightens the consumer freeze HOLD + closes the `phase contract` override bypass) → ESCALATED to the human even under autonomy:auto (per the flow-honesty lesson), not auto-resolved.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; the predicate is PURE+TOTAL (never raises on IO)
- [x] layering & dependencies follow CONVENTIONS.md — predicate beside `_task_produces`; hold beside the cross-component path; reuses `_contract_body_hash`/`_raw_phase_bodies`; tri-tree re-synced + ENGINE_MD5 re-pinned (286ecae8)
- [⚠] a person reviewed and approved — ESCALATING to Tin (trust-layer gate edit + 1 disclosed degrade-safe residual R1); gate is human-decided, NOT auto-resolved

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] a live producer that re-opened/drifted its §3 makes a NEW consumer HARD-STOP `producer_contract_stale` at scenarios->contract — confirmed by test_stale_leftover_blocks_at_advance + a live BE→FE repro
- [ ] `add.py phase contract fe` (the admin override) runs the SAME hold (stale -> producer_contract_stale; absent -> producer_contract_unfrozen), no longer a backdoor — confirmed by test_phase_contract_runs_stale_hold + test_phase_contract_enforces_absent_hold
- [ ] a current snapshot (live producer frozen + hash matches), a no-live-producer leftover (cross-milestone/federation), and a no-role task all proceed exactly as today — confirmed by the 3 green pins + the existing Hold class (5 tests) staying green
- [ ] `check` lists `contract_producer_stale` for a drifted consumer and stays exit 0 (measure-not-block) — confirmed by test_check_warns_drifted_consumer_never_red + a live `check` run
- [ ] zero-component / no produces|consumes is byte-identical — confirmed by the full suite (no other test moved) + the no-role pins
- [ ] the three engine trees stay byte-identical + ENGINE_MD5 re-pinned — confirmed by md5 ×3 + the engine-pin/parity tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_consumer_contract_hold` called from cmd_advance (`nxt=="contract"`) AND cmd_phase (`phase=="contract"`); `_producer_snapshot_stale` called from the hold + the cmd_check WARN; `contract_producer_stale` surfaces at check. Confirmed by the live BE→FE CLI repro (advance + phase + check all fired) + the refute-read's probe E.
- [x] DEAD-CODE (code) — no orphan: both new symbols have live call sites + tests. The `state` param of `_consumer_contract_hold` is intentionally unused (call-site symmetry with `_build_entry(root, state, slug, …)`), documented in the docstring (refute R2 — acceptable, cosmetic).
- [x] SEMANTIC (prose / non-code) — read the FROZEN §3 + the existing cross-component HOLD/pin path; confirmed the recency rule preserves the existence HARD-STOP and is additive (the 3 green pins prove no regression). Byte-identical for the real repo verified (no `produces:`/`consumes:` header tokens, no contracts/ dir).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (residual R1 disclosed → CLOSED this task)
By: agent affb3fcd (general-purpose, independent) + self · adversarially checked: A byte-identical for the 216-task real repo (early return on no-consumes; no contracts/ dir) · B false-positive on a current snapshot (producer at done keeps FROZEN; version-only bump doesn't churn the fence-hash; self-consume) · C false-negative/games (empty §3 fence → fail-closed True; multiple producers; corrupt snapshot) · D test reality (4/7 discriminating + 3 regression guards; the drift fixture faithfully models a stale leftover) · E cmd_phase wiring (only `phase contract` fires it; `_build_entry`/other targets unaffected) · F dead `state` param (documented, cosmetic).
Residual R1 (DISCLOSED → CLOSED this task, at Tin's gate direction): a snapshot JSON with a MISSING/null `hash` degraded the recency check to existence-only. The frozen §3 BEHAVIOR is kept (still existence-only, NOT blocked — no §3 change) but cmd_check now SURFACES it as a never-red WARN `contract_snapshot_hashless` (test_check_warns_hashless_snapshot_never_red + a live `check` repro; ENGINE_MD5 c757ce53). R2 (dead `state` param, documented for `_build_entry` symmetry) + R3 (loose docstring) left as cosmetic.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose live-producer-hash-match; rejected orphan-strict (block any snapshot with no live producer — too aggressive: breaks cross-milestone & federation consumes) · date/version-heuristic (compare `frozen` date / `version` — fragile vs the exact body-hash already recorded)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, all 8 batches, no deviation. `_producer_snapshot_stale` scans `root/tasks/*` for a live `produces: <cid>` task (archived → moved out → existence-only, which is the intended rule); `_consumer_contract_hold` preserves the existing `producer_contract_unfrozen` existence HARD-STOP and adds the recency branch; both call sites (cmd_advance `nxt=="contract"` + cmd_phase `phase=="contract"`) share the helper, closing the override bypass exactly like the `phase build`→`_build_entry` precedent. Verified by an independent refute-read (EARNED) + a live BE→FE CLI repro (drift → advance HARD-STOP + phase-contract HARD-STOP + check WARN). One disclosed degrade-safe residual (R1: a hash-less snapshot is existence-only — frozen behavior, forward delta).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] document the 3 new cross-component fail-loud codes in skill/add/components.md + glossary — `producer_contract_stale` (recency HARD-STOP), `contract_producer_stale` + `contract_snapshot_hashless` (never-red check WARNs) (evidence: §0 named the doc gap; overlaps the component-worked-example task's doc sweep)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a trust-layer gate edit (tightening a HOLD / closing an admin-override bypass) ESCALATES the verify gate to the human even under autonomy:auto — it is not auto-resolved (evidence: this gate + federation-harden were both human-decided) [folded foundation-version 58]
- [ADD · folded] "close gap before gate" can mean SURFACE-not-block: the refute's R1 was closed with a never-red WARN that keeps the frozen §3 behavior (still existence-only) yet makes the degraded state visible — no §3 change, no re-freeze (evidence: Tin chose close-R1-now; added contract_snapshot_hashless) [folded foundation-version 58]
- [TDD · folded] a recency/staleness guard earns green only via a refute-read probing BOTH false-positives (current snapshot · version-only bump · archived producer · self-consume) AND false-negatives (drift · empty fence · hash-less snapshot) — fixture coverage alone misses the degrade paths (evidence: agent affb3fcd surfaced R1, the hash-less blind spot) [folded foundation-version 58]
