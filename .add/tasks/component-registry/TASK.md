# TASK: Component registry: declare components with root + verify + green-bar

slug: component-registry · created: 2026-06-24 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project `auto`: method-defining engine scope (touches §5 scope-anchor + adds a new TASK-header field). risk:high under auto is refused at completion (`unguarded_high_risk_auto`); the §3 freeze + a human verify stay required. -->
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
  - `add-method/tooling/add.py:_declared_scope(root, slug) -> list[str]|None` (L3878) — parses §5 `Scope (may touch):`; anchors tokens to `root.parent` (the project root, since `root` = the `.add/` dir). THE seam a `component:` declaration redirects: the anchor must become the component's `root` instead of the project root.
  - `add-method/tooling/add.py:_in_scope(rel, declared) -> bool` (L3920) — subtree containment (`…/` prefix). Unchanged shape; consulted after the anchor resolves.
  - `add-method/tooling/add.py:_scope_walk(rootp) -> dict[str,str]` (L3932) — walks the whole tree from `rootp`, prunes `_SCOPE_EXCLUDE_DIRS` (L3873: `.git .add __pycache__ node_modules .serena …`). Per-component scoping narrows `rootp` to the component root (the unlock task 2 builds on).
  - `add-method/tooling/add.py:_autonomy_level(hdr) -> str|None` (L1289) + `_AUTONOMY_LINE_RE` (L1287: `(?:^|·)[ \t]*autonomy:[ \t]*([^\s<#|]+)`) — EXACT model for a new `component:` TASK-header field reader (`_task_component`): anchored line regex, member|None|"?" (placeholder `<…>` declines → None).
  - `add-method/tooling/add.py:_RISK_HIGH_RE` (L1278) — same `(?:^|·)…:` slug-line grammar a `component:` token follows.
  - `add-method/tooling/add.py:_task_header(root, slug) -> str` (L1308) — the header region (HTML-comments stripped, body split at first `## `) where `risk:`/`autonomy:`/the new `component:` live.
  - `add-method/tooling/add.py:_project_autonomy_token(root)` (L3599) — model for a PROJECT.md project-level reader; the component REGISTRY reader (`_components(root)`) is its analog but reads NEW `.add/components.toml` → `{name: {root, verify, green_bar, language}}`.
  - `add-method/tooling/add.py:find_root(start) -> Path|None` (L308) + `ROOT_DIRNAME=".add"` (L30) / `STATE_FILE="state.json"` (L31) — root resolution; `.add/components.toml` sits beside `state.json`.
  - NEW symbols the build adds: `_COMPONENT_LINE_RE`, `_task_component(root, slug)`, `_components(root)` (parse + fail-loud on malformed), `_component_root(root, name)` (resolve a component's anchor for `_declared_scope`). Registry is a parsed FILE read at gate time — stateless, like scope; NOT in state.json.
Context (working folder):
  - NEW `.add/components.toml` (does not exist yet) — the registry file + its schema; an example committed under the method.
  - `add-method/tooling/templates/TASK.md.tmpl` — §5 scope grammar comment + slug-line; gains a `component:` affordance (propagate to the 2 mirror templates).
  - 3-tree parity: edits land in canonical `add-method/tooling/add.py`, then mirror to `.add/tooling/add.py` + `add-method/src/add_method/_bundled/tooling/add.py`, and re-pin `add-method/tooling/engine_pin.py` (ENGINE_MD5) — per the release-gate parity discipline.
  - Tests live in `add-method/tooling/test_*.py`; models: `test_scope_gate_enforce.py` · `test_scope_decl_template.py` · `test_autonomy_reader_anchor.py`. NEW `test_component_registry.py`.
Honors (patterns / conventions):
  - MILESTONE.md invariants: opt-in/byte-identical when zero components declared (grandfather, mirrors the §5 undeclared-scope grandfather) · designed-for-failure: malformed/missing `components.toml` fails LOUD/CLOSED, never anchors to a guessed root.
  - CLAUDE.md: red/green TDD (suite red for the right reason before build) · design-for-failure on the IO/parse path.
  - Engine convention: scope readers are PURE + fail-closed (`_declared_scope`/`_scope_walk` take bytes-only, no git); the new readers match (read-only, pure, OSError → safe default).
Anchors the contract cites: `_declared_scope` · `_in_scope` · `_scope_walk` · `_autonomy_level` / `_AUTONOMY_LINE_RE` · `_task_header` · `_project_autonomy_token` · `find_root` · `ROOT_DIRNAME` · `.add/components.toml`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Component registry — declare named components (root · verify · green-bar · language) and let a task bind to one
Framings weighed: `.add/components.toml` + stdlib tomllib (chosen) · a fenced block in PROJECT.md · per-task `component:` only with no central registry
Must:
<must>
  - Parse `.add/components.toml` (stdlib `tomllib`, Python 3.11+) into a map `{name: {root, verify, green_bar, language}}`; `root` is required, the rest optional. Exposed by `_components(root) -> dict`.
  - A task MAY declare `component: <name>` in its header region, read by `_task_component(root, slug)` via an anchored line regex modelled on `_AUTONOMY_LINE_RE` — returns the name · None (no line / unfilled `<…>`) · "?" (real-but-unknown token).
  - Absent registry (no `components.toml`) ⇒ byte-identical to today: `_components` returns `{}`, no task is component-bound, scope-anchoring is unchanged. Components are OPT-IN.
  - A task declaring `component: X` gains component X's `root` subtree as IMPLICIT §5 scope cover — ADDED to (composing with) any explicit `Scope (may touch):` tokens, NOT redrawing their resolution. (`_declared_scope` appends the component root when bound.)
  - The `verify` field is stored OPAQUE this task (a raw string) — parsed + exposed, never executed here; task `per-component-verify` owns running it. Freezing it as a string keeps that door open.
  - All registry reads are PURE + read-only; an unreadable/absent file ⇒ `{}` (safe default), a malformed file ⇒ a NAMED failure (below), never a guessed anchor.
</must>
Reject:
<reject>
  - `.add/components.toml` present but unparseable, or an entry missing required `root` -> "components_malformed"
  - a task declares `component: <name>` absent from the registry -> "component_unknown"
  - a component `root` resolves OUTSIDE the project root -> "component_root_outside"  (fail-closed, mirrors `_confined`)
</reject>
After:
<after>
  - `_components(root)` returns the parsed map (or `{}` when the file is absent).
  - `_task_component(root, slug)` returns the bound component name | None | "?".
  - A `component: X` task's effective §5 scope contains X's `root` subtree (containment via `_in_scope`), composed with its explicit tokens.
  - Zero `components.toml` in any existing project ⇒ no observable change (suite stays green, scope gate unchanged).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `verify` frozen as an OPAQUE string now (executed later by task 2) — CONFIRMED (Tin, 2026-06-24). Residual risk acknowledged: if task 2 needs structured fields the schema reopens as a change-request; accepted to keep this freeze small.
  - [x] Scope binding ADDS the component root (composes with explicit tokens), does NOT redirect token resolution — CONFIRMED (Tin, 2026-06-24): backward-compatible, lowest blast radius.
  - [x] Registry lives in `.add/components.toml` (stdlib tomllib, zero-dep), not a PROJECT.md block — CONFIRMED (Tin, 2026-06-24).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Parse a well-formed registry
  Given a .add/components.toml with [component.gateway] root="apps/gateway" verify="pytest -q" green_bar="tests" language="python"
  When _components(root) is read
  Then it returns {"gateway": {"root": "apps/gateway", "verify": "pytest -q", "green_bar": "tests", "language": "python"}}

Scenario: A task binds to a component
  Given a TASK.md header line `component: gateway` and gateway in the registry
  When _task_component(root, slug) is read
  Then it returns "gateway"

Scenario: No registry means today's behavior (opt-in)
  Given a project with NO .add/components.toml
  When _components(root) is read and the scope gate runs on any task
  Then _components returns {} and the scope anchor + gate behave byte-identically to pre-component ADD
  And no task is treated as component-bound

Scenario: Binding adds the component root to scope (compose)
  Given a task `component: gateway` whose §5 declares `apps/gateway/rate_limits/` and gateway.root="apps/gateway"
  When the effective declared scope is resolved
  Then it covers both "apps/gateway/" (from the binding) and "apps/gateway/rate_limits/" (explicit), via _in_scope containment
  And the explicit token still resolves exactly as it does today (binding ADDS, never redraws)

Scenario: verify is stored opaque, not executed
  Given gateway.verify="pytest -q && rm -rf /"
  When _components(root) is read during this task
  Then the string is returned verbatim as data and NO shell command is executed

Scenario: Unreadable registry yields the safe default
  Given a .add/components.toml that raises OSError on read
  When _components(root) is read
  Then it returns {} (safe default) without raising

Scenario: Malformed registry is rejected loud
  Given a .add/components.toml that is not valid TOML, or a [component.x] missing the required root key
  When _components(root) is read
  Then it fails with "components_malformed"
  And no component is registered and no scope cover is granted (fail-closed, nothing partially applied)

Scenario: Unknown component binding is rejected
  Given a TASK.md `component: ghost` and ghost ABSENT from the registry
  When _task_component resolution is gated
  Then it fails with "component_unknown"
  And the task's explicit §5 scope is left exactly as declared (no implicit cover added)

Scenario: A component root outside the project is rejected
  Given [component.evil] root="../../etc"
  When _components(root) resolves the component root
  Then it fails with "component_root_outside"
  And that component grants no scope cover (fail-closed, mirrors _confined)

Scenario: Unfilled placeholder is not a binding
  Given a TASK.md header still carrying the template `component: <name>`
  When _task_component(root, slug) is read
  Then it returns None (an unfilled <…> placeholder is declined, exactly like _autonomy_level)
  And the task is treated as unbound — no component_unknown is raised

Scenario: Bound task with no explicit scope line is covered by its component root
  Given a task `component: gateway` with NO `Scope (may touch):` line
  When the effective declared scope is resolved
  Then it covers "apps/gateway/" (the component root alone)
  And a touch outside apps/gateway/ is still out-of-scope
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine API — add-method/tooling/add.py · all PURE + read-only · NO state.json · `root` = the .add/ dir (find_root())

_components(root) -> dict[str, dict]
  reads  root/"components.toml"   (beside state.json)
  absent file | OSError | malformed TOML | entry missing required `root`  -> {}   (DEGRADE-SAFE; never raises, never crashes a read)
  parsed OK -> { "<name>": {"root": str, "verify": str|None, "green_bar": str|None, "language": str|None}, … }

_component_root(root, name) -> str | None
  project-root-relative path WITH trailing "/" of component `name`'s root, resolved + _confined against root.parent.resolve()
  name absent | root resolves OUTSIDE the project root -> None   (FAIL-CLOSED: dropped, grants no cover — mirrors _declared_scope's _confined drop)

_task_component(root, slug) -> str | None | "?"
  _COMPONENT_LINE_RE (modelled on _AUTONOMY_LINE_RE) over _task_header(root, slug)
  no line | unfilled `<…>` placeholder -> None  ·  token in registry -> name  ·  token NOT in registry -> "?"

_declared_scope(root, slug) -> list[str] | None        # EXTENDED, additive
  unbound task (_task_component is None/"?") -> UNCHANGED from today (byte-identical)
  bound task (known name) -> the component root (_component_root) is APPENDED to the resolved token list (dedup);
    explicit token resolution is UNTOUCHED; a bound task with NO `Scope (may touch):` line returns [component_root] (not None)

_component_findings(root) -> list[(code, detail)]       # NEW · consumed by cmd_check / the scope gate (the scope_violation surface)
  "components_malformed"    — components.toml present but unparseable, or a [component.x] missing required `root`
  "component_unknown"       — a task header binds `component: <name>` absent from the registry  (_task_component == "?")
  "component_root_outside"  — a component `root` resolves outside the project root  (fail-closed: cover already dropped)

components.toml schema:
  [component.<name>]
  root      = "<project-root-relative path>"   # REQUIRED
  verify    = "<shell command>"                # optional · stored OPAQUE · NEVER executed by this task
  green_bar = "<phrase>"                        # optional
  language  = "<id>"                            # optional
```

Reject-code mapping (every §1 Reject has a contracted response):
  components_malformed   -> `_components` degrades to {} AND `_component_findings` emits it (red gate, loud — not a crash)
  component_unknown      -> `_task_component` returns "?"; `_component_findings` emits it; no implicit scope cover added
  component_root_outside -> `_component_root` returns None (cover dropped); `_component_findings` emits it

Least-sure flag surfaced at freeze: [contract] reject codes are degrade-safe GATE FINDINGS (readers return {} / drop cover), not exceptions that crash a read — because crashing `status`/`report` on a user-authored config is worse than a loud red gate; if wrong (you want a hard-crash on malformed config): rework all 4 readers + the `cmd_check` wiring. [contract] `verify` frozen as an opaque string — if task 2 needs structured fields: a change-request re-freeze rippling to tasks 2–5. Both ACCEPTED by Tin at freeze.
Status: FROZEN @ v1 — approved by Tin Dang, 2026-06-24.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 5 new/extended seams (the readers are small + pure).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - ParseRegistry: well-formed map · absent→{} · unreadable→{} (degrade-safe) · verify stored opaque (not executed)
  - ComponentRoot: known→"apps/gateway/" · absent→None · outside-project→None (fail-closed)
  - TaskBinding: bound→name · unfilled `<…>`→None · unknown token→"?"
  - ScopeBinding: bound ADDS component root composing with explicit token · bound-no-scope→[root] + out-of-root excluded · GREEN PIN unbound `_declared_scope` byte-identical
  - ComponentFindings: malformed→finding (not crash) · missing required root→malformed · unknown binding→finding · outside root→finding · clean→[]
</test_plan>
Red run (2026-06-24): 18 tests · 1 GREEN (unbound `_declared_scope` non-regression pin) · 17 RED — 15 AttributeError (missing `_components`/`_component_root`/`_task_component`/`_component_findings`) + 2 FAIL (`_declared_scope` not yet extended). Red for the right reason.

Tests live in: `add-method/tooling/test_component_registry.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py`
Strategy (ordered batches): 1. RED — write `add-method/tooling/test_component_registry.py` (11 scenarios) against the §3 signatures · 2. add `_COMPONENT_LINE_RE` + `_components` + `_component_root` + `_task_component` + `_component_findings` to canonical `add-method/tooling/add.py` · 3. EXTEND `_declared_scope` to append the bound component root (additive; unbound path untouched) · 4. wire `_component_findings` into `cmd_check` (scope_violation surface) · 5. add `component:` affordance to `templates/TASK.md.tmpl` · 6. GREEN, then propagate to the 2 mirrors + re-pin `engine_pin.py` ENGINE_MD5.
Safety rule (feature-specific): the unbound/zero-registry path MUST stay byte-identical — `_declared_scope` returns exactly today's value when `_task_component` is None/"?"; readers degrade-safe (never raise on a read), only `_component_findings` is loud.
Code lives in: `add-method/tooling/add.py` (+ mirrors)
Constraints: do NOT change any test or the contract; stdlib only (`tomllib`, no new dependency); ask if unclear.
Scope note: `.add/` is pruned by `_scope_walk` (`_SCOPE_EXCLUDE_DIRS`), so the gate-enforced token is `add-method/`; the `.add/tooling/add.py` mirror is declared for honesty though it is not walked. Re-cross tests→build after declaring to re-anchor `scope.declared` (per the §5-anchor-snapshot lesson).

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite **1686 green / 0 fail** (exit 0); the 20-test `test_component_registry.py` included.
- [x] coverage did not decrease — net +20 tests (suite 1666→1686).
- [x] no test or contract was altered during build — §3 FROZEN untouched; the 2 added tests were written in a re-opened `tests` phase (tripwire re-anchored), never edited mid-build.
- [x] the green was EARNED — adversarial refute-read (independent subagent) returned GREEN-NOT-EARNED on first pass: MAJOR (`_component_findings` `tasks/` scan could raise `PermissionError`, violating degrade-safe) + MINOR (`?` name/sentinel collision). BOTH FIXED + each now covered by a guarding test (`test_unreadable_tasks_dir_degrades_safe`, `test_reserved_question_mark_name_is_malformed`).
- [x] concurrency / timing — N/A: all new readers are PURE + read-only (no shared state, no writes; registry parsed fresh per call).
- [x] no exposed secrets, injection openings, or unexpected dependencies — `verify` stored OPAQUE, zero exec/subprocess/eval paths (refute-read confirmed); `_confined` fail-closes path traversal; dependency is stdlib `tomllib` only (guarded import), no new package.
- [x] layering & dependencies follow CONVENTIONS.md — new readers match the scope-reader idiom (pure, fail-closed, OSError→safe default); findings ride the established `cmd_check` red-check surface (like `wave_ledger_malformed`).
- [x] a person reviewed and approved the change — Tin Dang signed off the PASS, 2026-06-24.

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] Zero `components.toml` ⇒ byte-identical to pre-component ADD — GREEN PIN `test_unbound_declared_scope_unchanged` + full suite green; live `add.py status` on AIDD-Book (no components.toml) unchanged.
- [x] A well-formed `components.toml` parses to the typed map — `ParseRegistry` green + live `_components()` read on a temp registry returned the typed dict.
- [x] A `component: gateway` task's declared scope CONTAINS `apps/gateway/`, composed with its explicit tokens — `ScopeBinding` green (`test_binding_adds_component_root_composing`).
- [x] Malformed/outside `components.toml` surfaces a loud finding WITHOUT crashing a read — manual `add.py check` on a temp malformed registry printed `FAIL component registry (components_malformed): … Expected '=' …` + exit 1, **no traceback**; clean registry → 0 component findings.
- [x] The `verify` string is never executed during a read — `test_verify_is_stored_opaque_not_executed` (dangerous string `rm -rf /`, filesystem untouched); refute-read confirmed zero exec paths.
- [x] 3-tree parity holds — all 3 `add.py` byte-identical (md5 `0d1d0f18…`), ENGINE_MD5 re-aimed; parity/pin tests green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `_COMPONENT_LINE_RE`→`_task_component`; `_components`→`_component_root`/`_task_component`/`_component_findings`; `_component_root`→`_declared_scope`; `_task_component`→`_declared_scope`/`_component_findings`; `_component_findings`→`cmd_check` (the new red-check loop). Confirmed by grep + the refute-read trace.
- [x] DEAD-CODE (code) — no orphaned symbol; every new function has a live caller (above). The unbound `_declared_scope` path is unchanged (GREEN PIN).
- [x] SEMANTIC (prose) — `templates/TASK.md.tmpl` `component:` hint folded into the existing autonomy comment (no net-new comment → lean-pass `<12` invariant held, `test_template_form_tags` green); the `engine_pin.py` re-aim note narrates the change + self-heal.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: — · ticket: — · expires: —   (n/a — PASS, no security gap; the one refute-read MAJOR was FIXED, not waived)
Reviewed by: Tin Dang · date: 2026-06-24

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `add.py check` red rate for `components_malformed`/`component_unknown`/`component_root_outside` once projects adopt `.add/components.toml`.

### Spec delta
- [SPEC · open] add the `component:` affordance hint to `TASK.fast.md.tmpl` too (evidence: refute-read noted the fast-lane template omits it — fast tasks in a monorepo can't see the binding option) (evidence: refute-read non-finding #7).
- [SPEC · open] `per-component-verify` (task 2) should consume `_components()[name]["verify"]` + `green_bar` to run a bound task's own suite at the gate (evidence: that field is parsed-but-unused until task 2 — the deliberate opaque-now freeze) (evidence: §1 verify-opaque decision).

### Competency deltas
- [ADD · open] a degrade-safe contract clause ("never raise on a read") needs an explicit unreadable-dir/permission test — the happy-path tests passed while one OSError-subclass path (PermissionError from iterdir) still crashed; the refute-read caught it (evidence: refute-read MAJOR, fixed by `test_unreadable_tasks_dir_degrades_safe`).
- [ADD · open] a sentinel value used in logic (`"?"`) must be reserved from any user-supplied namespace it shares (TOML component names) or it silently collides (evidence: refute-read MINOR, fixed by reserving `"?"` + `test_reserved_question_mark_name_is_malformed`).
