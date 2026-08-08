# TASK: Freeze the wording rubric + ship wording-lint

slug: wording-rubric · created: 2026-06-06 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the wording RUBRIC (one frozen doc) + `wording-lint` (a deterministic regression fence)
Framings weighed: fence + judgment-guide (chosen) · pure-style-linter (rejected — a count/density
  gate false-positives on a GOOD rewrite, the same failure mode that disqualified v17's behavioral
  eval as a gate) · human-rubric-no-tool (rejected — no CI guard against idiom/emphasis regression)

Must:
  - Freeze ONE rubric doc holding five parts + the reject codes: (a) the idiom→direct MAP,
    (b) the KEEP-LIST of load-bearing terms, (c) the NEGATIVE-KEEP-LIST (negatives that stay,
    each with a `# why:`), (d) the emphasis policy, (e) the scope-qualifier rule.
  - Ship `wording-lint`: a checker that reads its lists FROM the frozen rubric (single source, no
    hardcoded duplicate) and checks the surface (`skill/add/` 18 files + `docs/appendix-b-prompts.md`).
  - Enforce ONLY collision-free FENCES — a check that can fail solely on a literal regression, never
    on a good rewrite: (F1) no ENFORCED banned phrase present · (F2) no banned emphasis token
    (`CRITICAL`, `NON-NEGOTIABLE`) · (F3) every keep-list term still present on the surface ·
    (F4, freeze-time) no banned phrase is a substring of any keep-list term and no direct-form
    reintroduces another banned phrase.
  - Seed the ENFORCED banned-list with ONLY entries already ABSENT from the surface, so the lint is
    GREEN at this task's close; the idiom→direct MAP carries the full retirement plan as the
    rewriters' judgment guide (mapped-but-not-yet-enforced).
  - Define the PROMOTION protocol: a rewrite task that retires a mapped idiom moves it MAP→ENFORCED
    in the SAME commit (re-running F4) — the lint stays green at every task close; the set only grows.
  - Match banned phrases word-boundary + phrase-level — case-insensitive for idioms (F1) and
    case-SENSITIVE for emphasis tokens (F2, the ALL-CAPS shout) — never a single word, never a
    substring (the 42×"fold"/48×"thin" substring trap).   <!-- v1.1 change-request, human-ratified at the verify gate -->
    <!-- WHY F2 is case-sensitive: a case-insensitive emphasis fence matches the legitimate header
         `## Non-negotiable rules` (SKILL.md) → §4 test_emphasis_token_fence goes red on GOOD content;
         the test forces the split (never weaken a test). -->

  - Design the lint for failure: a missing/malformed rubric or an unreadable surface file fails LOUD
    (exit 2, named error) — never a silent green pass.
  - Name the JUDGMENT axes as explicitly NON-lintable (the lint does not enforce them; the
    semantic-inventory test + human review do): positivize-a-negative-where-a-clean-positive-exists ·
    the scope-qualifier rule · honoring the negative-keep-list.

Reject:
  - a proposed lint check that is a count / density / threshold (CAPS-count · bold-density ·
    negative-count) -> "metric_gate"   (refused by design: it false-positives on good rewrites)
  - an ENFORCED banned entry that is a single word or a substring of a keep-list term -> "ambiguous_ban"
  - an ENFORCED banned phrase present on the surface -> "banned_idiom_present"
  - a banned emphasis token (`CRITICAL` / `NON-NEGOTIABLE`) present on the surface -> "banned_emphasis_token"
  - a keep-list term absent from the whole surface (a global rename/loss) -> "keep_term_missing"
  - (freeze-time) a direct-form (replacement) that reintroduces a banned phrase -> "rubric_self_collision"
    <!-- v1.1 change-request, human-ratified: substring-of-a-keep-term is the line-above's "ambiguous_ban",
         not this code (resolves the §1 line-49-vs-here contradiction; matches §4 test_ambiguous_ban_refused). -->
  - a negative on the NEGATIVE-KEEP-LIST reworded into a positive-only form -> "protected_negative_removed"
    (review/judgment-caught, rubric-prohibited — not a lint fence)

After:
  - The rubric is FROZEN (one doc — the single source every v17 rewrite task reads). `wording-lint`
    runs GREEN over the current surface (F2 + F3 + F4 + the already-absent F1 seed). The five rewrite
    tasks inherit a deterministic regression fence that grows monotonically green-to-green, plus a
    documented judgment guide the lint cannot enforce but review + semantic-inventory can.

Assumptions — least-sure first:
  ⚠ The idiom→direct MAP is seeded from a 19-file scan, not exhaustive — rewrite tasks WILL surface
    more decorative idioms — least sure because "decorative vs load-bearing" is a judgment I'm
    front-loading; if wrong: a term I retire is actually load-bearing and breaks a cross-ref/test —
    mitigated by F4 + keep-list-first review, but the SEED (`rubber-stamp` · `wall of` · `collapses to`
    · `FIRST FEEDER`/`feeder` · `blast radius`) wants your eyes.
  ⚠ Lint-is-a-fence-not-a-metric is the RIGHT measurement contract — least sure because it
    deliberately CANNOT prove "the rewrite reads better", only "no idiom/term regressed"; if wrong:
    you wanted the lint to enforce positivity/scope too — it provably can't without false-positiving,
    so those stay human-judgment + the semantic-inventory gate.
  - [ ] The surface is exactly `skill/add/` (18 files) + `docs/appendix-b-prompts.md`; `templates/*.tmpl`
        are fill-in forms with nothing executable to reword (matches v16's assessment).
  - [ ] The `Never:` `<prompt>`-skeleton field STAYS (negative-keep-list) — a designed prohibition slot
        AND test-enforced (`test_pilot_fully_converted` asserts `"Never:"` in the pilot) — confirmed by
        reading the test; positivizing it would trip the v16-frozen guard.
  - [ ] Reject-code NAMES are owned by the semantic-inventory (meaning-units), not by wording-lint
        (lexical) — the clean lexical/meaning seam, so neither double-covers nor leaves a gap.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the rubric is the single source the lint reads
  Given the five rubric parts + reject codes are frozen in WORDING_RUBRIC.md
  When wording-lint runs
  Then it loads its banned/keep lists from that doc (no hardcoded duplicate)
  And it prints the rubric path it read

Scenario: the lint catches a re-introduced idiom (machinery, via fixture)
  Given a fixture text containing the ENFORCED banned phrase "rubber-stamp"
  When wording-lint runs on the fixture
  Then it reports "banned_idiom_present" with the file + the phrase
  And it exits non-zero

Scenario: the lint does not false-positive on a substring or a clean rewrite
  Given a fixture with "unfolded", "within", and the rewrite "approve without reading"
  When wording-lint runs on the fixture
  Then it reports zero findings
  And it exits zero                       # a good rewrite is never blocked

Scenario: the emphasis-token fence is green now and would catch a regression
  Given the live surface has no "CRITICAL" / "NON-NEGOTIABLE"
  When wording-lint runs
  Then it reports zero "banned_emphasis_token"
  And injecting "CRITICAL:" into any surface file would report it

Scenario: the keep-list-presence fence guards against a rename
  Given the live surface
  When wording-lint runs
  Then every keep-list term resolves to at least one occurrence
  And a global rename of "one-approval front" would report "keep_term_missing"

Scenario: a self-collision in the rubric is refused at freeze
  Given the frozen banned-list and keep-list
  When the freeze-time self-collision check runs
  Then no banned phrase is a substring of any keep-list term
  And no direct-form reintroduces a banned phrase   # else "rubric_self_collision", freeze refused

Scenario: a metric check is refused by design
  Given a proposed lint rule "fail if a file has more than 20 bold spans"
  When it is checked against the rubric contract
  Then it is rejected as "metric_gate"
  And the rubric records WHY (it false-positives on a good rewrite)

Scenario: an ambiguous ban is refused at freeze
  Given a proposed ENFORCED entry "fold" (a single word, substring of "unfolded" and a keep term)
  When the freeze-time check runs
  Then it is rejected as "ambiguous_ban"
  And the enforced banned-list stays phrase-level only

Scenario: the lint fails loud on a broken rubric (design-for-failure)
  Given WORDING_RUBRIC.md is missing or malformed
  When wording-lint runs
  Then it exits 2 with a named error
  And it does NOT report a false green   # no silent pass

Scenario: a protected negative may not be positivized
  Given "never auto-pass a security finding" on the NEGATIVE-KEEP-LIST
  When a rewrite converts it to a positive-only form
  Then review flags "protected_negative_removed"
  And the original negative + its "# why:" remains

Scenario: the enforced banned-list is green over the live surface at freeze
  Given the enforced banned-list seeded only with already-absent entries
  When wording-lint runs over the live surface
  Then it reports zero "banned_idiom_present"
  And the still-present mapped idioms remain in the MAP, not yet enforced
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
RUBRIC  add-method/tooling/WORDING_RUBRIC.md           # single source; engine/dev guard, NOT skill surface
  idiom_map[]        : { idiom, direct, status: mapped | enforced }
                       seed (status=mapped, still on surface): rubber-stamp -> "approve without reading" ·
                       "wall of" -> "flat list of" · "collapses to" -> "shortens to" ·
                       "FIRST FEEDER"/"feeder" -> "first input" · "blast radius" -> "scope of impact"
                       seed (status=enforced, already absent): —   (none yet; emphasis tokens live in F2)
  keep_list[]        : load-bearing terms — F3 present-on-surface fence. Includes: one-approval front ·
                       the seam · fold · competency delta · least-sure flag · touch-boundary ·
                       the trust layer · evidence auto-gate · the autonomy dial · survivor[ layer] ·
                       dogfood · intake altitude · READY-QUEUE · REVIEW-QUEUE · change request ·
                       HARD-STOP · RISK-ACCEPTED · PASS · FROZEN · DDD · SDD · UDD · TDD · ADD · AIDD ·
                       the v16 XML tags (<prompt> <exit_gate> <constraints> <reject_codes> <output_format>) ·
                       the <prompt>-skeleton labels (Role: Read first: Objective: Steps: Never:)
  negative_keep_list[]: { negative, why } — NOT auto-removed; positivizing one -> protected_negative_removed.
                       Seed: the `Never:` <prompt>-skeleton field (designed slot + test_pilot_fully_converted) ·
                       "never weaken a test / edit a frozen contract" (method-integrity boundary) ·
                       "a security finding is always HARD-STOP" / "never auto-pass a security finding" (safety) ·
                       "never self-fold" (human-confirm boundary on foundation writes) · hard floors/ceilings
  emphasis_policy    : banned tokens = { CRITICAL, NON-NEGOTIABLE } (F2) ; elsewhere plain imperative.
                       Strong emphasis reserved for true hard-stops. NOT a CAPS-count or bold-density (metric_gate).
  scope_qualifier_rule: JUDGMENT (non-lintable) — a phase-wide rule states the scope it governs.
  reject_codes       : banned_idiom_present · banned_emphasis_token · keep_term_missing ·
                       rubric_self_collision · ambiguous_ban · metric_gate · protected_negative_removed

LINT  python3 add-method/tooling/wording_lint.py [--rubric <path>] [--surface <glob>...]
  reads  : WORDING_RUBRIC.md (ENFORCED entries + keep_list + emphasis tokens) + the surface files
  checks : FENCES only — F1 enforced-banned-absent · F2 emphasis-token-absent ·
           F3 keep-term-present · F4 self-collision (freeze-time, on the rubric itself)
  match  : word-boundary + phrase-level ; case-insensitive idioms (F1), case-SENSITIVE emphasis (F2) ; never single-word, never substring
  exits  : 0 = no findings · 1 = findings (prints file · code · phrase) · 2 = broken rubric /
           unreadable surface (LOUD, named error — never a false green)
  refuses: any count / density / threshold check -> metric_gate (would false-positive on a good rewrite)
  promotion: retiring a mapped idiom = flip status mapped->enforced in the same commit (re-runs F4); monotonic
Schema  : no DB — reads markdown. Surface = canonical add-method/skill/add/ (the _bundled & .claude
          mirrors are byte-identical via test_bundle_parity/test_tree_parity, so canonical suffices).
          WORDING_RUBRIC.md + wording_lint.py are tooling/ guards (like test_xml_convention.py) — NOT mirrored.
```

Status: FROZEN @ v1 — approved by Tin Dang, 2026-06-06 (one-approval front; "Approve — freeze @ v1") · prose-corrected @ v1.1 (human-ratified at the verify gate)
<!-- approved 2026-06-06 (one-approval front; human chose "Approve — freeze @ v1"). Changing a frozen contract = change request back to SPECIFY.
     v1.1 (2026-06-06, ratified at the verify-gate PASS): two one-line prose corrections that align the frozen bundle with the already-green §4 tests — NO behavior change, NO test weakened:
       CR-1  match rule split: case-insensitive idioms (F1) / case-SENSITIVE emphasis (F2) — forced by test_emphasis_token_fence (see §6 Disclosed Refinement #1).
       CR-2  rubric_self_collision = direct-form reintroduction only; substring-of-keep is ambiguous_ban — resolves the §1 line-49-vs-53/54 contradiction (see §6 Disclosed Refinement #2). -->

> **Bundle least-sure flag (read this at the freeze):** of everything frozen here, two are most likely
> wrong — **[spec]** the idiom MAP seed is non-exhaustive and "decorative vs load-bearing" is my judgment
> (cost: I retire a load-bearing term → broken cross-ref/test; mitigated by F4 + keep-list-first review),
> and **[contract]** lint-is-a-fence-not-a-metric (cost: if you wanted the lint to also enforce
> positivity/scope, it provably can't without false-positiving — those stay judgment + semantic-inventory).
> Everything else (reject codes · fence set · exit codes · promotion protocol) I'm confident on.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of fence branches (small, deterministic surface — every fence + every reject code)
Plan (one test per scenario; assert behavior, not internals):
  - test_lint_loads_from_rubric_single_source: lint reads banned/keep FROM WORDING_RUBRIC.md (no
    hardcoded dup) and prints the path / asserts the loaded set matches the doc.
  - test_lint_flags_enforced_idiom_fixture: fixture w/ an enforced banned phrase -> finding
    "banned_idiom_present" (file+phrase), exit 1.
  - test_lint_no_falsepositive_substring_and_rewrite: fixture w/ "unfolded"/"within"/"approve without
    reading" -> zero findings, exit 0.   (the good-rewrite-never-blocked guard)
  - test_emphasis_token_fence: live surface has no CRITICAL/NON-NEGOTIABLE (green now); an injected
    "CRITICAL:" fixture -> "banned_emphasis_token".
  - test_keep_term_presence: every keep-list term resolves on the live surface (green now); a fixture
    missing one -> "keep_term_missing".
  - test_self_collision_none_on_frozen_rubric: no banned phrase ⊂ any keep term; no direct-form
    reintroduces a banned phrase. (F4 over the REAL rubric)
  - test_ambiguous_ban_refused: a single-word / substring-of-keep enforced entry -> "ambiguous_ban".
  - test_metric_check_refused: lint exposes its check-kinds; assert all are 'fence', none 'metric'
    (encodes metric_gate as a design refusal).
  - test_lint_fails_loud_on_broken_rubric: missing/malformed rubric -> exit 2 + named error, NOT a
    false green. (design-for-failure)
  - test_enforced_banned_green_over_live_surface: the already-absent enforced seed -> zero
    "banned_idiom_present" over the live surface. (this task's green floor; the FULL-map green is
    owned by clarity-greenstate, not here)

Tests live in: `add-method/tooling/test_wording_lint.py` (beside the lint, run by the method's `unittest` suite — same home as `test_xml_convention.py`) · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the lint may fail ONLY on a literal regression — every fence is
collision-free and green at freeze. Design-for-failure: a missing/malformed rubric or unreadable
surface exits 2 (loud), never a silent green.
Code lives in: `add-method/tooling/wording_lint.py` + `add-method/tooling/WORDING_RUBRIC.md`
  (engine/dev guards beside `test_xml_convention.py` — NOT the 3-mirror skill surface, so no parity copy).
Constraints: stdlib only (argparse/re/dataclasses/pathlib) — no new dependency; the lint reads its
  lists FROM the rubric (single source); §3 contract honored.

Built:
- `WORDING_RUBRIC.md` — FROZEN @ v1: idiom_map (5 mapped seed) · enforced_banned (empty seed) ·
  keep_list (35 terms, all present-verified) · negative_keep_list (5, each `# why:`) ·
  emphasis_tokens (CRITICAL, NON-NEGOTIABLE) · scope_qualifier_rule (judgment).
- `wording_lint.py` — F1 (case-insensitive, boundary, inflection-tolerant) · F2 (case-SENSITIVE) ·
  F3 (presence over full surface) · F4 (freeze-time self-consistency) · CHECK_KINDS = fence-only
  (metric refused structurally) · exits 0/1/2.
- `test_wording_lint.py` — 14 tests, one per §2 scenario; red→green confirmed.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_wording_lint` 14/14 green; full method suite 488/488; `add.py check` 186/0; `audit` clean (43)
- [x] coverage did not decrease — net +14 tests; `wording_lint.py` fences all exercised
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; see the two DISCLOSED refinements below (surfaced, not silently edited)
- [x] concurrency / timing of the risky operation is safe — pure-function lint, no IO concurrency; reads are guarded (exit 2 on failure)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; reads local markdown; no eval/network/secrets
- [x] layering & dependencies follow CONVENTIONS.md — guard lives in `tooling/` beside `test_xml_convention.py`; not mirrored
- [x] a person reviewed and approved the change — **risk:high · conservative → human gate; human chose PASS at the verify gate (2026-06-06)**

### DISCLOSED REFINEMENTS (two literal-wording gaps surfaced for your ratification — NOT silent edits; neither weakens a test or relaxes a fence)
1. **F2 emphasis match is CASE-SENSITIVE** — and this is FORCED by §4's own test, not a preference.
   §1 line 38 says match "case-insensitive" generally. But §4's `test_emphasis_token_fence` asserts the
   LIVE surface yields zero `banned_emphasis_token` findings, and the live surface contains the legitimate
   header `## Non-negotiable rules` (SKILL.md). A case-insensitive F2 would match that header → the test
   goes red on GOOD content. Honoring the test ("never weaken a test or edit a frozen contract") FORCES
   F2 to match the ALL-CAPS shout only. Idiom matching (F1) stays case-insensitive as §1 says. NO security impact.
   → §3 change-request (one line) [APPLIED @ v1.1, post-PASS]: the match rule is "case-insensitive for idioms
     (F1); case-SENSITIVE for emphasis tokens (F2)" — splitting the single "case-insensitive" line to match §4.
2. **Substring-of-keep → `ambiguous_ban`** resolves a §3-INTERNAL contradiction (not a deviation from it).
   §3 maps the SAME condition to two codes: line 49 puts "a substring of a keep-list term → `ambiguous_ban`";
   lines 53–54 put "a banned phrase that is a substring of a keep term → `rubric_self_collision`". They
   cannot both hold. The implementation (and §4's `test_ambiguous_ban_refused`) agree with line 49:
   substring-of-keep → `ambiguous_ban`; `rubric_self_collision` is reserved for "a direct-form reintroduces
   a banned phrase". NO behavior gap — both codes exist and fire; only the line-53–54 overlap is removed.
   → §3 change-request (one line) [APPLIED @ v1.1, post-PASS]: drop "is a substring of a keep term, or" from
     the §1 reject line, leaving `rubric_self_collision` = direct-form reintroduction only (line 49 owns substring-of-keep).

### GATE RECORD
Outcome: PASS   <!-- human gated at the verify seam (risk:high·conservative, no auto-pass); both disclosed refinements ratified and applied as the v1.1 prose change-request before this PASS (close-gap-before-gate) -->
If RISK-ACCEPTED -> owner: — · ticket: — · expires: —   (N/A — clean PASS, no residual risk, no security gap)
Reviewed by: Tin Dang · date: 2026-06-06

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] F3 keep-term presence is near-vacuous for SHORT substring-prone keep terms like
  `ADD`/`PASS`/`DDD`/`TDD`/`Role:` — they appear so widely a real global rename could leave the
  lowercase substring present and F3 would stay green; F3 guards a TOTAL loss, never a PARTIAL rename.
  Don't oversell F3 in the v17 retro — semantic-inventory (task 2) + human review own rename-safety
  for these terms; a per-term occurrence-count fix is a metric, refused here, so its home is
  semantic-inventory's per-file unit diff (evidence: F3 is a lenient lowercase-substring presence
  check over the whole surface — keep_term_findings in wording_lint.py)
- [ADD · folded] §3 carried an internal contradiction — substring-of-keep mapped to TWO reject codes,
  line 49 to `ambiguous_ban` and lines 53–54 to `rubric_self_collision` — that survived the
  one-approval contract freeze and was caught only at build. A freeze-time self-consistency lint over
  the CONTRACT's own reject-code table, not just the rubric, would have caught it before the seam;
  cheap to add when a contract carries a code table (evidence: §6 Disclosed Refinement #2 records the
  contradiction and its resolution)
