# PLAN: Intake/scope loads a fitting persona before shaping the milestone

slug: persona-at-intake · created: 2026-07-24 · stage: mvp
milestone: strategy-intake
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: intake.md gains a "load the fitting persona FIRST" step so the persona shapes the analyze→interview→size work — delivering on the claim SKILL.md:88 already makes, mirroring design.md's load-or-seed pattern.
Framings weighed: extend intake.md with a persona-load step mirroring design.md:20 (chosen — SKILL.md:88 ALREADY claims "at each decision point (intake · …) the fitting persona OWNS the gate report", and design.md has the proven load-or-seed mechanism; the gap is that intake.md, the guide that RUNS intake, never loads one — so today a persona owns the intake REPORT via gate-udd but nothing loads one to shape the SIZING) · a new engine verb that auto-selects a persona at intake (rejected — the engine never spawns or selects personas; selection is skill-guided everywhere else, and an engine route would break that invariant)
Must:
<must>
  - M1 intake.md instructs loading the fitting persona BEFORE the analyze/interview/size work — not after, and not only at the report
  - M2 the load step mirrors the established mechanism: match a persona by role/flow in `.add/personas/`, else seed from `.add/personas-teacher/` via the add agent in persona mode, then load — never invent a new selection path
  - M3 the persona is advisory at intake exactly as everywhere else — it shapes framing/sizing but NEVER lowers the ask_human floor, the frozen-scope tie-break, or the security escalation
  - M4 all three skill trees carry byte-identical intake.md
</must>
Reject:
<reject>
  - an intake persona step that gates or blocks sizing on persona presence -> "persona_blocks_intake"
  - a persona-load path at intake that diverges from design.md's match-else-seed mechanism -> "divergent_selection"
</reject>
After:
<after>
  - a project WITH a fitting persona has its intake analysis/sizing shaped by that persona's expertise
  - a project WITHOUT one still completes intake unchanged (seed is offered, never required) — the personas-less path stays green
Boundary: a persona is present in TWO states the guide must handle — a `.add/personas/*.md` that matches by role/flow, and NONE present (seed-or-proceed); intake must never hard-depend on the first.
<assumptions>
  ⚠ the persona's home at intake is intake.md alone — if the sizing decision is ALSO shaped elsewhere (e.g. an engine nudge at new-milestone, test_persona_milestone_nudge), the guide edit covers the human-facing path but the nudge wording may need to point at intake too; mitigated because the nudge is additive stdout, not a gate
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Artifact: add-method/skill/add/intake.md  (+ 2 byte-identical twins)

New section, inserted AFTER the title/intro and BEFORE "## Analyze the request
before you size it" (so the persona is loaded before the first shaping step):

  ## Load the fitting persona first
  Intake is a decision — size it WITH the project's expertise, not generically.
  Before you analyze or size, load the fitting persona (the PM/product-direction
  lens), exactly as design.md loads the design-fit persona:
    - match a persona in `.add/personas/` by role/flow (frontmatter, else
      description-match) — e.g. a product-lead / method-product-owner lens;
    - NONE fits? seed from `.add/personas-teacher/` via the add agent in persona
      mode, then load — offered, NEVER required;
    - the persona shapes the framing, the latent-requirement read, and the
      sizing tradeoffs. It is ADVISORY: it never lowers the ask_human floor, the
      frozen-scope tie-break, or the security-always-escalates rule.
  No fitting persona and none seeded? Proceed generically — intake still runs.

Cross-references made consistent:
  - the persona already OWNS the intake report (SKILL.md:88, gate-udd.md); this
    step makes it own the SIZING too, so the two agree.

Twins (byte-identical): add-method/skill/add/intake.md ·
  add-method/src/add_method/_bundled/skill/add/intake.md · .claude/skills/add/intake.md
NOT changed: no engine module, no template, no pin, no SKILL.md byte change.
```

Grounding anchors (verified in-context): intake.md structure (title → "## Analyze the request before you size it" at L7 → "## Interview before you size" L26 → sizing L54+) · design.md:18-26 the load-or-seed pattern to mirror · SKILL.md:88 the existing "intake · … persona OWNS" claim · test_persona_milestone_nudge PERSONA_HINT (additive stdout, not a gate) · 3 skill trees confirmed present.

Target (measurable): intake.md gains exactly ONE persona-load section, positioned before "## Analyze" · the personas-less intake path stays green (test_persona_milestone_nudge + any intake tests unchanged) · 3 trees byte-identical · new content-guard green after / red before · full tooling suite stays green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/skill/add/intake.md` `add-method/src/add_method/_bundled/skill/add/intake.md` `.claude/skills/add/intake.md` `add-method/tooling/test_persona_at_intake.py` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` — specifically test_persona_milestone_nudge (the personas-less path must stay green) and any intake content tests — must stay green.
Persona (optional): `.add/personas/method-product-owner.md` — the PM lens this task is itself about; fitting because the change IS about intake-as-a-PM-decision.

Strategy (preferred, not hard): write the content-guard first (asserts the load step exists, is positioned before "## Analyze", names the match-else-seed mechanism, and carries the advisory/floor caveat) proven red; add the section to the canon intake.md; mirror byte-identical to the 2 twins; re-run green + confirm the personas-less nudge path still passes.

Least-sure flag surfaced at freeze: [spec] whether a persona at intake is genuinely load-bearing or is ceremony. design.md's persona clearly shapes a UI (visual systems, component states); a PM persona shaping "which bucket" is softer — the four buckets are mechanical enough that a persona may add little beyond the framing. Argument FOR: sizing/latent-requirement extraction (intake.md L14-19) IS expertise-shaped, and the milestone goal explicitly wants the persona as the PM brain — so the criterion is the spec, not my doubt. Chosen: ship the load step as ADVISORY (proceed-generically path kept) so it adds zero cost when no persona fits and real shaping when one does — the risk-proportional design the milestone itself argues for.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_intake_loads_persona_before_analyze: intake.md has a persona-load heading positioned before "## Analyze the request" · covers: M1
  - test_load_step_mirrors_match_else_seed: the step names matching `.add/personas/` AND seeding from `.add/personas-teacher/` · covers: M2, R:divergent_selection
  - test_intake_persona_is_advisory: the step states the persona never lowers ask_human / frozen-scope / security · covers: M3, R:persona_blocks_intake
  - test_intake_twins_identical: intake.md byte-identical across all three skill trees · covers: M4
</test_plan>

Kind: method/docs — these assert on SHIPPED GUIDE TEXT (a skill guide that ships in every tree), so they are executable checks over files, not behavioral unit tests. Each runs RED against intake.md as it stands (no persona step today).

M4 (twin parity) starts by construction — the section is written once and mirrored; its red-first duty is discharged by mutation (drop the edit from one tree → red).

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — guard written and proven red (M1/M2/M3) on intake.md as it stood, section added to canon before "## Analyze", mirrored byte-identical to the 2 twins (md5 41cf6549… ×3). One self-inflicted detour: my twin-mutation probe used a cwd-relative path that resolved wrong and briefly clobbered a twin + its backup; caught immediately (M4 went red as designed — which incidentally PROVED the parity check has teeth), restored all three from canon, re-verified md5-equal. Separately, a bare `unittest test_persona_milestone_nudge` from the add-method dir raised ModuleNotFoundError('add') — a path-harness artifact of the wrong invocation, NOT a regression; it passes 15/15 under CI's `unittest discover -s tooling`.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — FULL suite via CI's runner: **2293 tests, OK, exit 0** (208s), up from 2289 by this task's 4; guard 4/4; test_persona_milestone_nudge 15/15 via `discover` (the personas-less path)
- [x] coverage did not decrease — additive; only intake.md prose + one new test file
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unedited; guard written in direction, untouched after freeze; the mutation probe was reverted (git-clean)
- [x] the green was EARNED, not gamed — M1/M2/M3 red-first on the real file; M4 mutation-proven (a clobbered twin turned it red, restore returned green); the advisory-caveat check (M3) reads the persona SECTION specifically, not the whole file, so it can't pass on incidental "security" prose elsewhere
- [x] concurrency / timing — n/a, prose guide + read-only tests
- [x] no exposed secrets, injection openings, or unexpected dependencies — no dependency, no code path; a skill-guide edit
- [x] layering & dependencies — guard in `tooling/test_*.py` (CI's discover pattern); no engine/template/pin touched, so no twin/pin ritual beyond the 3 skill trees
- [x] a person reviewed and approved the change — Tin Dang approved the freeze (Freeze & build), having seen the exact section text and the least-sure [spec] flag

TARGET — met: exactly ONE persona-load section, positioned before "## Analyze" ✓ · personas-less path green (nudge 15/15) ✓ · 3 trees byte-identical (md5 ×3 equal) ✓ · guard red-before/green-after ✓ · full suite green (2293 OK) ✓. Delivers milestone exit-criterion "Intake/scope loads a fitting persona before shaping" → 5/8.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) the [spec] doubt — is a PM persona at intake load-bearing? — was resolved by DESIGN not assertion: the step is advisory with a proceed-generically path, so it adds zero cost when no persona fits and real shaping when one does; the milestone criterion is the spec, my doubt is recorded not suppressed; (2) M3's "advisory" check was scoped to the persona SECTION (heading-to-next-heading) so it can't be satisfied by the pre-existing "security · HARD-STOP" prose already in intake.md's inline-lane section — a real risk of a false green I closed deliberately; (3) the personas-less regression was verified POSITIVELY (nudge 15/15), not merely assumed from "additive".

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — guard written and proven red (M1/M2/M3) on intake.md as it stood, section added to canon before "## Analyze", mirrored byte-identical to the 2 twins (md5 41cf6549… ×3). One self-inflicted detour: my twin-mutation probe used a cwd-relative path that resolved wrong and briefly clobbered a twin + its backup; caught immediately (M4 went red as designed — which incidentally PROVED the parity check has teeth), restored all three from canon, re-verified md5-equal. Separately, a bare `unittest test_persona_milestone_nudge` from the add-method dir raised ModuleNotFoundError('add') — a path-harness artifact of the wrong invocation, NOT a regression; it passes 15/15 under CI's `unittest discover -s tooling`.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] intake.md now loads the fitting persona; the NEXT task in the chain (strategy-guide) can assume that persona is already loaded when it drives the discuss→optimize→converge loop — it should not re-select (evidence: this task delivers exit-criterion "Intake loads a fitting persona"; strategy-guide depends-on persona-at-intake)
- [SPEC · open] the new-milestone engine nudge (test_persona_milestone_nudge / PERSONA_HINT) points at add-persona/docs but NOT at intake.md's new load step — wording could name intake as the load point so the human-facing guide and the stdout nudge agree (evidence: §1 ⚠ flagged this; nudge is additive stdout, low-priority)

### Competency deltas
- [ADD · open] a persona at intake is worth shipping ONLY as advisory-with-a-generic-fallback — the risk-proportional design keeps it zero-cost when no persona fits, which is the same shape design.md uses; a blocking persona-load would have contradicted the milestone's own "personas REMOVE ceremony" thesis (evidence: proceed-generically path kept; nudge path stayed green)
- [TDD · open] scope a "must contain X" content check to the RELEVANT SECTION, not the whole file — M3 checking the whole intake.md for "security" would have passed vacuously on the pre-existing inline-lane HARD-STOP prose; heading-to-next-heading slicing made it actually test the persona step (evidence: intake.md already contained "security" before this task)
- [ADD · open] a cwd-relative path in a throwaway mutation probe is a foot-gun — mine clobbered a twin AND its backup by resolving against the wrong dir; the recovery was clean only because canon was untouched and byte-identical twins are trivially restorable by cp (evidence: M4 briefly red mid-verify, restored from canon, md5-equal). Prefer absolute paths in scratch probes.
- [ADD · open] running one test as a bare module (`unittest tooling.test_x`) can raise a false ModuleNotFoundError('add') that `unittest discover -s tooling` does not — always confirm a "regression" under CI's actual invocation before believing it (evidence: nudge test errored bare, passed 15/15 via discover)
