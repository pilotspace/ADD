---
type: Task
title: run reads the report path from the command it was handed
status: done
kind: feature
depth: standard
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 add.run() — the report path, sniffed from the command when not given
  - S2 BEAT_NEXT's build hint, which names the path once instead of twice
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:ddadec88bdd17392", binding: "sha256:901c5b554e941628" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:3834ef1864e76b85" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/run-reads-the-path-it-was-handed.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: plan, direction: "sha256:9cbe5b3ccbf8ecdc", binding: "sha256:901c5b554e941628" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:c2b2d3a59f46df30" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/run-reads-the-path-it-was-handed.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/run-reads-the-path-it-was-handed.d/runs/2.md, brief: "sha256:c2b2d3a59f46df30" }
---
## CARD
goal: `add run` finds the JUnit report the command it was given already names, so the path is written once.
why: `--junitxml` on `add run` only tells the ENGINE where to read; the command writes it. So the same path is typed twice — `add run x --junitxml "$X" -- pytest ... --junitxml="$X"` — and the engine already holds the command as a list. Getting it wrong costs a receipt with `ids: unknown`, which reads as every rule unbound.

## RULES
<must>
- M1 with no `--junitxml`, `run` reads the report path out of the command it was handed
- M2 an explicit `--junitxml` wins over anything sniffed — the flag stays an override, not a fallback
- M3 a command naming no report path leaves `ids: unknown`, exactly as today
- M4 the sniffed path is judged for staleness the same way an explicit one is
- M5 BEAT_NEXT's build hint names the path once
</must>
<reject>
- R:GUESSPATH `run` treats a token that is not a report path as one, and binds a receipt to a file the command never wrote -> "GUESSPATH"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · the path is read from the command the caller already supplied; no authority question is opened by reading an argument twice
- A2 [which] covers: S1, S2 · the request does not say which flag spellings to sniff; taking `--junitxml` and pytest's `--junit-xml` alias, in both `=path` and separate-token forms -> a broader guess would match a token that is not a report path, which is the Reject; a runner spelling it otherwise still has the explicit flag · probe: an unrecognised spelling leaves ids unknown rather than binding a wrong file
- A3 [when] covers: S1, S2 · the request does not say what happens when both are present, nor whether the hint should keep the engine-side flag for a transition; taking the explicit flag unconditionally, and dropping it from the hint immediately -> a sniffed value silently overriding a stated one would make the flag useless as an escape hatch, and a hint that keeps teaching the doubled form keeps producing the mistake it exists to prevent · probe: the explicit flag wins when the two disagree, and the hint carries the flag exactly once
- A4 [absent] covers: S1, S2 · the request does not say what an unsniffable command means; taking it as today's behaviour, `ids: unknown` -> inventing a default path would bind the receipt to a file the command never wrote · probe: no path is fabricated when none is named
- A5 [order] covers: S1, S2 · the request does not say which wins when the command names two report paths, nor where the path sits in the hint; taking the LAST occurrence because that is what the runner itself honours, and leaving the hint's path where the runner reads it -> taking the first would bind a report the command overwrote, and moving it in the hint would change what users paste for no gain · probe: the last occurrence is the one read
- A6 [experience] covers: S1, S2 · the request does not say who benefits; taking the author following the build hint -> the doubled path is the one line in the loop people paste wrong, and the punishment is a refusal about unbound rules that names nothing about the real cause · probe: the hint names the path once

## PLAN
contract: `run` gains `_sniff_report(command)`, used only when `junit` is None. It matches `--junitxml`/`--junit-xml` in `=path` and two-token form, takes the last, and returns None otherwise. Everything downstream — staleness, extraction, `ids` — is unchanged. `BEAT_NEXT`'s build hint drops the engine-side flag.
scope: add-method/tooling/add.py, add-method/tests/engine/test_run_reads_the_path_it_was_handed.py

## EDGES
- E1 the flag as the command's last token with no value after it
- E2 a command that mentions the flag inside a quoted argument to something else
- E3 two report paths in one command

## CHECKS
- test_run_sniffs_the_report_path_from_the_command · covers: M1, A2 · the doubled path, written once
- test_the_two_token_form_is_read_too · covers: M1, A2 · `--junitxml path`, not only `=path`
- test_an_explicit_flag_wins_over_a_sniffed_one · covers: M2, A3 · the override stays an override
- test_no_path_named_leaves_ids_unknown · covers: M3, A4, E1, E2, R:GUESSPATH · nothing is fabricated
- test_a_sniffed_path_is_judged_for_staleness · covers: M4 · sniffed and explicit are the same value
- test_the_last_report_path_wins · covers: A5, E3 · the runner honours the last, so must the reader
- test_the_build_hint_names_the_path_once · covers: M5, A6, S2 · the line people paste
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- when a flag restates something the engine was already handed, the flag is the bug -> add learn method
