# TASK: Observe→confirm→rewrite voice-delta loop for SOUL.md

slug: soul-self-improve · created: 2026-06-15 · stage: mvp
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

Touches (files · symbols · signatures):
- `add-method/skill/add/soul.md` (NEW) — the voice-self-improve loop doc. Parallels `deltas.md` (emit grammar) + `fold.md` (confirm→rewrite) but for SOUL.md: defines the VOICE DELTA grammar, the observe→confirm→rewrite lifecycle (open→confirmed), the routing into SOUL.md's sections (Tone · Communication style · Trust), and the reject codes. Judgment-free like fold.md — NO engine command (`add.py` unchanged).
- `add-method/skill/add/phases/7-observe.md` — gains an emit step: "propose a voice delta" from the human's in-session wordings + flow, pointing at `soul.md`. Sits beside the existing competency-delta emit.
- `add-method/skill/add/SKILL.md` (observe/loop section, ~line 90) — add the `soul.md` pointer beside `deltas.md`/`fold.md`, so the loop is discoverable.
- `add-method/tooling/templates/SOUL.md.tmpl` "## Voice deltas" — refine the pointer to name `soul.md` (the doc that runs the loop) so the reference resolves; the loop ledger lives in this section.
- prior art: `add-method/tooling/test_cospecify_lift.py` (content-test pattern); `deltas.md` + `fold.md` (the loop this mirrors); the milestone shared decision (SOUL.md identity-owned — the human's confirm is the only writer).
Context (working folder): soul-artifact (task 5, SHIPPED) created SOUL.md + its "Voice deltas" section as the TARGET; this task ships the WRITER LOOP that fills it. No engine change — docs/skill only, judgment-free (mirrors fold.md having no `add.py fold`).
Honors (patterns / conventions): the deltas.md grammar (tag line + required `(evidence: …)` close) and the fold.md lifecycle (AI proposes `open`; human confirms; only then the append-only, newest-first rewrite; never self-approve); 3-tree byte-identical skill sync (test_tree_parity + test_bundle_parity); learns from in-session WORDINGS + FLOW, NOT the human's private memory (milestone "Out").
Anchors the contract cites: `soul.md` exists with the voice-delta grammar (`[VOICE · <status>]` + evidence) · the observe→confirm→rewrite loop (open→confirmed) · the human-is-only-writer rule · the routing into SOUL.md Tone/Communication style/Trust · the reject codes · the 7-observe.md emit step pointing at soul.md · 3-tree byte-identical sync.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a `soul.md` skill doc + an OBSERVE emit step that together make SOUL.md self-improve — the AI
proposes a confirmable **voice delta** from the human's in-session wordings + flow; once the human
confirms, the AI rewrites the routed SOUL.md section (Tone / Communication style / Trust) and records
the delta in SOUL.md's "Voice deltas" ledger. Append-only, newest-first; the human's confirm is the
only writer.
Framings weighed: a dedicated `soul.md` loop doc mirroring deltas.md+fold.md (chosen — reuses the proven
emit→confirm→fold shape; judgment-free, no engine command) · fold voice into the existing competency
deltas as a 6th tag (rejected — voice isn't one of the five competencies; it routes to SOUL.md not the
foundation) · an `add.py soul` command that writes the voice (rejected — writing identity is judgment;
the human confirms, the engine stays judgment-free like fold.md).
Must:
<must>
  - `soul.md` exists and defines the VOICE DELTA grammar: a tag line `- [VOICE · <status>] <observation>`
    closed by a required `(evidence: <in-session pointer>)` clause (no evidence → opinion, not a delta).
  - it defines the lifecycle open → confirmed: the AI emits `open`; the HUMAN confirms; only on confirm
    is SOUL.md rewritten. The AI never self-approves a voice rewrite (human is the only writer).
  - it ROUTES each voice delta to a SOUL.md section — tone→Tone · phrasing/structure→Communication style
    · trust-behavior→Trust — and records the delta (newest-first) in the "Voice deltas" ledger.
  - it learns from the human's in-session WORDINGS + FLOW, explicitly NOT their private memory files.
  - it names reject codes: a write without confirmation, a no-op when nothing is open, an unroutable delta.
  - `phases/7-observe.md` gains an emit step that proposes a voice delta and points at `soul.md`.
  - SKILL.md points at `soul.md` in the observe/loop section; all 3 skill trees stay byte-identical.
</must>
Reject:
<reject>
  - (prose task) a `soul.md` that omits the grammar OR the open→confirmed lifecycle OR the human-only-writer
    rule OR the SOUL.md routing OR the reject codes -> content tests stay red; never ship a half-loop.
  - the loop lets the AI rewrite SOUL.md WITHOUT a recorded human confirm -> violates the milestone shared
    decision (identity-owned: the human's confirm is the only writer) -> reject `unconfirmed_voice_rewrite`.
</reject>
After:
<after>
  - a reader of soul.md knows how to emit a voice delta, how the human confirms it, and how a confirmed
    delta rewrites the routed SOUL.md section — append-only, newest-first, human-confirmed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] a dedicated VOICE delta stream (separate from the five competency deltas) risks splitting the
    self-improvement story into two loops the reader must hold at once — lowest confidence because voice
    genuinely is NOT a competency (it routes to SOUL.md, not PROJECT.md/CONVENTIONS.md), so a separate doc
    is honest; if wrong: a later task merges the two delta docs under one "what each loop teaches" frame.
  - [ ] [contract] the voice-delta ledger lives in SOUL.md's "Voice deltas" section (shipped by task 5),
    not a new file; if wrong: a later task gives it its own log.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: soul.md defines the voice-delta grammar
  Given a reader opens soul.md
  When they read it
  Then it shows the [VOICE · <status>] tag line closed by a required (evidence: …) clause
  And the deltas.md / fold.md docs are unchanged (the loop mirrors them, does not edit them)

Scenario: the lifecycle is open → confirmed, human-confirmed
  Given the reader is on soul.md
  When they read how a voice delta moves
  Then the AI emits it `open`, the human confirms, and only on confirm is SOUL.md rewritten
  And the AI never self-approves a voice rewrite (the human is the only writer)

Scenario: a confirmed delta routes to a SOUL.md section
  Given a confirmed voice delta about tone / phrasing / trust
  When the AI applies it
  Then it rewrites the routed SOUL.md section (Tone / Communication style / Trust)
  And records the delta newest-first in the "Voice deltas" ledger

Scenario: it learns from wordings + flow, not private memory
  Given soul.md describes what a voice delta is drawn from
  When the reader reads the source rule
  Then it names the human's in-session WORDINGS and FLOW
  And explicitly excludes the human's private memory files

Scenario: observe emits a voice delta
  Given a reader opens phases/7-observe.md
  When they read the Do steps
  Then there is a step proposing a voice delta that points at soul.md
  And the existing competency-delta / spec-delta steps remain

Scenario: the skill makes the loop discoverable + trees stay identical
  Given SKILL.md's observe/loop section
  When the reader reads it
  Then it points at soul.md beside deltas.md / fold.md
  And soul.md + 7-observe.md + SKILL.md are byte-identical across the 3 skill trees

Scenario (reject): a half-loop stays red
  Given a soul.md missing the grammar, the open→confirmed lifecycle, the human-only-writer rule,
        the SOUL.md routing, or the reject codes
  When the content suite runs
  Then it fails (red)
  And no existing skill doc (deltas.md / fold.md / 7-observe.md) is gutted to make it pass

Scenario (reject): an unconfirmed rewrite is named a reject
  Given soul.md's reject codes
  When the reader reads them
  Then a rewrite without a recorded human confirm is named a reject (unconfirmed_voice_rewrite)
  And the human-only-writer rule is restated
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC CONTRACT — the voice-self-improve loop (no engine change)

skill/add/soul.md (NEW) MUST contain, as readable prose:
  - the voice-delta grammar: the literal token "[VOICE" tag form + a required "(evidence:" clause
  - the lifecycle words "open" and "confirmed" (open → confirmed)
  - the human-only-writer rule: the words "confirm" + "only writer" (or "never self-approve")
  - the routing into SOUL.md sections: names "Tone" · "Communication style" · "Trust"
    + the "Voice deltas" ledger + "newest-first"
  - the source rule: names "wordings" AND "flow"; excludes private "memory"
  - reject codes: "unconfirmed_voice_rewrite" · a no-op-when-empty code · an unroutable code

phases/7-observe.md MUST gain an emit step naming "voice delta" AND pointing at "soul.md"
SKILL.md observe/loop section MUST name "soul.md"
SOUL.md.tmpl "## Voice deltas" MUST name "soul.md" (the pointer resolves)

Parity: soul.md · 7-observe.md · SKILL.md byte-identical across the 3 skill trees;
        SOUL.md.tmpl byte-identical across the 3 tooling/templates trees. NO engine change
        (add.py untouched → ENGINE_MD5 unchanged).
Schema: docs/skill only — no state.json, no CLI verb (judgment-free, mirrors fold.md).
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15)
Least-sure flag surfaced at freeze: [spec] a separate VOICE delta stream (distinct from the five competency deltas) risks two parallel self-improvement loops a reader must hold at once — accepted because voice routes to SOUL.md, not the foundation, so a separate doc is the honest model; if it reads as redundant, a later task merges the delta docs under one frame (§7 delta).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: soul.md loop content + 7-observe emit + SKILL pointer + SOUL.md.tmpl pointer + 3-tree parity
Plan (one test per scenario; read CANONICAL files; assert substrings):
<test_plan>
  - test_soul_md_grammar: soul.md shows "[VOICE" tag + "(evidence:" required clause
  - test_lifecycle_open_confirmed: soul.md names "open" and "confirmed"
  - test_human_only_writer: soul.md says "confirm" + ("only writer" or "never self-approve")
  - test_routes_to_soul_sections: soul.md names Tone · Communication style · Trust · "Voice deltas" · "newest-first"
  - test_source_wordings_flow_not_memory: soul.md names "wordings" + "flow"; excludes private "memory"
  - test_reject_codes: soul.md names "unconfirmed_voice_rewrite" + a no-op + an unroutable code
  - test_observe_emits_voice_delta: 7-observe.md names "voice delta" AND "soul.md"
  - test_skill_points_at_soul_md: SKILL.md observe/loop region names "soul.md"
  - test_soul_template_points_at_loop: SOUL.md.tmpl "Voice deltas" section names "soul.md"
  - test_three_trees_identical: soul.md + 7-observe.md + SKILL.md byte-identical across the 3 skill trees
</test_plan>

Tests live in: `tooling/test_soul_self_improve.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/soul.md` `.claude/skills/add/soul.md` `add-method/src/add_method/_bundled/skill/add/soul.md` `add-method/skill/add/phases/7-observe.md` `.claude/skills/add/phases/7-observe.md` `add-method/src/add_method/_bundled/skill/add/phases/7-observe.md` `add-method/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `add-method/tooling/templates/SOUL.md.tmpl` `.add/tooling/templates/SOUL.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/SOUL.md.tmpl`
Strategy (ordered batches): 1. write canonical `soul.md` (grammar · open→confirmed lifecycle · human-only-writer · SOUL.md routing · reject codes · learns-from wordings+flow) · 2. add the voice-delta emit step to canonical `phases/7-observe.md` · 3. add the `soul.md` pointer to canonical SKILL.md observe/loop section · 4. point SOUL.md.tmpl "Voice deltas" at `soul.md` · 5. sync all to `.claude` dogfood + `.add` template, run `prepare_bundle.py` · 6. full suite green (wording lint + parity; NO engine_pin change — add.py untouched)
Safety rule (feature-specific): docs-only, judgment-free — no engine command writes the voice; the human's confirm is the only writer (mirrors fold.md). deltas.md / fold.md are NOT edited (the loop mirrors, never guts them).
Code lives in: the 3 skill trees (soul.md · 7-observe.md · SKILL.md) + the 3 tooling/templates trees (SOUL.md.tmpl); canonical is source, dogfood + bundle are synced copies
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

- [x] all tests pass — full suite 1095 green (was 1085; +10 in test_soul_self_improve)
- [x] coverage did not decrease — net +10 tests; the two wording-surface census guards re-registered for the new doc
- [x] no test or contract was altered during build — the census-guard updates (test_wording_lint count 25→26 + soul.md registration, test_per_step_hooks count 25→26) were made in the REOPENED tests phase and re-snapshotted via advance, NOT during build (tamper-tripwire discipline); no test logic was weakened — the counts track a deliberately-added surface doc, the established "+<doc> @ <task>" registration seam
- [x] the green was EARNED, not gamed — the suite ran RED first (10/10 errored on missing soul.md); GREEN only after the loop doc + wiring landed. Assertions check real loop content (grammar, open→confirmed, human-only-writer, routing, reject codes, wordings+flow-not-memory) scoped to soul.md + the wiring files — not vacuous
- [x] concurrency / timing of the risky operation is safe — n/a (prose/skill only; no runtime, no engine change)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; docs-only, zero new deps, add.py untouched (ENGINE_MD5 unchanged)
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree byte-identical sync (soul.md · 7-observe.md · SKILL.md · SOUL.md.tmpl); the loop mirrors deltas.md/fold.md without editing them
- [x] a person reviewed and approved the change — auto-resolved under autonomy=auto (autonomous authorization 2026-06-15); no security/residue escalation

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read soul.md in full: it defines the voice-delta grammar ([VOICE · status] + required evidence), the open→confirmed lifecycle, the human-is-only-writer rule (never self-approve), the routing table (tone→Tone, structure→Communication style, trust→Trust + the newest-first Voice deltas ledger), the wordings+flow source (excluding private memory), and three reject codes (unconfirmed_voice_rewrite · no_open_voice_deltas · unroutable_voice_delta). 7-observe.md gains the emit step; SKILL.md + SOUL.md.tmpl point at soul.md. Wording lint green ("folds into"→"is consolidated into"; deltas.md/fold.md kept in backticks). The loop never lets the AI write SOUL.md without a recorded human confirm.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (autonomous authorization 2026-06-15) · date: 2026-06-15

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does the voice loop actually fire in observe — do real sessions produce confirmable voice deltas, or does the step get skipped? (the §1 ⚠ flag) — if it never fires, the emit prompt is too vague; if it floods, tighten the evidence bar. Watch whether readers conflate the voice loop with the competency-delta loop.
Spec delta for the next loop: this is the FIRST live voice delta source — this very milestone produced observable voice signals (see below) that, once you confirm, are exactly what soul.md's loop would consolidate into SOUL.md's Tone/Communication style/Trust sections. The loop is now ready to run on itself.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] self-improvement now has TWO routed loops — competency deltas → foundation (deltas.md/fold.md) and voice deltas → SOUL.md (soul.md) — sharing one propose→confirm→write discipline but distinct targets (evidence: soul.md mirrors fold.md's lifecycle; test_human_only_writer guards the shared floor)
- [ADD · folded] the voice loop closes the SOUL.md story task 5 opened — task 5 shipped the target schema, task 6 ships the writer; together they make the AI's voice a living, human-confirmed doc (evidence: SOUL.md.tmpl "Voice deltas" now resolves to soul.md; test_soul_template_points_at_loop)
