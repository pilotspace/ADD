# TASK: Mandatory recorded earned-green refute-read verdict — a §6 field the audit shape-checks before an auto-PASS is valid

slug: self-grading-refute-record · created: 2026-06-28 · stage: mvp · risk: high
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
- `add.py:cmd_gate` (×3 trees, ~993) — THE single verify gate (the AI runs `add.py gate PASS`; an "auto-PASS" is self-gating under `autonomy: auto`). A completing PASS/RISK-ACCEPTED runs a guard chain (verify-phase · `unguarded_high_risk_auto` · `_tamper_guard` · `_scope_guard` · `_consumer_stale_guard` · `component_green_bar_uncited`) THEN sets `phase=done` + records the gate. The new `refute_record_missing` guard inserts into this chain (completing PASS only, BEFORE the waiver write — never launderable through RISK-ACCEPTED, never on HARD-STOP).
- `add.py:_driver_stop` (~972) / `_effective_autonomy` (~983) — an AUTO-PASS ⟺ `_effective_autonomy(root,state,slug)=="auto"` (verify gate not human-owned). The new guard fires ONLY on an auto-PASS; a conservative/manual gate (human owns it) is the escape — no new `--force`.
- `add.py:_section_unfilled(body, heading)` (used ~5128) — presence-AND-unfilled check; an ABSENT block grandfathers a legacy task (never retro-flagged). Reused to test the new §6 refute block is filled.
- `add.py:_guarantee_lint_notices` (~5116) + `cmd_audit` (~5135) — the PRESENCE-ONLY MEASURE-NOT-BLOCK audit channel (exit 0); add a `refute_unrecorded` notice for review visibility (mirrors `shallow`/`risk_unset`).
- `add.py:_stamp_gate_record` (~199) — gate-record-writeback precedent: mirror state→§6, rewrite ONLY a `<…>` placeholder line, a hand-filled line is byte-untouched (grandfather). Model for the verdict block's placeholder semantics.
- `add.py:cmd_heal` (~1228) / `_heal_or_escalate` (~3790) — a NOT-EARNED verdict routes here (return-to-build ≤HEAL_CAP, then HARD-STOP escalation; a gamed green is never auto-passed). Already exists — the new field's NOT-EARNED branch REUSES it; no engine change to heal.
- `templates/TASK.md.tmpl` §6 (×2 tooling trees: add-method + _bundled; ~127-155) — add a `### Refute-read verdict` block AFTER `### Deep checks`, BEFORE `### GATE RECORD`; the existing §6 checklist line 132 already names the refute-read as "recommended under auto" — this PROMOTES it to a recorded, gate-checked field.

Context (working folder):
- Guide prose (×3 skill trees): `run.md` auto-gate disclosure (a run may auto-PASS on evidence; refute-read "recommended" → now "recorded verdict REQUIRED for an auto-PASS") · `phases/6-verify.md` (the earned-green refute-read rubric — names where the verdict is recorded + the NOT-EARNED→heal route).
- Book (×3 tracked trees): `docs/08-step-6-verify.md` — the verify chapter's auto-PASS precondition narrative (this task ADDS the recorded-refute precondition; `stale-guide-sync`[M5] later UNIFIES the precondition list across run.md/6-verify.md/ch.08).
- `.add/milestones/flow-honesty/MILESTONE.md` — risky-contract-to-freeze-first (line 24: "the recorded earned-green refute-read verdict field in §6 that the audit shape-checks → owning task self-grading-refute-record"); exit criterion (line 41): "an auto-PASS is invalid without a recorded earned-green refute-read verdict in §6 (verify: test_refute_record_required)".

Honors (patterns / conventions):
- judgment-free engine: the guard checks the verdict block is FILLED (no `<…>` placeholder), never the verdict's TRUTH — a self-recorded `EARNED` passes the presence check; honesty is the AI's/human's burden. Mirrors `_guarantee_lint_notices` (shape, not meaning).
- grandfather absent, never retro-red: an ABSENT refute block (every pre-this-task task + the 57 fixtures) grandfathers — the guard fires ONLY on a present-but-unfilled block. New tasks get the block from the template (bounds blast radius like guarantee-audit-lints).
- the ESCAPE is the autonomy DIAL, not a new `--force`: lower to conservative/manual → a human owns the gate → not an auto-PASS → the mandate doesn't apply (human judgment is the stronger backstop). Reserves forceable gates for the two structural holes (freeze, delta-drain) per the milestone ethic.
- engine NEVER spawns the refute-read — the AI records the verdict (advisor.md/run.md spawn-is-advisory invariant unchanged). security HARD-STOP untouched; a NOT-EARNED verdict still routes through the existing `cmd_heal`/HEAL_CAP→HARD-STOP, never auto-passed.
- 3-tree byte-identity (add.py ENGINE_MD5 · skill guides test_tree_parity+test_bundle_parity · book test_book_parity+bundle · template in tooling+_bundled) · lean byte budget (test_skill_lean) for run.md/6-verify.md edits · ENGINE_PKG_MD5 UNCHANGED (add_engine/ untouched — only add.py).

Anchors the contract cites: `cmd_gate` · `_effective_autonomy`/`_driver_stop` · `_section_unfilled` · the new `### Refute-read verdict` §6 block + its `Verdict:`/`By:` fields · reject `refute_record_missing` · `_guarantee_lint_notices` (`refute_unrecorded` notice) · `cmd_heal`/`_heal_or_escalate` (NOT-EARNED route) · `_stamp_gate_record` (placeholder/grandfather precedent) · new `test_refute_record_required.py`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Promote the earned-green refute-read to a RECORDED §6 verdict, and make `add.py audit` MEASURE whether it was recorded — a non-failing `refute_unrecorded` notice — paired with an honest disclosure that under `autonomy: auto` a recorded verdict is REQUIRED, backstopped by the audit notice + a human spot-audit. MEASURE-NOT-BLOCK: NO new hard gate (the measured ~167-test blast radius + the milestone's "reserve forceable gates for the two structural holes" ethic ruled the gate out). Engine never spawns the refute-read; it only measures PRESENCE, never the verdict's truth.
Framings weighed: measure-only audit notice + disclosure (chosen — engine adds a `refute_unrecorded` notice, zero test blast, consistent with the milestone ethic + the `security-escalation-disclosure` precedent; the auto mandate is DISCLOSED in run.md/6-verify.md/book and surfaced by audit + a human spot-audit) · universal hard gate at auto-PASS (MEASURED to break ~167 tests because gate→done is a universal setup primitive — declined by Tin after the scratch probe 2026-06-28) · opt-in hard gate, await_confirm-style (zero blast but conditional enforcement — a half-measure, declined)
Must:
<must>
  - Add a `### Refute-read verdict` block to the §6 template (×2 tooling trees: add-method/tooling + _bundled), placed AFTER `### Deep checks` and BEFORE `### GATE RECORD`, with a `<…>`-placeholder `Verdict:` line (`EARNED | NOT-EARNED`) + a `By:` line (`self | agent <id>` · what was adversarially checked).
  - `_guarantee_lint_notices` gains a `refute_unrecorded` key: tasks at phase ∈ {verify, observe, done} whose §6 refute block is PRESENT-but-unfilled (`_section_unfilled` — still holds the `<…>` placeholder). An ABSENT block grandfathers (legacy task / fixture never retro-flagged), exactly like `shallow`/`risk_unset`.
  - `cmd_audit` prints `refute_unrecorded — N task(s): <slugs>` (one grouped line, like `risk_unset`) and adds it to the `--json` `guarantee_lints` object — MEASURE-NOT-BLOCK: the audit EXIT CODE stays 0 (only real `_audit_findings` raise it).
  - NO `cmd_gate` change: a present-but-unfilled refute block NEVER blocks a gate (auto OR human) — measure, never block. The completing-gate guard chain is byte-unchanged.
  - Disclose the mandate honestly: `run.md` (auto bullet) + `phases/6-verify.md` (×3 skill trees) + book `08-step-6-verify.md` (×3 tracked) state that under `auto` a recorded refute verdict is REQUIRED, the engine MEASURES it (`audit: refute_unrecorded`) but does NOT auto-block, and a human spot-audit is the backstop for a missing record — the same honor-system disclosure shape as the security blind-spot ([[security-escalation-disclosure]]).
  - The engine NEVER judges the verdict's TRUTH (a self-recorded `EARNED` satisfies the presence measure) and NEVER spawns the refute-read; a `NOT-EARNED` verdict routes through the EXISTING `cmd_heal`/`_heal_or_escalate` (no heal change). judgment-free; security HARD-STOP + the two structural forceable gates (freeze, delta-drain) byte-unchanged.
  - Reword the milestone exit criterion (MILESTONE.md line 41) from "an auto-PASS is invalid without a recorded verdict" → "audit surfaces `refute_unrecorded` for a verify+ task whose refute verdict is unrecorded" (the measure, not a hard gate). The MILESTONE.md invites this ("update whenever a task reveals a milestone gap").
</must>
Reject:
<reject>
  - none new — `refute_unrecorded` is a NON-FAILING NOTICE, not a refusal (no reject code; `add.py audit` exit stays 0). The `refute_record_missing` hard gate was measured at ~167-test blast and ruled out; measure-not-block has no rejection surface.
</reject>
After:
<after>
  - a verify+ task whose §6 refute block is present-but-unfilled appears in `audit: refute_unrecorded` (exit 0); filling the verdict OR an absent block (legacy) clears it.
  - NO gate is blocked by a refute record (auto or human) — the completing-gate path is byte-unchanged; gate-PASS setups across the suite are unaffected.
  - `run.md` + `phases/6-verify.md` + book ch.08 disclose the auto mandate + the audit/spot-audit backstop; the milestone exit criterion is reworded to the measure.
  - full suite green; add.py 3-tree byte-identity + ENGINE_MD5 re-pinned (ENGINE_PKG_MD5 unchanged); template parity (tooling + _bundled); skill+book parity; lean budget honored.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ✓ RESOLVED (Tin, 2026-06-28) — initial pick was design A (hard gate, grandfather-absent); a scratch probe MEASURED A at ~167 broken tests (gate→done is a universal setup primitive) → Tin re-decided to **C: measure-only audit notice**. No hard gate, no `cmd_gate` change, no new reject code; the auto mandate is DISCLOSED + surfaced by `audit: refute_unrecorded` + a human spot-audit. Honors the milestone "reserve forceable gates for the two structural holes" ethic.
  ✓ RESOLVED (Tin, 2026-06-28): this task stays `risk: high` + `autonomy: conservative` — Tin owns its verify gate (matches the 3 method-defining siblings; a milestone-method change even as a notice). Header set.
  - [ ] residual blast radius of C: adding the §6 block to the template makes NEW tasks carry an unfilled block, so `audit`-clean-asserting + §6-shape fixtures may newly list `refute_unrecorded` — bounded (the guarantee-audit-lints class, ~handful), measured before build. The new `### Refute-read verdict` heading must stay inert to `_stamp_gate_record`/`_stamp_adr_record` (both key off their own headings) — confirmed by a write-back test on a §6 carrying the block.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: audit surfaces an unrecorded refute verdict, never fails on it
  Given a task at verify (or observe/done) whose §6 `### Refute-read verdict` block still holds its `<…>` placeholder
  When `add.py audit` runs
  Then a `refute_unrecorded` line names the task
  And the audit exit code stays 0 (measure-not-block)

Scenario: a recorded verdict clears the notice
  Given the same task with the block filled `Verdict: EARNED` + a `By:` line (no `<…>` placeholder)
  When `add.py audit` runs
  Then the task is NOT listed under refute_unrecorded

Scenario: a legacy task with no refute block grandfathers
  Given a task at verify whose §6 has NO `### Refute-read verdict` block (pre-this-task shape)
  When `add.py audit` runs
  Then the task is NOT listed under refute_unrecorded — an absent block is never retro-flagged

Scenario: an unrecorded verdict never blocks a gate (measure, not block)
  Given a task at verify, effective autonomy auto, with the refute block present-but-unfilled
  When `add.py gate PASS` is run
  Then PASS is recorded and the task advances to done — the completing-gate path is byte-unchanged
  And no `refute_record_missing` (or any new) refusal exists

Scenario: a freshly created task carries the verdict block
  Given `add.py new-task <slug>` just scaffolded a TASK.md from the template
  When its §6 is read
  Then it contains the `### Refute-read verdict` block with the `<…>` placeholder, between `### Deep checks` and `### GATE RECORD`

Scenario: the gate-record + ADR write-backs are inert to the new block
  Given a task whose §6 has the new verdict block AND its `### GATE RECORD` / §7 `### Decisions (ADR)` placeholders
  When a completing gate is recorded
  Then `_stamp_gate_record` stamps the GATE RECORD and `_stamp_adr_record` harvests the ADR exactly as before — the new heading is mistaken for neither

Scenario: the auto mandate is disclosed in the guides and book
  Given the shipped run.md, phases/6-verify.md, and book 08-step-6-verify.md
  When their refute-read passages are read
  Then each states that under auto a recorded verdict is REQUIRED, surfaced by `audit: refute_unrecorded` + a human spot-audit, and that the engine measures presence (never the verdict's truth) and never auto-blocks
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# ── §6 template block (templates/TASK.md.tmpl, ×2 tooling trees) ──────────────
### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED → `add.py heal`). The engine
> MEASURES this is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent <id>> · adversarially checked: <what was probed>
#   ^ a line still holding `<…>` = UNFILLED. Both lines filled (no `<…>`) = recorded.

# ── engine: audit NOTICE only (add.py _guarantee_lint_notices -> dict) — MEASURE-NOT-BLOCK ──
_guarantee_lint_notices(root, state) gains key  refute_unrecorded: [slug, …]
  # tasks at phase ∈ {verify, observe, done} whose §6 `### Refute-read verdict` block is
  # PRESENT-but-unfilled (_section_unfilled(body, "### Refute-read verdict")).
  # ABSENT block -> NOT listed (grandfather, like shallow / risk_unset).
cmd_audit prints (text):  "audit: refute_unrecorded — N task(s): <slugs>"   # ONE grouped line
cmd_audit --json:  guarantee_lints["refute_unrecorded"] = [slug, …]         # additive key
  exit code: UNCHANGED — only _audit_findings raise it; this notice never does (exit 0)

# ── cmd_gate: UNCHANGED ── no new guard, no reject code; an unfilled block blocks nothing.
# ── NO 4xx ── measure-not-block has no rejection surface.

Schema: NO state.json change (verdict lives in §6 TASK.md text, read fresh; mirrors the
  Deep-checks / risk_unset presence lints). add_engine/* UNTOUCHED -> ENGINE_PKG_MD5 unchanged;
  add.py changes (only _guarantee_lint_notices + cmd_audit print) -> ENGINE_MD5 re-pinned ×3.
  Template ×2 (tooling + _bundled). Guides ×3 + book ×3. MILESTONE.md exit-criterion line reworded.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
- [scope] design C reverses the initial A pick after a MEASURED ~167-test blast radius for the hard gate. C is measure-only (an `audit: refute_unrecorded` notice + disclosure), so "an auto-PASS is invalid without a verdict" SOFTENS to "audit surfaces an unrecorded verdict" — the milestone exit criterion (line 41) is reworded to the measure (the MILESTONE.md invites this). If you want hard enforcement instead, that is design A and its ~167-test sweep.
- [contract] the new `### Refute-read verdict` heading sits BETWEEN `### Deep checks` and `### GATE RECORD` — inert to `_stamp_gate_record`/`_stamp_adr_record` (both key off their OWN headings); cost if wrong: a write-back stamps the wrong block. Mitigated by the §2 inertness scenario before any build. Residual blast: `audit`-clean / §6-shape fixtures may newly list `refute_unrecorded` (guarantee-audit-lints class; ~handful) — measured before build.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + scenario has a test; the new notice + the gate-unaffected guarantee both exercised on the real CLI.
Plan (one test per scenario, asserting behavior not internals) — in `add-method/tooling/test_refute_record_required.py`:
<test_plan>
  - test_audit_surfaces_unrecorded: verify+ task, §6 refute block holds `<…>` / act `audit` / assert stdout has `refute_unrecorded` naming the slug AND exit 0
  - test_recorded_verdict_clears_notice: fill `Verdict: EARNED` + `By:` (no `<…>`) / `audit` / assert slug NOT under refute_unrecorded
  - test_absent_block_grandfathers: §6 with NO refute block / `audit` / assert slug NOT listed (legacy never retro-flagged)
  - test_gate_never_blocked_by_unrecorded: auto task, unfilled block / `gate PASS` / assert exit 0 + phase==done + gate==PASS (measure-not-block; no refute_record_missing)
  - test_no_new_reject_code_in_engine: assert the string `refute_record_missing` is ABSENT from add.py (no hard gate shipped)
  - test_template_carries_verdict_block: `new-task` / read §6 / assert `### Refute-read verdict` + `<…>` placeholder present, ordered AFTER `### Deep checks` and BEFORE `### GATE RECORD`
  - test_writebacks_inert_to_new_block: a §6 with the new block + GATE RECORD/§7 ADR placeholders / record a gate / assert `_stamp_gate_record` stamped GATE RECORD AND `_stamp_adr_record` harvested the ADR (neither captured the new heading)
  - test_audit_json_has_refute_key: `audit --json` / assert `guarantee_lints.refute_unrecorded` is a list
  - test_disclosure_in_guides_and_book: assert run.md + phases/6-verify.md + book 08-step-6-verify.md each contain the auto-mandate + `refute_unrecorded` + spot-audit disclosure (canonical tree)
  - test_exit_criterion_reworded: assert MILESTONE.md line for this task names the measure (`refute_unrecorded` / "audit surfaces"), not "auto-PASS is invalid"
</test_plan>
Existing suites that ride along: test_guarantee_lints (new notice is additive — confirm shallow/risk_unset unchanged), test_bundle_parity + test_shared_engine_pin + test_tree_parity + test_book_parity (mirrors/pins), test_skill_lean (rebaseline if run.md/6-verify.md grow), plus a handful of audit-clean fixtures that must stay clean (well-form their §6 refute block).

Tests live in: `add-method/tooling/test_refute_record_required.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/add.py` `.add/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/skill/add/run.md` `.claude/skills/add/run.md` `add-method/src/add_method/_bundled/skill/add/run.md` `add-method/skill/add/phases/6-verify.md` `.claude/skills/add/phases/6-verify.md` `add-method/src/add_method/_bundled/skill/add/phases/6-verify.md` `add-method/docs/08-step-6-verify.md` `add-method/src/add_method/_bundled/docs/08-step-6-verify.md` `add-method/../08-step-6-verify.md` `.add/milestones/flow-honesty/MILESTONE.md`
<!-- `add-method/tooling/` is a DIRECTORY token (subtree containment via _in_scope) — covers canonical add.py + engine_pin.py (re-pin) + templates/TASK.md.tmpl + the new test_refute_record_required.py + collateral fixture fixes (test_guarantee_lints, test_skill_lean rebaseline, the audit-clean fixtures that must stay clean). The other 2 add.py + 2 template mirrors declared explicitly. skill run.md + phases/6-verify.md ×3 trees; book 08-step-6-verify.md ×3 TRACKED (canonical docs · _bundled/docs · repo-root via the `add-method/..` climb). `.add/tooling/*` + `.add/milestones/*` are `_SCOPE_EXCLUDE_DIRS`-pruned (gate-invisible) → declared for honesty, propagated by hand. add_engine/ UNTOUCHED (ENGINE_PKG_MD5 unchanged). Modeled on freeze-gate-universal §5 (directory token for the collateral sweep). -->
Strategy (ordered batches): 1. write `test_refute_record_required.py` RED (notice fires/clears/grandfathers · gate-unaffected · no refute_record_missing in engine · template carries block · writebacks inert · disclosure · exit-criterion reworded). 2. add the `### Refute-read verdict` block to canonical `templates/TASK.md.tmpl` (after Deep checks, before GATE RECORD). 3. extend `_guarantee_lint_notices` → `refute_unrecorded` (present-but-unfilled at verify+, `_section_unfilled`) + `cmd_audit` text line + `--json` key; NO cmd_gate change. 4. measure the residual blast (run suite; fix the audit-clean / §6-shape fixtures by well-forming their refute block — all test edits in the TESTS phase to dodge the tamper tripwire). 5. write-once-copy add.py + template byte-identical to `.add/tooling/` + `_bundled/tooling/`; re-aim ENGINE_MD5 (PKG unchanged) in engine_pin.py. 6. edit canonical run.md + phases/6-verify.md → copy to `.claude/skills/add/` + `_bundled/skill/add/`; rebaseline test_skill_lean if needed (ratio-kept). 7. edit canonical book 08-step-6-verify.md → copy to repo-root + `_bundled/docs/`. 8. reword MILESTONE.md exit-criterion line 41 to the measure. 9. full suite + check + audit green.
Known-problem fixes: a §6-template change ripples into §6-shape + audit-clean fixtures (the guarantee-audit-lints class) — well-form their refute block in the TESTS phase, not at build (tamper tripwire watches the §4-declared red set only, but doing test edits in TESTS keeps it clean) · the new heading must NOT be captured by `_stamp_gate_record`/`_stamp_adr_record` — covered by test_writebacks_inert · book repo-root token needs the `add-method/..` climb (bare name → task dir → false scope_violation) · run.md=ORCHESTRATION lean pool, phases/6-verify.md=PHASES pool — rebaseline baseline += ⌈added÷ratio⌉, ratio kept · `_section_unfilled` ABSENT-block returns False (grandfather) — reused exactly as shallow_deep_check.
Strategy actually used: as planned — the 9 ordered batches ran in sequence with one detour. The lean reclaim (batch 6) cost ~360 B because the disclosure landed in TWO pools (ORCHESTRATION run.md + PHASES 6-verify.md); reclaimed from each guide's own restatement-of-run.md prose, NO rebaseline (honored "never weaken the budget"). A first refute-read over-trim hit 3 PINNED anchors — `overfit to the test fixtures` · `the engine never classifies` · the `HARD-STOP and is never auto-passed` safety line (split across a blockquote wrap) — restored verbatim, then re-reclaimed from non-pinned prose. Shipped exactly to the frozen §3: NO cmd_gate change, NO `refute_record_missing` reject, ENGINE_PKG_MD5 unchanged (add_engine untouched); refute block dogfooded onto this very task's §6.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
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

- [x] all tests pass — full suite 2157/0; new test_refute_record_required 13/13; check 474/0
- [x] coverage did not decrease — additive (one dict key + one print branch + one template block); no path removed
- [x] no test or contract was altered during build — tamper guard green at build→verify; §4 red set untouched
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP) — refute-read recorded below: EARNED
- [x] concurrency / timing of the risky operation is safe — N/A: `_guarantee_lint_notices` is a pure read of TASK.md + state; no new IO/concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; stdlib only; no new import
- [x] layering & dependencies follow CONVENTIONS.md — add_engine UNTOUCHED (ENGINE_PKG_MD5 unchanged); change confined to add.py + template + guides/book
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py audit` on a board with a verify+ task whose §6 refute block is still a placeholder prints ONE grouped `refute_unrecorded — N task(s):` naming the slug, and exits 0 — confirmed by a live run + test_audit_surfaces_unrecorded / test_one_grouped_line
- [x] a filled `Verdict: EARNED` clears the notice; an ABSENT block (legacy) is never listed; a pre-verify task is silent — confirmed by test_recorded_verdict_clears_notice / test_absent_block_grandfathers / test_not_at_verify_is_silent
- [x] `add.py gate PASS` on an auto task with an unfilled refute block STILL records PASS→done, and the string `refute_record_missing` is ABSENT from add.py — confirmed by test_gate_never_blocked_by_unrecorded + test_no_new_reject_code_in_engine (measure-not-block)
- [x] `new-task` scaffolds §6 with `### Refute-read verdict` + a placeholder verdict line, ordered AFTER Deep checks and BEFORE GATE RECORD; a gate stamps GATE RECORD + harvests §7 ADR with the block intact (count 1) — confirmed by test_template_carries_verdict_block + test_writebacks_inert_to_new_block
- [x] `audit --json` carries `guarantee_lints.refute_unrecorded`; run.md + phases/6-verify.md + book 08-step-6-verify.md disclose the auto mandate + `refute_unrecorded` + the human spot-audit; MILESTONE.md exit criterion reworded to the measure — confirmed by test_audit_json_has_refute_key + test_disclosure_in_guides_and_book + test_exit_criterion_reworded
- [x] full suite green; add.py + template byte-identical ×3/×2 trees; ENGINE_MD5 re-pinned (→9d73e5ab), ENGINE_PKG_MD5 UNCHANGED; check + audit clean — confirmed by the run + parity suites (test_min_pillar / test_bundle_parity / test_rewrite_guides)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the `refute_unrecorded` list is built in `_guarantee_lint_notices`, returned in its dict, and consumed in `cmd_audit` (the grouped print, the clean-check guard, and the `--json` dump of `glints`); the `### Refute-read verdict` template block is emitted by `new-task` and read by `_section_unfilled`. Every new symbol referenced — confirmed by test_audit_surfaces_unrecorded + test_audit_json_has_refute_key + test_template_carries_verdict_block.
- [x] DEAD-CODE (code) — `body6` is read once and reused for both the shallow + refute `_section_unfilled` checks (no duplicate read); no orphaned symbol. `grep refute_unrecorded add.py` = exactly the def-site list, the 3 cmd_audit consumers, and the docstring. No new unused code.
- [x] SEMANTIC (prose / non-code) — read run.md + phases/6-verify.md + book 08-step-6-verify.md disclosure edits in FULL: each names the auto mandate, the `refute_unrecorded` measure, and the human spot-audit backstop; the 3 pinned anchors + the HARD-STOP safety line + the earned-green rubric survived verbatim (test_protected_safety_lines_pinned + test_rubric_stated_identically + test_ground_wiring all green). MILESTONE.md lines 24/32/41 reworded measure-not-block.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: tried to refute the green four ways. (1) Vacuous/overfit? No — the 13 tests assert observable audit OUTPUT (the grouped line, the `--json` key, exit 0) + template structure + gate-not-blocked, not internal calls; the absence tests (clear/grandfather/pre-verify) are genuine, not tautological. (2) Weakened a test or the frozen §3? No — tamper guard green; the build shipped EXACTLY design C (no `cmd_gate` change; test_no_new_reject_code asserts `refute_record_missing` is absent from add.py). (3) Is measure-not-block real, or did a hard gate sneak in? Real — test_gate_never_blocked_by_unrecorded drives an auto task with an UNFILLED block through `gate PASS` → done. (4) Did the lean reclaim hide a regression? No — 2157/0 incl. the 3 pinned-anchor guards I over-trimmed then restored verbatim. (This block itself is the dogfood: the task that adds the field fills it.)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose measure-only audit notice + disclosure; rejected universal hard gate at auto-PASS (MEASURED to break ~167 tests because gate→done is a universal setup primitive — declined by Tin after the scratch probe 2026-06-28) · opt-in hard gate, await_confirm-style (zero blast but conditional enforcement — a half-measure, declined)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — the 9 ordered batches ran in sequence with one detour. The lean reclaim (batch 6) cost ~360 B because the disclosure landed in TWO pools (ORCHESTRATION run.md + PHASES 6-verify.md); reclaimed from each guide's own restatement-of-run.md prose, NO rebaseline (honored "never weaken the budget"). A first refute-read over-trim hit 3 PINNED anchors — `overfit to the test fixtures` · `the engine never classifies` · the `HARD-STOP and is never auto-passed` safety line (split across a blockquote wrap) — restored verbatim, then re-reclaimed from non-pinned prose. Shipped exactly to the frozen §3: NO cmd_gate change, NO `refute_record_missing` reject, ENGINE_PKG_MD5 unchanged (add_engine untouched); refute block dogfooded onto this very task's §6.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
