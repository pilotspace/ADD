# TASK: Prompt the user to commit the .add/ folder at setup/init

slug: setup-commit-prompt · created: 2026-06-25 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- `add-method/tooling/add.py:cmd_init` (943-1011) — the setup bootstrap. After `save_state` + guideline inject it prints a closing next-step in TWO branches: brownfield ("existing code detected … add.py lock") and greenfield ("next: open Claude Code, run `/add` …"). The function ends at 1011. NO reminder to commit `.add/` to git anywhere.
- The `.add/.gitignore` seed already keeps transient files out of git (see gitignore-bak-seed) — so committing `.add/` is safe; the reminder can say the transients are already ignored.
- engine 3 trees + `engine_pin.py:ENGINE_MD5` — cmd_init is engine source, so the change re-pins.

Anchors the contract cites: the cmd_init closing reminder line · printed once for BOTH branches.

---

## 1 · SPECIFY — the rules

Feature: setup reminds the user to commit the .add/ folder to git
Must:
  - `add.py init` prints, at the end of its output, a reminder to commit the `.add/` folder to git so the team shares the ADD state — noting its transient files are already `.gitignore`d.
  - The reminder shows for BOTH the greenfield and brownfield branches (one line after the branch-specific next-step), so every fresh setup sees it.
Reject:
  - (none — additive output line; no error code, no behavior gate. Idempotent: re-`init --force` prints it again, harmless.)
Accept: Given `add.py init` in a fresh dir, When it finishes, Then its output contains a reminder to commit `.add/` (e.g. matches /commit .* \.add/ to git/), for both greenfield and brownfield.
Assumptions: none material — biggest risk: it is a print, not an interactive prompt (init is non-interactive); a reminder line is the faithful, testable form of "ask the user to commit .add/". If a true interactive prompt is wanted, that belongs in the installer's clack flow (separate task).

---

## 3 · CONTRACT — freeze the shape

```
add.py cmd_init — after the brownfield/greenfield if/else (≈line 1011), one closing line
printed in BOTH paths:

  print("tip: commit the .add/ folder to git so your team shares the ADD state "
        "(its transient files are already .gitignored).")

+ mirror 3 trees (prepare_bundle + cp) + re-pin ENGINE_MD5.

Test: `add.py init` output (greenfield AND brownfield) contains a commit-.add reminder.
```

`Least-sure flag surfaced at freeze:` [spec] a printed REMINDER vs an interactive prompt — init is non-interactive, so a closing tip line is the testable, deterministic form; a true ask-and-wait prompt would live in the installer clack flow (out of scope, notable as a follow-up).
Status: FROZEN @ v1 — approved by Tin Dang (AskUserQuestion freeze), 2026-06-25.
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: `test_setup_commit_prompt.py` — run `add.py init` in a temp dir (greenfield) and capture
stdout; assert it contains a commit-`.add/` reminder (regex `commit .*\.add`). Also assert it shows
in a brownfield dir (drop a stray source file so `_is_brownfield` trips) — both branches.
Red first: cmd_init prints no commit reminder today.
Tests live in: `add-method/tooling/test_setup_commit_prompt.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_setup_commit_prompt.py`
Code lives in: `add-method/tooling/`   ·   Constraints: one additive print in cmd_init (both branches); no behavior/gate change; mirror 3 trees + re-pin; no new dependency.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 1773/0 (+2); 3-tree md5 ee6e2c58 + pin match.
- [x] green was EARNED — the test captures REAL init stdout and asserts the commit-.add reminder via regex in BOTH the greenfield and brownfield branches (the print sits after the if/else, so both paths hit it). No vacuous assert.
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — a single additive print; no logic/gate change, no input, no dep.

Build expectations (from §1 Accept + §3 CONTRACT): a fresh `add.py init` (greenfield AND brownfield) ends with a tip reminding the user to commit `.add/` to git — CONFIRMED by `test_setup_commit_prompt.py` red→green capturing init stdout in both branches.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on evidence, autonomy: auto) · date: 2026-06-25
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
