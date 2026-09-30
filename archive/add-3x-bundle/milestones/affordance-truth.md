---
type: Milestone
title: The engine's affordances name the beat you are actually on
status: done
generated: { by: add/3.2.0, at: 2026-08-17 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: check, authority: process, via: process, boxes: "EXIT:1,2,3,4,5,6,7" }
---
## CARD
goal: Make every `next:` the engine prints name a verb that can actually succeed against the node it names, so a node that was created and never authored is visible as such instead of reading identical to one that is ready for approval.
why: `direction.md` states the design plainly — "There is **no author verb** — you fill those sections by
  editing that file directly". The engine's affordances never learned it. `BEAT_NEXT["direction"]` maps the
  whole beat to `add freeze {slug}`, so from the moment `add new Task` writes a file of placeholders, five
  separate surfaces tell you to freeze it — and `freeze` is structurally guaranteed to refuse it
  (`add.py:1260`). The authoring beat is the only transition in the loop with no verb, no stamp, and no
  affordance, so `status: direction` and `verified: []` read identically before and after the work that
  matters most. Observed live: in `yoma-org/em-monorepo`, MS32 t2 `queue-adapter-truth` sat as an untouched
  scaffold from 2026-08-14 to 2026-08-17 while `add status` reported `next: add freeze queue-adapter-truth`
  and `add todo` printed `→ add freeze queue-adapter-truth  (gives: unauthored — no surfaces to sweep)` — a
  line that detects the condition and recommends the refusal in the same breath. This bundle carries the
  same defect: `v3-final-collateral` has been the active milestone since 2026-08-11 with `goal: <one line>`
  still in it, and `add new Milestone affordance-truth` answered with `next: add freeze affordance-truth`
  before a single word was authored.
  Probing that last case found the harder half. On Milestones the bad advice does not get refused — it
  SUCCEEDS. `add new Milestone probe-ms` then `add freeze probe-ms` returns `freeze recorded at authority
  process` with every section still template, because `placeholders_in` reads only RULES · ASSUMPTIONS ·
  CHECKS and a Milestone body has none of them. The guard is Task-only by construction and silently
  vacuous on the other lifecycle type, so the method's one human approval can be stamped against a node
  that states no goal, no scope, no risk and no exit criterion.
next: add freeze authoring-beat-named

## SCOPE
In:  BOTH directions of the same seam, one task each.
     ENGINE (← authoring-beat-named): the `next:` affordance wherever the engine derives it for a Task
     or Milestone in the `direction` beat — `BEAT_NEXT` and its readers (`status`, `todo`, `new`, the
     `## CARD` scaffold in `BODIES`, `brief`'s refusal); the predicate that separates a scaffold from an
     authored node at ADVICE time, which today exists (`placeholders_in`, `gives_unauthored`) but is
     consulted only inside REFUSALS; the Task-only placeholder guard that stamps a Milestone scaffold;
     the engine tests that pin the current affordance string.
     SKILL (← claimed-output-guard): every skill-tree sentence claiming a command SHOWS or PRINTS
     something, bound to a driven proof that it does — plus the two `loop.md` claims that have none.
Out: No new verb. `direction.md` rules deliberately against one ("the engine records; it never writes the
     method for you") and inventing `add draft` would re-open a closed design decision — this milestone
     changes what the engine SAYS, never what it does on the author's behalf. No change to any refusal:
     `freeze` and `gate` already catch placeholders correctly and their messages are already right; this
     moves that knowledge EARLIER, it does not restate it. No change to `status:` frontmatter values —
     splitting the enum would ripple through every bundle in the wild and through `add upgrade`; the beat
     is DERIVED, exactly as `_is_frozen` already derives the next one. No `doctor` triage of the
     `missing_frontmatter` noise (17 findings on legitimate task sub-documents) — real, separate, and not
     this milestone's claim.

## GROUND
touches: add-method/tooling/add.py (BEAT_NEXT:1468 · BODIES["Task"]:1092 · new:1242 ·
  status frontier verb:1777 · brief refusal:2673 · placeholders_in:2249 · gives_unauthored) ·
  add-method/tests/engine/test_new_scaffold.py:20 · add-method/tests/engine/test_persona_scaffold.py ·
  add-method/tooling/engine_pin.py · add-method/conftest.py · add-method/tooling/test_tree_parity.py ·
  add-method/tests/skill/test_run_completeness.py
risks:
  - `tests/engine/test_new_scaffold.py:20` asserts the literal string `"next: add freeze mul-fn"`. The
    affordance was hardened once to name the right SLUG and in doing so froze the wrong VERB — the test
    now pins the defect as an interface. Re-aiming it is part of the fix, not collateral damage, and it
    must be re-aimed deliberately rather than deleted.
  - Any `add.py` edit re-aims `ENGINE_MD5`, and the engine has four live twins that must move together:
    `add-method/tooling/`, `add-method/src/add_method/_bundled/tooling/`, `add-method/.add/tooling/`, and
    this bundle's gitignored `.add/tooling/`. A one-tree edit ships a mirror gap that CI catches late.
  - `status` holds `graph[f0]["fm"]` but not the node BODY, so deriving the beat needs a `read()` the
    frontier path does not do today. `status` was measured 4.3x faster in the 3.1 perf pass; one extra
    single-file read is the cost, and it should be measured rather than assumed negligible.
  - The two test roots both run in CI — `add-method/tests/` and `add-method/tooling/` (which owns the
    MD5 pins). Running one and shipping is how a red branch has gone out before.
  - This changes what an agent is TOLD to do next, so it changes agent behaviour in every downstream
    bundle. A wrong new string is worse than the current wrong string, because the current one at least
    fails loudly at `freeze`.
  - The skill half has an obvious wrong turn: making the two false `loop.md` claims TRUE by adding the
    missing `status` lines. That is a real improvement and a separate task — taken here it would ship a
    guard that has never once refused anything, which is indistinguishable from a guard that cannot.
    Adding a `goal not met (m/n exit criteria)` line to `status` is the candidate third task; it is
    deliberately NOT in this milestone.
  - Three live skill trees, not two: `.claude/skills/add/`, `add-method/skill/add/` and
    `add-method/src/add_method/_bundled/skill/add/`. Both false claims are in all three. Missing one
    fails at publish, late.

## EXIT
- [x] A Task or Milestone that still carries template placeholders is never advised to `freeze` by any
      surface that CAN read its body — `new`, `todo`, the CARD scaffold and `freeze` itself — proven by a
      test per surface and not by reading the diff. `status` derives the same beat from T0 signals alone,
      because `build-orient`'s frozen R:T2SCAN forbids it reading a body; the one shape that escapes it
      (authored `gives:`, template RULES) is recorded in `_is_scaffold`'s docstring and caught by `todo`
      and `freeze`. AMENDED 2026-09-01: the original wording said "every surface", which no surface bound
      by R:T2SCAN can satisfy   (← authoring-beat-named)
- [x] The advice-time predicate is the SAME one the refusals use, so a node the engine advises to freeze
      is a node `freeze` accepts — no third notion of "authored" enters the engine   (← authoring-beat-named)
- [x] `test_new_scaffold.py`'s pinned affordance string is re-aimed at the corrected verb rather than
      dropped, so the scaffold's `next:` stays a pinned interface   (← authoring-beat-named)
- [x] `freeze` refuses a Milestone whose CARD `goal:`, CARD `why:` or `## EXIT` criteria are still
      template, proven by a check that is red against today's engine — which records the stamp. AMENDED
      2026-09-01: narrowed from CARD · SCOPE · GROUND · EXIT to the three the milestone lifecycle
      actually reads, since `milestone_done` refuses on `why:` and on the EXIT tally, and a guard
      reaching SCOPE and GROUND would refuse real milestones whose ground is thin   (← authoring-beat-named)
- [x] All four engine twins carry the change and the MD5 pins are re-aimed; both test roots green
      (← authoring-beat-named)
- [x] Every skill-tree sentence claiming a command shows or prints something is proven by DRIVING that
      command and reading its stdout — a string found in `add.py` satisfies nothing, since that is
      precisely what let `goal not met (m/n exit criteria)` survive   (← claimed-output-guard)
- [x] The two false `loop.md` claims are repaired in all three live skill trees, and the guard is shown
      RED against the unrepaired tree first — a guard that never refused is not evidence
      (← claimed-output-guard)

## CLOSE
evidence: <one row per task>
