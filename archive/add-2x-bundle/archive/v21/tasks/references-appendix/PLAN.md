# TASK: Curated annotated references appendix + spec-kit↔ADD phase table

slug: references-appendix · created: 2026-06-08 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a curated, annotated references appendix (`appendix-g-references.md`) in the AIDD book that grounds ADD's dynamic/autonomous loop in VERIFIED external sources — grouped into 4 themed sections, rendered with a frozen author-year citation schema, plus a spec-kit↔ADD phase-comparison table. It is the FROZEN-FIRST artifact of v21: foundations-chapter and inline-citations both cite INTO its cite-keys, so its format is the milestone's shared contract.
Framings weighed: themed annotated bibliography + comparison table (chosen — gives the lineage a spine the downstream tasks cite into) · flat alphabetical bibliography (rejected: loses the RSI/SDD/agentic/tests-first thematic story) · inline-only references with no central appendix (rejected: leaves the chapter + inline-citations tasks no single citable home)
Must:
<must>
  - a NEW book doc `add-method/docs/appendix-g-references.md` (appendices a–f are taken; e=checklists), mirrored to all 4 book copies byte-identical (root `./` · `add-method/docs/` · `add-method/src/add_method/_bundled/docs/` · `.add/docs/`)
  - sources grouped into exactly 4 themed sections: (1) Recursive self-improvement · (2) Autonomous & agentic workflows · (3) Spec-driven development & spec-kit · (4) Tests-first & verification
  - each source rendered with the FROZEN author-year schema: `- **<Title>** (<Author/Org> <Year>) — <url> — <type>. <one-line annotation> ↔ ADD: <how it relates>` — every field present
  - the inline cite-key form (what foundations-chapter + inline-citations use) = the entry's lead `(<Author> <Year>)`: 1 author `[Surname Year]` · 2 `[Surname & Surname Year]` · 3+ `[Surname et al. Year]` · org `[Org Year]` (e.g. `[Anthropic 2026]`, `[GitHub 2025]`); multiples joined by `;`; same-author-same-year collisions get a `Year`-letter suffix (`2023a`/`2023b`)
  - a peer-systems↔ADD phase comparison covering BOTH named peers: spec-kit (constitution↔contract/foundation · specify↔specify · plan↔contract · tasks↔waves · implement↔build) AND GSD/get-shit-done (discuss→plan→execute→verify ↔ ADD's specify→bundle→build→verify→observe) — with a divergence note naming where ADD adds beyond both: failing-tests-first gate · observe→fold self-improvement · dynamic goal-loop (hold/reopen). The project goal positions ADD as "less doc-time than GSD" — state that contrast explicitly.
  - GSD/get-shit-done is a REQUIRED theme-3 entry [GSD 2025] (`github.com/gsd-build/get-shit-done`, now continued as GSD Core at `github.com/open-gsd/gsd-core`) — ADD's closest peer (spec-driven dev for Claude Code, context-rot-driven); user-requested 2026-06-08
  - curated to ~22–27 load-bearing sources from the 40 gathered (cache: `tmp/v21-references-research.md`) + GSD; EVERY link re-VERIFIED at build; NO `[UNVERIFIED]` token in the shipped doc — the 2 flagged arXiv items + the future-dated SDD paper (arXiv 2602.00180) are re-verified or dropped
  - a short intro paragraph: how to read the appendix + the "closing the loop" framing tying the corpus to ADD as the human-gated, evidence-trusted instance of recursive self-improvement
</must>
Reject:
<reject>
  - a source present whose link is unverified / dead / marked [UNVERIFIED] -> "unverified_source_shipped"
  - a source entry missing any of {title, (author year), url, annotation, ↔ ADD relevance} -> "malformed_citation"
  - a source with no "↔ ADD" relevance line (ungrounded trivia) -> "ungrounded_source"
  - the 4 book copies not byte-identical -> "mirror_drift"
  - a source placed outside the 4 named themed sections -> "unthemed_source"
</reject>
After:
<after>
  - the book carries `appendix-g-references.md` (×4 byte-identical): 4 themed sections, author-year entries each with a ↔ ADD line, the spec-kit↔ADD table with its divergence note, a framing intro, every link verified; a stable cite-key scheme exists that foundations-chapter + inline-citations cite into.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract·verify] "every link verified" is the user's HEADLINE rule, yet the offline suite only checks FORM (no "[UNVERIFIED]" token + a url exists) — it cannot tell a real arXiv id from a plausible fake. Lowest confidence as ENFORCEMENT: the teeth live at VERIFY (re-resolve every url as gate evidence — §3 VERIFICATION), not in a unit test. If build hallucinates a plausible id, only the verify re-resolution catches it; cost if missed = a dead/fake link ships, the one thing the milestone forbids
  ⚠ [contract] the frozen tests assert EXTERNAL facts not all primary-confirmed — spec-kit's 5 phases (agent-confirmed from repo+blog) and, weaker, GSD's cycle (from the search summary; the repo WebFetch hit rendering errors). test_gsd_referenced was relaxed to freeze STRUCTURE (GSD entry + doc-time contrast), not the literal cycle string; BUILD primary-source-confirms both before writing. Cost if wrong = a frozen-test/fact clash — avoided by confirming at build, not freezing the unconfirmed wording
  - [ ] [contract] cite-key disambiguation rules (et al. at 3+, org-as-author, `;`-joined, `Year`-letter on same-author/year collision) — SETTLED by the author-year choice; a real 2023 collision in the corpus will fire the suffix rule, but the appendix is the single source so one edit propagates to both downstream tasks (no scattered rework); medium-high
  - [ ] [scope/curation] which ~22–27 of the 40 are "load-bearing" — medium; chosen = seminal/canonical per theme (seed page · Building Effective Agents · spec-kit + SDD launch + spec-driven.md · Gödel→STOP→Self-Refine→Reflexion→Voyager→AlphaEvolve · ReAct/Toolformer/SWE-bench/SWE-agent/AI-Scientist · METR · TDD-for-codegen · GSD), drop secondary reposts; if wrong: add/swap — additive, no rework
  - [ ] the appendix is `appendix-g` (a–f taken); grouping by the 4 themes (not ADD-phase, v21 scope) — high confidence
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the appendix exists and is mirrored byte-identically
  Given the AIDD book
  When I look for appendix-g-references.md in all 4 doc copies
  Then it exists in each (root · add-method/docs · _bundled/docs · .add/docs)
  And all 4 copies are byte-identical

Scenario: the four themed sections are present
  Given appendix-g-references.md
  When I read its section headings
  Then it has exactly the 4 themed sections (RSI · agentic · SDD/spec-kit · tests-first)
  And no source sits outside those four sections

Scenario: every source entry is well-formed (author-year schema)
  Given any source entry in the appendix
  When I parse it
  Then it carries all of {title, (Author Year), url, annotation, ↔ ADD relevance}
  And an entry missing any field would fail "malformed_citation"

Scenario: no unverified source ships
  Given the shipped appendix
  When I scan its text
  Then it contains no "[UNVERIFIED]" token
  And every source line carries an http(s) link

Scenario: a source with no ADD relevance is rejected
  Given a candidate source with no "↔ ADD" line
  When the appendix is checked
  Then it fails "ungrounded_source" (every source must connect to ADD)

Scenario: the spec-kit↔ADD comparison table is present with its divergence note
  Given appendix-g-references.md
  When I read the comparison table
  Then it maps spec-kit phases to ADD phases (constitution↔contract … implement↔build)
  And it names where ADD diverges (tests-first gate · observe→fold · dynamic goal-loop)

Scenario: GSD (get-shit-done) is referenced with a GSD↔ADD contrast
  Given appendix-g-references.md
  When I look for GSD / get-shit-done
  Then it has a verified GSD entry in theme 3 ([GSD 2025], a real link)
  And the comparison names GSD's discuss→plan→execute→verify cycle and the "less doc-time than GSD" contrast

Scenario: the inline cite-key scheme is documented
  Given the appendix
  When I read its "how to cite" note
  Then it states the author-year form (et al. at 3+, org-as-author, ;-joined, year-letter on collision)
  And each entry's lead (Author Year) is its cite-key
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  add-method/docs/appendix-g-references.md   (canonical), mirrored ×4 byte-identical:
  ./appendix-g-references.md · add-method/docs/ · add-method/src/add_method/_bundled/docs/ · .add/docs/

DOC STRUCTURE (top to bottom):
  # Appendix G — References & Lineage
  <intro: how to read · the "closing the loop" framing · the cite-key rule>
  ## How to cite        — the inline form (author-year) the rest of the book uses
  ## spec-kit ↔ ADD     — the phase-comparison table + the divergence note
  ## 1. Recursive self-improvement      — entries
  ## 2. Autonomous & agentic workflows  — entries
  ## 3. Spec-driven development & spec-kit — entries
  ## 4. Tests-first & verification      — entries

ENTRY SCHEMA (frozen — one line, every field required):
  - **<Title>** (<Author/Org> <Year>) — <https url> — <type>. <annotation> ↔ ADD: <relevance>
  fields: Title · (cite-key = Author/Org + Year) · url(http/https) · type(paper|blog|docs|repo|essay|policy) · annotation · ↔ ADD relevance

CITE-KEY RULES (frozen — the inline form foundations-chapter + inline-citations MUST use):
  1 author  -> [Surname Year]            e.g. [Schmidhuber 2003]
  2 authors -> [Surname & Surname Year]  e.g. [Mathews & Nagappan 2024]
  3+ authors-> [Surname et al. Year]     e.g. [Zelikman et al. 2023]
  org author-> [Org Year]                e.g. [Anthropic 2026] · [GitHub 2025]
  multiple  -> joined by "; "            e.g. [Schmidhuber 2003; Zelikman et al. 2023]
  collision -> Year-letter suffix        e.g. [Yao et al. 2023a] / [Yao et al. 2023b]
  the entry's lead (Author Year) IS its cite-key — exactly one entry per key.

PEER-SYSTEMS ↔ ADD COMPARISON (required — both named peers):
  spec-kit rows: constitution↔contract+foundation · clarify↔co-specify flag · specify↔§1 specify ·
    plan↔§3 contract · tasks↔milestone/waves · analyze↔verify deep-checks · implement↔§5 build.
  GSD rows: discuss↔§1 specify (co-specify) · plan↔§3 contract · execute↔§5 build (fresh context) ·
    verify↔§6 verify. GSD shares ADD's Claude-Code + context-rot focus most closely.
  DIVERGENCE NOTE (required): spec-kit stops at implement and GSD at verify; ADD adds the
  failing-tests-first gate (§4) + observe→fold self-improvement (§7) + the dynamic goal-loop (hold/reopen).
  Plus the project's own positioning: ADD targets "less doc-time than GSD" (lean foundation over doc-heaviness).
  GSD entry: [GSD 2025] github.com/gsd-build/get-shit-done (continued as GSD Core, github.com/open-gsd/gsd-core).

ERRORS (the build/verify checks; a failing check blocks the gate):
  unverified_source_shipped — any [UNVERIFIED]/dead link present
  malformed_citation        — an entry missing any required field
  ungrounded_source         — an entry with no "↔ ADD" relevance
  mirror_drift              — the 4 copies not byte-identical
  unthemed_source           — a source outside the 4 themed sections

CURATION: ~20–25 sources (seminal/canonical per theme); the 2 [UNVERIFIED] arXiv items
  (2604.26615, 2406.12952) + the future-dated SDD paper (2602.00180) re-verified or DROPPED.

VERIFICATION (mechanism — how form-checks become evidence-of-truth):
  the offline suite freezes FORM (schema · themes · parity · no-"unverified"-token); it CANNOT tell a
  real arXiv id from a plausible-but-fake one. So "every link verified" gets its teeth at VERIFY (§6),
  not in a unit test: every http(s) url in the shipped appendix is RE-RESOLVED (WebFetch) and recorded
  pass/fail in the GATE RECORD as evidence; ANY non-resolving / wrong-title link = unverified_source_shipped
  -> HARD-STOP (no auto-pass). This keeps the suite offline while making the user's headline rule real.
  PHASE-MODEL CONFIRMATION (at BUILD): spec-kit's (constitution→specify→plan→tasks→implement) AND GSD's
  cycle are PRIMARY-SOURCE-confirmed before the comparison is written — the GSD repo WebFetch hit
  rendering errors, so its cycle is re-fetched from a primary source at build, never trusted from the
  search summary. The frozen suite asserts the comparison's STRUCTURE; build supplies the confirmed wording.

PARITY / INSTRUMENT REACTION (pre-declared, per CONVENTIONS instrument-reaction-by-artifact):
  the FIRING guard is test_bundle_parity (canonical add-method/docs ↔ _bundled/docs — byte-identical,
  same file set): adding appendix-g to canonical REQUIRES the twin in _bundled/docs or it goes red.
  The root `./` and `.add/docs/` copies are convention-mirrored (NOT previously test-guarded) — §4's
  suite ADDS a 4-copy byte-identity assertion (a net-new guard closing that gap). appendix-g is NOT on
  the wording-lint surface (= skill/add + docs/appendix-b only) → surface-count NOT tripped. test_tree_parity
  (skill trees only) is untouched. No engine/add.py change (docs-only).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must/Reject has a behavioral check that PARSES the shipped appendix (not a grep of internals); both new invariants — the entry schema and the 4-copy parity — exercised.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_appendix_exists_in_all_four_copies_byte_identical: arrange the 4 book-copy paths / act stat+md5 each / assert all 4 exist AND share one md5 (mirror_drift guard — net-new for root + .add)
  - test_four_themed_sections_present: read canonical / assert the 4 theme `##` headings exist AND every `- **…**` entry sits under one of them (unthemed_source guard)
  - test_every_entry_is_well_formed: parse every entry line / assert each has {bold title, (Author Year) key, http(s) url, type, ↔ ADD relevance} (malformed_citation + ungrounded_source guards); assert >=18 entries (curated floor)
  - test_no_unverified_token_and_links_present: assert no "[UNVERIFIED]" token (case-insensitive) AND every entry carries an http(s) link (unverified_source_shipped guard)
  - test_speckit_add_table_present_with_divergence: assert a spec-kit↔ADD table maps the key phases (constitution·specify·plan·tasks·implement) AND the divergence note names tests-first + fold + dynamic loop
  - test_cite_key_scheme_documented: assert a "How to cite" section documents the author-year form (et al. at 3+, org-as-author, the entry-lead-is-the-key rule)
  - test_gsd_referenced: assert the appendix references GSD/get-shit-done with a verified entry (bold title + link) AND states the "less doc-time than GSD" contrast (user-requested source). Freezes STRUCTURE not GSD's literal cycle wording — the cycle is primary-source-confirmed + written at BUILD (§3 VERIFICATION), so the frozen test can't clash with an unconfirmed external fact
</test_plan>

Tests live in: `add-method/tooling/test_references_appendix.py` · MUST run red (missing appendix) before Build.
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

- [x] all tests pass — references 7/7, ubiquitous-language 6/6, full tooling suite **633/633 OK**
- [x] coverage did not decrease — +7 net-new tests (test_references_appendix.py); none removed
- [x] no test or contract was altered during build — the test edits (parity skip-guard + GSD relax) were PRE-freeze advisor fixes (contract phase); during build only the appendix .md + the TOC README files were written
- [x] concurrency / timing — N/A (docs-only; no runtime, no IO, no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + links only; no code, no new package
- [x] layering & dependencies follow CONVENTIONS.md — additive book doc, mirrored ×4 + bundle per dogfood-parity; the instrument reaction (test_bundle_parity + ubiquitous-language extended surface) was absorbed
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the gate, 2026-06-08

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — appendix-g IS referenced: wired into the book TOC in all three indexes (add-method/docs/README.md · root ./README.md · .add/docs/README.md) + the _bundled mirror, under "Part IV — Reference" after Appendix F; downstream tasks (foundations-chapter, inline-citations) cite into its keys. Not orphaned.
- [x] DEAD-CODE — no orphaned doc: the TOC wiring above closed the one orphan gap a new appendix would otherwise leave; no source symbol added.
- [x] SEMANTIC (scope stated precisely — not "read in full") — **all 27 links re-resolved (WebFetch); each verified for resolution + page title + author-surname against its cite-key** — the frozen §3 VERIFICATION teeth. 13 arXiv ids each resolve to the expected paper, author surname matching the cite-key (Schmidhuber·Yao·Schick·Shinn·Madaan·Wang·Zelikman·Jimenez·Yuan·Mathews·Yang·Lu·Novikov); 10 web pages each match the expected headline; spec-kit (constitution→specify→plan→tasks→implement) + GSD (discuss→plan→execute→verify) phase models PRIMARY-confirmed; SDD survey (Piskala 2026) resolves. **The two load-bearing quantitative figures were additionally spot-checked against their primary sources this pass: PGR 0.97 / five-days-vs-seven, nine Claude agents (Automated Alignment Researchers) and >80% Claude-authored / four-month doubling (the RSI seed) — both confirmed verbatim.** Remaining per-source quantitative descriptors are carried from research gathering, not re-confirmed link-by-link. The 2 flagged arXiv items (2604.26615, 2406.12952) were DROPPED by curation. Zero dead/wrong links → unverified_source_shipped does NOT fire.

### Evidence — URL re-resolution sweep (gate evidence for the headline rule)
27/27 unique URLs re-resolved this session (build-time: spec-kit · gsd-core · 2602.00180 · the seed; verify-time sweep: 13 arXiv + 10 web pages). Every link reachable, correctly titled/attributed. No HARD-STOP trigger.

### GATE RECORD
Outcome: PASS   (human-gated; evidence complete — 633/633 green, 27/27 links re-resolved, 2 load-bearing figures spot-checked, orphan wiring closed; no security/residue finding)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the "no unverified source ships" scenario is the live monitor — re-resolve every appendix-g URL at each milestone close / before publish; a dead link or a wrong title/author is an `unverified_source_shipped` regression.
Spec delta for the next loop: a grounding/citation doc's VERIFY must spot-check its load-bearing quantitative claims, not only re-resolve URLs — link-resolution proves a source exists with that title+author, not that the number attributed to it is right.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the instrument-reaction prediction in the contract parity-note was INCOMPLETE — a new `add-method/docs/*.md` trips the ubiquitous-language EXTENDED surface (`extended_surface()` globs all docs + skill + templates + diagrams + README + GETTING-STARTED), not just the 19-file wording-lint surface the note named. Evidence: build hit 2 ubiquitous-language failures (`fold` / `collapses to`) on the new appendix, fixed via code-span exemption. Fold: when a task adds a doc, predict the EXTENDED lint surface, not only the wording-lint count.
- [TDD · folded] the frozen invariant "exactly one entry per cite-key" has NO test enforcing uniqueness — `test_every_entry_is_well_formed` asserts each entry HAS a key, not that keys are DISTINCT; a duplicate key would ship green. Evidence: advisor review. Fix: add a key-uniqueness assertion to `test_references_appendix.py`.
- [SDD · folded] cite-key suffix-assignment ORDER (2025a/b/c, 2026a/b) is deterministic-by-appendix-lookup but UNDOCUMENTED in "How to cite"; the 2 downstream tasks lock to these keys. Evidence: advisor review. Fix: a one-line "suffixes assigned in reading order" note hardens foundations-chapter + inline-citations.
- [ADD · folded] VERIFY teeth must extend past link-resolution to load-bearing FIGURES for a grounding doc — the §6 SEMANTIC line over-claimed ("read in full") until the 2 citable numbers (PGR 0.97 / 5-days-vs-7 · >80% Claude-authored / four-month doubling) were spot-checked against primary sources this pass; both confirmed verbatim. Evidence: advisor caught the overclaim. Fold: add "spot-check load-bearing quantitative claims" to the verification mechanism for citation/grounding docs.
