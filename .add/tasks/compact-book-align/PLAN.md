# TASK: Book + GLOSSARY describe foundation compaction + the 4 per-spec shapes

slug: compact-book-align · created: 2026-06-15 · stage: mvp
autonomy: conservative   <!-- LOWERED to match the milestone dial: additive doc alignment (book ch9 + glossary ×3 homes), normal risk, but the human gates the verify like every task this milestone. -->
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
  - `add-method/docs/09-the-loop.md` (+ 2 mirror homes: `add-method/src/add_method/_bundled/docs/09-the-loop.md` · `.add/docs/09-the-loop.md`) — §"Lessons learned and the retrospective consolidation" (L36–52). TWO edits: (a) L50 still says consolidation is "append-only … appends one row to §Key Decisions" — CONTRADICTS the newest-first invariant invariant-amend froze → reconcile to newest-first prepend; (b) add a "Foundation compaction" subsection after L52 (Tooling) describing the retrospective shrink + the per-spec shapes + newest-first.
  - `add-method/docs/appendix-c-glossary.md` (+ 2 mirror homes) — `## Terms` (L7–102), bold-led `**Term** (formerly "…") — def.` paragraphs ending L101 before `---` (L103) / `## Optional mapping` (L105). Add the 4 new terms at the end of ## Terms.
  - 3 doc homes are byte-identical (parity OK: 09-the-loop `a86a911a`, glossary `9243e970`) — every edit lands in ALL 3 (mirror-clause-all-copies, md5).
  - NEW `./tests/test_compact_book_align.py` — guards: ch9 + glossary name foundation compaction + the 4 terms + newest-first; 3-home mirror parity; engine untouched.
Context (working folder): the FROZEN `compaction-contract.md` + `compact-foundation.md` (the ritual this DOCUMENTS) · invariant-amend already froze "newest-first prepend + the compaction door" in fold.md/PROJECT/CONVENTIONS — the book must MATCH · `docs/*.md` are on the ubiquitous-language EXTENDED surface (slang scanned: bare `seam`/`fold`/`survivor` banned in prose → use "retrospective consolidation" / "foundation spec" / code-span doc names like `compact-foundation.md`).
Honors (patterns / conventions): mirror-clause-all-copies (3 doc homes byte-identical) · the book's plain-step voice ("retrospective consolidation", never bare "fold"; `folded` only in code-spans) · convention-guided (no `add.py` edit) · the 4 milestone glossary terms (foundation compaction · rolled-up settled line · per-spec shape · newest-first append-only).
Anchors the contract cites: `09-the-loop.md` §retrospective-consolidation (L50 reconcile + the new Foundation-compaction subsection) · `appendix-c-glossary.md` `## Terms` (the 4 new entries) · the per-spec shapes + newest-first ordering from `compact-foundation.md`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Align the book + glossary with the shipped foundation-compaction ritual — ch9 (`09-the-loop.md`) reconciles its append-only language to NEWEST-FIRST prepend AND gains a "Foundation compaction" passage (the retrospective shrink + per-spec shapes + newest-first); `appendix-c-glossary.md` gains the 4 new terms; every edit byte-identical across the 3 doc homes.
Framings weighed: extend ch9 §"Lessons learned and the retrospective consolidation" (chosen — compaction is the consolidation's sibling retrospective step; readers meet it where the consolidation lives) · a whole new chapter (over-surface for one ritual) · glossary-only (rejected — the exit criterion requires the BOOK to describe the ordering + shapes, not just define terms).
Must:
<must>
  - RECONCILE NEWEST-FIRST: ch9's consolidation prose no longer reads bare "append-only … appends one row" where it contradicts the shipped invariant — it reads newest-first prepend (newest record on top), consistent with fold.md / PROJECT.md / CONVENTIONS.md (invariant-amend).
  - DOCUMENT COMPACTION: ch9 gains a "Foundation compaction" passage — the retrospective shrink SEPARATE from the consolidation: AI proposes / human confirms; collapse the stable shipped tail of each foundation spec into ONE per-spec rolled-up settled line at the bottom; never delete (summarize + git pointer); convention-guided (no `add.py` command); distinct from the engine `add.py compact`.
  - NAME THE SHAPES + ORDERING: the passage names the per-spec shapes (PROJECT §Spec · §Key-Decisions · CONVENTIONS · GLOSSARY · MODEL_REGISTRY) and the newest-first ordering (settled tail at the bottom — collapse upward).
  - GLOSSARY 4 TERMS: `appendix-c-glossary.md` `## Terms` gains foundation compaction · rolled-up settled line · per-spec shape · newest-first append-only — each a single canonical line.
  - MIRROR PARITY: every edit lands byte-identical in all 3 doc homes (`09-the-loop.md` ×3, `appendix-c-glossary.md` ×3).
  - SLANG-CLEAN: the additions carry no banned prose idiom (bare seam/fold/survivor) — `docs/*.md` is on the ubiquitous-language surface; the engine is untouched.
</must>
Reject:
<reject>
  - `09-the-loop.md` or `appendix-c-glossary.md` is not byte-identical across the 3 homes -> "mirror-drift"
  - the book's compaction description diverges from the frozen ritual (shapes / eligibility / newest-first ordering) -> "book-drift"
  - a banned prose idiom (seam / fold / survivor) lands on the doc surface -> "slang-leak"
</reject>
After:
<after>
  - ch9 reads newest-first (no contradicting append-only) AND describes foundation compaction + the per-spec shapes + newest-first; `appendix-c-glossary.md` defines the 4 terms; all ×3 homes md5-identical; the ubiquitous-language + full engine suites stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the GLOSSARY target — `appendix-c-glossary.md` is THE method glossary (not `GLOSSARY.md.tmpl` nor the dogfood `.add/GLOSSARY.md`) — lowest confidence because "GLOSSARY" names 3 files; if wrong: the 4 terms land in the wrong file. Mitigation: appendix-c-glossary.md is the book's term list (the only glossary on the audit-trail/book surface the exit criterion cites); the template + dogfood glossaries are project-scaffolding, OUT of scope (forward-looking).
  - [ ] extending ch9 (not a new chapter) is right — placement; treated settled (compaction is the consolidation's sibling).
  - [ ] the L50 append-only→newest-first reconciliation belongs to THIS task — invariant-amend amended the spec files but the BOOK copy was missed; closing that gap here (close-gap-before-gate).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: ch9 reads newest-first (no contradicting append-only)
  Given 09-the-loop.md §retrospective-consolidation
  When a reader reaches the consolidation prose
  Then it describes the newest record prepended at the top (not bare "append-only … appends one row")
  And it is consistent with the shipped invariant in fold.md / PROJECT.md / CONVENTIONS.md

Scenario: ch9 documents foundation compaction
  Given 09-the-loop.md
  When read after the consolidation
  Then it names foundation compaction as a SEPARATE retrospective shrink (AI proposes, human confirms), collapsing the stable shipped tail of each foundation spec into one per-spec settled line at the bottom, never deleting (summarize + git pointer), convention-guided and distinct from the engine `add.py compact`
  And it names the per-spec shapes and the newest-first ordering

Scenario: the glossary defines the 4 new terms
  Given appendix-c-glossary.md ## Terms
  When read
  Then it defines foundation compaction, rolled-up settled line, per-spec shape, and newest-first append-only

Scenario: every edit is byte-identical across the 3 doc homes
  Given the 3 homes of 09-the-loop.md and appendix-c-glossary.md
  When the edits land
  Then each file is md5-identical across all 3 homes
  And a home left out of sync is rejected with "mirror-drift"

Scenario: the additions stay slang-clean and engine-free
  Given the doc additions
  When the ubiquitous-language + engine suites run
  Then no banned prose idiom (seam/fold/survivor) is introduced (else "slang-leak")
  And add.py is unchanged

Scenario: the book does not drift from the frozen ritual
  Given the compaction description in ch9
  When compared to compact-foundation.md / compaction-contract.md
  Then the shapes, eligibility, and newest-first ordering match
  And a divergence is rejected with "book-drift"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
COMPACT-BOOK-ALIGN CONTRACT — book + glossary document foundation compaction (convention-guided)

deliverables (each byte-identical across 3 doc homes — add-method/docs · add-method/src/.../_bundled/docs · .add/docs):

  09-the-loop.md §"Lessons learned and the retrospective consolidation":
    EDIT (a) reconcile: the consolidation "write" prose drops bare "append-only … appends one row"
       and reads newest-first prepend (newest record on top), matching fold.md/PROJECT/CONVENTIONS.
    EDIT (b) add a "Foundation compaction" passage AFTER the Tooling paragraph:
       - the retrospective SHRINK, SEPARATE from the consolidation (which prepends new learnings);
         compaction later collapses the stable shipped tail of each foundation spec
       - AI proposes / human confirms; never deletes (summarize + a surviving `see git` pointer);
         OPEN residues stay live; convention-guided (no `add.py` command) and distinct from the
         engine `add.py compact <slug>` (the archive recovery-bundle move)
       - names the per-spec shapes (PROJECT §Spec · §Key-Decisions · CONVENTIONS · GLOSSARY ·
         MODEL_REGISTRY) and the newest-first ordering (settled tail at the bottom — collapse upward)
       - voice: plain step names; "retrospective consolidation" (never bare "fold"); `folded` only in code-spans

  the 4 new terms land in ALL THREE glossary TYPES, each in that file's native format:
    A. appendix-c-glossary.md (book, ×3 homes) — `## Terms`, bold em-dash, before the closing `---`:
       - **Foundation compaction** — the retrospective shrink: collapse a foundation spec's stable,
         shipped, zero-residue tail into one rolled-up settled line; AI proposes, human confirms;
         summarize + point (never delete); SEPARATE from the retrospective consolidation; distinct
         from the engine `add.py compact`.
       - **Rolled-up settled line** — the single line left in place of a collapsed run: lossy on prose,
         lossless on traceability (carries a `see git` pointer).
       - **Per-spec shape** — each foundation spec's own tailored rolled-line format, sharing one
         eligibility rule (shipped + zero open residues).
       - **Newest-first append-only** — every append-only foundation sequence prepends the newest
         record at the top; the rolled-up settled line anchors at the bottom (oldest).
    B. tooling/templates/GLOSSARY.md.tmpl (×2 homes: canonical + `_bundled`) — lowercase `term: def`
       in the "ADD method vocabulary" section (same 4 terms, colon form; NO "formerly" — they are new).
    C. .add/GLOSSARY.md (dogfood, ×1) — lowercase `term: def` (same 4 terms, the dogfood's plain form).

mirror parity (WITHIN each type): appendix-c-glossary.md md5-identical ×3 · GLOSSARY.md.tmpl md5-identical
  ×2 · 09-the-loop.md md5-identical ×3. drift -> "mirror-drift"
NOTE: editing `.add/GLOSSARY.md` post-dates apply-compaction's frozen snapshot, so THAT shipped task's
  local `test_glossary_model_registry_unchanged` would read stale if re-run — a later approved change,
  not a regression (the engine suite never runs task-local tests; disclosed at this task's verify).
book fidelity: shapes/eligibility/ordering match compact-foundation.md. divergence -> "book-drift"
surface: additions slang-clean (no bare seam/fold/survivor in prose). leak -> "slang-leak"
engine: UNCHANGED — no add.py edit.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-15 (with the widened glossary scope: the 4 terms land in appendix-c-glossary.md ×3 AND GLOSSARY.md.tmpl ×2 AND .add/GLOSSARY.md)
Least-sure flag surfaced at freeze: [contract] the glossary now spans 3 formats (book bold-em-dash · template/dogfood lowercase-colon) — risk is a format-mismatch or an md5 drift within a type; mitigated by write-once-copy per type + a per-type parity test. Secondary [spec]: editing .add/GLOSSARY.md staleness-reads apply-compaction's shipped local snapshot (disclosed as a later approved change, not a regression).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each Must + each Reject has a test; assertions are behavioral over the live doc files (content + parity), not fixtures.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ch9_reads_newest_first: 09-the-loop.md no longer says "append-only" in the consolidation "write" prose; says prepend / newest-first [guards the reconcile]
  - test_ch9_documents_compaction: 09-the-loop.md contains a "Foundation compaction" passage naming separate-from-consolidation, AI-proposes/human-confirms, never-delete + git pointer, convention-guided, distinct from `add.py compact`
  - test_ch9_names_shapes_and_ordering: the passage names the 5 per-spec specs + "newest-first" + the settled line at the bottom
  - test_glossary_has_4_terms: ALL 3 glossary types (appendix-c-glossary.md ×4 · GLOSSARY.md.tmpl ×3 · .add/GLOSSARY.md) define foundation compaction · rolled-up settled line · per-spec shape · newest-first append-only — each as an OWN ENTRY in that type's native format (bold em-dash in the book, `term:` colon in template/dogfood), not a bare substring inside another entry's body [refute-read hardening]
  - test_doc_mirror_parity: 09-the-loop.md ×4 + appendix-c-glossary.md ×4 + GLOSSARY.md.tmpl ×3 are md5-identical within each type [guards mirror-drift]
  - test_no_engine_creep: add.py (both homes) gained no compaction command/reject-code [guards the convention-guided boundary]
  - test_slang_clean_additions: the new passages carry no bare seam/fold/survivor in prose (code-spans/`folded` exempt) [guards slang-leak]
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/../09-the-loop.md` `add-method/docs/09-the-loop.md` `add-method/src/add_method/_bundled/docs/09-the-loop.md` `.add/docs/09-the-loop.md` `add-method/../appendix-c-glossary.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `add-method/tooling/templates/GLOSSARY.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/GLOSSARY.md.tmpl` `.add/GLOSSARY.md` `./tests/`   — ch9 ×4 + appendix-c glossary ×4 + template glossary ×2 + dogfood glossary ×1 + guard tests. The book mirror is ×4 (engine `test_ground_prose._doc_trees`): the leading `add-method/../<name>` tokens are the REPO-ROOT copies (the 4th home, beside add-method/ and .add/ — the climb resolves them to project root for the scope-gate). NO `add.py`/engine edit (convention-guided). The `.add/…` homes are ride-along (scope-walk excludes `.add/`); the `add-method/…` homes, the repo-root copies, + `./tests/` are the gated anchors.
Strategy (ordered batches): 1. write `./tests/` red · 2. edit ch9 ONCE (reconcile + Foundation-compaction passage) → copy byte-identical to its 3 homes (md5) · 3. add the 4 terms to appendix-c-glossary.md ONCE → copy ×3 (md5); to GLOSSARY.md.tmpl ONCE → copy ×2 (md5); to `.add/GLOSSARY.md` (colon form) · 4. run green + re-run the ubiquitous-language + full engine suites.
Safety rule (feature-specific): each mirrored doc is written from ONE source (write-once-copy) so md5 parity is STRUCTURAL; additions are slang-clean (no bare seam/fold/survivor in prose); never edit the frozen contract or a spec file — the book DESCRIBES, it does not re-amend.
Code lives in: the 3 `09-the-loop.md` homes + the 3 `appendix-c-glossary.md` homes.
Constraints: do NOT change any test or the frozen contract; no `add.py`/engine edit; keep all 3 homes byte-identical; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — task suite 7/7 (`python3 -m unittest discover -s tests`); full engine suite 1027/1027 OK; `add.py check` 324 passed / 0 failed.
- [x] coverage did not decrease — one test per Must + per Reject (7 tests); two guards were STRENGTHENED this verify (see next line), never removed.
- [x] no FROZEN contract was altered; tests were HARDENED, not weakened — §3 stays FROZEN @ v1 (untouched). After the refute-read flagged two vacuous guards I re-crossed into the TESTS phase (the legitimate suite-revision path) and made them STRICTER (own-entry-by-format + an `ai proposes` assertion), then re-advanced tests→build (tripwire + scope re-baselined cleanly). No test was relaxed to pass a build; the engine never ran a weakened test.
- [x] the green was EARNED — independent adversarial refute-read verdict: **EARNED** on all 7 content checks (book-drift PASS, newest-first reconcile PASS, glossary fidelity PASS with md5 ×4/×3/×1 independently recomputed, slang-clean PASS, engine untouched PASS, contract-vs-build a faithful superset). It found TWO vacuous guards (substring-anywhere glossary check; `ai proposes` unasserted) — both CLOSED here and mutation-proved to bite (deleting an own-entry now FAILs the test; the old substring test would have green-passed).
- [x] concurrency / timing — N/A: pure additive prose/markdown edits, no runtime, no shared-state mutation.
- [x] no exposed secrets, injection openings, or unexpected dependencies — doc text only; no code, no deps; `add.py` (both homes) UNTOUCHED (convention-guided boundary held, confirmed by git + the refute-read).
- [x] layering & dependencies follow CONVENTIONS.md — mirror-clause-all-copies honored: book ×4, template ×3, dogfood ×1, each written write-once-copy so md5 parity is structural; the engine is not referenced from the docs and vice-versa.
- [x] a person reviewed and approved the change — Tin Dang resolved the verify gate 2026-06-15: PASS, accepting the ×4 superset (§3 stays frozen; the ×3→×4 home-count disclosed, not a weakening).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [—] WIRING (code) — N/A: no code symbols introduced (convention-guided doc task).
- [—] DEAD-CODE (code) — N/A: no code added; `add.py` untouched, no orphaned symbol.
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the ch9 consolidation prose + the new "Foundation compaction" passage and all 4 glossary entries (book bold-em-dash · template/dogfood colon) were read end-to-end by me AND by the independent refute-read. Confirmed: the passage faithfully restates the FROZEN ritual (5 per-spec shapes · shared eligibility shipped+zero-OPEN-residue · newest-first / settled-line-at-the-bottom / collapse-upward · never-delete + `see git` pointer · AI-proposes/human-confirms · convention-guided, no `add.py` command · distinct from the engine `add.py compact`); the reconcile drops the contradictory "appends one row" and reads newest-first prepend; no bare seam/fold/survivor in the additions.

### ⚠ Disclosed at the gate (not blockers — for the human's eye)
1. §3 said "byte-identical across **3** doc homes"; the real engine-mandated topology is **×4** (the repo-root copy too — `test_ground_prose._doc_trees`). The build synced ALL 4 (a strict superset — the 3 named homes ARE included and identical), so the contract is satisfied, not weakened. §3 was left FROZEN (not edited); the count undercount is disclosed here rather than papered over. → a human may PASS-with-disclosure or request a §3 change-request to correct "3"→"4".
2. §5 Scope was amended this verify to declare the 2 repo-root book copies (`add-method/../09-the-loop.md` · `add-method/../appendix-c-glossary.md`) — they are gated (outside `.add/`) and were previously a pending scope_violation; re-crossing tests→build re-anchored the snapshot, clearing it.
3. Editing `.add/GLOSSARY.md` post-dates apply-compaction's frozen local snapshot, so THAT shipped task's local `test_glossary_model_registry_unchanged` would read stale if re-run — a later approved change, not a regression (the engine suite never runs task-local tests). Already noted in §3's NOTE.
4. Scope-gate caveat (honesty): because the re-anchor was taken AFTER the edits, the gate's snapshot-diff is empty by construction — so out-of-scope assurance rests on the direct git audit (only the book mirror set + the test changed; `add.py` untouched) + the refute-read, not on the snapshot diff alone.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-15

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the ×4 book / ×3 template mirror-parity guards (`test_ground_prose` + this task's `test_doc_mirror_parity`) and the ubiquitous-language slang scan stay green in CI — a future doc edit that misses a home or leaks slang trips them.
Spec delta for the next loop: none new — this task CLOSES the milestone's last gap (book + glossary now describe the shipped ritual). The two deltas below feed the foundation, not a next feature.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] the §0 GROUND map undercounted the book mirror topology as ×3 when the engine mandates ×4 (the repo-root copy too) — grounding a mirror-parity task must enumerate homes from the engine's own `test_ground_prose._doc_trees`, not a hand-count (evidence: 6 engine sync-guard failures surfaced mid-build + the §3 ×3→×4 disclosure at verify)
  - [TDD · folded] a glossary-term guard that asserts bare substring presence is vacuous — the term string recurs inside other entries' bodies, so a deleted own-entry still greens; pin the OWN ENTRY by the home's native format (bold em-dash / `term:` colon) (evidence: refute-read mutation — deleting the `rolled-up settled line` bold entry passed the old test, FAILS the hardened one)
