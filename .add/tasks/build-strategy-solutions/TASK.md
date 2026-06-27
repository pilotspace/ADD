# TASK: §5 Strategy & known-problem solutions, fed consistently into subagent spawns

slug: build-strategy-solutions · created: 2026-06-27 · stage: mvp
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
  - `add-method/tooling/templates/TASK.md.tmpl` §5 BUILD — has `Scope (may touch):` + `Strategy (ordered batches):` + `Safety rule…` lines; ADD a plain-text `Known-problem fixes:` line (additive, NOT an XML tag — `FROZEN_TAGS` census is frozen)
  - `add-method/tooling/templates/TASK.fast.md.tmpl` §5 BUILD — currently Scope+Code+Constraints only (NO strategy); ADD a condensed `Strategy & known-problem fixes:` line
  - `add-method/skill/add/advisor.md` — the fenced ```xml plan-following template (`<objective>`/`<persona>`/`<context_files>`/`<return>`); ADD a `<strategy>` element INSIDE the fence that points the subagent at the task's §5
  - 3-tree parity: each of the above also in `.add/tooling/templates/` + `add-method/src/add_method/_bundled/tooling/templates/` (templates) and `.claude/skills/add/` + `add-method/src/add_method/_bundled/skill/add/` (advisor.md) — byte-identical
Context (working folder):
  - `add-method/tooling/test_scope_decl_template.py` — the precedent prose/template red-green suite for §5 (`STRATEGY_LABEL`, `EXISTING_LINES` byte-identical, 3-tree md5, `FROZEN_TAGS`, add.py==ENGINE_MD5) — EXTEND it for the new line
  - `add-method/tooling/test_advisor_strategy.py` — guards advisor.md (`_TEMPLATE_TAGS={objective,persona,return}` fenced; outside-fence vocab=={constraints}) — EXTEND for `<strategy>`
  - `add-method/tooling/test_skill_lean.py` — advisor.md ∈ orchestration pool (target 38995 B, headroom 82 B) → REBASELINE baseline 51994 += ⌈grow/0.75⌉
  - `add-method/tooling/test_xml_convention.py` — `WORKER_CONTRACT_TAGS` (streams.md home); advisor `<strategy>` stays fenced ⇒ exempt
Honors (patterns / conventions):
  - additive-only template edit (3 §5 lines byte-identical) + 3-tree byte parity (test_bundle_parity/test_tree_parity) — the scope-decl-template precedent
  - prose/template-only task: add.py + add_engine/*.py UNTOUCHED ⇒ ENGINE_MD5/ENGINE_PKG_MD5 unchanged (do NOT edit constants.py fallbacks — they stay floor-only)
  - lean-fence rebaseline = the documented "rebaseline for human-approved new surface" method (ratio kept, baseline += surface÷ratio)
  - red/green TDD (CLAUDE.md Rule 3); freeze §3 before build; no pre-stamping the human freeze
Anchors the contract cites: `TASK.md.tmpl` §5 `Known-problem fixes:` line · `TASK.fast.md.tmpl` §5 `Strategy & known-problem fixes:` line · `advisor.md` fenced `<strategy>` element · `test_scope_decl_template.py` · `test_advisor_strategy.py` · `test_skill_lean.py` orchestration baseline

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §5 carries strategy + known-problem solutions, and the advisor spawn template pulls from it
Framings weighed: source-of-truth-in-§5 + spawn-references-it (chosen) · spawn-only (rejected: TASK.md stays the consistency anchor) · rename-Strategy-line (rejected: EXISTING_LINES byte-identity)
Must:
<must>
  - the full `TASK.md.tmpl` §5 BUILD gains a plain-text `Known-problem fixes:` line (the planned fix for each anticipated trap), placed ADDITIVELY — the 3 pre-existing §5 lines stay byte-identical
  - the fast `TASK.fast.md.tmpl` §5 BUILD (today: no strategy line) gains ONE condensed `Strategy & known-problem fixes:` line
  - `advisor.md`'s fenced ```xml plan-following template gains a `<strategy>` element (INSIDE the fence) directing the subagent to follow the task's §5 Strategy (ordered batches) + Known-problem fixes
  - all edits are byte-identical across the 3 trees (canonical · _bundled · dogfood)
  - prose/template-only: `add.py` + `add_engine/*.py` UNTOUCHED ⇒ ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
  - a fresh `new-task` scaffold (full AND `--fast`) carries the new §5 line(s)
  - the orchestration lean-pool fence is rebaselined (ratio 0.75 kept; baseline += ⌈advisor-growth ÷ 0.75⌉) — admit the new surface, preserve the won ground
</must>
Reject:
<reject>
  - any of the 3 pre-existing §5 lines changed (non-additive) -> "non_additive_edit"
  - a NEW XML tag added to `TASK.md.tmpl` (the §5 line must be plain text) -> "frozen_tag_census"
  - `<strategy>` placed OUTSIDE the advisor.md code fence -> "vocab_offmidiom"
  - `add.py` / `add_engine/*.py` edited -> "engine_touched"
  - one tree edited but not all three -> "parity_break"
</reject>
After:
<after>
  - every newly scaffolded task (full + fast) records strategy AND known-problem solutions in §5, and the advisor spawn template tells the subagent to follow them — closing the doc-vs-reality gap the ai-proxy trace exposed (strategy lived in global Rule-5, never pulled from §5)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the exact WORDING/SHAPE of the three additions (a separate `Known-problem fixes:` line vs. folding into Strategy; a dedicated `<strategy>` tag vs. extending `<persona>` step-2) — lowest confidence because it is a method-voice choice the human owns; if wrong: re-edit prose across 6 files + re-rebaseline (cheap but churny) — THIS is the freeze flag
  - [ ] streams.md (the worker-contract HOME) stays UNCHANGED — the advisor fenced `<strategy>` needs no matching streams.md worker-contract tag / WORKER_CONTRACT_TAGS update; if wrong: a consistency gap between single-advisor and parallel-streams spawns (carry as a spec-delta, don't widen scope now)
  - [ ] the fast lane SHOULD carry strategy too (the human chose "Both"); if leanness should win, drop the fast-template edit
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: full template §5 carries known-problem fixes
  Given add-method/tooling/templates/TASK.md.tmpl
  When I read its §5 BUILD block
  Then a plain-text "Known-problem fixes:" line is present, below "Strategy (ordered batches):"
  And the 3 pre-existing §5 lines (Safety rule / Code lives / Constraints) are byte-identical

Scenario: fast template §5 carries strategy & known-problem fixes
  Given add-method/tooling/templates/TASK.fast.md.tmpl
  When I read its §5 BUILD block
  Then a single "Strategy & known-problem fixes:" line is present
  And the pre-existing "Scope (may touch):" line is unchanged

Scenario: advisor spawn template carries a fenced <strategy> that points at §5
  Given add-method/skill/add/advisor.md
  When I read the plan-following ```xml template
  Then a <strategy> element is present INSIDE the code fence and names the task's §5
  And after stripping code fences no <strategy> tag remains (it stays fenced/exempt)

Scenario: a fresh scaffold carries the new §5 lines
  Given a temp project after init + lock
  When I run new-task (full) and new-task --fast
  Then the full TASK.md shows "Known-problem fixes:" and the fast TASK.md shows "Strategy & known-problem fixes:"

Scenario: three trees stay byte-identical
  Given the canonical, _bundled, and dogfood copies of each edited file
  When I md5 each trio (TASK.md.tmpl, TASK.fast.md.tmpl, advisor.md)
  Then each trio is a single digest

Scenario: prose/template-only — engine untouched
  Given add.py and add_engine/*.py
  When I digest them
  Then ENGINE_MD5 and ENGINE_PKG_MD5 are unchanged from the current pin

Scenario: lean fence stays green after rebaseline
  Given test_skill_lean.py with the orchestration baseline rebaselined (ratio 0.75 kept)
  When I run the suite
  Then the orchestration pool and whole-tree fences pass

Scenario: reject a non-additive edit
  Given the §5 edit
  When any pre-existing §5 line (Strategy / Safety rule / Code lives / Constraints) is altered
  Then test_scope_decl_template fails -> "non_additive_edit"
  And the edit is rejected

Scenario: reject a new XML tag in the template
  Given TASK.md.tmpl's frozen tag census
  When the new §5 element is added as an XML tag instead of plain text
  Then the FROZEN_TAGS assertion fails -> "frozen_tag_census"
  And the tag census is unchanged

Scenario: reject <strategy> outside the fence
  Given advisor.md's outside-fence vocab == {constraints}
  When <strategy> is placed OUTSIDE the ```xml fence
  Then test_advisor_strategy / test_xml_convention fail -> "vocab_offmidiom"
  And the outside-fence vocab stays {constraints}
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
THREE LITERAL ADDITIONS (each applied byte-identically across canonical · _bundled · dogfood):

ADD-1 · full TASK.md.tmpl §5 BUILD — insert AFTER the "Strategy (ordered batches):" line,
        BEFORE "Safety rule (feature-specific):" (so Scope < Strategy < Known-problem fixes < Safety rule):
    Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>

ADD-2 · fast TASK.fast.md.tmpl §5 BUILD — insert AFTER the "Scope (may touch):" line,
        BEFORE "Code lives in:":
    Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge>

ADD-3 · advisor.md fenced ```xml template — insert a <strategy> block AFTER </persona>,
        BEFORE <context_files> (INSIDE the existing code fence):
    <strategy>
    Follow the task's §5 plan — do not invent your own: the Strategy (ordered batches) build order
    and the Known-problem fixes (trap → fix for each anticipated failure mode).
    </strategy>
  + one prose clause in "## The plan-following prompt template" naming that <strategy> mirrors §5.

INVARIANTS (frozen):
  INV-1 additive — the 3 pre-existing full-§5 lines + the fast "Scope (may touch):" line stay byte-identical
  INV-2 plain-text in templates — NO new XML tag in TASK.md.tmpl (FROZEN_TAGS unchanged); <strategy> lives ONLY in advisor.md's fence
  INV-3 fenced — advisor <strategy> inside the ```xml block; advisor outside-fence vocab stays {constraints}
  INV-4 parity — every edited file's canonical/_bundled/dogfood trio is a single md5
  INV-5 engine untouched — add.py + add_engine/*.py digests == current pins (ENGINE_MD5 / ENGINE_PKG_MD5)
  INV-6 lean fence — orchestration baseline rebaselined (ratio 0.75 kept, baseline += ⌈advisor-growth ÷ 0.75⌉); suite green
Tests: EXTEND test_scope_decl_template.py (ADD-1/2 + parity + engine-untouched) + test_advisor_strategy.py (ADD-3 fenced).
```

`Least-sure flag surfaced at freeze:` [spec/contract] the exact WORDING of ADD-1/2/3 (a separate `Known-problem fixes:` line vs. folding it into Strategy; a dedicated `<strategy>` tag vs. extending `<persona>` step-2) — a method-voice choice you own; if wrong, re-edit 6 prose files + re-rebaseline (cheap, churny).

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

Coverage target: behavior-anchored (prose/template task — no src/ %); every scenario has ≥1 assertion across the 2 extended suites
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_full_template_known_problem_fixes_line (ADD-1): Strategy < Known-problem fixes < Safety rule; EXISTING_LINES byte-identical — RED ✓
  - test_fast_template_strategy_line (ADD-2): fast §5 has 'Strategy & known-problem fixes:' below Scope — RED ✓
  - test_fast_template_mirrors: fast-template trio single md5 (parity)
  - test_scaffold_carries_strategy_solutions (ADD-1/2): fresh new-task + new-task --fast carry the lines — RED ✓
  - test_strategy_block_fenced_and_points_at_section5 (ADD-3, in test_advisor_strategy.py): <strategy> present raw, gone after fence-strip, names §5 — RED ✓
  - reject guards already live: EXISTING_LINES (non_additive_edit) · FROZEN_TAGS (frozen_tag_census) · test_vocab_subset_outside_fence (vocab_offmidiom) · test_mirrors_and_engine_untouched (engine_touched + parity_break)
  - test_skill_lean rebaselined → GREEN (regression fence, ratio 0.75 kept)
</test_plan>

Tests live in: `add-method/tooling/test_scope_decl_template.py` `add-method/tooling/test_advisor_strategy.py` `add-method/tooling/test_skill_lean.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `.add/tooling/templates/TASK.md.tmpl` `.add/tooling/templates/TASK.fast.md.tmpl` `add-method/skill/add/advisor.md` `add-method/src/add_method/_bundled/skill/add/advisor.md` `.claude/skills/add/advisor.md` `add-method/tooling/test_scope_decl_template.py` `add-method/tooling/test_advisor_strategy.py` `add-method/tooling/test_skill_lean.py`
Strategy (ordered batches): 1. extend test_scope_decl_template.py (ADD-1/2 + parity + engine-untouched) and test_advisor_strategy.py (ADD-3 fenced) RED · 2. apply ADD-1/2 to all 6 template copies + ADD-3 to all 3 advisor copies (byte-identical) · 3. measure advisor growth, rebaseline orchestration baseline (ratio 0.75 kept) · 4. run full suite green
Known-problem fixes: tree-parity drift (edit one copy, forget the others) → edit all 3 copies of each file in the same batch + the parity md5 test catches it · stale `wc -c` math on the rebaseline → recompute from the real bytes after the edit, never hand-estimate · a multibyte char (→ ⚠) miscounted → byte count not char count, matching the fence's `wc -c ÷ 4` proxy
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: the files named in Scope (no `./src/` — this is a method/template task)
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

- [x] all tests pass — full tooling suite 2107/0; check 457/0
- [x] coverage did not decrease — behavior-anchored prose/template task; 5 new assertions added, none removed
- [x] no test or contract was altered during build — all test edits done in the TESTS phase; build touched only the 9 method/template files (git status confirms)
- [x] the green was EARNED, not gamed — refute-read: the scaffold test invokes real `new-task` + `new-task --fast` and reads the scaffolded TASK.md (end-to-end, not a fixture); `<strategy>` test asserts present-raw + gone-after-fence-strip + names §5; templates are pure insertions (1+/0-), advisor's lone "-1" is the intro sentence extended in place (no content lost)
- [x] concurrency / timing of the risky operation is safe — N/A: static prose/template files, no runtime path
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: no code, no deps; allow-list untouched
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the scope-decl-template precedent (additive §5 line + 3-tree parity + engine-untouched)
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze @ v1 (the one human gate); auto-gated on complete evidence under `autonomy: auto`

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a freshly scaffolded full task shows `Known-problem fixes:` in §5; a `--fast` task shows `Strategy & known-problem fixes:` — confirmed by test_scaffold_carries_strategy_solutions running real new-task in a temp project
- [x] the advisor spawn template tells a subagent to follow the task's §5 — confirmed by reading the shipped `<strategy>` block (names §5 + Strategy + Known-problem fixes), fenced
- [x] the addition cost nothing elsewhere — confirmed: engine pins unchanged (no add.py/add_engine in git status), orchestration lean pool 39265 ≤ 39348 target (ratio 0.75 kept)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the §5 additions (full + fast) read as additive, in-place, ordered correctly (Scope < Strategy < Known-problem fixes < Safety rule); the advisor `<strategy>` block + intro clause read as consistent with §5's two field labels; no existing line lost; the lean rebaseline comment documents the +352 B / +470 baseline per the won-ground method

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether scaffolded tasks actually FILL the new §5 lines (a blank `Known-problem fixes:` is a non-use signal); whether spawned subagents cite §5 strategy in their returns

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] extend the SAME §5-strategy pull to streams.md's worker contract (the parallel-spawn HOME) + WORKER_CONTRACT_TAGS, so parallel workers and the single advisor are consistent (evidence: this task wired only advisor.md; the ai-proxy trace showed executors were parallel `streams.md`-style spawns, which still carry no §5 link) [→ streams-strategy-pull]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] a spawn template that doesn't reference the task's own §5 plan lets each spawn re-invent strategy (the ai-proxy trace: 319 spawns pulled strategy from global Rule-5, never from §5) — fixed for the advisor; streams.md still open (evidence: test_advisor_strategy now asserts the <strategy>→§5 link)
