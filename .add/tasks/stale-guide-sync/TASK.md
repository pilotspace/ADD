# TASK: Sync stale guide/book prose to the shipped engine — kill the 5-build scope-gate deferral note, unify the auto-PASS precondition list across run.md/6-verify.md/book, add a book→TASK.md artifact cross-ref, drain the doc-class deltas

slug: stale-guide-sync · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures) — PROSE-ONLY, no engine logic:
- `skill/add/phases/5-build.md:19` (×3 trees) — the STALE deferral note: "the engine gate (touched ⊆ declared) lands in the `scope-gate-enforce` task — until it ships this section is prose discipline." VERIFIED stale: `add.py:_scope_guard` (3746) is wired into `cmd_gate` (1029) and refuses a completing gate on an out-of-scope touch (`scope_violation` → `_heal_or_escalate`); `cmd_check`/`_scope_findings` surface it too. The gate SHIPPED (via the build-scope-lock milestone, not a "scope-gate-enforce" task — which never existed). Fix: rewrite the note to "enforced at the verify gate".
- `skill/add/run.md:68` (×3) — the CANONICAL auto-PASS precondition list ("Auto-PASS requires ALL of: every test green; coverage not decreased; no test weakened and no contract edited; loops dry; completeness-critic clean; and the deep check below."), now followed by the task-6 recorded-refute-read bullet (74) + the "Always escalates / no residue" bullet (75).
- `skill/add/phases/6-verify.md:6-9` (×3) — the autonomy blockquote states the auto-PASS in SUMMARY form ("complete evidence with no residue") — must be reconciled to name the SAME precondition set (or point at run.md as the one canonical list).
- `docs/08-step-6-verify.md:21` (×3 tracked + `.add/docs` ride-along) — the book's "Auto (the default)" bullet lists a DIFFERENT subset ("every test green, coverage not decreased, no test weakened and no contract edited, the convergence loops dry, and no residue") — missing completeness-critic + deep-check + the recorded refute-read.
- `docs/03-step-1-specify.md` + `docs/04-step-2-scenarios.md` (×3) — NEITHER cross-refs back to TASK.md §1/§2 (grep: 0 hits); add a one-line "this chapter fills §1/§2 of TASK.md" artifact pointer (parity with how other chapters name their §).

Context (working folder):
- The 5 open SPEC deltas (`add.py deltas`): 2 DOC-class drainable HERE — guarantee-audit-lints "add a note to 6-verify.md/run.md that audit SURFACES shallow_deep_check + risk_unset" + security-escalation-disclosure "sync the missed-finding disclosure into book ch.08". 3 ENGINE-class (CARRY forward, out of a prose task's scope): delta-drain verb/archived asymmetry · `risk:` first-class template field. 1 ALREADY-RESOLVED: the delta-drain reject-vocab delta (honest-reject-naming picked `ambiguous_spec_match`/`no_matching_spec_delta`) → DROP.
- Depends-on (all DONE): freeze-gate-universal · guarantee-audit-lints · honest-reject-naming.

Honors (patterns / conventions):
- 3-tree byte-identity for every guide+book edit (skill: test_tree_parity/test_bundle_parity · book: test_book_parity/bundle + repo-root mirror) · lean byte budget (test_skill_lean) for run.md(ORCHESTRATION 0.75)/6-verify.md(PHASES 0.80)/5-build.md(PHASES) edits — reclaim from own prose, never weaken the budget · PINNED anchors survive verbatim (test_protected_safety_lines_pinned · test_earned_green_rubric/test_verify_deepen `*_ANCHORS` · test_ground_wiring "seven lines" · test_ubiquitous_language enforced-idiom sweep incl. `blast radius`).
- PROSE-ONLY: NO add.py / add_engine change → ENGINE_MD5 + ENGINE_PKG_MD5 BOTH UNCHANGED (the first prose-only flow-honesty task since security-escalation-disclosure).

Anchors the contract cites: `5-build.md:19` deferral note · the canonical auto-PASS precondition list in `run.md` · `6-verify.md` autonomy blockquote · `docs/08-step-6-verify.md:21` book auto bullet · `docs/03/04` →TASK.md §1/§2 cross-ref · the 2 doc-class SPEC deltas drained + 3 carried + 1 dropped.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Sync the method's PROSE to the engine that actually shipped — (a) rewrite the stale 5-build scope-gate "deferred until it ships" note to "enforced at the verify gate", (b) reconcile the auto-PASS precondition list so run.md / 6-verify.md / book ch.08 name the SAME set (incl. the task-6 recorded refute-read + the guarantee-audit-lints surfacing note), (c) add a book ch.03/04 → TASK.md §1/§2 artifact cross-ref, (d) drain the 2 doc-class SPEC deltas, carry the 3 engine-class, drop the 1 already-resolved. PROSE-ONLY — no engine change.
Framings weighed: run.md = single canonical enumerated list, book ch.08 reconciled to name the SAME items, 6-verify.md blockquote keeps its summary + an explicit "the full list is canonical in run.md" pointer (chosen — one source of truth, least 3-way drift risk going forward, lean-friendly; a doc-grep still finds every precondition named in run.md + book, and 6-verify points to it) · full identical enumerated list verbatim in ALL THREE (maximal "identical" but heaviest byte cost ×3 files ×3 trees + perpetual 3-way drift surface — the very problem this task fixes) · leave 6-verify as summary-only (rejected — fails the "names the same set" goal)
Must:
<must>
  - 5-build.md (×3): the `scope-gate-enforce`/"until it ships this section is prose discipline" deferral is GONE; replaced by a note that the gate is ENFORCED — a completing verify gate refuses an out-of-scope build (`scope_violation` → self-heal) and `add.py check` surfaces it. No invented future task name.
  - run.md (×3): carries the ONE canonical auto-PASS precondition list, naming every item: tests green · coverage held · no test weakened / no contract edited · loops dry · completeness-critic clean · deep check filled · the earned-green refute-read verdict recorded · no residue (security/concurrency/architecture) escalates. (Items already present stay; the list is the reconciled superset.)
  - book ch.08 (×3 + ride-along): the "Auto (the default)" precondition bullet names the SAME set as run.md (adds the missing completeness-critic + deep-check + recorded-refute-read), so the two never disagree.
  - 6-verify.md (×3): the autonomy blockquote names the same preconditions in summary AND points to run.md as the canonical full list — no contradicting subset.
  - run.md + 6-verify.md (×3): a one-line note that `add.py audit` now SURFACES the shape lints (`shallow_deep_check` + `risk_unset` + `refute_unrecorded`) — draining the guarantee-audit-lints doc delta.
  - book ch.08 (×3 + ride-along): carries the missed-finding "blind to a never-marked security finding" disclosure (drained from the security-escalation-disclosure book-sync delta) so book ↔ skill no longer drift.
  - book ch.03 + ch.04 (×3): each gains a one-line "this chapter fills §1/§2 of the active TASK.md" artifact cross-ref.
  - SPEC deltas reconciled: the 2 doc-class drained (status flips off open), the delta-drain reject-vocab one DROPPED (resolved by honest-reject-naming), the 3 engine-class CARRIED with a reason; `add.py deltas` open-count drops by the 3 (2 drained + 1 dropped).
  - ENGINE_MD5 + ENGINE_PKG_MD5 BOTH byte-UNCHANGED (prose-only); all guide/book edits byte-identical across their mirror trees; lean budget held (reclaim from own prose).
</must>
Reject:
<reject>
  - a guide/book edit that drifts a mirror tree -> "tree_parity_drift" (test_tree_parity / test_book_parity)
  - an edit that drops a PINNED safety line / earned-green or deep-check anchor / "seven lines" / uses an enforced-swept idiom -> "pinned_anchor_lost" (test_protected_safety_lines_pinned / *_ANCHORS / test_ubiquitous_language)
  - a prose addition that busts the lean byte budget without reclaim -> "lean_budget_exceeded" (test_skill_lean)
  - any add.py / add_engine byte change -> "engine_touched" (ENGINE_MD5 / ENGINE_PKG_MD5 must not move)
</reject>
After:
<after>
  - reading run.md, 6-verify.md, or book ch.08 yields the SAME auto-PASS preconditions; no reader gets a stale or partial answer.
  - 5-build.md states the scope gate is enforced (matches the shipped `_scope_guard`); no "deferred" claim survives.
  - `add.py deltas` open SPEC-delta count dropped by 3 (2 drained + 1 dropped), 3 carried with reasons.
  - book ch.03/04 point back to the TASK.md section they fill.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] "identical list across the three" is satisfied by a CANONICAL list in run.md + book naming the same items + 6-verify pointing to it — NOT byte-identical prose in all three — lowest confidence because the exit-criterion word is "identical"; if wrong: Tin wants the full enumerated list verbatim ×3 (heavier byte reclaim, more drift surface) — a freeze-gate decision, cheap to switch before build.
  - [ ] the 3 "carry" vs "drop" delta dispositions are right (reject-vocab one is truly resolved by honest-reject-naming; verb-asymmetry + risk-first-class are genuinely engine-scope, not prose) — confirm at freeze.
  - [ ] adding the recorded-refute-read as a named auto-PASS precondition in the book is in-scope here (it was disclosed by task 6; this task UNIFIES it into the canonical list) — not a re-opening of task 6.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the stale scope-gate deferral note is gone
  Given 5-build.md said the scope gate "lands in the scope-gate-enforce task — until it ships this section is prose discipline"
  When stale-guide-sync ships
  Then 5-build.md (×3 trees) states the gate is ENFORCED at the verify gate (scope_violation → self-heal; add.py check surfaces it)
  And no "scope-gate-enforce" / "until it ships" / "prose discipline" phrasing remains

Scenario: the auto-PASS preconditions agree across the three surfaces
  Given run.md, 6-verify.md, and book ch.08 listed DIFFERENT auto-PASS precondition subsets
  When stale-guide-sync ships
  Then run.md carries the one canonical list and book ch.08 names the SAME set (incl. completeness-critic, deep check, recorded refute-read) and 6-verify points to run.md as canonical
  And no surface contradicts another (a doc-grep finds every canonical precondition in run.md + book)

Scenario: audit-surfacing + missed-finding disclosures are present
  Given the guarantee-audit-lints + security book-sync deltas were open
  When stale-guide-sync ships
  Then run.md + 6-verify.md note that add.py audit surfaces shallow_deep_check + risk_unset + refute_unrecorded, and book ch.08 carries the never-marked-security-finding disclosure
  And the standing "security is always HARD-STOP" guarantee is byte-unchanged

Scenario: the book chapters point back to the TASK.md section they fill
  Given docs/03 and docs/04 had no TASK.md cross-ref
  When stale-guide-sync ships
  Then ch.03 names it fills §1 and ch.04 names it fills §2 (×3 trees)
  And the change is prose-only

Scenario: the SPEC-delta backlog is reconciled
  Given 5 open SPEC deltas (2 doc-class, 3 engine-class, 1 already-resolved)
  When stale-guide-sync ships
  Then add.py deltas shows the 2 doc-class drained + the resolved one dropped (open-count −3) and the 3 engine-class carried with reasons
  And no delta is silently lost (carried deltas keep their text + evidence)

Scenario (reject): the engine must not move
  Given this is a prose-only task
  When the build runs
  Then ENGINE_MD5 and ENGINE_PKG_MD5 are both byte-unchanged
  And every guide/book edit is byte-identical across its mirror trees, no PINNED anchor lost, lean budget held
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE-SYNC CONTRACT (doc-only; engine BYTE-FROZEN)

THE CANONICAL auto-PASS precondition set (the one list; run.md owns it, the others name the same items):
  1. every test green
  2. coverage not decreased
  3. no test weakened, no contract edited
  4. convergence loops dry
  5. completeness-critic clean
  6. the deep check filled (wiring/dead-code | semantic read)
  7. the earned-green refute-read verdict recorded   (task 6, under auto)
  8. no residue (security · concurrency · architecture) — else ESCALATE (security ALWAYS HARD-STOP)

PER-FILE edit contract (each ×3 mirror trees, byte-identical):
  5-build.md          -> deferral note REWRITTEN to "enforced at the verify gate (scope_violation -> self-heal;
                         add.py check surfaces it)"; tokens `scope-gate-enforce` / `until it ships` / `prose discipline` GONE
  templates/TASK.md.tmpl -> the §5 comment's "engine enforcement (touched ⊆ declared) lands in scope-gate-enforce"
                         (3rd stale instance) REWRITTEN to "enforced at the verify gate" (×2 tooling trees)
  run.md              -> the canonical 8-item list present (already 1-6 + refute-read bullet + residue bullet) +
                         a one-line "add.py audit surfaces shallow_deep_check + risk_unset + refute_unrecorded"
  phases/6-verify.md  -> autonomy blockquote names the same set in summary + "full list: run.md" pointer +
                         the same audit-surfaces one-liner
  docs/08-step-6-verify.md -> "Auto (the default)" bullet names the SAME 8 items (adds 5,6,7) +
                         the never-marked-security-finding disclosure (book<->skill parity)
  docs/03-step-1-specify.md -> one-line "fills §1 of the active TASK.md"
  docs/04-step-2-scenarios.md -> one-line "fills §2 of the active TASK.md"

SPEC-DELTA dispositions (add.py deltas open-count -3):
  DRAIN (resolve): guarantee-audit-lints "audit surfaces lints"  ·  security-escalation-disclosure "book missed-finding sync"
  DROP (already resolved): delta-drain "reconcile reject vocabulary" (honest-reject-naming did it)
  CARRY (+reason, engine-scope): delta-drain "verb/archived asymmetry"  ·  guarantee-audit-lints "risk: first-class field"

INVARIANTS (un-negotiable):
  ENGINE_MD5 + ENGINE_PKG_MD5 BYTE-UNCHANGED · all mirrors byte-identical · PINNED anchors + safety lines verbatim ·
  lean budget held by own-prose reclaim · the standing "security is always HARD-STOP" guarantee untouched
```

Least-sure flag surfaced at freeze: [contract] "identical list across the three" is read as ONE canonical enumerated list in run.md + book ch.08 naming the same items + 6-verify.md pointing to run.md — NOT byte-identical prose in all three. Tin chose this ("Canonical + pointer") at the freeze; the alternative (verbatim ×3) costs heavier byte reclaim + re-creates the 3-way drift surface. Resolved at freeze — cheap to switch was pre-build.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: prose-presence (one assertion per scenario; reads the canonical guide/book files + ENGINE pins)
Plan (one test per scenario, asserting behavior not internals) — `test_stale_guide_sync.py`:
<test_plan>
  - test_no_stale_scope_gate_deferral: assert 5-build.md (×3) AND templates/TASK.md.tmpl (×2) contain NO `scope-gate-enforce` / `until it ships` / `prose discipline`; DO contain `scope_violation` / `enforced`
  - test_run_md_canonical_preconditions: assert run.md names all 8 canonical items (green · coverage · no-weaken/no-edit · loops dry · completeness-critic · deep check · refute-read recorded · residue escalates)
  - test_book_ch08_names_same_set: assert docs/08 "Auto" bullet names completeness-critic + deep check + recorded refute-read (the 3 it was missing) alongside the others
  - test_6verify_points_to_canonical: assert 6-verify.md blockquote contains a `run.md` canonical-list pointer
  - test_audit_surfaces_lints_noted: assert run.md AND 6-verify.md mention `add.py audit` surfaces `shallow_deep_check` + `risk_unset` + `refute_unrecorded`
  - test_book_missed_finding_disclosure: assert docs/08 carries the never-marked / spot-audit security disclosure
  - test_book_chapters_crossref_task: assert docs/03 names it fills §1 of TASK.md AND docs/04 names §2
  - test_engine_byte_unchanged: assert md5(add.py)==ENGINE_MD5==9d73e5ab… AND ENGINE_PKG_MD5 unchanged (prose-only invariant)
  - test_security_guarantee_intact: assert the "security is always HARD-STOP" guarantee phrase still present in 6-verify.md + book (test_protected_safety_lines_pinned backstop)
  - test_three_tree_parity_holds: assert each edited guide/book file is byte-identical across its mirror trees
</test_plan>

Tests live in: `add-method/tooling/test_stale_guide_sync.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/skill/add/phases/5-build.md` `.claude/skills/add/phases/5-build.md` `add-method/src/add_method/_bundled/skill/add/phases/5-build.md` `add-method/skill/add/run.md` `.claude/skills/add/run.md` `add-method/src/add_method/_bundled/skill/add/run.md` `add-method/skill/add/phases/6-verify.md` `.claude/skills/add/phases/6-verify.md` `add-method/src/add_method/_bundled/skill/add/phases/6-verify.md` `add-method/docs/08-step-6-verify.md` `add-method/src/add_method/_bundled/docs/08-step-6-verify.md` `add-method/../08-step-6-verify.md` `add-method/docs/03-step-1-specify.md` `add-method/src/add_method/_bundled/docs/03-step-1-specify.md` `add-method/../03-step-1-specify.md` `add-method/docs/04-step-2-scenarios.md` `add-method/src/add_method/_bundled/docs/04-step-2-scenarios.md` `add-method/../04-step-2-scenarios.md`
Strategy (ordered batches): 1. write `test_stale_guide_sync.py` RED (10 prose-presence + parity + engine-byte assertions). 2. canonical edits: 5-build.md note + TASK.md.tmpl §5 comment (kill `scope-gate-enforce`) · run.md canonical 8-item list + audit-surfaces line · 6-verify.md blockquote pointer + audit-surfaces line · book 08 same-set + missed-finding disclosure · book 03/04 cross-ref. 3. lean reclaim from each guide's OWN prose (no rebaseline); restore any PINNED anchor verbatim if a trim hits it. 4. propagate ×3 (prepare_bundle + copy to .claude + repo-root book mirror); NO engine re-pin (prose-only → ENGINE_MD5/PKG unchanged). 5. drain/drop/carry the SPEC deltas via `add.py drop-delta`/`carry-delta`. 6. full suite + check + audit green.
Known-problem fixes: a precondition-list edit to run.md(ORCHESTRATION)/6-verify.md(PHASES)/5-build.md(PHASES) trips test_skill_lean → reclaim from own prose, ratios kept · a trim that drops `overfit to the test fixtures`/`the engine never classifies`/`seven lines`/`always a HARD-STOP and is never auto-passed` or uses `blast radius` fails a pin/idiom guard → restore verbatim, reflow so a pinned phrase isn't split across a line-wrap · book repo-root token needs the `add-method/..` climb · the `add.py deltas` verbs are LIVE-scoped (drop/carry operate on live tasks via `_resolve_task`) — the 4 target deltas are all on LIVE tasks (guarantee-audit-lints/security-escalation-disclosure/delta-drain) so the verbs reach them.
Strategy actually used: as planned — the 6 batches ran in order. Two discoveries beyond the plan: (1) a THIRD stale instance — the `TASK.md.tmpl` §5 comment also said "lands in scope-gate-enforce" — folded into §3 before the freeze. (2) Two collateral guard tests (`test_scope_decl_template`: template-grammar + build-guide-section) PINNED the literal `scope-gate-enforce` token this task removes by design — updated them to assert the new `scope_violation`/enforced language (NOT weakening: same rigor, corrected token; out of the §4 red set so no tamper trip; `add-method/tooling/` covers them in §5). Lean cost ~210 B over ORCHESTRATION+PHASES, reclaimed from each guide's own prose (goal-clarity para, report-template intro, deep-check clause) — no rebaseline. Book edits also DE-staled the ch.03/04 "Produces:" lines (SPEC.md/features → §1/§2 of TASK.md). Deltas: 3 dropped (resolved) + 2 carried (engine-scope) → 0 open SPEC deltas. Engine byte-frozen (ENGINE_MD5 9d73e5ab unchanged).
Safety rule (feature-specific): prose-only — touch NO add.py / add_engine byte (ENGINE_MD5 + ENGINE_PKG_MD5 frozen); never weaken the "security is always HARD-STOP" guarantee.
Code lives in: the guide trees + book trees + templates (declared above)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2167/0; new test_stale_guide_sync 10/10; check 478/0
- [x] coverage did not decrease — prose-only + 10 new presence/parity tests; no path removed
- [x] no test or contract was altered during build — the frozen §3 + §4 red set untouched; the only test edit is a collateral guard (test_scope_decl_template) that pinned the removed stale token, corrected not weakened (see §5/§7)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP) — refute-read recorded below: EARNED
- [x] concurrency / timing of the risky operation is safe — N/A: prose-only, no code path
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; documentation edits only
- [x] layering & dependencies follow CONVENTIONS.md — engine byte-frozen (ENGINE_MD5 9d73e5ab unchanged); only guides/book/template touched
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] grep of 5-build.md + TASK.md.tmpl returns NO `scope-gate-enforce` / `until it ships` / `prose discipline`, and both say the gate is enforced — confirmed by test_no_stale_scope_gate_deferral + a live grep
- [x] reading run.md, 6-verify.md, or book ch.08 yields the SAME auto-PASS preconditions (run.md owns the 8-item list, book names the same set, 6-verify points to run.md) — confirmed by test_run_md_canonical_preconditions / test_book_ch08_names_same_set / test_6verify_points_to_canonical
- [x] run.md + 6-verify.md note `add.py audit` surfaces shallow_deep_check + risk_unset + refute_unrecorded; book ch.08 names the unescalated_security_note blind spot + spot-audit — confirmed by test_audit_surfaces_lints_noted + test_book_missed_finding_disclosure
- [x] book ch.03 names it fills §1 and ch.04 names §2 of TASK.md — confirmed by test_book_chapters_crossref_task
- [x] `add.py deltas` open SPEC-delta count drops to 0 (3 dropped/resolved + 2 carried with reasons) — confirmed by a live `add.py deltas` (was 5, now 0 open)
- [x] add.py + add_engine byte-unchanged (ENGINE_MD5 9d73e5ab + ENGINE_PKG_MD5 hold); every edited guide/book file byte-identical ×3 trees; lean held — confirmed by test_engine_byte_unchanged + test_three_tree_parity_holds + full suite

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — N/A: no production code changed; the only code edit is two assertions in test_scope_decl_template.py (the test corrects a token it was checking — exercised by the suite)
- [x] DEAD-CODE (code) — N/A: prose-only; no symbol added or orphaned (ENGINE_MD5 9d73e5ab unchanged)
- [x] SEMANTIC (prose / non-code) — read in full: re-read all 7 edited guide/book files end-to-end + the §3 contract. Confirmed: (1) 5-build.md & TASK.md.tmpl say the gate is ENFORCED (scope_violation → self-heal), no `scope-gate-enforce`/`until it ships`/`prose discipline` left; (2) run.md's auto-PASS list names all 8 items, book ch.08 names the SAME set (completeness-critic + deep check + recorded refute-read), 6-verify points to run.md; (3) run.md + 6-verify.md name shallow_deep_check + risk_unset + refute_unrecorded; book ch.08 names unescalated_security_note + the never-marked blind spot + spot-audit; (4) book ch.03/04 cross-ref §1/§2 of TASK.md; (5) the security guarantee ("always a HARD-STOP and is never auto-passed") survived the lean trims verbatim. No new claim contradicts engine behavior (scope_violation ships via cmd_gate; audit emits the 3 lints — both verified live).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) Overfit/vacuous/stubbed? No — each of the 10 new assertions checks a substantive prose fact (stale token gone · canonical 8-item list present · 3 lints named · never-marked disclosure · ×3-tree parity · engine byte-frozen); the prose genuinely SAYS what is asserted, not special-cased to a fixture. (2) The sharpest refutation — "you EDITED a test during build (test_scope_decl_template: scope-gate-enforce→scope_violation), the cardinal-rule line." Examined and rejected as a violation but FLAGGED for spot-audit: that guard is NOT in this task's §4 red set, and the token it pinned is removed BY the frozen §3 contract's design; the edit preserves equal rigor (same assertion count, the build-guide still must teach frozen + change-request + the enforcement token) — a corrected token, not a weakened check. This is the documented "collateral guard pinned the old doc-truth" pattern. The frozen §3 and §4 red set were untouched (tamper tripwire green). A human spot-audit of that one test diff is the right backstop — surfaced here, not hidden.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose run.md = single canonical enumerated list, book ch.08 reconciled to name the SAME items, 6-verify.md blockquote keeps its summary + an explicit "the full list is canonical in run.md" pointer; rejected full identical enumerated list verbatim in ALL THREE (maximal "identical" but heaviest byte cost ×3 files ×3 trees + perpetual 3-way drift surface — the very problem this task fixes) · leave 6-verify as summary-only (rejected — fails the "names the same set" goal)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — the 6 batches ran in order. Two discoveries beyond the plan: (1) a THIRD stale instance — the `TASK.md.tmpl` §5 comment also said "lands in scope-gate-enforce" — folded into §3 before the freeze. (2) Two collateral guard tests (`test_scope_decl_template`: template-grammar + build-guide-section) PINNED the literal `scope-gate-enforce` token this task removes by design — updated them to assert the new `scope_violation`/enforced language (NOT weakening: same rigor, corrected token; out of the §4 red set so no tamper trip; `add-method/tooling/` covers them in §5). Lean cost ~210 B over ORCHESTRATION+PHASES, reclaimed from each guide's own prose (goal-clarity para, report-template intro, deep-check clause) — no rebaseline. Book edits also DE-staled the ch.03/04 "Produces:" lines (SPEC.md/features → §1/§2 of TASK.md). Deltas: 3 dropped (resolved) + 2 carried (engine-scope) → 0 open SPEC deltas. Engine byte-frozen (ENGINE_MD5 9d73e5ab unchanged).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
