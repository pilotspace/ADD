# TASK: Faceted §5 strategy block in both TASK template twins

slug: strategy-facet-block · created: 2026-07-07 · stage: mvp · sensitivity: architecture
milestone: build-strategy-facets
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- add-method/tooling/templates/TASK.md.tmpl : §5 BUILD block — `Strategy (ordered batches):` line (the overloaded line the facets split); 4 twins in md5 lockstep (canon · .add/tooling · add-method/.add/tooling · _bundled), all currently 16642dca
- add-method/tooling/templates/TASK.fast.md.tmpl : §5 — `Strategy & known-problem fixes:` single line (fast collapse target); same 4-twin lockstep
- add-method/skill/add/phases/5-build.md : "## Declaring the scope of impact (Scope + Strategy)" section — where facet guidance teaches; 3 trees (canon · .claude/skills · _bundled), member of the `phases` lean pool
- add-method/docs/07-step-5-build.md : the build chapter — no strategy-choice prose today; 3 git-tracked twins (repo-root 07-step-5-build.md · add-method/docs · _bundled/docs)
Context (working folder): test_scope_decl_template.py (EXISTING_LINES pins only Safety-rule/Code-lives-in/Constraints — Strategy hint text is NOT pinned; FROZEN_TAGS census; scaffold test) · test_template_form_tags.py (<12 `

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: full template carries the four facet lines in order   # M1
  Given the canonical TASK.md.tmpl
  When its §5 block is read
  Then the four facet labels appear, ordered Strategy < Approach < Data strategy < Pattern < Optimization stance < Persona

Scenario: each facet hint names its upstream anchor   # M2
  Given the canonical TASK.md.tmpl §5 facet lines
  When each hint is read
  Then Approach cites §1 Framings, Data strategy cites §3 Schema, Pattern cites §0 Honors

Scenario: optimization stance carries the fill discipline   # M3
  Given the Optimization-stance line
  When its hint is read
  Then it states never-blank, the ⚠ lowest-confidence flag, add-advisor on risk high, tests->build timing, and advisory-never-a-gate

Scenario: fast template collapses to one Approach line   # M4
  Given the canonical TASK.fast.md.tmpl
  When its §5 block is read
  Then exactly one "Approach (domain strategy):" line is present and no other facet label

Scenario: template twins stay in lockstep   # M5
  Given the 4 twins of TASK.md.tmpl and of TASK.fast.md.tmpl
  When each set is hashed
  Then every set has exactly one md5

Scenario: build guide teaches the facets under the lean fence   # M6
  Given phases/5-build.md in all 3 trees
  When the guide is read and the phases pool is measured
  Then the facet anchors are present in all trees
  And the phases lean-pool fence holds (compressed, or rebaselined under this contract's approval)

Scenario: book chapter gains the strategy-choice passage   # M7
  Given the 3 git-tracked 07-step-5-build.md twins
  When each is read
  Then the "Choosing the implementation strategy" passage is present and the twins are identical

Scenario: no new census tag   # R:tag_census_amend
  Given the edited TASK.md.tmpl
  When the frozen tag regex scans it
  Then the tag census equals FROZEN_TAGS
  And no facet placeholder is a bare lowercase word

Scenario: comment ceiling held   # R:comment_ceiling
  Given the edited TASK.md.tmpl
  When its HTML comments are counted
  Then the count stays under 12
  And no facet guidance lives in a comment

Scenario: additive only   # R:nonadditive_change
  Given the edited templates
  When EXISTING_LINES and the three pinned labels are checked
  Then every pinned line and label is byte-identical to before
  And the change is purely additive

Scenario: no backtick in facet lines   # R:scope_token_leak
  Given the four new facet lines and the fast collapsed line
  When each is scanned
  Then none contains a backtick
  And the §5 Scope first-line token grammar is unaffected

Scenario: engine untouched   # R:engine_touched
  Given the add.py trio
  When hashed after the build
  Then all three equal ENGINE_MD5
  And engine_pin.py is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TASK.md.tmpl §5 — four ADDITIVE lines, after "Strategy (ordered batches):", before "Persona (required):", exactly:

Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

TASK.fast.md.tmpl §5 — ONE additive line, after "Strategy & known-problem fixes:", before "Strategy actually used:", exactly:

Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">

Schema: template twins (4×2 files, md5 lockstep) · phases/5-build.md ×3 trees (phases lean pool) ·
07-step-5-build.md ×3 git-tracked twins (+ gitignored .add/docs kept consistent) ·
guard suite add-method/tooling/test_strategy_facets.py (new file) · add.py NOT touched (engine_touched)
```

Glossary deltas: `Strategy facet: one declared dimension of the §5 implementation strategy — Approach (algorithm/technique) · Data strategy · Pattern · Optimization stance; advisory, upstream-anchored (§1/§3/§0), drafted at tests->build`
Status: FROZEN @ v1 — approved by Tin (2026-07-07; revision before freeze: domain-generic facet hints + parser-conflict check, both human-raised)
Reported: yes — banner/ARC/SHAPE rendered twice (initial + revised shape), approval on the revised render
Least-sure flag surfaced at freeze: [spec] four facets may be too much ceremony for the full template — every non-fast task sees four more lines; the fast-lane collapse mitigates; if wrong the cost is template noise plus harvest churn in the follow-up facet-adr-harvest task

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: content-anchor coverage — one test per scenario (prose/template task; line-coverage n/a)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_full_template_facet_lines_ordered: read canon tmpl / find 4 labels / assert order Strategy < Approach < Data < Pattern < Optimization < Persona · covers: M1
  - test_facet_hints_cite_upstream_anchors: read each facet line / assert Framings·Schema·Honors named · covers: M2
  - test_optimization_stance_fill_discipline: read the stance line / assert never-blank + ⚠ + add-advisor + tests->build + advisory · covers: M3
  - test_fast_template_single_collapsed_line: read canon fast tmpl / assert exactly one Approach label, no other facet label · covers: M4
  - test_template_twins_lockstep: hash 4 twins each / assert one md5 per set · covers: M5
  - test_build_guide_teaches_facets: read 5-build.md ×3 / assert facet anchors present + trio identical · covers: M6
  - test_phases_pool_fence_held: measure the phases pool vs its baseline·ratio (delegates to test_skill_lean invariants staying green) · covers: M6
  - test_book_chapter_strategy_passage: read 3 chapter twins / assert passage + identical · covers: M7
  - test_tag_census_unchanged: regex-scan edited tmpl / assert census == FROZEN_TAGS · covers: R:tag_census_amend
  - test_comment_ceiling_held: count HTML comments / assert < 12 · covers: R:comment_ceiling
  - test_additive_only: assert EXISTING_LINES + 3 pinned labels byte-identical · covers: R:nonadditive_change
  - test_no_backtick_in_facet_lines: scan the 5 new lines / assert no backtick · covers: R:scope_token_leak
  - test_engine_untouched: hash add.py trio / assert == ENGINE_MD5 · covers: R:engine_touched
  - test_scaffold_carries_facets: init+lock+new-task(+--fast) in a tmpdir / assert facet lines in full, collapsed line in fast · covers: After-1
</test_plan>

Tests live in: `add-method/tooling/` test_strategy_facets.py · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/` `.add/tooling/templates/` `add-method/.add/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/skill/add/phases/` `.claude/skills/add/phases/` `add-method/src/add_method/_bundled/skill/add/phases/` `add-method/docs/` `add-method/src/add_method/_bundled/docs/` `.add/docs/` `add-method/../07-step-5-build.md`
Strategy (ordered batches): 1. edit canon TASK.md.tmpl (4 facet lines, contract-exact) 2. edit canon TASK.fast.md.tmpl (1 collapsed line) 3. byte-copy both to their 3 sibling twins 4. compress phases/5-build.md prose in-file, add the facet paragraph, copy to 2 sibling trees, verify the phases fence 5. add the chapter passage to docs/07 ×3 (+ .add/docs consistency copy) 6. run the new guard suite green + full targeted sweep (scope-decl · form-tags · skill-lean · xml-convention · streams)

Persona (required): methodology-engine-dev
Spawn isolation (default): shared tree — orchestrator builds inline (sequential run mode, single-writer session; no parallel spawn planned)
Known-problem fixes: bare lowercase placeholder → every facet placeholder contains spaces/dashes (census-safe) · comment ceiling at 11 → guidance lives in line hints, zero new comments · backtick-as-scope-token → no backtick in any new §5 template line · phases pool fence → compress 5-build.md before adding; rebaseline only under this contract's approval · twin drift → byte-copy, then md5-verify all twin sets
Strategy actually used: as planned, with one deviation — in-file compression of 5-build.md recovered only ~100 B of the ~430 B facet bullet, so the M6 contract-signed rebaseline path was taken (phases pool 41190 → 41605, ledger comment in test_skill_lean.py); that post-freeze test edit was re-anchored by re-crossing tests->build per the known convention
Safety rule (feature-specific): add.py and engine_pin.py must not change by a single byte (engine trio == ENGINE_MD5); the streams/advisor pin-locked XML strategy blocks stay untouched
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 3132 run: 3130 green + 2 pre-existing-on-main failures (stale SEAMS.md anchor `add.py:4756`→4766 + its fresh-checkout echo; verified pre-existing via HEAD line check, healed as a disclosed out-of-task side-fix, test_seams_doc 15/15 OK after; fresh-checkout heals at commit)
- [x] coverage did not decrease — content-anchor coverage: 14 new tests, none removed; all guard suites (116 targeted) green
- [x] no test or contract was altered during build — EXCEPT the three contract-signed ceiling migrations (test_skill_lean baseline 41190→41605 per M6; the duplicate pins in test_domain_test_mapping + test_taskmd_lean migrated in lockstep), each re-anchored by re-crossing tests->build; frozen §3 untouched since v1
- [x] the green was EARNED, not gamed — adversarial refute-read by add-verify agent (below); mutation probe redded 3 tests on a corrupted facet line
- [x] concurrency / timing safe — static prose/template change; no shared mutable state (agent lens 2 CLEAR)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; zero packages added
- [x] layering follows CONVENTIONS.md — additive template change, twins byte-copied, engine untouched (ENGINE_MD5 verified twice)
- [ ] a person reviewed and approved the change — THIS gate (sensitivity: architecture -> human decision)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a fresh new-task scaffold's §5 renders the four facet lines between Strategy and Persona — confirmed by test_scaffold_carries_facets (tmpdir init+new-task, reads the scaffolded §5) + the refute-read's independent end-to-end run
- [x] a fresh --fast scaffold renders exactly one collapsed Approach line — confirmed in the same tmpdir run (count==1, other facet labels asserted absent)
- [x] phases/5-build.md teaches the four facets and the phases lean fence still holds — confirmed by SEMANTIC read of the Strategy-facets bullet + test_skill_lean green at 33275 B ≤ 33284 target (41605×0.80, M6-signed)
- [x] every twin set (2 templates ×4 · guide ×3 · chapter ×3) hashes to one md5 per set — confirmed by md5 sweep (mine) + the refute-read agent's independent sweep

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the four facet lines, the fast collapsed line, 5-build.md's Strategy-facets bullet, and the docs/07 "Choosing the implementation strategy" passage · confirmed domain-generic wording (M2), all upstream anchors named (§1 Framings · §3 Schema · §0 Honors), fill-discipline tokens verbatim (M3), and the ledger comments arithmetically honest (32943→33275, +⌈332/0.80⌉=415)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — STRATEGY_LABEL/FAST_STRATEGY_LABEL/ACTUAL_LABEL present (test_additive_only), FROZEN_TAGS census unchanged, EXISTING_LINES byte-identical, phases pool baseline at its migrated value; confirmed by the green guard suite + refute-read
- [x] one anchor moved since Ground SHA and is named, not silent: the phases pool baseline 41190 → 41605 (the M6 contract-signed rebaseline, ledgered in test_skill_lean.py); unrelated: SEAMS.md's add.py:4756 anchor was stale on main (pre-Ground drift), re-pinned to :4766 as a disclosed side-fix

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: add-verify agent acc70c8d716efb982 (persona tdd-verifier) · adversarially checked: self-referential-constant risk in 2 hint tests (mitigated — sibling test couples the constants to the live file, proven by mutation probe: corrupted anchor redded 3 tests) · fast-template label collision (absent) · rebaseline arithmetic re-derived (honest) · full twin/engine md5 sweep (all match) · scaffold end-to-end (passes). Agent disclosure: its probe `git checkout` momentarily wiped the uncommitted canon tmpl; restored byte-exact from the dogfood twin, md5-verified, no residue (I re-verified all four twins at 5899d7f7 after).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: add-verify agent acc70c8d716efb982
1. Security: CLEAR — prose/template-only, no execution path, no secrets, no injection surface
2. Concurrency: CLEAR — static text, no shared mutable state or timing dependency
3. Architecture: CLEAR — additive-only (byte-verified vs EXISTING_LINES + pinned labels), templates→guides→docs layering respected, engine untouched
Verdict: PASS
Residue: none blocking — 💭 note: two hint-tests assert only the test's own constants (coverage borrowed from the sibling file-read test, mutation-proven); carried to §7 as a competency delta, not a gap
Binding: advisory — architecture

### GATE RECORD
Reported: yes — gate report (banner/ARC/SUMMARY/FLAGS/EVIDENCE) rendered to Tin before any outcome is recorded
Outcome: PASS
Reviewed by: Tin · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose additive facet lines under the existing Strategy line; rejected replace the Strategy line with a structured sub-block (breaks EXISTING_LINES-style additive convention + every §5 consumer) · a new standalone §5.5 section (heavier; §-numbering ripples into engine parsers)
- [human] freeze — froze §3 @ v1 (approved by Tin (2026-07-07; revision before freeze: domain-generic facet hints + parser-conflict check, both human-raised))
- [AI] build — strategy used: as planned, with one deviation — in-file compression of 5-build.md recovered only ~100 B of the ~430 B facet bullet, so the M6 contract-signed rebaseline path was taken (phases pool 41190 → 41605, ledger comment in test_skill_lean.py); that post-freeze test edit was re-anchored by re-crossing tests->build per the known convention
- [AI] verify — gate PASS (reviewed by Tin)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

