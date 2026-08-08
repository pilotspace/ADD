# TASK: AGENTS.md routing for non-Claude agents via the CLI

slug: agent-portability · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: any agent (Cursor · Copilot · Codex · Claude) can locate and follow the
  correct phase guide starting from AGENTS.md alone, through the CLI (v14 exit
  criterion 4) — today the block routes to a Claude-only skill, and `guide`
  names the book chapter but never the phase PLAYBOOK
Framings weighed: CLI-named guide path + agent-agnostic block (chosen: the
  installers — npm cli.js and the pip mirror — already place the phase guides at
  `.claude/skills/add/phases/` in EVERY consumer project; they are plain
  markdown any agent can read; the only missing links are (a) the engine naming
  the right file and (b) the block telling any agent the loop) · duplicate the
  guides into .add/ (rejected: a second copy rots; the ×3 parity discipline
  already guards ONE canonical location) · embed phase instructions in the
  block (rejected: dynamic-by-reference is the block's whole design — ETH-Zurich
  note; live state in context files measurably hurts)
Must:
  - `add.py guide [slug]` (text) gains a `guide  :` line naming the phase-guide
    file for the task's phase — `.claude/skills/add/phases/<n>-<phase>.md` —
    printed only when that file EXISTS at the project root (never a dead
    pointer); when the skill tree is missing, print an install hint instead.
    `done` phase: no guide line (the `then:` already routes to the next feature).
  - `add.py guide --json` gains ADDITIVE key `"guide"`: the path string, or null
    (missing file / done / no active task). The frozen v1 keys
    {task, phase, owner, stop, next_step, chapter, gate} are untouched
    (test_machine_state pins by subset — additive-safe, same as planned_hint).
  - `_guideline_block()` rewritten agent-agnostic: ANY agent follows
    status → guide → read the named phase guide → work ONLY that phase →
    advance / gate. The three non-negotiables stay in the block (never weaken a
    test or edit a frozen contract · ONE human approval at the freeze ·
    security always escalates). One sentence notes that on Claude the `add`
    skill automates this loop. PINNED anchors kept byte-stable for
    test_guidelines: the heading "## ADD — how to work in this repo",
    "add.py status", "PROJECT.md", both markers.
  - Dogfood refresh: `sync-guidelines` re-run so AGENTS.md + CLAUDE.md carry the
    new block. Engine synced ×3.
Reject:
  - skill tree missing (consumer skipped the installer) -> guide prints
    "phase guides not installed" hint, NEVER a path to a nonexistent file
  - corrupted/unknown phase -> existing fail-clean behavior unchanged
After:
  - starting from AGENTS.md alone, a non-Claude agent reaches the exact phase
    guide for the active task by running the two commands the block names —
    proven by a protocol-walk test that does exactly that and only that
Assumptions — least-sure first:
  ⚠ [spec] the phase-guide location is `.claude/skills/add/phases/` in ALL
    install channels — confirmed for npm (cli.js line 66-69) and the dogfood
    repo; least sure for the pip channel (the bundle mirrors the same tree, but
    if its installer ever diverges the printed path goes stale); if wrong: the
    exists-check fails closed to the install hint, never a dead pointer
  - [x] guide --json key-set is subset-pinned, not exact-pinned — confirmed
    (test_machine_state asserts membership)
  - [x] test_guidelines pins only generic anchors — confirmed (markers ·
    heading · add.py status · PROJECT.md)

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: guide names the phase playbook when installed
  Given a project whose .claude/skills/add/phases/ tree exists
  And the active task is at any working phase (specify…observe)
  When `add.py guide` runs
  Then a `guide  :` line names .claude/skills/add/phases/<n>-<phase>.md
  And that file exists

Scenario: never a dead pointer
  Given the same project WITHOUT the skill tree
  When guide runs
  Then it prints an install hint and no path to a nonexistent file

Scenario: JSON twin carries the same fact additively
  Given the installed project at phase tests
  When `add.py guide --json` runs
  Then "guide" equals the 4-tests.md path and all seven frozen v1 keys remain

Scenario: the block routes any agent
  Given a fresh project after `sync-guidelines`
  When AGENTS.md (and CLAUDE.md) are read
  Then the block names the status and guide commands, the read-the-named-guide
       loop, and the three non-negotiables — with no Claude-only dependency in
       the routing steps

Scenario: protocol walk — the exit criterion, executed
  Given a project with the skill tree installed and a task at specify
  When an agent does ONLY what AGENTS.md says: run status, run guide, open the
       file the guide line names
  Then the opened file is the Specify phase guide (its heading confirms it)

Scenario: done phase has no playbook pointer
  Given the active task is done
  When guide runs
  Then no guide line is printed and JSON "guide" is null
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py guide [slug]            (text — additive line)
  phase in specify…observe AND .claude/skills/add/phases/<n>-<phase>.md exists
    -> "guide  : .claude/skills/add/phases/<n>-<phase>.md"
  tree missing -> "guide  : (phase guides not installed — npx @pilotspace/add init)"
  done / no active task -> no guide line
add.py guide --json            (additive key)
  "guide": "<path>" | null     · frozen v1 keys untouched
PHASE -> FILE (all working phases):
  specify→1-specify.md scenarios→2-scenarios.md contract→3-contract.md
  tests→4-tests.md build→5-build.md verify→6-verify.md observe→7-observe.md
_guideline_block() (sync-guidelines, AGENTS.md + CLAUDE.md):
  agent-agnostic loop: status → guide → READ THE NAMED FILE → work that phase
  only → advance | gate · three non-negotiables · one Claude-skill aside
  KEPT anchors: "## ADD — how to work in this repo" · "add.py status" ·
  "PROJECT.md" · _GUIDE_BEGIN/_GUIDE_END markers
GUARD: add-method/tooling/test_agent_portability.py — per-phase mapping loop ·
dead-pointer rejection · JSON twin · block anchors · PROTOCOL WALK (the exit
criterion executed literally). Engine ×3; dogfood AGENTS.md/CLAUDE.md resynced.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion; ⚠ install-channel path + dynamic-by-reference flags surfaced and accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has a test; suite stays green elsewhere
(block rewrite keeps test_guidelines' pinned anchors).
Plan (one test per scenario, asserting behavior not internals):
  - test_guide_names_playbook_per_phase: install fake phases tree in fixture,
    loop all 7 working phases / assert the `guide  :` path per phase + file
    exists (RED: no guide line)
  - test_no_dead_pointer_without_tree: no tree / assert hint, assert no
    ".claude/skills" path printed (RED)
  - test_json_guide_key_additive: tree present, phase tests -> "guide" path;
    seven frozen keys still present; tree absent -> null (RED)
  - test_done_phase_no_pointer: done task -> no guide line, JSON null (RED)
  - test_block_routes_any_agent: sync-guidelines fixture -> block names status,
    guide, the read-the-named-file loop, three non-negotiables, in BOTH
    AGENTS.md and CLAUDE.md (RED: old block)
  - test_protocol_walk_from_agents_md: the exit criterion executed — parse
    AGENTS.md for the two commands, run them, open the named file, assert it is
    the phase guide for the active phase by heading (RED)
  - guards: guide purity (state byte-identical, existing test_guide pattern);
    ×3 engine parity ride-along

Tests live in: `add-method/tooling/test_agent_portability.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): never print a path that does not exist (the
exists-check is the rule); the block stays dynamic-by-reference — no live state
(slug/phase/gate) ever embedded in AGENTS.md/CLAUDE.md.
Code lives in: `add-method/tooling/add.py` (cmd_guide + _guideline_block + mapping) · synced ×3 · dogfood AGENTS.md/CLAUDE.md via sync-guidelines
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 420/420 OK (was 413; +7 in test_agent_portability.py,
      incl. the protocol-walk exit-criterion proof)
- [x] coverage did not decrease — 6 red→green + 1 green-by-design purity guard;
      check 204/0 (4 pre-existing warnings)
- [x] no test or contract was altered during build — the two mid-build reds were
      PRE-EXISTING v8 guards (block ≤22 lines · no manual gate framing) satisfied
      by reshaping the BUILD output (block condensed + phrase reflowed); no test
      file touched after red, §3 contract untouched
- [x] concurrency / timing of the risky operation is safe — guide stays strictly
      read-only (state byte-identical, asserted); the exists-check is a single
      stat, no TOCTOU consequence (worst case: a printed path deleted mid-read
      fails loudly at open, never silently)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure
      stdlib path computation + static prose; no new dependency; the printed path
      is derived from a fixed mapping, never from user input
- [x] layering & dependencies follow CONVENTIONS.md — engine ×3 (md5
      ccb0aa1589c09d3238d7e7fbca1e0240); dynamic-by-reference preserved (no live
      state in the block); dogfood AGENTS.md/CLAUDE.md resynced
- [x] outcome recorded — auto-resolved under autonomy: auto (evidence complete ·
      loops dry · NO residue: security clean, no notes, nothing weakened); the
      live dogfood walk landed on the real Build playbook

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence)
Reviewed by: auto-gate under autonomy: auto — run: agent-portability build→verify,
  accountable owner this session · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a real non-Claude agent run (Cursor/Codex)
following the block end-to-end — does step 3 suffice without the skill?; the pip
channel's install layout staying at .claude/skills/add/phases/ (⚠ accepted at
freeze — fails closed to the hint); whether the install hint converts (consumers
running init after seeing it).
Spec delta for the next loop: v14 exit criterion 4 CLOSED by the protocol-walk
proof; review-checklist (next) rides the same freeze seam the block now names.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [TDD · folded] when a feature's exit criterion is a USER JOURNEY, write the
    protocol-walk test that executes the journey literally (parse the entry
    artifact for its instructions, run them, assert the destination) — it pins
    the criterion itself, not a proxy (evidence: test_protocol_walk_from_agents_md)
  - [SDD · folded] prose artifacts accrete PROPERTY guards across milestones (v8:
    ≤22 lines, no manual framing; v14: any-agent routing) — before rewriting one,
    grep its guards and design to the UNION, or the rewrite red-flags late
    (evidence: block rewrite tripped two v8 pins mid-build, satisfied by
    reshaping output)
