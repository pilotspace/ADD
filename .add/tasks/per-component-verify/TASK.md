# TASK: Per-component verify: gate a bound task on its component's suite + green-bar

slug: per-component-verify · created: 2026-06-24 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project `auto`: method-defining — modifies the core `cmd_gate` completing path. The unbound byte-identical invariant + a human verify guard the blast radius. -->
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
  - `add-method/tooling/add.py:cmd_gate(args)` (L1359) — records the verdict + enforces guards (high-risk · `_tamper_guard` · `_scope_guard`). KEY FACT: it does NOT execute any suite — the engine is bytes-only; the AI runs tests + records §6 evidence. This is the seam to make component-aware (surface the bound component's green-bar at the gate).
  - `add-method/tooling/add.py:_task_component(root, slug)` + `_components(root)` (task 1, DONE) — the binding + the component's `verify` (opaque cmd string) + `green_bar` phrase. The inputs this task consumes.
  - `add-method/tooling/add.py:_stamp_gate_record(root, state, slug, outcome)` — mirrors the verdict into §6 GATE RECORD; a place a per-component green-bar line could be stamped.
  - `add-method/tooling/add.py:_section_unfilled` / the build-expectations gate (flow-enforcement) — the precedent for a SOFT gate that requires a §6 block filled before PASS; a per-component-green-bar requirement would mirror it.
  - `add-method/tooling/add.py` report/status render (`render_report` / `cmd_status` / `_tests_info`) — where a bound task's component + green-bar would surface to the operator.
  - MILESTONE.md "### Ship by domain" (Close ship-review) — today human/AI-filled prose; the milestone exit criterion wants it to derive per component.
Context (working folder):
  - 3-tree parity + `engine_pin.py` re-pin (same discipline as task 1).
  - Tests: NEW `add-method/tooling/test_per_component_verify.py`; models `test_build_expectations_gate.py` (the soft-gate precedent) · `test_component_registry.py`.
Honors (patterns / conventions):
  - ENGINE INVARIANT (re-confirmed at `cmd_gate`): the engine does NOT run suites — it records evidence + guards. A per-component-verify must respect this (surface/record the bar, or soft-gate its presence) unless we deliberately choose to break it (the design fork below).
  - Opt-in: an unbound task / no-registry project ⇒ gate behaves byte-identically to today.
  - red/green TDD · design-for-failure · 3-tree parity.
Anchors the contract cites: `cmd_gate` · `_task_component` · `_components` · `_stamp_gate_record` · `green_bar` (registry field)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Per-component verify — at the gate, a component-bound task is held to its component's green-bar (surfaced + soft-gated), the engine still never executing a suite
Framings weighed: surface + soft-gate, engine stays no-exec (chosen) · engine executes the component's verify command · ship-by-domain auto-derive only
Must:
<must>
  - At `cmd_gate`, when the task is component-bound (`_task_component` → a known name with a non-empty `green_bar`), SURFACE the expected green-bar in the gate output AND stamp a "component: <name> · expected green-bar: <bar>" line into the §6 GATE RECORD (via `_stamp_gate_record`).
  - SOFT GATE `component_green_bar_uncited`: a COMPLETING gate (PASS / RISK-ACCEPTED) on a bound task whose §6 body does not reference the component's `green_bar` phrase is REFUSED — the evidence must show the right bar was met. Placed with the other completing-guards in `cmd_gate` (after high-risk, before the waiver write; HARD-STOP never blocked).
  - A bound component with NO `green_bar` declared ⇒ the soft gate is a no-op (cannot require an unspecified bar); surface a WARN at `check`, never block.
  - report/status: a bound task shows its `component:` + green-bar so the operator sees which bar applies.
  - OPT-IN / byte-identical: an unbound task (or a no-`components.toml` project) hits `cmd_gate` exactly as today — no surface change, no new gate, no stamp.
</must>
Reject:
<reject>
  - a COMPLETING gate on a bound task whose §6 omits the component's `green_bar` phrase -> "component_green_bar_uncited"
</reject>
After:
<after>
  - `cmd_gate` on a bound task (green_bar set) stamps the expected-bar line into §6 and refuses a PASS until §6 cites it.
  - Two tasks bound to different components each gate against their own bar — e.g. one cites "pytest + pyright", the other "vitest + a11y + build" — in one milestone.
  - Unbound / no-registry gate path is byte-identical to today.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "cite" = the component's `green_bar` phrase appears as a SUBSTRING in the §6 body — lowest confidence because a reworded bar (e.g. registry says "vitest + a11y" but §6 writes "vitest & accessibility") reads as uncited; if wrong: false `component_green_bar_uncited` blocks a real PASS. Mitigation: keep `green_bar` short + canonical; the WARN-on-missing-bar path softens it.
  - [x] the soft gate fires on ANY component-bound task (binding IS the opt-in), NOT behind `await_confirm` — CONFIRMED (Tin, 2026-06-24).
  - [x] stamp the expected-bar line into the §6 GATE RECORD via `_stamp_gate_record` (reuse, lowest blast radius) — CONFIRMED (Tin, 2026-06-24).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Bound task surfaces + stamps its component green-bar at the gate
  Given a task `component: dashboard`, dashboard.green_bar="vitest + a11y + build", and §6 citing "vitest + a11y + build"
  When `add.py gate PASS` runs
  Then the gate output names the expected green-bar "vitest + a11y + build"
  And the §6 GATE RECORD carries a "component: dashboard · expected green-bar: vitest + a11y + build" line

Scenario: Completing gate refused when §6 omits the component green-bar
  Given a bound task `component: dashboard` (green_bar="vitest + a11y + build") whose §6 does NOT contain that phrase
  When `add.py gate PASS` runs
  Then it fails with "component_green_bar_uncited"
  And the task stays NOT done — phase unchanged, gate not recorded

Scenario: Two tasks, two toolchains, one milestone
  Given task A `component: gateway` (green_bar="pytest + pyright", §6 cites it) and task B `component: dashboard` (green_bar="vitest + a11y", §6 cites it)
  When each runs `add.py gate PASS`
  Then both PASS, each having cited its own bar

Scenario: Bound component with no green-bar does not block
  Given a task `component: gateway` where gateway has NO green_bar declared
  When `add.py gate PASS` runs
  Then it PASSes (the soft gate is a no-op for an unspecified bar)
  And `add.py check` WARNs that the bound component declares no green-bar

Scenario: HARD-STOP is never blocked by the soft gate
  Given a bound task `component: dashboard` (green_bar set) whose §6 omits the bar
  When `add.py gate HARD-STOP` runs
  Then it records HARD-STOP (stopping is always allowed — the soft gate guards only completing outcomes)
  And no component_green_bar_uncited is raised

Scenario: Unbound task gate is byte-identical
  Given a task with no `component:` line (or a project with no components.toml) whose §6 is whatever it is today
  When `add.py gate PASS` runs
  Then it behaves exactly as pre-component ADD — no green-bar surfaced, no stamp, no new gate
  And the §6 GATE RECORD gains no component line
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine API — add-method/tooling/add.py · `root` = the .add/ dir · builds on task 1's readers

_task_green_bar(root, slug) -> str | None          # NEW · pure
  the green_bar phrase of the task's bound component, else None.
  = let c = _task_component(root, slug); if c in _components(root): _components(root)[c].get("green_bar") or None; else None
  (unbound / "?" / no-green_bar -> None)

_cite_region(body) -> str                          # NEW · pure (v3)
  the user-authored "Build expectations" evidence region of a §6 body, with the engine stamp stripped.
  = let m = re.search(r"(?im)^#*[ \t]*Build expectations\b.*?(?=\n#+[ \t]*GATE RECORD\b|\Z)", body, DOTALL)
    let region = m.group(0) if m else ""
    return re.sub(r"(?m)^component:.*·.*expected green-bar:.*$", "", region)
  - the marker matches BOTH template shapes: the standard "### Build expectations …" heading AND the
    fast-lane bare "Build expectations (from …):" line (so a component-bound FAST task is citable — Finding 2).
  - the region runs UP TO the GATE RECORD sub-block, so the top-of-§6 checklist ("- [ ] all tests pass")
    and the "Outcome: <PASS|…>" placeholder are excluded.
  - the trailing re.sub strips the engine's own "component: … · expected green-bar: …" stamp wherever it
    landed, so a stamp that fell inside the region (e.g. via an Outcome:<…> line authored in the block)
    cannot self-satisfy the gate (Finding 1).

cmd_gate(args)                                     # EXTENDED — only the bound-with-green_bar path is new
  let bar = _task_green_bar(root, slug)
  COMPLETING outcome (PASS / RISK-ACCEPTED) AND bar is not None:
    if bar not in _cite_region(_raw_phase_bodies(root, slug).get(6, ""))  ->  SystemExit(
        "component_green_bar_uncited: §6 Build-expectations must cite the '<name>' green-bar '<bar>'
        — record the evidence that bar was met")
    placed AFTER the unguarded_high_risk_auto guard, BEFORE the waiver write (never launderable; HARD-STOP never reaches it)
  on any recorded outcome with bar not None: print "component: <name> · expected green-bar: <bar>" to the gate stdout
  bar is None (unbound / no green_bar)  ->  cmd_gate is BYTE-IDENTICAL to today (no check, no stamp, no extra print)

_stamp_gate_record(root, state, slug, outcome)     # EXTENDED
  when _task_green_bar is not None: also write/refresh a "component: <name> · expected green-bar: <bar>" line inside §6 GATE RECORD

cmd_check                                          # EXTENDED — one WARN, never red
  a bound task (_task_component -> known name) whose component declares NO green_bar -> WARN "component_green_bar_unset"

Schema: no state.json change · no new file · reads task 1's _components/_task_component + §6 body bytes only
```

Reject-code mapping (the one §1 Reject has a contracted response):
  component_green_bar_uncited -> SystemExit at `cmd_gate` on a completing outcome (loud, blocks completion — like gate_pass_before_verify); HARD-STOP is exempt; unbound path never reaches it

Least-sure flag surfaced at freeze: [contract] "cite" = a SUBSTRING match of the component `green_bar` phrase in the §6 Build-expectations block — a reworded bar reads as uncited and false-blocks a real PASS; if wrong (too brittle): loosen to a token/normalized match or drop the gate to a WARN. [spec] the soft gate fires on ANY component-bound task (binding is the opt-in), not behind the `await_confirm` master switch — if wrong: ride `await_confirm` like build-expectations. Both default-accepted unless you steer otherwise at the freeze.
v2 CHANGE REQUEST (Tin, 2026-06-24): a second refute-read found the v1 whole-§6 substring search self-satisfied for a generic green_bar that collides with §6 boilerplate (e.g. "all tests pass" in the checklist, "PASS" in the Outcome placeholder) — a false-PASS that silently no-ops the gate. RESOLUTION: scope the cite-search to the user-authored "### Build expectations" block (subsumes the v1 stamp-strip; closes the boilerplate collision). Reject code + API surface + unbound byte-identity all unchanged.
v3 CHANGE REQUEST (Tin, 2026-06-24): a THIRD refute-read (scoped to v2) found two holes. Finding 1 (self-satisfy): `_stamp_gate_record` inserts the stamp after the FIRST `Outcome:` line — if a user authored an `Outcome:<…>` line INSIDE the Build-expectations block, the stamp landed inside the v2 region → HARD-STOP→PASS self-passed again. Finding 2 (false-block): the FAST-LANE template has no `### Build expectations` heading (a bare "Build expectations (from …):" line), so the v2 region regex returned None → a component-bound FAST task was permanently refused with no escape. RESOLUTION: factor the cite-region into a pure `_cite_region(body)` that (a) matches the Build-expectations marker in BOTH template shapes up to GATE RECORD, and (b) strips the engine stamp from the region. Reject code + API surface + unbound byte-identity all unchanged.
Status: FROZEN @ v3 — approved by Tin Dang, 2026-06-24. v1 flags still ACCEPTED; v2 scoped the region; v3 makes the region pure + template-shape-agnostic + stamp-stripped (closes both v2 refute findings).
<!-- Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen contract = change request back to SPECIFY. -->
<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new/extended seams (`_task_green_bar`, the `cmd_gate` cite-branch, the stamp, the check WARN).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - TaskGreenBar: bound→bar · unbound→None · bound-no-green_bar→None
  - CiteGate: uncited completing→refused+not-done · cited→PASS+surface+§6 stamp · no-green_bar→PASS · HARD-STOP→records · unbound→byte-identical (no surface/stamp)
  - CheckWarn: bound-no-green_bar → `component_green_bar_unset` WARN
</test_plan>
Red run (2026-06-24): 9 tests · 3 green (unbound-byte-identical + HARD-STOP-never-blocked non-regression pins already hold) · 6 RED (missing `_task_green_bar` errors + the cite-gate not yet enforced). Red for the right reason.

Tests live in: `add-method/tooling/test_per_component_verify.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py`
Strategy (ordered batches): 1. RED — `add-method/tooling/test_per_component_verify.py` (6 scenarios) · 2. add `_task_green_bar`; extend `cmd_gate` (bound+green_bar → cite-check before completing + surface line) · 3. extend `_stamp_gate_record` to stamp the expected-bar line · 4. add the `component_green_bar_unset` WARN to `cmd_check` · 5. GREEN; propagate to 2 mirrors + re-pin `engine_pin.py`.
Safety rule (feature-specific): the `bar is None` (unbound / no green_bar) path MUST be byte-identical — guard every new branch behind `_task_green_bar(...) is not None`; HARD-STOP must never reach the cite-check.
Code lives in: `add-method/tooling/add.py` (+ mirrors)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear. Re-cross tests→build after declaring §5 to re-anchor `scope.declared`. `.add/` is pruned by `_scope_walk` so the gate-enforced token is `add-method/`.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 1702/0 (`python3 -m unittest discover`); task suite test_per_component_verify.py 16/16.
- [x] coverage did not decrease — +16 new tests; every new/extended seam (`_task_green_bar`, `_cite_region`, cmd_gate cite-branch + surface, `_stamp_gate_record` line, cmd_check WARN) is exercised, incl. four cite-region/boilerplate-collision regressions across both template shapes.
- [x] no test or contract was altered during build — every test-edit was made via `add.py phase tests` and every §3 amendment (v2, v3) via `add.py phase contract`, BEFORE re-advancing — the tripwire re-anchored at each tests→build crossing.
- [x] the green was EARNED — THREE adversarial refute-reads, each finding the next edge. #1: BLOCKER (HARD-STOP stamp self-satisfied a later PASS). #2: MAJOR Finding 2 (generic green_bar collided with §6 boilerplate, self-passed on first gate). #3: FIX-HOLDS on prior, + two more — Finding 1 (a stamp landing INSIDE the scoped block via an Outcome:<…> line) and Finding 2 (the fast-lane template lacks the `### Build expectations` heading → component-bound fast task PERMANENTLY false-blocked). ALL CLOSED in v3 by the pure `_cite_region`: matches the Build-expectations marker in BOTH template shapes up to GATE RECORD, AND strips the engine stamp from the region. Each closure red→green-locked.
- [x] concurrency / timing safe — all new logic is pure reads + the existing `_atomic_write` stamp path; no new IO ordering. Engine still never executes a suite (invariant held).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (reuses task-1's guarded `tomllib`); no shell, no network; `verify` field stays OPAQUE/never-run.
- [x] layering & dependencies follow CONVENTIONS.md — soft-gate placed with the other completing-guards in `cmd_gate` (after `_scope_guard`, before the waiver write; HARD-STOP exempt), mirroring the build-expectations precedent.
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A bound task (green_bar set) whose §6 omits the bar is REFUSED at `gate PASS` with `component_green_bar_uncited` — `test_uncited_completing_gate_refused` (phase stays `verify`, message on stderr).
- [x] The same task, after §6 cites the bar in the Build-expectations block, PASSes and §6 GATE RECORD carries the "component: … · expected green-bar: …" line — `test_cited_gate_passes_and_stamps` re-reads §6 and asserts the stamped line; the cite-search is scoped to user evidence, so this proves USER evidence drove the PASS.
- [x] A generic green_bar that collides with §6 boilerplate ("all tests pass" / "PASS") does NOT self-pass — `test_generic_bar_colliding_with_boilerplate_does_not_self_pass` (refused) + `test_generic_bar_passes_when_cited_in_evidence` (passes once cited).
- [x] `_cite_region` (pure, v3) is correct across both §6 shapes + the self-satisfy edge — `CiteRegion` 4 tests: standard region = user evidence only · fast-lane bare-marker captured · stamp-inside-block stripped · no-marker → empty.
- [x] An UNBOUND task / no-registry project gates byte-identically — `test_unbound_gate_byte_identical` (no surface line, no stamp); full suite 1702/0, no existing gate test perturbed.
- [x] HARD-STOP on a bound uncited task still records, AND a later PASS is still refused — `test_hard_stop_never_blocked` + `test_hard_stop_then_pass_still_refused`.
- [x] 3-tree parity + ENGINE_MD5 re-pinned (`7a0135e5…`) — parity/pin tests green in the full run.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_task_green_bar` is called in `cmd_gate`/`_stamp_gate_record`/cmd_check; `_cite_region` is called in the cmd_gate cite-check; `_task_component`/`_components` (task 1) feed them. All reachable from the CLI gate/check paths.
- [x] DEAD-CODE (code) — no orphan symbols; the two new symbols (`_task_green_bar`, `_cite_region`) each have live call sites.
- [x] SEMANTIC — re-read the v3 `_cite_region` regex `(?im)^#*[ \t]*Build expectations\b.*?(?=\n#+[ \t]*GATE RECORD\b|\Z)` + the stamp strip: the marker matches the standard `###` heading AND the fast-lane bare line; the capture runs to GATE RECORD (excludes the top checklist + Outcome placeholder); the strip removes a mis-placed stamp — confirmed against both real templates (`TASK.md.tmpl` + `TASK.fast.md.tmpl`) and the 4 `CiteRegion` unit tests.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-24

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
