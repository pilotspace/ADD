# MILESTONE: Installer Experience

goal: stand up or repair ADD for any coding agent through one guided installer — interactive when the terminal allows, agent-aware, self-healing on partial setups, and installable globally or per-project
rationale: new-major — a distribution/onramp theme no active milestone's goal covers (delta-resolution-polish is delta machinery); 5 deliverables too big for one task. Confirmed via intake interview 2026-06-17.
stage: mvp · status: active · created: 2026-06-17

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  · interactive npm installer via @clack/prompts + graceful plain-text fallback
       (non-TTY / CI); pip gets the matching plain-text flow — npm↔pip parity held
       for every non-clack behavior
     · agent detection (Claude Code · Claude app/cowork · Codex · OpenCode · generic
       AGENTS.md fallback) → writes the right integration file + prints THAT agent's
       exact next step
     · heal/reconcile — init AND update scan .add/ for missing/stale managed assets,
       overwrite the managed layer, ADD missing components — never wipes user data
     · global install — engine+book+skill installable to a global ADD home, updated
       once for all projects
     · per-project data — local & git-tracked by DEFAULT; --global-data opt-in
       persists a project's data under the global home keyed by project path
Out: · per-project data in the global home by default (stays opt-in; the
       self-contained / git-tracked invariant holds)
     · auto-running `add.py init` from the installer (still deferred to /add — keeps
       the v12 lock-down gate + the brownfield signal intact)
     · auto-launching / spawning the user's agent (we print/hand a next step, not spawn)
     · a hosted / web / GUI installer; install-time telemetry or network calls

## Shared decisions & glossary deltas   (living — every task must honor these)
- The managed-layer ↔ user-data boundary is sacred: heal/reconcile and global install
  NEVER clobber state.json · PROJECT.md · milestones · tasks · archive.
- Designed-for-failure on every new IO path: clack import → plain text · agent detect
  → generic AGENTS.md · global home unwritable → clear error + local fallback.
- npm↔pip parity: identical behavior except clack richness; both share the managed-layer
  list, the .add-version stamp format, and the heal logic.
- New glossary terms: **global ADD home** (shared engine+book+skill location) ·
  **global-data** (opt-in per-project data under the global home) · **agent profile**
  (detect → integration-file → next-step mapping) · **heal/reconcile** (init/update
  gap-fill that adds missing managed components without wiping user data).

## Shared / risky contracts (freeze these first)
- global-home layout + project-keying + how a local .add/tooling resolves the global
  engine (pointer vs copy)   -> owning task `global-install`   ← riskiest, freeze first
- agent-profile shape {agent_id, detect_signal, integration_files, next_step}
                                                   -> owning task `agent-detect`
- heal manifest: the canonical managed-component list + the missing/stale/present rule
                                                   -> owning task `heal-reconcile`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] installer-prompts  depends-on: none           — @clack/prompts interactive npm flow + plain-text fallback; pip matching flow; parity preserved
- [x] agent-detect       depends-on: none           — detect the coding agent, write its integration file (CLAUDE.md/AGENTS.md), print its exact next step
- [x] heal-reconcile     depends-on: none           — init+update scan .add/, report missing/stale, overwrite managed + add missing, never touch user data
- [x] global-install     depends-on: heal-reconcile — global ADD home; engine+book+skill installed once, updated for all projects
- [x] global-data        depends-on: global-install — --global-data opt-in persists per-project data under the global home keyed by project path

## Exit criteria (observable; map each to the task that delivers it)
- [x] `npx @pilotspace/add` in a TTY shows a guided interactive install; in CI/non-TTY it falls back to plain text with the SAME outcome   (← installer-prompts)
- [x] the installer detects the active agent, writes its integration file, prints its exact next step; unknown agent → generic AGENTS.md   (← agent-detect)
- [x] `init`/`update` on a partial .add/ report what's missing/stale and restore it WITHOUT touching state/PROJECT/tasks   (← heal-reconcile)
- [x] a user installs ADD once to a global home and uses it across projects; `update` there refreshes all   (← global-install)
- [x] `--global-data` persists a project's data under the global home keyed by path; without it, data stays local & git-tracked (default)   (← global-data)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : ENGINE (add.py / state.json / templates) UNTOUCHED — the whole milestone is installer-side; `find_root` is only relied on (the seam that lets a project use any engine). The PACKAGE INSTALLER twins shipped it all: `bin/cli.js` + `src/add_method/_installer.py` (behavioral parity) + `src/add_method/_cli.py` (flag routing) gained the clack interactive flow + plain-text fallback, agent detection + pointer, reconcile/heal, the global home + registry, and the global-data snapshot.
- skill   : UNTOUCHED — SKILL.md / phases/* / guides unchanged. agent-detect writes a transitional CLAUDE.md/AGENTS.md POINTER reusing sync-guidelines' markers (init supersedes it) — installer behavior, not skill content.
- book    : UNTOUCHED — docs/* unchanged this milestone (a distribution/onramp theme; no method chapter required). An installer chapter is a candidate doc-delta, not an exit criterion.

### Cross-task evidence   (one row per task)
- installer-prompts : gate=PASS · clack interactive + EXACT plain-text fallback (parity) · residue=none (the PTY-only clack path is a seeded delta)
- agent-detect      : gate=PASS · tests=16 green (test_agent_detect) · residue=none (interactive agent-SELECT is PTY-only — seeded delta)
- heal-reconcile    : gate=PASS · reconcile restore-missing/refresh-present on init AND update; same-version heal · residue=none
- global-install    : gate=PASS · tests=13 green + INDEPENDENT adversarial review (verdict MERGE-WITH-NITS, 0 blocking; 2 gaps closed pre-gate) · residue=none (concurrency file-lock + registered-path validation seeded)
- global-data       : gate=PASS · tests=11 green · residue=none (RESTORE/sync + prune-data + snapshot symlink-parity seeded)
- FULL SUITE: 1266 green (was ~1206 at milestone start); no security HARD-STOP across any task.

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cited): TTY/plain guided install ← installer-prompts · agent detect→integration-file→next-step ← agent-detect · partial-.add heal without touching user data ← heal-reconcile · install-once-global + update-all ← global-install · `--global-data` keyed persist, default stays local ← global-data.
- goal: "stand up or repair ADD for any coding agent through one guided installer — interactive when the terminal allows, agent-aware, self-healing, global or per-project." PROVEN: one `npx @pilotspace/add` (or `pilotspace-add`) now interviews on a TTY / degrades to plain text in CI, detects the agent + prints its next step, heals a partial `.add/` without touching user data, and installs either per-project (self-contained git-tracked default) or to a shared global home (`--global`) that `update --global` refreshes for every registered project — with `--global-data` persisting per-project data under the home. 1266 green; managed↔user-data boundary held throughout.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from `feat/installer-prompts` → `main` using this Close ship-review as the description; the human reviews + merges (admin merge via the `TinDang97` gh account — `tindangtts` is pull-only).
- [ ] (optional) run a fresh-clone smoke of all four entry paths before merge: `npx . init` (TTY + `--yes`), `init --global --yes`, `update --global`, `init --global-data --yes` — confirm the home + registry + data snapshot land and the per-project default is untouched.
- [ ] bundle into the next release cut per release.md (this milestone joins the held queue — N milestones releasable; the version bump + CHANGELOG + tag/publish are the human-gated release scope, independently CI-gated).
