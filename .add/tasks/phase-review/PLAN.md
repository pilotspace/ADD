# TASK: drop only provably-redundant guide/phase ceremony

slug: phase-review · created: 2026-06-23 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): the 9 canonical phase guides `add-method/skill/add/phases/{0-setup,0-ground,1-specify,2-scenarios,3-contract,4-tests,5-build,6-verify,7-observe}.md` (audited, NOT edited) — cross-referenced against the engine enforcement in `add-method/tooling/add.py`: `cmd_advance` (`setup_unlocked` L953-954 · `unflagged_freeze` L963-967) · `cmd_gate` (`setup_unlocked` L1101) · `_tamper_guard`→`_heal_or_escalate` (L3739-3762) · `_scope_guard` · `_audit_findings` (`unescalated_security_note` L5064-5067) · `_setup_locked` · `HEAL_CAP`.
Context (working folder): the milestone mandate (exit criterion 3, L46) — "every dropped ceremony item is provably redundant (engine enforces it); a dogfood walk shows identical gates/decisions; nothing meaningful removed", AND the task line (L41) — "drop ONLY what carries no meaning; may find nothing — that is a valid result". The sibling spawn-fold v2 over-fold (deleted advisory-specific content treated as a duplicate) is the cautionary precedent.
Honors (patterns / conventions): conservative-when-unsure (KEEP on doubt); 3-tree byte parity (if anything were dropped, edit canonical → cp ×2); never weaken a gate/security/spec-first; depth-by-stage (mvp = full flow, light).
Anchors the contract cites: the AUDIT VERDICT (zero high-confidence provably-redundant items; 3 borderline items all lean KEEP — the two 5-build exit-gate self-checks + the 3-contract `unflagged_freeze` parenthetical) · the byte-unchanged invariant on all 9 phase guides · the full suite + 3-tree parity as the no-drift guardrail.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Audit the phase guides for provably-redundant ceremony the engine already enforces, and drop ONLY what carries no meaning. The audit's honest result is the deliverable — here it is "nothing qualifies": the guides are already tight, so ZERO guide bytes change.
Framings weighed: (audit → drop-nothing, guides confirmed tight) CHOSEN by Tin Dang — the audit cross-referenced all 9 guides against the engine and found no prose that MERELY restates enforcement without nuance/rationale/how-to; the milestone explicitly sanctions "may find nothing". · (drop the 3 borderline items) REJECTED — removing the two 5-build exit-gate self-checks trades a real heal-attempt-bookkeeping property (self-catch at build avoids consuming a HEAL_CAP attempt → the `heal_exhausted` path) for ~dozens of bytes; weakens no gate but is not worth the thin behavioral shift. · (find/force a removal to "show progress") REJECTED — that is the spawn-fold v2 over-fold mistake.
Must:
<must>
  - The audit covers all 9 canonical phase guides, each candidate VERIFIED against a specific engine mechanism in add.py (cmd_/gate/_die/_tamper_guard/_scope_guard/_audit_findings), not assumed.
  - A guide item is "provably redundant" ONLY if the engine mechanically enforces it AND the prose adds no rationale/how-to/judgment/orientation. Orientation sentences ("the engine refuses X") shape sequencing → KEEP. When unsure → KEEP.
  - Result: ZERO guide bytes change (nothing met the bar). All 9 phase guides stay byte-identical to HEAD across all 3 trees; the audit verdict is recorded as the task's evidence.
  - The no-drift guardrail is the EXISTING full suite (many tests assert guide prose verbatim) + the 3-tree parity tests staying green — a dogfood walk shows identical gates/decisions.
Reject:
<reject>
  - a guide item dropped while the engine does NOT fully enforce it (or the prose carried rationale/how-to) -> "meaning_removed" (the over-fold failure)
  - any phase-guide file changes bytes in this no-op task -> "unexpected_guide_drift"
  - the 3 trees diverge -> "parity_break"
  - an existing guide-prose test weakened/deleted to accommodate a drop -> "test_weakened"
</reject>
After:
<after>
  - The phase guides are AUDITED and confirmed tight; nothing dropped; all 9 guides byte-identical to HEAD ×3 trees; full suite + `add.py check` green; the audit verdict (0 high-confidence, 3 borderline KEEP) is recorded. The milestone's exit criterion 3 is met trivially (nothing removed → nothing to prove redundant).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] "found nothing" is the correct result, not under-auditing — lowest confidence because an audit that drops nothing can look like insufficient effort. Mitigated: every candidate was cross-referenced to a NAMED engine symbol/reject-code, and the 3 closest candidates were surfaced as borderline with the exact behavioral reason they lean KEEP (heal-bookkeeping). If wrong: a later pass drops a specific named item as its own change-request. Human accepted "found nothing".
  - [x] the engine mechanisms cited actually exist — VERIFIED by the audit subagent against add.py line refs (cmd_advance/cmd_gate/_tamper_guard/_scope_guard/_audit_findings).
  - [x] no behavior changes — VERIFIED by construction: zero bytes change, so every gate/decision/test is identical.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the audit drops nothing — guides stay byte-identical
  Given the 9 canonical phase guides at HEAD
  When the phase-review audit completes with verdict "0 provably-redundant items"
  Then no phase-guide file changes bytes
  And all 3 mirror trees stay byte-identical (md5)

Scenario: no-drift guardrail holds
  Given nothing was dropped from any guide
  When the full suite + `add.py check` run
  Then they are green (every guide-prose-assertion test unchanged)
  And a dogfood walk shows identical gates/decisions (no gate/security/spec-first weakened)

Scenario: reject meaning_removed
  Given a candidate item whose prose carries rationale/how-to/orientation
  When the audit evaluates it
  Then it is classified KEEP (not dropped)
  And dropping it anyway would fail -> "meaning_removed"

Scenario: reject unexpected_guide_drift
  Given this is a no-op audit task
  When verify runs
  Then a `git diff` on add-method/skill/add/phases/ is EMPTY
  And any byte change there fails -> "unexpected_guide_drift"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
AUDIT phases/ → drop only engine-enforced, meaning-free ceremony
  verdict -> { high_confidence_redundant: 0, borderline_keep: 3, dropped: 0 }
  guide bytes changed -> 0   (all 9 canonical phase guides byte-identical to HEAD)
  3-tree parity -> md5-identical (canonical add-method/skill/add/phases ≡ .claude ≡ _bundled)

Borderline items examined (ALL classified KEEP):
  - 5-build.md exit-gate "No test/contract modified" + "No file outside §5 Scope"
      enforced by _tamper_guard / _scope_guard at gate PASS, BUT self-catch at build
      avoids consuming a HEAL_CAP attempt (the heal_exhausted path) → real, KEEP
  - 3-contract.md "(unflagged_freeze)" parenthetical → names the reject code; orientation, KEEP

Guardrail (no new test — nothing changed to test):
  the EXISTING full suite (guide-prose-assertion tests) + 3-tree parity tests stay green;
  `git diff add-method/skill/add/phases/` is EMPTY. A dogfood walk shows identical gates.
```

Status: FROZEN @ v1 — approved by Tin Dang (audit accepted as "found nothing": 0 provably-redundant items, drop nothing, guides confirmed tight). autonomy:auto → verify may auto-gate on the byte-unchanged + suite-green evidence.

Least-sure flag surfaced at freeze: [contract] "found nothing" is the right result rather than under-auditing — why it could be wrong: a zero-drop audit can read as insufficient effort. Safe because every candidate was tied to a NAMED engine mechanism and the 3 closest were surfaced as borderline-KEEP with their exact behavioral reason (heal-bookkeeping); the milestone explicitly sanctions "may find nothing". Cost if wrong: a later targeted change-request drops one named item. Human accepted at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: existing suite held (no new code → no new coverage; nothing may regress)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - NO NEW TEST — this is a no-op audit; there is nothing changed to test. Writing a fence that
    re-pins the current guide bytes would itself be redundant ceremony (the very thing audited).
  - GUARDRAIL (already-existing, the no-drift oracle): the full `python3 -m unittest discover` suite
    — many tests assert phase-guide prose VERBATIM (test_rewrite_guides, test_xml_convention,
    test_skill_lean, the tree/bundle parity tests) → if any guide byte changed, they go red.
  - GUARDRAIL: `git diff --stat add-method/skill/add/phases/` is EMPTY (verified at verify).
  - GUARDRAIL: 3-tree md5 parity on phases/ unchanged.
</test_plan>

Tests live in: `./tests/` · no local tests (the existing suite + git-diff + parity ARE the guardrail).
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `./`   (the task's own TASK.md only — NO production file is written; the audit verdict is "drop nothing", so the 9 phase guides are deliberately NOT in scope and must stay byte-unchanged)
Strategy (ordered batches): 1. (audit already done in ground) 2. drop nothing 3. verify the no-drift guardrail: full suite green + `git diff add-method/skill/add/phases/` empty + 3-tree parity.
Safety rule (feature-specific): touch NO phase guide — a single byte changed here is `unexpected_guide_drift`. The whole point is that the audit found nothing to remove.
Code lives in: (none — no-op audit)
Constraints: do NOT change any test, contract, or guide; the result is intentionally empty.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1570/0 (the no-drift oracle: guide-prose-assertion tests unchanged → green)
- [x] coverage did not decrease — no code touched; +0 tests, −0 tests
- [x] no test or contract was altered during build — none touched; §3 FROZEN @ v1 unchanged
- [x] the green was EARNED, not gamed — there is NO green to game (no build); the real risk is a LAZY audit. Mitigated: the audit cross-referenced every candidate to a named add.py mechanism (cmd_advance/cmd_gate/_tamper_guard/_scope_guard/_audit_findings) and surfaced the 3 closest as borderline-KEEP with their exact behavioral reason (heal-bookkeeping) — not a hand-wave
- [x] concurrency / timing of the risky operation is safe — N/A (no operation; zero bytes changed)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A (no code)
- [x] layering & dependencies follow CONVENTIONS.md — N/A (nothing changed)
- [x] a person reviewed and approved the change — Tin Dang accepted "found nothing" at the §3 freeze; autonomy:auto → verify auto-resolves on the byte-unchanged + suite-green evidence (no security/concurrency/architecture residue)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `git diff --stat add-method/skill/add/phases/` (+ the 2 mirror trees) is EMPTY — confirmed: empty diff at verify
- [x] 3-tree md5 parity on the phase guides unchanged — confirmed: 0-setup/1-specify/3-contract/5-build/6-verify all OK across canonical ≡ .claude ≡ _bundled
- [x] the audit verdict is recorded — confirmed: §3 contract carries {high_confidence_redundant:0, borderline_keep:3, dropped:0} + the 3 borderline items named with their KEEP reason

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read all 9 phase guides in the audit, cross-referenced each candidate to the engine. Confirmed: no prose MERELY restates enforcement; "the engine refuses X" sentences are orientation (shape sequencing) → KEEP; exit-gate self-checks differ in heal-bookkeeping → KEEP. Nothing meets the drop bar.
- [x] DEAD-CODE — N/A (no code added)
- [x] WIRING — N/A (no code added)

### GATE RECORD
Outcome: PASS   (auto-resolved under autonomy:auto — no-op audit, complete evidence, no escalating residue)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (accepted "found nothing" at the §3 freeze) · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
