---
type: Milestone
title: The roster the skill names is the roster that ships and may run its beats
status: done
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:75a11da44c802486" }
---
## CARD
goal: The shipped skill names the two agents ADD actually ships, each agent is permitted the engine verbs its own beat guide requires, the Explore lane has a mode, and both installer twins land the roster where the host can discover it.
why: `add-worker` and `add-advisor` appear ZERO times across the entire shipped skill corpus. The one
  delegation guide, `streams.md:99-101`, instead names `backend-expert` · `security-expert` ·
  `frontend-expert` as the agentType to spawn — the maintainer's own private local subagents, present in
  `~/.claude/agents/` and shipped by nothing. A user who installs from npm or PyPI and asks the skill to
  delegate gets a subagent_type that does not exist, while the two agents they did install are unreachable
  through any documented path. The guard written for exactly this class proves the table's PERSONA column
  against the corpus and its EXECUTOR column against nothing. Worse, `add-worker.md:100` forbids running
  the engine or writing shared state — but `build.md:7` makes `add brief` Build's first verb and
  `verify.md:9` makes `add run` the only trusted artifact, so an agent that obeys its own boundary
  produces a plausible diff and no receipt, and the gate later refuses it with `R:UNBRIEFED`, a refusal
  nothing in the agent's context explains. Neither agent file names a single one of the 24 verbs. The
  Explore lane — the one rung ADD reserves for "do not guess" — has no mode in either file. And the two
  installer twins disagree: `personas-index` is in the JS `GLOBAL_TREES` and absent from the Python
  `_GLOBAL_TREES`, so pip users never receive a refreshed routing index, while a global install lands the
  roster at `<home>/agents` where Claude Code cannot see it.
next: add milestone-done roster-reachable

## SCOPE
In:  the `streams.md` roster table's executor column and a guard binding it to shipped agents · the
  agent files' verb boundary, split MAY/NEVER by beat · an `explore` mode · the retired 2.x vocabulary
  still load-bearing in the roster (`§3 Scope`, `§4 suite`, `Specify`, `scenarios`,
  `dependencies.allowlist`, `refute-read`) · `agents/` and `personas-index/` under tree-parity and the
  shipped-doc lint · the Python/JS `_GLOBAL_TREES` divergence · roster discoverability on a global install.
Out: splitting the roster back into more than two agents (the 3.3.0 collapse was right; the gap is a
  missing mode, not a missing agent) · the persona selection algorithm itself (live-persona-tier).

## GROUND
touches: add-method/skill/add/streams.md · add-method/agents · add-method/src/add_method/_installer.py · add-method/bin/cli.js · add-method/tests · add-method/scripts/book_lint.py · add-method/tooling/test_tree_parity.py
risks:
  - The four roster copies are byte-identical today; adding them to tree-parity must not red on the
    gitignored dogfood twin, which needs the established exists-skip.
  - Loosening the agents' "never run the engine" boundary must not loosen the two seams that are
    correctly forbidden — `freeze` and `gate` stay human-marked, and security stays HARD-STOP.

## EXIT
- [x] The roster table names only agents that ship, under a guard, and the skill names them   (← roster-named-and-bounded)
- [x] Each agent may run the verbs its beat requires and no seam verb, with Explore given a mode   (← roster-named-and-bounded)
- [x] Both installer twins land the same trees, and a global install puts the roster where the host sees it   (← installer-reach-parity)

## CLOSE
evidence:
