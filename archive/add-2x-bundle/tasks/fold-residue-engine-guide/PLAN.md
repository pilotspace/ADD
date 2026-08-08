# PLAN: PHASE_GUIDE stops instructing a retired section 2

slug: fold-residue-engine-guide · created: 2026-07-24 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the engine stops instructing users to write a §2 the scaffold template no longer contains — PHASE_GUIDE["direction"] is re-aimed at the shipped section set, and a guard makes any future phantom-section instruction fail.
Framings weighed: re-aim the string + guard every §N the engine cites against the template (chosen — this exact residual survived the fold, a milestone close AND a release cut with nothing objecting; the guard is the only part that prevents a repeat) · re-aim the string alone (rejected — same hand-sweep that produced the defect)
Must:
<must>
  - M1 no engine instruction string tells a user to fill a §N that PLAN.md.tmpl does not contain
  - M2 PHASE_GUIDE["direction"] still names the real Direction bundle work (rules · change plan · red suite) — the fix must re-aim the instruction, not delete it
  - M3 ENGINE_PKG_MD5 is re-aimed so package-digest parity holds after the edit
  - M4 all four engine twins carry byte-identical constants.py
</must>
Reject:
<reject>
  - an engine guide string citing a §N absent from the shipped template -> "phantom_section"
  - an add_engine/*.py edit landing without a pin re-aim -> "stale_engine_pin"
</reject>
After:
<after>
  - `add.py guide` in the direction phase describes only sections that exist in the file it is describing
  - the scenarios fold is complete: no shipped surface still instructs a standalone §2
</after>
Boundary: the engine cites sections in TWO shapes the guard must read — "§4" and section ranges like "§1–§4" (en-dash, not hyphen); a range implies every number it spans.
<assumptions>
  ⚠ PHASE_GUIDE is the ONLY engine map whose strings instruct section-filling — if another user-facing string does the same, this closes one instance and the guard's template-comparison would still catch it only for PHASE_GUIDE; mitigated by scanning every value in the phase maps, not just the direction key
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
add_engine/constants.py — PHASE_GUIDE["direction"], the action string add.py guide
prints to every user in the direction phase.

  BEFORE: "... §1 rules (...) · §2 one scenario per rule · §3 the change PLAN: ...
           · §4 red suite failing for the right reason; then the ONE approval: ..."
  AFTER : the "§2 one scenario per rule" clause is REMOVED and its duty carried by
          §4, matching the shipped template: scenarios live with the tests.
          Everything else in the string is preserved verbatim.

Applied to ALL FOUR engine twins (byte-identical constants.py):
    add-method/tooling/add_engine/constants.py            (source of truth)
    .add/tooling/add_engine/constants.py
    add-method/.add/tooling/add_engine/constants.py
    add-method/src/add_method/_bundled/tooling/add_engine/constants.py

PIN: constants.py is inside package_digest(add_engine/*.py), so ENGINE_PKG_MD5 in
     engine_pin.py must be re-aimed to the new digest (all four twins) or the 22
     files asserting package parity go red. ENGINE_MD5 = md5(add.py) is NOT
     affected — add.py itself is untouched.

Guard shipped with the fix (new, engine suite):
     every §N cited by any PHASE_GUIDE value must exist as a section in
     PLAN.md.tmpl; ranges "§1–§4" expand to every number they span.
```

Grounding anchors (verified in-context): add_engine/constants.py:85 PHASE_GUIDE["direction"] · PLAN.md.tmpl sections 1,3,4,5,6,7 · engine_pin.py:21 ENGINE_PKG_MD5 · engine_manifest.package_digest() digests add_engine/*.py · test_engine_extract_md5.py:87 asserts parity · reproduced live: `add.py guide` in a scratch project prints the §2 instruction.

Target (measurable): phantom §N citations in engine guide strings 1 -> 0 · PHASE_GUIDE["direction"] still names rules/change-plan/red-suite (not truncated) · ENGINE_PKG_MD5 parity restored 4/4 twins · new guard red before / green after · the two prior tasks' suites (5 + 4 checks) and test_scenarios_folded.py (9) all stay green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `.add/tooling/add_engine/constants.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/add_engine/constants.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_engine_guide_sections.py` `./tests/`
Regression floor: the full `tooling/` suite via `unittest discover` (CI's own runner) — the 22 files asserting ENGINE_PKG_MD5 parity are the real floor here; plus test_scenarios_folded.py (9) and the two prior tasks' suites (5 + 4).
Persona (optional): `.add/personas/methodology-engine-dev.md` — deterministic, fail-loud engine work with a digest pin in the blast radius.

Strategy (preferred, not hard): write the phantom-section guard first and prove it red on the real string; edit constants.py in the source tree; recompute package_digest and re-aim ENGINE_PKG_MD5 with a comment naming this task (the file's own convention); mirror BOTH files to the three twins; run the FULL tooling suite, not a subset, because the pin has 22 dependents.

Least-sure flag surfaced at freeze: [contract] whether removing the §2 clause loses instruction the user still needs. The clause carried a real duty — "write one case per rule" — and §4's remaining text says "red suite failing for the right reason", which is about test quality, not per-rule coverage. If the duty evaporates, users get a thinner instruction than before the fold. Mitigation chosen: fold the duty INTO the §4 clause rather than deleting it, so the guide still says one case per rule, just located where the fold put it. M2 exists to pin exactly that.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_guide_cites_no_phantom_section: every §N in any PHASE_GUIDE value exists as a section in PLAN.md.tmpl (ranges expanded) · covers: M1, R:phantom_section
  - test_direction_guide_keeps_its_duties: PHASE_GUIDE["direction"] still names rules, the change plan, the red suite, and one-case-per-rule · covers: M2
  - test_engine_pkg_pin_current: package_digest(add_engine) equals ENGINE_PKG_MD5 · covers: M3, R:stale_engine_pin
  - test_engine_twins_identical: constants.py + engine_pin.py byte-identical across all four trees · covers: M4
</test_plan>

Kind: engine. test_guide_cites_no_phantom_section and test_direction_guide_keeps_its_duties are the red-first pair. test_engine_pkg_pin_current starts GREEN (the pin matches today) and goes RED the moment constants.py is edited — it is the mechanism that FORCES the re-aim, so its red appears mid-build by design, not at the start. test_engine_twins_identical is a regression guard, green at the start.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned. Guard written and proven red on the real string first ("PHASE_GUIDE['direction'] instructs §2, absent from PLAN.md.tmpl"); constants.py re-aimed in the source tree; the pin went stale on cue (96f41126 -> 3d7ec2b9), which is the mechanism that FORCES the re-aim rather than a step to remember; both files mirrored to the three twins; the FULL tooling suite run via CI's own `unittest discover` because the pin has 22 dependents. Fix confirmed end-to-end by re-running `add.py guide` in the scratch project that originally reproduced the defect.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — FULL engine suite via CI's runner: **2285 tests, OK, exit 0** (222s); new guard 4/4; test_scenarios_folded.py 9/9; prior tasks' suites 5/5 and 4/4
- [x] coverage did not decrease — 4 checks added, none removed
- [x] no test or contract was altered during build — the guard was written in direction and untouched after the freeze; §3 FROZEN @ v1 unedited; no re-cross needed on this task
- [x] the green was EARNED, not gamed — M1 proven red on the exact defect before the edit; the fix verified END-TO-END by re-running `add.py guide` in the scratch project that first reproduced it, not by trusting the unit check
- [x] concurrency / timing — n/a, a constant string and a digest literal
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency; the pin re-aim is a literal, and its correctness is asserted by 22 existing files
- [x] layering & dependencies — guard lives in `tooling/test_*.py`, matching CI's discover pattern; pin re-aim follows engine_pin.py's own "re-aimed @ <task>, prior: <hash>" convention
- [x] a person reviewed and approved the change — Tin Dang approved the freeze

TARGET — all clauses met, one §4 label corrected:
  · phantom §N citations 1 -> 0 ✓ (guard confirms)
  · PHASE_GUIDE["direction"] not truncated ✓ — M2 pins rules/change-PLAN/red-suite/per-rule/freeze;
    the one-case-per-rule duty was FOLDED into the §4 clause, not dropped
  · ENGINE_PKG_MD5 parity restored 4/4 twins ✓ (2285-test suite is the proof, incl. 22 pin dependents)
  · guard red before / green after ✓ for M1
  · CORRECTION: §4 called M1 and M2 "the red-first pair". Only M1 was red-first. M2 was GREEN from
    the start by design — it is a do-not-thin-it-out guard whose job is to STAY green across the
    edit, which it did. Mis-labelled when drafting; recorded rather than quietly reframed.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) the obvious cheat here is deleting the §2 clause and calling it fixed while users lose the per-rule-coverage instruction — M2 was written specifically to make that cheat fail, and the duty was folded into §4 instead; (2) the pin is the classic silent-skip risk, so parity was not asserted by my own new check alone but by running the FULL 2285-test suite where 22 independent files assert it; (3) the fix was validated at the USER surface (`add.py guide` output in a scratch project), because a passing unit check on a constant proves the constant changed, not that the human-facing instruction is now correct.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose re-aim the string + guard every §N the engine cites against the template; rejected re-aim the string alone (rejected — same hand-sweep that produced the defect)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. Guard written and proven red on the real string first ("PHASE_GUIDE['direction'] instructs §2, absent from PLAN.md.tmpl"); constants.py re-aimed in the source tree; the pin went stale on cue (96f41126 -> 3d7ec2b9), which is the mechanism that FORCES the re-aim rather than a step to remember; both files mirrored to the three twins; the FULL tooling suite run via CI's own `unittest discover` because the pin has 22 dependents. Fix confirmed end-to-end by re-running `add.py guide` in the scratch project that originally reproduced the defect.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] the scenarios-into-tests fold is now COMPLETE across shipped surfaces — book chapter, mkdocs nav, GETTING-STARTED, templates and the engine's own guide string all agree that scenarios live in §4 (evidence: this task + getting-started-descenarios + fold-residue-templates; three guards now assert it)
- [SPEC · open] a retirement needs a SWEEP SET as a first-class artifact — the milestone should enumerate every surface that references the retired thing (book · nav · package docs · templates · engine strings · skill guides) and the close should check it, because three separate residuals each shipped to users (evidence: dead chapter link in v2.3.0 tarballs · `--fast` in every scaffolded MILESTONE.md · §2 in every `add.py guide`)

### Competency deltas
- [ADD · open] a digest pin is a GOOD forcing function, not overhead — editing constants.py made the pin go stale automatically and 22 files would have gone red, so the re-aim could not be forgotten; contrast the prose residuals in this same sweep, which had no such mechanism and survived a release (evidence: pin 96f41126 -> 3d7ec2b9 detected the instant constants.py changed)
- [TDD · open] validate a fix at the USER surface, not only at the changed symbol — a green unit check on PHASE_GUIDE proves the constant changed; re-running `add.py guide` proves the human now reads the right instruction (evidence: the defect was originally found by reading guide output, not by reading constants.py)
- [SDD · open] write a "must not thin out" guard whenever a fix REMOVES prose — M2 pinned the duties the direction string owes so that deleting the §2 clause could not quietly cost users the per-rule-coverage instruction; the duty was folded into §4 instead of dropped (evidence: M2 green before and after, by design)
- [ADD · open] run the FULL suite, not a subset, when the change touches a pinned artifact — the 4-test guard passed long before the 2285-test suite confirmed the 22 pin dependents were satisfied (evidence: full discover run, 222s, OK)
