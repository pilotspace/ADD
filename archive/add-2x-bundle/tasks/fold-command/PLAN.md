# TASK: add.py fold — mechanize competency-delta consolidation (flip+stamp+route+bump)

slug: fold-command · created: 2026-06-16 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/tooling/add.py:_DELTA_RE` (3828) — competency grammar `- [DDD|SDD|UDD|TDD|ADD · open|folded|rejected] <text>`; the `open` lines are what fold flips.
- `add-method/tooling/add.py:_collect_open_deltas` (3943) — READ-ONLY scan of every task's `### Competency deltas` block → `{comp: [{task,text,evidence}]}` (canonical order). Fold's source of truth for WHAT to fold — fold is its mutating sibling.
- `add-method/tooling/add.py:_SPEC_OPEN_TOKEN_RE` + `_resolve_spec_delta` (4057/4060) — the PURE first-open token-flip to MIRROR. New `_COMP_OPEN_TOKEN_RE` + `_fold_competency_delta(text, version)` flips EVERY `[<COMP> · open]`→`folded` in a TASK.md and appends ` [folded foundation-version N]`, byte-preserving the line's text + `(evidence: …)`.
- `add-method/tooling/add.py:cmd_drop_delta` (546) + its subparser — sibling resolution-verb shape to mirror for `cmd_fold` + the `fold` subparser.
- `add-method/tooling/add.py:cmd_deltas` (4618) — the read-only reporter; fold is its mutating counterpart over the same collector.
- `add-method/tooling/add.py:_atomic_write` (159) — temp-file + `os.replace` per-file atomic write; the validate-ALL-then-write-N-files spine.
- `add-method/tooling/add.py:_COMPETENCY_ORDER`/`_DELTA_STATUSES` (3820) · `_EVIDENCE_RE` (3831) — canonical competency set + evidence splitter.

Context (working folder):
- `.add/PROJECT.md` — header `… · foundation-version: 35` (l.8 — the int fold bumps); `## Domain (DDD)` (l.14); `## Spec / Living Document (SDD)` (l.37); `## Key Decisions` table `| date | decision | why | outcome |` (l.256–258 — newest-first prepend point, row 1 goes right below the `|---|` separator). NO `## Users (UDD)` section exists → a UDD/DDD route to a MISSING section is a real fail-closed case.
- `.add/CONVENTIONS.md` — `## Method learnings (folded from OBSERVE deltas)` (l.28); bullet form `- (TAG) **title.** prose` — the TDD/ADD route target.
- `add-method/skill/add/fold.md` (+ `add-method/src/add_method/_bundled/skill/add/fold.md` twin) — TODAY says "there is no `add.py fold`; the consolidation lives here so the engine stays judgment-free" (l.14) + routing table (l.24–35) + reject codes `no_open_deltas`/`unconfirmed_fold`/`unroutable_delta` (l.47–53). This task REWRITES it to describe the command.
- `add-method/tooling/test_min_pillar.py` — `LIFECYCLE` census (l.56) derives the command set from `sub.choices` DYNAMICALLY (l.187); `_NONZERO_OK` (l.120). A new SUBCOMMAND ripples here.
- Real fold target now: 7 open competency deltas — SDD 1 · TDD 2 · ADD 4 (no DDD, no UDD) across spec-delta-grammar / seed-and-drop / spec-delta-guards.

Honors (patterns / conventions):
- CONVENTIONS.md l.21 — errors machine-readable `add: error: <msg>`; l.25 — the Python tool is the only state writer, writes atomic + never clobber; append-only is newest-first (compaction door).
- fold.md — "each consolidation SESSION bumps `foundation-version` by one"; the batch design (one call → one bump → one stamp value) honors it.
- ADD delta (seed-and-drop): a new SUBCOMMAND must be pre-listed in §5 with test_min_pillar's LIFECYCLE + `_NONZERO_OK` census — `fold` with no open deltas refuses `no_open_deltas` (nonzero, like `drop-delta`).
- ADD delta (spec-delta-grammar): an add.py parser change ripples to the 3 byte-identical dogfood copies + `engine_pin.py` + test mirrors — pre-list them in §5.
- ADD delta (spec-delta-guards): scan downstream test assertions BEFORE freezing an additive engine change (pre-freeze downstream analysis killed all mid-build surprises in task 3).

Anchors the contract cites: `cmd_fold` · the `fold` subparser · `_fold_competency_delta` (pure flip+stamp) · `_COMP_OPEN_TOKEN_RE` · `_collect_open_deltas` (source) · `_atomic_write` · PROJECT.md `foundation-version:` header + `## Key Decisions` table · CONVENTIONS.md `## Method learnings` · the competency→target routing map · reject codes `no_open_deltas` / `unroutable_delta` / `missing_route_section`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py fold [--task <slug>] [--comp <TAG>]` — mechanize ONE competency-delta consolidation session in a single atomic call: flip every open competency delta to `folded`, stamp `[folded foundation-version N]`, transcribe it verbatim into its routed foundation section, prepend one §Key-Decisions session row, and bump `foundation-version` exactly once. Running the command IS the human's confirmation (fold.md's `unconfirmed_fold` is satisfied by invocation); the engine adds NO editorial judgment beyond deterministic routing + verbatim transcription.
Framings weighed: batch, one-bump-per-session, transcribe-and-route (chosen — honors the human's "also write content" pick + fold.md's "one session, one bump") · bookkeeping-only flip+stamp+bump (rejected — human chose to also write content) · per-delta bump (rejected — breaks "one session, one bump") · engine COMPOSES/consolidates prose (rejected — that is the judgment the method keeps human-owned).
Must:
<must>
  - Collect every OPEN competency delta project-wide via `_collect_open_deltas`; optional `--task <slug>` and/or `--comp <TAG>` narrow the set — still ONE bump for the call.
  - Compute N = current `foundation-version` + 1 (one monotonic int for the whole session); every flipped delta carries the SAME N.
  - For each selected delta: flip `[<COMP> · open]` → `[<COMP> · folded]` in its task's §7 and append ` [folded foundation-version N]`, byte-preserving the line's text + `(evidence: …)` (mirror `_resolve_spec_delta`/`_SPEC_OPEN_TOKEN_RE`).
  - Route + transcribe: prepend each folded delta VERBATIM as one bullet at the TOP (newest-first) of its routed section — DDD→PROJECT.md §Domain · SDD→§Spec · UDD→§Users · TDD/ADD→CONVENTIONS.md §Method learnings. Transcription only — never invent or merge prose.
  - Prepend ONE §Key-Decisions row to PROJECT.md (newest-first, directly below the `|---|` separator): `| <today> | fold <scope> → foundation-version N (<per-competency counts>) | consolidate captured OBSERVE deltas into the versioned foundation | <K> deltas open→folded; +<K> routed bullets; <N-1>→N |`. A mechanical skeleton the human may later polish/consolidate.
  - Bump the PROJECT.md header `foundation-version: <N-1>` → `<N>` exactly once.
  - Validate ALL preconditions (≥1 open delta in scope · every routed section present · parseable `foundation-version:`) and compute every edit in-memory BEFORE writing ANY file; write each touched file via `_atomic_write`; on any failure write NOTHING.
  - Print a summary: K deltas folded · per-competency counts · `<N-1>`→`<N>` · files touched.
</must>
Reject:
<reject>
  - no open competency delta in the selected scope -> "no_open_deltas"   (no bump, no write)
  - a delta routes to a foundation section that does not exist (e.g. a UDD delta with no `## Users` section) -> "missing_route_section"   (fail-closed; the human adds the header + re-runs)
  - PROJECT.md has no parseable `foundation-version:` header -> "no_foundation_version"
  (a bad `--comp` value is rejected by argparse `choices`; routing is TOTAL over the five competencies, so there is no reachable command-level `unroutable_delta` — it stays a unit invariant, not a contract reject.)
</reject>
After:
<after>
  - every selected open competency delta is `folded` + stamped `[folded foundation-version N]`; none left open in scope.
  - each folded delta appears verbatim exactly once at the top of its routed section.
  - exactly one new §Key-Decisions row; `foundation-version` == N; one bump.
  - on ANY reject: the whole tree + state are byte-unchanged (validate-all-then-write).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "write content" means TRANSCRIBE verbatim, NOT CONSOLIDATE — lowest confidence because this foundation's fold history ALWAYS merges N deltas into fewer re-worded bullets ("17→5, keeps it one-screen"), which a judgment-free engine cannot do. So fold leaves RAW per-delta bullets the human consolidates afterward (the compaction door already supports this). If you'd rather not have the engine touch foundation prose at all, drop the "route + transcribe" Must → fold writes only flip+stamp+bump + the §Key-Decisions row (option B), and you keep authoring the consolidated bullets by hand. DECIDE AT THE FREEZE. If wrong: the engine bloats the foundation off one-screen until you consolidate.
  - [ ] missing-route-section is FAIL-CLOSED (refuse), not auto-create — auto-creating a `## Users` header is a placement judgment we avoid. Confirm.
  - [ ] one §Key-Decisions row PER SESSION (not per delta), engine-templated skeleton (why/outcome), human-polished. Confirm.
  - [ ] `--task` / `--comp` filters ship in v1 (cheap — filter the collected dict; user named them). Confirm vs deferring as a SPEC delta.
  - [ ] today's date comes from the SAME source as new-task's `created:` stamp. Confirm date provenance.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fold_all_in_one_session
  Given tasks holding open competency deltas across competencies (an SDD delta + an ADD delta)
    And PROJECT.md header reads "foundation-version: N-1"
  When I run `add.py fold`
  Then every open competency delta is flipped "[<COMP> · folded] … [folded foundation-version N]" in its task §7
    And the SDD delta's text appears verbatim as a new bullet at the TOP of PROJECT.md "## Spec"
    And the ADD delta's text appears verbatim as a new bullet at the TOP of CONVENTIONS.md "## Method learnings"
    And exactly one new row is prepended to PROJECT.md "## Key Decisions" naming the per-competency counts and "foundation-version N"
    And the header now reads "foundation-version: N" (bumped exactly once)
    And the summary prints the count folded and "N-1 -> N"

Scenario: filter_narrows_scope
  Given task A and task B each hold one open competency delta
  When I run `add.py fold --task A`
  Then only task A's delta is folded and stamped
    And task B's delta is left "[<COMP> · open]" (untouched)
    And foundation-version bumped exactly once (one session, one bump)

Scenario: no_open_deltas_refuses
  Given no task holds an open competency delta
  When I run `add.py fold`
  Then it exits non-zero with "no_open_deltas"
    And foundation-version is unchanged and no file was written (tree + state byte-identical)

Scenario: missing_route_section_refuses_atomically
  Given an open UDD delta exists but PROJECT.md has no "## Users" section
    And a co-occurring open SDD delta would route cleanly to "## Spec"
  When I run `add.py fold`
  Then it exits non-zero with "missing_route_section"
    And the SDD delta is STILL "[SDD · open]" and "## Spec" is untouched (validate-all-then-write — nothing written)
    And foundation-version is unchanged

Scenario: no_foundation_version_refuses
  Given an open competency delta exists but PROJECT.md has no parseable "foundation-version:" header
  When I run `add.py fold`
  Then it exits non-zero with "no_foundation_version"
    And no file was written (tree + state byte-identical)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI  add.py fold [--task <slug>] [--comp {DDD,SDD,UDD,TDD,ADD}]
  exit 0 -> stdout: "folded <K> deltas -> foundation-version <N>"
                    "  <COMP>:<k> …            (per-competency counts, canonical order)"
                    "  bumped PROJECT.md  <N-1> -> <N>"
                    "  files: <touched paths>"
  exit 1 -> "add: error: <code>"   code ∈ { no_open_deltas, missing_route_section, no_foundation_version }

Behavior (the frozen seam):
  source    : _collect_open_deltas(root) → {comp: [{task,text,evidence}]}; --task and/or --comp FILTER the set.
  version   : N = int(PROJECT.md `foundation-version:`) + 1 — ONE bump per call; every stamp carries the SAME N.
  flip      : in each selected task's §7, every `[<COMP> · open]` → `[<COMP> · folded]` + append ` [folded foundation-version N]`
              via _fold_competency_delta (mirror of _resolve_spec_delta/_COMP_OPEN_TOKEN_RE; line text + `(evidence: …)` byte-preserved).
  route     : DDD→PROJECT.md `## Domain` · SDD→PROJECT.md `## Spec` · UDD→PROJECT.md `## Users`
              · TDD,ADD→CONVENTIONS.md `## Method learnings`.  The map is TOTAL over the five competencies.
  transcribe: prepend ONE verbatim bullet per folded delta at the TOP of its routed section (newest-first), uniform shape:
              "- (<COMP>) <text> (evidence: <evidence>)  [folded foundation-version N · from <task>]"
              (raw transcription — never invented/merged; the human consolidates later via the compaction door.)
  decisions : prepend ONE row below the `## Key Decisions` `|---|` separator (newest-first):
              "| <today> | fold <scope> → foundation-version N (<counts>) | consolidate captured OBSERVE deltas into the versioned foundation | <K> deltas open→folded; +<K> routed bullets; <N-1>→N |"
              (<scope> = "all" with no filter, else the filter expression; <today> = same source as new-task `created:`.)
  bump      : header `foundation-version: <N-1>` → `<N>`, exactly once.
  atomic    : validate ALL (≥1 selected open delta · EVERY routed section present · parseable header) and build every new
              file body in memory FIRST; only then _atomic_write each. Any failure → write NOTHING (whole tree byte-unchanged).

Files touched (only on exit 0): each selected `.add/tasks/<slug>/TASK.md` · `.add/PROJECT.md` · `.add/CONVENTIONS.md` (only when a TDD/ADD delta is in scope).
state.json: UNCHANGED — fold is a foundation/docs op, not a task-state transition.
Names (match GLOSSARY): "fold" (consolidation) · "foundation-version" · "competency delta"; the `[folded foundation-version N]` stamp matches the existing hand-written form byte-for-byte.
```

Least-sure flag surfaced at freeze: [contract] "write content" = TRANSCRIBE verbatim, not CONSOLIDATE — fold leaves RAW per-delta bullets (uniform `- (<COMP>) … [folded foundation-version N · from <task>]`) that you polish/merge later; the alternative is to DROP the `route + transcribe` Must and have fold write only flip+stamp+bump + the §Key-Decisions row (option B). [contract] uniform bullet shape carries a `(<COMP>)` prefix even in PROJECT.md sections that today omit it (signals machine-generated raw material).

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

Coverage target: every §2 scenario has ≥1 behavioral test (5/5) + 2 unit tests of the pure core; stdlib unittest (no % tool — CONVENTIONS.md "stdlib only").
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fold_all_in_one_session: arrange 2 tasks w/ open SDD+ADD deltas + header "foundation-version: N-1" / act `fold` / assert each delta "[<COMP> · folded] … [folded foundation-version N]" + SDD text verbatim atop PROJECT.md "## Spec" + ADD text verbatim atop CONVENTIONS.md "## Method learnings" + exactly one new "## Key Decisions" row naming counts+N + header bumped once + summary "N-1 -> N"
  - test_filter_narrows_scope: arrange open deltas in tasks A & B / act `fold --task A` / assert only A folded; B still "[<COMP> · open]"; one bump
  - test_no_open_deltas_refuses: arrange none open / act `fold` / assert exit≠0 "no_open_deltas" + tree+state byte-identical (snapshot equality)
  - test_missing_route_section_refuses_atomically: arrange open UDD delta + no "## Users" + co-occurring open SDD delta / act `fold` / assert exit "missing_route_section" + SDD STILL open + "## Spec" untouched + version unchanged (validate-all-then-write)
  - test_no_foundation_version_refuses: arrange open delta + header w/o "foundation-version:" / act `fold` / assert exit "no_foundation_version" + tree+state byte-identical
  - test_fold_competency_delta_pure: unit — flip+stamp byte-preserves the line text + (evidence:); returns None when no open (the validate-all-then-write earned-green proof)
  - test_one_bump_for_many_deltas: arrange 3 deltas across 2 competencies / act `fold` / assert all carry the SAME "[folded foundation-version N]" stamp + exactly one header bump ("one session, one bump")
</test_plan>

AUTHORIZED CHANGE-REQUEST guards (updated under §5 BUILD as the human-approved reversal — NOT this task's red suite; declared in §5 scope):
  - `test_foundation_update_loop.py` @v2 → @v3: invert `test_add_py_exposes_no_fold_command` (assert add.py HAS the `fold` subcommand + a transcription-only marker), reconcile `REJECT_CODES` to {no_open_deltas, missing_route_section, no_foundation_version}, keep all ritual/routing/version/example assertions.
  - `test_min_pillar.py`: +`["fold"]` in LIFECYCLE, +`"fold"` in `_NONZERO_OK` (fold on a delta-free board refuses no_open_deltas).
  - `test_ubiquitous_language.py`: +`"fold"` in `MACHINE_CONSTANTS` (the new subcommand name is a machine token); cmd_fold strings speak "consolidation" (prose), "folded" stays a machine token.
  - `test_scope_gate_enforce.py` (SECOND CR, human-authorized at the VERIFY HARD-STOP — folded into this task): +a `.serena/cache/python/symbols.pkl` exclusion fixture + banned-path assertion, proving the scope walk prunes serena's tool cache. Pairs with `_SCOPE_EXCLUDE_DIRS += ".serena"` in add.py. Proven red/green (pre-fix leaks, post-fix pruned). WHY: serena re-indexes add.py on every edit → the AI's own build churned `.serena/cache/*.pkl` → the build-entry snapshot baked them in → the gate flagged a FALSE-POSITIVE out-of-scope touch and the heal loop exhausted to HARD-STOP. The fix makes the gate immune to code-intelligence re-indexing.

Tests live in: `add-method/tooling/test_fold_command.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/test_foundation_update_loop.py` `add-method/tooling/test_ubiquitous_language.py` `add-method/tooling/test_scope_gate_enforce.py` `add-method/skill/add/fold.md` `add-method/src/add_method/_bundled/skill/add/fold.md` `.claude/skills/add/fold.md`
Strategy (ordered batches): 1. add.py: `_COMP_OPEN_TOKEN_RE` + pure `_fold_competency_delta` → routing map → `cmd_fold` → `fold` subparser. 2. sync the 3 engine copies (cp + prepare_bundle) + re-pin `engine_pin.ENGINE_MD5`. 3. AUTHORIZED CR to the guard tests (foundation-update-loop invert+codes @v3 · min_pillar census · ubiquitous-language machine-token). 4. rewrite fold.md (3 copies, byte-identical) to describe the command — keep `<reject_codes>` block, prose stays "consolidation". 5. full suite green.
Safety rule (feature-specific): validate-ALL-then-write across N files — every precondition checked + every new body built in memory FIRST; any failure writes NOTHING (whole tree byte-unchanged). NEVER compose/merge prose — verbatim transcription only.
Code lives in: `add-method/tooling/add.py`
Constraints: do NOT change this task's red suite (`test_fold_command.py`) or the frozen §3 contract; the three guard-test edits are the HUMAN-AUTHORIZED change-request (recorded), not silent weakening; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **1189 green**; the task's red suite `test_fold_command.py` **7/7** green.
- [x] coverage did not decrease — **+7** new behavioral tests (5 scenarios + 2 pure-core unit proofs); 3 guard suites strengthened under the authorized CR.
- [x] no test or contract was altered to pass the build — §3 contract + §4 red suite UNTOUCHED. The 3 guard-test edits (`test_foundation_update_loop` @v3 · `test_min_pillar` census · `test_ubiquitous_language` machine-token) are the HUMAN-AUTHORIZED change-request, recorded in §4/§5 — not silent weakening.
- [x] the green was EARNED — adversarial refute-read done (below). Every reject test asserts snapshot byte-equality; the pure-core test pins byte-preservation + None-on-empty. **One real design-for-failure gap was FOUND and CLOSED**, not gated over (see ⚠).
- [x] concurrency / timing safe — single-process CLI, no shared state. The risky op is the multi-file commit: hardened from N independent `_atomic_write`s to a **two-phase `_atomic_write_many` (stage every temp → rename all)**, so a mid-commit IO failure (disk-full/permission) writes NOTHING; the only residual window is the near-atomic same-dir rename loop, ordered foundation-FIRST so even that residue is a still-open lesson (visible/re-runnable), never a silent loss.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`, `tempfile`, `os`, `date` — all already imported); no network, no shell-out, no user string interpolated into a command.
- [x] layering & dependencies follow CONVENTIONS.md — the Python tool stays the only state writer; writes are atomic + never-clobber; foundation edits are append-only newest-first (the compaction door owns merging).
- [ ] a person reviewed and approved the change — **PENDING** (conservative gate; presented to the human now).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `_atomic_write_many` ← `cmd_fold`; `_fold_competency_delta` · `_COMP_OPEN_TOKEN_RE` · `_FOLD_ROUTES` · `_section_present` · `_prepend_to_section` · `_prepend_key_decision_row` · `_KEY_DECISIONS_HEADING` · `_TABLE_SEP_RE` ← `cmd_fold`; `cmd_fold` ← the `fold` subparser (`set_defaults`). Confirmed live: `test_min_pillar`'s LIFECYCLE census drives `fold` end-to-end.
- [x] DEAD-CODE (code) — no orphaned symbol: `_atomic_write` retains its other callers; every new helper is reached by `cmd_fold`.
- [x] SEMANTIC (prose / non-code) — read `fold.md` (×3 byte-identical) in full: prose stays "consolidation" (no slang `fold`), the `<reject_codes>` block names the new 3 codes, the retired-codes (`unconfirmed_fold`/`unroutable_delta`) bridge note is present. Confirmed across the canonical, `.claude/skills`, and `_bundled` trees.

### GATE RECORD
Outcome: PASS — green earned (1189 suite + 7/7 fold); the design-for-failure gap (cross-file commit) was CLOSED within-contract via the two-phase `_atomic_write_many`; no security finding. risk: high (human-authorized frozen-principle reversal).
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-reject-code rate of `fold` (no_open_deltas · missing_route_section · no_foundation_version) · whether `fold` ever leaves a flipped-but-untranscribed lesson (the two-phase-commit residual) · whether the foundation bloats off one-screen between a `fold` run and the next compaction.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] give the engine a true multi-file commit primitive (stage every temp → fsync → rename-all, rollback-on-fail) so `fold`/`seed`/`release` get all-or-nothing across N files, closing the near-impossible mid-rename residual two-phase commit still leaves (evidence: fold-command verify refute-read — `_atomic_write_many` shrank but did not eliminate the window). [→ multi-file-commit]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] the §5 scope-walk must prune code-intelligence tool caches (`.serena`), else an agent's OWN source edits churn the cache, the build-entry snapshot bakes it in, and the gate flags a false out-of-scope touch that exhausts the heal loop to a false HARD-STOP (evidence: fold-command verify HARD-STOP, attempts 1–3, cache empty yet still flagged because the snapshot recorded it). [folded foundation-version 36]
- [ADD · folded] a frozen "any failure → write nothing" clause that spans N files needs a TWO-PHASE commit (stage-all → rename-all); N independent atomic writes give only per-file atomicity and can leave a silent partial (evidence: fold-command verify refute-read found a flipped-but-untranscribed silent-loss path, closed via `_atomic_write_many` + foundation-first ordering). [folded foundation-version 36]
- [TDD · folded] run the FULL downstream + tool-ENVIRONMENT scan (here: which dirs the scope-walk excludes vs. which tools write to the tree) BEFORE freezing — the spec-delta-guards "scan downstream before freeze" lesson extends past test assertions to the agent's own toolchain side-effects (evidence: the serena-cache HARD-STOP would have been foreseen by a pre-freeze tool-artifact scan). [folded foundation-version 36]
