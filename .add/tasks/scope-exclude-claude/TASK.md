# TASK: Prune .claude from the scope walk

slug: scope-exclude-claude · created: 2026-06-29 · stage: mvp
autonomy: auto   <!-- Multi-component repo? add a `component: <name>` line (declared in .add/components.toml) to bind this fast task to a component — its root joins §5 Scope and its green-bar/verify surface at the gate. Omit for single-component projects. -->
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add.py:_SCOPE_EXCLUDE_DIRS` (~3673) — the tuple `os.walk` prunes by dir-name at any depth inside `_scope_walk` (~3973-3993); today `(".git", ".add", "__pycache__", "node_modules", ".serena", ".next", "coverage", "test-results")`. `.claude` is ABSENT, so the scope walk descends into Claude Code's internal dir — notably `.claude/worktrees/<wt>/` (linked git worktrees: full branch checkouts), whose files appear/change between the tests→build snapshot and the verify gate, producing a spurious `scope_violation` in `_scope_findings` (~3996-4017).
Context (working folder): observed live this session — `persist-run-mode`'s verify gate refused on `.claude/worktrees/image-docs/*` + `.claude/worktrees/debug-loop/*` (gitignored, unrelated worktrees). Recovery was a re-snapshot; this is the durable fix.
Honors (patterns / conventions): the exclude set already prunes other tools' internal dirs (`.serena`) + VCS/build state (`.git`, `.add`, `node_modules`); `.claude` is the same class (Claude Code config/skills/worktrees — never a task's declared source). BUILD TARGET = engine parity (3 git-tracked trees, ENGINE_MD5-pinned): edit CANONICAL `add-method/tooling/add.py`, then re-sync `_bundled/tooling/` + `.add/tooling/` byte-identical + re-pin `engine_pin.py` (ENGINE_MD5 only — `add_engine/*` untouched → ENGINE_PKG_MD5 unchanged).
Anchors the contract cites: `_SCOPE_EXCLUDE_DIRS` · `_scope_walk(rootp)` · `_scope_findings`

---

## 1 · SPECIFY — the rules

Feature: Prune `.claude` from the scope walk
Must:
  - `_SCOPE_EXCLUDE_DIRS` includes `.claude`, so `_scope_walk(root)` prunes it at ANY depth (like `.git`/`.add`/`.serena`) — the returned `{relpath: md5}` map never contains a key under `.claude/`.
  - consequently a file created or modified anywhere under `.claude/` (e.g. `.claude/worktrees/<wt>/<f>`) is never counted as a scope touch, so `_scope_findings` never reports it as an out-of-scope touch.
Reject:
  - (none — this only WIDENS an existing prune set; no new input, no new error code, no behavior removed)
Accept: Given a project whose tree has a file under `.claude/worktrees/wt/x.txt`, When `_scope_walk(project_root)` runs, Then no returned key starts with `.claude/` (the dir is pruned).
Assumptions: ⚠ excluding ALL of `.claude` (not only `.claude/worktrees`) — `.claude/` is Claude Code config/skills/worktrees by convention, never tracked task source (mirrors the `.serena` prune); if wrong: a project that unconventionally keeps source under `.claude/` would be invisible to the scope gate (fail-open for that file). Cost: negligible — no real project puts source there.

---

## 3 · CONTRACT — freeze the shape

```
_SCOPE_EXCLUDE_DIRS  (add.py, the os.walk prune set in _scope_walk)
  = (".git", ".add", ".claude", "__pycache__", "node_modules",
     ".serena", ".next", "coverage", "test-results")
  # ".claude" is NEW — pruned at any depth, same class as .git/.add/.serena

_scope_walk(rootp: Path) -> dict[str, str]   # {project-root-relative path: md5}
  POST: no returned key starts with ".claude/"  (the dir is pruned)
  => _scope_findings out-of-scope touches never include a .claude/ path
No rejection path / no new error code — a pure widening of an existing prune set.
```

`Least-sure flag surfaced at freeze:` [spec] excluding ALL of `.claude` rather than only `.claude/worktrees` — chosen for consistency with the dir-name-keyed prune set (`.serena`, `.git`); if wrong, source kept under `.claude/` (implausible) is unguarded by the scope gate. Cost: negligible.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: test_scope_walk_prunes_claude — arrange a temp project (`.add` init) with a file at `<root>/.claude/worktrees/wt/x.txt`; call `add._scope_walk(root)`; assert NO returned key starts with `.claude/` (Accept line's Then). RED before the fix (`.claude` is walked → the key is present), GREEN after. Render-blind: asserts on the returned path map, not on the constant's internals.
Tests live in: `add-method/tooling/test_scope_exclude_claude.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy & known-problem fixes: 1. write the red test (`.claude/worktrees/wt/x.txt` present in `_scope_walk` output) · 2. add `.claude` to `_SCOPE_EXCLUDE_DIRS` in canonical add.py → green · 3. `prepare_bundle.py` to re-sync `_bundled` · 4. copy canonical add.py → `.add/tooling/add.py` (mirror; add_engine untouched) · 5. re-pin ENGINE_MD5 (add.py changed) — ENGINE_PKG_MD5 UNCHANGED (no add_engine edit) · 6. full suite green. KNOWN TRAP: only add.py changes, so re-pin ENGINE_MD5 ONLY; do not disturb ENGINE_PKG_MD5.
Strategy actually used: as planned — red test → add `.claude` to `_SCOPE_EXCLUDE_DIRS` (+ a maintainer comment) → prepare_bundle + dogfood-sync → re-pin ENGINE_MD5 only (ENGINE_PKG_MD5 unchanged). One extra step: re-snapshotted the scope baseline after the engine sync, so the pre-fix snapshot's `.claude` entries didn't read as deletions at this task's own gate.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite **2295 passed, OK**; §3 frozen + the red test untouched after build
- [x] green was EARNED — the test arranges a real `.claude/worktrees/wt/x.txt` + a sibling `src.py`, asserts the walk DOES return `src.py` (proves it ran) and returns NO `.claude/` key; RED before the fix, GREEN after. Not vacuous, not overfit, not stubbed.
- [x] no exposed secrets, injection openings, or unexpected dependencies — a one-token widening of an existing prune tuple; no I/O, no deps, no new error path

Build expectations (from §1 Accept + §3 CONTRACT): `_scope_walk(root)` over a tree containing `.claude/worktrees/wt/x.txt` returns no key under `.claude/` (while still returning ordinary files) — confirmed by test_scope_exclude_claude (RED→GREEN) + the full suite; and live, the spurious `scope_violation` on Claude Code worktrees no longer fires. All 3 engine trees byte-identical (6ca872fa…), ENGINE_MD5 re-pinned, ENGINE_PKG_MD5 unchanged.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-29
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
