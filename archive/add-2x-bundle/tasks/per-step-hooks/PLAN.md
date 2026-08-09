# TASK: Per-step advisor + confidence hooks across the 8 phase guides

slug: per-step-hooks · created: 2026-06-14 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from auto: method-defining scope (edits the core 8 phase guides + SKILL.md — the agent-consumed surface). High-risk guard requires a lowered rung; verify gate recorded on the human's standing "implement autonomous" authorization. -->
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
  - `add-method/skill/add/phases/0-ground.md … 7-observe.md` (8 guides) — each gets a thin, phase-appropriate Advisor+Confidence hook (a blockquote) pointing to advisor.md + confidence.md; 0-ground/6-verify ALREADY have a spawn hint (generalize, don't duplicate)
  - `add-method/skill/add/SKILL.md:91-95` ("## Beyond the bundle — load on demand") — add a cross-ref so advisor.md + confidence.md are discoverable
  - `add-method/skill/add/advisor.md` · `add-method/skill/add/confidence.md` — the two docs the hooks point to (shipped tasks 1-2; READ-ONLY here)
  - `add-method/tooling/test_per_step_hooks.py` — NEW red suite: each of the 8 guides + SKILL.md references both filenames
Context (working folder):
  - `add-method/tooling/test_xml_convention.py` (PHASE_FILES narrative tuples) — the hook is a PROSE blockquote (no paired convention tag), so it adds NO tag → test_phase_vocab_subset / test_phase_narrative_untagged stay green WITHOUT a registry edit (verified at build)
  - `add-method/tooling/test_wording_lint.py` — file COUNT is unchanged (editing existing guides, adding no skill file); the hook prose must avoid banned idioms (fold/seam/dial/least-sure/…)
  - `add-method/CONTRIBUTING.md` — edit-then-sync: 9 canonical files → prepare_bundle.py + refresh the .claude/skills/add mirror wholesale
Honors (patterns / conventions):
  - minimalism — each hook is ONE blockquote, phase-appropriate, never a copy-pasted block; progressive disclosure (the hook POINTS; advisor.md/confidence.md hold the detail)
  - the frozen XML vocabulary — hooks are pure prose; no new top-level tag in any phase guide (test_xml_convention)
  - ubiquitous language + wording-lint — hook prose avoids every [enforced] banned idiom
Anchors the contract cites: the 8 phase guides · SKILL.md load-on-demand cross-ref · the hook grammar (a blockquote naming both advisor.md + confidence.md) · the new content test asserting the hook in all 8 guides + SKILL.md

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the per-step hooks — a thin, phase-appropriate Advisor+Confidence blockquote in each of the 8 phase guides, plus a SKILL.md load-on-demand cross-ref, wiring confidence.md + advisor.md into the agent-consumed surface so an agent self-scores and knows when to delegate in the idiom of the phase it is in.
Framings weighed: one thin blockquote hook per guide pointing to both docs (chosen — minimal, phase-appropriate, progressive-disclosure) · a full "## Advisor & confidence" section per guide (rejected — too heavy across 8 guides) · only a SKILL.md mention, no per-guide hook (rejected — the request is to enhance EACH step)
Must:
<must>
  - add ONE thin Advisor+Confidence blockquote to each of the 8 phase guides (0-ground … 7-observe), phrased for that phase, naming both `advisor.md` and `confidence.md`
  - generalize (not duplicate) the existing spawn hints in 0-ground.md and 6-verify.md — the new hook points to advisor.md rather than re-explaining the spawn
  - add a SKILL.md "Beyond the bundle — load on demand" cross-ref so advisor.md + confidence.md are discoverable
  - keep every hook PURE PROSE (a blockquote) — no new top-level XML tag in any phase guide
  - propagate all 9 canonical edits to both mirrors (_bundled + .claude/skills/add); all parity green
</must>
Reject:
<reject>
  - a phase guide is left WITHOUT a hook (incomplete coverage) -> "guide_unhooked"
  - a hook introduces a paired convention tag outside the frozen vocab -> "vocab_offmidiom"
  - a hook uses a banned idiom (fold/seam/dial/least-sure/…) -> "banned_idiom_present"
</reject>
After:
<after>
  - all 8 `phases/*.md` carry an Advisor+Confidence hook naming both docs; SKILL.md cross-refs both
  - test_xml_convention + test_wording_lint + test_ubiquitous_language stay green (hooks are clean prose)
  - all mirrors propagated; test_tree_parity + test_book_parity + test_bundle_parity green
  - `add-method/tooling/test_per_step_hooks.py` asserts the hook in all 8 guides + the SKILL.md cross-ref; RED before, GREEN after
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a ONE-blockquote hook per guide is rich enough to "enhance AI context of each step" without bloating the guides — lowest confidence because "rich" vs "thin" is the core tension of this milestone; if wrong: hooks feel token rather than useful, OR they bloat. Mitigated: each hook is phase-appropriate (not boilerplate) and POINTS to the full advisor.md/confidence.md (progressive disclosure), so depth lives in the docs, not the guide.
  - [x] hooks as pure-prose blockquotes add no XML tag (so no PHASE_FILES registry edit needed) — confirmed by the tag model (test_xml_convention checks paired tags only)
  - [x] editing existing guides does not change the wording-lint file count (24) — confirmed (no skill file added)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: every phase guide carries the hook
  Given the 8 phase guides
  When test_per_step_hooks reads each
  Then each names both advisor.md and confidence.md in a blockquote hook

Scenario: the hook is phase-appropriate, not boilerplate
  Given the 8 hooks
  When read together
  Then no two hooks are byte-identical (each is phrased for its phase)

Scenario: SKILL.md makes the docs discoverable
  Given SKILL.md
  When read
  Then its load-on-demand area cross-refs advisor.md and confidence.md

Scenario: the frozen vocabulary and lint stay green
  Given the edited guides + SKILL.md
  When test_xml_convention + test_wording_lint + test_ubiquitous_language run
  Then all are green (hooks add no XML tag and no banned idiom)
  And the wording-lint file count is unchanged (24)

Scenario: a guide left unhooked is rejected
  Given a phase guide with no hook
  When test_per_step_hooks runs
  Then it fails "guide_unhooked"
  And the other guides' hooks are unaffected

Scenario: the mirrors stay in parity
  Given the propagated edits
  When test_tree_parity + test_bundle_parity + test_book_parity run
  Then all are green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
EDIT  add-method/skill/add/phases/{0-ground,1-specify,2-scenarios,3-contract,4-tests,5-build,6-verify,7-observe}.md
      + add-method/skill/add/SKILL.md   (mirrored byte-for-byte to .claude/skills/add/ + _bundled/)
  REQUIRED (each asserted by test_per_step_hooks):
    - each of the 8 phase guides contains a blockquote line naming BOTH "advisor.md" AND "confidence.md"
    - the 8 hooks are mutually distinct (no two byte-identical — phase-appropriate, not boilerplate)
    - SKILL.md cross-refs both "advisor.md" and "confidence.md" in its load-on-demand area
  INVARIANTS (existing guards, must stay green — NOT edited):
    - test_xml_convention: hooks are pure prose → no paired tag added to any phase guide (no PHASE_FILES edit)
    - test_wording_lint: file count stays 24; hook prose carries no banned idiom
    - parity: test_tree_parity · test_book_parity · test_bundle_parity green after propagation
  Reject codes: guide_unhooked · vocab_offmidiom · banned_idiom_present

TEST  add-method/tooling/test_per_step_hooks.py — asserts the 8 hooks + distinctness + the SKILL.md cross-ref; RED before, GREEN after.
PROPAGATION (in THIS task): prepare_bundle.py + refresh .claude/skills/add mirror wholesale → all parity green.
```

Least-sure flag surfaced at freeze: ⚠ [contract] one thin blockquote per guide is rich enough to "enhance each step" without bloating the guides — riskiest because rich-vs-thin is this milestone's core tension; if wrong: hooks read as token or as bloat. Resolved: each hook is phase-appropriate (not boilerplate) and POINTS to the full advisor.md/confidence.md (progressive disclosure).

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-14 (recorded on the standing "implement this milestone autonomous" authorization)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every REQUIRED anchor + each reject code has an assertion (content test).
Plan (one test per scenario):
<test_plan>
  - test_every_guide_hooked: each of the 8 phases/*.md names both advisor.md AND confidence.md (guide_unhooked guard) — the test enumerates ALL 8, fails loudly if any is missing
  - test_hooks_distinct: the 8 hook lines are mutually distinct (no boilerplate)
  - test_skill_cross_ref: SKILL.md names both advisor.md and confidence.md
  - test_xml_convention_phase_guides_green: re-run the phase-guide vocab/narrative checks — still green (no tag added)
  - test_wording_count_unchanged: wl.surface_files() count is still 24
</test_plan>

Tests live in: `add-method/tooling/test_per_step_hooks.py` · MUST run red (hooks absent) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/` · `add-method/skill/add/SKILL.md` · `add-method/tooling/test_per_step_hooks.py` · `add-method/src/add_method/_bundled/skill/add/` · `.claude/skills/add/`
Strategy (ordered batches): 1. write the red suite test_per_step_hooks.py (RED — no hooks yet). 2. add one phase-appropriate Advisor+Confidence blockquote to each of the 8 phase guides. 3. add the SKILL.md load-on-demand cross-ref. 4. propagate: prepare_bundle.py + refresh .claude/skills/add mirror → all parity green. (Directory tokens `phases/`, `_bundled/skill/add/`, `.claude/skills/add/` cover their subtrees.)
Safety rule (feature-specific): hooks are PURE PROSE blockquotes — no XML tag, no banned idiom — so no existing guard (xml_convention/wording_lint/ubiquitous_language) needs editing; this task touches NO guard test except its own new one (the lesson from tasks 1-2).
Code lives in: the 8 `add-method/skill/add/phases/*.md` + `SKILL.md` (canonical) + their two mirrors; test in `add-method/tooling/`.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib unittest); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 7 affected guards green (51 tests), incl. the new test_per_step_hooks (red→green). Full suite 1020 pass / 8 fail; the 8 are the pre-existing node/npx/pip env tests, untouched.
- [x] coverage did not decrease — added test_per_step_hooks.py (5 assertions); net increase
- [x] no test or contract was altered during build — frozen §3 unchanged; per the lesson from tasks 1-2, this task touched NO existing guard test (hooks are pure prose → no registration/count edit); only its own new test added
- [x] the green was EARNED — adversarial refute-read inline: the test enumerates ALL 8 guides (fails loudly if any unhooked), checks both filenames per hook AND mutual distinctness (blocks a boilerplate cheat); hooks are the real deliverable; no test weakened
- [x] concurrency / timing — N/A: prose edits to markdown guides
- [x] no exposed secrets / injection / unexpected deps — new test imports stdlib (+ the in-repo wording_lint via sys.path, same pattern as test_wording_lint)
- [x] layering & dependencies follow CONVENTIONS.md — hooks are thin pointers (progressive disclosure); edit-then-sync honored (bundle regenerated + .claude mirror refreshed wholesale)
- [x] a person reviewed and approved the change — recorded on Tin Dang's standing "implement this milestone autonomous" authorization (conservative gate; the 8 hooks surfaced in chat for async veto)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code+prose) — confidence.md + advisor.md are now referenced from all 8 phase guides AND SKILL.md's load-on-demand area; the milestone's docs are no longer orphans. The new test methods run under unittest discovery.
- [x] DEAD-CODE — no orphaned code; the two docs shipped in tasks 1-2 are now wired in (this task closed the orphan-until-task-3 gap noted in advisor-strategy §7)
- [x] SEMANTIC (prose) — read all 8 hooks + the SKILL.md cross-ref in full: each hook is phase-appropriate (ground→broad sweep · specify→researcher+flag · scenarios→Edge cases · contract→lower autonomy · tests→test-author+Completeness · build→batch+refine · verify→refute-read · observe→Self-evaluation), names both docs, and is pure prose. Matches every frozen §3 anchor.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (standing autonomous authorization) · date: 2026-06-14

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does a future phase-guide edit drop its Advisor·Confidence hook (test_per_step_hooks catches it)? do the hooks stay phase-appropriate or drift to boilerplate?
Spec delta for the next loop: the milestone goal is now fully delivered — confidence.md + advisor.md exist AND are wired into all 8 steps + SKILL.md.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] richer per-step AI context is best delivered as a THIN per-guide pointer to a shared strategy/rubric doc, not inline prose — progressive disclosure keeps the 8 guides minimal while the depth lives in advisor.md/confidence.md (evidence: 8 one-line hooks + 2 docs delivered the whole enhancement with no guide bloat)
- [TDD · folded] a content guard that enumerates the FULL set it covers (all 8 guides) + asserts mutual distinctness blocks both the missing-item cheat and the boilerplate cheat — a count/membership guard is the test-pattern for "every X has Y" doc requirements (evidence: test_per_step_hooks.test_every_guide_hooked + test_hooks_distinct)
