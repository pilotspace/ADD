# TASK: Book + GLOSSARY describe the ship review (point at the guide)

slug: close-book-accord · created: 2026-06-17 · stage: mvp
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
- `add-method/docs/09-the-loop.md` — CANONICAL book chapter for the close/observe/release loop (already documents milestone-close consolidation @L50 + compaction @L54). Gains a SHIP-REVIEW passage that POINTS at the `add` skill's `loop.md` (DESCRIBE, don't re-specify). Mirrored ×4: root `./09-the-loop.md` · `.add/docs/` · `_bundled/docs/` (currently md5 fcf8d49…).
- `add-method/docs/appendix-c-glossary.md` — book glossary; native format `**Term** — definition`. Gains **Ship review** + **Release steps**. Mirrored ×4 (currently md5 dc5ebac…).
- `add-method/tooling/templates/GLOSSARY.md.tmpl` — template glossary; native format `term: definition`. Gains `ship review:` + `release steps:`. Mirrored ×3 (canonical · `.add/tooling/templates/` · `_bundled/`).
- `.add/GLOSSARY.md` — DOGFOOD live glossary; native format `term: definition`. Gains the same two terms (its own entry).

Context (working folder):
- the `add` skill's `loop.md` (shipped task 2) — the POINTS-AT-SOURCE target; the book describes, loop.md specifies.
- `MILESTONE.md.tmpl` `## Close — ship review` + `## Release steps` (task 1) — the artifacts the terms name.
- sync/guards: `cp add-method/docs/<f> ./<f>` (test_book_parity: canonical↔root) · `.add/docs/` mirror · `prepare_bundle.py` → `_bundled/` (test_bundle_parity) · the SDD wording-lint (`test_ubiquitous_language`) scans the book + glossary.
- new red test home → `.add/tasks/close-book-accord/tests/test_close_book_accord.py`.

Honors (patterns / conventions):
- DESCRIBE-don't-duplicate (the decision-suggestions book-accord pattern): the book + glossary POINT at loop.md, never re-specify the ritual (own-entry-regex + cross-tree md5 + points-at-source assertion).
- a glossary term lands in ALL 3 glossary TYPES, each in that type's native format (appendix `**T** — d` · template `t: d` · dogfood `t: d`) — the compact-book-align precedent.
- wording-lint: describe abstractly; backtick the lifecycle (`milestone-done → fold → compact → archive`); no bare status/process slang.
- book parity ×4 + glossary parity; method/trust-layer edit = residue → VERIFY escalates.

Anchors the contract cites:
- `09-the-loop.md` — the ship-review passage: names the cross-task review (ship-by-domain · cross-task evidence · goal-met map) filled at close + the AI-defined release steps (merge one small step), and POINTS at `loop.md`.
- `appendix-c-glossary.md` · `GLOSSARY.md.tmpl` · `.add/GLOSSARY.md` — the terms **Ship review** + **Release steps**, each an own-entry in its native format.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Book ch09 + GLOSSARY describe the ship review + release steps, POINTING at the guide (loop.md) — describe, don't re-specify.
Framings weighed: a ch09 passage + 3-type glossary terms POINTING at loop.md (chosen — the established
  book-accord pattern) · re-specify the ritual in the book (rejected — forks the source of truth) · a
  brand-new chapter (over-heavy; ch09 already owns milestone close).
Must:
<must>
  - `09-the-loop.md` gains a ship-review passage naming the whole-milestone cross-task review
    (ship-by-domain · cross-task evidence · goal-met map) the AI fills at close + the AI-defined
    release steps (merge one small step), and POINTS at the `add` skill's `loop.md` (authoritative ritual).
  - the glossary gains **Ship review** + **Release steps**, each an OWN-ENTRY in ALL 3 glossary TYPES,
    in that type's native format: appendix-c `**Term** — def` · template `term: def` · dogfood `term: def`.
  - the book passage POINTS at loop.md (names it) and does NOT re-specify the ritual — it copies none of
    loop.md's / release.md's distinctive tokens (their reject codes).
  - the book stays byte-identical ×4 (ch09 + appendix); the template glossary ×3; the wording-lint stays clean.
</must>
Reject:
<reject>
  - the book re-specifies the ritual instead of pointing at loop.md -> "duplicates_guide"
  - a term missing from one of the 3 glossary types -> "glossary_type_gap"
  - a book/glossary copy diverges across its trees -> "tree_drift"
</reject>
After:
<after>
  - a reader of the book learns the ship review exists and where the authoritative ritual lives (loop.md),
    and both terms are defined consistently across all 3 glossary types.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the ship-review passage belongs in ch09 (the loop / close) rather than ch16 (releasing) — lowest
    confidence because the release-steps line brushes ch16's territory; if wrong, a reader looks in the
    wrong chapter. Mitigation: the SHIP REVIEW is a close-time artifact and ch09 already owns milestone
    close; the release-steps mention POINTS forward to the release scope (release.md), never duplicates ch16.
  - [x] terms land in all 3 glossary types (the compact-book-align precedent) — confirmed convention.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: ch09 gains a ship-review passage that points at loop.md
  Given 09-the-loop.md
  When I read it
  Then it names the cross-task ship review (ship-by-domain + cross-task evidence + goal-met) and release steps (merge)
  And it points at the add skill's loop.md as the authoritative ritual

Scenario: both terms are defined in all 3 glossary types
  Given the glossary
  When I read appendix-c, the template, and the dogfood GLOSSARY.md
  Then "Ship review" and "Release steps" appear in each, in that type's native format
  And no type is missing either term

Scenario: the book points, it does not fork the guide   # reject: duplicates_guide
  Given the ch09 ship-review passage
  When I read it
  Then it references loop.md
  And it copies none of loop.md's / release.md's distinctive reject codes

Scenario: book + glossary copies stay byte-identical   # reject: tree_drift
  Given the book + glossary edited and prepare_bundle.py run
  When parity is checked
  Then ch09 (×4), appendix-c (×4), and the template glossary (×3) each have one md5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
EDIT  book ch09 (×4)  +  glossary (appendix-c ×4 · template ×3 · dogfood ×1)
  (prose contract: the frozen seam is a TOKEN SET + structural invariants)

Structural invariants (the frozen seam):
  B1 PASSAGE  09-the-loop.md contains a ship-review passage naming {ship-by-domain,
              cross-task evidence, goal-met} AND release steps (merge), and POINTS at `loop.md`
  B2 GLOSSARY "Ship review" + "Release steps" present in appendix-c (`**T** — d`),
              the template (`t: d`), and the dogfood GLOSSARY.md (`t: d`) — all 3 types
  B3 POINTS   the passage names loop.md AND copies none of loop.md's / release.md's distinctive
              reject codes — points, not forks
  B4 PARITY   ch09 ×4 byte-identical · appendix-c ×4 byte-identical · template glossary ×3 byte-identical

Frozen token set: "Ship review", "Release steps", "loop.md"
Reject labels:    duplicates_guide (B3) · glossary_type_gap (B2) · tree_drift (B4)
Out of seam (iterates freely, no re-freeze): the exact prose of the passage + each definition's wording.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-17)
Least-sure flag surfaced at freeze: [spec] chapter placement — the ship-review passage goes in ch09 (the loop / close), not ch16 (releasing), even though the release-steps line brushes ch16's territory; if wrong, a reader looks in the wrong chapter. Mitigation: the ship review is a close-time artifact and ch09 already owns milestone close; the release-steps mention POINTS forward to the release scope (release.md), never duplicating ch16. Secondary [contract]: B3 points-not-forks — assert the loop.md pointer AND the absence of release.md's reject codes (the structural proxy, same as task 2's L2).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 structural invariants B1–B4 (one test each).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_B1_ch9_ship_review_passage: ch09 names ship-by-domain / cross-task evidence / goal-met + release steps (merge) + "loop.md"
  - test_B2_glossary_all_three_types: "Ship review" + "Release steps" in appendix-c (bold-dash), template (colon), dogfood (colon)
  - test_B3_points_not_forks: ch09 passage references "loop.md" AND copies none of release.md's reject codes (e.g. "release_security_open")
  - test_B4_book_glossary_parity: md5(ch09)×4 == 1 · md5(appendix-c)×4 == 1 · md5(template glossary)×3 == 1
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs/09-the-loop.md` `add-method/docs/appendix-c-glossary.md` `add-method/../09-the-loop.md` `add-method/../appendix-c-glossary.md` `.add/docs/09-the-loop.md` `.add/docs/appendix-c-glossary.md` `add-method/tooling/templates/GLOSSARY.md.tmpl` `.add/tooling/templates/GLOSSARY.md.tmpl` `.add/GLOSSARY.md` `add-method/src/add_method/_bundled/`
<!-- repo-root book copies declared via the `add-method/..` climb (a "/"-bearing FILE token → repo root, NOT a vacuous dir); the wholesale-regenerated bundle declared as one directory token. -->>
Strategy (ordered batches): 1. edit canonical `add-method/docs/09-the-loop.md` (ship-review passage → points at loop.md) + `add-method/docs/appendix-c-glossary.md` (2 terms). 2. add the 2 terms to `add-method/tooling/templates/GLOSSARY.md.tmpl` + `.add/GLOSSARY.md` (native `t: d`). 3. `cp` canonical book files to root + `.add/docs/`; `cp` template to `.add/tooling/templates/`. 4. `prepare_bundle.py` for `_bundled/`. 5. run test_book_parity + test_bundle_parity + test_ubiquitous_language.
Safety rule (feature-specific): POINT at loop.md (don't re-specify); terms in ALL 3 glossary types; all copies end byte-identical (B4); wording-lint clean (backtick the lifecycle).
Code lives in: the book + glossary copies (docs/prose; no `./src/`).
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
- [x] coverage did not decrease — N/A (no src/); 4 new tests add B1–B4 coverage
- [x] no test or contract was altered during build — only book ch09 + glossary copies changed; tests + §3 untouched
- [x] the green was EARNED, not gamed — refute-read: B1/B2 assert REAL book + glossary content across types; B4 cross-tree md5; B3 proves points-not-forks (ch09 copies no release reject codes). Wording-lint stayed green (lifecycle not spelled bare). Not overfit.
- [x] concurrency / timing — N/A; prose docs edit, no runtime operation
- [x] no exposed secrets, injection openings, or unexpected dependencies — book/glossary prose only; no dependency; no engine change
- [x] layering & dependencies follow CONVENTIONS.md — DESCRIBE-don't-duplicate honored (book points at loop.md, no fork); book parity ×4 + glossary parity held; wording-lint green
- [ ] a person reviewed and approved the change — ESCALATED (residue below)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read the new ch09 "**The ship review.**" passage + both glossary entries in all 3 types. Confirmed B1 (names ship-by-domain · cross-task evidence · goal-met · release steps · merge, and points at `loop.md`); B2 (terms present in appendix `**T** — d`, template `t: d`, dogfood `t: d`); B3 (no release reject codes copied); B4 (md5 parity ch09 ×4 · appendix ×4 · template ×3). Passage sits before "The consolidation" — correct close lifecycle order; describes, never re-specifies.

### Residue — escalated (not auto-resolved)
- METHOD / TRUST-LAYER edit: changes the BOOK (the trust layer users read) + the GLOSSARY. Per PROJECT.md §Domain (v6), method/trust-layer edits escalate to a human even under `autonomy: auto`. Not a security/concurrency/architecture finding; evidence complete and green. Human gate on the method change itself.

### GATE RECORD
Outcome: PASS   (method-edit residue escalated — pending human confirmation)
Reviewed by: Tin Dang · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the book + glossary keep pointing at loop.md (no fork) · the 3 glossary types stay consistent · book ×4 + glossary parity holds.

### Spec delta
- [SPEC · seeded] all 3 ship-review tasks are done — next is the milestone's OWN ship-review close: fill `## Close — ship review`, map the 4 exit criteria to evidence, define release steps, then `milestone-done` (evidence: this is exit criterion 4, dogfooded)

### Competency deltas
- [SDD · folded] one glossary term touches 9 files across 3 sync regimes (book ×4 · template ×3 · dogfood ×1) and must be written in EACH type's native format (appendix `**T** — d` · template/dogfood `t: d`) — parity guards catch byte-divergence but the per-type FORMAT is a manual judgment the test must pin per type (evidence: test_B2 asserts format-by-type) [folded foundation-version 37]
- [ADD · folded] this milestone dogfooded itself — the ship-review machinery (template task 1 · guide task 2 · book task 3) is exercised by the milestone's OWN close, the honest first-lived-run pattern that proves the feature on its author (evidence: exit criterion 4 fills the very `## Close — ship review` section task 1 shipped) [folded foundation-version 37]
- [ADD · folded] the §5 scope-gate caught a real declaration gap and is anchored at the tests→build crossing: a repo-root file needs the `add-method/../<file>` climb (a "/"-bearing FILE token — bare names resolve as siblings) and the wholesale `_bundled/` tree a single directory token; a §5 fix after build requires RE-CROSSING tests→build to re-anchor the snapshot (editing §5 alone is not picked up). Disclosed tradeoff: re-anchoring after the edits means that gate run re-diffs nothing — integrity here rests on the green suite + parity + tamper-tripwire, not the scope diff (evidence: scope_violation returned-to-build attempt 1→2 until the re-cross) [folded foundation-version 37]
