# PLAN: Lock race probes: CI-starvation realism without losing teeth

slug: lock-probe-ci-realism · created: 2026-07-22 · stage: mvp
kind: infra
milestone: thin-engine-loop
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: lock-probe-ci-realism — the four lock-reclaim race probes (2 per file:
test_project_scope_lock.py · test_global_update_harden.py) stop red-flagging the engine's
DOCUMENTED probabilistic heartbeat boundary on starved CI runners, without losing one
assert of real teeth. `_lock_heartbeat`'s own docstring: "a probabilistic mitigation, not
a mathematical guarantee: if the heartbeat thread itself is starved past stale_after, the
window reopens — accepted". The probes override stale to 8s; a loaded 2-core runner that
starves a daemon thread 8s crosses that boundary → 4 consecutive red CI runs on behavior
the engine never promised (3× on the 2.1.0 release commit alone).
Framings weighed: margins for probe A + a measured starvation discriminator for probe B
(chosen — A's holder is inside 0.05s so wide margins cost nothing; B REQUIRES hold>stale
by design, so only observation can split starved-runner from broken-heartbeat) ·
blind retry-loop on failure (rejected: a real mutex bug firing intermittently would pass
almost surely — that IS test-weakening) · CI-env skip of both probes (rejected: loses all
CI coverage of the ticket arbitration, which is deterministic and healthy).
Must:
<must>
  - M1 engine byte-untouched — _installer.py, add.py, cli.js, add_engine all unchanged; the diff names ONLY the two test files + this task dir
  - M2 probe A (test_concurrent_stale_reclaim_exactly_one_wins, both files): stale override 8→90 and backdated lock age 10→100; every existing assert byte-preserved — a false stale-judgment of the winner's fresh lock now needs a 90s starvation inside a ≤5s join window (starvation-proof by margins, NO skip path)
  - M3 (v2) probe B (…survives_scheduling_delay, both files): gains a beat-observer thread sampling the lockfile ~4 Hz, recording per-inode {span, last observed age (time.time()−st_mtime), beats (same-inode mtime advances)}, global beats_observed, and its own worst sampling gap; on peak > 1 with a healthy observer (gap ≤ heartbeat interval) it discriminates THREE ways: (1) zero beats → FAIL (heartbeat dead); (2) the VICTIM inode (longest observed span — the delayed holder's lock) was observed replaced while its last observed age < stale_after − slack (slack = 2×poll + 0.1s) → FAIL (identity-blind steal / broken exclusivity: the lock provably never looked stale, so the overlap cannot be the documented boundary); (3) otherwise → unittest.SkipTest naming the measured evidence and citing the _lock_heartbeat docstring boundary; an UNHEALTHY observer always degrades to SKIP (never fails a healthy engine on blind evidence)
  - M4 the healthy-runner path (peak ≤ 1) keeps every assert byte-equivalent in all four probes (mutual exclusion · ≥1 acquired · all outcomes reported · no leak)
  - M5 FLOOR_DEF_COUNTS holds (test_project_scope_lock.py ≥ 31 `def test_`); no test removed anywhere
</must>
Reject:
<reject>
  - probe B skipping when the heartbeat was demonstrably dead on a healthy observer -> "heartbeat_dead_masked" (the regression the probe exists to catch must still FAIL)
  - probe B skipping when the victim lock was observed stolen while provably fresh (healthy heartbeat, age < stale − slack) -> "blind_steal_masked" (the refute-read's confirmed third cause — an identity-blind reclaim regression must still FAIL)
  - any assert weakened, loosened, or removed on the healthy-runner path -> "test_weakened"
</reject>
After:
<after>
  - a starved CI runner yields a SKIP with a measured gap in its reason (visible, counted, never a red) — a broken heartbeat still reds
  - 30 consecutive local runs of the 4 probes pass with zero skips (healthy-machine behavior unchanged)
</after>
Boundary: none — no external input; timing constants are test-internal
<assumptions>
  ⚠ the discriminator's "observer healthy" bar (own max sampling gap ≤ heartbeat interval) may itself misjudge under EXTREME starvation where the observer thread also stalls — if wrong: the starved case degrades to skip (safe direction: we never fail a healthy engine; a truly dead heartbeat on a starved observer escapes one run, and the healthy-runner reds would catch it next run)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
Scenario: healthy machine, delayed holder protected (the everyday PASS)
  Given a holder inside the lock for 10s with stale_after 8s
  And the heartbeat thread refreshing the lockfile every 2s unstarved
  When 5 sibling racers retry-acquire throughout the hold
  Then no sibling ever reclaims the live holder's lock (peak stays 1)
  And every assert runs byte-identical to today — zero skips

Scenario: starved CI runner, heartbeat alive but outpaced (today's false red → a measured SKIP)
  Given the same probe on a loaded 2-core runner
  And the observer saw the heartbeat fire, but a scheduling gap exceeded the 8s stale window
  When a sibling (correctly, per the lock's own rules) reclaims and peak reaches 2
  Then the probe SKIPS, naming the measured gap and the _lock_heartbeat docstring boundary
  And CI shows a counted skip, never a red

Scenario: heartbeat regression (the teeth — must still bite)
  Given a build where the heartbeat is broken (never fires: bad interval, dead thread, wrong path)
  And the beat-observer is demonstrably healthy (its own sampling gaps ≤ the 2s interval)
  When a sibling reclaims the "aging" live lock and peak reaches 2
  Then the probe FAILS exactly as today — the skip path is unreachable for a dead heartbeat

Scenario: identity-blind steal of a fresh, beating lock (v2 — the refute-read's third cause)
  Given the delayed holder's lock beating every 2s, never once looking older than ~2s
  And a regression (or saboteur) that unlinks/steals the live lock without re-checking identity
  When a sibling enters and peak reaches 2 while the victim's last observed age < stale − slack
  Then the probe FAILS naming the blind steal — a fresh lock's theft can never be the
    documented starvation boundary, so the skip path must be unreachable here

Scenario: stale-lock stampede stays deterministic (probe A, margins only)
  Given a genuinely stale lock (backdated 100s, stale_after 90s) and 6 simultaneous racers
  When all six race the identity-keyed reclaim ticket
  Then exactly one enters at any instant and every loser backs off untouched — asserts unchanged
  And a false re-reclaim of the winner's fresh 50ms hold would now need a 90s starvation
    inside a 5s join window — impossible, so this probe needs no skip path at all
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
TESTS-ONLY change — 4 probes across 2 files; engine byte-untouched
Probe A ×2 (exactly_one_wins):  ADD_{PROJECT_}LOCK_STALE_SECONDS "8" -> "90" ·
  _write_[project_]lock(age_seconds=10 -> 100) · asserts byte-preserved · no skip path
Probe B ×2 (survives_scheduling_delay):  keep stale "8" / hold 10s; NEW beat-observer
  (daemon thread, ~4 Hz stat of the lock path while first_holder is inside):
    beats_observed  = count of distinct mtime advances seen
    observer_gap    = max gap between its own consecutive samples
    hb_interval     = max(0.05, min(stale/4, 5.0)) == 2.0s   (mirrors _lock_heartbeat)
  observer records (v2): per-inode {first/last seen, last observed age = time.time() −
    st_mtime, beats}; victim = the inode with the LONGEST observed span (the delayed
    holder's); slack = 2 × poll + 0.1 = 0.6s
  outcome logic, ONLY reached when peak > 1:
    observer unhealthy (own gap > hb_interval) -> SKIP (blind evidence never fails a healthy engine)
    beats_observed == 0                        -> FAIL (heartbeat dead — regression)
    victim observed replaced while its last observed age < stale_after − slack
                                               -> FAIL (identity-blind steal — a provably
                                                  fresh lock's theft is never the boundary)
    else                                       -> SKIP naming the measured evidence
  peak <= 1 -> every existing assert unchanged, byte-equivalent
Anchors: _lock_heartbeat (interval formula + docstring boundary) · _project_lock ticket
  reclaim · _update_lock twin · FLOOR_DEF_COUNTS (test_corpus_slim) · the fresh-checkout
  meta-test (skips are tolerated, failures are not)
Never: touch _installer.py / any engine file · weaken a healthy-path assert · add a retry loop
```

Target (measurable): 30 consecutive local runs of the 4 probes, 0 failures 0 skips; a heartbeat-suppressed experiment (monkeypatched no-op beat, NOT committed) makes probe B FAIL not skip; full tooling suite ≥1962 passed / 0 failed; `add.py check` 0-failed; PR CI Tooling tests green on both Pythons (or skip-with-measured-gap, never red, if the runner starves again).
Status: FROZEN @ v2 — approved by Tin Dang (v1 → v2 change request: the refute-read
confirmed a third peak>1 cause — identity-blind reclaim — reachable through v1's SKIP;
v2 adds the victim-age FAIL rule so a provably-fresh lock's theft always reds)
Least-sure flag surfaced at freeze: [contract] the victim-selection heuristic (longest
observed span = the delayed holder's inode) is the judgment most likely wrong under
extreme scheduling where the observer under-samples the victim — if wrong, the case
degrades to SKIP, never to failing a healthy engine (safe direction), and the healthy-
runner hard asserts still stand.
Reported: yes — v1 design + 4 scenarios rendered at v1; the refute-read's confirmed hole +
the v2 rule rendered to the human before this v2 freeze

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `tmp/` `./`
Regression floor: full tooling suite (`add-method/tooling/./t` — 1962 passing at draft) + `add.py check` 0-failed
Persona (required): `.add/personas/tdd-verifier.md` (a test-realism change must be held to the never-weaken bar by the persona that owns it)

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - A1_engine_untouched: `git diff --name-only` ⊆ {test_project_scope_lock.py, test_global_update_harden.py, .add/tasks/lock-probe-ci-realism/*, .add/state.json} — RED-equivalent today (the change does not exist) · covers: M1
  - A2_probe_A_margins: both exactly_one_wins probes read stale "90" + age 100 with asserts byte-preserved (diff shows only the two constants + comment) · covers: M2
  - A3_discriminator_fails_dead_heartbeat: in-session experiment — monkeypatch `_lock_heartbeat` to a no-op and run probe B: it must FAIL (assert on peak), never skip — RED today (no discriminator exists; today it fails for the WRONG reason too, indistinguishable from starvation) · covers: M3, R:heartbeat_dead_masked
  - A4_discriminator_skips_starved: in-session experiment — monkeypatch the beat to fire once then stall past stale_after: probe B must SKIP with the measured gap in the reason · covers: M3
  - A5_healthy_path_unchanged: 30 consecutive local runs of the 4 probes — 0 failures, 0 skips (non-vacuous check: each run must literally print "4 passed") · covers: M4
  - A6_floors_and_suite: FLOOR_DEF_COUNTS green (≥31) · `./t --full` (the fast lane EXCLUDES both lock files) ≥2236 passed / 0 failed · `add.py check` 0-failed · covers: M5, R:test_weakened (the suite's own weakening-lints)
  - A7_saboteur_blind_steal_fails: in-session experiment — heartbeat UNPATCHED (beating normally), a saboteur thread unlinks the live victim lock mid-hold so a polling racer enters (peak 2, victim provably fresh): probe B must FAIL naming the blind steal, never skip — RED under v1 (the confirmed masking hole) · covers: M3-v2, R:blind_steal_masked
</test_plan>

Tests live in: evidence · acceptance checks (kind: infra — the artifact IS a test change; red→green rides A3/A4's missing-discriminator reds).

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: v1 built probe-A margins (stale 8→90s, age→100s, skip path removed) + a
3-way probe-B discriminator (observer-unhealthy→SKIP · beats==0→FAIL heartbeat_dead_masked · else→SKIP),
engine byte-untouched (M1, md5 ENGINE pin held). The freeze refute-read (add-advisor) found a
blind-steal masking hole — an identity-blind reclaim of a HEALTHY, beating lock reached v1's SKIP,
masking probe B's strongest catch — so a v2 change request added the `_HeartbeatObserver` victim-age
FAIL rule (victim replaced while age < stale−slack → fail blind_steal_masked). Both probe files
(test_project_scope_lock.py, test_global_update_harden.py) carry the observer identically.
Code lives in: `./src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full corpus 2236 passed / 0 failed; probe-B stress 30/30 × "4 passed", zero skips; `add.py check` 418/0
- [x] coverage did not decrease — test-only change (probe realism); no `src/` touched
- [x] no test or contract was altered during build — the frozen §3 authorized editing ONLY the two probe files (§5 Scope); engine byte-untouched (M1, md5 ENGINE pin held); no OTHER test weakened
- [x] the green was EARNED, not gamed — refute found the v1 blind-steal hole → v2 victim-age rule; A7 saboteur makes a beating-lock steal FAIL (RED under v1); A5 30× non-vacuous; no overfit/vacuous/stub
- [x] concurrency / timing of the risky operation is safe — the probes MEASURE the heartbeat race; the discriminator separates runner-starvation (SKIP) from a real regression (FAIL)
- [x] no exposed secrets, injection openings, or unexpected dependencies — test-only; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — no structural change
- [x] a person reviewed and approved the change — Tin Dang (authorized the gate + branch/PR split)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (two-pass)
By: add-advisor (freeze refute) + self (A7 mechanical proof) · adversarially checked: the v1 refute returned
NOT-EARNED — an identity-blind reclaim of a healthy beating lock reached v1's SKIP, masking blind_steal. v2
added the `_HeartbeatObserver` victim-age FAIL rule; A7's saboteur (real `_lock_heartbeat` + unlink at t=4s)
now FAILs blind_steal_masked in BOTH probe files (was RED under v1). A3 dead→FAIL, A4 starved→SKIP confirm the
three-way split; A1 diff-confined + A5 30× non-vacuous confirm no test was weakened.

### GATE RECORD
Reported: yes — evidence rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-22

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose margins for probe A + a measured starvation discriminator for probe B; rejected blind retry-loop on failure (rejected: a real mutex bug firing intermittently would pass almost surely — that IS test-weakening) · CI-env skip of both probes (rejected: loses all CI coverage of the ticket arbitration, which is deterministic and healthy).
- [human] freeze — froze §3 @ v2 (approved by Tin Dang (v1 → v2 change request: the refute-read)
- [AI] build — strategy used: v1 built probe-A margins (stale 8→90s, age→100s, skip path removed) + a 3-way probe-B discriminator (observer-unhealthy→SKIP · beats==0→FAIL heartbeat_dead_masked · else→SKIP), engine byte-untouched (M1, md5 ENGINE pin held). The freeze refute-read (add-advisor) found a blind-steal masking hole — an identity-blind reclaim of a HEALTHY, beating lock reached v1's SKIP, masking probe B's strongest catch — so a v2 change request added the `_HeartbeatObserver` victim-age FAIL rule (victim replaced while age < stale−slack → fail blind_steal_masked). Both probe files (test_project_scope_lock.py, test_global_update_harden.py) carry the observer identically.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
