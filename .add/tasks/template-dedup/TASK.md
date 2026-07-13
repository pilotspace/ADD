# TASK: Template comment dedup: EXIT pointers + engine-stamp comments

slug: template-dedup · created: 2026-07-13 · stage: mvp
milestone: ceremony-to-effort
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: template comment dedup — TASK.md.tmpl comments restate content whose canonical home is elsewhere (weight audit 2026-07-13, re-grounded: 11 comment blocks / 2848B, 2B under the 2850 ceiling). GROUND CORRECTION: the audit's "11 EXIT comments" = 11 total comment blocks, of which 5 carry EXIT sentences.
Must:
  - every EXIT-carrying comment compresses to a pointer-sized line (<=120B) — the phase guide read in the same turn carries the full gate
  - v2: the freeze mega-comment + §4 declare-paths comment keep their grammar restatements VERBATIM (4 pre-existing suites pin the template as the frozen scope-decl declaration surface — the assumption's named cost realized)
  - the Ground SHA comment (BOTH templates) says the engine stamps it at freeze and stops instructing `git rev-parse` hand-typing (derived-stamps shipped the stamp); phases/3-plan.md's Ground SHA bullet says the same
  - total template comment bytes <= 2650 (v2; headroom reclaimed under the existing 2850 ceiling)
Reject:
  - deleting a comment that carries UNIQUE load-bearing content (the Reported: field prompts, the skips block) -> keep, never dedup an attestation prompt
  - any new `<tag>` token in a comment -> the frozen tag census must stay green
Accept: Given the compressed template, When a fresh task renders, Then every comment either points or carries unique content, the ceilings bind with >=400B headroom, and all 5 template twins stay byte-identical.
Boundary: two template dialects — TASK.md.tmpl and TASK.fast.md.tmpl both carry the Ground SHA comment; both get the engine-stamps wording
Assumptions: ⚠ no suite pins the EXIT sentences' TEXT — why: grounded test_phase_detail/test_strip_scaffold_at_done pin only the STRIP behavior on fixture-local markers; if wrong: a pin surfaces at the full suite and the sentence is restored verbatim (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): templates/TASK.md.tmpl (11 comments: EXIT x5 at 36/54/94/109/121 · freeze mega-comment 948B · scope-lock 272B · Ground SHA line 68) · templates/TASK.fast.md.tmpl (Ground SHA line 38) · skill/add/phases/3-plan.md:22 (rev-parse bullet) · x5 template twins · x3 skill trees
Context (working folder): ceilings SIZE 12400B / COMMENT 2850B (test_taskmd_lean + test_facet_adr_harvest) — maxima, shrinking safe
Honors (patterns / conventions): frozen tag census (no new <tag> tokens); slang guard; twin byte-parity x5 (+x3 skill); strip-scaffold behavior untouched (comments still strip at done)
Anchors the contract cites: the 11 comment blocks · Ground SHA lines · 3-plan.md Ground SHA bullet
Ground SHA: 789e0cc — pins re-grounded: test_phase_detail/test_strip_scaffold pin STRIP behavior only, fixture-local markers, not template text

### Contract

```
TASK.md.tmpl comment layer, content-preserving-by-pointer:
  §1/§2/§4 EXIT comments -> `<!-- EXIT: the phase guide's exit_gate binds. -->`-class
    pointers, <=120B each, phase-guide named implicitly by the section
  v2 (change request, discovered at the full-suite fence): the scope grammar
    restatements are PINNED template content — 4 suites (declare-grammar-doc,
    path-confinement, scope-decl-template x2) hold the template as the frozen
    scope-decl declaration surface. The freeze mega-comment and the §4 declare-
    paths comment RESTORE verbatim; dedup narrows to the EXIT pointers, the
    scope-lock trim, and the Ground SHA stamps.
  §5 scope-lock comment -> keeps scope-lock source + exit pointer, <=170B
  Ground SHA comment (both tmpls) -> `<stamped by freeze — leave this placeholder;
    cite symbols, not bare line numbers>`; 3-plan.md bullet -> "stamped by freeze"
  Total comment bytes <= 2650 (v2 — grammar restored); SIZE ceiling untouched; census green;
  x5 twins byte-identical; TASK.fast.md.tmpl same Ground SHA treatment.
```

`Least-sure flag surfaced at freeze:` [test] the <=120B/<=2400B numeric pins — why: byte-count assertions are brittle to future template growth and may fight a later task's legitimate comment need; if wrong: the pin is loosened by THAT task's own frozen bundle, never silently (cost: one deliberate re-pin)
Status: FROZEN @ v2 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/` `.claude/skills/`
Strategy & known-problem fixes: 1) red tests in add-method/tooling/test_template_dedup.py 2) compress comments in canonical TASK.md.tmpl + fast twin 3) 3-plan.md bullet 4) sync x5 template twins + x3 skill trees 5) full-suite fence. Traps: the .add/tooling/templates/templates 5th twin; skill-tree byte pools bind 3-plan.md edits (compress-to-absorb); comments must still STRIP clean at done (no nested `--`).
Approach (domain strategy): pointer-over-restatement, canonical-home-per-rule, byte-budgeted

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (comment lines 36/54/94/109/121 · Ground SHA 68/38 · 3-plan.md:22 — at 789e0cc)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (numeric-pin brittleness, bounded to a deliberate re-pin)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T11:05:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_exit_comments_are_pointers (<=120B each) · test_scope_grammar_not_restated (no "sibling of the previous token" in tmpl) · test_ground_sha_comment_says_engine_stamps_both_tmpls (+ no rev-parse instruction) · test_plan_guide_bullet_updated · test_comment_budget (<=2400B) · test_no_new_census_tags (comment tag vocab unchanged).
Tests live in: `add-method/tooling/test_template_dedup.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: v1 deleted the grammar restatements per the audit; the full-suite fence refuted it (4 pins hold the template as the frozen scope-decl declaration surface) — v2 change request restored them verbatim (minus a slang 'seam' wording + the redundant EXIT: tail) and my M2 test flipped into its OPPOSITE (a pin protecting the restatement). Net: comments 2848->2568B (-10%, not v1's claimed -37%), EXIT pointers + scope-lock trim + Ground-SHA stamp comments kept, lean pins (one merged §3 comment · <12 total) honored by merging not splitting.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (test edits rode the v2 re-freeze, TESTS phase)
- [x] green was EARNED — 5 red-first v1; the v2 flip is itself fence-derived, not convenience (the fence REFUTED v1)
- [x] input dialect held — tests assert the template's own literal strings
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose/comment-only change, zero engine bytes

Build expectations (from §1 Accept + §3 CONTRACT): every comment points or carries unique/pinned content; ceilings bind with headroom (2568/2850 comments · 12055/12400 size); x5 twins byte-identical — confirmed by test_template_dedup 6/6 + 86 neighbor tests + full suite 3463/3463 OK

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

