# MILESTONE: Call Residuals

goal: Close the measured WM1 call-count gap (20.7 -> <=12) by killing the four message-layer residuals the six-phase re-measure anatomized: double init · post-freeze re-cross repairs · status re-reads · the --help habit — zero enforcement-path changes
rationale: sub-milestone — human decision 2026-07-14 'Close + draft follow-on milestone' at six-phase-loop close; the re-measure proved the calls bar is reachable (~11-12) through ergonomics, not phase surgery (benchmark/results/2026-07-sixphase-remeasure.md)
stage: mvp · status: active · created: 2026-07-14T04:33:38+00:00
release: pending
relations: <cross-MILESTONE edges — add header lines `depends-on:` / `extends:` / `relates-to:` with milestone slugs (comma-sep); omit if none. Non-blocking except depends-on; validated by `add.py check`>

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Ground (current assets this builds on)
- six-phase-loop MERGED (PRs #146/#149/#148): 6-phase lifecycle, compound ticks, bundle-disclosed guides, build-entry spec echo; WM1 re-measure sixphase-r{1,2,3}: fid 0.98x3 / 0 regr / $3.17 mean / calls 20.7 UNMET vs <=12.
- Waste anatomy per rep (the four levers, ~8-10 calls): double init+lock (r1: init x2 lock x2, r3: init x2) - re-cross scope repairs (r2 x3, r3 x1) - status re-reads (3-4/rep) - exactly one --help/rep.
- Precedent: skip-error-ergonomics proved message-layer-only tasks cut -24% turns/-34% cost with zero enforcement changes.

## Scope
IN: init idempotence messaging (existing project -> loud resume pointer, no re-init) - scope first-draft quality at freeze (kill the post-freeze re-cross class) - status/orientation diet (resume without re-reads) - --help habit kill (quick-ref in the error/skill surface).
OUT: any gate/freeze/tamper/scope ENFORCEMENT change - phase-list changes - roster changes - benchmark harness changes.

## Tasks (breadth-first)
- [ ] init-idempotent-nudge   depends-on: none — `init` on an already-initialized project prints the resume pointer (status/active task) and exits 0 WITHOUT re-seeding; status opens with "project exists — do NOT init" when state.json is present (kills double-init, the +2-4 calls/rep lever)
- [ ] scope-first-draft       depends-on: none — the freeze-time scope echo escalates from propose-to-stdout to a ready-to-paste §5 Scope line whenever declared tokens fail to cover §3 Touches (still propose-not-impose; target: post-freeze re-cross repairs -> 0)
- [ ] status-orientation-diet depends-on: none — one status read carries the full resume context (phase - next verb - active file), so re-orientation re-reads stop; audit the 3-4x/rep re-read transcripts for what was missing
- [ ] help-habit-kill         depends-on: none — the one --help/rep: unknown/misused subcommand errors restate usage inline (the skip-error-ergonomics recipe), and the skill quick-ref covers the verbs agents actually reach for

## Exit criteria (observable)
- [ ] init on an existing project is a no-op with a loud resume pointer — test-pinned
- [ ] scope echo emits a paste-ready Scope line on non-covering declarations — test-pinned
- [ ] a single status read carries phase + next verb + resume file — test-pinned
- [ ] misuse errors restate usage inline; no doc says "run --help" — test-pinned
- [ ] floors untouched: full fence green, no enforcement-path diff, ENGINE_MD5 re-pinned
- [ ] (paid, human-gated) WM1 re-measure: calls <= 12 mean, fidelity >= 0.97 held, zero double-init and zero post-freeze re-cross in transcripts
