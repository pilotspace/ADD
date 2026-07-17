# TASK: fast-lane component: hint + per-component-verify surfaces the bound component's own green-bar at the gate

slug: component-registry-fill · created: 2026-06-28 · stage: mvp
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
  - `add-method/tooling/templates/TASK.fast.md.tmpl` (×3 trees) — the fast-lane minimal template. Its `autonomy:` line (L4) is BARE `autonomy: {{autonomy}}` — UNLIKE the full TASK.md.tmpl whose autonomy line carries the `component: <name>` monorepo affordance comment. GAP (part A): a fast-lane task in a monorepo has no in-template hint to bind a component. Add the same affordance comment (3 trees byte-identical — test_fast_lane_template.test_three_trees_byte_identical; appends to an existing line so the <60%-of-full line budget + the {0,1,3,4,5,6} kept-section set are untouched).
  - `add-method/tooling/add.py:cmd_gate` (L1069-1071) — after a completing gate prints `component: <c> · expected green-bar: <bar>` via `_task_green_bar`. GAP (part B): it surfaces the descriptive GREEN_BAR but never the component's `verify` COMMAND (the literal suite, e.g. "pytest -q") — that command is only printed by `add.py components` (L2256), never at the gate where you'd run it.
  - `add-method/tooling/add.py:_task_green_bar` (L3663-3669) — `(_components(root).get(comp) or {}).get("green_bar") or None`; PURE. Add a TWIN `_task_verify(root, slug)` reading the `verify` field (same unbound/"?"/absent → None contract).
  - `add-method/tooling/add.py` gate-record writeback (L231-237) — records `component: <c> · expected green-bar: <bar>` after the §6 Outcome line; the verify command can be surfaced here too (record what suite to run).
  - `add-method/tooling/add.py:cmd_gate` green-bar CITE gate (L1036-1047) — the NO-EXEC enforcement: a bound task must CITE its green_bar in §6 before a completing outcome; the engine NEVER runs the suite. This task does NOT change that gate — it SURFACES the verify command (operator runs it), honoring NO-EXEC.
Context (working folder):
  - `add-method/tooling/test_fast_lane_template.py` — the 3-tree byte-identical + kept-section + line-budget guard (part A test home).
  - `add-method/tooling/test_per_component_verify.py` — the per-component green-bar cite/surface suite (part B test home).
  - `add-method/tooling/engine_pin.py` — ENGINE_MD5 re-pin after the add.py tri-tree sync. ENGINE_PKG_MD5 UNCHANGED — `_FALLBACK_TASK_FAST` lives in add_engine/constants.py (a SUBSET circuit-breaker, NOT byte-mirrored to the template), so the template-only hint does not touch add_engine/.
  - No components.toml in this repo (single-component) — tests build component fixtures in tmp projects.
Honors (patterns / conventions):
  - NO-EXEC (core invariant): the `verify` value is parsed + SURFACED as data, NEVER executed by the engine. Part B prints the command for the operator/agent to run; it never shells out.
  - OPT-IN + byte-identical-when-unbound: no `component:` / no green_bar|verify → `_task_verify` None → no new line (byte-identical), exactly like `_task_green_bar`.
  - measure-not-block consistency: the green_bar CITE gate is unchanged; surfacing the verify command is additive, never a new HARD-STOP.
  - Tri-tree + pin: edit canonical `add-method/tooling/` (add.py AND templates/), re-sync `.add/tooling/` + `_bundled/tooling/`, re-pin ENGINE_MD5.
Anchors the contract cites:
  - a `component:` affordance comment on the fast template's `autonomy:` line (3 trees byte-identical).
  - a new `_task_verify(root, slug) -> str | None` (twin of `_task_green_bar`); cmd_gate surfaces `verify: <cmd>` after a completing gate; the gate-record writeback records it. Engine NO-EXEC throughout.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fill the component registry into the fast lane + the gate — a `component:` hint in the fast template, and the bound component's `verify` COMMAND surfaced at the gate (NO-EXEC)
Framings weighed: surface-the-verify-command (chosen — the engine PRINTS the component's `verify` suite at the gate + records it; operator runs it; NO-EXEC honored) · cite-gate-on-verify (ALSO require the §6 evidence to cite the verify command, HARD-STOP if absent — rejected: redundant with the existing green_bar cite-gate, doubles the ceremony) · engine-runs-the-suite (REJECTED — violates the NO-EXEC core invariant)
Must:
<must>
  - The fast template (`TASK.fast.md.tmpl`, all 3 trees byte-identical) carries a `component:` affordance — the monorepo hint mirroring the full TASK.md.tmpl autonomy-line comment — so a fast-lane task can bind a component. The kept-section set ({0,1,3,4,5,6}) and the <60%-of-full line budget are unchanged (the hint appends to the existing `autonomy:` line).
  - A new PURE helper `_task_verify(root, slug) -> str | None` returns the bound component's `verify` command (twin of `_task_green_bar`: unbound / "?" / no verify declared -> None).
  - A completing gate (cmd_gate) SURFACES the bound component's `verify` command (e.g. `verify: pytest -q`) alongside the existing `expected green-bar:` line — so the operator sees the exact suite to run. The engine NEVER executes it (NO-EXEC).
  - The gate-record writeback records the surfaced verify command in §6 (next to the existing `component: … · expected green-bar: …` line) so the ledger shows which suite backed the gate.
  - Unbound / no `verify` declared -> `_task_verify` None -> NO new output, NO new §6 line (byte-identical, opt-in). The existing green_bar CITE gate (`component_green_bar_uncited`) is UNCHANGED — this task adds surfacing, not a new HARD-STOP.
</must>
Reject:
<reject>
  - (no new reject code — this is additive surfacing; the engine never executes `verify`, so there is no exec-failure path. The existing `component_green_bar_uncited` HARD-STOP is preserved unchanged.)
</reject>
After:
<after>
  - a fast-lane task in a monorepo can declare `component: <name>` guided by the in-template hint.
  - `add.py gate PASS` on a component-bound task prints both the expected green-bar AND the component's `verify` command; the §6 GATE RECORD records the verify command.
  - an unbound task (or a bound component with no `verify`) produces byte-identical output to today.
  - the tri-tree stays byte-identical; ENGINE_MD5 re-pinned; ENGINE_PKG_MD5 unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] "consume verify to run the suite at the gate" = SURFACE the command (the engine prints `verify: <cmd>` + records it; the operator runs it), NOT execute it — because NO-EXEC is a core invariant (the `verify` value is parsed as data, never shelled out). lowest confidence because the milestone wording ("run a bound task's own suite") could be misread as "the engine runs it"; surfacing is the only NO-EXEC-faithful reading and matches how `green_bar` is already consumed (cited, not run). If wrong (you want a hard cite-gate on the verify command too, like green_bar): add a `component_verify_uncited` HARD-STOP mirroring `component_green_bar_uncited` (still NO-EXEC — cite the result, never run).
  - [ ] the `component:` hint belongs on the fast template's `autonomy:` line (mirroring the full template), not as a new standalone line — keeps the 3-tree byte-identical + line-budget guards green. If wrong: a standalone hint line (still within budget).
  - [ ] surfacing the verify command at the gate is additive/never-block (consistent with measure-not-block). If wrong: make it part of the cite-gate (see ⚠).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fast template carries the component hint (3 trees identical)
  Given the shipped TASK.fast.md.tmpl in all three engine trees
  When its autonomy line is read
  Then it carries the `component: <name>` monorepo affordance comment
  And the three trees are byte-identical, the kept-section set is {0,1,3,4,5,6}, and the line count stays < 60% of the full template

Scenario: gate surfaces the bound component's verify command
  Given a component `gateway` with `verify = "pytest -q"` and a task bound `component: gateway`
  When `add.py gate PASS` completes
  Then the output prints `verify: pytest -q` (alongside the expected green-bar line)
  And the engine never executes the command (no shell-out; NO-EXEC)

Scenario: the verify command is recorded in the §6 GATE RECORD
  Given the same bound task at a completing gate
  When the gate-record writeback runs
  Then the §6 records the surfaced verify command next to the component line
  And a re-run is idempotent (the line is not duplicated)

Scenario: _task_verify is pure and total
  Given a bound task, an unbound task, and a bound task whose component declares no verify
  When `_task_verify` is called for each
  Then it returns the command, None, and None respectively
  And it never raises

Scenario: unbound task is byte-identical
  Given a task with no `component:` header (or a component with no verify)
  When `add.py gate PASS` completes
  Then no `verify:` line is printed and no §6 verify line is written
  And the output is byte-identical to today
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Part A — fast template affordance (3 trees byte-identical)
TASK.fast.md.tmpl `autonomy:` line gains the monorepo comment:
  "... Multi-component repo? add a `component: <name>` line (declared in .add/components.toml)
   to bind this fast task to a component (its root joins §5 Scope; its green-bar gates verify)."
Invariants preserved: kept sections == {0,1,3,4,5,6} · fast line-count < 60% of full · 3 trees identical.

# Part B — surface the verify command at the gate (NO-EXEC)
_task_verify(root: Path, slug: str) -> str | None
  # twin of _task_green_bar: return (_components(root).get(_task_component(root,slug)) or {}).get("verify") or None
  # unbound / "?" / no verify -> None. PURE. Parsed as DATA — never executed.

cmd_gate (after the existing `_gbar = _task_green_bar(...)` print block):
  _vfy = _task_verify(root, slug)
  if _vfy: print(f"verify: {_vfy}   # run this suite — the engine does not (NO-EXEC)")

gate-record writeback (_stamp_gate_record, beside the existing
  "component: <c> · expected green-bar: <bar>" line):
  append "· verify: <cmd>" to that line when _task_verify is set; idempotent (no dup on re-run).

Precedence / opt-in: unbound or no verify -> _task_verify None -> NO print, NO §6 line (byte-identical).
The green_bar CITE gate (component_green_bar_uncited) is UNCHANGED. No engine execution anywhere.
Schema: reads .add/components.toml `[component.<c>].verify` via _task_verify; writes the §6 component line only. No state fields.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
  ⚠ [contract] "consume verify to RUN the bound task's suite at the gate" is implemented as SURFACE-not-execute: the engine PRINTS `verify: <cmd>` + records it, and the operator runs it — because NO-EXEC is a core invariant (the verify value is data, never shelled out). This mirrors how `green_bar` is already consumed (cited, never run). COST if you instead want a hard cite-gate on the verify command (require §6 to cite it, HARD-STOP `component_verify_uncited` if absent — still NO-EXEC, just stricter): ~1 added gate branch + 1 test; say so and I'll fold it into the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must; 8 new tests, 6 RED for the right reason (`_task_verify` absent ×3; gate doesn't surface/record verify ×3) + 1 green pin (unbound byte-identical) in Part B, 1 RED (fast template lacks the hint) in Part A.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  Part B — test_per_component_verify.py:
  - TaskVerify.test_bound_returns_verify / test_unbound_returns_none / test_bound_but_no_verify_returns_none — the pure helper
  - VerifySurface.test_gate_surfaces_verify_no_green_bar — verify printed + recorded, no cite needed
  - VerifySurface.test_gate_surfaces_verify_and_green_bar — both green-bar + verify surfaced
  - VerifySurface.test_writeback_records_verify_once — §6 records the verify command exactly once
  - VerifySurface.test_unbound_gate_has_no_verify_line — GREEN PIN: byte-identical when unbound
  Part A — test_fast_lane_template.py:
  - TrustFloorRetained.test_component_affordance_present — the fast template carries the `component:` hint (+ the existing 3-tree/byte-identical/section/budget guards stay green)
</test_plan>

Tests live in: `add-method/tooling/test_per_component_verify.py` `add-method/tooling/test_fast_lane_template.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/test_per_component_verify.py` `add-method/tooling/test_fast_lane_template.py` `add-method/tooling/engine_pin.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. red tests (done). 2. Part A: add the `component:` affordance comment to the fast template's `autonomy:` line, in all 3 trees byte-identically. 3. Part B: add `_task_verify(root, slug)` twin of `_task_green_bar`. 4. cmd_gate: print `verify: <cmd>` after the existing green-bar print. 5. gate-record writeback: append `· verify: <cmd>` to the component line (idempotent). 6. green the suite. 7. re-sync `.add/tooling/` + `_bundled/tooling/` (add.py AND templates/), re-pin ENGINE_MD5.
Known-problem fixes: NO-EXEC → surface/record only, never shell out · byte-identical → `_task_verify` None short-circuits both the print and the writeback · idempotent writeback → guard the append with an `in` check so a re-stamp doesn't duplicate · tri-tree → the TEMPLATE has its own 3-tree parity (test_fast_lane_template) AND add.py has the engine pin; re-sync BOTH · ENGINE_PKG_MD5 untouched → do NOT edit add_engine/ (the fallback constant stays).
Strategy actually used: as planned, all 7 batches. One refinement beyond the plan: the gate-record writeback originally wrote the component line ONLY when green_bar was set — restructured it to compose `component: <c>` from whichever of {green-bar, verify} are present (` · `-joined), so a verify-only component still records the line while the green-bar-only output stays byte-identical (the existing CiteGate tests confirm). Surface-only / NO-EXEC throughout; tri-tree synced (add.py AND the fast template), ENGINE_MD5 re-pinned 6cc73630, ENGINE_PKG_MD5 unchanged.
Safety rule (feature-specific): the `verify` value is SURFACED as data only — the engine never executes it (NO-EXEC core invariant).
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

- [x] all tests pass — full suite 2224/0; dogfood `check` 464/0; `audit` exit 0
- [x] coverage did not decrease — +8 tests (TaskVerify ×3 + VerifySurface ×4 + the fast-template hint); no other test moved
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; test edits were all in the TESTS phase before crossing
- [x] the green was EARNED — self refute-read (additive surfacing, low-risk): NO-EXEC confirmed (no subprocess/shell call anywhere in the gate/verify path); the new `verify:` GATE-RECORD line is stripped by `_cite_region` so it cannot self-satisfy the green-bar cite-gate; byte-identical for unbound (test + full suite); idempotent writeback (test_writeback_records_verify_once + the live smoke shows ONE GATE-RECORD line)
- [x] concurrency / timing — synchronous; no concurrency surface; the engine never executes the verify command (NO-EXEC)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; `verify` is surfaced as data, never interpolated into a shell
- [x] layering & dependencies follow CONVENTIONS.md — `_task_verify` is a pure twin of `_task_green_bar`; tri-tree (add.py AND templates/) re-synced + ENGINE_MD5 re-pinned (6cc73630); ENGINE_PKG_MD5 unchanged
- [x] reviewed — additive surfacing, NOT a trust-layer/gate change (the green-bar cite-gate is unchanged, no new HARD-STOP), so auto-resolved under autonomy:auto with the recorded refute-read; the §3 surface-vs-execute decision was human-frozen by Tin

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py gate PASS` on a component-bound task whose component declares `verify = "pytest -q"` prints `verify: pytest -q` (and the §6 GATE RECORD records it once) — confirmed by VerifySurface tests + a live `gate` run
- [x] both lines appear together when the component declares green_bar AND verify (expected green-bar + verify) — confirmed by test_gate_surfaces_verify_and_green_bar
- [x] an unbound task (or a bound component with no verify) prints NO `verify:` line and writes no §6 verify line — byte-identical — confirmed by test_unbound_gate_has_no_verify_line + the full suite (no other gate test moved)
- [x] the fast template `TASK.fast.md.tmpl` carries the `component:` hint in all 3 trees byte-identically, kept-section set still {0,1,3,4,5,6}, line count still < 60% of full — confirmed by test_component_affordance_present + the existing 3-tree/section/budget guards green
- [x] the engine NEVER executes `verify` (NO-EXEC) — confirmed by the surfacing-only code path (no subprocess/shell call) + manual review
- [x] tri-tree (add.py AND templates/) byte-identical + ENGINE_MD5 re-pinned + ENGINE_PKG_MD5 UNCHANGED — confirmed by md5 + the engine-pin/parity tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_task_verify` called from cmd_gate (the `verify:` print) AND the gate-record writeback (`_stamp_gate_record`); both surface only when it returns non-None. Confirmed by the live gate run + the VerifySurface tests.
- [x] DEAD-CODE (code) — no orphan: `_task_verify` has two live call sites + 3 unit tests; the template hint is rendered (live `new-task --fast` shows it).
- [x] SEMANTIC (prose / non-code) — read the fast template diff (hint on the autonomy line, no new section, < 60% budget held) + the frozen §3; confirmed surface-only/NO-EXEC and the green-bar cite-gate is untouched.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self (additive, low-risk surfacing — no trust-layer/gate change) · adversarially checked: NO-EXEC (no subprocess/shell-out call in the gate or verify path — grep clean) · cite-gate isolation (the new `verify:` line lands in the GATE RECORD region, which `_cite_region` strips → cannot self-satisfy `component_green_bar_uncited`) · byte-identical for unbound (test_unbound_gate_has_no_verify_line + the full suite, no other test moved) · idempotent writeback (test_writeback_records_verify_once + the live smoke = ONE GATE-RECORD line) · green-bar-only output unchanged (the existing CiteGate tests stay green) · fast-template 3-tree parity + budget (md5 ×3 + the existing byte-identical/section/budget guards).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose surface-the-verify-command; rejected cite-gate-on-verify (ALSO require the §6 evidence to cite the verify command, HARD-STOP if absent — rejected: redundant with the existing green_bar cite-gate, doubles the ceremony) · engine-runs-the-suite (REJECTED — violates the NO-EXEC core invariant)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, all 7 batches. One refinement beyond the plan: the gate-record writeback originally wrote the component line ONLY when green_bar was set — restructured it to compose `component: <c>` from whichever of {green-bar, verify} are present (` · `-joined), so a verify-only component still records the line while the green-bar-only output stays byte-identical (the existing CiteGate tests confirm). Surface-only / NO-EXEC throughout; tri-tree synced (add.py AND the fast template), ENGINE_MD5 re-pinned 6cc73630, ENGINE_PKG_MD5 unchanged.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] document in components.md/book: a component's `verify` command is SURFACED at the gate (NO-EXEC, operator runs it) + the fast-lane `component:` affordance (evidence: this task added both; overlaps the component-worked-example doc sweep)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] "run the suite at the gate" under a NO-EXEC engine = SURFACE the command (print + record), never execute — the engine consumes the registry `verify` field as actionable DATA, mirroring how `green_bar` is cited-not-run (evidence: Tin froze surface-only over a hard cite-gate) [folded foundation-version 58]
- [TDD · folded] a template-artifact change is guarded by THREE pre-existing invariants at once — 3-tree byte-identical · the {0,1,3,4,5,6} kept-section set · the <60%-of-full line budget — so the hint must ride an EXISTING line (the autonomy comment), not add one (evidence: test_fast_lane_template's byte-identical + budget guards stayed green) [folded foundation-version 58]
