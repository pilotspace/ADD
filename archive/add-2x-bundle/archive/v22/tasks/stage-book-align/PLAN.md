# TASK: Align docs/10 + GLOSSARY: stage-graduation reads consistently with setup/intake/loop

slug: stage-book-align · created: 2026-06-09 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Book alignment for stage-graduation — `docs/10-setup-and-stages.md` + `appendix-c-glossary.md` describe the three v22 concepts (stage-graduation · graduation analytics · stage-goal-criteria) consistently with how the skill describes setup / intake / loop. Docs-only, additive.
Framings weighed: disambiguate — keep the granularity sense, add a distinct Stage-graduation entry (chosen, user-confirmed) · unify-one-ladder (force both axes into one list) · replace-with-skill-list (overwrite the granularity entry — lossy)
Must:
<must>
  - GLOSSARY gains three entries — **Stage graduation**, **Graduation analytics**, **Stage-goal-criteria** — each named and framed as the skill frames it: graduation = the 4th orchestration loop after setup · intake · milestone-loop (it proposes the move to the next stage as a confirmed roadmap, never a flip); analytics = the gather-not-judge RECORDS/TALLIES the engine emits for the human to verify; stage-goal-criteria = the human-authored `[x]` checklist in PROJECT.md that gates the graduation cue.
  - The existing **Scope level** granularity entry KEEPS its meaning (intake · milestone · setup/foundation · task) and gains ONE bridging clause pointing cross-stage decisions to the stage-graduation loop — so a reader following graduate.md's "4th scope level" lands somewhere coherent (the disambiguate choice).
  - `docs/10` gains a `### Graduating between stages` subsection under `## Stages` describing the orchestration layer: the cue (every milestone done + stage-goal-criteria all `[x]`) → analytics → interview → ≥1 production MILESTONE drafted → human confirms → the `stage production` flip as the FINAL step.
  - The `stage_no_roadmap` guard is documented (one line in that subsection + in the Stage-graduation entry): `add.py stage production` refuses without ≥1 production milestone (a status-agnostic tally, never a readiness judgment), `--force` overrides.
  - All three docs trees stay byte-identical: edit canonical `add-method/docs/`, sync to `.add/docs/` + `add-method/src/add_method/_bundled/docs/`.
  - New prose uses "scope level" (never "altitude"); the glossary `formerly "altitude"` bridge line is preserved.
  - Required existing tokens are preserved: glossary keeps `**onboarding**` (test_v8_docs); docs/10 keeps "parallel streams" / "ready-queue" / "review-queue" (test_v11_docs).
</must>
Reject:
<reject>
  - new prose contains "altitude" outside the bridge line -> "altitude_in_prose"   (test_ubiquitous_language goes red)
  - any docs tree diverges from canonical after the edit -> "docs_tree_drift"   (test_v8_docs glossary md5 / test_bundle_parity docs go red)
  - a required existing token is dropped (onboarding / parallel streams / ready-queue / review-queue) -> "required_token_dropped"   (test_v8_docs / test_v11_docs go red)
  - the **Scope level** granularity sense is overwritten or "task" is dropped -> "granularity_sense_lost"   (human read at gate; forbidden by the disambiguate choice)
  - a new term's name disagrees with the skill's name for it -> "name_mismatch"   (human read at gate; CONVENTIONS "names match GLOSSARY")
</reject>
After:
<after>
  - docs/10 + GLOSSARY describe stage-graduation, graduation analytics, and stage-goal-criteria consistently with setup/intake/loop; both senses of "scope level" coexist without collision; the three docs trees are byte-identical; the full suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A one-clause cross-reference in the **Scope level** entry is enough to dissolve the polysemy — lowest confidence because "scope level" genuinely carries two axes (granularity vs. orchestration loop) and a terse pointer may still read as two unrelated entries rather than one reconciled idea; if wrong: a reader cross-referencing graduate.md's "4th scope level" is mildly confused — cost is prose-clarity only (no engine/test impact), fixable by a follow-up change-request.
  - [ ] `## Stages` in docs/10 is the right home for the graduation subsection (vs. the parallel-streams area or a new top-level section) — confirm at contract.
  - [x] `stage_no_roadmap` is the exact engine error code, the guard is a status-agnostic ≥1-production-milestone tally with a `--force` escape — verified against add.py:671–701 / the `stage --force` help (add.py:2772).
  - [x] docs are a three-tree byte-identical structure (`.add/docs` · `add-method/docs` · `_bundled/docs`); canonical is edited then synced — verified via md5 + test_v8_docs/test_bundle_parity.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Glossary defines the three v22 terms with the skill's names
  Given the GLOSSARY before this task has no Stage-graduation / Graduation-analytics / Stage-goal-criteria entry
  When the canonical GLOSSARY is edited
  Then it contains a "**Stage graduation**" entry naming it the 4th orchestration loop after setup · intake · milestone-loop
  And a "**Graduation analytics**" entry framing it as gather-not-judge records/tallies
  And a "**Stage-goal-criteria**" entry framing it as the human-authored [x] checklist that gates the cue

Scenario: Scope level keeps its granularity meaning and bridges to the loop
  Given the existing "**Scope level**" entry lists intake · milestone · setup/foundation · task
  When the entry is edited
  Then that four-member granularity list is still present (task not dropped)
  And the entry carries one clause pointing cross-stage decisions to the stage-graduation loop

Scenario: docs/10 gains a graduation subsection under Stages
  Given docs/10 has a "## Stages" section and no graduation subsection
  When docs/10 is edited
  Then a "### Graduating between stages" subsection exists under "## Stages"
  And it describes the cue → analytics → interview → ≥1 production milestone → human confirm → stage flip as the final step

Scenario: the stage_no_roadmap guard is documented in both places
  Given the engine refuses `stage production` without ≥1 production milestone (status-agnostic), --force overrides
  When docs/10 and the GLOSSARY are edited
  Then the docs/10 subsection and the Stage-graduation entry each name the stage_no_roadmap guard and its --force escape

Scenario: the three docs trees stay byte-identical
  Given .add/docs · add-method/docs · _bundled/docs were byte-identical before the edit
  When the canonical edit is synced
  Then md5(docs/10) and md5(appendix-c-glossary.md) are equal across all three trees

Scenario: reject — altitude leaks into prose
  Given a new sentence is written in docs/10 or the GLOSSARY
  When it uses the retired term "altitude" outside the `formerly "altitude"` bridge line
  Then test_ubiquitous_language fails with the banned-term hit -> "altitude_in_prose"
  And the `formerly "altitude"` bridge line stays present and unchanged

Scenario: reject — a docs tree drifts
  Given the canonical tree is edited
  When one mirror tree is left unsynced
  Then test_v8_docs (glossary md5) / test_bundle_parity (docs) fail -> "docs_tree_drift"
  And the canonical content remains the intended edit (no rollback to make parity pass)

Scenario: reject — a required existing token is dropped
  Given the edit rewrites a region of docs/10 or the GLOSSARY
  When it removes "onboarding" (glossary) or "parallel streams" / "ready-queue" / "review-queue" (docs/10)
  Then test_v8_docs / test_v11_docs fail -> "required_token_dropped"
  And those tokens are restored without weakening either test

Scenario: reject — the granularity sense is overwritten
  Given the disambiguate choice forbids replacing the granularity list
  When an edit overwrites the "**Scope level**" list with the orchestration enumeration or drops "task"
  Then the human read at the gate refuses it -> "granularity_sense_lost"
  And the original four-member granularity list is preserved

Scenario: reject — a new term's name disagrees with the skill
  Given CONVENTIONS requires names match the GLOSSARY/skill
  When a new entry names a concept differently than graduate.md / SKILL.md does
  Then the human read at the gate refuses it -> "name_mismatch"
  And the skill's shipped term stays the single source of the name
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

This is a docs-only task: the "contract" is the frozen set of NAMES + STRUCTURE the edit
must produce, the THREE-TREE sync target, the DO-NOT-TOUCH boundary, and the guard mapping
(one response per §1 Reject). No API, no schema. Precedent: v12 `book-align` (parity guard +
human read, no new content test).

```
FROZEN NAMES  (must match the shipped skill — graduate.md / SKILL.md / add.py)
  glossary entry headers, verbatim:
    **Stage graduation**        — the 4th orchestration loop after setup · intake · milestone-loop
    **Graduation analytics**    — gather-not-judge RECORDS/TALLIES the engine emits; the human verifies
    **Stage-goal-criteria**     — the human-authored [x] checklist in PROJECT.md that gates the cue
  engine guard name, verbatim:  stage_no_roadmap   (--force overrides)

FROZEN STRUCTURE
  docs/10:   a new `### Graduating between stages` subsection UNDER the existing `## Stages`
  glossary:  the existing `**Scope level**` entry KEEPS its 4-member granularity list
             (intake · milestone · setup/foundation · task) + ONE bridging clause to the loop
  preserved tokens (must remain):
    glossary  -> `**onboarding**`  +  the `formerly "altitude"` bridge line
    docs/10   -> `parallel streams` · `ready-queue` · `review-queue`
  prose rule -> "scope level" only; "altitude" never (outside the one bridge line)

THREE-TREE SYNC TARGET  (edit canonical, then sync; all byte-identical)
  canonical (edit here):  add-method/docs/{10-setup-and-stages.md, appendix-c-glossary.md}
  bundle  (sync):         add-method/src/add_method/_bundled/docs/{…}   [guarded full: test_bundle_parity]
  dogfood (sync):         .add/docs/{…}                                  [guarded: glossary md5 only, test_v8_docs]
  NOTE: .add/docs/10 has NO mechanical parity guard — verified by manual md5 + the human read.

DO NOT TOUCH
  - add-method/tooling/templates/GLOSSARY.md.tmpl — the USER-PROJECT glossary template (domain terms),
    NOT the book glossary; v22 are METHOD concepts → out of scope. (It is a BRIDGE_FILE; leave its bridge intact.)
  - any docs file other than the two named targets; any test; any skill file; add.py.

GUARD MAPPING  (response for every §1 Reject code)
  altitude_in_prose       -> test_ubiquitous_language fails (banned-term hit)
  docs_tree_drift         -> test_bundle_parity (docs) / test_v8_docs (glossary md5) fail
  required_token_dropped  -> test_v8_docs (onboarding) / test_v11_docs (parallel-streams tokens) fail
  granularity_sense_lost  -> human read at gate refuses (no mechanical guard — disambiguate choice)
  name_mismatch           -> human read at gate refuses (CONVENTIONS: names match GLOSSARY/skill)
```

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-09
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: **parity (three docs trees byte-identical) + human read** — NOT a content
assertion. Precedent: v12 `book-align`, reinforced by graduate-guide's observe lesson: pinning
book PROSE in a unit test is the over-testing the method warns against. The book is the trust
layer; its mechanical guard proves the trees MATCH, never that the words are RIGHT — that is the
human read at the verify gate. So **no new test file** is written.

Plan (each §2 scenario → its existing guard; the red→green is the build-time divergence):
<test_plan>
  - Glossary defines three terms        -> human read at gate (no content test by design)
  - Scope level keeps granularity       -> human read at gate (granularity_sense_lost is human-judged)
  - docs/10 graduation subsection        -> human read at gate; + test_v11_docs keeps parallel-streams tokens
  - stage_no_roadmap documented          -> human read at gate (name verified vs add.py:694)
  - three trees byte-identical           -> test_bundle_parity::test_docs_tree_byte_identical (canon↔bundle, full)
                                            + test_v8_docs::test_glossary_defines_onramp (canon↔dogfood, glossary md5)
                                            + manual md5 for .add/docs/10 (no test covers that mirror)
  - reject: altitude_in_prose            -> test_ubiquitous_language (banned-term hit)
  - reject: docs_tree_drift              -> test_bundle_parity / test_v8_docs (md5 mismatch)
  - reject: required_token_dropped       -> test_v8_docs (onboarding) / test_v11_docs (parallel-streams tokens)
  - reject: granularity_sense_lost       -> human read at gate
  - reject: name_mismatch                -> human read at gate
</test_plan>

Red→green (build-time): the suite is GREEN now on the current unaligned book (676 OK, baseline
captured). During build, editing canonical AHEAD of the mirrors makes test_bundle_parity (docs) /
test_v8_docs (glossary md5) go RED — a real divergence detection — then GREEN after the sync.
This is the honest "red" for a docs task; there is no content-presence red because there is no
content test (by design above).

Tests live in: `add-method/tooling/test_bundle_parity.py` `test_v8_docs.py` `test_v11_docs.py` `test_ubiquitous_language.py` · existing guards (no new suite). The parity red→green is demonstrated at Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 676 OK (green half of red→green); parity green across all three docs trees
- [x] coverage did not decrease — 676 = baseline 676 (no test added or removed, by design: docs = trust layer, no content test)
- [x] no test or contract was altered during build — only `add-method/docs/{10,appendix-c}` + their two mirrors edited (+ this TASK.md's own sections); §3 FROZEN untouched; zero test files touched
- [N/A] concurrency / timing — docs-only change, no runtime path
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no secrets, no code, no dependency added
- [x] layering & dependencies follow CONVENTIONS.md — the change lives in the book (audit-trail layer): docs/10 chapter + appendix-c glossary; every engine reference verified against add.py this session (`graduation-report` → `cmd_graduation_report` add.py:2498/2818; `stage production` / `stage_no_roadmap` / `--force` → `cmd_stage` add.py:685–701)
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-09: read the rendered subsection + the three entries + the **Scope level** before→after at the gate; PASS

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [N/A] WIRING (code) — no code symbols introduced (docs-only)
- [N/A] DEAD-CODE (code) — no code introduced
- [x] SEMANTIC (prose / non-code) — read in full: docs/10 lines 85–97 (the `### Graduating between stages` subsection) + glossary lines 61–65 (the three new entries) + line 69 (the edited **Scope level** entry). Confirmed: (a) graduation framed as the 4th scope level after setup · intake · milestone-loop — matches graduate.md:5; (b) the cue, the five steps, the five record-sets, and the `stage_no_roadmap` floor (tally not readiness · `--force` · →production transition only · mirrors the milestone goal-gate) all match graduate.md in substance; (c) the **Scope level** granularity list is preserved with "task" intact, plus one bridging clause to the loop — the disambiguate choice honored, `granularity_sense_lost` avoided; (d) the gather-not-judge cardinal rule is carried; (e) no banned term leaked (test_ubiquitous_language green) and required tokens kept (test_v8_docs onboarding + test_v11_docs parallel-streams green); `.add/docs/10` (no test guard) byte-verified by manual md5. Honesty bound: a semantic read confirms the WORDS match the skill and the design choice — it does not prove a reader follows them.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-09

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the parity guards on every change under `docs/` (test_bundle_parity docs canon↔bundle · test_v8_docs glossary canon↔dogfood) · test_ubiquitous_language as the slang fence · the human read at any future book edit (the only substantive guard for prose).
Spec delta for the next loop: two engine-gaps surfaced (below) worth a future task — a new-task slug-collision warning, and full `.add/docs` tree parity when the mirror is present. Also: stage-graduation is now book-documented, so when THIS project graduates MVP→production, docs/10 `### Graduating between stages` is the human-facing reference for the run.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

- [ADD · folded] **Docs/book tasks have a ceremonial TDD red.** For a trust-layer edit the parity guard proves the three trees MATCH, never that the prose is RIGHT — the real guard is the human read at the gate. Codified in this task's §4 (no new content test). Lesson: do not manufacture a content test to fake a red; name the human read as the substantive guard and keep the parity red honest (evidence: §4 records "Coverage target: parity + human read"; the build red was 2 parity failures from canon-ahead-of-mirror, with zero content-presence red because there is no content test)
- [ADD · folded] **A cross-surface term can carry two axes; disambiguate before unify.** "Scope level" means decision-granularity in the glossary and orchestration-loop in graduate.md; unifying or overwriting loses a sense. Lesson: when a shipped skill reuses a term the book already defines differently, keep both senses and add one bridging clause rather than merging the lists (evidence: glossary line 69 keeps {intake · milestone · setup/foundation · task} + a bridge clause, while graduate.md:5 uses {setup · intake · milestone-loop · stage-graduation}; both coexist post-task)
- [SDD · folded] **A MILESTONE-declared task slug can collide with a prior done task.** v22 declared task 4 as `book-align`, already a done v12 task; `new-task` would have overwritten it. Lesson: needed a manual rename to `stage-book-align` + a MILESTONE.md reference reconciliation — a future engine guard could warn when a declared task slug matches an existing `tasks/` dir (evidence: `book-align` exists as a done v12 task dir; v22 MILESTONE.md lines 65/82 still read `book-align` while the delivering task is `stage-book-align`)
- [TDD · folded] **The `.add/docs` dogfood mirror is only partially parity-guarded.** test_bundle_parity covers canon↔bundle (full) and test_v8_docs covers canon↔dogfood for the GLOSSARY only — `.add/docs/10` has no test, so that mirror can drift silently. Lesson: verified here by manual md5; a future guard could md5 the whole `.add/docs` tree when it is present (evidence: test_v8_docs:90 checks only GLOSSARY_DOGFOOD md5; no test references `.add/docs/10`; this task synced and md5-verified that mirror by hand)
