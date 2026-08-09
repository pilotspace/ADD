# PLAN: Distil the fable-thinking protocol into an on-demand skill reference doc

slug: fable-thinking-reference · created: 2026-07-22 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: distil the ONE fable-thinking umbrella principle — **Fluent ≠ true** (a bundle's polish tracks its token count, not its evidence) — MINIMALLY into `direction.md` itself, framing the Floor + Shape-self-verify checks the earlier pass already added. No separate reference doc, no new test file.
Framings weighed: minimal-inline-in-direction (chosen — the disciplines already live in direction.md/advisor from task fable-floor-reasoning; only the framing principle was missing, and it belongs where the checks are, not in a parallel doc the reader must chase) · separate-reasoning.md-doc (REJECTED by the human — a parallel doc + pointer + test is apparatus the lean guide doesn't need) · nothing (rejected — the umbrella principle genuinely ties the checks together)
Must:
<must>
  - M1 — `direction.md` (×3, byte-identical) carries the **Fluent ≠ true** principle inline at the freeze-review, in one minimal clause — not a re-listing of the disciplines already present.
  - M2 — no new reference doc (`reasoning.md` does not exist) and no new fable-reasoning test file; the check folds into the existing `test_fable_floor.py`.
  - M3 — byte-parity holds (test_tree_parity green); no engine/SKILL.md change.
</must>
Reject:
<reject>
  - an edit to `add.py`/`add_engine`/the pin or `SKILL.md` -> "engine_or_skill_touched"
  - a divergent copy across the three trees -> "tree_parity_broken"
  - a resurrected `reasoning.md` or a new `test_fable_reasoning_ref.py` -> "apparatus_readded"
</reject>
After:
<after>
  - the Fluent≠true principle is embedded minimally in direction.md; no parallel doc/test exists; test_fable_floor + test_tree_parity green.
</after>
Boundary: none — one clause of method markdown; checked by reading the file.
<assumptions>
  ⚠ the minimal clause must not duplicate what task-1 already put in direction.md — if wrong: bloat, the exact thing the human vetoed. Mitigated: it adds only the umbrella principle, not the discipline bullets (those already exist).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (content guarantees for an additive docs/method reference; no HTTP surface)

```
DOC-CONTRACT (minimal inline distillation · acceptance-checked):
  direction.md (×3)  -> the freeze-review intro carries the "Fluent ≠ true" principle in one clause
  Invariant: direction.md stays 3× byte-identical · reasoning.md absent · no test_fable_reasoning_ref.py · SKILL.md & engine untouched
  Reject: engine_or_skill_touched · tree_parity_broken · apparatus_readded
```

Least-sure flag surfaced at freeze: [spec] the clause must not re-list the disciplines already inline (bloat = the vetoed outcome) — mitigated: it adds only the umbrella principle; residual low, read the rendered line at verify.

Target (measurable): test_fable_floor green incl. a new assertion that direction.md carries "Fluent"; test_tree_parity green; reasoning.md absent + test_fable_reasoning_ref.py absent; md5(add.py)==ENGINE_MD5 and SKILL.md md5 unchanged. Confirmed at verify.
Status: FROZEN @ v2 — approved by Tin Dang
Reported: yes

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/skill/add/phases/direction.md` `.claude/skills/add/phases/direction.md` `add-method/src/add_method/_bundled/skill/add/phases/direction.md` `add-method/tooling/test_fable_floor.py`
Regression floor: `add-method/tooling/test_tree_parity.py` · full `add-method/tooling` suite (parity ripple guard)
Persona (required): methodology-engine-dev (advisory).

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_fluent_not_true_principle (added to test_fable_floor.py): all 3 direction.md carry the "Fluent" principle at the freeze-review · covers: M1
  - (M2 apparatus-absent is verified by the reverts + no new file; M3 byte-parity/engine = REGRESSION FLOOR owned by test_tree_parity.py)
</test_plan>

Tests live in: `add-method/tooling/test_fable_floor.py` · acceptance-check kind (docs): one new grep assertion folded into the existing guard (NOT a new fable-reasoning file). MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: reverted the vetoed separate-doc approach (removed reasoning.md ×3 + test_fable_reasoning_ref.py, restored direction.md/advisor pointers), then added ONE Fluent≠true clause to the direction.md freeze-review intro, cp to twins; folded the check into the existing test_fable_floor.py (no new file).
Code lives in: `./src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: the clause is present + coherent (not a re-listing of the disciplines already inline); reasoning.md + test_fable_reasoning_ref.py confirmed ABSENT (apparatus_readded reject holds); parity 1 md5, SKILL/engine untouched.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-22

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose minimal-inline-in-direction; rejected separate-reasoning.md-doc (REJECTED by the human — a parallel doc + pointer + test is apparatus the lean guide doesn't need) · nothing (rejected — the umbrella principle genuinely ties the checks together)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: reverted the vetoed separate-doc approach (removed reasoning.md ×3 + test_fable_reasoning_ref.py, restored direction.md/advisor pointers), then added ONE Fluent≠true clause to the direction.md freeze-review intro, cp to twins; folded the check into the existing test_fable_floor.py (no new file).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
