# MILESTONE: Build-expectations in VERIFY

goal: The §6 VERIFY step lets the AI pre-declare observable build expectations (derived from §2 scenarios + §3 contract) that verify confirms — so a build is checked correct, not merely test-green.
rationale: new-major — a method-artifact-completeness theme, SIBLING to scope-drafting-quality (both make ADD's method artifacts complete so build/verify are correct); kept a separate milestone because a merged goal would need an "and" (scope.md's own two-milestone rule). Surfaced while drafting scope-complete-position. Template/guide edit, not a frozen contract.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A "Build expectations" subsection in TASK.md.tmpl §6 VERIFY — the AI fills it BEFORE build
     with the observable outcomes a correct build must produce (derived from §2 SCENARIOS + §3
     CONTRACT), each an evidence-you-can-see + a confirmed-by; a cue in phases/6-verify.md to
     fill them before build and CONFIRM each at verify (build-correctness, not just green).
     Landed across the 3 template parity trees + the 3 guide parity trees; pinned by a structure
     test (extending test_template_form_tags) + wording-lint.
Out: No engine (add.py) logic change — the block is AI-filled markdown, like §6's existing
     "### Deep checks" (engine never parses it). No change to gate OUTCOMES (PASS/RISK-ACCEPTED/
     HARD-STOP). No book rewrite beyond a minimal docs/08 accord touch if needed. The existing §6
     checklist items are retained, not replaced. scope-drafting-quality is untouched.

## Shared decisions & glossary deltas   (living — every task must honor these)
- the Build-expectations block is AI-filled prose/checklist (engine-agnostic) — it mirrors §6's
  existing "### Deep checks" subsection shape, so the engine reads the scaffold unchanged.
- expectations are DERIVED from §2 SCENARIOS + §3 CONTRACT — observable evidence, never a
  restatement of a test name (it complements the existing "green was EARNED, not gamed" check).
- 3-tree template parity (TASK.md.tmpl) + 3-tree guide parity (phases/6-verify.md) stay md5-equal.

## Shared / risky contracts (freeze these first)
- TASK.md.tmpl §6 "Build expectations" block shape (heading + fill-before-build cue + observable+confirmed-by rows) -> owning task verify-build-expectations

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] verify-build-expectations   depends-on: none   — Add the §6 Build-expectations block to TASK.md.tmpl + the fill/confirm cue to phases/6-verify.md across all parity trees; pin with a structure test.

## Exit criteria (observable; map each to the task that delivers it)
- [x] TASK.md.tmpl §6 has a "Build expectations" block the AI fills BEFORE build, each row observable + confirmed-by, derived from §2/§3   (← verify-build-expectations)
- [x] phases/6-verify.md cues filling the expectations before build AND confirming each at verify (build-correctness, not just green)   (← verify-build-expectations)
- [x] all template + guide parity copies are md5-equal; the structure test + wording-lint are green; add.py is untouched (ENGINE_MD5 holds)   (← verify-build-expectations)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `TASK.md.tmpl` §6 gains a `### Build expectations` block (fill-before-build cue + observable + confirmed-by rows) across all 3 template parity trees; `test_template_form_tags.py` gains a `BuildExpectationsBlock` class (5 tests: block-present · cue-observable-and-derived · engine-seams-untouched · guide-cues-fill-and-confirm · 3-tree template+guide parity); `add.py` untouched (ENGINE_MD5 holds).
- skill   : `phases/6-verify.md` gains a "Before you build — declare the build expectations" cue + a Part-one checklist line, across all 3 guide parity trees (md5-equal).
- book    : `docs/08-step-6-verify.md` accord (the human chose close-before-gate) — "Part one" + "The verification checklist" now name the pre-declared build-expectation confirmation; mirrored across all 4 copies (canonical · repo-root · `.add/docs` · `_bundled`), md5-equal.

### Cross-task evidence   (one row per task)
- verify-build-expectations : gate=PASS · tests=1276 green · residue=none (high-risk method edit, human-gated; docs/08 book-accord closed before the gate; §5 re-anchored after the §5 default was corrected to the real template/guide/book trees)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — all 3 delivered by `verify-build-expectations` (template + guide block + tooling assertions), suite 1276 green
- goal: §6 VERIFY now lets the AI pre-declare observable build expectations (derived from §2 scenarios + §3 contract) that verify confirms — proven by the `### Build expectations` block in `TASK.md.tmpl`, the fill+confirm cue in `6-verify.md`, the docs/08 accord, and `BuildExpectationsBlock` asserting all of it, md5-equal across the parity trees.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR bundling this milestone (alongside scope-drafting-quality) from the Close ship-review above; the human (TinDang97) reviews + merges
- [ ] no separate publish — these are method-quality template/guide/book edits; they ride the next ADD release cut (release.md) when the closed milestones are bundled
