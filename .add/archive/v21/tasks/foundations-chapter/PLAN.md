# TASK: Foundations & Lineage narrative chapter

slug: foundations-chapter · created: 2026-06-08 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a NEW narrative book chapter `add-method/docs/15-foundations-and-lineage.md` — "Foundations & Lineage" — that tells ADD's intellectual-lineage story in PROSE (the RSI "closing the loop" framing · the four currents · the spec-kit/GSD divergence · the evidence chain) and CITES INTO appendix-g's frozen author-year keys. v21 task 2 (deps: references-appendix, done); inline-citations (task 3) follows it. Mirrored ×4 byte-identical, wired into the TOC. The appendix is the reference list; this chapter is the STORY that resolves into it.
Framings weighed: a new appended chapter `15-foundations-and-lineage.md` citing into appendix-g (chosen — lowest blast radius; a narrative home distinct from the reference appendix AND from ch.14's operational "project context across milestones") · renumber 03–14 to fold a lineage chapter into Part I (rejected: touches every chapter file + cross-refs + engine pointers + 4 TOCs — high blast radius vs. the lean goal) · expand 00-introduction with a lineage section, no new chapter (rejected: buries the lineage; the milestone exit criterion calls for a distinct chapter)
Must:
<must>
  - a NEW book doc `add-method/docs/15-foundations-and-lineage.md`, mirrored to all 4 book copies byte-identical (root `./` · `add-method/docs/` · `add-method/src/add_method/_bundled/docs/` · `.add/docs/`)
  - the chapter NAMES the RSI "closing the loop" framing — ADD as the human-gated, evidence-trusted instance of recursive self-improvement (AI drives specify→build→verify→observe; a human owns the frozen contract + the verify gate; trust comes from passing tests + re-resolved evidence, never a plausible-looking diff)
  - the chapter NAMES the spec-kit↔ADD divergence TRIAD explicitly: the failing-tests-first gate, the observe→`fold` self-improvement step, and the dynamic goal-loop (hold/reopen) — the three things ADD adds that spec-kit and GSD lack as first-class gates
  - the chapter presents the EVIDENCE CHAIN: the task time-horizon doubling AND >80%-Claude-authored (both via the seed `[Favaro & Clark 2026]`) plus the Automated Alignment Researchers result (`[Anthropic 2026a]`) — the argument "the loop already runs; ADD's contribution is the safety discipline"
  - EVERY inline citation in the chapter uses the frozen `[Author Year]` form AND resolves to an existing appendix-g cite-key — no key invented in the chapter, no dangling cite, no METR key (the time-horizon point cites the seed, per the diverge decision)
  - a REQUIRED core cite-set proving this is a real lineage (not only the Anthropic story) — one anchor per current + evidence + math anchor: `[Favaro & Clark 2026]` · `[Anthropic 2026a]` · `[Schluntz & Zhang 2024]` (agentic) · `[GitHub 2025]` · `[GSD 2025]` · `[Schmidhuber 2003]` · and ≥1 tests-first anchor (`[Mathews & Nagappan 2024]` or `[Jimenez et al. 2023]`) — all present and resolving
  - standard chapter chrome: an H1 title + a `[← 14] · [Contents] · Next: [Appendix A]` nav line consistent with siblings, AND the nav-chain repaired so ch.15's insertion does not break sequential nav: ch.14's `Next:` re-points to ch.15, and Appendix A's back-pointer re-points to ch.15 (both ×4-mirrored docs); a TOC entry under a new "Lineage" heading in all 3 book indexes + the bundle mirror
  - prose honors the ubiquitous-language EXTENDED lint surface (this file is globbed by `extended_surface()`) — it avoids the FULL ban list (spine · dial · safety net · blast radius · rubber-stamp · seam · survivor · altitude · lock-down · blind spot · on-ramp · competency delta · least-sure · trust layer · "X front" · first feeder · wall of · collapses to), and writes `fold` ONLY as backticked `` `fold` `` (code-span exempt) or "retrospective consolidation"
</must>
Reject:
<reject>
  - the chapter file absent from any of the 4 book copies, or the copies not byte-identical -> "mirror_drift"
  - an inline `[Author Year]` cite that resolves to no appendix-g entry (a dangling / invented citation) -> "dangling_citation"
  - the chapter missing any of the 3 named divergence items (tests-first gate · observe→`fold` · dynamic goal-loop) -> "divergence_incomplete"
  - the chapter missing the evidence chain (time-horizon / 80%-authored / Automated Alignment Researchers) -> "evidence_chain_absent"
  - the chapter not referenced in the book TOC (an orphan chapter) -> "orphan_chapter"
  - a banned ubiquitous-language token in prose (`fold` unbackticked / "collapses to") -> caught by the extended-surface lint (the pre-declared instrument reaction)
</reject>
After:
<after>
  - the book carries `15-foundations-and-lineage.md` (×4 byte-identical), wired into the TOC: it narrates the RSI closing-the-loop framing, names the spec-kit↔ADD divergence triad and the evidence chain, and every inline citation resolves to an appendix-g key — giving inline-citations (task 3) a worked model of the cite form in prose.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract·test] the resolution test extracts "valid keys" from appendix-g ENTRY lead lines `(Author Year)` and asserts every chapter `[Author Year]` is among them — lowest confidence because the match is STRING-EXACT: a chapter cite must reproduce the key's punctuation exactly (`&` not `and`, `et al.`, the org name, any `Year`-letter suffix). If a cite drifts (`[Favaro and Clark 2026]`) a VALID citation reads as dangling, or a near-miss typo slips. Cost: a false build failure, or a real dangling cite shipping. Mitigation: the build COPIES keys verbatim from appendix-g; the appendix key-set is the single source of truth, the test normalizes nothing.
  ⚠ [spec] the "required core cite-set" (~6 keys the chapter MUST carry) is a curation judgment, not a derivable fact — lowest-confidence as a frozen assertion because another reviewer might pick a different anchor set; if wrong: the chapter is gated on a cite it didn't need, or misses one it should. Mitigation: the required set is exactly the keys the exit criterion's named elements resolve to (framing + divergence + evidence chain) plus the math anchor `[Schmidhuber 2003]` — tied to the milestone, not to taste.
  - [ ] [scope] chapter 15, appended after 14, NOT a renumber — SETTLED at diverge (renumbering ruled out; human-confirmed lean placement); high
  - [ ] [scope] METR time-horizon cites the seed `[Favaro & Clark 2026]`, no new METR entry — SETTLED at diverge (human chose lean; references-appendix stays frozen); high
  - [ ] the chapter is NARRATIVE — it cites a SUBSET of appendix-g, not all 27 entries; the resolution test asserts cites RESOLVE, not that every entry appears (guards against bibliography-reprint bloat); high
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the chapter exists and is mirrored byte-identically
  Given the AIDD book
  When I look for 15-foundations-and-lineage.md in the book copies
  Then it exists in root · add-method/docs · _bundled/docs (and .add/docs iff that copy is present)
  And every present copy is byte-identical
  And a copy missing or drifting fails "mirror_drift"

Scenario: the RSI closing-the-loop framing is named
  Given the chapter
  When I read its framing section
  Then it states "closing the loop" and casts ADD as the human-gated, evidence-trusted instance of recursive self-improvement
  And a chapter without that framing fails "evidence_chain_absent"/framing review

Scenario: the spec-kit divergence triad is named in full
  Given the chapter
  When I scan for ADD's contribution over spec-kit/GSD
  Then it names all three: the failing-tests-first gate, the observe→`fold` step, and the dynamic goal-loop
  And a chapter missing any one fails "divergence_incomplete"

Scenario: the evidence chain is present
  Given the chapter
  When I read the evidence section
  Then it presents the time-horizon doubling, the >80%-Claude-authored figure, and the Automated Alignment Researchers result
  And a chapter missing the chain fails "evidence_chain_absent"

Scenario: every inline citation resolves to an appendix-g key
  Given the chapter and appendix-g's set of (Author Year) entry keys
  When I extract every inline [Author Year] cite in the chapter
  Then each one is a member of the appendix-g key set
  And a cite resolving to no entry fails "dangling_citation"

Scenario: the required core cite-set is carried
  Given the chapter
  When I check for the anchor citations
  Then [Favaro & Clark 2026], [Anthropic 2026a], [Schluntz & Zhang 2024], [GitHub 2025], [GSD 2025], [Schmidhuber 2003], and ≥1 tests-first anchor all appear and resolve
  And a chapter missing a required anchor fails the core-cite check

Scenario: the chapter is wired into the book TOC
  Given the three book index files
  When I read each table of contents
  Then 15-foundations-and-lineage.md is linked in all three (root · add-method/docs · .add/docs)
  And an unlinked chapter fails "orphan_chapter"

Scenario: inserting ch.15 keeps the sequential nav chain intact
  Given ch.14, the new ch.15, and Appendix A
  When I read their prev/next nav lines
  Then ch.14's Next points to 15-foundations-and-lineage.md (not Appendix A)
  And ch.15 sits between (prev = 14-foundation.md, Next = appendix-a-templates.md)
  And Appendix A's back-pointer points to 15-foundations-and-lineage.md
  And a stale Next/prev at this boundary fails the nav-chain check

Scenario: prose honors the ubiquitous-language extended surface
  Given the chapter on the extended lint surface
  When the ubiquitous-language lint scans it
  Then `fold` appears only inside backticked code spans (or as "retrospective consolidation") and no "collapses to" escapee is present
  And an unbackticked `fold` / "collapses to" trips the extended-surface lint
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC  add-method/docs/15-foundations-and-lineage.md
     mirrored ×4 byte-identical: ./  ·  add-method/docs/  ·  add-method/src/add_method/_bundled/docs/  ·  .add/docs/ (gitignored)

Structure (in order):
  # 15 · Foundations & Lineage                         H1 title
  nav: [← 14 The foundation](./14-foundation.md) · [Contents](./README.md) · Next: [Appendix A …](./appendix-a-templates.md)
  §A  The frame — "closing the loop"                   names RSI closing-the-loop; ADD = human-gated, evidence-trusted instance  · cites [Favaro & Clark 2026]
  §B  The four currents                                RSI · agentic · SDD/spec-kit · tests-first — each current cites its theme anchor(s) from appendix-g
  §C  Where ADD diverges                                the TRIAD — failing-tests-first gate · observe→`fold` · dynamic goal-loop  · cites [GitHub 2025], [GSD 2025]
  §D  The evidence chain                                time-horizon + >80%-authored ([Favaro & Clark 2026]) + Automated Alignment Researchers ([Anthropic 2026a]); "the loop already runs; ADD adds the safety discipline" · may cite [Anthropic 2025c] / [Anthropic 2026b]

Citation rule (FROZEN — the resolution backbone):
  inline form = [Author Year]; the VALID key-set = the (Author Year) leads of appendix-g entry lines (lines starting "- **").
  EVERY inline [Author Year] in the chapter ∈ that key-set.  A cite ∉ key-set -> "dangling_citation".
  No new key is defined in the chapter; no METR key (time-horizon cites the seed, per the diverge decision).

Required core cite-set (all present AND resolving — one anchor per current + evidence + math anchor):
  [Favaro & Clark 2026] (RSI/framing/evidence) · [Anthropic 2026a] (AAR evidence) · [Schluntz & Zhang 2024] (agentic current) ·
  [GitHub 2025] (spec-kit) · [GSD 2025] (closest peer / divergence) · [Schmidhuber 2003] (RSI math anchor) ·
  (≥1 tests-first: [Mathews & Nagappan 2024] | [Jimenez et al. 2023])

Nav-chain repair (FROZEN — inserting ch.15 between ch.14 and Appendix A; all touched files re-mirrored ×4 + bundle parity):
  ch.14  `14-foundation.md`         nav `Next:` [Appendix A …] -> [15 Foundations & Lineage →](./15-foundations-and-lineage.md)
  ch.15  `15-foundations-and-lineage.md`  nav = [← 14 The foundation](./14-foundation.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)
  AppA   `appendix-a-templates.md`  nav `← 13 Adoption` (pre-existing drift, skips 14) -> `← 15 Foundations & Lineage`(./15-foundations-and-lineage.md)  — corrects the back-pointer at the boundary I'm editing
  (14-foundation.md + appendix-a-templates.md each exist in all 4 copies; the chain edits re-mirror them ×4.)

TOC wiring: a NEW "**Lineage**" heading between Part III and Part IV in all 3 indexes (./README.md · add-method/docs/README.md · .add/docs/README.md) + _bundled mirror:
  - [15 · Foundations & Lineage](./15-foundations-and-lineage.md)   (a one-chapter heading — thematically a bridge to Appendix G, not "Operating the method")

Instrument reaction (pre-declared — the FULL surface, not two tokens):
  a new/edited add-method/docs/*.md trips (a) test_bundle_parity (canonical add-method/docs ↔ _bundled/docs byte-identical + same file set) AND
  (b) the ubiquitous-language EXTENDED surface — extended_surface() globs ALL add-method/docs/*.md + skill + templates + diagrams + README + GETTING-STARTED (NOT the 19-file wording-lint surface-count).
  Prose must avoid the FULL ban list (exempt only inside `backtick` code spans): spine · dial(s/ed/ing) · safety net · blast radius · rubber-stamp · seam · survivor · altitude · lock-down · blind spot · on-ramp · competency delta · least-sure · trust layer · "X front" · first feeder · wall of · collapses to · fold (write `` `fold` `` or "retrospective consolidation").

Lint: no "[UNVERIFIED]" token; prose-only; no new dependency.
errors -> { mirror_drift | dangling_citation | divergence_incomplete | evidence_chain_absent | orphan_chapter }
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08
<!-- Bundle-wide flags surfaced at the freeze: ⚠1 [contract·test] cite-resolution is string-exact
     (build copies keys verbatim from appendix-g); ⚠2 [spec] required core cite-set is a curation
     judgment tied to the exit criterion. Diverge decisions: lean METR (cite the seed), ch.15 no renumber. -->

<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must/Reject has one asserting test (9 scenarios → ≥9 tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_chapter_exists_in_copies_byte_identical: require root/canonical/bundle copies; include .add/docs iff present; assert all present copies share one md5 (mirror_drift otherwise) — mirrors references-appendix's skip-guard
  - test_closing_the_loop_framing_named: assert the chapter text contains "closing the loop" AND ("human-gated" or "evidence-trusted") AND a recursive-self-improvement token (RSI / recursive self-improvement)
  - test_divergence_triad_named: assert all three present — a tests-first/failing-test gate token AND `fold` (backticked) AND a dynamic-loop token (dynamic loop / goal-loop / hold-reopen)  -> divergence_incomplete
  - test_evidence_chain_present: assert time-horizon token (time horizon / time-horizon) AND 80%-authored token (80% / Claude-authored) AND Automated-Alignment-Researchers token  -> evidence_chain_absent
  - test_every_inline_cite_resolves: build the appendix-g key-set from entry lead lines `(Author Year)`; extract every chapter inline `[Author Year]`; assert chapter-cites ⊆ key-set  -> dangling_citation  (THE RESOLUTION BACKBONE)
  - test_required_core_cites_present: assert each required anchor ([Favaro & Clark 2026] · [Anthropic 2026a] · [Schluntz & Zhang 2024] · [GitHub 2025] · [GSD 2025] · [Schmidhuber 2003]) appears AND is in the key-set; the tests-first anchor satisfied by ≥1 of [Mathews & Nagappan 2024] | [Jimenez et al. 2023]
  - test_chapter_in_toc: assert the 15-foundations-and-lineage.md link is present in all three TOC READMEs (root · add-method/docs · .add/docs iff present)  -> orphan_chapter
  - test_nav_chain_intact: assert ch.14's Next == 15-foundations-and-lineage.md, ch.15 prev == 14-foundation.md & Next == appendix-a-templates.md, and Appendix A's back-pointer == 15-foundations-and-lineage.md (across every copy each file is present in)  -> nav-chain break
  - test_no_unverified_token: assert no "[UNVERIFIED]" substring in the shipped chapter
  - (ubiquitous-language EXTENDED surface is already enforced by test_ubiquitous_language for any add-method/docs/*.md — not duplicated here; the contract pre-declares it)
</test_plan>

Tests live in: `add-method/tooling/test_foundations_chapter.py` · MUST run red (chapter absent) before Build.
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

- [x] all tests pass — foundations-chapter **9/9**, full tooling suite **642/642 OK** (+9 net-new)
- [x] coverage did not decrease — +9 net-new tests (test_foundations_chapter.py); none removed
- [x] no test or contract was altered during build — the build wrote prose + nav + TOC + mirrors only; the 2 red→green fixes were PROSE edits (attribute multi-cites per-subject; name the AAR result), NOT test edits — the frozen resolution test stood unchanged and caught both (⚠1 working as designed)
- [x] concurrency / timing — N/A (docs-only; no runtime, no IO, no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + intra-book links only; no code, no new package; no new external URL introduced (cites resolve to appendix-g keys, whose URLs were re-resolved last task)
- [x] layering & dependencies follow CONVENTIONS.md — additive book chapter, mirrored ×4 + bundle parity; the instrument reaction (test_bundle_parity + ubiquitous-language EXTENDED surface) absorbed cleanly — the FULL ban list was avoided (no spine/dial/safety-net/blast-radius/rubber-stamp slipped; `fold` backticked)
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-08 (gate PASS, recorded below)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — the chapter is reachable: linked under a new "Lineage" TOC heading in all 3 indexes (root · add-method/docs · .add/docs) + the _bundled mirror, AND the sequential nav chain is repaired bidirectionally — 13 → 14 → **15** → Appendix A and back (ch.14 Next→15, ch.15 prev=14/Next=AppA, AppA back-ptr→15). test_nav_chain_intact + test_chapter_in_toc green. Not orphaned.
- [x] DEAD-CODE — no orphaned doc/symbol: the TOC + nav wiring above closed the orphan gap a new chapter would leave; no source symbol added; the pre-existing .add/docs README drift (missing ch.14) was corrected at the same boundary.
- [x] SEMANTIC (read in full) — **the resolution backbone is proven: every inline `[Author Year]` resolves to an appendix-g key (test_every_inline_cite_resolves green; 0 dangling).** All 6+1 required anchors present & resolving. Each cited source's characterization is derived from its verified appendix-g annotation (Gödel "change-on-proof"·evaluator-optimizer·"done=tests pass" etc. all match). The evidence-chain figures restate the SAME load-bearing numbers spot-checked against primary sources last task: ~97% / five-vs-seven days / nine agents (AAR) and >80%-Claude-authored / time-horizon doubling (seed) — no NEW external claim introduced. Divergence triad named in full (failing-tests-first · observe→`fold` · dynamic goal-loop).
- [x] INTERNAL CONSISTENCY (second pass, advisor-assisted, pre-gate) — a counting read caught two prose contradictions the first "read in full" passed over (both invisible to the suite — nothing counts currents/facts, so 642 was green over them): (a) intro said "**three** currents meet" while §B is the frozen "**The four currents**" — fixed intro to enumerate four (RSI · agentic · SDD · tests-first), matching the frozen §3 heading; (b) §D said "**three** measured facts" but enumerated only two — fixed to First/Second/Third (time-horizon · >80%-authored · AAR), matching the §3 evidence-chain definition. Both were PROSE-only edits (no test token, no framing/evidence anchor touched); re-mirrored ×4 (md5 `9b7e55c9…`), re-ran → 642/642 still green. Close-gap-before-gate, same move as last task's quantitative spot-check.
- [x] CITATION DENSITY (honest framing) — the chapter cites **26 of 27** appendix-g keys (only `[Lu et al. 2024]`, the AI-Scientist, is unused; 0 dangling). This is a near-complete lineage *weave*, not the sparse "subset" my §1 ⚠ assumption pictured — but each of the 26 is load-bearing to its current's paragraph (none is a bare name-drop), so it is NOT bibliography-reprint bloat. The assumption's actual guard ("the test asserts cites RESOLVE, not that every entry appears, so I am not FORCED to reprint the bibliography") still holds; the high density is an authorial choice fit for a lineage survey. Recorded so the gate does not over-claim "subset".
- [x] ⚠ REOPEN → APTNESS RE-VERIFY (2026-06-08, post-gate; `reopen done→build`, reason recorded) — a cross-task aptness finding from inline-citations (task 3, `a85b81a`) caught this chapter's one inapt cite: line 40-42 framed `[Yuan et al. 2024]` as a CAUTIONARY example ("a model that judges its own reward **drifts**") — but a primary-source check (arxiv 2401.10020) shows the paper's result is POSITIVE: self-rewarding *improves* (outperforms Claude 2 / Gemini Pro / GPT-4 on AlpacaEval 2.0). The defect was the FRAMING, not just the word "drifts" — "The cautionary thread runs alongside" casts a positive result as a warning. Reframed the whole clause to match the 09 fix: "And where a self-rewarding loop has the model judge its own reward [Yuan et al. 2024], ADD diverges by design — it makes the tests and a human the reward signal, not the model's own opinion." Cite-key KEPT (anchor + density unchanged: still 26/27, 0 dangling); "The cautionary thread runs alongside:" governed ONLY the Yuan sentence (the positive kin list ends at `[Novikov et al. 2025].`) so nothing was stranded. Re-mirrored ×4 (md5 `bebeaf72…`); re-ran → foundations **9/9** (incl. test_divergence_triad_named, which the reframe reinforces) + full suite **649/649 OK**. This closes the LAST instance of the milestone's teeth/aptness lesson (the appendix annotation was apt; only the chapter prose overstated — annotation-vs-source fidelity). Human-authorized at the inline-citations gate (the reopen-and-fix decision, reframe direction specified).

### GATE RECORD
Outcome: PASS (original gate 2026-06-08; RE-GATED 2026-06-08 after the reopen aptness fix above — re-verify evidence complete: foundations 9/9, full suite 649/649 green, 26/27 chapter cites resolve with 0 dangling, all 6+1 required anchors present incl. the reframed [Yuan et al. 2024], 4 copies byte-identical md5 `bebeaf72…`; docs-only/additive — no security or residue finding). The re-PASS traces to the human's reopen-and-fix authorization at the inline-citations gate, not a fresh self-grant.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08 (original + re-gate)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `test_every_inline_cite_resolves` is the standing monitor — any future cite drift (an appendix-g key renamed, a new chapter cite that mistypes a key) re-fails it; `test_nav_chain_intact` + `test_chapter_in_toc` guard the wiring; `test_bundle_parity` guards the ×4 mirror.
Spec delta for the next loop: **inline-citations (task 3) must decide the multi-cite policy BEFORE weaving** — this build proved the resolution test parses ONE key per `[...]` bracket and cannot validate appendix-g's `;`-joined multi-cite form. Either the cite-style mandates one key per bracket, or the test is extended to split on `;` inside a bracket. Decide at task-3 specify, not mid-build.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] the resolution test (`test_every_inline_cite_resolves`) matches one `[Author Year]` per bracket, so it reads appendix-g's `;`-joined multi-cite form `[A; B]` as a single dangling key — directly blocks task 3's inline weave (evidence: 2 red→green build fixes where `[GitHub 2025; GSD 2025]` and `[Anthropic 2025c; Anthropic 2026b]` had to be rewritten to single-key brackets to stay green).
- [ADD · folded] a frozen offline resolution test proves cites RESOLVE but is silent on internal narrative consistency — two counting contradictions ("three currents" vs the four-currents heading; "three measured facts" enumerated as two) passed 642-green and were caught only by an advisor-assisted human read pre-gate; the VERIFY SEMANTIC check for a PROSE deliverable must include a counting/consistency pass, not just "read in full" (evidence: 2 pre-gate prose fixes, no test ever flagged them).
- [UDD · folded] the dogfood book copy `.add/docs/` drifts silently — it is gitignored and NOT covered by `test_bundle_parity` (which guards only canonical↔`_bundled`), so its README had pre-existing drift (missing the ch.14 line) discovered only while wiring ch.15; either extend parity to the dogfood README or accept it as a known-throwaway install artifact (evidence: ch.14 line restored in `.add/docs/README.md` at this boundary).
- [SDD · folded] the §1 assumption modeled the chapter as a "sparse subset" of appendix-g, but a lineage/survey chapter's natural density is near-complete — it wove 26/27 keys, each load-bearing; a survey-chapter spec should predict near-full coverage, not a subset (evidence: 26/27 keys cited, 0 dangling, no bare name-drops).
