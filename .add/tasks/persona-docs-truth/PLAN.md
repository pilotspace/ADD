# PLAN: Reconcile the persona chapter with what the surfaces actually read

slug: persona-docs-truth · created: 2026-07-25 · stage: mvp
milestone: persona-template-completeness
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the persona chapter and the delta grammar tell the truth about what the surfaces actually read and route — the retired `_template.md.tmpl` pointer dies, the build-overlay load set matches `agents/add-worker.md`, and `escalation` joins the persona delta hint vocabulary so the section `persona-template-legs` defined can actually grow.

Framings weighed: reconcile-docs-to-behavior (chosen — the agent and the engine are the ground truth; the prose is what drifted, so the prose moves) · change-the-behavior-to-match-the-docs (rejected — would mean narrowing what `add-worker` reads or adding an engine fold writer, both larger and both contradicting "the engine never edits a persona").

Must:
<must>
  - M1: `18-personas.md` cites no path that does not resolve on disk — the `templates/personas/_template.md.tmpl` claim is replaced by the live canonical source (`persona-author/references/contract.md`).
  - M2: the build-overlay load set stated in `18-personas.md` matches what `agents/add-worker.md` §2 actually instructs — the agent reads the persona body and runs its lead commands, so `## Abilities` is named.
  - M3: `deltas.md` persona hint vocabulary gains `escalation`, so a retrospective can grow the `## Escalation` section defined by `persona-template-legs`.
  - M4: `18-personas.md` names Escalation among the sections a confirmed delta can grow.
  - M5: the `## Escalation` routability sentence in `persona-author/references/contract.md` is corrected: routing is gated by the documented `deltas.md` hint vocabulary, NOT by the engine parse. The current sentence reasons from the parse layer and is misleading.
  - M6: every touched file stays byte-identical across its mirror set (2 book twins, 3 skill trees).
</must>
Reject:
<reject>
  - an edit landing in `add.py` or `add_engine/*` -> "engine_scope_violation"
  - a doc claim about what a surface loads or routes that cannot be pointed to in `add-worker.md` or `deltas.md` -> "unverified_claim"
  - a twin left diverged from its mirror set after the edit -> "mirror_gap"
</reject>
After:
<after>
  - a reader of `18-personas.md` can follow every path it cites and reach a file that exists.
  - an author who writes a `## Escalation` section can file a delta that the documented grammar accepts.
  - `persona-template-legs`' contract.md no longer tells an author routing is free when the grammar is closed.
</after>
Boundary: none — no external input; markdown across two mirror sets.
<assumptions>
  ⚠ that adding a fifth hint to the four-hint vocabulary is additive-safe — `test_fold_persona_sections.ProseNamesAllFour` asserts the four are PRESENT (`assertIn` per hint), not that exactly four exist; if that read is wrong the test goes red and the hint addition needs its own pinned-count update.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
ARTIFACT docs/18-personas.md   (canonical: add-method/docs/ · mirror: repo root)
  ~ "four machine-readable parts" para -> the template pointer moves from the
      retired templates/personas/_template.md.tmpl to
      persona-author/references/contract.md (the live canonical schema)
  ~ "Grow" section  -> the growable-section list gains Escalation
  ~ "Apply - build (overlay)" -> the load set matches agents/add-worker.md S2:
      the agent reads the persona BODY and runs its lead commands, so
      ## Abilities is named alongside Identity / Critical Rules / Anti-patterns

ARTIFACT skill/add/deltas.md   (the one home of the delta grammar)
  ~ persona-target hint vocabulary:
      critical-rule|success-metric|anti-pattern|ability
   -> critical-rule|success-metric|anti-pattern|ability|escalation

ARTIFACT persona-author/references/contract.md   (correction from persona-template-legs)
  ~ the ## Escalation "Routable:" sentence -> cites the deltas.md hint
      vocabulary as the gate; drops the "hint is free text, so nothing in the
      engine has to change" reasoning (true of the PARSE, wrong about the gate)

MIRRORS: book x2 (add-method/docs canonical + repo root) · skill x3
UNCHANGED (asserted): add.py · add_engine/* · ENGINE_MD5 · ENGINE_PKG_MD5
```

Target (measurable): 0 unresolvable paths cited in `18-personas.md` · the book overlay list names Abilities · `escalation` present in `deltas.md` across 3 skill trees · "Escalation" present in the book's growable-section list · `contract.md` Escalation entry cites `deltas.md` and no longer says "free text" · `test_fold_persona_sections` OK · md5 equal across each mirror set · `git diff main -- add-method/tooling/add.py add-method/tooling/add_engine/` empty.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/docs/18-personas.md` `add-method/../18-personas.md` `add-method/skill/add/` `.claude/skills/add/` `add-method/src/add_method/_bundled/skill/add/` `./`

Regression floor: `add-method/tooling/test_fold_persona_sections.py` (pins the hint vocabulary + the book's grown-section names), `add-method/tooling/test_tree_parity.py`, `add-method/tooling/test_ci_tooling_mirror_gap.py`, and `python3 .add/tooling/add.py check`.
Persona (optional): `.add/personas/book-technical-writer.md` — doc-truth across mirrored twins is exactly its seam (`use-when:` names doc-twin parity work).

Least-sure flag surfaced at freeze: [contract] the hint-vocabulary widening (M3). It is the only change here that alters a grammar other surfaces pin rather than just correcting prose, and `test_fold_persona_sections` carries a frozen-@-v1 contract docstring naming exactly four hints. My read is that the assertions are per-hint `assertIn` and therefore additive-safe, but that read is the thing most likely to be wrong in this bundle.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - check_no_dead_path: every backticked path cited in `18-personas.md` resolves on disk. RED now: `templates/personas/_template.md.tmpl` occurs 1x and exists only inside the stale `add-method/build/lib/` artifact. · covers: M1
  - check_overlay_matches_agent: the build-overlay load set in `18-personas.md` names `## Abilities`, matching `agents/add-worker.md` S2 ("read the body of the ONE you become" + "run the persona's lead commands"). RED now: the list is Identity + Critical Rules + Anti-patterns only. · covers: M2
  - check_hint_grammar_escalation: `escalation` appears in the persona-target hint vocabulary in `deltas.md`, in all 3 skill trees. RED now: `grep -ci escalation deltas.md` = 0. · covers: M3
  - check_book_names_escalation: "Escalation" appears in the book's growable-section list. RED now: 0 occurrences in `18-personas.md`. · covers: M4
  - check_contract_routability_accurate: the `## Escalation` entry in `persona-author/references/contract.md` cites the `deltas.md` hint vocabulary as the gate and no longer contains "free text". RED now: the shipped sentence says the hint is free text so nothing in the engine must change — true of the parse, wrong about the gate. · covers: M5
  - check_fold_test_green: `python3 -m unittest test_fold_persona_sections` OK. GREEN now and must STAY green — this is what pins the hint vocabulary and the book's grown-section names; it is the direct test of the M3 assumption. · covers: M3, M4
  - check_mirror_parity: md5 equal across each mirror set — `18-personas.md` x2 (canonical `add-method/docs/` + repo root), `deltas.md` and `contract.md` x3 skill trees. GREEN now and must STAY green. · covers: M6, R:mirror_gap
  - check_engine_untouched: `git diff --stat main -- add-method/tooling/add.py add-method/tooling/add_engine/` empty and both pin literals unchanged. GREEN now and must STAY green. · covers: R:engine_scope_violation
  - check_claims_are_citable: each load/route claim added or edited in this task points to a line in `add-worker.md` or `deltas.md` that says it. Judged by re-reading both files at verify, not by grep. · covers: R:unverified_claim
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: evidence · MUST run red before Build.

Non-coding task (`kind: docs`): §4 is a failing-first ACCEPTANCE CHECK set. Five checks are RED now, each probe-verified (counts recorded in the check bodies above); four are standing GREEN regression checks the build must not break. `check_claims_are_citable` is deliberately a judgement check, not a grep: it is the direct guard against the failure this task exists to fix — a plausible claim about what a surface reads, asserted from the wrong layer.

Build-guidance (prose, not gated): the book is the READER-facing chapter; keep the corrections short and declarative rather than narrating the drift. Edit the canonical tree (`add-method/docs/`, `add-method/skill/add/`) first, then propagate.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus TWO self-caught defects. (1) The §5 scope declaration named the repo-root book mirror with a BARE `18-personas.md` token, which `_declared_scope` resolves as a sibling of the previous token's dir — silently collapsing onto the canonical `add-method/docs/` copy and leaving the mirror uncovered. Caught by reading the freeze echo (5 paths, mirror absent), fixed with a "/"-bearing token and a `re-cross --by`. (2) `check_no_dead_path` — the check written to catch M1 — caught a dead path this task INTRODUCED: `agents/add-worker.md` does not exist at repo root (it is `.claude/agents/` and `add-method/agents/`). Retargeted to `.claude/agents/add-worker.md` in both the book and contract.md. A third, smaller catch: the parenthetical persona-template-legs added to contract.md ("18-personas.md still enumerates a shorter overlay set") went stale the moment this task fixed the chapter, and was removed.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all §4 acceptance checks pass — 9/9. The 5 red-first checks flipped (dead-path 1→0, add-worker citation 0→1, `escalation` 0→1 in all 3 trees, "Escalation" 0→2 in the book, "free text" 1→0). The 4 standing checks held.
- [x] coverage did not decrease — n/a for `kind: docs`.
- [x] no test or contract was altered during build — the §4 check set and frozen §3 are unchanged since the re-cross; scope re-snapshotted at that point and no tripwire finding at the gate.
- [x] the green was EARNED — the bundle's least-sure flag was RESOLVED empirically, not argued: `test_fold_persona_sections` (which pins the hint vocabulary with a "frozen @ v1" contract naming four hints) runs OK with the fifth hint present, confirming the assertions are per-hint `assertIn` and the widening is additive-safe.
- [x] concurrency / timing — n/a; markdown only.
- [x] no exposed secrets, injection openings, or unexpected dependencies — 8 markdown files, no code, no CI surface.
- [x] layering & dependencies — mirror discipline held across BOTH sets: book ×2 identical, `deltas.md` ×3 identical, `contract.md` ×3 identical (md5 sort -u = 1 per set). Engine untouched: `git diff main` on `add.py` + `add_engine/` empty, pins unchanged.
- [x] a person reviewed and approved the change — Tin Dang, at the verify gate, after the three self-caught defects were disclosed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: this task exists because two prior claims were asserted from the wrong layer, so the refute-read targeted exactly that failure mode.
  (1) The M3 assumption (a fifth hint is additive-safe) was NOT reasoned about a second time — it was run. `test_fold_persona_sections` green with `escalation` present.
  (2) `check_claims_are_citable` re-read both source files rather than grepping: `.claude/agents/add-worker.md` §2 does say "read the body of the ONE you become" and "run the persona's lead commands"; `deltas.md` line 21 does carry the closed hint vocabulary. Both new claims point at text that exists.
  (3) The dead-path check was pointed at THIS task's own output, not only at the pre-existing defect it was written for — which is what caught the `agents/add-worker.md` path this task introduced. A check that only validates the old state would have passed a new dead link.
  Residue: none. The `contract.md` parenthetical that deferred to this task was removed as part of it, so no forward-pointing claim is left dangling.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose reconcile-docs-to-behavior; rejected change-the-behavior-to-match-the-docs (rejected — would mean narrowing what `add-worker` reads or adding an engine fold writer, both larger and both contradicting "the engine never edits a persona").
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus TWO self-caught defects. (1) The §5 scope declaration named the repo-root book mirror with a BARE `18-personas.md` token, which `_declared_scope` resolves as a sibling of the previous token's dir — silently collapsing onto the canonical `add-method/docs/` copy and leaving the mirror uncovered. Caught by reading the freeze echo (5 paths, mirror absent), fixed with a "/"-bearing token and a `re-cross --by`. (2) `check_no_dead_path` — the check written to catch M1 — caught a dead path this task INTRODUCED: `agents/add-worker.md` does not exist at repo root (it is `.claude/agents/` and `add-method/agents/`). Retargeted to `.claude/agents/add-worker.md` in both the book and contract.md. A third, smaller catch: the parenthetical persona-template-legs added to contract.md ("18-personas.md still enumerates a shorter overlay set") went stale the moment this task fixed the chapter, and was removed.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
