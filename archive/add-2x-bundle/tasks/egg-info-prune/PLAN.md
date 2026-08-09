# PLAN: Prune *.egg-info artifact dirs from the scope walk

slug: egg-info-prune · created: 2026-07-23 · stage: mvp
milestone: wm1-lean-to-twelve
autonomy: auto · gate_mode: ai-plan-verify · sensitivity: mechanical
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: egg-info-prune — `<name>.egg-info/` build-metadata dirs never read as out-of-scope writes
Framings weighed: suffix filter in _scope_walk's dirnames prune (chosen — one seam, both snapshot and gate agree) · add literal names to _SCOPE_EXCLUDE_DIRS (rejected: the name is project-derived, e.g. app.egg-info — no literal covers it)
Must:
<must>
  - _scope_walk prunes any directory whose name ends ".egg-info" at any depth (pip editable-install metadata; 2026-07-23 run-3: 3/3 reps tripped scope_violation on app.egg-info/*)
  - a dir merely CONTAINING that substring (e.g. egg-info-tools/) is NOT pruned — suffix match only
</must>
Reject:
<reject>
  - a real out-of-cover write in a non-pruned dir still fails the gate -> "scope_violation"
</reject>
After:
<after>
  - the run-3 trap (pip install -e . -> app.egg-info -> violation -> re-cross -> re-gate) is gone
</after>
Boundary: none — no external input
<assumptions>
  ⚠ a project legitimately owns a dir named `*.egg-info` as source — if wrong: gate blind there; conventionally setuptools-owned, cost bounded
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Surface: _scope_walk (add.py ~5208) — the dirnames prune line only

dirnames[:] = [d for d in dirnames if d not in _SCOPE_EXCLUDE_DIRS and not d.endswith(".egg-info")]

Invariant: _SCOPE_EXCLUDE_DIRS tuple unchanged · 4 add.py twins byte-identical · ENGINE_MD5 repinned · ENGINE_PKG_MD5 unchanged
```

Target (measurable): test_scope_walk_prune's new egg-info cases green (app.egg-info pruned · egg-info-tools kept) + full tooling suite green. Boots: N/A.
Status: FROZEN @ v1 — approved by add-worker
Freeze mode: ai-plan-verify — verified by add-worker at 2026-07-23T16:02:52+00:00
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling` `add-method/src/add_method/_bundled/tooling` `add-method/.add/tooling` `.add/tooling`   <the 4 tooling twins>
Regression floor: test_scope_walk_prune · test_scope_first_freeze · test_scope_gate_enforce · test_edge_truth stay green
Persona (optional): `.add/personas/methodology-engine-dev.md` (advisory)

Least-sure flag surfaced at freeze: [spec] whether suffix-pruning a project-derived name class over-hides — mitigated by the kept-dir negative test and dist/build staying watched

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — _scope_walk dirnames prune @~5208 present
- [x] §1 every Must + every Reject present, each Reject paired with an error code — 2 Musts; Reject scope_violation
- [x] §3 Contract shape is concrete (no template placeholder text remains) — the exact one-line filter
- [x] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar) — [spec] over-hide risk
Verified by: claude-opus-4-8 (add-worker, direction beat) · at: 2026-07-23T22:30:00Z

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_egg_info_dir_pruned: tree with app.egg-info/PKG-INFO + src/app.py; walk yields only src/app.py · covers: M1
  - test_egg_info_substring_kept: tree with egg-info-tools/x.py; walk still sees it · covers: M2
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `add-method/tooling/test_egg_info_prune.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: <fill at VERIFY — what you ACTUALLY did (or "as planned"); harvested into §7 Decisions (ADR)>
Code lives in: `src/`
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
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose suffix filter in _scope_walk's dirnames prune; rejected add literal names to _SCOPE_EXCLUDE_DIRS (rejected: the name is project-derived, e.g. app.egg-info — no literal covers it)
- [human] freeze — froze §3 @ v1 (approved by add-worker)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
