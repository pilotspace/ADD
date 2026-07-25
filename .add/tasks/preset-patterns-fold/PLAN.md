# PLAN: Retire the 12 orphaned preset persona templates

slug: preset-patterns-fold
kind: docs · created: 2026-07-25 · stage: mvp
milestone: persona-template-completeness
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the 12 orphaned preset persona templates are deleted from all three tooling trees, finishing the retirement commit `e29ddac4` began — removing ~96K of dead weight from the npm tarball and the pip wheel, and removing the trap of an authoritative-looking artifact nothing loads.

Framings weighed: retire (chosen — no consumer exists, and the persona-author skill plus its two worked example assets ARE the seeding path; a shipped template nobody renders is a lie about how the method works) · fold-them-as-an-example-corpus (rejected — pays ~48 authored sections and keeps 96K shipping, for a library `references/seeding.md` already points at better via the vendored teacher corpus) · revive-them-with-a-seeding-verb (rejected — an engine change with a pin re-aim that partly re-litigates the deliberate e29ddac4 decision to go skill-authored).

Must:
<must>
  - M1: 11 of the 12 `*.md.tmpl` files under `templates/personas/` are deleted from all 3 tooling trees (33 files), and the now-empty `templates/personas/` directory is gone from each.
  - M1b: `software-architect.md.tmpl` is PROMOTED, not deleted — it lands as `persona-author/assets/example-architect-persona.md` in all 3 skill trees, where the skill's example list actually reads it.
  - M1c: the promoted example is brought to the four-leg standard before it lands: an ORIENT-first `## Abilities` (it has none today), a per-flow stance for the `design, advisor` flows it claims (it has none today), and an `## Escalation` section. The last one is the POINT of a third example — `example-persona.md` and `example-design-persona.md` both already demonstrate ORIENT and a per-flow stance, and NEITHER demonstrates `## Escalation`.
  - M1d: `SKILL.md` names the third example in its assets list and states what it demonstrates that the other two do not, in all 3 skill trees.
  - M2: no live code path, test assertion, or reader-facing doc references `templates/personas/` after the removal — historical task PLANs under `.add/tasks/` are an immutable archive and are excluded.
  - M3: the stale `templates/personas/_template.md.tmpl` reference in `test_persona_task_kinds.py`'s CONTRACT docstring is corrected — it already names a file deleted at `e29ddac4`, and leaving it re-seeds the confusion this task removes.
  - M4: the FULL tooling suite is green — a deletion this wide is only safe if nothing depended on the files, and only the whole suite can show that.
  - M5: `add.py init` still scaffolds a working project in a scratch dir (fresh-init smoke), proving no seeding path silently depended on them.
  - M6: the 3 tooling trees agree after the removal — `test_tree_parity` globs `templates/**/*.tmpl` dynamically, so it passes only if the deletion is uniform.
</must>
Reject:
<reject>
  - an edit to `add.py` or `add_engine/*` (no engine change is needed; the presets are unreferenced) -> "engine_scope_violation"
  - a deletion applied to some tooling trees but not all -> "mirror_gap"
  - a live reference to `templates/personas/` left outside the `.add/tasks/` archive -> "dangling_reference"
</reject>
After:
<after>
  - `init` behaves identically, because nothing ever read these files.
  - the shipped npm tarball and pip wheel stop carrying ~96K of unreachable templates.
  - the only documented way to create a persona is the one that actually works: the persona-author skill, seeded from the vendored teacher corpus.
</after>
Boundary: none — no external input; a uniform deletion across three mirrored trees.
<assumptions>
  ⚠ that no test asserts a COUNT over the templates tree. This repo has pinned-count meta-tests elsewhere (FLOOR_DEF_COUNTS; test_ci_tooling_mirror_gap's pinned skip count), and greps found only a dynamic glob plus one docstring — but a pinned count would go red on deletion. If one exists it is a legitimate in-scope pin update, recorded rather than silently re-tuned. This is exactly why M4 runs the FULL suite instead of a targeted set.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
PROMOTE templates/personas/software-architect.md.tmpl
     -> persona-author/assets/example-architect-persona.md  (3 skill trees)
     upgraded to the four legs first: ORIENT-first ## Abilities · a per-flow
     stance for its `design, advisor` flows · ## Escalation.
     WHY this one: it is the strongest of the twelve (trade-off matrices,
     reversibility, ADR discipline), and a third example earns its place only
     by demonstrating something the other two do not — both existing assets
     already show ORIENT and a per-flow stance; NEITHER shows ## Escalation.
  ~ SKILL.md assets list gains it, with what it demonstrates (3 skill trees).

DELETE the OTHER 11 templates/personas/*.md.tmpl from each of 3 tooling trees:
    add-method/tooling/templates/personas/
    .add/tooling/templates/personas/
    add-method/src/add_method/_bundled/tooling/templates/personas/
  = 33 files; the templates/personas/ directory itself goes with them.

  build-engineer · data-steward · evidence-verifier · platform-engineer
  product-lead · quality-auditor · release-manager · security-gatekeeper
  stream-orchestrator · technical-writer · ux-experience-lead

EDIT add-method/tooling/test_persona_task_kinds.py
  ~ CONTRACT docstring line naming templates/personas/_template.md.tmpl
    (a file deleted at e29ddac4) -> name the live schema source instead.
    Test files are NOT pinned: package_files walks add_engine/*.py only.

UNCHANGED (asserted): add.py · add_engine/* · ENGINE_MD5 · ENGINE_PKG_MD5 ·
    .add/personas/ (the live roster) · personas-teacher/ (the vendored corpus,
    which is the real seeding source and is NOT affected)

WHY SAFE: test_tree_parity globs templates/**/*.tmpl dynamically (line ~120),
    so a uniform deletion keeps it green; no other test references the files.
```

Target (measurable): `example-architect-persona.md` present + byte-identical across the 3 skill trees, carrying ORIENT + per-flow stance + the only `## Escalation` among the 3 assets, and named in SKILL.md · 0 files remain under `templates/personas/` in all 3 tooling trees · 0 live references to `templates/personas/` outside `.add/tasks/` · FULL tooling suite green with 0 failures · a fresh `add.py init` in a scratch dir scaffolds without error and creates an empty `.add/personas/` · `git diff main` on `add.py` + `add_engine/` empty and both pin literals unchanged.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/.add/tooling/` `.claude/skills/add/persona-author/` `add-method/skill/add/persona-author/` `add-method/src/add_method/_bundled/skill/add/persona-author/` `add-method/build/` `./`

Regression floor: the FULL tooling suite (`python3 -m unittest discover -s add-method/tooling -p 'test_*.py'`) — not a targeted subset. A 36-file deletion's whole risk is an unknown dependency, and only the full suite can rule that out. Plus `python3 .add/tooling/add.py check` and a fresh-init smoke in a scratch dir.
Persona (optional): `.add/personas/method-product-owner.md` — this is a method-shape decision (retire a shipped artifact vs keep it), and its Critical Rules include the ceremony/weight discipline that makes retirement the right call.

Least-sure flag surfaced at freeze: [test] whether a pinned-count meta-test covers the templates tree. Greps found only a dynamic glob and one docstring, but this repo HAS pinned-count tests that go red on file-set changes (FLOOR_DEF_COUNTS; test_ci_tooling_mirror_gap's pinned skip count), and a grep that finds nothing is weaker evidence than a suite that runs. The full-suite regression floor is the mitigation, not the assumption.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - check_presets_gone: 0 files match `templates/personas/*.tmpl` in all 3 tooling trees, and the `templates/personas/` directory does not exist in any of them. RED now: 12 files in each of 3 trees. · covers: M1
  - check_architect_example_promoted: `persona-author/assets/example-architect-persona.md` exists in all 3 skill trees, is byte-identical across them, and is schema-conformant as a persona (the four required sections present). RED now: the file does not exist. · covers: M1b
  - check_example_demonstrates_escalation: the promoted example carries an ORIENT-first `## Abilities`, a per-flow stance line for its two declared flows, and an `## Escalation` section — and it is the ONLY one of the three assets with `## Escalation`, which is its reason to exist. RED now: the source preset has no Abilities, no stance, and no Escalation; and 0 of the 3 assets demonstrate Escalation. · covers: M1c
  - check_skill_names_third_example: `SKILL.md` lists the third asset and says what it demonstrates that the other two do not, in all 3 skill trees. RED now: SKILL.md names two assets. · covers: M1d
  - check_no_live_reference: no file outside `.add/tasks/` (the immutable task archive) references `templates/personas/`. RED now: `test_persona_task_kinds.py` docstring names `templates/personas/_template.md.tmpl`. · covers: M2, M3, R:dangling_reference
  - check_full_suite_green: the FULL tooling suite runs with 0 failures and 0 errors. This is the check that actually decides whether the deletion was safe; it is deliberately not narrowed to a subset. GREEN now and must STAY green. · covers: M4
  - check_fresh_init_smoke: `add.py init` in a scratch dir exits 0 and produces an empty `.add/personas/` directory — proving no seeding path read the deleted templates. GREEN now (it never read them) and must STAY green; a failure here would mean the retirement premise was wrong. · covers: M5
  - check_tree_parity_uniform: `test_tree_parity` green — it globs `templates/**/*.tmpl` from the canonical tree and asserts twins agree, so a partial deletion shows up here. GREEN now and must STAY green. · covers: M6, R:mirror_gap
  - check_engine_untouched: `git diff --stat main -- add-method/tooling/add.py add-method/tooling/add_engine/` empty; both pin literals unchanged. GREEN now and must STAY green. · covers: R:engine_scope_violation
  - check_teacher_corpus_intact: `.add/personas-teacher/` and the live `.add/personas/` roster are untouched — the deletion must hit the orphaned TEMPLATES only, not the vendored corpus that is the real seeding source or the 9 working personas. GREEN now and must STAY green. · covers: (standing floor — the blast-radius guard for a wide delete)
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: evidence · MUST run red before Build.

Non-coding task (`kind: docs`): §4 is a failing-first ACCEPTANCE CHECK set. Two are RED now (36 preset files exist; one live docstring reference). Five are standing GREEN checks — and for a DELETION that is the correct ratio: the risk of removing files is not that the removal fails, it is that something depended on them. The standing checks are the real test, which is why `check_full_suite_green` runs the whole suite rather than a chosen subset.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: promoted first, then deleted — so the kept content was safe before anything was removed. TWO corrections. (1) THE FULL-SUITE FLOOR PAID FOR ITSELF: the templates tree is FOUR-way, not three. `add-method/.add/tooling/templates/` is the dogfood install INSIDE add-method/ and is distinct from the repo-root `.add/tooling/`. My §3 named three trees, so the first deletion was PARTIAL, and `test_template_flag_vocabulary.TemplateTreeParity` failed on the file-set mismatch. Nothing short of the full suite would have caught it — this is exactly the risk the [test] least-sure flag named, and the reason M4 mandated the whole suite instead of a targeted subset. Scope widened by `re-cross --by`, fourth tree deleted, suite re-run clean. (2) The promoted example's `source:` line carried a literal `templates/personas/...` path, which `check_no_live_reference` flagged — correctly: a provenance note that reads like a live path is the same defect class this task removes. Reworded to name the retired preset without a path token.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all §4 acceptance checks pass — 7/7 (plus the 3 added for the promote-one variant = 10/10). Presets gone from all FOUR tooling trees; the promoted example present and byte-identical across 3 skill trees; SKILL.md names it in all 3.
- [x] coverage did not decrease — n/a for `kind: docs`; no code paths removed (nothing referenced the deleted files).
- [x] no test or contract was altered during build — one test file WAS edited (M3's stale docstring, an explicit Must) and the §5 scope was widened, both through `re-cross --by`. Frozen §3 unchanged.
- [x] the green was EARNED — the FULL suite ran twice: 2316 tests FAILED (1) before the fourth tree was found, then 2316 tests OK after. The first run is the evidence that the check was real and not decorative.
- [x] concurrency / timing — n/a.
- [x] no exposed secrets, injection openings, or unexpected dependencies — a deletion plus one promoted markdown example.
- [x] layering & dependencies — `add.py`/`add_engine/` diff vs main empty, both pins unchanged; teacher corpus (23 dirs) and the live 9-persona roster untouched; fresh `add.py init` exits 0 and still creates an EMPTY `.add/personas/`, proving no seeding path read the deleted templates.
- [x] a person reviewed and approved the change — Tin Dang, at the verify gate, having required the package-build verification that found the third orphan

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: the premise of the whole task — that the presets were truly orphaned — and the blast radius of a wide delete.
  (1) The orphan claim was established from FOUR independent directions before deleting anything: `constants.SETUP_FILES` (no persona entry), `add.py:770` (an explicit comment that personas are skill-authored, not template-seeded), `bin/cli.js` (references personas-teacher only), `scripts/prepare_bundle.py` (same). Then confirmed EMPIRICALLY after the fact: a fresh `init` exits 0 and produces an empty `.add/personas/`.
  (2) The blast radius was guarded by a dedicated standing check (`check_teacher_corpus_intact`), because the failure mode of a wide `rm -rf` is hitting the neighbour — `personas-teacher/` is the real seeding source and sits one directory away in name.
  (3) The full suite was run rather than a chosen subset, and it FAILED first. A targeted run of the tests I predicted would matter (`test_tree_parity`, `test_ci_tooling_mirror_gap`) would have passed and shipped a half-deleted four-way tree.
  (4) PACKAGE-BUILD VERIFICATION (added at the human's request before the gate, and it earned its place): building the real artifacts found a THIRD orphan that the entire 2316-test suite could not. The wheel still carried `_bundled/tooling/templates/personas/_template.md.tmpl` — the very file `e29ddac4` documented as retired — sourced from the stale gitignored `add-method/build/lib/` tree that setuptools reuses as a build cache. That file has been shipping in every wheel since e29ddac4. The suite cannot see this because it reads the source trees, not the built artifact. Cache removed; both artifacts rebuilt and inspected:
        wheel  pilotspace_add-2.4.0-py3-none-any.whl : templates/personas=0 · _template.md.tmpl=0 · example-architect-persona.md=1 · personas-teacher=259
        npm    pilotspace-add-2.4.0.tgz (328 files)  : templates/personas=0 · _template.md.tmpl=0 · example-architect-persona.md=1 · personas-teacher=259
      Removing the cache registered a pending scope_violation — `build/` is gitignored but is NOT pruned from the engine's scope walk — so the scope was widened by a second `re-cross --by` rather than the touch being hidden.
  Residual: none in scope. The `.add/tasks/` and `.add/milestones/` archive still contains historical references to `templates/personas/` — deliberately, per M2: those documents record what was true when they were written, and rewriting them would destroy the audit trail this method depends on.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose retire; rejected fold-them-as-an-example-corpus (rejected — pays ~48 authored sections and keeps 96K shipping, for a library `references/seeding.md` already points at better via the vendored teacher corpus) · revive-them-with-a-seeding-verb (rejected — an engine change with a pin re-aim that partly re-litigates the deliberate e29ddac4 decision to go skill-authored).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: promoted first, then deleted — so the kept content was safe before anything was removed. TWO corrections. (1) THE FULL-SUITE FLOOR PAID FOR ITSELF: the templates tree is FOUR-way, not three. `add-method/.add/tooling/templates/` is the dogfood install INSIDE add-method/ and is distinct from the repo-root `.add/tooling/`. My §3 named three trees, so the first deletion was PARTIAL, and `test_template_flag_vocabulary.TemplateTreeParity` failed on the file-set mismatch. Nothing short of the full suite would have caught it — this is exactly the risk the [test] least-sure flag named, and the reason M4 mandated the whole suite instead of a targeted subset. Scope widened by `re-cross --by`, fourth tree deleted, suite re-run clean. (2) The promoted example's `source:` line carried a literal `templates/personas/...` path, which `check_no_live_reference` flagged — correctly: a provenance note that reads like a live path is the same defect class this task removes. Reworded to name the retired preset without a path token.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
