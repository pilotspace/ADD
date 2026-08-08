# TASK: Wire both validators into add.py check + cross-file token resolution — named reds on layer/catalog/tree violations

slug: udd-check-lint · created: 2026-06-13 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
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
  - `add-method/tooling/add.py:cmd_check` (L1360) — the read-only linter. Accumulates `checks: list[(ok, desc,
    reason)]` (L1374); a FAIL = `checks.append((False, "<desc>", "<named_code>: <detail>"))`; warnings are a
    SEPARATE `warnings` list (L1381, never red). Tally (L1521–1541): `failed = len-passed`; text `FAIL  <desc>:
    <reason>` / `PASS  <desc>` (TWO spaces); summary `check: N passed, M failed (K warnings)`; JSON shape
    `{passed,failed,warned,warnings:[{name,reason}],checks:[{ok,name,reason}]}`; `raise SystemExit(1)` IFF failed>0.
    cmd_check NEVER mutates a file. The NEW "UDD foundation" section appends here, mirroring the wave-section style.
  - `add-method/tooling/add.py:_token_layer_violations` (L1142) — `(tokens: dict) -> list[(code,path,detail)]`,
    [] == valid; 6 codes (unknown_layer · unknown_type · unresolved_alias · cross_layer_citation ·
    primitive_has_alias · malformed_value). Task 1. udd-check-lint CALLS it on the loaded tokens.json.
  - `add-method/tooling/add.py:_catalog_tree_violations` (L1270) — `(catalog: dict, tree: dict) -> list[(code,
    path,detail)]`, 9 codes. Task 2. The DEFERRAL: its token-prop check (L1261–1266) is LAYER-ONLY —
    `value[1:-1].split(".",1)[0] != "semantic"` → non_semantic_prop_token; it does NOT resolve the alias's
    EXISTENCE in tokens.json nor $type-match (no tokens.json in its signature). udd-check-lint fills exactly that.
Context (working folder):
  - the NAMED SET has NO path constant in add.py yet (not wired anywhere). Convention (templates/udd-catalog.md L9–14
    + templates/DESIGN.md.tmpl `## Foundation`): bare project-relative names → live directly under `.add/` (the
    `find_root()` root): `root/"tokens.json"` · `root/"catalog.json"` · `root/"prototypes"/"*.json"`. The shipped
    `templates/*.sample.json` are TEMPLATES the AI adapts into those live files — they are NOT the live files.
  - file-discovery idiom to reuse (the wave section, L1564–1566): `sorted(p for p in (root/"prototypes").glob("*.json")
    if p.is_file())` for the many; `root/"tokens.json"` + `.exists()` for the singletons.
  - JSON-load idiom: NO `_load_json` helper; inline `try: json.loads(p.read_text()) except (JSONDecodeError, OSError)`.
    Fail-CLOSED like the wave section: a malformed/missing file → `checks.append((False, ..., "<code>"))` + continue,
    NEVER `_die` (which would abort all of cmd_check).
Honors (patterns / conventions):
  - SILENT-when-absent: a project with NO named-set files emits NO UDD checks (the wave section is silent without a
    ledger). REQUIRED for green — `test_check_passes_on_clean_project` + this dogfood repo (no tokens.json) must stay 0-fail.
  - cmd_check is READ-ONLY (asserted before==after in many suites); the UDD section must not write.
  - add.py code change → ×3 mirrors byte-identical (`test_bundle_parity` add.py canonical↔bundle) + re-aim
    `engine_pin.py:ENGINE_MD5` (`test_shared_engine_pin` checks all 3 copies) carrying udd-design-template.
  - the output-format + exit contract is pinned by ~30 cmd_check tests (test_add.py · test_waiver · test_merge_base_
    enforcement · test_goal_auto_ready_gate · test_deltas_lint · …) — the new section must not break PASS/FAIL/WARN
    prefixes, the summary line, the JSON schema, or SystemExit(1)-iff-failed.
Anchors the contract cites: `cmd_check` (the new UDD-foundation section) · `_token_layer_violations` + `_catalog_tree_violations` (composed, unchanged) · a NEW pure `_prop_token_resolution_violations(tokens, catalog, tree)` (the cross-file resolution task 2 deferred — existence + $type-match of a semantic token-prop alias) · the named-set paths `root/tokens.json` · `root/catalog.json` · `root/prototypes/*.json` · the SILENT-when-absent rule · the new codes unresolved_prop_token · prop_token_type_mismatch · engine_pin re-aim.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: wire BOTH pure validators into `add.py check` as a new SILENT-when-absent "UDD foundation" section, plus
the cross-file token resolution tasks 1+2 deferred — so `add.py check` goes RED with a NAMED code on any
layer/catalog/tree/cross-file violation in a project's named set (`tokens.json` · `catalog.json` ·
`prototypes/*.json`), and stays silent + green when there is no named set. This is the milestone's exit criterion
("`add.py check` goes red, with a named code, on a layer or catalog violation") and the composer that closes the
two deferrals (task-2 token-prop existence/$type-match; the single cross-file holder of tokens+catalog+tree).

Framings weighed: compose-into-cmd_check (chosen) · standalone `add.py lint-design` subcommand · validate-on-init.
  - CHOSEN compose-into-cmd_check: the milestone names `check` — the named reds ride the existing read-only linter;
    one discoverable surface, no second command a UI project could forget to run.
  - standalone subcommand: rejected — splits the lint surface; the exit criterion is `check`, not a new verb.
  - validate-on-init/on-build: rejected — check is the read-only monitor; gating a write seam is a heavier, separate
    concern (additive later); this task only adds named reds to the monitor.

Must:
<must>
  - SECTION: a new "UDD foundation" section in `cmd_check` (read-only) that, when named-set files exist under the
    project root, loads them and appends one FAIL per violation with the validator's NAMED code as the reason;
    a present-and-clean file yields a PASS line. Mirrors the wave-section style; writes nothing.
  - TOKENS: if `root/design/tokens.json` exists → load (fail-closed) → `_token_layer_violations(tokens)` → each
    `(code,path,detail)` becomes a FAIL whose reason starts with `<code>`.
  - CATALOG×TREES: if `root/design/catalog.json` exists → load (fail-closed); for each `root/design/prototypes/*.json`
    (sorted, `.is_file()`) → load (fail-closed) → `_catalog_tree_violations(catalog, tree)` → FAILs.
  - CROSS-FILE (the deferral): when tokens.json + catalog.json + a tree all load, a NEW pure
    `_prop_token_resolution_violations(tokens, catalog, tree)` resolves every tree token-prop alias that targets the
    `semantic` layer against tokens.json — not present → `unresolved_prop_token`; present but its `$type` ≠ the
    catalog PropSpec's declared `token:<$type>` → `prop_token_type_mismatch`. PURE: never mutates inputs, stdlib
    only, deterministic document order, `[]` == clean.
  - LOCATION (Fork A, frozen): the named set lives under `.add/design/`; reconcile the DESIGN.md.tmpl + udd-catalog.md
    live-file pointers to `design/…` (×3 each) to match.
  - SILENT-WHEN-ABSENT: a project with NO design/tokens.json AND NO design/catalog.json AND NO design/prototypes/ emits
    ZERO UDD checks (no PASS / FAIL / WARN) — keeps clean & non-UI projects (and this dogfood repo) green.
  - FAIL-CLOSED LOAD: a present-but-malformed named-set JSON → a FAIL with a named code (`malformed_tokens_json` ·
    `malformed_catalog_json` · `malformed_prototype_json`), NEVER a crash, NEVER `_die` (cmd_check must finish).
  - PRESERVE: the section keeps cmd_check read-only; PASS/FAIL/WARN prefixes, the summary line, the JSON schema, and
    `SystemExit(1)`-iff-failed are unchanged — the ~30 existing cmd_check tests stay green.
  - MIRRORS+PIN: add.py ×3 byte-identical (`test_bundle_parity`); `engine_pin` re-aimed (carry udd-design-template).
</must>
Reject:
<reject>
  - a `tokens.json` layer/citation/value violation -> the validator's code surfaced as a check FAIL (e.g. "cross_layer_citation")
  - a `catalog.json`/tree violation -> the validator's code as a FAIL (e.g. "tree_cites_uncataloged_component")
  - a tree token-prop alias resolving to no semantic token in tokens.json -> "unresolved_prop_token"
  - a tree token-prop alias whose semantic token's $type ≠ the catalog prop's declared $type -> "prop_token_type_mismatch"
  - a present-but-malformed named-set JSON file -> "malformed_tokens_json" | "malformed_catalog_json" | "malformed_prototype_json"
</reject>
After:
<after>
  - on a project whose named set is clean, the UDD section emits only PASS lines and check stays green.
  - on any violation, check exits 1 with the named code in the FAIL reason; the named-set files are read, never written.
  - a project with no named set sees NO change to check output (silent); this dogfood repo stays 305+/0.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ NAMED-SET LOCATION (Fork A) — RESOLVED at the freeze to the `.add/design/` subdir (`root/design/tokens.json` ·
    `root/design/catalog.json` · `root/design/prototypes/*.json`) — the human chose the grouped subdir over the `.add/`
    root to keep the root uncluttered. Was lowest-confidence because nothing pinned the location and it is a layout
    convention the human owns. Reconciled: the DESIGN.md.tmpl + udd-catalog.md live-file pointers move to `design/…`
    (contained doc co-edit; the task-3 substring tests survive — `design/tokens.json` still contains `tokens.json`).
  - [ ] CROSS-FILE CODES (Fork B) — two new codes `unresolved_prop_token` · `prop_token_type_mismatch` in a new pure
    helper. If the names/scope are wrong: rename/extend (additive, test-guarded).
  - [ ] INDEPENDENT PRESENCE (Fork C) — each validator runs on whatever is present (tokens alone → layer check;
    catalog+tree → structural; all three → cross-file). If wrong (require all-or-nothing): tighten the guard (additive).
  - [ ] SILENT-WHEN-ABSENT is FORCED by the green-on-clean tests + the optional-doc nature — low risk, but it means a UI
    project that FORGETS the named set gets no nudge (a future WARN-when-DESIGN.md-present-but-no-tokens is additive).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a clean named set passes check
  Given a project with a valid tokens.json + catalog.json + a prototype that all validate clean
  When add.py check runs
  Then check exits 0, the UDD section emits PASS lines, and no file is written

Scenario: a token-layer violation goes red with its named code
  Given a project tokens.json with a semantic token citing a component token (cross_layer_citation)
  When add.py check runs
  Then check exits 1 and a FAIL reason starts with "cross_layer_citation"
  And the tokens.json file is read, never modified

Scenario: a catalog/tree violation goes red with its named code
  Given a prototype that cites a component absent from catalog.json
  When add.py check runs
  Then check exits 1 and a FAIL reason starts with "tree_cites_uncataloged_component"
  And catalog.json + the prototype are read, never modified

Scenario: an unresolved token-prop alias goes red (the deferral, half 1)
  Given a prototype whose token-prop alias "{semantic.color.ghost}" has no match in tokens.json
  When add.py check runs
  Then check exits 1 and a FAIL reason starts with "unresolved_prop_token"
  And a sibling prop whose alias DOES resolve reports no such failure

Scenario: a token-prop $type mismatch goes red (the deferral, half 2)
  Given a prototype token-prop bound to a catalog PropSpec token:color, but the resolved semantic token's $type is dimension
  When add.py check runs
  Then check exits 1 and a FAIL reason starts with "prop_token_type_mismatch"
  And a sibling prop whose $type matches reports no such failure

Scenario: a malformed named-set JSON fails closed, never crashes
  Given a tokens.json that is not valid JSON
  When add.py check runs
  Then check exits 1 with a FAIL reason "malformed_tokens_json" (no traceback, cmd_check still finishes its other sections)
  And the malformed file is read, never rewritten

Scenario: a project with no named set is silent
  Given a project with no .add/design/tokens.json, no .add/design/catalog.json, and no .add/design/prototypes/ (this dogfood repo)
  When add.py check runs
  Then the output contains NO UDD-section line (no PASS/FAIL/WARN naming tokens/catalog/prototype) and check stays green

Scenario: the cross-file resolver is pure and deterministic
  Given tokens.json + catalog.json + a tree with two injected cross-file faults
  When _prop_token_resolution_violations runs twice
  Then it returns the same ordered list both times, reports both injected faults, and mutates none of its three inputs

Scenario: the existing check contract is preserved
  Given any project the existing cmd_check tests exercise
  When the suite runs
  Then the PASS/FAIL/WARN prefixes, the "check: N passed, M failed" summary, the --json schema, and SystemExit(1)-iff-failed are unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CMD_CHECK — a new read-only "UDD foundation" section (appended to the existing `checks` list; writes nothing):
  Discovery (Fork A — under the `.add/design/` subdir of the project root = `find_root()`):
    TOKENS   = root/"design"/"tokens.json"                       (singleton, .exists())
    CATALOG  = root/"design"/"catalog.json"                       (singleton, .exists())
    TREES    = sorted(root/"design"/"prototypes"/*.json, .is_file())
  SILENT-WHEN-ABSENT: if none of TOKENS/CATALOG/TREES exist → append NOTHING (no PASS/FAIL/WARN). (A clean/non-UI
    project — and this dogfood repo — stays byte-for-byte unchanged in check output.)
  Per present file, FAIL-CLOSED load (inline try/except json.loads; on JSONDecodeError/OSError → one FAIL, then
    continue — NEVER _die, NEVER crash):
    tokens.json present:
      malformed → checks.append((False, "tokens.json parses", "malformed_tokens_json: <detail>"))
      else → V = _token_layer_violations(tokens); clean → 1 PASS "tokens.json layer-valid";
             else one FAIL per v: (False, "tokens.json layer-valid", "<code>: <path> — <detail>")
    catalog.json present:
      malformed → (False, "catalog.json parses", "malformed_catalog_json: <detail>")
    each prototype tree:
      malformed → (False, "prototype '<name>' parses", "malformed_prototype_json: <detail>")
      else (catalog loaded clean) → V = _catalog_tree_violations(catalog, tree)
             + (tokens loaded clean) _prop_token_resolution_violations(tokens, catalog, tree)
             clean → 1 PASS "prototype '<name>' valid"; else one FAIL per v: (False, "prototype '<name>' valid",
             "<code>: <path> — <detail>")
  The two existing validators are COMPOSED UNCHANGED (no signature/behavior change). The output format
  (PASS/FAIL/WARN prefixes · "check: N passed, M failed (K warnings)" · the --json schema), read-only-ness, and
  `raise SystemExit(1)` IFF failed>0 are PRESERVED — the ~30 existing cmd_check tests stay green.

NEW PURE HELPER (the deferral task 2 left — the single holder of tokens+catalog+tree):
  fn _prop_token_resolution_violations(tokens: dict, catalog: dict, tree: dict) -> list[tuple[str,str,str]]
    []                      -> every token-prop alias resolves to an existing semantic token of the right $type
    [(code, path, detail)…] -> one tuple per violation, deterministic document order (elements then props in key order)
    PURE + TOTAL: never mutates inputs; stdlib only; never raises on dict inputs (defensive — skips non-dict
      elements/props/groups; those structural faults are _catalog_tree_violations' job, not re-flagged here).
    SCOPE — acts ONLY on a prop that is BOTH (a) a catalog PropSpec {type:"token", token:<$type>} AND (b) a tree
      value that is a `{semantic.dotted.path}` alias (i.e. the props task-2's LAYER-only check passed). Anything
      else (non-token prop · non-alias · non-semantic alias · uncataloged component · unknown prop) is SKIPPED —
      task 1/2 already own those codes; no double-flag.
    RESOLUTION (DTCG $type inheritance — confirmed from tokens.sample.json: `$type` sits on the GROUP, the leaf
      token carries only `$value`): walk tokens by the path segments after "semantic", tracking the NEAREST ancestor
      `$type` seen; the alias must terminate at a TOKEN node (a dict carrying `$value`):
        terminal node absent / not a token (a group with no $value, or a non-dict) -> "unresolved_prop_token"
        terminal token's inherited $type ≠ the catalog PropSpec's `token` $type    -> "prop_token_type_mismatch"
    path = "elements.<id>.props.<prop>" (matches _catalog_tree_violations' path grammar).

CODES (the udd-check-lint named reds, all surfaced inside cmd_check):
  composed from task 1: unknown_layer · unknown_type · unresolved_alias · cross_layer_citation · primitive_has_alias · malformed_value
  composed from task 2: malformed_catalog · missing_root · tree_cites_uncataloged_component · unknown_prop ·
                        prop_type_mismatch · non_semantic_prop_token · dangling_child · children_not_allowed · malformed_element
  NEW cross-file:       unresolved_prop_token · prop_token_type_mismatch
  NEW fail-closed load:  malformed_tokens_json · malformed_catalog_json · malformed_prototype_json

BOUNDARY:
  Fork A (location) — FROZEN to the `.add/design/` subdir (root/design/tokens.json · root/design/catalog.json ·
    root/design/prototypes/*.json), keeping the `.add/` root uncluttered (human choice at the freeze). The
    DESIGN.md.tmpl + udd-catalog.md live-file pointers are reconciled to `design/…` as part of THIS task (×3 each;
    the task-3 substring tests survive — `design/tokens.json` still contains `tokens.json`).
  Fork B (codes) — exactly the two new cross-file codes above; existence + $type-match, nothing more (interactivity /
    state passthrough stays unlinted, as in task 2).
  Fork C (presence) — INDEPENDENT: tokens alone → layer check; catalog+tree → structural; all three → + cross-file.
    cmd_check is NAMED-not-otherwise-touched: only the new section is added; no existing section changes.

Files touched (→ §5 scope): add.py (+2 mirrors) the new cmd_check UDD section + the new pure
  `_prop_token_resolution_violations` · engine_pin.py re-aim (carry udd-design-template) ·
  templates/DESIGN.md.tmpl (+2 mirrors) + templates/udd-catalog.md (+2 mirrors) — the live-file pointers reconciled
  to `design/…` (Fork A) · test_udd_check_lint.py (NEW red suite, this task — lives in add-method/tooling/ for `import add`).
```

Least-sure flag surfaced at freeze: [contract] FORK A — the NAMED-SET LOCATION, FROZEN to `.add/design/`
  (`root/design/tokens.json` · `root/design/catalog.json` · `root/design/prototypes/*.json`). It was the
  lowest-confidence point because nothing pinned the location and it is a layout convention the human owns; the human
  chose the `.add/design/` subdir over the `.add/` root to keep the root uncluttered. The DESIGN.md.tmpl +
  udd-catalog.md live-file pointers are reconciled to `design/…` to match (a contained doc co-edit; no validator change).

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-13.
  v1 (the freeze approval, "Freeze — .add/design/ subdir"): Fork A (the named-set LOCATION — the flagged
  lowest-confidence point) RESOLVED to the `.add/design/` subdir (root/design/tokens.json · root/design/catalog.json ·
  root/design/prototypes/*.json) over the `.add/` root, to keep the `.add/` root uncluttered. §1/§2/§3 discovery paths
  amended to `design/…`; §5 scope expanded with DESIGN.md.tmpl + udd-catalog.md (×3 each) so their live-file pointers
  reconcile to `design/…` before the doc is inconsistent (the task-3 substring tests survive). All other terms (the
  two composed validators · the new pure `_prop_token_resolution_violations` · the 2 cross-file + 3 fail-closed codes ·
  silent-when-absent · read-only/format/exit preservation · Forks B/C) unchanged.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% (the new resolver + the cmd_check UDD section's discovery/compose/fail-closed/silent paths)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  PropTokenResolutionTest (the new pure helper):
  - test_clean_triple_resolves / test_shipped_samples_resolve_clean: clean inputs → [] (incl. the shipped samples)
  - test_unresolved_prop_token: an alias with no semantic match → ("unresolved_prop_token", path)
  - test_prop_token_type_mismatch: token:color prop bound to a dimension token → ("prop_token_type_mismatch", path)
  - test_group_alias_is_unresolved: an alias terminating at a GROUP (no $value) → unresolved_prop_token
  - test_skips_non_token_and_non_semantic_props: non-alias literal / primitive alias → [] (task 1/2 own those)
  - test_pure_and_deterministic: two faults, run ×2 same order, none of tokens/catalog/tree mutated
  CheckUddSectionTest (the cmd_check integration over .add/design/):
  - test_clean_named_set_passes: clean triple → exit 0, a UDD PASS line, design/ files byte-unchanged (read-only)
  - test_token_layer_violation_red: cross_layer_citation tokens.json → exit 1, "cross_layer_citation" in out
  - test_catalog_tree_violation_red: uncataloged component → exit 1, "tree_cites_uncataloged_component" in out
  - test_unresolved_prop_token_red / test_prop_token_type_mismatch_red: the deferral → exit 1, the named code in out
  - test_malformed_tokens_failclosed: invalid JSON → exit 1, "malformed_tokens_json" + "check:" tally (no crash)
  - test_no_named_set_is_silent: no design/ → exit 0, no "layer-valid"/"prototype '" line (the dogfood case)
</test_plan>

Tests live in: `add-method/tooling/test_udd_check_lint.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_udd_check_lint.py` `add-method/tooling/templates/DESIGN.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/DESIGN.md.tmpl` `.add/tooling/templates/DESIGN.md.tmpl` `add-method/tooling/templates/udd-catalog.md` `add-method/src/add_method/_bundled/tooling/templates/udd-catalog.md` `.add/tooling/templates/udd-catalog.md`
Strategy (ordered batches): 1. red suite + JSON fixtures (a clean named set + per-code broken variants) → red for the right reason. 2. `_prop_token_resolution_violations` in canonical add.py (the DTCG $type-inheritance walk) → its unit tests green. 3. the cmd_check UDD section (discovery under `.add/design/` · fail-closed load · compose both validators + the resolver · silent-when-absent) → section tests green + the ~30 existing cmd_check tests still green. 4. reconcile DESIGN.md.tmpl + udd-catalog.md live-file pointers to `design/…` (×3 each, byte-identical) — re-run the task-3 suite to confirm its substring tests survive. 5. mirror add.py ×2 + re-pin engine_pin.py (`re-aimed @ udd-check-lint`, carry `udd-design-template`) → parity green. 6. pin self-test green.
Safety rule (feature-specific): cmd_check stays READ-ONLY (write nothing) + FAIL-CLOSED (a malformed/missing named-set file → a named FAIL + continue, NEVER _die, NEVER a traceback); the new section is PURELY ADDITIVE — no existing cmd_check sub-section changes; SILENT-when-absent (no named set → zero new output) so this dogfood repo + clean projects stay green; the resolver is pure/total (never mutates, never raises on dict inputs).
Code lives in: `add-method/tooling/add.py` (cmd_check UDD section + `_prop_token_resolution_violations`; the two existing validators are composed unchanged).
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

- [x] all tests pass — full tooling suite 996 OK on python3.14 + python3.10; new test_udd_check_lint.py 18/18; add.py check 310/0 (silent on this no-design/ repo).
- [x] coverage did not decrease — +18 net new tests (was +14 at build; +4 added at verify, none removed); the resolver, the cmd_check UDD section's discovery/compose/fail-closed/silent paths, AND the two previously-untested fail-closed codes + two no-double-flag boundaries are now covered.
- [x] no test or contract was altered during BUILD — the build changed zero tests, zero contract. (The fix + 4 tests below happened at VERIFY in response to the refute, routed honestly back through the tests phase — `phase tests` → re-snapshot at tests→build → re-advance — NOT slipped in during build; `check` reported NO build_tampered after the re-baseline. §3 FROZEN @ v1 untouched — this was a CODE-faithfulness fix, not a contract change: the §3 'no double-flag' clause and the §1 Reject malformed codes were already the law; the code now obeys them.)
- [x] the green was EARNED — adversarial refute-read ran (python-expert subagent, autonomy=auto). Verdict: REFUTED on CONTRACT-FAITHFULNESS grounds — NO confirmed test cheat, NO vacuous/overfit live-path assert, NO security finding. FIVE gaps disclosed: (1 mine, manual review) the resolver DOUBLE-FLAGGED a malformed token PropSpec (task-2's malformed_catalog); (refute #1/#2) it also double-flagged a resolved semantic token whose inherited $type is malformed/absent (task-1's unknown_type); (refute #3/#4) malformed_catalog_json + malformed_prototype_json — §1 Reject codes — shipped UNTESTED. ALL FIVE closed before the gate (close-gap-before-gate): two `want ∉ _TOKEN_TYPES` / `got ∉ _TOKEN_TYPES` skip-guards route the malformed shapes back to their task-1/2 owners (manually re-probed: all 3 double-flag shapes → [], while unresolved/real-mismatch/clean still fire correctly); +2 red no-double-flag resolver tests (red-first against the unfixed code, green after) + 2 fail-closed integration tests + the clean test strengthened to assert the prototype PASS line (the refute's one WEAKLY-SPECIFIED flag).
- [x] concurrency / timing — N/A: cmd_check is single-threaded + READ-ONLY; the three new functions are pure/total (no shared state, no I/O beyond read_text, never raise on dict inputs). The read-only-ness is asserted (before==after) by test_clean_named_set_passes + the ~30 existing cmd_check suites.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (json · pathlib); the named set is parsed with json.loads (data, never code — no eval/exec/subprocess/network); files are read, never written; fail-CLOSED on malformed JSON (a named code, never a traceback, never _die).
- [x] layering & dependencies follow CONVENTIONS.md — the new section mirrors the wave-section style (silent-when-absent, fail-closed, append to the existing `checks` list before the tally); it COMPOSES the two pre-existing pure validators unchanged; no new layer, no import added.
- [x] a person reviewed — auto-gated on evidence under autonomy=auto; surfaced to Tin Dang (the refute + the five closes + the manual re-probe). No security/concurrency/architecture residue and autonomy stayed `auto`, so the auto-gate applies.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `_semantic_token_index` ← called by `_prop_token_resolution_violations` (add.py:1402); `_prop_token_resolution_violations` ← called by `_udd_named_set_checks` (add.py:1492); `_udd_named_set_checks` ← called by cmd_check (add.py:1665, `checks.extend(...)` before the tally). End-to-end confirmed green by the 6 CheckUddSectionTest integration tests.
- [x] DEAD-CODE (code) — no new unused or orphaned symbol; all three functions are reachable from cmd_check; `_TOKEN_TYPES` (reused by the new skip-guards) pre-existed.
- [x] SEMANTIC (prose / non-code) — the DESIGN.md.tmpl + udd-catalog.md live-file pointers were reconciled to `design/…` (Fork A) and re-checked: the task-3 substring tests survive (`design/tokens.json` still contains `tokens.json`); all ×3 mirrors byte-identical (the parity suites are green).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-gated under autonomy=auto; refute ran + 5 gaps closed + manually re-probed) · date: 2026-06-13

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the per-code FAIL rate of the UDD section on real projects — especially the cross-file pair (unresolved_prop_token · prop_token_type_mismatch); a spike in either after a tokens.json/catalog.json edit is the signal that a design change broke a binding. The silent-when-absent rate (UI projects with a DESIGN.md but no design/ named set) is the leading nudge metric for the future WARN.
Spec delta for the next loop: two refute observations are NOT violations but are future-additive nudges — (a) a standalone catalog.json (no tokens, no trees) emits no structural PASS; (b) a `prototypes` that is a FILE not a dir is silently ignored. Both could become additive WARNs (a separate task) without touching this validator's contract.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a COMPOSING validator needs first-class "no-double-flag" boundary tests — proof that a sibling validator's codes are NOT re-emitted — not just per-code happy/sad tests (evidence: the build green missed 3 double-flag shapes; the verify refute caught them; +2 red boundary tests now guard them).
- [SDD · folded] cross-check every §1 Reject code against a §4 test line at the contract freeze — an asymmetry here shipped 2 untested Reject codes (malformed_catalog_json · malformed_prototype_json) past a green build (evidence: refute #3/#4; +2 fail-closed tests closed them).
- [UDD · folded] DTCG $type-inheritance means a resolved token's effective $type can be malformed/absent at the GROUP — a cross-file resolver must treat "resolved $type ∉ the valid set" as the UPSTREAM (task-1 unknown_type) validator's concern, never its own mismatch (evidence: the `got ∉ _TOKEN_TYPES` skip-guard).
- [ADD · folded] the verify-gate adversarial refute surfaces contract-faithfulness gaps even when the build is green AND honest (no cheat) — close-gap-before-gate caught 5 here that the build's own green missed (evidence: 1 manual + 4 refute findings, all closed via an honest re-baseline through `phase tests`, never by forcing the gate).
