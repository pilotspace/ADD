# TASK: test suite stops leaking tempfile.mkdtemp dirs (leak-guard + cleanup sweep)

slug: test-tempdir-cleanup · created: 2026-06-25 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/test_*.py` — 119 use `tempfile.mkdtemp(...)`; 98 of them never `rmtree`/`addCleanup`, leaking a tempdir into the OS tmp on every run. The dominant idiom (91 files): `setUp` sets `self._cwd`, `self.tmp = Path(tempfile.mkdtemp(prefix=...))`, `os.chdir(self.tmp)`; `tearDown` does ONLY `os.chdir(self._cwd)` (41 classes verbatim). ~7 bespoke (no chdir / extra teardown logic). 21 already clean up — untouched. Deep-audit F14.
  - NEW `add-method/tooling/test_temp_hygiene.py` — a leak-GUARD meta-test: every `test_*.py` calling `.mkdtemp(` must also reference `rmtree`/`addCleanup` (a cleanup seam). The behavioral unit this task adds; RED now (98 fail), GREEN after the sweep, and a forward fence so new leaks can't reappear.
  - `add-method/tooling/test_skill_lean.py` etc. — NOT touched. Test files are NOT mirrored to `_bundled` (only the engine + skill + templates are), so this is a CANONICAL-tree-only change: NO ENGINE_MD5 re-pin, NO 3-tree mirror.
Context (working folder):
  - The full suite (1811 tests) is the safety net — any cleanup edit that breaks a test goes red. A scripted, reviewed sweep keeps the 98 edits uniform.
  - `add.py audit` reads `.add` only; this change is confined to `add-method/tooling/`.
Honors (patterns / conventions):
  - `_atomic_write`/`shutil.rmtree(..., ignore_errors=True)` = best-effort, never raise in teardown. red/green TDD: the guard is the red.
  - "design for failure": rmtree must be `ignore_errors=True` so a teardown can never mask a test's real assertion.
Anchors the contract cites: `tempfile.mkdtemp` · `shutil.rmtree(self.tmp, ignore_errors=True)` · the new `test_temp_hygiene` guard predicate.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: stop the test suite leaking tempdirs — a new `test_temp_hygiene` guard requires every `test_*.py` that calls `tempfile.mkdtemp` to also clean up (`rmtree`/`addCleanup`), and a one-pass sweep adds `shutil.rmtree(self.tmp, ignore_errors=True)` to the 98 leaking files' teardowns to satisfy it.
Framings weighed: direct-rmtree-per-tearDown (chosen) · shared-base-class · global-tmpdir-redirect
  - chosen (direct-rmtree): add `shutil.rmtree(self.tmp, ignore_errors=True)` to each leaking file's `tearDown` (add a `tearDown` + `import shutil` where absent). Each edit is independently obvious and correct — ZERO inheritance/super()-ordering risk; the guard enforces the outcome regardless of mechanism. More lines than a base class, but the safest to review across ~98 files.
  - shared-base-class: a `CleanTempCase` base whose `tearDown` rmtree's `self.tmp`. DRY, but the 98 subclasses' own `tearDown`s do `os.chdir(self._cwd)` and DON'T call `super().tearDown()` — so inheriting cleanly requires editing every `tearDown` to add `super().tearDown()` anyway (same churn + ordering hazard). SURFACED at freeze as the alternative.
  - global-tmpdir-redirect: point TMPDIR at a wiped dir. Rejected — runner/CI-level, doesn't clean during a run, and hides the per-test discipline the guard enforces.
Must:
<must>
  - A new `test_temp_hygiene` guard fails (lists offenders) if any `add-method/tooling/test_*.py` calls `.mkdtemp(` without referencing a cleanup seam (`rmtree` or `addCleanup`). It excludes itself.
  - After the sweep, EVERY mkdtemp test file references cleanup; the guard is GREEN and the full suite stays GREEN (no test regressed by the added teardown).
  - rmtree is best-effort (`ignore_errors=True`) so a teardown never raises and never masks a real assertion; the 21 already-clean files are untouched.
</must>
Reject:
<reject>
  - guard finding (not an error code, a test failure): `temp_leak` — "<file> calls mkdtemp but never rmtree/addCleanup".
</reject>
After:
<after>
  - The suite leaves no mkdtemp dirs behind; a new leaking test is caught by `test_temp_hygiene` going forward.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Adding `shutil.rmtree(self.tmp, ...)` to 98 teardowns regresses NO test. Lowest confidence because a few tests may keep using `self.tmp` paths AFTER tearDown, or chdir back into a removed dir, or share a tmp across tests. Mitigation: the full 1811-test suite is the gate (any breakage = red), rmtree is `ignore_errors=True`, and the sweep is scripted + spot-reviewed. If a specific file breaks, it gets a bespoke fix, not a weakened guard.
  - [x] test files are NOT in `_bundled` → no mirror / no ENGINE_MD5 re-pin — confirmed (prepare_bundle syncs engine+skill+templates only).
  - [x] the guard predicate count is 98 today — confirmed by a dry run.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guard catches a leaking test file
  Given a test_*.py that calls tempfile.mkdtemp but never rmtree/addCleanup
  When test_temp_hygiene runs
  Then it fails and names that file as a temp_leak offender

Scenario: a cleaning test file passes the guard
  Given a test_*.py that calls mkdtemp and rmtree(self.tmp, ignore_errors=True)
  When test_temp_hygiene runs
  Then it is not flagged

Scenario: the sweep keeps the suite green
  Given shutil.rmtree(self.tmp, ignore_errors=True) added to the 98 leaking teardowns
  When the full suite runs
  Then all tests still pass (no regression) and test_temp_hygiene is green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
NEW test_temp_hygiene.py — the leak guard (canonical tree only):
  HOME = Path(__file__).resolve().parent
  for f in sorted(HOME.glob("test_*.py")):
      if f.name == "test_temp_hygiene.py": continue
      t = f.read_text()
      if ".mkdtemp(" in t and not ("rmtree" in t or "addCleanup" in t):
          offenders.append(f.name)
  assertEqual(offenders, [], "<n> test files leak mkdtemp dirs: ...")   # temp_leak

SWEEP (mechanism — direct rmtree, scripted + reviewed) for each of the 98 leakers:
  - ensure `import shutil`
  - in tearDown, add:  shutil.rmtree(self.tmp, ignore_errors=True)
  - if a class has no tearDown, add one that rmtree's self.tmp (best-effort)
  - bespoke files (no self.tmp / no chdir): hand-fix to register cleanup

Invariants: canonical tree ONLY (no _bundled mirror, no ENGINE_MD5 re-pin) ·
            rmtree is ALWAYS ignore_errors=True (teardown never raises) ·
            the 21 already-clean files + non-mkdtemp files are untouched ·
            full suite stays 1811+ green; guard goes green.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (leak guard + direct-rmtree sweep of the 98 leaking teardowns; no base class, no mirror/re-pin).
Least-sure flag surfaced at freeze: [contract] adding rmtree to 98 teardowns could regress a test that reuses self.tmp after teardown or chdirs into a removed dir; cost = a red test. Mitigation: the full 1811-test suite gates every edit, rmtree is ignore_errors=True, and any breakage gets a bespoke fix — never a weakened guard. Canonical-tree-only: no _bundled mirror, no ENGINE_MD5 re-pin.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the leak guard + its self-exclusion (the sweep is verified by the full suite staying green).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_no_test_file_leaks_tempdir (test_temp_hygiene.py): enumerate test_*.py; assert none call .mkdtemp( without rmtree/addCleanup. RED now (98 offenders), GREEN after the sweep. The guard itself IS the red test.
  - (scenario 2 — a cleaning file passes — is the same guard's negative: the 21 already-clean files are not flagged; asserted implicitly by the empty-offenders assertion once the sweep lands.)
  - (scenario 3 — sweep keeps suite green — verified by `python3 -m unittest discover` staying 1811+/0 at verify, not a unit test.)
</test_plan>

Tests live in: `add-method/tooling/test_temp_hygiene.py` · MUST run red (98 offenders) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/`   <!-- the whole tooling dir: the new guard + the ~98 leaking test_*.py teardowns all land here; no engine/skill/_bundled files touched (test files aren't mirrored) -->
Strategy (ordered batches): 1. write test_temp_hygiene.py (the guard) — RED (98 offenders). 2. scripted sweep: add `import shutil` + `shutil.rmtree(self.tmp, ignore_errors=True)` to each leaker's tearDown (add tearDown where absent); hand-fix the ~7 bespoke. 3. guard GREEN + full suite 1811+/0; spot-review a sample of edits.
Safety rule (feature-specific): rmtree ALWAYS `ignore_errors=True`; never edit add.py / the engine / _bundled / skill; touch only test_*.py (+ the new guard). If a file breaks under the added teardown, fix THAT file bespoke — never weaken the guard.
Code lives in: `add-method/tooling/` (test files only)
Constraints: change no engine/contract; allow-list (stdlib shutil only); ask if a bespoke file is unclear.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1812/0 (clean synchronous run, exit 0); test_temp_hygiene guard green
- [x] coverage did not decrease — +1 guard test; the 98 swept files keep all their existing tests (no test removed/weakened)
- [x] no test or contract was altered during build — the §4 unit (test_temp_hygiene.py) is unchanged since the tests phase; BUILD edited only the 98 SRC test files (the subject of the fix, declared in §5), never the guard or §3
- [x] the green was EARNED, not gamed — refute-read: the guard is a real static fence (RED at 98 offenders, GREEN only when every mkdtemp file references a cleanup seam); the sweep's correctness is proven by the FULL suite staying 1812/0 — two earlier mechanisms that merely satisfied the guard but broke behavior (NameError; cwd cascade, 816 errors) were caught and rejected, NOT papered over
- [x] concurrency / timing — the cwd-deletion hazard (rmtree of a dir that is cwd) is handled: chdir-using classes register `addCleanup(os.chdir, os.getcwd())` which, by addCleanup LIFO, runs BEFORE the rmtree cleanup; verified by the green suite (no FileNotFoundError on os.getcwd())
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `shutil` only; no new third-party dep
- [x] layering & dependencies — canonical-tree-only; test files are NOT mirrored, so NO _bundled change and NO ENGINE_MD5 re-pin (engine untouched)
- [x] a person reviewed and approved the change — Tin Dang froze v1 (leak guard + direct-rmtree sweep)

### Realization note (mechanism vs the frozen §3 SWEEP text)
> §3's SWEEP bullet read "in tearDown, add shutil.rmtree(self.tmp, …)". The literal tearDown-append
> proved UNSAFE at scale: it added a second tearDown to subclasses of in-file base cases (e.g.
> `AutonomyRejectTest(_Board)`), OVERRIDING the base's cwd-restoring tearDown and deleting cwd
> (816-error cascade). The realization uses `self.addCleanup(shutil.rmtree, <var>, ignore_errors=True)`
> at the mkdtemp site (+ a paired cwd-restore for chdir classes) — which attaches to the OWNING class,
> never overrides an inherited tearDown, and runs AFTER any cwd-restoring tearDown. This stays within
> the FROZEN guard (it explicitly accepts `addCleanup`) and the approved decision ("direct rmtree, no
> base class"); §3's "bespoke files: hand-fix to register cleanup" anticipated mechanism latitude. No
> frozen artifact was edited.

### Build expectations — what "correct" looks like
- [x] test_temp_hygiene fails listing offenders before the sweep, passes after — confirmed (RED 98 → GREEN)
- [x] the sweep regresses no behavior — confirmed: full suite 1812/0 (the two unsafe interim mechanisms were caught by this exact gate and reverted)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every swept file references `shutil.rmtree`/`addCleanup` (guard-enforced) and has a module-level `import shutil` (anchored after `import tempfile`); spot-checked test_autonomy_command (chdir class → both cleanups, LIFO order)
- [x] DEAD-CODE — no orphaned symbol; each added line is a registered cleanup that runs at teardown
- [x] SEMANTIC — re-read the cleanup ordering invariant: addCleanup is LIFO, so the cwd-restore (registered last) runs first, guaranteeing cwd is outside self.tmp before rmtree

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

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
