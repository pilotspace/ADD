# PLAN: Retire the Phase 2 Scenarios section from GETTING-STARTED.md

slug: getting-started-descenarios · created: 2026-07-24 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the GETTING-STARTED walkthrough drops the retired "Phase 2 — Scenarios" step, folds its Given/When/Then guidance into Phase 4, and states the true section count.
Framings weighed: retire-in-place — delete Phase 2, keep every surviving heading's number (chosen — mirrors how the fold itself shipped; §3–§7 numbers were deliberately preserved so links and references keep working) · renumber Phases 3-7 down to 2-6 (rejected — breaks the doc's 1:1 map onto the book chapter numbers, which were NOT renumbered)
Must:
<must>
  - M1 no "Phase 2 — Scenarios" walkthrough step remains in the doc
  - M2 no link to the retired 04-step-2-scenarios chapter remains
  - M3 the Given/When/Then guidance survives inside the Phase 4 step, matching shipped §4 rigor (readable case for a human stakeholder, never ceremony)
  - M4 the stated count of PLAN.md phase sections equals the template's actual numbered-section count
  - M5 every surviving phase heading keeps the number it has today
</must>
Reject:
<reject>
  - a walkthrough step linking to a book chapter absent from add-method/docs/ -> "dead_chapter_link"
  - a stated section count that disagrees with PLAN.md.tmpl -> "stale_section_count"
</reject>
After:
<after>
  - every pilotspace.github.io/ADD/ chapter URL in the doc resolves to a file that exists in add-method/docs/
  - the walkthrough teaches the shipped flow: rules -> contract -> red tests -> build -> verify -> observe
</after>
Boundary: chapter links appear ONLY as published-site URLs of the form https://pilotspace.github.io/ADD/nn-slug/ , which map to add-method/docs/nn-slug.md — the checks must speak that URL-to-file mapping.
<assumptions>
  ⚠ the Phase 2 section plus the "seven sections" claim are the ONLY fold-drift left in this doc — if wrong: a second stale claim keeps shipping to npm and PyPI users, and this task closes on a false green
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Artifact: add-method/GETTING-STARTED.md   (the ONE walkthrough; ./GETTING-STARTED.md at the
          repo root is an 18-line pointer stub to it and is NOT touched)

Walkthrough steps AFTER this task — exactly these six, in this order, numbers unchanged:
  Phase 1 — Specify        -> 03-step-1-specify
  Phase 3 — Contract       -> 05-step-3-plan
  Phase 4 — Tests, red first -> 06-step-4-tests
  Phase 5 — Build          -> 07-step-5-build
  Phase 6 — Verify         -> 08-step-6-verify
  Phase 7 — Observe        -> 09-the-loop

Removed: the "Phase 2 — Scenarios" step and its 04-step-2-scenarios link.
Folded : Phase 4 gains the Given/When/Then guidance — including the rejection
         invariance point (a rejected call must leave state unchanged).
Fixed  : the scaffold sentence claiming "all seven phase sections".

Invariant: every https://pilotspace.github.io/ADD/nn-slug/ URL in the doc has a
           matching add-method/docs/nn-slug.md on disk.
```

Grounding anchors (verified in-context this session): add-method/GETTING-STARTED.md heading set at lines 213-289 · the "all seven phase sections" claim at line 203 · add-method/tooling/templates/PLAN.md.tmpl numbered sections 1,3,4,5,6,7 · add-method/docs/ has no 04-step-2-scenarios.md · mkdocs.yml:76 already retitled.

Target (measurable): dead chapter links 1 -> 0 · walkthrough steps 7 -> 6 · surviving heading numbers changed: 0 · all 5 acceptance checks red before the edit and green after · the regression floor (test_scenarios_folded.py, 9 tests) stays green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/GETTING-STARTED.md` `./tests/`
Regression floor: `add-method/tooling/test_scenarios_folded.py` (9 tests — the fold's own guard) must stay green.
Persona (optional): `.add/personas/book-technical-writer.md` — the method prose IS the product surface; this file ships in both the npm and PyPI tarballs.

Strategy (preferred, not hard): write the 5 acceptance checks as one executable script under `./tests/` so red-then-green is reproducible evidence rather than a claim; run it RED first, then make the single-file edit, then re-run GREEN.

Least-sure flag surfaced at freeze: [spec] whether the folded Phase 4 should keep a full gherkin block at all. Shipped §4 rigor demotes Given/When/Then to "inline ONLY when a human stakeholder needs a readable case — never as ceremony", so preserving the whole gherkin example may itself reproduce the ceremony the fold retired. Chosen: keep ONE short gherkin case (a tutorial reader IS the human stakeholder who needs a readable case) and say plainly that the test_plan is the canonical encoding. DECIDED by Tin Dang at the freeze — "Keep one gherkin case"; the prose-only alternative was shown and declined.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_no_phase2_step: the doc has no "Phase 2 — Scenarios" walkthrough heading · covers: M1
  - test_no_retired_chapter_link: the string 04-step-2-scenarios appears nowhere in the doc · covers: M2, R:dead_chapter_link
  - test_gwt_folded_into_phase4: the Phase 4 step's body teaches Given/When/Then AND the rejection-invariance point · covers: M3
  - test_section_count_matches_template: the count the doc states equals the numbered sections in PLAN.md.tmpl · covers: M4, R:stale_section_count
  - test_every_chapter_link_resolves: every ADD/nn-slug/ URL in the doc has a matching add-method/docs/nn-slug.md · covers: M5, After
</test_plan>

Kind: docs — §4 is a failing-first ACCEPTANCE CHECK suite, not a behavioral unit suite. Each check is executable and must run RED against the doc as it stands today, GREEN after the edit.

Scenario a human reader needs (the one readable case, per §4 rigor):
  Given a newcomer following the walkthrough top to bottom
  When they finish Phase 1 and click through to the next step
  Then they land on Contract, and no step points at a chapter the book no longer publishes

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Evidence form: an executable acceptance script — pass/fail per check, exit non-zero while any check is red.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — 5 acceptance checks written first and run RED (5 failed), then one file edited, then GREEN (5 passed). Added beyond plan: a mutation check (re-inject the retired step into the file, confirm 3 checks flip red, restore) to prove the green was earned rather than vacuous.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — 5/5 acceptance green; regression floor test_scenarios_folded.py 9/9 green
- [x] coverage did not decrease — 5 checks added where the doc had none; no check removed
- [x] no test or contract was altered during build — checks written in direction, untouched after the freeze; §3 FROZEN @ v1 unedited
- [x] the green was EARNED, not gamed — mutation-checked: re-injecting the "Phase 2 — Scenarios" step flips test_no_phase2_step, test_no_retired_chapter_link and test_every_chapter_link_resolves to RED; restoring returns 5/5 green
- [x] concurrency / timing — n/a, a single prose file with no runtime behavior
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only edit, no new dependency, no code path
- [x] layering & dependencies — the repo-root GETTING-STARTED.md pointer stub was deliberately NOT touched; one source of truth preserved
- [x] a person reviewed and approved the change — Tin Dang approved the freeze after seeing the exact diff and decided the gherkin question

Target check: dead chapter links 1 -> 0 ✓ · walkthrough steps 7 -> 6 ✓ · surviving heading numbers changed: 0 ✓ (Phases 1,3,4,5,6,7 all intact) · red-before-green demonstrated ✓ · regression floor green ✓ — target HIT.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) mutation — the retired step re-injected into the real file turned 3 of 5 checks red, so the suite is not vacuous; (2) scope — `git status` shows only add-method/GETTING-STARTED.md plus this task dir and engine-owned state.json; (3) the §1 ⚠ assumption was itself tested, not assumed: test_every_chapter_link_resolves scans EVERY chapter URL in the doc and found exactly one dead link, now zero — so no second stale link is hiding.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose retire-in-place — delete Phase 2, keep every surviving heading's number; rejected renumber Phases 3-7 down to 2-6 (rejected — breaks the doc's 1:1 map onto the book chapter numbers, which were NOT renumbered)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — 5 acceptance checks written first and run RED (5 failed), then one file edited, then GREEN (5 passed). Added beyond plan: a mutation check (re-inject the retired step into the file, confirm 3 checks flip red, restore) to prove the green was earned rather than vacuous.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] the fold's book sweep covered add-method/docs/ and mkdocs.yml but missed GETTING-STARTED.md — package-root docs that SHIP (npm `files` allowlist + MANIFEST.in) need to be in the sweep set for any chapter retirement (evidence: a dead link to 04-step-2-scenarios survived from the 2026-07-23 fold into the published v2.3.0 tarballs, found 2026-07-24)
- [SPEC · open] no guard asserts that every book-chapter URL in shipped prose resolves to a real docs file — this task's test_every_chapter_link_resolves is task-local; promoting it to the engine suite would make the whole class of dead chapter links impossible (evidence: the link survived a full milestone close and a release cut with no test objecting)

### Competency deltas
- [SDD · open] "retire in place" must name its SWEEP SET, not just its edit — the fold correctly preserved §-numbers but the milestone had no list of every surface that references a chapter, so a shipped file was missed (evidence: GETTING-STARTED.md dead link found one day after the milestone archived)
- [TDD · open] for a docs task, a mutation check is what separates an earned green from a tautology — re-injecting the defect and watching named checks flip red cost one command and converted "the checks pass" into "the checks would have caught this" (evidence: 3 of 5 checks flipped red on re-injection, restoring returned 5/5)
- [ADD · open] a stale GLOBAL skill mirror silently teaches retired verbs — `~/.claude/skills/add` sat at v1.8.0 against a shipped 2.3.0 and told the agent to run `new-task --fast`, a flag the engine removed with lanes; the engine's own error was the only thing that caught it (evidence: `add.py new-task --fast` -> "unrecognized arguments: --fast" this session)
