════════════════════════════════════════════════════════════════════════
 verify-integrity · Verify integrity — prove the green was EARNED, not gamed
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  A verify gate can tell whether the build EARNED its green or
       gamed the TDD signal — test/contract tampering is caught
       MECHANICALLY (an md5 tripwire on the red suite), the judgment
       cheats (src overfit to fixtures · vacuous asserts · stubbed-away
       logic) by an INDEPENDENT adversarial refute-read, and a confirmed
       cheat self-heals for up to 3 honest re-build attempts before it
       HARD-STOPs to the human; a gamed green is never auto-passed.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 tamper-tripwire             done      PASS 0     ●●●●●●●●●
 earned-green-rubric         done      PASS 0     ●●●●●●●●●
 heal-then-escalate          done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (16 carried)
   • ADD · open · the method now has a reusable mechanical-HARD-STOP
     pattern — snapshot at a phase seam, re-check at the gate before any
     completing outcome, fail-closed, tri-state co-witnessed by an
     existing flag — generalizable to any "freeze X at phase A, enforce
     at phase B" guard beyond tamper (evidence: tamper-tripwire shipped
     as the method's FIRST mechanical HARD-STOP, 815 suite green,
     dogfood check clean)
   • TDD · open · a tripwire whose snapshot lives in agent-writable
     state.json is necessary-not-sufficient: a co-witness flag raises
     the bypass cost (forge two, not one) but a determined agent
     patching both still slips — mechanical TDD enforcement raises cost,
     it does not seal; the semantic refute-read + the human gate stay
     the real backstops (evidence: the §3 freeze flag "accept honest
     ceiling", human-ratified at the verify gate)
   • ADD · open · a security-line classification can EMERGE during build
     (md5-as-tamper-evidence), not only at the §3 freeze — when it does,
     surface it for human ratification AT the verify gate rather than
     self-granting, even when the reasoning holds (evidence: §6 md5
     ratification line; the advisor caught a pre-checked self-granted
     box and it was reframed to an explicit ask)
   • SDD · open · when a new feature needs the exact file set an
     existing counter resolves, extract a path-returning helper and
     delegate the counter to it (one resolution source), never re-glob —
     the snapshot and the engine then agree by construction (evidence:
     the
     `_primary_test_files`/`_declared_test_files`/`_resolved_test_files`
     refactor preserved every prior count, full suite green)
   • ADD · open · a LIVE engine-dogfood task that crossed a phase seam
     under the OLD engine can re-snapshot under the NEW engine via
     `phase tests` + `advance` (the method-sanctioned backward move for
     a live task; `reopen` only works on `done` tasks) — the
     overwrite-on-cross snapshot makes this re-anchor path work
     (evidence: own task re-snapshotted to tripwire {contract_md5
     786a844e…, tests {}} after the ×3 sync)
   • ADD · open · a build-integrity property needs BOTH a mechanical
     floor and a judgment ceiling — the tamper-tripwire (task 1) catches
     the cheats it can SEE (edited test / frozen contract), the
     earned-green rubric the cheats it cannot (src overfit to fixtures ·
     vacuous asserts · stubbed-away logic) via an adversarial
     refute-read; neither layer alone closes the gamed-green gap
     (evidence: this task adds the judgment layer atop the now-shipped
     mechanical floor — the §3 two-layer contract).
   • ADD · open · anchor-presence proves a phrase EXISTS on a surface,
     NOT that two surfaces AGREE on its qualifier — the template read
     "for high-risk" while the guide read "recommended under `autonomy:
     auto`", and no presence test could see the mismatch; cross-surface
     qualifier agreement needs a shared render or an adversarial/human
     read (evidence: advisor caught the template↔guide trigger
     disagreement after all 13 anchor tests were green; reconciled to
     the guide's framing pre-commit).
   • ADD · open · the first NORMAL task run THROUGH a freshly-shipped
     engine guard is its cheapest end-to-end test — task 2 crossed
     tests→build under task 1's live tamper-tripwire and its §3 snapshot
     re-checked clean at the gate (evidence: `add.py gate PASS
     earned-green-rubric` exit 0, no HARD-STOP — the tripwire validated
     on a real task, not a fixture).
   • ADD · open · one milestone can exercise BOTH verify-gate paths,
     proving the autonomy ladder discriminates by risk not ceremony —
     task 1 was human-gated (conservative · high-risk · md5
     security-line ratified by a person), task 2 auto-resolved (auto ·
     normal-risk · deterministic evidence) (evidence: tamper-tripwire
     gate = human PASS; earned-green-rubric gate = auto-resolved PASS,
     same milestone).
   • TDD · open · a prose/method change is testable by anchor-presence +
     mirror-parity rather than coverage — one frozen wording carried
     across guide ×3 / book ×4 / template ×3 / glossary, each guarded by
     a `_norm`-normalized anchor (hard-wrap is incidental) and a
     one-hash md5 parity test, with the engine held byte-identical to
     the pin (evidence: 13 green tests in `test_earned_green_rubric.py`;
     full suite 815→828; add.py md5 == engine_pin).
   • SDD · open · a method built in stages needs a scope guard that
     fails if a LATER stage's machinery leaks BACKWARD into an earlier
     stage's prose — the task-3 loop tokens (self-heal · re-build · 3
     attempts) are asserted ABSENT from the task-2 guide so the rubric
     describes without pre-empting enforcement (evidence:
     `test_principle_no_loop_forward_ref` red-then-green; §3 KNOWN LIMIT
     names the task-2-describes / task-3-enforces boundary).
   • TDD · open · when an engine change legitimately invalidates an
     EXISTING assertion, the test edit is an EVOLUTION (not a weakening)
     iff three hold: the real invariant stays guarded, coverage
     holds-or-rises, and the reason is documented — a reusable
     discriminator for "is this green earned?" (evidence: 3 existing
     tests edited under this rule — `_assert_blocked` kept
     `gate=="none"` strict while loosening phase,
     `test_engine_unchanged` went 1→3 cheat tokens, `test_min_pillar`
     added `heal` coverage — and the independent refute-read returned
     EARNED)
   • ADD · open · a self-heal cap is only real if it cannot be cleared
     without a RECORDED HUMAN ACTION — an unguarded reset (e.g. on
     tests→build re-cross via the open `cmd_phase`) is a trivial bypass;
     the safe default is MONOTONIC (never auto-reset) (evidence: the
     advisor BLOCKED reset-on-recross as a cap bypass; froze monotonic,
     proven by `test_attempts_are_monotonic`)
   • ADD · open · a confirmed-cheat self-heal is HARD-STOP-class, not
     RISK-ACCEPTED-class — it returns-to-build for an honest redo and
     escalates at the cap, but a gamed green is NEVER waived through,
     exactly like a security finding (evidence: `_heal_or_escalate`
     records `gate="HARD-STOP"` at exhaustion with no RISK-ACCEPTED
     branch; `test_fourth_cheat_hard_stops`)
   • ADD · open · a method can audit its OWN builds — dogfooding task
     2's earned-green rubric on task 3's build (a fresh adversarial
     subagent) caught a real nit before the gate, proving the rubric
     bites on the method's own work, not just user features (evidence:
     refute-read flagged the trivially-true `"3" in run_md` assert →
     strengthened to `"3 honest"` before the gate)
   • SDD · open · an anchor-PRESENCE test proves a phrase EXISTS, not
     that two surfaces AGREE on its qualifier — cross-surface contracts
     need an agreement check, not just a presence check (evidence: task
     2's template/guide drift — both carried the earned-green line but
     disagreed on its qualifier — slipped every presence test; caught
     only by manual read)

 DECIDE NEXT  consolidate learnings + archive-milestone
              verify-integrity
════════════════════════════════════════════════════════════════════════