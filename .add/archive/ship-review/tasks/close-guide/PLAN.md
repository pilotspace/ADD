# TASK: Close-flow guide: cross-task ship review + AI-defined release steps

slug: close-guide · created: 2026-06-17 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/skill/add/loop.md` — CANONICAL milestone-close guide; its step 6 "Close" (≈L40-44) is where the ship-review ritual belongs. Today it: check exit-criteria boxes → `milestone-done` → consolidate + archive. Does NOT yet mention ship-review / per-domain / cross-task evidence / `release.md` (grep clean).
- `.claude/skills/add/loop.md` + `add-method/src/add_method/_bundled/skill/add/loop.md` — DOGFOOD + BUNDLE mirrors; byte-identical, synced by `test_tree_parity` (canonical↔dogfood) + `test_bundle_parity` (canonical↔bundle).
- `add-method/skill/add/release.md` — the 5th scope level; the AI-defined `## Release steps` FEED it (the close hands off here; loop.md must POINT at release.md, not re-specify it).
- `add-method/tooling/templates/MILESTONE.md.tmpl` — the `## Close — ship review` + `## Release steps` scaffolds shipped by task 1; this guide tells the AI HOW to fill them.

Context (working folder):
- `add-method/skill/add/SKILL.md` — the router; already cues loop.md (≈L113-115) + release.md (≈L124). Extending loop.md needs NO new router entry (vs a new close.md, which would).
- `add-method/scripts/prepare_bundle.py` — re-run after editing the skill to refresh `_bundled/`.
- new red test home → `.add/tasks/close-guide/tests/test_close_guide.py` (cross-tree reference test).
- `report-template.md` — loop.md step 6 already cues it for the close report; the ship-review evidence is what that report SHOWS.

Honors (patterns / conventions):
- skill is synced ×3 (canonical · dogfood · bundle); edits propagate to all three, parity guarded (`test_tree_parity` + `test_bundle_parity`).
- progressive disclosure / lean skill — prefer EXTENDING loop.md (it already owns "Close") over a new file + router entry.
- DESCRIBE-don't-duplicate: loop.md POINTS at release.md for the release scope, never re-specifies it (the decision-suggestions docs-accord pattern).
- Method/trust-layer edit = residue → VERIFY escalates to the human even under autonomy:auto.

Anchors the contract cites:
- `loop.md` step 6 "Close" — gains the ship-review ritual: AI FILLS the MILESTONE `## Close — ship review` (Ship-by-domain + Cross-task evidence + Goal-met map) as the evidence read BEFORE checking the exit-criteria boxes; then AI DEFINES `## Release steps` (merge = one step) that FEED `release.md`.
- the cross-tree reference seam: loop.md (×3 trees) cites the ship-review + points at `release.md`; the 3 copies stay byte-identical.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Extend `loop.md` step 6 "Close" with the cross-task ship-review ritual + the AI-defined release-steps handoff to `release.md`.
Framings weighed: EXTEND loop.md step 6 (chosen — loop.md already owns "Close" and is already cued;
  no new file, no new SKILL.md router entry) · a new `close.md` guide (more discoverable but adds a
  skill file + a router entry + a parity surface) · put the ritual in release.md (wrong scope —
  release bundles ≥1 milestone; the ship-review is per-milestone, at close).
Must:
<must>
  - loop.md's Close step instructs the AI to FILL the MILESTONE `## Close — ship review` section —
    Ship-by-domain (tooling·skill·book) · Cross-task evidence (one row/task: gate·tests·residue) ·
    Goal-met map (each Exit criterion ↔ its evidence) — as the evidence read BEFORE checking the
    exit-criteria boxes (it is evidence, NOT a new gate).
  - loop.md's Close step instructs the AI to DEFINE `## Release steps` (merge as one small step) and
    states they FEED `release.md` — a POINTER to the 5th-scope flow, never a re-spec of it.
  - the ritual sits in the correct lifecycle order: fill ship-review → human reads it + checks
    exit-criteria boxes → `milestone-done` → fold → compact → archive → (release).
  - loop.md stays byte-identical across the 3 skill trees (canonical · dogfood · bundle).
  - no engine command added; the ritual is guide prose the AI follows (tool-agnostic).
</must>
Reject:
<reject>
  - loop.md re-specifies release.md's flow instead of pointing at it -> "duplicates_release_scope"
  - the ship-review framed as a NEW human approval (a second gate) -> "new_gate_introduced"
  - a skill tree copy diverges -> "tree_drift"
</reject>
After:
<after>
  - a reader of loop.md at milestone close knows to fill the MILESTONE Close section, define the
    release steps, and where the release handoff goes — with no second approval introduced.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ EXTENDING loop.md (vs a new close.md) is the right home — lowest confidence because loop.md is
    framed as "the dynamic loop (next tasks)" and the ship-review is a close-time artifact, so it
    could read as two concerns in one file. If wrong: a future reader misses the ritual. Mitigation:
    place it squarely inside the EXISTING step-6 "Close" (already the close-home) and keep the release
    handoff a one-line pointer, not a fork.
  - [x] release-steps FEED release.md, never replace it — confirmed (milestone shared decision).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: loop.md Close step cues the ship-review fill
  Given loop.md
  When I read step 6 "Close"
  Then it instructs filling the MILESTONE `## Close — ship review` (ship-by-domain + cross-task evidence + goal-met map)
  And it frames that as the evidence read before checking the exit-criteria boxes

Scenario: loop.md defines release steps that feed release.md
  Given loop.md Close step
  When I read it
  Then it instructs defining `## Release steps` (merge as one step) and points at release.md as the feed
  And it does NOT re-specify the release flow (no release.md reject codes copied in)

Scenario: the ship-review is evidence, not a new gate   # reject: new_gate_introduced
  Given loop.md Close step
  When I read the ritual
  Then the only human affirmation named is checking the exit-criteria boxes (the existing gate)
  And no second "approve merge/ship" gate is introduced

Scenario: loop.md stays byte-identical across the 3 skill trees   # reject: tree_drift
  Given loop.md edited and prepare_bundle.py run
  When parity is checked
  Then md5(canonical) == md5(dogfood) == md5(bundle) for loop.md
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
EDIT  add-method/skill/add/loop.md (×3 trees)  — extend step 6 "Close" with the ship-review ritual
  (prose contract: the frozen seam is a TOKEN SET + structural invariants)

Structural invariants (the frozen seam):
  L1 FILL    loop.md Close step instructs filling the MILESTONE `## Close — ship review`
             — names Ship-by-domain + Cross-task evidence + Goal-met map
  L2 FEED    loop.md Close step instructs defining `## Release steps` AND references `release.md`
             as the feed — a POINTER, not a re-spec (release.md's distinctive reject codes NOT copied in)
  L3 NO-GATE the ritual introduces NO new human approval — the exit-criteria affirmation stays the only gate
  L4 PARITY  md5(canonical) == md5(dogfood) == md5(bundle) for loop.md

Frozen token set: "Close — ship review", "Release steps", "release.md"
Reject labels:    duplicates_release_scope (L2) · new_gate_introduced (L3) · tree_drift (L4)
Out of seam (iterates freely, no re-freeze): the exact wording/ordering of the ritual prose.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-17)
Least-sure flag surfaced at freeze: [contract] L2 (point, don't duplicate) — "loop.md doesn't re-specify release.md" is subjective and not fully testable; if wrong, the close guide forks the release truth. Mitigation in §4: test_L2 asserts loop.md REFERENCES release.md AND does NOT copy release.md's distinctive reject codes (e.g. `release_security_open`) — a structural proxy for points-not-forks. Secondary [spec]: the extend-loop.md-vs-new-close.md home choice — mitigated by placing the ritual inside the existing step-6 "Close" + a one-line release handoff.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 structural invariants L1–L4 (one test each).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_L1_loop_cues_ship_review_fill: loop.md contains "Close — ship review" + names ship-by-domain / cross-task evidence / goal-met map
  - test_L2_loop_feeds_release: loop.md references "release.md" AND does NOT copy release.md's own reject codes (e.g. "release_security_open") — a structural proxy for points-not-forks
  - test_L3_no_new_gate: loop.md Close ritual introduces no second approval token (no "approve merge"/"approve ship"); the exit-criteria affirmation remains the sole gate
  - test_L4_loop_tree_parity: md5(canonical)==md5(dogfood)==md5(bundle) for loop.md
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/loop.md` `.claude/skills/add/loop.md` `add-method/src/add_method/_bundled/skill/add/loop.md`
Strategy (ordered batches): 1. edit canonical `add-method/skill/add/loop.md` step 6 "Close" (add the ship-review fill + release-steps→release.md handoff). 2. mirror byte-for-byte to `.claude/skills/add/loop.md`. 3. run `prepare_bundle.py` to refresh `_bundled/`. 4. run test_tree_parity + test_bundle_parity.
Safety rule (feature-specific): POINT at release.md (don't duplicate its flow); introduce NO new gate; the 3 copies end byte-identical (L4).
Code lives in: the three `loop.md` copies (skill prose; no `./src/`).
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

- [x] all tests pass — task suite 4/4 green; full engine suite 1189 OK
- [x] coverage did not decrease — N/A (no src/); 4 new tests add L1–L4 coverage
- [x] no test or contract was altered during build — only the 3 loop.md copies changed; tests + §3 untouched
- [x] the green was EARNED, not gamed — refute-read: L1/L2/L4 assert REAL loop.md content + cross-tree md5; L2 proves points-not-forks structurally (references release.md AND no release reject codes copied). The wording-lint caught a real bare-"fold" slang in my first draft (full-suite red) — fixed to the code-span form, re-verified. Not overfit.
- [x] concurrency / timing — N/A; prose guide edit, no runtime operation
- [x] no exposed secrets, injection openings, or unexpected dependencies — skill prose only; no dependency; no engine command added
- [x] layering & dependencies follow CONVENTIONS.md — DESCRIBE-don't-duplicate honored (loop.md points at release.md, no fork); 3-tree parity held (md5 8f6fc75…); wording-lint green
- [ ] a person reviewed and approved the change — ESCALATED (residue below)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read the edited loop.md step 6 "Close" end-to-end. Confirmed: L1 the ship-review fill (Ship by domain · Cross-task evidence · Goal met? map) framed as evidence before the exit-criteria boxes; L2 `## Release steps` defined + `release.md` pointed-to (no re-spec, no reject codes); L3 the only affirmation is the exit-criteria boxes ("the same gate as ever") — no second approval; L4 byte-parity across 3 trees. Lifecycle `milestone-done → fold → compact → archive` rendered as a code span (lint-clean). No dead/orphaned content; merge is one small step among tool-agnostic release hints.

### Residue — escalated (not auto-resolved)
- METHOD / TRUST-LAYER edit: changes `loop.md`, the milestone-close guide every agent follows. Per PROJECT.md §Domain (v6), method/trust-layer edits escalate to a human even under `autonomy: auto`. Not a security/concurrency/architecture finding; evidence complete and green. Human gate on the method change itself.

### GATE RECORD
Outcome: PASS   (method-edit residue escalated + confirmed by the human)
Reviewed by: Tin Dang · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): loop.md keeps pointing at release.md (no fork) · the 3 skill copies stay md5-equal · future close runs produce a filled ship-review before the boxes are checked.

### Spec delta
- [SPEC · seeded] task 3 (close-book-accord) DESCRIBES this ritual in the book + GLOSSARY, pointing at loop.md — not re-specifying (evidence: this task ships the guide; the book accord is task 3's scope)

### Competency deltas
- [SDD · folded] the wording-lint scans skill guides for bare status/process slang AND exempts code spans — the lifecycle `milestone-done → fold → compact → archive` must be backticked (as release.md does), not bare prose; a bare "fold" turned the full suite red (evidence: test_slang_absent_extended_surface term='fold' until the code-span reword) [folded foundation-version 37]
- [ADD · folded] "point, don't duplicate" between two guides is testable as a structural proxy — assert the pointer (the other file is named) AND the absence of the other file's distinctive tokens (its reject codes) — rather than trying to prove non-duplication directly (evidence: test_L2 design) [folded foundation-version 37]
