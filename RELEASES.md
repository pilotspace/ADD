# Releases

## 1.18.0 — 2026-07-07
milestones: delta-drain, build-strategy-facets
loose tasks: none
waivers: reclaim-ticket-race, js-reclaim-lock-heartbeat
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: test_release_1_18_0.py 11/11 green · add.py check green · milestones build-strategy-facets(#139) + delta-drain(#140) merged to main

## 1.17.0 — 2026-07-07
milestones: persona-domain-fit, method-ergonomics, dynamic-personas, self-improving-loop
loose tasks: grep-binary-agnostic-milestone-test, prune-data-update-lock, sweep-orphan-reclaim-tickets, adr-harvester-multiline-fields, strip-scaffold-backtick-comment-fix, worktree-isolated-spawn-default, fold-glossary-deltas, reclaim-ticket-race, js-reclaim-lock-heartbeat, scope-components-check, fastlane-intake-nudge, persona-required-domain-hint
waivers: reclaim-ticket-race, js-reclaim-lock-heartbeat
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: recorded by add.py release; amended (unpublished — no tag cut yet) to attribute dynamic-personas (2/2 tasks, flow: routing + load performance) and self-improving-loop (3/3 tasks, fold persona sections + loop surfacing nudges + self-improve.md) merged via PR #137 after the initial cut; PRs #135 (method-ergonomics + persona-domain-fit), #136 (release cut), #137 all merged to main; suite/check green throughout, no HARD-STOP

## 1.16.1 — 2026-07-04
milestones: none
loose tasks: persona-seed-nudge
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: ADD 1.16.1 — persona-loop hotfix (project-scoped seed nudge PR #132 + flow/abilities persona-schema template PR #133); no engine-validation change; full suite green; 1 open SPEC delta rides unresolved (rule-id-coverage's grandfathered-dialect question, owned by an archived milestone task carry-delta can't reach — unrelated to this patch's scope); tag v1.16.1 triggers npm/PyPI publish

## 1.16.0 — 2026-07-03
milestones: install-update-hardening
loose tasks: none
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: 1 milestone (install-update-hardening — 4/4 tasks gate=PASS, 1167+ combined adversarial concurrency attempts / 0 anomalies, independent verify + advisor 3-lens on every task, human-reviewed for the risk:high task); PR #129 merged 2eeb008 (66 commits); CI 9/9 green; check 513/0 (65 warn, routine); zero HARD-STOP / RISK-ACCEPTED across 116 tasks

## 1.15.0 — 2026-07-03
milestones: seams, context-search, drift-guard, artifact-graph, ground-trust, traceability-ids, persona-teacher-bundle, persona-learning-loop, advisor-gated-autonomy, portable-roster, loop-readability
loose tasks: scope-exclude-claude, mirror-resync, untrack-add-tooling, installer-gitignore-mirrors, ci-tooling-mirror-gap, phase-agents-lean, gitignore-vendor-path-fix, update-global-gitignore-seed, nested-suite-skip-count-tolerance, report-plan-approve, status-pagination, skill-tree-compaction-audit, add-advisor
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: 11 milestones (seams + context-search + drift-guard + artifact-graph + ground-trust + traceability-ids + persona-teacher-bundle + persona-learning-loop + advisor-gated-autonomy + portable-roster + loop-readability) + 13 loose tasks since 1.14.0; targeted suites green (report-shape-scan-audit 7/7, skill-banner-cue 5/5, uiux-hint-adoption 17/17, release-1.15.0 forward-pin 11/11); check 506/0 (58 warn); foundation-version 62; 7 open SPEC delta(s) ridden forward unresolved --force (unchanged carry from the original 1.15.0 cut, all from permanently-live loose tasks: add-advisor x2, gitignore-vendor-path-fix, nested-suite-skip-count-tolerance, skill-tree-compaction-audit x2, update-global-gitignore-seed; 18 further deltas exist project-wide but belong to the still-active install-update-hardening milestone, not this bundle — see add.py deltas)

## 1.14.0 — 2026-06-29
milestones: component-polish, installer-polish
loose tasks: none
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: 2 milestones (component-polish + installer-polish); suite 2279/0; engine pins unchanged (installer/validator only); PR #114 merged a8bad226; independent pre-merge review MERGE-SAFE

## 1.13.0 — 2026-06-28
milestones: adr-at-observe, flow-honesty
loose tasks: skill-todo-flag, build-strategy-solutions, streams-strategy-pull, strategy-soft-not-hard
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: 2 milestones (adr-at-observe + flow-honesty) + 4 loose tasks since 1.12.0 + npm Trusted Publishing (OIDC) migration; suite 2173/0; ENGINE_MD5 9d73e5abb8f0536c9192234efc7ba053

## 1.12.0 — 2026-06-26
milestones: udd-design-intake, multi-milestone-intake, multi-active-polish
loose tasks: milestone-naming, queued-await-confirm-hint, freeze-actor-stamp, flow-jit-tasks-doc
waivers: none
actor: Tin Dang <tindang.ht97@gmail.com> (git)
evidence: 3 milestones (udd-design-intake + multi-milestone-intake + multi-active-polish) + 4 loose tasks since 1.11.0; suite 2063/0; ENGINE_MD5 0d03e178

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
