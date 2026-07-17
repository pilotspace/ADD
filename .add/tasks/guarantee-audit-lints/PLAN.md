# TASK: Add shallow_deep_check + risk_unset measure-not-block lints to add.py audit

slug: guarantee-audit-lints · created: 2026-06-27 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED: engine change to the CI-consumed `audit` surface + dogfoods the new risk_unset lint (this task declares its own risk). Tin owns the verify gate. inherited default was auto. -->
<!-- ORIGINAL hint: inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_audit` (~4994) — surfaces `_audit_findings` (BLOCKING, exit 1) + `_freeze_skip_notices` (NON-blocking, exit 0). NEW: a sibling `_guarantee_lint_notices(root, state)` (mirrors `_freeze_skip_notices`, ~4980) whose lines `cmd_audit` prints AND `--json` includes; NEVER a finding → audit stays exit 0 (measure-not-block).
  - `add-method/tooling/add_engine/predicates.py:_section_unfilled(md, header)` (43-64) — REUSE as-is for `shallow_deep_check`: `_section_unfilled(s6, "### Deep checks")` → True iff the §6 Deep-checks block is PRESENT-but-unfilled (empty or `<…>` placeholder); ABSENT block → False (auto-grandfathers legacy tasks). §6 read via `_raw_phase_bodies(root, slug).get(6, "")`.
  - `add-method/tooling/add.py:_RISK_HIGH_RE` (~841) parses `risk: high` from the header; NEW `_RISK_ANY_RE` (`(?:^|·)[ \t]*risk:[ \t]*\S`) detects ANY `risk:` token. `risk_unset` = a verify/done task whose header (`_task_header`) has NO `risk:` token. Volume guard: GROUP risk_unset into ONE summary notice (count + slugs), since ~85 existing done tasks lack `risk:` — one grouped line keeps audit readable (decision at freeze).
  - `_task_done` / phase predicates — to scope the lints to tasks that REACHED verify (phase ∈ {verify, observe, done} OR a §6 GATE RECORD outcome present).
  - 3 engine trees byte-identical (canonical `add-method/tooling/` · dogfood `.add/tooling/` · bundled `_bundled/tooling/`) + re-pin ENGINE_MD5 + ENGINE_PKG_MD5 (canonical-only engine_pin.py).
Context (working folder): test lives next to the engine (`add-method/tooling/test_guarantee_lints.py`, the exit-criterion verifier); `test_min_pillar` LIFECYCLE may need no new subcommand (audit already covered). Book/guide: 6-verify.md already says "an unfilled deep checks block is a shallow verify, not a pass" — a one-line note that `add.py audit` now SURFACES it is optional (keep scope tight; the exit criterion is the audit behavior + test).
Honors (patterns / conventions): MEASURE-NOT-BLOCK (non-failing notices like `freeze_skipped` / `goal_not_auto_ready`, never a CI-failing finding) · PRESENCE-ONLY, never judgment (check the placeholder/token, not content quality) · GRANDFATHER legacy (absent → not flagged, via `_section_unfilled`) · engine NO-EXEC · 3-tree byte-identity · the milestone ethic: honest LABELING, only the two structural holes get a forceable gate.
Anchors the contract cites: `_guarantee_lint_notices` · notice codes `shallow_deep_check` + `risk_unset` · `_section_unfilled` (reused) · `_freeze_skip_notices` (pattern) · `_RISK_ANY_RE` · audit stays exit 0.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Two PRESENCE-ONLY, MEASURE-NOT-BLOCK audit notices that SURFACE (never fail on) verify/done tasks with an unfilled §6 Deep-checks block (`shallow_deep_check`) or no `risk:` declaration (`risk_unset`) — honest visibility for the verify guarantees, NOT a new forceable gate.
Framings weighed: non-blocking audit NOTICES mirroring `_freeze_skip_notices` (chosen — audit stays exit 0; matches the milestone ethic "only the two structural holes get a forceable gate") · blocking audit FINDINGS via `_audit_findings` (rejected — would retroactively FAIL CI on 78 risk-less + 1 shallow existing tasks; a hard gate, not honest labeling) · a new tests→build/gate enforcement (rejected — the deep-check CONTENT quality is the human's judgment; only PRESENCE of the fill is engine-checkable)
Must:
<must>
  - `add.py audit` SURFACES, per verify/done task whose §6 "### Deep checks" block is PRESENT-but-unfilled, a `shallow_deep_check <slug>` notice — reuses `_section_unfilled`, so an ABSENT block grandfathers (per-task: the live dogfood shows only 1).
  - `add.py audit` SURFACES a SINGLE grouped `risk_unset` notice naming the COUNT + slugs of verify/done tasks whose header has no `risk:` token — grouped because ~78 qualify; one line keeps audit readable while still showing the honest count.
  - Both are NOTICES, never findings: the audit EXIT CODE is unchanged by them (stays 0 when only notices; 1 only on a real `_audit_findings`).
  - `add.py audit --json` includes both under a new `guarantee_lints` key, alongside `findings` + `freeze_skips`.
  - PRESENCE-ONLY + PURE: the lints check the placeholder/token, never content quality; the engine writes nothing (read-only); scoped to tasks that REACHED verify (phase ∈ {verify, observe, done}).
</must>
Reject:
<reject>
  - a task NOT yet at verify (phase ∈ ground..build) -> neither lint counts it (stays silent)
  - a §6 Deep-checks block ABSENT entirely (legacy task) -> no `shallow_deep_check` (grandfathered via `_section_unfilled`)
  - a header WITH any `risk:` token (`risk: high`, `risk: normal`, …) -> not counted in `risk_unset`
  - these notices alone -> audit must NOT exit nonzero (`audit_exit_stays_zero`)
</reject>
After:
<after>
  - `add.py audit` on the live project prints `shallow_deep_check fold-command` + one grouped `risk_unset — 78 task(s): …` line, EXIT 0; THIS task (guarantee-audit-lints, `risk: high` declared) is ABSENT from the risk_unset list (dogfood); `audit --json` carries both under `guarantee_lints`; ENGINE_MD5 + ENGINE_PKG_MD5 re-pinned across the 3 trees.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] `risk_unset` SHAPE — ONE grouped notice (count + slugs) vs per-task vs forward-only-grandfather. I chose GROUPED because the dogfood shows 78 would fire (per-task = unreadable spam) and grouping still shows the honest count (forward-grandfather would HIDE the 78 — less honest); lowest confidence because it is a presentation call the human owns; if wrong: reshape the notice (cheap, presentation-only, no logic change).
  - [ ] "reached verify" = phase ∈ {verify, observe, done}; archived tasks are already excluded (audit scans `state.tasks`). If wrong: widen/narrow the phase set.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: shallow_deep_check surfaces an unfilled Deep-checks block
  Given a verify/done task whose §6 "### Deep checks" block is still a <…> placeholder
  When add.py audit runs
  Then it prints a "shallow_deep_check <slug>" notice
  And the audit exit code stays 0 (a notice, not a finding)

Scenario: risk_unset is one grouped notice naming the count + slugs
  Given N verify/done tasks whose header has no risk: token
  When add.py audit runs
  Then it prints exactly ONE "risk_unset — N task(s): <slugs>" notice
  And the audit exit code stays 0

Scenario: notices never change the audit exit code
  Given a project with only these notices and no real _audit_findings
  When add.py audit runs
  Then it exits 0
  And a real finding (e.g. unescalated_security_note) still exits 1 (notices don't mask findings)

Scenario: --json carries both lints under guarantee_lints
  Given add.py audit --json
  When it runs
  Then the JSON has a "guarantee_lints" key listing shallow_deep_check items + the risk_unset group
  And the existing "findings" and "freeze_skips" keys are unchanged

Scenario: rejection — a task not yet at verify is silent
  Given a task at phase build (contract frozen, not yet verified)
  When add.py audit runs
  Then neither lint counts that task
  And the audit output for it is unchanged

Scenario: rejection — an absent Deep-checks block is grandfathered
  Given a legacy verify/done task with NO "### Deep checks" block at all
  When add.py audit runs
  Then no shallow_deep_check notice names it (_section_unfilled returns False for absent)
  And the audit exit code stays 0

Scenario: rejection — a declared risk silences risk_unset for that task
  Given a verify/done task whose header carries "risk: high" (or any risk: token)
  When add.py audit runs
  Then that task is NOT in the risk_unset group
  And this guarantee-audit-lints task (risk: high) dogfoods that exclusion
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE CONTRACT — extends the read-only `add.py audit`; no new subcommand, no state write.

NEW helper (PURE; mirrors _freeze_skip_notices):
  _guarantee_lint_notices(root, state) -> { "shallow": [<slug>,…], "risk_unset": [<slug>,…] }
    scope: tasks in state.tasks with phase ∈ {verify, observe, done}
    shallow[]    = slugs where _section_unfilled(<§6 body>, "### Deep checks") is True
                   (§6 via _raw_phase_bodies(root, slug).get(6, "")); ABSENT block → not listed (grandfather)
    risk_unset[] = slugs where _RISK_ANY_RE.search(_task_header(root, slug)) is None
    reads TASK.md + state only; writes nothing.

NEW regex:
  _RISK_ANY_RE = re.compile(r"(?:^|·)[ \t]*risk:[ \t]*\S", re.MULTILINE)   # any risk: token in the header

cmd_audit  (text, printed AFTER findings + freeze_skips):
  for s in shallow:   "audit: shallow_deep_check {s} — §6 Deep-checks block unfilled (a shallow verify, not a pass)"
  if risk_unset:      "audit: risk_unset — {N} task(s) reached verify with no risk: declaration: {s1, s2, …}"
  EXIT CODE: unchanged — sys.exit(1) ONLY when _audit_findings is non-empty; notices NEVER raise it.

cmd_audit --json:
  { "checked": int, "findings": [...], "freeze_skips": [...],
    "guarantee_lints": { "shallow": [...], "risk_unset": [...] } }     # additive key; existing keys unchanged

Reject codes (test labels): audit_exit_stays_zero (notices alone keep exit 0).
Schema: NONE — read-only; no state.json write; no migration; no new subcommand.
3-tree byte-identical add.py + re-pin ENGINE_MD5 + ENGINE_PKG_MD5 (canonical-only engine_pin.py).
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the `risk_unset` SHAPE — I drafted it as ONE grouped notice (count + slugs) because the live dogfood shows **78** verify/done tasks lack a `risk:` token (per-task would be 78 spam lines), and grouping keeps audit readable while still printing the honest count. Alternatives: per-task lines (loud), or forward-only-grandfather (hides the 78 — less honest). It is a presentation call you own; cost if changed: reshape the one notice line (no logic change). Sibling: scope = phase ∈ {verify, observe, done} (archived tasks already excluded).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the two notice paths + their exit-code/json invariants (9 tests / 7 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_shallow_surfaces_unfilled_block: verify task, unfilled §6 deep-check / audit / "shallow_deep_check t" + exit 0
  - test_filled_block_not_flagged: fill the deep-check / audit / no shallow_deep_check
  - test_absent_block_grandfathered: drop the deep-check block / audit / not flagged + exit 0
  - test_not_at_verify_is_silent: ground-phase task / audit / no shallow + no risk_unset
  - test_risk_unset_is_one_grouped_notice: 3 risk-less verify tasks / audit / ONE "risk_unset — 3 task(s): a, b, c" + exit 0
  - test_declared_risk_excluded: one risk:high + one risk-less / audit / risk-less in group, risk:high excluded
  - test_notices_keep_exit_zero: notices present / audit / exit 0
  - test_findings_still_exit_one: inject unguarded_high_risk_auto / audit / finding present + exit 1 (notices don't mask)
  - test_json_carries_guarantee_lints: audit --json / guarantee_lints.{shallow,risk_unset} + findings/freeze_skips intact
</test_plan>

Tests live in: `add-method/tooling/test_guarantee_lints.py` · RED now (5 must-have fails, 4 guards green) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. add `_RISK_ANY_RE` + `_guarantee_lint_notices(root, state)` to canonical add.py (mirror `_freeze_skip_notices`) → 2. wire into `cmd_audit` (print after findings + freeze_skips; never raise the exit code; suppress the "clean" line when notices exist; add to `--json`) → 3. propagate add.py byte-identically to the 2 mirror trees → 4. re-pin ENGINE_MD5 + ENGINE_PKG_MD5 (canonical engine_pin.py) → 5. suite green + dogfood `add.py audit` on the live project.
Safety rule (feature-specific): the notices are PURE + NON-blocking — audit's `sys.exit(1)` stays gated ONLY on `_audit_findings`; no state write; no new subcommand.
Code lives in: the 3 engine trees (add.py) + engine_pin.py (canonical only).
Constraints: do NOT change any test or the contract; no new packages; the 3 trees stay byte-identical.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2098/0; test_guarantee_lints 9/9
- [x] coverage did not decrease — +9 tests; the 3 collateral edits accommodate contracted behavior (no coverage lost — refute confirmed)
- [x] no test or contract was altered during build — my §4 set (test_guarantee_lints.py) + §3 untouched since tests→build (tripwire clean); the 3 sibling-test edits are OUT of the §4 set + faithful (not weakening)
- [x] the green was EARNED — independent refute-read (agent a4bf606e) VERDICT **EARNED**: exit code structurally gated on `_audit_findings` only, scope/grandfather/purity correct, all 3 collateral edits REQUIRED faithful accommodations (the `"Deep check"` guard removal forced by the contracted heading reference; no weaker than before — SEMANTIC was never guarded), 9 non-vacuous tests incl. a finding-co-existence guard, no masked finding
- [x] concurrency / timing — N/A (read-only pure function; no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re` only; reads TASK.md + state, writes nothing
- [x] layering & dependencies follow CONVENTIONS.md — mirrors `_freeze_skip_notices`; reuses `_section_unfilled`; 3-tree byte-identical
- [x] a person reviewed and approved the change — Tin Dang owned the verify gate (conservative) and chose Gate PASS

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] live `add.py audit` prints `shallow_deep_check fold-command` + one grouped `risk_unset — 78 task(s): …`, EXIT 0 — confirmed by running it on this project
- [x] this task (guarantee-audit-lints, `risk: high`) is ABSENT from the risk_unset group — confirmed: grep count 0 in the live audit output (dogfood)
- [x] `add.py audit --json` carries `guarantee_lints.{shallow,risk_unset}`; `findings`/`freeze_skips` unchanged — confirmed by json inspection (keys: checked, findings, freeze_skips, guarantee_lints)
- [x] a real finding still exits 1; notices alone exit 0 — confirmed by test_findings_still_exit_one + test_notices_keep_exit_zero (both green)
- [x] 3-tree add.py byte-identical + ENGINE_MD5 re-pinned — md5 d8c3ff43 single-valued = ENGINE_MD5; ENGINE_PKG unchanged (no add_engine/ edit); full suite green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_guarantee_lint_notices` is called by `cmd_audit` (text + --json); `_RISK_ANY_RE` used inside it; both reach a referenced caller. No orphan symbol.
- [x] DEAD-CODE (code) — no new unused symbol; `_section_unfilled`/`_raw_phase_bodies`/`_task_header` are pre-existing reused helpers; the engine embeds NO deep-check content tokens (WIRING/DEAD-CODE/SEMANTIC absent from add.py — test_verify_deepen guards it)
- [x] SEMANTIC (prose / non-code) — read the implementation + the 3 collateral test edits in full; confirmed presence-only (no content judgment), exit-code gated on findings only, and each test edit faithfully accommodates the contracted notice (verified independently by the refute-read)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the 78-task `risk_unset` count is the drain signal — it should fall as new tasks declare risk; a CI consumer must treat `guarantee_lints` as NON-failing (a regression that lets a notice raise the audit exit code would redden every clean-board run).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] make `risk:` a FIRST-CLASS task-template field (default `risk: normal` on the slug line) so new tasks declare it explicitly and the risk_unset count drains toward 0 (evidence: 78 existing verify/done tasks have no risk: token; the lint surfaces the gap but the template never prompts for it) [carried: engine/template-scope: default risk: normal on the slug line; deferred past flow-honesty]
- [SPEC · dropped] add a one-line note to 6-verify.md / run.md that `add.py audit` now SURFACES the shallow_deep_check + risk_unset lints (evidence: the guides describe the deep-check + risk rubric but not that audit measures their presence — a stale-guide-sync candidate)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a MEASURE-NOT-BLOCK lint (non-failing audit notice) is the honest tool when the engine can check PRESENCE but cannot JUDGE quality — surface the gap, never gate on it; reserve forceable gates for the structural holes (evidence: shallow_deep_check/risk_unset would have failed CI on 79 existing tasks if blocking — dishonest; as notices they inform without breaking) [folded foundation-version 56]
- [TDD · folded] a behavior change to a SHARED output surface (audit) ripples into sibling "clean board" fixtures — fix by making the fixture WELL-FORMED (declare risk) not by loosening the assertion; a presence/format test stays strong (evidence: 3 collateral fixtures gained `risk: normal`; refute-read confirmed no coverage lost) [folded foundation-version 56]
- [TDD · folded] when a later task legitimately relaxes an earlier invariant (engine now NAMES the deep-check block), update the guard to the NARROWER true invariant (no content tokens) rather than deleting it (evidence: test_verify_deepen `assertNotIn("Deep check")` → `assertNotIn("DEAD-CODE")` + WIRING, preserving judgment-free) [folded foundation-version 56]
