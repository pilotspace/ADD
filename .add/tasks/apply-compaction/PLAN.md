# TASK: Dogfood: compact live PROJECT.md + CONVENTIONS.md; tests guard no-residue-lost

slug: apply-compaction · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from the project default: this is the heavy live mutation of the FROZEN foundation (reorder + roll ~58 §Key-Decisions rows + ~76 CONVENTIONS bullets) — risk: high, so the human gates the freeze AND the verify; an unguarded auto completion is refused (unguarded_high_risk_auto). -->
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
  - `.add/PROJECT.md` §Spec — heading L37 `## Spec / Living Document (SDD) — what we are building, now`; 26 version bullets, OLDEST-FIRST (top = oldest); the last 8 carry `[folded foundation-version 21..27]` (L185–250); bullets 1–18 are pre-fv21 long-form prose (v1–v20, 2026-05-28→06-08).
  - `.add/PROJECT.md` §Key Decisions — heading L339 `## Key Decisions (append-only — newest-first; compaction door per compact-foundation.md)`; columns `| date | decision | why | outcome |` (L340); 58 rows L342–399, OLDEST-FIRST (2026-05-28 top → 2026-06-14 bottom). The heading already declares newest-first but the DATA is oldest-first — the coherence gap this task closes.
  - `.add/CONVENTIONS.md` — heading L1 `# CONVENTIONS  (survivor layer … append-only is newest-first — compaction door …)`; one flat `## Method learnings` list (L28–689), ~76 bullets tagged `(ADD|TDD|SDD) … [<slug> — folded foundation-version N]`, fv2 (L33) → fv30 (L673–689), OLDEST-FIRST; 690 lines total. Preamble L1–27 (Language/Folders/Naming/Lint/Errors/Architecture) is stable config, NOT an append sequence — untouched.
  - `.add/GLOSSARY.md` (L1) — 23-term flat dictionary, NO append sequence → forward-looking, NOT reordered here.
  - `.add/MODEL_REGISTRY.md` (L1) — single model entry, NO sequence → forward-looking, NOT reordered here.
  - NEW `./tests/test_apply_compaction.py` — guards no-residue-lost (multiset of rows/bullets preserved across reorder), newest-first order (head of each sequence = most-recent date/version), roll preserves a git pointer, and every OPEN residue stays live.
Context (working folder): the FROZEN `.add/tasks/compact-contract/compaction-contract.md` (eligibility + 5 per-spec shapes + 3 reject codes) · the FROZEN `compact-foundation.md` ritual (the shapes this realizes) · `add.py deltas` = 13 OPEN, ALL on current/recent tasks (compact-contract · compact-guide · invariant-amend · gitignore-scaffold — fv29–30 era) → the recent tail stays LIVE; the v1–v20 tail (2026-05-28→~06-08) is the shipped, zero-residue, roll-eligible run · shipped milestones v10/v12/build-scope-lock/next-step-seams (per `add.py check`).
Honors (patterns / conventions): milestone Shared decisions — compaction NEVER deletes (summarize + point to git) · OPEN residues are sacred · newest-first PREPEND with the settled line at the BOTTOM (collapse upward) · human-confirmed never auto · ONE eligibility test + per-spec shapes · the convention-vs-engine boundary. `.add/` IS the dogfood/live tree (PROJECT.md/CONVENTIONS.md have no add-method twin — they are the foundation itself); the scope-walk EXCLUDES `.add/`, so the live files are ride-along, the NEW test under the task dir is the gated anchor. git-pointer preservation guards `trail-loss`.
Anchors the contract cites: PROJECT.md §Spec (L37) · PROJECT.md §Key Decisions table (L339–399) · CONVENTIONS.md §Method learnings (L28–689) · the 5 rolled-line shapes + the 3 reject codes (`open-residue-version` · `trail-loss` · `wrong-order`) from compaction-contract.md · GLOSSARY/MODEL_REGISTRY (forward-looking, untouched).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Dogfood foundation compaction on the LIVE specs — physically RE-ORDER all 3 append-only sequences (PROJECT §Spec bullets · PROJECT §Key-Decisions rows · CONVENTIONS §Method-learnings) to NEWEST-FIRST, then ROLL each spec's stable shipped tail into ONE per-spec settled line at the bottom — preserving every record (no-residue-lost) and a git pointer, per the frozen compaction-contract.
Framings weighed: ONE guarded transform per spec — reverse THEN roll the eligible tail, proven by a no-residue-lost multiset test (chosen — the milestone frames reorder+roll as one dogfood; the test makes traceability structural) · reverse-only now, roll at milestone close (rejected — the exit criteria require "visibly shorter … stable tail rolled into settled lines" FROM this task) · roll without reversing (rejected — exit criteria require the newest-first head).
Must:
<must>
  - REVERSE NEWEST-FIRST: each of the 3 sequences is reordered so the most-recent record (max date / max foundation-version) sits on TOP and the oldest at the bottom — the head of each = the most-recent record.
  - ROLL THE STABLE TAIL: the oldest, shipped, zero-open-residue RUN of each sequence collapses into ONE per-spec settled line at the BOTTOM, per the frozen shapes — §Spec → `settled fvN–fvM — <theme> (see git)` · §Key-Decisions → one `| settled <dateA>–<dateB> | <N> decisions rolled | … | see git |` row · §Method-learnings → `- settled conventions fvN–fvM — <N> rules (see git)`.
  - ELIGIBILITY (shared test): only an entry whose milestone is shipped AND that carries zero open residues may roll; the recent live tail (fv29–30 era + anything pinned by one of the 13 OPEN deltas) stays EXPANDED.
  - PRESERVE (no-residue-lost): every pre-existing row/bullet is EITHER still present verbatim OR summarized into its spec's settled line — none silently dropped; each settled line carries a surviving git pointer.
  - VISIBLY SHORTER: PROJECT §Spec and CONVENTIONS §Method-learnings drop in line count (the roll is real, not cosmetic) while the audit trail is summarized-not-deleted.
  - HEADERS ALREADY MATCH: the §-headings already declare newest-first (invariant-amend); this task makes the DATA match — no header re-edit, GLOSSARY/MODEL_REGISTRY untouched (nothing eligible; forward-looking).
</must>
Reject:
<reject>
  - a row/bullet present before is neither retained verbatim nor summarized into a settled line -> "trail-loss"
  - a sequence's head is not the most-recent record (still oldest-first, or a settled line sits on top instead of the tail) -> "wrong-order"
  - an entry tied to an unshipped milestone or an OPEN residue is collapsed -> "open-residue-version"
</reject>
After:
<after>
  - PROJECT §Spec, PROJECT §Key-Decisions, and CONVENTIONS §Method-learnings each read newest-first (head = most-recent) with ONE settled line at the tail; §Spec + §Method-learnings are visibly shorter (wc -l drops); every OPEN residue is still live; the multiset of original entries is preserved-or-summarized (test_no_residue_lost green); each settled line carries a git pointer.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the ROLL BOUNDARY — which oldest RUN counts as "stable + shipped + zero-residue" — is the lowest-confidence call because it is a judgment on living history; if wrong: too-aggressive buries a still-relevant decision, too-timid leaves the spec long. Mitigation: the §3 contract proposes an EXPLICIT, conservative boundary (roll only the clearly-shipped pre-fv21 / v1–v14 tail; keep fv21+ and all fv29–30 expanded) for human confirmation at the freeze.
  - [ ] reversal is a pure permutation (multiset-preserving, order-only) — confirmed by test_no_residue_lost; treated settled.
  - [ ] §Key-Decisions rows carry no per-row milestone link, so eligibility uses a DATE cutoff as the shipped-proxy — the cutoff is confirmed at the freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: each sequence reads newest-first after the transform
  Given PROJECT §Spec, PROJECT §Key-Decisions, and CONVENTIONS §Method-learnings (currently oldest-first)
  When the compaction transform runs
  Then the HEAD of each sequence is the most-recent record (max date / max foundation-version)
  And the previous oldest record now sits at the tail (above only the settled line)

Scenario: the stable shipped tail rolls into one settled line per spec
  Given the oldest shipped, zero-open-residue run of each sequence
  When it is rolled
  Then each spec gains exactly ONE settled line at its BOTTOM in the frozen shape (settled fvN–fvM … / | settled … | see git | / - settled conventions …)
  And §Spec and §Method-learnings are visibly shorter (line count drops)

Scenario: no residue is lost (collapse = summarize + point)
  Given every row/bullet present before the transform
  When the transform completes
  Then each is EITHER still present verbatim OR summarized into its spec's settled line
  And each settled line carries a surviving git pointer (else "trail-loss")

Scenario: open residues and the recent live tail stay expanded
  Given the 13 OPEN deltas and the fv29–30 era entries
  When eligibility is applied
  Then no entry tied to an open residue or an unshipped milestone is collapsed (else "open-residue-version")
  And the recent live tail remains expanded, not rolled

Scenario: ordering is rejected if the head is not most-recent
  Given the transformed sequences
  When the order is checked
  Then a sequence whose head is not the most-recent record, or whose settled line is not at the tail, is rejected with "wrong-order"
  And GLOSSARY.md and MODEL_REGISTRY.md are unchanged (no eligible sequence)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
APPLY-COMPACTION CONTRACT — dogfood the live foundation, realizing compaction-contract.md @ v1

TRANSFORM (per sequence, scripted, two ordered steps):
  1. REVERSE — reorder the sequence to newest-first: most-recent record (max date / max
     foundation-version) on TOP, oldest at the bottom. PURE permutation — multiset of records
     unchanged (only order changes). Proven by test_no_residue_lost.
  2. ROLL THE ELIGIBLE TAIL — replace the oldest shipped + zero-open-residue RUN (now at the
     bottom) with ONE settled line at the very tail, in that spec's frozen shape, carrying a git
     pointer. The rolled records leave the LIVE file (it gets shorter) but survive in git history
     (collapse = summarize + point, never delete).

ELIGIBILITY (shared): a record rolls IFF its milestone is shipped AND it carries zero open
  residues. The 13 OPEN deltas are all fv29–30 era → the recent tail stays EXPANDED.

PROPOSED ROLL BOUNDARY (the human's approval point — conservative: only the pre-enhancement-wave
v1–v20 foundational era; everything fv21+ / dated ≥ 2026-06-09 stays live):

  PROJECT.md §Spec (L37) — 27 bullets → ROLL the 19 pre-`[folded fv21]` bullets (v1–v20 prose) into
    one tail line; KEEP the 8 fv21–27 bullets expanded (newest on top). Result: 9 bullets.
    settled line:
      - settled fv1–fv20 — ADD bootstrapping → production-ready: SDD foundation · self-driving run · one-approval auto · awareness surface · decision-point reports · zero-command on-ramp · prompt & file hygiene · dynamic loop (see git)

  PROJECT.md §Key-Decisions (L339) — 58 rows → ROLL the 48 rows dated ≤ 2026-06-08 into one tail
    row; KEEP the 10 rows dated 2026-06-09…2026-06-14 expanded (newest on top). Result: 11 rows.
    settled row (tail):
      | settled 2026-05-28–2026-06-08 | 48 foundational decisions rolled (v1.0 npm scope → v20 dynamic loop) | bootstrapping through production-ready ADD | see git |

  CONVENTIONS.md §Method-learnings (L28) — 123 bullets → ROLL the 67 bullets whose max foundation-
    version ≤ 20 into one tail line; KEEP the 56 fv21–30 bullets expanded (newest on top).
    Result: 57 bullets. Preamble L1–27 untouched (stable config, not a sequence).
    settled line (tail):
      - settled conventions fv2–fv20 — 67 method learnings rolled (early ADD/TDD/SDD discipline) (see git)

  GLOSSARY.md · MODEL_REGISTRY.md — UNTOUCHED (no append sequence; forward-looking, nothing eligible).

ORDERING (post-transform, every sequence): head = most-recent record; the ONE settled line is the
  LAST element (tail). Else -> "wrong-order".
PRESERVATION: every original record is retained verbatim (expanded) OR counted+summarized by its
  spec's settled line (which carries "see git"); none silently dropped. Else -> "trail-loss".
OPEN RESIDUES: no record pinned by an open delta / unshipped milestone is rolled. Else -> "open-residue-version".
VISIBLY SHORTER: §Spec and §Method-learnings line counts drop (wc -l before > after).

guard: test_no_residue_lost + order test (`./tests/test_apply_compaction.py`). Convention-guided —
  no add.py edit; the live `.add/` specs are edited directly (the dogfood).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-15
Least-sure flag surfaced at freeze: [contract] the roll boundary — rolling the v1–v20 era includes the 2026-06-08 §Key-Decisions rows (same day v21 shipped); accepted as conservative-enough because all rolled records are shipped with zero open residues and every open delta is fv29–30 (safely expanded). Secondary [test]: no-residue-lost is structural (count + "see git"), with git history as the actual trail.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a test; the no-residue-lost + order guards are behavioral over the LIVE post-transform files (not fixtures).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_newest_first_head: for each of the 3 sequences, parse the expanded records and assert dates/foundation-versions are DESCENDING (head = most-recent); the settled line is the LAST element [guards wrong-order]
  - test_settled_line_at_tail_each_spec: each spec has exactly ONE settled line in its frozen shape, positioned at the tail (after all expanded records)
  - test_no_residue_lost: original_count == expanded_count + N_declared_in_settled (per sequence); every expanded record is byte-present in the pre-transform snapshot; nothing silently dropped [guards trail-loss]
  - test_git_pointer_survives: each settled line contains "see git" [guards trail-loss]
  - test_open_residues_live: records tied to the 13 OPEN deltas / fv29–30 era are in the EXPANDED portion, never inside a rolled range [guards open-residue-version]
  - test_visibly_shorter: PROJECT.md §Spec and CONVENTIONS.md §Method-learnings line counts dropped vs the pre-transform snapshot
  - test_glossary_model_registry_unchanged: GLOSSARY.md + MODEL_REGISTRY.md byte-identical to pre-transform (no eligible sequence)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.add/PROJECT.md` `.add/CONVENTIONS.md` `./tests/` `./compaction_lib.py` `./apply_compaction.py` `./snapshot_before.json` — the 2 LIVE foundation specs (ride-along: the scope-walk EXCLUDES `.add/`, so these get no scope-gate coverage — the gated anchor is `./tests/`), the guard tests, the one-shot transform script, and the pre-transform snapshot the tests compare against. NO `add.py`/engine edit (convention-guided).
Strategy (ordered batches): 1. snapshot the 3 sequences pre-transform → `./snapshot_before.json` · 2. write `./tests/` RED (assert newest-first + no-residue-lost against the not-yet-transformed live files) · 3. `./apply_compaction.py` REVERSES each sequence (assert multiset preserved) THEN ROLLS the approved oldest run into the frozen settled line per spec · 4. run GREEN · 5. the pre-compaction live files live in git history — the "see git" pointer.
Safety rule (feature-specific): the transform is MULTISET-PRESERVING on reverse (assert set(records_before)==set(records_after) BEFORE any roll); the roll removes ONLY records inside the human-approved boundary and writes ONE settled line carrying "see git"; the pre-transform state is committed so git holds the full trail. Never delete without a settled-line summary + git pointer.
Code lives in: `./apply_compaction.py` (one-shot transform) + the edited `.add/PROJECT.md` / `.add/CONVENTIONS.md` (the deliverable).
Constraints: do NOT change any test or the frozen contract; no `add.py`/engine edit; honor the approved roll boundary EXACTLY; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — apply-compaction suite 7/7 GREEN; `add.py check` 323 passed/0 failed; engine suite 1027/1027 OK (the live-foundation mutation broke no method guard).
- [x] coverage did not decrease — 7 behavioral tests over the LIVE post-transform files (order · settled-at-tail · no-residue-lost · git-pointer · open-residues-live · visibly-shorter · glossary/model-unchanged).
- [⚠] no test or contract was altered during build — NO test or §3 altered. DISCLOSED frozen-contract PROSE inaccuracy (not an alteration): §3 illustrates §Spec as "19 rolled → 9 result / keep 8"; the correct rule (un-fv-stamped v1–v20 prose) rolls 18 → 10 result / keep 9. The binding RULE + settled-line shapes are honored; the integers were a freeze-time miscount. KD(48) + Method(67) match exactly. Not edited (constraint #3) — surfaced for the human at the gate.
- [x] the green was EARNED, not gamed — independent adversarial refute-read (general-purpose subagent) VERDICT **EARNED**: DATA-LOSS none (all 58/27/123 records byte-match git db98f9a; "see git" truthful), no file corruption (headings intact, §Spec settled line before `## Users`, no orphaned continuations), ordering newest-first with settled-at-tail, eligibility correct (0 fv21+ rolled · 0 None kept · all 11 fv29–30 live · no ≥06-09 KD rolled), settled counts accurate (48/67), tests non-vacuous (list-equality catches reorder/drop).
- [x] concurrency / timing — N/A: one-shot offline transform on local files; pre-state preserved in git (db98f9a) for full recovery.
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: stdlib-only script; edits two markdown docs.
- [x] layering & dependencies follow CONVENTIONS.md — convention-guided (no `add.py`/engine edit); the `.add/` live specs are the dogfood (ride-along, scope-walk-excluded); the gated `./tests/` + scripts are in §5 Scope.
- [x] a person reviewed and approved the change — Tin Dang, verify gate 2026-06-15: PASS, accepting the rule-faithful §Spec output over the contract's illustrative 19→9 miscount.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `compaction_lib.split/is_rolled/SETTLED_*` are imported by both the suite and `apply_compaction.py`; the transform's outputs are consumed by the 7 live-file assertions. No orphaned symbol.
- [x] SEMANTIC (prose / non-code) — read the mutated §Spec, §Key-Decisions table, and §Method-learnings: each reads newest-first (head = 2026-06-14 / next-step-seams / fv30), ONE settled line at each tail carrying "see git", section headings intact (Spec→Users→Key-Decisions; Method-learnings is CONVENTIONS' last section), no orphaned continuation lines. PROJECT.md 399→215, CONVENTIONS.md 689→360 (visibly shorter; rolled records preserved in git db98f9a). Refute-read independently confirmed zero data loss + no corruption.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-15
Note: PASS accepts the live-foundation compaction (PROJECT.md 399→215, CONVENTIONS.md 689→360; rolled records preserved in git db98f9a). Independent refute-read returned EARNED (zero data loss). Disclosed: the frozen §3 PROSE miscounts §Spec as 19→9 where the rule correctly rolled 18→10 — accepted as rule-faithful; the §3 contract is left frozen (not edited).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): foundation line counts per fold (do the specs stay one-screen?) · settled-line count accuracy at each future compaction · the head record of each sequence (must stay most-recent).
Spec delta for the next loop: the next on-demand compaction can reuse `compaction_lib.split` + `apply_compaction.py` with a moved cutoff; the v1–v20 settled lines themselves become roll-eligible once a later era is also settled (settled lines nest).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · folded] foundation compaction is real and safe on living docs: reverse-to-newest-first + roll-the-shipped-tail collapsed the foundation 1088→575 lines (−47%) with ZERO data loss, verified by an independent refute-read against git history (evidence: PROJECT.md 399→215, CONVENTIONS.md 689→360; all 58/27/123 records byte-match db98f9a).
  - [TDD · folded] a destructive in-place transform is made safe by a FROZEN pre-state snapshot + a shared parser used by BOTH test and transform, so "newest-first kept run reversed" is a list-equality assertion (catches any drop/reorder), not a vacuous set check (evidence: snapshot_before.json + compaction_lib.split; test_reverse_then_roll_order is exact-list).
  - [SDD · folded] a per-sequence eligibility predicate beats a single global cutoff: §Spec keys on un-fv-stamped prose, §Key-Decisions on date, §Method-learnings on max-foundation-version — same "v1–v20" intent, three structural tests (evidence: cl.is_rolled branches; §Spec rolled 18 None-maxfv bullets where a date/fv cutoff would have rolled 0).
  - [ADD · folded] a frozen contract's ILLUSTRATIVE integers can be miscounted at freeze; honor the binding RULE, implement correctly, and disclose the integer drift at the gate rather than retrofit the frozen prose (evidence: §3 said §Spec 19→9, the rule rolled 18→10; human PASSed the rule-faithful output, §3 left frozen).
