# TASK: fast-lane skill guide + glossary

slug: fast-lane-guide · created: 2026-06-23 · stage: mvp
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

Touches (files · symbols · signatures): NEW `phases/fast-lane.md` (the guide) ×3 skill trees [`add-method/skill/add/`, `.claude/skills/add/`, `add-method/src/add_method/_bundled/skill/add/`] · `SKILL.md` pointer ×3 skill trees · `appendix-c-glossary.md` "fast lane" term ×3 docs trees [`add-method/docs/`, `.add/docs/`, `add-method/src/add_method/_bundled/docs/`] · `.add/GLOSSARY.md` "fast lane" entry (dogfood survivor). NO add.py change (prose/skill-only) → engine_pin UNTOUCHED.
Context (working folder): the `--fast` flag + the freeze-before-build fast arm are already SHIPPED (fast-new-task-flag, gate=PASS); this task is the human-facing HOW/WHEN. Test `test_fast_lane_guide.py` in `add-method/tooling/` pins guide+pointer+term presence.
Honors (patterns / conventions): 3-skill-tree byte parity (test_tree_parity + test_bundle_parity) · book/docs canonical↔bundle parity · progressive disclosure (load-on-demand guide, like streams.md/design.md — named from SKILL.md, body loaded only when chosen) · one-name-per-concept glossary (GLOSSARY.md compact + appendix-c book term) · collapse-never-skip framing (the guide must NOT teach skipping the floor).
Anchors the contract cites: `SKILL.md` "Beyond the bundle — load on demand" section (where the pointer lands) · the existing short load-on-demand guides as the voice/format template · `appendix-c-glossary.md` "## Terms" + `.add/GLOSSARY.md` line format · the milestone glossary delta ("new term fast lane").

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a `phases/fast-lane.md` skill guide + a SKILL.md pointer + a "fast lane" glossary term that teach WHEN to choose the fast lane and HOW to run it as ONE batched approval — without ever teaching to skip the trust floor.
Framings weighed: a load-on-demand guide named from SKILL.md (chosen — mirrors streams.md/design.md; progressive disclosure, body loaded only when chosen) · inlining the how-to into SKILL.md (rejected — bloats the always-loaded file, breaks progressive disclosure) · a book chapter only (rejected — the agent reads the skill, not the book, in the loop; the book gets only the glossary term)
Must:
<must>
  - a NEW `phases/fast-lane.md` exists in all 3 skill trees (byte-identical) naming WHEN to pick the fast lane (a small, low-risk, single-file-ish task) and HOW to run it (`new-task --fast` → batch specify+scenarios+contract to ONE freeze → red test → build → verify gate)
  - the guide STATES the floor is KEPT, only collapsed: a FROZEN §3 · ≥1 red test before build · a recorded verify gate (security always HARD-STOP) — and that a `--fast` task is freeze-gated under ANY milestone; it NEVER teaches a bypass (collapse-never-skip)
  - `SKILL.md` gains a one-line fast-lane pointer in the "Beyond the bundle — load on demand" section, in all 3 skill trees
  - the term "fast lane" is defined in `appendix-c-glossary.md` (×3 docs trees) and `.add/GLOSSARY.md` (the dogfood survivor)
  - NO add.py change (engine_pin UNTOUCHED); skill 3-tree parity + docs canonical↔bundle parity stay green
</must>
Reject:
<reject>
  - none NEW — a prose/skill task adds no engine reject. The quality bar (the guide must not teach skipping the floor) is enforced by a test asserting the guide names the freeze/red-test/gate floor, not by an engine code.
</reject>
After:
<after>
  - a session can read `phases/fast-lane.md` and run a small task on the fast lane in one batched approval, with the floor intact; the glossary defines "fast lane" the same everywhere
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a load-on-demand guide (not an inline SKILL.md section) is the right home — lowest confidence because a brand-new agent might miss a guide it must opt to load; mitigated by the SKILL.md pointer (always loaded) that names WHEN to read it, exactly like streams.md/design.md. If wrong, the pointer can be expanded inline later (a cheap follow-up).
  - [ ] putting only the glossary term (not a how-to chapter) in the book is enough — the book explains WHY, the skill drives HOW; deny only if the fast lane needs a book chapter of rationale.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guide exists across the skill trees
  Given the shipped skill
  When I look for phases/fast-lane.md in each of the 3 skill trees
  Then it is present and byte-identical across all three

Scenario: the guide keeps the floor (collapse-never-skip)
  Given phases/fast-lane.md
  When I read it
  Then it names the frozen contract, the red-test-before-build, and the recorded verify gate as KEPT
  And it never instructs skipping any of them

Scenario: SKILL.md points to the fast lane
  Given SKILL.md
  When I read the "Beyond the bundle — load on demand" section
  Then it names phases/fast-lane.md and when to read it
  And the pointer is present in all 3 skill trees

Scenario: the glossary defines the term
  Given the glossary files
  When I look up "fast lane"
  Then appendix-c-glossary.md (book) and .add/GLOSSARY.md (survivor) both define it

Scenario: no engine drift
  Given this is a prose/skill task
  When the build completes
  Then add.py is byte-unchanged across the 3 trees and engine_pin is untouched
  And the skill + docs parity suites stay green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  phases/fast-lane.md  (×3 skill trees, BYTE-IDENTICAL) — a load-on-demand guide with:
  · WHEN — pick the fast lane for a small, low-risk, roughly single-file task; NOT for a milestone,
    a release, an architecture/security change, or anything you'd want scenarios to enumerate.
  · HOW — `add.py new-task <slug> --fast` → the minimal TASK.fast.md (sections {0,1,3,4,5,6}) →
    draft §1 + §3 and FREEZE the contract as ONE batched approval → ≥1 red test → build → verify gate.
  · FLOOR (kept, only collapsed) — a FROZEN §3, a red test before build, a recorded verify gate
    (security = HARD-STOP) all REMAIN; a `--fast` task is freeze-gated under ANY milestone
    (contract_not_frozen). Speed comes from fewer sections + auto-gating, NEVER from dropping the seam.
  · NOT — the engine never auto-classifies a task as small; the human opts in (like the autonomy header).

POINTER  SKILL.md "Beyond the bundle — load on demand" gains ONE line naming phases/fast-lane.md +
         when to read it (a small task you want to run with less ceremony). ×3 skill trees.

GLOSSARY  "fast lane" defined in appendix-c-glossary.md (book ## Terms, ×3 docs trees) AND
          .add/GLOSSARY.md (the compact survivor) — same concept, one name.

TEST  test_fast_lane_guide.py asserts: the guide is present (canonical) · names the floor
      (frozen/contract + red/test + gate) · SKILL.md contains a fast-lane pointer · the glossary
      term exists. (Parity of the new files is covered by the existing tree/bundle parity suites.)

NO ENGINE CHANGE: add.py + engine_pin BYTE-UNCHANGED. The deliverable is prose + skill files.
```

`Least-sure flag surfaced at freeze:` [contract] the guide is a load-on-demand file an agent must CHOOSE to read — the bet is the always-loaded SKILL.md pointer is enough to surface it at the right moment (mirrors streams.md/design.md); if wrong, the pointer expands inline — a cheap follow-up. why: progressive disclosure keeps SKILL.md lean; cost if wrong: one missed fast-lane opportunity, not a broken floor.

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

Coverage target: presence + floor-keeping content of the guide/pointer/term (6 tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_exists_in_all_three_trees / test_guide_byte_identical_across_trees: phases/fast-lane.md present + identical ×3
  - test_guide_keeps_the_floor: the guide names the frozen contract + red test + verify gate + "collapse"
  - test_guide_does_not_teach_skipping_the_floor: no bypass phrasing ("skip the freeze/contract/gate", "without a gate", …)
  - test_skill_points_to_the_guide: SKILL.md names fast-lane.md in all 3 trees
  - test_glossary_defines_the_term: "fast lane" in appendix-c-glossary.md (book) AND .add/GLOSSARY.md (survivor)
</test_plan>

Tests live in: `add-method/tooling/test_fast_lane_guide.py` · MUST run red (missing implementation) before Build.
RED confirmed (2026-06-23): guide/pointer/term absent → 4 failures + 2 errors (the floor-content checks raise on the missing file). After build all 6 green.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/fast-lane.md` `.claude/skills/add/phases/fast-lane.md` `add-method/src/add_method/_bundled/skill/add/phases/fast-lane.md` `add-method/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `add-method/docs/appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `appendix-c-glossary.md` `.add/GLOSSARY.md` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_wording_lint.py` `add-method/tooling/test_per_step_hooks.py`
<!-- scope grew at build (discovered constraints, all conscious-acknowledgment tripwires for NEW surface):
     the book mirrors x4 incl. the repo-root copy `appendix-c-glossary.md`; the lean-pass byte fence
     `test_skill_lean.py` REBASELINED for the new guide (human-approved "rebaseline for new surface" —
     ratios kept, won ground untouched); the wording-lint surface-count tripwires (test_wording_lint.py +
     test_per_step_hooks.py) bumped 28→29 to acknowledge the new guide joining the linted surface. -->

Strategy (ordered batches): 1. write phases/fast-lane.md (canonical) → cp to the 2 mirror skill trees. 2. add the SKILL.md pointer (canonical) → cp to mirrors. 3. add the "fast lane" term to appendix-c-glossary.md (canonical) → cp to the 2 docs mirrors. 4. add the compact term to .add/GLOSSARY.md. 5. run the parity + full suites.
Safety rule (feature-specific): prose/skill only — NO add.py / engine_pin edit; keep every parity tree byte-identical (write canonical, copy to mirrors).
Code lives in: the skill + docs trees above (no `./src/`).
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

- [x] all tests pass — test_fast_lane_guide.py 6 green; full suite 1634 green
- [x] coverage did not decrease — +6 new tests; no test removed (the 3 fence tests were rebaselined, not dropped)
- [x] no test or contract was altered during build — the §3 contract is byte-unchanged; the 3 fence edits are NOT logic weakening: they rebaseline byte/surface-count tripwires to ACCOUNT for the new guide (human-approved "rebaseline for new surface"; ratios kept, the won compaction on every existing guide untouched), declared in §5
- [x] the green was EARNED, not gamed — the suite asserts real artifact facts (file present + byte-identical ×3, the guide NAMES the floor + carries no bypass phrasing, SKILL.md points to it, the term is defined); no overfit/stub possible (prose presence/content)
- [x] concurrency / timing of the risky operation is safe — N/A: prose/skill files; no code path, no IO added
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; add.py + engine_pin BYTE-UNCHANGED (md5 d4807ff9 ×3)
- [x] layering & dependencies follow CONVENTIONS.md — load-on-demand guide named from SKILL.md (progressive disclosure, like streams.md/design.md); 3-skill-tree + x4-docs parity green; one-name-per-concept glossary honored
- [x] a person reviewed and approved the change — §3 FROZEN @ v1 + the lean-fence rebaseline both human-approved (the "rebaseline for new surface" decision); verify auto-gated on complete evidence

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `phases/fast-lane.md` exists byte-identical in all 3 skill trees and reads as a real WHEN/HOW/floor guide — confirmed by reading the file + test_guide_* (md5 72129b… ×3)
- [x] the guide KEEPS the floor (names frozen contract + red test + verify gate + "collapse") and teaches no bypass — confirmed by test_guide_keeps_the_floor + test_guide_does_not_teach_skipping_the_floor
- [x] SKILL.md points to the guide (×3) and the term "fast lane" is defined in the book (x4) + .add/GLOSSARY.md — confirmed by test_skill_points_to_the_guide + test_glossary_defines_the_term

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (prose) — the SKILL.md "Beyond the bundle" pointer names `phases/fast-lane.md`; the guide is reachable from the always-loaded surface; the glossary term cross-refs the guide
- [x] DEAD-CODE (n/a) — no code symbol added; add.py untouched
- [x] SEMANTIC (prose · read in full, not skimmed) — re-read the guide end-to-end: WHEN (small/low-risk, NOT milestone/release/security) · HOW (--fast → minimal template → one batched freeze → red → build → gate) · FLOOR kept (frozen/red/gate, freeze-gated under any milestone) · NOT (no bypass, task-level, human opts in). No instruction to skip any floor element. Voice matches the sibling guides.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

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
