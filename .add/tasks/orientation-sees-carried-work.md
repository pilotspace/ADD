---
type: Task
title: status and doctor see carried work; the root is authored
status: direction
depth: standard
sensitivity: architecture
milestone: loop-that-drains
scope:
  - add-method/tooling
  - add-method/tests
  - add-method/.add/tooling
  - add-method/src/add_method/_bundled/tooling
  - .add/tooling
  - .add/PROJECT.md
gives:
  - S1 an integer `open_deltas:` key on every Spec, written by `learn` and `fold`, read at T0
  - S2 the `status` header — a total-open-deltas clause and the project goal line
  - S3 two `doctor` findings — `unauthored_root` and `delta_count_drift`, the latter repaired by `--sync`
  - S4 the authored root — `init` writes an `invariants:` key, `upgrade` carries a 2.x goal forward
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:57650d4da95043ab", binding: "sha256:1273fce507ef8b6a" }
  - { by: "builder", at: 2026-09-08, act: replan, authority: process, note: "A13 put the delta clause on the hidden-nodes tally line; that line only exists when something is HIDDEN, so --all would have dropped the very count it most needs. Both the goal and the clause now ride the title line — A13's stated purpose (no new line in the 20-line budget) is held, its letter is not. Second turn: the counter is seeded open_deltas: 0 by init, not left for the first learn, because absence must mean exactly one thing (this bundle predates the key) or a fresh bundle and an unmigrated one report the same word. test_status_unknown_counter_is_not_zero's absence case now strips the seeded key rather than relying on a fresh bundle to lack it — same two assertions, a fixture that actually produces absence." }
---
## CARD
goal: no orientation surface reports zero carried work while lessons are open, and the bundle root stops standing in its own scaffold
why: 75 lessons are open in this bundle and `status`, `todo` and `doctor` between them report none of them; meanwhile `.add/PROJECT.md` has read `state: initialised` for a month because `upgrade` carried only `title:`, and the `invariants:` key that CLAUDE.md and nine skill lines bind every task to is written by nothing and read by nothing. This task is the instrument the rest of the milestone is measured by, so it ships first and adds no refusal.
beat: direction · next: add freeze orientation-sees-carried-work

## RULES
<must>
- M1 the `status` header names the total count of open deltas across every Spec, and names the project goal, reading frontmatter only
- M2 a Spec whose `open_deltas:` key is absent or unparsable contributes an UNKNOWN to that total, rendered as a question mark, never as zero
- M3 `doctor` files an `unauthored_root` warning against a Project or a Spec still standing in its creation scaffold
- M4 `doctor` files `delta_count_drift` when a Spec's `open_deltas:` disagrees with the open deltas in its body, and `doctor --sync` rewrites the key to the body count
- M5 `init` writes an `invariants:` key into PROJECT.md frontmatter, and `doctor` is its reader
- M6 `upgrade` carries a 2.x `goal:` forward into the fresh PROJECT.md alongside `title:`
- M7 both writers of a delta line maintain the counter: `learn` increments it, `fold` decrements it by the number of deltas it actually retagged
</must>
<reject>
- R:T2SCAN status must never read a node body to produce the count -> "T2SCAN"
- R:UNKNOWNCLEAN an absent or unreadable counter must never render as a clean zero -> "UNKNOWNCLEAN"
- R:GREENROOT a bundle whose PROJECT.md is pure scaffold must never yield a doctor report carrying no finding against it -> "GREENROOT"
- R:DEADKEY no frontmatter key is written that no engine path reads -> "DEADKEY"
- R:CLOBBERGOAL upgrade must never replace an authored goal with a placeholder -> "CLOBBERGOAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say who may write the counter; taking the reading that it is engine-maintained only, never a slot a human edits, so `--sync` is always free to overwrite it -> a human who hand-tunes the number has it silently reverted, which is correct but must be documented in the key's comment
- A2 [who] covers: S4 · the request does not say who authors `invariants:`; taking the reading that `init` seeds it EMPTY and the human fills it, because the engine has nothing true to put there -> if the engine seeded content, every bundle would ship invariants nobody chose
- A3 [which] covers: S1 · the request does not say which delta statuses count as open; taking the reading that only status `open` counts — `folded` and `rejected` are both resolved · probe: a spec holding one open, one folded and one rejected delta reports 1
- A4 [which] covers: S2 · the request does not say which nodes the goal line is read from; taking the reading that it is the Project node's frontmatter `goal:`, not the CARD goal, because only frontmatter is available at T0 · probe: status names the frontmatter goal on a bundle whose CARD goal differs
- A5 [which] covers: S3 · the request does not say which node types `unauthored_root` covers; taking the reading that it is Project and Spec only — the two types LIFECYCLE_TYPES excludes and that no other finding reaches -> a Persona standing in scaffold stays unreported, accepted because a Persona has no RULES to author
- A6 [which] covers: S4 · the request does not say which 2.x key the goal is read from; taking the reading that it is a `goal:` line anywhere in the archived PROJECT.md, matched the same loose way `title:` already is · probe: upgrade of a 2.x bundle carrying a goal line lands that goal in the fresh PROJECT.md
- A7 [when] covers: S1 · the request does not say when the counter is written; taking the reading that it is written in the same atomic write as the delta line itself, never as a second pass, so a crash cannot leave the two disagreeing -> a separate write would make drift the normal state rather than the exception
- A8 [when] covers: S2, S3 · the request does not say when an unauthored root stops being reported; taking the reading that it is reported until authored, with no grace period and no first-run exemption -> a fresh `init` bundle reports one warning immediately, which is the intended read of R:GREENBUNDLE
- A9 [when] covers: S4 · the request does not say when `invariants:` is written; taking the reading that only `init` writes the key, so an existing bundle gains it through `upgrade` or a hand-edit, never through a silent migration on an unrelated verb -> a bundle predating this change reports drift rather than being rewritten under its owner
- A10 [absent] covers: S1, S2 · the request does not say what a missing counter means; taking the reading that absent means UNKNOWN and never zero, matching `_as_date`'s existing refusal to default -> the whole point of the listing is lost if an unmigrated bundle reads as clean (this is R:UNKNOWNCLEAN)
- A11 [absent] covers: S3 · the request does not say what an absent Spec body section means; taking the reading that a Spec with no `## Deltas` section at all has a body count of zero, not unknown, because the section is engine-written and its absence is authored, not missing -> a spec whose section was deleted reports drift against 0, which is the honest signal
- A12 [absent] covers: S4 · the request does not say what an absent 2.x `goal:` means; taking the reading that `upgrade` then writes the same placeholder `init` writes, and never crashes or invents -> the fresh bundle carries a warning instead of a fiction
- A13 [order] covers: S2 · the request does not say where the delta clause and the goal sit in the header; taking the reading that the goal rides the title line and the delta clause is appended to the existing hidden-nodes tally line, so no new line is added to the 20-line budget -> a new line costs budget the report has already fought for
- A14 [order] covers: S3 · the request does not say how the two new findings order against the existing ones; taking the reading that they follow the existing severity ordering with no special case, `unauthored_root` as `warn` and `delta_count_drift` as `info` -> a new finding that jumps the queue re-ranks an already-tuned report
- A15 [order] covers: S1, S4 · the request does not say where the new keys sit in frontmatter; taking the reading that `set_key` places them as it already does and no key order is asserted anywhere -> asserting order would break every hand-edited bundle
- A16 [experience] covers: S2 · the receiver is an agent resuming a cold session, and what would make this hard is a number with no next verb; taking the reading that the clause names the verb that acts on it · probe: the status line naming a nonzero count also names `add deltas`
- A17 [experience] covers: S3 · the receiver is a newcomer running `doctor` to ask whether the bundle is in good shape; taking the reading that `unauthored_root` names WHICH slot is unauthored rather than saying the file is scaffold, because the actionable unit is the slot · probe: the finding text on a template PROJECT.md names the goal slot
- A18 [experience] covers: S1, S4 · the receiver is a human reading raw frontmatter in a diff, and what would make it hard is an unexplained integer; taking the reading that both keys carry no inline comment (frontmatter here holds none anywhere) and are instead explained in the engine docstring that writes them -> an inline comment would be the first in the corpus and `set_key` would have to preserve it
- A19 [experience] covers: S3 · n/a for `delta_count_drift` beyond A17 — its receiver and its hardship are the same newcomer and the same slot-naming rule, and splitting it would restate A17 with one word changed

## PLAN
contract: `open_deltas` is an int on each Spec, maintained inside the existing single write in `learn` and `fold` via `set_key`. `status` sums the key across Spec nodes from `scan()` frontmatter, rendering a question mark for any Spec missing or holding an unparsable value, and appends one clause to the existing tally line; the Project goal rides the title line. `doctor` gains `unauthored_root` (warn, Project and Spec, naming the standing slots the way `unauthored_node` already does) and `delta_count_drift` (info, frontmatter versus body count), with `doctor_sync` rewriting the key. `init` seeds `invariants: []` and `upgrade` matches a 2.x `goal:` the same loose way it already matches `title:`.
strategy: engine first with checks red, then the four-way twin mirror and the `engine_pin` repin in the same commit, then the full suite before the receipt (M32 — a verb-level guard fires on the whole source, so a `learn` change can red a `status` guard).

## EDGES
- E1 a Spec carrying `open_deltas: 0` and no open delta in its body: no drift finding, and the total omits it without rendering a zero clause
- E2 a bundle where no Spec carries the key at all, which is every bundle that exists today: the total renders unknown, `doctor` files drift for each Spec, and one `--sync` repairs all five
- E3 a `fold` call whose match retags more than one delta decrements the counter by the number actually retagged, not by one
- E4 a PROJECT.md whose frontmatter goal is authored but whose CARD goal is still a placeholder: `unauthored_root` still fires, naming the CARD slot
- E5 an `upgrade` from a 2.x PROJECT.md carrying no `goal:` line: the fresh root gets the ordinary placeholder and the verb does not fail

## CHECKS
- test_status_counts_open_deltas · covers: M1 · a bundle with three open deltas across two Specs reports a total of three, and the project goal appears in the header
- test_status_unknown_counter_is_not_zero · covers: M2, R:UNKNOWNCLEAN, A10 · a Spec with the key absent, and a Spec with the key set to a non-integer, both render the total as unknown rather than as a number
- test_status_stays_t0 · covers: R:T2SCAN · the existing tier spy sees no read above T0 while the new clause is produced
- test_doctor_warns_unauthored_root · covers: M3, R:GREENROOT, A17 · a freshly initialised bundle yields a `unauthored_root` warning against PROJECT.md naming its goal slot, and one against each scaffold Spec
- test_doctor_reports_and_syncs_delta_drift · covers: M4, E2 · a Spec whose key disagrees with its body files `delta_count_drift`, and `doctor_sync` rewrites the key to the body count
- test_init_writes_invariants_and_doctor_reads_it · covers: M5, R:DEADKEY, A2 · `init` writes `invariants:` as an empty list, and the key is named by at least one `doctor` code path so no key exists that nothing reads
- test_upgrade_carries_the_goal · covers: M6, R:CLOBBERGOAL, A6, E5 · a 2.x bundle carrying a goal line lands that goal in the fresh PROJECT.md, and a 2.x bundle with no goal line lands the ordinary placeholder without failing
- test_learn_and_fold_maintain_the_counter · covers: M7, A7, A3, E3 · `learn` raises the key by one in the same write as the delta line, `fold` lowers it by the number retagged, and only `open` deltas are counted
- test_status_clause_names_its_verb · covers: A16, A13 · a nonzero total renders on the existing tally line and names `add deltas`
- test_doctor_root_finding_reads_the_card_too · covers: E4, A4 · a PROJECT.md with an authored frontmatter goal and a placeholder CARD goal still yields the finding, and `status` names the frontmatter goal
- test_no_new_verb · covers: A5, A9, A15 · the CLI verb set is unchanged, and `unauthored_root` fires on Project and Spec while leaving Persona untouched
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
