# MILESTONE: Report hardening

goal: close v13's disclosed residue: declaration grammar stated, declared paths confined, DECIDE NEXT plan-aware
stage: mvp · status: active · created: 2026-06-05

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the three residues v13 itself disclosed at its fold — (1) the `Tests live in:`
     declaration grammar written into the §4 template + phase guide; (2) declared
     test paths confined to the project root (contract v2 of the declared-fallback
     seam, via change-request — the frozen v1 is never edited); (3) DECIDE NEXT
     plan-aware: a "n planned tasks not yet scaffolded" hint sourced from MILESTONE.md.
Out: any other report/engine change; recursive directory globbing or new declaration
     token forms (grammar is STATED, not extended); changes to the frozen decide
     facts key-set {phase, gate, deps, tests} (the hint is additive, outside it);
     enforcement/CI gates (still tracked at v7 MILESTONE); chat-template changes.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Additive evolution (foundation v8): every surface change leaves existing output
  lines, JSON keys, and exit codes unchanged — new lines/keys only.
- The declared-fallback grammar is ONE source of truth: what task 1 writes as prose
  MUST byte-match what `_declared_tests_count` parses; task 2 changes resolution
  (confinement), not the token grammar.
- 3-tree md5 parity (canonical · dogfood · bundled) for every touched artifact.

## Shared / risky contracts (freeze these first)
- declared-path resolution v2 (root-confinement Reject rule) -> owning task declared-path-confinement

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] declare-grammar-doc        depends-on: none — state the `Tests live in:` grammar in TASK.md.tmpl §4 + phases/4-tests.md (prose-guide task; content anchors + parity)
- [x] declared-path-confinement  depends-on: none — contract v2: a token resolving outside the project root counts 0, fail-closed (closes the §6-reviewed read leak)
- [x] decide-planned-hint        depends-on: none — DECIDE NEXT shows "n planned tasks not yet scaffolded" diffed from MILESTONE.md's task list (additive line + additive JSON key)

## Exit criteria (observable; map each to the task that delivers it)
- [x] A reader of TASK.md.tmpl §4 or phases/4-tests.md can write every declaration form the engine parses (tokens · ./ · root-relative · sibling shorthand · dir → non-recursive *.py)  (← declare-grammar-doc)
- [x] A declared token resolving outside the project root contributes 0 tests — no read occurs outside the root  (← declared-path-confinement)
- [x] When MILESTONE.md lists tasks with no TASK.md, the decide digest names the count — and stays byte-identical when none are missing  (← decide-planned-hint)
- [x] All v13 surfaces unchanged where untouched: suite green, 3-tree parity, frozen key-set intact  (← all)
