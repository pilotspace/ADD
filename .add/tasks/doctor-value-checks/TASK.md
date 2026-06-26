# TASK: doctor value-domain checks: gate/phase enum, archived consistency, owner/assignee shape

slug: doctor-value-checks · created: 2026-06-26 · stage: mvp
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
- `add-method/tooling/add.py:_doctor_findings` (2272-2318) — the read-only state.json diagnosis. TODAY it appends only REFERENTIAL findings (orphan active milestone · missing/mislabeled active task · task→missing milestone). This task APPENDS value-domain findings AFTER the referential ones, before `return findings`. Already has `state` (migrated), `milestones`, `tasks` in scope.
- `add-method/tooling/add.py:cmd_doctor` (2321-2334) — unchanged: prints `doctor: PASS …` when findings empty, else `✗`-bullets + exit 1. New findings flow through it automatically.
- `add_engine/constants.py:PHASES` = `("ground","specify","scenarios","contract","tests","build","verify","observe","done")` · `GATES` = `("none","PASS","RISK-ACCEPTED","HARD-STOP")` — re-exported by add.py (referenced by name there). The two enums the value checks validate against.
- actor shape (owner/assignee): `{name, email, source}` — `add_engine/identity.py:_whoami`/`_parse_actor_arg` mint it; a well-formed value is a dict with a non-empty str `name` (email str|None, source str). Absent = fine (present-only model).
- `engine_pin.py:ENGINE_MD5` = `e67bc6d796a2c9529ca580deee16b147` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies (`add-method/tooling` · `.add/tooling` · `add-method/src/add_method/_bundled/tooling`) — edit in lockstep + re-pin. `add-method/tooling/test_state_doctor.py` (9 tests green) is the sibling oracle; new tests land in `add-method/tooling/test_doctor_value_checks.py`.
- VERIFIED the new checks do NOT trip on THIS project's real state.json: task gates ∈ {PASS, none} (⊆ GATES), phases ∈ {done, ground} (⊆ PHASES), zero owner/assignee present, all 45 archived entries have `tasks == len(task_slugs)` and no archived slug is also live. So `doctor` stays PASS here.

Honors (patterns / conventions):
- detect, never auto-resolve: doctor REPORTS + exits non-zero; it never mutates state (the milestone's "reports, does not auto-fail history" decision — a finding is a human-run diagnostic, not a suite/audit retro-red).
- present-only / low-false-positive: flag PRESENT-but-invalid values only (an absent owner/assignee or a gate that is legitimately `none` is NOT a finding); never raise on malformed input (every access `.get`-guarded + isinstance-checked, mirroring the existing referential loops).
- engine-edit discipline: 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; the existing suite is the regression oracle.

Anchors the contract cites: `_doctor_findings` (the appended value-domain block) · `constants.PHASES` · `constants.GATES` · the actor `{name,email,source}` shape · `state["archived"]` entries (`slug` · `tasks` · `task_slugs`) · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: widen `add.py doctor` from referential-only to VALUE-DOMAIN integrity — `_doctor_findings` also flags a task whose `gate`/`phase` is outside the canonical enum, a malformed `owner`/`assignee` stamp, and an inconsistent `archived` entry. Detect-and-report only (doctor still never mutates state); present-but-invalid only, so a healthy state stays PASS.
Framings weighed: append the value checks to `_doctor_findings` after the referential loop (chosen — same pure read-only function, same `✗`-bullet surface through `cmd_doctor`, one place to read state) · a separate `doctor --strict` flag gating the value checks (rejected — splits the diagnostic; the milestone wants doctor to be the one integrity surface, and present-only checks are already low-false-positive) · validate at WRITE time in each command instead of in doctor (rejected — that is a different, larger task; doctor is the read-only auditor and the carried-forward delta names doctor).
Must:
<must>
  - `gate` is REQUIRED: for each task, if `gate` is absent (None) → a "missing gate" finding; if PRESENT and not in `GATES` ("none","PASS","RISK-ACCEPTED","HARD-STOP") → an "invalid gate '<g>'" finding. NOTE the string `none` is a VALID gate (an ungated task) — only None/absent or an unknown value is flagged.
  - `phase` is REQUIRED: for each task, if `phase` is absent (None) → a "missing phase" finding; if PRESENT and not in `PHASES` (ground…done) → an "invalid phase '<p>'" finding.
  - for each task, for role in (`owner`,`assignee`): if PRESENT (not None) and not a well-formed actor (a dict with a non-empty str `name`) → a finding "task '<slug>' has a malformed <role> …"; absent owner/assignee is fine (present-only model).
  - archived consistency: an archived entry whose `slug` is ALSO a live milestone → a finding ("…is also a live milestone…"); an entry whose integer `tasks` count ≠ `len(task_slugs)` → a finding ("…task count N ≠ M listed…").
  - PURITY + TOTALITY preserved: `_doctor_findings` still reads only, never mutates, never raises on malformed input (every access `.get`-guarded + isinstance-checked); the value findings are APPENDED after the referential findings, before `return findings`.
  - a referentially-clean state with all-valid values + no archived inconsistency still returns `[]` → `doctor: PASS` (the existing test_state_doctor healthy fixtures stay green, no test weakened); THIS project's real state stays PASS.
  - all 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned; parity/pin tests green.
</must>
Reject:
<reject>
  - (no new CLI error code — `cmd_doctor` already exits 1 when findings is non-empty; the value checks only ADD findings to that same list. The "rejection" surface is a richer finding set, not a new exit code.)
</reject>
After:
<after>
  - `add.py doctor` reports gate/phase enum violations, malformed owner/assignee, and archived inconsistencies alongside the referential findings; a healthy state (incl. this project) still prints `doctor: PASS`; the full suite is green with no test changed; 3 copies + pin green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "archived consistency" is the fuzziest of the four — I picked TWO concrete invariants (archived-slug-also-live · `tasks` ≠ `len(task_slugs)`) verified to hold on all 45 real archived entries. Lowest confidence because "consistency" could mean more (e.g. task_slugs all resolvable) and the exact two are a judgment call; if too narrow, a future state inconsistency slips past doctor (cost: a follow-up delta widens it) — never a false-positive on today's data (verified).
  - [x] RESOLVED at freeze (Tin, 2026-06-26): `gate`/`phase` are REQUIRED — absent OR invalid both flagged (a task with no gate/phase is corrupt, worth surfacing). `owner`/`assignee` stay OPTIONAL — absent fine, present-but-malformed flagged. (Verified safe: every real task has a present, valid gate+phase, so doctor stays PASS here.)
  - [ ] owner/assignee "well-formed" = dict with non-empty str `name` (email/source not deep-checked) — matches the mint shape; confirm the shallow check is enough.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Invalid gate is flagged
  Given a referentially-clean state with a task whose gate is "DONE" (not in GATES)
  When `add.py doctor` runs
  Then it reports a finding naming that task's invalid gate and exits non-zero

Scenario: Invalid phase is flagged
  Given a task whose phase is "shipping" (not in PHASES)
  When `add.py doctor` runs
  Then it reports a finding naming that task's invalid phase

Scenario: Missing required gate/phase is flagged
  Given task X with no gate key and task Y with no phase key (referentially clean otherwise)
  When `add.py doctor` runs
  Then it reports a "missing gate" finding for X and a "missing phase" finding for Y

Scenario: Malformed owner/assignee is flagged, well-formed/absent is not
  Given task A owner = "Tin" (a bare string, not an actor dict), task B owner = {name:"Tin",email:null,source:"assigned"}, task C with no owner
  When `add.py doctor` runs
  Then it reports a finding for task A's malformed owner
  And it reports NO finding for task B or task C

Scenario: Archived inconsistency is flagged
  Given an archived entry whose slug is also a live milestone, and another whose tasks=3 but task_slugs has 2 entries
  When `add.py doctor` runs
  Then it reports a finding for the live-duplicate archived slug
  And it reports a finding for the count mismatch

Scenario: Healthy state still PASSes
  Given a referentially-clean state where every task gate∈GATES and phase∈PHASES, no owner/assignee, archived entries consistent
  When `add.py doctor` runs
  Then it prints "doctor: PASS" and exits 0
  And state.json is unchanged (doctor never mutates)

Scenario: doctor never raises on malformed input
  Given a state whose tasks map has a non-dict task value (e.g. a string)
  When `_doctor_findings` runs
  Then it returns a list without raising (the non-dict task is skipped, not crashed on)

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  When the parity + ENGINE_MD5 tests run
  Then the three copies are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# doctor value-domain checks — appended to _doctor_findings (internal; READ-ONLY, pure, total)

_doctor_findings(root) -> list[str]   # unchanged signature; APPENDS these AFTER the referential loop, before `return findings`:

  for slug, t in tasks.items():
    if not isinstance(t, dict): continue
    g = t.get("gate")
    if g is None:
        findings.append(f"task '{slug}' is missing its gate — fix: one of {', '.join(GATES)}")
    elif g not in GATES:
        findings.append(f"task '{slug}' has invalid gate '{g}' — fix: one of {', '.join(GATES)}")
    p = t.get("phase")
    if p is None:
        findings.append(f"task '{slug}' is missing its phase — fix: one of {', '.join(PHASES)}")
    elif p not in PHASES:
        findings.append(f"task '{slug}' has invalid phase '{p}' — fix: one of {', '.join(PHASES)}")
    for role in ("owner", "assignee"):
        v = t.get(role)
        if v is not None and not (isinstance(v, dict) and isinstance(v.get("name"), str) and v.get("name")):
            findings.append(f"task '{slug}' has a malformed {role} — fix: an actor object {{name, email, source}} or remove it")

  archived = state.get("archived") if isinstance(state.get("archived"), list) else []
  for a in archived:
    if not isinstance(a, dict): continue
    aslug = a.get("slug")
    if aslug is not None and aslug in milestones:
        findings.append(f"archived milestone '{aslug}' is also a live milestone — fix: remove the live duplicate or the archived entry")
    ts = a.get("task_slugs")
    if isinstance(ts, list) and isinstance(a.get("tasks"), int) and a.get("tasks") != len(ts):
        findings.append(f"archived milestone '{aslug}' task count {a.get('tasks')} ≠ {len(ts)} listed — fix: reconcile its task_slugs")

  return findings

Surface: unchanged — cmd_doctor prints `doctor: PASS …` (empty) or `✗`-bullets + exit 1 (non-empty).
Invariant: present-but-invalid only; absent gate/phase/owner/assignee NOT flagged; pure/total (no raise, no mutate);
  a healthy state (incl. this project's real state.json) returns [] → PASS. Errors: none new.
Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] "archived consistency" is the fuzziest of the four checks — I chose TWO concrete invariants (an archived slug that is ALSO a live milestone · an integer `tasks` count ≠ `len(task_slugs)`), both verified to hold on all 45 real archived entries so doctor stays PASS here. If "consistency" should mean more (e.g. every task_slug resolvable), a future inconsistency slips past — cost is a follow-up delta to widen, never a false-positive on today's data. Second flag: [spec] RESOLVED at freeze — `gate`/`phase` are REQUIRED (absent OR invalid both flagged; `none` is a valid gate); `owner`/`assignee` stay OPTIONAL (absent fine). Verified every real task has a valid present gate+phase, so doctor stays PASS here.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each of the 4 new check groups (gate · phase · owner/assignee · archived ×2) at flag + no-flag, plus the purity/totality guard; the existing test_state_doctor as the healthy-PASS oracle.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_invalid_gate_flagged: task gate="DONE" → doctor exit≠0, output names the task + "invalid gate"
  - test_invalid_phase_flagged: task phase="shipping" → output names "invalid phase"
  - test_missing_gate_phase_flagged: task X no gate key → "missing gate"; task Y no phase key → "missing phase"
  - test_malformed_owner_flagged: owner="Tin" (str) → flagged; owner={name,email,source} → NOT flagged; no owner → NOT flagged (one test, 3 tasks)
  - test_malformed_assignee_flagged: assignee=123 → flagged "malformed assignee"
  - test_archived_slug_also_live_flagged: archived entry slug in milestones → flagged "also a live milestone"
  - test_archived_count_mismatch_flagged: archived {tasks:3, task_slugs:[a,b]} → flagged "count 3 ≠ 2"
  - test_healthy_state_still_passes: clean state, valid gate/phase, no owner, consistent archived → "doctor: PASS", exit 0, state md5 unchanged
  - test_doctor_pure_total_on_malformed: tasks has a non-dict value (a string) → _doctor_findings returns a list, no raise, the non-dict is skipped
  - (regression) the FULL existing suite incl. test_state_doctor (9) stays green with NO test changed
  - test_three_trees_pinned: 3 add.py copies byte-identical AND == engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_doctor_value_checks.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_doctor_value_checks.py`
Strategy (ordered batches): 1. write `test_doctor_value_checks.py` red (4 check groups + purity + pin). · 2. in `add-method/tooling/add.py`, append the value-domain block to `_doctor_findings` after the referential loop (uses in-scope `tasks`, `milestones`, `state`, module-level `GATES`/`PHASES`). · 3. run the FULL suite — test_state_doctor + the healthy-PASS paths must stay green with NO test change; `add.py doctor` on THIS project must still print PASS. · 4. mirror byte-identically to the other 2 copies; re-pin ENGINE_MD5; green incl. parity/pin.
Safety rule (feature-specific): every new access is `.get`-guarded + isinstance-checked (pure/total, never raises); flag PRESENT-but-invalid only (no false-positive on absent optional fields); doctor stays read-only (no state write). Diff the 3 copies before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2048 OK (2037→2048, +11 test_doctor_value_checks); check 437/0; audit clean (91 tasks)
- [x] coverage did not decrease — 11 new tests cover gate (invalid/missing/none-valid), phase (invalid/missing), owner/assignee (malformed/well-formed/absent), archived ×2, purity, pin
- [x] no test or contract was altered during build — git shows only add.py ×3 + engine_pin.py changed; test_doctor_value_checks.py is NEW; no existing test touched; §3 FROZEN @ v1 untouched
- [x] the green was EARNED, not gamed — 7 behavioral tests were RED before / GREEN after; LIVE `add.py doctor` PASSes on this project's 91 real tasks + 45 archived entries (no false-positive); the malformed-owner test asserts out.count("malformed")==1 so well-formed/absent are provably NOT flagged
- [x] concurrency / timing of the risky operation is safe — read-only diagnostic; `_doctor_findings` is pure/total (no mutation, no raise on malformed input); single-process CLI
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new import; reads state.json only; no shell/eval
- [x] layering & dependencies follow CONVENTIONS.md — value checks appended to the existing `_doctor_findings`, same `✗`-bullet surface through `cmd_doctor`; uses module-level GATES/PHASES; no new surface
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) + the §3 freeze approval (gate/phase made required) + a manual adversarial refute-read

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a task with gate="DONE"/phase="shipping" makes `doctor` exit non-zero naming "invalid gate"/"invalid phase" — confirmed: test_invalid_gate_flagged / test_invalid_phase_flagged green
- [x] a task missing gate or phase → "missing its gate"/"missing its phase"; gate="none" is NOT flagged — confirmed: test_missing_gate_phase_flagged + test_none_gate_string_is_valid green
- [x] owner="Tin" (bare str) flagged "malformed owner"; a well-formed actor + an absent owner are NOT flagged (out.count("malformed")==1) — confirmed: test_malformed_owner_flagged_wellformed_and_absent_not green
- [x] an archived slug also live → "also a live milestone"; tasks≠len(task_slugs) → "task count 3 ≠ 2 listed" — confirmed: ArchivedConsistencyTest pair green
- [x] healthy state still `doctor: PASS` (incl. live `add.py doctor` on THIS project); a non-dict task is skipped, no crash — confirmed: test_healthy_state_still_passes + test_doctor_pure_total_on_malformed green + LIVE `doctor: PASS` on this repo's 91 tasks / 45 archived
- [x] 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned — confirmed: all three == `1e01586bbb7df7328f792e508b08f499` == engine_pin.ENGINE_MD5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the appended block runs inside `_doctor_findings` (called by `cmd_doctor`); findings flow through the existing `✗`-bullet/exit-1 surface; GATES/PHASES referenced from module scope (verified importable)
- [x] DEAD-CODE (code) — no new symbol; the "missing gate/phase" arms are reachable (verified `_migrate_state` does NOT backfill task gate/phase, so an absent field survives to the check — exercised by test_missing_gate_phase_flagged)
- [ ] SEMANTIC (prose / non-code) — N/A (code change; the new finding strings passed the ubiquitous-language lint)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does `doctor` ever flag a value-domain problem in real use (would mean a command wrote a bad enum/actor)? a recurring finding points at the WRITE-side validation the carried-forward delta deferred.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] "archived consistency" covers only slug-also-live + count≠len(task_slugs); a deeper check (every task_slug resolvable to a real/archived task record) was deliberately left out — widen if a real inconsistency of that kind ever appears (evidence: the freeze flag, this task)
- [SPEC · open] the value checks DETECT bad enums/actors but don't PREVENT them — write-side validation in the commands that stamp gate/phase/owner is the natural follow-up (evidence: doctor is read-only by design; the milestone scoped detection, not prevention)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] before adding a doctor/audit check, GREP the real long-lived state.json for the values it will judge (gates/phases/archived shape) — a check that trips on legitimate history is a false-positive that erodes trust; here all 91 tasks + 45 archived passed, verified pre-build (evidence: the §0 GROUND "VERIFIED" note, this task) [folded foundation-version 55]
