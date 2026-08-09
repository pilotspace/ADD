# PLAN: Seed the three method-lens planner personas on init (non-clobbering, load-proven)

slug: seed-method-personas · created: 2026-07-25 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: seed the three METHOD-LENS planner personas (task-planner · milestone-planner · release-planner) into `.add/personas/` at `init` and `migrate`, non-clobbering, and prove a surface loads them.
Framings weighed: seed-into-the-roster (chosen — `status --all` reads `.add/personas/`, so that is the only location a surface actually loads) · ship-as-a-library-the-ladder-copies-from (rejected — a second location nothing reads recreates the retired-preset failure) · leave-unseeded (rejected — every project is forced onto the ladder's most expensive rung, author, for lenses identical in every project)
Must:
<must>
  - M1 `init` seeds exactly the three method personas into `.add/personas/`, schema-conformant
  - M2 `migrate` retrofits the same three into an existing project (the `_seed_spec_file` twin-call precedent)
  - M3 a seeded persona is LOADED, not merely present — the `status --all` roster lists all three by slug and flow
  - M4 seeding is non-clobbering — a persona the user has edited is returned untouched, never overwritten
  - M5 the shipped artifacts (wheel + npm tarball) carry the three seed files
</must>
Reject:
<reject>
  - a seed whose template renders blank or missing -> skipped with a warning, never a 0-byte survivor file -> "seed_skipped_blank"
  - a domain-lens persona proposed for seeding -> refused by the written criterion in contract.md -> "not_a_method_lens"
</reject>
After:
<after>
  - a fresh `init` reports a roster of three instead of `personas: unseeded`
  - re-running `init` or `migrate` over a customised roster leaves every existing persona byte-identical
  - `add.py check` reports 0 failed and no persona-quality WARN for the seeded three
</after>
Boundary: one variant per pre-existing roster state the tests must speak — an empty `.add/personas/` (fresh init) vs a roster already holding a user-edited file of the same slug (the clobber case).
<assumptions>
  ⚠ that reversing the documented `persona-skill:` decision at add.py:771 (personas are AUTHORED, not seeded from a template) is right for THIS class of persona — if wrong: we re-ship dead weight one day after retiring 12 presets for exactly that, and the contract.md criterion is the only thing holding the line
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
add.py init      -> seeds .add/personas/ with task-planner, milestone-planner, release-planner
add.py migrate   -> the same three, retrofitted into an existing project
  existing file present  -> returned untouched (never clobbered)
  template missing/blank -> skipped + stderr warning -> "seed_skipped_blank"
  domain-lens candidate  -> refused by the contract.md criterion -> "not_a_method_lens"
New symbols: METHOD_PERSONAS (tuple of 3 slugs) and _seed_persona_file(root, slug)
  mirrors _seed_spec_file exactly — never clobber, never write blank, returns the path
  either way so init and migrate share ONE seeding truth, not two drifting copies
Seed content: templates/personas/[slug].md.tmpl across all four tooling trees
  (reuses the existing template-tree parity test for free mirror-gap protection)
Criterion (written into persona-author/references/contract.md, all three skill trees):
  ship a persona ONLY if it reasons about ADD's own artifacts — PLAN.md sections, the
  frozen contract, the milestone DAG, the release cut — never about a project domain
  (security, data, UX). The three planners qualify; 11 of the 12 retired presets did not.
```

Target (measurable): a fresh `init` yields a 3-persona roster printed by `status --all`; `add.py check` 0 failed with 0 persona WARNs; the full tooling suite green (2316 today plus the new cases); `wording_lint` 0 findings; and BOTH built artifacts (wheel + npm tarball) contain all three seed files — verified by unzipping them, not by reading the source tree (the lesson the preset retirement taught).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/.add/tooling/` `add-method/skill/add/persona-author/references/contract.md` `.claude/skills/add/persona-author/references/contract.md` `add-method/src/add_method/_bundled/skill/add/persona-author/references/contract.md`
Regression floor: the full `add-method/tooling` unittest suite (2316 today) plus `wording_lint.py` plus `add.py check` — all three green before the gate
Persona (optional): `.add/personas/methodology-engine-dev.md`

Least-sure flag surfaced at freeze: [contract] this task REVERSES a documented engine decision — add.py:771 states personas are authored, never seeded — one day after we retired 12 preset personas for having no consumer. The bundle rests entirely on the method-lens vs domain-lens distinction being real and enforceable rather than a rationalisation. If that line does not hold, this is the same mistake with better paperwork.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_init_seeds_the_three_method_personas: init a temp project / assert .add/personas/ holds exactly the 3 slugs, each schema-conformant · covers: M1
  - test_migrate_retrofits_method_personas: init at an older shape, remove the personas, run migrate / assert the 3 are restored · covers: M2
  - test_seeded_personas_appear_in_the_status_roster: init / run `status --all` / assert each slug AND its flow list is printed — the LOAD proof, not a presence check · covers: M3
  - test_seeding_never_clobbers_an_edited_persona: write a sentinel body into task-planner.md / re-run init and migrate / assert bytes unchanged · covers: M4
  - test_blank_template_is_skipped_not_seeded_empty: point the loader at a blank template / assert no 0-byte file and a stderr warning · covers: R:seed_skipped_blank
  - test_method_persona_seeds_ship_in_both_artifacts: build the wheel and npm tarball / assert all 3 seed files present in each · covers: M5
  - test_shipping_criterion_documented: assert the method-lens vs domain-lens rule is present in all three persona-author contract.md trees · covers: R:not_a_method_lens
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Build-guidance, not gated: the engine pins (ENGINE_MD5, ENGINE_PKG_MD5) must be re-pinned and the four tooling twins kept byte-identical — the existing mirror-gap and parity tests already enforce both, so this task adds no new case for them.

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus two unplanned repairs. (1) The template flag-vocabulary
guard fired on the seed content — `templates/` had never held persona files, so its rule "every
flag cited here is an add.py flag" met `git log --oneline` / `git diff --stat`. Reworded the seed
prose in all 4 tooling trees + the 3 authored sources rather than relax the guard. (2) Four
pre-existing tests encoded the superseded "personas dir starts empty" contract; re-crossed
(approved by Tin Dang) — 3 were setup drift repaired with coverage preserved verbatim, 1
(test_init_creates_empty_personas_dir -> test_init_seeds_only_the_method_personas) genuinely
rewritten to the new contract.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2327 OK (untainted run) · wording_lint 0 findings · add.py check 317 passed / 0 failed · test_packaging 16/16 incl. both M5 artifact tests
- [x] coverage did not decrease — +11 tests; the 4 re-crossed cases keep asserting the same behaviours (3 setup-only repairs)
- [!] TESTS WERE ALTERED — NOT an unrecorded build edit: 4 pre-existing tests encoded the contract this task supersedes. Declared and human-approved via `re-cross --by "Tin Dang"` BEFORE any edit. Recording as a flagged deviation, not a tick.
- [x] the green was EARNED — mutation-proven: disabling the seeding call in add.py turns 4/9 red; add.py restored byte-identical (md5 checked). A vacuous wheel test WAS found (inserted after `if __name__`, never collected) and relocated — it now runs against a real built wheel.
- [x] concurrency / timing safe — seeding is a bounded loop over a 3-element constant through `_atomic_write`; never-clobber makes a re-run idempotent
- [x] no exposed secrets, injection openings, or unexpected dependencies — paths derive from the fixed METHOD_PERSONAS tuple, no user input reaches a path (no traversal); no new deps
- [x] layering & dependencies follow CONVENTIONS.md — `_seed_persona_file` mirrors `_seed_spec_file`; one seeding truth shared by init and migrate
- [~] a person approved the re-cross and the freeze; a full line-by-line human code review has NOT happened — stated, not assumed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) mutation test — disabled the init seeding call, confirmed 4/9 tests
go red, restored add.py byte-identical; (2) the loosest assertion `assertIn(rc,(0,1))` could have hidden an
early bail, so proved by hand that `init --force` returns 0 AND reaches seeding (it restored a deleted
persona) while leaving an edited one untouched — then tightened it to `rc == 0`; (3) both engine pins
recomputed live and matched; add.py byte-identical across all 4 tooling trees; (4) M5 read from a REAL built
wheel and `npm pack --dry-run`, never the source tree. KNOWN LIMIT: only 4/9 tests detect the mutant because
migrate seeds via its own path — the load proof is not uniformly redundant.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose seed-into-the-roster; rejected ship-as-a-library-the-ladder-copies-from (rejected — a second location nothing reads recreates the retired-preset failure) · leave-unseeded (rejected — every project is forced onto the ladder's most expensive rung, author, for lenses identical in every project)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus two unplanned repairs. (1) The template flag-vocabulary guard fired on the seed content — `templates/` had never held persona files, so its rule "every flag cited here is an add.py flag" met `git log --oneline` / `git diff --stat`. Reworded the seed prose in all 4 tooling trees + the 3 authored sources rather than relax the guard. (2) Four pre-existing tests encoded the superseded "personas dir starts empty" contract; re-crossed (approved by Tin Dang) — 3 were setup drift repaired with coverage preserved verbatim, 1 (test_init_creates_empty_personas_dir -> test_init_seeds_only_the_method_personas) genuinely rewritten to the new contract.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
