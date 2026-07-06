# TASK: ADR Harvester Multi-Line Field Capture

slug: adr-harvester-multiline-fields · created: 2026-07-03 · stage: mvp
milestone: (none)
sensitivity: mechanical
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py:_framing` (L429-446, nested in the ADR-harvest function, `re.search(r"(?m)^Framings weighed:[ \t]*(.+)$", bodies.get(1, ""))` at L430) and `add.py:_strategy` (L460-469, same file, `re.search(r"(?m)^Strategy actually used:[ \t]*(.+)$", bodies.get(5, ""))` at L462) — both are single-line-only extractors over genuinely free-form prose fields that authors legitimately wrap across physical lines
Context (working folder): 3 pinned engine-tree mirrors (same convention as strip-scaffold-backtick-comment-fix) — any change here re-pins ENGINE_MD5
Honors (patterns / conventions): the ADR-harvest's own existing UNFILLED-placeholder-degrades-to-`<unrecorded>` discipline (`_framing`'s `if chosen is UN or chosen.startswith("<")`) — must be preserved exactly, only the LINE-SPAN captured changes, not the placeholder-detection logic
Seams consulted: none cited
Anchors the contract cites: `_framing` (L430) and `_strategy` (L462)'s regex patterns
Issues/Risks (→ feed §1): CONFIRMED, already-manifested, not hypothetical — `.add/tasks/update-global-gitignore-seed/TASK.md` (L78-83) has "Framings weighed:" wrapped across 6 physical lines; its own §7 OBSERVE (L394-399) documents the auto-harvest degraded to `chose <unrecorded>` and required hand-correction, with a Spec delta (L410-414) explicitly seeding THIS task. Other single-line extractors in the same harvest function (`^Outcome:`, `^Reviewed by:`, `^Verdict:`, `^Residue:`, `^autonomy:`) are intentionally single-token/short-value fields by design — NOT in scope, wrapping them is not an expected authoring pattern and "fixing" them would be scope creep with no real defect behind it.
Related intent: seeded from update-global-gitignore-seed spec-delta — a multi-line "Framings weighed:" field degrades its `(chosen — ...)` marker to `<unrecorded>` today [← update-global-gitignore-seed]
Ground SHA: `ba42053` (`git rev-parse --short HEAD`) — all cited line numbers current as of this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: harden `_framing()` (and any other `^Label:[ \t]*(.+)$` single-line extractor in add.py's ADR harvester) to capture through a field's full wrapped paragraph instead of stopping at the first physical line (from update-global-gitignore-seed spec-delta)
Framings weighed: a small shared helper `_capture_wrapped(label, body)` that, after matching the label's first line, keeps consuming subsequent physical lines while they are non-blank AND do not themselves start a new `^[A-Z][A-Za-z ]*:` label, joining with a single space (chosen — one helper reused by both `_framing` and `_strategy`, matches the real authoring convention of indented continuation lines seen in update-global-gitignore-seed) · use `re.DOTALL` and capture up to the next blank line only, no label-boundary check — rejected, would over-capture if a field is followed immediately (no blank line) by the next label, exactly the layout used in most existing TASK.md files · require every prose field to be single-line by convention (reject wrapping) going forward — rejected, prose fields are legitimately long and wrapping for readability is normal Markdown authoring; the harvester should adapt to real authoring, not constrain it
Must:
<must>
  - `_framing()` correctly captures the full "Framings weighed:" value even when the source TASK.md wraps it across multiple physical (indented continuation) lines, preserving today's existing `(chosen ...)`/rejected-list parsing on the FULL captured text, not just its first line
  - `_strategy()` gets the identical fix for "Strategy actually used:", via the same shared helper (not a duplicated one-off regex)
  - the existing UNFILLED-placeholder-degrades-to-`<unrecorded>` behavior is unchanged — a real value starting with "<" (e.g. quoting a type) is still kept, only an actual unfilled template token still degrades
</must>
Reject:
<reject>
  - a wrapped field's continuation lines run into the NEXT label line (e.g. "Must:" right after "Framings weighed:" with no blank line) -> the new capture must stop at that next label boundary, never swallow the following field
  - a wrapped field's continuation runs into a blank line separating sections -> capture must stop there too
  - the fix changes behavior for the SINGLE-line case (the common case today) -> a field that fits on one line must harvest byte-identically to current behavior
</reject>
After:
<after>
  - a "Framings weighed:" or "Strategy actually used:" field wrapped across any number of physical lines harvests its full value correctly into the §7 Decisions (ADR) block, with no manual correction ever needed again for this reason
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ every real continuation line in this repo's existing TASK.md files is either indented OR does not itself start with a `Label:` pattern — lowest confidence because this is inferred from ONE observed real example (update-global-gitignore-seed), not exhaustively verified against every existing TASK.md; if wrong: a rare wrapped field whose continuation line happens to start with something matching `^[A-Z][A-Za-z ]*:` (e.g. a continuation that begins "Note: ...") would be truncated early, same failure mode as today just less common
  - [x] only `_framing`/`Framings weighed:` and `_strategy`/`Strategy actually used:` are true prose fields needing this fix — confirmed via Ground: the other single-line extractors (`Outcome:`, `Reviewed by:`, `Verdict:`, `Residue:`, `autonomy:`) are short-token fields by design, not in scope
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: wrapped Framings weighed harvests correctly   # M1
  Given a TASK.md's §1 "Framings weighed:" value is wrapped across 3 indented continuation lines
  When _framing() runs
  Then it returns the full chosen value + full rejected list, joined correctly
  And this matches what a single-line equivalent value would have produced

Scenario: wrapped Strategy actually used harvests correctly   # M2
  Given a TASK.md's §5 "Strategy actually used:" value is wrapped across multiple lines
  When _strategy() runs
  Then it returns the full value, not just the first physical line

Scenario: single-line fields are unaffected   # M3
  Given both fields are written on a single physical line each (today's common case)
  When _framing()/_strategy() run
  Then the harvested value is byte-identical to current behavior

Scenario: continuation does not swallow the next label   # R1
  Given "Framings weighed:" wraps across 2 lines and is immediately followed by "Must:" with no blank line
  When _framing() runs
  Then the captured value stops before "Must:" — the next field is never absorbed

Scenario: continuation does not cross a blank line   # R2
  Given a wrapped field is followed by a blank line before the next content
  When the harvester runs
  Then the capture stops at the blank line
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION _capture_wrapped(label, body)   body: { label: str, body: str }
  matches ^<label>:[ \t]*(.+)$ (first line) -> then consumes subsequent physical lines while
    non-blank AND not matching ^[A-Z][A-Za-z ]*: (a new label) -> joins with a single space
  returns -> str | None (None if label not found, unchanged from today's per-field behavior)

FUNCTION _framing()   body: { bodies[1]: str }
  calls _capture_wrapped("Framings weighed", bodies.get(1, "")) instead of the old single-line regex
  UNCHANGED: "(chosen ...)" / rejected-list parsing + UNFILLED-placeholder degrade-to-<unrecorded>

FUNCTION _strategy()   body: { bodies[5]: str }
  calls _capture_wrapped("Strategy actually used", bodies.get(5, "")) instead of the old single-line regex
  UNCHANGED: "<fill" placeholder degrade-to-default behavior

Schema: no data schema touched — pure parsing helper; 3 pinned engine-tree mirrors re-pin ENGINE_MD5
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 ("freeze as drafted, start with the trivial mechanical fixes first")
Least-sure flag surfaced at freeze: [spec] the "stop at a line matching a new label OR a blank line" heuristic is inferred from one real observed example (update-global-gitignore-seed), not exhaustively verified against every existing TASK.md's continuation-line style; cost if wrong: a rare wrapped field whose continuation line itself starts with a `Label:`-shaped prefix would still truncate early, same failure mode as today just rarer.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — parsing helper, behavior proven by direct assertion
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_framing_captures_wrapped_field: arrange a TASK.md fixture with "Framings weighed:" wrapped across 3 lines / act call the ADR harvest / assert the full chosen+rejected values are captured · covers: M1
  - test_strategy_captures_wrapped_field: same shape for "Strategy actually used:" · covers: M2
  - test_single_line_fields_unchanged: arrange both fields on one line each / act harvest / assert byte-identical to pre-fix output · covers: M3
  - test_wrapped_field_stops_at_next_label: arrange "Framings weighed:" wrapping into an immediately-following "Must:" line, no blank line / act harvest / assert "Must:" content is NOT absorbed · covers: R1
  - test_wrapped_field_stops_at_blank_line: arrange a wrapped field followed by a blank line / act harvest / assert capture stops there · covers: R2
</test_plan>

Tests live in: `add-method/tooling/test_adr_harvest.py` (extend existing file — confirmed it already exercises `_framing`/`_strategy`) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py`, `.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`, `add-method/tooling/test_adr_harvest.py`, `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. write the 5 new RED tests against `test_adr_harvest.py` · 2. add `_capture_wrapped(label, body)` + wire `_framing`/`_strategy` to use it, in `add-method/tooling/add.py` only · 3. confirm green on that one tree · 4. propagate byte-identically to the other 2 mirrors · 5. re-pin ENGINE_MD5 · 6. run the full suite + `add.py check`

Persona (optional): methodology-engine-dev
Known-problem fixes: an over-eager "consume until blank line" with no label-boundary check would swallow the NEXT field's line if no blank line separates them (the common layout in this repo's TASK.md template) → planned fix: check `^[A-Z][A-Za-z ]*:` as a stop condition, not just blank lines
Strategy actually used: as planned, plus one refute-read-caught fix — the label-boundary regex was widened from `^[A-Z][A-Za-z ]*:` to `^[A-Z][A-Za-z ]*(\([^)]*\))?[ \t]*:` after the add-verify agent found it missed parenthetical labels (`Safety rule (feature-specific):`, `Persona (optional):`) that sit directly after `Strategy actually used:` in the real, unmodified template with no blank line — a real gap, not a contrived fixture, closed with a dedicated regression test before the gate
Safety rule (feature-specific): the shared helper must be a pure function (no IO), and existing single-line harvests for ALL OTHER fields (`Outcome:`, `Reviewed by:`, `Verdict:`, `Residue:`, `autonomy:`) must remain untouched — this task only touches `_framing`/`_strategy`
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib `re`, already imported); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 17/17 in `test_adr_harvest.py`; full tooling suite 2926 tests, 1 known pre-existing unrelated failure (see Live-verify evidence)
- [x] coverage did not decrease — 8 new tests added (5 planned + 1 M3 dedicated + 1 refute-read-caught regression), 0 removed
- [x] no test or contract was altered during build — §3 CONTRACT text unchanged; only `_capture_wrapped`'s internal regex was refined mid-build to actually satisfy the contract's stated intent ("not itself start a new field label"), same category as the strip-scaffold-backtick-comment-fix precedent
- [x] the green was EARNED, not gamed — two adversarial refute-read rounds by the add-verify agent (round 1: NOT-EARNED, found a real gap; round 2: EARNED after the fix) — see below
- [x] concurrency / timing of the risky operation is safe — pure function over an immutable string, no shared state (Advisor: CLEAR)
- [x] no exposed secrets, injection openings, or unexpected dependencies — hardcoded, `re.escape`d labels; stdlib `re` only (Advisor: CLEAR)
- [x] layering & dependencies follow CONVENTIONS.md — change stays inside the harvester helper, no new coupling (Advisor: CLEAR)
- [x] a person reviewed and approved the change — Tin Dang via explicit freeze + sequencing instruction; auto-gated at Verify per `autonomy: auto` + `sensitivity: mechanical`

### Build expectations — what "correct" looks like
- [x] a "Framings weighed:" value wrapped across 3 indented continuation lines harvests its full chosen framing into the §7 ADR block — confirmed by `test_framing_captures_wrapped_field`
- [x] a "Strategy actually used:" value wrapped across lines, immediately followed by "Safety rule (feature-specific):" with NO blank line (the real template's actual layout), harvests in full and does NOT swallow "Safety rule" — confirmed by `test_wrapped_field_stops_at_parenthetical_label` (added after the refute-read caught this exact real-template shape)
- [x] a single-line field harvests byte-identically to pre-fix behavior — confirmed by `test_single_line_fields_unchanged`

### Deep checks
- [x] WIRING (code) — `_capture_wrapped` is called from both `_framing()` and `_strategy()` (the only 2 call sites, both inside `_stamp_adr_record`); no orphaned reference
- [x] DEAD-CODE (code) — no unused symbol introduced; the old inline single-line regexes were replaced, not left behind
- [x] SEMANTIC (prose) — re-read the full `_capture_wrapped` docstring + both call sites after the parenthetical-label fix; confirmed the docstring names the exact real-template shape it now handles

### Live-verify evidence — confirm the §0 GROUND anchors still resolve
- [x] `_capture_wrapped` (new): line 402 · `_framing` (nested): line 451 · `_strategy` (nested): line 483 — all confirmed resolving in the current working tree by the add-verify agent's second pass
- [x] anchor drift disclosed: `.add/SEAMS.md:57` cited `_declared_scope` at `add.py:4535` — this was ALREADY off by 4 lines in committed git HEAD before this session (confirmed via `git show HEAD:add-method/tooling/add.py | grep -n def _declared_scope` → 4539), a pre-existing, unrelated drift, not caused by this task. This task's own +20-line insertion shifted it further to 4560 (updated in `.add/SEAMS.md` for the working tree). The pre-existing HEAD-vs-4535 drift remains uncommitted-unfixed — it is what causes `test_ci_tooling_mirror_gap.py::test_fresh_checkout_survives_test_job_sequence` to fail on a fresh clone of git HEAD (out of this task's scope; flagged as a Spec delta below)

### Refute-read verdict — the earned-green check
Verdict: EARNED (round 2; round 1 was NOT-EARNED)
By: add-verify agent (two sequential passes). Round 1 adversarially probed gherkin-boundary lines, bullet lines, CRLF, multi-field bodies, and — critically — the REAL unmodified `templates/TASK.md.tmpl` layout, finding that `Safety rule (feature-specific):` and `Persona (optional):` (which sit immediately after `Strategy actually used:` with no blank line in the real template) were NOT matched by the original `^[A-Z][A-Za-z ]*:` stop-regex because of the parenthetical — a wrapped Strategy value would swallow the next field in practice, not just in a contrived fixture. Fixed by widening the regex to `^[A-Z][A-Za-z ]*(\([^)]*\))?[ \t]*:` plus a dedicated regression test. Round 2 re-probed the fix (hyphenated labels, colon-inside-parens, a new false-positive shape where legitimate continuation prose ending in "(...):" would now over-match) — confirmed the fix closes the real gap; the one residual false-positive is self-limiting (stops capture early, never corrupts an adjacent field) and no real template content produces that shape.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: add-verify agent (two sequential passes, final verdict from round 2)
1. Security: CLEAR — pure regex/string helper, hardcoded `re.escape`d labels, no eval/injection/ReDoS surface
2. Concurrency: CLEAR — pure function over an immutable string argument, no shared state
3. Architecture: CLEAR (round 2; round 1 flagged RESIDUE — the boundary heuristic was too narrow for the real document shape it parses — resolved by the parenthetical-label fix)
Verdict: PASS
Residue: none blocking. Disclosed, non-blocking, self-limiting edge case: a continuation line that is legitimate prose ending in "(parenthetical remark):" would now be mistaken for a label and stop the capture early — bounded impact (early stop only, never corrupts the next field), no real template field produces this shape; also disclosed, the pre-existing hyphenated-label case (`Non-negotiable:`) is still unmatched by the boundary regex, unchanged from before this task, no real template label uses a hyphen.
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gated per `autonomy: auto` + `sensitivity: mechanical`, per the project's advisor-gate-relax rule; two adversarial refute-read rounds recorded above as the evidence trail) · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a small shared helper `_capture_wrapped(label, body)` that, after matching the label's first line, keeps consuming subsequent physical lines while they are non-blank AND do not themselves start a new `^[A-Z][A-Za-z ]*:` label, joining with a single space; rejected use `re.DOTALL` and capture up to the next blank line only, no label-boundary check — rejected, would over-capture if a field is followed immediately (no blank line) by the next label, exactly the layout used in most existing TASK.md files · require every prose field to be single-line by convention (reject wrapping) going forward — rejected, prose fields are legitimately long and wrapping for readability is normal Markdown authoring; the harvester should adapt to real authoring, not constrain it
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 ("freeze as drafted, start with the trivial mechanical fixes first"))
- [AI] build — strategy used: as planned, plus one refute-read-caught fix — the label-boundary regex was widened from `^[A-Z][A-Za-z ]*:` to `^[A-Z][A-Za-z ]*(\([^)]*\))?[ \t]*:` after the add-verify agent found it missed parenthetical labels (`Safety rule (feature-specific):`, `Persona (optional):`) that sit directly after `Strategy actually used:` in the real, unmodified template with no blank line — a real gap, not a contrived fixture, closed with a dedicated regression test before the gate
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-gated per `autonomy: auto` + `sensitivity: mechanical`, per the project's advisor-gate-relax rule; two adversarial refute-read rounds recorded above as the evidence trail))

### Spec delta
- [SPEC · dropped] fix the pre-existing `.add/SEAMS.md:57` `_declared_scope` anchor drift at git HEAD (cites `add.py:4535`, real def is at `:4539` in the last commit before this session) — unrelated to this task, discovered as the sole remaining full-suite failure (`test_ci_tooling_mirror_gap.py::test_fresh_checkout_survives_test_job_sequence` fails on any fresh clone of HEAD until this is committed) (evidence: `git show HEAD:add-method/tooling/add.py | grep -n def _declared_scope` → 4539 vs `.add/SEAMS.md`'s cited 4535)

### Competency deltas
- [TDD · folded] a written test suite can pass 100% while still missing the real-world shape of its own primary target field — the frozen contract's stop-regex (`^[A-Z][A-Za-z ]*:`) looked complete against 5 fixture-authored tests, but the REAL unmodified template places a parenthetical-suffixed label (`Safety rule (feature-specific):`) directly after the exact field (`Strategy actually used:`) this task targets; only an adversarial refute-read against the real template — not more fixture tests in the same style — caught it (evidence: add-verify round 1 NOT-EARNED, closed by round 2 EARNED) [folded foundation-version 64]
