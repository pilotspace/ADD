# TASK: advisor-verdict-audit

slug: advisor-verdict-audit · created: 2026-06-29 · stage: mvp · sensitivity: architecture · risk: high
autonomy: conservative   <!-- method-defining / dogfood — cannot use the auto relaxation; lowered from project default per risk: high guard -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:_guarantee_lint_notices(root, state) -> dict` ~line 5625 — the MEASURE-NOT-BLOCK audit lint collector; extend its body and return dict with 3 new advisor-quality keys
  - `add-method/tooling/add.py:cmd_audit(args)` ~line 5658 — the read-only audit command; extend the glint-print block + clean-line conjunction (~line 5692) to surface and guard the 3 new keys
  - `add-method/tooling/add.py:_task_sensitivity(hdr, valid=None)` line 989 — sensitivity accessor; used as the `mechanical` mis-tier predicate
  - `add-method/tooling/add.py:_RISK_HIGH_RE` line 982 — anchored declaration grammar (declaration-position model shared by all header readers)
  - `add-method/tooling/add.py:_AUDIT_REVIEWED_RE` line 5518 — `re.compile(r"^Reviewed by:(.*)$", re.M)` — style model for reading a named §6 field; the `Advisor:` field reader follows the same line-start pattern
  - `add-method/tooling/add.py:gate_actor` dict on `state["tasks"][slug]` (stamped at line 1185 by `identity._actor_stamp(state)`); field `gate_actor["name"]` — the WHO that called `add.py gate`
  - `add-method/tooling/add.py:_raw_phase_bodies(root, slug)` — body6 accessor already used by the existing glints at line 5642
  - `add-method/tooling/add.py:_section_unfilled(body6, heading)` — section-presence predicate (mirrors shallow/refute_unrecorded pattern)
  - `add-method/tooling/add.py:_effective_autonomy(root, state, slug)` — task-level autonomy resolver; predicate for `advisor_verdict_unrecorded`
Context (working folder):
  - `add-method/tooling/add.py` engine (canonical) + `add-method/src/add_method/_bundled/tooling/` + `.add/tooling/` — all 3 engine trees re-pin on any engine change (ENGINE_MD5 via engine_pin.py)
  - existing guarantee lints for pattern reference: `shallow_deep_check` · `risk_unset` · `refute_unrecorded` · `sensitivity_unset` — the 4 incumbent glints this task extends
  - `add-method/tooling/test_guarantee_audit_lints.py` — the existing glint test suite; 3 new test scenarios join it
  - this task MUST ship BEFORE advisor-gate-relax (the relaxation gate that reads these codes as evidence)
Honors (patterns / conventions):
  - MEASURE-NOT-BLOCK is inviolable: these codes NEVER enter `_audit_findings` (which exits 1); they live only in `_guarantee_lint_notices`, surfaced in cmd_audit at exit 0 — exactly as the 4 incumbent glints
  - ABSENT-block grandfathering: `_section_unfilled` returns False (no flag) when the section heading is wholly absent from body6 — pre-existing tasks that predate the advisor block are never retro-flagged (mirrors shallow/refute_unrecorded ABSENT-means-grandfather rule)
  - engine ships across 3 trees: any add.py change re-pins ENGINE_MD5 + re-bundles (test_shared_engine_pin / test_bundle_parity / test_engine_repin_parity)
  - `cmd_audit` clean-line prints ONLY when `findings` + ALL glint lists are empty — the conjunction at ~line 5692 must extend to include the 3 new glint list guards
  - add.py is PURE/read-only in `_guarantee_lint_notices` (reads TASK.md + state, writes nothing) — new advisor reads follow the same PURE contract
Anchors the contract cites: `_guarantee_lint_notices` · `_raw_phase_bodies` body6 · `_section_unfilled` · `_effective_autonomy` · `_task_sensitivity` · `gate_actor["name"]` · `_AUDIT_REVIEWED_RE` (field-reading model) · cmd_audit clean-line conjunction · the 3 new glint keys

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Three MEASURE-NOT-BLOCK advisor-quality audit codes in `add.py audit`
Framings weighed: extend `_guarantee_lint_notices` with 3 new glint keys surfaced in cmd_audit at exit 0 (chosen) — mirrors the 4 incumbent glint codes exactly; zero gate-blocking behavior · move `advisor_reviewer_is_author` to `_audit_findings` (exit 1) (rejected — milestone plan explicitly designates MEASURE; a human spot-audit backstops; escalation path is preserved as the §3 Least-sure flag) · add a separate `add.py advisor-check` command (rejected — audit is the measurement surface; a new command adds discoverability cost with zero benefit)
Must:
<must>
  - `_guarantee_lint_notices` return dict gains 3 new keys (all list-of-slug): `advisor_verdict_unrecorded`, `advisor_reviewer_is_author`, `advisor_residue_on_mechanical_mis_tier`
  - `advisor_verdict_unrecorded`: MIRRORS `refute_unrecorded` EXACTLY — flag a task slug when phase ∈ {verify, observe, done} AND `_section_unfilled(body6, "### Advisor 3-lens verdict")` is True; NO autonomy filter (phase-only, same as the incumbent `refute_unrecorded`); an ABSENT block grandfathers (never retro-flagged)
  - `advisor_reviewer_is_author`: flag a task slug when phase ∈ {verify, observe, done} AND the advisor block is present AND filled AND both the §6 `Advisor:` name field and `state["tasks"][slug]["gate_actor"]["name"]` are non-empty and compare equal (case-insensitive strip)
  - `advisor_residue_on_mechanical_mis_tier`: flag a task slug when phase ∈ {verify, observe, done} AND `_task_sensitivity(hdr) == "mechanical"` AND the advisor block `Residue:` field is non-empty and not `"none"` AND the advisor block `Verdict:` field starts with `"PASS"`; incoherent tier+residue combination
  - cmd_audit surfaces each new glint key in a dedicated print line (exit 0); print format mirrors the incumbent glints
  - the clean-line conjunction at ~line 5692 extends from 4 to 7 guard terms: all 3 new glint lists must be empty before "audit: clean (N tasks checked)" prints
  - all three codes: exit stays 0; NEVER entered into `_audit_findings`; human spot-audit is the backstop
</must>
Reject:
<reject>
  - task with advisor block ABSENT at verify/observe/done → must NOT flag `advisor_reviewer_is_author` or `advisor_residue_on_mechanical_mis_tier` (no block to read); and an absent block does NOT flag `advisor_verdict_unrecorded` either (grandfather), exactly as `refute_unrecorded` grandfathers an absent Refute-read block
  - any of the 3 new codes → must NOT appear in `_audit_findings` or cause cmd_audit to exit 1
</reject>
After:
<after>
  - `add.py audit` surfaces `advisor_verdict_unrecorded`, `advisor_reviewer_is_author`, and `advisor_residue_on_mechanical_mis_tier` lines for qualifying tasks, all at exit 0
  - `add.py audit` prints "audit: clean (N tasks checked)" only when all 7 glint lists AND findings are empty
  - `add.py audit --json` includes the 3 new keys in the `guarantee_lints` object
  - tasks that predate the advisor block are never retro-flagged (ABSENT-block grandfather holds)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the §6 `Advisor:` field-reading grammar — the advisor block introduced by advisor-review-step uses a line `Advisor: <name>` parseable via a `_AUDIT_REVIEWED_RE`-style `re.compile(r"^Advisor:(.*)$", re.M)` on body6; if the block format differs (e.g. nested heading, different field name), the `advisor_reviewer_is_author` predicate needs a grammar correction — lowest confidence because advisor-review-step is still at ground phase and the §6 block shape is not yet frozen; if wrong: correct the field regex (isolated to the predicate, no contract shape change)
  - [ ] the `Residue:` and `Verdict:` field names and their exact line grammar in the advisor block — assumed to be `Residue: <text>` and `Verdict: <text>` parseable with `re.compile(r"^(Residue|Verdict):(.*)$", re.M)` on body6; if the advisor-review-step block uses different names, update the field readers; if wrong: rename the regex group (isolated)
  - [ ] advisor_verdict_unrecorded introduction split — the context notes that advisor-review-step may add this code first and this task formalizes it; if advisor-review-step has not yet added it, this task introduces all 3; if it already exists in _guarantee_lint_notices when this task builds, this task adds the remaining 2 and the clean-line wiring only, leaving the first code unduplicated
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: advisor_verdict_unrecorded fires for auto task with unfilled advisor section
  Given a task at phase done with autonomy: auto and a "### Advisor 3-lens verdict" section present but unfilled
  When I run add.py audit
  Then it prints "audit: advisor_verdict_unrecorded — 1 task(s): <slug> …" at exit 0
  And the task does not appear in audit findings (exit stays 0)

Scenario: advisor_verdict_unrecorded is silent for a conservative task even if section unfilled
  Given a task at phase done with autonomy: conservative and the advisor section unfilled
  When I run add.py audit
  Then advisor_verdict_unrecorded does NOT include that slug
  And exit is 0 and the task is not in findings

Scenario: advisor_reviewer_is_author fires when reviewer name matches gate actor name
  Given a task at phase done with the advisor block present and filled, Advisor: "Alice", and gate_actor.name "alice"
  When I run add.py audit
  Then it prints "audit: advisor_reviewer_is_author — 1 task(s): <slug> …" at exit 0
  And the task does not appear in audit findings (exit stays 0)

Scenario: advisor_residue_on_mechanical_mis_tier fires for mechanical+residue+PASS
  Given a task at phase done with sensitivity: mechanical, advisor Residue: "some concern", and Verdict: PASS
  When I run add.py audit
  Then it prints "audit: advisor_residue_on_mechanical_mis_tier — 1 task(s): <slug> …" at exit 0
  And the task does not appear in audit findings (exit stays 0)

Scenario: absent advisor block scopes out reviewer and tier checks
  Given a task at phase done with NO "### Advisor 3-lens verdict" section in §6 and autonomy: auto
  When I run add.py audit
  Then advisor_reviewer_is_author does NOT include that slug
  And advisor_residue_on_mechanical_mis_tier does NOT include that slug
  And advisor_verdict_unrecorded DOES include that slug (auto + absent block = grandfathered but auto fires)

Scenario: clean line prints only when all seven glint lists and findings are empty
  Given all tasks at verify/done have advisor sections filled, distinct reviewers, coherent tiers, and no hard findings
  When I run add.py audit
  Then it prints "audit: clean (N tasks checked)" at exit 0
  And none of the seven glint print lines appear
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
MEASURE-NOT-BLOCK  add.py audit   (no new CLI subcommand; extends the existing audit command)

Extends: _guarantee_lint_notices(root, state) -> dict
  New keys (all list[str] of task slugs), added alongside the 4 incumbent keys:

  advisor_verdict_unrecorded[]   # MIRRORS refute_unrecorded EXACTLY (phase-only, NO autonomy filter)
    predicate: phase ∈ {verify, observe, done}
               AND _section_unfilled(body6, "### Advisor 3-lens verdict")
    absent block grandfathers (ABSENT → _section_unfilled returns False → never flagged)

  advisor_reviewer_is_author[]
    predicate: phase ∈ {verify, observe, done}
               AND advisor block PRESENT AND filled (not grandfathered-absent)
               AND re.search(r"^Advisor:(.*)$", _advisor_body, re.M) extracts a non-empty name
               AND state["tasks"][slug].get("gate_actor", {}).get("name", "").strip() non-empty
               AND both names equal case-insensitively
    scope guard: advisor block absent → NOT flagged (no field to read)

  advisor_residue_on_mechanical_mis_tier[]
    predicate: phase ∈ {verify, observe, done}
               AND _task_sensitivity(hdr) == "mechanical"
               AND advisor block PRESENT AND filled
               AND re.search(r"^Residue:(.*)$", _advisor_body, re.M) extracts non-empty text != "none" (stripped, lowercase)
               AND re.search(r"^Verdict:(.*)$", _advisor_body, re.M) extracts text starting with "PASS" (stripped)
    scope guard: advisor block absent → NOT flagged

cmd_audit print lines (exit 0; glints only — never findings):
  advisor_verdict_unrecorded  -> "audit: advisor_verdict_unrecorded — N task(s): <slugs> — fill the Advisor 3-lens verdict (§6); spot-audit is the backstop"
  advisor_reviewer_is_author  -> "audit: advisor_reviewer_is_author — N task(s): <slugs> — advisor and gate actor are the same identity"
  advisor_residue_on_mechanical_mis_tier -> "audit: advisor_residue_on_mechanical_mis_tier — N task(s): <slugs> — mechanical tier with non-none residue and PASS verdict is incoherent; consider re-tiering"

clean-line conjunction extends from 4 to 7 guard terms (clean only when ALL are empty):
  not findings AND not skips
  AND not glints["shallow"] AND not glints["risk_unset"]
  AND not glints["refute_unrecorded"] AND not glints["sensitivity_unset"]
  AND not glints["advisor_verdict_unrecorded"]
  AND not glints["advisor_reviewer_is_author"]
  AND not glints["advisor_residue_on_mechanical_mis_tier"]
  -> "audit: clean (N tasks checked)"

add.py audit --json: guarantee_lints object gains the 3 new keys (list[str])

Invariant: all three codes live ONLY in _guarantee_lint_notices; NEVER in _audit_findings;
           cmd_audit exit stays 0 regardless of glint list contents.
INV (v2): the Advisor:/Residue:/Verdict: fields are read from `_advisor_body` — the slice of
          body6 under the "### Advisor 3-lens verdict" heading up to the next "### " heading —
          NOT from the full body6. The §6 Refute-read verdict block ALSO carries Verdict:/Residue:
          lines, so a full-body6 regex would cross-match the wrong block. Sub-section scoping is
          the correctness fix (re-froze v1→v2 at verify; dogfooded contract amendment).
```

Least-sure flag surfaced at freeze: [contract] `advisor_reviewer_is_author` as MEASURE-NOT-BLOCK (exit 0, glint only) vs. HARD-BLOCK (in `_audit_findings`, exit 1) — the design chose MEASURE per the milestone plan: this is "measure before relax" instrumentation that ships before advisor-gate-relax; a human spot-audit is the backstop, and a reviewer-is-author signal should surface for review rather than auto-block. Cost if wrong: move the code from `_guarantee_lint_notices` to `_audit_findings` and raise exit 1; callers scripting on `audit` exit 0 would be affected.

Status: FROZEN @ v2 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario (22 cases)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_reviewer_is_author_flagged / test_reviewer_differs_not_flagged: §6 Advisor: name vs state gate_actor.name (case-insensitive)
  - test_absent_block_neither_code: a grandfathered legacy task flags NEITHER new code
  - test_mechanical_residue_pass_flagged: mechanical + Residue!=none + Verdict PASS → mis-tier flagged
  - test_mechanical_residue_none_not_flagged / test_nonmechanical_residue_not_flagged: only mechanical mis-tiers
  - test_codes_never_in_findings + test_audit_exit_zero: MEASURE-NOT-BLOCK
  - test_clean_line_suppressed_by_either: clean-line conjunction now 7 terms
</test_plan>

Tests live in: `add-method/tooling/test_advisor_verdict_audit.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. RED test_advisor_verdict_audit.py (22 cases) 2. add the 2 codes to the existing verify/observe/done loop in _guarantee_lint_notices 3. 2 cmd_audit prints + extend clean-line 5→7 4. 3-tree sync + re-pin 5. green full suite

Known-problem fixes: re-adding advisor_verdict_unrecorded (already shipped by review-step) → ADD ONLY the 2 new codes; flagging a grandfathered-absent block → require header PRESENT + filled before reading fields
Strategy actually used: as planned — build subagent (TDD) on canonical, then orchestrator-run 3-tree parity + re-pin; engine-only (no template change), ENGINE_PKG_MD5 unchanged
Safety rule (feature-specific): MEASURE-NOT-BLOCK — both codes glint-only, NEVER in _audit_findings, exit 0; this is the "measure before relax" instrumentation that MUST ship before advisor-gate-relax
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

- [x] all tests pass — full suite 2378/0 green
- [x] coverage did not decrease — +22 new tests (test_advisor_verdict_audit.py)
- [x] no test or contract was altered to make a build pass — the reverse: §3 was AMENDED v1→v2 (Tin-approved change request) to make the CONTRACT match the more-correct build (_advisor_body sub-section scoping). No test weakened; the build was already green against the v2 intent.
- [x] the green was EARNED — independent refute-read (agent aedfdfdf288f320b6) ran 7 adversarial probes, all PASS
- [x] concurrency / timing — _guarantee_lint_notices is pure read-only; no writes, no races
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib re/string only
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the incumbent glint codes
- [ ] a person reviewed and approved the change — AWAITING human gate (risk: high · architecture · conservative)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py audit` names a task whose §6 Advisor == gate actor (advisor_reviewer_is_author) at exit 0 — confirmed by the audit run + test_reviewer_is_author_flagged
- [x] `add.py audit` names a mechanical task with non-none residue + PASS verdict (advisor_residue_on_mechanical_mis_tier) at exit 0 — confirmed by test_mechanical_residue_pass_flagged
- [x] a grandfathered-absent advisor block flags NEITHER new code — confirmed by test_absent_block_neither_code
- [x] both codes appear in `audit --json` guarantee_lints and NEVER in findings[] — confirmed by test_codes_never_in_findings; exit stays 0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — both new keys set in the verify/observe/done loop, printed in cmd_audit, in the 7-term clean-line conjunction, and serialized in --json
- [x] DEAD-CODE (code) — no orphaned symbol; both keys consumed by cmd_audit + the 22 tests
- [x] SEMANTIC (prose) — frozen §3 re-read in full; build matches intent; the one literal-regex delta (_advisor_body vs body6) is disclosed above

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent aedfdfdf288f320b6 (independent) · adversarially checked: scope guards (absent block flags neither code), reviewer==author case-insensitive comparison on _advisor_body (both directions), mechanical mis-tier all 4 boundary conditions + capital-N "None", MEASURE-NOT-BLOCK (neither code in _audit_findings, exit 0), non-vacuous tests on real tmp projects, 7-term clean-line conjunction

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Dogfooded: grandfathered template lacked the block, so it is recorded here by hand.
Advisor: agent aedfdfdf288f320b6
1. Security: CLEAR — MEASURE-NOT-BLOCK by design; reviewer-is-author is a surfaced signal, not a hard block (contract acknowledges the escalation cost)
2. Concurrency: CLEAR — pure read-only function, no writes/races
3. Architecture: CLEAR — the _advisor_body vs body6 delta is RESOLVED: §3 re-frozen v1→v2 (approved by Tin Dang) to specify sub-section scoping + INV note; contract == build again
Verdict: PASS
Residue: none — contract amended to v2 to match the build
Binding: advisory — architecture

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned — build subagent (TDD) on canonical, then orchestrator-run 3-tree parity + re-pin; engine-only (no template change), ENGINE_PKG_MD5 unchanged
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
