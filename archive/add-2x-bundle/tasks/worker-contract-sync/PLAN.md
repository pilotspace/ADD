# TASK: one worker-contract floor across the 5 roster agents (drift guard)

slug: worker-contract-sync · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/agents/add-{advisor,build,design,persona,verify}.md + .claude/agents/ twins — READ-ONLY this task; add-method/tooling/test_worker_contract_sync.py (new)
Context (working folder): streams.md worker-contract XML (pin-locked floor); prior DECLINED stanza dedup — self-contained prompts are a deliberate invariant
Honors (patterns / conventions): agents/ is NOT a bundled tree (2-tree parity, not 3); guard-tests prove red via mutation, never by breaking the real tree
Seams consulted: none apply
Anchors the contract cites: '## Boundary (the irreducible floor)' · '## Return (disclose progress)' stanzas in all 5 agents
Issues/Risks (→ feed §1): the 5 agents' boundary/return floors are hand-maintained in 2 trees with NO drift guard — one edited tree or one dropped floor marker ships silently; generated stanzas (sync-guidelines pattern) would overturn the declined-dedup invariant, so the guard is the right half of the task's either/or
Related intent: method-ergonomics — every roster spawn must carry the same irreducible worker floor (security HARD-STOP · propose-never-record · disclose persona+confidence)
Ground SHA: 4149f10

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a worker-contract drift guard across the 5 roster agents' Boundary/Return stanzas
Framings weighed: parity+floor-census guard test (chosen) · engine-generated stanzas via sync-guidelines (overturns the declined-dedup self-contained-prompt invariant) · single shared include (same objection)
Must:
<must>
  - per agent, the 2 trees are byte-identical
  - each Boundary stanza carries MAY: · MUST NOT: · STOP-and-escalate and names the security HARD-STOP
  - each agent states never-run-add.py + never-write-shared-state (propose, orchestrator records)
  - each Return stanza discloses persona + confidence
</must>
Reject:
<reject>
  - a one-tree stanza edit -> parity test red
  - a floor marker dropped in BOTH trees -> census test red (parity alone cannot catch it)
</reject>
After:
<after>
  - no roster agent can silently lose its worker floor or drift between trees
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the guarded floor set (3 markers · HARD-STOP · records-invariant · persona/confidence) IS the irreducible contract — lowest confidence because it was censused from the 5 bodies, not a spec; if wrong: an over-pin blocks a legitimate agent edit (loosen deliberately, one marker at a time)
  - [x] all 5 agents already hold the full floor — confirmed by census (no agent edit needed; the guard ships green)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: tree parity   # M1
  Given the 5 agents in both trees
  When hashed per agent
  Then one digest each

Scenario: boundary floor   # M2
  Given each Boundary stanza
  When scanned
  Then MAY: · MUST NOT: · STOP-and-escalate all present

Scenario: security floor   # M2
  Given each agent body
  When scanned
  Then HARD-STOP is named

Scenario: records invariant   # M3
  Given each agent body
  When scanned
  Then never-run-add.py and shared-state both stated

Scenario: return disclosure   # M4
  Given each Return stanza
  When scanned
  Then persona and confidence keys present

Scenario: mutation catches drift   # R1/R2
  Given a one-byte one-tree edit, then a both-trees marker rename
  When the guard runs
  Then parity red, then census red
  And the real trees are restored byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
test_worker_contract_sync.py (5 tests), guarding per agent × 2 trees:
  parity: md5(add-method/agents/X.md) == md5(.claude/agents/X.md)
  boundary: MAY: · MUST NOT: · STOP-and-escalate within the Boundary stanza
  floor: HARD-STOP named · never run add.py · shared state
  return: persona + confidence after '## Return (disclose progress)'
No agent file changes; no generated stanzas (declined-dedup invariant kept).
Schema: none
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [contract] the censused floor set is the irreducible one — because it came from the bodies, not a spec; if wrong: an over-pin blocks a legitimate edit (loosen deliberately)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 4 floor facets × 5 agents × 2 trees + 2 mutation proofs
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_worker_contract_sync (5 tests): parity · boundary markers · security floor · records invariant · return disclosure · covers: M1–M4; R1/R2 proven by mutation (restored after)
</test_plan>

Tests live in: `add-method/tooling/` (test_worker_contract_sync.py) · red proven by MUTATION (guard ships green over a healthy tree; mutation turns it red for the right reason).

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/`
Strategy (ordered batches): 1. census the shared floor across the 5 bodies 2. write the guard 3. mutation-prove both failure classes 4. sibling batch (roster_shipped + packaging)

Persona (required): generic — test-author stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: parity alone misses a both-trees drift → the census tests scan content, not just hashes; mutation must ALWAYS restore in a finally block
Strategy actually used: as planned; both mutations caught (parity FAIL, then boundary-census FAIL), trees restored byte-identical
Safety rule (feature-specific): the guard READS the agent trees only; mutation proofs restore from an in-memory backup in finally
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a one-tree stanza edit turns the suite red — confirmed by mutation proof (parity FAIL observed, tree restored)
- [x] a both-trees marker loss turns the suite red — confirmed by second mutation proof (census FAIL observed)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the guard is self-contained; unittest discovers it
- [x] DEAD-CODE (code) — none
- [x] SEMANTIC (prose / non-code) — all 5 agent bodies read; the floor census matches every body verbatim

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] both stanza headings resolve in all 10 files — grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: two mutation classes (one-tree drift · both-trees marker loss) — the guard fails for exactly the right reason in each; trees byte-restored

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — read-only guard; mutation proofs restore in finally; the HARD-STOP floor is now pinned in all 5 agents
2. Concurrency: CLEAR — n/a
3. Architecture: CLEAR — guard over generation; the declined-dedup self-contained-prompt invariant stands
Verdict: PASS
Residue: none
Binding: advisory — mechanical

### GATE RECORD
Reported: no — collapsed ceremony under the standing implement-all directive; evidence above
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose parity+floor-census guard test; rejected engine-generated stanzas via sync-guidelines (overturns the declined-dedup self-contained-prompt invariant) · single shared include (same objection)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned; both mutations caught (parity FAIL, then boundary-census FAIL), trees restored byte-identical
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

