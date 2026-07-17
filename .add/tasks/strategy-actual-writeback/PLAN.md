# TASK: §5 records the AI's actual build strategy (Strategy actually used) — closes the report→§5 loop

slug: strategy-actual-writeback · created: 2026-06-28 · stage: mvp
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
  - `add-method/tooling/templates/TASK.md.tmpl` §5 — ADD a "Strategy actually used:" field after "Known-problem fixes:" (filled at VERIFY/OBSERVE; the [AI] build decision the §7 ADR harvest reads). Inline hint: "(fill at verify — what you ACTUALLY did, or 'as planned'; harvested into §7 Decisions)"
  - `add-method/tooling/templates/TASK.fast.md.tmpl` §5 — ADD the same "Strategy actually used:" field after "Strategy & known-problem fixes:" (fast tasks produce an ADR too)
  - 3-tree parity: also `.add/tooling/templates/…` + `add-method/src/add_method/_bundled/tooling/templates/…` (6 template files total)
  - `add-method/tooling/test_scope_decl_template.py` — ADD: both templates carry the new field; the scaffolded TASK.md/TASK.fast.md carry it
Context (working folder): milestone adr-at-observe (this is task 1/3); the field is the INPUT CONTRACT the harvest (task 2 `adr-harvest`) reads as the [AI] build decision; it closes the report→§5 loop seeded by strategy-soft-not-hard
Honors (patterns / conventions): template/skill-only ⇒ `add.py` + `add_engine/*.py` UNTOUCHED (ENGINE_MD5 / ENGINE_PKG_MD5 unchanged); 3-tree byte parity; the field label is a STABLE harvest key (frozen here, adr-harvest depends on it); additive — no existing §5 line changes
Anchors the contract cites: `§5 "Strategy actually used:"` field label (both templates) · 6-file 3-tree parity · `test_scope_decl_template`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §5 gains a "Strategy actually used:" field — the AI records the strategy it REALLY used at verify, so the §7 ADR harvest (task 2) has the [AI] build decision and the report→§5 loop closes
Framings weighed: §5-field-next-to-planned-strategy (chosen — planned vs actual sit together; §5 is the build/strategy home) · §7-observe-field (rejected: splits planned/actual across sections, harder to compare) · no-field-harvest-from-prose (rejected: the harvest needs a stable parseable key)
Must:
<must>
  - `TASK.md.tmpl` §5 gains a "Strategy actually used:" line after "Known-problem fixes:", with an inline hint that it is filled at VERIFY (what was ACTUALLY done, or "as planned") and harvested into the §7 Decisions block
  - `TASK.fast.md.tmpl` §5 gains the same "Strategy actually used:" line after "Strategy & known-problem fixes:"
  - the field label is byte-identical in both templates and a STABLE key the harvest can grep ("Strategy actually used:")
  - all 6 template files (canonical · _bundled · dogfood, ×2 templates) stay byte-identical per template
  - additive only: no existing §5 line (Scope · Strategy · Known-problem fixes · Safety · Constraints) changes
  - template-only: `add.py` + `add_engine/*.py` UNTOUCHED ⇒ ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
</must>
Reject:
<reject>
  - the field label drifts between the two templates -> "label_drift" (harvest key must be one string)
  - an existing §5 planned line is altered/removed -> "section5_regression"
  - one template tree edited but not all three -> "parity_break"
  - `add.py` / `add_engine/*.py` edited -> "engine_touched"
</reject>
After:
<after>
  - every newly-scaffolded task (full + fast) carries a §5 "Strategy actually used:" field ready to record the AI's real build strategy — the stable input the adr-harvest task reads as the [AI] decision
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that §5 (not §7) is the right home — lowest confidence because the value is known only POST-build while §5 is otherwise pre-build-planned; mitigated: §5 is the strategy home and planned-vs-actual adjacency aids the audit, and the inline hint marks it "fill at verify"; if wrong: task 2's harvest reads the wrong section — cheap to repoint — THIS is the freeze flag
  - [ ] the fast lane should carry the field too (vs staying minimal) — chosen: a fast task still produces an ADR, so consistency wins; the one extra line is negligible
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the full template §5 carries a "Strategy actually used:" field
  Given add-method/tooling/templates/TASK.md.tmpl
  When I read §5
  Then a "Strategy actually used:" line appears after "Known-problem fixes:"
  And the four pre-existing §5 lines (Scope · Strategy · Known-problem fixes · Safety) are unchanged

Scenario: the fast template §5 carries the same field
  Given add-method/tooling/templates/TASK.fast.md.tmpl
  When I read §5
  Then a "Strategy actually used:" line appears after "Strategy & known-problem fixes:"

Scenario: the field label is one stable harvest key
  Given both templates
  When I extract the "Strategy actually used:" label from each
  Then the two labels are byte-identical

Scenario: a freshly scaffolded task carries the field
  Given a new task scaffolded from the full template (and a fast task from the fast template)
  When I read the produced §5
  Then it contains "Strategy actually used:"

Scenario: six template files stay byte-identical per template
  Given the canonical / _bundled / dogfood copies of each template
  When I md5 each template's trio
  Then each is a single digest

Scenario: template-only — engine untouched
  Given add.py and add_engine/*.py
  When I digest them
  Then ENGINE_MD5 and ENGINE_PKG_MD5 are unchanged

Scenario: reject a label drift between templates
  Given the harvest needs one label string
  When the two templates use different "actually used" labels
  Then the label-identity assertion fails -> "label_drift"
  And neither variant ships

Scenario: reject a regression of an existing §5 line
  Given the four planned §5 lines must remain
  When any is altered or removed
  Then the §5-preserve assertion fails -> "section5_regression"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: a §5 "Strategy actually used:" field on both task templates (full + fast) — additive,
byte-identical label, filled at VERIFY, harvested into the §7 Decisions (ADR) block by task 2.

FROZEN — full template (TASK.md.tmpl §5), inserted AFTER "Known-problem fixes:" / BEFORE "Safety rule":
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>

FROZEN — fast template (TASK.fast.md.tmpl §5), inserted AFTER "Strategy & known-problem fixes:":
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>

STABLE HARVEST KEY (byte-identical in both templates): "Strategy actually used:"

INVARIANTS:
INV-1  the label "Strategy actually used:" is byte-identical in both templates
INV-2  additive — the planned §5 lines (Scope · Strategy (ordered batches) · Known-problem fixes · Safety rule) are unchanged
INV-3  each template byte-identical across canonical / _bundled / dogfood (6 files, 2 trios)
INV-4  a freshly scaffolded full AND fast task carries the field
INV-5  add.py + add_engine/*.py untouched -> ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
error codes: label_drift · section5_regression · parity_break · engine_touched
```

Least-sure flag surfaced at freeze: [contract] §5 (not §7) as the field's home — the value is known only post-build, so a reviewer might expect it in §7 OBSERVE; chosen §5 for planned-vs-actual adjacency + the "fill at verify" hint, and task 2's harvest will read whichever section this freezes. Cheap to repoint if wrong. No engine risk (template-only).
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/templates/TASK.fast.md.tmpl` `.add/tooling/templates/TASK.md.tmpl` `.add/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/test_scope_decl_template.py`
Strategy (ordered batches): 1. TESTS — add to test_scope_decl_template: both templates carry "Strategy actually used:", labels identical, scaffold carries it (red). 2. BUILD — edit canonical TASK.md.tmpl (after Known-problem fixes) + TASK.fast.md.tmpl (after Strategy & known-problem fixes), then cp each canonical → its 2 mirrors. 3. Verify each template's trio is one md5 + suite green.
Known-problem fixes: scaffold test reads the engine's template-resolution path not the canonical → assert against the resolved scaffold output, not a hand-read file · forgetting a mirror → cp from canonical + md5 the trio · a tmpl placeholder `<...>` containing `:` confusing the label grep → grep the literal "Strategy actually used:" prefix only
Safety rule (feature-specific): edit the canonical template, then cp to BOTH mirrors in the same batch — never hand-type a mirror (keeps each template's 3-tree md5 single)
Code lives in: the 6 template files above
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 2115/0; check 469/0
- [x] coverage did not decrease — +4 template assertions (full/fast field, label-identity, scaffold ×2); none removed
- [x] no test or contract was altered during build — test edits in the TESTS phase; build touched only the 6 template copies (git status confirms)
- [x] the green was EARNED, not gamed — refute-read: the 4 new tests proved RED (label absent in templates + scaffold), then GREEN after the additive edit; the placement asserts Known-fix < actually-used < Safety, and EXISTING_LINES guards the 4 planned lines
- [x] concurrency / timing of the risky operation is safe — N/A: static template prose
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: no code/deps
- [x] layering & dependencies follow CONVENTIONS.md — additive §5 line; mirrors the Known-problem-fixes field pattern
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze @ v1 (milestone adr-at-observe confirmed); auto-gated on complete evidence

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] both templates' §5 carry "Strategy actually used:" in the right slot — confirmed: full has Known-fix < actually-used < Safety; fast has it after the strategy line
- [x] the label is one stable harvest key — confirmed: byte-identical "Strategy actually used:" in both templates (label-identity test green)
- [x] a fresh scaffold (full + fast) carries the field — confirmed by the scaffold test (init→new-task→read §5)
- [x] no cost elsewhere — confirmed: engine pins unchanged (no add.py/add_engine in git status); each template's 3-tree md5 = 1; 4 planned §5 lines intact

### Deep checks
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the new line reads as a post-build field ("fill at VERIFY … or 'as planned'"), names its harvest destination (§7 Decisions / [AI] decision), and is additive — the planned Strategy/Known-fix/Safety lines are untouched; this is the input contract task 2 (adr-harvest) will read

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the label drifting between templates (label_drift); a future template edit dropping the field

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] adr-harvest renders the §7 Decisions (ADR) block, reading this §5 "Strategy actually used:" field as the [AI] build decision (evidence: this task froze the field as the harvest's input contract; harvest is the next milestone task) [→ adr-harvest]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the AI's actual build decision now has a stable home (§5 "Strategy actually used:") — half of the report→§5 loop from strategy-soft-not-hard; the harvest into §7 completes it (evidence: field shipped; adr-harvest pending) [folded foundation-version 56]
