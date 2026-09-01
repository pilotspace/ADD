---
type: Task
title: The skill names the agents it ships, and each may run the verbs its beat requires
status: done
depth: quick
milestone: roster-reachable
scope:
  - add-method/skill/add
  - add-method/agents
  - add-method/tests
gives:
  - S1 the delegation roster table — which agent the skill tells you to spawn
  - S2 the agents' verb boundary — which engine verbs each agent may and may not run
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:6ecb07c77a2f36fc" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:1f9a1abbfd5010ab" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/roster-named-and-bounded.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: process, outcome: PASS, receipt: /tasks/roster-named-and-bounded.d/runs/1.md, brief: "sha256:9569be6734c35837" }
---
## CARD
goal: The skill names the two agents ADD ships, the roster table points only at agents that ship, each agent is permitted the verbs its own beat guide requires while the human seams stay forbidden, and Explore has a mode.
why: `add-worker` and `add-advisor` appear ZERO times across the shipped skill corpus — verified by grep over `skill/add/*.md` and `skill/add/phases/*.md`. The one delegation guide, `streams.md:99-101`, instead names `backend-expert` · `security-expert` · `frontend-expert` as the agentType to spawn; those are the maintainer's own local subagents, present in `~/.claude/agents/` and shipped in no package manifest, no installer tree and no `_bundled/agents/`. A user who installs from npm or PyPI and asks the skill to delegate gets a subagent_type that does not exist, while the two agents they did install are unreachable through any documented path. The guard written for exactly this class proves that table's PERSONA column against the corpus and its EXECUTOR column against nothing. The boundary is worse: `add-worker.md:100` forbids running the engine or writing shared state, but `build.md:7` makes `add brief` Build's FIRST verb and `verify.md:9` makes `add run` the only trusted artifact — so an agent that obeys its own boundary produces a plausible diff and no receipt, and the gate later refuses with `R:UNBRIEFED`, a refusal nothing in the agent's context explains. Two of the eight steps in a full beat are correctly forbidden, three are wrongly forbidden, and one — who creates the node — is undefined. Neither file names a single one of the 24 verbs. And Explore, the rung reserved for "do not guess", has no mode in either file, though it has its own guide, its own freeze refusal and its own gate path. Retired 2.x vocabulary rides along: `§3 Scope` and `§4 suite` resolve against the current format to the wrong sections, `Specify` is not a 3.x beat, and `dependencies.allowlist` is a hard MUST NOT naming a thing the engine never materialises and the book lint bans.
beat: done · next: add status

## RULES
<must>
- M1 The roster table's executor column names only agents this package ships, and a guard binds it the way the persona column is already bound.
- M2 The skill names `add-worker` and `add-advisor` where it tells the reader to delegate.
- M3 Each agent file states the verbs it MAY run — the beat verbs its guide requires — and the seam verbs it must NEVER run.
- M4 `freeze`, `gate`, `done`, `milestone-done` and `check` remain forbidden to both agents, and security remains HARD-STOP.
- M5 `add-worker` carries an `explore` mode pointing at the explore phase guide.
- M6 No agent file names a section, beat or artifact the current format does not have.
</must>
<reject>
- R:PHANTOMAGENT a shipped file must never instruct a reader to spawn an agent the package does not ship -> "R:PHANTOMAGENT"
- R:SELFSEAL an agent must never be permitted a verb that marks a human seam -> "R:SELFSEAL"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S2 · the request does not say which verbs are beat verbs; taking the ones the phase guides actually require — `brief`, `run`, `replan`, plus the read-only `status`, `todo`, `locate` -> if wrong an agent is blocked mid-beat again or handed a seam · probe: the permitted set is derived from the phase guides.
- A2 [which] covers: S1 · the request does not say which agents count as shipped; taking the installer's managed roster tree as the authority, since that is what lands on a user's disk -> if wrong the table names something only the maintainer has · probe: the guard reads the shipped roster, not a hand list.
- A3 [who] covers: S2 · the request does not say who creates the node; taking the ORCHESTRATOR, because node creation precedes the beat an agent is spawned for -> if wrong two actors race to create it · probe: the agent file states the node already exists when it is spawned.
- A4 [absent] covers: S1 · the request does not say what an absent specialist means; taking `add-worker` as the always-available executor, with a specialist named only as an optional environment-specific upgrade -> if wrong the table is right for one machine and wrong everywhere else · probe: the default executor ships with the package.
- A5 [order] covers: S2 · the request does not say what happens when a beat verb and a seam verb are both plausible; taking the seam as the stop — an agent that is unsure marks nothing -> if wrong an agent stamps a seam under ambiguity · probe: the boundary is stated as an explicit NEVER list, not as guidance.
- A6 [experience] covers: S2 · the request does not say what the agent needs; taking the verbs named literally in the mode lines, because a cold agent that must infer a verb name will invent one -> if wrong the agent guesses · probe: each mode line names its verbs.
- A7 [who] covers: S1 · n/a · the roster table is read identically by every orchestrator.
- A8 [when] covers: S1 · n/a · a table has no temporal boundary.
- A9 [when] covers: S2 · n/a · the boundary applies for the whole life of a beat.
- A10 [absent] covers: S2 · n/a · a verb absent from both lists is forbidden by default, which A5's stop already states.
- A11 [order] covers: S1 · n/a · the table's rows are independent.
- A12 [experience] covers: S1 · n/a · the table's reader is the orchestrator, served by A6's literalness.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: the roster table's executor column names the shipped roster; a new guard binds it to the installer's roster tree; both agent files gain a MAY/NEVER verb split derived from the phase guides, an `explore` mode, and lose the retired 2.x vocabulary; `agents/` joins the shipped-doc lint.
scope: add-method/skill/add, add-method/agents, add-method/tests

## EDGES
- E1 a user who DOES have a specialist subagent installed — the table must still let them use it, as an upgrade rather than a requirement (A4).
- E2 the four byte-identical roster copies — every edit lands in all tracked twins or parity reds.
- E3 `refute-read`, load-bearing in the worker and banned by the book lint — resolved by defining it in the verify guide or renaming it, never by leaving it undefined.
- E4 the persona service mode, which genuinely writes nothing — its NEVER list stays total.

## CHECKS
- test_the_roster_names_only_shipped_agents · covers: M1, A2, R:PHANTOMAGENT · bound to the installer's roster tree.
- test_the_skill_names_the_shipped_roster · covers: M2 · the delegation text names both agents.
- test_each_agent_states_its_permitted_verbs · covers: M3, A1, A6 · derived from the phase guides, named literally.
- test_the_seam_verbs_stay_forbidden · covers: M4, A5, R:SELFSEAL · the NEVER list is explicit and complete.
- test_the_worker_carries_an_explore_mode · covers: M5 · the mode points at the explore guide.
- test_no_agent_file_names_a_retired_section · covers: M6, E3 · the 2.x vocabulary is gone or defined.
- test_the_agent_files_are_under_the_shipped_doc_lint · covers: M6, E2 · the roster tree is swept.
- test_a_specialist_stays_an_optional_upgrade · covers: A4, E1 · the table permits without requiring.
- test_the_orchestrator_owns_node_creation · covers: A3 · the agent file states the node exists at spawn.
- test_the_persona_mode_writes_nothing · covers: E4 · the service mode's total prohibition is unchanged.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
