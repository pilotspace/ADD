# MILESTONE: Prompt structure & file hygiene

goal: ADD artifacts and guides are XML-structured for AI effectiveness, and done work compacts out of the active tree
stage: mvp · status: active · created: 2026-06-07

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a v18 FORM-TAG amendment to the frozen v16 XML convention (templates gain a
     closed fill-region tag class); internal lean restructure of the tooling
     templates; a parse-seam test suite proving the engine reads new scaffolds
     unchanged; a file-level "heavy archive" that compacts done milestone/task
     files out of the active tree.
Out: re-tagging the skill guides (done + frozen in v16); new add.py parsing of
     form-tag content (future milestone); changing the directory grammar
     (`.add/tasks/<slug>/TASK.md` stays); rewriting the book.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Intake rationale (2026-06-07): "XML-enhance templates + optimize file structure" —
  guides found already converted (v16); template tagging is a sanctioned AMENDMENT
  to the frozen closed vocabulary ("additions only by amending this frozen list"),
  reversing appendix-templates-xml's "nothing to tag" assessment by explicit approval.
- Parsed-seam invariant: every engine-parsed line/heading (`phase:`, `## N ·`,
  `Status:`, `Outcome:`, `Tests live in:`, the §6 checklist, `- [ ] <slug>` rows,
  `## Exit criteria`) stays byte-compatible; form tags are additive, paired,
  own-line, multi-line only (an inline one-line element reads as a placeholder —
  add.py `_clean_phase_body`).
- Form tags are a SEPARATE class from v16 instruction tags: instruction tags stay
  guides-only; form tags stay template/artifact-only. Neither side borrows.

## Shared / risky contracts (freeze these first)
- v18 form-tag amendment (closed set + boundary rules) -> owning task xml-prompt-structure

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] xml-prompt-structure   depends-on: none     — form-tag amendment + template lean pass + parse-seam suite
- [x] archive-compaction     depends-on: none     — heavy archive: compact done milestone/task files out of the active tree

## Exit criteria (observable; map each to the task that delivers it)
- [x] A task scaffolded from the new TASK.md.tmpl carries paired form tags, and the full engine suite (phase sync · §spans · freeze · gate audit · declared-tests · deltas lint) is green on it        (← xml-prompt-structure; archive-compaction was the first scaffold from the new template — full suite green on it)
- [x] User can run one command that moves an archived milestone's task+milestone files out of the active tree, recoverably, with deltas folded first        (← archive-compaction; `add.py compact <slug>` — proven by the 11-test harness incl. reverse-move restore; honest bound: recovery restores files, the `compacted:` stamp persists)
