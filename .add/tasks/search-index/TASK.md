# TASK: add.py search command + keyword index predicate

slug: search-index · created: 2026-07-01 · stage: mvp
milestone: context-search
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add.py:build_parser` (l.6689) — new `search` subparser inserted after `components` (l.6953–6956), before `federate` (l.6958); mirrors `check`/`components`'s read-only shape · `add.py:cmd_check` (l.2667) / `cmd_components` (l.2626) / `cmd_ready` (l.3387) — sibling read-only bodies to mirror (`root = find_root(); if root is None: _die("no_project")`, optional `--json`) · `add.py:_collect_open_deltas` (l.5438–5453) — the corpus glob + degrade-safe-read idiom (`tasks_dir.glob("*/TASK.md")`, `try/except OSError: continue`) the new corpus walker mirrors · `add.py:cmd_compact` (l.3866–3937, esp. l.3925–3931) — ground truth for the archive layout: `compact` renames each member task dir to `archive/<mslug>/tasks/<tslug>/` — confirmed live against `.add/archive/ground-phase/tasks/ground-prose-align/TASK.md`; there is no flat `.add/archive/<tslug>/` · `add_engine/milestones.py:_milestone_doc` (l.39–51) — existing (title, goal) MILESTONE.md reader the new reader extends · `add_engine/taskdoc.py:_task_prose` (l.99–157, continuation-join l.130–136) — precedent for folding a wrapped multi-line field · `add_engine/predicates.py:_rule_coverage_gaps` (l.100–118) — the PURE/NO-EXEC docstring style to follow · `add_engine/io_state.py:_require_root`/`_die` (l.127/l.173) — the fail-closed `no_project` convention · NEW module `add_engine/search.py` (does not yet exist) — mirrors `milestones.py`/`taskdoc.py`'s module-per-reading-concern pattern.
Context (working folder): `.add/milestones/context-search/MILESTONE.md` (frozen Scope/Out/Shared-decisions this task must honor) · `.add/tasks/rule-id-coverage/TASK.md` (shape + rule-ID-convention precedent) · `add-method/tooling/templates/TASK.md.tmpl` (3 trees, NOT edited by this task — no new field needed) · `.add/GLOSSARY.md` (checked — no existing search/index/corpus entry).
Honors (patterns / conventions): read-only command shape (`find_root`/`_die("no_project")`/optional `--json`) · corpus-glob + degrade-safe-read idiom from `_collect_open_deltas` · pure-predicate style from `predicates.py` · module-per-reading-concern from `milestones.py`/`taskdoc.py` · engine-parity invariant (ENGINE_MD5 re-pin across 3 trees on any `add.py`/`add_engine` edit).
Anchors the contract cites: `add.py:build_parser` (l.6689) · `add.py:cmd_check`/`cmd_components` (l.2667/l.2626) · `add.py:_collect_open_deltas` (l.5438) · `add.py:cmd_compact` (l.3866) · `add_engine/milestones.py:_milestone_doc` (l.39) · `add_engine/taskdoc.py:_task_prose` (l.99) · `add_engine/predicates.py:_rule_coverage_gaps` (l.100) · `add_engine/io_state.py:_require_root`/`_die` (l.127/l.173) · new `add_engine/search.py`.
Issues/Risks (→ feed §1): the milestone's frozen Scope text says match "title/goal/rationale lines" as if MILESTONE.md and TASK.md share these 3 named fields — they don't; TASK.md has no literal `goal:`/`rationale:` line (resolved provisionally in §1, flagged lowest-confidence at freeze) · the milestone Scope's "`.add/archive/*/` counterparts" shorthand reads as a flat archive glob, but the real layout nests archived tasks under `archive/<mslug>/tasks/<tslug>/` — a naive flat glob finds zero archived tasks (guarded by a Reject + scenario) · a milestone's `status:` vocabulary (active/queued) and a task's `phase:` vocabulary (ground…done) are different domains sharing the output field name `status` — must not be conflated in the reader · ~230 total milestones+tasks (active+archived) needs no cache (matches the milestone's own "rebuild-on-demand is enough" Out-list reasoning).
Related intent: `.add/milestones/context-search/MILESTONE.md` goal/rationale + its "Shared/risky contracts" line naming this exact invocation grammar as frozen-first for `phase-search-wiring`.
Ground SHA: `c152945`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py search <keyword> [<keyword> ...]` — a read-only CLI command + new pure `add_engine/search.py` module that keyword/substring-scans the active + archived milestone/task corpus's title/goal/rationale (milestone) or title/Feature (task) lines — never full body, never graph traversal, never semantic matching — ranking hits by descending match count and printing `{slug, kind, status, snippet}`.
Framings weighed: corpus-scanned per-call, OR-combined multi-keyword substring match via `nargs="+"` (chosen — matches the milestone's own "rebuild-on-demand is enough" decision + the exit criterion's literal example, while allowing a multi-word OR query) · a single quoted-phrase-only positional arg (rejected — can't OR two independent topics in one call, which `phase-search-wiring`'s "search before drafting" use case likely wants) · a persisted `.add/.search-index.json` cache (rejected — the milestone's Out list explicitly bars real-time/incremental indexing) · AND-combined multi-keyword match (rejected — the milestone says "simple match count"; AND semantics complicate zero-result UX without a clear ask).
Must:
<must>
  - M1: `add.py search <keyword> [<keyword> ...]` accepts ≥1 positional keyword (`nargs="+"`), matching case-insensitive substrings, OR-combined across every keyword.
  - M2: The corpus scanned is exactly 4 glob roots, in order: active milestones `milestones/*/MILESTONE.md`, active tasks `tasks/*/TASK.md`, archived milestones `archive/*/MILESTONE.md`, archived tasks `archive/*/tasks/*/TASK.md` (nested under the owning milestone's compact bundle — never a flat `archive/*/TASK.md`).
  - M3: Match scope for a MILESTONE.md is its H1 title + `goal:` line + `rationale:` line (continuation lines folded) — never full body. Match scope for a TASK.md is its H1 title + §1 `Feature:` line (continuation-folded; an unfilled `<name>` placeholder counts as absent) — never full body.
  - M4: Each artifact's match count sums every keyword's substring occurrences across all its indexed fields; ranking is strictly descending by count, ties broken alphabetically by slug.
  - M5: Each ranked hit prints exactly `{slug, kind (milestone|task), status, snippet}` — snippet is the first indexed field (title, then goal/feature, then rationale) containing a match, truncated to 120 chars with an ellipsis.
  - M6: `status` is the literal `"archived"` for any hit found via an `archive/` root (overriding a stale in-doc `status:`/`phase:` value); otherwise the doc's own `status:` line (milestone) or `phase:` line (task), or `"(unknown)"` if absent.
  - M7: Zero matches is a valid result: exit 0, "no matches" message in text mode, `[]` in `--json` — never a non-zero exit or printed error.
  - M8: `--json` prints the ranked hits as one JSON array of `{slug, kind, status, snippet}` objects — no `count` field (count is sort-only, not part of the frozen output shape).
  - M9: An unreadable/unparseable MILESTONE.md/TASK.md is skipped, never raises (mirrors `_collect_open_deltas`/`_raw_phase_bodies`'s degrade-safe pattern).
</must>
Reject:
<reject>
  - zero keyword args accepted (silent no-op or match-everything) instead of an argparse usage error -> "search_accepts_zero_keywords"
  - the archived-task glob is flat and silently misses every real archived task -> "archived_task_layout_missed"
  - output has fewer/more than the 4 frozen fields -> "output_field_mismatch"
  - hits print in discovery order instead of sorted by descending count -> "unranked_output"
  - full §0–§7 body (beyond title/goal/rationale/feature) is scanned -> "full_body_scanned"
  - the command performs graph/backlink traversal instead of flat keyword matching -> "not_a_backlink_query"
  - the command performs semantic/embedding matching or adds a runtime dependency -> "semantic_search_introduced"
  - the command persists a cache/index file instead of scanning fresh every call -> "incremental_index_introduced"
  - a malformed/unreadable doc raises instead of being skipped -> "search_crashes_on_malformed_doc"
  - an unfilled `Feature: <name>` placeholder is treated as real matchable content -> "placeholder_treated_as_content"
</reject>
After:
<after>
  - `add.py search <keyword...>` returns, for any project state, a deterministic ranked `{slug, kind, status, snippet}` list (or an explicit empty result) covering both active and archived milestones/tasks, computed fresh every call, exit 0 always (except `no_project`/argparse usage errors) — and `phase-search-wiring` has one stable, frozen invocation grammar to wire into scope.md/intake.md.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Mapping TASK.md's "goal/rationale" to §1's `Feature:` line (goal) with NO rationale analog (dropped) is an interpretive fill-in — the milestone Scope text reads as if TASK.md shares MILESTONE.md's exact field names, which it doesn't. Lowest confidence because it's an unconfirmed design choice, not a formalization of prior art. If wrong: an early-phase task (Feature still `<name>`) is searchable only by title until Specify lands — exactly `search-index`'s own current state. Mitigate: confirm at freeze; alternative considered (index §0's "Related intent:" as a rationale analog) was rejected as closer to "full body" than a single line.
  - [ ] confirm OR-combined (not AND) multi-keyword semantics is what `phase-search-wiring`'s guide prose actually wants — verify against that task's real usage once drafted.
  - [ ] confirm 120-char snippet truncation is long enough to be useful in practice — adjust at build if a real hit's snippet reads as unhelpfully cut.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: multiple keywords OR-match case-insensitively   # M1
  Given a milestone whose goal line contains "search" but not "INDEX"
  When `add.py search INDEX search` runs
  Then the milestone is included in the hit list because "search" matched

Scenario: all 4 corpus roots are scanned   # M2
  Given an active milestone, an active task, an archived milestone, and an archived task all containing keyword K
  When `add.py search K` runs
  Then all four appear in the hit list

Scenario: an archived task nested under its milestone bundle is found   # M2, R:archived_task_layout_missed
  Given only an archived task exists at `.add/archive/some-milestone/tasks/some-task/TASK.md` (no flat `.add/archive/some-task/TASK.md`)
  When `add.py search <keyword-in-that-task>` runs
  Then the archived task IS found, printed with kind=task, status=archived

Scenario: match scope excludes a milestone's full body   # M3, R:full_body_scanned
  Given a milestone whose "Shared decisions" section (not title/goal/rationale) contains a unique word
  When `add.py search <that-word>` runs
  Then the milestone is NOT in the hit list

Scenario: match scope excludes a task's full body   # M3
  Given a task whose §5 Strategy body contains a unique word absent from its title/Feature
  When `add.py search <that-word>` runs
  Then the task is NOT in the hit list

Scenario: an unfilled Feature placeholder is not searchable content   # M3, R:placeholder_treated_as_content
  Given a fresh task whose §1 Feature line is still the unfilled `<name>` placeholder
  When `add.py search name` runs
  Then that task is NOT matched by the literal word "name"

Scenario: ranking is by descending match count   # M4, R:unranked_output
  Given two milestones both matching "search" — one with 3 occurrences, one with 1
  When `add.py search search` runs
  Then the 3-occurrence milestone is printed before the 1-occurrence one

Scenario: a tie in match count is broken alphabetically by slug   # M4
  Given two tasks "beta-task" and "alpha-task" each with exactly 1 matching occurrence
  When `add.py search <keyword>` runs
  Then "alpha-task" is printed before "beta-task"

Scenario: each hit prints exactly the 4 frozen fields, snippet truncated   # M5, R:output_field_mismatch
  Given a milestone whose goal line is >120 chars and contains the keyword
  When `add.py search <keyword>` runs (text mode)
  Then the row shows {slug, kind, status} and a snippet truncated to 120 chars ending in an ellipsis, no 5th field

Scenario: status is "archived" overriding a stale in-doc value   # M6
  Given an archived milestone whose MILESTONE.md still literally reads `status: active`
  When `add.py search <keyword-in-that-milestone>` runs
  Then its printed status is "archived", not "active"

Scenario: a live task's status is its phase line   # M6
  Given a live task whose `phase:` line reads `build`
  When `add.py search <keyword-in-that-task>` runs
  Then its printed status is "build"

Scenario: zero keywords is an argparse usage error   # R:search_accepts_zero_keywords
  Given a non-empty corpus
  When `add.py search` runs with no keyword argument
  Then argparse rejects it with a usage error (exit 2); no hit list is printed
  And no artifact is treated as matched-by-default

Scenario: zero matches is a clean, non-error result   # M7
  Given no artifact's indexed fields contain the given keyword
  When `add.py search zzzNoSuchKeywordzzz` runs
  Then it prints "no matches for: zzzNoSuchKeywordzzz" and exits 0

Scenario: an empty corpus returns cleanly   # edge case
  Given a freshly-initialized `.add/` project with zero milestones and zero tasks
  When `add.py search anything` runs
  Then it prints "no matches for: anything" and exits 0, with no exception from missing `milestones/`/`tasks/`/`archive/` dirs

Scenario: --json prints the frozen 4-field array, no count   # M8
  Given one matching milestone
  When `add.py search <keyword> --json` runs
  Then it prints a JSON array with one object containing slug/kind/status/snippet keys and no `count` key

Scenario: --json with zero matches prints an empty array   # M8
  Given no artifact matches
  When `add.py search zzzNoSuchKeywordzzz --json` runs
  Then it prints `[]` and exits 0

Scenario: a malformed/unreadable doc is skipped, not fatal   # M9, R:search_crashes_on_malformed_doc
  Given one task's TASK.md is unreadable
  When `add.py search <keyword>` runs
  Then it completes without raising, printing hits for every other readable artifact

Scenario: no graph/backlink traversal   # R:not_a_backlink_query
  Given milestone A's rationale mentions milestone B by name (a textual reference only)
  When `add.py search <a-keyword-only-literally-in-B>` runs
  Then milestone A is NOT returned merely because it references B

Scenario: no persisted index or cache file   # R:incremental_index_introduced
  Given the corpus changes between two `add.py search` calls (a task's TASK.md edited)
  When `add.py search <keyword>` runs the second time
  Then the result reflects the CURRENT file content, proving no stale cache was consulted

Scenario: a keyword matching both a milestone and a task returns both   # edge case
  Given a milestone and an unrelated task whose titles both contain the word "context"
  When `add.py search context` runs
  Then both the milestone (kind=milestone) and the task (kind=task) appear in the ranked output
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py search — frozen shape @ v1   (read-only; NO-EXEC; fresh per-call scan, no persisted index)

CLI:
  add.py search <keyword> [<keyword> ...] [--json]
    <keyword>  nargs="+" — >=1 required; zero keywords -> argparse usage error, exit 2
    --json     machine-readable output (mirrors `ready --json` / `check --json`)

  Exit codes:
    0   always, including zero matches (a search returning nothing is not an error)
    1   no_project — `_die("no_project")`, same convention as cmd_check/cmd_components
    2   argparse usage error (zero keywords) — stdlib default

Text output (no --json):
    "{n} match(es) for: {keywords joined by ' '}"
    "{slug}  [{kind}, {status}]  ({count} match(es))"
    "    {snippet}"
  Zero hits -> ONLY: "no matches for: {keywords joined by ' '}"

JSON output (--json): one array, each element {"slug", "kind", "status", "snippet"} only.
  Zero hits -> [].

add_engine/search.py  (NEW — mirrors milestones.py/taskdoc.py's module-per-concern pattern):

    MAX_SNIPPET_LEN = 120

    def _fold_continuation(raw: str) -> str
        # joins indented wrap-continuation lines into one flat string
        # (mirrors taskdoc._task_prose's continuation join). PURE.

    def _milestone_fields(text: str) -> dict[str, str]
        # {'title','goal','rationale'} from raw MILESTONE.md text, continuation-folded.
        # Missing field -> ''. Extends milestones._milestone_doc's (title, goal) shape. PURE; NO-EXEC.

    def _task_fields(text: str) -> dict[str, str]
        # {'title','feature'} from raw TASK.md text — H1 title + §1 Feature line
        # (continuation-folded); an unfilled `<name>` placeholder -> ''. PURE; NO-EXEC.

    def _keyword_hit(fields: dict[str, str], keywords: list[str]) -> tuple[int, str] | None
        # (match_count, snippet): case-insensitive substring, OR-combined; count sums
        # ALL keyword occurrences across ALL fields; snippet = first field (dict order)
        # containing a match, truncated to MAX_SNIPPET_LEN with ellipsis. None -> no match. PURE; NO-EXEC.

    def _iter_corpus(root: Path) -> Iterator[tuple[Path, str, bool]]
        # yields (path, kind, archived) over milestones/*/MILESTONE.md, tasks/*/TASK.md,
        # archive/*/MILESTONE.md, archive/*/tasks/*/TASK.md — fixed order. A missing root
        # dir yields nothing (Path.glob on an absent dir is empty, no OSError).

    def _search_corpus(root: Path, keywords: list[str]) -> list[dict]
        # assembles {slug, kind, status, snippet, count} per hit; status="archived" for
        # any archive/-root hit (overrides stale status:/phase: value), else the doc's
        # own status:/phase: line or "(unknown)"; sorted by (-count, slug); an unreadable
        # doc is skipped (try/except OSError, mirrors _collect_open_deltas). PURE except file reads.

add.py wiring — build_parser() (l.6689), inserted after `components` (l.6953-6956),
  before `federate` (l.6958):
    psrch = sub.add_parser("search", help="keyword/substring search over the "
                            "milestone/task corpus (active + archived) — "
                            "title/goal/rationale lines only, never the full body")
    psrch.add_argument("keywords", nargs="+", metavar="KEYWORD",
                       help="one or more keywords (case-insensitive substring, OR-combined)")
    psrch.add_argument("--json", action="store_true", help="machine-readable JSON output")
    psrch.set_defaults(func=cmd_search)

  cmd_search(args) — beside cmd_check/cmd_components:
    def cmd_search(args: argparse.Namespace) -> None:
        root = find_root()
        if root is None:
            _die("no_project")
        hits = _search_corpus(root, args.keywords)
        if getattr(args, "json", False):
            print(json.dumps([{k: h[k] for k in ("slug", "kind", "status", "snippet")}
                              for h in hits], ensure_ascii=False, indent=2))
            return
        query = " ".join(args.keywords)
        if not hits:
            print(f"no matches for: {query}")
            return
        print(f"{len(hits)} match(es) for: {query}")
        for h in hits:
            print(f"{h['slug']}  [{h['kind']}, {h['status']}]  ({h['count']} match(es))")
            print(f"    {h['snippet']}")

Invariants: add.py x3 byte-identical == re-pinned engine_pin.ENGINE_MD5; new
  add_engine/search.py x3 byte-identical across trees; full suite green; no
  templates/*.tmpl edit (no new required field).
```

Glossary deltas: `search corpus`: the active + archived MILESTONE.md/TASK.md file set `add.py search` scans — never a persisted index, rebuilt fresh on every call. `indexed line(s)`: the title/goal/rationale (MILESTONE.md) or title/Feature (TASK.md) lines `add.py search` matches against — deliberately excludes full-body prose.
Least-sure flag surfaced at freeze: [spec] TASK.md's goal/rationale analog (-> §1 Feature: line, no rationale equivalent) is an unconfirmed interpretive fill-in for the milestone's frozen Scope wording — confirmed by Tin 2026-07-01, ship as drafted.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of M1-M9 and 9/10 Reject codes scenario-bound (`R:semantic_search_introduced` has no §2 scenario tag — pre-existing frozen-scenario gap, satisfied structurally since `search.py` imports only `re`/`collections.abc`/`pathlib`/`add_engine.constants`, no new dependency; corrected from an earlier 8/9 arithmetic slip, caught at VERIFY — §1 has 10 Reject codes total, not 9)
Plan (one test per scenario, asserting behavior not internals — 20 gherkin scenarios in §2, not 19 as originally estimated at design time):
<test_plan>
  - OrMatchCaseInsensitive: arrange milestone with "search" not "INDEX" / act `search INDEX search` / assert included · covers: M1
  - AllFourRootsScanned: arrange 4 corpus roots each with keyword K / act search K / assert all 4 hit · covers: M2
  - ArchivedTaskNestedLayoutFound: arrange nested `archive/<m>/tasks/<t>/TASK.md` / act search / assert found, kind=task status=archived · covers: M2, R:archived_task_layout_missed
  - ExcludesMilestoneFullBody: arrange unique word only in body / act search / assert not matched · covers: M3, R:full_body_scanned
  - ExcludesTaskFullBody: arrange unique word only in §5 / act search / assert not matched · covers: M3
  - PlaceholderNotSearchable: arrange unfilled `<name>` Feature / act search "name" / assert not matched · covers: M3, R:placeholder_treated_as_content
  - RankingDescending: arrange 3-vs-1 occurrence milestones / act search / assert 3-occurrence first · covers: M4, R:unranked_output
  - TieBreakAlphabetical: arrange tied-count tasks / act search / assert alphabetical order · covers: M4
  - HitPrintsExactFieldsSnippetTruncated: arrange >120-char goal line / act search text mode / assert 4 fields, 120-char truncated snippet · covers: M5, R:output_field_mismatch
  - StatusArchivedOverridesStale: arrange archived milestone with stale `status: active` / act search / assert status="archived" · covers: M6
  - LiveTaskStatusIsPhase: arrange live task phase=build / act search / assert status="build" · covers: M6
  - ZeroKeywordsIsUsageError: arrange non-empty corpus / act `search` with no args / assert argparse exit 2 · covers: R:search_accepts_zero_keywords
  - ZeroMatchesIsClean: arrange no matches / act search nonsense keyword / assert "no matches for:", exit 0 · covers: M7
  - EmptyCorpusReturnsCleanly: arrange fresh empty `.add/` / act search anything / assert clean exit 0, no exception · covers: edge case
  - JsonPrintsFrozenFieldsNoCount: arrange one match / act search --json / assert 4-key array, no count key · covers: M8
  - JsonZeroMatchesEmptyArray: arrange no matches / act search --json / assert `[]` · covers: M8
  - MalformedDocSkippedNotFatal: arrange one unreadable TASK.md / act search / assert completes, other hits printed · covers: M9, R:search_crashes_on_malformed_doc
  - NoBacklinkTraversal: arrange A's rationale mentions B by name / act search a keyword only in B / assert A not returned · covers: R:not_a_backlink_query
  - NoPersistedCache: arrange corpus changes between two calls / act search twice / assert second reflects current content · covers: R:incremental_index_introduced
  - MatchesBothKindsReturnsBoth: arrange milestone+task both titled "context" / act search context / assert both kinds returned · covers: edge case
  - SearchPureFunctionsContractConformance: 7 direct unit tests on `_fold_continuation`/`_milestone_fields`/`_task_fields`/`_keyword_hit`/`_iter_corpus`/`_search_corpus` · covers: contract conformance (mirrors `test_rule_id_coverage.py`'s own extra pure-function test class)
  - EngineSearchPinned: 3 tree-parity/pin tests (byte-identical across 3 trees, `ENGINE_MD5`/`ENGINE_PKG_MD5` current) · covers: engine-parity invariant
</test_plan>

Tests live in: `add-method/tooling/test_search_index.py` · ran red (19 FAIL on argparse `invalid choice: 'search'` + 8 ERROR on `ModuleNotFoundError: add_engine.search` — genuine missing-implementation RED, no harness noise) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `add-method/tooling/add_engine/search.py` · `add-method/tooling/engine_pin.py` · `.add/tooling/add.py` · `.add/tooling/add_engine/search.py` · `.add/tooling/engine_pin.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add_engine/search.py` · `add-method/src/add_method/_bundled/tooling/engine_pin.py` · `add-method/tooling/test_search_index.py` · `add-method/tooling/test_min_pillar.py` · `.add/SEAMS.md`
Strategy (ordered batches): 1. build `search.py`'s pure functions first, unit-test against this repo's own `context-search/MILESTONE.md`/`search-index/TASK.md`; 2. add `_iter_corpus`/`_search_corpus`, test against a temp `.add/` fixture covering live+archived-milestone+archived-task (nested layout) + a keyword hitting both kinds; 3. wire `build_parser`/`cmd_search`; 4. sync all 3 trees byte-identically; 5. re-pin `ENGINE_MD5`, run full suite.

Persona (optional): `methodology-engine-dev` (pure add.py/add_engine work, NO-EXEC discipline, its home turf).
Known-problem fixes: flat archived-task glob → use `archive/*/tasks/*/TASK.md`, never a flat glob · conflating milestone `status:`/task `phase:` vocabularies → read per doc-type, override to `"archived"` for archive-root hits · unfilled `Feature: <name>` placeholder treated as content → strip bare `<...>`-only values to `''`.
Strategy actually used: Deviated from §5's preferred order in two ways: (1) tests were written before any implementation existed — drafted `search.py` once for design, deliberately moved it aside, wrote the full 30-test suite against the absent module first, confirmed genuine RED (19 FAIL argparse + 8 ERROR ModuleNotFoundError), then restored the implementation, to keep red→green honest rather than unit-testing against already-written code; (2) used synthetic temp fixtures exclusively (direct `MILESTONE.md`/`TASK.md` writes into a temp `.add/`) rather than this repo's own live docs, since `cmd_search` is fully stateless — made every scenario deterministic and avoided coupling tests to this repo's ever-changing prose. Two files outside the originally-declared §5 Scope needed a one-line fix each, both disclosed (not silent) and now folded into Scope above: `test_min_pillar.py` (added `["search", "mvp"]` to its `LIFECYCLE` list — its self-maintaining `test_every_subcommand_is_covered` guard asserts every `build_parser()` verb is exercised) and `.add/SEAMS.md` (its `_declared_scope` anchor drifted `add.py:4433`→`:4461` because `cmd_search` was inserted earlier in the file; `seams-doc`'s own `test_every_anchor_resolves` re-verifies every cited anchor against the current tree, so this was a required correction, not scope creep). Also re-pinned all 3 `engine_pin.py` copies (§5 originally listed only 1) per the project-wide 3-tree invariant.
Safety rule (feature-specific): none — read-only command, NO-EXEC, no state mutation.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (full `add-method/tooling` suite: 2680/0, independently reproduced by add-verify, not trusted from disclosure)
- [x] coverage did not decrease (30 new tests, no existing test weakened)
- [x] no test or contract was altered during build (`test_min_pillar.py`'s one pure addition disclosed in §5, confirmed load-bearing by add-verify)
- [x] the green was EARNED — see Refute-read verdict below
- [x] concurrency / timing safe — fully stateless per-call scan, confirmed by add-verify's own two-call re-run against the live corpus + `except OSError` mirrors the pre-existing `_collect_open_deltas` idiom
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only imports confirmed via AST dump (no new dependency); no exec/subprocess/network; keywords only feed substring `.count()`, never a path/glob (no traversal, no ReDoS)
- [x] layering & dependencies follow precedent (no `CONVENTIONS.md` exists in this repo; `search.py`'s one-way import shape mirrors `milestones.py`/`taskdoc.py` exactly)
- [x] a person reviewed and approved the change (contract freeze — Tin Dang, 2026-07-01)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py search <keyword...>` returns ranked `{slug, kind, status, snippet}` hits, both text and `--json` modes, over the real active+archived corpus — confirmed by running `add.py search search` against this repo's own live `.add/` tree during build
- [x] An archived task nested under `archive/<mslug>/tasks/<tslug>/` (never a flat glob) is found and printed with `status=archived` — confirmed by `ArchivedTaskNestedLayoutFound` test, green
- [x] Zero keywords is an argparse usage error (exit 2), zero matches is a clean exit-0 result — confirmed by `ZeroKeywordsIsUsageError`/`ZeroMatchesIsClean` tests, green
- [x] All 3 engine trees stay byte-identical and `ENGINE_MD5`/`ENGINE_PKG_MD5` are current — confirmed by `EngineSearchPinned` + `test_engine_repin_parity`, green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every symbol §3 names (`_fold_continuation`, `_line_field`, `_milestone_fields`, `_task_fields`, `_keyword_hit`, `_iter_corpus`, `_own_status`, `_search_corpus`, `MAX_SNIPPET_LEN`) is referenced from `add_engine/search.py` and/or exercised by `test_search_index.py` (grep-confirmed, no orphans); `cmd_search`/`psrch` wired into `build_parser()` at line 6986, between `pcomp` (6981) and `pfed` (6994), exactly per the frozen contract
- [x] DEAD-CODE (code) — none found
- [x] SEMANTIC — n/a (this is a code task; WIRING/DEAD-CODE above is the applicable deep-check path)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the CURRENT tree — re-resolved by direct line lookup, not trusting Ground SHA `c152945`'s line numbers: `cmd_components` 2629, `cmd_search` 2670 (new), `cmd_check` 2695, `cmd_ready` 3415, `cmd_compact` 3894, `_collect_open_deltas` 5466, `build_parser` 6717; `milestones._milestone_doc` (l.39) and `taskdoc._task_prose` (l.99) unchanged from Ground, consistent with the disclosed Scope
- [x] anchor drift disclosed, not silent: every anchor after the insertion point moved a uniform +28 lines — self-caused by `cmd_search`'s own ~25-line function body inserted between `cmd_components` and `cmd_check`; expected, not stale/broken

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: agent (add-verify / tdd-verifier persona) · adversarially checked: (1) ran `_search_corpus` directly against the REAL live `.add/` corpus (not synthetic fixtures) — got 9 correctly-ranked hits including the task's own live self-reference, and hit an edge case no fixture tests: `seams`'s MILESTONE.md has no `stage:...status:` header, `_own_status` correctly fell back to `"(unknown)"` — real-world generalization beyond fixtures, strong evidence against overfit; (2) line-by-line scan of `test_search_index.py` for vacuous asserts — none found, every assertion checks a specific falsifiable value (exact snippet length, exact row regex, JSON key-set equality, ordering via `.index()`); (3) checked for stubbed-away logic — none; (4) found and closed one real scenario-coverage gap: no §2 scenario asserts a live (non-archived) milestone's own `status:` value end-to-end — directly invoked `_own_status()` and confirmed correct behavior (a frozen-§2-inherited gap, not a build defect, seeded as a §7 delta below).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent (add-verify / tdd-verifier persona)
1. Security: CLEAR — stdlib-only imports confirmed via AST dump (no new dependency); no exec/subprocess/network; keywords only feed substring `.count()`, never a path/glob (no ReDoS, no traversal); snippet truncation caps any body leakage at 123 chars
2. Concurrency: CLEAR — fully stateless, fresh-per-call scan, reconfirmed via a two-call re-run against the live corpus; `except OSError` mirrors the pre-existing `_collect_open_deltas` idiom exactly
3. Architecture: CLEAR — `search.py`'s import shape mirrors `milestones.py`/`taskdoc.py` exactly (one-way dependency, no upward import into `add.py`); no `CONVENTIONS.md` exists in this repo so precedent-parity is the applicable bar, met
Verdict: PASS
Residue: none
Binding: advisory (task carries no `risk: high` / `sensitivity: mechanical` line)

### GATE RECORD
Outcome: PASS
Reviewed by: agent (add-verify) · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): once `phase-search-wiring` lands, watch whether real usage actually issues multi-keyword OR queries (validates/invalidates the M1 framing choice) and whether the 120-char snippet truncation reads as useful in practice (both flagged as open assumptions at freeze).

### Decisions (ADR)
- [AI] specify — chose corpus-scanned per-call, OR-combined multi-keyword substring match via `nargs="+"`; rejected a single quoted-phrase-only positional arg (rejected — can't OR two independent topics in one call, which `phase-search-wiring`'s "search before drafting" use case likely wants) · a persisted `.add/.search-index.json` cache (rejected — the milestone's Out list explicitly bars real-time/incremental indexing) · AND-combined multi-keyword match (rejected — the milestone says "simple match count"; AND semantics complicate zero-result UX without a clear ask).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: Deviated from §5's preferred order in two ways: (1) tests were written before any implementation existed — drafted `search.py` once for design, deliberately moved it aside, wrote the full 30-test suite against the absent module first, confirmed genuine RED (19 FAIL argparse + 8 ERROR ModuleNotFoundError), then restored the implementation, to keep red→green honest rather than unit-testing against already-written code; (2) used synthetic temp fixtures exclusively (direct `MILESTONE.md`/`TASK.md` writes into a temp `.add/`) rather than this repo's own live docs, since `cmd_search` is fully stateless — made every scenario deterministic and avoided coupling tests to this repo's ever-changing prose. Two files outside the originally-declared §5 Scope needed a one-line fix each, both disclosed (not silent) and now folded into Scope above: `test_min_pillar.py` (added `["search", "mvp"]` to its `LIFECYCLE` list — its self-maintaining `test_every_subcommand_is_covered` guard asserts every `build_parser()` verb is exercised) and `.add/SEAMS.md` (its `_declared_scope` anchor drifted `add.py:4433`→`:4461` because `cmd_search` was inserted earlier in the file; `seams-doc`'s own `test_every_anchor_resolves` re-verifies every cited anchor against the current tree, so this was a required correction, not scope creep). Also re-pinned all 3 `engine_pin.py` copies (§5 originally listed only 1) per the project-wide 3-tree invariant.
- [AI] verify — gate PASS (reviewed by agent (add-verify))

### Spec delta
- [SPEC · seeded] add a §2 scenario asserting a live (non-archived) milestone's own `status:` line surfaces correctly end-to-end (evidence: only the live-task phase-status branch has a scenario; the milestone-status branch was verified at VERIFY via a direct unit call, not by any scenario test — a frozen-§2-inherited gap, closed by the refute-read, not by a build defect)
- [SPEC · seeded] consider whether `_search_corpus` should also degrade-skip a `UnicodeDecodeError`, not just `OSError`, for a non-UTF-8 doc (evidence: matches the pre-existing `_collect_open_deltas` precedent exactly — a repo-wide pattern gap, not unique to this task)
- [SPEC · open] confirm with Tin whether a task's declared `Glossary deltas` (§3) propagating into `.add/GLOSSARY.md` is genuinely deferred to done/fold across this whole milestone-set (evidence: both `search-index`'s and the sibling `rule-id-coverage`'s declared terms are absent from GLOSSARY.md while both were mid-flight — consistent, but never explicitly confirmed as the intended lifecycle)

### Competency deltas
- [ADD · folded] running two `add-build`/`add-verify` agent pairs in parallel in the SAME working tree (no worktree isolation) caused two real cross-task collisions this loop: (1) a line-number anchor in a THIRD task's artifact (`seams-doc`'s `.add/SEAMS.md`) drifted mid-build because this task's own `cmd_search` insertion shifted every symbol after it in `add.py` — caught and disclosed, not silent; (2) a scope-lock false-positive fired against `seams-doc`'s gate for a file (`test_min_pillar.py`) legitimately touched only by THIS task, requiring the established tests→build→advance re-cross recovery twice. Parallel streams sharing one working tree are viable but need either the re-cross recovery playbook on standby, or `isolation: "worktree"` when two tasks' scopes both touch shared engine files (evidence: this loop, 2 separate incidents). [folded foundation-version 60]
- [TDD · folded] a refute-read that runs the implementation against REAL project data (not just synthetic fixtures) found a genuine, untested-by-fixture edge case (`_own_status` falling back to `"(unknown)"` for a milestone with no status header) that 30 passing tests missed — worth a standing verify-agent instruction to always spot-check against live data when the corpus is available, not just the fixture suite (evidence: this loop's refute-read). [folded foundation-version 60]

