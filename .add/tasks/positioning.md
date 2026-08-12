---
type: Task
title: The front door names an audience wider than code
status: done
depth: standard
milestone: adoption-beyond-code
scope:
  - README.md
  - add-method/README.md
  - add-method/tests/skill/
gives:
  - S1 the root README's onboarding surface — where a reader is offered a way in
  - S2 the package README's onboarding surface — the same offer, as npm and PyPI render it
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:8460a9ed6a3d5935" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:fb8bfb1b172880e7" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/positioning.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/positioning.d/runs/1.md, brief: "sha256:fb8bfb1b172880e7" }
advised_by: method-steward
---
## CARD
goal: a non-code reader is offered the non-code way in at the same place, and with the same prominence, as the code one
why: `BEYOND-CODE.md` is reachable from neither README — zero references from either file. A walkthrough nobody links is exactly the defect `test_no_orphan_refs` was written for one milestone ago, reproduced for a shipped doc instead of a skill ref: it can be correct, executed and complete, and still do nothing, because the reader who needed it never learns it exists. Both READMEs list "Full hands-on walkthrough" today and mean the code one; a finance lead reading that list is told, by omission, that the code walkthrough is the only walkthrough.
beat: done · next: add status

## RULES
<must>
- M1 every reader-facing walkthrough the package ships is linked from at least one README — no orphan doc
- M2 wherever a README offers the code walkthrough, it offers the non-code one alongside it, in the same list and at the same level
- M3 every document a README links by relative path actually exists at that path
- M4 the guard derives the walkthrough set from what the package ships, so the next walkthrough added is checked without editing the check
</must>
<reject>
- R:IDENTITYCREEP this task must not change the project's name, tagline, package names, or book title — that decision is the human's and is unanswered -> "identity_creep"
- R:DEADLINK a link added here must never point at a path that does not exist -> "dead_link"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whether "non-code audience" means naming specific domains (finance, research, ops) or simply not presupposing code; taking the weaker reading — offer the path, let the walkthrough name its own domain — because listing domains is a claim about who ADD serves, which is the same human-owned decision as the name -> if wrong, the front door is neutral where the user wanted it explicit, and the stronger version is a one-line edit once they answer
- A2 [which] covers: S1, S2 · it does not say which files count as "reader-facing walkthroughs"; taking it as the top-level `*.md` under `add-method/` that address a reader directly (`GETTING-STARTED`, `BEYOND-CODE`), excluding `README`, `CHANGELOG` and machine-facing files, because those are indexes and records rather than paths in -> if wrong, the guard either nags about a changelog or misses a real walkthrough
- A3 [when] covers: S1, S2 · it does not say whether the link must exist at commit time or only at release; taking it as every test run, matching the rule `front-door-truth` already set for the same two files -> if wrong, main ships an orphan between milestones
- A4 [absent] covers: S1, S2 · it does not say what a README with no walkthrough list at all should do; taking silence as non-compliant for M1, because the two files are the ONLY front door and a walkthrough linked from nowhere else is unreachable -> if wrong, the guard forces a list into a README that deliberately has none
- A5 [order] covers: S1, S2 · it does not say whether the code walkthrough must come first; taking the order as unconstrained but the LEVEL as constrained — same list, same nesting — because prominence is what M2 is about and a fixed order would be a preference this task has no basis to impose -> if wrong, the non-code path is present but visually subordinate, which is the omission M2 exists to prevent

## PLAN
contract: both READMEs list `BEYOND-CODE.md` beside `GETTING-STARTED.md` as a peer entry, and the surrounding sentence stops presupposing that the reader is building software. The name, tagline, package identity and book title are untouched. A guard derives the shipped walkthrough set from the package tree and fails on any that no README reaches, on any relative link that resolves to nothing, and on any change to the identity strings.
scope: README.md, add-method/README.md, add-method/tests/skill/

## EDGES
- E1 the root README and the package README resolve relative links from DIFFERENT directories — `./GETTING-STARTED.md` means `add-method/GETTING-STARTED.md` from the root file and `add-method/GETTING-STARTED.md` from the package file. A link that is correct in one is broken in the other, so the guard must resolve each link against its own file's directory rather than against the repo root.

## CHECKS
- test_every_shipped_walkthrough_is_reachable · covers: M1, M4 · derives the walkthrough set from the package tree and fails on any that neither README links
- test_walkthroughs_are_offered_as_peers · covers: M2 · in any README list that names the code walkthrough, the non-code one appears as a sibling entry at the same nesting level
- test_readme_relative_links_resolve · covers: M3, R:DEADLINK, E1 · every relative link in each README is resolved against THAT file's own directory and must exist
- test_identity_is_unchanged · covers: R:IDENTITYCREEP · the project name, tagline, package names and book title are byte-identical to what this task inherited
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
