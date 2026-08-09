# TASK: Propagate RELEASE to the book (ch.16 16-releasing.md) + 5 GLOSSARY entries + ×3-tree byte-parity; document the lifecycle order + the root-CHANGELOG nested-package caveat

slug: release-docs-align · created: 2026-06-16 · stage: mvp
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
  - NEW book chapter `16-releasing.md` in the BOOK trees — canonical `add-method/docs/16-releasing.md` + repo-root `./16-releasing.md` (test_book_parity: byte-identical twin) + bundled `add-method/src/add_method/_bundled/docs/16-releasing.md` (test_bundle_parity: byte-identical) + the gitignored dogfood `.add/docs/16-releasing.md` (synced locally, NOT committed/guarded). 4 copies, byte-identical.
  - `appendix-c-glossary.md` (×4 same trees): 5 NEW entries (`release` · `release scope level` · `readiness floor` · `RELEASES.md ledger` · `hotfix release`) + EXTEND the existing **Scope level** entry (L75: lists intake/milestone/setup/task/stage-graduation — add release) so the enumeration is complete. NOTE the existing wording: "Scope level (formerly altitude)" — the book uses **scope level**, NEVER "altitude" (the bare-word wording fence bans it; my task-1 outline title says "altitude" → MUST reword in the chapter).
  - `README.md` docs index (×4): add the `16 · Releasing` line after `15 · Foundations & Lineage`, before the appendices. README.md is EXCLUDED from test_book_parity, so it is NOT byte-guarded — sync all copies for consistency anyway.
  - NEW guard `add-method/tooling/test_release_docs_accord.py` (mirrors test_docs_accord): the book ch.16 names the 7-step release flow IN ORDER + the 5 glossary terms exist + they ACCORD with the shipped `release.md` (a flow rename re-reds it). Asserts CONTENT on the CANONICAL copy only (byte-parity is owned by test_book_parity/test_bundle_parity — do NOT duplicate).
Context (working folder): the content source is `tmp/release-chapter-outline.md` (task-1 outline §1–§7) + the REALIZED behavior from release.md (7-step flow: cue→gather→draft notes→readiness floor→human confirms→cut→watch) · release-report (the 5 record-sets + the `→ releasable` cue) · release-command (the 4 floor codes, security un-forceable; CHANGELOG+RELEASES.md writes; engine-records-human-ships). The §7 deltas from release-command name the doc must-cover items: the lifecycle order, the brownfield first-cut, and finding #3 (root-CHANGELOG nested-package caveat — DOCUMENT-only per the human).
Honors (patterns / conventions): the book keeps the WHY + points to the skill guides for the operational recipe (test_docs_accord's scope-split: book = conceptual + pointer, the recipe stays in release.md) · "scope level" wording (never "altitude") · 4-tree byte-parity (canonical = source; repo-root + bundled byte-identical; .add/docs synced local) · the glossary entry voice + the "formerly altitude" lineage note · engine-records-never-acts stated in the book's own voice.
Anchors the contract cites: `16-releasing.md` (the 7-step flow, in order) · the 5 glossary terms · `appendix-c-glossary.md` Scope-level entry · `README.md` index line · `test_release_docs_accord.py` · the 3 byte-parity book trees + the .add/docs local sync · `release.md` (the accord source).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: book ch.16 `16-releasing.md` + 5 GLOSSARY entries that teach the RELEASE scope level to a PERSON (the book keeps the why; release.md keeps the recipe), propagated byte-identical across the book trees and held in accord with release.md by a new guard.
Framings weighed: append as a NEW ch.16 (chosen — zero renumber churn; chapters 00–15 + appendices stay byte-stable) · insert thematically as ch.11 beside graduation (rejected — renumbers 11→17 + rewrites every cross-ref) · a NEW test_release_docs_accord (chosen — clean parallel to the UDD test_docs_accord; that one is UDD-specific) · extend test_docs_accord (rejected — conflates two features in one guard).
Must:
<must>
  - CHAPTER: `16-releasing.md` exists in all 4 book trees (canonical `add-method/docs/` + repo-root `./` + bundled `_bundled/docs/` byte-identical [3 tracked] + `.add/docs/` synced local). It opens with the "the prior chapters build / loop / graduate but none SHIP" framing and covers, in the book's own voice: the RELEASE scope level (5th, bundles ≥1 closed milestone, ORTHOGONAL to stage) · the `→ releasable: N` cue + release-report's 5 record-sets (gather-not-judge) · drafting notes from FOLDED deltas + the human-confirmed version · the 4-code floor with SECURITY UN-FORCEABLE · engine-records-human-ships (no tag/publish/deploy) · watch + the hotfix path · depth-by-stage · the dogfooded worked example. It POINTS to release.md / release-report / release for the recipe (book = why, not a command reference).
  - FLOW IN ORDER: the chapter names the 7-step flow in canonical order — cue → gather → draft notes → readiness floor → human confirms → cut → watch (the accord anchor).
  - FINDING #3 (document-only): the chapter notes `add.py release` writes CHANGELOG.md at the PROJECT ROOT, and that a repo with a different changelog convention (e.g. a nested-package root pointer) gets release blocks prepended above its existing content — reconcile per repo.
  - GLOSSARY (`appendix-c-glossary.md`, ×4): 5 NEW entries — `release` · `release scope level` · `readiness floor` · `RELEASES.md ledger` · `hotfix release` — in the established entry voice; AND EXTEND the existing **Scope level** entry to include release in its enumeration.
  - INDEX: `README.md` (docs index, ×4) gains the `16 · Releasing` line after `15 · Foundations & Lineage`, before the appendices.
  - WORDING: the chapter + entries use **scope level**, NEVER bare "altitude"; BOTH wording fences (phrase-level wording_lint + bare-word test_ubiquitous_language) stay clean.
  - ACCORD GUARD: new `test_release_docs_accord.py` asserts (on the canonical copy) the 7 steps appear IN ORDER + the 5 glossary terms exist + they ACCORD with release.md (a step/term rename re-reds it). It does NOT duplicate byte-parity (owned by test_book_parity/test_bundle_parity).
  - PARITY: test_book_parity (canonical ↔ repo-root) + test_bundle_parity (canonical ↔ bundled) stay green for the new chapter + glossary.
</must>
Reject:
<reject>
  - ch.16 missing from a tracked tree, or the trees diverge -> "book_parity_drift"  (test_book_parity / test_bundle_parity)
  - a required glossary term is absent, or Scope-level not extended -> "glossary_incomplete"
  - the chapter uses bare "altitude", or trips either wording fence -> "wording_fence_violation"
  - the book contradicts release.md (a flow step / term renamed out of accord) -> "docs_discord"  (test_release_docs_accord)
  - the chapter omits the security-un-forceable OR engine-records-human-ships principle -> "governance_omission"
</reject>
After:
<after>
  - `16-releasing.md` is byte-identical across the 3 tracked trees (+ synced in .add/docs); README index updated; the 5 terms + the extended Scope-level entry are in the glossary; test_release_docs_accord + test_book_parity + test_bundle_parity + both wording fences green; the full engine suite stays green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The accord guard is a NEW `test_release_docs_accord.py` (not an extension of test_docs_accord) — lowest confidence because both choices work; I split it because test_docs_accord is UDD-specific and a single-feature guard reads clearer. If wrong: trivial (one small file vs one larger). No behavior differs.
  - [ ] ch.16 is an APPEND (new chapter), not a thematic insert — settled in the task-1 outline (zero renumber churn; the book is append-friendly).
  - [ ] the book = WHY + a pointer to release.md for the recipe (the test_docs_accord scope-split) — settled; the chapter never becomes a command reference.
  - [ ] `.add/docs/` is gitignored (synced locally for the dogfood engine, never committed) — confirmed via git check-ignore; only the 3 tracked trees are committed.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the chapter ships in every tracked tree, byte-identical
  Given the new ch.16
  When test_book_parity + test_bundle_parity run
  Then 16-releasing.md is present and byte-identical in canonical, repo-root, and bundled trees

Scenario: the chapter names the 7-step flow in order
  Given 16-releasing.md
  When test_release_docs_accord scans it
  Then cue → gather → draft notes → readiness floor → human confirms → cut → watch appear in that order

Scenario: the chapter states the two governance principles
  Given 16-releasing.md
  When the accord guard scans it
  Then it asserts the security HARD-STOP is un-forceable AND engine-records / human-ships (no tag/publish/deploy)
  And it documents that release writes CHANGELOG.md at the project root + the nested-package caveat

Scenario: the five glossary terms exist and Scope level is extended
  Given appendix-c-glossary.md
  When the accord guard scans it
  Then release · release scope level · readiness floor · RELEASES.md ledger · hotfix release are all defined
  And the existing Scope level entry now enumerates release

Scenario: the docs index lists the chapter
  Given README.md (docs index)
  When a reader opens the table of contents
  Then a `16 · Releasing` link appears after `15 · Foundations & Lineage`

Scenario: the prose clears both wording fences
  Given the new chapter + glossary entries
  When wording_lint and test_ubiquitous_language run
  Then there are zero findings (no bare "altitude"; "scope level" is used)
  And no existing surface regressed

Scenario: a flow rename re-reds the accord guard (the guard has teeth)
  Given test_release_docs_accord pinned to release.md's 7 steps
  When a step name in the book is changed out of accord with release.md
  Then the guard fails
  And byte-parity tests are unaffected (accord ≠ parity — separate guards)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  docs/16-releasing.md   (×4 trees; the 3 TRACKED byte-identical: add-method/docs · repo-root · _bundled/docs; .add/docs synced local)
  Sections, IN ORDER:
    intro       — "the prior chapters build / loop / graduate but none SHIP"; the RELEASE scope level (5th · bundles ≥1 closed milestone · ORTHOGONAL to stage)
    §1 Why release is its own scope level   (the stage × released-version axes; release ≠ milestone-close ≠ graduation)
    §2 The cue + the inventory              (`→ releasable: N` · release-report's 5 record-sets · gather-not-judge · folded deltas = the changelog source)
    §3 Drafting the notes + the version     (Keep-a-Changelog grouping · the human-CONFIRMED version · show-before-ask)
    §4 The floor                            (the 4 codes · SECURITY UN-FORCEABLE · disclosure-as-floor · `--force` ≠ security)
    §5 The cut vs. the ship                 (engine RECORDS: CHANGELOG prepend + append-only RELEASES.md row + attribution; NEVER tags/publishes/deploys + the root-CHANGELOG nested-package caveat)
    §6 Watch + the hotfix path              (§2 scenarios → monitors · a regression → narrowed PATCH hotfix re-entering Specify)
    §7 Worked example                       (the dogfooded cut)
  FLOW STRING (verbatim, in order): cue → gather → draft notes → readiness floor → human confirms → cut → watch
  POINTERS (book = why; recipe lives in the guides): release.md · release-report · release; cross-refs ch.08 verify · ch.10 stages · ch.11 governance · ch.09/14 fold.

ARTIFACT  appendix-c-glossary.md  (×4): 5 NEW `**term** — definition.` entries + EXTEND the existing **Scope level** entry to enumerate release.
  release · release scope level · readiness floor · RELEASES.md ledger · hotfix release

ARTIFACT  README.md index line  `- [16 · Releasing](./16-releasing.md)` after the `15 · …` line — in BOTH the docs index (add-method/docs/README.md ×3 doc trees) AND the repo-root landing README's Table of contents.

GUARD  add-method/tooling/test_release_docs_accord.py  (asserts CONTENT on the CANONICAL copy; byte-parity NOT duplicated):
  test_chapter_in_all_trees          — 16-releasing.md present in the 3 tracked trees
  test_flow_seven_steps_in_order     — the 7 step names appear in canonical order in ch.16
  test_governance_principles_present — security-un-forceable + engine-records-human-ships + the root-CHANGELOG caveat are stated
  test_glossary_terms_exist          — the 5 terms defined + Scope-level enumerates release
  test_accord_with_release_md        — the book's 7 steps == release.md's flow arc (a rename re-reds)

Files: 16-releasing.md ×4 · appendix-c-glossary.md ×4 · README.md (docs index ×3 + repo-root landing) · test_release_docs_accord.py ×1.
NO add.py / engine change → NO engine_pin re-aim. The 3 tracked book trees stay byte-identical (test_book_parity + test_bundle_parity).
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-16)
Least-sure flag surfaced at freeze: [contract] the accord guard is a NEW `test_release_docs_accord.py`, not an extension of `test_docs_accord` — both work; split because test_docs_accord is UDD-specific and a single-feature guard reads clearer; cost if wrong is trivial (one small file vs one larger, no behavior differs). Surfaced + accepted at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: binary guard (a docs-accord test — each check is present/absent, not a % of branches); the existing test_book_parity + test_bundle_parity + both wording fences carry the rest.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_chapter_in_all_trees: arrange the 3 tracked trees / act stat 16-releasing.md / assert present in canonical + repo-root + bundled  → scenario "ships in every tracked tree" (byte-identity itself stays owned by the parity tests)
  - test_flow_seven_steps_in_order: arrange ch.16 / act scan / assert FLOW_ARC verbatim + the 7 step tokens unfold in order  → scenario "names the 7-step flow in order"
  - test_governance_principles_present: arrange ch.16 / act scan / assert release_security_open + un-forceable + "the engine records" + "never tags" + "nested-package" present  → scenario "states the two governance principles" + finding #3
  - test_glossary_terms_exist + test_scope_level_enumerates_release: arrange appendix-c-glossary.md / act scan / assert the 5 **headwords** defined AND the **Scope level** entry now contains "release"  → scenario "five terms exist and Scope level is extended"
  - test_accord_with_release_md: arrange ch.16 + release.md / act scan both / assert FLOW_ARC appears in BOTH (a step rename in either re-reds)  → scenario "a flow rename re-reds the accord guard"
  - (scenarios "docs index lists the chapter" + "clears both wording fences" are guarded by README presence + the existing wording_lint/test_ubiquitous_language fences, run in the green step — not re-implemented here)
</test_plan>
RED proof (pre-build): 6 methods, 16 sub-assertions fail because ch.16 + the 5 glossary entries do not exist yet; the accord-SOURCE half passes (release.md already names FLOW_ARC verbatim — `grep -c` = 1), so the guard is red for the RIGHT reason (missing book content, not a broken pin).

Tests live in: `add-method/tooling/test_release_docs_accord.py` · MUST run red (missing implementation) before Build.  <!-- the accord guard lives in tooling/ beside test_docs_accord / test_book_parity, NOT ./tests/ — a repo-suite guard, run by the full engine suite -->.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs` `add-method/src/add_method/_bundled/docs` `.add/docs` `add-method/../16-releasing.md` `add-method/../appendix-c-glossary.md` `add-method/../README.md` `add-method/tooling/test_release_docs_accord.py`   — the 3 directory tokens cover each tree's `16-releasing.md` (NEW) + `appendix-c-glossary.md` (EDIT) + `README.md` docs-index line (EDIT); the 3 `add-method/../` climb tokens are the repo-root twins (chapter byte-twin · glossary byte-twin · the landing README's ToC); the last is the NEW accord guard (lives in `add-method/tooling/`, NOT `./tests/` — it mirrors test_docs_accord). NO `add.py`/`engine_pin.py`/`test_min_pillar.py` — this task ships ZERO engine change (no new subcommand → no census re-red, no md5 re-aim).
Strategy (ordered batches): 1. write the canonical `add-method/docs/16-releasing.md` from `tmp/release-chapter-outline.md` (reword "altitude"→"scope level") · 2. extend `add-method/docs/appendix-c-glossary.md` (5 new entries + the Scope-level enumeration) + the `add-method/docs/README.md` index line · 3. write `add-method/tooling/test_release_docs_accord.py` RED (chapter/terms absent in the other trees) · 4. propagate byte-identical to repo-root (`./16-releasing.md` · `./appendix-c-glossary.md`) + bundled + `.add/docs` (local) · 5. update the repo-root landing `README.md` ToC + the bundled/.add docs-index READMEs · 6. run green (accord + test_book_parity + test_bundle_parity + both wording fences + full engine suite).
Safety rule (feature-specific): the CANONICAL copy (`add-method/docs/`) is the single source — author there, then COPY byte-for-byte to the other 3 trees (never hand-edit a twin); verify with `cmp`/md5 before the green run so test_book_parity + test_bundle_parity cannot drift. The accord guard asserts CONTENT on the canonical copy only — it must not re-assert byte-parity (that is owned by the parity tests). Wording: scan the new prose against BOTH fences before propagating (a bare "altitude" or a tripped phrase reds late + ×4).
Code lives in: the 4 book trees (canonical source + 3 propagated) + the new guard in `add-method/tooling/`
Constraints: do NOT change any test or the contract; this is a DOCS task — NO engine/code change (no add.py, no engine_pin, no test_min_pillar); the book stays WHY + a pointer (the recipe lives in release.md); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add-method engine suite 1158/1158 green (1152 baseline + 6 new accord tests); the 5 guard families (accord · book-parity · bundle-parity · bare-word fence · phrase fence) each green
- [x] coverage did not decrease — +6 accord tests, ZERO engine code removed/changed; `add.py check` 340 passed / 0 failed (14 pre-existing legacy-task warnings, unrelated)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the red guard `test_release_docs_accord.py` is byte-unchanged since RED (it flipped to green purely because the book content now exists); no existing test edited
- [x] the green was EARNED, not gamed — adversarial self-refute: the accord guard reads the CANONICAL chapter (not a fixture), asserts the FLOW_ARC verbatim AND in-order, the 5 glossary headwords by regex, the Scope-level enumeration, the 3 governance anchors, and the arc's presence in BOTH book and release.md (a rename in either re-reds — proven by the RED run where the book-half failed while the release.md-half already passed). No vacuous asserts; parity is delegated to test_book_parity/test_bundle_parity, not faked here
- [x] concurrency / timing of the risky operation is safe — N/A: a pure docs+test change, no runtime/IO/state mutation (engine code untouched; no add.py/engine_pin/test_min_pillar change → no md5 re-aim, no census shift)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + a stdlib-only test (re · unittest · pathlib); no new imports, no network/shell/eval; the bundle re-sync re-copied skill/add.py/templates BYTE-IDENTICAL (git shows zero churn there)
- [x] layering & dependencies follow CONVENTIONS.md — the book keeps the WHY + a pointer to `release.md` (the test_docs_accord scope-split honored: recipe stays in the guide); canonical add-method/docs is the single source, propagated byte-identical to the 3 trees; "scope level" wording throughout (zero bare "altitude"); both wording fences clean
- [ ] a person reviewed and approved the change — PENDING the conservative gate (autonomy: conservative → human owns the gate)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: re-read `16-releasing.md` end to end (intro + §16.1–§16.8) against `release.md` and the realized engine behavior — confirmed the 7-step arc matches, the 4 floor codes + security-un-forceable match release-command, engine-records-human-ships is stated in the book's own voice, finding #3 (root-CHANGELOG nested-package caveat) is a callout, and the 1.5.0 worked example is factually accurate. Glossary: the 5 new entries + the extended Scope-level enumeration read true and use no banned wording. NOTE: the ch.15 nav footer intentionally still points "Next: Appendix A" — chapters 00–15 are byte-frozen per the §1 contract (the Contents index carries the authoritative ch.16 link); recorded as a §7 nav-delta, not a defect.
- [x] WIRING (non-code) — the new chapter is reachable: README docs-index (×3 trees) + the repo-root landing README ToC both link `16 · Releasing`; the glossary's **Scope level** + **Release scope level** entries cross-link; no orphaned file
- [x] DEAD-CODE — the accord guard's every symbol (FLOW_ARC · STEPS · HEADWORDS · GOVERNANCE_TOKENS · the 6 test methods) is exercised by the green run; no unused helper

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (conservative gate; no security surface — docs + a stdlib-only guard)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): test_release_docs_accord is now a permanent regression monitor — a future rename of a release step in `release.md` OR in ch.16 re-reds it; test_book_parity / test_bundle_parity catch any tree drift; both wording fences catch a bare "altitude"/"fold" creeping back in.
Spec delta for the next loop: the milestone's final exit criterion is met (4/4) — release-altitude is ready to close. Deferred from the task-1 outline's wiring checklist (out of this task's frozen scope, candidates for a follow-up): an appendix-e release checklist + an appendix-f requirements-matrix row + adding RELEASE to the `02-the-flow.md` lifecycle diagram (`add-flow.png` regen).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] an appended book chapter cannot repair the prior chapter's nav footer — chapters 00–15 are byte-frozen, so ch.16 chains forward-only and the Contents index is the authoritative link; an append-friendly book trades perfect prev/next nav for byte-stability (evidence: ch.15 still reads "Next: Appendix A" by design, test_book_parity green)
- [SDD · folded] the wrapped-backtick-arc hazard recurs whenever a code-span lifecycle arc wraps to a second source line — test_ubiquitous_language's per-line stripper only exempts spans closed on the SAME physical line, so a bare "fold" inside `milestone-done → fold → …` leaked until the span was single-lined (evidence: 16-releasing.md:64 fence hit, fixed by putting the arc on one line)
- [TDD · folded] a docs-accord guard that asserts the flow arc appears VERBATIM in BOTH the book and its source guide buys a real "rename re-reds" property cheaply, without duplicating byte-parity (owned by the parity tests) (evidence: the RED run failed the book-half while the release.md-half already passed — the guard has teeth on both sides)
