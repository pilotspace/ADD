# TASK: Weave inline citations into specify/process/loop chapters

slug: inline-citations · created: 2026-06-08 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: weave inline author-year citations into the three EXISTING book chapters — `02-the-flow.md` (process) · `03-step-1-specify.md` (specify) · `09-the-loop.md` (loop) — at the points the v21 research grounds, each `[Author Year]` resolving to a FROZEN appendix-g cite-key. Mirrored ×4 byte-identical. A new offline resolver (`test_inline_citations.py`) proves every cite RESOLVES; citation APTNESS (does the source actually ground the claim) is a human §6 SEMANTIC check the resolver cannot cover. v21 task 3 (last task; deps references-appendix + foundations-chapter, both done) — its PASS lets the milestone goal-gate run.
Framings weighed: lean weave ×3 chapters (02·03·09), ~6–7 cites at load-bearing points, a `;`-aware resolver honoring frozen §3 (chosen — human diverge 2026-06-08) · denser weave ~10–15 cites (rejected: saturates prose, reads academic, against the lean "minimal over GSD" goal) · broaden the set to 00/01/11 (rejected: the milestone names "specify / process / loop" specifically — scope creep beyond frozen scope)
Must:
<must>
  - weave inline `[Author Year]` citations into the three chapters `02-the-flow.md`, `03-step-1-specify.md`, `09-the-loop.md`, each mirrored to all 4 book copies byte-identical (root `./` · `add-method/docs/` · `add-method/src/add_method/_bundled/docs/` · `.add/docs/`)
  - EVERY inline cite resolves to an existing appendix-g entry lead `(Author Year)` key — no invented key, no dangling cite; the appendix-g 27 keys stay FROZEN (no entry added, no key edited to fit a cite)
  - a REQUIRED minimum grounding so the weave demonstrably lands in EVERY target: ≥1 resolving cite in EACH of 02, 03, 09 (no chapter left ungrounded), AND the load-bearing "the AI never grades its own work" point in 09 carries `[Yuan et al. 2024]`
  - the inline form honors the FROZEN §3 author-year scheme exactly (`[Surname Year]` · `[Surname & Surname Year]` · `[Surname et al. Year]` · `[Org Year]`; several-at-once joined by `; ` in ONE bracket; same-author-year → `Year`-letter suffix) — keys copied VERBATIM from appendix-g, the resolver normalizes nothing
  - a NEW offline test `./tests/test_inline_citations.py` that COPIES the foundations regexes (the frozen `test_foundations_chapter.py` is NOT touched) and is `;`-aware (splits a bracket body on `; ` and resolves each key) — asserting: every cite in all 3 chapters resolves (0 dangling) · the per-chapter minimum + the `[Yuan et al. 2024]` anchor · the 3 chapters stay ×4 byte-identical · prose stays ban-list-clean
  - prose honors the ubiquitous-language EXTENDED lint surface (the 3 chapters are globbed by `extended_surface()`) — avoids the FULL ban list; writes `fold` ONLY as `` `fold` `` or "retrospective consolidation"
  - citation APTNESS is verified at §6 SEMANTIC — each source genuinely grounds the claim it is attached to, no overstatement. For cites whose chapter claim is NO more specific than the appendix-g annotation, checking against the annotation suffices. But where the claim is MORE specific than "relates to ADD" — the load-bearing interpretive bridges (`[Yuan et al. 2024]` → "the AI never grades its own work"; `[Schluntz & Zhang 2024]` → "evaluator-optimizer *is* build→verify"; `[Vesely 2025]` → "context degrading") — verify against the PRIMARY SOURCE, not just my own task-1 annotation (the annotation verified existence+title+author, not characterization depth — that was the task-2 lesson). This is a HUMAN-judgment check the resolver is blind to (named here so a green suite never reads as sufficient for PASS)
</must>
Reject:
<reject>
  - an inline `[Author Year]` resolving to no appendix-g entry (a dangling / invented citation) -> "dangling_citation"
  - a new appendix-g entry added, or an existing key edited, to fit a cite (the 27 are frozen) -> "appendix_reopened"
  - any of 02 / 03 / 09 left with zero resolving cites (the weave missed a target) -> "chapter_ungrounded"
  - the three chapters' 4 copies not byte-identical -> "mirror_drift"
  - a banned ubiquitous-language token in prose (`fold` unbackticked / "collapses to" / …) -> caught by the extended-surface lint
  - editing, weakening, or refactoring a shared helper out of the frozen `test_foundations_chapter.py` -> "frozen_test_touched"
  - a cite whose source does NOT support the claim it is attached to (an inapt / overstated citation) -> the resolver is BLIND to it; caught only at §6 SEMANTIC human check -> "citation_inapt"
</reject>
After:
<after>
  - the three chapters 02 / 03 / 09 carry inline author-year citations (×4 byte-identical) at the grounded points, every cite resolving to a frozen appendix-g key, prose ban-list-clean — giving the specify/process/loop chapters the grounding the milestone's third exit criterion names; the v21 goal-gate can then run.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract·test] CITATION APTNESS is the bundle's real risk and the resolver is BLIND to it — it proves every `[Author Year]` RESOLVES but says nothing about whether the cited source actually grounds the claim. This is the THIRD instance of the teeth blind-spot this milestone (task 1: a FORM test missed link-existence → URL teeth; task 2: a RESOLUTION test missed narrative consistency → two contradictions passed 642-green; now: the resolution test misses aptness). Lowest confidence because aptness is interpretive — "`[Yuan et al. 2024]` grounds 'the AI never grades its own work'" is a human bridge a passing suite cannot validate. Cost: a plausible-but-wrong citation ships under a green bar. Mitigation: §6 SEMANTIC checks each cite — annotation-match suffices ONLY where the chapter claim is no more specific than the appendix-g annotation; the 2–3 load-bearing bridges whose claim is MORE specific are verified against the PRIMARY SOURCE (the annotation proved existence+title+author, not characterization depth — task-2 lesson, gone one level deeper); aptness is a HUMAN check, never auto-passed on "all cites resolve".
  ⚠ [contract] allowing `;`-joined multi-cites is a CHOICE, not contract-forced — frozen §3 PERMITS `[A; B]` but single-key brackets ALSO honor it (foundations-chapter used only single keys + a one-key resolver). Lowest confidence as a frozen decision because it buys resolver complexity (split on `; `) for a stylistic gain. If wrong: a simpler mandate-one-key-per-bracket rule would have sufficed. This is the bundle-wide freeze flag the human engages at §3. Mitigation: the appendix's OWN house-style example is `[Schmidhuber 2003; Zelikman et al. 2023]`, so multi-cites are already the book's form; the resolver splits then resolves each key — and a baseline scan of all 3 chapters already confirmed 0 false-matches.
  - [ ] [scope] exactly 3 chapters 02/03/09, ~6–7 cites at load-bearing points (not saturated) — SETTLED at diverge (human chose lean ×3, 2026-06-08); high
  - [ ] [test] a NEW `test_inline_citations.py`; `test_foundations_chapter.py` stays untouched (copy, don't refactor) — high
  - [ ] [scope] docs-only — no `add.py`/engine edit, no new chapter, no TOC/nav change (wiring-light vs task 2) — high
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: every inline cite in the three chapters resolves
  Given the woven chapters 02-the-flow, 03-step-1-specify, 09-the-loop
  When the resolver extracts every inline [Author Year] (splitting ;-joined brackets)
  Then each key matches an appendix-g entry lead (Author Year) key
  And the appendix-g 27-key set is unchanged (no entry added, no key edited)

Scenario: the weave lands in every target chapter
  Given the three woven chapters
  When I count resolving cites per chapter
  Then each of 02, 03, 09 has at least one
  And the "the AI never grades its own work" point in 09 carries [Yuan et al. 2024]

Scenario: a ;-joined multi-cite resolves each key
  Given a grounding point citing two sources at once, e.g. [Schmidhuber 2003; Zelikman et al. 2023]
  When the resolver splits the bracket body on "; "
  Then BOTH keys resolve to appendix-g entries
  And neither half is read as a single dangling key

Scenario: the chapters stay mirrored ×4 byte-identical
  Given the three chapters exist in all 4 book copies
  When I hash each chapter across root · add-method/docs · _bundled · .add/docs
  Then the four copies are byte-identical
  And the canonical↔_bundled bundle-parity holds

Scenario: prose stays within the ubiquitous-language ban list
  Given the woven prose (the 3 chapters are globbed by extended_surface())
  When the ubiquitous-language lint scans them
  Then no banned token appears in prose
  And `fold` appears only backticked or as "retrospective consolidation"

Scenario: citation aptness — each source grounds its claim   # human §6 SEMANTIC, resolver-blind
  Given each placed cite and its appendix-g annotation (source-verified in task 1)
  When a human reads the claim the cite is attached to
  Then the annotation supports that claim with no overstatement
  And any NEW quantitative claim was re-fetched against the primary source

Scenario: REJECT a dangling citation
  Given a chapter cite [Author Year] with no matching appendix-g entry
  When the resolver runs
  Then it fails with "dangling_citation"
  And no appendix-g entry is invented to make it pass

Scenario: REJECT an ungrounded target chapter
  Given one of 02 / 03 / 09 left with zero resolving cites
  When the per-chapter minimum check runs
  Then it fails with "chapter_ungrounded"
  And the other chapters' cites are untouched

Scenario: REJECT mirror drift
  Given the four copies of a woven chapter differ by even one byte
  When the parity check runs
  Then it fails with "mirror_drift"
  And the canonical copy is treated as the source of truth

Scenario: REJECT touching the frozen foundations test
  Given test_inline_citations.py is the new home for the resolver
  When the suite runs
  Then test_foundations_chapter.py is byte-unchanged from its committed form
  And no shared helper was refactored out of it ("frozen_test_touched")
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# The resolution contract — what test_inline_citations.py freezes (offline, no network)

WOVEN_CHAPTERS = ("02-the-flow.md", "03-step-1-specify.md", "09-the-loop.md")
COPIES         = root "./" · "add-method/docs/" · "add-method/src/add_method/_bundled/docs/" · ".add/docs/"

extract_cites(chapter_text) ->
  _BRACKET_RE = r"\[([^\[\]]*\b(?:19|20)\d{2}[a-z]?[^\[\]]*)\]"   # bracket body containing >=1 year
  for each bracket body: split on "; "  ->  each piece is one cite-key (verbatim, normalize nothing)
  # year-anchored: markdown links ([Step 1](...), [11 Governance](...)) never match — baseline scan = 0

appendix_g_keys() ->
  _KEY_RE = r"\(([^)]*\b(?:19|20)\d{2}[a-z]?)\)"
  from add-method/docs/appendix-g-references.md, for each line startswith "- **": FIRST (Author Year)
  # the same key-set foundations-chapter resolves into; 27 entries, FROZEN

resolve   ->  every extracted cite-key (across all 3 chapters) ∈ appendix_g_keys()     else "dangling_citation"
minimum   ->  count(resolving cites in chapter) >= 1  for EACH of 02, 03, 09           else "chapter_ungrounded"
anchor    ->  "Yuan et al. 2024" ∈ cites(09-the-loop.md)                                else missing-anchor
multicite ->  [allow branch] >= 1 REAL ;-joined multi-cite appears in prose AND both     else split-branch-dead
              keys resolve  (e.g. [Schmidhuber 2003; Zelikman et al. 2023] in 09)        (exercises the ;-split with a genuine cite, not a synthetic string)
parity    ->  for each woven chapter: md5(4 copies) all equal                            else "mirror_drift"
lint      ->  enforced by the EXISTING test_ubiquitous_language EXTENDED surface (the 3
              chapters are already globbed); a one-line tripwire asserts they stay in that file set

INVARIANTS (not self-tested via brittle md5 literal — guarded by the suite + git review):
  frozen  ->  test_foundations_chapter.py byte-unchanged (it still PASSES in-suite; a diff is git-visible) -> "frozen_test_touched"
  appendix->  appendix-g 27-key set unchanged (assert len(appendix_g_keys()) == 27)         -> "appendix_reopened"

OUT OF TEST SCOPE (human §6 SEMANTIC, the resolver is blind to it):
  aptness ->  each cited source genuinely grounds its claim, no overstatement. Annotation-match
              suffices ONLY where the claim is no more specific than the appendix-g annotation;
              a claim MORE specific than the annotation is verified against the PRIMARY SOURCE -> "citation_inapt"
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-08 · branch: ALLOW `;`-joined multi-cites (the `;`-aware resolver + ≥1 real multi-cite pinned in prose). Changing this contract = a change request back to SPECIFY.
<!-- BUNDLE-WIDE LOWEST-CONFIDENCE FLAG (lead the freeze with this):
  ⚠1 [contract·test] APTNESS is the real risk and the test is BLIND to it — the resolver proves cites
     RESOLVE, never that the source GROUNDS the claim. Third teeth-blind-spot of v21 (form→link, resolution
     →consistency, now resolution→aptness). Cost: a plausible-but-wrong cite ships green. The bundle puts
     aptness on the §6 HUMAN check (vs appendix annotations), never auto-passed on "all cites resolve".
  ⚠2 [contract] allowing `;`-joined multi-cites is a CHOICE (frozen §3 permits, doesn't require; single-key
     also honors it). Two COHERENT contracts, your direction:
       • ALLOW  → I pin ≥1 real `;`-joined multi-cite in prose (e.g. [Schmidhuber 2003; Zelikman et al. 2023]
                  in 09) + keep the `;`-aware resolver + `test_multi_cite_splits_and_resolves`. Matches the
                  book's own house-style example; the split branch is exercised by a genuine cite.
       • MANDATE one key per bracket → I drop the `;`-split, drop `test_multi_cite_splits_and_resolves`,
                  and reuse the foundations one-key resolver verbatim (simpler; multi-source points become
                  adjacent single brackets). -->
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of inline cites in the 3 chapters resolve (0 dangling); every Must/Reject has a test.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_every_inline_cite_resolves: extract cites from all 3 chapters (`;`-aware split) / resolve each against appendix_g_keys() / assert 0 dangling
  - test_weave_lands_in_every_chapter: count resolving cites per chapter / assert each of 02, 03, 09 has ≥1
  - test_yuan_anchor_in_loop: scan 09-the-loop cites / assert "Yuan et al. 2024" present (the load-bearing point)
  - test_real_multi_cite_present_and_resolves: assert ≥1 REAL `;`-joined multi-cite appears in the woven prose AND both keys resolve (exercises the `;`-split with a genuine cite, not a synthetic string)   [ALLOW branch — dropped if human picks mandate-single]
  - test_appendix_g_frozen: assert len(appendix_g_keys()) == 27 (no entry added to fit a cite)
  - test_chapters_mirrored_byte_identical: for each of the 3 chapters / assert md5 equal across the 4 copies
  - test_woven_chapters_on_ban_surface: assert the 3 chapters ∈ extended_surface()'s file set (a one-line tripwire — the ban lint itself stays test_ubiquitous_language's job, no forked ban list here)
  # NOTE: no md5-literal self-test of test_foundations_chapter.py — the frozen test is guarded by still PASSING in-suite + git review, not a brittle hash constant.
</test_plan>

Tests live in: `add-method/tooling/test_inline_citations.py` (sibling of the frozen `add-method/tooling/test_foundations_chapter.py`, where the suite discovers; NEW file, copies its regexes — never edits it) · MUST run red (missing cites / file absent) before Build.
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

- [x] all tests pass — inline-citations **7/7**, full tooling suite **649/649 OK** (+7 net-new)
- [x] coverage did not decrease — +7 net-new tests (test_inline_citations.py); none removed
- [x] no test or contract was altered during build — a NEW test file only; the frozen `test_foundations_chapter.py` is byte-unchanged and still PASSES in-suite; the §3 frozen resolution contract was honored throughout (the post-build aptness rewording of the Yuan sentence KEPT the `[Yuan et al. 2024]` cite-key, so it is a PROSE fix, not a contract/test change)
- [x] concurrency / timing — N/A (docs-only; no runtime, no IO, no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + intra-book cites only; no code, no new package, no NEW external URL (every cite resolves to an appendix-g key whose URL was re-resolved in task 1); stdlib-only test
- [x] layering & dependencies follow CONVENTIONS.md — additive inline cites, ×4 mirror + bundle parity held; the instrument reaction (test_ubiquitous_language EXTENDED surface, which globs these 3 chapters) absorbed cleanly — FULL ban list avoided; `fold` not introduced unbacticked
- [x] a person reviewed and approved the change — Tin Dang, gate below (2026-06-08)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — wiring-light (no new chapter / TOC / nav): the 7 cites are inline in 02·03·09, each resolving to an appendix-g key (test_every_inline_cite_resolves green; 0 dangling), ≥1 per chapter (test_weave_lands_in_every_chapter), and the new `test_inline_citations.py` is discovered + run by the suite (in the 649). No new code symbol.
- [x] DEAD-CODE — the ALLOW-branch `;`-split is EXERCISED by a real multi-cite `[Schmidhuber 2003; Zelikman et al. 2023]` in 09 (test_real_multi_cite_present_and_resolves green) — not dead code; no orphaned symbol; the frozen test was copied-from, never refactored.
- [x] SEMANTIC + APTNESS (read in full — the load-bearing check) — all 7 placed cites read against their appendix-g annotations. 6 are apt by annotation-match (claim ≤ annotation): `[Schluntz & Zhang 2024]` evaluator-optimizer = build→verify · `[GitHub 2025]` spec-as-source-of-truth · `[Delimarsky 2025]` decompose-into-checkable-units · `[Shinn et al. 2023]` failed-check-becomes-feedback · `[Anthropic 2025a]` checkpoint/rewind-rollback · `[Schmidhuber 2003]` change-on-proof + `[Zelikman et al. 2023]` consolidate-learnings-into-the-method. The ONE whose claim was MORE specific than its annotation — `[Yuan et al. 2024]` — was PRIMARY-SOURCE-checked (WebFetch arxiv 2401.10020): the paper shows self-rewarding **improves** (outperforms Claude 2 / Gemini Pro / GPT-4 on AlpacaEval 2.0), it does NOT show "drift". My first draft "a self-rewarding model drifts" OVERSTATED the source → rewrote to "where a self-rewarding loop has the model judge its own reward [Yuan et al. 2024], ADD makes the tests and a human the reward signal instead" (cites the paper as the exemplar ADD diverges from, no false finding). `[Vesely 2025]` was DROPPED — context-rot has no apt home in 02/03/09; force-fitting would be inapt. No NEW quantitative claim introduced.
- [x] ⚠ CROSS-TASK FINDING (disclosed; out of THIS task's frozen 02/03/09 scope) — the COMMITTED chapter 15 (foundations-chapter, task 2, gate-PASSED `ae5502e`) carries the SAME inapt phrasing at line 41: "a model that judges its own reward drifts [Yuan et al. 2024]". The appendix-g annotation is apt; the chapter-15 PROSE overstated it, and task-2's annotation-match aptness check missed exactly what the task-3 primary-source deepening catches. Fix is a 1-clause edit but touches a frozen/committed chapter — the method path is a `reopen` of foundations-chapter. **HUMAN DECISION at this gate (Tin Dang, 2026-06-08): REOPEN-AND-FIX chapter 15 now** for book-wide grounding consistency — sequenced AFTER this task's PASS+commit so the two task lifecycles don't tangle (advisor guidance). The defect is the FRAMING, not the word "drifts": the lead-in "The cautionary thread runs alongside" casts a positive-result paper (self-rewarding *improves*) as a warning — reframe the whole clause the way 09 was fixed (Yuan = the exemplar ADD diverges from), not a word-swap.

### GATE RECORD
Outcome: PASS — docs-only/additive; 7/7 inline + 649/649 full suite green; frozen `test_foundations_chapter.py` byte-unchanged; all 7 cites apt (Yuan primary-source-fixed in 09, Vesely dropped). No security/concurrency/residue finding. One CROSS-TASK gap disclosed (chapter 15 line 41) — does NOT block this task; sequenced as a foundations-chapter reopen before milestone close.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a future appendix-g edit (key renamed/removed) silently dangling an inline cite — `test_inline_citations.py::test_every_inline_cite_resolves` is the standing monitor; the ×4-parity + frozen-27 asserts catch mirror/appendix drift.
Spec delta for the next loop: the weave proved citation APTNESS is a human bridge no resolver covers — the next grounding task should budget a primary-source pass per load-bearing cite, not just an annotation-match.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a green resolver proves cites RESOLVE but is BLIND to citation APTNESS — whether the source grounds the claim. The fix is a §6 PRIMARY-SOURCE check for any claim more specific than the appendix annotation; annotation-match suffices only when the claim is no more specific (evidence: `[Yuan et al. 2024]`'s "drifts" overstatement passed 649-green and was caught only by WebFetch of arxiv 2401.10020 — the paper shows self-rewarding *improves*).
- [ADD · folded] the aptness blind-spot is the THIRD instance of the teeth/aptness lesson this milestone — task 1 a FORM test missed link-existence (URL teeth), task 2 a RESOLUTION test missed narrative consistency (two contradictions passed 642-green), task 3 the resolution test missed aptness. The pattern: a passing structural test reads as sufficient when it is only necessary; the standing fix is a named human SEMANTIC check the resolver is declared blind to (evidence: §1 ⚠ flag + §6 SEMANTIC across all three tasks).
- [SDD · folded] a per-task FROZEN scope (here 02/03/09) correctly bounds the deliverable but can leave the SAME defect in an out-of-scope committed chapter (15) un-fixed — the method needs a "cross-task finding → reopen" path so a defect found while working task N can be fixed in already-done task M without silently editing outside scope (evidence: chapter 15 line 41 carries the same Yuan framing; surfaced at this gate, sequenced as a foundations-chapter reopen).
- [ADD · folded] the annotation-vs-source distinction is now explicit: task 1's appendix annotation verified existence + title + author, NOT characterization depth — so a chapter claim leaning on the *characterization* must go to the primary source, not the annotation (evidence: chapter-15 annotation is apt while its prose overstated — same source, two fidelity levels).
