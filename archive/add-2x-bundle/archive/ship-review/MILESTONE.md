# MILESTONE: ship-review

goal: at milestone close the AI fills a whole-milestone cross-task ship review (ship-by-domain manifest, per-task evidence, goal-met mapping) that the existing engine gate reads, and defines the milestone's release steps (merge is one small step) as hints in MILESTONE.md feeding release.md — no new gate, no new engine command, no new dependency
rationale: sub-milestone — a slice of the live ADD-method theme, multi-domain (template + guide +
  book), convention-guided (precedent: decision-suggestions, compact-foundation). Confirmed intake.
stage: mvp · status: active · created: 2026-06-17

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  ① MILESTONE.md.tmpl gains `## Close — ship review` (3 domains · cross-task evidence · goal-met map)
       + `## Release steps` (AI-defined hints; merge = one step).
     ② a close guide the close flow CUEs (from loop.md / release.md / SKILL.md).
     ③ book + GLOSSARY describe it, pointing at the guide.
Out: NO new engine command · NO bundled docx writer / no python-docx dep (pandoc one-liner is a HINT)
     · NO new human gate (rides the existing exit-criteria affirmation) · NO `gh pr` shell-out (PR is an
     AI-suggested step the human runs) · does NOT replace release.md — it FEEDS it.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Ship review** — the AI-filled cross-task close evidence; read at the existing engine gate, never a new approval.
- **Release steps** — AI-defined per-milestone hints (merge · PR · export · publish); feed the release scope.
- Tool-agnostic invariant holds: the engine never renders binary assets and never performs the outward git act.

## Shared / risky contracts (freeze these first)
- the Close-section + Release-steps SCHEMA in MILESTONE.md.tmpl (section headers · the 3 domains · the
  evidence-row shape · the goal-met map) -> owning task `close-section-template` (the seam tasks 2–3 build on).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] close-section-template  depends-on: none                   — add `## Close — ship review` + `## Release steps` hints to MILESTONE.md.tmpl.
- [x] close-guide             depends-on: close-section-template — close guide the close flow CUEs: AI fills evidence → engine gate reads it → AI defines release steps feeding release.md.
- [x] close-book-accord       depends-on: close-section-template — book + GLOSSARY describe ship-review + release-steps, pointing at the guide.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `new-milestone` renders a MILESTONE.md with `## Close — ship review` (3 domains + cross-task evidence + goal-met map) and `## Release steps`   (verify: test_milestone_template_close_section)  (← close-section-template)
- [x] the close flow CUEs the guide from loop.md and FEEDS release.md, not a competing flow   (verify: test_close_guide_cued_and_feeds_release — cross-tree reference)  (← close-guide)
- [x] the book + GLOSSARY name the ship review pointing at the guide, not re-specifying   (verify: test_book_points_at_close_guide — points-at-source)  (← close-book-accord)
- [x] the ship review proves goal-met: each Exit criterion maps to evidence before the gate closes, dogfooded on THIS milestone's own close   (verify: close-guide goal-met mapping + this milestone's filled Close section)  (← close-guide)

## Close — ship review   (AI-filled — the whole-milestone cross-task evidence the engine gate reads)

### Ship by domain
- tooling : `MILESTONE.md.tmpl` gained `## Close — ship review` + `## Release steps` (placed after `## Exit criteria`); NO `add.py` logic change; the goal-tally regex is untouched. [close-section-template]
- skill   : `loop.md` step 6 "Close" gained the ship-review ritual (fill evidence → check boxes → define release steps that feed `release.md`); no new file, no router entry. [close-guide]
- book    : `09-the-loop.md` gained "The ship review." passage; the GLOSSARY gained **Ship review** + **Release steps** in all 3 types — all pointing at `loop.md`. [close-book-accord]

### Cross-task evidence
- close-section-template : gate=PASS · tests=5/5 (S1–S5) + engine 1189 OK · residue=method-edit (escalated, confirmed)
- close-guide            : gate=PASS · tests=4/4 (L1–L4) + engine 1189 OK · residue=method-edit; wording-lint caught a bare "fold" (fixed to a code-span)
- close-book-accord      : gate=PASS · tests=4/4 (B1–B4) + engine 1189 OK · residue=method-edit; scope-gate caught a repo-root decl gap (fixed via `add-method/..` climb + a tests→build re-anchor)

### Goal met?   (each Exit criterion ↔ the evidence)
- [x] criterion 1 — live `new-milestone` render shows `## Close — ship review` + `## Release steps` after `## Exit criteria`; goal tally stayed `0/1` (S1–S5 green)
- [x] criterion 2 — `loop.md` step 6 ritual references `release.md` and copies none of its reject codes (L1–L4 green)
- [x] criterion 3 — ch09 passage + 3-type glossary point at `loop.md`, no fork (B1–B4 green)
- [x] criterion 4 — THIS section: filled on the milestone's own close, mapping all 4 criteria to evidence before the gate (the honest first-lived dogfood)
- goal: a cross-task ship review + AI-defined release steps as MILESTONE.md hints feeding release.md, with no new gate / command / dependency — PROVEN: 3/3 PASS · engine 1189 green · zero new `add.py` command (grep) · zero new dependency · the only human touchpoint is the existing exit-criteria affirmation (+ the disclosed method-edit residue).

## Release steps   (AI-defined — the engine records, the human runs them)
- [ ] open a PR for the ship-review work; the human reviews the cross-task evidence above and merges
- [ ] (optional) export this Close — ship review to a hand-off doc — e.g. `pandoc` the section to `.docx`
- [ ] this milestone joins the next release cut (1.7.0, currently held) per `release.md` — the human runs the tag / publish
