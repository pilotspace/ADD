# TASK: new-milestone --tiny: one-approval compact plan for small scope

slug: tiny-plan-small-scope · created: 2026-07-08 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches: add-method/tooling/add.py (3-tree parity: .add/tooling + _bundled twins) —
cmd_new_milestone (add.py:3743; arg parser ~:7580), cmd_new_task fast-lane branch
(add.py:663; --fast :720; fast-candidate heuristic hint :657), cmd_milestone_confirm
contracts gate (add.py:3819; milestone_contracts_unfilled :3841);
templates/MILESTONE.md.tmpl (full scaffold a --tiny plan must NOT require);
TASK.fast.md template (existing task-level minimal template the tiny lane reuses);
engine_pin.py ENGINE_MD5; .add/SEAMS.md _declared_scope line pin (drifts on add.py growth).
Evidence base: benchmark wm2/wm3 — ADD already 2-3x faster/cheaper on small scope; the
small-scope waste is the full MILESTONE.md scaffold (mandatory contracts section),
full-template member tasks, and per-task observe. Floor today: fast lane is task-level
only; NO milestone-level tiny plan exists.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

R1. `new-milestone <slug> --tiny --goal "..."` scaffolds a COMPACT plan: goal line +
    `## Plan` (≤5 one-line task bullets) + `## Done when` (≤3 observable checks). No
    Shared/risky-contracts section is required; milestone-confirm passes a tiny plan
    whose Plan and Done-when sections are non-empty.
R2. Member tasks of a tiny milestone default to the fast lane (TASK.fast.md) without
    the per-task `--fast` flag; a full-template task remains available via `--full`.
R3. The trust floor is UNCHANGED in tiny: every member task still freezes a contract,
    goes red before build, and records exactly one gate outcome.
R4. Observe defers: tiny member tasks skip per-task observe prose; deltas buffer and
    are emitted once at `milestone-done` (grammar unchanged, task attribution kept).
R5. --tiny is HUMAN-declared, never engine-elected; the fast-candidate heuristic may
    SUGGEST it in new-milestone output for small goals (advisory note: convention).
R6. Guard: a task with sensitivity security|data|architecture inside a tiny milestone
    scaffolds the FULL template regardless of R2 (base-class floor, GLOSSARY-extensible).
Lowest confidence: R4 delta buffering — where deferred deltas live between task done and
milestone-done (proposal: the task's own §7 stub, harvested by milestone-done) — flag for
contract review.

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

S1. Given a repo with ADD initialized, when the human runs `new-milestone quick-fixes
    --tiny --goal "polish CLI errors"`, then MILESTONE.md contains goal + Plan + Done-when
    only, and `milestone-confirm quick-fixes` succeeds with both sections filled.
S2. Given a confirmed tiny milestone, when `new-task fix-exit-codes` runs under it, then
    the task scaffolds TASK.fast.md (fast lane) with no --fast flag given.
S3. Given a tiny member task, when it reaches done, then no per-task observe section is
    demanded, and `milestone-done quick-fixes` emits the buffered deltas once, each line
    attributed to its task.
S4. Given a tiny milestone, when `new-task patch-auth --sensitivity security` runs, then
    the FULL TASK.md template scaffolds despite the tiny default (R6).
S5. Given an empty Plan section, when `milestone-confirm` runs, then it dies
    tiny_plan_unfilled (parallel to milestone_contracts_unfilled).
S6. Given a normal (non-tiny) milestone, when created without --tiny, then behavior is
    byte-identical to today (no regression to the full scaffold or confirm gate).

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

Status: FROZEN @ v1 — approved by Tin Dang · 2026-07-08

CLI surface (frozen):
  new-milestone <slug> --tiny [--goal G] [--stage S] [--await-confirm]
    -> writes milestones/<slug>/MILESTONE.md with EXACTLY: header block (unchanged grammar:
       goal/rationale/stage/status/created/release) + "## Plan" + "## Done when".
    -> state.json milestones[<slug>].tiny = true
  new-milestone (no --tiny) -> byte-identical to today.
  milestone-confirm <slug>:
    tiny=true  -> die "tiny_plan_unfilled: fill '## Plan' and '## Done when'" if either
                  section is empty/placeholder; else confirm (contracts check SKIPPED).
    tiny=false -> today's milestone_contracts_unfilled check, unchanged.
  new-task <slug> under a tiny milestone:
    default template TASK.fast.md; --full opts back to TASK.md;
    sensitivity in {security,data,architecture} (base ∪ GLOSSARY) -> TASK.md always.
  milestone-done <slug> (tiny) -> harvests each member task's §7/OBSERVE stub lines into
    the retro output once, prefixed "[<task-slug>]"; per-task observe never demanded.
Errors (frozen names): tiny_plan_unfilled. Existing error names unchanged.
Compat: tiny flag absent in state.json -> false (grandfather: all existing milestones full).

Least-sure flag surfaced at freeze: [contract] deferred-delta buffering — the tiny lane's observe deferral stores lessons in each task's §7/OBSERVE stub until milestone-done harvests them; if the stub grammar drifts from deltas.md's, attribution is lost silently. Verify harvests against the deltas.md grammar in tests.

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

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_tiny_plan_small_scope.py` · `.add/` · `tmp/`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>
Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

Persona (required): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; name "generic" if no project persona fits yet>
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe (CLI scaffold path, single-process atomic writes)
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change (contract freeze approved by Tin Dang; gate on evidence under autonomy: auto)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `new-milestone x --tiny` writes a MILESTONE.md containing ## Plan + ## Done when and NO contracts section; state.json milestones.x.tiny == true — confirmed by reading the scaffold in a temp repo
- [x] `milestone-confirm` on an unfilled tiny plan exits nonzero printing tiny_plan_unfilled; a filled one confirms — confirmed by CLI runs in the suite
- [x] `new-task` under a tiny milestone scaffolds the fast template; `--full` or sensitivity security|data|architecture scaffolds the full one — confirmed by scaffold inspection
- [x] non-tiny milestones scaffold/confirm byte-identically to today — confirmed by the S6 pin + full tooling suite green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — --tiny/--full/--sensitivity wired parser→cmd; tiny read at confirm + new-task — every new symbol is referenced; record where / how confirmed
- [x] DEAD-CODE (code) — no orphan symbols; all new branches test-covered — no new unused or orphaned symbol introduced
- [x] SEMANTIC (prose / non-code) — tiny scaffold prose + help strings read in full — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves (cmd_new_milestone/cmd_milestone_confirm/cmd_new_task re-grepped post-build) in the current tree — confirmed by <how / where>
- [x] any anchor that moved/renamed since Ground SHA — _declared_scope 4900→4938, SEAMS re-pinned x8 is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: S6 non-tiny byte-compat pin green pre-change and post-change; tiny_plan_unfilled refuses empty AND placeholder-only sections via the shared _section_unfilled predicate; full suite 3217 (1 env-junk pycache failure purged, test green on rerun)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR (no new IO surface beyond scaffold writes; no secret/exec paths)
2. Concurrency: CLEAR (atomic writes, same as existing scaffold path)
3. Architecture: CLEAR (lane marker mirrors the existing fast-task marker pattern)
Verdict: PASS
Residue: none
Binding: advisory — mechanical-adjacent scaffold change

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-08

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang · 2026-07-08)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

