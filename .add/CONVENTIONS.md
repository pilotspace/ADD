# CONVENTIONS  (survivor layer — set once, kept for the whole project; append-only is newest-first — compaction door per compact-foundation.md)

Language/framework:
  - Tooling: Python 3.12+ (standard library only — no third-party packages).
  - Installer: Node.js >= 16 (built-in modules only).
  - Method content: Markdown (the skill + the AIDD book).

Folders:
  - `add-method/`            the shippable npm package (`@pilotspace/add`)
    - `skill/add/`           thin router SKILL.md + `phases/*.md` (progressive disclosure)
    - `tooling/`             `add.py` (scaffolder + state tracker) + `templates/` + `test_add.py`
    - `bin/cli.js`           the `npx @pilotspace/add init` installer
    - `docs/`                the AIDD book bundled as the trust layer
  - `*.md` (repo root)       the AIDD book source chapters
  - `.add/`                  ADD runtime for THIS repo (dogfooding): state, tasks, survivor files

Naming: kebab-case files; snake_case Python; lowerCamelCase JS; task slugs alphanumeric + - _.

Lint/format: keep Python stdlib-idiomatic and type-hinted; no formatter enforced yet (add ruff in CI later).

Errors: machine-readable, never free text. The Python tool exits non-zero with `add: error: <msg>`.

Architecture:
  - The skill is thin and stateless; ALL state lives in `.add/state.json` (anti-context-rot).
  - The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber.
  - The method is tool-agnostic: gates are enforced by process/CI, not inside the agent.

## Method learnings (folded from OBSERVE deltas)
- (ADD) a 25% pure-compaction tends to land EQUIVALENT, not CLEARER — the realistic effectiveness bar for already-tight guides is "no rule/nuance lost + leaner", and a quality-review subagent reliably surfaces the dropped sidebars to restore (evidence: review flagged 5, all restored, suite stayed green).  [folded foundation-version 46 · from orchestration-fold]
- (ADD) test-pinned per-phase guides have an effectiveness floor like the always-loaded core — set the target at the realistic ceiling (20%) UP-FRONT with rationale, rather than freezing 25% and re-speccing after build (saves the tamper/reopen cycle); the tree-wide 25% is carried by the load-on-demand reference pool (evidence: 20% hit cleanly, CLEARER, no re-spec needed).  [folded foundation-version 46 · from phase-guides-trim]
- (ADD) a token-reduction TARGET can collide with the effectiveness floor; the honest resolution is a human-approved change-request that re-specs the number, NEVER weakening the test or gutting the prompt (evidence: v1 ≥25% re-specced to ≥12% on build evidence; full suite stayed green).  [folded foundation-version 46 · from skill-core-compact]
- (ADD) the tamper tripwire fires when a frozen §3 + red test are edited in place at verify — even for a LEGITIMATE re-spec; the method-correct flow is to re-cross tests→build so the snapshot re-takes cleanly (evidence: `tamper_detected:contract_tampered,build_tampered` → `phase tests`→`advance`×2 cleared it; `reopen` is for DONE tasks only).  [folded foundation-version 46 · from skill-core-compact]
- (TDD) a "spans multiple X" test must assert the SEPARATOR/fencing, not just that both X appear — both-present passes even if the blocks run together or the header sits in the wrong place (evidence: refute-read nit — added `assertIn("\n\nmilestone: m2")` to pin the blank-line fence between stream blocks)  [folded foundation-version 45 · from cross-active-waves]
- (TDD) when a setup command REPLACES rather than ADDS to a set (here `new-milestone` resets `active_milestones` to `[new]`), build the desired set EXPLICITLY at the end of arrange (a complete-value `_poke` or a final reconcile) instead of relying on per-create activation — interleaved create+activate silently drops earlier members (evidence: the first my-work-lens fixture left only the last milestone active → t1 vanished from the lens)  [folded foundation-version 45 · from my-work-lens]
- (TDD) a test named `*_byte_identical` must actually assert byte-identity (or absence of EVERY new fragment, incl. empty separators), not just absence of the one new keyword — else a different spurious fragment passes under a name that claims more than it checks (evidence: refute-read Finding 2 — `test_no_owner_stream_byte_identical` only checked `not in "owner:"`; renamed + strengthened to also reject the `· ` separator)  [folded foundation-version 45 · from per-stream-owner]
- (ADD) when widening a single-target command to multi-target, EXTRACT the per-target render into a pure helper and keep the len==1 path calling it verbatim — `print("\n".join(lines))` is byte-identical to the old per-line `print()`s, so the single-target output (and every existing test) stays green while the multi-target path is purely additive (evidence: cross-active-waves extracted `_wave_block_lines`; the whole unchanged test_dag_scheduler suite stayed green)  [folded foundation-version 45 · from cross-active-waves]
- (ADD) a multi-field identity match (owner/assignee vs resolved actor) needs an explicit BOTH-DIRECTIONS test — the positive (matches) AND the near-miss (same name, different email → no match) — or the discriminating half of the rule is unverified (evidence: refute-read confirmed test_mine_match_email_first_name_fallback exercises both branches; the role="both" + ordering branches were initially untested and added post-review)  [folded foundation-version 45 · from my-work-lens]
- (ADD) a present-only render that reuses a formatter (`_fmt_actor`) must replicate that formatter's OWN emptiness guard at the call site — `_fmt_actor` returns a truthy ` <email>` for a blank-NAME record, so a naked `if _fmt_actor(x)` check emits a fragment the contract forbids; guard on `.get("name")` like `_fmt_ownership` does (evidence: refute-read Finding 1 — blank-name owner leaked an `owner:  <email>` fragment until the name-guard was added)  [folded foundation-version 45 · from per-stream-owner]
- (TDD) a "no-false-positive" test must build its fixture through the REAL constructor (CLI/new-task), not a hand-rolled partial record — a partial dict passes the guard then crashes a DOWNSTREAM consumer, masking what the test means to prove (evidence: the first regex-false-positive test built a task dict missing `gate` → cmd_status KeyError, not the guard; fixed by `new-task`).  [folded foundation-version 44 · from merge-guard]
- (TDD) a substring assert on a 1-char slug (`assertIn("t", out)`) is vacuous — incidental letters in the PASS line satisfy it; assert the QUOTED form (`"'t'"`) so the test actually pins provenance (evidence: refute-read Finding 2, tightened in this build)  [folded foundation-version 44 · from state-doctor]
- (ADD) a fail-closed guard that REPLACES a generic error with a specific one belongs at the single shared read seam, routed into every caller — not duplicated per call site; the callers' existing `except` must catch only the GENERIC failure (Exception subclasses) so the specific `_die`/SystemExit propagates past them (evidence: merge-guard routed 3 read sites through one `_state_text_or_die`; the review's #1 refutation target was a swallowed SystemExit — avoided precisely because SystemExit ⊄ Exception).  [folded foundation-version 44 · from merge-guard]
- (ADD) a "REPORTS instead of aborts" diagnostic must be tested against TYPE-corrupt (not just parse-corrupt) state — the refute-read found an AttributeError path the 6 contracted scenarios missed; the design-for-failure promise only holds with an explicit type-robustness scenario (evidence: test_doctor_reports_not_aborts_on_type_corrupt_state added post-review)  [folded foundation-version 44 · from state-doctor]
- (TDD) when a parser NORMALIZES input (extracts a name from `"<...>"`), validate the PARSED value, not the raw arg — a raw `.strip()` check let `--owner "<>"` write a blank name (evidence: review BLOCK on ownership-model; the red test only covered raw whitespace, missing the parsed-empty case).  [folded foundation-version 43 · from ownership-model]
- (ADD) a second record-typed field that shares the actor `{name,email,source}` shape (owner/assignee, after gate_actor/done_actor) confirmed a reusable surface pattern: one `_fmt_actor` + a thin per-feature `_fmt_*` wrapper + a present-only render guard — adding a surface is now a 3-edit recipe (report_data row + render block + status line) (evidence: ownership-surface reused identity-in-status's exact shape with zero new primitives).  [folded foundation-version 43 · from ownership-surface]
- (ADD) the descriptive-additive stamp still rippled an exact-diff invariant test (test_retro `changed <= {status,updated}`) — an "additive" record write needs a census sweep for tests that pin a record's EXACT key-set, not just its values (evidence: test_close_state_diff_is_status_only went red until done_actor was ratified into the allowed set)  [folded foundation-version 42 · from actor-stamping]
- (ADD) a write-then-render ordering coupling: when a render reads a state field, the field must be set BEFORE the render that persists it (RETRO.md), or the persisted artifact diverges from the canonical recompute (evidence: cmd_milestone_done wrote done_actor AFTER `_write_retro`, so the saved RETRO.md lacked the `closed by` line the report re-render adds — fixed by reordering the stamp before the retro write).  [folded foundation-version 42 · from identity-in-status]
- (ADD) a present-only render helper must default-read every key (`actor.get('name','')`, not `actor['name']`) so a hand-edited/partial state record degrades to empty, not a KeyError crash (evidence: python-expert refute-read NIT; hardened `_fmt_actor`).  [folded foundation-version 42 · from identity-in-status]
- (TDD) a byte-identity + pin guard proves the copies MATCH, not that they still DO anything — a parity backstop for a feature must also assert the feature's BEHAVIOR survives (born-migrated init · migration · the verbs · the render), else a refactor can keep 3 files identical+pinned while silently dropping the feature (evidence: this task's hardening guards exist precisely to close that blind spot)  [folded foundation-version 41 · from engine-repin-parity]
- (TDD) a behavior-preserving refactor's regression hides where NO test arranges the precondition — the stale-scalar path needed a task created BEFORE the replace-to-focus `new-milestone`; add a coverage case for each pre-existing guard a routing change subsumes (evidence: test_archive_deactivates_from_set created zero tasks, so the dropped guard read green)  [folded foundation-version 41 · from multi-active-commands]
- (TDD) a "byte-identical at N≤1" claim needs a test that LOCKS the unchanged path (the N=1 rollup `*`, the N=1 json shape), not just one asserting the new path's ABSENCE — else the oracle can't catch a future regression in the boundary (evidence: review NIT — the absence-only tests left the rollup-mark change unproven until the hardening assertions were added)  [folded foundation-version 41 · from parallel-status-view]
- (ADD) a global find-and-replace that routes accessors will also rewrite the accessor's OWN body into self-recursion — introduce the helper, then route, then re-fix the two helper bodies (evidence: the _active_milestone/_active_task RecursionError caught at first test run, this task)  [folded foundation-version 41 · from active-accessors]
- (ADD) a backstop/audit task is honest TDD when each guard is PROVEN to bite under the regression it names — green-on-correct-engine is fine IF the bite is demonstrated (transient real-file drift for the file guard; in-memory predicate for the rest), not assumed (evidence: independent review flagged the 2 in-memory "bites" tests as demonstrations-not-guards until the docstrings named the scope + the out-of-band real-drift proof was recorded)  [folded foundation-version 41 · from engine-repin-parity]
- (ADD) a frozen contract can hold an INTERNAL tension — here "replace the clear-pair with `_deactivate_milestone`" collided with the frozen "every N≤1 decision unchanged" invariant; the literal instruction REGRESSED the invariant. Resolution: honor the structural instruction (route through the SET writer) AND restore the invariant additively (a back-compat guard), rather than treat either clause as the whole truth (evidence: independent verify-gate review found the BLOCK that the green suite missed because no test exercised a non-primary archive with a live scalar)  [folded foundation-version 41 · from multi-active-commands]
- (ADD) a frozen presentation-only render still has a guarded SURFACE — `status --json` is ratified by an explicit sanctioned-keys test; adding keys is a census co-update (extend the sanctioned set, keep base immutable + the equality tight), not a silent append (evidence: test_wave_status_hint.test_json_surface_frozen went red on the 2 new keys until ratified)  [folded foundation-version 41 · from parallel-status-view]
- (ADD) an engine-editing milestone should run a verify-gate independent review by default — it caught a false self-audit WIRING claim (a third undocumented load seam) that a manual refute-read had passed over (evidence: python-expert review nit 2, this task)  [folded foundation-version 41 · from state-schema-migration]
- (TDD) interactive-TUI tests need a non-zero PTY winsize (e.g. 80×24 via TIOCSWINSZ) or the emulator wraps per-character and substring markers never match (evidence: happy-path raised prompt_timeout until the winsize was set in pty_clack.py)  [folded foundation-version 40 · from pty-clack-harness]
- (TDD) a test that greps its OWN source for a literal token is self-referential and unpassable; assert object identity / `__module__` instead (evidence: HelperReuseTest had to be redesigned mid-build)  [folded foundation-version 40 · from pty-clack-harness]
- (ADD) a flag-first freeze flag naming the riskiest unknown ("clack under a stdlib PTY") localized the ACTUAL bug site — flag-first paid off (evidence: the §3 ⚠ assumption was exactly the winsize defect)  [folded foundation-version 40 · from pty-clack-harness]
- (ADD) the tamper tripwire correctly forced human review of build/verify test edits; the human-approved re-baseline (phase tests → re-advance to re-snapshot) is the sanctioned path, not a launder (evidence: gate PASS blocked until re-baseline this loop)  [folded foundation-version 40 · from pty-clack-harness]
- (ADD) the engine measures §0 grounding from content INLINE on the `Anchors the contract cites:` line — a following bullet list reads as empty → false `task_not_grounded` (evidence: check warned not-grounded until the anchors were inlined on that line)  [folded foundation-version 40 · from pty-clack-harness]
- (TDD) every NEW interactive prompt ripples into existing interactive tests that feed fixed stdin — make trailing OPTIONAL prompts EOF-tolerant (skip on exhausted stdin), so they don't re-break sibling tests (evidence: the scope step broke 3 sibling pip-interactive tests at EOF→cancel, needing a nav stdin edit; the intent step, made EOF→skip, broke none).  [folded foundation-version 39 · from intent-handoff]
- (ADD) when a build legitimately ripples into sibling-test files, declare them in §5 and re-anchor (re-cross tests→build) BEFORE the gate; surface the ripple at the gate (human-confirm if it touches a frozen-pin file, auto-resolve otherwise) — never silently (evidence: global-first-scope touched test_installer_prompts' happy-path stdin → human-confirmed; intent-handoff touched only its own task-3 test → auto-resolved).  [folded foundation-version 39 · from intent-handoff]
- (TDD) a test that inherits the ambient agent env (CLAUDECODE under Claude Code) silently changes behavior between local and CI — scrub the signal to pin the intended scenario deterministically (evidence: test_installer_handoff passed in CI but failed locally until its runners scrubbed the agent env)  [folded foundation-version 38 · from agent-detect]
- (TDD) for a COPY/snapshot feature, assert on CONTENT + ABSENCE (new state mirrored · deleted file gone · managed trees NOT present), never just "the dir exists" — presence-only tests pass for the wrong reason (evidence: §6 earned-green read).  [folded foundation-version 38 · from global-data]
- (TDD) a "propagate FROM X" contract where, at runtime, X is rebuilt from the same fixture the test seeds, is UN-distinguishable by a naive presence test — assert the SOURCE is complete instead of trying to prove which source was read (evidence: review N2 → §6 hardening asserts the home holds skill/add+tooling+docs).  [folded foundation-version 38 · from global-install]
- (TDD) interactive/clean-replace IO is best proven by real on-disk asserts on a synthetic bundle (mirrors test_update.py) rather than mocking the copy — keeps the green earned (evidence: all 11 heal tests assert real file content/absence, caught the orphan-sweep + fail-closed behaviors)  [folded foundation-version 38 · from heal-reconcile]
- (TDD) interactive TUI flows aren't feedable via piped stdin (clack raw-mode); test branch-reachability via a CONTRACTED force seam ({"1","fail"}) + the happy path via a PTY probe — the seam is fault-injection, not a logic-deleting stub (evidence: earned-green refute-read passed; pty probe closed the M1 gap).  [folded foundation-version 38 · from installer-prompts]
- (ADD) "detect + auto-correct the agent" splits cleanly into a PURE detect (unit-testable) + a fail-soft WRITE (mirror the existing marker-injector, same markers so the canonical writer supersedes it) — never a second source of truth for the block (evidence: test_init_supersedes_pointer proves sync-guidelines replaces the drop-time pointer in place)  [folded foundation-version 38 · from agent-detect]
- (ADD) env-signal detection should degrade to a SAFE default that equals prior behavior, so a wrong guess is never harmful — gate the feature on graceful fallback, not signal accuracy (evidence: every unmatched env → the generic AGENTS.md path proven agent-portable by test_agent_portability)  [folded foundation-version 38 · from agent-detect]
- (ADD) a task whose word ("persist") spans a spectrum (snapshot↔sync↔restore) should freeze the SAFE subset (one-way, can't clobber) + seed the rest as deltas, rather than over-build under full-auto (evidence: D-A1 → one-way mvp + restore/sync deltas).  [folded foundation-version 38 · from global-data]
- (ADD) a frozen-contract INTERNAL inconsistency found at build (here: "propagate from <home>" but the home layout lacked the skill source MANAGED needs) is a legit CHANGE REQUEST — re-freeze (v2) + re-cross contract→tests→build BEFORE coding around it, never a silent code-around (evidence: §3 v2 mirror change).  [folded foundation-version 38 · from global-install]
- (ADD) for the riskiest task in a milestone, an INDEPENDENT adversarial review subagent is a proportionate stand-in for the human gate under full-auto — and its disclosed NITs should be CLOSED (test-hardening) before the PASS, not just filed (evidence: review found N5/N2; both addressed pre-gate).  [folded foundation-version 38 · from global-install]
- (ADD) a refactor that collapses a structural shape (two-arg copy → one MANAGED mapping) silently breaks structural-regex tests OUTSIDE the declared §5 scope — disclose + re-aim the regex to the new shape, never weaken intent (evidence: test_v8_install::test_cli_bundles_brain went red on the MANAGED collapse, fixed by re-aiming to `"skill/add"`)  [folded foundation-version 38 · from heal-reconcile]
- (ADD) a refactor leaves orphaned helpers (copyDir/_warn) behind — sweep dead code in the same loop and re-run the full suite to prove nothing referenced them (evidence: both removed, suite held 1226 green)  [folded foundation-version 38 · from heal-reconcile]
- (ADD) an ESM-only dep forces a CJS installer to dynamic-import() + go async; keep the non-interactive path await-free so exit-code/stdout ordering the piped tests assert is preserved (evidence: A1 flag held; clack 1.x is type:module; full suite stayed green after the async refactor).  [folded foundation-version 38 · from installer-prompts]
- (TDD) a presence-only assertion can pass for the WRONG reason when the artifact already holds similar tokens — S4's first form leaned on the pre-existing `## Tasks` checkboxes (`whole_boxes > exit_boxes` was true before any build); pin the NEW artifact's contribution specifically (count Close+Release boxes), not a whole-file delta (evidence: S4 green-at-red until tightened)  [folded foundation-version 37 · from close-section-template]
- (ADD) this milestone dogfooded itself — the ship-review machinery (template task 1 · guide task 2 · book task 3) is exercised by the milestone's OWN close, the honest first-lived-run pattern that proves the feature on its author (evidence: exit criterion 4 fills the very `## Close — ship review` section task 1 shipped)  [folded foundation-version 37 · from close-book-accord]
- (ADD) the §5 scope-gate caught a real declaration gap and is anchored at the tests→build crossing: a repo-root file needs the `add-method/../<file>` climb (a "/"-bearing FILE token — bare names resolve as siblings) and the wholesale `_bundled/` tree a single directory token; a §5 fix after build requires RE-CROSSING tests→build to re-anchor the snapshot (editing §5 alone is not picked up). Disclosed tradeoff: re-anchoring after the edits means that gate run re-diffs nothing — integrity here rests on the green suite + parity + tamper-tripwire, not the scope diff (evidence: scope_violation returned-to-build attempt 1→2 until the re-cross)  [folded foundation-version 37 · from close-book-accord]
- (ADD) "point, don't duplicate" between two guides is testable as a structural proxy — assert the pointer (the other file is named) AND the absence of the other file's distinctive tokens (its reject codes) — rather than trying to prove non-duplication directly (evidence: test_L2 design)  [folded foundation-version 37 · from close-guide]
- (ADD) the freeze flag must be PERSISTED in TASK.md §3 as `Least-sure flag surfaced at freeze:`, not only surfaced in chat — the `unflagged_freeze` guard blocks tests→build until the line exists (evidence: `advance` rejected with `unflagged_freeze` despite the flag being shown at the freeze report)  [folded foundation-version 37 · from close-section-template]
- (TDD) run the FULL downstream + tool-ENVIRONMENT scan (here: which dirs the scope-walk excludes vs. which tools write to the tree) BEFORE freezing — the spec-delta-guards "scan downstream before freeze" lesson extends past test assertions to the agent's own toolchain side-effects (evidence: the serena-cache HARD-STOP would have been foreseen by a pre-freeze tool-artifact scan).  [folded foundation-version 36 · from fold-command]
- (TDD) a new SUBCOMMAND ripples into test_min_pillar's LIFECYCLE census, which derives the command set from `sub.choices` DYNAMICALLY — grep `LIFECYCLE`/`sub.choices`/`_NONZERO_OK` before adding a subcommand, not just `add_parser`/`--help` (evidence: `drop-delta` tripped test_every_subcommand_is_covered after a clean pre-build grep, forcing a §5 expansion + re-cross)  [folded foundation-version 36 · from seed-and-drop]
- (TDD) before removing a template/placeholder field, grep its downstream consumers first — observe-reading tests broke on the removed legacy `Spec delta for the next loop:` line (evidence: test_report.py 2 regressions surfaced only at full-suite run)  [folded foundation-version 36 · from spec-delta-grammar]
- (ADD) the §5 scope-walk must prune code-intelligence tool caches (`.serena`), else an agent's OWN source edits churn the cache, the build-entry snapshot bakes it in, and the gate flags a false out-of-scope touch that exhausts the heal loop to a false HARD-STOP (evidence: fold-command verify HARD-STOP, attempts 1–3, cache empty yet still flagged because the snapshot recorded it).  [folded foundation-version 36 · from fold-command]
- (ADD) a frozen "any failure → write nothing" clause that spans N files needs a TWO-PHASE commit (stage-all → rename-all); N independent atomic writes give only per-file atomicity and can leave a silent partial (evidence: fold-command verify refute-read found a flipped-but-untranscribed silent-loss path, closed via `_atomic_write_many` + foundation-first ordering).  [folded foundation-version 36 · from fold-command]
- (ADD) verb-vs-flag sizes the census ripple: a new FLAG on an existing command (`--from-delta`) adds no subcommand and is census-free, but a new SUBCOMMAND (`drop-delta`) costs a LIFECYCLE entry — declare the census file in §5 up front whenever a task adds a subcommand (evidence: the flag was free, the verb was not)  [folded foundation-version 36 · from seed-and-drop]
- (ADD) a §5 BUILD scope for an `add.py` parser change must pre-list the test mirrors, `engine_pin.py`, and the 3 byte-identical dogfood copies up front — the change ripples to all of them (evidence: scope under-declared mid-build forced a tests→build re-cross to re-anchor the tripwire)  [folded foundation-version 36 · from spec-delta-grammar]
- (ADD) pre-freeze downstream analysis (grep exact-match assertions + the subcommand census + compact-fixture SPEC injection) eliminated ALL mid-build surprises here — task 2 hit a census surprise + scope expansion; task 3 pre-checked the same classes and hit ZERO. Codify "scan downstream test assertions before freezing an additive engine change" as a §0/§5 step (evidence: task 3 needed no §5 expansion, no re-cross)  [folded foundation-version 36 · from spec-delta-guards]
- (ADD) seed a downstream task from a prior's SPEC delta via `new-task --from-delta`, not plain `new-task` — else the source delta stays `open` and (now) BLOCKS compaction even though the work is done; the live `status` showed 3 open SPEC deltas that tasks 2/3 had already implemented (evidence: the guard this task shipped surfaced its own milestone's un-seeded lineage — resolve at delta-resolution close)  [folded foundation-version 36 · from spec-delta-guards]

- (ADD) **A presentation convention ships as a single-source trail and dogfoods its own gates.** A cross-cutting UX
  refinement (here: the guided choice — a highlighted ▶ recommended pick + 1–3 described alternatives) ships as ONE
  specifying source (`report-template.md`) → a one-line cue in every human-gate guide → a describing-not-respecifying
  book + GLOSSARY entry; it never adds a gate or re-freezes a contract (it is the presentation/layout layer that
  iterates WITHOUT a re-freeze). Validate it by dogfooding it on its OWN gates — the milestone-confirm, the §3 freeze,
  and the verify gate all rendered as the very guided choice being built. A MILESTONE exit criterion that
  over-enumerates the work (a phantom 9th "human-gated-advance" gate) is reconciled to the real set (the 8 guides;
  phase-advance is engine-mechanical, its human moments fold into the freeze + verify gates) as the recorded
  change-as-method move, never a silent edit. `after EVIDENCE` and `Least-sure flag surfaced at freeze:` are PARSED
  prose tokens a guard reads — the literal label is the machine seam, not decoration.
- (ADD) **Discriminate autonomy by change-TYPE, not milestone theme.** Within one milestone a method-DEFINING task (it
  writes a new convention/contract others build on) runs `conservative` + `risk: high`; a method-APPLYING or pure-docs
  task runs `auto`. suggestion-block (defined the convention) ran conservative; gate-wiring + suggest-book-align
  (applied + described it) ran auto. The axis is the KIND of change a task makes, decided per task — not the theme it
  shares with its siblings.
- (TDD) **A prose feature's red suite splits RED feature-token tests from STAY-GREEN invariant guards.** "Red for the
  right reason" comes from the feature-token tests (the new prose absent → fail); the invariant guards (N-home md5
  parity · five-block · no-new-tag) ride green from the start and catch regression during the multi-home edit. Two
  guide-lint hazards: match CLOSING tags only (`</tag>`) — real block tags are paired but prose placeholders
  (`<name>`,`<slug>`) never close, so a `</?tag>` matcher false-positives; and a per-guide tag-vocab check uses the FULL
  closed-5 vocab (the on-demand guides intake/scope/release carry the engine-doc tags `constraints`/`reject_codes`, not
  just the phase-guide trio). A repo-root book copy is declared in §5 with the `add-method/../<name>` climb (a
  slash-bearing token resolves at project root; a bare `<name>` resolves as a SIBLING of the previous token's dir, so
  the root copy goes undeclared) — and §5 scope is anchored at the tests→build crossing, so a declaration fix must
  re-cross tests→build to re-anchor (reaffirms fv29 §5-scope-frozen-at-tests→build).
- (ADD) **The RELEASE scope level is an engine that RECORDS, never acts — and its one security reject is
  un-forceable.** `add.py release <version>` is guarded like `cmd_stage` with a SINGLE deliberate divergence: the
  `release_security_open` check runs FIRST and carries NO `not forced` guard, so `--force` can never reach it
  (the un-forceable reject, cleanly modeled as an unguarded leading check). It then RECORDS only — prepends
  `CHANGELOG.md` + appends one newest-first `RELEASES.md` row + attributes the bundled milestones — and NEVER
  writes `state.json`, tags, publishes, or deploys (attribution lives in RELEASES.md membership, so the
  `→ releasable` cue re-reads the ledger and release stays a pure 2-file write with a CHANGELOG-rollback if the
  2nd write fails). Because a tool-agnostic engine cannot run the suite, `release_tests_red` is a recorded-evidence
  PROXY (an in-flight build with no green gate); the human's real run is the `release.md` readiness backstop.
  `release` writes `CHANGELOG.md` at the project ROOT — a repo with a different convention (e.g. a nested-package
  root pointer) gets release blocks prepended ABOVE its content (preserved, not clobbered); reconcile per repo.
  [release-command — folded foundation-version 34]
- (ADD) **A new skill/docs prose surface must clear BOTH wording fences, and the bare-word fence's code-span
  exemption is PER-LINE.** Two fences guard wording: the phrase-level `wording_lint`/WORDING_RUBRIC (skill/add +
  appendix-b only) AND the stricter bare-word `test_ubiquitous_language` over the EXTENDED surface (skill + docs +
  README + templates), which bans `fold`/`altitude`/`seam`/… as whole words in prose (inline-code-span-stripped
  before matching). That strip is PER PHYSICAL LINE: a backtick span (e.g. `` `milestone-done → fold → …` ``) that
  WRAPS to a second source line leaves the first line's banned tokens exposed — keep a code-span arc on ONE line.
  Adding a skill GUIDE also auto-joins the wording-lint surface, so BOTH its surface-count guards (count +
  membership) must bump in the SAME build. [release-guide + release-docs-align — folded foundation-version 34]
- (ADD) **The subcommand census self-maintains — register a new verb additively.** A new `add.py` subcommand
  reddens `test_min_pillar.test_every_subcommand_is_covered`; register it additively in `LIFECYCLE`, and if it can
  legitimately exit non-zero at its census slot (a guarded WRITER like `release` that refuses on its floor) add it
  to `_NONZERO_OK` alongside `heal`/`wave-verify`. (Reaffirms the fv29 `§5-scope-frozen-at-tests-build` rule: the
  scope gate reads `declared` from the state.json ANCHOR snapshotted at tests→build, so a mid-build scope
  expansion must amend §5 AND re-cross tests→build, never just edit the prose.)
  [release-report + release-command — folded foundation-version 34]
- (ADD) **An appended book chapter chains forward-only; prior chapters stay byte-frozen.** Appending ch.16 (zero
  renumber churn) means chapters 00–15 keep their existing nav footers — ch.16 cannot repair the prior chapter's
  "Next:" link without breaking the byte-parity that made the append cheap. The Contents/README index is the
  authoritative link; an append-friendly book trades perfect prev/next adjacency for byte-stability.
  [release-docs-align — folded foundation-version 34]
- (TDD) **Release & docs guards: test the durable invariant and the rename-trap, on a real harness.** Patterns that
  earned their keep this milestone: a docs-ACCORD guard asserts the flow arc appears VERBATIM in BOTH the book AND
  its source guide (`release.md`), buying a "rename re-reds" property cheaply without duplicating byte-parity (owned
  by the parity tests); design-for-failure rollback is testable by monkeypatching `_atomic_write` to fail on the
  2nd write (assert the 1st file rolls back + state unchanged); an "engine-untouched" guard must assert a DURABLE
  invariant (the engine never references the guide FILE), never "no <feature> command" (a sibling task legitimately
  adds that command); the §3 freeze flag label is a parsed MACHINE TOKEN (`unflagged_freeze` requires the literal
  `Least-sure flag surfaced at freeze:`); and mirroring the `graduation_data` harness (temp project + `add.main`
  capture + direct state seeding) produces honest RED-first tests with zero throwaway scaffolding.
  [release-command + release-report + release-guide + release-docs-align — folded foundation-version 34]
- (TDD) **A docs-content guard earns its keep by cross-checking the SOURCE, not just asserting the target — and a
  content-reference test must be scoped to its evidence section AND assert a REAL artifact.** `test_docs_accord`
  intersects book ∩ `design.md` (`test_beats_are_sourced_from_the_guide`), so a beat rename can't pass by editing only
  the book — the book is forced to FOLLOW the guide. Symmetric vacuity hazard: a "the capture is cited in TASK.md"
  test vacuously matched the §4 test-plan's OWN literal `captures/welcome.png` prose until hardened to a §6-scoped
  reference + a file-exists assert. Newest face of words-exist≠method-works / presence-necessary-not-sufficient.
  [book-glossary-align + capture-evidence — folded foundation-version 33]
- (ADD) **The scope-walk's `_SCOPE_EXCLUDE_DIRS` omits tool caches — a mid-verify MCP/tool write (`.serena/cache/`)
  shows as an out-of-scope touch and would escalate at the gate.** The workaround is to re-anchor (`phase tests` +
  `advance`) AFTER the cache settles so the snapshot baselines it; the DURABLE fix is adding `.serena` to
  `_SCOPE_EXCLUDE_DIRS` alongside `.git`/`.add`/`__pycache__`/`node_modules` (a recorded forward engine task). A scope
  gate that walks the live filesystem must exclude every regenerable tool-state dir, not only VCS/build junk.
  [book-glossary-align — folded foundation-version 33]
- (ADD) **The release-gate forward-pin migration belongs in the SAME `chore(release)` commit as the version bump.**
  Cutting 1.5.0 bumped the 3 version sources + the CHANGELOG but left `test_release_1_4_0.py` pinned at 1.4.0,
  reddening the suite (the pinned release test + the `test_shared_engine_pin` five-guards aggregator that re-runs it)
  until migrated in a follow-up (`d8bc376`). A version bump and its forward-pin migration (rename → bump VERSION,
  prepend the prior version to PRIOR_VERSIONS, retarget FEATURE_ANCHORS, repoint the aggregator's importer list) are
  ONE atomic release step, never two. [book-glossary-align — folded foundation-version 33]
- (TDD) **A presence/substring assertion is vacuous when the asserted token ALSO lives in a sibling section, a
  header comment, or fixture scaffold — anchor the assertion to a UNIQUE new marker (or the parsed VALUE token),
  and keep the wording-lint inside the prose green bar.** Three faces this milestone: `set conservative` "passed"
  only because the autonomy header COMMENT enumerates `manual < conservative < auto` (assert the parsed value, not
  the whole line); a whole-file substring greened on sibling Run-mode vocabulary until the suite scoped to a unique
  `kickoff` / `## 2c` marker region; and the wording-lint caught "dial" slang the content tests would have passed,
  so a prose freeze is not green until the lint is too. The newest face of words-exist≠method-works /
  presence-necessary-not-sufficient. [autonomy-command + setup-suggest-milestone + setup-domain-deepdive +
  setup-run-mode — folded foundation-version 32]
- (TDD) **When a build (or a sibling census) needs a NEW or CHANGED test, reopen to TESTS and re-snapshot — editing
  a test during BUILD trips the tamper tripwire (build_tampered).** The honest loop is `phase tests → advance`
  (re-snapshot) `→ build`. Dogfooded twice: a dag-scheduler guard test discovered at build, and the soul-self-improve
  wording-surface census guards (count 25→26) registered in a REOPENED tests phase, never in build. Reinforces the
  fv29 mid-build-CR-trips-tamper bullet. [dag-scheduler + soul-self-improve — folded foundation-version 32]
- (ADD) **A MUTABLE first-class state needs a real CLI verb AND a wording fence — a verb alone leaves the
  command-shaped prose that lures the phantom-command hallucination.** `autonomy` was the only mutable first-class
  state with no `add.py` verb, so an agent under `auto` hallucinated `add.py autonomy` and derailed; closing the
  failure class needed BOTH `add.py autonomy show|set` AND a WORDING_RUBRIC fence banning the command-shaped idiom on
  the agent surface. [autonomy-command — folded foundation-version 32]
- (ADD) **A hand-written-input parser that reads only the FIRST matching line (re.M, no re.S) silently drops a
  WRAPPED continuation — it LOOKS complete but isn't, surfacing the build's legitimate touches as a scope_violation
  at the verify gate.** `_declared_scope` parses only the first `Scope (may touch):` line, so a wrapped §5 scope
  dropped its continuation tokens (pin re-aim · bundle sync · census co-updates) → declare scope on ONE line (or fix
  the parser); a silent truncation is worse than a loud reject. Reinforces fv28 hand-written-input-parsing-discipline.
  [autonomy-command — folded foundation-version 32]
- (ADD) **The verify adversarial refute-read is not ceremony, and reuse inherits correctness.** The refute caught a
  real HIGH bug all 9 first-pass tests missed (transitive blocking not propagated, so a task whose only dep was a
  blocked sibling was mis-scheduled into wave 1); and because the read-only `waves` reporter REUSES the existing
  `_dep_satisfied` predicate, the base was correct for free — the bug lived only in the NEW transitive layer.
  [dag-scheduler — folded foundation-version 32]
- (ADD) **"Show before ask" and "auto deepens DRAFTING, never the gate" extend to the SETUP / foundation altitude.**
  A default-flip ships as a PROPOSAL + comparison table + confirm-to-keep (the human sees the flow before owning it);
  and under autonomy=auto the per-drive domain deep-dive auto-completes its turns with full context but NEVER skips
  the human baseline approval (the lock). [setup-run-mode + setup-domain-deepdive — folded foundation-version 32]
- (ADD) **The AI's VOICE is a first-class human-owned living doc (SOUL.md) with its OWN propose→confirm→rewrite loop
  (soul.md) — distinct target from competency deltas: voice routes to SOUL.md, not the foundation.** Self-improvement
  now runs TWO routed loops sharing one discipline (the AI proposes, the human confirms, only then the append-only
  newest-first write) but distinct homes. Ship identity content as a test-UNLOCKED PROPOSED starter — the gate attests
  the mechanism while the human keeps the voice (the tests assert the schema, never the tone words). [soul-artifact +
  soul-self-improve — folded foundation-version 32]
- (ADD) **A frozen contract's NON-BINDING detail can collide with reality discovered at build — honor the binding
  rule, DISCLOSE the deviation at the verify gate for the human to rule, never silently retrofit the frozen prose.**
  Two faces this milestone: an ILLUSTRATIVE integer (§3 said §Spec "19→9"; the binding RULE rolled 18→10 — one
  old-positioned bullet carried an fv21 reinforcement cite) and a PROSE-SKETCH heading (§3 sketched `## Seam`, but a
  SEPARATE frozen engine guard `test_slang_absent_extended_surface` bans "seam" on the surface → shipped
  `## Distinct from add.py compact`). In each, the realization honored the binding/harder thing and ESCALATED the
  deviation AT the gate — a disclosed boundary lets the human rule the reach explicitly instead of the AI guessing it,
  and the §3 prose is left frozen, not retrofitted. Reinforces "the change-request is the method working" + "a
  security-line emerges at build → ratify at the gate". [compact-contract + apply-compaction + compact-guide +
  invariant-amend — folded foundation-version 31]
- (TDD) **A destructive in-place transform is made safe by a FROZEN pre-state snapshot + a shared parser used by BOTH
  the test and the transform — turning "newest-first kept-run reversed, stable tail rolled" into an exact list-equality
  assertion that catches any drop or reorder, never a vacuous set check.** apply-compaction froze `snapshot_before.json`
  and shared `compaction_lib.split` so the test asserts the exact reordered+rolled list against the pre-state; a
  byte-identical multi-home edit is likewise provable by an md5-parity test + a fail-closed verbatim-transform script
  (invariant-amend). [apply-compaction + invariant-amend — folded foundation-version 31]
- (TDD) **A presence guard is vacuous when the token recurs elsewhere or the behavior goes unobserved — pin the OWN
  ENTRY by native format AND assert REAL enforcement + a delete-the-impl refute.** (a) `assertIn(term, file)` greened
  even with a glossary term's OWN entry deleted, because the term string recurs inside another entry's body — pin it by
  the home's native format (`**Term** —` bold / `term:` colon) and mutation-prove the guard bites (compact-book-align).
  (b) A "git ignores X" / behavioral feature is verified by REAL `git check-ignore` enforcement + a refute (delete the
  impl → the test fails), never by asserting the pattern STRING is present (gitignore-scaffold). The newest faces of
  "words-exist≠method-works" / presence-necessary-not-sufficient. [compact-book-align + gitignore-scaffold — folded
  foundation-version 31]
- (TDD) **A never-clobber / preserve-existing guard cannot run RED pre-build — doing nothing already satisfies "leave
  the file unchanged" — so disclose it as a green regression guard, never manufacture a vacuous RED.** The honest red
  suite reds on the CREATE / ENFORCE drivers; the preserve guard is named as a disclosed green-throughout regression
  guard, not faked red to look like a driver. [gitignore-scaffold — folded foundation-version 31]
- (ADD) **The scope-walk EXCLUDES `.add/` (`_SCOPE_EXCLUDE_DIRS`), so a task that ALSO edits files under `.add/` gets
  ZERO scope-gate coverage there — declare the canonical `add-method/…` files and treat the `.add/…` twins as
  ride-along.** Only the canonical tree is gated; a `.add/` twin (the md5 mirror, a dogfood scaffold, a
  `git rm --cached`) is synced by hand and confirmed by the task's own md5-parity test, never by the scope gate — so the
  gated anchor must be the canonical file, never the `.add/` copy. [gitignore-scaffold + apply-compaction — folded
  foundation-version 31]
- (ADD) **A convention-guided method contract (the engine stays judgment-free — no `add.py` command) is still TDD-able
  via a prose contract doc + structural asserts; and amending a frozen-invariant DOC means reconciling EVERY
  position-describing sentence, not just the named clause.** compact-contract froze `compaction-contract.md` and pinned
  it with structural tests though zero engine code changed; invariant-amend's newest-first re-freeze had to reconcile
  every "appends one row / at the bottom" sentence across fold.md + PROJECT + CONVENTIONS + the book, because coherence
  spans the whole ritual, not the one clause the change names. [compact-contract + invariant-amend — folded
  foundation-version 31]
- (ADD) **Two authoring rules for method-surface milestones: build in the build phase, and deliver per-step
  context as thin pointers.** (a) Authoring the implementation during SPECIFY makes the tests→build snapshot
  capture an already-built tree, so the scope-gate becomes a no-op — write code IN build so the gate
  meaningfully checks touched ⊆ declared. (b) Richer per-step AI context belongs in ONE shared doc
  (`advisor.md` / `confidence.md`) reached by a thin per-guide pointer, never inline prose — progressive
  disclosure kept the 8 guides minimal (applies single-source-point-not-restate to per-step hooks).
  [advisor-strategy + per-step-hooks — folded foundation-version 30]
- (TDD) **A content guard that enumerates the FULL set it covers + asserts mutual distinctness defeats both
  the missing-item cheat and the boilerplate cheat.** `test_per_step_hooks` lists all 8 phase guides and
  asserts each Advisor·Confidence hook is present AND distinct from its siblings — a count/membership pair
  plus distinctness is the test-pattern for any "every X carries a non-boilerplate Y" doc requirement.
  [per-step-hooks — folded foundation-version 30]
- (SDD) **A new skill-engine doc silently trips two surface-inventory guards — register AND declare it
  before tests→build.** Adding `confidence.md` / `advisor.md` reddened `test_xml_convention.ENGINE_FILES`
  (registration) and the `test_wording_lint` surface COUNT at the same time; both must be named in §5 Scope
  before the tests→build cross, or the frozen anchor records an undeclared touch. Sharpens
  §5-scope-frozen-at-tests-build for the new-engine-doc case: the inventory guards, not just the prose,
  define the scope a method-surface task must declare. [advisor-strategy — folded foundation-version 30] **Re-validated at
  foundation-compaction:** shipping the new surface guide `compact-foundation.md` reddened the wording-lint COUNT (24→25) + the
  membership assert (`test_surface_files_cover_the_contract`) at once — fold the count+membership registration into §5 Scope up
  front, before the tests→build cross. [compact-guide — flip-cite foundation-version 31]
- (ADD) **Every state-CREATING seam needs its state-REMOVING transition specified in the SAME contract — and a
  shared-cap cross-source escalation test, not a same-source one.** Declared→undeclared had no cleanup path
  until a verify refute disclosed it (v3 change-request). Proving a SHARED violation cap is distinct: seeding the
  counter from one source (tamper) then triggering a different source (scope) is the only assertion that
  distinguishes a shared cap from parallel independent caps.
  [scope-gate-enforce + scope-violation-heal — folded foundation-version 29]
- (ADD) **The §5 scope declaration is FROZEN into `state.json`'s anchor at tests→build — editing §5 prose alone
  cannot clear a scope violation.** Only a full tests→build re-cross (reopen → contract → tests → advance)
  re-baselines the anchor. Sibling caveat: sibling-session commits landing on the shared branch mid-task can redden
  unrelated guards; the full-suite-before-gate rule catches and routes them rather than letting the gate record
  over them. [next-footer-engine + scope-decl-template — folded foundation-version 29] **Re-validated at foundation-compaction:**
  compact-guide's scope_violation PERSISTED after editing §5 prose alone until a `phase tests`+`advance` re-cross re-anchored the
  declared list (check 14→13 warnings); compact-book-align hit it again for two repo-root book copies. The live-run re-cross form is
  `phase tests → advance` (no `reopen` mid-task). [compact-guide + compact-book-align — flip-cite foundation-version 31]
- (ADD) **A human-approved mid-build change-request trips the tamper tripwire — the honest re-arm is
  `phase tests → advance`, never a gate override.** The tripwire snapshots the red test paths + §3 at tests→build;
  any edit (even a legitimate, human-approved bundle change) re-fires it. The path: reopen → contract → tests →
  build → re-advance (re-snapshot). Worth one line in run.md so agents do not read `build_tampered` as a cheat
  signal. Distinct from strengthening a test at VERIFY (close-gap-before-gate), which ALSO trips build_tampered
  and follows the same honest path. [scope-decl-template + udd-design-template — folded foundation-version 29]
- (ADD) **The engine-pin idiom has three mandatory parts: re-aim the slug annotation AND bump the md5 AND carry the
  PRIOR task's "re-aimed @ <slug>" marker.** (1) The self-test (`test_pin_annotation_names_this_task`) is part of
  the idiom, not optional — omitting it from the red suite means a stale annotation only surfaces at verify. (2) A
  same-task verify re-cross updates ENGINE_MD5 WITHOUT changing the `re-aimed @` slug — the slug names the TASK,
  the md5 names the build. (3) The prior task's annotation test asserts its marker survives; if the re-aim
  overwrites it, that sibling test goes red.
  [gate-owner-marker + udd-catalog-content-schema + next-footer-engine — folded foundation-version 29]
- (TDD) **String-PRESENCE asserts under-enforce a structured-prose contract — add STRUCTURE asserts.**
  `assertIn(anchor)` misses ordering, table form, and OR-halves (a non-hex literal passed presence); a prose
  contract with layout/order obligations needs asserts that enforce those dimensions. Reinforces
  words-exist≠method-works applied to prose tests specifically. [udd-design-template — folded foundation-version 29]
- (TDD) **The verify-gate adversarial refute earns its keep even on an honest, green build: conformant fixtures test
  the happy grammar, not the fail-closed promise.** Three traversal/validator tasks confirmed this in one milestone:
  (a) a total-function (never-raises) probe + a wrong-JSON-type input must be in the red suite FROM GROUND — 13
  conformant scenarios all passed yet missed an AttributeError on non-object input; (b) a COMPOSING validator needs
  first-class "no-double-flag" boundary tests — the build green missed 3 double-flag shapes; (c) a recursive
  validator needs a "never-skip-a-subtree / no phantom children" probe — 10 behavior scenarios passed while a
  `$value` node with non-`$` children skipped its whole subtree. In each case the verify refute, not the build,
  found the gap. Author these adversarial fixtures at red-suite time, not as verify residue.
  [udd-catalog-content-schema + udd-check-lint + udd-token-schema — folded foundation-version 29]
- (SDD) **A contract that broadens an engine verb-set must (a) NAME the verb CLASS, not "every verb", and (b) map
  which frozen tests lock the old shape before freezing.** "Every mutating verb" swept setup/lifecycle verbs whose
  bespoke output must NOT converge; the collision with test_brownfield_scan surfaced only at a 909-test full-suite
  run, forcing a post-build change-request. Naming the class (workflow vs setup vs control) at the freeze makes the
  scope precise; mapping the frozen test surface makes the collision a freeze-blocker, not a build surprise.
  [next-footer-engine + gate-owner-marker — folded foundation-version 29]
- (SDD) **Contract completeness has three mechanical checks at freeze: (1) every Reject code is SATISFIABLE by the
  frozen signature — a reject needing a parameter the signature never receives ships dead; (2) every Reject code has
  a matching §4 test line — an asymmetry here shipped 2 untested codes past a green build; (3) structural/containment
  rules must be STATED, not implied — "a token is a leaf (no child tokens)" and "props is an object, children is an
  array" each existed only in the validator, never in the frozen §1, so a verify refute found both gaps after green.**
  Apply all three as a freeze-time self-lint over the Reject table before the human approves.
  [udd-catalog-content-schema + udd-check-lint + udd-token-schema — folded foundation-version 29]
- (ADD) **Design-for-failure on a concurrency invariant: the check SHIFTS, never SKIPS, when its evidence cell is
  unsatisfiable.** Relocate the guarantee (pre-spawn rev-parse → worker step-0 echo + merge-time verify), never drop
  it — an unsatisfiable check that silently lifts un-guards the invariant it existed for. [wave-protocol-runtime — folded foundation-version 28]
- (ADD) **A folded runtime-exception must be MIRRORED onto every protocol surface it governs.** One surface carrying
  the rule while a sibling protocol file contradicts it re-opens the prose-only gap the fold closed (the cross-surface
  recursion v19 delta #7 named). [wave-protocol-runtime — folded foundation-version 28]
- (ADD) **Close-gap-before-gate converges.** A disclosed non-finding observation routed as a MICRO change-request (one
  contract sentence · one red fixture · one-line fix · targeted re-refute) closes in a single short cycle and lets the
  gate record a clean PASS instead of a PASS-with-asterisk — disclosure plus a small honest loop beats waving residue
  through. [engine-merge-base-enforcement: pass-6 N12 → v4 — folded foundation-version 28]
- (ADD) **Grounding probes against MUTATING engine verbs run in a sandbox, never the live project.** A §0 `new-task`/
  `use` probe polluted live state.json and needed a git restore; read-only verbs may probe live, mutating verbs never.
  [engine-argv-portability — folded foundation-version 28]
- (TDD) **Token-presence + ×N-mirror-parity is the honest test shape for a prose-discipline change with no executable
  engine hook.** Lock the WORDS and the MIRROR; let the adversarial refute-read confirm the words carry mechanism —
  red→green works on prose exactly like code when the assert is a vocabulary token. [wave-protocol-runtime — folded foundation-version 28]
- (TDD) **A red suite for a PARSER of hand-written artifacts must include grammar-DRIFT fixtures, not only
  template-conformant ones.** Ten conformant tests stayed green across six contract-violating false-greens that only
  adversarial probing surfaced — conformant fixtures test the happy grammar, not the fail-closed promise.
  [engine-merge-base-enforcement: refute passes 1–4 — folded foundation-version 28]
- (TDD) **A refute-read's coverage gaps route as NEXT-LOOP deltas, never post-hoc test edits.** After the tests→build
  snapshot the suite is tamper-guarded; hardening it in place reads as tamper. The honest absorb-point is the next
  freeze (a change-request re-snapshot) — exactly how the 11 refute-discovered wave vectors became pinned fixtures.
  [engine-argv-portability — folded foundation-version 28]
- (SDD) **When a spec's enforcement crosses a seam the engine cannot observe, NAME the enforcement-deferral explicitly
  at the freeze.** Prose must never masquerade as enforcement: the frozen flag that declared the spawn-time fork-base
  check DEFERRED to a future engine task is what made the gap honest — and what engine-merge-base-enforcement closed.
  [wave-protocol-runtime — folded foundation-version 28]
- (SDD) **Parsing a hand-written artifact: exactly-one-match + terminator-explicit — never substring-first-wins, never
  regex-`\b`.** Two clauses, one discipline. A label lookup must match EXACTLY ONE candidate (>1 → refuse as malformed,
  naming the collision) — first-wins on hand-written input is fail-open by construction: a decoy `fork-base-prev` label
  stole the echo column. And a keyword token must name its terminators (whitespace/separator/end-of-line) or use exact
  token equality — `\b` fires at `|` and `-`, so the unfilled template placeholder `live|merging` parsed as its valid
  prefix and greened an unfilled ledger on both surfaces. [engine-merge-base-enforcement: refute passes 4–5 — folded foundation-version 28]
- (SDD) **Two how-we-author sharpenings.** (1) A staged method needs a scope guard that fails if a LATER stage's
  machinery leaks BACKWARD into an earlier stage's prose — assert the later tokens ABSENT from the earlier guide so each
  stage describes without pre-empting the next's enforcement. (2) When a new feature needs the exact file set an existing
  counter resolves, extract a path-returning helper and delegate the counter to it (one resolution source), never
  re-glob — the snapshot and the engine then agree by construction. [verify-integrity: earned-green-rubric + tamper-tripwire — folded foundation-version 27]
- (ADD) **A security-line classification can EMERGE during build, not only at the §3 freeze — surface it for human
  ratification AT the verify gate, never self-grant.** When a build discovers a property that deserves HARD-STOP weight
  (md5-as-tamper-evidence), the reasoning holding is not licence to self-check the box: present it as an explicit ask.
  [verify-integrity: tamper-tripwire — folded foundation-version 27]
- (TDD) **An engine change that legitimately invalidates an EXISTING assertion makes the test edit an EVOLUTION, not a
  weakening — iff three hold: the real invariant stays guarded, coverage holds-or-rises, and the reason is documented.**
  The reusable discriminator behind "split, never loosen": when the landed behavior makes an old assertion false (a
  first tamper now returns-to-build, not dies), move the assertion to the new truth while keeping the real invariant
  strict (`gate=="none"`) and letting coverage rise (1→3 cheat tokens), then disclose every touched file at the gate.
  The independent refute-read is the backstop that judges evolution-vs-weakening when no test can. [verify-integrity: heal-then-escalate — folded foundation-version 27]
- (ADD) **A mechanical-HARD-STOP guard = snapshot at a phase seam → re-check at the gate before any completing outcome
  → fail-closed; and a self-heal cap is real only if it cannot be cleared without a recorded human action.**
  Generalizable to any "freeze X at phase A, enforce at phase B" (the tamper-tripwire snapshots md5(test paths + §3) at
  tests→build, re-checks at verify). The bounded loop returns a confirmed cheat to BUILD for an honest redo and counts
  attempts MONOTONICALLY — never auto-resetting, because the phase verb is unguarded (a tests→build re-cross would
  otherwise zero the counter with zero human action); after the cap it forces the HARD-STOP. [verify-integrity: tamper-tripwire + heal-then-escalate — folded foundation-version 27] Validated under real fire: engine-merge-base-enforcement ran the loop to its cap TWICE — 3 honest src-only redos, then heal_exhausted HARD-STOP escalations the human routed as change-requests; refute→heal→re-refute converged to two consecutive EARNED passes. [flip-cite — folded foundation-version 28]
- (ADD) **Build-integrity needs a mechanical floor AND a judgment ceiling — and a confirmed cheat is HARD-STOP-class.**
  The tamper-tripwire catches the cheats it can SEE (a test or the frozen §3 edited after the red run, by md5); the
  earned-green refute-read the ones it cannot (src overfit to fixtures · vacuous asserts · stubbed-away logic) — neither
  layer alone closes the gamed-green gap. The mechanical floor lives in agent-writable state.json, so it is
  necessary-not-sufficient: a co-witness flag raises the forgery cost (forge two, not one) but a determined agent
  patching both still slips — the adversarial read + the human gate stay the real backstop. A confirmed cheat is never
  auto-passed nor RISK-ACCEPTED-waived, exactly like security. [verify-integrity: earned-green-rubric + tamper-tripwire + heal-then-escalate — folded foundation-version 27]
- (TDD) **A prose feature is RED-greenable by token-presence guards; triage the RED split.** A prose/template task's
  red suite splits into two halves: "the feature is missing" (the NEW behavior — must be red before build) and "the
  invariants still hold" (must stay green throughout); triaging the split confirms the red is the new behavior, not
  a broken invariant. Pin the behavior by token presence — assert `"subagent"`+(`"index"`|`"skim"`), `"deepen"`,
  `"working folder"` — so the phrasing stays free and only the behavior is locked. A prose-economics hint is as
  pinnable as a structural one. [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (ADD) **Dogfooding the shipped technique in-flight validates it.** The build of the sweep-cheap-then-deepen hint
  USED that very split — a haiku subagent ran the broad working-folder sweep (returning the ×3/×3 sync md5s + the
  guard list) while the main context deepened on the precise guard assertions, pre-mapping the `Anchors the contract
  cites:` measure line before the broaden touched it. The method proved itself by being the method that built it;
  reinforces "a method-defining task dogfoods its own rule." [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (ADD) **A capability can be ADDED as guide-prose recommendation while the engine stays tool-agnostic — the pin
  holds across the addition.** The gather-method hint RECOMMENDS a subagent; `add.py` spawns nothing (the
  orchestrating agent chooses the tool), so the engine stayed byte-identical to `engine_pin` through BOTH
  ground-context tasks. When a new method capability is advice, not mechanism, it lands entirely in the ×3 guide
  prose — no engine action, no new measure, no new gate — and the unchanged engine pin is the proof the line was not
  crossed. [ground-gather-hint — folded foundation-version 26]
- (ADD) **Ground has two axes — completeness (WHAT) and economics (HOW).** The §0 gather names not only WHAT to
  gather (the working-folder categories: docs/textbase · TODOs · config/manifests · data/fixtures, beyond code) but
  HOW to gather it — sweep the BROAD pass cheaply (a small-model subagent / fast index / skim, returning a compact
  map), then DEEPEN task-specifically on what THIS task needs. Naming the economics closes both failure modes at
  once: skipping context, and indexing the whole repo. A complete §0 is the task-relevant delta gathered
  cheaply-then-deeply, never a repo-wide scan. [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (ADD) **A ladder change grandfathers pre-existing tasks — retrofit to dogfood, never claim the lived run.** A
  phase inserted into the ladder grandfathers every existing task at its current phase (all three ground-phase
  tasks were created at `specify`, before `ground` existed). Retrofit the new §0 section onto each so the surface
  is dogfooded HONESTLY (it records the grounding that informed §3) WITHOUT claiming the task flowed THROUGH the
  new phase — which narrows the residual from "zero lived dogfood" to "zero lived runs STARTING at ground," the
  accepted ceiling recorded for the next milestone, never papered over. Reinforces "a method-defining task
  dogfoods its own rule." [ground-phase-engine + ground-bundle-wiring + ground-prose-align — folded foundation-version 25]
  **CEILING CLOSED at ground-context:** the FIRST lived ground run (a task created AT `ground`, not retrofitted)
  reached `grounded ✓` live, closing the "zero lived runs STARTING at ground" residual recorded here as the accepted
  next-milestone ceiling. [ground-context-sources — folded foundation-version 26]
- (TDD) **A prose guard derived from the engine constant self-maintains — a ladder change then satisfies it
  minimally.** Derive the test's expected set from the engine constant (`FLOW_PHASES = [p for p in add.PHASES if
  p != "done"]`) so a ladder change AUTO-propagates the prose requirement — adding `ground` to `PHASES` made
  `test_flow_diagram` REQUIRE ground in the mermaid + CHECKLIST with no test edit. The ladder change must then
  make the MINIMAL diagram/CHECKLIST edit to keep the suite green, deferring the narrative to the prose task; and
  guarding a checklist by an exact item-COUNT + a line BUDGET (`==6→7` items, `≤16` lines) makes "gains one line"
  a precise, self-checking change. The book diagram + CHECKLIST are a ladder-shape reaction class — extends the
  instrument-reaction guard family. [ground-phase-engine + ground-bundle-wiring + ground-prose-align — folded foundation-version 25]
- (ADD) **An additive measure-not-block surface stays byte-invisible to existing tests and copies the proven
  shape.** Two moves land a new engine surface for free: (a) SUPPRESS the no-op/legacy case so CURRENT output is
  byte-unchanged — every existing task's status is identical, zero existing output-tests need conforming, the
  dogfood `check` count is unmoved; (b) MIRROR the established measure-not-block shape verbatim — a human-readable
  `status` line + a never-red WARN riding the existing `warnings` array, never a new `--json` key (sidesteps the
  `json_surface_unsanctioned_key` landmine and the design churn). Reinforces "a harmless additive `--json` key
  still stays inside the frozen contract." [ground-bundle-wiring — folded foundation-version 25] **VALIDATED at the
  ground-context fold:** the TEMPLATE twin held — an additive `## 0 · GROUND` template LINE inserted BETWEEN existing
  fields was byte-invisible to the structure/token-pinning template guards (the suite grew with zero scaffold/render
  test broken), because template tests pin tokens + structure, not exact line-sets. [ground-context-sources — folded foundation-version 26]
- (TDD/ADD) **Mutating an ordered constant is an absolute-index hazard — grep the absolute forms first.**
  Inserting at index 0 of an ordered tuple (`PHASES`) silently shifts every ABSOLUTE index/slice (`PHASES[:7]`,
  `names[n-1]`, `i = p["n"]-1`) while RELATIVE logic (`PHASES.index(...)`) stays correct. Before mutating an
  ordered constant, grep the absolute forms and prefer relative derivations. [ground-phase-engine — folded foundation-version 25]
- (ADD) **Ground the contract in the real code before §3 — the ground phase's founding proof.** Reading the
  actual symbols a task touches (`PHASES` + every keyed function) BEFORE drafting the frozen contract pre-caught
  four shipping defects the spec alone would have missed — a `decide_data` else→`gate` seam mislabel, a
  `render_decide` seam_label `KeyError`, the `PHASES[:7]` structural-slice shifts (the index-hazard bullet), and
  header-parsed-vs-positional numbering — each surfaced during §0 grounding / the advisor pass, before build.
  Grounding INFORMS a human-approved contract, it never authors it; the `## 0 · GROUND` map records the anchors
  §3 cites. A phase-0 PREAMBLE earns prose in the FLOW chapter, not a dedicated step-chapter — preserving the
  "seven steps" brand and the lean-over-GSD rule (the engine pointer was already correct).
  [ground-phase-engine + ground-prose-align — folded foundation-version 25]
- (ADD) **A lint forces a SLOT, never honesty — the irreducible floor.** `(verify: <citation>)` on every
  exit criterion raises the goal-clarity floor (a citation MUST exist, an empty `(verify:)` does not count)
  but cannot prove the citation is real — `(verify: it works)` passes the lint (citation-theater). The
  engine raises the floor; the human still owns whether the citation is honest (autonomy is EARNED, not
  mechanically proven). Recurring face of necessary-not-sufficient; RESOLVING/running the cited verifier
  (a test that exists, a command that passes) is the recorded forward upgrade. [goal-auto-ready-gate — folded foundation-version 24]
- (TDD/ADD) **A live-only / never-retro guard must key on the milestone's terminal STATUS, not just the
  active-pointer + dict-membership.** A done-but-not-yet-archived milestone stays the `active_milestone`
  pointer (and in the dict) until `archive` clears it, so pointer-membership alone briefly flags a CLOSED
  milestone — the build keyed the `goal_not_auto_ready` WARN on the pointer and fired on a `status=done`
  milestone; the verify adversarial pass caught the Must #4 violation and closed it test-first
  (`status != "done"` guard + `test_done_active_milestone_not_flagged`, red→green). Reinforces
  verified-marker-scopes-forward (enforce live, never retro-red). [goal-auto-ready-gate — folded foundation-version 24]
- (ADD) **Anchor a declaration-token reader to a declaration POSITION — line-start or a `·`-separator,
  never a bare substring.** A freeform H1 title or quoted prose containing `token: value` must never be
  read as a declaration; the symmetric hazard is worse — a title faking a *lowered* rung can DEFEAT a
  guard that trusts the first match. Anchor every header-token reader (autonomy AND risk) to its
  declaration column. [init-auto-default — fixed @ 55d64d9 — folded foundation-version 24]
- (TDD/ADD) **A prose-accord guard pins EVERY surface the contract names, and a word-ban is blind to a stale
  multi-VALUED enumeration** — two faces of necessary-not-sufficient on a "prose ≡ enforcement" deliverable.
  (a) DocsAccordTest pinned 1 of the 4 surfaces frozen §4 named ("GLOSSARY + the autonomy docs ×3"), so 2
  shipped stale-green — caught by human review at the gate, not CI; enumerate every named surface or the accord
  is only as wide as the pin (same shape as the census whole-and-closed rule). (b) A word-ban catches a banned
  WORD, never a stale ENUMERATION — once a 3rd rung landed, "auto | conservative" descriptions read green to the
  slang fence; widen level-set prose by a structural/test pin or a manual sweep, never the vocab ban.
  [explicit-autonomy-dial — folded foundation-version 23]
- (ADD) **A new guard gains teeth without retro-redding its predecessors via a VERIFIED-MARKER.** Stamp the
  marker on the guarded crossing (the freeze/gate the guard newly governs) and enforce only on MARKED records;
  pre-marker records pre-date the rule and stay green — no fabricated retro-pass, no silent grandfather.
  Distinct from "adjudicate epoch debt at the human gate" (which retro-ratifies old records *by choice*; this
  scopes enforcement forward *by construction*). [unflagged-freeze — folded foundation-version 23]
- (SDD) **How-we-author contracts — five v22 sharpenings.** (1) A guarded transition must NAME its at-creation door
  (`init --stage`) as a `declared_at_init` boundary, or the "NEVER reaches S" silently leaks through a second door.
  (2) A data-shape-bounded reject clause NAMES its trigger (the first archived RISK-ACCEPTED/HARD-STOP) so it
  re-opens as a change-request the day the shape stops being empty, instead of under-reporting. (3) An assumption
  resolved-by-DESIGN yet milestone-spanning gets a *resolved-with-forward-watch* state (a §7 monitor), not a bare
  `[x]`/`[ ]`/⚠. (4) A MILESTONE-declared task slug is checked against existing `tasks/` (and archived) dirs before
  create — a collision would overwrite a done task. (5) Contract-freeze greps for the PRIOR contract that froze an
  extended `--json`/state seam and states additive-vs-closed explicitly. [graduate-guide + graduation-analytics + report-arc + stage-book-align + stage-goal-criteria — folded foundation-version 22]
- (TDD) **A new guard that invalidates an existing test's PREMISE is adapted by SPLITTING, never loosening — and
  disclosed at the gate.** Move the old guarantee to where it still holds (the bare flip → a non-guarded stage), add
  the new guarantee (refuse@0 / succeed@≥1 / --force), surface the touched files as a strictly-strengthening
  amendment for the human to judge. Reinforces "a strictly-strengthening in-build amendment is legal but never silent". [graduate-guide — folded foundation-version 22]
- (TDD) **A presence / marker / structural test is necessary-not-sufficient — it pins vocabulary or existence, never
  that the CLAIM holds or the behavior works.** A presence fence ("the term exists") is not a coverage fence ("the
  claim 'every X' is true" — the chapter named 5 of 7 wired gates, 690-green); a prose-marker test pins steps NAMED,
  not orchestration DRIVEN; a gather-not-judge invariant is asserted STRUCTURALLY (no verdict field in the schema),
  never via a word denylist that lags the contract. The human SEMANTIC read + the engine seam carry what the test is
  blind to — recurring face of "words-exist≠method-works". A presence test also proves a phrase EXISTS on ONE surface,
  never that two surfaces AGREE on its qualifier (a template read "for high-risk" while the guide read "recommended
  under auto"; every anchor test passed) — cross-surface qualifier agreement needs a shared render or an
  adversarial/human read. [arc-book-align + graduate-guide + graduation-analytics — folded foundation-version 22 · reinforced verify-integrity fv27]
- (ADD) **Reinterpreting or closing a contract sweeps the LOADED foundation prose for the stale shape, not just the
  test guard.** A green suite cannot catch prose drift (tests don't exercise docs); add "sweep loaded-layer prose
  for the old shape" to the change-request checklist (close-gap-before-gate). Reinforces stale-guard-sweep. [stage-goal-criteria — folded foundation-version 22]
- (ADD) **A cross-surface term can carry two axes — disambiguate before unifying, keep both senses + one bridging
  clause.** "scope level" (decision-granularity vs orchestration-loop) and "report" (the chat report at a decision
  point vs the verify gate's three Test/Quality/Risk reports) each carry two senses; never merge the lists.
  [stage-book-align + arc-book-align "report" polysemy — folded foundation-version 22] A lived working LABEL
  drifts from its canonical glossary TERM the same way — §3's "Least-sure flag surfaced at freeze" vs the
  glossary's "lowest-confidence flag" shipped bridged-not-migrated; introduce a working label only with a
  bridge ("formerly …") or migrate it in the same breath, never a silent rename. [unflagged-freeze — folded foundation-version 23]
- (ADD) **A gate report's FLAGS must reconcile with `add.py report --decide`'s open-item count before stamping —
  fix the data (the TASK.md markers), never the sentence.** Prose calling an item "resolved" while the digest still
  counts it open is the un-transparent gate the decision arc exists to kill. Now SHIPPED as report-template.md's
  reconcile rule. [report-arc — folded foundation-version 22]
- (ADD) **A multi-source report declares ONE traversal basis per tier (filesystem OR state), or the sets silently
  diverge under archival.** `open_deltas` globs `tasks/*` while residue/coverage iterate `state["tasks"]`; they agree
  only while every archived milestone is compacted out of `tasks/`. Same archive seam as the done-tally blind spot
  (§Domain). Pin each tier's source-of-truth in the contract or document the divergence. [graduation-analytics — folded foundation-version 22]
- (ADD) **To prove "X can NEVER reach state S", enumerate every WRITER of S — not the string-callers of the obvious
  command.** Grep every assignment to the guarded state field; a transition guard's completeness IS the full set of
  mutators (here: exactly two writers — `cmd_init` declared-at-init boundary + `cmd_stage` guard). [graduate-guide — folded foundation-version 22]
- (ADD) **A single-source rule is POINTED-to, never restated — and no presence test catches a verbatim restatement.**
  The reconcile rule folded into report-template.md was duplicated verbatim into 6-verify.md; only review caught it.
  A "traceable everywhere, defined once" design needs a no-restate lint or parity check, not a presence assertion
  (words-exist≠method-works, applied to single-sourcing). [arc-gate-wiring — folded foundation-version 22]
- (ADD) **The change-request is the method working, not a failure.** A frozen-contract gap caught at verify is
  fixed via reopen→contract→re-freeze (the live-run form is `add.py phase contract`; `reopen` is for DONE tasks),
  never a silent build edit; the §3 carries both freeze stamps. Reinforces "a frozen guard is fixed in the BUILD
  output / route it as a human-ratified change-request". [arc-book-align v1→v2 — folded foundation-version 22]
- (ADD) **Dogfooding a rule at its own gate is its first live proof — and catches what no test asserts.** Rendering
  the decision arc · running the reconcile rule · presenting a presentation-contract AT the very gate that ships
  it surfaced gaps every green suite missed: the 5-of-7 gate-coverage gap, the verbatim reconcile-rule
  duplication, the digest-vs-prose mismatch. Practice the rule on its own gate the session it lands — reinforces
  "a method-defining task dogfoods its own rule". Reinforced by verify-integrity: the first NORMAL task through a
  freshly-shipped guard is its cheapest end-to-end test (task 2 crossed tests→build under task 1's live tripwire,
  re-checked clean at the gate), and the method audits its OWN builds — dogfooding the earned-green rubric on task 3
  caught a real nit (a trivially-true assert) before the gate. [report-arc + arc-gate-wiring + arc-book-align — folded foundation-version 22 · reinforced verify-integrity fv27]
- (ADD) **The book has FOUR mirror trees — root · canonical · bundle · dogfood — and an APPENDIX's root copy is
  guarded by NO test.** Only CHAPTERS are cross-tree guarded (test_inline_citations + test_flow_diagram span all
  four incl. the repo-root published copy); an appendix's root copy drifts silently. A docs task syncs all four
  by hand and md5-confirms the appendix root leg — bundle-green is false comfort. Extends "Dogfood parity" /
  the mirror-clause-enumerates-ALL-copies family. [arc-book-align — folded foundation-version 22] **VALIDATED at
  the ground fold:** a byte-sync test added for a NEW term (`test_book_glossary_synced_x4`) caught the
  PRE-EXISTING repo-root appendix-c drift this bullet predicted — the root mirror had silently fallen a whole term
  behind canonical; a "synced ×N" guard pays for itself beyond the change that adds it, and the appendix-root leg
  is now guarded. [ground-prose-align — folded foundation-version 25] **Re-validated at foundation-compaction:**
  compact-book-align's §0 GROUND map UNDERCOUNTED the book mirror as ×3 when the engine mandates ×4 (the repo-root copy
  too) — ground a mirror-parity task's home-count from the engine's own `test_ground_prose._doc_trees`, never a
  hand-count; the ×3 miss surfaced as 6 sync-guard failures mid-build and a §3 ×3→×4 disclosure the human accepted at
  the gate. [compact-book-align — flip-cite foundation-version 31]
- (TDD) **A count-vs-set assertion guards an invariant only against the mutation it can see — name the blind
  spot, or a "latent guard" reads as a false all-clear.** "Exactly one entry per cite-key" has no dedicated
  uniqueness test; `test_appendix_g_frozen` asserts `len(set(keys)) == 27`, so an entry EDITED to collide
  collapses the set to 26 → red. But a 28th entry ADDED with a colliding key gives 28 lines / 27 unique → green:
  the entry count is only floored (`assertGreaterEqual(len(entries), 18)`), never pinned at 27. A dedicated
  uniqueness (or exact-count) assert therefore closes a REAL gap for the add-case — not optional hardening.
  The headline lesson a 4th time: `len(set)==27` is necessary, never sufficient, blind to the mutation no test
  names. [references-appendix — folded foundation-version 21; sharpened by advisor re-check]
- (TDD) **A cite-resolver that matches one [Author Year] per bracket reads the appendix's own `;`-joined form
  `[A; B]` as a single dangling key.** Split the bracket body on `; ` and resolve each key. A FROZEN test that
  predates the multi-cite form keeps the single-key limitation — copy its regexes into a NEW `;`-aware test,
  never refactor the frozen one (copy, don't couple). v21: 2 red→green fixes forced single-key brackets in
  foundations; inline-citations shipped the `;`-aware resolver + a real `[Schmidhuber 2003; Zelikman et al. 2023]`
  exercising the split. [foundations-chapter + inline-citations — folded foundation-version 21]
- (TDD) **A passing structural/resolution test over a grounding or prose deliverable is necessary, never
  sufficient — the human SEMANTIC check must carry what the resolver is blind to.** A resolver proves cites
  RESOLVE / sections EXIST / tokens are banned; it cannot see (a) **APTNESS** — whether the source grounds the
  claim: for any claim MORE specific than the appendix annotation, verify against the PRIMARY SOURCE, because
  the annotation fixed existence+title+author, not characterization depth; (b) internal **CONSISTENCY** — a
  counting pass ("three currents" over a four-currents heading slipped 642-green); (c) load-bearing **FIGURES**
  — spot-check each citable number against its source. Declare the §6 SEMANTIC blind-spots explicitly so green
  never reads as done. v21 hit this THREE times (form-test missed link-existence · resolution-test missed
  consistency · resolution-test missed aptness: [Yuan et al. 2024]'s "drifts" overstatement passed 649-green,
  caught only by WebFetch of arxiv 2401.10020 showing self-rewarding *improves*).
  [references-appendix + foundations-chapter + inline-citations — folded foundation-version 21]
- (ADD) **The instrument-reaction guard-class set depends on the ARTIFACT you ship.** A CLI verb trips three —
  the subcommand census (`test_min_pillar` LIFECYCLE), the `engine_pin` re-aim + 3-copy mirror, and the
  ubiquitous-language prose-ban on add.py literals. A NEW skill/doc FILE additionally trips two more — bundle/tree
  parity (the file-SET + byte-identity across the 3 skill trees) and the wording-lint surface-COUNT contract
  (shipping `loop.md` turned test_bundle_parity / test_tree_parity / test_wording_lint::surface red until each was
  updated). Pre-declare BY type: CLI verb → census + engine_pin + prose-ban; new skill/doc file → + bundle/tree
  parity + surface-count. Supersedes the "all three guard classes" note as artifact-keyed. [dynamic-task-loop — folded foundation-version 20] **v21 refinement:** a new `add-method/docs/*.md` ALSO trips the EXTENDED
  ubiquitous-language surface — `extended_surface()` globs every docs file + skill + templates + diagrams +
  README + GETTING-STARTED, not only the wording-lint surface-count; predict the EXTENDED surface for a new
  doc, not just the lint count. [references-appendix — folded foundation-version 21]
- (TDD) **Words-exist ≠ method-works.** Structural/string tests prove an artifact reads as worded, not
  that the behavior works or is enforced (recurring gap). Where behavior matters — md5 parity, an
  enforced default, real convergence — add a behavioral test, not a presence assertion.
- settled conventions fv2–fv20 — 67 method learnings rolled (early ADD/TDD/SDD discipline) (see git)
