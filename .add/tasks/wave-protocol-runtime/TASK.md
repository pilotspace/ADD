# TASK: streams.md: merge-time fork-base check + worker commits SUMMARY.md

slug: wave-protocol-runtime · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — amends the method's own orchestration rubric (streams.md), same surface as wave-ledger;
     autonomy lowered to conservative: the verify gate stops for the human. Source: v19 wave deltas #7 + #8. -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: amend streams.md "Wave ledger" so its fork-base discipline is SATISFIABLE on a runner that creates the worktree AT spawn, and so a worker durably persists its own report — closing v19 wave deltas #7 (merge-time fork-base) + #8 (worker commits SUMMARY.md). This is a method-surface (prose) change-request, not engine code.
Framings weighed: amend the existing ledger protocol in place — add a merge-time alternative to the pre-spawn `unverified_fork_base` cell + a "worker commits SUMMARY.md/deltas.md" line to the worker `<return>` (chosen: the CONVENTIONS:90 amendment already states the rule; streams.md must mirror it or the check stays prose-only — the exact lesson #7 teaches) · invent a new add.py refusal that runs the check (rejected: the check is orchestrator-discipline across an opaque harness seam, not engine state — words-exist≠method-works cuts both ways, but engine enforcement of a worktree-pool fact the engine can't observe is vacuous) · leave it CONVENTIONS-only (rejected: the human already declined this — a shipped protocol doc that contradicts its own folded convention is the recursion)
Must:
<must>
  - streams.md states that on a spawn-time-worktree runner the pre-spawn fork-base evidence cell is impossible, and the `unverified_fork_base` refusal SHIFTS to: worker step-0 sync-to-base + re-echo, verified by the orchestrator at MERGE-time before merge-back — the check shifts, it never skips
  - streams.md worker `<return>` contract requires the worker to COMMIT its SUMMARY.md + deltas.md in the worktree (not merely write them) — uncommitted worktree files survive only by harness courtesy
  - both add.py copies of streams.md (canonical add-method + dogfood .add, + bundle if present) stay md5-identical after the edit (dogfood-parity convention)
  - the existing pre-spawn rule is PRESERVED as the default for fresh-HEAD-worktree runners — the merge-time path is an additive alternative, not a replacement (positivization-boundary: don't delete the working rule)
</must>
Reject:
<reject>
  - the edit removes/weakens the fresh-base pre-spawn rule rather than adding the merge-time alternative -> "fork_base_rule_weakened"
  - streams.md mirror copies diverge in md5 after the edit -> "mirror_drift"
</reject>
After:
<after>
  - a future wave on a spawn-time-worktree runner has a contracted, in-protocol path for the fork-base check — the CONVENTIONS:90 runtime-exception and the shipped streams.md text agree, and the worker contract names the SUMMARY.md commit
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a prose amendment is enough — the check is orchestrator-discipline and cannot be engine-enforced (the harness creates the worktree, the engine never sees the pool) — lowest confidence because "words-exist≠method-works" warns that prose checks don't run; mitigation/cost: the merge-time leg IS engine-adjacent (the orchestrator verifies the echo before a cherry-pick the engine could guard later) — name the enforcement-deferral explicitly rather than claim prose = enforcement; if wrong: a follow-up add.py guard on merge-back
  - [ ] streams.md is the only surface carrying the pre-spawn rule (vs. the book docs/ chapter on streams) — confirm by grep before freeze; if a book chapter also states it, the cross-cutting-reword rule applies (enumerate every surface)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: spawn-time-worktree runner has an in-protocol fork-base path   # Must 1
  Given a runner that creates each worker's worktree AT spawn from a pool (the pre-spawn rev-parse evidence cell is unsatisfiable)
  When a reader consults streams.md's "Design for failure" / "Wave ledger" section
  Then streams.md states the unverified_fork_base check SHIFTS to worker step-0 (sync-to-base + re-echo) verified by the orchestrator at MERGE-time before merge-back — the check shifts, it never skips
  And the shifted check still names the same refusal code (unverified_fork_base), so the shipped text and the folded CONVENTIONS runtime-exception agree

Scenario: a worker durably persists its own report   # Must 2
  Given the worker PROMPT `<return>` contract in streams.md
  When the worker finishes its task inside the worktree
  Then streams.md instructs the worker to COMMIT SUMMARY.md + deltas.md in the worktree, not merely write them
  And the "worker PROPOSES, orchestrator RECORDS; a worker never runs add.py" rule remains stated unchanged

Scenario: fresh-HEAD-worktree runner keeps the pre-spawn rule as the default   # Must 4
  Given a runner that forks the worktree from current HEAD (the pre-spawn rev-parse cell IS satisfiable)
  When a reader consults streams.md
  Then the original "Fresh worktree base (verify base == HEAD)" pre-spawn rule is still stated as the default path
  And the merge-time path reads as an additive ALTERNATIVE for the spawn-time case, never a replacement of the pre-spawn rule

Scenario: the three streams.md copies stay byte-identical   # Must 3
  Given the canonical (add-method/skill), dogfood (.claude/skills), and bundle (_bundled) copies of streams.md
  When the wave-protocol-runtime amendment is applied
  Then md5 of all three copies yields exactly one hash

Scenario: REJECT — the pre-spawn rule is removed or weakened   # Reject 1 -> fork_base_rule_weakened
  Given the amendment edit to streams.md
  When the edit deletes or weakens the fresh-base pre-spawn fork-base rule instead of ADDING the merge-time alternative
  Then the change is rejected as "fork_base_rule_weakened"
  And the pre-spawn rule's anchor tokens ("Fresh worktree base", "verify base == HEAD") must remain present in streams.md

Scenario: REJECT — the mirror copies diverge   # Reject 2 -> mirror_drift
  Given the three streams.md copies
  When the edit lands in fewer than all three (their md5 differs)
  Then the change is rejected as "mirror_drift"
  And no copy is left partially amended — all three carry identical bytes, or the edit does not ship
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
AMEND  add-method/skill/add/streams.md   (×3 byte-identical mirror:
       .claude/skills/add/streams.md · add-method/src/add_method/_bundled/skill/add/streams.md)

  Amendment A — merge-time fork-base shift   (in the "Design for failure" fork-base bullet
                and/or the evidence-cell `unverified_fork_base` note)
    ADD: on a runner that creates the worktree AT spawn from a pool, the pre-spawn
         rev-parse evidence cell is UNSATISFIABLE; the `unverified_fork_base` check
         SHIFTS to worker step-0 (sync-to-base + re-echo), verified by the orchestrator
         at MERGE-time before merge-back. The check shifts, it never skips.
    KEEP: the "Fresh worktree base (verify base == HEAD)" pre-spawn rule stays the
          DEFAULT for fresh-HEAD-worktree runners — additive alternative, not replacement.

  Amendment B — worker commits its own report   (in the worker PROMPT `<return>` contract)
    CHANGE: "write the same into SUMMARY.md" -> the worker COMMITS SUMMARY.md + deltas.md
            in the worktree (uncommitted worktree files survive only by harness courtesy).
    KEEP: "the worker PROPOSES; the orchestrator RECORDS; a worker never runs add.py".

  200 (conformant) -> {
    present:   "MERGE-time" shift · "step-0" sync/re-echo · `unverified_fork_base` (shifted, not deleted)
               · worker "commit" of SUMMARY.md + deltas.md
    preserved: "Fresh worktree base" · "verify base == HEAD"   (pre-spawn rule intact)
    parity:    md5(×3 streams.md) == one hash
  }
  4xx -> { error: "fork_base_rule_weakened" | "mirror_drift" }

Schema: prose-only edit to streams.md ×3. NO engine/add.py change -> `engine_pin` HOLDS
        (no bump). Guard: extend `add-method/tooling/test_streams.py` to assert the
        present+preserved tokens (`_norm`-normalized, hard-wrap incidental) + the ×3 md5
        parity. Names match GLOSSARY: wave ledger · fork-base · unverified_fork_base · worktree.
```

Least-sure flag surfaced at freeze: [spec] a prose amendment is enough — streams.md DESCRIBES the merge-time fork-base shift; the engine never ENFORCES it (it cannot see the worktree pool), so enforcement is explicitly DEFERRED to a future task, NOT claimed. Cost if wrong: a future wave still skips the check — mitigated because the merge-time leg is engine-ADJACENT (a cherry-pick add.py could guard later). Discriminator: "does the contract claim enforcement, or discipline?" → discipline, honestly labelled, mirroring the already-folded CONVENTIONS runtime-exception. [contract] secondary: Amendment A's insertion point is token-pinned, not location-pinned — either home (the "Design for failure" bullet or the evidence-cell note) is conformant.

⚠ Lowest-confidence flag — surfaced for the one approval:
  [spec] **A prose amendment is enough — streams.md DESCRIBES the merge-time shift; the engine never ENFORCES it.**
    The fork-base check is orchestrator-discipline across an opaque harness seam (the engine can't see the
    worktree pool). Most-likely-wrong because "words-exist≠method-works" — a prose check no test runs is the exact
    recursion v19 delta #7 warned about. Cost if wrong: a future wave still skips the check. Mitigation (why we
    ship anyway): the merge-time leg is engine-ADJACENT — the orchestrator verifies the echo before a cherry-pick
    that add.py COULD guard later — so enforcement is explicitly DEFERRED (a separate future task), NOT claimed.
    The contract ships prose-that-agrees-with-the-folded-CONVENTIONS-rule, honestly labelled discipline-not-enforcement.
  [contract] secondary — Amendment A's insertion point (the "Design for failure" bullet vs the evidence-cell note):
    the guard pins TOKENS, not location, so either spot is conformant — flagging only in case you want a specific home.

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-11 (prose-describes-the-shift; engine-enforcement deferred — the approved lowest-confidence call).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: token-presence (prose feature — phrasing free, behavior locked) + ×3 md5 parity.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_merge_time_fork_base_shift_stated (Scenario 1 / Must 1): assert streams.md states the
    shift — tokens `merge-time` + `step-0` present, and `unverified_fork_base` still present
    (the check shifts, never skips). RED now (no merge-time/step-0 in streams.md).
  - test_worker_commits_its_report (Scenario 2 / Must 2): assert `commit summary.md` + `deltas.md`
    present in the worker `<return>` region. RED now (today it says "write", not "commit").
  - test_pre_spawn_rule_preserved (Scenario 4 / Must 4 · Reject 1 fork_base_rule_weakened): assert
    `fresh worktree base` + `base == head` still present. GREEN invariant (must stay green).
  - test_three_streams_copies_byte_identical (Scenario 3 / Must 3 · Reject 2 mirror_drift): all 3
    streams.md copies present and md5 == one hash. GREEN invariant (re-sync keeps it green).
</test_plan>
RED triage: the 2 NEW-behavior tests are red before build; the 2 invariant tests stay green throughout.

Tests live in: `add-method/tooling/test_streams.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 843 OK on **py3.10 AND py3.14** (the 4 wave tests added; CI-version run per the PR-#6 lesson); `WaveProtocolRuntimeTest` 4/4 green
- [x] coverage did not decrease — additive: +4 tests, 0 removed/weakened; the 2 invariant tests stayed green throughout
- [x] no test or contract was altered during build — tamper tripwire CLEAN via the engine's own `_tripwire_divergence` → `[]` (§3 `c4da6753` + test_streams.py `a957a335` byte-unchanged; build touched ONLY streams.md ×3)
- [x] concurrency / timing of the risky operation is safe — the amendment HARDENS concurrency-failure design: the `unverified_fork_base` check SHIFTS (never skips) to worker step-0 on spawn-time pool runners, verified at merge-time; worker now COMMITS its report so the serial-integration merge-back carries it (no harness-courtesy data loss)
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown prose ×3 only; no code, no deps, `engine_pin` HOLDS (no bump)
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the already-folded CONVENTIONS runtime-exception (fv-folded); pre-spawn rule preserved as DEFAULT, merge-time path additive
- [x] a person reviewed and approved the change — Tin Dang, verify gate 2026-06-11 (PASS + log follow-up)

### Earned-green refute-read (verify-integrity rubric · risk:high → conducted, presented to the human)
- VERDICT: green is **EARNED**, not gamed. The 2 new-behaviour tests pass *because* substantive mechanism prose was added (streams.md:75-80 explains WHY the pre-spawn rev-parse cell is unsatisfiable on a spawn-time pool, the shift to step-0 sync+re-echo, merge-time verification, "it never skips"; streams.md:213-215 states the worker COMMITS its report + the WHY). Not keyword-stuffing. The 2 invariant tests pass because the pre-spawn rule is preserved (DEFAULT, "never a replacement") and ×3 copies are byte-identical.
- DISCLOSED RESIDUE (= the frozen lowest-confidence flag, not a verify surprise): these are token-presence + ×3-parity guards — they lock that the WORDS and the MIRROR hold, not that the engine EXECUTES the merge-time shift (it can't see a worktree pool). Enforcement is explicitly DEFERRED to a future engine task; this change-request ships prose-discipline, honestly labelled. No security finding → not HARD-STOP.

### GATE RECORD
Outcome: PASS — human-gated (green EARNED per the refute-read; the only residue is the freeze-approved deferred-enforcement flag, now logged as `engine-merge-base-enforcement`)
Reviewed by: Tin Dang · date: 2026-06-11
Post-gate refinement (honest record): the PR #7 careful review found Amendment A stated the merge-time shift in the design-for-failure bullet but NOT in the ledger "Evidence cells" paragraph (a same-file second mention). One clause was added there — Amendment A's OTHER §3-named home ("the evidence-cell `unverified_fork_base` note … either spot is conformant", see §3 + the freeze flag). WITHIN the frozen contract, no test weakened, no contract edited; streams.md ×3 re-synced (md5 `82e08b0d`), suite 843 OK on py3.10. Text changed AFTER the PASS — disclosed here so the record is honest.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the 4 `test_streams.py::WaveProtocolRuntimeTest` guards are the standing monitors — a future streams.md refactor that drops the merge-time/step-0 tokens, un-commits the worker report, weakens the pre-spawn rule, or breaks ×3 parity fails loudly. Live signal for the deferred half: a wave on a spawn-time runner whose worker arrives with a stale base (the merge-time echo mismatches) — currently caught by orchestrator discipline, not the engine.
Spec delta for the next loop: the merge-time fork-base check is prose-discipline, not engine-enforced — `engine-merge-base-enforcement` (logged this gate) is the contracted follow-up to add an add.py guard on merge-back.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] a folded CONVENTIONS runtime-exception must be MIRRORED onto every protocol surface it governs (streams.md), or the convention ships prose-only on one surface and the other contradicts it — the cross-surface recursion v19 delta #7 named (evidence: this task existed solely because CONVENTIONS:90 stated the rule but streams.md still told orchestrators to do the unsatisfiable pre-spawn check)
- [ADD · open] design-for-failure on a concurrency invariant means the check SHIFTS, never SKIPS, when its evidence cell is unsatisfiable — relocate the guarantee (here: pre-spawn rev-parse → worker step-0 + merge-time verify), don't drop it (evidence: streams.md:75-80 keeps `unverified_fork_base` while moving WHERE it's proven)
- [SDD · open] when a spec's enforcement crosses an opaque harness seam the engine can't observe, NAME the enforcement-deferral explicitly at freeze rather than let prose masquerade as enforcement (evidence: the frozen lowest-confidence flag + `engine-merge-base-enforcement` follow-up, not a silent prose check)
- [TDD · open] token-presence + ×3-mirror-parity guards are the honest test shape for a prose-discipline change with no executable engine hook — they lock the WORDS and the MIRROR, and the refute-read confirms the words carry mechanism, not keywords (evidence: 4/4 green on substantive amendments; the 2 invariant tests pin the preserved pre-spawn rule)
