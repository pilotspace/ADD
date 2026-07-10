# MILESTONE: Risk Proportional Ceremony

goal: cut ADD's big-milestone cost premium (1.8x dollars / 2x wall-clock vs spec-kit) toward ~1.3x by scaling ceremony to task risk — never by lowering the trust floor (frozen contract, red suite, recorded gate hold in every lane)
rationale: sub-milestone (user-signaled after the add-bench WM4-6 verdict): the benchmark proved the premium is turn fragmentation + suite-run churn + done-phase ceremony on big milestones — not the spec phases (~3%) — and that ceremony pays only where risk lives; scale it to risk.
stage: mvp · status: active · created: 2026-07-08T08:28:21+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  cut ADD's per-feature TURN COUNT — the measured cost driver — by collapsing MECHANICAL engine round-trips, without lowering the trust floor. Live evidence (fixed-harness add WM1, 2026-07-09, `scratchpad/baseline-runs/add/wm1`): **63 turns / $3.99 / 4.03M tok (96% cache_read) / fidelity 0.96**; **26 of 63 turns (~41%) are `add.py` round-trips** — `advance`×7, `status`/`guide`×5, ceremony (`new-task`/`lock`/`freeze`/`gate`/`init`/`new-milestone`)×12. Each round-trip re-reads the full ~60K context (that IS the cost). Three levers: (1) collapse the `advance` chain, (2) fold `status`+`guide` orientation, (3) trim per-call stdout that grows cache_read.
Out: touching app-code turns (irreducible deliverable work); suite-run churn / done-phase ceremony on BIG milestones (separate lever — this milestone targets per-feature fast/oneshot round-trips); any change that skips a freeze, a red suite, or a recorded gate (the floor is non-negotiable); lean-agent roster work (shipped in [[add-lean-loop]]).

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- TRUST FLOOR IS INVARIANT: every lane still requires a FROZEN §3 contract, a red suite before build, a recorded §6 gate, and security = HARD-STOP. A round-trip may be collapsed ONLY if it carries no human/proxy decision — freeze and gate are decision points and are never auto-crossed.
- MEASURE, DON'T ASSUME: each task states its before-number from the live baseline transcript and re-measures after; the milestone's proof is a fresh fixed-harness add WM1 run, not a code-reading argument.
- BACKWARD-COMPATIBLE CLI: existing subcommands/flags keep working; new behavior is additive (a flag or a smarter default that a bare call still honors) so the 3-tree byte-parity engine and its ~3k tests hold.

## Shared / risky contracts (freeze these first)
- `add.py advance` collapse semantics (where the chain STOPS) -> owning task advance-chain-collapse — the freeze/gate stop-points every other task assumes.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
> GROUND (2026-07-09) reshaped these: the `advance --to <phase>` bundle fast-forward ALREADY exists (add.py:1259, stops hard at `tests` to preserve the freeze gate) — the agent never used it. The live waste is the engine not HANDING the agent the exact/collapsed next command, so it spelunks `--help` ×7 + single-steps `advance` ×7. Root cause = `_next_footer` (add.py:5993) + `status` emit generic hints, not copy-pasteable commands.
- [x] advance-chain-collapse   depends-on: none                    — the post-advance `next:` footer emits the COLLAPSED `advance --to <phase>` command (front drafting span → contract) so the agent uses the existing bundle-advance instead of N single steps. Floor intact: `--to` still stops at `tests`; freeze/gate never auto-crossed.   (DONE `027063a`)
- [x] status-guide-fold        depends-on: advance-chain-collapse  — `status` folds in the guide's next-action AND the `next:` footer emits the EXACT copy-pasteable command WITH its required flags (e.g. `freeze --by <name>`, `gate PASS`) — killing the 7 `--help` discovery turns + the 6 status/guide re-orientation turns.   (DONE `76136f3`)
- [x] terser-engine-stdout     depends-on: none                    — DROPPED pre-spec, grounded at ~$0.02–0.04 (see Lever-3 note).

> LOOP round 2 (2026-07-09) — goal unmet at re-measure; the pinned-sonnet transcripts name the residual waste
> as engine-call REDUNDANCY (best run 21 `add.py` calls vs ~10 ideal; worst 33 with a repair loop). Three
> evidence-named defects (all from `mr-lever-sonnet` rep1/rep2 transcripts):
> (a) scope_violation death spiral — §5 Scope never declared before the tests→build snapshot → `gate PASS`
>     fails ×3 (`cheat detected`) → `heal_exhausted` → the agent GREPS THE ENGINE SOURCE ~10 turns to discover
>     `re-cross`. ~15 wasted turns in rep2.
> (b) wrong/stale next-footer + non-idempotent retries — after a successful `freeze` the footer says
>     `next: add.py freeze --by <name>` (phase hasn't moved when the footer renders); `already_frozen` /
>     `already_locked` / `skip_not_allowed` / `advance`-at-done hard-error on retry instead of no-op'ing
>     with the true next command.
> (c) kickoff `--help` spelunking — 7 `--help` calls even in the BEST run; the exact-footer only exists after
>     a first successful call, so the init→new-milestone→new-task span has no guidance yet.
- [x] first-call-ergonomics    depends-on: none                    — (DONE `5a76222`) kill (b)+(c): post-freeze/gate/re-cross footers emit the TRUE next command for the post-transition state; `already_*`/at-done retries become exit-0 no-ops that restate the state + exact next command; `init` stdout hands the full kickoff sequence (new-milestone → new-task → advance --to contract) as copy-pasteable commands so first-use `--help` is unnecessary. Floor intact: no gate/freeze auto-crossed, errors that guard the floor stay errors.
- [x] scope-gate-repair-path   depends-on: first-call-ergonomics   — kill (a): the tests→build crossing warns fail-fast when §5 Scope is still the template default (and suggests real paths, e.g. from git status); a scope_violation gate failure names the EXACT 3-step repair recipe (fix §5 → `re-cross --by <name>` → `gate PASS`) instead of prose that sends the agent source-diving. The tripwire itself is untouched — only its ERROR MESSAGE and the pre-crossing nudge change.   (DONE `1327e3b`)
- [ ] skip-error-ergonomics    depends-on: none                    — LOOP-3, from the re-measure census: `skip_not_allowed` dies naming the raw declaration + bad token(s) + the computed allowed set + the fix; the no-project error hands the exact `init --name --stage` command. Message layer only.

## Exit criteria (observable; map each to the task that delivers it)
- [x] a fresh fixed-harness add WM1 run shows TURNS and COST below the 63-turn / $3.99 baseline, with fidelity ≥0.95 and app_reachable   (← levers 1+2, re-measured; lever 3 dropped — see note) **RESOLVED AT CLOSE: the 63t/$3.99 anchor is VOID (model-unpinned, disclosed below) — superseded by the pinned-meter LOOP-2 criterion; human-accepted 2026-07-10.**

> **Re-measure verdict (2026-07-09, pinned `claude-sonnet-5`/medium, n=3 vs n=3).** The 63t/$3.99
> anchor is VOID — it ran on an unpinned ambient model (harness bug #28, fixed in `4d0c52e`); the
> only valid comparison is same-model A/B. On the pinned meter: lever (HEAD) mean **98t / $4.30**
> vs pre-lever (94486bb) mean **102t / $4.51** — levers 1+2 are real (−4% turns / −5% cost) but the
> effect sits inside the harness's ~2× run-to-run variance (turns 66–127) and the fidelity gate is
> unjudgeable (judge grounded on PROMPT.md + a reachable-bit only, judge model unpinned — fid spread
> 0.0–1.0 on runs that all built working apps). Transcript anatomy found the REAL residual lever:
> even the best run makes 21 `add.py` calls (~2× the ~10-call ideal; worst run 33 with a
> `status`×6/`gate`×5/`freeze`×3 repair loop) and ceremony consumes ~55–60% of all turns vs
> spec-kit's 22-turn total. Continuation → LOOP round 2 tasks below (held open per loop.md).
- [x] LOOP-2 re-anchored criterion (valid meter): a fresh pinned-sonnet add WM1 run (n=3) shows mean `add.py` calls ≤ 12 with ZERO engine-source spelunking turns, and mean turns/cost at or below the pinned pre-lever mean (102t / $4.51)   (← first-call-ergonomics + scope-gate-repair-path, re-measured on the same harness) **PARTIAL, human-accepted at close 2026-07-10: turns/cost PASS decisively (77.7t/$2.97, −24%/−34%, verdict below); calls 21 > 12 — the shortfall is agent habit + legitimate repair overhead, accepted with the follow-on levers named in the CLOSE VERDICT.**

> **Lever 3 (terser-engine-stdout) — DROPPED, disclosed 2026-07-09.** Grounded the actual
> per-call stdout: fattest is `check` (1251 B) / full `status` (1202 B); `advance` already
> terse (156 B) from task 1. Total add.py stdout across the whole 63-turn baseline ≈ 4K tokens
> added to context once → ~60–120K cache_read (~1–3% of 3.87M) ≈ $0.02–0.04. Trimming it in
> half moves cents, inside the 3× measurement noise. The real wins are levers 1+2 (fewer TURNS,
> each avoiding a ~61K-token full-context re-read). Kept the milestone honest rather than spend
> full rigor on a $0.02 lever; the re-measure below proves the 1+2 gain on real evidence.
- [x] `add.py advance` crosses multiple AI-owned phases in one invocation yet still halts at contract-freeze and verify-gate (floor intact)   (← advance-chain-collapse, `027063a` — `advance --to <phase>` stops hard at tests; live smoke confirmed)
- [x] `add.py status` surfaces the next phase action inline — an agent can proceed without a separate `guide` call   (← status-guide-fold, `76136f3` — `_next_command` composer feeds guide/status/footer; live smoke confirmed all three)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` + `add_engine/io_state.py` — 5 shipped levers across 3 LOOPs: (1) collapsed `advance --to` footer (`027063a`); (2) `_next_command` one-composer status/guide/footer (`76136f3`); (3) post-freeze truth + idempotent retries + init kickoff (`5a76222`); (4) default-scope crossing warning + scope_violation repair recipe (`1327e3b`); (5) skip_not_allowed evidence + exact no-project init command (`901cd1f`). ENGINE_MD5 4fefc0bb → 147820fd (PKG → 5f60c0b2), 3-tree parity held throughout
- skill   : untouched
- book    : untouched
- harness (out-of-tree but shipped alongside): `benchmark/runner/agent.py` pins `--model claude-sonnet-5 --effort medium` (`4d0c52e`) — every prior cross-run cost comparison was model-confounded

### Cross-task evidence   (one row per task)
- advance-chain-collapse : gate=PASS · targeted green + full suite green · residue=none
- status-guide-fold      : gate=PASS (auto-gate, refute-read EARNED) · full suite 1 transient pyc flake re-run green in isolation · residue=none
- terser-engine-stdout   : DROPPED pre-spec — grounded at ~$0.02–0.04 of a $3.99 run (see Lever-3 note); never opened, no gate
- first-call-ergonomics  : gate=PASS (auto) · 7 red→green + suite 3345 OK · residue=none · `5a76222`
- scope-gate-repair-path : gate=PASS (auto) · 5 red→green + suite 3350 OK · residue=none · `1327e3b`
- skip-error-ergonomics  : gate=PASS (auto) · 4 red→green + suite 3354 OK (first run caught a real quoting regression pre-gate) · residue=none · `901cd1f`

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] every criterion resolved: 2 met outright (advance-collapse `027063a` · status-fold `76136f3`); 3 resolved-with-disclosure at the human close (void-baseline superseded · LOOP-2 partial · LOOP-3 partial — each annotated inline above)
- goal: cut the per-feature turn count — **PARTIALLY MET, closed by human decision 2026-07-10** after 3 LOOPs + 2 live re-measures: **−24% turns / −34% cost at stable 0.97 fidelity** (n=3, pinned meter, outside the noise floor), every death-spiral repair loop dead, floor never lowered. Premium vs spec-kit ~3.3× (was ~5×), not the aspirational ~1.3× — the residual is structural trust ceremony + agent habit, out of message-layer reach. Follow-on levers named in the CLOSE VERDICT.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR for branch `feat/add-bench-scaffold` (bundles three-phase-flow + harness fixes incl. model pin `4d0c52e` + this milestone's `027063a`/`76136f3`); the human reviews + merges
- [ ] bundle into the next release cut with the 4 already-closed milestones (release.md; engine records, human tags/publishes)
