# TASK: status folds in the guide next-action + the footer emits exact copy-pasteable commands with flags (kills the --help discovery churn)

slug: status-guide-fold · created: 2026-07-09 · stage: mvp
milestone: risk-proportional-ceremony
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py:cmd_guide` (add.py:2699) — prints `next: {action}` (PHASE_GUIDE prose) + a HARDCODED `then:` line: `add.py gate ...` at verify, else `add.py advance` (add.py:2779-2787). This `then: add.py advance` is now DIVERGENT + WRONG at contract (says advance; the real next step is freeze — task 1's `_next_footer` fixed this but cmd_guide was not updated). · `cmd_status` (add.py:2321) — `--brief` ALREADY delegates to `_next_footer` (add.py:2355, so it inherits task 1's collapse); plain full `status` renders its own next-step line separately (its own composer, does not reuse `_next_footer`). · `_decide_next_pair(state, d) -> (text, human_stop)` (add.py:5946) — the Arm-B command source: empty milestone → `"decompose into tasks — add.py new-task {ms}"` (MISSING `--title`); front-phase → `"approve the contract of {slug} — add.py report {ms} {slug} --decide"`; verify → `"gate {slug} — add.py report {ms} {slug} --decide"`. · Setup footers: `init` prints `next: open Claude Code, run /add …` (prose, NO exact CLI ceremony command); `new-milestone` prints `next: decompose into tasks — add.py new-task {ms}` (missing `--title`). `_next_footer` (add.py:5993, task 1) is the canonical command composer both should reuse.
Context (working folder): live baseline transcript `scratchpad/baseline-runs/add/wm1/transcript.jsonl` — the agent ran `--help` on init/lock/new-milestone/new-task/advance/freeze/gate (7 turns) + status×4/guide×2, because the next-step surfaces name partial/prose hints, not exact copy-pasteable CLI commands with flags. Milestone doc `.add/milestones/risk-proportional-ceremony/MILESTONE.md`.
Honors (patterns / conventions): `_next_footer` is the SINGLE next-step composer (`next-footer-engine`) — this task makes cmd_guide + plain status REUSE it rather than keep parallel `then:` logic. cmd_guide stays strictly read-only (load_state only, never writes). The `escape hatch: add.py new-task <slug> --title "..."` line in the no-task status (add.py ~2470) is the exact-flag pattern to propagate. 3-tree byte-parity + ENGINE_MD5 pin bind every add.py edit.
Seams consulted: `next-footer-engine` (the one next-step channel); `.add/tasks/advance-chain-collapse/TASK.md` §3 (the collapse contract this fold propagates to the read-only surfaces).
Anchors the contract cites: `cmd_guide`, `cmd_status`, `_next_footer`, `_decide_next_pair`.
Issues/Risks (→ feed §1): (1) cmd_guide's `then:` and plain status render next-steps INDEPENDENTLY of `_next_footer` → three surfaces can disagree (already do: guide says `then: advance` at contract, footer says `freeze`). Fold = reuse the one composer. (2) `_decide_next_pair`'s `report … --decide` hints assume INTERACTIVE human review; a headless agent uses `freeze`/`gate` directly — so exact-command emission must name the CLI verb+flags a headless run actually uses, not only the interactive `--decide` path. (3) MANY tests pin these exact strings (test_next_footer_engine, test_loop_aware_orient, test_progressive_context, guide/status tests) → grep + update in the TESTS phase, red-first. (4) Must not weaken the driver marker (`[human gate]`/`[you drive]`) — the human_stop bit stays truthful.
Related intent: MILESTONE `risk-proportional-ceremony` — kill the 7 `--help` + 6 re-orient turns (measured) by handing the agent the exact next command everywhere it looks. Builds directly on [[advance-chain-collapse]] (the collapse contract).
Ground SHA: 027063a

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: every next-step surface hands the agent the EXACT copy-pasteable CLI command — the read-only surfaces (`guide`, plain `status`) reuse the one `_next_footer` composer (no parallel/divergent `then:` logic), and the setup-ceremony + empty-milestone next-steps name the command WITH its required flags — so a headless agent never reads `--help` and never needs a separate `guide` round-trip.
Framings weighed: fold the read-only surfaces onto `_next_footer` + enrich the setup/Arm-B commands with flags (chosen — one composer, kills the measured 7 `--help` + 6 re-orient turns) · leave surfaces independent but string-sync them (rejected — three parallel emitters keep drifting, exactly today's `then: advance`-at-contract bug) · document the flags in the book only (rejected — the census proved guide-only docs go unread; the footer is the read-every-turn channel).
Must:
<must>
  - M1 `cmd_guide`'s `then:` command == the command `_next_footer` yields for that phase (reuse the composer) — so guide teaches `advance --to contract` at front phases and `add.py freeze` at contract, never the divergent/wrong `then: add.py advance`.
  - M2 plain full `status` surfaces the same `_next_footer` next-command inline — an agent reading `status` alone can proceed without a separate `guide` call (the fold).
  - M3 the empty-milestone next-step (`_decide_next_pair`) names the required flag: `add.py new-task <ms> --title "..."` (not the bare `add.py new-task <ms>`).
  - M4 the setup-ceremony next-steps (`init`, `new-milestone`) name the exact CLI command WITH flags as a headless escape-hatch — a headless agent gets the real next command, not only "open Claude Code, run /add".
  - M5 exact-flag coverage names the flags for the verbs the live run spelunked: `freeze --by <name>`, `lock --by <name>`, `new-milestone <slug> --title "..." --goal "..."`, `new-task <slug> --title "..."` — wherever each appears as a next-step.
  - M6 read-only + purity invariants hold: `cmd_guide`/`status` still write nothing; `_next_footer` stays pure/fail-soft; the `[you drive]`/`[human gate]` driver marker stays truthful (human_stop unchanged).
</must>
Reject:
<reject>
  - R1 unknown/absent/corrupt phase in `guide`/`status` -> the existing fail-clean path (`_die "unknown phase"` / re-orient), never a fabricated command -> "unmapped_phase" (unchanged behavior).
  - R2 no active in-flight task -> the exact-flag Arm-B/setup command (never a collapse hint), driver marker truthful -> "arm_b_exact_command".
</reject>
After:
<after>
  - `add.py guide` at contract prints `then: add.py freeze` (not `advance`); at front phases prints the collapse command — identical to the mutating-verb footer.
  - `add.py status` (plain) shows the exact next command inline; no separate `guide` needed to proceed.
  - the setup ceremony + empty milestone print exact flagged commands; a headless run reaches build without a single `--help`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that routing `cmd_guide`/plain `status` through `_next_footer` won't break the many tests pinning their CURRENT `then:`/next strings — lowest confidence because these strings are widely asserted (loop-aware-orient, progressive-context, guide/status suites); if wrong: those asserts fail red in the TESTS phase and are updated there (legitimate — behavior changed by design; test edits belong in §4, never build). Mitigation: grep every pinned string before build, enumerate via the full suite red-first.
  - [ ] that changing Arm-B `new-task <ms>` → `new-task <ms> --title "..."` doesn't violate task 1's "Arm B byte-unchanged" (task 1's contract froze TASK-1's behavior; task 2 has its own contract that supersedes — not an edit of a frozen doc) — confirm the freeze guard treats this as a new contract, not a tamper.
  - [ ] that the setup footers' "run /add" prose should GAIN a CLI escape-hatch, not be replaced (interactive users still want /add) — keep both: the skill line + the exact CLI command.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: guide reuses the footer command at contract   # M1
  Given an active task at phase contract
  When `add.py guide` runs
  Then the `then:` line reads "add.py freeze" (not "add.py advance")
  And guide writes nothing to disk

Scenario: guide teaches the collapse at a front phase   # M1
  Given an active task at phase ground
  When `add.py guide` runs
  Then the `then:` line contains "add.py advance --to contract"

Scenario: plain status carries the next command inline   # M2
  Given an active task at phase contract
  When `add.py status` runs
  Then its next-step surface names "add.py freeze" (no separate guide call needed)

Scenario: empty milestone names the flagged new-task   # M3
  Given an active milestone with zero tasks
  When a completing verb prints its next: footer
  Then it reads "add.py new-task <ms> --title" (the required flag present)

Scenario: setup ceremony gives the headless CLI command   # M4 + M5
  Given a just-initialised project (no skill available, headless)
  When `init` / `new-milestone` print their next-step
  Then an exact CLI command with flags is named (e.g. new-milestone <slug> --title --goal, new-task <slug> --title)
  And the interactive "/add" guidance still appears

Scenario: read-only + markers preserved   # M6
  Given any next-step surface renders
  When guide/status/footer print
  Then no file is written
  And the [you drive] / [human gate] marker matches the phase's true owner

Scenario: corrupt phase fails clean   # R1
  Given a task whose state.json phase is unknown
  When `add.py guide` runs
  Then it exits with an unmapped-phase error and prints no fabricated command

Scenario: no in-flight task -> exact Arm-B command   # R2
  Given no active in-flight task
  When a completing verb prints its footer
  Then the command is the flagged Arm-B/setup command, never a collapse hint
  And the driver marker is truthful
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# add-method/tooling/add.py — ONE shared command composer, reused everywhere

_next_command(phase: str) -> str                 # NEW pure helper (extracted from _next_footer)
  verify                      -> "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
  ground | specify | scenarios -> "add.py advance --to contract   (or step-by-step: add.py advance --fill <draft>)"
  contract                    -> "add.py freeze --by <name>"        # ENRICHED: names --by (still contains "add.py freeze")
  tests                       -> "add.py advance --fill <draft>"
  else (build|observe)        -> "add.py advance"

_next_footer(root, state)      -> Arm A reuses _next_command(phase); Arm B + fail-soft as in task 1
                                  EXCEPT the empty-milestone command gains its flag (below).
cmd_guide(...)   -> the `then:` line prints _next_command(phase)  (was hardcoded advance/gate); READ-ONLY preserved
cmd_status()     -> plain full status prints _next_command(phase) inline as its next-command; READ-ONLY preserved

_decide_next_pair(state, d) -> empty milestone: "decompose into tasks — add.py new-task {ms} --title \"...\""

Setup footers (headless escape-hatch — the /add prose STAYS, a CLI line is ADDED):
  init          -> + "or headless: add.py new-milestone <slug> --title \"...\" --goal \"...\""
  new-milestone -> "decompose into tasks — add.py new-task {ms} --title \"...\""

INVARIANT: _next_command is PURE; guide/status write nothing; _next_footer stays fail-soft;
           driver markers ([you drive]/[human gate]) unchanged; task-1 asserts still hold
           (contract command still contains "add.py freeze", no "advance"/"--to").
```

Glossary deltas: exact-command surface: any next-step line (footer · guide · status · setup) that names the copy-pasteable CLI verb WITH its required flags, composed by the single `_next_command` helper — so a headless agent never reads `--help`.
Least-sure flag surfaced at freeze: [spec] routing cmd_guide + plain status through `_next_command` will red many tests that pin their CURRENT `then:`/next strings (loop-aware-orient, progressive-context, guide/status suites). This is behavior changed BY DESIGN — those asserts get updated in the TESTS phase (never during build). Risk is churn, not correctness; mitigated by grepping every pinned string + enumerating breakage via the full suite red-first. Task-1's contract-phase asserts survive (the enriched `freeze --by <name>` still satisfies them).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_hint_batch_ops.py` `add-method/tooling/test_loop_aware_orient.py` `add-method/tooling/test_progressive_context.py`
Strategy (ordered batches): 1. extract `_next_command(phase)` from `_next_footer`'s Arm-A elif (single source). 2. point `cmd_guide`'s `then:` line + plain `status`'s next-command at `_next_command`. 3. enrich the contract command to `add.py freeze --by <name>` + `_decide_next_pair` empty-milestone + init/new-milestone setup footers with exact flags. 4. sync twins (prepare_bundle + cp .add), restore bundled engine_pin, re-pin ENGINE_MD5, rm __pycache__. 5. full add.py suite red-first to enumerate every pinned-string breakage; update those asserts in §4.
Approach (domain strategy): DRY the next-step composition — one pure `_next_command` helper feeds every surface, replacing three parallel emitters; enrich the setup/Arm-B strings with the flags a headless run needs. methodology-engine-dev stance: deterministic, fail-loud, backward-compatible.
Data strategy: no data-shape change — all surfaces return `str`; the shared helper is the single source, so drift is structurally impossible.
Pattern: extends `next-footer-engine` (the ONE next-step channel) from the mutating-verb footer to the read-only surfaces + setup.
Optimization stance: token-cost (turn-count) — kill the 7 `--help` + 6 re-orient turns; budget = beat 63t/$3.99. ⚠ least-trusted facet: the breadth of pinned-string test churn (many suites) — mitigated by red-first enumeration. correctness-first otherwise.

Persona (required): methodology-engine-dev — builds the engine that drives builds; deterministic, fail-loud.
Spawn isolation (default): none — single-author engine edit + mechanical twin sync.
Known-problem fixes: (a) three parallel next-step emitters drift → collapse to one `_next_command` (root-cause fix, not a string patch). (b) prepare_bundle deletes bundled engine_pin.py → git-restore + re-pin (memory lesson). (c) wide pinned-string test churn → enumerate red-first via full suite, update asserts in §4 (never build — tamper tripwire). (d) task-1 contract-phase asserts must still pass → keep "add.py freeze" as a substring of the enriched command.
Strategy actually used: as planned — extracted `_next_command(phase)` (pure) from `_next_footer`'s Arm-A elif; `_next_footer`, `cmd_guide` `then:` line, and plain status's `resume:` block all now call it (contract→`add.py freeze --by <name>`). Enriched `_decide_next_pair` empty-milestone → `new-task {ms} --title "..."` and init's footer → headless `new-milestone <slug> --title --goal` escape-hatch. Twin sync + git-restore bundled pin + re-pin ENGINE_MD5 6bb86306→dccb78ac. One test-structure fix (test_hint_batch_ops source anchor moved to `_next_command`), done in the TESTS phase.
Safety rule (feature-specific): the driver marker (human_stop) is computed unchanged; the fold only replaces the command TEXT, never the ownership bit — a `[human gate]` never silently becomes `[you drive]`.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add.py suite 3337/3338 green; the 1 was a transient `_bundled/tooling/__pycache__/*.pyc` left by a sibling test importing the bundled engine (the "rm __pycache__ before parity checks" quirk) — cleaned, `test_bundle_parity` re-run green in isolation
- [x] coverage did not decrease — 4 new red→green tests added (test_next_footer_engine + test_guide + test_hint_batch_ops); none removed
- [x] no test or contract was altered during build — build touched only add.py (helper + prose) · 3 engine_pin.py · .add/SEAMS.md; no test body or frozen §3 edited
- [x] the green was EARNED, not gamed — refute-read verdict EARNED (below): tests assert observable CLI next-step strings via the REAL binary, confirmed RED→GREEN, live smoke corroborates independently
- [x] concurrency / timing of the risky operation is safe — N/A: `_next_command` is a pure static-string composer; guide/status stay read-only (load_state only)
- [x] no exposed secrets, injection openings, or unexpected dependencies — no IO/eval/network/secret; no user input flows into the emitted command text
- [x] layering & dependencies follow CONVENTIONS.md — DRYs three parallel emitters into one composer (removes drift); 3-tree parity + ENGINE_MD5 pin re-satisfied
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `guide` at contract prints `then: add.py freeze --by <name>` (not advance) — CONFIRMED by live smoke
- [x] plain `status` at contract prints `next: add.py freeze --by <name>` inline — CONFIRMED by live smoke
- [x] empty milestone footer names `add.py new-task <ms> --title "..."`; `init` names the headless `new-milestone <slug> --title --goal` escape-hatch — CONFIRMED by live smoke
- [x] front-phase guide/footer teach `advance --to contract`; task-1 collapse asserts still green — CONFIRMED by test_guide + test_next_footer_engine green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_next_command` is referenced by `_next_footer`, `cmd_guide`, and plain status's resume block (grep-confirmed 3 call sites + the def); the live smoke prints each surface.
- [x] DEAD-CODE (code) — `_next_command` extracted the logic that previously lived inline in `_next_footer` (no duplication left behind); no orphan symbol.
- [x] SEMANTIC (prose) — the emitted commands read in full: each names the exact CLI verb + required flag a headless run uses; the `/add` prose is kept alongside (not replaced) at init.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] `cmd_guide`, `cmd_status`, `_next_footer`, `_decide_next_pair` all resolve; new `_next_command` added and referenced.
- [x] no anchor renamed since Ground SHA 027063a — only the next-step command TEXT + one extracted helper.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed for overfit — tests assert observable next-step strings via the REAL CLI (guide/status/footer output), not internals; confirmed RED→GREEN (4 new tests failed pre-build); confirmed the fold is real (independent live smoke shows guide+status+setup all naming the exact flagged command); confirmed no test weakened (test_guide_verify's `assertNotIn("advance")` still holds under `_next_command`).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — pure static-string composition; no IO/eval/network/secret; no user input in the command text.
2. Concurrency: CLEAR — `_next_command` is pure; guide/status stay read-only (load_state only).
3. Architecture: CLEAR — DRYs three parallel emitters to one composer (removes drift); reuses the single next-step channel; 3-tree parity + pin re-satisfied.
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — gate ARC (goal · evidence · advisor verdicts) rendered before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: auto-gate (autonomy: auto — refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, architecture binding advisory; no security/concurrency/architecture residue to escalate) · date: 2026-07-09

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose fold the read-only surfaces onto `_next_footer` + enrich the setup/Arm-B commands with flags; rejected leave surfaces independent but string-sync them (rejected — three parallel emitters keep drifting, exactly today's `then: advance`-at-contract bug) · document the flags in the book only (rejected — the census proved guide-only docs go unread; the footer is the read-every-turn channel).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: DRY the next-step composition — one pure `_next_command` helper feeds every surface, replacing three parallel emitters; enrich the setup/Arm-B strings with the flags a headless run needs. methodology-engine-dev stance: deterministic, fail-loud, backward-compatible.
- [AI] build — data strategy: no data-shape change — all surfaces return `str`; the shared helper is the single source, so drift is structurally impossible.
- [AI] build — pattern: extends `next-footer-engine` (the ONE next-step channel) from the mutating-verb footer to the read-only surfaces + setup.
- [AI] build — optimization stance: token-cost (turn-count) — kill the 7 `--help` + 6 re-orient turns; budget = beat 63t/$3.99. ⚠ least-trusted facet: the breadth of pinned-string test churn (many suites) — mitigated by red-first enumeration. correctness-first otherwise.
- [AI] build — strategy used: as planned — extracted `_next_command(phase)` (pure) from `_next_footer`'s Arm-A elif; `_next_footer`, `cmd_guide` `then:` line, and plain status's `resume:` block all now call it (contract→`add.py freeze --by <name>`). Enriched `_decide_next_pair` empty-milestone → `new-task {ms} --title "..."` and init's footer → headless `new-milestone <slug> --title --goal` escape-hatch. Twin sync + git-restore bundled pin + re-pin ENGINE_MD5 6bb86306→dccb78ac. One test-structure fix (test_hint_batch_ops source anchor moved to `_next_command`), done in the TESTS phase.
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy: auto — refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, architecture binding advisory; no security/concurrency/architecture residue to escalate))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

