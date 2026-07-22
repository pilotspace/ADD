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
- [open · 2026-07-22] rolling a ship bullet that carries an explicitly-OPEN tail needs a supersession note on its ledger line (settled-since | superseded-by | carried-unverified) — else open work hides behind the see-git pointer (evidence: foundation-split F3, ledger #26/#30/#32/#34 annotated post-refute) (task:foundation-split)
- [open · 2026-07-22] a two-clause Must needs one acceptance check per clause — foundation-split A5 proved M5's ceremony-collapse half but never its ship-rows-stay clause; only the cross-agent refute-read's fresh ledger sampling caught the silent deviation (evidence: F1, 15 ship rows restored byte-identical from git) (task:foundation-split)
- [open · 2026-07-17] lessons now land in-flight via delta-append; the milestone-close fold consumes .add/specs/, not a batch recall
<!-- prepended by `add.py delta-append add "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
