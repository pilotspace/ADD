# TASK: Flag-first freeze guard (fail-closed unflagged_freeze)

slug: unflagged-freeze · created: 2026-06-10 · stage: mvp · risk: high
autonomy: conservative   <!-- method-defining fail-closed guard; Verify STOPS for the human (no auto-PASS). -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a fail-closed `unflagged_freeze` guard — a FROZEN §3 may not cross into build without a
well-formed lowest-confidence flag (the `Least-sure flag surfaced at freeze:` unit), making the
"surface the flag" convention machine-enforced instead of prose-only.
Framings weighed: mechanize at advance + audit + CI (chosen) · advance-refuse only (no finished-record teeth) · a new freeze verb (ADD has none, larger surface)
Must:
<must>
  - crossing tests->build via `advance` with a FROZEN §3 requires a WELL-FORMED flag, else REFUSE
  - well-formed := the label `Least-sure flag surfaced at freeze:` + >=1 `[part]` tag (part in
    spec/scenario/contract/test, slash-joinable like `[spec/contract]`) + substantive content
  - a bare `none` is refused unless it takes the honest escape `none material — biggest risk: X`
  - on a passed crossing, stamp `flag_verified: true` on the task (the verified-marker discriminator)
  - `audit` flags `unflagged_freeze` ONLY on `flag_verified` records whose flag is absent/malformed
    (open/new freezes only — the unmarked predecessors are never retro-redded)
  - the refuse is a pure no-op on state.json; below the build boundary the flag is never checked
  - read-only for `audit`; CI consumes `audit` (the third fire-point)
</must>
Reject:
<reject>
  - frozen §3 crosses into build with no well-formed flag (absent · malformed · bare-none) -> "unflagged_freeze"
</reject>
After:
<after>
  - no frozen bundle reaches build without its lowest-confidence flag surfaced; the audit arm keeps
    every flag_verified record honest, while 45 pre-existing frozen tasks stay clean (verified-marker)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the refuse fires at advance->build, not on a freeze verb (ADD has no freeze command) —
    lowest confidence because the flag becomes load-bearing only at the build crossing; if wrong: a
    freeze that never advances would be unguarded (audit's verified-marker arm is the backstop)
  - [x] grammar accepts slash forms like `[spec/contract]` — confirmed against the 3 lived flags (deltas-report uses it)
  - [x] audit scope excludes the archive and skips open fronts — confirmed (live state["tasks"], done/observe-or-gated)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a frozen §3 with no flag refuses the build crossing
  Given a task at tests whose §3 is FROZEN and carries no flag line
  When I run `add.py advance` into build
  Then it REFUSES with "unflagged_freeze"
  And state.json is unchanged (phase stays tests, no flag_verified)

Scenario: a bare 'none' flag refuses
  Given a frozen §3 whose flag reads only "Least-sure flag surfaced at freeze: none"
  When I advance into build
  Then it REFUSES with "unflagged_freeze"

Scenario: a flag with no [part] tag refuses
  Given a frozen §3 flag with prose but no [part] tag
  When I advance into build
  Then it REFUSES with "unflagged_freeze"

Scenario: a well-formed flag passes and stamps the marker
  Given a frozen §3 with "⚠ [contract] … — …"
  When I advance into build
  Then it succeeds (phase=build)
  And flag_verified: true is stamped on the task

Scenario: the honest-none escape passes
  Given a flag "Least-sure flag surfaced at freeze: none material — biggest risk: X"
  When I advance into build
  Then it succeeds

Scenario: a slash-form tag passes
  Given a flag carrying "[spec/contract]"
  When I advance into build
  Then it succeeds (the grammar must not over-red the lived flags)

Scenario: below the build boundary the flag is never checked
  Given a frozen §3 with no flag, advancing specify->scenarios
  When I advance
  Then it succeeds (the guard fires ONLY at the build crossing)

Scenario: audit flags a marked record whose flag was deleted
  Given a flag_verified done record whose §3 flag was removed post-freeze
  When I run `add.py audit`
  Then it reports "unflagged_freeze" (exit 1)

Scenario: audit is silent on an unmarked predecessor
  Given a frozen done record with no flag and no flag_verified marker
  When I run `add.py audit`
  Then it does NOT report "unflagged_freeze" (the 45 stay clean)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py advance   (extended — same command + a build-boundary flag guard)
  when the next phase is "build" AND §3 is FROZEN (_contract_frozen):
    require _flag_well_formed(§3)  else  _die("unflagged_freeze: …")   # no state write
    on pass: state["tasks"][slug]["flag_verified"] = True              # then the normal phase write
  the flag is NEVER checked below the build boundary; the refuse is a pure no-op on state.json.

_flag_well_formed(raw3) -> bool   (shared by advance + audit; PURE; strips HTML comments)
    label  : "Least-sure flag surfaced at freeze:"  present
    tag    : >=1  [spec|scenario|contract|test]  (slash-joinable: [spec/contract])
    content: substantive text beyond the tag(s)
    none   : bare 'none' refused unless 'none material — biggest risk: X'

add.py audit   (extended — sibling of unstamped_freeze, verified-marker discriminator)
  for each checked record:  if t.get("flag_verified") and not _flag_well_formed(s3):
      finding "unflagged_freeze"  (exit 1)        # marked records only — predecessors skipped
  READ-ONLY. CI consumes audit (audit-ci) — the third fire-point.

Reject code: unflagged_freeze   (absent · malformed · bare-none, at the frozen build crossing)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-10
Least-sure flag surfaced at freeze: ⚠ [contract] the refuse fires at advance→build, not on a freeze verb (ADD has no freeze command) — if it misfired, a freeze that never advances would be unguarded (audit's verified-marker arm is the backstop); ⚠ [spec/contract] the grammar must accept slash forms like [spec/contract] or it over-reds the 3 lived flags. Human approved both, plus the two build-time refinements (verified-marker discriminator · evidence-corrected grammar), in view.
<!-- The freeze IS the one approval. Lead it with the bundle's lowest-confidence flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject + both audit arms (advance refuse/pass · audit flag/silent · prose-accord)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_refuses_absent_flag / _bare_none / _untagged: advance into build REFUSES "unflagged_freeze", state no-op
  - test_allows_wellformed / _multiline / _slash_tag / _none_escape: advance succeeds + flag_verified: true
  - test_below_build_boundary_unchecked: specify->scenarios with no flag succeeds (build-boundary only)
  - test_flags_marked_missing_flag / _marked_malformed_flag: audit reports "unflagged_freeze" (exit 1)
  - test_silent_unmarked_predecessor / _marked_wellformed: audit silent (predecessors + valid flags clean)
  - test_contract_guide_states_guard: 3-contract.md states the enforcement, synced ×3 (prose ≡ enforcement)
</test_plan>

Tests live in: `add-method/tooling/test_unflagged_freeze.py` · MUST run red (missing implementation) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the refuse path NEVER writes state (design-for-failure: a refused
crossing is a pure no-op); the marker is stamped only on a verified pass, in the same atomic save.
Code lives in: `add-method/tooling/add.py` (+ synced byte-identical to `.add/tooling/` and `_bundled/`)
Constraints: do NOT change any test or the frozen contract; stdlib only; reuse `_contract_frozen` + the audit seams.

Built: `_FLAG_*` regexes + `_flag_well_formed()` (next to `_contract_frozen`); `cmd_advance` build-boundary
guard + `flag_verified` stamp; `_audit_findings` verified-marker sibling. 13 tests green; full suite 704 green;
3-tree engine parity re-pinned (`engine_pin.py` -> cc890d6…); guide anchor synced ×3; GLOSSARY bridge added.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `Ran 704 … OK` (13 new incl. prose-accord)
- [x] coverage did not decrease — new suite is purely additive
- [x] no test or contract was altered during build — frozen §3 honored
- [x] concurrency / timing of the risky operation is safe — single-process CLI; refuse is no-op before save
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — pure helper + existing advance/audit seams
- [x] a person reviewed and approved the change

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_flag_well_formed` referenced by `cmd_advance` (build crossing) + `_audit_findings`;
      `flag_verified` written by advance, read by audit; live dogfood: this task's tests->build crossing
      set `flag_verified: true` on a real record
- [x] DEAD-CODE (code) — no orphaned symbol; every `_FLAG_*` constant is used by `_flag_well_formed`
- [ ] SEMANTIC (prose / non-code) — n/a (code task)

### GATE RECORD
Outcome: PASS — human-confirmed at verify gate
Reviewed by: Tin (human, at verify gate) · date: 2026-06-10

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of `unflagged_freeze` refusals at advance · count of `flag_verified`
records · any `unflagged_freeze` audit finding (should be zero unless a flag is tampered post-freeze)
Spec delta for the next loop: whether the label↔term drift (`Least-sure flag` vs canonical `lowest-confidence`)
warrants a separate naming-migration task across template + guides + lived task labels.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a guard gains teeth without retro-redding predecessors via a verified-marker — stamp on the guarded crossing, enforce only on marked records (evidence: live audit 48→49 clean; the 45 pre-existing frozen tasks stayed silent)
- [SDD · folded] a lived artifact label can drift from its canonical glossary term — §3 `Least-sure flag surfaced at freeze:` vs `lowest-confidence flag`; bridged, not migrated, this loop (evidence: needed a MACHINE_SPAN + GLOSSARY bridge + guide reword to keep the ubiquitous-language & wording linters green)
