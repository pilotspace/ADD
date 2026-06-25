# TASK: Capture todo tasks (lightweight backlog primitive)

slug: todo-capture · created: 2026-06-25 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- GREENFIELD — no `todo` command and no `todos` state key exist today (verified by grep).
- command pattern: `sub.add_parser("<name>", help=…)` + `parser.set_defaults(func=cmd_<x>)`; dispatched via `args.func(args)` in `main`. Model verb: `cmd_autonomy` (1561) — a small `_require_root` → `load_state` → mutate → `save_state` → print verb.
- helpers reused: `_require_root`, `load_state`, `save_state` (603), `_now()` (213), `_die`.
- storage: a NEW top-level `state["todos"]` array. State schema is drift-TOLERANT (test_state_hardening: status survives a missing key) and has NO top-level key lock — so adding a key is safe (unlike the check-json surface lock).
- engine mirrors (same discipline as standalone-fast-task): canonical `add-method/tooling/add.py` → `.add/tooling/add.py` + `_bundled` (prepare_bundle.py) → re-pin `engine_pin.py:ENGINE_MD5`.

Anchors the contract cites: a new `cmd_todo` verb · the `state["todos"]` array shape · the `todo` subparser.

---

## 1 · SPECIFY — the rules

Feature: Todo capture — a lightweight backlog primitive (capture an idea without sizing it into a task)
Must:
  - `add.py todo "<text>"` captures a todo: appends `{id, text, created, status:"open"}` to `state["todos"]`; prints `captured todo #<id>: <text>`.
  - `add.py todo` (no text) LISTS open todos (one `#<id>  <text>` line each); empty → `no open todos`.
  - `add.py todo --done <id>` closes a todo (status→"done"); prints `todo #<id> done`.
Reject:
  - blank/whitespace-only capture text → "todo_empty"
  - `--done <id>` for a missing/closed id → "todo_unknown"
Accept: Given a project, When `add.py todo "seed soul.md if missed when update/init ADD into project"`, Then it is captured as todo #1 (open) and `add.py todo` lists it; then `add.py todo --done 1` closes it and `add.py todo` shows `no open todos`.
Assumptions: ⚠ scope = capture · list · done ONLY (no promote-to-task, no `status` board integration) — kept lean for the fast lane; if wrong, both are purely ADDITIVE follow-ups. (This task's first real todo IS the SOUL.md-seed idea above — dogfooded at the gate.)

---

## 3 · CONTRACT — freeze the shape

```
state["todos"] : list of { id:int (1-based = max(existing)+1), text:str, created:<iso>, status:"open"|"done" }

add.py todo "<text>"     -> append {open}; print: captured todo #<id>: <text>
                            blank text            -> _die "todo_empty: a todo needs text"
add.py todo              -> list OPEN todos as "#<id>  <text>"; none -> "no open todos"
add.py todo --done <id>  -> set status=done; print "todo #<id> done"
                            id not an open todo   -> _die "todo_unknown: no open todo #<id>"

Engine parity: edit canonical add.py; mirror to .add + _bundled (prepare_bundle.py); re-pin ENGINE_MD5.
`todos` is a NEW additive state key — state schema is drift-tolerant, no key lock to update.
```

`Least-sure flag surfaced at freeze:` [spec] scope = capture·list·done with NO promote-to-task and NO `status` board count — RESOLVED at freeze: lean scope (promote/status deferred as additive follow-ups).
Status: FROZEN @ v1 — approved by Tin Dang (AskUserQuestion freeze, capture/list/done), 2026-06-25.
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: `test_todo_capture.py` —
  (a) `todo "seed soul.md…"` → captured as #1 open; `todo` lists it;
  (b) `todo` when empty → "no open todos";
  (c) `todo --done 1` → "todo #1 done"; `todo` then shows "no open todos";
  (d) blank text → exit≠0 "todo_empty"; `--done 99` → exit≠0 "todo_unknown";
  (e) a second `todo "..."` after #1 → gets id #2 (max+1, stable even after #1 closed).
Red first: today `add.py todo` is an unknown subcommand (argparse error) — no `cmd_todo` exists.
Tests live in: `add-method/tooling/test_todo_capture.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_todo_capture.py` · `add-method/tooling/test_min_pillar.py`
Note: test_min_pillar.py added at build — its LIFECYCLE subcommand-coverage surface lock must classify the new `todo` verb (reads/writes state, never docs/); declared before re-anchoring the state.json scope anchor.
Code lives in: `add-method/tooling/` (+ mirrored trees)   ·   Constraints: change no existing test, no contract; allow-list packages only; additive `todos` state key only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 1753/0; the test_min_pillar LIFECYCLE edit is a SURFACE-lock classification (a new verb must be exercised under the read-spy), not a weakening
- [x] green was EARNED — the test asserts observable behavior (capture→#1 open→listed · done closes · blank/unknown rejected · ids = max+1 stable); dogfood-captured the real SOUL.md todo as backlog #1
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure state read/write + prints; no I/O beyond state.json, no deps, no security surface

Build expectations (from §1 Accept + §3 CONTRACT): `add.py todo "<text>"` captures into `state["todos"]` and `add.py todo` lists open items; `--done <id>` closes; blank→todo_empty, bad id→todo_unknown — confirmed by `test_todo_capture.py` red→green + full suite + tree-parity/pin green. Dogfood: the SOUL.md-seed idea is captured as the first real todo at the gate.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on evidence, autonomy: auto) · date: 2026-06-25
OBSERVE: [ADD · open] `todos` are captured but not yet surfaced in `status` — a future `status` todo-count would make the backlog visible at orient time (deferred follow-up, as flagged at freeze). First real backlog entry = the SOUL.md-seed idea.
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
