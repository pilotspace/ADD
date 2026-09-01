---
type: Task
title: What one installer twin lands, the other lands, and Claude Code can see it
status: direction
depth: standard
sensitivity: architecture
milestone: roster-reachable
scope:
  - add-method/src/add_method/_installer.py
  - add-method/bin/cli.js
  - add-method/tests
gives:
  - S1 the global-install tree set — which trees a `--global` install and refresh carry, in both twins
  - S2 the roster's host-visible landing path — where a global install puts the agents
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:87b9c99cca01209e" }
---
## CARD
goal: The Python and JavaScript installers carry the same set of global trees, a parity check proves it, and a global install lands the roster where the host agent can discover it.
why: `_installer.py:566-574` lists four global trees; `bin/cli.js:946-953` lists five. `personas-index` is in the JS set and absent from the Python one, while being MANAGED and OPTIONAL in both — and MANAGED propagation is sourced FROM the home, so a tree absent from the home is soft-skipped forever. pip users who run a global update therefore never receive a refreshed persona routing index in any registered project; npm users do. The divergence is silent, one-sided and invisible precisely because the tree is optional. The comment sitting beside the `agents` entry records that this exact bug already happened once to the roster and was fixed for it alone. Separately, a global install deploys only the SKILL into a host-discoverable location: the roster stops at `<home>/agents`, verified on this machine — `~/.add/agents/` exists and `~/.claude/agents/` contains neither `add-worker.md` nor `add-advisor.md`. A user who installs globally and works in a project they never initialised gets a discoverable skill and an undiscoverable roster, and nothing surfaces the mismatch.
beat: direction · next: add freeze installer-reach-parity

## RULES
<must>
- M1 The Python and JavaScript global tree sets are equal, member for member.
- M2 A test asserts that equality by reading BOTH twins, and fails when either grows an entry the other lacks.
- M3 A global install deploys the roster into the host-discoverable agents location, through the same replace path the project install already uses.
- M4 The deployment is idempotent and removes a retired agent the way the project install does.
- M5 An optional tree that is genuinely absent from the package still soft-skips rather than failing the install.
</must>
<reject>
- R:TWINDRIFT one installer twin must never carry a tree the other silently lacks -> "R:TWINDRIFT"
- R:UNREACHABLEROSTER a global install must never land the roster where the host cannot discover it -> "R:UNREACHABLEROSTER"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S1 · the request does not say which twin is authoritative; taking the UNION as the target and the equality as the invariant, because each twin's list was written deliberately and neither is a copy of the other -> if wrong a deliberate entry is deleted to satisfy a check · probe: no existing entry is removed from either twin.
- A2 [who] covers: S2 · the request does not say whose home receives the roster; taking the invoking user's host config directory, the same one the skill already lands in -> if wrong a multi-user machine crosses installs · probe: the roster lands beside the skill, in the same resolved directory.
- A3 [when] covers: S2 · the request does not say when the roster is refreshed; taking every global install and every global update, matching the skill's own cadence -> if wrong the roster goes stale while the skill moves · probe: an update refreshes the roster.
- A4 [absent] covers: S1 · the request does not say what an absent optional tree means; taking the incumbent soft skip -> if wrong a lean package fails to install · probe: a package built without the corpus still installs globally.
- A5 [absent] covers: S2 · the request does not say what an absent host config directory means; taking creation, as the skill path already does -> if wrong a first-ever install fails · probe: a machine with no host config directory still receives both.
- A6 [order] covers: S2 · the request does not say the order of skill and roster deployment; taking trees first then host deployment, matching the incumbent flow -> if wrong a partial home is deployed · probe: host deployment reads a fully reconciled home.
- A7 [experience] covers: S2 · the request does not say what the installer should report; taking one line naming the roster and where it landed, because an invisible deployment is what produced this defect -> if wrong the user cannot tell whether it worked · probe: the install output names the roster path.
- A8 [who] covers: S1 · n/a · the tree set is a static declaration taking no actor.
- A9 [when] covers: S1 · n/a · the set is evaluated once per install.
- A10 [order] covers: S1 · n/a · trees are reconciled independently.
- A11 [experience] covers: S1 · n/a · the tree set prints nothing of its own; A7 carries the reporting.
- A12 [which] covers: S2 · n/a · A1 fixes the set; the landing path applies to the roster tree alone.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `personas-index` joins the Python global tree set; a twin-parity test reads both declarations and asserts equality; the global install deploys the roster to the host agents directory through the existing shared-file replace path and names it in its output.
scope: add-method/src/add_method/_installer.py, add-method/bin/cli.js, add-method/tests

## EDGES
- E1 a package built without the optional corpus or index — soft skip, install succeeds (A4, M5).
- E2 a machine with no host config directory — created (A5).
- E3 a retired agent file present in the host directory from an older release — removed by the idempotent replace (M4).
- E4 a second global install over the first — idempotent, no duplication (M4).
- E5 the parity test itself — it must read the twins' declarations rather than restate them, or it rots on the next entry.

## CHECKS
- test_the_global_tree_sets_are_equal · covers: M1, M2, R:TWINDRIFT · both declarations parsed and compared.
- test_the_parity_test_reads_both_twins · covers: E5, A1 · no restated list.
- test_no_existing_tree_entry_is_removed · covers: A1 · the union is the target.
- test_a_global_install_lands_the_roster_where_the_host_looks · covers: M3, A2, R:UNREACHABLEROSTER · the roster sits beside the skill.
- test_a_global_update_refreshes_the_roster · covers: A3 · the roster moves with the skill.
- test_the_install_names_the_roster_path · covers: A7 · the output reports it.
- test_a_lean_package_still_installs · covers: M5, A4, E1 · optional trees soft-skip.
- test_a_missing_host_directory_is_created · covers: A5, E2 · a first-ever install succeeds.
- test_a_retired_agent_is_removed · covers: M4, E3 · the replace tombstones it.
- test_a_second_install_is_idempotent · covers: M4, E4, A6 · no duplication, fully reconciled home.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
