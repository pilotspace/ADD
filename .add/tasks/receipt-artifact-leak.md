---
type: Task
title: the receipt artifact leaks into the repo root
status: done
depth: standard
milestone: all-domain-evidence
scope:
  - add-method/skill/add
  - add-method/docs
  - add-method/GETTING-STARTED.md
  - add-method/tests/skill
gives:
  - S1 the documented receipt-scratch path — the `--junitxml` argument every doc tells an agent to copy
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:6315bbf4e4bba2b3" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:78ed308eec8f0618" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:6315bbf4e4bba2b3" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:d6503b0ed8f9ce7f" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/receipt-artifact-leak.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:6315bbf4e4bba2b3" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:f6b1d2d471b69e92" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/receipt-artifact-leak.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/receipt-artifact-leak.d/runs/2.md, brief: "sha256:f6b1d2d471b69e92" }
  - { by: loop, at: 2026-08-12, act: reopen, to: direction, reason: "gate passed on a three-way quoting inconsistency the check was built to tolerate; add a canonical-form Must and pin it" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:2a3fe8040eddd341" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:0f510588949c1335" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/receipt-artifact-leak.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/receipt-artifact-leak.d/runs/3.md, brief: "sha256:0f510588949c1335" }
---
## CARD
goal: following the documented receipt command must leave nothing behind in the working tree
why: `r.xml` is gitignored nowhere, and the cookbook every agent copies writes it to CWD — so the next `git add -A` commits a JUnit report. Hit live during domain-evidence-recipe; the artifact reached the index and had to be force-removed.
ground: the leak is 9 source files, not one line — SKILL.md (2 lines), phases/verify.md, domains.md across THREE skill trees, plus GETTING-STARTED.md and docs/{05-verify,13-command-reference,17-components,appendix-d-worked-example}.md. domains.md propagated it: the ref shipped one task ago already tells readers to write r.xml.
revised at draft: the first draft chose `.add/run.xml` + ignore entries. A probe showed the engine parses ANY path, so the scratch leaves the tree entirely and the gitignore/template-twin half of the contract was cut before freeze, not after.
widened at 2nd freeze: `add-method/tests/skill` was missing, so a defective CHECK was unrepairable during build and the only in-scope 'fix' would have been to reshape the docs around the broken regex. A task's scope MUST reach the directory its own checks live in.
order: MUST settle before or with `skill-pointer-truth` — both edit SKILL.md, and the milestone's tasks are otherwise scope-disjoint.
beat: done · next: add status

## RULES
<must>
- M1 every documented `--junitxml` path in the shipped skill and the book docs must resolve OUTSIDE the working tree
- M2 the change must land byte-identical across all three skill trees
- M3 every documented `--junitxml` argument must use ONE canonical, shell-quoted form. Added at reopen: the first gate passed on three variants (8 bare, 1 quoted, 1 with a stray backtick) because the check tolerated any out-of-tree path — honest about what it claimed, blind to what nobody claimed
</must>
<reject>
- R:TREELEAK a shipped doc instructing a receipt artifact be written anywhere inside the working tree -> "TREELEAK"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · no actor distinction — every agent copies the identical cookbook line
- A2 [which] covers: S1 · the request does not say which docs count; taking "every SHIPPED surface that instructs the command — the three skill trees and the book docs/ chapters" -> if wrong, a missed doc keeps teaching the leak and the fix reads complete
- A3 [when] covers: S1 · n/a · the path is an argument, not a step; it carries no timing
- A4 [absent] covers: S1 · the request does not say what happens when TMPDIR is unset; taking "`${TMPDIR:-/tmp}` falls back, and the POSIX assumption is pre-existing — the cookbook is already ```bash" -> if wrong, the documented line fails on a shell with neither TMPDIR nor /tmp
- A5 [order] covers: S1 · n/a · one argument, nothing to sequence

## PLAN
contract: one scratch path, outside the working tree, documented everywhere the command is instructed
strategy: the JUnit XML is REQUIRED — it is what upgrades a receipt from `command-exit` (exit code only) to `test-ids` (named checks), and `covers:` binds against the IDs the runner reported, so without it the gate refuses every bound rule at any depth. The FILENAME is not required: the engine parses whatever path it is handed. Verified `--junitxml /tmp/add-run-probe.xml` → kind test-ids, 2/2 reported, gate PASS, zero repo footprint. So the fix is docs-only — no gitignore, no template twins, nothing to ignore because nothing lands.
scope: add-method/skill/add, add-method/docs, add-method/GETTING-STARTED.md, add-method/tests/skill

## EDGES
<!-- none. The first draft's edge (a project predating the fix has no `.add/.gitignore`)
     dissolved when the scratch left the tree. DELETED, not retired with `n/a`: an `E<n>`
     line is a gate referent whatever it says, so an `n/a` edge still holds the PASS. -->

## CHECKS
- test_documented_receipt_paths_are_outside_the_tree · covers: M1 · every `--junitxml` argument in the shipped skill and docs resolves outside the working tree
- test_no_shipped_doc_writes_into_the_tree · covers: R:TREELEAK · no shipped surface instructs an in-tree artifact
- test_receipt_path_has_one_canonical_form · covers: M3 · every documented argument is the identical quoted string
- test_skill_bundle_matches_canonical · covers: M2 · package payload skill tree matches canonical
- test_dogfood_skill_matches_canonical_when_present · covers: M2 · dogfood mirror matches canonical
red-first: TWO are driven red — M1 and R:TREELEAK both fail while the docs still say `r.xml`. TWO are the EXISTING parity guards reused for M2 (qualification gate), green at freeze and declared so; they go red the moment a tree is missed. The earlier draft's M2/M3-templates/E1/R:BUNDLEPOLLUTE were cut: they existed only to serve an in-tree scratch path, which the probe showed is unnecessary.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
