# PLAN: Prune virtualenv/tooling dirs from the scope walk + self-explaining default warn

slug: scope-walk-prune · created: 2026-07-23 · stage: mvp
milestone: wm1-lean-to-twelve
autonomy: auto · gate_mode: ai-plan-verify · sensitivity: mechanical
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: scope-walk-prune — virtualenv/tooling dirs never read as out-of-scope writes; the untouched-Scope-default warning explains how it clears
Framings weighed: extend _SCOPE_EXCLUDE_DIRS (chosen — one authoritative tuple, snapshot AND gate both walk through it) · gate-side allowlist filter (rejected: two truths, snapshot still bloats)
Must:
<must>
  - _SCOPE_EXCLUDE_DIRS additionally prunes `.venv` `venv` `.tox` `.mypy_cache` `.ruff_cache` `.eggs` at any depth
  - _scope_walk over a tree containing .venv/bin + .venv/lib/site-packages yields NO key under .venv/
  - a build that creates .venv/ passes the scope gate clean when every REAL write is in cover (2026-07-23 re-measure: 3/3 reps tripped scope_violation on .venv alone)
  - the untouched-Scope-default warning states it is a note that clears ONLY by editing the Scope line — re-cross does not clear it (rep1 re-crossed 3x trying)
  - ambiguous artifact dirs `dist` `build` are NOT pruned — they can be a project's real write-set; hiding writes there would blind the gate
</must>
Reject:
<reject>
  - a REAL source write outside cover in a NON-pruned dir still fails the gate -> "scope_violation"
</reject>
After:
<after>
  - the WM1 flow's only remaining deterministic call sink (venv scope_violation -> grep -> re-cross -> re-gate) is gone
</after>
Boundary: none — no external input
<assumptions>
  ⚠ some project legitimately WRITES into a dir named `venv`/`.tox` as its artifact — if wrong: the gate is blind there; cost bounded: these names are conventionally tool-owned, and dist/build stay watched
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Surface: _SCOPE_EXCLUDE_DIRS (add.py ~5115) + the untouched-default warning text in _build_entry (~1991)

_SCOPE_EXCLUDE_DIRS: append ".venv", "venv", ".tox", ".mypy_cache", ".ruff_cache", ".eggs"
  (exact-name prune at any depth via _scope_walk's dirnames filter — ONE tuple feeds both
   the tests->build snapshot and the gate diff, so they can never disagree)
NOT pruned: dist · build — ambiguous, can be a real write-set; documented in the tuple's comment

warning text (_build_entry, both hint-era detections unchanged): REPLACE the tail
  ", then re-snapshot: add.py re-cross --by <name>" — which itself instructed the rep1 thrash loop —
  with " (a note, not a blocker — it clears only when the Scope line itself is edited; re-cross does not clear it)"

Invariant: 4 add.py twins byte-identical · ENGINE_MD5 repinned · ENGINE_PKG_MD5 unchanged · zero template edits
```

Target (measurable): new test_scope_walk_prune green (walk excludes .venv tree · live board: a build creating .venv/ + in-cover writes gates PASS · a real out-of-cover write still fails scope_violation · warn text self-explains) + full tooling suite green. Boots: N/A.
Status: FROZEN @ v1 — approved by add-worker
Freeze mode: ai-plan-verify — verified by add-worker at 2026-07-23T14:36:11+00:00
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling` `add-method/src/add_method/_bundled/tooling` `add-method/.add/tooling` `.add/tooling`   <the 4 tooling twins — add.py + the new conformance test>
Regression floor: the tooling suite — test_scope_first_freeze · test_scope_echo_draft · test_scope_gate_enforce · test_edge_truth · bundle/packaging/ship stay green
Persona (optional): `.add/personas/methodology-engine-dev.md` (advisory)

Least-sure flag surfaced at freeze: [spec] whether the pruned-name set is the right cut — `venv` (no dot) is the riskiest inclusion since a project could own a dir by that name; mitigated by keeping dist/build watched and by the still-fails test pinning that real out-of-cover writes are caught

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — _SCOPE_EXCLUDE_DIRS @5115 · _build_entry warn @~1991, both present
- [x] §1 every Must + every Reject present, each Reject paired with an error code — 5 Musts; Reject scope_violation
- [x] §3 Contract shape is concrete (no template placeholder text remains) — exact tuple additions + exact warn suffix
- [x] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar) — [spec] venv-name collision risk
Verified by: claude-opus-4-8 (add-worker, direction beat) · at: 2026-07-23T21:20:00Z

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_walk_prunes_venv_tree: build a tree with .venv/bin/x, venv/y, .tox/z, .mypy_cache/m, .ruff_cache/r, .eggs/e + src/app.py; _scope_walk yields ONLY src/app.py · covers: M1, M2
  - test_gate_clean_with_venv (live board): freeze with cover, build writes src/ + creates .venv/site-packages junk; gate PASS clean · covers: M3
  - test_real_violation_still_caught (live board): build also writes an out-of-cover rogue.py; gate refuses scope_violation naming rogue.py not .venv · covers: M5, R:scope_violation
  - test_dist_build_not_pruned: _scope_walk still sees dist/artifact.txt and build/out.txt · covers: M5
  - test_warn_self_explains: freeze --cross with untouched default prints "not a blocker" + "re-cross does not clear it" · covers: M4
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `add-method/tooling/test_scope_walk_prune.py` · MUST run red (missing implementation) before Build.

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
- [AI] specify — chose extend _SCOPE_EXCLUDE_DIRS; rejected gate-side allowlist filter (rejected: two truths, snapshot still bloats)
- [human] freeze — froze §3 @ v1 (approved by add-worker)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
