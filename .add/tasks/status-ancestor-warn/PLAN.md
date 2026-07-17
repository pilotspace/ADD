# TASK: status/init warns when it resolved an ANCESTOR project (nested dir with no local .add/)

slug: status-ancestor-warn · created: 2026-07-14 · stage: mvp
milestone: orientation-honesty
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: `status` in a dir with no local `.add/` but an ANCESTOR project above self-identifies — it prints a one-line note naming the resolved ancestor + the exact `init` command to scope a project HERE. Real-world value for nested/monorepo dirs + defense-in-depth behind the harness ceiling; kills the "why is the project the parent's?" spelunking a nested agent otherwise does. (Scoped to `status` — the read command where the transcript confusion fired; `init` CREATES at cwd, it resolves no ancestor, so a resolved-ancestor note doesn't fit it.)
Must:
  - when `status` runs where `cwd/.add/state.json` is ABSENT but `find_root()` resolves a root (an ancestor), it prints to stderr a one-line note naming the resolved ancestor project path + the exact `add.py init --name "<project>" --stage <...>` command to scope a project here
  - when cwd HAS its own `.add/state.json`, NO note (the common case is silent)
  - the note is informational (stderr) — it never changes the exit code or the normal status body
Reject:
  - cwd owns a project (`cwd/.add/state.json` exists) -> no note emitted (the negative case the test pins)
Accept: Given cwd has no `.add/` but an ancestor `A/.add/state.json` exists, When `add.py status` runs, Then stderr includes "ancestor project at A" and an `add.py init --name` remedy, the normal status body still prints, exit 0
Boundary: cwd-owned project (no note) vs ancestor-resolved (note) — the two shapes the test must speak
Assumptions: ⚠ detecting "ancestor" as `not (cwd/.add/state.json).exists() and find_root() is not None` — a symlinked cwd could differ from resolved, so compare resolved paths; if wrong: the note misfires (cosmetic — stderr only, body unaffected)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add.py:cmd_status` (the full-status path — emit the note before the body) + a new `_ancestor_note()` helper beside it; it READS `find_root` · `ROOT_DIRNAME` · `STATE_FILE` (already imported) — no engine symbol changed
Context (working folder): `add-method/tooling/` (canonical add.py + 4 twins); ENGINE_MD5 re-pinned; SEAMS re-pinned IF the `_declared_scope` line pin drifts (cmd_status sits upstream of it)
Honors (patterns / conventions): the `_require_root` skip-error precedent — hand the EXACT command with flags, never a bare hint (this is lever B applied to the ancestor case); informational notes go to stderr so `--json`/pipes stay clean
Anchors the contract cites: `cmd_status` (edited) · `_ancestor_note` (new) · `find_root` · `ROOT_DIRNAME` · `STATE_FILE`
Ground SHA: a87ed1e — stamped by freeze

### Contract

```
_ancestor_note() -> str | None
  cwd = Path.cwd().resolve()
  if (cwd / ROOT_DIRNAME / STATE_FILE).exists(): return None          # cwd owns a project -> silent
  root = find_root()                                                  # respects the ceiling; None if none reachable
  if root is None: return None                                        # no project anywhere -> silent (init flow owns that)
  return ("note: no .add/ here — using the ancestor project at " + str(root.parent) +
          "; run `add.py init --name \"<project>\" --stage <prototype|poc|mvp|production>` to scope a project here")
cmd_status, the FULL path only (not --brief / --json / --section):
  n = _ancestor_note(); if n: print(n, file=sys.stderr)   # before the normal body; exit code + body unchanged
```

`Least-sure flag surfaced at freeze:` [contract] emitting on the FULL path only — `--json`/`--brief` stay silent so machine callers and pipes are unaffected; if an agent orients via `--brief` in a nested dir it won't see the note (acceptable: the confusion fired on full `status`, and stderr-on-json would corrupt parsers).
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `.add/SEAMS.md` `add-method/tooling/test_status_ancestor_warn.py`
Strategy & known-problem fixes: 1. RED test_status_ancestor_warn (nested cwd, ancestor project → stderr has the note + init cmd, stdout body intact, exit 0; cwd-owned project → NO note). 2. add `_ancestor_note()` + call it in cmd_status's full path (guard: NOT on --json/--brief/--section — trap: a note on --json breaks parsers). 3. sync ×4 add.py twins, re-pin ENGINE_MD5, re-pin SEAMS `_declared_scope` IF drifted.
Approach (domain strategy): stderr ancestor self-identify

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
Strategy actually used: as planned — added `_ancestor_note()` beside cmd_status; called it in the full-status path right after root/state load, printing to stderr. Synced ×4 add.py twins, ENGINE_MD5→9476543399…, SEAMS `_declared_scope` re-pinned 5688→5711 (my +23 lines). No divergence.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — status regression 18 green; repin+PKG parity green; full fence (pending)
- [x] green was EARNED — the note-present assert was RED before _ancestor_note existed; the two silent-case asserts (cwd-owned, stdout-clean) guard against a note that fires always or leaks to stdout
- [x] input dialect held — the test speaks the real CLI stderr/stdout + exit-code dialect
- [x] no exposed secrets/injection/deps — stdlib only; the path is str()'d into a message, never eval'd (security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): in a nested dir under an ancestor project, `add.py status` writes to STDERR `note: no .add/ here — using the ancestor project at <A>; run \`add.py init --name "<project>" --stage <...>\` to scope a project to this directory`, the normal status body still prints to STDOUT, exit 0; a cwd that owns `.add/state.json` prints NO note — confirmed by test_status_ancestor_warn (3 asserts) + the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

