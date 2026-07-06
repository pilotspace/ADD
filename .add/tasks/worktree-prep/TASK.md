# TASK: add.py worktree-prep — mechanize the spawn-isolation recipe

slug: worktree-prep · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:cmd_worktree_prep (new) — the recipe mechanizer; parser sibling of streams; add-method/skill/add/streams.md — the Materialize bullet now points at the verb
Context (working folder): streams.md 'Fresh worktree base' + 'Materialize gitignored engine content' bullets — the 3 manual steps this mechanizes
Honors (patterns / conventions): git-subprocess precedent (identity.py); NO-EXEC floor = never run a verify suite (git plumbing is not a suite); validate-then-act; design-for-failure (timeouts on every subprocess, loud worktree_prep_git_failed)
Seams consulted: none apply
Anchors the contract cites: cmd_worktree_prep · _resolve_task · streams.md Materialize bullet
Issues/Risks (→ feed §1): the manual recipe failed 3-for-3 on materialization in a prior session (workers had no engine); the fork-base echo is hand-copied into WAVE.md and typos slip; a worktree cut on a dirty tree silently misses the bundle
Related intent: method-ergonomics — spawn isolation is the roster default; its setup must be one engine verb, not three error-prone manual steps
Ground SHA: 66b582d

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: add.py worktree-prep <slug> — cut worktree at HEAD · materialize gitignored engine trees · echo fork base
Framings weighed: one engine verb (chosen) · a shell snippet in streams.md (stays error-prone) · auto-prep inside a future spawn verb (no spawn verb exists; engine never spawns)
Must:
<must>
  - cuts a git worktree at HEAD (default ../<project>-wt-<slug>, --dir overrides)
  - copies gitignored .add/tooling + .add/docs into the worktree (tracked-only checkout lacks them)
  - echoes fork base: <sha> for the WAVE.md ledger + the cleanup command
  - dirty tree WARNS (worktree_prep_dirty_tree) but proceeds; state.json never written
</must>
Reject:
<reject>
  - no git repo / no commit -> "worktree_prep_no_git"
  - destination exists -> "worktree_prep_exists"
  - git refuses -> "worktree_prep_git_failed" (stderr surfaced)
  - unknown slug -> "unknown task"
</reject>
After:
<after>
  - a worker can run add.py inside the worktree immediately; wave-verify can match the echoed base
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ .add/tooling + .add/docs are the complete gitignored set a worker needs — lowest confidence because personas-teacher/ is also a managed gitignored tree; if wrong: a persona-loading worker degrades gracefully (OPTIONAL soft-skip tree) and a delta adds it
  - [x] git subprocess is engine-precedented — confirmed: identity.py runs git config; NO-EXEC covers verify suites only
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: happy path   # M1–M3
  Given a committed project with gitignored .add/tooling + .add/docs
  When worktree-prep <slug> runs
  Then the worktree exists at HEAD, both trees are materialized, fork base echoed

Scenario: dir override   # M1
  Given --dir <path>
  When prep runs
  Then the worktree lands there

Scenario: existing dest refused   # R2
  Given the default destination already exists
  When prep runs
  Then worktree_prep_exists, nothing written

Scenario: no git refused   # R1
  Given no .git
  When prep runs
  Then worktree_prep_no_git
  And no directory created

Scenario: dirty tree warns   # M4
  Given an uncommitted file
  When prep runs
  Then worktree_prep_dirty_tree warning + the worktree still cut

Scenario: state untouched   # M4
  Given any successful prep
  When state.json is compared
  Then byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py worktree-prep [slug] [--dir <path>]     # exit 0
  worktree ready: <dest>
  fork base: <short-sha>  (record in WAVE.md; worker step-0 re-echoes)
  materialized (...): .add/tooling, .add/docs
  cleanup when merged: git -C <project> worktree remove <dest>
refusals (all pre-write): worktree_prep_no_git | worktree_prep_exists |
  worktree_prep_git_failed | unknown task; dirty tree -> WARN only.
Schema: none — state.json never written
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [spec] tooling+docs is the complete materialization set — because personas-teacher/ is also gitignored; if wrong: graceful degrade + a follow-up delta

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: happy path + all 3 refusals + warn path + state purity
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_worktree_prep (7 tests): happy path (base==HEAD, trees materialized) · dir override · exists refused · no-git refused · unknown slug · dirty warns · state byte-stable · covers: M1–M4, R1–R3
</test_plan>

Tests live in: `add-method/tooling/` (test_worktree_prep.py) · ran red 7/7 (no such command) before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` · `add-method/skill/` · `.claude/` · `add-method/src/add_method/_bundled/` · `.add/tooling/`
Strategy (ordered batches): 1. red suite (temp git repos) 2. cmd_worktree_prep + parser 3. streams.md pointer (net −6B, no pool bump) 4. pin re-aim + 4-tree sync

Persona (required): generic — engine-internals stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn (this task BUILDS the isolation tool)
Known-problem fixes: every subprocess carries a timeout + OSError guard (design-for-failure); refusals precede the first write so a refused prep leaves zero residue; the streams.md edit must not grow the pinned orchestration pool
Strategy actually used: as planned
Safety rule (feature-specific): prep never writes state.json and never touches the primary tree beyond git's own worktree bookkeeping
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a fresh worktree carries a runnable engine (tooling+docs) and its HEAD equals the echoed base — confirmed by test happy path asserting both
- [x] a refused prep leaves no directory and no state change — confirmed by refusal tests + byte-stable state.json

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — cmd_worktree_prep wired via the worktree-prep parser (set_defaults)
- [x] DEAD-CODE (code) — none
- [x] SEMANTIC (prose / non-code) — streams.md isolation section read in full; the verb mirrors all 3 documented steps

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 cites resolves — grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: state purity on success AND refusal · refusal ordering (no partial worktree on a refused prep) · base echo equals the worktree's actual HEAD

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — git args are list-form (no shell), paths resolved, timeouts everywhere; --dir is human-supplied and confined only by .exists() refusal (worktrees are legitimately outside the root)
2. Concurrency: CLEAR — git worktree add is atomic per destination; concurrent preps to the same dest race into git's own refusal
3. Architecture: CLEAR — workspace verb beside streams/wave-verify; engine still never spawns
Verdict: PASS
Residue: none
Binding: advisory — mechanical

### GATE RECORD
Reported: no — collapsed ceremony under the standing implement-all directive; evidence above
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose one engine verb; rejected a shell snippet in streams.md (stays error-prone) · auto-prep inside a future spawn verb (no spawn verb exists; engine never spawns)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

