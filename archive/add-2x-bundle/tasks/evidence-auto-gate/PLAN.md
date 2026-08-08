# TASK: The evidence auto-gate: auto-PASS + residue escalation

slug: evidence-auto-gate · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto   <!-- v6 dial: dogfood -->

> v6 · *DD driver: ADD. Owns run.md §"The evidence auto-gate". Stands on principle-reframe (P6/P7).
> THE riskiest contract in v6. Lean TASK.md — substance is the rubric prose.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
The verify gate may be resolved by EVIDENCE (not a person) when sufficient and recorded — principle 7
reframed. Auto-PASS is bounded; the residue tests cannot judge always escalates.
Must:
  - **auto-PASS requires ALL**: tests green · coverage not decreased · no test weakened / contract edited
    · convergence loops dry · completeness-critic found nothing open
  - **always escalates to a human (never auto-passed)**: any **security** finding (HARD-STOP, always);
    a **concurrency**/timing risk tests can't exercise; an **architecture**/layering violation; any failing test
  - records **exactly one outcome** (no silent skip): PASS (evidence + named run as owner) · RISK-ACCEPTED
    (non-security, signed) · HARD-STOP; the record says it was AUTO-RESOLVED and names the run
  - the auto-gate NEVER writes a human signature it did not get (honesty = the pass/skip line)
Reject:
  - security auto-passed                        -> "security_autopass" (method violation; always HARD-STOP)
  - an auto-PASS with a forged human reviewer    -> "forged_signature"
  - a gate left with no recorded outcome         -> "silent_skip"
After: run.md §"The evidence auto-gate" documents auto-PASS conditions + residue escalation + one recorded outcome.

<!-- EXIT: rules stated, rejections named, no open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: auto-PASS only on full evidence
  Given run.md
  Then auto-PASS requires all green + loops dry + critic clean + nothing weakened
Scenario: security never auto-passes
  Given run.md
  Then a security finding is HARD-STOP and always escalates to a human
Scenario: one recorded outcome, honestly attributed
  Given an auto-resolved gate
  Then exactly one outcome is recorded, marked auto-resolved, with no forged human signature
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"The evidence auto-gate" (both trees, md5-identical)
FROZEN: auto-PASS = {green · coverage held · nothing weakened · loops dry · critic clean};
        residue {security=HARD-STOP always · concurrency · architecture · any fail} -> human;
        record exactly one outcome, auto-resolved, no forged signature.
GUARD: test_v6_run.py::test_evidence_auto_gate_pass_and_escalation
reject codes: security_autopass · forged_signature · silent_skip
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit; originally self-gated at v6 dogfood — no human at the original seam)
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v6_run.py asserts auto-PASS defined + security-always-escalates + residue + one outcome. RED first.
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose in run.md (both trees byte-identical). No add.py change. No test/contract edits.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — test_v6_run 8/8 green; full suite 147 OK
- [x] coverage held — auto-PASS + escalation + one-outcome asserted; proven RED first
- [x] no test/contract altered; no secrets/deps; both trees md5-identical
- [x] **SECURITY check (this gate): no security finding in this docs change — so the auto-gate's own
      security rule is NOT exercised here; it remains unproven against a real security case**
- [ ] a person reviewed — **NO. Self-gated (v6 dogfood).**

BLIND-SPOT FINDING (the sharp one): every self-gate in this whole v6 run recorded `PASS` while the
"a person reviewed" box stayed unchecked. By THIS task's own contract, an unreviewed gate that needs
human judgment and gets none is closer to `silent_skip` than `PASS`. The auto-gate I'm specifying would
arguably FAIL its own residue rule on each of these docs tasks (each edits the trust layer = an
"architecture"-class change to the method). The contract is sound; the dogfood violated it to ship it. → delta.

### GATE RECORD
Outcome: PASS  (provisional — automated evidence only; see blind-spot finding)
Reviewed by: AI self-gate (v6 dogfood) — NOT human-verified · date: 2026-06-01
<!-- security = HARD-STOP; one outcome. -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: any real auto-PASS — was the residue actually checked, or rubber-stamped?
Spec delta: "edits the method/trust layer" should be an explicit residue class that always escalates — this run proves method-edits are exactly what an auto-gate must NOT self-approve.

### Competency deltas
- [ADD · folded] the dogfood auto-gated method-defining changes (the book, the rubric) — the one class most needing human judgment — exposing that "what counts as residue" is under-specified (evidence: 5 self-gated PASSes, each editing the trust layer, none human-reviewed)
- [SDD · folded] the auto-gate's security rule is untestable by string checks and was never exercised (no security case in v6) — its most important guarantee is unproven (evidence: §6 security line; test asserts the WORDS only)
- [DDD · folded] "residue" needs a sharper domain definition — security/concurrency/architecture is not exhaustive; method/trust-layer edits are a missing category (evidence: this task's blind-spot finding)
