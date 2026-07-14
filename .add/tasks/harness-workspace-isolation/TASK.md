# TASK: WM runner isolates the workspace from any ancestor .add/ (bounded root-walk)

slug: harness-workspace-isolation · created: 2026-07-14 · stage: mvp
milestone: orientation-honesty
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: a benchmark WM workspace nested under an ancestor `.add/` resolves its OWN project (absent-then-init'd), not the parent — via a bounded root-walk the harness scopes to the workspace. Kills the 7-13 startup-confusion cmds/rep the pre-measure anatomy found were HARNESS-induced (workspace lives inside AIDD-Book's own `.add/` tree), so the re-measure meters the method, not the nesting.
Framings weighed: env ceiling on `find_root` consumed by the harness (chosen — minimal, general, zero-behavior-change when unset; `init` already writes at cwd so only the pre-init READ walk leaks) · relocate runs outside the repo tree (breaks archived-run paths + carry-forward) · pre-seed a `.add/` boundary in the workspace (would read as an existing project / change the arm's init task)
Must:
<must>
  - `find_root` honors an env ceiling `ADD_ROOT_CEILING=<dir>`: the upward walk visits cur..ceiling INCLUSIVE and never ascends above it — a `.add/state.json` in an ancestor ABOVE the ceiling is not resolved (returns None if that is the only project)
  - env unset (every real end-user invocation): `find_root` walks cur..filesystem-root exactly as today — byte-for-byte behavior unchanged (the ceiling is opt-in, harness-only)
  - the WM runner sets `ADD_ROOT_CEILING=<workspace_dir>` in the agent subprocess env (`_invoke_once` Popen), so the agent's pre-init `status` in a fresh nested workspace resolves NO project (prints "run init") instead of the parent AIDD-Book project
  - `io_state.py` synced across all 4 engine twins byte-identical; `ENGINE_PKG_MD5` re-pinned (add_engine package digest); `ENGINE_MD5` UNCHANGED (add.py not touched); SEAMS re-pinned only if an add.py line pin drifted (it won't — the edit is in io_state.py)
</must>
Reject:
<reject>
  - a `.add/state.json` strictly above the set ceiling -> find_root returns `None` (the ancestor project is NOT resolved) — the negative behavior the whole task turns on
  - ceiling set but not on cwd's ancestor chain -> the break never fires; the walk proceeds to filesystem root as if unset (fail-open, no error — the ceiling only ever CONSTRAINS, never redirects)
</reject>
After:
<after>
  - a fresh nested workspace resolves its own project after `init`; a re-run of the sixphase anatomy shows zero `find_root`/`STATE_FILE` engine-internals spelunking at startup
  - all existing add.py/add_engine tests stay green (env unset in every existing test) — the change is invisible outside the harness
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the startup confusion is caused ENTIRELY by `find_root`'s unbounded upward walk, not by `init` mislocating the new `.add/` — lowest confidence because I'm inferring cause from the transcript's grep targets; mitigated: `cmd_init` uses `base = Path(args.dir).resolve()` (cwd), so init already writes at the workspace regardless — verified in source; if wrong: the ceiling alone wouldn't fix it and init would also need scoping (add.py change + ENGINE_MD5 re-pin)
  - [ ] the harness `_invoke_once` Popen is the single agent-launch point (setup steps run uv/pip, never add.py) — so one env injection covers every agent add.py call; confirm by reading core.py's invoke path
  - [ ] `ADD_ROOT_CEILING` is not already a meaningful env name elsewhere in the engine — confirm by grep before naming
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: ancestor project above the ceiling is not resolved   # M1, R1
  Given a dir W with no .add/ of its own, nested under A where A/.add/state.json exists
  And the env ADD_ROOT_CEILING is set to W
  When find_root() is called from inside W
  Then it returns None
  And A/.add/state.json is neither read as the project nor modified

Scenario: env unset preserves the legacy walk   # M2
  Given the same W nested under A/.add/state.json
  And ADD_ROOT_CEILING is unset
  When find_root() is called from inside W
  Then it returns A/.add   # byte-for-byte the behavior shipped today

Scenario: the workspace's own project resolves once init has run   # M1
  Given ADD_ROOT_CEILING is set to W and W/.add/state.json now exists
  When find_root() is called from W or a subdir of W
  Then it returns W/.add   # the ceiling constrains the top, never the workspace itself

Scenario: the runner scopes the agent env to the workspace   # M3
  Given execute_wm drives a fake agent that records $ADD_ROOT_CEILING to a file
  When the WM run completes
  Then the recorded value equals the run's workspace dir
  And no existing runner behavior (record/timeout/carry-forward) changes
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add_engine/io_state.py:find_root(start=None)` — add an `ADD_ROOT_CEILING` env-bounded break to the existing `for d in (cur, *cur.parents)` walk (×4 twins); `engine_pin.py:ENGINE_PKG_MD5` — re-aim the package-digest literal (×4 twins; `ENGINE_MD5` untouched); `benchmark/runner/core.py:_invoke_once` — pass `env={**os.environ, "ADD_ROOT_CEILING": str(cwd)}` to the agent `subprocess.Popen` (os already imported)
Context (working folder): the engine `add_engine/` package (4 twins) + the benchmark runner; no docs/config touched
Honors (patterns / conventions): the existing `os.environ.get(...)` opt-in idiom (cf. `ADD_NO_UPDATE_CHECK` in add.py, `NO_COLOR` in render.py) — a default-unset env that changes nothing when absent; twin-sync + `ENGINE_PKG_MD5` re-pin per engine-package edit (SEAMS unaffected — no add.py line moves)
Seams consulted: `.add/SEAMS.md` — no `_declared_scope`/add.py line pin drifts (edit is confined to io_state.py); the package parity gate is `test_engine_extract_md5.py` (TREES = canonical · `.add/tooling` · `_bundled`)
Anchors the contract cites: `find_root` · `ROOT_DIRNAME` · `STATE_FILE` · `_invoke_once` · `os.environ`
Issues/Risks: the ceiling must be INCLUSIVE (break AFTER visiting the ceiling dir) or the workspace's own post-init `.add/` would be skipped; the `resolve()` on both cwd and ceiling must match (symlinked tmpdirs on macOS — `/var` vs `/private/var`) so compare resolved paths; env unset MUST be a no-op or every existing add_engine test breaks
Related intent: orientation-honesty milestone rationale + `benchmark/results/2026-07-callres-preflight-anatomy.md` (lever A — harness-induced startup confusion)
Ground SHA: e9fc44a — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
find_root(start: Path | None = None) -> Path | None
  cur = (start or Path.cwd()).resolve()
  ceil = Path(os.environ["ADD_ROOT_CEILING"]).resolve() if os.environ.get("ADD_ROOT_CEILING") else None
  for d in (cur, *cur.parents):
      if (d / ROOT_DIRNAME / STATE_FILE).exists(): return d / ROOT_DIRNAME   # unchanged match
      if ceil is not None and d == ceil: break                              # NEW: stop at the ceiling (inclusive)
  return None
  · env unset  -> ceil is None -> the break never fires -> walk cur..fs-root (LEGACY, byte-identical)
  · env = W    -> ancestor above W never visited -> None when the only .add/ is above W; W/.add/ still resolves

benchmark/runner/core.py :: _invoke_once
  subprocess.Popen(argv, cwd=str(cwd), env={**os.environ, "ADD_ROOT_CEILING": str(cwd)}, …)   # else unchanged
```

Glossary deltas: `root-walk ceiling: an opt-in env (ADD_ROOT_CEILING) that bounds find_root's upward search at a dir inclusive — the mechanism that isolates a nested workspace from an ancestor project`
`Least-sure flag surfaced at freeze:` [contract] the resolved-path equality of the ceiling break (`d == ceil`) — on macOS a tmpdir resolves `/var`→`/private/var`, so both `cur` and `ceil` MUST be `.resolve()`d or the break silently never fires; the hard edge is that env-unset stays byte-identical to the legacy walk (any regression there breaks every add_engine test).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/add_engine/io_state.py` `.add/tooling/add_engine/io_state.py` `add-method/.add/tooling/add_engine/io_state.py` `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `benchmark/runner/core.py` `add-method/tooling/test_findroot_ceiling.py` `benchmark/tests/test_workspace_isolation.py`
Strategy (ordered batches): the build ORDER the Contract doesn't carry — 1. RED both tests. 2. edit `find_root` in the CANONICAL twin. 3. sync byte-identical → 3 io_state twins. 4. `env=` on `_invoke_once`. 5. recompute `package_digest` → `ENGINE_PKG_MD5` × the twins. 6. green: targeted + `test_engine_extract_md5` (PKG parity) + `test_engine_extract_io_state` + benchmark runner suite → full fence.
Approach (domain strategy): env-ceiling — see §1 Framings weighed (chosen over run-relocation / boundary-seeding); no re-narration here.
Data strategy: none — no persisted shape (Contract signature unchanged).
Pattern: default-unset env opt-in (Grounding Honors) + engine-package twin-sync/`ENGINE_PKG_MD5` re-pin.
Optimization stance: correctness-first, no budget — trusted-least facet is the resolve()-equality edge, surfaced in the §3 Least-sure flag (not repeated here).
Persona: methodology-engine-dev — load-bearing root-resolution → minimal guard, honest pins.
Spawn isolation (default): none — inline build (single focused change).
Known-problem fixes: (unique to build) stray `_bundled/__pycache__/add.cpython-*.pyc` regenerates on import → `find _bundled -name __pycache__ -exec rm -rf` before the PKG parity assertion. (Ceiling inclusiveness + resolve()-equality live in §3 Issues/Risks + the Least-sure flag.)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned — added an `ADD_ROOT_CEILING` env read to `find_root` (resolve() both sides, break AFTER the state.json check so the ceiling is inclusive), synced byte-identical to the 3 other io_state twins (md5 6f06f2e7…), added `env={**os.environ, "ADD_ROOT_CEILING": str(cwd)}` to `_invoke_once`'s Popen, recomputed `package_digest`→`ENGINE_PKG_MD5` 955023db… across all 4 engine_pin twins (ENGINE_MD5 untouched). No divergence. RED→green: engine test_ancestor_above_ceiling_not_resolved + harness env-unset both flipped; env-unset legacy + off-chain fall-open + workspace-own asserts green throughout.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling fence 3601 passed (FENCE_EXIT=0); benchmark suite 189 green; engine targeted 28 green
- [x] coverage did not decrease — 2 new tests added, none removed/weakened
- [x] no test or contract was altered during build — find_root/_invoke_once/engine_pin only; tests untouched since red
- [x] the green was EARNED — the ancestor-above-ceiling assert resolved the PARENT before the code (RED), returns None after; env-unset asserts the byte-identical legacy path so a broken guard would fail, not pass
- [x] concurrency / timing — none; a pure per-call env read, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib os only; env value is a path str, never eval'd
- [x] layering & dependencies follow CONVENTIONS.md — os.environ opt-in mirrors ADD_NO_UPDATE_CHECK/NO_COLOR
- [x] a person reviewed and approved the change — Tin Dang approved the frozen §3 contract

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] with `ADD_ROOT_CEILING=W` set, `io_state.find_root(W)` returns `None` when the only `.add/state.json` is in an ancestor above W — confirmed by test_findroot_ceiling.test_ancestor_above_ceiling_not_resolved flipping RED→green
- [ ] with the env UNSET, `find_root(W)` still returns the ancestor `A/.add` byte-identically — confirmed by test_env_unset_preserves_legacy_walk staying green + the full add_engine suite unbroken
- [ ] after `init`, `find_root(W)` and `find_root(W/sub)` return `W/.add` even with the ceiling set — confirmed by test_workspace_own_project_resolves_under_ceiling
- [ ] a WM run exports `ADD_ROOT_CEILING=<workspace>` into the agent process — confirmed by the fake agent's recorded `ceiling_seen.txt` == the workspace dir (test_workspace_isolation)
- [ ] `ENGINE_PKG_MD5` equals `package_digest` across all 3 gated trees; `ENGINE_MD5` unchanged — confirmed by test_engine_extract_md5 + test_engine_repin_parity green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — tests use real nested tmpdirs + real Path/env, the same dialect the runtime sees (not synthetic path strings) — resolve()-equality exercised for real
- [x] WIRING (code) — `ADD_ROOT_CEILING` is read in `find_root` (×4 twins) and written in `_invoke_once`; the harness test proves the write reaches the agent, the engine test proves the read bounds the walk
- [x] DEAD-CODE (code) — no orphaned symbol; the env read + break are on the live walk path
- [ ] SEMANTIC — n/a (code task)

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves — `find_root`, `ROOT_DIRNAME`, `STATE_FILE` in io_state.py; `_invoke_once`, `os.environ` in core.py — all present, edited in place
- [x] no anchor moved/renamed since Ground SHA e9fc44a

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed the guard's failure modes — (1) an off-chain ceiling must not redirect (test_ceiling_off_the_chain_falls_open green), (2) the ceiling must be inclusive so the workspace's own post-init root still resolves (test_workspace_own_project_resolves_under_ceiling green incl. subdir), (3) env-unset must be byte-identical (test_env_unset + 189 benchmark + engine parity green). A vacuous pass is impossible: the RED test resolved the PARENT project before the code existed.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — env value is a filesystem path used only for a Path() compare, never eval'd/shell'd; no new dep; a malicious ADD_ROOT_CEILING can only NARROW resolution (fail-closed to None), never escalate
2. Concurrency: CLEAR — stateless per-call env read; no shared mutation
3. Architecture: CLEAR — opt-in env mirrors the engine's existing os.environ idiom; the harness consumes an engine capability, no new coupling
Verdict: PASS
Residue: none
Binding: advisory — architecture (a benchmark-enforcement + engine-package change; not mechanical)

### GATE RECORD
Reported: yes — build evidence rendered (fence 3601 green, refute EARNED, advisor PASS) before this outcome
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose env ceiling on `find_root` consumed by the harness; rejected relocate runs outside the repo tree (breaks archived-run paths + carry-forward) · pre-seed a `.add/` boundary in the workspace (would read as an existing project / change the arm's init task)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: env-ceiling — see §1 Framings weighed (chosen over run-relocation / boundary-seeding); no re-narration here.
- [AI] build — data strategy: none — no persisted shape (Contract signature unchanged).
- [AI] build — pattern: default-unset env opt-in (Grounding Honors) + engine-package twin-sync/`ENGINE_PKG_MD5` re-pin.
- [AI] build — optimization stance: correctness-first, no budget — trusted-least facet is the resolve()-equality edge, surfaced in the §3 Least-sure flag (not repeated here).
- [AI] build — strategy used: as planned — added an `ADD_ROOT_CEILING` env read to `find_root` (resolve() both sides, break AFTER the state.json check so the ceiling is inclusive), synced byte-identical to the 3 other io_state twins (md5 6f06f2e7…), added `env={**os.environ, "ADD_ROOT_CEILING": str(cwd)}` to `_invoke_once`'s Popen, recomputed `package_digest`→`ENGINE_PKG_MD5` 955023db… across all 4 engine_pin twins (ENGINE_MD5 untouched). No divergence. RED→green: engine test_ancestor_above_ceiling_not_resolved + harness env-unset both flipped; env-unset legacy + off-chain fall-open + workspace-own asserts green throughout.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

