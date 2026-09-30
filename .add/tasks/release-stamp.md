---
type: Task
title: add release binds a tag's tree to the receipts that verified it
status: done
depth: standard
sensitivity: architecture
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
  - add-method/FORMAT.md
  - add-method/docs
gives:
  - S1 `add release <tag> --milestone <m> [--artifact <name@digest>] [--build <ref>] --by <name>` — the 29th verb, and the `act: release` stamp it appends to each named milestone
  - S2 the rendering of a released milestone — `status --all` names the tag on the row, `show` carries the stamp
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:db13577b8394716f", binding: "sha256:69e14c1306e71f45", gives: "sha256:760ca27e0587b1cd" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:f063da1e6f01b80c" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/release-stamp.d/runs/1.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/release-stamp.d/runs/2.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/release-stamp.d/runs/3.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/release-stamp.d/runs/4.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 25, receipt: /tasks/release-stamp.d/runs/3.md, tier: T2, note: "gate PASS on runs/1 then a red narrow run (exit 1) on the same tree -> release v1 stamps receipts: runs/2.md (a FAIL receipt) and, with an uncommitted scope edit, refuses R:UNANCHORED a tag the gated receipt anchors — vs CARD/R:UNANCHORED 'gated receipt' and A6 'proven by which receipts'; also a 78-char tag makes the status --all row 158 > ROW_WIDTH 100 vs a-roadmap R:ROWBLOAT" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:0a580b646f88a90d", binding: "sha256:8190f3aa8dea8cbf", gives: "sha256:760ca27e0587b1cd" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:87050446e782b9a9" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/release-stamp.d/runs/5.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/release-stamp.d/runs/6.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 12, receipt: /tasks/release-stamp.d/runs/5.md, tier: T2, note: "done task + red run + gate HARD-STOP after done -> release v2 (the finding's tree) STAMPS receipts: runs/2.md (a FAIL receipt) and release v1 (the PASS'd tree) refuses R:UNANCHORED saying t 'verified' a blob a HARD-STOP was written against — vs CARD 'receipts that verified it', A6 'proven by which receipts', and done's 'HARD-STOP entitles nothing' (M3 letter 'newest act: gate' obeyed; needs 'newest CLOSING gate')" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:535d480c9b7273e7", binding: "sha256:679cc367aa761920", gives: "sha256:760ca27e0587b1cd" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:f018354e9ff95516" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/release-stamp.d/runs/7.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/release-stamp.d/runs/8.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/release-stamp.d/runs/9.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 11, receipt: /tasks/release-stamp.d/runs/7.md, tier: T2, note: "milestone m with done task t (anchored) + member u reopened to build (unmet) -> release v1 lands with note 'anchored by 1 receipt' and never names u — vs M3 'a member that is not done is named in the note as not anchored' (_anchor drops not_done on the success path; FORMAT §8.6 narrows the clause to the refusal)" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:bd0925c5798255d6", binding: "sha256:bb9c6769906f86c2", gives: "sha256:760ca27e0587b1cd" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:403c8e7577086119" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/release-stamp.d/runs/10.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/release-stamp.d/runs/11.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 10, receipt: /tasks/release-stamp.d/runs/10.md, tier: T2, changed: "three T2 reads moved the anchor to the newest CLOSING gate after the last reopen, named not-done members, refused an empty anchor and clamped the row (E7–E12)" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/release-stamp.d/runs/10.md, brief: "sha256:f08cbaf49c13d20c" }
---
## CARD
goal: `add release <tag> --milestone m [--artifact name@digest] [--build ref]` appends `act: release` to a done milestone, refusing a tag whose tree lacks any scope blob a gated receipt recorded (R:UNANCHORED); status --all and show render it; the engine never tags, publishes or deploys
why: a PASS proves a source state and a receipt now names the commit it observed, but nothing in the bundle can say which tree a tag shipped — production telemetry is then evidence about an unknown build; the seam stays human (the engine never acts outward) while the record gains the one comparison only git can make
beat: done · next: add status

## RULES
<must>
- M1 `add release <tag> --milestone <m> --by <name>` appends one stamp `{ by, at, act: release, authority: process, tag, tree: <the tag's tree sha>, receipts: "<cid,…>" }` to each named milestone; `--artifact` and `--build` are recorded verbatim under `artifact:` and `build:` exactly when given, never defaulted and never verified
- M2 it refuses a milestone that is not `done` or `archived` (R:NOTDONE) and a tag git cannot resolve to a tree (R:NOSUCHTAG), naming each
- M3 the anchor: for every member Task with status `done`, the receipt its NEWEST CLOSING gate stamp cites (`act: gate` with outcome PASS or RISK-ACCEPTED — `CLOSING_VERDICTS`, the verdicts `done` reads; a HARD-STOP is a finding and entitles nothing) and that POSTDATES the member's last `act: reopen` stamp — the window `done` reads; a closing gate the loop reset anchors nothing — never the latest run, which may postdate the verdict — has every `scope_digest` entry's blob equal to the blob the tag's tree holds at that path; one mismatch or absence refuses R:UNANCHORED naming the task, the path and both blobs; a done Task whose gated receipt carries no content digest, or whose cited receipt file is gone, refuses R:UNANCHORED naming it as unanchorable; a done Task with no closing gate stamp citing a receipt (an explore, a hand-marked done) is skipped by name in the success note; a member that is not `done` is named in the SUCCESS note as not anchored, with its status, beside the skipped explores; a milestone in which NO member anchors refuses R:UNANCHORED — a tree and no receipts is a label
- M4 the verb calls git READ-ONLY — `rev-parse` and `ls-tree` only — and never `tag`, `push`, `publish` or any command that acts outward
- M5 `status --all` names the tag at the end of a released milestone's row and `show <m>` carries the stamp; a milestone released twice carries two stamps, newest last; the row never exceeds ROW_WIDTH — the title yields first, then the tag is cut, never the other way
- M6 FORMAT §8.6 states the stamp, the anchor and the read-only rule; docs/16 §16.5 and docs/13 carry the verb; every registry that counts verbs counts 29
</must>
<reject>
- R:UNANCHORED a release stamp over a tag whose tree does not hold what the gated receipts observed -> "UNANCHORED"
- R:OUTWARD the engine tagging, publishing, pushing or deploying — a notary with credentials -> "OUTWARD"
- R:PROVENANCEJUDGED `--artifact` or `--build` checked against anything — they are recorded as handed; SLSA-style provenance is consumed by the pipeline, never produced or verified here -> "PROVENANCEJUDGED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · the request does not say who may release; taking anyone who can write the bundle, recorded by `--by` as every stamp is — the outward act (the tag itself) is where authorization lives, not here -> cost if wrong: a stamp claims a release a person never made; `by:` says who claimed it
- A2 [which] covers: S1 S2 · the request does not say which receipts anchor; taking the receipt each done member's newest CLOSING gate stamp CITES — the one the verdict read; a later HARD-STOP cites a finding's receipt, not a verdict's — never the latest run (a red or wider run after the PASS is not what was verified) and never a floor receipt (the gate never cites one) -> cost if wrong: a task re-gated on a later run anchors on that gate's receipt, which is the newest gate stamp by construction · probe: a red narrow run after the PASS leaves the anchor on the gated receipt (found by the T2 refute)
- A3 [when] covers: S1 S2 · the request does not say whether the tag must postdate the gates; taking NO ordering rule — the tree comparison is the whole claim, a tag cut before a PASS whose tree still holds the same blobs is honestly anchored -> cost if wrong: none the digest does not already cover
- A4 [absent] covers: S1 S2 · the request does not say what a done task with no digest means; taking unanchorable = refused by name (an unmeasurable receipt is not an anchored one, as `fresh` already distinguishes), and no-receipt = skipped by name (nothing to anchor) -> cost if wrong: a doc-profile milestone outside git can never be released — acceptable, a tag needs git
- A5 [order] covers: S1 S2 · the request does not say the order tasks are checked; taking sorted member cid, first mismatch refuses -> cost if wrong: a CI diff churns
- A6 [experience] covers: S1 S2 · the request does not say who reads the stamp; the readers are a release manager (`status --all`), an incident reader (`show`, "which tree shipped?") and the next task's `observes:`; hard for them is a stamp with a tag and no tree, or a tree and no receipts — taking both plus the receipt cids, so `show <m>` answers "which tree, proven by which receipts" without a second command -> cost if wrong: the stamp is a label, not an anchor

## PLAN
contract: `release(root, tag, milestones, by, artifact=None, build=None) -> (stamps|None, note)` · `_tag_tree(root, tag) -> sha|None` · `_anchor(root, graph, mcid, tree) -> (ok, detail, receipts)` · cli `release` parser + dispatch · `status --all` suffix · FORMAT §8.6 · docs/16 §16.5 · docs/13 row · README count 29 · WIRED set
strategy: reuse `_git` (read-only by construction of the argument list), `latest_receipt`, `_committed_to_head`'s ls-tree shape aimed at `<tag>` instead of HEAD; members = Tasks whose `milestone:` is the slug, as `milestone_done` enumerates them; the git spy in the check wraps `add._git` and asserts the subcommand set; four twins, both pins, WIRED and the count registries
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/tooling/cli.py add-method/src/add_method/_bundled/tooling/cli.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md add-method/docs README.md
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change and a new verb (method.md bind: a change to the verb set runs the full suite — ~9 registries)
port: `add.release` on a git fixture with a done milestone, one done task and a real tag

## EDGES
- E1 Given a done milestone whose done task's receipt is committed and tagged `v1` · When `release v1 --milestone m` · Then one stamp with tag, tree and the receipt cid; `status --all` shows `v1`
- E2 Given a scope file edited and committed after the receipt, tagged `v2` · When `release v2` · Then R:UNANCHORED naming the task, the path and both blobs; no stamp
- E3 Given a milestone still active · When `release` · Then R:NOTDONE; given a tag that does not exist · Then R:NOSUCHTAG
- E4 Given `--artifact api@sha256:abc --build gha://run/1` · When `release` · Then both land verbatim on the stamp; given neither · Then neither key is present
- E5 Given a done explore (no receipt) beside the done task · When `release` · Then the stamp lands and the note names the explore as skipped
- E7 Given the done task gated on runs/1, then a red narrow run (exit 1) recorded as runs/2 on the same tree · When `release v1` · Then the stamp cites runs/1, never runs/2; given a scope file edited uncommitted before that red run · Then `release v1` still lands — the gated receipt anchors (found by the T2 refute)
- E8 Given a 78-character tag and a long milestone title · When `status --all` · Then the row is at most ROW_WIDTH characters, ends with the tag, and the title was truncated before the tag (found by the T2 refute: R:ROWBLOAT of a-roadmap)
- E9 Given the done task gated PASS on runs/1, then a red run recorded as runs/2 on a moved committed tree tagged v2, then `gate HARD-STOP` recorded against runs/2 · When `release v1` · Then it lands citing runs/1; when `release v2` · Then R:UNANCHORED — the finding's tree ships nothing (found by the second T2 refute)
- E10 Given a done milestone whose only member was reopened (not done), or one with no members · When `release` · Then R:UNANCHORED naming the not-done member (or that there are none) — never `anchored by 0 receipts` (the second read's A6 note, ruled here)
- E11 Given done task t (anchored) beside member u reopened to build · When `release v1` · Then it lands and the note names `/tasks/u.md (build)` as not anchored (found by the third T2 refute)
- E12 Given t gated PASS on runs/1, reopened, hand-marked done again with no later gate · When `release v1` · Then t is skipped by name — its only closing gate predates the reopen (the third read's change request, ruled here)
- E6 Given a git spy · When `release` · Then only `rev-parse` and `ls-tree` were called

## CHECKS
- test_release_stamps_a_done_milestone_anchored_to_the_tag · covers: M1, M5, E1 · acceptance · stamp keys, tree sha, receipt cid, status --all and show render
- test_release_refuses_a_tree_that_moved_after_the_receipt · covers: M3, R:UNANCHORED, E2 · acceptance · names task, path, both blobs; no stamp
- test_release_refuses_not_done_and_no_such_tag · covers: M2, E3 · acceptance · both refusals by name
- test_artifact_and_build_are_recorded_as_handed · covers: M1, R:PROVENANCEJUDGED, E4 · acceptance · verbatim when given, absent otherwise, never checked
- test_unanchorable_and_receiptless_members · covers: M3, A4, E5 · acceptance · a digest-less receipt refuses by name; an explore is skipped by name
- test_floor_receipt_never_anchors · covers: A2 · acceptance · a later floor receipt leaves the anchor on the narrow receipt
- test_release_calls_git_read_only · covers: M4, R:OUTWARD, E6 · acceptance · the spy saw only rev-parse and ls-tree
- test_anchor_is_the_gated_receipt_not_the_latest_run · covers: M3, A2, E7 · acceptance · a red run after PASS neither moves the cited receipt nor refuses the gated tree
- test_long_tag_keeps_the_row_bounded · covers: M5, E8 · acceptance · row ≤ ROW_WIDTH, tag at the end, title yields first
- test_anchor_is_the_closing_gate_not_a_later_finding · covers: M3, A2, E9 · acceptance · a HARD-STOP after done neither moves the anchor nor stamps its tree
- test_empty_anchor_refuses_and_names_the_not_done · covers: M3, A6, E10 · acceptance · a reopened-only or memberless milestone refuses by name
- test_success_note_names_not_done_members · covers: M3, A6, E11 · acceptance · a mixed milestone lands and names the reopened member with its status
- test_closing_gate_must_postdate_the_reopen · covers: M3, E12 · acceptance · a reopened-then-hand-marked member is skipped, not anchored on the reset verdict
- test_registries_and_docs_carry_the_verb · covers: M6 · static · WIRED, README 29, docs/13 row, docs/16 §16.5, FORMAT §8.6
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/release-stamp.d/runs/10.md · kind: test-ids · 14/14 reported · exit 0 · 2026-09-11
refute: held · 10 probe(s) · tier T2 · by advisor:engine-notary · against /tasks/release-stamp.d/runs/10.md · 2026-09-11 · changed: three T2 reads moved the anchor to the newest CLOSING gate after the last reopen, named not-done members, refused an empty anchor and clamped the row (E7–E12)
gate: PASS · authority plan · by plan:loop-that-closes · receipt /tasks/release-stamp.d/runs/10.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/release-stamp.md (add learn <lens> "<lesson>" --evidence /tasks/release-stamp.md)
