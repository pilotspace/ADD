---
type: Task
title: A quick commit into a sensitive or frozen path is refused where the bundle sees it
status: direction
depth: standard
sensitivity: security
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
gives:
  - S1 `learn` inspects a lesson opening `quick:` whose `--evidence` is a commit sha: the commit's changed paths are matched against `index.md`'s `sensitive_paths:` and every OPEN task's `scope:`; a hit refuses R:QUICKSIZEUP naming the path, the floor or the owning task, and the fix `add new Task`
  - S2 intake.md's Quick step runs `add locate <path>` per file before the first edit, so the tripwire fires before the commit
  - S3 the lesson is still recorded when the sha is unreadable — the tripwire never blocks the direct lane's one bundle write on git's absence
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "human:Tin Dang", at: 2026-09-13, act: interview, authority: human, interview: "sha256:a458fac71bbc31d9", receipt: /tasks/quick-lane-tripwire.d/interviews/1.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|E1=confirm|E2=confirm|E3=confirm|E4=confirm|E5=confirm|E6=confirm|R:QUICKSIZEUP=confirm|R:OUTWARD=confirm|R:LANEBLOCKED=confirm|M1=confirm|M2=confirm|M3=confirm|M4=confirm|M5=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-13, act: interview, authority: human, interview: "sha256:55f34d86fa8a5350", receipt: /tasks/quick-lane-tripwire.d/interviews/2.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|A7=confirm|A8=confirm|A9=confirm|A10=confirm|A11=confirm|E1=confirm|E2=confirm|E3=confirm|E4=confirm|E5=confirm|E6=confirm|R:QUICKSIZEUP=confirm|R:OUTWARD=confirm|R:LANEBLOCKED=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-13, act: freeze, authority: human, direction: "sha256:1f26b21a39082c6e", binding: "sha256:69e14c1306e71f45", gives: "sha256:c185c7e6098c90b2" }
---
## CARD
goal: `learn` inspects a `quick:` lesson's commit sha against `index.md` `sensitive_paths:` and every open task's `scope:`, refusing R:QUICKSIZEUP with the path and the owner; intake.md's Quick step runs `add locate` per file before the first edit
why: the direct lane is the one route the floor never sees; "when in doubt size up" is prose, and the one bundle write a Quick change makes is a `learn` line with a sha the engine records and checks nothing about (C11)
beat: direction · next: add interview quick-lane-tripwire, then add freeze quick-lane-tripwire --by "human:<name>"

## RULES
<must>
- M1 `learn` whose lesson text starts `quick:` and whose `--evidence` is a git object name resolving to a commit (`rev-parse --verify -q <sha>^{commit}`) reads that commit's changed paths (`diff-tree --no-commit-id --name-only -r`, read-only) and refuses R:QUICKSIZEUP when any path matches an `index.md` `sensitive_paths:` pattern (naming the path and `floor human`) or lies under an OPEN Task's `scope:` (naming the path and the task cid); the refusal names the fix — `add new Task <slug> --scope <path>` — and writes no lesson (from: interview)
- M2 the match is the engine's own: `_paths_touch` for sensitive patterns (A17's matcher) and scope containment as `scope_digest` reads a scope entry; OPEN means a Task whose status is not `done`, `dropped` or `archived` and that carries a freeze stamp (an unfrozen scope has frozen nothing) (from: interview)
- M3 a `quick:` lesson whose evidence is not a commit (a receipt cid, a path, prose), or whose sha git cannot resolve, or in a tree that is not a repo, is recorded exactly as today — the tripwire reads git and never blocks the lane on git's absence; a lesson not opening `quick:` is never inspected (from: interview)
- M4 the verb calls git READ-ONLY (`rev-parse`, `diff-tree`) — never `commit`, `checkout`, `reset` or any command that moves the tree (R:OUTWARD) (from: interview)
- M5 intake.md's Quick step says to run `add locate <path>` per file BEFORE the first edit and names R:QUICKSIZEUP as what the learn line refuses after; the skill surface stays line-neutral vs HEAD and the three trees identical (from: interview)
</must>
<reject>
- R:QUICKSIZEUP a quick lesson citing a commit that touched a sensitive path or an open task's frozen scope -> "QUICKSIZEUP"
- R:OUTWARD the engine moving the working tree while inspecting a commit -> "OUTWARD"
- R:LANEBLOCKED the direct lane's one bundle write refused because git is absent, the sha is unreadable, or the lesson is not a quick line -> "LANEBLOCKED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · the request does not say who files the quick line; taking the agent or human who made the change, as intake.md's route line already says — the engine reads the sha, not the author -> cost if wrong: a quick line filed by a reviewer for someone else's commit is inspected the same way, which is the point
- A2 [which] covers: S1 · the request does not say which tasks' scopes count; taking OPEN and FROZEN Tasks only — a done task's scope is history, an unfrozen task's scope is a draft nobody sealed -> cost if wrong: a quick commit into a task's scope the day before its freeze is not refused; the freeze's own receipt freshness catches the moved blob · probe: a scope of an unfrozen task draws no refusal
- A3 [when] covers: S1 S2 · the request does not say whether the tripwire runs before or after the commit; taking both — `add locate` before (skill) and `learn` after (engine) — because the engine sees nothing until the bundle is written, and a refusal after the commit still names the task to create before the branch merges -> cost if wrong: a refused commit stays in the branch history; the refusal names the fix, and the direct lane's commit is the author's to amend
- A4 [absent] covers: S1 S3 · the request does not say what `sensitive_paths: []` means; taking no sensitive floor — only open scopes are matched — and an `index.md` with no key the same -> cost if wrong: a bundle that never declared sensitive paths gets no sensitivity tripwire, which is what it declared
- A5 [order] covers: S1 · the request does not say which hit is named when a path matches both; taking the sensitive floor first (it is unstrikeable and outranks a scope), then the first open task in cid order -> cost if wrong: a CI diff churns
- A6 [experience] covers: S1 S2 S3 · the request does not say who reads the refusal; the reader is the agent that just took the direct lane in good faith; hard for them is a refusal that says "sensitive" and not which path — taking the refusal to name the path, the reason (the pattern or the task) and the exact `add new Task` line with the path as `--scope` -> cost if wrong: the agent files the lesson without the `quick:` prefix, which M3 records as an ordinary lesson — the leak stays visible in the record as a lesson with no route line
- A7 [which] covers: S2 · the request does not say which surface carries the pre-edit step; taking intake.md's Quick step alone — the one file the direct lane actually opens — not verify.md and not the book, because a lane that skips ceremony reads exactly one page -> cost if wrong: an author who never opens intake.md meets the refusal at the learn line instead, which is the tripwire working late
- A8 [which] covers: S3 · the request does not say which git failures are 'git absent'; taking every one — not a repo, an unresolvable sha, a git binary that is missing or errors — because the direct lane's one bundle write must never be lost to the engine's own inability to look (R:LANEBLOCKED) -> cost if wrong: a quick lesson about a sensitive path is recorded in a tree the engine cannot read; the next `doctor` still sees the lesson
- A9 [when] covers: S3 · the request does not say when the inspection runs; taking it at `learn`, after the lesson's own grammar is accepted and before anything is written, so a refused quick line writes nothing at all -> cost if wrong: none; a refusal that half-wrote would be the partial-merge shape the engine forbids elsewhere
- A10 [absent] covers: S2 · the request does not say what an ABSENT `sensitive_paths:` or an empty open-task set means; taking both as 'nothing matches' — the tripwire is a floor check, not a default-deny -> cost if wrong: a bundle that declares no sensitive paths gets no protection from this rung, which is what declaring none means
- A11 [order] covers: S2 S3 · the request does not say the order of the two matches or of the doc edit; taking sensitive paths FIRST (the floor outranks an owner) and the doc landing in the source tree and mirrored, never edited per-tree -> cost if wrong: a path that is both sensitive and owned is reported as sensitive, which is the higher answer

## PLAN
contract: `_commit_paths(repo, sha) -> list|None` (read-only git) · `quick_hit(root, graph, paths) -> (kind, path, owner)|None` · `learn(...)` gains the tripwire before the write · intake.md Quick step sentence
strategy: the sha is recognised by `rev-parse --verify -q <evidence>^{commit}`, never by shape, so a receipt cid or prose is never mistaken for a commit; `_paths_touch` and `_scope_list` are reused; four twins, both pins, three skill trees line-neutral (the intake.md prose pin re-aimed with its reason)
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change on learn (method.md bind)
- O1 covers: M1 · signal count of learn calls refused R:QUICKSIZEUP · window 7d · threshold > 3 · action alert
port: `add.learn` on a git fixture with a sensitive path, a frozen open task and a quick commit

## EDGES
- E1 Given `sensitive_paths: [src/auth/**]` and a commit touching `src/auth/token.py` · When `learn add "quick: rotate keys — small" --evidence <sha>` · Then R:QUICKSIZEUP naming the path, `floor human` and `add new Task`; no lesson
- E2 Given an open frozen task with `scope: [src/billing.py]` and a commit touching it · When the same · Then R:QUICKSIZEUP naming the path and `/tasks/<task>.md`; given the task is done · Then the lesson lands
- E3 Given a commit touching only `README.md` · When the same · Then the lesson lands
- E4 Given `--evidence /tasks/t.d/runs/1.md`, `--evidence deadbeef` (no such object), and a bundle outside any repo · When a quick lesson · Then each lands exactly as today
- E5 Given a lesson not opening `quick:` citing the sensitive commit · When `learn` · Then it lands — only the quick line is inspected
- E6 Given a git spy · When the tripwire runs · Then only `rev-parse` and `diff-tree` were called

## CHECKS
- test_quick_commit_into_a_sensitive_path_is_refused · covers: M1, R:QUICKSIZEUP, A5, E1 · acceptance · names path, floor, fix; nothing written
- test_quick_commit_into_an_open_frozen_scope_is_refused · covers: M1, M2, A2, E2 · acceptance · names path and task; done and unfrozen tasks draw none
- test_clean_quick_commit_lands · covers: M1, E3 · acceptance · the lesson is written
- test_lane_is_never_blocked_on_git · covers: M3, R:LANEBLOCKED, A4, E4, E5 · acceptance · receipt cid, unknown sha, no repo, non-quick lesson all land
- test_tripwire_calls_git_read_only · covers: M4, R:OUTWARD, E6 · acceptance · the spy saw rev-parse and diff-tree only
- test_intake_md_states_it · covers: M5 · static · the Quick step names add locate before the edit and R:QUICKSIZEUP; trees identical; line-neutral; the prose pin re-aimed with a reason
red-first: every check MUST fail first.

## EVIDENCE
receipt: <none yet>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
