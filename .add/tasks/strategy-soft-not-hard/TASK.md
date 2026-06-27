# TASK: Soften the <strategy> block: §5 is preferred, builder self-improves + reports actual strategy for audit

slug: strategy-soft-not-hard · created: 2026-06-28 · stage: mvp
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
  - `add-method/skill/add/advisor.md` — the plan-following template: (a) the intro clause "The `<strategy>` block mirrors … builds in the planned order and dodges the known traps" (outside the fence) + (b) the fenced `<strategy>` block (after `</persona>`); SOFTEN both — §5 becomes the PREFERRED path (drop "do not invent your own"), builder self-improves + reports the actual strategy for audit
  - `add-method/skill/add/streams.md` — the worker-contract `<strategy>` block (same fenced block, byte-identical to advisor's); SOFTEN to match
  - 3-tree byte parity for BOTH files: also `.claude/skills/add/…` + `add-method/src/add_method/_bundled/skill/add/…`
  - `add-method/tooling/test_advisor_strategy.py` `test_strategy_block_fenced_and_points_at_section5` — ADD softening assertions (preferred/not-hard · self-improve · report-for-audit · rigid phrase gone)
  - `add-method/tooling/test_streams.py` `WorkerStrategyPullTest` — ADD the same softening assertions
  - `add-method/tooling/test_skill_lean.py` — orchestration baseline 52731 → 53125 (+⌈295/0.75⌉=394; ratio 0.75 kept)
Context (working folder): the just-shipped PR #106 (build-strategy-solutions + streams-strategy-pull) whose block reads "Follow … do not invent your own" — the user feedback: strategy is PREFERRED not hard; builder self-improves + reports actual strategy for audit (ties to ADR-at-observe todo #22)
Honors (patterns / conventions): change-request discipline (the edited §3 wording RE-freezes @ v1); 3-tree byte parity; prose/skill-only ⇒ ENGINE_MD5/ENGINE_PKG_MD5 untouched; lean rebaseline = documented "human-approved surface" (ratio kept); WORKER_CONTRACT_TAGS keeps "strategy" (no regression)
Anchors the contract cites: advisor.md intro clause + `<strategy>` block · streams.md `<strategy>` block · the two blocks byte-identical · `test_skill_lean` orchestration baseline 53125

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: soften the `<strategy>` spawn-prompt block — §5 is the builder's PREFERRED plan it self-improves and reports on, not a hard directive (change-request on PR #106, per user feedback)
Framings weighed: soften-block-and-intro (chosen — the intro still says "builds in the planned order", which contradicts a softened block) · block-only (rejected: leaves the rigid intro) · add-the-§5-writeback-engine-now (rejected: that audit-record mechanism is the bigger todo #22; this task is wording only)
Must:
<must>
  - the `<strategy>` block (advisor.md + streams.md, byte-identical) frames the task's §5 as the PREFERRED starting path, explicitly "not a hard rule"; instructs the builder to improve on it when a better strategy emerges during build; and on done to report the strategy ACTUALLY used so the orchestrator can update §5 for the audit trail
  - the rigid phrase "do not invent your own" is GONE from both blocks
  - advisor.md's intro clause is softened to match (no "builds in the planned order and dodges the known traps")
  - the two `<strategy>` blocks stay byte-identical to each other AND across the 3 trees each (advisor.md + streams.md)
  - skill-prose-only: `add.py` + `add_engine/*.py` UNTOUCHED ⇒ ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
  - WORKER_CONTRACT_TAGS still includes "strategy"; the block stays inside the ```xml fence (no regression of the PR #106 guard)
  - the orchestration lean pool is rebaselined 52731 → 53125 (ratio 0.75 kept; +⌈295/0.75⌉)
</must>
Reject:
<reject>
  - "do not invent your own" (or any hard-rule phrasing) left in either block -> "rigid_strategy"
  - advisor `<strategy>` block text ≠ streams `<strategy>` block text (drift) -> "block_drift"
  - one tree edited but not all three, for either file -> "parity_break"
  - `<strategy>` moved OUTSIDE the ```xml fence -> "vocab_offmidiom"
  - `add.py` / `add_engine/*.py` edited -> "engine_touched"
</reject>
After:
<after>
  - both spawn homes tell the builder: follow §5 as your PREFERRED plan, self-improve to the best strategy as you build, and report what you ACTUALLY used so §5 is updated for the audit trail — the "too rigid" feedback is closed
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that the EXISTING positive tests (test_advisor_strategy / test_streams asserting "§5" present + fenced) stay green under the new wording — lowest confidence because dropping "§5" from the block would break them; mitigated: the new block keeps "§5" verbatim; if wrong: those two go red in the build run — cheap to spot — THIS is the freeze flag
  - [ ] reusing the SAME softened block text in advisor + streams (byte-identical) is right vs a worker-flavored variant — identical maximizes consistency; the established choice from PR #106
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the strategy block frames §5 as preferred, not hard
  Given advisor.md and streams.md <strategy> blocks
  When I read each block
  Then it states §5 is the PREFERRED path / "not a hard rule"
  And the phrase "do not invent your own" is absent

Scenario: the block tells the builder to self-improve and report for audit
  Given each <strategy> block
  When I read it
  Then it instructs improving on the plan when a better strategy emerges
  And reporting the strategy actually used so §5 is updated for the audit trail

Scenario: advisor and streams blocks stay byte-identical
  Given the two <strategy> blocks
  When I compare their text
  Then they are byte-identical

Scenario: each file stays byte-identical across the three trees
  Given canonical / _bundled / dogfood advisor.md and streams.md
  When I md5 each file's trio
  Then each is a single digest

Scenario: the block stays fenced and registered
  Given WORKER_CONTRACT_TAGS includes "strategy"
  When test_engine_worker_contract_preserved runs
  Then strategy is present-raw AND gone after fence-strip (still fenced)

Scenario: skill-prose-only — engine untouched
  Given add.py and add_engine/*.py
  When I digest them
  Then ENGINE_MD5 and ENGINE_PKG_MD5 are unchanged

Scenario: lean fence green after rebaseline
  Given the orchestration baseline 53125 (ratio 0.75 kept)
  When I run the suite
  Then the orchestration pool and whole-tree fences pass

Scenario: reject rigid phrasing
  Given the softened block
  When "do not invent your own" (hard-rule phrasing) is present in a block
  Then the softening assertion fails -> "rigid_strategy"
  And the block is not shipped

Scenario: reject block drift
  Given advisor + streams blocks must match
  When their text differs
  Then the byte-identity assertion fails -> "block_drift"
  And neither half ships alone
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: the <strategy> block — fenced (inside the worker / plan-following xml code fence),
byte-identical in advisor.md (after </persona>) and streams.md (after </persona>, before <touch_boundary>)

FROZEN BLOCK TEXT (327 B · byte-identical in both files · all 3 trees):
<strategy>
The task's §5 plan — the Strategy (ordered batches) order and the Known-problem fixes — is
your PREFERRED starting path, not a hard rule. Improve on it when a better strategy emerges
as you build; on done, report the strategy you ACTUALLY used so the orchestrator can update
§5 for the audit trail.
</strategy>

FROZEN ADVISOR INTRO CLAUSE (188 B · advisor.md only · prose above the fence):
The `<strategy>` block mirrors the task's §5 (Strategy + Known-problem fixes) as the subagent's PREFERRED path — it self-improves on that plan and reports the strategy it actually used.

INVARIANTS:
INV-1  both <strategy> blocks byte-identical to each other and to the FROZEN BLOCK TEXT
INV-2  advisor.md AND streams.md each byte-identical across canonical / _bundled / dogfood
INV-3  "do not invent your own" absent from both blocks
INV-4  WORKER_CONTRACT_TAGS still includes "strategy"; block stays inside the xml fence
INV-5  add.py + add_engine/*.py untouched -> ENGINE_MD5 / ENGINE_PKG_MD5 unchanged
INV-6  orchestration lean baseline 52731 -> 53125 (ratio 0.75 kept; +ceil(295/0.75)=394)
error codes: rigid_strategy · block_drift · parity_break · vocab_offmidiom · engine_touched
```

Least-sure flag surfaced at freeze: [test] the existing positive tests assert "§5" is present in the block — the new wording keeps "§5" verbatim, so they stay green; had I dropped it they'd go red (caught in the build run). No other material risk: pure prose, no engine, byte-parity + lean enforced.
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

Coverage target: behavior-anchored (skill/test-only); every Must + Reject has ≥1 assertion
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_strategy_block_is_preferred_not_hard (test_advisor_strategy.py): block has "not a hard rule" + "Improve on it" + "report the strategy" + "audit"; "do not invent your own" absent; advisor intro softened ("self-improves on that plan", no "builds in the planned order") — RED ✓
  - test_strategy_block_is_preferred_not_hard (test_streams.py): same block assertions for streams.md — RED ✓
  - test_block_byte_identical_to_advisor (test_streams.py): the two <strategy> blocks byte-identical (block_drift guard) — green now (both old), stays green after identical edit
  - test_strategy_block_fenced_and_points_at_section5 (existing): §5 + fenced preserved
  - test_engine_worker_contract_preserved / WORKER_CONTRACT_TAGS: "strategy" still present-raw + fenced
  - three-trees byte-identity (existing, advisor + streams): single md5 each after the mirror cp
  - test_skill_lean rebaselined 53125 → GREEN (ratio 0.75 kept)
  - ENGINE_MD5 / ENGINE_PKG_MD5 suites: unchanged (no engine touched)
</test_plan>

Tests live in: `add-method/tooling/test_advisor_strategy.py` `add-method/tooling/test_streams.py` `add-method/tooling/test_skill_lean.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/advisor.md` `add-method/skill/add/streams.md` `.claude/skills/add/advisor.md` `.claude/skills/add/streams.md` `add-method/src/add_method/_bundled/skill/add/advisor.md` `add-method/src/add_method/_bundled/skill/add/streams.md` `add-method/tooling/test_advisor_strategy.py` `add-method/tooling/test_streams.py` `add-method/tooling/test_skill_lean.py`
Strategy (ordered batches): 1. TESTS — add softening assertions to test_advisor_strategy + test_streams (preferred/not-hard · self-improve · report-for-audit · "do not invent your own" absent) and rebaseline lean to 53125 (all red/adjusted before build). 2. BUILD — edit canonical advisor.md (intro clause + `<strategy>` block) and streams.md (`<strategy>` block), then cp canonical → both mirrors for each file. 3. Verify the two blocks are byte-identical to each other + each file's trio is one md5; run the suite green.
Known-problem fixes: greedy block-match catching the intro's backtick `<strategy>` reference → anchor the block regex to a line-start `\n<strategy>\n` · a stray bracketed tag (e.g. `<return>`) inside the block confusing the convention parser → keep tag-like words out of the prose · forgetting a mirror → always cp from canonical and md5 the trio · editing a test during BUILD trips the tamper tripwire → do ALL test edits (incl. the lean rebaseline) in the TESTS phase
Safety rule (feature-specific): edit the canonical file, then cp to BOTH mirrors in the same batch — never hand-type a mirror (keeps the 3-tree md5 single)
Code lives in: `./src/`
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

- [x] all tests pass — full tooling suite 2112/0; check 464/0
- [x] coverage did not decrease — +3 softening tests (advisor + streams + block-identity); none removed
- [x] no test or contract was altered during build — all test edits in the TESTS phase; build touched only the 6 skill copies (git status confirms)
- [x] the green was EARNED, not gamed — refute-read: the softening tests proved RED against the old "do not invent your own" block, then GREEN after the edit; block-identity + 3-tree md5 enforce no drift; the §5 marker survives so the existing positive tests still bind
- [x] concurrency / timing of the risky operation is safe — N/A: static skill prose
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: no code/deps
- [x] layering & dependencies follow CONVENTIONS.md — block stays fenced; intro stays outside-fence; mirrors the established <strategy> pattern
- [x] a person reviewed and approved the change — Tin Dang approved the §3 re-freeze @ v1 (and the before/after wording before the task); auto-gated on complete evidence

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] the block now reads "PREFERRED starting path, not a hard rule … Improve on it … report the strategy you ACTUALLY used … for the audit trail" — confirmed by reading the shipped block in advisor.md + streams.md
- [x] the rigid framing is gone from BOTH homes — confirmed: "do not invent your own" in advisor=False, in streams=False; advisor intro no longer says "builds in the planned order"
- [x] no cost elsewhere — confirmed: engine pins unchanged (no add.py/add_engine in git status); blocks byte-identical (True); 3-tree md5 = 1 each; lean pool green at 53125 (ratio 0.75 kept)

### Deep checks
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the new block reads as a preference (preferred path / not a hard rule), invites self-improvement (Improve on it when a better strategy emerges), and closes the loop (report the strategy actually used → §5 audit trail); the advisor intro now mirrors that framing; both blocks fenced, identical, registered (WORKER_CONTRACT_TAGS keeps "strategy")

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a future spawn prompt drifting back to a hard directive (grep the blocks for "do not invent your own" / "must follow"); the two blocks drifting apart (block_drift)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] make the report→§5 loop real at OBSERVE — the builder's reported actual-strategy is written back into §5 as a durable ADR-style record for BOTH human and AI decisions, not just prose guidance (evidence: this task only softened the prompt wording; the write-back is still manual — ties to todo #22)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] spawn-prompt strategy guidance must be PREFERRED-not-hard + self-improve-during-build + report-actual-for-audit, never a rigid "do not invent your own" (evidence: the shipped block contradicted advisor.md's own confidence.md self-score/refine ethos; the user flagged it as too hard)
