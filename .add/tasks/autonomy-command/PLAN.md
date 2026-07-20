# TASK: First-class add.py autonomy show|set verb + de-command-shape the autonomy header-edit wording

slug: autonomy-command · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default `auto`: method-defining + security-relevant (autonomy decides whether a HUMAN owns the verify gate). The engine refuses an unguarded high-risk completion, so verify escalates to a human PASS. (Ironically hand-edited — the exact friction this task removes.) -->
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
  - `add-method/tooling/add.py` — the engine. ADD `cmd_autonomy(args)` + an `autonomy` subparser in
    the registration block (~4076, slot beside `gate`/`stage`, template = `gate`'s parser at 4076-4082).
    READ-reuse (all already exist, all pure): `_effective_autonomy(root,state,slug)`:672 ·
    `_autonomy_level(hdr)`:643 · `_AUTONOMY_LEVELS`:635 · `_AUTONOMY_LINE_RE`:640 ·
    `_autonomy_lowered(hdr)`:656 · `_RISK_HIGH_RE`:631 (set-time risk guard) ·
    `_project_autonomy(root)`:2285 / `_project_autonomy_token`:2273 · `_task_header(root,slug)`:662 ·
    `_driver_stop`/`_driver_marker`:682/697 (the "why it stopped" line) · `_resolve_task` ·
    `load_state`/`save_state` · `_require_root` · `_now`.
  - KEY GAP: the engine has NO writer for the `autonomy:` header line today — every autonomy symbol is
    READ-only. `autonomy set` is the FIRST writer of this token → must rewrite the single declaration
    line idempotently (no duplicate `autonomy:` line — the exact scla-mono failure) and preserve the
    trailing rationale comment. PROJECT.md default writes go through the same discipline.
  - Command-shaped strings to de-command-shape: `"set autonomy: …"` at add.py:480, :730, :1575 +
    the new-task header-comment template that seeds line `autonomy: auto <!-- … -->`.
  - Guides (3 mirrors each — `.claude/skills/add/`, `add-method/skill/add/`,
    `add-method/src/add_method/_bundled/skill/add/`): `run.md` (autonomy/auto-gate authority) ·
    `SKILL.md`:77 · `phases/3-contract.md`:69 · `confidence.md`:29 · `streams.md`:40,43.
  - `add-method/tooling/WORDING_RUBRIC.md`:53 — "lower the dial -> lower the autonomy level [enforced]".
Context (working folder): prior task `autonomy-dial` [v6, done] introduced the 3-mode ladder
  (manual<conservative<auto) as a header token BY DESIGN — this task adds only the missing CLI verb +
  de-command-shapes the wording; it does NOT change ladder semantics or the verify-gate owner rule.
Honors (patterns / conventions): subcommand pattern (`add_parser` + `set_defaults(func=cmd_*,
  _opt_positionals=…)`, argv-portability via `_rebind_optional_positionals`:4173) · fail-safe autonomy
  resolution (absent→auto, garbled→conservative) · "AI may LOWER (RECOMMEND-only), RAISING is
  human-owned" (confidence.md:29 + test_confidence_rubric) · the `risk: high` ⇒ no-`auto` guard
  (`unguarded_high_risk_auto`) enforced ALSO at set-time, not only at gate.
Anchors the contract cites: `cmd_autonomy` · the `autonomy` subparser · `_effective_autonomy` ·
  `_autonomy_level` · `_AUTONOMY_LINE_RE` · `_autonomy_lowered` · `_RISK_HIGH_RE` · `_project_autonomy`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py autonomy` — a first-class read/write verb for the autonomy dial, + de-command-shaping
the header-edit wording so an agent is never lured into a phantom command (the scla-mono derailment).
Framings weighed: mirror-the-verb-pattern (chosen — `autonomy` joins the 24 subcommands as `show`+`set`,
the engine enforces invariants a hand-edit can't) · read-only-show-only (safer, but leaves the
error-prone hand-edit write) · flags-on-existing-commands (least discoverable; can't change mid-run).
Must:
<must>
  - `add.py autonomy [show] [slug]` — READ-ONLY. Prints the task's DECLARED level, the EFFECTIVE level
    (fallback-resolved), the PROJECT default, and WHO owns the verify gate under it (the `_driver_stop`
    marker — "why it will stop/drive"). Mutates nothing. Defaults to the active task.
  - `add.py autonomy set <manual|conservative|auto> [slug]` — rewrites the task's SINGLE `autonomy:`
    declaration line in TASK.md, preserving its trailing rationale comment, IDEMPOTENTLY (exactly one
    `autonomy:` line ever — re-running replaces, never appends: the scla-mono duplicate-line bug).
  - `add.py autonomy set <level> --project` — rewrites the project default (PROJECT.md) under the same
    single-line discipline; new tasks then inherit it.
  - LOWERING (auto→conservative→manual) is allowed for the agent and recorded. RAISING
    (toward auto) is a human-owned trust escalation: refused UNLESS `--yes` is passed.
  - `set auto` (or any raise to a non-lowered rung) on a `risk: high` task is REFUSED AT SET-TIME, not
    deferred to gate — fail-closed, reusing the `unguarded_high_risk_auto` contract.
  - De-command-shape: every user-facing `"set autonomy: X"` string (add.py:480,:730,:1575) + the
    new-task header-comment template now point at `add.py autonomy set …`; an unknown `autonomy …`
    arg already lists valid choices via argparse (the verb now EXISTS, so the phantom resolves real).
  - Wording-lint FENCE (freeze decision): add an `[enforced]` entry to `WORDING_RUBRIC.md` banning the
    command-shaped "set autonomy: <level>" idiom on the agent-facing surface (skill/add + docs/appendix-b)
    so the phantom phrasing can never regress. The surface is already clean → the fence lands green.
</must>
Reject:
<reject>
  - `set` with missing/unknown level token -> "autonomy_level_invalid"
  - `set auto` on a `risk: high` task -> "unguarded_high_risk_auto"  (reuse existing code/guard)
  - raising the rung (toward auto) without `--yes` -> "autonomy_raise_unconfirmed"
  - run outside a `.add/` project -> "no .add/ project found …" (reuse `_require_root` verbatim — v2)
  - `show`/`set` naming an unknown task slug -> "unknown task '<slug>'" (reuse `_resolve_task` verbatim — v2)
</reject>
After:
<after>
  - show: nothing mutated; stdout reflects declared + effective + project + gate-owner.
  - set (task): TASK.md holds exactly ONE `autonomy:` line at the new level with its comment;
    `_effective_autonomy` now returns it; `status`/`guide` reflect it.
  - set (--project): PROJECT.md default line is the new level; subsequent `new-task` inherits it.
</after>
Assumptions — RESOLVED at the freeze (human-decided):
<assumptions>
  ✓ RAISE guard = refuse-without-`--yes` (`autonomy_raise_unconfirmed`) — CONFIRMED by the human; the
    engine's first confirm flag, accepted as the human-owned trust-escalation seam.
  ✓ De-command-shape scope = minimal (3 strings + TASK.md.tmpl) PLUS a `WORDING_RUBRIC.md` `[enforced]`
    fence — CONFIRMED. Surface already clean, so the fence lands green and guards future regression.
  ✓ `set` rationale = free-text comment, no required owner/ticket (no waiver-grade signing).
  ✓ PROJECT.md write target = the same anchored `autonomy:` declaration line `_project_autonomy_token`
    parses — confirmed at add.py:2273-2291.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: show reports declared, effective, project default and gate-owner
  Given an active task declared `autonomy: conservative` under a project default of `auto`
  When I run `add.py autonomy`
  Then it prints declared=conservative, effective=conservative, project=auto, and "verify: human gate"
  And no file is modified (read-only)

Scenario: show falls back to the project default when the task line is unset
  Given a task whose header has no `autonomy:` line and a project default of `auto`
  When I run `add.py autonomy show <slug>`
  Then it prints declared=(unset) and effective=auto
  And no file is modified

Scenario: set lowers a task level by rewriting the single declaration line
  Given an active task declared `autonomy: auto`
  When I run `add.py autonomy set conservative`
  Then the TASK.md header has exactly ONE `autonomy:` line reading conservative, comment preserved
  And `add.py autonomy show` now reports effective=conservative

Scenario: set is idempotent — re-running never appends a duplicate line
  Given a task already at `autonomy: conservative`
  When I run `add.py autonomy set conservative` again
  Then the TASK.md header still has exactly ONE `autonomy:` line
  And no second `autonomy:` line is appended

Scenario: set --project rewrites the inherited default
  Given a project default of `auto` in PROJECT.md
  When I run `add.py autonomy set conservative --project`
  Then PROJECT.md's single `autonomy:` line reads conservative
  And a newly created task inherits conservative

Scenario: raising the rung is refused without --yes (human-owned escalation)
  Given an active task declared `autonomy: conservative`
  When I run `add.py autonomy set auto`
  Then it exits non-zero with "autonomy_raise_unconfirmed"
  And the TASK.md `autonomy:` line is unchanged (still conservative)

Scenario: raising the rung succeeds with explicit --yes
  Given an active task declared `autonomy: conservative`
  When I run `add.py autonomy set auto --yes`
  Then the TASK.md `autonomy:` line reads auto
  And `add.py autonomy show` reports effective=auto

Scenario: set auto on a risk:high task is refused at set-time
  Given an active task whose slug line declares `risk: high`
  When I run `add.py autonomy set auto --yes`
  Then it exits non-zero with "unguarded_high_risk_auto"
  And the `autonomy:` line is unchanged

Scenario: an unknown level token is rejected
  Given any active task
  When I run `add.py autonomy set yolo`
  Then it exits non-zero with "autonomy_level_invalid"
  And no file is modified

Scenario: running outside a .add project is rejected
  Given a directory with no `.add/` project
  When I run `add.py autonomy`
  Then it exits non-zero referencing "no .add/ project found" (reused _require_root)
  And nothing is created

Scenario: naming an unknown task slug is rejected
  Given a valid .add project
  When I run `add.py autonomy show no-such-task`
  Then it exits non-zero with "unknown task 'no-such-task'" (reused _resolve_task)
  And no file is modified

Scenario: the engine no longer emits a command-shaped autonomy string
  Given the garbled-project-autonomy warning path (add.py:480) and the gate guards (:730,:1575)
  When any of those user-facing strings is rendered
  Then it references `add.py autonomy set …`, never a bare "set autonomy: X" that reads as a command
  And the `autonomy` subcommand is registered (an unknown `autonomy` arg can no longer be invalid)

Scenario: the wording-lint fence bans the command-shaped idiom
  Given WORDING_RUBRIC.md carries an [enforced] entry against the "set autonomy: <level>" idiom
  When wording_lint runs over the agent-facing surface (skill/add + docs/appendix-b)
  Then it passes (the surface is clean) and would FAIL if the idiom reappeared
  And the rubric stays self-consistent (F4)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py autonomy [show] [slug]                                   # READ-ONLY (default action: show)
  exit 0, mutates nothing. stdout (one line each):
    task        : <slug>
    declared    : <manual|conservative|auto|unset>
    effective   : <manual|conservative|auto>      # fallback: task→project; absent→auto, garbled→conservative
    project     : <manual|conservative|auto>
    verify gate : <human gate | you drive>         # _driver_marker(_driver_stop(...,'verify'))

add.py autonomy set <manual|conservative|auto> [slug] [--project] [--yes]
  WRITES the SINGLE `autonomy:` declaration line (idempotent — replace in place, NEVER append;
  trailing rationale comment preserved). Target: tasks/<slug>/TASK.md, or PROJECT.md with --project.
  exit 0 -> "task '<slug>' autonomy -> <level>"   |  "project autonomy -> <level>"   (then prints the show block)
  exit 1 (named reject, stderr) -> exactly one of:
      autonomy_level_invalid        # <level> ∉ {manual, conservative, auto} (or missing)
      autonomy_raise_unconfirmed    # target rung is HIGHER than current and --yes was not passed
      unguarded_high_risk_auto      # task slug declares `risk: high` and target is not a lowered rung (reused guard)
      "unknown task '<slug>'"       # <slug> resolves to no task — _resolve_task verbatim (v2; was task_not_found)
      "no .add/ project found …"    # no .add/ root — _require_root verbatim (v2; was no_add_project)
  exit 2 (argparse) -> malformed usage

Ladder: manual(0) < conservative(1) < auto(2).  "raise" ⇔ index(target) > index(current effective for that scope).
Lower or same-rung: allowed, no --yes. Raise: requires --yes (human-owned). risk:high guard checked BEFORE the write.

Registration (build detail, cites the chosen shape): sub.add_parser("autonomy") · positional `action`
  choices={show,set} nargs='?' default='show' · positional `a1`/`a2` nargs='?' (set: a1=level, a2=slug;
  show: a1=slug) · flags --project (store_true), --yes (store_true) · set_defaults(func=cmd_autonomy,
  _opt_positionals=("a1","a2")). New cmd_autonomy(args) in the cmd_* band near cmd_gate.

De-command-shape (same freeze): the user-facing strings at add.py:480, :730, :1575 and the
  templates/TASK.md `autonomy:` comment now reference `add.py autonomy set <level> [--project]` instead
  of a bare command-shaped "set autonomy: X". No behavior change to the guards they belong to.

Schema: NO database. State surfaces touched: a single header line in tasks/<slug>/TASK.md and in
  PROJECT.md. state.json schema UNCHANGED (autonomy stays a header token, never a state.json field).
```

Status: FROZEN @ v2 — approved by Tin Dang (2026-06-15)
Least-sure flag surfaced at freeze: [contract] the raise-guard mechanism — the engine's FIRST `--yes`
confirm flag (no prior precedent in this fail-closed CLI); resolved by the human → refuse-without-`--yes`
(`autonomy_raise_unconfirmed`). Cost if wrong: a re-freeze. Also [contract] the v1→v2 reject-code
alignment to the reused guards (resolved, human-approved).
<!-- v2 change-request (raised at TESTS, human-approved): the v1 reject codes `no_add_project` /
     `task_not_found` were idealized names that did NOT match the guards §3 cited to REUSE. Aligned to
     the engine's verbatim strings — `_require_root` ("no .add/ project found …") and `_resolve_task`
     ("unknown task '<slug>'") — so `autonomy` shares the same error vocabulary as the other 24 commands.
     Behavior unchanged; only the contracted code strings. v1 was approved 2026-06-15. -->
<!-- The freeze IS the one approval — surfaced lowest-confidence flag: [contract] the raise-guard
     `--yes` mechanism (resolved → refuse-without-`--yes`). -->
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per §2 scenario (12); behavior via a temp `.add/` project + invoking
`cmd_autonomy(args)` / argparse, mirroring `test_explicit_autonomy_dial.py` & `test_gate_owner_marker.py`.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_show_reports_all_four_fields: declared+effective+project+gate-owner printed; no file mtime change
  - test_show_unset_falls_back_to_project: no task autonomy line / project auto → effective=auto
  - test_set_lowers_single_line: auto→conservative leaves exactly ONE autonomy: line, comment kept
  - test_set_idempotent_no_duplicate: set conservative twice → still exactly ONE autonomy: line
  - test_set_project_rewrites_default: set conservative --project → PROJECT.md line conservative; new task inherits it
  - test_raise_refused_without_yes: set auto on conservative → exit1 "autonomy_raise_unconfirmed"; line unchanged
  - test_raise_succeeds_with_yes: set auto --yes → line=auto
  - test_set_auto_on_risk_high_refused: risk:high task, set auto --yes → exit1 "unguarded_high_risk_auto"; line unchanged
  - test_invalid_level_rejected: set yolo → exit1 "autonomy_level_invalid"; no write
  - test_no_add_project_rejected: run outside .add → exit≠0 referencing "no .add/ project found" (_require_root)
  - test_unknown_slug_rejected: show no-such-task → exit≠0 "unknown task 'no-such-task'" (_resolve_task); no write
  - test_no_command_shaped_string: add.py:480/:730/:1575 + TASK.md.tmpl reference `add.py autonomy set`, not bare "set autonomy: X"; `autonomy` subcommand is registered
  - test_wording_fence_enforced: WORDING_RUBRIC.md carries the [enforced] "set autonomy: <level>" entry; wording_lint passes over the clean surface + rubric stays self-consistent
</test_plan>

Tests live in: `add-method/tooling/test_autonomy_command.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/engine_pin.py` `add-method/tooling/WORDING_RUBRIC.md` `add-method/tooling/test_min_pillar.py` `add-method/tooling/test_rewrite_guides.py` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py` `.add/tooling/templates/TASK.md.tmpl`
  <!-- ALL scope tokens live on the SINGLE line above — `_declared_scope` parses only the FIRST declaring
       line (`^…Scope \(may touch\):.*$`, re.M, no re.S). A wrapped multi-line scope SILENTLY drops every
       continuation token → the build's pin re-aim / bundle sync / census co-updates read as out-of-scope
       at the verify gate (the scope_violation this task hit while dogfooding — recorded as an ADD finding in §7).
       Coverage: engine_pin (pin re-aim) · WORDING_RUBRIC (the fence) · the `_bundled/tooling/` directory token
       covers _bundled/tooling/add.py + _bundled/tooling/templates/TASK.md.tmpl (subtree) · `.add/tooling/*`
       are walk-excluded (the `.add/` subtree is pruned by _scope_walk) but kept for intent · the two CENSUS
       guards test_min_pillar (LIFECYCLE) + test_rewrite_guides (AUTONOMY_COMMAND_IDIOMS) ratify the additions.
       The §4 test add-method/tooling/test_autonomy_command.py is baseline (written pre-snapshot). Guides/skill NOT touched. -->
Strategy (ordered batches):
  1. add.py canonical — `cmd_autonomy(args)` + `autonomy` subparser (template = `gate` parser), wired
     `set_defaults(func=cmd_autonomy, _opt_positionals=("a1","a2"))`.
  2. set-time guards — level-invalid · ladder raise-without-`--yes` (`autonomy_raise_unconfirmed`) ·
     `risk: high`+raise (`unguarded_high_risk_auto`, reuse `_RISK_HIGH_RE` + `_autonomy_lowered`).
  3. idempotent ATOMIC header writer — replace the single `autonomy:` line in TASK.md / PROJECT.md
     (comment preserved) via `_atomic_write`; fail-closed if no declaration line present.
  4. de-command-shape — reword add.py:480/:730/:1575 + the TASK.md.tmpl autonomy comment to cite
     `add.py autonomy set <level> [--project]`; add the `[enforced]` `WORDING_RUBRIC.md` entry banning
     the "set autonomy: <level>" idiom (surface already clean → wording_lint stays green).
  5. re-sync + pin — run `scripts/prepare_bundle.py`; mirror add.py + template into `.add/tooling/`;
     re-aim `ENGINE_MD5` in engine_pin.py + append its changelog line.
  6. green — new test red→green, then the FULL suite incl. test_bundle_parity + test_tree_parity + the
     5 ENGINE_MD5-pinned prose suites.
Safety rule (feature-specific): the header writer is the risky op — idempotent + atomic (exactly ONE
  `autonomy:` line, trailing comment preserved, NEVER append) and fail-closed when the line is absent;
  the level / raise / risk:high guards all run BEFORE any write (no partial mutation).
Code lives in: `add-method/tooling/` (+ its synced bundle/dogfood mirrors).
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — no new deps); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — FULL suite `1044 tests OK, exit=0` (13 new in test_autonomy_command.py all green)
- [x] coverage did not decrease — +13 behavioral tests for the new verb; +2 census ratifications (test_min_pillar LIFECYCLE, test_rewrite_guides idiom set)
- [x] no test or contract was altered during build — tamper tripwire clean: test_autonomy_command.py + §3 CONTRACT unchanged since the tests→build snapshot (the `advance` build→verify did not trip tamper)
- [x] the green was EARNED, not gamed — refute-read (manual, conservative-gate): writer `_autonomy_decl_line` is PURE + idempotent (`count=1` in-place sub) + atomic (`_atomic_write`); `_autonomy_value` asserts the level TOKEN (not the line), so the `manual < conservative < auto` comment can't vacuously pass — the once-vacuous idempotent test now asserts value=conservative; raise-refused asserts exit≠0 AND line unchanged. No overfit, no stub.
- [x] concurrency / timing of the risky operation is safe — the ONLY write goes through `_atomic_write` (tmp+rename); all three guards (level-invalid · raise · risk:high) run BEFORE the write → no partial mutation on any reject path
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`/`argparse`/`pathlib`); no new dep (allow-list held); no shell/eval; the level-token regex is bounded `[^\s<#|]+`
- [x] layering & dependencies follow CONVENTIONS.md — joins the 24 subcommands via the canonical `add_parser` + `set_defaults(func=…, _opt_positionals=…)` pattern; reuses existing pure helpers only; all 3 add.py copies byte-identical @ ENGINE_MD5 `475d9d40…`, pin re-aimed, bundle+tree parity green
- [ ] a person reviewed and approved the change — **HUMAN GATE (this task is `autonomy: conservative` + `risk: high`): pending Tin Dang's decision**

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_autonomy` is wired by the `autonomy` subparser's `set_defaults(func=cmd_autonomy)`; the subparser registers (proven by the dogfood `add.py autonomy` run + test_min_pillar census coverage). Helpers `_autonomy_decl_line` · `_guard_autonomy_raise` · `_print_autonomy` are each called by `cmd_autonomy`.
- [x] DEAD-CODE (code) — no orphan: every new helper is referenced by `cmd_autonomy`, which the parser dispatches; no symbol left unreferenced.
- [x] SEMANTIC (prose / non-code) — read in full: the 3 reworded add.py strings (:480/:730/:1575), the TASK.md.tmpl autonomy comment, and the WORDING_RUBRIC.md `[enforced]` fence all cite `add.py autonomy set` — zero command-shaped "set autonomy: X" idiom remains; wording_lint = 0 findings.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-15
Note: human verify gate (conservative + risk:high) — 7/7 evidence checks green, earned-green refute-read clean, no security/concurrency residue. Approved at the gate decision point.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-reject-code rate (`autonomy_level_invalid` · `autonomy_raise_unconfirmed` ·
  `unguarded_high_risk_auto`) · adoption signal = `add.py autonomy` invocations replacing hand-edits of the header line
  (the phantom is resolved when agents call the verb instead of inventing it) · zero `set autonomy:` regressions on the
  lint surface (the [enforced] fence is the monitor).
Spec delta for the next loop: harden the §5 Scope grammar so a multi-line declaration can never silently drop tokens
  (the dogfood finding below) — either parse contiguous continuation lines, OR turn a wrapped/over-long scope into a
  loud lint/exit instead of a silent truncation. Candidate follow-up: `scope-decl-multiline` (intake → likely a `task`).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] autonomy was the only MUTABLE first-class state with no CLI verb, so an agent under `auto` hallucinated
    `add.py autonomy` and derailed — the phantom-command class of failure. Closing it needs BOTH the verb AND a wording
    fence (a verb alone leaves the command-shaped prose that lures the hallucination). (evidence: scla-mono logs
    `invalid choice: 'autonomy'`; test_no_command_shaped_string + the [enforced] WORDING_RUBRIC fence)
  - [ADD · folded] `_declared_scope` parses ONLY the first `Scope (may touch):` line (re.M, no re.S), so a WRAPPED §5
    scope silently drops every continuation token — it LOOKS complete but isn't, and the build's legitimate touches
    (pin re-aim · bundle sync · census co-updates) surface as `scope_violation` at the verify gate. A silent truncation
    is worse than a loud reject. (evidence: THIS task hit scope_violation at the gate — declared captured 2 of 9 tokens;
    fixed by collapsing §5 to one line; root-caused at add.py:2629)
  - [TDD · folded] a vacuous green hides where a fixture string contains the asserted token — `set conservative` "passed"
    only because the header COMMENT enumerates `manual < conservative < auto`. Assert the parsed VALUE token, never the
    whole line. (evidence: test_set_idempotent_no_duplicate's first form; fixed with the `_autonomy_value` helper)
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
