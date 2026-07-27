# PLAN: No arm claims a method it never invokes

slug: arm-honesty · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an arm that installs a method's scaffolding must invoke that method — enforced by a guard, not by reviewer memory.
Framings weighed: a mechanical guard over every arm TOML plus a real spec-kit wrapper (chosen — the defect was invisible to 493 green tests for months precisely because nothing compared an arm's setup against its wrapper; a guard is the only thing that stops it recurring) · fix spec-kit's wrapper only (rejected — gsd carries the identical defect, and a one-off fix leaves the class alive) · rename both to `baseline-*` (rejected — archived records already carry the name `spec-kit`, and renaming makes them unreadable without fixing the honesty problem for future runs)
Must:
<must>
  - an arm whose setup_steps install a method's scaffolding either invokes that method through its prompt_wrapper, or declares `scaffold_only = true` with a stated reason
  - the spec-kit arm installs the CLAUDE integration (`--integration claude`), so its slash commands land where the runner's agent reads them
  - the spec-kit arm's prompt_wrapper drives its own documented cycle: specify -> plan -> tasks -> implement
  - the guard enumerates every arm TOML on disk, so an arm added later is covered without editing the guard
</must>
<reject>
  - an arm that installs scaffolding, sets prompt_wrapper = "raw", and declares no scaffold_only -> "silent_method_arm"
  - a scaffold_only declaration with no reason -> "unexplained_scaffold_only"
</reject>
After:
<after>
  - spec-kit's workspace contains Claude-readable commands, and its records can be read as a spec-driven-development arm
  - gsd's status is explicit on its face: either it invokes GSD, or its TOML says in words that it does not
  - the raw-with-no-scaffolding control (`vanilla`) is untouched and still passes the guard
</after>
Boundary: arm TOMLs are the only input shape — `prompt_wrapper` is a bare string, `setup_steps` a list of shell strings; an arm with `setup_steps = []` is scaffolding-free and out of the guard's reach by construction.
<assumptions>
  ⚠ spec-kit v0.12.5's `--integration claude` writes commands the runner's agent can actually invoke — if wrong: the wrapper's cycle instructions still drive the workflow by reading `.specify/`, so the arm degrades to "method described, not slash-invoked" rather than back to raw; cost = one wrapper reword.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/arms/<name>.toml
  setup_steps      : list[str]   installs scaffolding when non-empty
  prompt_wrapper   : str         "raw" | "add-loop" | "add-loop-enumerate"
                                 | "plan-then-execute" | "spec-kit"   <- NEW
  scaffold_only    : bool        OPTIONAL; when true a reason MUST follow
  scaffold_only_reason : str     OPTIONAL; required iff scaffold_only

benchmark/runner/core.py :: _wrap_prompt(text, "spec-kit")
  -> prepends the documented SDD cycle: specify -> plan -> tasks -> implement

guard: benchmark/tests/test_arm_invokes_its_method.py
  enumerates arms/*.toml
  scaffolding AND raw AND not scaffold_only      -> fail "silent_method_arm"
  scaffold_only AND no reason                    -> fail "unexplained_scaffold_only"
```
Ground: `benchmark/arms/spec-kit.toml` (`prompt_wrapper = "raw"`, setup lacks `--integration`) · `benchmark/arms/gsd.toml` (same defect) · `benchmark/arms/vanilla.toml` (`setup_steps = []`, the honest control) · `benchmark/runner/core.py::_wrap_prompt` (`raw` is the fall-through return) · `benchmark/arms/loader.py::REQUIRED_KEYS` · `benchmark/tests/test_arms.py::test_all_arms_validate_with_fairness_parity` (asserts pins, never wrappers). Evidence the defect is real: `specify init` help states it "default[s] to Copilot in non-interactive sessions"; every pay/wm spec-kit workspace carries `.specify/init-options.json` with `"ai": "copilot"` and `.github/prompts/speckit.*.prompt.md`, and ZERO `specs/` artifacts.

Target (measurable): the new guard is RED against today's tree naming both `spec-kit` and `gsd`, and GREEN after the change with 0 arms unaccounted for; `benchmark/tests/` stays fully green (493 -> 493+new); `load_arm` accepts every existing arm unchanged (no arm rejected by the new optional keys).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/arms/` `benchmark/runner/core.py` `benchmark/tests/` `benchmark/BENCHMARK.md`   <HARD — fill before the freeze; the file write-set, single source of truth; every file the build may write. Token grammar (backtick each): name/ = project root · ./… = THIS task's dir (rarely what a build writes) · a directory covers its whole subtree>
Regression floor: `benchmark/tests/` — all 493 must stay green (test_arms.py in particular must keep passing unchanged).
Persona (optional): `.add/personas/tdd-verifier.md` — the guard is the deliverable; the arm edits merely satisfy it.

Least-sure flag surfaced at freeze: [contract] the `scaffold_only` escape hatch is the part I trust least — it is exactly the shape of a guard that gets satisfied by declaring the problem instead of fixing it, and gsd will be its first user. It is still the honest option (I cannot verify GSD's command surface offline), but if it becomes the default answer the guard stops biting.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_every_arm_that_installs_scaffolding_invokes_it: enumerate arms/*.toml; scaffolding + raw + no scaffold_only -> fail · covers: M1, R:silent_method_arm
  - test_scaffold_only_requires_a_reason: a TOML with scaffold_only and no reason is rejected · covers: M1, R:unexplained_scaffold_only
  - test_guard_enumerates_disk_not_a_hardcoded_list: a NEW arm file dropped into a tmp arms dir is covered without editing the guard · covers: M4
  - test_spec_kit_installs_the_claude_integration: spec-kit setup_steps carry --integration claude · covers: M2
  - test_spec_kit_wrapper_drives_the_sdd_cycle: _wrap_prompt(text, "spec-kit") names specify, plan, tasks, implement and still contains the raw prompt · covers: M3
  - test_vanilla_needs_no_declaration: setup_steps == [] passes the guard untouched · covers: M1 [edge]
  - test_existing_arms_still_load: every arms/*.toml loads through load_arm after the new optional keys · covers: M1 [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: <fill at VERIFY — what you ACTUALLY did (or "as planned"); harvested into §7 Decisions (ADR)>
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
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose a mechanical guard over every arm TOML plus a real spec-kit wrapper; rejected fix spec-kit's wrapper only (rejected — gsd carries the identical defect, and a one-off fix leaves the class alive) · rename both to `baseline-*` (rejected — archived records already carry the name `spec-kit`, and renaming makes them unreadable without fixing the honesty problem for future runs)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
