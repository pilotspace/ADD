# TASK: path-confine the federation manifest source (reject traversal/absolute under a sibling-repo allowlist)

slug: federation-harden · created: 2026-06-28 · stage: mvp
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
  - `add-method/tooling/add.py:cmd_federate` (L2182) — `source = (root.parent / fed[fid]["source"])` (L2196) then `source.read_bytes()` — NO path confinement today: an absolute `/etc/passwd` or a `../../../../x` source resolves + reads OUTSIDE the workspace. This is where the new HARD-STOP guard lands, BEFORE the read.
  - `add-method/tooling/add.py:cmd_check` federation loop (L2460) — `for _fid,_fspec in _federation(root).items(): if not (root.parent / _fspec["source"]).is_file(): warn federation_source_unreadable`. An escaping source whose target EXISTS (e.g. /etc/passwd) passes is_file() → no warn today. The check-time early-surface for an out-of-allowlist source lands here.
  - `add_engine/components.py:_confined(p, rootp) -> bool` (L20) — `p.resolve().is_relative_to(rootp)`, errors→False; rootp must be PRE-resolved. Reuse it for the allowlist check.
  - `add_engine/components.py:_federation(root) -> {id:{source,pin}}` — the manifest reader; returns the raw `source` string (degrade-safe). Unchanged.
Context (working folder):
  - `add-method/tooling/test_multirepo_federation.py` — the existing federation suite; EVERY fixture source is `../producer/.add/contracts/gateway-api.json` = a legit one-level sibling → MUST stay allowed (non-regression). `self.producer = (tmp/".."/"producer")` confirms siblings live under the workspace (root.parent.parent).
  - `add-method/skill/add/components.md` — the federation beat ("fail-loud: unknown id / unreadable source / invalid snapshot / version mismatch each HARD-STOPS"); a traversal `source` is a new fail-loud class to document. 4-tree skill mirror.
  - `add-method/tooling/engine_pin.py` — ENGINE_MD5 re-pin after the dogfood mirror sync (tri-tree).
  - No components.toml in this repo (single-component) — tests build sibling-repo fixtures in tmp dirs.
Honors (patterns / conventions):
  - FAIL-LOUD transport (components.md · cmd_federate docstring): a bad source HARD-STOPS and lands NOTHING — never reads/copies a guessed or out-of-bounds file. The new guard fires BEFORE any read.
  - OPT-IN + DEGRADE-SAFE: no [federation.*] → byte-identical; the confinement helper never raises (errors→reject, fail-closed).
  - design-for-failure (PROJECT.md / CLAUDE.md): validate-then-act; reject before the IO.
  - Tri-tree + pin: edit canonical `add-method/tooling/`, re-sync `.add/tooling/` + `_bundled/tooling/`, re-pin ENGINE_MD5.
Anchors the contract cites:
  - a new helper `_federation_source_confined(root, source) -> bool` — True iff `(root.parent/source)` resolves INSIDE the sibling-repo allowlist = the workspace `root.parent.parent` (one level up + down = a sibling; absolute / deeper `../` escape → False). PURE, never raises.
  - `cmd_federate` HARD-STOP: a new reject `federation_source_escapes` fired before `read_bytes` when the source is not confined.
  - the `cmd_check` federation loop: an out-of-allowlist source surfaced early (WARN, consistent with federation_source_unreadable).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: path-confine the federation manifest `source` — HARD-STOP a traversal/absolute source before any read; surface it early at `check`
Framings weighed: workspace-confinement (root.parent.parent sibling allowlist) (chosen) · own-repo-only (root.parent — too strict, breaks documented cross-repo siblings) · configurable allowlist path (over-engineered for now)
Must:
<must>
  - `cmd_federate` resolves the manifest `source` and HARD-STOPs with `federation_source_escapes` BEFORE any `read_bytes`, when the resolved path falls OUTSIDE the sibling-repo allowlist (the workspace `root.parent.parent`). Lands nothing.
  - A legit one-level sibling source (`../<sibling>/.add/contracts/<id>.json`) still resolves INSIDE the allowlist and pulls exactly as today (non-regression — the existing 9 federation tests stay green).
  - An absolute source (`/etc/passwd`) and a deeper-traversal source (`../../../../x`) each escape the allowlist → HARD-STOP, nothing landed.
  - The confinement check is a PURE helper `_federation_source_confined(root, source) -> bool` that NEVER raises (errors → False = reject, fail-closed).
  - `check` surfaces an out-of-allowlist declared source EARLY as a never-red WARN (`federation_source_escapes`), consistent with the existing `federation_source_unreadable` WARN — the HARD-STOP at `pull` is the real gate.
  - No `[federation.*]` declared → byte-identical (opt-in); every existing valid pull is unchanged.
</must>
Reject:
<reject>
  - a federation `source` resolving outside the sibling-repo allowlist — an absolute path OR a `../`-escape beyond one level -> "federation_source_escapes"   (HARD-STOP at `federate pull`; never-red WARN at `check`)
</reject>
After:
<after>
  - `federate pull <id>` on an escaping source dies with `federation_source_escapes` and lands NOTHING (no `.add/contracts/<id>.json` written, no `contracts/` dir created).
  - a legit sibling source still lands the byte-copy; the precedence is: unknown id → escapes → missing → invalid → version (escape checked before the read, after the id lookup).
  - `check` lists `federation_source_escapes` as a WARN for an escaping declared source; silent when none.
  - the tri-tree stays byte-identical; ENGINE_MD5 re-pinned.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the allowlist boundary is the WORKSPACE dir `root.parent.parent` — a source may reach a DIRECT sibling (`../x/…`) but not `../../…` — lowest confidence because the "right" boundary is a judgment call: too tight (root.parent = own repo only) breaks the documented cross-repo sibling pattern every existing federation test uses; too loose (no bound) is the hole. Workspace-confinement matches "sibling-repo allowlist" AND keeps all 9 tests green. If wrong (you want own-repo-only, or a configurable/deeper root): the boundary Path in the helper changes (~1 line) + the sibling tests would need a vendored-in source.
  - [ ] `check` surfaces the escape as a never-red WARN (not a RED check-fail) — consistent with the existing federation WARN; the real HARD-STOP is at `federate pull`. If wrong: move it to `checks` (RED).
  - [ ] a symlinked source is resolved (symlinks followed) before the boundary test — `_confined` uses `.resolve()`, so a symlink pointing outside the workspace is rejected. If wrong (you want lexical-only): swap `.resolve()` for a lexical normalize.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a legit sibling source still pulls (non-regression)
  Given [federation.gw].source = "../producer/.add/contracts/gw.json" with a valid sibling snapshot
  When I run `add.py federate pull gw`
  Then it lands the byte-copy at .add/contracts/gw.json and succeeds
  And the existing 9 federation tests stay green

Scenario: an absolute source hard-stops
  Given [federation.gw].source = "/etc/passwd"
  When I run `add.py federate pull gw`
  Then it dies with "federation_source_escapes"
  And nothing is landed — no .add/contracts/ dir is created   # fail-loud, lands nothing

Scenario: a deeper-traversal source hard-stops
  Given [federation.gw].source = "../../../../tmp/evil.json" (escapes the workspace)
  When I run `add.py federate pull gw`
  Then it dies with "federation_source_escapes"
  And nothing is landed   # escape rejected before any read

Scenario: the escape is checked before the read (precedence)
  Given an escaping source that also does not exist on disk
  When I run `add.py federate pull gw`
  Then it dies with "federation_source_escapes" (NOT federation_source_missing)
  And nothing is landed   # confinement precedes the read_bytes

Scenario: the confinement helper is pure and total
  Given _federation_source_confined(root, source) for a sibling, an absolute, a deep-escape, and a junk source
  When I call it
  Then it returns True for the sibling and False for the others, never raising

Scenario: check warns an escaping declared source (never red)
  Given [federation.gw].source = "/etc/passwd"
  When I run `add.py check`
  Then a WARN line names "federation_source_escapes"
  And check still exits 0 — no PASS becomes FAIL   # measure-not-block

Scenario: no federation declared is byte-identical
  Given a components.toml with only [component.web], no [federation.*]
  When I run `add.py check`
  Then no federation finding appears and behavior is unchanged   # opt-in
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
new engine helper (PURE · TOTAL · never raises):
  _federation_source_confined(root: Path, source: str) -> bool
    allow = root.parent.parent.resolve()          # the workspace dir holding the project + its siblings
    return _confined(root.parent / source, allow) # _confined: (p).resolve().is_relative_to(allow); errors -> False
    # True  for a direct sibling  "../<repo>/.add/contracts/<id>.json"
    # False for an absolute "/etc/passwd", a deep "../../../../x", or any erroring path (fail-closed)

cmd_federate <id>   (HARD-STOP precedence, escape checked AFTER id lookup, BEFORE the read):
  fid not in federation        -> _die federation_unknown          (unchanged)
  NOT _federation_source_confined(root, source) -> _die "federation_source_escapes: <source> resolves outside the sibling-repo allowlist"   (NEW — lands nothing)
  source unreadable            -> _die federation_source_missing    (unchanged)
  bad json / id≠ / no hash     -> _die federation_snapshot_invalid  (unchanged)
  pin set and version≠pin      -> _die federation_version_mismatch  (unchanged)
  else                         -> atomic byte-copy to .add/contracts/<id>.json  (unchanged)

cmd_check federation loop (per declared [federation.<id>]):
  NOT confined  -> warnings += ("federation '<id>'", "federation_source_escapes — '<source>' resolves outside the
                   sibling-repo allowlist; `federate pull <id>` will HARD-STOP")   (NEW, never-red WARN)
  else if not is_file(source)  -> federation_source_unreadable WARN   (unchanged)
  # escape takes precedence over unreadable (an escaping source is reported as escapes, not unreadable)

Anchors (from §0): _federation_source_confined (new) · _confined (reused) · cmd_federate · the cmd_check federation loop.
IO: reads NOTHING new (confinement is a pure path test before the existing read); writes nothing new.
Glossary: federation · source · sibling-repo allowlist (= the workspace, root.parent.parent).
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the allowlist boundary is the WORKSPACE dir root.parent.parent — a source may reach a direct sibling (`../x`) but not `../../` — cost: a ~1-line boundary change + sibling-test rework if you want own-repo-only or a configurable root; resolved workspace-confinement by Tin at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject; 6 new tests (HardenConfine) + the existing 9 federation tests stay green. Red now: 5 (3 fail + 2 error) for the right reason — `/etc/passwd` is currently READ (federation_snapshot_invalid), escapes report missing, helper absent; 1 green PIN (sibling pull unchanged).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  HardenConfine (test_multirepo_federation.py):
  - test_sibling_source_still_pulls — GREEN PIN: `../producer/...` lands (non-regression)
  - test_absolute_source_escapes — `/etc/passwd` -> federation_source_escapes, no contracts/ dir
  - test_deep_traversal_escapes — `../../escape.json` (above workspace) -> escapes, nothing landed
  - test_escape_checked_before_read — escaping + nonexistent -> escapes NOT missing (precedence)
  - test_confined_helper_is_pure_and_total — sibling True; absolute/deep/`\x00` junk all False, never raises
  - test_check_warns_escaping_source_never_red — check WARNs federation_source_escapes, exit 0
  (+ the existing Pull/Check classes = the 9-test non-regression guard)
</test_plan>

Tests live in: `add-method/tooling/test_multirepo_federation.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_multirepo_federation.py` `add-method/tooling/engine_pin.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. write red tests in test_multirepo_federation.py (new HardenConfine class: sibling-allowed · absolute-escapes · deep-escapes · escape-before-read precedence · helper-pure · check-warns-escape) — RED. 2. add `_federation_source_confined(root, source)` beside `_federation_findings`/`_confined` import. 3. insert the HARD-STOP in cmd_federate after the id lookup, before read_bytes. 4. add the escape WARN to the cmd_check federation loop (escape precedes unreadable). 5. green the suite (existing 9 federation tests unchanged). 6. re-sync `.add/tooling/` + `_bundled/tooling/`, re-pin ENGINE_MD5.
Known-problem fixes: boundary trap → confine to root.parent.parent (workspace) NOT root.parent (would break the legit `../sibling` pattern every existing test uses) · precedence trap → check confinement BEFORE read_bytes so an escaping+nonexistent source reports escapes, not missing · check-ordering → an escaping source must WARN escapes, not silently pass is_file() (a real /etc/passwd exists) · tri-tree drift → re-sync all three + re-pin or parity tests go red · fail-closed → the helper returns False on any error (never raises into the command).
Strategy actually used: as planned, all 6 batches. One deviation: the new HardenConfine test class needed a `_check` helper that lived only on the sibling `Check` class — caught at first green run; fixed by stepping the phase BACK to tests (`add.py phase tests`), adding the helper, and re-crossing tests→build so the tamper snapshot re-baselined (never hand-edited a test under build). The helper catches (OSError, ValueError) — wider than `_confined`'s OSError-only — to stay total on an embedded-NUL source. Independent security review (security-expert) ran 7 bypass probes → HOLDS; surfaced a LOW TOCTOU residue (disclosed, not closed — the complete fix is a §3 change).
Safety rule (feature-specific): validate-then-read — the confinement test runs BEFORE any filesystem read of the source; a non-confined source HARD-STOPS and the command lands nothing (fail-loud, fail-closed).
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2208/0; dogfood `check` 454/0; `audit` exit 0
- [x] coverage did not decrease — +6 federation tests (HardenConfine); existing 9 stay green
- [x] no test or contract was altered during build — re-crossed tests→build after a test-helper fix (`_check` on HardenConfine) so the tamper snapshot re-baselined cleanly; §3 FROZEN @ v1 untouched
- [x] the green was EARNED — security review verdict HOLDS (no escaping source bypasses the guard); refute clean
- [⚠] concurrency / timing — the guard is synchronous; ONE residual TOCTOU disclosed (a symlink swapped between the confine-check and the unresolved `read_bytes` could redirect). LOW risk: needs local workspace FS write (an actor who can read /etc/passwd directly) — OUTSIDE the threat model. ESCALATED to the human + recorded as a §7 forward delta.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; this change REMOVES an arbitrary-absolute-path read hole (the guard's whole point)
- [x] layering & dependencies follow CONVENTIONS.md — helper beside cmd_federate, reuses `_confined`; tri-tree re-synced + ENGINE_MD5 re-pinned (bed34cee)
- [⚠] a person reviewed and approved — ESCALATING to Tin (security-adjacent guard + a disclosed TOCTOU residue); gate is human-decided, NOT auto-resolved

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `federate pull` on `source = "/etc/passwd"` HARD-STOPs with `federation_source_escapes` and writes NO `.add/contracts/` dir — confirmed by test_absolute_source_escapes + the live run (before: it READ the file → snapshot_invalid; after: it never reads)
- [x] a `../../escape.json` (above the workspace) HARD-STOPs `federation_source_escapes`, and an escaping+nonexistent source reports escapes NOT missing (the guard precedes read_bytes) — confirmed by test_deep_traversal_escapes + test_escape_checked_before_read
- [x] a legit `../producer/.add/contracts/gateway-api.json` sibling source still lands the byte-copy — confirmed by test_sibling_source_still_pulls + the existing 9 federation tests staying green
- [x] `_federation_source_confined` returns True for a sibling, False for absolute/deep/`\x00`-junk, and never raises — confirmed by test_confined_helper_is_pure_and_total + the security review's P1–P5 probes
- [x] `check` surfaces an escaping declared source as a never-red WARN `federation_source_escapes` (exit 0) — confirmed by test_check_warns_escaping_source_never_red + the live run (2 escaping sources WARNed, 0 failed)
- [x] the three engine trees stay byte-identical + ENGINE_MD5 re-pinned — confirmed by md5 (bed34cee ×3) + the engine-pin/parity tests green in the 2208-test suite

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_federation_source_confined` wired into BOTH cmd_federate (HARD-STOP before read_bytes) and the cmd_check federation loop (escape WARN, elif-precedence over unreadable); reuses the imported `_confined`. Confirmed by the live run + the security review tracing the call sites.
- [x] DEAD-CODE (code) — no orphan; the helper has two live call sites + a unit test; `federation_source_escapes` surfaces at both federate (die) and check (warn).
- [x] SEMANTIC (prose / non-code) — read the FROZEN §3 + components.md federation beat; confirmed the new fail-loud class fits the documented "unknown/unreadable/invalid/version each HARD-STOPS" list (a doc line is a §7 delta for component-worked-example).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (with a disclosed LOW residual — TOCTOU, below)
By: agent ab252cd8 (security-expert, independent) + self · adversarially checked: P1 absolute paths (/etc/passwd, C:\) · P2 deep traversal + workspace-boundary (.. resolves to a dir → harmless) · P3 symlink escape incl. multi-hop chains (all rejected via .resolve()) · P4 NUL/empty/"."/".." (fail-closed) · P5 ~ and $VAR NOT expanded by pathlib (stay literal, inside workspace) · P6 TOCTOU (see below) · P7 cmd_check is read-free for an escaping source. VERDICT HOLDS — no escaping source string bypasses the guard within the threat model.
Residual (DISCLOSED, escalated): the confine-check resolves the path but cmd_federate reads the UNRESOLVED path, so a symlink swapped between check and read could redirect (TOCTOU). LOW: needs local workspace FS write = an actor who can read the target directly anyway; OUTSIDE the threat model (project-owner config string, not network input). Complete fix = read the RESOLVED path / O_NOFOLLOW — a §3 change, recorded as a §7 forward delta, not closed here.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose workspace-confinement (root.parent.parent sibling allowlist); rejected own-repo-only (root.parent — too strict, breaks documented cross-repo siblings) · configurable allowlist path (over-engineered for now)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, all 6 batches. One deviation: the new HardenConfine test class needed a `_check` helper that lived only on the sibling `Check` class — caught at first green run; fixed by stepping the phase BACK to tests (`add.py phase tests`), adding the helper, and re-crossing tests→build so the tamper snapshot re-baselined (never hand-edited a test under build). The helper catches (OSError, ValueError) — wider than `_confined`'s OSError-only — to stay total on an embedded-NUL source. Independent security review (security-expert) ran 7 bypass probes → HOLDS; surfaced a LOW TOCTOU residue (disclosed, not closed — the complete fix is a §3 change).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] close the federation TOCTOU residue — read the RESOLVED path (or open with O_NOFOLLOW), not the unresolved `root.parent/source`, so a symlink swapped between the confine-check and `read_bytes` can't redirect (evidence: security-expert P6 demoed a symlink-swap read of /etc/passwd; LOW + outside the threat model, deferred at Tin's PASS+forward-delta gate) [carried: LOW risk, outside the threat model (Tin chose PASS+forward-delta at federation-harden); harden with O_NOFOLLOW / resolved-path read if a real symlink-swap threat lands]
- [SPEC · dropped] document `federation_source_escapes` as the 5th fail-loud federation class in skill/add/components.md (joins unknown / unreadable / invalid-snapshot / version-mismatch) (evidence: §0 named the doc gap; overlaps the component-worked-example task's doc sweep)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a security-adjacent verify gate ESCALATES to the human even under autonomy:auto — the engine auto-resolves, but a disclosed residue (here: a TOCTOU) is human-signed, not auto-passed (evidence: this gate was human-decided PASS+forward-delta, not auto) [folded foundation-version 58]
- [TDD · folded] an adversarial path-confinement guard earns its green only via a bypass-probe refute-read (absolute · deep-traversal · symlink-chains · NUL · ~/$VAR literalness · TOCTOU), not fixture coverage alone (evidence: security-expert's 7 probes turned the green from asserted to EARNED) [folded foundation-version 58]
- [TDD · folded] a new test class sharing a `_Board` base may reference a helper defined only on a SIBLING class — re-cross tests→build to fix it, never hand-edit a test under build (evidence: HardenConfine needed `_check`, caught at first green run) [folded foundation-version 58]
