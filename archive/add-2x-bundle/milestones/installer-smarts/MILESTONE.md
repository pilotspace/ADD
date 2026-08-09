# MILESTONE: Smart onboarding installer

goal: On first run in a real terminal, add init onboards the user (brand, feature showcase, readiness, global-first scope, optional intent handoff to /add) instead of a silent file-drop; non-interactive/CI stays byte-identical.
rationale: sub-milestone — a slice of the already-shipped installer & onboarding theme (the 1.7.0 headline), too big for one task. Forward evolution of the interactive path; the frozen non-interactive byte-identical guarantee is preserved, so it is NOT a change-request.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Branded ADD logo + fuller feature showcase (value paragraph + the 7-step
     Specify→Observe loop), interactive path ONLY with a plain non-unicode/no-color
     fallback within that path; a readiness pre-flight line (git · python3 · detected
     agent); smarter agent detection (env + installed-CLI probe + existing
     CLAUDE.md/AGENTS.md, still degrading to generic + overridable); a global-first
     scope step (▶ recommended, EXPLICIT pick, writes HOME only on pick); an optional
     one-line build-intent captured to `.add/.intent` that /add reads. Both twins
     (bin/cli.js + src/add_method/_installer.py) kept in parity (same decisions).
Out: No change to non-interactive/CI output (byte-identical pin holds); no `add.py
     init` run from the installer (deferred-init / v12-lock invariant); no new
     dependency beyond @clack/prompts (pip stays stdlib input()); no TUI framework /
     color-theme engine (logo is static ASCII); no change to update / global-home /
     global-data mechanics (only the interactive prompt that toggles --global); no
     engine (add.py) edits (md5 pin holds); logo WORDMARK CONTENT decided with the
     human in specify (identity-owned), not pre-baked.

## Shared decisions & glossary deltas   (living — every task must honor these)
- onboarding interview — the interactive-only sequence the installer runs on a real TTY.
- byte-identical boundary — the non-interactive/CI output stays byte-for-byte as today;
  every new affordance rides the interactive path only.
- intent note — `.add/.intent`, a handoff file (NOT state.json) consumed by /add; writing
  it never implies `add.py init`.
- both twins stay decision-equivalent; rendering may differ (clack vs stdlib input()).

## Shared / risky contracts (freeze these first)
- non-interactive byte-identical boundary (what prints interactive vs not) -> owning task onboarding-brand
- intent-note shape + location (`.add/.intent` schema + how /add consumes it) -> owning task intent-handoff

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] onboarding-brand      depends-on: none              — Logo + fuller feature showcase, interactive-only + plain fallback; sets the byte-identical boundary contract.
- [x] readiness-and-detect  depends-on: onboarding-brand  — Readiness line (git/python3) + smarter agent detection (env + CLI + integration-file).
- [x] global-first-scope    depends-on: onboarding-brand  — Scope step: ▶ global recommended, explicit pick, CI never auto-global.
- [x] intent-handoff        depends-on: onboarding-brand  — Capture one-line intent → `.add/.intent`; /add reads it; never runs init.

## Exit criteria (observable; map each to the task that delivers it)
- [x] A TTY run prints the logo + feature showcase before the first prompt; a piped/CI run is byte-identical to today's baseline   (← onboarding-brand)
- [x] The interactive flow shows a readiness line (git · python3 · agent), and detection also recognizes an installed CLI / existing CLAUDE.md/AGENTS.md, still degrading to generic   (← readiness-and-detect)
- [x] The scope step offers global as the ▶ explicit pick; choosing installs the home, declining stays local, CI never goes global   (← global-first-scope)
- [x] An answered intent writes `.add/.intent` and the handoff names it for /add; no state.json is created by the installer   (← intent-handoff)
- [x] Both twins stay in parity and the engine md5 pin holds   (← all tasks; guarded by test_installer_prompts / test_agent_detect)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- installer (bin/cli.js + src/add_method/_installer.py) : the interactive onboarding — ADD brand + 7-step showcase (caps-aware ASCII fallback) · readiness pre-flight line (git · python3 · agent) · enriched agent detection (env > CLAUDE.md > installed-CLI, interactive default only; non-interactive write stays env-only) · global-first scope step (▶ recommended, explicit pick, CI never auto-global, strictly additive) · optional `.add/.intent` build-intent note. All interactive-only; the non-interactive/CI path is byte-identical. npm got `require.main` guard + exports (detectAgent/detectAgentEnriched/readinessLine/whichSync/scopeOptions/writeIntentNote) for the hermetic harness.
- tooling : add.py UNTOUCHED — ENGINE_MD5 pin green across all 3 trees.
- skill   : SKILL.md (×3, md5-equal) — autonomous-setup now reads `.add/.intent` (if present) as the kickoff seed, a NOTE never an init trigger.
- book    : docs/* untouched.
- tests   : suite 1276 → 1319 (+43) — test_onboarding_brand (10) · test_readiness_detect (14) · test_global_scope (8) · test_intent_handoff (11); all hermetic (pip in-process / npm node-harness + subprocess; clack happy-path PTY-manual per convention).

### Cross-task evidence   (one row per task)
- onboarding-brand     : gate=PASS · tests=+10 · residue=none (banner + showcase + ASCII fallback live-smoked)
- readiness-and-detect : gate=PASS · tests=+14 · residue=none (env-only detector + byte-identical boundary pins held)
- global-first-scope   : gate=PASS · tests=+8  · residue=3 sibling pip-interactive tests took 1 navigation stdin line ("n"=project-only) — human-confirmed at the gate, no assertion/pin weakened
- intent-handoff       : gate=PASS · tests=+11 · residue=test_global_scope `_Script` made EOF-tolerant for the new optional prompt (robustness, not weakening); deferred-init invariant preserved + newly pinned (no state.json)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which): EC1←onboarding-brand (installer row) · EC2←readiness-and-detect · EC3←global-first-scope · EC4←intent-handoff (`.add/.intent` + no state.json) · EC5←all tasks (ENGINE_MD5 + parity pins green in the +43 tests)
- goal: On first run in a real terminal, `add init` now onboards (brand · showcase · readiness · global-first scope · optional intent→/add) instead of a silent drop, while non-interactive/CI stays byte-identical — proven by the live smoke (both twins render the full interactive flow) + the 1319-green suite holding the byte-identical-boundary, ENGINE_MD5, and deferred-init pins.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit the milestone (4 task TASK.md + this MILESTONE.md + the twins + SKILL.md ×3 + the 4 new test files) on a feature branch — the prior method-quality milestones are still uncommitted, so stage deliberately
- [ ] open a PR from the Close ship-review above; the human (TinDang97 admin) reviews + merges to main; CI must be green (setup-node + npm ci for the @clack runtime dep)
- [ ] fold confirmed deltas (`add.py fold`) + (optional) archive the milestone
- [ ] bundle into the next release (`release.md`): this is the 2nd milestone closed since 1.7.0 — cut a MINOR (installer onboarding is user-facing); human runs the tag/publish (npm + PyPI), publish.yml guard re-runs the suite
