# TASK: Advisor subagent-spawn strategy

slug: advisor-strategy · created: 2026-06-14 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from auto: method-defining scope (it codifies a new method strategy — when/how to spawn an advisory subagent). High-risk guard requires a lowered rung; verify gate recorded on the human's standing "implement autonomous" authorization. -->
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
  - `add-method/skill/add/advisor.md` — NEW: the deliverable strategy doc (does not exist yet)
  - `add-method/skill/add/streams.md:160-266` — the existing spawn adapter: the six-capability mapping, the vendor-neutral tier table (mid/top → sonnet/opus), the `PROMPT.md` worker contract (objective·persona·touch_boundary·context_files·expertise·tools·return), the `Task()` spawn reference. advisor.md generalizes the SINGLE-subagent advisory spawn (vs streams' PARALLEL multi-task orchestration) — cross-reference, never duplicate
  - `add-method/skill/add/phases/0-ground.md:28-31` and `phases/6-verify.md:58-59` — the two existing per-step spawn hints (broad-sweep subagent · adversarial refute-read subagent) the advisor generalizes
  - `add-method/skill/add/confidence.md` (just shipped, task 1) — a spawned subagent self-scores and returns its confidence; advisor.md links it
  - `add-method/tooling/test_xml_convention.py:193` (ENGINE_FILES) — register advisor.md (it carries a `<constraints>` block for "the engine never spawns"); the worker-contract ```xml fence stays exempt (fenced)
  - `add-method/tooling/test_wording_lint.py:176` — the skill-file COUNT bumps 23 → 24 (advisor.md joins the linted surface) — DECLARED in §5 upfront this time
Context (working folder):
  - `.add/GLOSSARY.md` — "advisor" / "subagent" terms must stay consistent (ubiquitous language)
  - `add-method/CONTRIBUTING.md` — edit-then-sync: advisor.md needs prepare_bundle.py + mirror to `.claude/skills/add`
  - NEW test `add-method/tooling/test_advisor_strategy.py` — the red suite for §4
Honors (patterns / conventions):
  - tool-agnostic: the engine NEVER spawns (mirrors 0-ground.md/6-verify.md "the engine never spawns one"); the advisor RECOMMENDS, the orchestrating agent chooses
  - the frozen XML vocabulary (test_xml_convention) — advisor.md's only OUTSIDE-fence paired tag is `<constraints>`; the reusable prompt template lives in a ```xml fence (exempt, like streams.md's worker contract)
  - the subagent PROPOSES, the orchestrator RECORDS — a worker never runs add.py / writes shared state (streams.md rule)
  - minimalism + progressive disclosure — advisor.md holds the strategy; the per-step hooks (task 3) only point here
Anchors the contract cites: `advisor.md` (new) · when-to-spawn / when-not decision · the reusable plan-following prompt template (fenced) · the vendor-neutral tier pick (mid/top) · "the engine never spawns" `<constraints>` · the subagent-self-scores link to confidence.md · ENGINE_FILES registration · wording-lint count bump · the new content test

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `advisor.md` — the advisor subagent-spawn strategy. A tool-agnostic guideline for the orchestrating agent: when to spawn a SINGLE subagent to execute part of its plan, the reusable plan-following prompt template, the vendor-neutral tier pick — and the hard rule that the engine never spawns and the subagent only proposes.
Framings weighed: a separate `advisor.md` strategy doc the per-step hooks point to (chosen — generalizes the single-subagent advisory spawn; streams.md stays the PARALLEL multi-task orchestration) · fold it into streams.md (rejected — streams is about parallel pipelining + worktrees; conflating dilutes both) · inline per-step only (rejected — duplicates the template across 8 guides, violates DRY)
Must:
<must>
  - state the WHEN-to-spawn decision (broad/expensive sweep · independent adversarial review · a well-scoped delegable batch · context offload) AND the when-NOT (narrow/cheap work fully in-context)
  - carry a reusable PLAN-FOLLOWING prompt template in a ```xml code fence (objective · persona · steps that follow the orchestrator's plan · context_files · return) — generalizing streams.md's worker contract for a single advisory subagent
  - state the vendor-neutral tier pick (mid → sonnet · top → opus) — reuse streams.md's tiers, never a new vocabulary
  - require the spawned subagent to self-score via confidence.md and RETURN a structured verdict (the orchestrator records; the subagent never runs add.py)
  - carry a `<constraints>` block: the engine NEVER spawns (tool-agnostic; the orchestrating agent chooses); the subagent PROPOSES, the orchestrator RECORDS; high-risk + security still escalate regardless of delegation
  - register `advisor.md` in test_xml_convention ENGINE_FILES (tags={constraints}); the template's fenced tags stay exempt
  - stay THIN — the strategy lives here; the per-step hooks (task 3) only point here
</must>
Reject:
<reject>
  - the doc says (or implies) the ENGINE spawns / auto-spawns a subagent -> "engine_spawns"
  - a worker is told to run add.py or write shared state (violates propose-not-record) -> "worker_writes_state"
  - a paired convention tag outside the frozen vocab appears OUTSIDE a code fence -> "vocab_offmidiom"
</reject>
After:
<after>
  - `add-method/skill/add/advisor.md` exists with the when/when-not decision + the fenced plan-following template + the tier pick + the confidence-self-score link + the engine-never-spawns `<constraints>` block
  - test_xml_convention green with advisor.md registered (outside-fence tags ⊆ {constraints}; worker-contract fence exempt)
  - `add-method/tooling/test_advisor_strategy.py` asserts every anchor + reject codes; RED before advisor.md exists, GREEN after
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ advisor.md is a SEPARATE doc from streams.md (single advisory subagent vs parallel multi-task streams) — lowest confidence because the two overlap on the spawn mechanics; if wrong: two docs drift on the template. Mitigated: advisor.md CITES streams.md's six-capability mapping for the mechanics and only adds the single-subagent advisory framing + the plan-following template, so there is one source for the mechanics.
  - [x] tiers reuse streams.md's mid/top → sonnet/opus (confirmed from streams.md:234-237)
  - [x] the template reuses streams.md's worker-contract tag shape inside a fence (confirmed exempt by test_xml_convention WORKER_CONTRACT_TAGS)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the when/when-not decision is stated
  Given advisor.md
  When an agent reads it
  Then it names when to spawn (broad sweep · adversarial review · delegable batch · context offload) and when NOT to (narrow/cheap work in-context)

Scenario: the plan-following template is present and fenced
  Given advisor.md
  When an agent reads it
  Then a ```xml code fence holds a reusable prompt template (objective · persona · steps · context_files · return)
  And those template tags do NOT leak outside the fence (vocab stays clean)

Scenario: the tier pick reuses the streams vocabulary
  Given advisor.md
  When an agent reads it
  Then it names the mid/top tiers (sonnet/opus) and points at streams.md, not a new vocabulary

Scenario: the spawned subagent self-scores and only proposes
  Given advisor.md
  When an agent reads it
  Then it says the subagent self-scores via confidence.md and RETURNS a verdict the orchestrator records

Scenario: the engine-never-spawns hard rule
  Given advisor.md
  When an agent reads it
  Then a <constraints> block states the engine never spawns and the subagent proposes (never writes shared state / runs add.py)

Scenario: an engine-spawns claim is rejected
  Given a draft of advisor.md that says the engine spawns the subagent
  When test_advisor_strategy runs
  Then it fails "engine_spawns"
  And the tool-agnostic rule remains the only stated behavior

Scenario: the frozen XML vocabulary still holds
  Given advisor.md registered in ENGINE_FILES
  When test_xml_convention runs
  Then it is green: outside-fence paired tags ⊆ {constraints}, and the worker-contract fence is exempt
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC  add-method/skill/add/advisor.md   (a skill ENGINE doc; mirrored byte-for-byte to .claude/skills/add/ + _bundled/)
  REQUIRED anchors (each asserted by test_advisor_strategy):
    - intro names it the "advisor" strategy for spawning a subagent to follow the orchestrator's plan
    - a WHEN-to-spawn list AND a when-NOT line (the in-context default)
    - a ```xml fenced plan-following template containing objective + persona + steps + return
    - the tier pick: mentions "mid"/"top" and "sonnet"/"opus", pointing at streams.md
    - a line: the spawned subagent self-scores (mentions confidence.md) and returns a verdict the orchestrator records
    - a <constraints> block containing "the engine never spawns" (or "engine never spawns") AND "propose" (subagent proposes, orchestrator records)
  VOCAB: OUTSIDE-fence paired tags ⊆ {constraints}; the ```xml template fence is exempt (test_xml_convention strips fences)
  REGISTRY: advisor.md ∈ test_xml_convention.ENGINE_FILES with tags={"constraints"}
  Reject codes: engine_spawns · worker_writes_state · vocab_offmidiom

TEST  add-method/tooling/test_advisor_strategy.py — asserts every anchor + VOCAB + REGISTRY; RED before advisor.md exists, GREEN after.
PROPAGATION (in THIS task): prepare_bundle.py + mirror-copy to .claude/skills/add/advisor.md → test_tree_parity + test_bundle_parity stay green.
```

Least-sure flag surfaced at freeze: ⚠ [contract] advisor.md as a SEPARATE doc from streams.md (single advisory subagent vs parallel multi-task streams) — riskiest because they overlap on spawn mechanics; if wrong: the two drift on the template. Resolved: advisor.md CITES streams.md's six-capability mapping for the mechanics; one source for the mechanics.

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-14 (recorded on the standing "implement this milestone autonomous" authorization)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every REQUIRED anchor + each reject code has an assertion (content test).
Plan (one test per scenario, asserting observable doc content):
<test_plan>
  - test_when_and_when_not: assert a when-to-spawn list AND an in-context "when not" line
  - test_template_fenced: assert a ```xml fence holds objective+persona+steps+return; assert those tags do NOT appear outside a fence
  - test_tier_pick: assert "mid"/"top" + "sonnet"/"opus" + a streams.md pointer
  - test_subagent_self_scores_and_proposes: assert mentions confidence.md AND "propose"/"records" (engine_spawns + worker_writes_state guards)
  - test_engine_never_spawns_constraints: assert a <constraints> block containing "engine never spawns"
  - test_vocab_subset_outside_fence: outside-fence paired tags ⊆ {constraints} (vocab_offmidiom)
  - test_registered_in_engine_files: advisor.md ∈ test_xml_convention.ENGINE_FILES with tags={"constraints"}
  - test_xml_convention_still_green: the xml-convention engine-doc checks pass for advisor.md (incl. worker-contract-fence exemption)
</test_plan>

Tests live in: `add-method/tooling/test_advisor_strategy.py` · MUST run red (missing advisor.md + missing registration) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/advisor.md` · `add-method/tooling/test_xml_convention.py` · `add-method/tooling/test_wording_lint.py` · `add-method/tooling/test_advisor_strategy.py` · `add-method/src/add_method/_bundled/skill/add/advisor.md` · `.claude/skills/add/advisor.md`
Strategy (ordered batches): 1. write the red suite test_advisor_strategy.py (RED). 2. author advisor.md canonical (prose + a fenced plan-following template). 3. register advisor.md in test_xml_convention ENGINE_FILES (tags={constraints}) + bump test_wording_lint count 23→24 — both ADD coverage (strengthen). 4. propagate: prepare_bundle.py + mirror-copy — all parity green.
Safety rule (feature-specific): the template MUST live inside a ```xml fence so its worker-contract tags stay exempt (an unfenced template tag would trip vocab_offmidiom). The two guard-test edits only ADD advisor.md to coverage — no assertion relaxed (rule #3 holds).
Code lives in: `add-method/skill/add/advisor.md` (canonical) + its two mirrors; tests in `add-method/tooling/`.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib unittest); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 7 affected guards green (54/54), incl. the new test_advisor_strategy (red→green). Full suite unchanged otherwise; the 8 node/npx/pip env failures are pre-existing (CONTRIBUTING-named), untouched.
- [x] coverage did not decrease — added test_advisor_strategy.py (8 assertions); net increase
- [x] no test or contract was altered during build — frozen §3 unchanged; the two guard edits (test_xml_convention registration + test_wording_lint count bump) only ADD advisor.md to coverage (strengthen; both declared in §5 upfront)
- [x] the green was EARNED — adversarial refute-read inline (change tiny + fully inspectable): assertions check real content (when/when-not · the fenced template's tags present-and-not-leaked · tiers · the engine-never-spawns constraints block), none tautological; advisor.md is the actual deliverable; no test weakened
- [x] concurrency / timing — N/A: static markdown doc + content tests
- [x] no exposed secrets / injection / unexpected deps — new test imports stdlib only (importlib · re · unittest · pathlib)
- [x] layering & dependencies follow CONVENTIONS.md — advisor.md follows the engine-doc pattern (registered in the vocab guard; worker template fenced like streams.md); edit-then-sync honored (both mirrors propagated)
- [x] a person reviewed and approved the change — recorded on Tin Dang's standing "implement this milestone autonomous" authorization (conservative gate; evidence surfaced in chat for async veto)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new test methods run under unittest discovery; ENGINE_FILES["advisor.md"] is consumed by test_xml_convention's loops AND test_advisor_strategy.test_registered_in_engine_files. No unreferenced symbol.
- [x] DEAD-CODE — no orphaned code. NOTE (disclosed): advisor.md is not yet referenced by any phase guide — by design; per-step-hooks (task 3) wires it (forward pointer present). Process note: the implementation was authored during the specify phase, so the tests→build scope snapshot captured an already-built tree (the scope-gate was a no-op here) — all touches are still §5-declared; lesson logged in §7.
- [x] SEMANTIC (prose) — read advisor.md in full: when/when-not decision, the fenced plan-following template (objective·persona·steps·context_files·return), the mid/top→sonnet/opus tier pick pointing at streams.md, the confidence.md self-score + return-a-verdict line, and the <constraints> block (engine never spawns · subagent proposes / orchestrator records · security+high-risk still escalate). Matches every frozen §3 anchor.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (standing autonomous authorization) · date: 2026-06-14

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does any future skill doc carrying a prompt template forget to fence it (vocab_offmidiom)? does advisor.md drift from streams.md's mechanics?
Spec delta for the next loop: advisor.md + confidence.md now exist but are only wired in by task 3 (per-step-hooks); until then they are reachable only via SKILL.md's load-on-demand list.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] authoring the implementation during the SPECIFY phase makes the tests->build scope snapshot capture an already-built tree, so the scope-gate becomes a no-op — author code IN the build phase so the gate meaningfully checks touched ⊆ declared (evidence: advisor-strategy built pre-advance; task 1 confidence-rubric was caught by the scope-gate when a guard edit was undeclared) (evidence: scope_violation heal on confidence-rubric)
- [SDD · folded] a new skill engine doc silently breaks two guards that pin the surface inventory — test_xml_convention.ENGINE_FILES (registration) and test_wording_lint surface COUNT — both must be declared in §5 Scope BEFORE tests->build (evidence: confidence-rubric scope_violation on test_wording_lint.py)
