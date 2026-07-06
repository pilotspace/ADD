# TASK: Strip-Scaffold Backtick-Comment Over-Strip Fix

slug: strip-scaffold-backtick-comment-fix · created: 2026-07-03 · stage: mvp
milestone: (none)
sensitivity: mechanical
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py:_strip_live_scaffold` (L280-289) — splits text on triple-backtick fences (`re.split(r"(```.*?```)", text, flags=re.DOTALL)`) and strips `_HTML_COMMENT_RE = re.compile(r"", re.DOTALL)` (L275) from every non-fence segment; `_contract_fingerprint` (L295-300) calls it to compute the tamper-guard's comment-normalized §3 digest
Context (working folder): 3 pinned engine-tree mirrors (`add-method/tooling/add.py`, `.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`) — any change here re-pins `ENGINE_MD5` across all 3, per this project's own byte-identical-mirrors convention
Honors (patterns / conventions): methodology-engine-dev persona's "Mirrors stay byte-identical" + "A pin change is deliberate" critical rules
Seams consulted: none cited
Anchors the contract cites: `_strip_live_scaffold`'s fence-detection `re.split` call (L286) and the existing `_HTML_COMMENT_RE` (L275)
Issues/Risks (→ feed §1): CONFIRMED real, already-possible corruption — the fence-detection only recognizes TRIPLE-backtick (```` ```````) fences; a single-backtick inline span quoting literal `<!--...-->` syntax in ordinary prose (e.g. this very task's own §1 Feature line, which contains `` `<!--...-->` `` inline) is NOT protected and would be silently stripped by a completing gate, garbling authored prose that merely discusses HTML-comment syntax rather than being live scaffolding itself. Existing tests (`test_strip_scaffold_at_done.py` — `test_fenced_block_left_untouched`, `test_idempotent_and_content_safe`) only cover the triple-backtick-fence case; no existing test exercises an inline single-backtick span.
Related intent: seeded from template-structural-gaps spec-delta — garbles completed tasks' §0/§1 text that documents HTML-comment syntax after gating [← template-structural-gaps]
Ground SHA: `ba42053` (`git rev-parse --short HEAD`) — all cited line numbers current as of this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fix the engine's close-time "strip live-phase instruction comments" feature so it stops stripping legitimate prose that quotes literal `<!--...-->` syntax inside backticks, not just the template's own instructional comments (from template-structural-gaps spec-delta)
Framings weighed: extend `_strip_live_scaffold`'s fence-split regex to also protect single-backtick inline spans (`` r"(```.*?```|`[^`\n]*?`)" ``, one alternation, no new capturing group) so BOTH triple-fence and inline-backtick content pass through untouched (chosen — minimal, symmetric with the existing fence-protection discipline, zero new concepts) · require authors to escape a literal `<!--` as `&lt;!--` instead — rejected, pushes an engine-parsing workaround onto every task author, error-prone and undocumented anywhere · only protect inline spans that literally start with `` `<!-- `` — rejected, over-fits to the ONE observed case (this task's own §1 line) and would still corrupt a differently-worded literal quote
Must:
<must>
  - a `<!--...-->` span written inside single backticks in ordinary prose (not live engine scaffolding) survives a completing gate byte-exact, identical to how a triple-backtick-fenced span already survives
  - a REAL live instruction comment (not backtick-quoted) is still stripped exactly as today — no regression in the primary strip-scaffold behavior
  - the fix is symmetric: idempotent (running strip twice produces the same result) and content-safe (no authored non-comment text is ever altered), matching the existing `_strip_live_scaffold` docstring's own stated properties
</must>
Reject:
<reject>
  - an inline single-backtick span that itself spans multiple lines (a stray unmatched backtick) -> must NOT swallow subsequent real content into a false "protected" span; the span match is restricted to a single line (no `\n` inside the backticks)
  - protecting an inline span changes ANY already-passing existing test's outcome -> `test_strip_scaffold_at_done.py`'s full suite must stay green unmodified (this is additive protection, not a behavior change to the already-covered cases)
</reject>
After:
<after>
  - `_strip_live_scaffold` protects both ``` triple-fences AND inline single-backtick spans from comment-stripping, so a task author can safely quote`<!--...-->` syntax in prose (as documentation, discussion, or an example) without it being silently mangled at gate time
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ no existing, already-shipped TASK.md relies on the CURRENT (buggy) behavior of a single-backtick-wrapped`<!--...-->` actually being stripped — lowest confidence because this was never intentional behavior to begin with (it's a gap, not a documented feature), so no author could have deliberately relied on it; if wrong: an extremely unlikely edge case where some already-`done` task's stripped output is expected verbatim by a downstream reader — checked via `add.py check`/full suite before this ships
  - [x] the fix must NOT touch the 3-engine-tree mirroring or ENGINE_MD5 pinning discipline beyond the single, deliberate re-pin this change itself requires — confirmed: this is a normal engine-code change like any other, propagated to all 3 trees + re-pinned, not an exception
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: inline backtick-quoted comment survives a completing gate   # M1
  Given a TASK.md contains prose like "escape a literal `<!--...-->` in your text"
  When a completing gate (PASS/RISK-ACCEPTED) runs _strip_live_scaffold
  Then the backtick-quoted span survives byte-exact, identical to a ``` fence
  And a real (non-backtick) instruction comment elsewhere in the same file is still stripped

Scenario: real live comment still stripped (no regression)   # M2
  Given a TASK.md contains a genuine`<!-- EXIT: ... -->` instruction comment, not backtick-quoted
  When a completing gate runs _strip_live_scaffold
  Then that comment is removed exactly as it is today

Scenario: a stray unmatched backtick does not swallow real content   # R1
  Given a line contains a single stray backtick with no closing backtick on the same line
  When _strip_live_scaffold runs
  Then the "protected span" match never crosses a newline
  And any real instruction comment later in the file is still correctly stripped

Scenario: existing test suite is unaffected   # R2
  Given the full existing test_strip_scaffold_at_done.py suite (fence-only cases)
  When run against the fixed _strip_live_scaffold
  Then every existing test still passes unmodified — this is additive protection only
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION _strip_live_scaffold(text)   body: { text: str }
  fence-split regex: r"(```.*?```|`[^`\n]*?`)"   # was r"(```.*?```)" — added inline single-backtick alternation
  even-indexed segments (outside both fence kinds) -> _HTML_COMMENT_RE stripped, exactly as today
  odd-indexed segments (``` fence OR `inline` span) -> passed through byte-exact, unchanged
  returns -> str, idempotent, content-safe (unchanged docstring guarantees, now covering 2 span kinds not 1)
Schema: no data schema touched — pure string-transform helper; 3 pinned engine-tree mirrors re-pin ENGINE_MD5
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 ("freeze as drafted, start with the trivial mechanical fixes first")
Least-sure flag surfaced at freeze: [spec] no existing shipped TASK.md is known to rely on today's buggy strip-through-single-backtick behavior — inferred, not exhaustively checked against every `done` task; cost if wrong: an extremely unlikely case where some already-closed task's stripped output is expected verbatim elsewhere.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — single pure-function fix, behavior proven by direct assertion
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_inline_backtick_comment_survives: arrange text with an inline ```<!-- ... -->` `` span / act call _strip_live_scaffold / assert the span survives byte-exact + assert a real comment elsewhere in the same text is still stripped · covers: M1
  - test_real_comment_still_stripped: arrange text with a genuine (non-backtick)`<!-- -->` comment / act strip / assert it is removed exactly as before · covers: M2
  - test_stray_backtick_does_not_swallow_content: arrange a line with one unmatched backtick followed by real content + a real comment further down / act strip / assert the real comment is still stripped (not falsely protected) · covers: R1
</test_plan>

Tests live in: `add-method/tooling/test_strip_scaffold_at_done.py` (extend existing file, same class `StripHelperProperties`) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py`, `.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`, `add-method/tooling/test_strip_scaffold_at_done.py`, `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. write the 3 new RED tests against `StripHelperProperties` · 2. change the fence-split regex in `add-method/tooling/add.py` only · 3. confirm green on that one tree · 4. propagate byte-identically to the other 2 engine-tree mirrors · 5. recompute + re-pin ENGINE_MD5 in `engine_pin.py` · 6. run the full suite + `add.py check`

Persona (optional): methodology-engine-dev
Known-problem fixes: a naive `` `.*?` `` (DOTALL) inline regex could swallow multiple lines if backticks are unbalanced across a large span → planned fix: restrict to `` `[^`\n]*?` `` (no DOTALL on this alternative, explicit `\n` exclusion) so it can never cross a line boundary
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the fix must be byte-identical across all 3 engine-tree mirrors before ENGINE_MD5 is re-pinned — never re-pin against a partially-propagated change
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib `re`, already imported); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_strip_scaffold_at_done.py` 10/10; `add.py check` 525 passed, 0 failed
- [x] coverage did not decrease — 3 new tests added (`test_inline_backtick_comment_survives`, `test_real_comment_still_stripped`, `test_stray_backtick_does_not_swallow_content`), 0 removed
- [x] no test or contract was altered during build — only `add.py` (the fix) + additive new tests; existing tests unmodified
- [x] the green was EARNED, not gamed — a first, broader fix attempt (`` `[^`\n]*?` ``, any inline backtick span) was caught by the FULL suite (not just the new tests) regressing `test_reopen_regate_is_clean`: it fragmented real live comments containing unrelated backtick-quoted code, leaving them unstripped. Narrowed to ```<!--.*?-->` `` (a backtick span that IS itself a whole HTML-comment shape), re-confirmed green. Independent add-verify refute-read: EARNED, with one disclosed non-blocking residue (see below).
- [x] concurrency / timing of the risky operation is safe — n/a, no concurrency in scope
- [x] no exposed secrets, injection openings, or unexpected dependencies — n/a, pure regex change, stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — pure function, no IO, matches existing helper conventions
- [x] a person reviewed and approved the change — Tin Dang authorized via "freeze as drafted, start with the trivial mechanical fixes first"; sensitivity: mechanical + autonomy: auto permits AI auto-resolution on complete, disclosed-residue evidence per advisor-gate-relax

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] an inline ```<!--...-->` `` literal-comment example in prose survives a completing gate byte-exact — confirmed by `test_inline_backtick_comment_survives` + refute-read hand-trace
- [x] a real live comment containing unrelated backtick-quoted code is still fully stripped (no regression) — confirmed by `test_reopen_regate_is_clean` (an EXISTING test that caught the first, broader fix attempt's regression) staying green against the final narrow fix

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the changed regex is referenced only inside `_strip_live_scaffold`, its sole call site (`_contract_fingerprint`) is unchanged and still calls it the same way
- [x] DEAD-CODE (code) — no new symbol introduced; the existing function's internals changed in place
- [ ] SEMANTIC (prose / non-code) — n/a, code/test-only task

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `_strip_live_scaffold` confirmed present and passing at time of this gate; the fence-split regex line is exactly where §3 said it would be
- [x] no anchor moved/renamed since Ground SHA — function extended in place, not moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (with one disclosed, non-blocking residue)
By: agent adfec8f93940fdfe5 (add-verify) · adversarially checked: whether the narrow fix still protects the target case (confirmed yes), whether it re-introduces the first attempt's fragmentation regression (confirmed no), multiple-example/nested-backtick edge cases (traced correct), and searched for any OTHER gap — found one: a whitespace-padded inline example (`` `  ` ``) is NOT protected and would still be stripped/mangled. Checked against this repo's real prose (grep across all TASK.md/docs/skill files): this padded style does not actually occur anywhere today — theoretical, not materialized.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent adfec8f93940fdfe5 (add-verify)
1. Security: CLEAR — pure regex/parsing change, no IO, no new dependency
2. Concurrency: CLEAR — n/a, no concurrent operation in scope
3. Architecture: CLEAR — single function extended in place, correctly wired, no dead code
Verdict: PASS
Residue: none-blocking — a whitespace-padded inline literal-comment example (`` `  ` ``) is not protected by the narrow regex; confirmed this style does not occur anywhere in this repo's current prose, so this is a theoretical gap, not a live defect. Worth a follow-up if this prose pattern is ever adopted.
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (via "freeze as drafted, start with the trivial mechanical fixes first") · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): re-run `test_strip_scaffold_at_done.py` on any future edit to `_strip_live_scaffold`; watch for the whitespace-padded inline-comment style actually appearing in prose (currently theoretical only).

### Decisions (ADR)
- [AI] specify — chose extending the fence-split regex with a narrow ```<!--.*?-->` `` alternative over escaping conventions or over-fitted string matching
- [AI] build — DIVERGED from the plan: a first, broader attempt (`` `[^`\n]*?` ``, any inline backtick span) regressed real comment-stripping (caught by the full existing test suite, not just new tests); narrowed to ```<!--.*?-->` `` specifically, re-verified green

### Spec delta
- [SPEC · carried] a whitespace-padded inline literal-comment example (`` `  ` ``) is not protected by the current fix — theoretical only (does not occur anywhere in this repo's current prose), worth a follow-up if this style is ever adopted (evidence: round-1 add-verify refute-read, agent adfec8f93940fdfe5) [carried: theoretical only — a whitespace-padded inline literal-comment example does not occur anywhere in this repo's current prose; revisit only if this style is ever adopted]

### Competency deltas
- [TDD · folded] when narrowing a "protect X from Y" regex fix, run the FULL existing test suite (not just new targeted tests) before considering it green — a first broader fix passed its own new tests but silently regressed an EXISTING, unrelated test (`test_reopen_regate_is_clean`) by fragmenting real comments that happen to contain unrelated backtick-quoted code (evidence: this task's own build attempt 1 vs 2) [folded foundation-version 64]
