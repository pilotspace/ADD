# PLAN: Creating a task shows the invariants it inherits, without a second store

slug: invariant-inherit · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: creating a task with `--depends-on` shows the invariants it inherits from its ancestors — a VIEW over the existing graph, with no second store.
Framings weighed: read each ancestor's §3 fresh at `new-task` and print the transitive closure, attributed to its owner (chosen — `graph --signals` already settled this project's answer that the graph is a VIEW not a store, and an invariant read fresh from the node that owns it cannot drift) · copy inherited invariants into the new task's PLAN.md (rejected — the copy is what the builder reads, and it silently disagrees with the ancestor the moment that ancestor changes; this is the failure mode the whole no-second-store rule exists to prevent) · a `state.json` inherited-invariants key (rejected — same drift, plus it must now be migrated, repaired, and kept consistent by every verb that touches edges)
Must:
<must>
  - `new-task --depends-on <a>` prints each invariant `a` publishes, attributed to the node that owns it
  - inheritance is TRANSITIVE: an invariant published by a grandparent binds too
  - it is a VIEW — nothing is copied into the new task's PLAN.md and no new key enters state.json
  - it degrades quietly: an ancestor whose PLAN.md is missing or unreadable contributes nothing and never blocks the new task, and an empty inheritance prints NOTHING at all
</must>
<reject>
  - none — this surface only READS. A `--depends-on` naming an unknown task already refuses upstream through the existing edge validation, and adding a second refusal here would make a broken neighbour block a healthy new node -> "none (read-only view)"
</reject>
After:
<after>
  - a published invariant has a consumer, which is what makes publishing one worth doing
  - a builder starting a task knows what it must not break before writing a line
  - the ancestor's PLAN.md stays the single owner of its own invariants
</after>
Boundary: input is the existing `depends_on` edge set in state.json plus each ancestor's `.add/tasks/<slug>/PLAN.md` §3; a missing, unreadable or non-UTF-8 ancestor doc is treated as publishing nothing. No new input shape.
<assumptions>
  ⚠ the full transitive closure is the right depth rather than direct parents only — if wrong (a deep graph prints a wall of inherited text at every `new-task`): the closure is computed in one place and capping it to N hops, or to direct parents, is a one-line change with no stored data to migrate; cost = one edit.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract

```
add.py :: _inherited_invariants(root, state, deps) -> list[tuple[str, str]]
  walks the TRANSITIVE depends_on closure of `deps` (cycle-safe: a visited set)
  reads each ancestor's §3 via _published_invariants
  -> [(ancestor_slug, invariant_text), ...] in a stable order, deduped
  fail-soft: an unreadable/missing PLAN.md contributes [] and never raises

cmd_new_task
  after the "linked to milestone ... depends-on [...]" line:
    rows := _inherited_invariants(root, state, depends_on)
    rows non-empty -> print "inherits (must not break):" then one attributed row each
    rows empty     -> print NOTHING
  writes NOTHING extra: not to PLAN.md, not to state.json
```
Ground: `add-method/tooling/add.py::cmd_new_task` — `depends_on = _parse_deps(...)`, and when no explicit edge is given it falls back to the milestone's compiled `planned` map, so the view must read the RESOLVED `depends_on` and not the raw flag. Its print surface is `created task '<slug>' -> <path>` followed by `linked to milestone '<m>'` + `, depends-on [...]`; the new rows belong immediately after that pair and before the `active task set. phase: direction.` line. `_published_invariants(raw3)` is the PURE reader shipped by `invariants-publish`, and `_phase_spans(text).get(3, "")` is how §3 is read everywhere. `state["tasks"][slug]["depends_on"]` is the stored edge set that `graph`/`locate` already walk. `.add/PROJECT.md` `invariants:` remains the project-wide layer and is deliberately untouched — this is the per-node counterpart.

Target (measurable): the new suite is RED before and GREEN after; a 3-node chain c->b->a surfaces a's invariant at c; the new task's PLAN.md and state.json both contain NO copy of any inherited text; deleting an ancestor's PLAN.md leaves `new-task` exiting 0; a task with no invariants to inherit prints no header at all; `add-method/tooling/` (2892 green) stays green.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/tooling/` `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Regression floor: `add-method/tooling/` — the whole method suite; `test_min_pillar.py` in particular exercises `new-task` under a read-spy and will catch any accidental docs/ read or extra write, and `test_tree_parity.py` holds the four-twin mirror + the `engine_pin` re-aim.
Persona (optional): `.add/personas/tdd-verifier.md`.

Least-sure flag surfaced at freeze: [spec] printing the FULL transitive closure. On this repo's own graph the depth is 2-3 and the output is a few lines, but a long dependency chain would print a wall of inherited text at every `new-task` — exactly the per-turn output cost the `engine-output-trim` milestone spent a whole cycle removing. I am shipping the full closure because a silently-truncated inheritance is worse than a verbose one (you cannot act on what you were not shown), and because the cap is a one-line change over a computed view with no stored data to migrate. If real use shows it is noisy, cap it and say so in the output.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_new_task_prints_an_ancestors_published_invariant: b --depends-on a surfaces a's invariant · covers: M1  [GATED]
  - test_the_view_attributes_each_invariant_to_its_owner: the row names the owning node · covers: M1  [GATED]
  - test_inheritance_is_transitive: c->b->a surfaces a's invariant at c · covers: M2  [GATED]
  - test_nothing_is_copied_into_the_new_plan: the new PLAN.md contains no copy · covers: M3  [GATED]
  - test_no_new_state_key: state.json contains no copy · covers: M3  [GATED]
  - test_missing_ancestor_doc_is_fail_soft: a deleted ancestor PLAN.md leaves new-task at exit 0 · covers: M4  [GATED]
  - test_several_invariants_all_surface: a multi-entry block surfaces every row · covers: M1  [edge]
  - test_ancestor_with_no_invariants_prints_nothing: no header when there is nothing to show · covers: M4  [edge]
  - test_no_depends_on_prints_nothing: a solo task prints no header · covers: M4  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated.

Build-guidance (prose, not gated): the closure walk must carry a visited set — a `--relates-to` cycle elsewhere in this engine has already proven the graph is not guaranteed acyclic. Keep `_inherited_invariants` free of printing so it can be tested directly.

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned for the view itself — a pure `_inherited_invariants` walking the transitive closure with a visited set, printed by cmd_new_task and stored nowhere. The placement was NOT as planned and cost a real regression: the loop first landed between the `if milestone:` body and its `else:`, which binds the else to the FOR, so the orphan nudge fired on every task that HAD a milestone. It now sits after the whole if/else with a comment stating why. Direction bundle authored by `add.py draft --from … --run-red --freeze --cross`.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) `test_nothing_is_copied_into_the_new_plan` and `test_no_new_state_key` assert the ABSENCE of the invariant text in both stores — the view claim is measured on disk, not asserted in prose; (2) `test_inheritance_is_transitive` builds a real 3-node chain, so a first-hop-only implementation fails rather than passing on a 2-node fixture; (3) `test_ancestor_with_no_invariants_prints_nothing` and `test_no_depends_on_prints_nothing` are the negative controls that stop an unconditional header passing everything; (4) `test_missing_ancestor_doc_is_fail_soft` deletes the ancestor's PLAN.md and requires exit 0. TWO defects of mine were caught by guards I did not write: `test_v8_1_orphan_guard` caught the for/else binding, and `test_ci_tooling_mirror_gap`'s nested fresh-checkout run caught that the sibling task's template guard demanded gitignored dogfood twins exist — the second had ALREADY gated, so it is recorded as a post-gate repair plus a TDD delta rather than quietly amended. NOT claimed: that the full transitive closure stays readable on a deep graph — the §3 flag says so and names the one-line cap.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose read each ancestor's §3 fresh at `new-task` and print the transitive closure, attributed to its owner; rejected copy inherited invariants into the new task's PLAN.md (rejected — the copy is what the builder reads, and it silently disagrees with the ancestor the moment that ancestor changes; this is the failure mode the whole no-second-store rule exists to prevent) · a `state.json` inherited-invariants key (rejected — same drift, plus it must now be migrated, repaired, and kept consistent by every verb that touches edges)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned for the view itself — a pure `_inherited_invariants` walking the transitive closure with a visited set, printed by cmd_new_task and stored nowhere. The placement was NOT as planned and cost a real regression: the loop first landed between the `if milestone:` body and its `else:`, which binds the else to the FOR, so the orphan nudge fired on every task that HAD a milestone. It now sits after the whole if/else with a comment stating why. Direction bundle authored by `add.py draft --from … --run-red --freeze --cross`.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
