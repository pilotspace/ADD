# TASK: Audit lint adr_record_missing at done + observe guide + book + glossary + 3-tree skill parity

slug: adr-audit-and-docs · created: 2026-06-28 · stage: mvp
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

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` `_audit_findings` (add.py:5011) — the gate-audit core; per-task it reads `_raw_phase_bodies` §3/§6 and appends `{task, code, detail}` findings (real findings → exit 1). ADD an `adr_record_missing` check reading §7. `_raw_phase_bodies` must yield §7 (verify it parses "## 7 · OBSERVE")
  - `add-method/tooling/add.py` re-pin ENGINE_MD5 after the change (add_engine/* untouched → ENGINE_PKG_MD5 stays)
  - observe guide `skill/add/phases/7-observe.md` — 3 trees: `add-method/skill/add/`, `.claude/skills/add/`, `add-method/src/add_method/_bundled/skill/add/` (parity-tested) — add a short "Decisions (ADR)" note
  - book observe chapter `docs/09-the-loop.md` — 3 trees: `add-method/docs/`, `add-method/src/add_method/_bundled/docs/`, `.add/docs/` (test_book_parity) — document the harvested §7 ADR record
  - glossary `docs/appendix-c-glossary.md` — 3 trees: `add-method/docs/`, bundle, `.add/docs/` (test_v8_docs md5 parity) — add a "Decisions (ADR)" term
Context (working folder): milestone adr-at-observe task 3/3 (final); depends on adr-harvest (the §7 block + `_stamp_adr_record` it audits/documents); closes the milestone
Honors (patterns / conventions): grandfather like the gate-record audits (a task with NO §7 "### Decisions (ADR)" block is legacy → never retro-flagged) · audit is PURE read · finding shape `{task, code, detail}` · 3-tree parity for EVERY skill/doc surface (canonical = dogfood = bundle, byte-identical) · engine change re-pins ENGINE_MD5
Anchors the contract cites: `_audit_findings` · `adr_record_missing` code · §7 "### Decisions (ADR)" placeholder probe · the grandfather (block-absent) rule · the 3 doc/skill surfaces + their parity tests

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py audit` fires `adr_record_missing` when a done/gated (non-grandfathered) task's §7 Decisions (ADR) block was never harvested; the observe guide + book + glossary document the harvested record (3-tree parity)
Framings weighed: real-finding-grandfathered-by-block-absence (chosen — parallels the gate-record audits malformed_gate_record/gate_record_mismatch; only fires on a genuinely-broken record, and a task with no §7 block is legacy → exempt) · measure-not-block-surface-only (rejected: a gated-but-unharvested block is a real defect, not a soft guarantee like deep-checks/risk-unset; the milestone wants audit to FIRE) · check-state.json-not-§7 (rejected: the record lives in the FILE — the audit reads §7 like the other gate-record audits)
Must:
<must>
  - `_audit_findings` appends an `adr_record_missing` finding for a task it already audits (phase done/observe OR gate≠none) whose §7 has a "### Decisions (ADR)" block STILL holding its BARE `<harvested at done…>` placeholder line (the harvest never ran) — using the SAME bare-line probe `(?m)^<harvested at done[^\n]*>$` as `_stamp_adr_record` (a substring would false-positive on harvested prose that quotes the placeholder)
  - GRANDFATHER: a task whose §7 has NO "### Decisions (ADR)" block is legacy → NEVER flagged (parallels the gate-record-block-absent grandfather; protects all 84+ pre-feature done tasks)
  - the lint is PURE read — it writes nothing; `add.py audit` stays the CI enforcement gate (a real finding → exit 1)
  - the observe guide `phases/7-observe.md` gains a short "Decisions (ADR)" note; byte-identical across the 3 skill trees
  - the book observe chapter `docs/09-the-loop.md` documents the engine-harvested §7 ADR record; byte-identical across the 3 doc trees
  - the glossary `docs/appendix-c-glossary.md` gains a "Decisions (ADR)" term; byte-identical across the 3 doc trees
  - the engine change re-pins ENGINE_MD5 (add_engine/* untouched → ENGINE_PKG_MD5 unchanged)
</must>
Reject:
<reject>
  - a legacy task (no §7 "### Decisions (ADR)" block) is flagged -> "legacy_retro_flagged"
  - harvested prose that merely CONTAINS the substring "<harvested at done" trips a finding -> "false_positive_substring" (must use the bare-line probe)
  - the audit writes to any file -> "audit_not_pure"
  - a doc/skill surface diverges across its 3 trees -> "parity_break"
</reject>
After:
<after>
  - `add.py audit` fires `adr_record_missing` for a gated task whose §7 block was never harvested; every legacy task still passes; the observe guide + book + glossary document the record; all 3-tree parities hold; ENGINE_PKG_MD5 unchanged; milestone adr-at-observe closes (3/3)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ REAL-finding (exit 1) vs MEASURE-not-block (exit 0): I chose a real finding because a gated-but-unharvested §7 block is a genuine defect (the harvest always runs at gate) and the block-absent grandfather exempts every legacy task; lowest confidence because the recent audit trend (shallow_deep_check, risk_unset) leans measure-not-block; if wrong: a future edge case fires exit 1 in CI unexpectedly — trivially downgraded to `_guarantee_lint_notices`. THIS is the freeze flag.
  - [ ] §7-block-presence is the right grandfather key (absent = legacy) — confirmed: only post-feature full-template tasks carry the block; strategy-actual-writeback (task 1, pre-block) has none → exempt
  - [ ] the doc/glossary/guide additions are prose-only (no engine behavior beyond the lint) — the docs explain, the lint enforces
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a gated task whose §7 ADR block was never harvested is flagged
  Given a done/gated task whose §7 "### Decisions (ADR)" block still holds its bare "<harvested at done…>" placeholder line
  When I run add.py audit
  Then a finding {code: "adr_record_missing"} names that task
  And add.py audit exits non-zero (a real finding, the CI gate)

Scenario: a gated task whose §7 ADR block was harvested passes
  Given a done/gated task whose §7 "### Decisions (ADR)" block holds four actor-tagged lines (no placeholder)
  When I run add.py audit
  Then no adr_record_missing finding names that task
  And the file is unchanged (audit is pure read)

Scenario: a legacy task with no §7 ADR block is grandfathered
  Given a done task whose §7 has NO "### Decisions (ADR)" block (pre-feature scaffold)
  When I run add.py audit
  Then no adr_record_missing finding names that task
  And no other task's findings change

Scenario: harvested prose quoting the placeholder is not a false positive
  Given a gated task whose harvested §7 lines CONTAIN the substring "<harvested at done" inside prose (e.g. a strategy line) but hold no bare placeholder line
  When I run add.py audit
  Then no adr_record_missing finding names that task

Scenario: the record is documented across the three doc/skill trees
  Given the observe guide, the book observe chapter, and the glossary
  When I read each across its three trees (canonical · dogfood · bundle)
  Then each carries a "Decisions (ADR)" entry describing the engine-harvested §7 record
  And the three copies of each file are byte-identical
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION (add.py, inside _audit_findings — the existing per-task loop, beside the gate-record checks):
  for each already-audited task (phase in {done, observe} OR gate != "none"):
    s7 = _raw_phase_bodies(root, slug).get(7, "")
    if "### Decisions (ADR)" in s7 and re.search(r"(?m)^<harvested at done[^\n]*>$", s7):
      f(slug, "adr_record_missing",
        "§7 Decisions (ADR) block still holds its <harvested…> placeholder (never harvested at gate)")

GRANDFATHER: no "### Decisions (ADR)" in s7 -> NO finding (legacy / fast task; protects 84+ pre-feature tasks).
PROBE: the BARE-LINE regex (mirrors _stamp_adr_record). Harvested prose CONTAINING the substring
  "<harvested at done" (e.g. a strategy line quoting it) holds no bare placeholder line -> NO finding.
PURITY: _audit_findings stays read-only; finding shape {task, code, detail}; a real finding -> cmd_audit exit 1 (CI gate).

DOCS (prose; each byte-identical across its 3 trees — canonical · dogfood · bundle):
  - skill/add/phases/7-observe.md : short "Decisions (ADR)" note — what the engine harvests (§1/§3/§5/§6), when (at gate)
  - docs/09-the-loop.md           : the observe chapter documents the engine-harvested, actor-tagged §7 record
  - docs/appendix-c-glossary.md   : a "Decisions (ADR)" glossary term

INVARIANTS:
INV-1  GRANDFATHER — a §7 with no "### Decisions (ADR)" block is never flagged
INV-2  BARE-LINE PROBE — only a literal "^<harvested at done…>$" line fires; a substring never does
INV-3  PURE — audit writes nothing; every other command stays byte-identical
INV-4  3-tree byte-identical for each of the 3 doc/skill surfaces (parity-tested)
INV-5  add_engine/*.py byte-identical -> ENGINE_PKG_MD5 unchanged; only add.py re-pins ENGINE_MD5
error codes: adr_record_missing · (rejects) legacy_retro_flagged · false_positive_substring · audit_not_pure · parity_break
```

Least-sure flag surfaced at freeze: [contract] adr_record_missing is a REAL finding (exit 1), not a measure-not-block surface — chosen because a gated-but-unharvested §7 block is a genuine defect and the block-absent grandfather exempts every legacy task; if the auto-gate ever leaves a block unharvested in an edge case it would fail CI, but that IS the signal we want. Trivially downgraded to `_guarantee_lint_notices` (exit 0) if it proves noisy. Docs are prose-only; the only engine change is this one PURE read.
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

Coverage target: behavior-anchored; every Must + Reject has ≥1 assertion (test_adr_audit.py, 6 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_lint_fires_on_unharvested_block: gated task, §7 reset to placeholder → adr_record_missing fires — RED ✓
  - test_unharvested_is_a_real_finding_not_a_soft_surface: it rides in findings[] not guarantee_lints[] (--json) — RED ✓
  - test_docs_carry_adr_term_and_parity: observe guide + book + glossary each carry "Decisions (ADR)" + 3-tree md5 parity — RED ✓
  - test_harvested_block_passes_and_audit_is_pure: harvested §7 → no finding; file byte-unchanged (pure)
  - test_legacy_no_block_grandfathered: §7 with no block → no finding (grandfather)
  - test_substring_in_prose_no_false_positive: a harvested line CONTAINING "<harvested at done" (not a bare line) → no finding
</test_plan>

Tests live in: `add-method/tooling/test_adr_audit.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_adr_audit.py` `add-method/skill/add/phases/7-observe.md` `.claude/skills/add/phases/7-observe.md` `add-method/src/add_method/_bundled/skill/add/phases/7-observe.md` `add-method/docs/09-the-loop.md` `add-method/src/add_method/_bundled/docs/09-the-loop.md` `.add/docs/09-the-loop.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `add-method/../09-the-loop.md` `add-method/../appendix-c-glossary.md`
Strategy (ordered batches): 1. TESTS — new test_adr_audit.py: lint fires on unharvested §7 (RED) · harvested passes · legacy grandfathered · substring-no-false-positive · audit pure · 3-tree parity of the 3 doc surfaces. 2. BUILD — add the `adr_record_missing` probe in `_audit_findings`; write the observe-guide note + book paragraph + glossary term, cp each ×3. 3. Re-pin ENGINE_MD5; confirm ENGINE_PKG_MD5 unchanged; suite green.
Known-problem fixes: a substring false-positive on harvested prose → use the BARE-LINE probe (not `in`) · flagging legacy tasks → grandfather on block-absence · a doc tree drifting → cp canonical ×3 + md5 · the §3 fence truncating on a line-leading `##` → none here (fence has no `##`) · forgetting the bundle/dogfood add.py mirrors or a doc tree → declared all 14 paths in §5 up front (the adr-harvest scope lesson)
Strategy actually used: as planned (RED tests → bare-line probe in _audit_findings → docs ×3 → re-pin), plus one unplanned reclaim: the phases lean pool had only ~2 bytes of headroom, so the observe-guide note required tightening that guide's own prose (~180 bytes) to hold the frozen lean budget rather than weaken it; also synced the repo-ROOT book mirror (4th tree) test_book_parity enforces.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
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

- [x] all tests pass — full tooling suite 2132/0
- [x] coverage did not decrease — +6 new tests (test_adr_audit.py); no test removed/weakened
- [x] no test or contract was altered during build — frozen §3 untouched; build touched only add.py + engine_pin + the 3 doc surfaces (test_adr_audit.py was authored in the TESTS phase)
- [x] the green was EARNED, not gamed — adversarial refute-read run (subagent, autonomy: auto); verdict EARNED — see DEEP CHECKS
- [~] concurrency / timing — N/A: the lint is a pure synchronous read of an in-memory string; no IO, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re` only; no new import; no network/FS write
- [x] layering & dependencies follow CONVENTIONS.md — the probe sits inside the existing `_audit_findings` per-task loop beside the gate-record audits; same `{task, code, detail}` shape; no new module
- [x] a person reviewed and approved the change — the §3 freeze @ v1 (Tin Dang) was the human approval; verify auto-gates on complete evidence under autonomy: auto (no security/residue to escalate)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py audit` on a gated task with an unharvested §7 block prints `adr_record_missing` + exits non-zero; a legacy (no-block) task is silent — confirmed by test_lint_fires_on_unharvested_block + test_legacy_no_block_grandfathered + test_unharvested_is_a_real_finding_not_a_soft_surface
- [x] the harvested adr-harvest task (whose strategy line quotes "<harvested at done") raises NO finding — confirmed: full-repo `add.py audit --json` → adr_record_missing count: 0; findings: 0
- [x] the observe guide + book §09 + glossary each say "Decisions (ADR)" and are byte-identical across their 3 (book: 4) trees — confirmed by md5 trios (test_adr_audit + test_book_parity + test_v8_docs all green)
- [x] only add.py + the docs changed — ENGINE_PKG_MD5 e87f5652 unchanged (add_engine/* untouched), ENGINE_MD5 re-pinned → 03b422b2

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the `adr_record_missing` probe is reached inside the `_audit_findings` per-task loop (after the waiver check) and exercised by 5 of the 6 new tests; `cmd_audit` surfaces it via `findings` (drives exit 1)
- [x] DEAD-CODE (code) — no orphan introduced; the probe reuses `raw` (already computed §-bodies) and `f(...)`; no helper left uncalled
- [x] SEMANTIC (prose) — read all 3 doc surfaces in full: observe-guide note, book §09 "The decision record (ADR)" paragraph, glossary term. Adversarial refute-read confirmed the lean-budget prose-trim of 7-observe.md (goal/items 1–4) lost NO instruction — every rule (release-behind-flag · scenarios-as-monitors · spec-delta · voice-delta open→confirm→rewrite, soul.md routing/human-is-only-writer) survives; the harvest faithfulness claims hold

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose real-finding-grandfathered-by-block-absence; rejected measure-not-block-surface-only (rejected: a gated-but-unharvested block is a real defect, not a soft guarantee like deep-checks/risk-unset; the milestone wants audit to FIRE) · check-state.json-not-§7 (rejected: the record lives in the FILE — the audit reads §7 like the other gate-record audits)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (RED tests → bare-line probe in _audit_findings → docs ×3 → re-pin), plus one unplanned reclaim: the phases lean pool had only ~2 bytes of headroom, so the observe-guide note required tightening that guide's own prose (~180 bytes) to hold the frozen lean budget rather than weaken it; also synced the repo-ROOT book mirror (4th tree) test_book_parity enforces.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
