# PLAN: Harden _update_lock stale-reclaim: peak<=1 holds under publish-job load

slug: lock-reclaim-hardening · created: 2026-07-24 · stage: mvp
milestone: lock-reclaim-hardening
autonomy: auto   <!-- manual<conservative<auto — lower for high-risk (`add.py autonomy set`); a `component: <name>` line joins that root to §3 Scope; task edges: `--depends-on`/`--extends`/`--relates-to`; high-risk/method-defining? declare `risk: high` on the slug line; headless agent-crossed freeze? declare `gate_mode: ai-plan-verify` here (human floor: security|data|architecture never AI-frozen) -->
phase: direction   <!-- direction→build→verify→done; direction drafts §1–§4 (rules · change plan · red suite) to the ONE freeze -->
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: make `_installer._update_lock`'s stale-reclaim path pass `peak<=1` (mutual exclusion) DETERMINISTICALLY under the publish-job's concurrent load, so `test_concurrent_stale_reclaim_exactly_one_wins` / `_survives_scheduling_delay` stop flaking and the release publish gate is reliable.
Framings weighed: (a) fix a residual TOCTOU/double-hold in the reclaim path (chosen IF a real overlap is reproducible locally under load — the peak-tracking in the test is correctly synchronized, so peak=2 is a genuine momentary double-hold when it occurs) · (b) prove the failure is a CI-filesystem O_EXCL-atomicity artifact (overlayfs/tmpfs not honoring O_EXCL atomically) and make the test assert only what the FS guarantees — WITHOUT weakening the `peak<=1` contract (e.g. detect non-atomic-O_EXCL filesystems and xfail there, keeping the guarantee on real filesystems) · (c) do nothing / keep RISK-ACCEPTED (rejected — it now BLOCKS the publish gate, not just a PR).
Context (CI evidence, 2026-07-24): failed 2/2 on `publish.yml`'s "Test suite + tag/version match" gate under load (runs alongside the fresh-checkout materialize suite); PASSED both py3.10+3.12 on #178's normal `ci.yml`. `_update_lock` (add-method/src/add_method/_installer.py:1466) is already heavily hardened: per-generation inode reclaim tickets (`.reclaim-<st_ino>`), re-stat-before-unlink identity checks, deadline handling. So the remaining failure is subtle — a deep residual race OR an FS-atomicity artifact.
Must:
<must>
  - M1 the two concurrency tests pass deterministically across ≥20 consecutive runs under artificial load locally, AND on the publish.yml gate
  - M2 the `peak<=1` mutual-exclusion contract is NEVER weakened — O_EXCL stays the sole arbiter; any test change must preserve the temporal double-hold detection
  - M3 if the cause is FS-level (non-atomic O_EXCL), the resolution DETECTS that filesystem and scopes the assertion honestly (xfail/skip with a named reason), never a blanket skip
  - M4 no regression to the lock's existing guarantees (fail-fast BlockingIOError, --lock-timeout polling, no leaked lock/ticket, cross-twin npm/pip serialization)
</must>
Reject:
<reject>
  - weakening `peak<=1` to `count==1` or removing the temporal check to make it pass -> "weakened_mutual_exclusion"
  - a blanket unconditional skip of the concurrency tests -> "silent_skip"
</reject>
After:
<after>
  - the v2.4.0 publish (already tagged on main @ 7490603f, unpublished) can be re-run and reaches npm+PyPI green
  - the release publish gate no longer flakes on this test class
Boundary: two environments the fix must hold in — a normal single-suite CI runner (already green) AND the publish job's concurrent multi-suite load (currently 2/2 red).
<assumptions>
  ⚠ peak=2 is a genuine code-level double-hold, not an FS O_EXCL-atomicity artifact — if it's actually the FS, no code change to _update_lock will fix it and the honest resolution is framing (b): detect + scope the assertion, since the lock genuinely cannot guarantee mutual exclusion on a filesystem that doesn't honor O_EXCL atomically. Determine WHICH first (reproduce locally under load + check the CI runner's FS) before touching the lock code.
</assumptions>

<!-- §2 (the old standalone SCENARIOS section) was RETIRED — pass/fail cases now live with the tests in §4 · TESTS & SCENARIOS. The §3–§7 numbers are unchanged so the freeze parser and every §-reference keep working; the jump from §1 to §3 is intentional. -->

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
<METHOD> <path>   body: { <fields> }
  200 -> { <success fields> }
  4xx -> { error: "<code>" | "<code>" }
Schema: <tables/fields touched, and access pattern>
```

Target (measurable): <the success bar §6 evidence must hit — numbers, not adjectives — judged at the gate via --target-hit; name any outcome tests can't show (boots · renders) + how it's confirmed>
Status: DRAFT
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `src/`   <HARD — fill before the freeze; the file write-set, single source of truth; every file the build may write. Token grammar (backtick each): name/ = project root · ./… = THIS task's dir (rarely what a build writes) · a directory covers its whole subtree>
Regression floor: <optional — the existing suite(s) that must stay green; the host repo's own tests are a floor when present; run them before the gate — or omit / "none — greenfield">
Persona (optional): <persona file under `.add/personas/` this build embodies — advisory, never lowers a gate; omit or "generic" if none fits>

Least-sure flag surfaced at freeze: [spec|scenario|contract|test] <the ONE part you trust least + why — REQUIRED at the freeze (unflagged_freeze refuses without it); pick ONE part tag from the menu; §1's top ⚠ usually feeds it>

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

<!-- The freeze IS the one approval, led by the bundle's lowest-confidence flag — Contract + Scope (may touch) = HARD (tamper-guarded); Strategy · Regression floor · Persona = SOFT/optional. Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen Contract = change request back to SPECIFY. Scope tokens, backticked: `./…` = this task dir · a "/" token = project root · a bare name = sibling of the previous token's dir · a directory covers its whole subtree · outside-root drops fail-closed · absent line = UNDECLARED (grandfathered, never retro-red). -->

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_<name>: arrange / act / assert behavior not internals · covers: <M#, R:code>
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0. The test_plan bullets' `covers:` tails are machine-read too: `add.py locate path::test_name` resolves a failing test to the frozen §3 clause it proves -->
<!-- NON-CODING task (kind: docs · release · infra, or a non-coding project)? §4 is a failing-first ACCEPTANCE CHECK, not a script — verifiable pass/fail evidence (mkdocs build succeeds · §X covers A/B/C · every internal link resolves), red before the artifact exists and green after. Set `Tests live in: evidence` (no `./tests/`). The red→green discipline holds; only the must-be-executable-code requirement is lifted. -->

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
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Refute-read verdict is recorded, never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
