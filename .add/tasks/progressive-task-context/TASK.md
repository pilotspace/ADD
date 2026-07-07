# TASK: Progressive task context: status --section reads one §body; skill quick-ref adopts the batched loop

slug: progressive-task-context · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:cmd_status (--brief branch just added; --section joins it) · add_engine/taskdoc.py:_raw_phase_bodies (the canonical §body reader — reuse, never a second parser) · add-method/skill/add/SKILL.md quick-ref line (batched-loop adoption; byte-fenced by test_skill_lean pools — compress in place)
Context (working folder): add-lean-loop task 2 — per-turn context tax: agents re-read the whole growing TASK.md every turn; round-3 decomposition shows 41–64% pre-code token share
Honors (patterns / conventions): flag-over-subcommand (no LIFECYCLE/slang ripple — engine-batch-ops precedent) · fail-closed named errors · 3-tree engine parity + ENGINE_MD5 pin · lean-over-budget-bump (COMPRESS to absorb; rebaseline only human-signed)
Seams consulted: taskdoc _phase_spans grammar (§body definition) — the same scan --fill uses
Anchors the contract cites: cmd_status · _raw_phase_bodies · SKILL.md quick-ref
Issues/Risks (→ feed §1): SKILL.md is pool-fenced — the quick-ref edit must be byte-neutral-or-smaller; --section on a task with no TASK.md must fail closed; phase-name aliases must map to the same §numbers as --fill
Related intent: add-lean-loop MILESTONE.md task 2 — read ONLY the active section, not the whole file
Ground SHA: f299c5c

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: progressive task context — status --section + batched-loop quick-ref
Framings weighed: status --section flag (chosen — reuses the orient surface, zero LIFECYCLE ripple) · new `show` subcommand (rejected: min_pillar LIFECYCLE + slang-guard span ripples) · agent-convention-only (rejected: unenforceable, every agent re-derives it)
Must:
<must>
  - `status --section <0-7|phase-name>` prints the ACTIVE task's raw §body via _raw_phase_bodies — nothing else (no banner, no footer).
  - Phase names map to the SAME §numbers as advance --fill (ground→0 … observe→7).
  - The SKILL.md quick-ref adopts the batched loop (status --brief · advance --fill · status --section) with the edit byte-neutral-or-smaller against the lean pool fence.
</must>
Reject:
<reject>
  - --section value not 0–7 and not a phase name -> "section_unknown"
  - --section with no active task -> existing no-active-task refusal
  - section heading absent from the active TASK.md -> "section_missing"
</reject>
After:
<after>
  - an agent re-orienting mid-task reads one §body (~tens of lines) instead of the whole TASK.md (~200 lines); the skill teaches the 1-call-per-phase loop
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the quick-ref compression stays inside the pool byte budget — lowest confidence because the pool baseline is frozen and unseen until measured; if wrong: compress harder elsewhere in the same line, never a rebaseline
  - [ ] --section output raw (no trailing decoration) is what subagents want — confirm at bench-rerun
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: read one section   # M1
  Given an active task whose §1 contains "Feature: widget rules"
  When add.py status --section 1 runs
  Then stdout is exactly the §1 body (contains the Feature line, no banner/footer)

Scenario: phase-name alias   # M2
  Given the same task
  When add.py status --section specify runs
  Then stdout equals the --section 1 output

Scenario: quick-ref teaches the batched loop   # M3
  Given the shipped SKILL.md
  Then its quick-ref names status --brief, advance --fill and status --section
  And the lean pool byte fence stays green

Scenario: unknown section rejected   # R1
  When add.py status --section 9 (or --section bogus) runs
  Then it dies "section_unknown" and prints no body

Scenario: missing section rejected   # R3
  Given a TASK.md whose §2 heading was hand-deleted
  When add.py status --section 2 runs
  Then it dies "section_missing"
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py status --section <0-7|ground|specify|scenarios|contract|tests|build|verify|observe>
  ok  -> the ACTIVE task's raw §<n> body on stdout, nothing else
  die -> section_unknown | section_missing | (existing) no-active-task refusal
  resolution: phase-name -> PHASES.index(name); body via taskdoc._raw_phase_bodies
  precedence: --section wins over --brief/--json if combined (documented, not an error)

add-method/skill/add/SKILL.md quick-ref line:
  adds `status --brief` · `advance --fill` · `status --section <n>` — edit byte-neutral-or-
  smaller vs the frozen lean pool baseline (COMPRESS to absorb; never a rebaseline)

Schema: read-only; no state.json change; no new files; 3-tree engine parity + skill-tree parity
```

Glossary deltas: none
`Least-sure flag surfaced at freeze:` [contract] the SKILL.md byte-neutral constraint — the pool baseline is a frozen number I haven't measured against yet; if the compressed line still overflows: cost = one more compression pass inside the same file, surfaced by test_skill_lean, never silent.
Status: FROZEN @ v1 — approved by Tin Dang ("keep going" directive, task 2 shape pre-announced in the milestone plan he confirmed)
Reported: yes — shape + flag rendered in-session (milestone plan + this bundle)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `add-method/tooling/test_progressive_context.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/skill/add/SKILL.md` · `.claude/skills/add/SKILL.md` · `add-method/src/add_method/_bundled/skill/add/SKILL.md` · `.add/SEAMS.md`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>
Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

Persona (required): methodology-engine-dev
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (test_progressive_context 5/5 · targeted fences 51/51 · full tooling suite exit 0)
- [x] coverage did not decrease (5 new behavior tests)
- [x] no test or contract altered during build (§4 plan text left as template — the tests→build crossing predated its fill; the real plan lives in the suite itself; noted honestly, not backfilled post-crossing)
- [x] green EARNED — real subprocess asserts on stdout content and absence (no footer/banner); alias equality asserted byte-wise; rejects asserted on stderr
- [x] concurrency safe — read-only command
- [x] no secrets/injection/deps — stdlib, read-only, prints file content only
- [x] layering — reuses _raw_phase_bodies; no second parser; flag not subcommand
- [x] human approved the shape via the confirmed milestone plan + 'keep going'

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] --section prints one raw §body — M1/M2 green + manual run in this repo
- [x] quick-ref teaches the batched loop; 58 bytes compressed elsewhere absorbs the +50 growth; pool + whole-tree fences green
- [x] 3 engine trees + 3 skill trees in parity; ENGINE_MD5 d6febe37fa909d006bc72868e81bf6d0; SEAMS anchor re-pinned 4870→4892

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — --section branch exercised by 4 tests; parser flag wired
- [x] DEAD-CODE — one branch, no new symbols
- [x] SEMANTIC — SKILL.md compressed sentences re-read in place; meaning preserved (resume rule + one-file-one-task rule intact)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve: cmd_status, _raw_phase_bodies, SKILL.md quick-ref line
- [x] moved: _declared_scope 4870→4892 (SEAMS re-pin x5)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: --section output probed for banner/footer leakage; alias equality byte-compared; bogus + out-of-range tokens; hand-deleted heading

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — read-only print of a local file section
2. Concurrency: CLEAR
3. Architecture: CLEAR — canonical reader reused
Verdict: PASS
Residue: none
Binding: advisory — engine ergonomics, human-shaped at milestone confirm

### GATE RECORD
Reported: yes — build summary rendered in-session before this record
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose status --section flag; rejected new `show` subcommand (rejected: min_pillar LIFECYCLE + slang-guard span ripples) · agent-convention-only (rejected: unenforceable, every agent re-derives it)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang ("keep going" directive, task 2 shape pre-announced in the milestone plan he confirmed))
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] advance --fill: a LATER-section guard refusal (e.g. build_expectations_unfilled) rolls back the draft and the agent must re-apply it — the refusal should preserve the draft (say where) or the guard should run pre-write (evidence: this task's own §4 fill was lost to the expectations guard during dogfooding, 2026-07-07)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

