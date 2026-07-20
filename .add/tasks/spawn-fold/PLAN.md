# TASK: one canonical worker-contract home (streams.md); advisor references it, no duplicate

slug: spawn-fold · created: 2026-06-23 · stage: mvp
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

Touches (files · symbols · signatures): the spawn/delegation surface, today spread across 3 canonical guides (`add-method/skill/add/`) ×3 trees:
  · `run.md` §"The change scope" (L38–53) — the `touch_boundary` MAY/MUST-NOT block; streams.md copies it ("from run.md").
  · `streams.md` §"The worker contract" (L154–219, the full `PROMPT.md` tag template: objective/persona/touch_boundary/context_files/expertise/tools/return) + §"vendor-neutral tiers" (L221–232, mid/top→sonnet/opus) + §"spawn adapter" (L234–253).
  · `advisor.md` — a SIMPLIFIED PROMPT.md template (objective/persona/context_files/return) that already REFERENCES streams.md for the tags/tiers/adapter; holds the "delegate-not-abdicate" hard rule.
  Duplication to fold: the PROMPT.md tag template (2 copies), the touch_boundary (run.md + streams copy), the "worker proposes / orchestrator records / delegation never lowers a gate" rule (streams boundary + advisor constraints). The tiers are single-sourced in streams.md but live in a parallel-specific guide.
Context (working folder): the fold's scope (resolved at freeze, change-request from v2 → v3): WHAT in advisor.md is a genuine duplicate of streams.md. Verify (v2 build) revealed the split: advisor's `## Choosing the model` tier paraphrase (L56–59, `mid→sonnet / top→opus`) IS a true duplicate of streams' authoritative tier table (L221–232) → fold it to a streams pointer. BUT advisor's `## The plan-following prompt template` (L29–52) is advisory-SPECIFIC content (`<objective>` = "Execute THIS piece {{PIECE}}, verdict-only, do not record state"; `<return>` = `{piece, result, evidence, confidence, open_questions}`) — NOT a duplicate of streams' full locked-task contract (`{{TASK_SLUG}}`, §3 FROZEN/§4 RED, drive src/ green, SUMMARY.md, commit). **Design C′ chosen** (human approval, this change-request): fold ONLY the tier mapping; KEEP advisor's advisory template (it already credits streams for the tag vocabulary + adapter). No new file; streams/run/SKILL untouched. Why C′ over v2's pointer-only C: pointing advisory spawns at streams' task-run contract was a behavior loss (an ill-fitting contract for a one-piece sweep) — the v2 premise "advisor's template is a removable duplicate" was true for the tiers, false for the template.
Honors (patterns / conventions): 3-tree byte parity (canonical→`cp`×2); wording_lint; the worker-PROMPT XML tags are a SEPARATE vocab from the guide 5-tag vocab; `test_xml_convention` pins advisor's narrative headings (`## The plan-following prompt template`, `## Choosing the model — vendor-neutral tiers`) — both headings STAY (template body kept; tier body collapsed to a pointer) so that registry stays untouched; per-step Advisor hook → advisor.md (test_per_step_hooks, unchanged). Behavior-PRESERVING: advisor's advisory template AND streams' contract are both unchanged in substance; only advisor's duplicated tier MAPPING is replaced by a streams pointer.
Anchors the contract cites: streams.md = the tier-table home (mid/top → sonnet/opus, unchanged) · advisor KEEPS its advisory template (the `{{PIECE}}`/verdict-only fenced block) · advisor's `## Choosing the model` body collapses to a streams pointer (no sonnet/opus id mapping duplicated) · run.md touch_boundary single source (unchanged) · test pins: `test_advisor_strategy` (test_template_is_fenced UNCHANGED — advisor keeps its fenced template; test_tier_pick reframed: tier tokens live in streams, advisor references), `test_spawn_fold` (new: advisor's tier section references streams + carries NO sonnet/opus mapping; advisor STILL has its advisory template; streams is the tier home), `test_xml_convention` (advisor narrative headings unchanged → green), `test_skill_lean` (advisor barely changes → pool stays ≤ budget).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Fold the ONE genuinely-duplicated piece of the advisory surface — advisor.md's tier mapping — to a pointer at streams.md's authoritative tier table, single-sourcing it; keep advisor's advisory-specific template intact.
Framings weighed: (C′) fold ONLY the tier mapping; advisor KEEPS its advisory template (CHOSEN — change-request from v2; the template is advisory-specific content, not a duplicate, so only the tiers are a true fold target) · (C, v2) pointer-only — advisor references streams for BOTH template and tiers (REJECTED at this change-request: pointing advisory spawns at streams' full locked-task contract is a behavior loss — an ill-fitting contract for a one-piece sweep) · (A, v1) new neutral `delegation.md` (REJECTED earlier: +1 guide + rippled 4 surface registries + the safety inventory)
Must:
<must>
  - `streams.md` stays the single home of the vendor-neutral tier table (`mid`/`top` → `sonnet`/`opus`) + the spawn adapter (unchanged, not edited by this fold).
  - `advisor.md`'s `## Choosing the model — vendor-neutral tiers` body collapses to a one-line pointer at streams.md — it no longer repeats the `sonnet`/`opus` model-id mapping (the one true duplicate). The heading string STAYS (keeps the `test_xml_convention` narrative registry untouched).
  - `advisor.md` KEEPS its advisory-specific `## The plan-following prompt template` — the fenced `<objective>`/`<persona>`/`<context_files>`/`<return>` block (the `{{PIECE}}`/verdict-only framing). It is NOT a duplicate of streams' locked-task contract; deleting it loses advisory guidance (the v2 finding). It continues to credit streams.md for the shared tag vocabulary + adapter.
  - `run.md` touch_boundary + advisor's `<constraints>` hard rule + streams' worker contract are all UNCHANGED — this fold touches only advisor's tier paraphrase.
  - Behavior-PRESERVING: the assembled ADVISORY prompt (advisor's template) AND the assembled streams worker prompt are both unchanged in substance; only advisor's duplicated tier MAPPING moves to a streams pointer.
  - 3 trees byte-identical; full suite + `add.py check` green; wording_lint clean; the worker-PROMPT XML vocab unchanged. Net advisor bytes not up (the tier duplicate removed); no other guide changes.
  - The tier-fold's test moves red-first (§4) and is ≥ as strict (streams HAS the tier tokens; advisor POINTS at streams and no longer carries the sonnet/opus mapping) — never weakened to pass.
Reject:
<reject>
  - advisor still repeats the sonnet/opus tier model-id mapping (the duplicate survives) -> "duplication_remains"
  - advisor's advisory template is dropped or altered in substance (a tag, the {{PIECE}} framing, the verdict return) -> "behavior_drift"
  - advisor's tier section names streams.md but the anchor is wrong/absent, or streams' tier table is touched -> "broken_reference"
  - an edit diverges the 3 trees -> "parity_break"
  - a pinned test weakened (assertion deleted, not moved) to make the fold pass -> "test_weakened"
</reject>
After:
<after>
  - streams.md is the single tier-table home (unchanged); advisor's tier section points at it (no sonnet/opus duplicate); advisor's advisory template intact; run.md/streams/SKILL unchanged; 3 trees byte-identical; suite + check green; net advisor bytes not up.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] The tier MAPPING (mid→sonnet/top→opus) is the only genuine duplicate worth folding — lowest confidence because the persona block + the proposes-not-records rule are ALSO near-identical between advisor and streams, so a stricter fold could dedup those too; but they are short, advisory-flavored, and folding them risks the same over-removal the v2 build hit on the template. If wrong: a follow-up can fold the persona/rule too (this fold deliberately stops at the clearest duplicate). Cost of stopping here: a few near-duplicate lines remain.
  - [ ] `test_advisor_strategy.test_template_is_fenced` stays UNCHANGED (advisor keeps its fenced template) — reverting the v2 edit that asserted the template moved to streams is a correction to the right premise, not a weakening; test_tier_pick is reframed to assert the tier tokens live in streams + advisor references (≥ strict on the real fold).
  - [ ] `test_skill_lean` needs NO edit under C — advisor only shrinks, so the orchestration pool stays ≤ budget and no guide joins/leaves the pool (verified: no new file). If the pool somehow tightened, that is a separate fence, not this fold's to weaken.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: streams.md is the single tier-table home
  Given the tier table (mid/top → sonnet/opus) lives in streams.md (unchanged)
  When advisor.md's "## Choosing the model" section is read
  Then it references streams.md by name for the tier vocabulary
  And advisor no longer repeats the sonnet/opus model-id mapping

Scenario: advisor keeps its advisory template (behavior-preserving)
  Given advisor's "## The plan-following prompt template" is advisory-specific (the {{PIECE}}/verdict-only block)
  When advisor.md is read after the fold
  Then the fenced <objective>/<persona>/<context_files>/<return> template is still present
  And it still credits streams.md for the shared tag vocabulary + adapter

Scenario: the assembled prompts are unchanged (behavior-preserving)
  Given a dogfood spawn — one advisory subagent (advisor's template) AND one streams worker
  When each PROMPT.md is assembled
  Then both carry the same tags and the same tier tokens as pre-fold
  And no decision the orchestrator makes changes

Scenario: streams' tier table is untouched
  Given streams.md owns the authoritative tier table + spawn adapter
  When advisor's tier section points at it
  Then streams.md is not edited by this fold
  And the tier tokens (mid/top/sonnet/opus) remain in streams.md

Scenario: reject duplication_remains
  Given the fold is applied
  When advisor's "## Choosing the model" section is scanned for the model-id mapping
  Then the sonnet/opus mapping is found only in streams.md
  And a surviving copy in advisor fails the fence -> "duplication_remains"

Scenario: reject behavior_drift
  Given advisor's advisory template is the baseline
  When the post-fold advisor is read
  Then the template's tags + {{PIECE}} framing + verdict return are intact
  And any dropped tag or altered framing fails -> "behavior_drift"

Scenario: reject broken_reference
  Given advisor's tier section references streams.md
  When the reference is resolved
  Then streams.md + its tier-table heading exist
  And a dangling reference fails -> "broken_reference"

Scenario: reject parity_break
  Given canonical is edited
  When propagated
  Then the 3 trees are md5-identical
  And divergence fails -> "parity_break"

Scenario: reject test_weakened
  Given a test pinned the old location
  When the structure moves
  Then the test moves with it and is >= as strict (reference + tokens-in-source asserted)
  And a deleted/loosened assertion fails -> "test_weakened"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FOLD advisor-tier-mapping   body: { tier_home: "streams.md" (unchanged), refs_from: [advisor.md "## Choosing the model"] }
  200 -> { tier_sources: 1, advisor_template: "kept (advisory-specific)", streams: "untouched",
           touch_boundary_home: "run.md", trees_identical: true, suite: "green", net_bytes: "not up" }
  4xx -> { error: "duplication_remains" | "behavior_drift" | "broken_reference"
                 | "parity_break" | "test_weakened" }
Schema:
  HOME streams.md — UNCHANGED. Stays the authoritative tier table `## Choosing the model — vendor-
       neutral tiers` (mid/top → sonnet/opus) + `## The spawn adapter` + `## The worker contract`
       (the full locked-task PROMPT.md). NOT edited by this fold.
  EDIT advisor.md  → in `## Choosing the model — vendor-neutral tiers` ONLY: replace the body that
       repeats the sonnet/opus model-id mapping with a one-line pointer at streams.md's tier table
       (name streams.md; may keep the conceptual mid/top, drop the sonnet/opus id mapping). KEEP the
       heading string. KEEP everything else in advisor UNCHANGED — intro, `## When to spawn`, the
       advisory `## The plan-following prompt template` (its fenced {{PIECE}}/verdict block stays),
       the `<constraints>` hard rule, the footer.
  UNCHANGED run.md, SKILL.md, streams.md — no pointer or one-liner changes needed.
  PROPAGATE advisor.md canonical → .claude/skills/add/advisor.md + add-method/src/add_method/_bundled/skill/add/advisor.md.
  TESTS (red-first, ≥ as strict):
       · test_advisor_strategy — test_template_is_fenced UNCHANGED (advisor keeps its fenced
         advisory template); test_tier_pick reframed: tier tokens (mid/top/sonnet/opus) asserted in
         STREAMS.md, advisor asserted to reference streams.md for the tier vocabulary.
       · test_spawn_fold (NEW) — advisor's tier section references streams.md AND no longer carries
         the sonnet/opus mapping; advisor STILL has its fenced advisory template ({{PIECE}}/verdict);
         streams.md is the tier-table home (tokens present) and is byte-untouched.
  UNCHANGED test_skill_lean (advisor barely changes → pool ≤ budget), test_xml_convention (advisor's
       two narrative headings kept → registry untouched), test_streams, test_per_step_hooks.
  Measurement: net advisor bytes not up vs pre-fold; `add.py check` + full suite green.
```

Status: FROZEN @ v3 — approved by Tin Dang (Design C′ change-request from v2: fold ONLY the duplicated tier mapping; advisor keeps its advisory-specific template — the v2 build's pointer-only fold was a behavior loss for the advisory path)

Least-sure flag surfaced at freeze: [contract] this fold stops at the tier mapping — the only unambiguous duplicate. Why it could be wrong: advisor's persona block + the proposes-not-records rule are ALSO near-identical to streams', so a maximal fold would dedup those too; but v2 proved over-folding the advisory surface loses fitted content, so this fold deliberately takes only the clearest duplicate. Cost: a few near-duplicate advisory lines remain (a follow-up can revisit). v2's pointer-only fold was REJECTED because pointing advisory spawns at streams' locked-task contract was an ill fit (behavior loss); v1's delegation.md was REJECTED for a 4-registry + safety-inventory ripple.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a fence; behavior-equivalence asserted structurally
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_streams_is_tier_home (test_spawn_fold): assert streams.md carries the tier tokens (mid/top/sonnet/opus) — the authoritative table (the one home)
  - test_advisor_tier_section_references_streams (test_spawn_fold): assert advisor's `## Choosing the model` section body names `streams.md` AND no longer contains BOTH `sonnet` and `opus` (the model-id mapping is folded away) (fences "duplication_remains" + "broken_reference")
  - test_advisor_keeps_advisory_template (test_spawn_fold): assert advisor STILL has its fenced advisory template — `<objective>`/`<persona>`/`<return>` paired tags present (fenced) AND the `{{PIECE}}` framing AND the verdict-only "do not record state" rule (fences "behavior_drift" — the v2 over-removal)
  - test_streams_tier_table_untouched (test_spawn_fold): assert streams.md still owns the sonnet/opus mapping (the fold did not move it out of streams)
  - (existing) test_advisor_strategy.test_template_is_fenced — UNCHANGED: advisor keeps its fenced template (objective/persona/return present + fenced). Reverts the v2 edit (correction to the right premise, not a weakening).
  - (existing, reframed ≥ as strict) test_advisor_strategy.test_tier_pick_reuses_streams: the tier tokens (mid/top/sonnet/opus) asserted in STREAMS.md (the home); advisor asserted to reference streams.md for the tier vocabulary.
  - UNCHANGED (carried by the full suite, must stay green): test_skill_lean, test_xml_convention (advisor narrative headings kept), test_streams, test_per_step_hooks, parity, wording_lint
</test_plan>

Tests live in: `add-method/tooling/test_spawn_fold.py` (new) + edits to `add-method/tooling/test_advisor_strategy.py` · MUST run red before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/advisor.md` `.claude/skills/add/advisor.md` `add-method/src/add_method/_bundled/skill/add/advisor.md` `add-method/tooling/test_spawn_fold.py` `add-method/tooling/test_advisor_strategy.py`
Strategy (ordered batches): 1. edit advisor.md (canonical) — in `## Choosing the model — vendor-neutral tiers` ONLY: replace the body repeating the sonnet/opus model-id mapping with a one-line pointer at streams.md's tier table (drop the id mapping; the conceptual mid/top may stay). Touch nothing else — the advisory template + intro + `<constraints>` + footer stay byte-for-byte. 2. propagate advisor.md ×2 (cp) 3. update the tests green (test_spawn_fold for C′ + reframe test_advisor_strategy.test_tier_pick; revert test_template_is_fenced to its original).
Safety rule (feature-specific): the ONLY advisor change is the tier-section body — diff advisor against HEAD and confirm the diff is confined to `## Choosing the model`; the fenced advisory template (`{{PIECE}}`/verdict) must be byte-identical to HEAD (no behavior_drift). streams.md is NOT touched.
Code lives in: `add-method/skill/add/` (canonical) → propagated to the other 2 trees
Constraints: behavior-preserving fold; tests move red-first as declared in §4 (re-spec, never weaken); 3 trees byte-identical; allow-list only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1560 OK (`python3 -m unittest discover`); `add.py check` 377/0
- [x] coverage did not decrease — added test_spawn_fold (4 tests for C′); advisor still covered by test_advisor_strategy + test_xml_convention + test_skill_lean + test_per_step_hooks
- [x] no test or contract was altered during build — build touched ONLY advisor.md ×3; the §4 tests + §3 contract were written/frozen before the tests→build advance (tripwire snapshot clean)
- [x] the green was EARNED, not gamed — adversarial refute-read (manual, change is small/contained): the RED test passed because the sonnet/opus mapping was genuinely removed from advisor (not by loosening); the pool test passed because advisor genuinely shrank (−65 B vs HEAD); no vacuous asserts. Notably the refute-read on the v2 build CAUGHT the over-removal (advisory template is not a duplicate) → this C′ build corrects it.
- [x] concurrency / timing — N/A (doc-only fold; no IO/runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A (prose)
- [x] layering & dependencies follow CONVENTIONS.md — advisor still references streams as the tier home; no new file, no new dependency
- [x] a person reviewed and approved the change — the human (Tin Dang) chose the C′ design at the change-request; gate auto-resolved on evidence under `autonomy: auto`, naming this run (not a forged signature)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] advisor's `## Choosing the model` section names streams.md and NO LONGER prints the sonnet/opus model-id mapping — confirmed by `git diff` (the two mapping lines removed; "streams.md" present) + manual read of advisor.md L54–57
- [x] advisor's advisory template (`## The plan-following prompt template`, the fenced `{{PIECE}}`/verdict block) is byte-identical to HEAD — confirmed by `git diff --stat` (only 4 ins/4 del, all inside the tier section; the template lines unchanged)
- [x] streams.md is byte-untouched and still owns the tier mapping — confirmed by `git status` (streams.md not modified) + test_streams_tier_table_untouched green
- [x] net advisor bytes DOWN, 3 trees byte-identical — confirmed by byte measure (3830→3765, −65) + md5 (all three trees `d326373…`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read advisor.md L54–57 in full: the pointer correctly directs the reader to streams.md's `## Choosing the model — vendor-neutral tiers` (which exists, L221) for the authoritative tier→model-id mapping + adapter; the conceptual mid/top stays for orientation; "high-risk still escalates" rule retained. No advisory content lost (the {{PIECE}} template is intact). No dangling reference.

### GATE RECORD
Outcome: PASS
Auto-resolved by: ADD verify auto-gate (run: spawn-fold C′ build, autonomy=auto) · date: 2026-06-23
Human direction approval: Tin Dang chose Design C′ at the v2→v3 change-request (the fold scope)
Residue: none (doc-only · no security/concurrency/architecture · behavior-preserving for both prompts)

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
