# Method — the ADD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — how we work: the loop, autonomy, ceremony budget (ADD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append add "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<!-- migrated from PROJECT.md §Domain/§Spec loop-rules @ fv66 (foundation-split) -->
- The loop: INTAKE sizes a request into a milestone; each task runs the specification
  bundle (Spec+Scenarios+Contract+Tests) to ONE human approval at the frozen contract,
  then a self-driving build→verify run. Lifecycle above the task:
  `milestone-done → fold → compact → archive → (repeat ≥1×) → release → watch` —
  the engine RECORDS, the human SHIPS (never tags/publishes/deploys). [fv34]

## Decisions that bind
- Verify re-checks the milestone's frozen exit criteria after a task changes shape — a shared-contract drift turns a gate red, never slips silently to milestone close. [v9 · SDD]
- Residue an evidence auto-gate must escalate is not limited to security·concurrency·architecture — method/trust-layer edits are a residue category. [v6]
- Additive content folds into a frozen contract with NO re-freeze: removes no frozen §3 section, changes no reject → it is INSIDE the frozen shape; likewise a presentation/layout layer iterates freely without a re-freeze — the freeze binds the data/interface seam. [fv33 · udd-design-loop]
- A frozen descriptive annotation can be wrong while the binding seam holds: honor the seam, disclose at verify, never silently retrofit the frozen text. [fv33]
- A defect found while working task N in an already-done task M is fixed by the recorded `reopen M` (gate reset), never a silent out-of-scope edit. [fv21 · foundations-chapter]
- Foundation specs are append-only NEWEST-FIRST and compact by the per-spec rolled settled line (summarize + `see git`, NEVER delete; open residue stays live) — the ritual is convention-guided (`compact-foundation.md`), deliberately no engine verb. [fv31 · foundation-compaction]
- The skill lean fence is a hard floor: genuinely-new doc-truth on a guide is reclaimed from the same guide's prose, not a budget rebaseline, absent an explicit human bump. [fv58 · component-worked-example]

## Deltas (newest first)
- [open · 2026-07-23] a global str.replace fill script rewrote the frozen §3 (its target string appeared INSIDE the contract block) and tripped contract_tampered — anchor §5/§6 fills to their section or use line-scoped edits; repair = revert + re-cross --by <human> (evidence: scope-first-freeze return_to_build attempt 1) (task:scope-first-freeze)
- [open · 2026-07-23] A milestone-level ## Strategy slot mirrors a task's Build-strategy: SOFT/advisory, drafted-blank valid, placed AFTER ## Exit criteria so it stays OUT of the ## Tasks DAG-parse span (_compile_task_graph bounds ## Tasks at the next ## heading). Renders verbatim via new-milestone — zero engine parse, zero ENGINE_MD5 churn (evidence: strategy-section PASS, live confirm/check clean). (task:strategy-section)
- [open · 2026-07-23] _FALLBACK_TASK + skill guides needed NO change — they never carried the SOFT-mislabel or a required-Persona (the terse _FALLBACK has no qualifier + no Persona line; build.md already frames the Persona overlay as optional). Verifying 'already consistent' is an honest close, not a skipped scope (evidence: grep of guides + _FALLBACK for SOFT/required = clean). (task:trim-build-strategy-labels)
- [open · 2026-07-23] A 'trim' milestone can be a pure RELABEL — the enforced Scope (may touch) line stays HARD scope-lock; only the human-facing framing + Persona/Regression optionality changed. No engine kernel removed, no gate weakened (evidence: trim-build-strategy-labels PASS, full suite 2253/0). (task:trim-build-strategy-labels)
- [open · 2026-07-23] a milestone task's premise can go OBSOLETE under sibling work finishing first — grounding engine-kernel-trim proved its 'usage-mined strike-list' was EMPTY (all 34 verbs load-bearing: 6-57 test invokes each; 'guide-unreferenced' is a false dead-code signal) and its dedup was already delivered (14 add_engine modules + engine-hygiene). The honest close is retire-as-superseded (no freeze on empty scope; signal-graph precedent), and produce a dependent task's evidence artifact DIRECTLY (CENSUS.md) rather than run the redundant standalone task. Also: an exit criterion can be MIS-TOOLED — call-census's _engine_call_census counts ALL add.py calls (median 9.3/task incl. orientation) while the criterion means the ≤3 CROSSING calls (median 3.5, within the milestone's own 'happy path not a cap' clause). evidence: thin-engine-loop closed 6/6, 105 archived (task:gate-experience-udd)
- [open · 2026-07-23] a long-stale frozen contract (frozen 2026-07-16, tree moved for months) carries literal anchors that later unrelated work supersedes — test names removed by corpus-slim, byte ceilings grown by other tasks, ENGINE_MD5 rotated. The honest close is NOT to edit the frozen §3 but to (a) pin DRIFT-STABLE invariants in the acceptance test, (b) re-resolve every stale anchor in §6 Live-verify rather than silently, (c) fix the build_tampered + missing scope-snapshot via signed re-cross --by <human> (the sanctioned post-freeze-test-addition path), then gate. evidence: gate-experience-udd PASS after re-cross; suite 2247/0 (task:gate-experience-udd)
- [open · 2026-07-23] Repo-root book-mirror files can't be named by the bare scope grammar — use the add-method/../<name> climb (slash-bearing → resolves at project root) on ONE physical Scope line; a mkdocs config change required by a docs Must (M6 mermaid-enable) is IN-scope and belongs on that same line (evidence: 17-token re-cross resolved clean, gate PASS no scope_violation) (task:book-de-scenarios)
- [open · 2026-07-23] Book de-scenarios fold: retire-in-place mirrors the engine's non-contiguous §1·3·4·5·6·7 in prose too — the frozen §1 Boundary (structural = numbered 'Step 2'/'§2'/file-link; bare 'Scenarios' = activity, may stay) is what let a mechanical grep-check cleanly separate must-change from may-keep (evidence: 12-roles RACI merged Scenarios→Tests&Scenarios column, but skip-cost/profile-rigor 'Scenarios' rows kept) (task:book-de-scenarios)
- [open · 2026-07-22] prefer minimal inline distillation over a parallel reference doc: a separate reasoning.md + pointer + test was apparatus the human vetoed — the umbrella principle belongs INLINE where its checks already live (direction.md), guarded by extending the existing test, not a new file (evidence: task fable-thinking-reference redirected from doc to one Fluent≠true clause) (task:fable-thinking-reference)
- [open · 2026-07-22] fable Floor pass: the fable-thinking protocol's front-half (claim grammar OBSERVED/DERIVED/PRIOR/ASSUMED · Goal+Leftovers Floor · GROUND observation-over-memory · output-shape constraint-loop) fills ADD's empirically-thinnest reasoning spots — measured 9/27/32 hits per 3021 fable thinking blocks vs 334 for mechanism; landed in add-advisor.md + direction.md, zero SKILL.md growth (evidence: task fable-floor-reasoning, test_fable_floor 4/4) (task:fable-floor-reasoning)
- [open · 2026-07-22] rolling a ship bullet that carries an explicitly-OPEN tail needs a supersession note on its ledger line (settled-since | superseded-by | carried-unverified) — else open work hides behind the see-git pointer (evidence: foundation-split F3, ledger #26/#30/#32/#34 annotated post-refute) (task:foundation-split)
- [open · 2026-07-22] a two-clause Must needs one acceptance check per clause — foundation-split A5 proved M5's ceremony-collapse half but never its ship-rows-stay clause; only the cross-agent refute-read's fresh ledger sampling caught the silent deviation (evidence: F1, 15 ship rows restored byte-identical from git) (task:foundation-split)
- [open · 2026-07-17] lessons now land in-flight via delta-append; the milestone-close fold consumes .add/specs/, not a batch recall
<!-- prepended by `add.py delta-append add "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
