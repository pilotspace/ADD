# TASK: git-native whoami resolver + actor model

slug: actor-identity · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/tooling/add.py` imports (14-24) — add `subprocess` + `shutil`; `getpass` already imported.
- `add-method/tooling/add.py:cmd_lock` (1083) — line 1100 `who = args.by or getpass.getuser()` is the EXISTING identity seam (OS user); `_whoami` generalizes it (task 2 routes lock through it). Read-only anchor here.
- NEW `_git_config(key)` + `_whoami(state)` near the other small helpers (e.g. by `getpass`/`_now`); NEW `cmd_whoami` + the `whoami` subparser (next to `lock`/`status` in build_parser).
- NEW state key `actor_override` = `{name, email}` (the `whoami --set` store); absent by default.
- `engine_pin.py:ENGINE_MD5` = `fa8e981875354468ad426b8012e11689` — re-pin after this engine edit.

Context (working folder):
- the engine has NO subprocess/git usage today (only `getpass` in cmd_lock) — this is the FIRST git call, so it MUST be fail-soft + bounded (design-for-failure: shutil.which gate, timeout, swallow git-absent/unset/empty). The engine stays usable with no git installed.
- freeze (`approved by <name>`) + gate (`Reviewed by:`) stamps are HUMAN-AUTHORED TASK.md text (regex-read at add.py:4475/4479), NOT engine-written — so task-2 stamping splits into engine-written records (lock/gate-state/milestone-done/release) vs author-suggested text. THIS task only builds the resolver + command; that split is task 2's contract.
- 3 byte-identical add.py copies — edit in lockstep + re-pin; full suite is the regression oracle.

Honors (patterns / conventions):
- design-for-failure (CLAUDE.md MUST) — the git subprocess gets a hard timeout + total fail-soft (never raises, never hangs); a missing/!partial git config degrades to the OS user, never an error.
- additive + backward-compatible — `actor_override` is a new optional state key; absent state behaves exactly as today (whoami resolves git→os).
- no injection surface — `_git_config` runs a FIXED argv (`git config --get <fixed key>`), never interpolates user input into a shell (no shell=True).
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin.

Anchors the contract cites: NEW `_git_config(key)` · `_whoami(state)` returning `{name,email,source}` · `cmd_whoami` + the `whoami` subparser · the `actor_override` state key · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A git-native ACTOR resolver — `_whoami(state)` returns the current actor `{name, email, source}` from (1) an `actor_override` stored by `whoami --set`, else (2) `git config user.name`/`user.email`, else (3) the `getpass.getuser()` OS user — plus `add.py whoami` to show / set / unset it. This is the identity every later stamp (task 2) and surface (task 3) reads.
Framings weighed: git config → OS-user fallback, optional override (chosen — confirmed at intake: zero-config + truly git-native; the override is sugar for when git config is wrong/shared) · OS-user only (rejected — not git-native, the whole point of the major) · a separate identity FILE / account (rejected — server-ish; git config IS the team's identity source).
Must:
<must>
  - `_whoami(state)` resolves, in priority: `actor_override` (source="override") → git config user.name/email (source="git") → `getpass.getuser()` (source="os"); ALWAYS returns a dict with a non-empty `name` (the OS user is the guaranteed floor); `email` may be None.
  - `_git_config(key)` is FAIL-SOFT + BOUNDED: returns the stripped value of `git config --get <key>`, or None when git is absent (`shutil.which`), the key is unset (non-zero exit), the call times out (hard timeout), or the output is empty. It NEVER raises and NEVER hangs.
  - `add.py whoami` (no args) prints the resolved actor + its source; `--json` emits `{name,email,source}`.
  - `add.py whoami --name <N> [--email <E>]` stores `actor_override={name,email}` in state (source becomes "override"); `--unset` removes it. A set with an empty/blank name is refused.
  - No injection / shell surface: `_git_config` uses a fixed argv list, never `shell=True`, never interpolates the key from user input.
  - Single-user behavior is unchanged elsewhere — this task adds a resolver + command only; no existing command's decision changes. All 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
</must>
Reject:
<reject>
  - `whoami --unset` when no override is set -> "no_actor_override" (nothing to clear; state byte-unchanged)
  - `whoami --name ""` (blank) -> "actor_name_blank" (a stored actor must have a real name)
</reject>
After:
<after>
  - `add.py whoami` reports the current actor (git config name/email when set, else the OS user), `--set` overrides it and `--unset` restores the git/os resolution; the resolver never raises or hangs even with git absent; the 3 copies + pin are green; the full prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Reading git config via a `subprocess.run(["git","config","--get",...], timeout=…)` is acceptable as the engine's FIRST git call, given strict fail-soft + a fixed argv. Lowest confidence because the engine has deliberately stayed "never runs git" (wave-verify used a ledger instead); chosen because the milestone is explicitly git-NATIVE identity and `git config` is the canonical team identity, with the OS-user floor preserving the no-git path. If wrong: the override + OS-user fallback already make git optional, so dropping the git read is a one-branch change.
  - [ ] `--set` stores ONLY name+email (not the source) under `actor_override`; source is always recomputed as "override" on read. Confirm at freeze.
  - [ ] email may be None throughout (git user.email unset, or OS-user path) — every consumer must tolerate a None email. Confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: whoami resolves from git config
  Given git config user.name="Ada" and user.email="ada@x.io" and no actor_override
  When `_whoami(state)`
  Then it returns {name:"Ada", email:"ada@x.io", source:"git"}

Scenario: whoami falls back to the OS user when git config is unset/absent
  Given _git_config returns None for both keys (git absent or unset)
  When `_whoami(state)`
  Then it returns {name: <getpass user>, email: None, source:"os"}

Scenario: an override wins over git
  Given actor_override={name:"Bob", email:"bob@y.io"} and git config set to someone else
  When `_whoami(state)`
  Then it returns {name:"Bob", email:"bob@y.io", source:"override"}

Scenario: _git_config is fail-soft when git is absent
  Given git is not on PATH (shutil.which returns None)
  When `_git_config("user.name")`
  Then it returns None (no raise, no hang)

Scenario: whoami --set stores an override
  Given a project
  When `whoami --name "Cleo" --email "cleo@z.io"`
  Then state.actor_override == {name:"Cleo", email:"cleo@z.io"} and a later `whoami` shows source=override

Scenario: whoami --unset clears the override
  Given actor_override is set
  When `whoami --unset`
  Then actor_override is removed and `whoami` resolves git/os again

Scenario: --unset with no override is refused
  Given no actor_override
  When `whoami --unset`
  Then it dies "no_actor_override" and state is unchanged

Scenario: --set with a blank name is refused
  When `whoami --name ""`
  Then it dies "actor_name_blank" and state is unchanged

Scenario: the engine edit stays pinned
  Given all three add.py copies are edited
  Then they are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# git-native actor resolver + the whoami command (add.py)

_git_config(key: str) -> str | None
  if shutil.which("git") is None: return None
  try: out = subprocess.run(["git","config","--get",key], capture_output=True,
                            text=True, timeout=2).stdout.strip()
  except (OSError, subprocess.SubprocessError): return None      # absent/timeout/any spawn error
  return out or None                                             # empty (unset) -> None

_whoami(state: dict) -> dict   # {"name": str, "email": str|None, "source": "override"|"git"|"os"}
  ov = state.get("actor_override")
  if ov and (ov.get("name") or "").strip():
      return {"name": ov["name"], "email": ov.get("email"), "source": "override"}
  name = _git_config("user.name")
  if name:
      return {"name": name, "email": _git_config("user.email"), "source": "git"}
  return {"name": getpass.getuser(), "email": None, "source": "os"}

whoami  (cmd_whoami)
  no flags        -> print "actor : <name> [<<email>>] (source: <source>)" ; --json -> {name,email,source}
  --name N [--email E]
                  -> reject actor_name_blank if N.strip()=="" ; state["actor_override"]={"name":N,"email":E}; save; print
  --unset         -> reject no_actor_override if "actor_override" not in state ; del it; save; print

Reject codes: no_actor_override · actor_name_blank   (validate BEFORE any write)
Invariant: _git_config never raises/hangs (fail-soft, bounded); _whoami always returns a non-empty name
  (OS-user floor); no shell=True / no key interpolation. No existing command's decision changes.
Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; auto-mode standing authorization; user-identity foundation 1/3; git→os priority + optional override · fail-soft fixed-argv git read · OS-user floor)
Least-sure flag surfaced at freeze: [contract] the engine's FIRST git subprocess (`git config --get`) — accepted because it is the milestone's git-native point, strictly fail-soft (shutil.which gate + 2s timeout + swallow-all), fixed-argv (no injection), and the override + OS-user floor keep the no-git path working. Second flag: [contract] `actor_override` stores only {name,email}; `source` is recomputed "override" on read (never stored), so a hand-edited override can't claim a false source.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the resolver's 3 priority branches + fail-soft git + the command's set/unset/show + 2 reject codes; full suite as the no-regression oracle.
Plan (one test per scenario; monkeypatch `_git_config`/`shutil.which` for deterministic git branches; drive `whoami` via add.main in a tmp project):
<test_plan>
  - test_resolves_from_git: _git_config patched to return name/email → source=git
  - test_falls_back_to_os: _git_config patched None → source=os, name=getpass user, email None
  - test_override_wins: actor_override set → source=override even with git present
  - test_git_config_failsoft_no_git: shutil.which patched None → _git_config returns None (no raise)
  - test_git_config_failsoft_timeout: subprocess.run patched to raise TimeoutExpired → None
  - test_whoami_set_stores_override: whoami --name/--email → state.actor_override set; show prints source=override
  - test_whoami_unset_clears: --unset → override removed
  - test_unset_without_override_rejected: --unset → SystemExit "no_actor_override", state unchanged
  - test_set_blank_name_rejected: --name "" → SystemExit "actor_name_blank", state unchanged
  - test_engine_three_trees_pinned: 3 copies byte-identical == ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_actor_identity.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_actor_identity.py` `add-method/tooling/test_min_pillar.py`
Strategy (ordered batches): 1. write `test_actor_identity.py` red. · 2. add `import subprocess`+`import shutil`; add `_git_config`/`_whoami` near getpass; add `cmd_whoami` + the `whoami` subparser. · 3. green new suite + FULL suite. · 4. mirror to 2 copies; re-pin ENGINE_MD5; green incl. parity.
Safety rule (feature-specific): the git subprocess MUST be bounded (timeout) + total fail-soft (catch OSError/SubprocessError) + fixed argv (no shell, no key interpolation); validate-before-write on --set/--unset (reject leaves state byte-unchanged).
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only (subprocess/shutil are stdlib); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add-method suite 1447 green; `add.py check` 391 passed / 0 failed
- [x] coverage did not decrease — added test_actor_identity.py (17 tests) + `whoami` census in test_min_pillar
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; tests written RED first (the 17-test suite ran red before the resolver existed)
- [x] the green was EARNED, not gamed — an independent adversarial refute-read (python-expert) returned BLOCK (0.97) on 2 real crash paths; BOTH fixed (UnicodeDecodeError catch + getpass.getuser KeyError floor) + 2 NITs; no overfit/vacuous asserts
- [x] concurrency / timing of the risky operation is safe — the git subprocess is bounded (timeout=2), fail-soft, fixed-argv, no shell; no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — fixed argv (no shell=True), no interpolation; subprocess/shutil are stdlib
- [x] layering & dependencies follow CONVENTIONS.md — additive helpers + one command; engine byte-pinned in lockstep across all 3 copies
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); engine edit independently reviewed (findings fixed before re-application)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `whoami` on a git-configured repo shows the git name/email + source=git; with git absent/unset it shows the OS user + source=os — confirmed by test_resolves_from_git / test_falls_back_to_os + a CLI run (`actor : Tin Dang <…> (source: git)`)
- [x] `whoami --name/--email` then `whoami` shows source=override; `--unset` returns to git/os — confirmed by test_whoami_set_stores_override / test_whoami_unset_clears
- [x] the git read is fail-soft + bounded (no raise on absent git, no hang on timeout, no crash on non-UTF-8 config) and uses a fixed argv (no shell/injection) — confirmed by test_failsoft_no_git / _timeout / _nonutf8_value / _uses_fixed_argv_no_shell + a read of `_git_config`

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_git_config`/`_os_user`/`_whoami` referenced by cmd_whoami; the `whoami` subparser dispatches via set_defaults(func=cmd_whoami); no dead helper
- [x] DEAD-CODE (code) — no orphaned symbol; subprocess/shutil imports are used by `_git_config`
- [x] SEMANTIC (prose / non-code) — n/a (engine-logic + test only)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22
Notes: re-applied additively onto the fold-suggestion-seams base (PR #47, commit 9dc3e944)
after a live parallel-writer contention reset clobbered the in-flight engine; the independent
adversarial review's 2 BLOCKING crash-path findings were fixed before re-application
(UnicodeDecodeError catch · getpass.getuser KeyError floor) + 2 NITs (email "" → None ·
--name/--unset mutually exclusive). No security finding. Engine re-pinned 1911b250 → 6f28abab,
byte-identical across all 3 copies; full suite 1447 green.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
