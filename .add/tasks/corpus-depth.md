---
type: Task
title: finance/legal/academic persona depth + routing index
status: done
depth: quick
milestone: all-domain-evidence
scope:
  - add-method/personas-index
  - add-method/scripts
  - add-method/tests/skill
gives:
  - S1 the corpus routing coverage — which teacher files are reachable through the index, and which are knowingly not
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:bdc1c6dfb8fe6024" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:e4a8a84b2c65e9da" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/corpus-depth.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/corpus-depth.d/runs/1.md, brief: "sha256:e4a8a84b2c65e9da" }
---
## CARD
goal: every persona in the teacher corpus is reachable through the routing index, and every file that is not is accounted for out loud
why: THE ORIGINAL PREMISE IS VOID. This task was drafted to "thicken finance/legal/academic personas" on the belief the corpus was engineering-heavy. It is not — 256 personas across 18 divisions incl. finance, academic, marketing, gis. And it CANNOT be thickened here: `personas-teacher/` is a byte-verbatim vendored MIT snapshot that `update_teacher.py` replaces with `shutil.rmtree`, so anything added is erased on the next refresh and corrupts third-party attribution besides. The real gap is ours: 22 of 256 corpus files are unreachable through the index, the skip is silent, and NOTHING pins coverage — a refresh that drops or renames personas would shrink routing invisibly.
beat: done · next: add status

## RULES
<must>
- M1 every corpus `.md` must be either indexed or accounted for by a stated reason the check verifies
- M2 the index must reach every division that ships agent definitions — finance and academic included, the ones this milestone claimed were thin
- M4 the generator must REPORT what it skipped and why — the silence is the defect: it reports "232 personas" and says nothing about the 22 files it passed over, so a persona that lost its frontmatter in a refresh disappears from routing with no signal
- M3 the accounting must be DERIVED from the corpus, never a pinned file list — a pinned list rots on the very next vendor refresh, which is the failure this task exists to prevent
</must>
<reject>
- R:HANDEDIT hand-editing `personas-index/use-when.md` or anything under `personas-teacher/` — the first is generated and the second is vendored, so a hand edit is erased without warning -> "HANDEDIT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · the generator alone writes the index; no actor chooses coverage
- A2 [which] covers: S1 · the request does not say which non-persona files are legitimately skipped; taking "a corpus file with no `description:` frontmatter is not an agent definition — playbooks, runbooks, examples, LICENSE, VENDOR.md — which is the generator's OWN rule, just never stated at the size it actually operates" -> if wrong, a real persona that merely lost its frontmatter reads as a deliberate exclusion
- A3 [when] covers: S1 · the request does not say when coverage is checked; taking "on every suite run, not only at refresh time — a refresh PR is exactly when nobody re-reads the index" -> if wrong, drift is caught only by whoever happens to look
- A4 [absent] covers: S1 · the request does not say what happens when the corpus is absent entirely; taking "fail loud — an empty corpus must not pass as full coverage" -> if wrong, a broken checkout reads as a clean bill of health
- A5 [order] covers: S1 · n/a · coverage is a set property; nothing is ordered

## PLAN
contract: a derived coverage guard over the generated index, plus the generator saying out loud what it skipped
strategy: the strongest available check is REGENERATE-AND-COMPARE — run `build_persona_index.py` into a temp location and assert the committed index is byte-identical. That catches a hand-edit and a stale index in one assertion, and it is derived by construction. Coverage is then a set difference over the corpus, never a pinned list.
scope: add-method/personas-index, add-method/scripts, add-method/tests/skill

## EDGES
- E1 an absent or empty corpus must fail loud, never pass as complete coverage

## CHECKS
- test_every_corpus_file_is_indexed_or_accounted · covers: M1 · every corpus .md is indexed or has no description: frontmatter
- test_index_reaches_every_agent_division · covers: M2 · every division holding agent definitions is routable, finance and academic included
- test_index_is_regenerable · covers: M3, R:HANDEDIT · regenerating byte-identical proves both derivation and no hand-edit
- test_empty_corpus_fails_loud · covers: E1 · zero personas raises rather than reporting full coverage
- test_check_reports_what_it_skipped · covers: M4 · --check names the skipped count, not only the indexed count
red-first: ONE is driven red — M4, because `--check` today prints "232 personas" and reports nothing about the 22 files it silently passed over. The other FOUR are green at freeze and declared: they guard properties that already hold, which is the point of a coverage guard over a VENDORED tree — the risk is a future `update_teacher.py` refresh, not today's state. An earlier draft of the regenerate check invented a `--stdout` mode, did not find it, and pytest.skip'd; a skipped check binds NOTHING (the engine records `skip`, never `pass`), so it was rewritten onto the `--check` mode the generator already ships.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
