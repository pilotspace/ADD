# TASK: Extend the §5-strategy pull to streams.md's worker contract

slug: streams-strategy-pull · created: 2026-06-27 · stage: mvp
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
  - `add-method/skill/add/streams.md` — the worker-contract ```xml fence (§ "## The worker contract"); has `<objective>`/`<persona>`/`<touch_boundary>`/`<context_files>`/`<expertise>`/`<tools>`/`<return>`; ADD a `<strategy>` block AFTER `</persona>`, BEFORE `<touch_boundary>` (INSIDE the fence) — same 200 B block shipped to advisor.md
  - 3-tree parity: also `.claude/skills/add/streams.md` + `add-method/src/add_method/_bundled/skill/add/streams.md` — byte-identical
  - `add-method/tooling/test_xml_convention.py:190` `WORKER_CONTRACT_TAGS` — ADD `"strategy"` so test_engine_worker_contract_preserved requires it present-raw + gone-after-strip (fenced)
  - `add-method/tooling/test_skill_lean.py` — streams.md ∈ orchestration pool → REBASELINE 52464 → 52731 (+⌈200/0.75⌉=267); ratio 0.75 kept
Context (working folder):
  - `add-method/tooling/test_streams.py` — guards streams.md worker contract (does NOT assert the XML tag set; that's test_xml_convention) — ADD one positive test: `<strategy>` present, fenced, names §5
  - the just-shipped `advisor.md` `<strategy>` block (build-strategy-solutions) — reuse the EXACT same text for consistency
Honors (patterns / conventions):
  - mirror the just-merged advisor pattern (fenced <strategy> → task §5); 3-tree byte parity; prose/skill-only ⇒ ENGINE_MD5 untouched
  - lean rebaseline = documented "rebaseline for human-approved new surface" (ratio kept, baseline += surface÷ratio)
  - red/green TDD; freeze §3 before build; resolves the build-strategy-solutions [SPEC · seeded] delta
Anchors the contract cites: `streams.md` worker-contract `<strategy>` block · `WORKER_CONTRACT_TAGS` += "strategy" · `test_skill_lean.py` orchestration baseline 52731 · `test_streams.py` strategy test

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: extend the SAME §5-strategy pull to streams.md's worker contract (the parallel-spawn HOME) + WORKER_CONTRACT_TAGS, so parallel workers and the single advisor are consistent (from build-strategy-solutions spec-delta)
Framings weighed: register-in-WORKER_CONTRACT_TAGS (chosen — the home guards it like every other worker tag) · advisor-only (rejected: leaves the parallel-spawn home inconsistent) · prose-only-no-tag (rejected: a tag is what the worker-contract preserve-test enforces)
Must:
<must>
  - streams.md's worker-contract ```xml fence gains a `<strategy>` block (AFTER `</persona>`, BEFORE `<touch_boundary>`) — the EXACT same 200 B text shipped to advisor.md, pointing the worker at the task's §5 Strategy + Known-problem fixes
  - `WORKER_CONTRACT_TAGS` (test_xml_convention.py) gains `"strategy"`, so test_engine_worker_contract_preserved requires it present-raw AND gone-after-fence-strip (fenced/exempt)
  - all edits byte-identical across the 3 streams.md trees (canonical · _bundled · dogfood)
  - skill-prose-only: `add.py` + `add_engine/*.py` UNTOUCHED ⇒ ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
  - the orchestration lean-pool fence rebaselined 52464 → 52731 (ratio 0.75 kept; +⌈200/0.75⌉)
  - resolves the build-strategy-solutions [SPEC · seeded] delta (advisor + streams now both pull §5)
</must>
Reject:
<reject>
  - `<strategy>` placed OUTSIDE the streams.md fence -> "vocab_offmidiom" (worker tags must stay fenced)
  - `WORKER_CONTRACT_TAGS` left without "strategy" while the block is added (or vice-versa) -> "preserve_test_red"
  - one streams.md tree edited but not all three -> "parity_break"
  - `add.py` / `add_engine/*.py` edited -> "engine_touched"
</reject>
After:
<after>
  - both spawn homes — the single advisor (advisor.md) AND the parallel worker (streams.md) — direct the spawned agent to follow the task's §5 plan; the consistency gap the ai-proxy trace exposed is fully closed
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that adding "strategy" to WORKER_CONTRACT_TAGS has no OTHER consumer that breaks — lowest confidence because the constant is imported by test_advisor_strategy (_TEMPLATE_TAGS is a separate local set, but worth a grep); if wrong: a sibling test goes red — cheap to spot in the red run — THIS is the freeze flag
  - [ ] reusing the advisor block VERBATIM in streams.md is the right call (vs. a worker-flavored wording); identical text maximizes consistency and is the lean choice
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: streams worker contract carries a fenced <strategy> that points at §5
  Given add-method/skill/add/streams.md
  When I read the worker-contract ```xml fence
  Then a <strategy> element is present between </persona> and <touch_boundary>, naming §5
  And after stripping code fences no <strategy> tag remains (fenced/exempt)

Scenario: the worker-contract preserve-test recognises strategy
  Given WORKER_CONTRACT_TAGS includes "strategy"
  When test_engine_worker_contract_preserved runs
  Then strategy is in raw tags AND absent from fence-stripped tags
  And the other worker tags (objective…return) stay present + fenced

Scenario: three streams.md trees stay byte-identical
  Given the canonical, _bundled, and dogfood streams.md
  When I md5 the trio
  Then it is a single digest

Scenario: skill-prose-only — engine untouched
  Given add.py and add_engine/*.py
  When I digest them
  Then ENGINE_MD5 and ENGINE_PKG_MD5 are unchanged

Scenario: lean fence stays green after rebaseline
  Given test_skill_lean orchestration baseline 52731 (ratio 0.75 kept)
  When I run the suite
  Then the orchestration pool and whole-tree fences pass

Scenario: the seeded spec-delta is resolved
  Given build-strategy-solutions' [SPEC · seeded] streams delta
  When this task reaches done
  Then advisor.md AND streams.md both direct the spawn at the task's §5

Scenario: reject <strategy> outside the fence
  Given streams.md worker tags must stay fenced
  When <strategy> is placed OUTSIDE the ```xml fence
  Then test_engine_worker_contract_preserved fails -> "vocab_offmidiom"
  And the worker tags stay fenced

Scenario: reject a block/tag mismatch
  Given the <strategy> block and WORKER_CONTRACT_TAGS must move together
  When only one is changed
  Then the preserve-test fails -> "preserve_test_red"
  And neither half ships alone
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TWO LITERAL ADDITIONS (byte-identical across canonical · _bundled · dogfood):

ADD-A · streams.md worker-contract ```xml fence — insert AFTER </persona>, BEFORE
        <touch_boundary> (INSIDE the fence), the EXACT block shipped to advisor.md:
    <strategy>
    Follow the task's §5 plan — do not invent your own: the Strategy (ordered batches) build
    order and the Known-problem fixes (trap → fix for each anticipated failure mode).
    </strategy>

ADD-B · test_xml_convention.py WORKER_CONTRACT_TAGS — add "strategy" to the set.

INVARIANTS (frozen):
  INV-1 fenced — <strategy> inside the worker-contract ```xml; present-raw, gone-after-strip
  INV-2 paired-move — the block (ADD-A) and the tag registration (ADD-B) ship together
  INV-3 parity — the streams.md canonical/_bundled/dogfood trio is a single md5
  INV-4 engine untouched — add.py + add_engine/*.py == current pins (ENGINE_MD5 / ENGINE_PKG_MD5)
  INV-5 lean fence — orchestration baseline 52464 → 52731 (ratio 0.75 kept, +⌈200/0.75⌉=267); suite green
  INV-6 delta — resolves build-strategy-solutions [SPEC · seeded] → [SPEC · folded/resolved]
Tests: ADD-B turns test_engine_worker_contract_preserved RED→GREEN; + a positive test in test_streams.py (<strategy> fenced + names §5).
```

`Least-sure flag surfaced at freeze:` [test] adding "strategy" to WORKER_CONTRACT_TAGS — grep CONFIRMED its only consumer is test_engine_worker_contract_preserved (test_advisor_strategy uses a separate local _TEMPLATE_TAGS); risk fully retired. Otherwise a faithful mirror of the v1 you just approved.

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

Coverage target: behavior-anchored (skill/test-only); every scenario has ≥1 assertion
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_strategy_block_present_and_names_section5 (test_streams.py): <strategy> present, between </persona> and <touch_boundary>, names §5 — RED ✓
  - test_strategy_stays_fenced (test_streams.py): <strategy> gone after fence-strip
  - test_engine_worker_contract_preserved (test_xml_convention.py): WORKER_CONTRACT_TAGS now includes "strategy" → requires it present-raw + fenced — RED ✓
  - test_streams_mirror (existing): the 3 streams.md trees single md5 (parity guard)
  - reject guards reused: preserve-test (vocab_offmidiom if unfenced; preserve_test_red if block/tag mismatch) · ENGINE_MD5 suites (engine_touched)
  - test_skill_lean rebaselined 52731 → GREEN (ratio 0.75 kept)
</test_plan>

Tests live in: `add-method/tooling/test_streams.py` `add-method/tooling/test_xml_convention.py` `add-method/tooling/test_skill_lean.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/streams.md` `add-method/src/add_method/_bundled/skill/add/streams.md` `.claude/skills/add/streams.md` `add-method/tooling/test_xml_convention.py` `add-method/tooling/test_streams.py` `add-method/tooling/test_skill_lean.py`
Strategy (ordered batches): 1. add "strategy" to WORKER_CONTRACT_TAGS + a positive test_streams.py test RED · 2. insert the <strategy> block into all 3 streams.md copies (byte-identical, reuse advisor text) · 3. rebaseline orchestration 52464→52731 · 4. full suite green + resolve the seeded delta
Known-problem fixes: tree-parity drift → edit all 3 streams.md in one batch + parity md5 catches it · forgetting WORKER_CONTRACT_TAGS while adding the block → the preserve-test goes red (paired-move enforced) · stale rebaseline math → recompute from real bytes (block measured at 200 B)
Safety rule (feature-specific): the block (ADD-A) and tag (ADD-B) move together — neither half ships alone
Code lives in: the files named in Scope (skill/test, not `./src/`)
Constraints: do NOT change any test logic beyond the named additions or the contract; allow-list only.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 2109/0; check 461/0
- [x] coverage did not decrease — 2 new test_streams assertions + WORKER_CONTRACT_TAGS now guards strategy; none removed
- [x] no test or contract was altered during build — all test edits in the TESTS phase; build touched only the 3 streams.md copies (git status confirms)
- [x] the green was EARNED, not gamed — refute-read: the preserve-test now FAILS if strategy is absent or unfenced (proved red first); the streams positive test asserts placement (between </persona> and <touch_boundary>) + §5 reference + fenced; streams.md is a pure insertion
- [x] concurrency / timing of the risky operation is safe — N/A: static skill prose
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: no code/deps
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the advisor.md pattern + worker-contract fence convention exactly
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze @ v1; auto-gated on complete evidence under `autonomy: auto`

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] streams.md's worker contract directs the worker at the task's §5 — confirmed by reading the shipped `<strategy>` block (names §5 + both field labels), fenced, between persona and touch_boundary
- [x] both spawn homes now consistent — confirmed: advisor.md (single) + streams.md (parallel) carry the SAME `<strategy>` block; the seeded delta is resolved
- [x] no cost elsewhere — confirmed: engine pins unchanged (no add.py/add_engine in git status), orchestration pool 39465 ≤ 39548 target (ratio 0.75 kept)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the streams.md `<strategy>` block reads identically to advisor's (deliberate consistency), sits correctly inside the worker-contract fence, and the WORKER_CONTRACT_TAGS addition is the single guard that now binds it; no worker-contract tag lost (preserve-test green)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

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
