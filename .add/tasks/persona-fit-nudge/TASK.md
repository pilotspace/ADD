# TASK: Persona domain-fit nudge

slug: persona-fit-nudge · created: 2026-07-05 · stage: mvp
milestone: persona-domain-fit
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add_engine/io_state.py:_personas_unseeded(root)` (bool — no REAL, non-template `.md` under `.add/personas/`); `add-method/tooling/add_engine/constants.py:PERSONA_HINT` (single-sourced hint string, `PERSONA_FRONTMATTER_KEYS = ("name", "vibe")`); 3 call sites in `add-method/tooling/add.py` (+2 byte-identical mirrors `.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`) all gated on `_personas_unseeded(root)`: `cmd_new_milestone` (prints `note: {PERSONA_HINT}`, active-arm only), `cmd_check` (`infos.append(("personas", f"unseeded — {PERSONA_HINT}"))`), and the `status`-printing function (`print(f"persona : {PERSONA_HINT}")`)
Context (working folder): `.add/personas/*.md` (this project's own 6 real personas: book-technical-writer, security-gatekeeper, method-product-owner, tdd-verifier, methodology-engine-dev, terminal-ux-accessibility — each `## Identity`/`## Critical Rules`/`## Default Requirement`/`## Success Metrics` + `name`/`vibe` frontmatter); `docs/18-personas.md` (the persona loop's own book chapter); the `add-persona` agent (roster's cross-cutting persona-selection/drafting service)
Honors (patterns / conventions): persona-seed-nudge's OWN established shape — single-sourced hint constant (never a per-callsite copy), non-blocking (`note:`/INFO/orientation-line, never a WARN or gate), NO-EXEC (the engine measures a structural predicate, content-quality/domain-fit judgment stays the AI's job via `add-persona`) — this task must NOT invert that separation by having the engine itself judge fit
Seams consulted: none cited
Anchors the contract cites: `_personas_unseeded`, `PERSONA_HINT`, `cmd_new_milestone`
Issues/Risks (→ feed §1): (1) genuine domain-fit judgment ("does any of these 6 personas actually cover THIS new milestone's domain") is semantic — only computable by the AI reading PROJECT.md/the milestone goal against each persona's own stance, never by the engine; a naive keyword-overlap heuristic in the engine would be a fragile, false-confidence proxy for that judgment, not a measurement — this is the central tension the freeze must resolve (see §1 lowest-confidence flag). (2) whatever new hint this task adds must stay MUTUALLY EXCLUSIVE with the existing `_personas_unseeded` nudge (never both firing on one invocation) or `new-milestone`'s output becomes noisy/contradictory for a project with zero personas.
Related intent: milestone `persona-domain-fit`'s own rationale — grounded directly against ai-proxy's real repo (8 real, git-tracked personas; the reported "missed personas folder" was not a literal missing-file bug, the actual gap is nothing hints at a NEW milestone/task whose domain none of the existing personas plausibly cover) [← persona-domain-fit]
Ground SHA: `90baca1`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py new-milestone <slug>` (the active, non-queued arm) ALSO prints a `persona-fit:`
  orientation line listing this project's existing REAL persona slugs whenever at least one
  exists (mutually exclusive with the existing unseeded `note: {PERSONA_HINT}` line), naming the
  add-persona fix path — so the AI is nudged to confirm domain fit or draft a new persona for the
  milestone just created, instead of silently reusing personas that may not fit.
Framings weighed: ALWAYS list existing persona slugs (existence-only, no content judgment) when
  ≥1 real persona exists (chosen — mirrors the proven existence-only pattern `status` already uses
  for its `context`/`voice` pointers; zero false-precision, and `new-milestone` is low-frequency
  enough not to be noisy) · a keyword/token-overlap heuristic between the milestone goal and each
  persona's own text, nudging only on zero overlap — rejected, a fragile false-confidence proxy for
  a semantic judgment the engine has no business making (risks both false negatives and false
  positives) · folding this into the SAME `_personas_unseeded`/`PERSONA_HINT` predicate (treating
  "may not fit" as another flavor of "unseeded") — rejected, conflates two genuinely different
  conditions with different wording behind one boolean · also nudging at `check`/`status` in v1 —
  rejected for now (mirrors persona-seed-nudge's own staged v1→v2 rollout: ship `new-milestone`
  only first, add the other surfaces later if it proves worth it)
Must:
<must>
  - M1: `add.py new-milestone <slug>` (active, non-queued arm) prints a `persona-fit:` line listing
    this project's existing REAL persona slugs (comma-joined) whenever `_personas_unseeded(root)`
    is False (≥1 real persona already exists)
  - M2: the new `persona-fit:` line and the existing unseeded `note: {PERSONA_HINT}` line are
    MUTUALLY EXCLUSIVE — never both printed for the same invocation (one predicate, opposite branches)
  - M3: the wording names the concrete fix path (`add-persona` agent / `docs/18-personas.md`),
    single-sourced in a new constant — never inline-duplicated (mirrors `PERSONA_HINT`'s own rule)
  - M4: a `--queued` milestone creation NEVER prints this hint (mirrors the existing unseeded
    nudge's own active-arm-only rule)
</must>
Reject:
<reject>
  - teaching the engine to compute/guess domain fit via keyword overlap or any content heuristic ->
    reject; content-quality/fit judgment is the AI's job via `add-persona`, never the engine's
  - printing the new hint on `check`/`status` in this v1 -> reject; scope for a possible later v2
  - printing BOTH the new hint and the existing unseeded nudge on one invocation -> reject; exactly
    one nudge fires per invocation
</reject>
After:
<after>
  - `add.py new-milestone <slug>` (active arm), when ≥1 real persona exists, prints a
    `persona-fit:` line naming the existing personas + the add-persona fix path
  - a project with ZERO real personas still gets only the existing `note: {PERSONA_HINT}` line —
    byte-identical to today for that case
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ printing this new hint on EVERY `new-milestone` call (rather than gating it on some heuristic
  signal of actual mismatch) trades precision for honesty about what the engine can measure —
  lowest confidence because it means even a project whose persona genuinely already fits gets a
  one-line reminder every time; if wrong: mildly noisy output for well-seeded projects (cheap to
  reverse — a pure prose/gating change, easily narrowed later if it proves annoying in practice)
  - [ ] should this hint also go out to `check`/`status` (matching persona-seed-nudge's own staged
  v1→v2 rollout), or stay `new-milestone`-only for v1 — leaning `new-milestone`-only (matches the
  precedent, avoids nudge fatigue); confirm at freeze
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: new-milestone with real personas prints the fit-check line   # M1
  Given a project with ≥1 real persona under .add/personas/
  When `add.py new-milestone <slug>` runs (active, non-queued)
  Then it prints a `persona-fit:` line listing the existing persona slugs
  And it names the add-persona fix path

Scenario: the two persona nudges never co-occur   # M2
  Given a project with ZERO real personas under .add/personas/
  When `add.py new-milestone <slug>` runs (active, non-queued)
  Then it prints the EXISTING `note: {PERSONA_HINT}` line
  And it does NOT print the new `persona-fit:` line

Scenario: the fit-check wording is single-sourced   # M3
  Given the new `persona-fit:` hint constant is defined once
  When all call sites that print it are inspected
  Then every one references the SAME constant, never an inline literal copy

Scenario: a queued milestone never gets the fit-check hint   # M4
  Given a project with ≥1 real persona under .add/personas/
  When `add.py new-milestone <slug> --queued` runs
  Then no `persona-fit:` line is printed
  And no `note: {PERSONA_HINT}` line is printed either (mirrors the existing queued-arm rule)

Scenario: the engine never computes domain fit itself   # R1
  Given the new hint's implementation
  When it is inspected for how it decides whether to print
  Then it is driven ONLY by `_personas_unseeded(root)` (existence, not content)
  And no keyword/token-overlap or other content-matching logic exists

Scenario: check/status stay untouched in this v1   # R2
  Given this task's declared scope
  When `add.py check` and `add.py status` are run against a project with ≥1 real persona
  Then their output is BYTE-IDENTICAL to before this task
  And no new `persona-fit:` line appears on either surface

Scenario: exactly one nudge per new-milestone invocation   # R3
  Given any project state (zero or ≥1 real personas)
  When `add.py new-milestone <slug>` runs (active, non-queued)
  Then at most ONE of {`note: {PERSONA_HINT}`, `persona-fit:`} is printed, never both
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION cmd_new_milestone(args)   body: { active, non-queued arm only }
  _personas_unseeded(root) is True  -> print(f"note: {PERSONA_HINT}")            (UNCHANGED)
  _personas_unseeded(root) is False -> print(f"persona-fit: {PERSONA_FIT_HINT}")  (NEW)
    where PERSONA_FIT_HINT names the existing persona slugs (comma-joined, sorted, excluding
    `_template`) + the add-persona fix path, single-sourced as a new constant next to PERSONA_HINT
  --queued arm: UNCHANGED — neither line ever prints (existing early-return structure preserved)
Schema: no new file, no new persona schema field; `add-method/tooling/add_engine/constants.py`
  gains ONE new string constant (`PERSONA_FIT_HINT` or equivalent name); `cmd_new_milestone`'s
  existing active-arm branch gains one `elif`/`else` printing it — `check`/`status` untouched
```

Glossary deltas: `persona-fit hint`: the `new-milestone` line printed when ≥1 real persona already
  exists, listing the project's existing persona slugs and pointing at `add-persona` — distinct from
  `PERSONA_HINT` (which fires only when ZERO real personas exist); the two are mutually exclusive,
  driven by the same `_personas_unseeded` predicate. [folded foundation-version 64]
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 (AskUserQuestion freeze-confirmation timed
  out with no response, proceeded per project-lead autonomy on the recommended, well-reasoned,
  low-risk option — disclosed here for review/reversal)
Reported: yes — this contract's summary + lowest-confidence flag were shown in-chat before freeze
Least-sure flag surfaced at freeze: [spec] printing the new `persona-fit:` line on EVERY
  `new-milestone` call once ≥1 persona exists, rather than gating on any actual mismatch signal —
  trades precision for engine honesty (no content-judgment heuristic); cost if wrong: a mildly
  repetitive one-line reminder for well-seeded projects, cheap to narrow later (pure prose/gating
  change, no schema/data impact).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of new branches (the new `elif` in `cmd_new_milestone` + the new slug-listing helper)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_milestone_prints_fit_line_when_real_persona_exists: arrange a project with 1 real
    persona / act `new-milestone` (active) / assert a `persona-fit:` line names the persona slug
    + the add-persona fix path · covers: M1
  - test_new_milestone_note_only_when_personas_absent: arrange zero real personas / act
    `new-milestone` (active) / assert the EXISTING `note: {PERSONA_HINT}` line prints and the new
    `persona-fit:` line does NOT · covers: M2
  - test_persona_fit_hint_is_single_sourced: arrange nothing (static inspection) / act read
    constants.py + add.py / assert exactly one `PERSONA_FIT_HINT_TEMPLATE`-shaped constant is
    defined and `cmd_new_milestone` references it (no inline literal copy) · covers: M3
  - test_queued_milestone_never_prints_fit_hint: arrange 1 real persona / act `new-milestone
    --queued` / assert neither `persona-fit:` nor `note:` prints · covers: M4
  - test_no_content_heuristic_in_source: arrange nothing (static inspection) / act read the new
    branch's source / assert no keyword/token-overlap/similarity logic exists — only
    `_personas_unseeded(root)` gates the branch · covers: R1
  - test_check_and_status_byte_identical_with_real_persona: arrange 1 real persona / act `check`
    and `status` / assert output has no `persona-fit:` line and is unchanged from pre-task
    behavior · covers: R2
  - test_exactly_one_nudge_per_invocation: arrange both a zero-persona project and a
    real-persona project / act `new-milestone` (active) on each / assert exactly one of
    {`note:`, `persona-fit:`} appears, never both, never neither · covers: R3
</test_plan>

Tests live in: `add-method/tooling/test_persona_fit_nudge.py` (project root — mirrors sibling `test_persona_milestone_nudge.py`) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py`, `add-method/tooling/add_engine/constants.py`, `add-method/tooling/add_engine/io_state.py`, `.add/tooling/add.py`, `.add/tooling/add_engine/constants.py`, `.add/tooling/add_engine/io_state.py`, `add-method/src/add_method/_bundled/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add_engine/constants.py`, `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py`, `add-method/tooling/test_persona_fit_nudge.py`, `add-method/tooling/engine_pin.py`, `.add/tooling/engine_pin.py`, `add-method/src/add_method/_bundled/tooling/engine_pin.py`, `add-method/tooling/test_persona_milestone_nudge.py`, `.add/SEAMS.md`
Strategy (ordered batches): 1. add `_real_persona_slugs(root)` next to `_personas_unseeded` in `io_state.py` (sorted, excludes `_template`) 2. add `PERSONA_FIT_HINT_TEMPLATE` to `constants.py` next to `PERSONA_HINT`, export it 3. wire the new `elif` branch in `cmd_new_milestone` (add.py) 4. mirror all 3 files byte-identical to `.add/tooling/` and the bundled tree 5. re-aim `engine_pin.py`'s `ENGINE_MD5` to the new live md5

Persona (optional): methodology-engine-dev
Spawn isolation (default): not spawned — small, single-file-cluster change done directly
Known-problem fixes: engine scope-anchor re-cross (hit twice this session) → declared Scope on ONE physical line up front, before tests→build crosses, to avoid a `build_tampered`/`scope_violation` false positive
Strategy actually used: as planned (5 batches), plus one unplanned addition: the pre-existing sibling
  suite `test_persona_milestone_nudge.py::test_new_milestone_silent_when_real_persona_exists`
  encoded the OLD, now-superseded behavior (fully silent once any real persona exists) and had to
  be narrowed to assert only that the OLD unseeded `note:` line stays silent — not that the NEW
  mutually-exclusive `persona-fit:` line is absent too (that line firing there is this task's whole
  point). Added that file + both `engine_pin.py` mirrors to Scope and re-crossed tests->build twice
  (`add.py phase build`) to refresh the scope-anchor snapshot before touching them — the same fix
  pattern already learned from `sweep-orphan-reclaim-tickets`/`fold-glossary-deltas`. Re-aimed
  ENGINE_MD5 + ENGINE_PKG_MD5 (both `add.py` and the `add_engine` package changed).
Safety rule (feature-specific): none — pure additive read-only string/prose change, no state mutation
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 2967/2967 green, full `python3 -m unittest discover` (exit 0)
- [x] coverage did not decrease — 2 new pure symbols, each covered by 2+ of the 8 new tests
- [x] no test or contract was altered during build — this task's OWN §3/§4 stayed frozen/untouched;
  ONE pre-existing sibling test (`test_persona_milestone_nudge.py`, from the already-DONE
  `persona-seed-nudge` task) was narrowed because its assertion encoded behavior this task's own
  frozen contract deliberately supersedes — disclosed in "Strategy actually used" above, added to
  Scope, scope-anchor re-crossed before touching it
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP) — see Refute-read verdict below
- [x] concurrency / timing of the risky operation is safe — no risky operation (pure read + print)
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor 3-lens below
- [x] layering & dependencies follow CONVENTIONS.md — mirrors `_personas_unseeded`'s existing layering exactly (io_state helper -> constants template -> add.py call site)
- [ ] a person reviewed and approved the change — reserved for the human/orchestrator gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-milestone` (active, non-queued) on a project with ≥1 real persona prints a `persona-fit:`
  line naming the persona slug(s) + the add-persona fix path — confirmed by
  `test_new_milestone_prints_fit_line_when_real_persona_exists` (green)
- [x] the same command on a zero-persona project prints ONLY the existing `note: {PERSONA_HINT}`
  line, never both — confirmed by `test_new_milestone_note_only_when_personas_absent` +
  `test_exactly_one_nudge_per_invocation` (green)
- [x] `--queued` creation never prints either hint — confirmed by
  `test_queued_milestone_never_prints_fit_hint` (green)
- [x] `check`/`status` output is byte-identical to before this task — confirmed by
  `test_check_and_status_byte_identical_with_real_persona` (green)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_real_persona_slugs` referenced once at `add.py:3482`, defined once at
  `add_engine/io_state.py:218`; `PERSONA_FIT_HINT_TEMPLATE` referenced once at `add.py:3483`,
  defined once + `__all__`-exported in `add_engine/constants.py` — confirmed via `grep -rn` +
  `python3 -c "import add; ... in dir(add)"` (all resolve True)
- [x] DEAD-CODE (code) — both new symbols have exactly one call site each; no orphaned helper
- [ ] SEMANTIC (prose / non-code) — n/a, this task is pure code (no book/doc prose changed)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites (`_personas_unseeded`, `PERSONA_HINT`, `cmd_new_milestone`,
  `PERSONA_FIT_HINT_TEMPLATE`, `_real_persona_slugs`) still resolves in the current tree —
  confirmed by direct `grep -n`/`python3 -c "import add"` re-resolution above
- [x] no anchor moved/renamed since Ground SHA `90baca1` — `cmd_new_milestone`'s existing
  `if _personas_unseeded(root): print(f"note: ...")` block stayed at its same location; only a
  new `else:` branch was appended directly beneath it

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: neutered the new `else:` branch's print call (replaced with
  `pass`) in `add-method/tooling/add.py` and re-ran `test_persona_fit_nudge.py` — 4/8 tests
  (`test_new_milestone_prints_fit_line_when_real_persona_exists`,
  `test_exactly_one_nudge_per_invocation`, `test_persona_fit_hint_is_single_sourced`,
  `test_persona_fit_nudge_source_parity`) correctly regressed to FAIL/red for the right reason
  (missing `persona-fit:` output / missing constant reference); restored the file byte-for-byte
  and confirmed 8/8 green again. Also confirmed the pre-existing sibling suite
  (`test_persona_milestone_nudge.py`, `test_persona_setup.py`) and the prose lint
  (`test_ubiquitous_language.py`) stay green (193 tests across the related-surface slice).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — pure stdout formatting of already-trusted local filenames (persona slugs
   derived from `.add/personas/*.md` stems, the same source `_personas_unseeded` already reads);
   no new file I/O, no new external input, no state.json write, no injection surface
2. Concurrency: CLEAR — read-only glob over an existing directory at print time; no lock, no
   shared mutable state, same read pattern `_personas_unseeded` already uses
3. Architecture: CLEAR — mirrors the existing `PERSONA_HINT`/`_personas_unseeded` single-sourced-
   constant + NO-EXEC separation exactly (engine measures existence, AI judges fit); no schema
   change, no new file, additive `elif` only
Verdict: PASS
Residue: none
Binding: advisory — sensitivity unset (base default)

### GATE RECORD
Reported: yes — the verify summary (evidence + disclosed side-effect) was rendered and approved
  before this outcome was recorded
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose ALWAYS list existing persona slugs (existence-only, no content judgment) when ≥1 real persona exists; rejected a keyword/token-overlap heuristic between the milestone goal and each persona's own text, nudging only on zero overlap — rejected, a fragile false-confidence proxy for a semantic judgment the engine has no business making (risks both false negatives and false positives) · folding this into the SAME `_personas_unseeded`/`PERSONA_HINT` predicate (treating "may not fit" as another flavor of "unseeded") — rejected, conflates two genuinely different conditions with different wording behind one boolean · also nudging at `check`/`status` in v1 — rejected for now (mirrors persona-seed-nudge's own staged v1→v2 rollout: ship `new-milestone` only first, add the other surfaces later if it proves worth it)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 (AskUserQuestion freeze-confirmation timed)
- [AI] build — strategy used: as planned (5 batches), plus one unplanned addition: the pre-existing sibling suite `test_persona_milestone_nudge.py::test_new_milestone_silent_when_real_persona_exists` encoded the OLD, now-superseded behavior (fully silent once any real persona exists) and had to be narrowed to assert only that the OLD unseeded `note:` line stays silent — not that the NEW mutually-exclusive `persona-fit:` line is absent too (that line firing there is this task's whole point). Added that file + both `engine_pin.py` mirrors to Scope and re-crossed tests->build twice (`add.py phase build`) to refresh the scope-anchor snapshot before touching them — the same fix pattern already learned from `sweep-orphan-reclaim-tickets`/`fold-glossary-deltas`. Re-aimed ENGINE_MD5 + ENGINE_PKG_MD5 (both `add.py` and the `add_engine` package changed).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · carried] should `check`/`status` also print the `persona-fit:` hint (matching [carried: deliberately deferred to a possible v2, mirroring persona-seed-nudge own staged rollout; revisit only if the new-milestone-only nudge proves insufficient in practice — no evidence of that yet]
  persona-seed-nudge's own staged v1→v2 rollout) — deliberately deferred in this task's §1 Reject;
  revisit if the `new-milestone`-only nudge proves insufficient in practice (evidence: none yet —
  a forward-looking option, not a known gap)

### Competency deltas
- [ADD · folded] a §5 Scope amendment made mid-build now has THREE known trigger shapes this [folded foundation-version 64]
  session (a wrapped multi-line declaration, a Scope addition after tests→build crossed, and — new
  this task — an OUT-OF-DECLARED-SCOPE doc file, `.add/SEAMS.md`, whose pinned `path:line` anchor
  silently drifted from an EARLIER, in-scope edit elsewhere in the same file it anchors into,
  `add.py`) — the engine has no way to warn "this edit may invalidate a line-number anchor
  elsewhere in the docs," so the drift was caught only by a full-suite run, not by `add.py check`
  at build time (evidence: `test_seams_doc.py::test_every_anchor_resolves` only failed once the
  full 2967-test suite ran, well after the targeted slice had already gone green)
- [TDD · folded] a broad substring-ban static-inspection test (banning "overlap" anywhere in [folded foundation-version 64]
  add.py) produced a false positive against unrelated, pre-existing prose ("...only overlaps
  builds...") — narrowed to scan just the new function's body instead of the whole file; a
  static-inspection test should always scope its search to the code it's actually asserting about,
  not the whole source file (evidence: `test_no_content_heuristic_in_source` first FAILed for the
  wrong reason before being narrowed)

