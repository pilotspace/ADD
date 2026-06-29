# TASK: advisor-review-step

slug: advisor-review-step · created: 2026-06-29 · stage: mvp · risk: high · sensitivity: architecture
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:_guarantee_lint_notices(root, state) -> dict` — ~line 5625; the MEASURE-NOT-BLOCK lint runner for verify-reached tasks; add `advisor_verdict_unrecorded` here (alongside `refute_unrecorded` at ~5647), detected via `_section_unfilled(body6, "### Advisor 3-lens verdict")`; extend the return dict to include the new key.
  - `add-method/tooling/add.py:cmd_audit` — ~line 5658; consumes `_guarantee_lint_notices` output; add an `advisor_verdict_unrecorded` print block (mirroring the `refute_unrecorded` print at ~5684) and extend the clean-line guard at ~line 5692 to require `glints["advisor_verdict_unrecorded"]` to be empty.
  - `add_engine/predicates.py:_section_unfilled(md_text, header) -> bool` — line 44; PURE predicate; NO CHANGE required — reused as-is with the new header `"### Advisor 3-lens verdict"`.
  - `add-method/tooling/templates/TASK.md.tmpl` — §6 template; insert the new `### Advisor 3-lens verdict` block between `### Refute-read verdict` and `### GATE RECORD`.
  - `add-method/skill/add/advisor.md` — defines the single-subagent delegation pattern; vocabulary source for "security · concurrency · architecture" escalation classes and the HARD-STOP escalation rule.
  - `add-method/skill/add/run.md` — ~line 72; names the three escalation residues (security/concurrency/architecture) under the automated quality gate constraints; the 3-lens mirrors these exactly.
  - `add-method/skill/add/sensitivity.md` — line 14; `mechanical` definition: "the only class a recorded advisor verdict can gate for auto-completion (`advisor-gate-relax`)"; anchors the Binding field logic.
Context (working folder):
  - engine ships across 3 trees: canonical `add-method/tooling/` → `add-method/src/add_method/_bundled/tooling/` + repo-root `.add/tooling/`; any engine change re-pins ENGINE_MD5 (`engine_pin.py`) + re-bundles.
  - template ships across 3 trees: canonical `add-method/tooling/templates/TASK.md.tmpl` → `_bundled` copy + `.claude/skills/add/` copy; all 3 must receive the new block.
  - `add-method/tooling/test_engine_repin_parity.py` · `test_bundle_parity.py` · `test_shared_engine_pin.py` — parity suite that must pass after any engine edit.
Honors (patterns / conventions):
  - MEASURE-NOT-BLOCK invariant: `advisor_verdict_unrecorded` NEVER raises `sys.exit(1)` and NEVER blocks a gate — it surfaces as a notice, `cmd_audit` exits 0, mirroring `refute_unrecorded` exactly.
  - ENGINE NEVER SPAWNS — the block is filled by the orchestrating agent; the engine only detects whether it is filled via `_section_unfilled`.
  - Grandfather rule: ABSENT `### Advisor 3-lens verdict` section (tasks predating this feature) → `_section_unfilled` returns `False` → not flagged; only present-but-unfilled is flagged.
  - The 3-lens vocabulary (security → concurrency → architecture) is already defined in `run.md` and `advisor.md`; this task records and measures it — never invents new vocabulary.
Anchors the contract cites: `_guarantee_lint_notices` · `cmd_audit` clean-line guard · `_section_unfilled` · `### Advisor 3-lens verdict` template block shape · `advisor.md` 3-escalation-class vocabulary · `sensitivity.md` `mechanical` binding definition.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Upgrade the §6 verify section with a tier-aware Advisor 3-lens sequential checklist block (`### Advisor 3-lens verdict`) and a matching MEASURE-NOT-BLOCK engine audit notice `advisor_verdict_unrecorded`.
Framings weighed: new `### Advisor 3-lens verdict` template block in §6 (between `### Refute-read verdict` and `### GATE RECORD`) + engine `advisor_verdict_unrecorded` notice mirroring `refute_unrecorded` (chosen) · replace the `### Refute-read verdict` block entirely (rejected — refute-read is the earned-green anti-gaming check; the 3-lens is a non-functional sweep; distinct purposes, both required for an auto-PASS under `auto`) · run all 3 lenses in parallel (rejected — Security HARD-STOP must short-circuit the checklist; parallel cannot stop early cleanly without extra coordination; sequential matches `run.md` ordering)
Must:
<must>
  - The `### Advisor 3-lens verdict` block is added to `TASK.md.tmpl` §6, positioned between `### Refute-read verdict` and `### GATE RECORD`, with the exact shape specified in §3 CONTRACT.
  - Lenses run SEQUENTIALLY: security → concurrency → architecture. A Security HARD-STOP ends the checklist immediately; concurrency and architecture fields are NOT filled (stop on first HARD-STOP).
  - Verdict is `PASS` or `HARD-STOP` only — never `RISK-ACCEPTED` (security residue is never waivable; non-security residue is surfaced in the Residue field with Verdict: PASS).
  - Binding field: `yes — mechanical` when `sensitivity: mechanical` (the value that `advisor-gate-relax` reads for gating); `advisory — <sensitivity>` for every other sensitivity class.
  - The engine adds `advisor_verdict_unrecorded` to `_guarantee_lint_notices` in `add.py` — detected via `_section_unfilled(body6, "### Advisor 3-lens verdict")`; scope = tasks at phase `verify / observe / done`; MEASURE-NOT-BLOCK, NEVER raises `sys.exit(1)`.
  - `cmd_audit` surfaces `advisor_verdict_unrecorded` as a print notice (exit 0) and the clean-line guard is extended to require `glints["advisor_verdict_unrecorded"]` to be empty before printing "audit: clean".
  - The new block COEXISTS with `### Refute-read verdict` — both blocks must be present and filled in §6 for an auto-PASS under `autonomy: auto`; the refute-read block is byte-identical and unchanged.
  - Parity: engine re-pinned across all 3 tooling trees + re-bundled; `### Advisor 3-lens verdict` block propagated to all 3 template trees.
</must>
Reject:
<reject>
  - a task at verify/observe/done with `### Advisor 3-lens verdict` block present-but-unfilled → audit surfaces `advisor_verdict_unrecorded` (MEASURE-NOT-BLOCK; never blocks the gate; exit 0)
  - a Security lens returning HARD-STOP → Verdict field is `HARD-STOP`; concurrency + architecture lenses are NOT filled; GATE RECORD outcome is `HARD-STOP` (never an auto-PASS from a security finding)
</reject>
After:
<after>
  - every TASK.md generated from `TASK.md.tmpl` after this task ships contains `### Advisor 3-lens verdict` between `### Refute-read verdict` and `### GATE RECORD`.
  - `add.py audit` surfaces `advisor_verdict_unrecorded` for any verify/observe/done task whose `### Advisor 3-lens verdict` block is present-but-unfilled; absent block = grandfathered, never flagged.
  - `add.py audit: clean (N tasks checked)` prints only when BOTH `refute_unrecorded` AND `advisor_verdict_unrecorded` (and all other notice lists) are empty.
  - `### Refute-read verdict` block is byte-identical to before — the new block is purely additive, placed immediately after it.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ RESOLVED at freeze (Tin) — `advisor_verdict_unrecorded` MIRRORS `refute_unrecorded` EXACTLY: phase ∈ {verify,observe,done} only, NO autonomy filter (the incumbent `refute_unrecorded` code at add.py ~5644 has no autonomy guard). An ABSENT block grandfathers, so only tasks created AFTER the template revision that leave the block unfilled are flagged — measure-not-block. If a narrower auto-only scope is ever wanted: add a `_task_autonomy(hdr)=="auto"` predicate to the loop (contained change).
  - [ ] position of the block in `TASK.md.tmpl` — between `### Refute-read verdict` and `### GATE RECORD` is the only sensible location; if wrong: reposition (additive change, no existing filled tasks are affected since they were created before this template revision).
  - [ ] whether the Binding field value needs engine validation or is prose-only — design treats it as prose `advisor-gate-relax` reads by convention, not an engine-enforced field; if wrong: add a `_section_unfilled`-style validator for the binding token — cost is an additional engine predicate.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: full 3-lens verdict recorded — audit does not flag it
  Given an auto task at verify with a filled ### Advisor 3-lens verdict block (all 3 lenses CLEAR, Verdict: PASS, Binding: advisory — architecture)
  When add.py audit runs
  Then advisor_verdict_unrecorded is NOT listed for that task
  And add.py exits with code 0

Scenario: block present-but-unfilled triggers advisor_verdict_unrecorded notice
  Given a task at verify/observe/done whose ### Advisor 3-lens verdict block is still a placeholder (unfilled)
  When add.py audit runs
  Then it prints "audit: advisor_verdict_unrecorded — 1 task(s): <slug> — record the 3-lens advisor verdict (§6); a spot-audit is the backstop"
  And add.py exits with code 0 (MEASURE-NOT-BLOCK — never sys.exit(1))

Scenario: Security HARD-STOP ends the checklist and gates HARD-STOP
  Given a task at verify with ### Advisor 3-lens verdict block: Security: HARD-STOP: <finding> and Verdict: HARD-STOP (concurrency + architecture fields intentionally blank)
  When the task's GATE RECORD is examined
  Then the Verdict field reads HARD-STOP
  And the GATE RECORD Outcome reads HARD-STOP (never PASS or RISK-ACCEPTED)
  And add.py audit does NOT flag advisor_verdict_unrecorded for this task (block is filled)

Scenario: mechanical sensitivity uses binding "yes — mechanical"
  Given a task at verify with sensitivity: mechanical and a filled verdict block with Verdict: PASS and Binding: yes — mechanical
  When add.py audit runs
  Then advisor_verdict_unrecorded is NOT listed for that task
  And the Binding field reads "yes — mechanical"

Scenario: non-mechanical sensitivity uses advisory binding
  Given a task at verify with sensitivity: architecture and a filled verdict block with Verdict: PASS and Binding: advisory — architecture
  When add.py audit runs
  Then advisor_verdict_unrecorded is NOT listed for that task
  And the Binding field reads "advisory — architecture" (not "yes — mechanical")

Scenario: legacy task without the block is grandfathered
  Given a task at verify/observe/done that predates this feature and has no ### Advisor 3-lens verdict section in its §6
  When add.py audit runs
  Then advisor_verdict_unrecorded is NOT listed for that task
  And add.py waves and all other commands produce byte-identical output to before

Scenario: clean line prints only when advisor_verdict_unrecorded list is also empty
  Given all tasks at verify/observe/done have both ### Refute-read verdict and ### Advisor 3-lens verdict blocks filled, and there are no other findings
  When add.py audit runs
  Then it prints "audit: clean (N tasks checked)"
  And advisor_verdict_unrecorded does NOT appear anywhere in the output
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE  add-method/tooling/add.py

  _guarantee_lint_notices(root, state) -> dict
    EXTEND with advisor_verdict_unrecorded[]:
      for each slug at phase ∈ {verify, observe, done}:
        body6 = _raw_phase_bodies(root, slug).get(6, "")
        if _section_unfilled(body6, "### Advisor 3-lens verdict"):
            advisor_verdict_unrecorded.append(slug)
      (no autonomy filter — mirrors refute_unrecorded exactly as coded)
    return dict:
      {"shallow": […], "risk_unset": […], "refute_unrecorded": […],
       "sensitivity_unset": […], "advisor_verdict_unrecorded": […]}

  cmd_audit(args) -> None
    EXTEND print block:
      if glints["advisor_verdict_unrecorded"]:
          av = glints["advisor_verdict_unrecorded"]
          print(f"audit: advisor_verdict_unrecorded — {len(av)} task(s): {', '.join(av)} "
                f"— record the 3-lens advisor verdict (§6); a spot-audit is the backstop")
    EXTEND clean-line guard (~line 5692):
      if not findings and not skips
              and not glints["shallow"] and not glints["risk_unset"]
              and not glints["refute_unrecorded"] and not glints["sensitivity_unset"]
              and not glints["advisor_verdict_unrecorded"]:          # ← new guard
          print(f"audit: clean ({checked} tasks checked)")
    exit 0 always (MEASURE-NOT-BLOCK — only real findings in `findings` raise sys.exit(1))

PREDICATE  add_engine/predicates.py:_section_unfilled  — NO CHANGE (reused as-is)

TEMPLATE  add-method/tooling/templates/TASK.md.tmpl
  §6 addition — insert immediately after the ### Refute-read verdict block, before ### GATE RECORD:

    ### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
    > Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
    > order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
    > sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
    > The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
    Advisor: <agent-id | self>
    1. Security: <CLEAR | HARD-STOP: finding>
    2. Concurrency: <CLEAR | RESIDUE: finding>
    3. Architecture: <CLEAR | RESIDUE: finding>
    Verdict: <PASS | HARD-STOP>
    Residue: <none | summary>
    Binding: <yes — mechanical | advisory — <sensitivity>>

COEXISTENCE  §6 block order (unchanged blocks shown for position; all required):
  ### Refute-read verdict        (UNCHANGED — anti-gaming earned-green check)
  ### Advisor 3-lens verdict     (NEW — non-functional sweep, placed immediately after)
  ### GATE RECORD                (UNCHANGED)

VERDICT STATES:
  All 3 lenses CLEAR                    → Verdict: PASS
  Security: HARD-STOP: <finding>        → Verdict: HARD-STOP; lenses 2–3 NOT filled; no auto-PASS
  Concurrency or Architecture residue   → Verdict: PASS, Residue: <summary>
    (non-security residue is surfaced in Residue, not a HARD-STOP unless also a security gap)

BINDING LOGIC (prose field, no engine enforcement):
  sensitivity: mechanical  → Binding: yes — mechanical    (advisor-gate-relax may gate on this)
  all other sensitivity    → Binding: advisory — <sensitivity>   (surfaced, not engine-enforced)

PARITY (same pattern as all prior engine changes):
  engine re-pin: ENGINE_MD5 updated in add-method/tooling/engine_pin.py across 3 trees
  template propagated: canonical → _bundled copy + .claude/skills/add/ copy (3 template trees)
  suite: test_shared_engine_pin · test_bundle_parity · test_engine_repin_parity must pass
```

Least-sure flag surfaced at freeze: [contract] whether the `### Advisor 3-lens verdict` block **REPLACES or COEXISTS** with the `### Refute-read verdict` block — design chose COEXIST (refute-read = anti-gaming earned-green check; 3-lens = non-functional security/concurrency/architecture sweep; distinct roles, both required for an auto-PASS under `autonomy: auto`). If wrong: merge into one combined block — cost is a non-trivial template restructure and the loss of the distinct "was green earned?" vs. "does it pass non-functional review?" signals.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario (17 cases across 8 classes)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_filled_block_not_flagged: a filled §6 Advisor 3-lens block → advisor_verdict_unrecorded omits the slug
  - test_unfilled_block_flagged: present-but-unfilled block at verify → glint lists slug; audit prints it at exit 0
  - test_security_hardstop_shape: Verdict HARD-STOP with lenses 2–3 blank is a valid recorded verdict
  - test_mechanical_binding / test_advisory_binding: Binding text "yes — mechanical" vs "advisory — architecture"; neither flagged when filled
  - test_legacy_grandfathered: a task with NO advisor section → never flagged; other commands byte-identical
  - test_clean_line_requires_advisor_empty: "audit: clean" prints only when advisor_verdict_unrecorded is also empty
</test_plan>

Tests live in: `add-method/tooling/test_advisor_review_step.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. RED test_advisor_review_step.py (17 cases) 2. extend _guarantee_lint_notices + cmd_audit (mirror refute_unrecorded exactly) 3. insert §6 template block after Refute-read 4. 3-tree sync (prepare_bundle + .add mirror) + re-pin ENGINE_MD5 5. green full suite

Known-problem fixes: nested `<sensitivity>` placeholder trips the v16 tag census → update FROZEN_TAGS to the new frozen reality (not reword the frozen block); add an autonomy filter by mistake → mirror refute_unrecorded EXACTLY (phase-only)
Strategy actually used: as planned — built canonical via a build subagent (TDD), then ran the 3-tree parity ceremony + re-pin myself; one ripple (FROZEN_TAGS census) corrected to reflect the frozen template
Safety rule (feature-specific): MEASURE-NOT-BLOCK is inviolable — the new glint NEVER enters `findings`/exits 1; absent-block grandfathers
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

- [x] all tests pass — full suite 2356/0 green
- [x] coverage did not decrease — +17 new tests (test_advisor_review_step.py)
- [~] no test or contract was altered during build — §3 contract UNTOUCHED; ONE guard-test census corrected: test_scope_decl_template FROZEN_TAGS += 'sensitivity' (the frozen block's `Binding: advisory — <sensitivity>` placeholder is a NEW token the v16 vocab census pinned against). Not a weakening — it records the new frozen template reality. FLAGGED for human spot-audit.
- [x] the green was EARNED — independent refute-read (agent a194661134d8acd69) ran 6 adversarial probes, all PASS
- [x] concurrency / timing — _guarantee_lint_notices is a pure read-only function over immutable task files; no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib re/string predicate
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the incumbent refute_unrecorded glint exactly
- [ ] a person reviewed and approved the change — AWAITING human gate (risk: high · architecture · conservative)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a new TASK.md generated from the template carries `### Advisor 3-lens verdict` between Refute-read and GATE RECORD — confirmed: templates/TASK.md.tmpl §6 block present, em-dashes intact (refute-read probe 5)
- [x] a task at verify with that block present-but-unfilled is named by `add.py audit` (exit 0, never exit 1) — confirmed: scratch-project break attempt [A] printed the slug at exit 0 (refute-read probe 6)
- [x] a legacy task lacking the block is NOT flagged — confirmed: this milestone's `add.py audit` prints NO advisor_verdict_unrecorded; break attempt [C] grandfathered
- [x] all 3 add.py + 3 template copies byte-identical and ENGINE_MD5 re-pinned — confirmed: md5 trio == 3cadd4dd…, green test_scope_decl_template / test_bundle_parity

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `advisor_verdict_unrecorded` referenced in `_guarantee_lint_notices` (set), `cmd_audit` (print + clean-line guard), and the return dict; template block fields read by `_section_unfilled`
- [x] DEAD-CODE (code) — no orphaned symbol; the key is consumed by cmd_audit and the test suite
- [x] SEMANTIC (prose) — frozen §3 re-read in full; the build matches the contract verbatim (mirror, coexist, grandfather)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent a194661134d8acd69 (independent) · adversarially checked: exact-mirror of refute_unrecorded (no autonomy filter), MEASURE-NOT-BLOCK (key never in _audit_findings, exit 0), grandfather (absent block→False), non-vacuous behavioral tests on real tmp projects, 3-tree template byte-identity, live scratch break attempt (unfilled→flagged, filled→clears, stripped→grandfathered)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Dogfooded: this task built the block, so it records its own (grandfathered template lacked it).
Advisor: agent a194661134d8acd69
1. Security: CLEAR — pure read-only predicate, no injection surface
2. Concurrency: CLEAR — pure function over immutable task files, no shared state
3. Architecture: CLEAR — the flagged residue is CLOSED: test_clean_line_appears_when_advisor_also_empty now provisions a fully-clean task and asserts the POSITIVE "audit: clean" line (both suppress + appear directions pinned); re-crossed tests→build to re-baseline the tamper snapshot
Verdict: PASS
Residue: none
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
- [AI] specify — chose new `### Advisor 3-lens verdict` template block in §6 (between `### Refute-read verdict` and `### GATE RECORD`) + engine `advisor_verdict_unrecorded` notice mirroring `refute_unrecorded`; rejected replace the `### Refute-read verdict` block entirely (rejected — refute-read is the earned-green anti-gaming check; the 3-lens is a non-functional sweep; distinct purposes, both required for an auto-PASS under `auto`) · run all 3 lenses in parallel (rejected — Security HARD-STOP must short-circuit the checklist; parallel cannot stop early cleanly without extra coordination; sequential matches `run.md` ordering)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — built canonical via a build subagent (TDD), then ran the 3-tree parity ceremony + re-pin myself; one ripple (FROZEN_TAGS census) corrected to reflect the frozen template
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
