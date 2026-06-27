# TASK: Capture/list/close todos via /add --todo flag

slug: skill-todo-flag · created: 2026-06-27 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
  - `add-method/skill/add/SKILL.md` — canonical orchestrator instructions; the `argument-hint:` frontmatter line + the "Always start here" / "Flag mode" section where the `--todo` fast-path doc goes. THE change is here (prose only).
  - `.claude/skills/add/SKILL.md` + `add-method/src/add_method/_bundled/skill/add/SKILL.md` — byte-identical mirrors; propagated by `cp` (not re-authored).
  - `add-method/tooling/add.py:cmd_todo` (lines 1040–1076) — the engine command the fast-path routes to; UNCHANGED. It already exposes the full mirror: `[--done ID] [text]` + bare = list.
  - NEW guard test `add-method/tooling/test_skill_todo_flag.py` — asserts SKILL.md documents the `--todo` fast-path (presence/format, canonical tree).
Context (working folder):
  - `add-method/tooling/test_skill_lean.py` — core pool (SKILL.md+intake.md) baseline 19675 · ratio 0.88 · target 17314; current 17171 → only 143 B headroom, so the new surface needs a human-approved rebaseline.
  - `add-method/tooling/test_tree_parity.py` + `test_bundle_parity.py` — the 3-tree byte-identical guards that catch un-propagated edits.
Honors (patterns / conventions):
  - 3-tree byte-identical parity (canonical = dogfood = _bundled) — cp, never hand-edit twice.
  - Lean "rebaseline-for-human-approved-new-surface": keep the ratio EXACTLY, grow baseline by surface÷ratio (the won compaction stays pinned).
  - Presence/format guard anchored on a DISCLOSURE-UNIQUE token, not a common word (lesson from security-escalation-disclosure).
  - Fast-lane floor: FROZEN §3 · ≥1 red test before build · recorded §6 gate.
Anchors the contract cites:
  - the `--todo` fast-path block + the `argument-hint:` line in `SKILL.md`
  - `test_skill_todo_flag.py` (the new red guard)
  - `cmd_todo` in `add.py` (the route target, unchanged)

---

## 1 · SPECIFY — the rules

Feature: `--todo` flag on the `/add` skill — a front-of-skill fast-path that routes a todo
capture/list/close straight to the engine, bypassing the orient/status flow.

Must:
  - SKILL.md documents a `--todo` fast-path the orchestrator checks BEFORE orienting: when the
    skill ARGUMENTS begin with `--todo`, route the remainder to `python3 .add/tooling/add.py todo …`,
    print the engine's output, and STOP (no status/resume flow).
  - The doc covers the full mirror of `cmd_todo`: `--todo <text>` → capture · `--todo` (no
    remainder) → list open todos · `--todo --done <id>` → close.
  - Engine errors are surfaced verbatim, never swallowed (`todo_empty` on blank text,
    `todo_unknown` on a bad id) — no silent pass.
  - The `argument-hint:` frontmatter names `--todo`, and the fast-path is byte-identical across
    all three skill trees (canonical · dogfood · _bundled).

Reject:
  - `--todo` with blank text -> engine emits "todo_empty" (surfaced, not hidden)
  - `--todo --done <unknown-id>` -> engine emits "todo_unknown" (surfaced, not hidden)

Accept: Given the canonical SKILL.md, when the lean+parity suite runs, then SKILL.md contains a
`--todo` fast-path block documenting all three sub-forms (capture/list/close) AND `argument-hint`
names `--todo` AND all three trees stay byte-identical — drives the §4 guard test.

Assumptions: ⚠ A presence/format guard proves the INSTRUCTION is written, NOT that the LLM
orchestrator obeys it at runtime — same epistemic blind spot as the security-escalation
disclosure (the engine cannot test an instruction-to-the-AI). If wrong: the doc is present but
ignored and `/add --todo` falls through to orient; cost = one mis-routed invocation, self-evident
to the user. Mitigation: put the fast-path FIRST in SKILL.md (first thing read) + anchor the guard
on a disclosure-unique token. No engine code changes (cmd_todo already does the work).

---

## 3 · CONTRACT — freeze the shape

```
SKILL.md `--todo` fast-path — checked at the TOP of the skill, BEFORE the orient/status flow:

  /add --todo <text>       → run: add.py todo "<text>"     → "captured todo #N: <text>"
  /add --todo              → run: add.py todo              → lists open todos (or "no open todos")
  /add --todo --done <id>  → run: add.py todo --done <id>  → "todo #id done"
  then STOP — do not run status/resume. Engine errors surfaced verbatim
  (todo_empty on blank text · todo_unknown on a bad id).

argument-hint frontmatter: names "--todo <text>" (discoverable cue).

Doc surface: present + byte-identical in all 3 skill trees
  (add-method/skill/add/ · .claude/skills/add/ · add-method/src/add_method/_bundled/skill/add/).

Guard (test_skill_todo_flag.py, canonical tree only):
  - SKILL.md contains a `--todo` fast-path block naming all 3 sub-forms
    (the `--todo` token, the `--done` close form, and capture + list)
  - the `argument-hint:` line names `--todo`
  (presence/format only — it cannot prove the orchestrator OBEYS, see §1 Assumptions)

No engine change: cmd_todo (add.py:1040–1076) already implements capture/list/close.
```

`Least-sure flag surfaced at freeze:` [contract] how tightly the guard pins wording. Too strict →
a future lean-compaction reword trips the fence (cost: a fence edit); too loose → vacuous pass,
doc drift undetected (cost: silent regression). Chosen middle: assert the disclosure-unique multi-token
set (`--todo` + `--done` + capture/list semantics), not the exact sentence.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: test_skill_todo_flag.py — 4 cases: the fast-path block marker · the 3 sub-forms
(capture/list/close) · routes to `add.py todo` · `argument-hint` names `--todo`. RED before build:
3/4 fail (the `add.py todo` route token already exists in the Flag-mode line, so that 1 case is
green from the start; the 3 meaningful guards are red — verified).
Tests live in: `add-method/tooling/test_skill_todo_flag.py` · MUST run red (missing doc) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/skill/add/SKILL.md` · `.claude/skills/add/SKILL.md` · `add-method/src/add_method/_bundled/skill/add/SKILL.md` · `add-method/tooling/test_skill_lean.py`
Code lives in: `add-method/skill/add/SKILL.md` (canonical prose) → cp to the 2 mirrors · Constraints: change no §4 test, no frozen §3; SKILL.md prose only + the core lean-fence rebaseline (human-approved new surface, ratio 0.88 kept).

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 2102/0; §4 test_skill_todo_flag.py + frozen §3 unchanged during build (tripwire clean); changed files (SKILL.md ×3 + test_skill_lean.py) all within §5 scope
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic — the guard asserts the disclosure-unique `--todo` fast-path marker + all 3 sub-forms + route + arg-hint (the honest blind spot — it can't prove runtime obedience — is disclosed in §1, not papered over)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — prose + a test-fence only; NO engine change (ENGINE_MD5 untouched), zero new deps

Build expectations (from §1 Accept + §3 CONTRACT): canonical SKILL.md gains a `--todo` fast-path block
(capture/list/close routing to `add.py todo`, then STOP) + `argument-hint` names `--todo`; cp'd byte-identical
to the 2 mirrors; core lean fence rebaselined (ratio kept). Confirmed by: test_skill_todo_flag (4/4 green) +
test_skill_lean + test_tree_parity + test_bundle_parity all green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-27
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
