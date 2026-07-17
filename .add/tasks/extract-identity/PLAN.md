# TASK: Extract identity/actor cluster to add_engine/identity.py (call-qualification refactor)

slug: extract-identity · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:120-208` — the 7 identity/actor fns (CONTIGUOUS): `_git_config` · `_os_user` · `_whoami` · `_actor_stamp` · `_render_actor_line` · `_parse_actor_arg` · `_actor_matches`. Stdlib-only deps (shutil/subprocess/getpass/re); call each other (_whoami→_git_config/_os_user; _actor_stamp→_whoami; _render_actor_line→_actor_stamp). NOT a pure-move leaf: add.py commands call `_whoami` BOTH directly (5 sites) AND via `_actor_stamp` (5 sites) → a verbatim move makes `patch.object(add,"_whoami")` dual-path. Human (Tin) AUTHORIZED the call-qualification refactor.
  - `add-method/tooling/add_engine/identity.py` — NEW module (the 7 fns + import shutil/subprocess/getpass/re).
  - `add-method/tooling/add.py` — `from add_engine import identity`; QUALIFY 16 call sites to `identity.X(...)` (_whoami:1374·1410·1525·1550·2614 · _actor_stamp:267·1133·1347·2833·3086 · _render_actor_line:6010 · _parse_actor_arg:1403·1404·2614 · _actor_matches:220·221) so ONE patch target (`add_engine.identity.X`) covers every path; keep a re-export for `add.X` attribute compat.
  - 13 test patch sites repointed `patch.object(add,"X")` → `patch("add_engine.identity.X")`: test_actor_identity.py(_git_config ×5) · test_actor_stamping.py(_whoami ×5) · test_identity_in_status.py(_whoami ×2) · test_ownership_model.py(_whoami ×1). `patch.object(add.subprocess,"run")`/`add.getpass` patches UNCHANGED (shared stdlib module — still work).
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context (working folder): the engine package (5 modules → +identity); 3-tree mirror.
Honors (patterns / conventions): re-export + QUALIFIED calls so one patch target works; two-pin model; 3-tree mirror; zero behavior change (qualification + patch-target only — assertions untouched).
Anchors the contract cites: `add_engine/identity.py` (NEW) · the 7 fns · qualified call sites · repointed patches · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 7 identity/actor fns to a NEW `add_engine/identity.py`; QUALIFY add.py's 16 call sites to `identity.X(...)` so a single patch target (`add_engine.identity.X`) controls every path; repoint the 13 add-namespace test patches to that target. Behavior-preserving call-qualification refactor (human-authorized). Zero behavior change.
Framings weighed: call-qualification + single-target repoint (chosen, Tin-authorized) · pure verbatim move (rejected — dual-path) · leave in add.py (reduce — rejected by Tin)
  - chosen — qualify all add.py call sites to `identity._whoami(...)` etc.; then `patch("add_engine.identity._whoami")` reaches BOTH the direct-command path and the `_actor_stamp`-internal path. Faithful: no assertion changes, only call qualification + patch retarget.
Must:
<must>
  - `add_engine/identity.py` defines the 7 (moved verbatim); add.py imports the module + re-exports the names (so `add.X` still resolves as an attribute).
  - add.py's 16 call sites are qualified to `identity.X(...)`; NO bare call to the 7 remains in add.py.
  - the 13 add-namespace test patches are repointed to `add_engine.identity.X`; the subprocess/getpass patches are untouched; every identity/actor/ownership test passes with its ORIGINAL assertions.
  - both pins re-aimed; identity.py joins the digest; 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's behavior changes or a qualified call misfires -> "identity_drift" (the identity/actor/ownership suites are the oracle).
  - a bare `_whoami(`/`_actor_stamp(` etc. remains in add.py -> "unqualified_call" (single-target repoint would silently miss it).
  - the pin recomputes itself -> "vacuous_pin"; identity.py missing from a tree -> "mirror_incomplete".
</reject>
After:
<after>
  - the engine package gains identity.py (6 modules); the identity/ownership engine is a clean module reachable by one patch target; full suite ≥1854 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Qualifying all 16 call sites + repointing the 13 patches makes `add_engine.identity.X` the single sufficient target — lowest confidence because a MISSED bare call site (or a test patching add.X I didn't catch) would break: the failure is LOUD (the identity/actor/ownership suites go red and name it). Mitigation: a grep asserts zero bare `\b_whoami(` etc. remain in add.py post-build; the full suite + the 6 identity test files are the gate. Cost: qualify/repoint the missed site.
  - [ ] subprocess/getpass patches keep working post-move — confirmed (they mutate the shared stdlib module attr, not add's namespace).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 7 fns moved and resolve via the module
  Given the identity fns live in add_engine/identity.py
  When a test imports add
  Then add._whoami / add._git_config / ... resolve (re-export) AND add_engine.identity.<name> is the home

Scenario: ONE patch target controls both call paths
  Given add.py qualified its calls to identity.X
  When a test patches add_engine.identity._whoami and runs a command that stamps via _actor_stamp
  Then the patched identity is used (the _actor_stamp-internal path sees it)
  And a command that calls _whoami directly also sees it

Scenario: the existing identity/actor/ownership suites pass with original assertions
  Given the 13 repointed patches + qualified calls
  When test_actor_identity / test_actor_stamping / test_identity_in_status / test_ownership_model / test_my_work_lens / test_wave_status_hint run
  Then every assertion passes unchanged (behavior preserved)

Scenario: no bare identity call remains in add.py
  Given the refactor
  When add.py is scanned for `\b_whoami(` / `\b_actor_stamp(` / etc.
  Then zero bare calls remain (all qualified to identity.X)

Scenario: pins re-aimed, 3-tree consistent
  Given identity.py joined the package
  Then ENGINE_PKG_MD5 == package_digest (incl. identity.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/identity.py (NEW):
  from __future__ import annotations
  import getpass, re, shutil, subprocess
  def _git_config(key) -> str | None        # moved verbatim
  def _os_user() -> str
  def _whoami(state) -> dict
  def _actor_stamp(state) -> dict
  def _render_actor_line(state) -> str
  def _parse_actor_arg(s) -> dict
  def _actor_matches(rec_actor, me) -> bool

add.py:
  from add_engine import identity
  from add_engine.identity import (   # re-export for `add.X` attribute compat
      _git_config, _os_user, _whoami, _actor_stamp,
      _render_actor_line, _parse_actor_arg, _actor_matches,
  )
  # the 7 defs removed; 16 call sites qualified: `_whoami(` -> `identity._whoami(` etc.

tests (repoint 13 add-namespace patches; subprocess/getpass UNCHANGED):
  mock.patch.object(add, "_git_config", ...)  ->  mock.patch("add_engine.identity._git_config", ...)
  mock.patch.object(add, "_whoami", ...)       ->  mock.patch("add_engine.identity._whoami", ...)

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+engine_pin+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] the single-target sufficiency — a MISSED bare call site or an un-repointed add.X patch breaks LOUDLY (identity/actor/ownership suites red + named). A post-build grep asserts zero bare `\b_whoami(`/`\b_actor_stamp(`/etc. in add.py; the 6 identity test files + full suite are the gate. Cost: qualify/repoint the missed site. Human (Tin) authorized this behavior-adjacent refactor over the safe "leave in add.py" reduce.
Status: FROZEN @ v1 — approved by Tin Dang (explicit AskUserQuestion authorization 2026-06-26: "Authorize identity refactor"; behavior-preserving, suite-gated, verify-hard)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; the 6 existing identity test files + full suite (≥1854) stay green with original assertions.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_identity_fns_in_module_and_reexported: the 7 live in add_engine.identity AND `add.X` resolves (re-export).
  - test_single_patch_target_controls_actor_stamp_path: patch add_engine.identity._whoami; call add._actor_stamp(state); assert the patched whoami flows through (the internal path sees one target).
  - test_no_bare_identity_call_in_add_py: scan add.py — zero `\b_whoami(`/`\b_actor_stamp(`/`\b_render_actor_line(`/`\b_parse_actor_arg(`/`\b_actor_matches(` (all qualified).
  - test_pkg_digest_includes_identity_3tree + test_pins_literal_and_md5.
  - (existing) repoint the 13 add-namespace patches → add_engine.identity.X; their original assertions must pass post-build.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_identity.py` (NEW) + repoint `add-method/tooling/test_actor_identity.py` `add-method/tooling/test_actor_stamping.py` `add-method/tooling/test_identity_in_status.py` `add-method/tooling/test_ownership_model.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/identity.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/identity.py` `add-method/tooling/test_actor_identity.py` `add-method/tooling/test_actor_stamping.py` `add-method/tooling/test_identity_in_status.py` `add-method/tooling/test_ownership_model.py`
Strategy (ordered batches): 1. (tests phase) write the new test + repoint the 13 patches. 2. (build) AST-extract the 7 → identity.py; add `from add_engine import identity` + re-export; qualify the 16 call sites (`\bFN(`→`identity.FN(`). 3. grep-assert zero bare calls remain. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule (feature-specific): behavior-preserving; the original assertions in all 6 identity test files must pass; zero bare identity call left in add.py; engine_pin.py never hashes.
Code lives in: `add-method/tooling/`
Constraints: do NOT weaken any assertion; only qualify calls + retarget patches; stdlib only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened (only call-qualification + patch-target changes)
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] the 7 resolve via add_engine.identity AND add.X (re-export) — §4 test
- [ ] patching add_engine.identity._whoami controls the _actor_stamp-internal path — §4 single-target test
- [ ] zero bare `\b_whoami(`/`\b_actor_stamp(`/etc. remain in add.py — §4 scan
- [ ] all 6 identity test files pass with ORIGINAL assertions — full suite green
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. identity.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING (code) — add.py imports identity + qualifies all 16 sites; identity.py stdlib-only leaf; engine_manifest globs it
- [ ] DEAD-CODE (code) — the 7 GONE from add.py; the re-export is referenced (attr compat); no orphan
- [ ] SEMANTIC — the repoint is faithful: confirm each repointed test's assertion is unchanged vs git

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): identity/ownership suite green · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] the big regions (commands/report/udd) need the SAME qualification technique or a DI refactor — scope as a sub-milestone (evidence: this task proved qualification works for a patched cluster)

### Competency deltas
- [ADD · folded] when commands call a fn BOTH directly and via an intermediary, a single patch target requires CALL-QUALIFICATION at every add.py site (evidence: identity dual-path; Tin authorized over reduce) [folded foundation-version 52]
