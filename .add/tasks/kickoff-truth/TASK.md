# TASK: Kickoff truth: lane-aware kickoff + full call recipe + dup-failure short-circuit

slug: kickoff-truth · created: 2026-07-13 · stage: mvp
milestone: ceremony-to-effort
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: kickoff truth — the engine's own stdout stops generating wasted calls (evidence: transcript audit 2026-07-13, loop2-lever rep0/1/2)
Must:
  - `init` kickoff names the single-task lane (`new-task <slug> --oneshot`) BEFORE the milestone lines — rep2 (best run) skipped the milestone; rep0/rep1 followed the milestone-first kickoff and paid 2+ extra calls
  - `new-task` stdout ends with the task's FULL remaining engine-call recipe (advance --to plan · freeze --by <name> · advance x3 · gate PASS) so the agent never re-orients via status/guide/--help — measured 6-11 orientation calls per run
  - a byte-identical failing call repeated consecutively gets a short-circuit hint line naming that it already failed identically — measured 12-21% of all calls were exact duplicate failures
Reject:
  - a DIFFERENT failing call after a failure -> no hint (only consecutive identical repeats short-circuit)
  - a repeated call that now SUCCEEDS -> no hint (state clears on success)
Accept: Given a fresh project, When the agent follows only init/new-task stdout, Then the printed lines alone name the oneshot lane + the complete per-task call sequence, and a repeated identical failing call visibly says so.
Boundary: lane variants — normal · --fast · --oneshot tasks each get the recipe (one shared wording; the freeze/gate lines are lane-invariant)
Assumptions: ⚠ engine errors funnel through ONE emitter add.py can hook — why: the `add: error:` prefix suggests a shared path; if wrong: the dup-hint misses some error paths (silent no-hint, never a wrong hint) and the hook lands on the main emitter only

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add.py:cmd_init (587, kickoff print block ~673-677) · add.py:cmd_new_task (705, footer prints) · add.py:main (8760, single dispatch — success exit path) · add_engine/io_state.py:_die (178, the ONE error emitter, 183 call sites in add.py) · x4 engine twins + engine_pin re-pin
Context (working folder): .add/.gitignore transient list (init-scaffolded — last-fail sidecar joins it)
Honors (patterns / conventions): milestone Ground (ceremony-to-effort) — extend _next_command conventions, never fork a 4th stdout surface; first-call-ergonomics suite pins existing stdout (additive lines only); slang guard on message text
Anchors the contract cites: cmd_init · cmd_new_task · main · _die
Ground SHA: 497c6bf — baits re-verified live probe 2026-07-13: --to-plan bait DEAD (succeeds unfilled) · already-at retry DEAD (exit-0 no-op) · milestone-first kickoff LIVE · recipe + dup-short-circuit MISSING

### Contract

```
1  cmd_init kickoff block: the single-task lane line prints FIRST —
     kickoff (single task):    add.py new-task <slug> --title "..." --oneshot
     kickoff (multi-task):     add.py new-milestone ... / add.py new-task ... --milestone ...
   then the shared `add.py advance --to plan` line. Existing lines kept (additive).
2  cmd_new_task stdout ends with the full remaining call recipe (all lanes):
     recipe — this task's remaining engine calls:
       add.py advance --to plan   (write the section rules first)
       add.py freeze --by <name>   [human gate — approves the whole plan]
       add.py advance   (plan -> tests: write the RED suite)
       add.py advance   (tests -> build: make it green)
       add.py advance   (build -> verify: gather evidence)
       add.py gate PASS   (record the verify outcome)
3  _die dup short-circuit: sig = md5(registered argv + error-code head of msg);
   if the sidecar holds the same sig, stderr gains ONE extra line:
     hint: this exact call already failed with the same error - change the command or
     input before retrying (add.py status shows the true state)
   then the sig is (re)written. main() clears the sidecar on any successful exit
   (success clears the state). No root resolvable -> no sidecar, no hint (fail-open).
   v2 (change request, discovered in build): the sidecar lives OUTSIDE the project
   tree — OS tmp dir, keyed by md5(project root path) — because the engine's own
   byte-fence floor pins that a REJECTED command writes ZERO bytes to the .add tree
   (reject-writes-nothing invariant, 16 pre-existing suites). A failing call must
   leave the tree byte-identical; the hint state is ephemeral cache, never a record.
```

`Least-sure flag surfaced at freeze:` [contract] the main()-unlink success hook — why: SystemExit(0) paths inside commands may bypass the post-dispatch unlink, leaving a stale sig that fires one wrong hint after an intervening success; if wrong: one misleading stderr line, never a blocked call — mitigate by also clearing on any successful state write if trivially reachable
Status: FROZEN @ v2 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy & known-problem fixes: 1) red tests in add-method/tooling/test_kickoff_truth.py (tmp-project subprocess pattern from sibling suites) 2) cmd_init kickoff reorder 3) cmd_new_task recipe block 4) _die sidecar + main unlink 5) init .gitignore scaffold line 6) twin sync x4 + engine_pin re-pin. Traps: first-call-ergonomics tests pin existing stdout — ADD lines, never edit existing ones; _die runs pre-root sometimes — guard find_root() None; the .gitignore scaffold must stay idempotent (init never clobbers an existing copy).
Approach (domain strategy): message-layer additive, fail-open sidecar, correctness-first

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (cmd_init:587 · cmd_new_task:705 · main:8760 · _die io_state.py:178 — all re-verified at 497c6bf)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome (no-hint behaviors)
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (main-unlink bypass risk, cost bounded to one stderr line)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T09:05:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_init_kickoff_names_single_task_lane_first · test_new_task_emits_full_recipe (freeze + gate lines, all lanes incl --fast/--oneshot) · test_repeated_identical_failing_call_gets_hint · test_different_failure_gets_no_hint · test_success_clears_dup_state · test_advance_to_plan_unfilled_succeeds (bait-dead regression pin).
Tests live in: `add-method/tooling/test_kickoff_truth.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned EXCEPT the sidecar storage — v1's in-tree `.add/last-fail.json` was refuted by the full suite (16 reject-writes-nothing suites + 4 packaging failures from my twin-sync leaking test sources); the v2 change request (re-frozen, approved) moved it to the OS tmp dir keyed by md5(root) and dropped every .gitignore edit. Also: the pre-kickoff headless hint was made oneshot-first too (unpinned line, same measured bait — SOFT-strategy self-improvement); the sibling InitKickoffTest pin was STRENGTHENED to the v2 lane-aware shape, never deleted.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (test edit happened in TESTS phase after the v2 re-freeze; fresh snapshot at the tests→build crossing)
- [x] green was EARNED — 4 tests red-first for the feature's absence; v1 build REFUTED by the full suite (real fence, not overfit); v2 full suite 3453/3453 OK
- [x] input dialect held — tests assert the contract's own stdout strings (kickoff/recipe/hint lines verbatim)
- [x] no exposed secrets, injection openings, or unexpected dependencies — sidecar carries only an md5 sig in the OS tmp dir; a poisoned/pre-created sidecar yields at worst one spurious stderr hint (fail-open, never a blocked call, never a tree write)

Build expectations (from §1 Accept + §3 CONTRACT): a fresh project's init/new-task stdout alone names the oneshot lane + the complete 6-call sequence; a repeated identical failing call visibly says so; `.add` stays byte-identical across failures — confirmed by test_kickoff_truth (7/7) + a live end-to-end probe (scratchpad/proof: kickoff ✓ recipe ✓ hint-on-2nd ✓ no-hint-on-different ✓ success-clears ✓ tree-md5 identical ✓)

### GATE RECORD
Outcome: PASS
Reviewed by: AI auto-gate on evidence (autonomy: auto; full suite 3453 OK · check 734/0 · live probe · sibling pins strengthened) · date: 2026-07-13

