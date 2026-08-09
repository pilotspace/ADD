# MILESTONE: Foundation compaction — every survivor spec shrinks too

goal: A maintainer can keep every foundation spec relevant-first and one-screen as the project grows past v50 — append-only records read NEWEST-FIRST (recent decisions on top), and at milestone close shipped-and-stable entries collapse upward into a per-spec rolled-up settled tail while every OPEN residue and the audit trail stay live.
rationale: new-major — survivor-layer compaction across all foundation specs is a new method theme no prior milestone's goal covers; it extends v18's archive lifecycle (light-archive → compact) inward from finished-milestone files to the living foundation, broadened from the stashed-and-abandoned v24's PROJECT-only scope to all four specs with per-spec shapes. Confirmed via /add intake 2026-06-15.
stage: mvp · status: active · created: 2026-06-15
autonomy: conservative (amends a FROZEN invariant — high-risk; human stays at the gate)

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  One guarded, recorded compaction for ALL FOUR foundation specs — sharing ONE
     eligibility rule (shipped + zero OPEN residues), each spec its OWN tailored
     rolled-line shape:
       · PROJECT.md     §Spec version bullets + matching §Key-Decisions rows → settled vN–vM line
       · CONVENTIONS.md runs of stable §Method-learnings (folded deltas)     → settled-conventions pointer
       · GLOSSARY.md    a verbose, stable definition → terse canonical + git pointer (small today)
       · MODEL_REGISTRY superseded model rows → one "prior models (see git)" line (forward-looking)
     PLUS a newest-first re-ordering of ALL append-only sequences (§Key-Decisions rows ·
     §Spec version bullets · CONVENTIONS method-learnings) — fold.md prepends new records at
     the TOP; the rolled-up settled line anchors at the BOTTOM (oldest), so compaction collapses
     upward from the tail.
     Plus preservation guarantees (OPEN residues stay live · trail summarized-not-deleted ·
     git/archive pointer survives), the append-only invariant re-frozen (newest-first + the door), a
     `compact-foundation.md` guide + SKILL cue at milestone close, a dogfood on the live files,
     and book + GLOSSARY alignment.
Out: No change to FOLD (deltas still append; compaction is a SEPARATE retrospective step) ·
     no auto-compaction (human-confirmed, like fold) · no deletion of history (collapse =
     summarize + point) · `dependencies.allowlist` is OUT (data file, not a prose spec) ·
     no graduation/stage change · GLOSSARY & MODEL_REGISTRY shapes stay MINIMAL/forward-looking,
     not built past the smallest collapse rule (they are 25 & 6 lines today — anti-over-engineering).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Compaction NEVER deletes — it summarizes and points to git/archive; a rolled-up settled line
  is lossy on prose, LOSSLESS on traceability.
- OPEN residues are sacred — any spec entry with an open delta/residue is NOT eligible to collapse.
- Append-only is NEWEST-FIRST — every append-only foundation sequence (§Key-Decisions · §Spec
  bullets · CONVENTIONS learnings) PREPENDS the newest record at the TOP; fold.md prepends, not
  appends. The rolled-up settled line sits at the BOTTOM (oldest) — compaction collapses upward.
- Compaction is SEPARATE from fold — fold prepends new learnings (newest-first); compaction later
  collapses the stable tail.
- Human-confirmed, never auto — mirrors fold's "AI proposes, human confirms".
- ONE eligibility test, FOUR tailored rolled-line shapes — shared guarantee, per-spec collapse format.
- Disambiguate from the existing `compact` (archive recovery-bundle move): this is **foundation
  compaction**, a distinct operation on LIVING survivor docs — the contract MUST name the seam.
- New glossary terms: **foundation compaction** · **rolled-up settled line** · **per-spec shape** ·
  **newest-first append-only** (prepend at top, settled tail at bottom).

## Shared / risky contracts (freeze these first)
- the compaction contract — shared eligibility (shipped + zero OPEN residues) + the FOUR per-spec
  rolled-line shapes + the newest-first ordering rule (prepend top · settled tail bottom) +
  preservation guarantees + the convention-guided (judgment, like fold) vs engine-checked
  (reject codes, like compact) decision   -> owning task `compact-contract`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] compact-contract    depends-on: none                          — shared eligibility + the 4 per-spec rolled-line shapes + the newest-first ordering rule + preservation guarantees + the convention-vs-engine seam (freeze-first)
- [x] invariant-amend     depends-on: compact-contract              — re-freeze append-only as NEWEST-FIRST PREPEND (was bottom-append) + "EXCEPT via the recorded compaction door" in fold.md + PROJECT.md §Key-Decisions + §Spec + CONVENTIONS header; reject codes (open-residue-version · trail-loss · wrong-order)
- [x] compact-guide       depends-on: compact-contract              — write `compact-foundation.md` (one section per spec, newest-first + collapse-from-tail) + cue it from SKILL.md at milestone close; mirror to the dogfood tree
- [x] apply-compaction    depends-on: invariant-amend,compact-guide — dogfood the LIVE specs: RE-ORDER §Key-Decisions + §Spec bullets + CONVENTIONS learnings newest-first, then roll the stable tail into settled lines; GLOSSARY/MODEL_REGISTRY only where eligible; tests guard no-residue-lost + order
- [x] compact-book-align  depends-on: compact-contract              — book (loop / file-hygiene chapter) + GLOSSARY describe foundation compaction + the 4 shapes + newest-first ordering; book mirror parity

## Exit criteria (observable; map each to the task that delivers it)
- [x] A documented rule defines shared eligibility + the 4 per-spec rolled-line shapes + the newest-first ordering rule (← compact-contract) (verify: compact-foundation.md names all 4 shapes + the ordering rule; add.py check green)
- [x] append-only reads "newest-first prepend … EXCEPT via the recorded compaction door" in fold.md + PROJECT.md + CONVENTIONS.md, with open-residue/trail-loss/wrong-order reject codes (← invariant-amend) (verify: grep the clause in 3 files; reject-code tests pass)
- [x] All append-only sequences read NEWEST-FIRST — the most-recent §Key-Decisions row, §Spec bullet, and CONVENTIONS learning sit on top; fold.md prepends; the settled tail sits at the bottom (← invariant-amend + apply-compaction) (verify: head of each sequence is the most-recent date/version; order test green)
- [x] compact-foundation.md exists with a section per spec and SKILL.md cues it at milestone close (← compact-guide) (verify: file exists + SKILL.md references it)
- [x] PROJECT.md §Spec and CONVENTIONS.md §Method-learnings are re-ordered newest-first AND visibly shorter — the stable tail rolled into settled lines, every OPEN residue still live, audit trail summarized-not-deleted (← apply-compaction) (verify: wc -l before/after + test_no_residue_lost green)
- [x] book + GLOSSARY describe foundation compaction + the 4 shapes + newest-first ordering consistent with the ritual (← compact-book-align) (verify: book-mirror parity check + GLOSSARY has the 4 terms)
