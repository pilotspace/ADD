# TASK: reconcile the scope-level enumeration across ch10/ch16/appendix-c to one canonical ordered list

slug: scope-level-enum-reconcile · created: 2026-06-25 · stage: mvp
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
  - `add-method/docs/16-releasing.md:14` — "Releasing is the **fifth scope level** — after **the task, the milestone, the foundation/setup level, and stage graduation**." OUTLIER ordered base (splits task/milestone, drops intake). Deep-audit F9.
  - `add-method/docs/appendix-c-glossary.md:87` ("**Scope level**" entry) — lists "intake · milestone · setup/foundation · **task** · release" UNORDERED + stage-graduation only parenthetically. Disagrees with the numbered ladder.
  - `add-method/docs/10-setup-and-stages.md:87` — "its own scope level, **the fourth after setup, intake, and the milestone loop**." ALREADY CANONICAL (the anchor — unchanged).
  - `add-method/docs/appendix-c-glossary.md:79` ("Stage graduation": "the **4th** scope level after **setup · intake · milestone-loop**") + `:93` ("Release scope level": "the **fifth** scope level") — already canonical; unchanged.
Context (working folder):
  - Docs are a 3-tree pillar: canonical `add-method/docs/` → `_bundled/docs/` (via `scripts/prepare_bundle.py`) + `.add/docs/` (manual `cp`). A doc edit re-mirrors ×3. Engine untouched → NO ENGINE_MD5 re-pin.
  - "altitude" is BANNED slang (ubiquitous-language fence) — every edit says "scope level".
Honors (patterns / conventions):
  - The numbering the method SHIPS: stage-graduation = 4th (memory: stage-transition design), release = 5th (memory: release-altitude milestone). The canonical ordered base is therefore setup → intake → milestone-loop → stage-graduation → release, with TASK as the inner unit of the milestone loop (not a separately-numbered top level).
Anchors the contract cites: the canonical ordered list `setup · intake · milestone-loop · stage-graduation · release` · ch16:14 · appendix-c "Scope level".

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: reconcile the scope-level enumeration so all three docs cite ONE canonical ordered list — setup → intake → milestone-loop → stage-graduation → release (task = the inner unit of the milestone loop) — matching the shipped numbering (stage = 4th, release = 5th). A new doc-consistency guard pins it.
Framings weighed: canonical = setup·intake·milestone-loop·stage·release (chosen) · canonical = task·milestone·release granularity ladder · leave-as-prose
  - chosen: keep ch10's already-correct ordered base (setup·intake·milestone-loop, stage=4th) as the anchor; fix ch16:14 + appendix-c "Scope level" to match; release=5th. Matches the engine's shipped numbering and the two already-canonical appendix-c entries → minimal, non-arbitrary.
  - granularity-ladder (task<milestone<release): rejected as the PRIMARY numbering — it conflicts with the shipped "stage=4th/release=5th" and with ch10/appendix-c; the granularity sense is kept as a SECONDARY note (task is the milestone loop's inner unit).
  - leave-as-prose: rejected — F9 flagged the contradiction; without a guard it silently re-drifts.
Must:
<must>
  - ch16:14 enumerates the first four levels in canonical order: "after setup, intake, the milestone loop, and stage graduation" (release = fifth). The old "after the task, the milestone, the foundation/setup level" base is gone.
  - appendix-c "Scope level" entry presents the SAME ordered five: setup/foundation · intake · milestone loop (task = inner unit) · stage graduation · release — no separately-counted "task level".
  - ch10:87 + appendix-c "Stage graduation"/"Release scope level" stay byte-equivalent in meaning (already canonical); no "altitude" slang introduced.
  - A guard test asserts the canonical order in all three docs and fails on the old contradictory phrasing.
</must>
Reject:
<reject>
  - guard finding (test failure): `scope_level_enum_drift` — a doc states the scope levels out of canonical order or re-introduces a conflicting base.
</reject>
After:
<after>
  - The three docs cite one canonical ordered scope-level list; a future drift is caught by the guard. 3-tree doc parity holds.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The canonical numbering is stage=4th / release=5th (setup·intake·milestone-loop base), NOT the task<milestone<release granularity ladder. Lowest confidence because the glossary "Scope level" entry currently leads with the granularity sense; if the project actually wants the granularity ladder as the primary numbering, ch10 + two appendix-c entries would ALSO need changing (bigger edit). I chose the shipped-numbering reading (memory: stage-transition = 4th, release-altitude = 5th) because it's what the engine/flow already commit to and what 3 of the 5 enumerations already say. AUTO-MODE decision; documented at freeze.
  - [x] docs are a 3-tree pillar (canonical + _bundled + .add), engine untouched → no ENGINE_MD5 re-pin — confirmed.
  - [x] "altitude" is banned slang — every edit uses "scope level" — will hold.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: ch16 cites the canonical ordered base
  Given 16-releasing.md
  When the guard reads the "fifth scope level" sentence
  Then it lists setup, intake, milestone loop, stage graduation (in order) and NOT "after the task, the milestone"

Scenario: appendix-c "Scope level" cites the canonical ordered five
  Given appendix-c-glossary.md "Scope level" entry
  When the guard reads it
  Then setup precedes intake precedes milestone precedes stage precedes release, and no separate "task level" is counted

Scenario: the canonical anchor is intact
  Given 10-setup-and-stages.md
  When the guard reads it
  Then "the fourth after setup, intake, and the milestone loop" is present (unchanged anchor)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Canonical ordered scope levels (the ONE list all docs cite):
  1. setup / foundation   2. intake   3. milestone loop (task = inner unit)
  4. stage graduation     5. release

EDIT A — 16-releasing.md:14:
  - after the task, the milestone, the foundation/setup level, and stage graduation.
  + after setup, intake, the milestone loop, and stage graduation.

EDIT B — appendix-c-glossary.md "Scope level" entry (:87): replace the unordered
  "intake · milestone · setup/foundation · task · release" granularity list with the
  canonical ORDERED five (setup/foundation · intake · milestone loop [task = inner unit] ·
  stage graduation · release), folding the stage-graduation parenthetical INTO the list as #4.

UNCHANGED: 10-setup-and-stages.md:87 (anchor) · appendix-c "Stage graduation" (4th) ·
  appendix-c "Release scope level" (fifth). No "altitude" slang.

NEW guard test_scope_level_enum.py: for each of the 3 docs, assert the canonical
  ordered tokens (setup<intake<milestone<stage<release) by index; assert the old
  "after the task, the milestone" base is ABSENT from ch16. -> scope_level_enum_drift

Invariants: 3-tree doc parity (canonical + _bundled + .add) · engine untouched (no ENGINE_MD5) ·
            meaning-preserving prose edits only.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (auto mode: canonical = setup·intake·milestone-loop·stage-graduation·release; reconcile ch16:14 + appendix-c "Scope level").
Least-sure flag surfaced at freeze: [contract] canonical numbering is stage=4th / release=5th (NOT the task<milestone<release granularity ladder); cost if wrong = ch10 + two appendix-c entries would also need changing. Chosen because it's the shipped engine/flow numbering and what 3 of the 5 enumerations already state; the granularity sense is kept as a secondary note (task = the milestone loop's inner unit). Docs-only, 3-tree mirror, no ENGINE_MD5.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the canonical order in all 3 docs + the absent old-base (3 assertions).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ch16_canonical_order: 16-releasing.md contains "after setup, intake, the milestone loop, and stage graduation" AND not "after the task, the milestone" (RED now)
  - test_appendix_c_scope_level_ordered: in the "Scope level" entry, idx(setup) < idx(intake) < idx(milestone) < idx(stage) < idx(release) AND no "· task level" counted token (RED now)
  - test_ch10_anchor_intact: 10-setup-and-stages.md contains "the fourth after setup, intake, and the milestone loop" (GREEN now — guards the anchor)
</test_plan>

Tests live in: `add-method/tooling/test_scope_level_enum.py` · MUST run red (ch16/appendix-c not yet reconciled) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs/16-releasing.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/16-releasing.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `16-releasing.md` `appendix-c-glossary.md` `add-method/tooling/test_scope_level_enum.py`   <!-- canonical ch16+appendix-c + their _bundled mirrors + the REPO-ROOT book twins (4-tree pillar: test_book_parity + test_ground_prose require them) + the guard; .add/docs mirror is pruned (.add excluded), synced via cp -->
Strategy (ordered batches): 1. write test_scope_level_enum.py (RED on ch16+appendix-c). 2. EDIT A (ch16:14) + EDIT B (appendix-c "Scope level") in canonical tree. 3. GREEN; mirror docs -> _bundled (prepare_bundle) + .add (cp); 3-tree doc parity + full suite green.
Safety rule (feature-specific): meaning-preserving prose only; never introduce "altitude"; do not touch ch10 or the two already-canonical appendix-c entries.
Code lives in: `add-method/docs/` (+ _bundled + .add mirrors)
Constraints: docs only — no engine edit; allow-list (no deps); ask if a doc's meaning is unclear.
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

- [x] all tests pass — full suite 1815/0 (clean run, exit 0); guard test_scope_level_enum 3/3; book parity (test_book_parity + test_ground_prose x4) green
- [x] coverage did not decrease — +1 guard (3 assertions); no test removed
- [x] no test or contract was altered during build — the §4 guard is unchanged since the tests phase; BUILD edited only docs (the subject); §3 frozen, untouched
- [x] the green was EARNED, not gamed — refute-read: the guard checks the REAL canonical order by token index in the live doc text (not a fixture), RED on both ch16 + appendix-c before the edits, GREEN only when the prose actually reads in canonical order; the ch10 anchor assertion guards against "fixing" by deleting the reference
- [x] concurrency / timing — n/a (prose edit)
- [x] no exposed secrets / deps — docs only; no code, no deps
- [x] layering & dependencies — 4-tree doc pillar synced byte-identical (canonical + _bundled + .add + repo-root); engine untouched → no ENGINE_MD5 re-pin
- [x] a person reviewed and approved the change — Tin Dang froze v1 (auto mode; canonical numbering documented)

### Build expectations — what "correct" looks like
- [x] ch16 reads "after setup, intake, the milestone loop, and stage graduation" (release fifth) — confirmed by test_ch16_canonical_order + grep
- [x] appendix-c "Scope level" lists the five in order setup<intake<milestone<stage<release, no separate "task level" — confirmed by test_appendix_c_scope_level_ordered
- [x] ch10 anchor + the two already-canonical appendix-c entries unchanged in meaning — confirmed (ch10 anchor test green; no edit to those entries)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose) — read both edited entries in full: ch16 now lists the canonical four-before-release base; appendix-c "Scope level" presents the ordered five with task as the milestone loop's inner unit and stage graduation folded in as #4; "(formerly altitude)" reference preserved, no new "altitude" slang
- [x] WIRING — the guard reads the canonical tree; the repo-root twins (in §5 scope) carry the same edit; 4-tree parity verified by md5
- [x] DEAD-CODE — n/a (prose)

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
