# TASK: Replace method slang with domain-standard terminology

slug: ubiquitous-language · created: 2026-06-07 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: replace the method's 17 invented slang terms with domain-standard terminology across the
  agent surface (skill/add), the scaffold templates, the book docs, README/GETTING-STARTED, and
  add.py's emitted prose — via a ratified change-request that revs the two FROZEN v17 artifacts
  (WORDING_RUBRIC → v2, SEMANTIC_INVENTORY → v2). §3 freezes the MAP; the surface-wide rename is
  staged BUILD behind it. Machine tokens (CLI verbs · reject codes · state keys · file names) keep
  their names, bridged in the glossary.

> Intake rationale (recorded per intake.md): the rename modifies ALREADY-FROZEN scope — wording-rubric
> §3 (keep_list, F3 fence) + semantic-inventory §3 (S1/S2 anchors). Frozen-scope test fires first →
> `change-request`, carried by this task because both owning tasks are archived (v17); precedent:
> rewrite-core carrying the ratified ENGINE_FILES CR-1. Human confirmed at intake (Tin Dang, 2026-06-07):
> full 17-term Group-A map · change-request route, no new milestone · all four surfaces · CR-2 add.py
> prose included · lint stays phrase-bound (no match-rule change).

Framings weighed: freeze-the-map / stage-the-build in ONE carrier task (chosen — human override of a
  v18 milestone at intake; the map is the reviewable decision, the rename is mechanical execution
  behind gates; the split line is pre-drawn if build proves too big) · new-major v18 with a v17-style
  5-task split (rejected at intake — human sized it smaller) · gloss-only GLOSSARY anchoring, no rename
  (rejected at intake — the ask is replacement, not annotation).

Must:
  - CR-R — WORDING_RUBRIC → v2: move the 11 renamed keep_list terms (one-approval front · seam · fold ·
    competency delta · least-sure · touch-boundary · trust layer · evidence auto-gate · autonomy dial ·
    survivor · intake altitude) OUT of keep_list INTO idiom_map as `[mapped]` rows carrying their §3
    replacements; ADD the 6 never-listed slang terms (lock-down · blind-spot · red safety net ·
    forward spine · on-ramp · state/story surface) as `[mapped]` rows. All entries PHRASE-BOUND —
    the match rule ("never a single bare word") is UNCHANGED. Each new domain term enters keep_list
    in the SAME commit its rename lands (the atomic F3 swap), never before.
  - CR-I — SEMANTIC_INVENTORY → v2: re-anchor the `never-self-fold` invariant (+ its coverage key and
    the rubric's negative_keep_list twin) to the renamed prose with IDENTICAL meaning (the
    human-confirm boundary on foundation writes); every other unit, anchor, and machine token unchanged.
  - CR-2 — add.py emitted prose (sync-guidelines block · CLI help text · status/guide hints) renamed;
    test edits bounded to STRING LITERALS that quote renamed prose (test_guidelines.py and peers),
    each in an isolated commit that enumerates its deltas — any logic or matcher change is out of bounds.
  - RENAME the surface per the §3 frozen map: both written forms (hyphen + space — the v17 both-forms
    clause), staged per-term commits, machine tokens untouched, mirrors propagated in-commit
    (bundle-parity + tree-parity + the installed `.add/` dogfood copies).
  - PROMOTE per protocol v2: flip `[mapped]`→`[enforced]` + add to enforced_banned + swap keep_list in
    the SAME commit that removes the term's LAST occurrence from the lint surface AND the extended
    surface (templates · docs · README — asserted by the new test, since the lint stops at 19 files).
  - BRIDGE in the glossary: appendix-c-glossary.md + GLOSSARY.md.tmpl carry every renamed term as
    `<new domain term> — <definition> (formerly "<slang>"; runs as <machine token> where applicable)`.
  - SWEEP the v17 enforced escapees from the newly covered surfaces: `first feeder` (TASK.md.tmpl:59),
    plus any surviving `rubber-stamp` / `blast radius` / `wall of` / `collapses to` in templates/docs/README.
  - KEEP gates green after every commit: wording_lint F1–F4 · semantic_inventory S1–S3 · bundle+tree
    parity · the whole pre-existing suite · `add.py check` · `add.py audit`; regenerate the CLAUDE.md/
    AGENTS.md guideline block via `add.py sync-guidelines` (never hand-edited) after CR-2.

Reject:
  - a reword that alters a RULE's meaning (drops/renames/relocates a unit · breaks an invariant ·
    introduces an exception) -> "semantics_changed"  (route back to SPECIFY, never a wording edit)
  - renaming a machine token (CLI verb · reject code · state key · file name · task slug) -> "machine_token_renamed"
  - replacing a Group-B term that is already domain-standard (dogfood · red/green · contract ·
    Given/When/Then · change request · gate outcomes · intake · context rot · READY/REVIEW-QUEUE) -> "keep_term_renamed"
  - a guard/test edit outside CR-2's bounded string-literal class, or not isolated -> "silent_guard_edit"
  - a term's last occurrence removed without the same-commit promotion swap, or flipped while either
    written form survives anywhere on lint + extended surface -> "idiom_unretired"
  - a canonical edit not mirrored to `_bundled/` + `.claude/` (+ `.add/` installed copies) in-commit -> "parity_drift"
  - a renamed term shipping without its glossary bridge entry -> "bridge_missing"
  - an edit outside the §3 CHANGE SCOPE (history under .add/tasks · .add/milestones · CHANGELOG.md ·
    state.json) -> "scope_creep_surface"

After:
  - The whole surface speaks domain-standard vocabulary: all 17 idioms `[enforced]`, their replacements
    F3-guarded in keep_list v2; the inventory v2 proves no rule changed meaning; add.py emits the new
    terms; every renamed concept carries a glossary bridge to its legacy name + machine token; the v17
    escapees are swept; mirrors and the dogfood install are byte-aligned; method semantics unchanged.

Assumptions — least-sure first:
  ⚠ TERM-CHOICE FIDELITY is the bundle's lead flag — least sure because the 17 replacement terms are my
    domain judgment calls (e.g. "scope level" for altitude, "specification bundle" for the front), and a
    wrong pick bakes a permanent name into GLOSSARY, keep_list, and every surface. If wrong: a rename of
    the rename later — the costliest class of change this method knows. Mitigated: the map IS the §3
    payload — your freeze approves each row individually; amend rows at the seam, not after.
  ⚠ THE THREE FROZEN-ARTIFACT CRs are the second flag — least sure because editing frozen guards is the
    cardinal method sin unless pre-declared, exact, ratified, isolated. CR-R/CR-I are exact deltas; CR-2
    is a bounded CLASS (string literals quoting renamed prose), weaker than v17's two-line CR-1. If wrong:
    a meaning-bearing test silently weakens under cover of the class. Mitigated: isolation + per-commit
    enumeration + the conservative human verify gate reads those diffs first.
  - [ ] container size — this is bigger than any single v17 slice; if build stalls, the pre-drawn split
        (map lands in this task · rename remainder forks to a follow-on by change-request) is raised
        explicitly, never executed silently.
  - [ ] the extended-surface fence is TEST-based, weaker than the lint: wording_lint stops at 19 files;
        templates/book/README ride test_ubiquitous_language — a future drift there is caught by the test
        only. Accepted; widening the lint surface is a separate rubric rule change, out of scope.
  - [ ] identity loss — the book's voice flattens where slang carried rhetoric; accepted at intake
        (the human chose domain terms over method identity).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
# --- one per Must ---
Scenario: the rubric revs to v2 and stays internally consistent
  Given the 17-row §3 map ratified at the freeze
  When CR-R lands (11 keep_list terms moved to idiom_map [mapped] · 6 new [mapped] rows · match rule untouched)
  Then wording_lint F4 (self-consistency) and F1–F3 are green with zero surface edits yet
  And every machine token and Group-B term still sits in keep_list

Scenario: the inventory revs to v2 with identical meaning
  Given the `never-self-fold` invariant anchored on the old prose
  When CR-I re-anchors it (+ coverage key + negative_keep_list twin) to the renamed prose
  Then semantic_inventory exits 0 and the human-confirm boundary on foundation writes still has ≥1 covering invariant
  And every other unit, anchor, and token is byte-unchanged

Scenario: add.py emits domain terms after CR-2
  Given sync-guidelines and CLI help currently emit "one-approval front" / "lock-down"
  When CR-2 renames the prose strings and `add.py sync-guidelines` regenerates the block
  Then the emitted CLAUDE.md/AGENTS.md block and --help text carry no banned form
  And CLI verbs, exit codes, and state keys behave byte-identically

Scenario: a term is renamed surface-wide in one staged commit
  Given a §3 map row (e.g. survivor → living documentation)
  When its commit lands
  Then both written forms are gone from the lint surface AND templates/docs/README
  And the same commit flips [mapped]→[enforced], adds the term to enforced_banned, and swaps keep_list

Scenario: every renamed concept keeps a bridge to its past
  Given a reader (or agent) who knows only the old term or the machine token
  When they open appendix-c-glossary.md or GLOSSARY.md.tmpl
  Then each new term carries its definition, its former name, and its machine token where one exists
  And the bridge lives outside the lint surface, so F1 never fires on the legacy mention

Scenario: the v17 escapees are swept from the newly covered surfaces
  Given `first feeder` survives in TASK.md.tmpl:59 because templates were never lint surface
  When the sweep commit lands
  Then no v17-enforced idiom (first feeder · rubber-stamp · blast radius · wall of · collapses to)
       remains anywhere on the extended surface, either written form

Scenario: gates green after every commit, suite green at close
  Given the staged build of CR-R · CR-I · per-term renames · CR-2 · bridge · sweep
  When any single commit is checked out
  Then wording_lint 0 · semantic_inventory 0 · bundle+tree parity green · pre-existing suite green ·
       add.py check + audit green; test_ubiquitous_language is fully green at task close

# --- one per Reject ---
Scenario: a meaning-changing reword is refused
  Given a rename that drops an anchor, relocates a unit, or adds an "unless"
  When semantic_inventory or human review runs
  Then it is rejected "semantics_changed" and routed back to SPECIFY as a change-request
  And no gate or test is weakened to absorb it

Scenario: renaming a machine token is refused
  Given a build edit that renames `add.py lock`, a reject code, a state key, or fold.md's filename
  When test_machine_tokens_unchanged or review runs
  Then it is rejected "machine_token_renamed" and the token is restored

Scenario: replacing an already-domain term is refused
  Given a rewrite that touches dogfood · red/green · contract · Given/When/Then · change request · gate outcomes
  When wording_lint F3 runs (each still keep_list-guarded)
  Then F3 fails — reported as "keep_term_renamed"

Scenario: a test edit outside the CR-2 class is refused
  Given a build commit editing a test's logic, matcher, or an unrelated string
  When the isolated-commit review runs at verify
  Then it is rejected "silent_guard_edit" — indistinguishable-from-cheating class, HARD-STOP candidate

Scenario: an un-promoted or half-promoted rename is caught
  Given a term's last occurrence removed without the same-commit swap, or flipped with a space-form alive
  When test_ubiquitous_language + wording_lint run
  Then the gap is reported "idiom_unretired" and the commit is amended before the next term starts

Scenario: mirror drift is caught
  Given a canonical edit not propagated to _bundled/ · .claude/ · the installed .add/ copies
  When test_bundle_parity / test_tree_parity / the install-copy check run
  Then the commit fails "parity_drift"

Scenario: a missing bridge is caught
  Given a renamed term with no glossary entry
  When test_glossary_bridge_complete runs
  Then it fails "bridge_missing"

Scenario: history stays history
  Given the rename sweeping the repo
  When any edit touches .add/tasks/** · .add/milestones/** · CHANGELOG.md · state.json
  Then it is rejected "scope_creep_surface" — archived records keep the vocabulary of their era
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
THE MAP (the frozen payload — approving the freeze approves each row; the build may not invent a term)
  #   retire (ban forms: hyphen+space twins)              -> replacement (enters keep_list)       bridge
  1   one-approval front · the front · whole front        -> specification bundle (single-approval,
                                                             approved once at the contract freeze)  —
  2   the seam · decision seam · freeze seam · human seam
      · at the seam · a seam                              -> decision point                         —
  3   the fold · fold ritual · self-fold · fold(s) the
      delta(s) · folded into                              -> retrospective consolidation
                                                             (verb: consolidate; "self-fold" ->
                                                             "self-approve a consolidation")        deltas.md filename + `add.py deltas` stay
  4   competency delta(s)                                 -> lesson learned (tagged by competency)  deltas.md filename + reject codes stay
  5   least-sure · least sure                             -> lowest-confidence (ranked, lowest-
                                                             confidence first)                      —
  6   touch-boundary · touch boundary                     -> change scope                           —
  7   survivor layer · survivor(s)                        -> living documentation                   —
  8   intake/milestone/setup/foundation altitude ·
      setup-altitude · every altitude                     -> scope level (intake level · milestone
                                                             level · setup level)                   —
  9   lock-down · lockdown · lock down (noun)             -> baseline approval                      `add.py lock` verb stays
  10  blind-spot(s) · blind spot(s)                       -> non-functional review (the checks) /
                                                             non-functional risks (the spots)       —
  11  red safety net · safety net                         -> failing-first suite (TDD red)          "red"/"green" stay (Group B)
  12  evidence auto-gate                                  -> automated quality gate (evidence-
                                                             based); descriptive "auto-gated" stays —
  13  autonomy dial · the dial · lower the dial           -> autonomy level                         `autonomy:` state key stays
  14  trust layer · the trust layer                       -> method rationale                       —
  15  forward spine · the spine                           -> primary flow                           —
  16  on-ramp · onramp                                    -> onboarding                             task slugs/test filenames stay
  17  state surface · story surface                       -> working state / audit trail            state.json name stays

CR-R  WORDING_RUBRIC.md → v2 (exact delta; the ONLY rubric edits this task may make)
  - idiom_map: +17 rows above, each `[mapped]` at landing, flipped `[enforced]` per promotion protocol v2.
  - keep_list: REMOVE the 11 rows being renamed (one-approval front · seam · fold · competency delta ·
    least-sure · touch-boundary · trust layer · evidence auto-gate · autonomy dial · survivor · intake
    altitude); ADD each replacement term in the SAME commit its rename lands (atomic F3 swap) —
    EXCEPT replacements that never appear on the 19-file lint surface (primary flow · working state /
    audit trail): F3 would be falsely red for them, so they are guarded by test_ubiquitous_language
    only. dogfood ·
    READY-QUEUE · REVIEW-QUEUE · change request · gate outcomes · DDD/SDD/UDD/TDD/ADD/AIDD · the XML tag
    names · the <prompt>-skeleton fields are UNTOUCHED.
  - negative_keep_list: reword the `never self-fold` row to `never self-approve a consolidation`,
    SAME `# why:`; the other four negatives byte-unchanged.
  - match rule · emphasis_tokens · scope_qualifier_rule: UNCHANGED (phrase-bound stands, per intake).
  - header: `FROZEN @ v2 · 2026-06-07 · CR: ubiquitous-language` (version note, not a silent overwrite).

CR-I  SEMANTIC_INVENTORY.md → v2 (exact delta)
  - invariants: `never-self-fold @ fold.md | anchors: self-approve, never | neg:` (id and file
    unchanged; anchors follow the renamed prose; meaning identical — the human-confirm boundary).
  - coverage: `self-fold -> never-self-fold` becomes `self-approve -> never-self-fold`.
  - token_layer + all other invariants/units: byte-unchanged. Header versioned like CR-R.

CR-2  add.py prose + bounded test-string deltas
  - add.py: rename SLANG in emitted prose ONLY — the sync-guidelines block, --help text, status/guide/
    report hint strings. CLI verbs, flags, exit codes, state keys, JSON shapes byte-unchanged.
  - tests: ONLY string literals that quote renamed prose may change (test_guidelines.py and peers,
    incl. header literals like "## The evidence auto-gate" in test_rewrite_core.py if that header is
    renamed). Each CR-2 commit is ISOLATED and enumerates its string deltas in the commit message.
    Any logic/matcher/threshold edit -> "silent_guard_edit".

CHANGE SCOPE  (the build may edit ONLY these; everything else is out of bounds)
  IN : add-method/skill/add/** · add-method/tooling/templates/** · add-method/docs/** ·
       add-method/diagrams/*.md · add-method/README.md · add-method/GETTING-STARTED.md ·
       add-method/tooling/add.py (prose strings per CR-2) · WORDING_RUBRIC.md (CR-R) ·
       SEMANTIC_INVENTORY.md (CR-I) · tooling tests (CR-2 class) · NEW test_ubiquitous_language.py ·
       MIRRORS in-commit: src/add_method/_bundled/** (bundle-parity) · .claude/skills/add/**
       (tree-parity) · installed dogfood copies .add/tooling/{add.py,templates/} + .add/docs/ ·
       CLAUDE.md/AGENTS.md guideline block via `add.py sync-guidelines` only.
  OUT: .add/tasks/** · .add/milestones/** · CHANGELOG.md · state.json · *.png diagrams · task slugs ·
       test/file names · this TASK.md's frozen sections.

PROMOTION PROTOCOL v2  (extends the v17 surface-wide both-forms rule to the extended surface)
  flip `[mapped]`→`[enforced]` + add to enforced_banned + swap keep_list in the SAME commit that removes
  the term's LAST occurrence — BOTH written forms — from the lint surface (19 files, F1 enforces) AND the
  extended surface (templates · docs · diagrams/*.md · README · GETTING-STARTED — test_ubiquitous_language
  enforces, since the lint stops at 19). Glossary bridge mentions of a legacy term live in
  appendix-c/GLOSSARY.md.tmpl marked `(formerly "…")` and are EXEMPT in the test's matcher — the lint
  never sees them (off-surface).

COMMIT STAGING  (by risk; one gate failure localizes)
  0  CR-R + CR-I land first, [mapped]-only (zero surface edits — lint provably green before any rename)
  1..n  per-term commits, lowest-risk first (on-ramp · spine · safety net · …), riskiest last
        (fold · seam · front — they live inside safety-rule prose; the inventory guards the windows);
        each commit = rename surface-wide (both forms) + promotion swap + glossary bridge row + mirrors
  n+1  CR-2 isolated (add.py prose + enumerated test strings + sync-guidelines regen)
  n+2  escapee sweep + final greenstate (suite · check · audit · parity · both gates · new test fully green)

reject_codes: semantics_changed · machine_token_renamed · keep_term_renamed · silent_guard_edit ·
              idiom_unretired · parity_drift · bridge_missing · scope_creep_surface
```

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-07   <!-- the one approval over the §1–§4 bundle. Changing a frozen contract = change request back to SPECIFY. -->

> **Bundle least-sure flags (read at the freeze, 2026-06-07):**
> ⚠ [contract] TERM-CHOICE FIDELITY — the 17 replacements are AI domain judgment calls; approving froze
> each row; a wrong pick costs a rename-of-the-rename. Approved as listed, no rows amended.
> ⚠ [contract] THE THREE FROZEN-ARTIFACT CRs — CR-R/CR-I exact deltas; CR-2 a bounded string-literal
> CLASS (weaker than v17's CR-1); isolation + per-commit enumeration + the conservative human verify
> read are the protection.
> [test] the extended-surface fence is TEST-based (lint stops at 19 files) and the `formerly "…"` bridge
> exemption is honor-bound — the human verify read is the backstop.
> [scenario] bare-token regexes (the front · dial · spine) may catch legitimate English in book prose —
> resolved by rewording at build; the lint itself stays phrase-bound (intake decision).

> **Build-time ratifications (dated addenda — the frozen text above is unedited):**
> **CR-3 (ratified by Tin Dang, 2026-06-07, at the build decision point):** the frozen closed-set guard
> `test_idiom_map_fully_enforced` (clarity-greenstate) pins enforced idioms to exactly the 5 v17 names —
> un-pre-declared by §3 and discovered at term 1. Ratified shape: `V17_IDIOMS | UBIQUITOUS_IDIOMS`, where
> UBIQUITOUS_IDIOMS grows ONLY with this task's §3 map, one enumerated addition per landed term commit;
> identity semantics, no-[mapped]-residue, and the never-shrinking v17 core are preserved. Landed as an
> isolated commit with UBIQUITOUS empty (provable no-op), then grown per term.
> **Execution calls (v17 rewrite-core delta class — derived from the binding suite-green-per-commit
> invariant; to ratify at verify):** (1) idiom rows enter the rubric directly as `[enforced]` in their
> term's commit, never `[mapped]` at rest — the standing fence forbids residue; (2) CR-2-class test
> string-literal updates ride the SAME commit as the prose they quote (an isolated-but-red commit pair
> would break the invariant); enumerated per commit message; (3) the `enforced_banned` SECTION stays
> `(none yet)` — the `[enforced]` row IS the promotion (the parser unions both; duplicating double-counts).
> (4) **(term 14)** the engine's embedded `_FALLBACK_TASK` §1 scaffold is template-coupled —
> `test_cospecify_scaffold` pins tmpl + fallback + a real `new-task` run as ONE shape — so its two
> scaffold lines ride the term-14 commit instead of CR-2's isolated commit (suite-green-per-commit
> binds over CR-2's staging prose; calls 1–2 precedent). Consequence: the five `ENGINE_MD5` tripwires
> (getting-started-spine · installer-handoff · release-1-1-0 · review-checklist · skill-onramp) fired
> as designed and are re-stamped to the new digest in the SAME commit — a disclosed re-pin, not a
> weakening (the change is contract-ratified CR-2 class; an accidental engine edit still fails). The
> CR-2 commit will re-stamp them once more.
> (5) **(term 15)** the §4 seam ban gains a surgical negative lookahead — `\bseams?\b(?!-audit)` —
> because `seam-audit` is a Group C machine token (the CI job/workflow name; test_audit_ci pins the
> job key + canonical command, test_release_1_1_0 anchors it in the release record). Alignment to
> the contract's machine-layer rule (MACHINE_HEADINGS precedent, term 13), not a weakening: every
> prose form of seam stays banned; only the literal machine compound is exempt. The add.py machine
> names (`--json` owner enum `seam` · decide-digest key `seam`) keep their names per the contract;
> their AddPyProseTest handling lands with CR-2. Glossary bridges name all three machine survivors.
> (6) **(term 16)** the §4 suite's scan() gains machine-layer awareness: fenced code blocks (the
> deltas.md status-lifecycle diagram, yml workflows, the delta grammar) and inline code spans
> (`folded` · `fold.md` · `seam` · `add.py fold`) are exempt from the prose bans — they ARE the
> Group C machine layer the contract says keeps its names. Verified non-hiding: the
> one-approval-front expected-hit count is unchanged (24) before/after. The human verify read
> stays the backstop against slang smuggled into a span/fence (same honor-bound class as the
> `formerly "…"` bridge exemption disclosed at the freeze).
> (7) **(CR-2)** AddPyProseTest gains the same machine-layer rule for add.py string literals:
> exact Group C constants (`"seam"` — the --json owner enum + decide key; `"folded"` — the delta
> status) and machine-token fragments inside longer strings (the `### Competency deltas` block
> locator + docstring quotes of it · the `(human|seam|ai)` enum listing · the
> `(open|folded|rejected)` grammar in _DELTA_RE · "folded/rejected" status references) are exempt
> from the prose bans — every other add.py literal (help · hints · docstrings · the
> sync-guidelines block · the decide digest's emitted text) was renamed. The five ENGINE_MD5
> tripwires re-stamped once more (per call 4's plan); CLAUDE.md/AGENTS.md regenerated via
> `add.py sync-guidelines`.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 17 map rows (parametrized per term, both written forms) + the 5 v17
  escapee idioms + every bridge entry. Reject scenarios ride EXISTING gates where one stands
  (wording_lint F1–F4 · semantic_inventory S1–S3 · bundle/tree parity · check/audit); the genuine
  RED lives in the new suite below.

NEW red suite — `add-method/tooling/test_ubiquitous_language.py` (RED now, permanent guards after):
  - test_rubric_v2_carries_the_map      : all 17 idiom rows present; the 11 renamed terms absent from
                                          keep_list; each replacement present in keep_list once its
                                          rename lands (parametrized)            — RED (rubric is v1)
  - test_slang_absent_extended_surface  : per-term word-boundary regex (both forms) finds ZERO hits
                                          across skill/add + templates + docs + diagrams/*.md +
                                          README + GETTING-STARTED; glossary `(formerly "…")` bridge
                                          lines exempt                            — RED (slang everywhere)
  - test_enforced_escapees_swept        : first feeder · rubber-stamp · blast radius · wall of ·
                                          collapses to — zero hits on the extended surface
                                                                                  — RED (TASK.md.tmpl:59)
  - test_glossary_bridge_complete       : appendix-c + GLOSSARY.md.tmpl carry every renamed term with
                                          definition + former name (+ machine token where the map says) — RED
  - test_sync_guidelines_domain_clean   : the block add.py emits contains no banned form — RED
  - test_machine_tokens_unchanged       : CLI verbs · reject codes · state keys · skill file names
                                          unchanged — GREEN-now standing regression guard

Scenario → covering test:
  - rubric v2 consistent                -> test_rubric_v2_carries_the_map + wording_lint F4 (existing)
  - inventory v2 identical meaning      -> semantic_inventory S1–S3 (existing) + human review of CR-I diff
  - add.py emits domain terms           -> test_sync_guidelines_domain_clean
  - per-term rename + promotion swap    -> test_slang_absent_extended_surface + wording_lint F1/F3
  - bridge complete                     -> test_glossary_bridge_complete
  - escapees swept                      -> test_enforced_escapees_swept
  - gates green per commit              -> existing gates + parity (process: checked at every commit)
  - semantics_changed / silent_guard_edit / parity_drift / scope_creep_surface
                                        -> semantic_inventory · isolated-commit review at verify ·
                                           bundle/tree parity · git diff scope check at verify
  - machine_token_renamed / keep_term_renamed / idiom_unretired / bridge_missing
                                        -> test_machine_tokens_unchanged · wording_lint F3 ·
                                           test_slang_absent_extended_surface+F1 · test_glossary_bridge_complete

Tests live in: `test_ubiquitous_language.py` `add-method/tooling/` (engine/dev guard beside
  wording_lint.py — NOT the 3-mirror skill surface, so no parity copy). MUST run red before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the riskiest renames (fold · seam · front) live INSIDE safety-rule
  prose — the never-self-fold window, run.md's security/auto-gate constraints, report-template's
  decision rules. A gate RED there is a meaning-drift signal: fix the prose, NEVER the gate. Run both
  gates + parity after EVERY commit; stage riskiest terms last per §3.
Code lives in: the §3 CHANGE SCOPE surface files + their mirrors (no `./src/`); CR-2 isolated.
Constraints: do NOT weaken a test or edit the frozen contract; the ONLY guard edits are the three
  pre-declared CRs (CR-R · CR-I · CR-2's bounded string class), each isolated; mirror every canonical
  edit in-commit; machine tokens untouched; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 533 OK · wording_lint 0 · semantic_inventory 0 · check 191/0 · audit clean
- [x] coverage did not decrease — the feature suite is now a permanent 17-term + escapee regression guard
- [x] no test or contract was altered during build — except the pre-declared CR class (CR-R · CR-I ·
      CR-2 string literals) and execution calls 4–7, each isolated, enumerated, and ratified at this gate
- [x] concurrency / timing N/A (prose rename; no runtime paths changed beyond emitted strings)
- [x] no exposed secrets, injection openings, or unexpected dependencies — machine/CI tokens
      byte-identical (seam-audit job · canonical audit command · owner enum · delta statuses)
- [x] layering & dependencies follow CONVENTIONS.md — mirrors propagated in-commit (bundle ⇄ tree ⇄
      .add dogfood ⇄ root book), suite-asserted
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-07: ratified execution calls 4–7 +
      the riding-literal class; PNG residue (diagrams/add-flow.png old labels) disclosed → follow-up CR

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-07   (conservative gate — human-led; security line reviewed, no finding)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the standing fences ARE the monitors — wording_lint F1 (a
  retired idiom reappears), test_ubiquitous_language (slang/escapee/bridge regression on the
  extended surface), test_rewrite_guides enforced-set identity. Plus: do new readers/agents use the
  domain terms unprompted (the rename's real success signal)?
Spec delta for the next loop: diagrams/add-flow.png still renders the legacy labels (*.png was OUT
  of the frozen CHANGE SCOPE) — a small follow-up change-request re-renders it from the renamed
  diagram sources. CHANGELOG/history keep legacy terms by design (audit trail, bridged via glossary).

### Competency deltas
- [ADD · folded] machine/prose boundary was discovered five separate times mid-build (### heading ·
  ⚠ glyph · seam-audit job · folded status · owner enum) costing execution calls 4–7; a contract
  that enumerates the machine-token REGISTRY up front (or `add.py` emitting one) would pre-draw the
  line once (evidence: TASK.md §3 addenda, execution calls 4–7 this build)
- [TDD · folded] five duplicated ENGINE_MD5 tripwires make every intentional engine edit a 5-file
  re-stamp; one shared pin constant keeps the tripwire with 1/5 the ceded surface (evidence: two
  re-stamp rounds this build, term 14 + CR-2)
- [SDD · folded] the both-forms (hyphen+space) ban clause missed the ALL-hyphen compound
  ("one-approval-front" at 0-setup:85, invisible to `one[- ]approval front`); the raw-grep recipe
  caught it — fence specs should name the fully-hyphenated form too (evidence: term-17 commit 63534e1)
