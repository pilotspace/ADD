---
type: Task
title: Repository orientation invokes the installed CLI and yields a resume point
status: done
depth: standard
scope:
  - AGENTS.md
  - AGENTS.md.bak
  - add-method/tests/test_repo_orientation.py
gives:
  - S1 repository agent orientation — a working resume command and current beat guidance
generated: { by: add/3.6.0, at: 2026-09-14 }
verified:
  - { by: "agent:codex", at: 2026-09-14, act: freeze, authority: process, direction: "sha256:1757c8bbe75ea6b4", binding: "sha256:e3b0c44298fc1c14", gives: "sha256:56371d7b4921a141" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:7ceb26e0630f47ed" }
  - { by: "process:run", at: 2026-09-14, act: run, authority: process, outcome: PASS, receipt: /tasks/orientation-matches-the-cli.d/runs/1.md }
  - { by: "agent:codex", at: 2026-09-14, act: gate, authority: process, outcome: PASS, receipt: /tasks/orientation-matches-the-cli.d/runs/1.md, brief: "sha256:1640606185b88582" }
---
## CARD
goal: a Codex session starts from real ADD state instead of a silent library invocation
why: the installed CLI moved to cli.py; the repository AGENTS pointer still names add.py and the retired guide verb

## RULES
<must>
- M1 The repository AGENTS orientation invokes cli.py status and names no retired guide command. (from: user-approved enhancement plan Track II · fails-on: the current stale pointer)
- M2 Running its status command emits a non-empty resume point from a real initialized bundle. (from: user expected picture continuity · fails-on: exit-zero library invocation)
- M3 Refresh via the existing installer preserves content outside its managed block. (from: existing installer contract · fails-on: replacing the whole user instruction file)
</must>
<reject>
</reject>

## ASSUMPTIONS
- A1 [who] n/a · restoring the existing supported installer pointer introduces no new who policy
- A2 [which] n/a · restoring the existing supported installer pointer introduces no new which policy
- A3 [when] n/a · restoring the existing supported installer pointer introduces no new when policy
- A4 [absent] n/a · restoring the existing supported installer pointer introduces no new absent policy
- A5 [order] n/a · restoring the existing supported installer pointer introduces no new order policy
- A6 [experience] n/a · restoring the existing supported installer pointer introduces no new experience policy

## PLAN
contract: regenerate the managed AGENTS block with the existing Python installer, preserving user material
regression: affected · python3 -m pytest tests/test_repo_orientation.py tests/test_agent_pointer_sizing.py tests/test_npm_pip_parity.py -q · repository pointer plus installer parity

## CHECKS
- test_repo_orientation_uses_current_cli · covers: M1 · current command and no retired verb
- test_orientation_status_produces_resume_output · covers: M2 · subprocess executes status against a real bundle
- test_pointer_refresh_preserves_user_content · covers: M3 · installer refresh retains surrounding bytes

## EVIDENCE
receipt: /tasks/orientation-matches-the-cli.d/runs/1.md · kind: test-ids · 16/16 reported · exit 0 · 2026-09-14
gate: PASS · authority process · by agent:codex · receipt /tasks/orientation-matches-the-cli.d/runs/1.md · 2026-09-14

## LESSONS
- none filed — no lesson cites /tasks/orientation-matches-the-cli.md (add learn <lens> "<lesson>" --evidence /tasks/orientation-matches-the-cli.md)
