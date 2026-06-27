# TASK: Disclose that a MISSED security finding is invisible to the engine under auto

slug: security-escalation-disclosure · created: 2026-06-27 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/skill/add/phases/6-verify.md` (line ~29, the "Security —" residue bullet) — claims a security note "escalates to the human — start it with NOTE or ⚠ so `add.py audit` can see it (`unescalated_security_note`)". DOC EDIT: disclose that this only works for a MARKED note; an unmarked (missed) finding is invisible. (+ 2 parity mirrors: `.claude/skills/add/phases/6-verify.md`, `add-method/src/add_method/_bundled/skill/add/phases/6-verify.md`)
  - `add-method/skill/add/run.md` (lines ~74 "Always escalates to a human … any security finding (HARD-STOP, always)" + ~121 "Security still always escalates.") — the auto-gate escalation claim. DOC EDIT: qualify "always escalates" with "only a finding the AI SURFACES; a missed one is invisible to the engine — a human spot-audit is the only backstop under `auto`". (+ 2 parity mirrors)
  - `add-method/tooling/add.py:~4957` `unescalated_security_note` (audit check) — READ-ONLY ANCHOR, no code change: it fires only when §6 carries a security NOTE/⚠ marker AND the reviewer is the auto-gate (`marked and rev and "auto-gate" in rev`). So it catches MIS-escalation (a marked note auto-passed), NEVER a finding that was never marked. The disclosure names exactly this blind spot.
Context (working folder): the skill phase guides live in 3 parity-tracked trees (canonical `add-method/skill/add/`, installed `.claude/skills/add/`, bundled `add-method/src/add_method/_bundled/skill/add/`); a doc edit must land byte-identically in all 3 (book/skill parity tests). The book chapter `docs/08-step-6-verify.md` is a sibling surface (not in scope unless the parity/lint requires it).
Honors (patterns / conventions): security is ALWAYS HARD-STOP (never weakened) · honest disclosure over false assurance (name the blind spot, don't imply total coverage) · the engine NEVER auto-passes a security finding — but it can only act on one it can SEE; present-only/measure-not-block framing (a doc disclosure, not a new gate).
Anchors the contract cites: `unescalated_security_note` (catches mis-escalation, blind to a MISSED finding) · the human spot-audit as the only backstop under `auto` · the 3 parity-tracked skill trees (`run.md`, `phases/6-verify.md`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: An HONEST disclosure, in the verify-phase guides, that the engine cannot detect a MISSED security finding — `unescalated_security_note` only catches a finding the AI SURFACED (a marked NOTE/⚠ that got auto-gated) — so under `auto` a human spot-audit (reading the code) is the only backstop for a finding never marked.
Framings weighed: doc-only disclosure in `run.md` + `phases/6-verify.md` (chosen — the gap is epistemic, not mechanical: the engine literally cannot see what was never written down) · add an engine gate forcing a human security sign-off on every task (rejected: theater — a forced checkbox still can't make the engine SEE a missed finding; it manufactures false precision) · weaken nothing, change nothing (rejected: the docs currently over-promise "security always escalates" without the "if surfaced" caveat — that is the dishonesty the audit flagged)
Must:
<must>
  - `phases/6-verify.md` (the "Security —" residue bullet) DISCLOSES: `unescalated_security_note` catches a MARKED security note (NOTE/⚠) that was auto-gated, but is BLIND to a finding the reviewer never marked — under `auto`, a human spot-audit (reading the diff/code) is the only backstop for a MISSED finding.
  - `run.md` (the auto-gate "always escalates … any security finding" claim + the "Security still always escalates" line) is QUALIFIED: the auto-gate escalates only a security finding the AI SURFACES; one it misses is invisible to the engine — so under `auto` a human spot-audit is the only backstop.
  - The disclosure ADDS the limitation; it never WEAKENS the standing guarantee — "a security finding is always HARD-STOP, never auto-passed/RISK-ACCEPTED" stays verbatim in both guides.
  - No engine code change: `unescalated_security_note` (add.py) is documented, not altered — the engine stays byte-identical.
  - The disclosure lands BYTE-IDENTICALLY in all 3 parity-tracked skill trees (canonical `add-method/skill/add/` · installed `.claude/skills/add/` · bundled `_bundled/skill/add/`), so the doc-parity test stays green.
</must>
Reject:
<reject>
  - the disclosure phrase absent from `phases/6-verify.md` (the missed-finding blind spot + spot-audit backstop) -> "missing_disclosure_verify"
  - the disclosure phrase absent from `run.md` (the "if surfaced" qualifier + spot-audit backstop) -> "missing_disclosure_run"
  - the existing "security … always HARD-STOP / always escalates" wording removed or softened -> "guarantee_weakened"
  - the disclosure present in canonical but not byte-identical in a mirror tree -> "skill_tree_drift" (the existing parity test)
</reject>
After:
<after>
  - a grep for the disclosure (the missed-finding blind spot + "spot-audit") succeeds in BOTH `run.md` and `phases/6-verify.md`, in all 3 skill trees; the security-always-HARD-STOP wording is still present in both; `add.py` is byte-identical (ENGINE_MD5 unchanged — a doc-only task).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the parity test that guards `run.md`/`phases/6-verify.md` across the 3 skill trees — I must confirm WHICH test (test_book_parity / test_bundle_parity / a skill-parity suite) so the build propagates to exactly the files it checks; lowest confidence because I have not yet read the parity assertion; if wrong: the build edits canonical only and reddens the parity test (cost: a propagation fix-up in build). Confirm in TESTS.
  - [ ] the added wording won't trip a wording-lint or a lean-fence byte budget on the skill tree — confirm by running the suite after the edit; if wrong: reword to fit.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: 6-verify.md discloses the missed-finding blind spot
  Given the verify phase guide phases/6-verify.md
  When I read the "Security —" residue bullet
  Then it states unescalated_security_note catches a MARKED note but is blind to a MISSED finding
  And it names a human spot-audit as the only backstop under auto
  And the "a security finding is always HARD-STOP" wording is still present unchanged

Scenario: run.md qualifies the auto-gate "always escalates" claim
  Given run.md's auto-gate section
  When I read the "always escalates … any security finding" claim
  Then it is qualified — the auto-gate escalates only a finding the AI SURFACES; a missed one is invisible
  And it names a human spot-audit as the only backstop under auto
  And the "Security still always escalates" / HARD-STOP guarantee wording is still present unchanged

Scenario: the disclosure is byte-identical across all 3 skill trees
  Given the disclosure added to canonical add-method/skill/add/{run.md,phases/6-verify.md}
  When the skill-parity test runs
  Then the installed (.claude/skills/add) and bundled (_bundled/skill/add) copies are byte-identical
  And no tree carries the disclosure while another lacks it

Scenario: the task is doc-only — the engine is untouched
  Given this is a disclosure task with no code change
  When the build completes
  Then add.py is byte-identical (ENGINE_MD5 unchanged) and unescalated_security_note is unaltered

Scenario: rejection — a removed/softened guarantee is caught
  Given a (hypothetical) edit that deletes or softens "security … always HARD-STOP"
  When the disclosure test runs
  Then it fails "guarantee_weakened" (the standing guarantee wording must remain verbatim)

Scenario: rejection — a missing disclosure is caught
  Given run.md or phases/6-verify.md without the missed-finding + spot-audit disclosure
  When the disclosure test greps that guide
  Then it fails "missing_disclosure_run" / "missing_disclosure_verify" respectively
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC-ONLY DISCLOSURE CONTRACT — no API, no engine change. The "shape" is the set of claims each
guide MUST carry + the invariants the test asserts. test_security_escalation_disclosure.py greps
the 3 skill trees.

phases/6-verify.md  (the "Security —" residue bullet)
  MUST add, near the unescalated_security_note mention, a disclosure containing BOTH:
    - the blind spot: unescalated_security_note only catches a MARKED note (NOTE/⚠) that was
      auto-gated; a finding the reviewer never marked is INVISIBLE to the engine
    - the backstop: under `auto`, a human spot-audit (reading the diff/code) is the only backstop
  MUST keep verbatim: "a security finding is always `HARD-STOP`" (the standing guarantee)

run.md  (the auto-gate escalation section, ~"any security finding (HARD-STOP, always)" + ~"Security
         still always escalates")
  MUST add a qualifier containing BOTH:
    - the "if surfaced" caveat: the auto-gate escalates only a security finding the AI SURFACES;
      one it misses is invisible to the engine
    - the backstop: under `auto`, a human spot-audit is the only backstop for a missed finding
  MUST keep verbatim: "Security still always escalates" + the HARD-STOP guarantee

Test anchors (grep, case-insensitive), present in BOTH guides across ALL 3 trees:
  - a missed/invisible-finding phrase   (e.g. "cannot detect a MISSED" / "never marked … invisible")
  - "spot-audit"  (the named human backstop)
Invariants the test also asserts:
  - the guarantee wording "always HARD-STOP" still present in BOTH guides   (guarantee_weakened)
  - md5(add.py) == engine_pin.ENGINE_MD5 unchanged   (doc-only; no engine edit)
  - the 3 skill trees stay byte-identical for run.md + phases/6-verify.md   (existing parity test)

Reject codes (test assertion labels): missing_disclosure_verify · missing_disclosure_run ·
  guarantee_weakened · skill_tree_drift
Schema: NONE — markdown doc edits only; no state.json / no engine symbol change.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [test] the exact GREP ANCHOR strings — the test must pin a phrase stable enough to survive light copy-editing yet specific enough that a missing disclosure fails. I'll anchor on a coined, unlikely-to-pre-exist token ("spot-audit") + a "missed"/"invisible" phrase, asserted case-insensitively in both guides across all 3 trees; cost if wrong: a brittle test that reddens on a reword (fix: loosen to the stable token). Sibling risk: the parity test's identity — confirmed in TESTS before the build edits anything.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: presence (doc-grep) — 5 assertions over 6 scenarios; not a % (markdown, no executable lines).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_verify_guide_discloses_missed_finding: each tree's phases/6-verify.md / assert `spot-audit` + a missed/invisible phrase (missing_disclosure_verify)
  - test_run_guide_qualifies_always_escalates: each tree's run.md / assert `spot-audit` + a surfaces/missed/invisible phrase (missing_disclosure_run)
  - test_guarantee_not_weakened: assert "always `HARD-STOP`" (6-verify) + "Security still always escalates" (run.md) still present in all 3 trees (guarantee_weakened)
  - test_skill_trees_byte_identical_for_both_guides: md5 of run.md + phases/6-verify.md equal across the 3 trees (skill_tree_drift)
  - test_engine_untouched: md5(add.py) == engine_pin.ENGINE_MD5 (doc-only; engine byte-identical)
</test_plan>

Tests live in: `add-method/tooling/test_security_escalation_disclosure.py` · RED now (2 disclosure fails, 3 guards green) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/` `.claude/skills/add/` `add-method/src/add_method/_bundled/skill/add/` `add-method/tooling/`
Strategy (ordered batches): 1. edit canonical run.md + phases/6-verify.md (append the disclosure; keep the guarantee verbatim) → 2. propagate byte-identically to the installed + bundled mirrors → 3. rebaseline test_skill_lean.py (orchestration pool for run.md, phases pool for 6-verify.md — `baseline += ⌈added÷ratio⌉`, ratios kept; tree budget flows via sum) → 4. run the suite green.
Safety rule (feature-specific): the disclosure ADDS to the security bullet/auto line — it never removes or softens the standing "always HARD-STOP / Security still always escalates" guarantee; no engine (add.py) byte changes.
Code lives in: the 3 skill trees (markdown) + test_skill_lean.py (rebaseline).
Constraints: do NOT change any test or the contract; no new packages; the 3 trees stay byte-identical.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2089/0; new test_security_escalation_disclosure 5/5
- [x] coverage did not decrease — N/A (doc-only, no executable lines); presence-tested by grep
- [x] no test or contract was altered during build — the tighten edit was made in TESTS then re-crossed tests→build (tripwire re-baselined); §3 contract untouched (FROZEN @ v1)
- [x] the green was EARNED, not gamed — independent refute-read (agent a4e02332) VERDICT **EARNED**: engine claim verified precise (the `marked` boolean gates `unescalated_security_note`, so a never-marked finding is genuinely invisible), prose non-hollow, guarantee verbatim-intact; its disclosed test-rigor nit (vacuous `invisible` branch) was CLOSED before this gate (re-anchored on `never marked|wrote down`)
- [x] concurrency / timing — N/A (markdown doc edit; no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — the change DOCUMENTS a security limitation; it introduces no finding/vuln/dependency (no engine byte change)
- [x] layering & dependencies follow CONVENTIONS.md — doc-only; 3 skill trees kept byte-identical
- [x] a person reviewed and approved the change — Tin Dang reviewed the gate evidence + refute verdict and chose "Tighten test, then PASS"

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] both verify guides name the missed-finding blind spot + a `spot-audit` backstop — `spot-audit` grep-present 1× in run.md + 1× in phases/6-verify.md across all 3 trees
- [x] the standing guarantee survives — "always `HARD-STOP`" (6-verify) + "Security still always escalates" (run.md) still grep-present in all 3 trees (test_guarantee_not_weakened green)
- [x] the disclosure is byte-identical across the 3 skill trees — md5 run.md=2fad9c05…, 6-verify.md=01f193ab… single-valued across canonical/installed/bundled (test_skill_trees_byte_identical green)
- [x] the engine is untouched — md5(add.py)=7e05d07c… == engine_pin.ENGINE_MD5; full suite 2089/0 after the lean-fence rebaseline (orchestration 51732→51994, phases 39008→39446, ratios kept)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read BOTH guides' security sections in full (the test failure dumped them verbatim) + the `unescalated_security_note` source (add.py ~4957). Confirmed: (1) the disclosure accurately states the engine blind spot — `marked and rev and "auto-gate"` only fires on a MARKED note, so a never-marked finding escapes; (2) the standing "always HARD-STOP / Security still always escalates" guarantee is qualified, never removed; (3) the 3 trees are byte-identical; (4) add.py is byte-unchanged. No new symbols (doc-only) → WIRING/DEAD-CODE N/A.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a future skill-guide reword that drops the `spot-audit` token (or the "never marked / wrote down" blind-spot phrase) re-reddens test_security_escalation_disclosure — the disclosure is now a pinned invariant.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] sync the same missed-finding disclosure into the BOOK chapter `docs/08-step-6-verify.md` (+ `.add/docs/` + `_bundled/docs/`) — the skill guides now disclose the blind spot but the book chapter still presents `unescalated_security_note` without the "blind to a never-marked finding" caveat (evidence: this task scoped the book out; skill↔book drift on the security-escalation claim)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] when the engine's enforcement has an EPISTEMIC blind spot (it cannot see what was never written down), DISCLOSE the limitation in the guide rather than fake a gate that manufactures false precision — measure-not-block honesty (evidence: `unescalated_security_note` catches mis-escalation but is structurally blind to a missed finding; a forced human-signoff checkbox would not change that)
- [TDD · open] a presence/format test must anchor on a DISCLOSURE-UNIQUE token, not a common word — bare "invisible" was vacuously satisfied by unrelated prose (line 40); "spot-audit"/"never marked" uniquely gate the disclosure (evidence: refute-read caught the vacuous branch; closed before the gate by re-anchoring)
