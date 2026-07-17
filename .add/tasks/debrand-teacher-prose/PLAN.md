# TASK: Strip the agency-agents brand from method prose + engine; repoint persona phase at the local teacher library

slug: debrand-teacher-prose · created: 2026-06-30 · stage: mvp
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
- `add-method/docs/18-personas.md` (line ~21) — names the teacher as `[agency-agents](https://github.com/msitarzewski/...)`. Book tree; twins: repo-root `./18-personas.md`, `.add/docs/18-personas.md`, `_bundled/docs/` (via prepare_bundle).
- `add-method/docs/appendix-c-glossary.md` — **persona** headword says "distilled from a *teacher* corpus" (no brand, but should point at the local library). Same book twins.
- `add-method/skill/add/phases/0-setup.md` (line ~55) — "a teacher (e.g. agency-agents)". Skill tree; twin: `.claude/skills/add/phases/0-setup.md`; `_bundled/skill/` via prepare_bundle.
- `add-method/tooling/templates/personas/_template.md.tmpl` (line ~5-6) — "distilled from a teacher source (e.g. github.com/msitarzewski/agency-agents)". Engine-tree template; twin: `.add/tooling/templates/...`; `_bundled/tooling/` via prepare_bundle.
- `add-method/tooling/add_engine/constants.py` (line ~96) — engine COMMENT "(agency-agents)". 3 engine trees (add-method/tooling, .add/tooling, _bundled/tooling); editing it re-pins `ENGINE_PKG_MD5` in `add-method/tooling/engine_pin.py` (current: da3fb1b53bbdfd10e963bb909cde86eb).
- KEEPERS (brand legitimately retained, MUST NOT scrub): `add-method/scripts/update_teacher.py` (UPSTREAM url), `add-method/personas-teacher/VENDOR.md` (pin url). NOTICES uses "AgentLand Contributors" (no agency-agents token).
- PINNED tests asserting the brand (update in TESTS): `add-method/tooling/test_persona_setup.py` (asserts 0-setup cites "agency-agents"), `add-method/tooling/test_persona_method_docs.py` (required-terms tuple lists "agency-agents").

Context (working folder): the persona-learning-loop prose shipped citing the upstream by name; this milestone moved the corpus to a vendored local library, so the prose must repoint at `.add/personas-teacher/` and drop the brand (LICENSE/NOTICES retain it per MIT).
Honors (patterns / conventions): book parity (3 git twins + `.add/docs` runtime mirror), skill parity (2 trees), engine parity (3 trees + single-source pin), bundle parity (prepare_bundle regenerates `_bundled`); de-brand is PROSE-only — the legal notice + the refresh script keep the URL; engine stays hands-off (no path literal added to engine source — the bundle-teacher guard forbids "personas-teacher" in engine_src).
Anchors the contract cites: `18-personas.md`, `appendix-c-glossary.md`, `0-setup.md`, `_template.md.tmpl`, `constants.py`, `engine_pin.py:ENGINE_PKG_MD5`, `.add/personas-teacher/`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Remove the `agency-agents` brand (name + URL) from every method-prose + engine surface and repoint the persona phase at the LOCAL vendored library `.add/personas-teacher/` — while the LICENSE/THIRD_PARTY_NOTICES (legal) and the refresh script/VENDOR.md (operational) legitimately retain the upstream URL.
Framings weighed: de-brand prose + repoint at the local library, keep legal/operational refs (chosen — MIT-compliant, name-free user surface, single guard test) · scrub EVERYWHERE incl. LICENSE/script (rejected — breaks MIT attribution + the refresh can't fetch) · leave prose as-is (rejected — the milestone's explicit de-brand goal).
Must:
<must>
  - No method-prose surface names `agency-agents`/`msitarzewski`: book ch.18, glossary persona headword, skill `0-setup.md`, the persona `_template.md.tmpl`, and the engine `constants.py` comment.
  - Those prose surfaces point the persona phase at the local vendored library `.add/personas-teacher/`.
  - The de-brand is mirrored across every tree twin (book 3 + `.add/docs`; skill 2; engine/template 3 + `_bundled`) so no twin keeps the brand.
  - The legal + operational refs KEEP the upstream URL: `personas-teacher/LICENSE`, `THIRD_PARTY_NOTICES.md`, `update_teacher.py`, `personas-teacher/VENDOR.md`.
  - Editing `constants.py` re-pins `ENGINE_PKG_MD5` (all 3 engine trees byte-identical + the single pin re-aimed); `ENGINE_MD5` (add.py) stays unchanged; engine source gains NO "personas-teacher" path literal (bundle-teacher guard holds).
  - A guard test asserts both directions: brand ABSENT from the prose surfaces, brand PRESENT in the legal/operational keepers.
Reject:
<reject>
  - Any method-prose/engine surface still names agency-agents/msitarzewski -> "brand_in_prose"
  - The LICENSE / THIRD_PARTY_NOTICES lost the MIT attribution -> "attribution_stripped"
  - A tree twin diverges (one keeps the brand, another dropped it) -> "twin_drift"
  - `ENGINE_MD5` changed (add.py touched) OR a "personas-teacher" path literal landed in engine source -> "engine_contaminated"
</reject>
After:
<after>
  - `grep -rl "agency-agents"` over the method-prose surfaces returns nothing; over LICENSE/NOTICES/update_teacher.py/VENDOR.md it still returns them.
  - The persona prose points at `.add/personas-teacher/`; full suite green; ENGINE_PKG_MD5 re-aimed + consistent across 3 trees; ENGINE_MD5 unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The de-brand guard must scope to the METHOD-PROSE surfaces only — NOT the dogfood `.add/tasks/*` / `.add/milestones/*` / `.add/state.json` (which legitimately record the brand as project history) nor the keepers — lowest confidence because a naive repo-wide grep would false-red on history + the legal notice; if wrong: the guard over/under-scopes → adjust the file list, no behavior cost.
  - [x] constants.py re-pin is mechanical + authorized — confirmed: the user chose "De-brand + re-pin engine"; ENGINE_MD5 (add.py) is untouched, only ENGINE_PKG_MD5 (the add_engine package) re-aims.
  - [x] The glossary persona headword carries no brand token today (says "*teacher* corpus") — confirmed; it only needs the local-library pointer added.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: method prose carries no upstream brand
  Given the method-prose surfaces (ch.18, glossary, 0-setup, _template, constants.py) across their trees
  When each is scanned for "agency-agents"/"msitarzewski"
  Then none of them names the brand
  And the persona-loop guidance still reads coherently

Scenario: the prose points at the local vendored library
  Given ch.18 + 0-setup + _template + the glossary persona headword
  When the teacher-source pointer is read
  Then it names `.add/personas-teacher/` (the local vendored library)
  And no external fetch is implied

Scenario: legal + operational refs keep the URL
  Given LICENSE, THIRD_PARTY_NOTICES.md, update_teacher.py, VENDOR.md
  When scanned for the upstream URL
  Then the URL is retained (MIT attribution + the refresh source)
  And the de-brand did not over-scrub them

Scenario: engine re-pin is clean
  Given constants.py de-branded across all 3 engine trees
  When the package digest is recomputed
  Then ENGINE_PKG_MD5 equals the digest in every tree AND ENGINE_MD5 (add.py) is unchanged
  And no "personas-teacher" path literal entered engine source

Scenario: every tree twin agrees
  Given the de-branded files and their mirror trees
  When the twins are compared
  Then each de-branded surface is byte-identical across its trees (book/skill/engine/_bundled)
  And no twin still carries the brand
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DE-BRAND CONTRACT — name-free method prose, attribution retained

DROP the brand (agency-agents / msitarzewski) from + repoint at `.add/personas-teacher/`:
  book   : add-method/docs/18-personas.md        (+ ./18-personas.md · .add/docs/ · _bundled/docs/)
           add-method/docs/appendix-c-glossary.md (persona headword — add the local pointer)
  skill  : add-method/skill/add/phases/0-setup.md (+ .claude/skills/add/phases/ · _bundled/skill/)
  tmpl   : add-method/tooling/templates/personas/_template.md.tmpl (+ .add/ · _bundled/)
  engine : add-method/tooling/add_engine/constants.py  (comment only; NO path literal in engine src)
           → 3 engine trees byte-identical; re-aim ENGINE_PKG_MD5 in tooling/engine_pin.py

KEEP the brand (do NOT scrub):
  personas-teacher/LICENSE · THIRD_PARTY_NOTICES.md · scripts/update_teacher.py · personas-teacher/VENDOR.md

OUT of scope (project history, never method prose): .add/tasks/* · .add/milestones/* · .add/state.json

INVARIANTS:
  ENGINE_MD5 (add.py) UNCHANGED · engine src contains no "personas-teacher" literal (bundle-teacher guard)
  MIT attribution retained · book/skill/engine/bundle parity all green
errors: brand_in_prose · attribution_stripped · twin_drift · engine_contaminated
```

Least-sure flag surfaced at freeze: ⚠ [test] the guard must scope to the exact method-prose surface list (not a repo-wide grep) — why: the dogfood `.add/tasks/*` + the legal NOTICES legitimately contain the brand and a broad scan false-reds; cost if wrong: adjust the file list, no behavior change. (Secondary: the engine re-pin is mechanical but a trust-surface change — recorded at the gate for a human spot-audit.)

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

Coverage target: behavioral — one test per scenario; plus repoint the 2 pinned brand-assert tests.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_no_brand_in_prose: scan ch.18/glossary/0-setup/_template/constants.py across their trees / assert no "agency-agents"/"msitarzewski"
  - test_prose_points_at_local_library: assert ch.18 + 0-setup + _template + glossary persona headword name ".add/personas-teacher"
  - test_keepers_retain_url: assert LICENSE/THIRD_PARTY_NOTICES/update_teacher.py/VENDOR.md still carry the upstream URL (no over-scrub)
  - test_engine_repin_clean: assert package_digest==ENGINE_PKG_MD5 across 3 trees, ENGINE_MD5 unchanged, no "personas-teacher" literal in engine source
  - test_twins_byte_identical: assert each de-branded surface is byte-identical across its mirror trees
  - UPDATE test_persona_setup.py: swap the "agency-agents" assert → assert 0-setup names the local teacher library (.add/personas-teacher)
  - UPDATE test_persona_method_docs.py: swap "agency-agents" in the required-terms tuple → "personas-teacher"
</test_plan>

Tests live in: `add-method/tooling/test_debrand_teacher_prose.py` · plus edits to `add-method/tooling/test_persona_setup.py` `add-method/tooling/test_persona_method_docs.py` · MUST run red before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs/` `add-method/../18-personas.md` `add-method/../appendix-c-glossary.md` `add-method/skill/` `add-method/../.claude/` `add-method/tooling/` `add-method/src/` `add-method/../.add/docs/` `add-method/../.add/tooling/`
Strategy (ordered batches): 1. (TESTS) write test_debrand_teacher_prose.py + repoint the 2 pinned brand asserts (red). 2. de-brand canonical prose (ch.18, glossary, 0-setup, _template, constants.py) → repoint at `.add/personas-teacher/`. 3. propagate to mirror twins (book repo-root + .add/docs; skill .claude; engine/template .add/tooling). 4. re-aim ENGINE_PKG_MD5 (recompute package_digest). 5. run prepare_bundle.py to refresh _bundled. 6. full suite green.

Persona (optional): none (de-brand / docs+config task — generic stance)
Known-problem fixes: editing constants.py ripples into ENGINE_PKG_MD5 + 3-tree parity → re-aim the single pin + sync all 3 trees byte-identical · adding a path literal to engine source would trip the bundle-teacher guard → keep constants.py comment path-free ("vendored teacher library", no `.add/personas-teacher` token) · 4-twin glossary/chapter sync → mirror to `.add/docs` too.
Strategy actually used: as planned. De-branded 5 canonical surfaces → repointed at `.add/personas-teacher/`, propagated to twins via `cp` (book repo-root + .add/docs; skill .claude), regenerated `_bundled` via prepare_bundle, re-aimed ENGINE_PKG_MD5 fe09afcd→51671e2b (constants.py comment-only; computed via engine_manifest.package_digest, identical across 3 trees). One unplanned reclaim: the 0-setup.md repoint pushed the phases lean-pool +22 bytes over — trimmed the same bullet's prose (per the lean-pool rule; never touched test_skill_lean) back under 32052.
Safety rule (feature-specific): ENGINE_MD5 (add.py) must stay byte-unchanged; MIT attribution (LICENSE/NOTICES) must survive.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2491/0 (+5 new de-brand tests)
- [x] coverage did not decrease — added the de-brand guard + repointed 2 pinned brand asserts; none removed
- [x] no test or contract was altered during build — the 2 pinned-test repoints + the new guard were written in TESTS phase; build touched only prose/engine/pin/bundle
- [x] the green was EARNED, not gamed — verified by a direct repo-wide grep (prose clean, keepers retained) independent of the test; the de-brand is real
- [x] concurrency / timing of the risky operation is safe — pure text/comment edits + a derived hash re-pin; no runtime path
- [x] no exposed secrets, injection openings, or unexpected dependencies — removed text only; no new dep
- [x] layering & dependencies follow CONVENTIONS.md — book/skill/engine/bundle parity all green; engine source carries no teacher path literal
- [x] a person reviewed and approved the change — Tin Dang (contract frozen @ v1; chose "De-brand + re-pin engine" for the engine surface)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] the brand grep over the 5 prose surfaces (all trees) returns nothing — confirmed: manual `grep -rIl` printed "(clean — no brand in prose)"; test_no_brand_in_prose green
- [x] the same grep over LICENSE/THIRD_PARTY_NOTICES/update_teacher.py/VENDOR.md STILL returns them — confirmed: grep listed VENDOR.md + update_teacher.py; test_keepers_retain_url green
- [x] ch.18/0-setup/_template/glossary name `.add/personas-teacher/` as the teacher source — confirmed by test_prose_points_at_local_library
- [x] package_digest==ENGINE_PKG_MD5 (51671e2b) across 3 trees; ENGINE_MD5 unchanged (d15f4180); no "personas-teacher" literal in engine src — confirmed by test_engine_repin_clean + engine-skeleton/repin-parity green
- [x] every de-branded surface byte-identical across its mirror trees; _bundled refreshed — confirmed by test_twins_byte_identical + test_book_parity/test_tree_parity/test_bundle_parity green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — engine_manifest.package_digest recomputed + re-pinned; every de-branded surface re-propagated to its twins + bundle
- [x] DEAD-CODE (code) — no orphaned symbol; the only code change is a one-line comment in constants.py + the single pin literal
- [x] SEMANTIC (prose / non-code) — read all 5 de-branded surfaces in full: each drops the brand, points at `.add/personas-teacher/`, and the persona-loop guidance still reads coherently; the lean-pool prose trim preserved the asserted tokens (persona/author/teacher/personas-teacher/baseline approval)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: ran a direct repo-wide grep INDEPENDENT of the guard — confirmed the brand is gone from all 5 prose surfaces (every tree) yet retained in the keepers (VENDOR.md, update_teacher.py). Probed the engine re-pin for a vacuous swap: package_digest was recomputed from the actual changed bytes and matches across all 3 trees; ENGINE_MD5 (add.py) is byte-unchanged, proving the re-pin is the constants.py comment delta only. Probed that the lean-pool trim didn't drop an asserted token — test_persona_setup green. Probed engine contamination — no "personas-teacher" literal entered engine source.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — text/comment removal + a derived-hash re-pin; no executable path, no secret, no input surface; MIT attribution (LICENSE/NOTICES) retained.
2. Concurrency: CLEAR — no runtime/concurrent path touched.
3. Architecture: CLEAR — de-brand respected every parity boundary (book/skill/engine/bundle); engine kept hands-off (no teacher path literal); the single-source pin re-aimed cleanly across 3 trees.
Verdict: PASS
Residue: none — NOTE for the human spot-audit: ENGINE_PKG_MD5 re-aimed fe09afcd→51671e2b (constants.py persona comment de-branded, comment-only; ENGINE_MD5/add.py byte-unchanged). User pre-authorized "De-brand + re-pin engine".
Binding: advisory — sensitivity mechanical (prose de-brand + a comment-only engine re-pin; no logic/contract/API change)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose de-brand prose + repoint at the local library, keep legal/operational refs; rejected scrub EVERYWHERE incl. LICENSE/script (rejected — breaks MIT attribution + the refresh can't fetch) · leave prose as-is (rejected — the milestone's explicit de-brand goal).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. De-branded 5 canonical surfaces → repointed at `.add/personas-teacher/`, propagated to twins via `cp` (book repo-root + .add/docs; skill .claude), regenerated `_bundled` via prepare_bundle, re-aimed ENGINE_PKG_MD5 fe09afcd→51671e2b (constants.py comment-only; computed via engine_manifest.package_digest, identical across 3 trees). One unplanned reclaim: the 0-setup.md repoint pushed the phases lean-pool +22 bytes over — trimmed the same bullet's prose (per the lean-pool rule; never touched test_skill_lean) back under 32052.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
