# Releases

## 1.11.0 — 2026-06-26
milestones: audit-hardening, engine-modularization
loose tasks: add-check, quickstart-guide, milestone-layer, onboarding-align, question-summary-layer, intake-interview, ubiquitous-language, wave-ledger, wave-status-hint, wave-protocol-runtime, engine-argv-portability, engine-merge-base-enforcement, gitignore-scaffold, autonomy-command, standalone-fast-task, todo-capture, flag-mode-quickref, loose-task-release, soul-seed-npm-parity, gitignore-bak-seed, setup-commit-prompt, ground-phase-harden, lean-tree-baseline-derive, atomic-scope-sidecar, audit-ungated-verdict, test-tempdir-cleanup, scope-level-enum-reconcile
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: suite 1959/0 · audit clean 102 · engine 14-module package; 2 milestones (audit-hardening + engine-modularization) + 27 loose tasks

## 1.10.0 — 2026-06-25
milestones: docs-site, loop-steering, component-aware-add
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: suite 1745/0 · audit clean (74 tasks) · mkdocs --strict clean; bundles component-aware-add + docs-site + loop-steering + ccsk --rule-file

## 1.9.0 — 2026-06-24
milestones: flow-simplification, skill-effectiveness, flow-enforcement, fast-lane
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: suite 1642/0 · check 378/0 · audit clean (74 tasks) · 4 milestones (lean-pass M1 skill-effectiveness + M3 flow-simplification + M4 flow-enforcement + fast-lane)

## 1.8.0 — 2026-06-23
milestones: state-model-reshape, user-identity, ownership-assignment, git-merge-safety, multi-active-UX, delta-resolution-polish
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: suite 1543/0 · check 377/0 · audit clean · 6 milestones

## 1.7.3 — 2026-06-18
milestones: multi-agent-installer
waivers: none
evidence: npm @pilotspace/add@1.7.3 + PyPI pilotspace-add 1.7.3 (post-tag)

## 1.7.2 — 2026-06-18
milestones: installer-smarts-polish
waivers: none
evidence: ADD 1.7.2 — installer-smarts-polish (PTY harness via tooling/pty_clack.py exercises clack select/confirm under a real pseudo-terminal in CI) + SECURITY.md security policy shipped in npm + PyPI; suite 1345 green; tag v1.7.2 triggers npm/PyPI publish

## 1.7.1 — 2026-06-18
milestones: installer-smarts, scope-drafting-quality, verify-expectations, installer-soul-seed
waivers: none
evidence: ADD 1.7.1 — installer-smarts (brand-aware prompts, readiness detection, intent handoff via .add/.intent) + installer-soul-seed (SOUL.md seeded on init/update) + verify-expectations (Build-expectations block in §6 VERIFY) + scope-drafting-quality (scope drafting quality guard); suite 1324 green; tag v1.7.1 triggers npm/PyPI publish

Append-only release ledger (newest-first) — date · version · milestones · waivers · evidence.
A milestone is "released" iff it appears in a row here (membership is the attribution source).
The engine records a row via `add.py release <version>`; the human owns the tag/publish.

## 1.7.0 — 2026-06-18
milestones: delta-resolution, udd-design-loop, decision-suggestions, ship-review, installer-experience
waivers: none
evidence: ADD 1.7.0 — installer-experience (guided/agent-aware/self-healing/global onramp via @clack/prompts + --global/--global-data) + delta-resolution + decision-suggestions + ship-review + udd-design-loop attribution; suite 1266 green; tag v1.7.0 triggers npm/PyPI publish

## 1.6.0 — 2026-06-16
milestones: release-altitude
waivers: none
evidence: ADD 1.6.0 — the RELEASE scope level; suite 1158 green; tag v1.6.0 triggers npm/PyPI publish

## 1.5.0 — 2026-06-16 (pre-ledger baseline)
milestones: v1-1, v1-2, v2, v3, v4-1, v5, v6, v7, v8, v8-1, v9, v9-1, v10, v12, v12-1, v13, v13-1, v14, v15, v16, v17, v18, v19, v20, v21, v22, v23, flag-first-freeze, goal-auto-ready, ground-phase, ground-context, verify-integrity, udd-design-foundation, advisor-context, build-scope-lock, next-step-seams, foundation-compaction, v13-onboarding-polish
waivers: none
evidence: pre-ledger baseline — these 38 milestones shipped via the by-hand release recipe across 1.0.0–1.5.0, before the RELEASES.md ledger existed (see add-method/CHANGELOG.md). This row seeds the ledger so the first `add.py release` cut attributes only new work.
