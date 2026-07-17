# TASK: §5 BUILD declares its scope of impact — Scope allowlist + Strategy batches, frozen with the bundle

slug: scope-decl-template · created: 2026-06-12 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): VERIFIED 2026-06-12 — `add-method/tooling/templates/TASK.md.tmpl` §5 (lines 105–115: `Safety rule (feature-specific):` · `Code lives in:` · `Constraints:` plain lines + the EXIT comment; the template set is mirrored ×3 — canonical · `_bundled/tooling/templates/` · `.add/tooling/templates/` — byte-identical today, md5 c6f75f8f08b124a15f23e1bf64165782). `add-method/skill/add/phases/5-build.md` (×3 mirrors with `_bundled/skill/add/` + `.claude/skills/add/`; sections: small-batches · cardinal-rule · AI-prompt · exit-gate — no Scope/Strategy prose anywhere today). The grammar PRECEDENT: `_declared_test_files` (add.py:1911) parses the §4 `Tests live in:` line — backticked tokens on the FIRST declaring line · `./…` → task dir · token with `/` → project root · bare name → sibling of previous · directory → its `*.py` non-recursive · v2 confinement: everything must resolve inside the project root, fail-closed drop. Section reader: `_raw_phase_bodies(root, slug)` keyed by §-number — **NO consumer of `.get(5)` exists today** (§5 is parse-greenfield). The future enforcement seam (NEXT task, not this one): `_tripwire_snapshot` (add.py:1990) at the tests→build advance.
Context (working folder): `.add/milestones/build-scope-lock/MILESTONE.md` (this task owns the freeze-first contract: "the §5 Scope/Strategy declaration grammar — parseable by the engine, writable by any agent"). Direct ANALOG task: `archive/v13-1/tasks/declare-grammar-doc/TASK.md` — same shape for §4 (template comment line + a guide section, ×3 byte-identical, `add.py untouched (md5 ×3 unchanged)`, prose-only). Guard suites that constrain this change: `test_template_form_tags.py` (v18 form-tag parse seams on TASK.md.tmpl) · `test_xml_convention.py` (v16 FROZEN closed tag vocab — adding a NEW XML tag is an amendment, not a drive-by; plain declaring lines avoid it) · `test_bundle_parity.py` (×3 byte parity incl. templates) · `test_declare_grammar_doc.py` (the §4 precedent suite to mirror in shape).
Honors (patterns / conventions): the §4 declaring-line idiom — a PLAIN `<label>:` line with backticked path tokens, grammar documented in an adjacent template comment (NOT a new XML tag — the v16 vocab is frozen); token-presence + ×N-mirror-parity as the honest test shape for prose-discipline changes (fv28); Scope/Strategy join the SPECIFICATION BUNDLE — one approval at the §3 freeze, no new gate (milestone shared decision); the engine stays tool-agnostic (the grammar must be parseable from bytes, no git — constraint inherited by the NEXT task's parser); enforcement-deferral named explicitly at freeze (fv28 — this task ships grammar + prose, the gate enforcement is scope-gate-enforce: words-exist≠method-works applies until then and must be SAID).
Anchors the contract cites: `templates/TASK.md.tmpl` §5 block (×3) · `phases/5-build.md` (×3) · the `Tests live in:` grammar at `_declared_test_files` (add.py:1911 — cited as the resolution-rule source the Scope grammar reuses verbatim) · `_raw_phase_bodies` §-keyed reader · `test_bundle_parity.py` / `test_template_form_tags.py` / `test_xml_convention.py` guard names · `engine_pin.ENGINE_MD5` (cited as UNCHANGED — prose/template-only task).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §5 BUILD declares its scope of impact — a `Scope (may touch):` file-touch allowlist line + a `Strategy (ordered batches):` plan line in TASK.md.tmpl, drafted with the specification bundle and frozen at the §3 contract freeze; the phase guides teach the discipline. This task ships the GRAMMAR + the prose; the engine gate (touched ⊆ declared) is the NEXT task (scope-gate-enforce) — the enforcement-deferral is named explicitly, per the fv28 convention.
Framings weighed: plain declaring lines mirroring the §4 `Tests live in:` idiom (chosen — same grammar family, no vocab amendment, template-comment carrier precedent from declare-grammar-doc) · a new `<scope>` XML form tag (rejected — the v16 tag vocab is FROZEN; an amendment is its own task, not a drive-by) · declaring scope in §3 CONTRACT (rejected — §3 freezes the external shape; the scope of impact is build mechanics and §5 is its home, where the milestone placed it)
Must:
<must>
  - TASK.md.tmpl §5 gains TWO placeholder lines ABOVE the existing ones (which stay byte-identical): `Scope (may touch): <backticked path tokens — every file the build may write>` and `Strategy (ordered batches): <1. … 2. … — the planned build order>`, plus the grammar FOLDED into the existing §5 EXIT comment (the lean-pass guard pins the template's total comment count under 12 — no new comment open)
  - the Scope grammar := the §4 `Tests live in:` resolution rules (FIRST declaring line · backticked tokens · `./…` → task dir · token with `/` → project root · bare name → sibling of the previous token · outside-root resolution dropped fail-closed) with ONE NAMED divergence: a directory token covers its WHOLE SUBTREE (containment semantics — enforcement needs prefix cover, not the §4 non-recursive `*.py` counting)
  - declare-at-bundle, freeze-at-contract: the template placeholder text and the guides say Scope/Strategy are FILLED with the bundle and FROZEN by the one §3 approval — never invented mid-build
  - phases/5-build.md (×3) gains a "Declaring the scope of impact" section (the v17 rubric's enforced vocabulary — `blast radius` is banned on the live surface): the grammar, the honor-it rule during build (touching an undeclared file = stop, change-request — not improvise), and the explicit deferral line (engine enforcement lands in scope-gate-enforce; until then this is prose discipline — words-exist≠method-works)
  - phases/5-build.md exit gate gains one line: no file outside the declared Scope was touched
  - phases/3-contract.md (×3) gains ONE line at the freeze: the approval also freezes §5 Scope/Strategy (the bundle covers them)
  - both artifacts stay byte-identical across their ×3 trees; `add.py` untouched — `engine_pin.ENGINE_MD5` unchanged; NO new XML tag anywhere
  - existing TASK.md files (no Scope line) stay valid: absence means UNDECLARED — the future parser grandfathers, never retro-reds
</must>
Reject:
<reject>
  - a new XML tag as the scope carrier -> rejected at specify (v16 frozen vocab; plain lines chosen)
  - an absent Scope line in a pre-existing task treated as a violation -> never: absence = undeclared, grandfathered (the NEXT task's parser must honor this)
  - a Scope token resolving outside the project root -> dropped fail-closed by the grammar (inherited from the §4 confinement rules)
  - teaching the discipline without naming the deferral -> rejected: the guide MUST say enforcement is the next task (prose-only until then)
</reject>
After:
<after>
  - a fresh `add.py new-task` scaffold carries the Scope/Strategy placeholder lines + grammar comment in §5; the build and contract guides teach declare-at-bundle/freeze-at-contract/honor-or-change-request; the grammar is frozen and citable by scope-gate-enforce; all ×3 trees identical; the engine is byte-unchanged
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the subtree divergence (a directory token covers its whole subtree) is the right containment semantics for the FUTURE gate — lowest confidence because the consumer (scope-gate-enforce) is not yet specified; if wrong (it wants exact-file sets or §4's non-recursive rule), the grammar re-freezes via change-request before any parser exists — cost: one cheap re-freeze, zero code rework (that is exactly why the grammar task ships first).
  ⚠ the declare-teaching placement (5-build.md + one 3-contract.md line) reaches the BUNDLE drafter — because the drafter works from 1-specify→4-tests and might never open 5-build.md before the freeze; if wrong: scope lines stay template placeholders at freeze; mitigated by the template placeholder text itself saying "fill before the §3 freeze" — the artifact teaches at the point of use.
  - [x] additive beside `Code lives in:` (never replacing it) is right — the settled additive-surfaces convention (PROJECT.md §Spec, orphan-task-guard v8-1) and the declare-grammar-doc precedent both keep existing lines byte-identical.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a fresh scaffold carries the scope-of-impact placeholders
  Given a sandbox project initialized from the shipped template set
  When add.py new-task scaffolds a TASK.md
  Then §5 contains the "Scope (may touch):" and "Strategy (ordered batches):" lines ABOVE the existing lines
  And the existing Safety-rule / Code-lives-in / Constraints lines are byte-identical to today's

Scenario: the grammar comment states the rules and the named divergence
  Given the shipped TASK.md.tmpl
  When the §5 grammar comment is read
  Then it names: backticked tokens · ./ = task dir · "/" = project root · bare = sibling · outside-root dropped fail-closed · a DIRECTORY token covers its whole subtree · absence = undeclared (grandfathered) · enforcement lands in scope-gate-enforce

Scenario: the build guide teaches the discipline with the deferral said
  Given phases/5-build.md
  When the guide is read
  Then a "Declaring the scope of impact" section names declare-at-bundle, freeze-at-contract, and touch-outside-Scope = stop -> change-request
  And the section says engine enforcement is scope-gate-enforce (prose discipline until then)
  And the exit gate carries the no-file-outside-declared-Scope line

Scenario: the contract guide names the freeze coverage
  Given phases/3-contract.md
  When the freeze prose is read
  Then one line says the §3 approval also freezes §5 Scope and Strategy

Scenario: mirrors hold and the engine is untouched
  Given the build is complete
  When the parity and pin guards run
  Then TASK.md.tmpl and both touched guides are byte-identical across their x3 trees
  And md5(add.py) still equals engine_pin.ENGINE_MD5 (x3 — no engine change)
  And the template's XML tag census is UNCHANGED (no new tag)

Scenario: pre-existing tasks are grandfathered (regression)
  Given a TASK.md scaffolded before this change (no Scope line)
  When the shipped prose and template are read
  Then absence is defined as UNDECLARED — nothing marks the old task invalid, and no deliverable of this task asks the future parser to retro-red it
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TASK.md.tmpl §5 — ABOVE the existing lines (which stay byte-identical), add:
  Scope (may touch): `./src/`   <fill before the §3 freeze — every file the build may write>
  Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features>

FOLD the grammar into the existing §5 EXIT comment (v2 — the lean-pass guard pins
the template's total `<!--` count under 12; the §4-comment carrier text, one open):
  <!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
       with "/" = project root · a bare name = sibling of the previous token's dir ·
       outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
       whole subtree (containment — diverges from §4's non-recursive counting) ·
       absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
       engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
       EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

phases/5-build.md — new section "## Declaring the scope of impact (Scope + Strategy)"
  (v2 — the v17 rubric's enforced replacement; `blast radius` is banned surface-wide)
  between "## Work in small batches" and "## The cardinal rule": ~10 lines — Scope/
  Strategy are drafted WITH the bundle and frozen by the one §3 approval; during build,
  needing a file outside the declared Scope is a STOP -> change request back to Specify,
  never improvisation; Strategy is the ordered plan (guidance, not enforced); the
  deferral NAMED: the engine gate is the scope-gate-enforce task — until it ships this
  section is prose discipline.
  Exit gate gains ONE line: "- [ ] No file outside the declared §5 Scope was touched."

phases/3-contract.md — ONE line in the freeze prose: the §3 approval also freezes the
  §5 Scope (may touch) + Strategy declarations (the bundle covers them).

Sync: TASK.md.tmpl + 5-build.md + 3-contract.md each byte-identical across their ×3
trees (templates: canonical/_bundled/.add — guides: skill/_bundled/.claude) ·
add.py UNTOUCHED (engine_pin.ENGINE_MD5 unchanged ×3) · NO new XML tag (v16 vocab
frozen; census unchanged) · prose/template-only task. The grammar above is the frozen
citable contract for scope-gate-enforce's parser.
```

Status: FROZEN @ v2 — approved by Tin Dang (2026-06-12, in-chat change-request approval: heading → "scope of impact" per the v17 enforced rubric row + grammar folded into the §5 EXIT comment per the lean-pass budget; v1 approved same day — whole-subtree divergence + grandfather semantics accepted with the two flags surfaced).
Least-sure flag surfaced at freeze: ⚠ [contract] the subtree divergence (a directory token covers its WHOLE subtree, not §4's non-recursive counting) is chosen BEFORE its consumer exists — scope-gate-enforce is not yet specified; if wrong: the grammar re-freezes via a cheap change-request with zero code rework (the reason the grammar task ships first). ⚠ [spec] the declare-teaching lives in 5-build.md + one 3-contract.md line, but the BUNDLE drafter works §1→§4 and may never open 5-build.md pre-freeze; if wrong: Scope lines stay placeholders at freeze; mitigated at the point of use — the template placeholder itself says "fill before the §3 freeze".
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 6 scenarios pinned; suite-level count not decreased (865-test baseline stays green). RED drivers: every token-presence test fails today (no Scope/Strategy text exists anywhere); the parity/pin test is a GREEN pin at write (declared honestly — it pins the ×3 trees and the untouched engine, the declare-grammar-doc suite shape).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_scaffold_carries_scope_of_impact_lines: sandbox init + new-task / read §5 of the scaffolded TASK.md / assert "Scope (may touch):" and "Strategy (ordered batches):" present ABOVE "Safety rule" + the three existing lines byte-identical to today's text
  - test_template_grammar_comment: read TASK.md.tmpl §5 region / assert comment tokens: "whole subtree" · "UNDECLARED" · "grandfathered" · "scope-gate-enforce" · "fail-closed"
  - test_build_guide_scope_of_impact_section: read 5-build.md / assert "Declaring the scope of impact" heading + "change request" + "scope-gate-enforce" tokens / assert exit gate carries the no-undeclared-touch line
  - test_contract_guide_freeze_line: read 3-contract.md / assert the freeze prose names §5 Scope + Strategy as covered by the approval
  - test_mirrors_and_engine_untouched: md5 equality ×3 for TASK.md.tmpl + 5-build.md + 3-contract.md / md5(add.py) == engine_pin.ENGINE_MD5 ×3 / template XML tag census UNCHANGED vs the literal frozen set (no new tag)
  - test_grandfather_is_prose_not_retro_red: the template comment + guide section define absence = UNDECLARED; assert the tokens appear with the grandfather meaning (render-blind: vocabulary, not layout)
</test_plan>

Tests live in: `add-method/tooling/test_scope_decl_template.py` · MUST run red (missing prose) before Build.
Red run (2026-06-12): `Ran 6 tests · FAILED (failures=5)` — scaffold/grammar-comment/build-guide/contract-guide/grandfather all fail on missing prose tokens (AssertionError "… not found in …", never an import error); mirrors/engine pin GREEN as declared.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the change is ADDITIVE — the three existing §5 template lines stay byte-identical, the v16 tag census stays frozen, and add.py is never written (ENGINE_MD5 unchanged; a diverged trio is a build failure, not a re-pin).
Code lives in: `add-method/tooling/templates/TASK.md.tmpl` · `add-method/skill/add/phases/5-build.md` · `add-method/skill/add/phases/3-contract.md` — each synced byte-identical ×3 (canonical · `_bundled` · dogfood).
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib-only — no new dependency); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — task suite 6/6 (incl. the strengthened Scope<Strategy<Safety ordering asserts); full suite 871/871 OK on python3.14.5 AND python3.10.20
- [x] coverage did not decrease — suite count 865 → 871 (+6); zero failures
- [x] no test or contract was altered during build — the v2 change-request (heading wording + comment fold, human-approved) and the refute-disclosed gap-close each re-armed the tripwire via phase tests→build; `add.py check` clean (262/0, no build_tampered)
- [x] the green was EARNED, not gamed — adversarial refute-read subagent: verdict EARNED; all 23 §3 clauses mapped to enforcing asserts; per-test wrong-build analysis found no pass-while-wrong path; the one disclosed coverage gap (Strategy ordering unasserted) was closed BEFORE the gate
- [x] concurrency / timing — n/a: prose/template-only, no runtime code path touched
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; stdlib-only suite; no new package
- [x] layering & dependencies follow CONVENTIONS.md — declaring-line idiom mirrors §4 (fv28 token-presence + ×N-mirror-parity shape); engine pin unchanged ×3; v16 tag census frozen (20 tags); lean-pass comment budget held at 11
- [x] a person reviewed and approved the change — Tin Dang approved the freeze (v1 + v2 change-request) and both routing decisions in-chat; gate auto-resolves under `autonomy: auto`

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no new code symbol; the template lines are consumed by the `new-task` scaffold path, exercised end-to-end by test_scaffold_carries_scope_of_impact_lines (sandbox init+lock+new-task)
- [x] DEAD-CODE (code) — n/a: no symbol introduced; add.py byte-identical to engine_pin.ENGINE_MD5 ×3
- [x] SEMANTIC (prose / non-code) — read in full by the refute subagent + spot-read by the orchestrator: TASK.md.tmpl §5 (both lines above the existing trio · grammar folded into the EXIT comment with all 7 rules incl. whole-subtree + grandfather) · 5-build.md (section placed small-batches→cardinal-rule; declare-at-bundle/freeze-at-§3/stop→change-request; deferral NAMED scope-gate-enforce; exit-gate line present) · 3-contract.md (one freeze-coverage line); no banned idiom on any shipped surface

### GATE RECORD
Outcome: PASS
Auto-resolved under `autonomy: auto` — complete evidence (red→green run, ×2-interpreter full suite, EARNED refute verdict, tripwire clean), no security finding, no residue.
Reviewed by: refute subagent (EARNED) + auto-gate; freeze + change-request approvals by Tin Dang · date: 2026-06-12

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether fresh TASK.md bundles arrive at the §3 freeze with Scope/Strategy FILLED (not placeholders) — the ⚠ [spec] flag's failure mode; first real signal lands when the next task's bundle is drafted.
Spec delta for the next loop: scope-gate-enforce consumes THIS frozen grammar verbatim — whole-subtree containment, fail-closed outside-root drop, and absent=UNDECLARED grandfather are its contract inputs, already citable from §3 v2.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [SDD · folded] §0 GROUND for a prose-surface task must sweep the WORDING guards (WORDING_RUBRIC.md + ubiquitous-language/wording-lint/rewrite suites), not just the structural ones — the frozen §3 named a banned idiom and a comment-budget breach the ground map never surfaced (evidence: 5 guard failures at the first full discover; v2 change-request approved 2026-06-12)
- [ADD · folded] a human-approved mid-build change-request still trips the tamper tripwire; the honest re-arm is phase tests→advance after the bundle edits — worth one line in run.md so agents don't read build_tampered as a cheat signal (evidence: add.py check build_tampered after the v2 re-freeze, cleared by re-advance)
- [TDD · folded] when a frozen §4 plan says "both lines above X", write BOTH ordering asserts — the refute-read caught Strategy's position unasserted while the plan claimed it (evidence: refute subagent coverage-gap finding; assert added before the gate)
- [ADD · folded] sibling-session commits landing on the shared branch mid-task can redden unrelated guards; the full-suite-before-gate rule caught and routed it instead of letting the gate record over it (evidence: helios commits 37ce66a..7f778be → 3 guard reds; fix commit 30153a1)
