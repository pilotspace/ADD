# TASK: Engine-scaffolded §6 verify record

slug: verify-record-scaffold · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:_guarantee_lint_notices — pure reader building the per-code glint dict {code: [slug…]}; add-method/tooling/add.py:cmd_audit — prints one grouped line per code after findings+skips, exit code untouched by notices; add-method/tooling/templates/TASK.md.tmpl §6 — already scaffolds every verify block (`### Build expectations` "fill BEFORE build" · `### Deep checks` · `### Live-verify evidence` · `### Refute-read verdict` · `### Advisor 3-lens verdict` · `### GATE RECORD` with `Reported:`); add-method/skill/add/phases/4-tests.md — the guide the bundle-drafting agent reads when the expectations block must be filled
Context (working folder): mirror twin .add/tooling/add.py (dogfood — re-sync after build); test files pinning existing lint shapes: test_guarantee_lints.py · test_refute_record_required.py · test_advisor_review_step.py · test_report_rendered_trace.py · test_stale_guide_sync.py · test_docs_align.py · test_skill_lean.py (phases-pool byte budget)
Honors (patterns / conventions): MEASURE-NOT-BLOCK — a glint never raises audit's exit code or blocks a gate; append-frozen lint vocabulary (milestone shared decision) — existing codes/lines keep exact shape ("exactly ONE grouped line per <code>" pinned per-code); lean-over-budget-bump — 4-tests.md may not grow the phases pool (reclaim in-file); engine NO-EXEC + pure-reader discipline for audit
Seams consulted: none apply
Anchors the contract cites: _guarantee_lint_notices · cmd_audit · phases/4-tests.md · templates/TASK.md.tmpl §6 `### Build expectations`
Issues/Risks (→ feed §1): (1) the review's original "collapse 4 lints to 1" would break frozen per-code tests — must be ADDITIVE rollup, old codes untouched; (2) the review's "engine stamps the skeleton" is ALREADY TRUE (template-scaffolded at new-task) — scope shrinks honestly; (3) the rollup must union per-task across four §6 lists (shallow · refute_unrecorded · advisor_verdict_unrecorded · verify_report_unrecorded) without double-counting a slug; (4) `audit: clean` conjunction already gates on all four — the rollup must not break the clean line; (5) 4-tests.md is inside the frozen phases byte-pool
Related intent: MILESTONE.md method-ergonomics exit criterion 1; milestone shared decision "engine presents, agent fills"; review item 1+2 (2026-07-06 methodology review)
Ground SHA: ec64f18

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §6 verify-record rollup glint + declare-expectations-at-tests pointer
Framings weighed: additive rollup glint, old codes untouched (chosen) · replace the 4 lints with one code (breaks frozen per-code tests — rejected) · engine-stamp the §6 skeleton at tests→build (already true via TASK.md.tmpl — rejected as no-op)
Must:
<must>
  - M1: `_guarantee_lint_notices` returns an ADDITIVE key `verify_record_incomplete` = the sorted, per-slug-deduped union of its four §6 shape lists (`shallow` · `refute_unrecorded` · `advisor_verdict_unrecorded` · `verify_report_unrecorded`)
  - M2: `cmd_audit` prints exactly ONE grouped line `audit: verify_record_incomplete — N task(s): <slugs> — …` AFTER the existing per-code lines, only when the union is non-empty
  - M3: `cmd_audit --json` carries the additive `guarantee_lints["verify_record_incomplete"]`
  - M4: the four existing codes keep their exact output shape and the `audit: clean` conjunction is unchanged (the rollup is derived, adds no new term)
  - M5: `phases/4-tests.md` instructs filling the §6 Build-expectations block AT TESTS TIME (before build), in both skill twins, with the phases byte-pool not exceeding its current baseline
</must>
Reject:
<reject>
  - a slug unfilled in MORE than one §6 block listed twice in the rollup -> "rollup_duplicate_slug" (behavioral: union dedupes)
  - the rollup line printed when every §6 record is filled -> "rollup_on_clean" (behavioral: silent when empty)
  - a task with phase before verify listed -> "rollup_scope_violation" (behavioral: same {verify, observe, done} scope as the four)
  - audit exit code raised by the rollup -> "notice_raised_exit" (behavioral: MEASURE-NOT-BLOCK)
</reject>
After:
<after>
  - an agent (or human spot-auditor) reads ONE summary line to know a task's §6 verify record needs filling, instead of joining four; the per-code detail lines remain beneath it; the bundle-drafting agent is told at TESTS time to pre-declare expectations
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the rollup should include `shallow` (Deep checks) but NOT `risk_unset`/`sensitivity_unset` (header lints, not §6-record blocks) — lowest confidence because the "verify record" boundary is my judgment; if wrong: the rollup under- or over-reports and needs a member change (cheap, additive)
  - [x] the four per-code tests pin "exactly ONE grouped line" PER CODE, not globally — a fifth line does not break them (confirmed by reading the assertions: each counts its own token)
  - [x] 4-tests.md has reclaimable slack in-file (confirmed at draft: tightened two verbose lines)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: <short name>   # <Must/Reject item this covers, e.g. M1 or R1>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # required for every rejection
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_guarantee_lint_notices() -> dict   gains ADDITIVE key
  "verify_record_incomplete": sorted(set(shallow) | set(refute_unrecorded)
                                     | set(advisor_verdict_unrecorded) | set(verify_report_unrecorded))
cmd_audit (plain):  ONE grouped line, AFTER the per-code lines, only when non-empty,
  "audit: verify_record_incomplete — N task(s): <slugs> — …" (line contains NO member code token)
cmd_audit --json:   guarantee_lints["verify_record_incomplete"] additive
exit code / clean-line conjunction: UNCHANGED (derived key adds no term)
phases/4-tests.md (all 3 twins): Produce gains the §6 Build-expectations fill-now bullet; phases pool ≤ frozen target
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (chat directive 2026-07-06: "implement directly without fill all task's template"; ceremony collapsed, floor kept)
Reported: yes — bundle shape + both ⚠ flags surfaced in-chat at the milestone confirm; freeze approval subsumed by the human's implement-directly directive
Least-sure flag surfaced at freeze: ⚠ [contract] the rollup unions the four §6-record lists but EXCLUDES the header lints (risk_unset · sensitivity_unset) — because the "verify record" boundary is my judgment call; if wrong: the rollup under-/over-reports and needs a one-line member change (cheap, additive)

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

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_verify_record_rollup.py` `add-method/skill/add/phases/4-tests.md` `.claude/skills/add/phases/4-tests.md` `add-method/src/add_method/_bundled/skill/add/phases/4-tests.md` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/.add/tooling/add.py`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>

Persona (required): methodology-engine-dev
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn, not only explicit parallel mode; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: red suite first (8F/3E, right reason) → derived-union rollup in _guarantee_lint_notices + one grouped cmd_audit line → 4-tests.md bullet with in-file byte reclaim (2541→2539 B) → ENGINE_MD5 re-aim → 4-way engine twin sync
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (rollup 11/11; frozen sibling pins 108/108 after re-pin + pool reclaim)
- [x] coverage did not decrease (new suite added; none removed)
- [x] no test or contract was altered during build (dedupe-test slug fix happened pre-red-run, before build)
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] audit on an unfilled verify task prints ONE verify_record_incomplete line after the per-code lines — confirmed by test_verify_record_rollup output + manual run
- [x] phases pool at/below frozen target with the new bullet present in all 3 twins — confirmed by test_skill_lean green + wc -c 2539

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new dict key is consumed by cmd_audit's print + --json passthrough; no other consumer needed (derived) — confirmed by grep + suite
- [x] DEAD-CODE (code) — no new function/symbol introduced beyond the dict entry + print block
- [x] SEMANTIC (prose) — 4-tests.md re-read in full after trim: Produce bullet + hook line still correct, machine-doc section untouched

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 cites still resolves — _guarantee_lint_notices/cmd_audit at add.py (post-edit), 4-tests.md twins synced — confirmed by green targeted suites
- [x] no anchor moved since ec64f18

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: rollup line vs the four per-code pins (member tokens excluded from the line — test_member_codes_not_in_rollup_line); union-vs-members equality asserted in JSON; clean-line conjunction untouched; suite ran red for the right reason BEFORE the implementation existed

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — read-only audit path, no new input parsing, no exec/IO added
2. Concurrency: CLEAR — pure derivation over already-built lists
3. Architecture: CLEAR — derived key pattern matches existing glint conventions; per-code lists stay source of truth
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — evidence summarized in-chat before this record (ceremony collapsed by directive; floor kept)
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto; evidence complete, residue none) under Tin's implement-directly directive · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose additive rollup glint, old codes untouched; rejected replace the 4 lints with one code (breaks frozen per-code tests — rejected) · engine-stamp the §6 skeleton at tests→build (already true via TASK.md.tmpl — rejected as no-op)
- [human] freeze — froze §3 @ v1 (approved by Tin (chat directive 2026-07-06: "implement directly without fill all task's template"; ceremony collapsed, floor kept))
- [AI] build — strategy used: red suite first (8F/3E, right reason) → derived-union rollup in _guarantee_lint_notices + one grouped cmd_audit line → 4-tests.md bullet with in-file byte reclaim (2541→2539 B) → ENGINE_MD5 re-aim → 4-way engine twin sync
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto; evidence complete, residue none) under Tin's implement-directly directive)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

