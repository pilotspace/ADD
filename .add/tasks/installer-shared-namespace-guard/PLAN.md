# TASK: Installer: .claude/agents is a shared namespace — never clean-replace it whole

slug: installer-shared-namespace-guard · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: installer shared-namespace guard — .claude/agents holds the USER's own subagents; ADD's install/update may own only its shipped roster files there, never the directory (bug: clean-replace swept every non-ADD agent as an orphan)
Must:
  - a foreign file in .claude/agents (any name not shipped and not tombstoned) survives init AND update byte-identical, in BOTH installers (npm bin/cli.js + pip _installer.py)
  - shipped roster files still land/refresh (bytes == packaged agents/ copy), each via a per-file temp-sibling + rename (atomic overwrite; dest dir created when missing)
  - upstream-retired roster names are removed ONLY via an explicit tombstone list (empty today) — no heuristic sweep, no prefix-based deletion
  - every other managed tree keeps its whole-dir clean-replace semantics byte-unchanged (orphans there still swept)
Reject:
  - clean-replacing .claude/agents as a whole directory -> "data_loss" (the reported bug — user agents deleted as orphans); never again
  - deleting by name pattern (e.g. add-*.md heuristic) -> forbidden; a user file named add-anything.md survives unless explicitly tombstoned
Accept: Given a project with .claude/agents/my-custom.md and a modified add-verify.md, When cli.js update (and the pip twin) runs, Then my-custom.md is byte-identical, add-verify.md matches the shipped copy, and a docs-tree orphan is still swept.
Boundary: three destination states x two installers — fresh (no .claude/agents: dir created, roster lands) · populated with foreign files (all survive) · a tombstoned name present (removed)
Assumptions: ⚠ no OTHER code path clean-replaces .claude/agents outside the MANAGED-table loops (heal/reconcile/global restore route through the same helpers) — why: grep shows :690/:1466 (py) + dropFiles/update (js) as the call sites; if wrong: the fence names it, the same shared-branch applies there (cost: one more call site)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/bin/cli.js:MANAGED (:755 agents row) + cleanReplaceTree call sites (dropFiles + update loop) · add-method/src/add_method/_installer.py:MANAGED (:35) + _clean_replace call sites (:690, :1466) · NEW sharedFileReplace (js) / _shared_file_replace (py)
Context (working folder): npm<->pip parity comments bind the twins ("Mirror of _installer.py:_clean_replace"); this repo's own .claude/agents is dogfood evidence (roster + the user's 12+ own agents)
Honors (patterns / conventions): per-file temp-sibling + rename (the cleanReplaceTree staging idiom, applied per file) · design-for-failure (a crashed landing leaves dest valid) · explicit-tombstone-over-heuristic (the delta-evidence discipline) · Seams consulted: .add/SEAMS.md
Anchors the contract cites: MANAGED · cleanReplaceTree · _clean_replace
Ground SHA: e2cde5c — stamped by freeze

### Contract

```
SHARED namespace set (both installers; today exactly {"agents"}):
  a MANAGED tree whose destination is a directory OTHER TOOLS also write.
  install/update routes it to the per-file lander instead of the dir swap:

js:  sharedFileReplace(src, dest)  -> {restored, refreshed}
py:  _shared_file_replace(src, dest) -> {"restored": n, "refreshed": n}
  - mkdir dest if missing
  - per shipped file: copy to dest/<name>.add-tmp-* then rename onto
    dest/<name> (atomic overwrite; refreshed if it existed, restored if not)
  - remove ONLY names in RETIRED_AGENTS / _RETIRED_AGENTS (explicit list,
    empty today); every other destination file is never opened
non-shared MANAGED trees: cleanReplaceTree/_clean_replace UNCHANGED
```

`Least-sure flag surfaced at freeze:` [contract] the update path may report per-tree file counts a fixed harness test pins (restored/refreshed roll-up shape) — why: cleanReplaceTree's return is consumed by reporting code I haven't fully traced; if wrong: the shared lander returns the same {restored, refreshed} shape so the consumer is agnostic (cost: small re-read, no shape change)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/`
Strategy & known-problem fixes: 1) red test_installer_shared_namespace.py (subprocess fixtures mirroring test_installer_handoff) 2) py _shared_file_replace + route :690/:1466 3) js sharedFileReplace + route dropFiles/update 4) parity comments updated 5) fence; traps: BOTH init and update paths must route (two call sites in py) · the .claude/skills/add dest is already namespaced (NOT shared — do not touch) · keep {restored, refreshed} roll-up shape for the reporting consumer
Approach (domain strategy): ownership-scoped writes in shared namespaces — per-file atomic rename, explicit tombstones over heuristics, correctness-first

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_installer_shared_namespace.py — foreign-file survival through init+update x both installers (subprocess, scrubbed env) · roster files land/refresh to shipped bytes · fresh dir created · tombstone mechanism removes a listed name (py unit-level with an injected list) · a non-shared tree (docs) still sweeps an orphan · user file named add-custom.md survives (no prefix heuristic).
Tests live in: `add-method/tooling/test_installer_shared_namespace.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — _SHARED/_RETIRED_AGENTS + _shared_file_replace routed in _reconcile (py; init AND update both funnel through it), SHARED/RETIRED_AGENTS + sharedFileReplace routed in reconcile (js); GLOBAL_TREES excludes agents in both so no other call site; roll-up shape kept
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): after update, .claude/agents contains the user's files byte-identical + the shipped roster refreshed, while .add/docs orphans are still swept — confirmed by test_installer_shared_namespace.py + the full fence

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14
[SPEC · open] `update --global` propagation never refreshes the roster: agents are absent from _GLOBAL_TREES/GLOBAL_TREES, so the home mirror soft-skips them — user agents SAFE (verified live: my-precious.md survived, stale add-verify.md kept its local edit), but a roster refresh needs a project-level `update`. Candidate follow-up: add agents to the global mirror, routed through the shared lander. Also observed: the opt-in --global-data snapshot excludes .claude/agents (a MANAGED dest), so user agents are not backed up by it. (evidence: global-audit live run 2026-07-14)

