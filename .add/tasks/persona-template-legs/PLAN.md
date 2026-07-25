# PLAN: Name the four persona legs and define the Escalation section

slug: persona-template-legs · created: 2026-07-25 · stage: mvp
kind: docs
milestone: persona-template-completeness
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the persona authoring contract names four legs — Role · Process · Standards · Rules — over the sections that already exist, gives each leg a checkable quality bar, states which surfaces load `## Abilities`, and defines an OPTIONAL `## Escalation` section that a retrospective delta can route into.

Framings weighed: vocabulary-over-existing-sections (chosen — the legs are a reading aid plus a bar, so the 6 real personas, 12 presets, `constants.PERSONA_REQUIRED_SECTIONS`, the book, and the benchmark fixtures all keep working untouched) · rename-the-sections-to-the-four-legs (rejected — a breaking edit across five surfaces that buys no behavior change; `_persona_missing` matches `## Identity` literally).

Must:
<must>
  - M1: `contract.md` names all four legs, each mapped to the existing `## Section` header(s) it covers.
  - M2: each leg carries a quality bar an author can check before finishing — including Process, which has none today.
  - M3: `contract.md` documents `## Escalation` in its Sections list as OPTIONAL, stating its purpose (the stop-condition this lens refuses to proceed past) and that a persona delta can route into it.
  - M4: the `## Abilities` entry states its load contract — which apply-surfaces read it — instead of standing as a bare RECOMMENDED bullet.
  - M5: `patterns.md` gains an Escalation-stance pattern, and its Contents list tags each pattern with the leg it fills.
  - M6: every file this task touches is byte-identical across the three skill trees.
</must>
Reject:
<reject>
  - an edit landing in `add.py` or `add_engine/*` (promoting a section into the engine schema) -> "engine_scope_violation"
  - a leg introduced by renaming an existing `## Section` header rather than mapping onto it -> "section_rename"
  - a skill tree left diverged from its twins after the edit -> "mirror_gap"
</reject>
After:
<after>
  - an author reading `contract.md` can name which section each leg lives in and check each against a stated bar.
  - a retrospective can file a persona delta hinting `Escalation` and the fold has a documented target section.
  - the engine schema is unchanged: `add.py check` reports the same persona findings as before this task.
</after>
Boundary: none — no external input; the artifacts are markdown files under three mirrored skill trees.
<assumptions>
  ⚠ that `## Abilities` should be KEPT and surfaced rather than cut — if wrong: tasks 2 and 4 carry an Abilities section into 12 presets × 3 trees plus 2 book twins that a later fold must strip back out (~38-file re-edit).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
ARTIFACT references/contract.md   (the hard schema an author reads first)
  + "## The four legs"   -> table: leg | section(s) it covers | quality bar
        Role      -> ## Identity
        Rules     -> ## Critical Rules
        Standards -> ## Default Requirement + ## Success Metrics
        Process   -> ## Abilities + ## Playbook
  ~ "## Sections"        -> the Abilities bullet gains its load contract (which
                            surfaces read it); OPTIONAL gains `## Escalation`
                            with purpose + "routable by a persona delta hint"

ARTIFACT references/patterns.md   (the judgment layer that fills the schema)
  + pattern 12 "Escalation stance" -> what makes this lens STOP, distinct from
                                      a Critical Rule (always-do) and an
                                      Anti-pattern (guilty-until-proven)
  ~ "## Contents"        -> 12 entries, each tagged with the leg it fills

MIRRORS (byte-identical, all three):
  .claude/skills/add/persona-author/references/
  add-method/skill/add/persona-author/references/
  add-method/src/add_method/_bundled/skill/add/persona-author/references/

UNCHANGED (asserted, not assumed): add.py · add_engine/* · ENGINE_MD5 · ENGINE_PKG_MD5
```

Target (measurable): 4/4 legs present in `contract.md`, each with a bar line · `## Escalation` documented OPTIONAL + routable · `patterns.md` Contents = 12 entries, each leg-tagged · `md5` of both touched files EQUAL across all 3 skill trees · `git diff main -- add-method/tooling/add.py add-method/tooling/add_engine/` empty · `add.py check` persona-finding count unchanged from the pre-build baseline (currently 0).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.claude/skills/add/persona-author/references/` `add-method/skill/add/persona-author/references/` `add-method/src/add_method/_bundled/skill/add/persona-author/references/` `./`
Regression floor: `add-method/tooling/test_tree_parity.py` (the 3 skill trees ↔ parity), `add-method/tooling/test_ci_tooling_mirror_gap.py`, and `python3 .add/tooling/add.py check` — all green before the gate.
Persona (optional): `.add/personas/book-technical-writer.md` — the method prose IS the product surface; this task is guidance prose across mirrored doc twins, which is exactly its seam.

Least-sure flag surfaced at freeze: [spec] the keep-and-surface decision for `## Abilities`. It is a settled human choice, but it is the assumption with the largest downstream cost in the milestone: tasks 2 and 4 both write Abilities into artifacts on the strength of it, so a reversal is a ~38-file re-edit rather than a one-file fix.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - check_four_legs: read `contract.md`; assert each of Role · Process · Standards · Rules appears in the legs table, each mapped to a literal `## Section` header that exists in the Sections list. RED now: the string "four legs" occurs 0 times. · covers: M1
  - check_leg_bars: assert every one of the 4 leg rows carries a bar an author can check before finishing (Process included). RED now: no bar exists for Process anywhere in the references. · covers: M2
  - check_escalation_documented: assert `## Escalation` appears under OPTIONAL in the Sections list, with its purpose stated and the word "routable" (or an equivalent explicit note that a persona delta hint can target it). RED now: "Escalation" occurs 0 times. · covers: M3
  - check_abilities_load_contract: assert the `## Abilities` entry names the apply-surfaces that load it, rather than standing as a bare RECOMMENDED bullet. RED now: the entry is one unqualified bullet. · covers: M4
  - check_pattern_escalation: assert `patterns.md` Contents lists 12 entries, that entry 12 is the Escalation stance, and that every Contents entry is tagged with the leg it fills. RED now: Contents lists 11, none leg-tagged. · covers: M5
  - check_mirror_parity: `md5` of `contract.md` and of `patterns.md` is identical across all three skill trees. GREEN now and must STAY green — this is a regression check, red only if the build diverges a twin. · covers: M6, R:mirror_gap
  - check_engine_untouched: `git diff --stat main -- add-method/tooling/add.py add-method/tooling/add_engine/` is empty, and both pin literals in `engine_pin.py` are unchanged. GREEN now and must STAY green. · covers: R:engine_scope_violation
  - check_no_section_rename: `add.py check` reports the same persona-finding count as the pre-build baseline (0), and no `## Identity`/`## Critical Rules`/`## Default Requirement`/`## Success Metrics` header was renamed in any persona or preset. GREEN now and must STAY green. · covers: R:section_rename
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: evidence · MUST run red (the asserted strings absent) before Build.

Non-coding task (`kind: docs`): §4 is a failing-first ACCEPTANCE CHECK set, not a script. Five checks are RED now (verified by probe: `grep -c "four legs\|Escalation"` returns 0 on both reference files); three are standing GREEN regression checks that the build must not break — they are what makes the two Rejects and M6 observable rather than aspirational.

Build-guidance (prose, not gated): keep the legs table above the existing Sections list so an author meets the vocabulary before the schema. Do not restate `patterns.md` content inside `contract.md` — the split (schema vs judgment) is the reason both files are short enough to read.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, with ONE mid-build correction. Edited the canonical tree (`add-method/skill/add/persona-author/references/`) then propagated byte-identically to the two mirrors, verified by md5. The correction: while adversarially checking the M4 claim I opened `agents/add-worker.md` — which §2 instructs to "read the body of the ONE you become" and to "run the persona's lead commands" on load. So `## Abilities` is ALREADY consumed by the roster agent; only the surface DOCS (`docs/18-personas.md`, `design.md`, `phases/verify.md`) omit it from their enumerated load set. The first draft of the M4 sentence asserted a build-overlay load contract that was not yet true; it was rewritten to cite `add-worker.md` (true today) with a parenthetical naming the chapter that lags. This shrinks `persona-docs-truth` from "make it true" to "reconcile the chapter to what the agent already does".
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all §4 acceptance checks pass — 8/8; the 5 red-first checks flipped, the 3 standing regression checks held. Regression floor green: `test_tree_parity` + `test_ci_tooling_mirror_gap` = 15 tests, OK; `add.py check` = 298 passed, 0 failed (91 warnings, down from 92 — `goal_not_auto_ready` closed).
- [x] coverage did not decrease — n/a for a `kind: docs` task; no code paths added or removed.
- [x] no test or contract was altered during build — frozen §3 and the §4 check set are byte-unchanged since the freeze; no tripwire finding at the gate.
- [x] the green was EARNED, not gamed — see the refute-read below; the two load-bearing claims were probed against the engine and the agent file, not asserted from the docs.
- [x] concurrency / timing — n/a; markdown edits, no runtime behavior.
- [x] no exposed secrets, injection openings, or unexpected dependencies — the diff is 6 markdown files; no code, no imports, no CI surface.
- [x] layering & dependencies — mirror discipline held: canonical tree edited, twins propagated, md5-identical across all three (`57403494…` contract, `5970b6a2…` patterns). Engine untouched: `git diff main` on `add.py` + `add_engine/` is empty, both pin literals unchanged.
- [x] a person reviewed and approved the change — Tin Dang, at the verify gate, after the diff and the refute-read findings were rendered

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: the two claims this task ADDS to a reference doc, either of which would make the guidance lie if wrong.
  (1) "`## Escalation` is routable with no engine change" — probed directly rather than reasoned: fed `- [ADD · open · persona:tdd-verifier · Escalation] …` through the real `_DELTA_RE` + `_PERSONA_TAG_RE`; both matched, hint captured as `('tdd-verifier', 'Escalation')`. TRUE.
  (2) "`## Abilities` load contract" — the first draft asserted the build overlay loads it, sourced from three surface docs I had read. Opening `agents/add-worker.md` REFUTED the framing: §2 already instructs the roster agent to read the whole persona body and run its lead commands. The sentence was rewritten to cite the agent (accurate now) instead of a book chapter that lags. This is a `patterns.md` #4 (read-before-you-assert) miss caught by the refute-read, and it is filed as a delta below.
  Residual honestly stated: `docs/18-personas.md` still enumerates a shorter overlay set than the agent reads. `contract.md` names that gap in a parenthetical rather than papering over it; `persona-docs-truth` (the next task, promoted to run second at the freeze gate) closes it.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose vocabulary-over-existing-sections; rejected rename-the-sections-to-the-four-legs (rejected — a breaking edit across five surfaces that buys no behavior change; `_persona_missing` matches `## Identity` literally).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with ONE mid-build correction. Edited the canonical tree (`add-method/skill/add/persona-author/references/`) then propagated byte-identically to the two mirrors, verified by md5. The correction: while adversarially checking the M4 claim I opened `agents/add-worker.md` — which §2 instructs to "read the body of the ONE you become" and to "run the persona's lead commands" on load. So `## Abilities` is ALREADY consumed by the roster agent; only the surface DOCS (`docs/18-personas.md`, `design.md`, `phases/verify.md`) omit it from their enumerated load set. The first draft of the M4 sentence asserted a build-overlay load contract that was not yet true; it was rewritten to cite `add-worker.md` (true today) with a parenthetical naming the chapter that lags. This shrinks `persona-docs-truth` from "make it true" to "reconcile the chapter to what the agent already does".
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
