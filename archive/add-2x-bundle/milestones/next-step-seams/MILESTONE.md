# MILESTONE: Next Step Seams

goal: after every mutating engine verb both the human and the AI see the engine-sourced next step and who drives it — next: footer plus [you drive] / [human gate] marker
rationale: sub-milestone of the developer-experience theme (human-confirmed intake 2026-06-11) — today the resume point lives only in status/guide; after any mutating verb the driver must re-orient manually, and nothing names WHO acts next
stage: mvp · status: active · created: 2026-06-12

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  an engine-sourced `next:` footer after every MUTATING verb (single resolution source — the guide resolver); a driver marker `[you drive]` vs `[human gate]` derived from autonomy × phase; the two stale v20 UX follow-ups (milestone-done hint line · placeholder goal on fresh init)
Out: interactive `guide` · colorized/rich output · notification hooks · footers on read-only verbs (status/check/report already orient)

## Shared decisions & glossary deltas   (living — every task must honor these)
- ONE resolver: the footer reuses the guide resolution path — no duplicated next-step logic, no second source of truth
- no double-printing: a verb that already emits a next-step hint (precedent cmd_status) converges onto the footer, never prints both
- the driver marker derives from recorded state (autonomy level + phase + gate), never from prose

## Shared / risky contracts (freeze these first)
- the footer line grammar (`next: <command> — <why> [you drive|human gate]`, render-blind testable) -> owning task next-footer-engine

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] next-footer-engine     depends-on: none                — mutating verbs print an engine-sourced `next:` footer; one resolver, no duplicated logic
- [x] gate-owner-marker      depends-on: next-footer-engine  — the footer + guide name the driver: [you drive] vs [human gate] from autonomy × phase
- [x] ux-stale-followups     depends-on: none                — fold the v20 leftovers: milestone-done hint line + placeholder goal on fresh init

## Exit criteria (observable; map each to the task that delivers it)
- [x] Every mutating verb ends with exactly one engine-sourced `next:` line               (← next-footer-engine)
- [x] Under conservative/manual the footer names the human; under auto it names the AI    (← gate-owner-marker)
- [x] The two v20 UX follow-ups are closed and their stale notes removed                  (← ux-stale-followups)
