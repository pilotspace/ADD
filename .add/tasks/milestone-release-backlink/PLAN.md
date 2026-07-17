# TASK: MILESTONE.md header carries an engine-stamped release: backlink

slug: milestone-release-backlink · created: 2026-06-30 · stage: mvp
milestone: artifact-graph
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
  - `add-method/tooling/add.py:cmd_release` (l.6286; RECORD block l.6324-6342, atomic `_atomic_write_many` at l.6339 with `bundle` = list of `{slug}`) — STAMP each bundled milestone's MILESTONE.md `release:` line to args.version, in the same atomic batch.
  - `add-method/tooling/add.py:_set_milestone_line` (just shipped, l.~160) — the sibling pattern; add a parallel `_set_release_line(text, value)` keying on `^release:`.
  - `add-method/tooling/templates/MILESTONE.md.tmpl` (l.5 `stage: {{stage}} · status: active · created: {{date}}`) — ADD a `release: pending` header line. (×3 template trees)
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — re-pinned. (×3 add.py copies)
  - `add-method/tooling/test_milestone_release_backlink.py` — NEW test, mirrors test_milestone_backlink.
Context (working folder):
  - RELEASES.md is the attribution ledger (`_released_milestones` reads its `milestones:` rows); the `release:` backlink mirrors the cut INTO each milestone file. The reverse link (release→milestones) already exists in RELEASES.md → bidirectional.
  - cmd_release is record-only + validate-before-write + atomic + NO save_state — the stamp must JOIN that atomicity, not break it.
Honors (patterns / conventions):
  - validate-before-write + all-or-nothing `_atomic_write_many` (the stamp writes ride the SAME batch as CHANGELOG+RELEASES, so a failed write rolls back everything); degrade-safe; the engine RECORDS, never tags/publishes.
  - `release: pending` is a literal in the template (no `{{token}}`) — the initial value; cmd_release rewrites it to the version. Mirrors the milestone backlink's engine-maintained discipline.
Anchors the contract cites: cmd_release RECORD/atomic batch (add.py:6339) · `_set_release_line` helper · MILESTONE.md.tmpl `release: pending` line · engine_pin.ENGINE_MD5
Issues/Risks (→ feed §1):
  - **atomicity** — the MILESTONE.md stamps MUST be added to the existing `_atomic_write_many([CHANGELOG, RELEASES])` call (one commit), NOT written separately after; a separate write breaks cmd_release's all-or-nothing rollback contract.
  - **grandfathered milestones** — ~50 archived + existing milestones have no `release:` line; cmd_release's `_set_release_line` must INSERT it (mirror set-milestone), and the bundle only contains closed-unreleased ones anyway.
  - **stage-line collision** — `release:` must be its own line, not appended to the `stage: … created:` line (a regex on `^release:` is cleaner + won't disturb the status/created reads).
  - **engine re-pin** — touching add.py drifts ENGINE_MD5; re-pin ×3 in lockstep.
Related intent: PROJECT.md "RELEASE is the 5th scope level (engine-records-human-ships)" · GLOSSARY "release"/"milestone" · originating request — Tin's "enhance metadata block ... cross artifact" + "[you should fill more]"; artifact-graph M2 task 2 (milestone↔release backlink, depends on task-milestone-backlink's header pattern).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: MILESTONE.md header carries an engine-stamped `release:` backlink (milestone→release)
Framings weighed: engine-stamped header field — the template seeds `release: pending`, cmd_release rewrites it to the version at the cut (chosen, mirrors task-milestone-backlink) · hand-filled (rejected — drifts) · a separate release→milestone index file (rejected — RELEASES.md already is that; minimal)
Must:
<must>
  - M1: `MILESTONE.md.tmpl` gains a literal `release: pending` header line (after the `stage: … created:` line) — every newly-created milestone carries it. (×3 template trees, byte-identical)
  - M2: `add.py release <version>` STAMPS each bundled (closed-and-unreleased) milestone's MILESTONE.md `release:` line to `<version>` — rewriting it (or inserting it, for a grandfathered file) via a `_set_release_line` helper.
  - M3: the stamp writes JOIN cmd_release's existing all-or-nothing `_atomic_write_many` batch (with CHANGELOG + RELEASES) — a failed write rolls back EVERYTHING; the engine still NEVER tags/publishes/saves state.
  - M4: invariants — every `add.py` copy byte-identical == the RE-PINNED `engine_pin.ENGINE_MD5`; MILESTONE.md.tmpl ×3 byte-identical; the phases lean pool UNTOUCHED.
</must>
Reject:
<reject>
  - release stamps a milestone NOT in the bundle (only closed-and-unreleased get stamped) -> "stamp_outside_bundle"
  - the stamp is written OUTSIDE the atomic batch (breaks rollback) -> "stamp_breaks_atomicity"
  - a grandfathered MILESTONE.md without a `release:` line makes release crash instead of inserting -> "release_insert_crash"
  - the build edits add.py without re-pinning ENGINE_MD5 across all 3 copies -> "engine_pin_drift"
</reject>
After:
<after>
  - A new milestone reads `release: pending`; after `add.py release X`, each bundled milestone's MILESTONE.md reads `release: X`; the stamp is part of the atomic cut (rolls back on failure); add.py re-pinned ×3; template ×3 byte-identical; full suite green; phases pool unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Joining the stamp writes into `_atomic_write_many` — lowest confidence: that I build ALL the MILESTONE.md new-contents in memory BEFORE the single batch call (so the rollback contract holds), rather than writing them after. If wrong: a partial cut (ledger updated, stamps missing, or vice-versa) on a write failure. Mitigate: extend the existing `[(changelog,..),(releases,..)]` list with the stamp tuples, one `_atomic_write_many`.
  - [ ] `release: pending` as a template literal (no `{{token}}`) needs no render change — confirmed: cmd_new_milestone's render passes title/goal/stage/date only; a literal line is simplest.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a new milestone carries release: pending   # M1
  Given a fresh project
  When I run `add.py new-milestone v1`
  Then v1's MILESTONE.md header has `release: pending`

Scenario: release stamps each bundled milestone   # M2
  Given a closed-and-unreleased milestone v1 (its MILESTONE.md reads `release: pending`)
  When I run `add.py release 1.0.0`
  Then v1's MILESTONE.md header reads `release: 1.0.0`
  And RELEASES.md attributes v1 to 1.0.0 (the reverse link)

Scenario: a grandfathered milestone is inserted, not crashed   # M3, R:release_insert_crash
  Given a closed-and-unreleased milestone whose MILESTONE.md has NO `release:` line
  When I run `add.py release 1.0.0`
  Then the `release: 1.0.0` line is INSERTED into its header
  And the release completes without error

Scenario: a failed cut rolls back the stamp too   # M3, R:stamp_breaks_atomicity
  Given the stamp writes are part of the atomic batch
  When any write in the batch fails
  Then CHANGELOG, RELEASES, and every MILESTONE.md stamp are all rolled back together
  And nothing is half-recorded

Scenario: the engine stays pinned and templates match   # M4, R:engine_pin_drift
  Given the change is applied
  When I md5 every add.py copy and the 3 MILESTONE.md.tmpl copies
  Then each add.py equals the re-pinned engine_pin.ENGINE_MD5
  And the 3 template copies are byte-identical
  And the phases lean pool is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
MILESTONE.md release backlink — frozen shape @ v1   (engine-stamped milestone↔release link)

MILESTONE.md.tmpl header gains, after the `stage: … · created: …` line:
    release: pending
  (a literal — every new milestone starts pending; cmd_release rewrites it at the cut.)

add.py _set_release_line(text, value)  — mirror of _set_milestone_line:
    rewrite `^release:.*$` -> `release: <value>`; if absent, INSERT after the
    `stage: … created:` line; no anchor line -> return unchanged (degrade-safe).

add.py cmd_release (RECORD block, before the single _atomic_write_many):
    for each m in bundle:  read its MILESTONE.md, _set_release_line(text, version),
    and APPEND (path, new_text) to the SAME write batch as CHANGELOG + RELEASES.
  -> stamp + ledgers commit all-or-nothing; a failed write rolls back everything.
  Only `bundle` (closed-and-unreleased) milestones are stamped; loose tasks + state.json untouched.

Invariants: add.py ×3 byte-identical == re-pinned engine_pin.ENGINE_MD5; MILESTONE.md.tmpl
×3 byte-identical; phases lean pool unchanged.
```

Least-sure flag surfaced at freeze: [contract/test] the atomicity join — the stamp tuples MUST be built in memory and appended to the EXISTING `_atomic_write_many` call (not written after it), or cmd_release's all-or-nothing rollback breaks. Verified the call shape (l.6339 takes a list of (path, text)); cost if wrong: a partial cut on write failure → mitigated by one batch + a rollback scenario test.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_milestone_has_release_pending: new-milestone / assert header `release: pending`
  - test_release_stamps_bundled_milestone: closed milestone / release 1.0.0 / assert `release: 1.0.0` + RELEASES names it
  - test_grandfathered_milestone_inserted: strip the line / release / assert inserted, no crash
  - test_failed_cut_rolls_back_stamp_and_ledgers: mock _atomic_write_many to raise / release / assert line stays pending + no CHANGELOG
  - test_template_has_release_field_and_is_parity / test_engine_byte_identical_to_pin / test_phases_pool_untouched
</test_plan>

Tests live in: `add-method/tooling/test_milestone_release_backlink.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/tooling/templates/MILESTONE.md.tmpl` `.add/tooling/templates/MILESTONE.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl` `add-method/tooling/test_milestone_release_backlink.py`
Strategy (ordered batches): 1. MILESTONE.md.tmpl: add literal `release: pending` after the `stage:` line. 2. add.py: `_set_release_line(text, value)` helper (mirror _set_milestone_line, key `^release:`); in cmd_release RECORD block, build the stamp tuples for each bundled milestone and APPEND them to the existing `_atomic_write_many([changelog, releases])` list. 3. propagate add.py + template to twins; re-pin engine_pin (×2 — bundled has no engine_pin); prepare_bundle. 4. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
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

- [x] all tests pass — full suite 2536/0 (2529 + 7 new)
- [x] coverage did not decrease — new behavior fully guarded incl. the atomic-rollback path
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; only the NEW test_milestone_release_backlink.py was added (in §5 scope)
- [x] the green was EARNED, not gamed — refute-read below; no sibling regression this time
- [x] concurrency / timing — the stamp RIDES the existing atomic `_atomic_write_many` batch; rollback proven by the mock-raise test
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib re; reads/writes confined under the project root
- [x] layering & dependencies follow CONVENTIONS.md — `_set_release_line` mirrors `_set_milestone_line`; validate-before-write + all-or-nothing honored
- [ ] a person reviewed and approved the change — ENGINE/method-trust change → ESCALATED to Tin (human-gated, not auto-resolved)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A new milestone's MILESTONE.md reads `release: pending` — confirmed: new-milestone test green
- [x] `add.py release X` rewrites each bundled milestone's line to `release: X` (inserts for grandfathered) — confirmed: stamp + grandfathered tests green
- [x] a forced batch-write failure leaves the line `pending` and no CHANGELOG — confirmed: atomic-rollback test green (mock raises → line stays pending, no CHANGELOG)
- [x] every add.py copy == re-pinned engine_pin.ENGINE_MD5 (79f37673); MILESTONE.md.tmpl ×3 byte-identical; phases pool ≤ target — confirmed: parity/pin tests green
- [x] full suite green — confirmed: 2536/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — `_set_release_line` is called by cmd_release (stamp loop); the template literal is read by cmd_new_milestone's render; both paths test-exercised.
- [x] DEAD-CODE — no orphaned symbol; the helper has a live caller + tests; `_RELEASE_LINE_RE`/`_STAGE_LINE_RE` both used.
- [x] SEMANTIC — read the cmd_release RECORD block in full: the stamp tuples are built BEFORE the single `_atomic_write_many` and concatenated into its list (rollback contract intact); only `bundle` milestones stamped; no save_state added.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (a) Is the atomicity claim real or just asserted? REAL — the mock-raise test patches `_atomic_write_many` to throw and proves the milestone line stays `pending` AND no CHANGELOG is written; the stamp genuinely rides the same batch. (b) Are only bundled milestones stamped? Yes — the loop iterates `bundle` (closed-and-unreleased); a released/active milestone is never touched. (c) Grandfathered insert vs crash? The grandfathered test strips the line and proves insertion, exit-0. (d) Engine/parity? add.py ×3 == re-pinned pin; MILESTONE.md.tmpl ×3 identical; phases pool untouched. No overfit, no contract edit, no sibling weakened.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — writes confined to `root/milestones/<slug>/MILESTONE.md`; no secrets, no injection (stdlib re on a known header).
2. Concurrency: CLEAR — the stamp joins the existing all-or-nothing `_atomic_write_many`; no new partial-write window.
3. Architecture: CLEAR — `_set_release_line` mirrors `_set_milestone_line`; the engine still RECORDS only (no tag/publish/state write).
Verdict: PASS
Residue: none.
Binding: advisory — method/trust (engine change → human-gated; NOT mechanical)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (human-gated; engine/method-trust change; clean build, no residue) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose engine-stamped header field — the template seeds `release: pending`, cmd_release rewrites it to the version at the cut; rejected hand-filled (rejected — drifts) · a separate release→milestone index file (rejected — RELEASES.md already is that; minimal)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang (human-gated; engine/method-trust change; clean build, no residue))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
