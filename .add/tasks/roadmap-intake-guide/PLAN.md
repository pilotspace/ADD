# TASK: Roadmap intake (decompose to N milestones)

slug: roadmap-intake-guide · created: 2026-06-26 · stage: mvp
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
- `add-method/skill/add/intake.md` (canonical) — the intake guide. `## The four buckets` (new-major · sub-milestone · task · change-request), `## What you emit (the proposal)`, reject codes incl. `split_required` ("spans more than one bucket; propose the SMALLEST set"). Add a `## Roadmap — a request that is several milestones` section: when a request decomposes into N milestones, propose the roadmap and CREATE all N — first active, the rest `new-milestone --queued` — then promote with `activate` as each starts.
- `add-method/src/add_method/_bundled/skill/add/intake.md` + `.claude/skills/add/intake.md` — the 2 mirrors (byte-identical). 3-tree.
- `add-method/skill/add/SKILL.md:73` `## Intake` section — the one-line intake summary; extend only if it must name the roadmap/queued path (3-tree).
- `add-method/docs/appendix-c-glossary.md` (×4 book trees) — add a glossary entry for the `queued` milestone status + "roadmap intake" (new method vocabulary from task 1 + this task).

Context (working folder):
- depends-on `milestone-queued-state` (DONE, PASS): `new-milestone --queued` + `activate`-promotes already shipped — this task is the GUIDANCE layer that USES them.
- lean fence: intake.md is in the `core` pool (test_skill_lean.py:53, with SKILL.md), ratio 0.88, current headroom ~142 B — adding the roadmap section overflows it → rebaseline the core pool (surface ÷ ratio), don't bypass.
- tests: a new `test_roadmap_intake_guide.py` asserts the intake.md section + the queued/roadmap glossary terms + 3-tree parity.

Honors (patterns / conventions):
- **Convention-only** — intake.md/SKILL.md/book are PROSE; NO `add.py`/engine change (task 1 already shipped the engine). ENGINE_MD5 unchanged.
- **3-tree mirror parity** — intake.md + SKILL.md edits byte-identical ×3; book ×4.
- **AI proposes, human confirms** (intake.md core rule) — the roadmap is a PROPOSAL; the human confirms before any milestone is created.
- **Lean fence** — grow the core pool minimally; rebaseline, never bypass.

Anchors the contract cites:
- intake.md `## Roadmap` section — decompose → create 1 active + N−1 `--queued`, human-confirmed
- the `split_required` reject code relationship (roadmap is the CREATE path for a multi-milestone request)
- glossary: `queued` milestone + roadmap intake terms
- convention-only (ENGINE_MD5 unchanged) + 3-tree/4-tree parity + core lean-fence rebaseline

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: intake.md guidance for a request that is SEVERAL milestones — the AI proposes a roadmap and creates ALL N (first active, the rest `new-milestone --queued`), instead of only the first. Convention-only; uses the engine shipped in task 1.
Framings weighed: a dedicated `## Roadmap` section in intake.md (chosen — discoverable, sits beside the four buckets) · fold it into the `split_required` reject note (rejected: roadmap is a CREATE path, not a rejection) · a separate roadmap.md guide (rejected: too heavy for the guidance delta)
Must:
<must>
  - `intake.md` gains a `## Roadmap` section: when a request decomposes into N>1 milestones, the AI proposes the roadmap (the ordered milestone list + one-line goals) and, on confirm, CREATES all N — the first active (`new-milestone`), the rest queued (`new-milestone --queued`).
  - The section states the queued milestones are PROMOTED one at a time with `activate <slug>` as each is started (the 1-active-at-a-time working model).
  - It keeps the intake floor: AI PROPOSES the roadmap, the human CONFIRMS before any milestone is created (never auto-creates N milestones unprompted).
  - It distinguishes roadmap from `split_required`: split_required is for a request spanning DIFFERENT buckets; a roadmap is several milestones of the SAME line, created queued.
  - `appendix-c-glossary.md` defines `queued` milestone status + "roadmap" (the multi-milestone intake artifact), consistently named (×4 book trees).
  - All edits propagate byte-identical (intake.md ×3, glossary ×4); NO `add.py`/engine change (ENGINE_MD5 unchanged); the core lean fence is rebaselined, not bypassed.
</must>
Reject:
<reject>
  - the guidance auto-creates N milestones without a human confirm -> "roadmap_unconfirmed" (violates the intake floor)
  - any engine edit (`add.py` / ENGINE_MD5) -> "engine_touched"
  - a mirror left out of sync (intake.md ×3 / glossary ×4) -> "mirror_drift"
</reject>
After:
<after>
  - A multi-milestone request has a documented path: propose the roadmap → create 1 active + N−1 queued → promote each with `activate`.
  - Identity of the engine is unchanged (ENGINE_MD5 same); mirrors + lean fence in sync.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The roadmap guidance lives as a new `## Roadmap` SECTION in intake.md (not folded into the bucket table) — lowest confidence because it grows the tight `core` lean pool and a terse table-row note might suffice; if wrong: the section is heavier than needed and the rebaseline was avoidable. (Surface at the freeze.)
  - [ ] a glossary entry for `queued`/`roadmap` belongs in the BOOK glossary (appendix-c) vs only the skill — confirm the book is the right home (task 1 added no glossary term, so this also backfills the queued term).
  - [ ] the 1-active-at-a-time promotion model (vs activating several) is the guidance default — matches the milestone behavior chosen earlier.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: intake.md has a Roadmap section
  Given the intake guide intake.md
  When I read it
  Then a "## Roadmap" section explains decomposing an N-milestone request into 1 active + N−1 queued

Scenario: the roadmap section names the engine path
  Given the Roadmap section
  When I read how milestones are created
  Then it names `new-milestone` (first, active) and `new-milestone --queued` (the rest) and `activate` to promote

Scenario: the intake floor is preserved
  Given the Roadmap section
  When I read who creates the milestones
  Then it states the AI PROPOSES and the human CONFIRMS before any milestone is created   # reject: roadmap_unconfirmed

Scenario: roadmap is distinguished from split_required
  Given intake.md
  When I read the roadmap guidance
  Then it contrasts roadmap (several milestones, same line, queued) with split_required (spans different buckets)

Scenario: glossary defines the new terms
  Given docs/appendix-c-glossary.md
  When I read it
  Then it defines the `queued` milestone status and "roadmap" as the multi-milestone intake artifact

Scenario: convention-only, mirrors in sync
  Given the change set
  When I inspect it
  Then add.py / ENGINE_MD5 are unchanged   # reject: engine_touched
  And intake.md is byte-identical across its 3 trees and the glossary across its 4   # reject: mirror_drift
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONTENT CONTRACT (prose/convention task — the shape of the change)

intake.md  + new "## Roadmap — a request that is several milestones" section
  - WHEN: a request decomposes into N>1 milestones of the same line
  - PROPOSE: the ordered milestone list + one-line goals (AI proposes)
  - ON CONFIRM (human): create the first with `new-milestone`, the rest with `new-milestone --queued`
  - PROMOTE: `activate <slug>` flips a queued milestone to active, one at a time
  - CONTRAST: roadmap (same line, queued) ≠ `split_required` (spans different buckets)

appendix-c-glossary.md  + entries:
  - "Queued milestone" — status active·queued·done; created via new-milestone --queued, promoted via activate
  - "Roadmap" — the multi-milestone intake artifact (1 active + N−1 queued)

SKILL.md  ## Intake — extend the one-liner ONLY if needed to name the roadmap/queued path

INVARIANTS (reject codes):
  roadmap_unconfirmed — the guidance must keep AI-proposes / human-confirms (never auto-create N)
  engine_touched      — add.py / ENGINE_MD5 UNCHANGED (convention-only; engine shipped in task 1)
  mirror_drift        — intake.md ×3 + SKILL.md ×3 + glossary ×4 byte-identical

Lean: core pool (test_skill_lean.py) rebaselined to the new intake.md size (ratio 0.88 kept), not bypassed.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-26); roadmap prose = full `## Roadmap` section
Least-sure flag surfaced at freeze: [spec] full `## Roadmap` section vs a terse bucket-table note. Why most likely wrong: a section grows the tight core lean pool (forces a rebaseline); a one-line note might suffice. Cost if wrong: avoidable rebaseline. RESOLVED by the human at freeze → full section.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every frozen scenario has one assertion (prose/convention task)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_roadmap_section_exists: intake.md has a `## Roadmap` section
  - test_section_names_engine_path: the section names `--queued` + `activate` + "1 active"
  - test_floor_propose_then_confirm: the section says PROPOSE + CONFIRM (roadmap_unconfirmed)
  - test_distinguished_from_split_required: intake.md contrasts roadmap vs split_required
  - test_glossary_defines_terms: glossary defines `queued` + `roadmap`
  - test_intake_mirrored: intake.md byte-identical across its 3 trees (mirror_drift)
  - test_engine_unchanged: ENGINE_MD5 still the task-1 value (engine_touched)
</test_plan>

Tests live in: `test_roadmap_intake_guide.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/intake.md` `add-method/src/add_method/_bundled/skill/add/intake.md` `.claude/skills/add/intake.md` `add-method/skill/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/docs/appendix-c-glossary.md` `appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_roadmap_intake_guide.py`
Strategy (ordered batches): 1. write red `test_roadmap_intake_guide.py` · 2. add `## Roadmap` section to intake.md canonical + glossary entries (canonical) + SKILL.md if needed · 3. propagate intake.md ×3, SKILL.md ×3, glossary ×4 byte-identical · 4. rebaseline core pool in test_skill_lean.py · 5. full suite + confirm ENGINE_MD5 unchanged
Safety rule (feature-specific): convention-only — NO add.py/engine edit (ENGINE_MD5 must stay 8a6440cf…); the roadmap guidance keeps AI-proposes/human-confirms; all mirrors byte-identical.
Code lives in: the guide/book/test paths above (no `./src/`).
Constraints: do NOT change the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2009/0 (+7 new); task suite 7/7 green
- [x] coverage did not decrease — +1 test file (test_roadmap_intake_guide.py, 7 assertions); nothing removed
- [x] no test or contract was altered during build — all test/guide edits happened in the tests phase BEFORE the tests→build snapshot; build phase made no edits (tripwire clean)
- [x] the green was EARNED, not gamed — assertions read the SHIPPED prose (the `## Roadmap` section body via a heading-slice, the glossary terms) + byte-compare the 3 intake.md trees + the engine_pin literal. No vacuous asserts; the section-slice test would pass on a stray keyword elsewhere only if the heading existed (it asserts the heading too).
- [x] concurrency / timing — N/A (static prose/doc edit)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — convention-only; engine untouched (ENGINE_MD5 unchanged); 3-tree skill + 4-tree book parity held; lean fence rebaselined not bypassed
- [ ] a person reviewed and approved the change — pending the gate (contract human-approved at freeze)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] intake.md reads with a `## Roadmap — a request that is several milestones` section that walks propose → confirm → create (1 active + N−1 `--queued`) → promote (`activate`) — confirmed: read the section in add-method/skill/add/intake.md
- [x] the section contrasts roadmap with `split_required` (same line vs different buckets) — confirmed: final paragraph of the section
- [x] the book glossary defines `Queued milestone` + `Roadmap` — confirmed: read appendix-c-glossary.md entries
- [x] engine identity unchanged — confirmed: ENGINE_MD5 still 8a6440cf… (test_engine_unchanged green); git shows no NEW add.py delta beyond task 1
- [x] mirrors in sync — confirmed: intake.md ×3 byte-identical (test_intake_mirrored), glossary ×4 copied, book-parity green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read the new `## Roadmap` section + both glossary entries in full: the propose→confirm→create→promote sequence is correct, names the real commands (`new-milestone --queued`, `activate`), keeps the AI-proposes/human-confirms floor, and the split_required contrast is accurate. No overstated claim.
- [x] WIRING (prose) — the section sits between `## What you emit` and `## Worked examples`; the glossary entries cross-ref `activate`/`new-milestone --queued` consistent with the engine shipped in task 1.

### GATE RECORD
Outcome: PASS
Note: convention-only; engine untouched (ENGINE_MD5 8a6440cf… verified). Lean core pool rebaselined for the human-approved `## Roadmap` surface (+1064 B, ratio kept). No security/concurrency/architecture concern. Task 2 of 3 in multi-milestone-intake.
Reviewed by: Tin Dang (contract approved @ freeze; verify auto-gated on complete evidence under autonomy:auto) · date: 2026-06-26

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
