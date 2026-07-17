# TASK: Capture-evidence convention: design-confirm capture location/naming + @json-render/image default + add.py check missing_capture WARN + captures-in-TASK.md + reopen design.md beat 4

slug: capture-evidence · created: 2026-06-16 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from the project default (auto): engine/method-defining scope — a new `add.py check` never-red WARN (×3 engine copies + the ENGINE_MD5 pin) + a reopened design.md guide. The human owns the verify gate (run.md unguarded_high_risk_auto). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/tooling/add.py` `cmd_check` (~L1609) — the never-red WARN seam: `warnings: list[tuple[str,str]]` (L1630) printed as `WARN {name} {reason}` (L1788), counted in the summary, NEVER fed into `failed`. NEW: append a `missing_capture` WARN per prototype lacking a confirmed capture. Mirror byte-identical to `add-method/src/add_method/_bundled/tooling/add.py` + the dogfood `.add/tooling/add.py` (test_bundle_parity `test_add_py_byte_identical`).
- `add-method/tooling/add.py` `_udd_named_set_checks` (L1547) — prototype discovery: `proto_dir = design/"prototypes"`, `trees = …glob("*.json")` (L1557-1558); silent-when-absent (L1559-1560). The capture check parallels this discovery (likely a small pure helper `_missing_captures(root)` so it stays testable + read-only).
- `add-method/tooling/engine_pin.py` `ENGINE_MD5` (L13, canonical-ONLY) — re-aim the hard-coded md5 of add.py after the logic change (the 5 prose suites import it). No `_bundled`/dogfood copy.
- `add-method/skill/add/design.md` beat 4 `### 4 · render-capture-confirm` (L41-48) + `## Tool-agnostic capture` (L50-64) — reopen to add: captures live at a conventional path + are attached/mentioned in the feature's `TASK.md` + the `add.py check` missing_capture WARN + `@json-render/image` as the named-default capture engine. ×3 skill trees (`skill/add/`, `src/add_method/_bundled/skill/add/`, dogfood `.claude/skills/add/`) byte-identical (test_tree_parity + test_bundle_parity).
- `add-method/tooling/templates/udd-wireframe.md` "## Capture is evidence" — align: name the conventional capture location + `@json-render/image` default. ×2 template trees byte-identical.
- NEW test `add-method/tooling/test_capture_evidence.py` — asserts the WARN fires for an uncaptured prototype (never red) AND a captured image is referenced from a TASK.md (exit-criterion 4).

Context (working folder):
- the `.add/design/` named set (`tokens.json`·`catalog.json`·`prototypes/*.json`) is the existing UDD foundation shape (udd-check-lint, Fork A); THIS dogfood repo has NO `.add/design/`, so the new WARN MUST stay silent-when-absent or the 1131-green suite goes red.
- existing cmd_check tests (`test_udd_check_lint.py`, ~test_add cmd_check cases) build a temp `.add/design/` project — the harness pattern to reuse for `test_capture_evidence.py`.

Honors (patterns / conventions):
- **measure-never-block** — `missing_capture` is a WARN that never feeds `failed` (mirrors `goal_not_auto_ready` / `task_not_grounded` / scope-pending warnings on the same `warnings` array). cmd_check stays read-only, exit-1-iff-failed PRESERVED.
- **silent-when-absent** — no `.add/design/prototypes/` ⇒ zero new output (mirrors `_udd_named_set_checks`).
- **tool-agnostic / engine-never-renders** — the engine only MEASURES whether a capture exists; it never renders or screenshots (`capability-as-prose-recommendation-engine-tool-agnostic`).
- **milestone shared decisions** — captures-in-TASK.md (traceability) · `@json-render/image` earmarked default · two render tiers (floor + fast-path).
- engine change ⇒ re-sync 3 add.py copies + re-aim engine_pin.ENGINE_MD5.

Anchors the contract cites: `add.py cmd_check` + the `warnings` array · a pure `_missing_captures(root)` helper · the capture location/naming convention (`.add/design/captures/<name>.<ext>`) · the `missing_capture` WARN code (silent-when-absent, never-red) · `design.md` beat 4 + `udd-wireframe.md` capture section · `engine_pin.ENGINE_MD5` · `test_capture_evidence.py`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the capture-evidence convention — design-confirm captures live at `.add/design/captures/<name>.<ext>` (one per prototype), are attached/mentioned in the feature's `TASK.md`, and are produced by a tool-agnostic recipe whose named default is `@json-render/image`; + a never-red `add.py check` `missing_capture` WARN measuring which prototypes still lack a capture (the engine measures, never renders).
Framings weighed: WARN keyed on capture-FILE presence at `.add/design/captures/<name>.*` (chosen — deterministic, read-only, silent-when-absent) · WARN keyed on a TASK.md cross-reference (engine can't reliably map a prototype→its owning TASK.md; fragile) · a hard FAIL on a missing capture (rejected — violates measure-never-block; design is iterative). Capture dir: a sibling `captures/` (chosen — keeps `prototypes/` pure JSON) · co-located `prototypes/<name>.png`.
Must:
<must>
  - `add.py check` emits a never-red WARN `missing_capture` naming each prototype under `.add/design/prototypes/*.json` that has NO capture file `.add/design/captures/<name>.<ext>` (ext ∈ png·svg·jpg·jpeg·webp). It NEVER feeds `failed`; cmd_check stays read-only and exit-1-iff-failed is preserved.
  - silent-when-absent: with no `.add/design/prototypes/` (or zero prototypes), the check emits ZERO new output — clean / non-UI projects and THIS dogfood repo stay green.
  - the measure is a pure, total, deterministic helper `_missing_captures(root) -> list[str]` (read-only, never raises on a malformed/odd tree, document-order); cmd_check maps each returned name to one WARN.
  - the convention is DOCUMENTED on the agent surface: `design.md` beat 4 + `udd-wireframe.md` state captures live at `.add/design/captures/<name>.<ext>`, are attached/mentioned in the feature's `TASK.md`, name `@json-render/image` (Satori → PNG/SVG) as the recommended default, and keep the engine render-free.
  - the convention is DEMONSTRATED: a captured image is referenced from a `TASK.md` (this milestone dogfoods it — the worked welcome/settings captures are recorded in the task record), satisfying milestone exit-criterion 4.
  - ship discipline: the 3 `add.py` copies (canonical · `_bundled` · dogfood `.add/`) stay byte-identical and `engine_pin.ENGINE_MD5` is re-aimed to the new add.py; design.md ships byte-identical ×3 skill trees, udd-wireframe.md ×2 template trees.
</must>
Reject:
<reject>
  - a prototype `<name>.json` with no `.add/design/captures/<name>.*` -> "missing_capture"  (a never-red WARN — the named situation, not a failure)
  - `missing_capture` (or any capture logic) feeding `failed` / flipping cmd_check's exit code -> "capture_blocks"  (forbidden — measure-never-block)
  - the WARN firing when there is no named set / no prototypes -> "noisy_when_absent"  (forbidden — silent-when-absent)
  - the engine rendering or screenshotting to PRODUCE a capture -> "engine_renders"  (forbidden — tool-agnostic; the engine only measures file presence)
  - add.py logic changed but `engine_pin.ENGINE_MD5` not re-aimed, or a copy drifts -> "engine_pin_stale / parity_break"
</reject>
After:
<after>
  - on a project WITH prototypes but no captures, `add.py check` prints `WARN  missing_capture …` (one per uncaptured prototype) and still exits 0 if nothing else failed; adding the capture file removes the WARN. On a project with no `.add/design/`, output is unchanged. design.md + udd-wireframe.md document the convention; a TASK.md references a real capture; the 3 engine copies + pin are in sync; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] "confirmed capture" = a capture FILE present at `.add/design/captures/<name>.*` (chosen) vs requiring a TASK.md cross-reference — lowest confidence because exit-criterion 4 says "referenced from TASK.md", yet the engine cannot reliably map a prototype to its owning TASK.md (one screen may span tasks; a TASK.md may live anywhere). I split it: the ENGINE WARN measures file presence (deterministic, read-only); the TASK.md attachment stays a DOCUMENTED + DEMONSTRATED convention, not an engine-enforced link. If wrong (human wants the engine to verify the TASK.md link): the helper needs a fragile prototype→TASK.md resolver + a new reject.
  - [ ] [contract] capture dir is a sibling `.add/design/captures/` vs co-located `prototypes/<name>.png` — chose the sibling dir to keep prototypes/ pure JSON; if wrong: trivial path change.
  - [ ] [spec] ext allow-set png·svg·jpg·jpeg·webp — covers headless + @json-render/image (PNG/SVG) outputs; if too narrow: extend the set.
  - [x] never-red WARN on the existing `warnings` array is the right mechanism (milestone-confirmed: measure-never-block, mirrors goal_not_auto_ready).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# --- one per Must ---

Scenario: missing_capture WARN for an uncaptured prototype       # Must 1
  Given a project with .add/design/prototypes/welcome.json and NO .add/design/captures/welcome.*
  When add.py check runs
  Then output includes "WARN  missing_capture" naming welcome
  And the process still exits 0 (the WARN did not feed `failed`)

Scenario: silent when there is no named set                       # Must 2
  Given a project with no .add/design/ directory
  When add.py check runs
  Then no "missing_capture" line appears
  And the check output + exit code are unchanged from before this feature

Scenario: capture present clears the WARN                         # Must 1/3
  Given .add/design/prototypes/welcome.json AND .add/design/captures/welcome.png
  When _missing_captures(root) is called
  Then welcome is NOT in the returned list
  And the list is deterministic document-order and the call mutates nothing

Scenario: helper is pure and total on a malformed tree            # Must 3
  Given a captures dir with odd entries and a prototypes dir with a non-.json file
  When _missing_captures(root) is called
  Then it returns a list without raising
  And it reads only — no file is created or changed

Scenario: convention documented on the agent surface              # Must 4
  Given design.md and udd-wireframe.md
  When a reader looks for the capture convention
  Then both name ".add/design/captures/<name>" , "TASK.md", and "@json-render/image"
  And design.md still states the engine never renders

Scenario: convention demonstrated from a TASK.md                  # Must 5
  Given the capture-evidence TASK.md
  When test_capture_evidence inspects it
  Then it references a real captured image path (a .png/.svg under captures/)

Scenario: engine copies + pin stay in sync                        # Must 6
  Given the 3 add.py copies and engine_pin.ENGINE_MD5
  When the parity + pin guards run
  Then the 3 copies are byte-identical AND ENGINE_MD5 equals md5(add.py)

# --- one per Reject ---

Scenario: capture_blocks — a missing capture must never fail       # Reject
  Given prototypes present and zero captures
  When add.py check runs
  Then exit code is 0 (nothing else failing) and `failed` count excludes capture
  And the missing capture surfaces only as a WARN (unchanged: read-only, no _die)

Scenario: noisy_when_absent — no prototypes, no WARN               # Reject
  Given .add/design/ exists with tokens.json but no prototypes/
  When add.py check runs
  Then no missing_capture WARN appears
  And the existing UDD-foundation checks are unchanged

Scenario: engine_renders — the engine must not produce a capture   # Reject
  Given the missing_capture code path
  When it runs
  Then it only tests file existence (os.path / glob), never invokes a renderer/browser
  And no image file is written by the engine

Scenario: engine_pin_stale / parity_break — drift is caught        # Reject
  Given add.py logic changed
  When ENGINE_MD5 is not re-aimed OR a copy diverges
  Then the pin guard / test_bundle_parity goes red
  And shipping requires md5 re-aim + all 3 copies byte-identical
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
HELPER  _missing_captures(root: Path) -> list[str]      (add.py — pure · total · read-only · doc-order)
  design = root/"design" · proto_dir = design/"prototypes" · cap_dir = design/"captures"
  names   = sorted(p.stem for p in proto_dir.glob("*.json") if p.is_file())   # [] if proto_dir absent
  captured(name) = any((cap_dir/f"{name}.{ext}").is_file() for ext in CAPTURE_EXTS)
  CAPTURE_EXTS = ("png","svg","jpg","jpeg","webp")
  returns [name for name in names if not captured(name)]   # uncaptured, document(sorted) order
  NEVER raises (missing dirs -> []); NEVER writes.

cmd_check WIRING  (on the EXISTING `warnings` array — never `checks`, so never feeds `failed`)
  for name in _missing_captures(root):
      warnings.append(("missing_capture",
        f"prototype '{name}' has no design-confirm capture at "
        f".add/design/captures/{name}.<png|svg|…> — render + confirm it before build (design.md beat 4)"))
  - read-only; the "check: N passed, M failed (K warnings)" summary + --json schema + SystemExit(1)-iff-failed
    are PRESERVED (the new line only grows `warnings`); silent-when-absent (no prototypes -> [] -> no WARN).

DOC CONVENTION  (design.md beat 4 + "## Tool-agnostic capture", ×3 skill trees;
                 udd-wireframe.md "## Capture is evidence", ×2 template trees) — states:
  - captures live at `.add/design/captures/<name>.<ext>` (one per prototype <name>)
  - the capture is ATTACHED/mentioned in the feature's `TASK.md` (traceability of the approved screen)
  - `@json-render/image` (Satori -> PNG/SVG, no browser) is the recommended DEFAULT capture engine
  - `add.py check` WARNs (never red) for a prototype lacking a capture — `missing_capture`
  - the engine never renders (capture is a tool-agnostic recipe + named default)

DEMONSTRATION  (exit-criterion 4: "a captured image is referenced from TASK.md")
  the worked welcome + settings captures (rendered in task 2's verify) are committed to
  `.add/design/captures/` and REFERENCED from this task's §6 — a real design-confirm artifact in the repo.

REJECT CODES (named, observable)
  missing_capture   — a never-red WARN: prototype <name> has no captures/<name>.* (the named situation)
  capture_blocks    — FORBIDDEN: capture logic feeding `failed` / flipping the exit code
  noisy_when_absent — FORBIDDEN: a WARN with no prototypes present
  engine_renders    — FORBIDDEN: the engine rendering/screenshotting (it only tests file existence)
  engine_pin_stale / parity_break — add.py changed but ENGINE_MD5 not re-aimed, or a copy drifts

SHIP DISCIPLINE
  - 3 add.py copies byte-identical (canonical · _bundled · dogfood .add/) AND
    engine_pin.ENGINE_MD5 == md5(add.py)  (test_argv_portability L179)
  - design.md byte-identical ×3 skill trees (test_tree_parity + test_bundle_parity)
  - udd-wireframe.md byte-identical ×2 template trees (test_bundle_parity)

TOUCHES read-only / preserved: the prototype-discovery glob shape (reused, not reshaped) ·
  cmd_check's output format + read-only-ness + exit semantics · the existing UDD-foundation checks.
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-16
Least-sure flag surfaced at freeze: ⚠ [contract] "confirmed capture" = a capture FILE present at `.add/design/captures/<name>.*` (engine measures file-presence, read-only) vs an engine-verified TASK.md cross-reference; the TASK.md attachment stays a documented + DEMONSTRATED convention (real welcome/settings PNGs committed to `.add/design/captures/` + cited in §6), not an engine-enforced link. Human approved the file-presence model + committing the demonstration PNGs.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject; cmd_check integration over a temp .add/design/ (reuse the test_udd_check_lint harness) + helper unit tests + doc-surface asserts.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_missing_capture_warns (Must 1): temp project, prototypes/welcome.json + NO captures/ → run cmd_check (capsys/SystemExit) → stdout has "missing_capture" naming welcome AND exit 0.
  - test_silent_when_no_design (Must 2): temp project, no .add/design/ → cmd_check stdout has no "missing_capture" AND output/exit unchanged.
  - test_capture_present_clears (Must 1/3): prototypes/welcome.json + captures/welcome.png → _missing_captures(root) == [] AND a second call leaves the tree unchanged (read-only).
  - test_helper_pure_total (Must 3): captures dir with odd entries + a non-.json in prototypes/ → _missing_captures returns a list, no raise, writes nothing; multiple prototypes → sorted order.
  - test_convention_documented (Must 4): design.md + udd-wireframe.md each contain ".add/design/captures", "TASK.md", "@json-render/image"; design.md still says the engine never renders.
  - test_demonstrated_in_taskmd (Must 5): the capture-evidence TASK.md references a capture image path matching `captures/.*\.(png|svg|jpg|jpeg|webp)`.
  - test_copies_and_pin_synced (Must 6): the 3 add.py copies are byte-identical AND md5(add.py) == engine_pin.ENGINE_MD5  (mirrors test_argv_portability).
  # Rejects
  - test_capture_blocks (Reject): prototypes + zero captures → cmd_check exit code is 0 and the JSON `failed` count does not include the capture (it is in `warnings`, not `checks`).
  - test_noisy_when_absent (Reject): .add/design/ with tokens.json but no prototypes/ → no missing_capture WARN; existing UDD-foundation checks unchanged.
  - test_engine_renders_never (Reject): the _missing_captures source uses only path existence (no subprocess/browser/render import); no image written during the check.
  - test_pin_drift_caught (Reject): asserted via test_copies_and_pin_synced + test_bundle_parity — a stale pin / drift goes red (documented; the guard already exists).
</test_plan>

Tests live in: `add-method/tooling/test_capture_evidence.py` · checks the CANONICAL tree + a temp .add/design/ fixture · MUST run red (helper + WARN + doc lines absent) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/skill/add/design.md` `add-method/src/add_method/_bundled/skill/add/design.md` `.claude/skills/add/design.md` `add-method/tooling/templates/udd-wireframe.md` `add-method/src/add_method/_bundled/tooling/templates/udd-wireframe.md` `add-method/tooling/test_capture_evidence.py` `.add/design/captures/`   <!-- 3 add.py copies + the pin · design.md ×3 skill trees · udd-wireframe.md ×2 template trees · the new test · the demonstration captures dir. Declared BEFORE the freeze so the tests→build scope anchor captures the real footprint (task-1/2 lesson). -->
Strategy (ordered batches): 1. canonical add.py — add `_missing_captures` + the cmd_check WARN loop · 2. mirror add.py to _bundled + dogfood `.add/` (byte-identical) · 3. re-aim engine_pin.ENGINE_MD5 = md5(add.py) · 4. reopen design.md (×3) + udd-wireframe.md (×2) with the convention · 5. commit the demonstration captures + reference from §6 · 6. green the red test.
Safety rule (feature-specific): the WARN goes ONLY on the `warnings` array, NEVER on `checks` — cmd_check must stay exit-1-iff-failed and read-only; silent-when-absent must hold (the dogfood repo gains a captures-only `.add/design/`, which must NOT trigger any FAIL).
Code lives in: `add-method/` (+ the dogfood `.add/` engine copy & captures)
Constraints: do NOT change any test or the contract; stdlib only (pathlib/glob — no new dependency, no renderer); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

DEMONSTRATION (exit-criterion 4 — captures-in-TASK.md): the worked design-confirm captures
rendered in task 2's verify are committed and referenced here as real design-confirm evidence —
`.add/design/captures/welcome.png` and `.add/design/captures/settings.png` (the welcome + settings
mocks the human approved). This dogfoods the convention: the screen the human signed off on is
attached to the task record at the conventional captures path.

- [x] all tests pass — test_capture_evidence 14/14; full suite 1145 green.
- [x] coverage did not decrease — net-new test file; helper unit tests + cmd_check integration + doc-surface + pin-sync.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the one in-test fix (hardening test_demonstrated_in_task_md from a vacuous prose-match to real file + §6-scoped check) happened during TESTS, never weakened.
- [x] the green was EARNED, not gamed — adversarial refute-read (self): caught + fixed a vacuous test (test_demonstrated_in_task_md was matching the §4 test-plan's literal "captures/welcome.png"; now asserts a REAL committed capture file + a §6-scoped reference). The 4 guards green pre-build are must-stay-green (silence / no-false-WARN / pin-sync). test_capture_blocks_guard_json confirms the WARN rides `warnings`, never `checks` (exit 0). No vacuous/overfit pass remains.
- [x] concurrency / timing — N/A: a pure read-only file-existence measure; no runtime/shared state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (pathlib/glob); the helper reads file presence, runs no subprocess/renderer; the demonstration PNGs are static images. No security finding.
- [x] layering & dependencies follow conventions — the WARN rides the existing `warnings` array (measure-never-block, like goal_not_auto_ready); cmd_check read-only + exit-1-iff-failed preserved; 3 add.py copies byte-identical + ENGINE_MD5 re-aimed.
- [ ] a person reviewed and approved the change   <!-- conservative gate: human-owned; left unstamped until the answer -->

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_missing_captures` is called by cmd_check (the WARN loop) AND exercised by 6 helper tests + 5 integration tests; `_CAPTURE_EXTS` is consumed by the helper. No orphan.
- [x] DEAD-CODE — no unused symbol introduced; the helper's every branch (no-dir → [], captured, uncaptured) is tested.
- [x] SEMANTIC (prose) — read the design.md (×3) + udd-wireframe.md (×2) edits in full: they name `.add/design/captures/<name>.<ext>`, the TASK.md attachment, `@json-render/image` (Satori→PNG/SVG), the never-red `missing_capture` WARN, and keep "the engine never renders". Accurate + mutually consistent. DEMONSTRATION: the welcome/settings captures are committed at `.add/design/captures/` and cited above — exit-criterion 4 met.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (conservative gate; approved after the live missing_capture WARN demo + 1145-green suite)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): missing_capture WARN counts as real projects add prototypes; that the WARN never flips an exit code (measure-never-block regressions).
Spec delta for the next loop: task 4 `book-glossary-align` propagates the convention (wireframe · mock · capture · design-confirm) to the book + GLOSSARY; the capture-location + @json-render/image + missing_capture terms should land there too.

### Competency deltas
- [UDD · folded] capture-evidence is measure-never-block: the engine MEASURES a design-confirm capture's presence at `.add/design/captures/<name>.*` but never renders or blocks — a never-red WARN mirroring `goal_not_auto_ready` (evidence: live demo fires then clears, exit 0; test_capture_blocks_guard_json).
- [TDD · folded] a content-reference test can vacuously pass by matching the TASK.md's OWN test-plan prose — scope such assertions to the evidence section (§6) AND assert a real artifact, not a substring anywhere in the file (evidence: test_demonstrated_in_task_md matched §4's literal "captures/welcome.png" until hardened to a file-exists + §6-scoped check).
- [ADD · folded] an engine change costs 3 add.py copies + the `engine_pin.ENGINE_MD5` re-aim in lockstep; a guard (test_argv_portability / test_copies_and_pin_synced) turns a forgotten pin red (evidence: clean after re-sync; reaffirms the release-gate discipline).
- [UDD · folded] the milestone's original ask — "confirm with REAL captured images" — is now end-to-end dogfooded: task 2 rendered them, task 3 commits them as design-confirm evidence at the conventional path + cites them in TASK.md (evidence: `.add/design/captures/welcome.png` + `settings.png`).
