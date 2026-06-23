# TASK: milestone-confirm refuses unfilled cross-task contracts

slug: contract-fill-gate · created: 2026-06-23 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `add-method/tooling/add.py:cmd_milestone_confirm` — the human gate that flips `confirmed:true`; today it checks only `unknown_milestone` then writes. Add the content check BEFORE the write.
  - `add-method/tooling/add.py` (new) `_section_unfilled(md_text, header)` — the shared placeholder predicate (task `build-expectations-gate` reuses it for §6).
  - MILESTONE.md path: `root/milestones/<slug>/MILESTONE.md` — read via the existing `(root / "milestones" / slug / "MILESTONE.md")` pattern.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-aim (any engine byte change). `test_min_pillar` LIFECYCLE: NO change (milestone-confirm already exercised).
Context (working folder): `.add/milestones/flow-enforcement/MILESTONE.md` (this milestone, contracts FILLED — must still confirm green); the scaffold default `- <contract name> -> owning task <slug>` is the canonical UNFILLED shape.
Honors (patterns / conventions): mirrors the `unflagged_freeze` / `_flag_well_formed` PRESENCE-gate pattern (check filled, never quality); validate-then-write (refuse before `save_state`); grandfather-by-absence (like `_milestone_confirmed`).
Anchors the contract cites: `cmd_milestone_confirm` · `_section_unfilled` · reject `milestone_contracts_unfilled`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: content-aware milestone-confirm — "confirmed" means the cross-task contracts are actually present
Framings weighed: gate at milestone-confirm (chosen — confirm is already the human checkpoint; one place) · gate at new-task (rejected — fires repeatedly, further from the authoring moment) · a separate `check` warning only (rejected — a warning is not a gate; the request is a refusal)
Must:
<must>
  - SCOPE (v2): the content gate fires ONLY for a milestone that OPTED IN — i.e. its state record HAS a `confirmed` key (created with `--await-confirm`). A grandfathered no-key milestone is NEVER content-gated; `milestone-confirm` on it stays the plain stamp (this keeps the census + every existing flow byte-green).
  - for an OPTED-IN milestone: when its MILESTONE.md `## Shared / risky contracts` section is still a placeholder (contains a `<…>` token) or empty, REFUSE and write nothing
  - for an OPTED-IN milestone whose section is FILLED (≥1 non-blank bullet, no `<…>` token), confirm normally
  - when the section is ABSENT entirely (legacy/hand-edited MILESTONE.md), grandfather — confirm normally, never refuse
  - the predicate is a single reusable `_section_unfilled(md_text, header)` (so `build-expectations-gate` reuses it for §6) — "confirmed:true" now MEANS the cross-task contracts were present at confirm time
</must>
Reject:
<reject>
  - milestone-confirm on a milestone whose contracts section is a `<…>` placeholder/empty -> "milestone_contracts_unfilled"
  - milestone-confirm on an unknown slug -> "unknown_milestone"   (existing — unchanged, runs FIRST)
</reject>
After:
<after>
  - `confirmed:true` is set ONLY when the contracts section is filled or legitimately absent; a refused confirm leaves `confirmed:false` and state byte-unchanged
  - `_section_unfilled` exists as a pure helper, exercised by this task and available to the next
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ OPTED-IN scope (confirmed-key present) is the right boundary — lowest confidence because a determined user could still milestone-confirm an opted-in milestone after deleting the contracts heading (absent→grandfather) to bypass; chosen because it folds the check into the opt-in contract already drawn by --await-confirm and ripples to ZERO existing tests beyond the feature's own; if wrong: the gate misses a milestone someone deliberately un-scaffolded (cost: low + self-defeating — they lose the contract scaffold too).
  - [x] placeholder signal = the `<…>` angle-bracket token (the scaffold's own marker) — confirmed: every scaffold field uses `<…>`; a filled line never does.
  - [x] gate lives at confirm, opted-in only — confirmed by the change-request: gating all milestones broke the census; opted-in contains it.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: filled contracts confirm
  Given a milestone created --await-confirm whose "## Shared / risky contracts" has a real bullet (no <…>)
  When add.py milestone-confirm <slug>
  Then confirmed:true is recorded and the success line prints

Scenario: opted-in placeholder contracts refuse
  Given a milestone created --await-confirm whose "## Shared / risky contracts" still reads "- <contract name> -> owning task <slug>"
  When add.py milestone-confirm <slug>
  Then it dies "milestone_contracts_unfilled"
  And confirmed stays false and state.json is byte-unchanged

Scenario: opted-in empty contracts section refuse
  Given a milestone created --await-confirm whose contracts header is present but has no bullet under it
  When add.py milestone-confirm <slug>
  Then it dies "milestone_contracts_unfilled"
  And nothing is written

Scenario: grandfathered no-key milestone is NOT content-gated (census-safe)
  Given a milestone created WITHOUT --await-confirm (no confirmed key) whose contracts are still the scaffold placeholder
  When add.py milestone-confirm <slug>
  Then confirmed:true is recorded (the plain stamp — the content gate never runs)
  And the existing census walk stays green

Scenario: legacy MILESTONE.md with no contracts section is grandfathered
  Given an opted-in milestone whose MILESTONE.md has no "## Shared / risky contracts" heading at all
  When add.py milestone-confirm <slug>
  Then confirmed:true is recorded (no refusal)
  And no other behavior changes

Scenario: unknown slug still refuses first
  Given no milestone "ghost"
  When add.py milestone-confirm ghost
  Then it dies "unknown_milestone"
  And the contracts check never runs
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py milestone-confirm <slug>
  ok  -> confirmed:true            (NOT opted-in [no confirmed key] · OR opted-in + contracts FILLED · OR section ABSENT/legacy)
  4xx -> error: "unknown_milestone"            (slug not in state — checked FIRST, unchanged)
       | "milestone_contracts_unfilled"        (OPTED-IN [confirmed key present] AND section PRESENT but a <…> placeholder/empty)
Predicate (new, pure): _section_unfilled(md_text: str, header: str) -> bool
  True  iff the `header` section is PRESENT and (has no non-blank bullet OR contains a `<…>` token)
  False iff the section is filled (≥1 real bullet, no `<…>`) OR is ABSENT entirely (grandfather)
Gate scope: the gate runs _section_unfilled ONLY when the milestone record contains a "confirmed" key
  (opted into --await-confirm). No key → grandfathered → plain stamp, gate skipped.
Order in cmd_milestone_confirm: unknown_milestone -> (opted-in? else stamp) -> read MILESTONE.md -> _section_unfilled gate -> write
Schema: state.json milestones[slug].confirmed flip is the ONLY write; refusal writes nothing (validate-then-write)
```

Status: FROZEN @ v2 — approved by Tin Dang (change-request from v1: content gate scoped to OPTED-IN milestones [confirmed-key present] only; grandfathered no-key milestones keep the plain stamp — contains the census ripple, folds the check into the meaning of "confirmed")
Least-sure flag surfaced at freeze:
[spec] OPTED-IN scope (confirmed-key present) is the gate boundary — biggest risk in the bundle: a determined user could delete the contracts heading on an opted-in milestone (absent→grandfather) to bypass. Chosen because it folds the requirement into the opt-in contract --await-confirm already draws, and ripples to ZERO existing tests beyond this feature's own; cost if wrong is low + self-defeating (they lose the contract scaffold). All other points (placeholder = `<…>` token, gate-at-confirm, unknown-first) are confirmed, not flagged.
risk: high   <!-- method-defining engine change -->
autonomy: conservative
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject + the predicate (≥6 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_optedin_filled_contracts_confirm: --await-confirm + fill contracts / milestone-confirm / assert confirmed:true
  - test_optedin_placeholder_refuse: --await-confirm, leave scaffold "- <contract name> -> ..." / milestone-confirm / assert SystemExit + "milestone_contracts_unfilled" + confirmed still false + state bytes unchanged
  - test_optedin_empty_section_refuse: --await-confirm, header present no bullet / milestone-confirm / assert refuse + nothing written
  - test_no_key_milestone_not_gated: new-milestone WITHOUT --await-confirm (placeholder contracts) / milestone-confirm / assert confirmed:true (census-safe — gate skipped)
  - test_optedin_legacy_no_section_grandfathered: --await-confirm, strip the heading / milestone-confirm / assert confirmed:true
  - test_unknown_slug_still_first: milestone-confirm ghost / assert "unknown_milestone" (contracts check never runs)
  - test_section_unfilled_predicate: unit-table the helper (placeholder/empty -> True · filled/absent -> False)
</test_plan>

Tests live in: `add-method/tooling/test_contract_fill_gate.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_contract_fill_gate.py` `add-method/tooling/test_confirm_parent.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. add `_section_unfilled` helper + the gate in `cmd_milestone_confirm` (canonical add.py). 2. `cp` canonical → 2 mirror trees. 3. re-aim engine_pin.py ENGINE_MD5. 4. full suite green.
Safety rule (feature-specific): validate-then-write — the `_section_unfilled` refusal must `_die` BEFORE the `confirmed=True` assignment / `save_state`; a blocked confirm mutates nothing.
Code lives in: `add-method/tooling/add.py` (canonical) → propagated byte-identical to the 2 mirror trees
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1577/0 (`python3 -m unittest discover`), incl. red→green test_contract_fill_gate.py [7]
- [x] coverage did not decrease — +7 new tests; the 2 adapted test_confirm_parent tests now fill contracts (legitimate v2 adaptation), 8 others untouched & green
- [x] no test or contract was altered during build — §3 FROZEN @ v2 unchanged; only NEW test_contract_fill_gate.py + the 2 sanctioned test_confirm_parent adaptations (in §5 scope) + engine_pin re-aim
- [x] the green was EARNED, not gamed — adversarial refute-read (below); the gate fires on a real _section_unfilled read of the on-disk MILESTONE.md, not a fixture flag; the 2 opted-in refuse tests assert SystemExit + state-bytes-unchanged, the no-key test proves the gate is genuinely skipped (not vacuously passing)
- [x] concurrency / timing of the risky operation is safe — no new IO/threading; one extra in-memory file read before the existing single-writer save_state; validate-then-write means a refused confirm writes NOTHING
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports (reuses re/MILESTONE_FILE already present); reads only the project's own MILESTONE.md
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the `_flag_well_formed`/`unflagged_freeze` PRESENCE-gate pattern; 3-tree engine parity held (md5 428ca1d1)
- [ ] a person reviewed and approved the change — **PENDING: risk:high + autonomy:conservative → this gate STOPS for the human (you)**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] an OPTED-IN milestone with placeholder contracts CANNOT be confirmed — `milestone-confirm` prints `add: error: milestone_contracts_unfilled …` and `confirmed` stays false (seen live: this very flow-enforcement milestone refused new-task until contracts were filled, then confirmed)
- [x] a milestone created WITHOUT --await-confirm confirms normally despite a placeholder — the census walk (test_min_pillar) + test_no_key_milestone_not_gated stay green (the gate is genuinely skipped)
- [x] "confirmed:true" now carries meaning — after a successful confirm, the MILESTONE.md `## Shared / risky contracts` provably had ≥1 real bullet (no `<…>`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_section_unfilled` is referenced in `cmd_milestone_confirm` (the `if "confirmed" in m:` block) AND unit-tested directly (test_section_unfilled_predicate); the gate path is exercised by the 3 opted-in tests
- [x] DEAD-CODE (code) — no orphaned symbol; `_section_unfilled` has both a caller and a direct test; no v1 stragglers (the gate is the only new call site)
- [x] SEMANTIC (prose / non-code) — re-read the §3 v2 contract + the engine_pin changelog: gate is OPTED-IN only, predicate is grandfather-on-absent; the inline comment matches (no "all milestones" stale wording)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

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
