# MILESTONE: Persona domain-fit nudge

goal: a new milestone/task whose domain doesn't fit any existing project persona gets a concrete nudge to draft a fitting one, not just a one-time zero-personas nudge
rationale: sub-milestone of the long-running persona system (persona-setup seeds at project setup ·
  persona-seed-nudge nudges once when ZERO real personas exist · persona-self-improve grows an
  existing persona from usage) — this is the missing NEXT slice: once ≥1 real persona exists, nothing
  checks whether a NEW milestone/task's domain is actually covered by one. Grounded directly against
  ai-proxy's own repo (a separate, real ADD project): it already has 8 real, git-tracked personas
  (backend-architect, appsec-engineer, ux-researcher, billing-precision-engineer, frontend-engineer,
  ui-designer, protocol-translation-engineer, sre-reliability-engineer) — so the reported "missed
  personas folder" is NOT a literal missing-file bug (worktrees inherit git-tracked personas fine);
  the real gap is domain drift: a new milestone (e.g. a "batch-cache" theme) landing with no
  fitting persona among the 8, and no engine surface flagging that mismatch the way
  persona-seed-nudge flags a total absence. AskUserQuestion timed out twice on sizing/priority during
  intake; proceeded on project-lead judgment (Rule 2), fully disclosed. NOTE: the second half of the
  original request — "optimize ADD SKILL.md" / distill design-flow rules into personas — is
  DELIBERATELY OUT of this milestone (see Scope Out) pending human confirmation, since direct
  inspection found SKILL.md already lean (192 lines, a pure phase-guide router under progressive
  disclosure) — the real distillation target, if any, would be the phase guides themselves, a
  materially bigger and separately-sized ask.
stage: mvp · status: active · created: 2026-07-05T03:21:03+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  extend the existing persona-absence nudge (persona-seed-nudge's `new-milestone`/`check`/`status`
  surfaces) with a lightweight DOMAIN-FIT heuristic — when ≥1 real persona already exists but none
  plausibly covers the NEW milestone's stated goal/domain, print the same class of non-blocking hint
  (name the concrete fix: spawn/consult `add-persona`, or read `docs/18-personas.md`) rather than
  staying silent just because SOME persona exists. NO-EXEC + content-quality judgment stays the AI's
  job (mirrors persona-seed-nudge's own v1/v2 framing) — the engine only ever measures/hints, never
  judges fit or auto-drafts.
Out: (1) teaching the engine to auto-judge domain fit with certainty or auto-draft a persona — same
  rejection as persona-seed-nudge, content judgment is the AI's job; (2) distilling SKILL.md/phase-guide
  prose into persona-delegated content ("optimize ADD SKILL.md") — deferred pending human confirmation;
  SKILL.md itself was found already lean on inspection, so this needs its own sized investigation
  (likely into the phase guides, not SKILL.md) before it becomes a task; (3) any change to the
  persona schema/template (`_template.md`, the 4 required sections) — out of scope, this milestone
  only adds a NEW nudge surface, never touches persona file shape.

## Shared decisions & glossary deltas   (living — every task must honor these)
- "domain fit" is judged by the AI reading PROJECT.md's domain + the new milestone's own goal against
  each persona's own stated domain stance — NOT a keyword-matching heuristic in the engine; the engine
  only ever detects "an unconfirmed nudge is due" (a structural/measurable predicate), never "which
  persona is the right one" (a content judgment, same separation persona-seed-nudge already draws)

## Shared / risky contracts (freeze these first)
- the domain-fit nudge predicate (what the engine can measure vs. what stays AI judgment) -> owning task persona-fit-nudge

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] persona-fit-nudge   depends-on: none   — extend `new-milestone` (+ `check`/`status`, mirroring persona-seed-nudge's 3 surfaces) to hint domain-fit review even when ≥1 real persona exists, never just the zero-persona case

## Exit criteria (observable; map each to the task that delivers it)
- [x] a fresh milestone whose goal shares no domain vocabulary with any existing real persona prints a
  domain-fit hint naming `add-persona`/docs/18-personas.md — byte-identical output otherwise (no
  regression for an already-fitting project)  (verify: `test_persona_fit_nudge.py`, 8/8 green;
  full suite 2967/2967 green)        (← persona-fit-nudge)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` gains a new `elif` branch in `cmd_new_milestone`; `add_engine/constants.py` gains
  `PERSONA_FIT_HINT_TEMPLATE`; `add_engine/io_state.py` gains `_real_persona_slugs`; mirrored
  byte-identical across the 3 engine trees; `ENGINE_MD5`/`ENGINE_PKG_MD5` re-aimed; `.add/SEAMS.md`
  anchor line-number corrected (unrelated line-shift side-effect)
- skill   : untouched
- book    : untouched

### Cross-task evidence   (one row per task)
- persona-fit-nudge : gate=PASS · tests=8 new green (2967/2967 full suite) · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — the sole exit criterion is satisfied by the persona-fit-nudge row above
- goal: a new milestone/task whose domain doesn't fit any existing project persona gets a concrete
  nudge to draft a fitting one — met: `new-milestone` now prints `persona-fit:` naming existing
  persona slugs + the add-persona fix path whenever ≥1 real persona exists, mutually exclusive with
  the pre-existing zero-persona `note:` hint (test_persona_fit_nudge.py, all 8 scenarios green)

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit the change (tmp/{name}.txt commit-message convention, then `git commit -F`)
- [ ] ask the human for PR-creation permission before opening one
- [ ] bundle into the next release cut alongside the other loose 2026-07-05 tasks (`add.py release`,
  human-run tag/publish)
