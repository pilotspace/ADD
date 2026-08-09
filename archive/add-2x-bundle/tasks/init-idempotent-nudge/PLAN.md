# TASK: init on an existing project is a loud no-op resume pointer

slug: init-idempotent-nudge · created: 2026-07-14 · stage: mvp
milestone: call-residuals
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: idempotent init — re-running `init` on an initialized project is a loud no-op resume pointer, and `status` tells the agent not to re-init in the first place (kills the +2–4 calls/rep double-init lever).
Must:
  - `init` on a project WITH state.json and WITHOUT `--force` exits 0, prints the resume pointer (`already initialised … — resume: add.py status`), and re-seeds NOTHING (no state / .gitignore / survivor-template / .bak write)
  - `status` (default view) opens with a "project exists — do not re-init (use --force to reset)" line whenever state.json is present
  - `init --force` on an existing project still resets (unchanged); `init` on a fresh dir still seeds + exits 0 (unchanged)
Reject:
  - none new — this task REPLACES the prior nonzero refusal (init-resume-pointer v1) with an exit-0 no-op; that frozen test is superseded by change-request, not weakened
Accept: Given an initialized project, When `add.py init` runs again without --force, Then it exits 0, writes nothing under .add/, and prints the resume pointer (not the old nonzero "already initialised" error)
Boundary: none — no external input shape (CLI invocation only; state.json present vs absent is the only branch)
Assumptions: ⚠ the double-init call is a second `init` MID-session (the first legitimately seeds) — making the repeat an exit-0 no-op is safe because `--force` still resets; if wrong (a user WANTED a reset): they must add --force, and the message names it

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add-method/tooling/add.py:cmd_init` (the state-exists guard that today `_die`s on a re-init without --force) · `add-method/tooling/add.py:cmd_status` (the default-view opening, before the project banner) · `add-method/tooling/test_init_resume_pointer.py:ResumePointerTest.test_refusal_names_resume` (the frozen v1 contract this supersedes: nonzero exit → exit 0)
Context (working folder): `add-method/tooling/` (canonical engine) — the change syncs byte-identical to the two twins (`.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`) after build; SEAMS.md + engine_pin ENGINE_MD5 re-pinned
Honors (patterns / conventions): the `_die` (exit≠0) vs `print(...)+return` (exit 0) idiom; the survivor-file "never clobber / never write blank" skip idiom stays intact (early-return simply skips the whole seed block); no gate/freeze/tamper/scope enforcement path touched (milestone OUT-of-scope)
Anchors the contract cites: `cmd_init`, `cmd_status`, `state.json` (STATE_FILE), `--force`
Ground SHA: e1a967a — stamped by freeze

### Contract

```
cmd_init(args), state.json PRESENT, args.force is False:
  → stdout: "add: already initialised at <root> — resume: add.py status" (+ active-task/next pointer if resolvable)
  → writes: NOTHING under .add/ (no state.json, .gitignore, survivor template, or .bak)
  → exit: 0                       # was: _die → exit 2 (superseded; init-resume-pointer v1)
cmd_init(args), args.force is True            → unchanged (resets, exit 0)
cmd_init(args), state.json ABSENT             → unchanged (seeds, exit 0)
cmd_status default view, state.json PRESENT:
  → the opening includes a line: "project exists — do not re-init (use --force to reset)"
cmd_status, no .add project                   → unchanged ("no .add/ project found …")
```

`Least-sure flag surfaced at freeze:` [contract] the exact placement/wording of the status "project exists — do not re-init" line — banner-head vs a dedicated line; if wrong: cosmetic one-line move, no behavior change.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/.add/tooling/add.py add-method/tooling/engine_pin.py add-method/tooling/test_add.py add-method/tooling/test_init_resume_pointer.py add-method/tooling/test_init_idempotent_nudge.py
Strategy & known-problem fixes: (1) in `cmd_init`, replace the `_die(...)` at the `state_path.exists() and not args.force` guard with `print(<resume pointer>)` + `return` — exit 0, and because it returns before the `tasks/.mkdir` + survivor-template loop, nothing is re-seeded (trap dodged: must return BEFORE any write, and must NOT fall through to --run-mode/PROJECT.md edits). (2) in `cmd_status` default path, emit the "project exists — do not re-init (use --force to reset)" line when state.json is present (trap: place it in the plain-status path only — do not perturb `--brief`, `--json`, or `--section` outputs). (3) tests RED first (below); the superseded `test_init_resume_pointer` flips `assertNotEqual(code,0)`→`assertEqual(code,0)` + asserts no-write — done in the TESTS phase, flagged as change-request supersession. (4) sync ×3 twins, re-pin ENGINE_MD5 + SEAMS.
Approach (domain strategy): message-layer only — early-return idempotence + one orientation line; correctness-first, zero enforcement-path change.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — cmd_init early-returns (print resume pointer + optional active-task, exit 0) before any seed when state.json exists and not --force; cmd_status default view prints "project exists — do not re-init (use --force to reset)" as its opening line (plain path only). Change-request supersession touched three legacy tests (test_init_resume_pointer, test_add's reinit test → new no-op contract) + the new test_init_idempotent_nudge. ×3 twins synced, ENGINE_MD5→ee4ef957, SEAMS _declared_scope pin 5653→5670.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): a second `add.py init` (no --force) on an initialized project exits 0, writes nothing under .add/, and prints "already initialised … resume: add.py status"; `add.py status` opens with "project exists — do not re-init"; --force still resets; fresh init still seeds — confirmed by test_init_idempotent_nudge (5 asserts) + the superseded test_init_resume_pointer / test_add reinit tests, all green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

