---
type: Task
title: A run receipt names the commit it ran against
status: done
depth: standard
sensitivity: mechanical
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/FORMAT.md
gives:
  - S1 `receipt.head` / `receipt.committed` — two scalar keys on a `type: Run` node's `receipt:` map and on the dict `run()` returns
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:c1f1a998c881784b", binding: "sha256:8fd57a8108a35a7f" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:e25f53ffd6e8a27a" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/receipt-anchored-to-head.d/runs/1.md }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/receipt-anchored-to-head.d/runs/1.md, brief: "sha256:5504dc415227fc4f" }
---
## CARD
goal: run records head: and committed: on every receipt inside git, absent and said so outside it, so a release can cite the tree a receipt verified
why: a receipt names the blobs it observed and not the commit — so nothing in the bundle can say whether a tag shipped the tree a PASS verified; `release-stamp` needs this anchor and cannot invent it after the fact
beat: done · next: add status

## RULES
<must>
- M1 inside a git working tree with at least one commit, `run` records `head: <40-hex sha>` — the commit HEAD named when the run STARTED — on the Run node's `receipt:` map and on the returned receipt dict
- M2 `committed: true` exactly when every entry of the receipt's `scope_digest` carries the same blob as that path in HEAD's tree; any differing, untracked or vanished scope path makes it `false`
- M3 outside a git working tree, or on an unborn branch (no commit yet), NEITHER key is written, and the receipt's `note:` names the cause in the same line the digest degrade already uses
- M4 FORMAT §8.1 states both keys, their absence rule, and that `committed` compares scope blobs to HEAD and nothing else
</must>
<reject>
- R:INVENTEDHEAD a `head:` written when `git rev-parse HEAD` did not answer — a sha nobody observed -> "INVENTEDHEAD"
- R:COMMITTEDBYCLAIM `committed:` derived from whole-tree cleanliness (`git status`) instead of the scope blobs — a dirty file OUTSIDE scope must not flip it, and a scope file changed but the tree otherwise clean must -> "COMMITTEDBYCLAIM"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · a receipt field has no actor; `run` already records `by: "process:run"`
- A2 [which] covers: S1 · the request does not say which files decide `committed`; taking EXACTLY the `scope_digest` set already recorded (directory scopes enumerated through git as today), never the whole tree -> cost if wrong: a receipt reads `committed: false` because of a build artifact nobody reviewed, and `release` refuses a tree that is in fact the verified one · probe: a dirty file outside scope leaves `committed: true`
- A3 [when] covers: S1 · the request does not say when HEAD is read; taking the run's START, before the command executes, so a command that commits mid-run cannot move the anchor under its own digest -> cost if wrong: a receipt cites a commit that contains files the digest never saw
- A4 [absent] covers: S1 · the request does not say what a reader makes of a missing key; taking absent = UNKNOWN, never `false` and never `null` — a pre-3.7 receipt and a non-git receipt both simply lack the keys, and `release` (the next task) must refuse on absence rather than read it as uncommitted -> cost if wrong: every receipt written before 3.7 becomes unreleasable OR silently releasable
- A5 [order] n/a · two scalars on a map; the receipt writer already fixes key order
- A6 [experience] covers: S1 · the request does not say who reads these keys and what would make it hard for them; the readers are `release-stamp` (next task), `show`, and a human opening `runs/<n>.md` — hard for them is a sha with no prefix to grep and a boolean spelled three ways; taking bare 40-hex for `head` and YAML `true|false` for `committed` -> cost if wrong: the next task's comparison has to normalise, and a grep for the tag's sha misses the receipt

## PLAN
contract: `receipt.head: <sha>` · `receipt.committed: true|false` — written by `run` after the digest and before the command; read by `release` (next task) and rendered by `show`
strategy: read HEAD with the existing `_git(root.parent, "rev-parse", "HEAD")` (None on unborn/non-git); batch the HEAD blobs with one `git ls-tree -r -z HEAD -- <paths>` and compare to `scope_digest`; write both keys into the same `receipt` dict the body serialiser already walks; extend the degrade note, never add a second note; mirror to the bundled twin and re-aim `ENGINE_MD5`
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/FORMAT.md
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind: a change to add.py runs the full suite before its receipt)
port: `add.run(bundle, cid, cmd)` → the returned `receipt` dict — every acceptance check reads it, none parses the file

## EDGES
- E1 Given a git repo with one commit and an unchanged scope file · When `run` records a receipt · Then `head` equals `git rev-parse HEAD` and `committed` is true
- E2 Given the scope file edited but not committed · When `run` records · Then `head` is unchanged and `committed` is false
- E3 Given `git init` with no commit yet · When `run` records · Then the receipt has no `head` and no `committed` key, and its note says the tree has no commit
- E4 Given a file OUTSIDE scope edited and the scope file clean · When `run` records · Then `committed` is true

## CHECKS
- test_receipt_records_head_sha · covers: M1, E1 · acceptance · the returned receipt's `head` is HEAD's 40-hex sha, read at start
- test_committed_true_when_scope_matches_head · covers: M2, E1 · acceptance · clean scope → `committed` is True (the bool, not a string)
- test_committed_false_when_scope_edited · covers: M2, E2 · acceptance · an uncommitted edit to a scope file → False, head unchanged
- test_unrelated_dirt_does_not_flip_committed · covers: R:COMMITTEDBYCLAIM, E4, A2 · acceptance · a dirty non-scope file leaves `committed` True
- test_no_head_on_unborn_branch_or_outside_git · covers: M3, E3, R:INVENTEDHEAD · acceptance · both keys absent and the note names the cause, in both trees
- test_head_read_before_the_command_runs · covers: A3 · acceptance · a command that commits mid-run leaves `head` at the pre-run sha
- test_format_states_head_and_committed · covers: M4 · static · FORMAT §8.1 names both keys and the absence rule
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/receipt-anchored-to-head.d/runs/1.md · kind: test-ids · 7/7 reported · exit 0 · 2026-09-11
gate: PASS · authority process · by plan:loop-that-closes · receipt /tasks/receipt-anchored-to-head.d/runs/1.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/receipt-anchored-to-head.md (add learn <lens> "<lesson>" --evidence /tasks/receipt-anchored-to-head.md)
