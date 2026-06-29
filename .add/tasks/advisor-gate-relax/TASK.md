# TASK: advisor-gate-relax

slug: advisor-gate-relax · created: 2026-06-29 · stage: mvp · risk: high · sensitivity: architecture
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
  - `add-method/tooling/add.py:_RISK_HIGH_RE` — line 982; compiled pattern detecting `risk: high` in a task header; unchanged — both guard sites key on it.
  - `add-method/tooling/add.py:_task_sensitivity(hdr)` — line 989; reads the declared sensitivity token from a stripped header; returns `"mechanical"` when the relaxed path is active.
  - `add-method/tooling/add.py:_autonomy_lowered(hdr)` — line 1065; True iff dial is `manual` or `conservative`; remains the primary guard predicate.
  - `add-method/tooling/add.py:_raw_phase_bodies(root, slug) -> dict[int, str]` — returns body text keyed by section index; `body6 = .get(6, "")` is the input to both new helpers.
  - `add-method/tooling/add.py:cmd_gate` — SITE 1: lines ~1143-1147; the completing-outcome guard (`PASS` / `RISK-ACCEPTED`); relaxation applied here.
  - `add-method/tooling/add.py:_audit_findings` — SITE 2: lines ~5580-5586; emits `unguarded_high_risk_auto`; relaxation applied here.
  - `add-method/tooling/add.py:cmd_autonomy (set)` — SITE 3: line ~1283; LEFT STRICT and UNCHANGED — still refuses raising a `risk: high` task to `auto` regardless of any advisor verdict.
  - `add-method/tooling/add_engine/constants.py:_SENSITIVITY_VALUES` — line 231; already contains `"mechanical"`; no change needed.
  - NEW: `_advisor_verdict_is_pass(body6: str) -> bool` — pure helper; reads the `Verdict:` line from the `### Advisor 3-lens verdict` block in §6.
  - NEW: `_advisor_no_residue(body6: str) -> bool` — pure helper; reads the `Residue:` line from that same block.
Context (working folder):
  - `add-method/tooling/test_high_risk_signal.py` — existing guard suite; `unguarded_high_risk_auto` cited at lines 101, 188, 195; fixtures lack the `sensitivity: mechanical + advisor-PASS` combo so they still fire → must pass unchanged.
  - New test file (e.g., `test_advisor_gate_relax.py`) needed: relaxed-pass case + the three still-fires reject cases + audit-side relaxation.
  - Engine ships across three trees: canonical `add-method/tooling/` → `_bundled/` + repo-root `.add/tooling/`; any engine change re-pins `ENGINE_MD5` (`engine_pin.py`) + re-bundles (`test_shared_engine_pin` / `test_bundle_parity`).
Honors (patterns / conventions):
  - Security is ALWAYS a HARD-STOP — the relaxation NEVER touches `sensitivity: security`; nor `data` nor `architecture`; only `sensitivity: mechanical` qualifies.
  - Engine is OFFLINE/PURE — `_advisor_verdict_is_pass` and `_advisor_no_residue` are pure text readers; the engine never spawns.
  - Fail-safe default: missing or unmatched verdict block → helpers return False → guard fires (no silent relaxation).
  - Measure-before-relax: `advisor-verdict-audit` ships before or concurrently in this milestone.
Anchors the contract cites: `_RISK_HIGH_RE` · `_task_sensitivity` · `_autonomy_lowered` · `_raw_phase_bodies` · `cmd_gate` (SITE 1, ~1143-1147) · `_audit_findings` (SITE 2, ~5580-5586) · `cmd_autonomy set` guard (SITE 3, ~1283, strict) · new `_advisor_verdict_is_pass` · new `_advisor_no_residue`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Relax the `unguarded_high_risk_auto` guard at the completing-outcome gate and the audit emitter so that a `sensitivity: mechanical` high-risk task with a recorded advisor PASS and no residue auto-completes without requiring a lowered dial.
Framings weighed: apply the relaxation at both consumption sites (cmd_gate + _audit_findings) via two new pure body6 helpers; leave cmd_autonomy set guard STRICT (chosen) · relax the cmd_autonomy set guard too (rejected: T1 — the §6 advisor verdict must already exist when the gate fires; relaxing at dial-set time would allow raising to auto before the verdict is recorded, creating a TOCTOU gap) · relax ALL non-security high-risk tasks on advisor PASS (rejected: too broad — `data` and `architecture` remain non-mechanical and require a human; `mechanical` is the narrowest, deterministic class)
Must:
<must>
  - At `cmd_gate` (SITE 1): the `unguarded_high_risk_auto` `_die()` does NOT fire iff ALL of: `_RISK_HIGH_RE.search(hdr)` AND `NOT _autonomy_lowered(hdr)` AND `_task_sensitivity(hdr) == "mechanical"` AND `_advisor_verdict_is_pass(body6)` AND `_advisor_no_residue(body6)` — equivalently the guard fires iff: `_RISK_HIGH_RE.search(hdr) AND NOT _autonomy_lowered(hdr) AND NOT (_task_sensitivity(hdr) == "mechanical" AND _advisor_verdict_is_pass(body6) AND _advisor_no_residue(body6))`.
  - At `_audit_findings` (SITE 2): the `unguarded_high_risk_auto` finding is NOT emitted when the same relaxed predicate holds (mechanical + PASS + no residue); both the "not lowered" branch and the "auto-gate reviewer" branch are gated by `NOT relaxed_path(hdr, body6)`.
  - `_advisor_verdict_is_pass(body6: str) -> bool`: `re.search(r"(?m)^Verdict:[ \t]*(\S+)", body6)` — True iff `m.group(1).upper().startswith("PASS")`; False if no match (fail-safe).
  - `_advisor_no_residue(body6: str) -> bool`: `re.search(r"(?m)^Residue:[ \t]*(\S+)", body6)` — True iff `m.group(1).strip().lower() == "none"`; False if no match (fail-safe).
  - Both helpers are PURE (read §6 body text only) and default to False on missing/unmatched input — the guard fires whenever the verdict is absent.
  - The `cmd_autonomy set` guard at SITE 3 (~line 1283) is LEFT STRICT and UNCHANGED — it still refuses raising any `risk: high` task to `auto`, regardless of any advisor verdict recorded in §6.
</must>
Reject:
<reject>
  - `risk: high` + `sensitivity: data` (or `architecture` or `security`) + advisor PASS + Residue: none → guard STILL fires `"unguarded_high_risk_auto"` — only `sensitivity: mechanical` relaxes.
  - `risk: high` + `sensitivity: mechanical` + advisor verdict NOT starting `"PASS"` (e.g., `HARD-STOP`, `FLAG`, absent block) → guard STILL fires.
  - `risk: high` + `sensitivity: mechanical` + `Residue:` value is anything other than `none` → guard STILL fires.
</reject>
After:
<after>
  - A task with `risk: high · sensitivity: mechanical` whose §6 `### Advisor 3-lens verdict` block records `Verdict: PASS` and `Residue: none` auto-completes at PASS without error — even with `autonomy: auto`.
  - A task with `risk: high` and `sensitivity: data`, `architecture`, or `security` still requires a lowered dial to gate; the guard fires unchanged.
  - A mechanical high-risk task whose advisor verdict is HARD-STOP, or has any residue other than `none`, still fires `unguarded_high_risk_auto`.
  - `cmd_autonomy set auto` on any `risk: high` task still dies `unguarded_high_risk_auto` (SITE 3 unchanged).
  - `test_high_risk_signal.py` tests at lines 101, 188, 195 still pass — their fixtures lack the `mechanical + advisor-PASS` combo and so the guard still fires for them.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the `### Advisor 3-lens verdict` block's `Verdict:` and `Residue:` field names are stable — lowest confidence because if `advisor-review-step` ever renames them, the helpers silently return False (guard fires = fail-safe, never unsafe); if wrong: update the two regex patterns in the helpers (isolated one-line change each).
  ⚠ SITE 3 (`cmd_autonomy set`) left STRICT is the right design cut (T1) — lowest confidence among design decisions because a relaxed set-time guard would let the user raise the dial before any §6 content exists; if wrong: apply the same `relaxed_path` predicate at SITE 3; cost: a TOCTOU window (dial raised to auto while verdict is not yet recorded).
  - [ ] `advisor-verdict-audit` (the measure-before-relax peer) ships before or concurrently in this milestone — if not, the engine cannot audit that the verdict is recorded; helpers fail-safe (missing → False → guard fires), so this is non-blocking but required for full integrity.
  - [ ] the `_raw_phase_bodies` §6 body is stable as the §6 access path — confirmed by existing usage at add.py line 5642; no change expected.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: mechanical high-risk task with advisor PASS and no residue auto-completes at gate
  Given a task with risk: high · sensitivity: mechanical and autonomy: auto at verify phase
  And its §6 contains "Verdict: PASS" and "Residue: none" in the Advisor 3-lens verdict block
  When I run add.py gate PASS <slug>
  Then the gate succeeds and state.json records Outcome: PASS for the task
  And no "unguarded_high_risk_auto" error is emitted

Scenario: done mechanical high-risk task with advisor PASS and no residue is silent in audit
  Given a done task with risk: high · sensitivity: mechanical and autonomy: auto
  And its §6 contains "Verdict: PASS" and "Residue: none" in the Advisor 3-lens verdict block
  When I run add.py audit
  Then "unguarded_high_risk_auto" does NOT appear in the audit findings for that task

Scenario: cmd_autonomy set refuses to raise a high-risk task to auto (SITE 3 strict)
  Given a task with risk: high and current autonomy: conservative
  When I run add.py autonomy set auto <slug>
  Then it dies "unguarded_high_risk_auto"
  And the task TASK.md autonomy line is unchanged

Scenario: non-mechanical high-risk task still fires the guard even with advisor PASS (reject a)
  Given a task with risk: high · sensitivity: architecture and autonomy: auto at verify phase
  And its §6 contains "Verdict: PASS" and "Residue: none"
  When I run add.py gate PASS <slug>
  Then it dies "unguarded_high_risk_auto"
  And state.json is unchanged

Scenario: mechanical high-risk task with HARD-STOP advisor verdict still fires the guard (reject b)
  Given a task with risk: high · sensitivity: mechanical and autonomy: auto at verify phase
  And its §6 contains "Verdict: HARD-STOP" in the Advisor 3-lens verdict block
  When I run add.py gate PASS <slug>
  Then it dies "unguarded_high_risk_auto"
  And state.json is unchanged

Scenario: mechanical high-risk task with non-none residue still fires the guard (reject b variant)
  Given a task with risk: high · sensitivity: mechanical and autonomy: auto at verify phase
  And its §6 contains "Verdict: PASS" and "Residue: open security gap"
  When I run add.py gate PASS <slug>
  Then it dies "unguarded_high_risk_auto"
  And state.json is unchanged

Scenario: missing advisor verdict block keeps the guard firing (fail-safe)
  Given a task with risk: high · sensitivity: mechanical and autonomy: auto at verify phase
  And its §6 has no "### Advisor 3-lens verdict" block (both helpers return False)
  When I run add.py gate PASS <slug>
  Then it dies "unguarded_high_risk_auto"
  And state.json is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine  add-method/tooling/add.py  (no new CLI subcommand; no state.json field added)

TWO NEW PURE HELPERS (read §6 body only; both default False on missing/unmatched input):

  _advisor_verdict_is_pass(body6: str) -> bool
    m = re.search(r"(?m)^Verdict:[ \t]*(\S+)", body6)
    return bool(m) and m.group(1).upper().startswith("PASS")
    # reads the `### Advisor 3-lens verdict` block introduced by advisor-review-step;
    # False when the block is absent → guard fires (fail-safe).

  _advisor_no_residue(body6: str) -> bool
    m = re.search(r"(?m)^Residue:[ \t]*(\S+)", body6)
    return bool(m) and m.group(1).strip().lower() == "none"
    # False when the field is absent or value ≠ "none" → guard fires (fail-safe).

RELAXED PREDICATE (inline helper; not a named function in the engine):
  relaxed_path(hdr, body6) :=
      _task_sensitivity(hdr) == "mechanical"
      and _advisor_verdict_is_pass(body6)
      and _advisor_no_residue(body6)

SITE 1 — cmd_gate (~line 1143)  [MODIFIED]:
  body6 = _raw_phase_bodies(root, slug).get(6, "")
  # before: fires iff _RISK_HIGH_RE.search(hdr) and not _autonomy_lowered(hdr)
  # after:
  if (_RISK_HIGH_RE.search(hdr)
          and not _autonomy_lowered(hdr)
          and not relaxed_path(hdr, body6)):
      _die("unguarded_high_risk_auto: ...")
  # HARD-STOP is never blocked — that path bypasses this guard entirely.

SITE 2 — _audit_findings (~line 5580)  [MODIFIED]:
  body6 = _raw_phase_bodies(root, slug).get(6, "")
  # before: fires both sub-branches whenever _RISK_HIGH_RE.search(hdr)
  # after: both sub-branches additionally gated by not relaxed_path(hdr, body6):
  if _RISK_HIGH_RE.search(hdr) and not relaxed_path(hdr, body6):
      if not _autonomy_lowered(hdr):
          f(slug, "unguarded_high_risk_auto",
            "risk: high declared but autonomy is not lowered (manual or conservative)")
      elif rev and "auto-gate" in rev.group(1):
          f(slug, "unguarded_high_risk_auto",
            "risk: high task whose GATE RECORD reviewer is the auto-gate")

SITE 3 — cmd_autonomy set (~line 1283)  [LEFT STRICT — UNCHANGED]:
  if _RISK_HIGH_RE.search(_task_header(root, slug)) and level not in ("manual", "conservative"):
      _die("unguarded_high_risk_auto: ...")
  # Rationale (T1): the §6 advisor block must already exist when the gate fires;
  # relaxing at dial-set time would allow raising to auto before the verdict is
  # recorded (TOCTOU gap). If wrong: apply relaxed_path at this site too.

INVARIANTS:
  - security NEVER relaxed: sensitivity: security → relaxed_path always False
    (security ∉ {"mechanical"}); security findings remain HARD-STOP always.
  - data and architecture NEVER relaxed: only sensitivity: mechanical qualifies.
  - any Residue ≠ "none" keeps guard firing (unresolved risk).
  - any Verdict not starting "PASS" (HARD-STOP, FLAG, or absent) keeps guard firing.
  - missing §6 advisor block → both helpers False → guard fires (fail-safe).

Schema: no state.json field added; no new CLI subcommand; no .gitignore change.
        Changes: add _advisor_verdict_is_pass + _advisor_no_residue helpers;
        extend existing guard predicate at SITE 1 and SITE 2 only.
        Engine change → re-pin ENGINE_MD5 across all 3 trees + re-bundle
        (test_shared_engine_pin / test_bundle_parity / test_engine_repin_parity).
        test_high_risk_signal.py passes unchanged (fixtures lack mechanical+advisor-PASS).
        New tests cover: relaxed-pass (gate + audit) + three still-fires reject cases
        + cmd_autonomy set strict + fail-safe (missing block).
```

Least-sure flag surfaced at freeze: [contract] leaving the `cmd_autonomy set` guard (SITE 3) STRICT (T1) vs. relaxing it too. Design chose STRICT: the relaxation is a gate-time decision — the §6 advisor verdict must already exist when the gate fires; relaxing the dial-set guard would allow the dial to be raised to `auto` before any §6 content is written (TOCTOU gap). If wrong: apply the same `relaxed_path(hdr, body6)` predicate at SITE 3; cost: a window where `autonomy: auto` is set on a high-risk task whose §6 advisor block does not yet exist.

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

Coverage target: every §2 scenario + 7 security invariants (29 cases)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_relaxed_pass_gate_and_audit: mechanical + advisor PASS + Residue none + auto → gate SUCCEEDS, audit clean of unguarded_high_risk_auto
  - test_security/data/architecture_never_relaxes: non-mechanical → still blocked
  - test_blocks_when_residue_non_none / _verdict_hard_stop / _flag: unresolved → still blocked
  - test_blocks_when_advisor_block_absent: fail-safe → blocked
  - test_autonomy_set_auto_still_blocked: SITE 3 strict
  - test_refute_read_verdict_does_not_satisfy: sub-section scoping (no cross-block bleed)
</test_plan>

Tests live in: `add-method/tooling/test_advisor_gate_relax.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. RED test_advisor_gate_relax.py (29 cases incl. 7 security invariants) 2. add 3 helpers (_advisor_slice + _advisor_verdict_is_pass + _advisor_no_residue) 3. extend guard at SITE 1 (cmd_gate) + SITE 2 (_audit_findings); leave SITE 3 strict 4. 3-tree sync + re-pin 5. green full suite + test_high_risk_signal unchanged

Known-problem fixes: reading full body6 → matches the refute-read's Verdict: line first (cross-block bleed) → scope to the advisor sub-section via _advisor_slice; relaxing SITE 3 → TOCTOU window → leave strict; relaxing non-mechanical → SECURITY HOLE → only mechanical qualifies, fail-safe False on absent block
Strategy actually used: as planned — security-focused build subagent (TDD, 7 invariant tests), orchestrator-run 3-tree parity + re-pin; engine-only, ENGINE_PKG_MD5 unchanged
Safety rule (feature-specific): security/data/architecture sensitivity NEVER relax; absent advisor block fails safe (guard fires); any non-PASS verdict or non-none residue keeps the guard firing
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

- [x] all tests pass — full suite 2407/0; test_high_risk_signal unchanged 12/12
- [x] coverage did not decrease — +29 new tests (7 dedicated security-invariant tests)
- [x] no test or contract was altered to pass a build — no test weakened; §3 left at v1 per the gate decision (PASS as-is): the literal helper bodies say `body6` but the build correctly scopes to `_advisor_slice` to avoid cross-block bleed; the delta is accepted and documented here in §6 (the build is more correct than the literal text; same delta as advisor-verdict-audit which chose to re-freeze v2 — here you chose to document instead).
- [x] the green was EARNED — independent SECURITY refute-read (agent a90c79b190ec9e7c9), 10/10 probes, explicit "NO non-mechanical or unresolved high-risk task can auto-complete"
- [x] concurrency / timing — pure read-only helpers; SITE 3 kept strict to close the dial-set TOCTOU window
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib re only
- [x] layering & dependencies follow CONVENTIONS.md — extends the existing guard at its two consumption sites
- [ ] a person reviewed and approved the change — AWAITING human gate (risk: high · architecture · conservative · SECURITY-sensitive)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a risk:high + mechanical + advisor-PASS + Residue-none task at auto `gate PASS` SUCCEEDS (guard stands down) — confirmed by test_relaxed_pass + audit not flagging unguarded_high_risk_auto
- [x] a risk:high + security (or data/architecture) task with a perfect advisor block STILL blocks — confirmed by test_security/data/architecture_never_relaxes
- [x] a risk:high + mechanical task with NO advisor block STILL blocks (fail-safe) — confirmed by test_blocks_when_advisor_block_absent
- [x] `autonomy set auto` on a risk:high task STILL dies (SITE 3 strict) even with a passing advisor block — confirmed by test_autonomy_set_auto_still_blocked; test_high_risk_signal unchanged (12/12)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_advisor_slice` feeds `_advisor_verdict_is_pass` + `_advisor_no_residue`; both consumed by `_relaxed` at SITE 1 (cmd_gate) and the inline predicate at SITE 2 (_audit_findings); SITE 3 untouched
- [x] DEAD-CODE (code) — no orphaned symbol; 3 helpers consumed by both sites + 29 tests
- [x] SEMANTIC (code) — frozen §3 re-read; build matches intent; the one literal-regex delta (`_advisor_slice` vs `body6`) disclosed above for the v2 amendment

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent a90c79b190ec9e7c9 (independent, security-focused) · adversarially checked: security/data/architecture never relax (perfect advisor block still blocks), absent-block fail-safe, cross-block bleed (refute-read & GATE RECORD Verdict: lines never satisfy the advisor check), Residue exact-none only, Verdict PASS-prefix, SITE 3 strict, happy-path relaxes, non-vacuous behavioral tests — explicit "NO non-mechanical or unresolved high-risk task can auto-complete"

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Dogfooded: grandfathered template lacked the block, recorded here by hand. This is the security-critical task.
Advisor: agent a90c79b190ec9e7c9
1. Security: CLEAR — the relaxation is provably scoped to sensitivity:mechanical; security/data/architecture always escalate; absent block fails safe; SITE 3 (dial-set) kept strict to close the TOCTOU window
2. Concurrency: CLEAR — pure read-only helpers, no shared state
3. Architecture: RESIDUE (both advisory, accepted at gate) — (a) §3 literal `body6` vs build `_advisor_slice` delta → accepted as-is, documented in §6 (§3 stays v1 per gate decision; build is more correct); (b) a deliberately dual-`### Advisor 3-lens verdict` TASK.md lets the first block win — within the existing "TASK.md is trusted" model (the author could equally drop risk:high), not a new vulnerability
Verdict: PASS
Residue: two advisory notes accepted at the gate (body6→_advisor_slice delta documented not re-frozen; dual-block within existing trust model) — carry the dual-block note to deltas
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
- [AI] specify — chose apply the relaxation at both consumption sites (cmd_gate + _audit_findings) via two new pure body6 helpers; leave cmd_autonomy set guard STRICT; rejected relax the cmd_autonomy set guard too (rejected: T1 — the §6 advisor verdict must already exist when the gate fires; relaxing at dial-set time would allow raising to auto before the verdict is recorded, creating a TOCTOU gap) · relax ALL non-security high-risk tasks on advisor PASS (rejected: too broad — `data` and `architecture` remain non-mechanical and require a human; `mechanical` is the narrowest, deterministic class)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — security-focused build subagent (TDD, 7 invariant tests), orchestrator-run 3-tree parity + re-pin; engine-only, ENGINE_PKG_MD5 unchanged
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
