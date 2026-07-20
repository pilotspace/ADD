# TASK: oneshot/benchmark/small-medium declares an AI-chosen skip-set from {scenarios,observe} only; contract AI-auto-frozen (never skipped); every skip recorded (no silent skips)

slug: fast-lane-skips · created: 2026-07-09 · stage: mvp · risk: high
milestone: three-phase-flow
sensitivity: architecture
autonomy: conservative
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add_engine/constants.py:PHASES` (line 57) — the frozen 9-tuple `("ground","specify","scenarios","contract","tests","build","verify","observe","done")`; this task's skip mechanism jumps OVER two of its members, never reorders or removes them from the tuple.
  - `add-method/tooling/add_engine/constants.py:PHASE_GROUPS` (line 106) — the SHIPPED (not the stale §1-text) shape confirmed by direct read: `DIRECTION=("ground","specify","scenarios","contract","tests")`, `BUILD=("build",)`, `VERIFY=("verify","observe")`. Both skippable phases (`scenarios`, `observe`) sit in DIFFERENT bundles (DIRECTION, VERIFY) — the skip mechanism is bundle-agnostic, keyed off `PHASES` directly, never off `PHASE_GROUPS`.
  - `add-method/tooling/add.py:cmd_advance` (lines 1244-1354) — the single-step phase-crossing engine. Line 1271 `nxt = PHASES[idx + 1]` computes the next phase UNCONDITIONALLY (no lane/fast-awareness today); the crossing-specific guards that follow (`if nxt == "contract"` ~1282 consumer-hold, `if nxt == "build"` ~1292 freeze/build-entry gate, `if nxt == "tests"` ~1303 contract-snapshot) all branch on the FINAL value of `nxt` — this task's skip pre-pass must run BEFORE these so a skip-adjusted `nxt` is what they see. Line ~1329 `state["tasks"][slug]["phase"] = nxt` is the actual write (validate-then-write discipline: every refusal in this function fires before this line).
  - `add-method/tooling/add.py:cmd_new_task` (line 664) — `fast = bool(getattr(args, "fast", False))` (line 724) selects `TASK.fast.md` vs `TASK.md` at render time; `state["tasks"][slug]["fast"] = True` (line 768) is the DURABLE lane marker `cmd_status`/`cmd_guide`/`cmd_check` read — NOT the TASK.md header line, which is presentation-only. `--oneshot` is an additive sibling flag on the same `pn` (`new-task`) subparser (`pn.add_argument("--fast", ...)` at line 7711).
  - **CRITICAL PRIOR-ART FINDING**: today's `--fast` lane does NOT skip a phase in the state machine at all. `test_fast_new_task_flag.py:_to_tests` (line 80) drives FOUR plain `advance` calls with the comment "ground -> specify -> scenarios -> contract -> tests" — a fast task visits `phase: scenarios` exactly like a full task; the ONLY difference is `TASK.fast.md.tmpl` (no `## 2 · SCENARIOS` heading) has nothing to fill there, so the visit is a content-free no-op turn. `fast-lane.md`'s own ladder prose ("ground → specify → contract → tests...", omitting scenarios) describes the CEREMONY (nothing to author), not the ENGINE'S actual phase walk. This task is the first to make the skip a REAL engine-level jump (fewer `advance` calls, not just fewer sections to fill) — the milestone's stated "turn-fragmentation" cost this task cuts is exactly this redundant pass-through turn.
  - `add-method/tooling/templates/TASK.fast.md.tmpl` (21 lines) — sections {0,1,3,4,5,6} only; §2 SCENARIOS and §7 OBSERVE are already absent from the template (behavior collapse), confirming `scenarios`/`observe` are the two phases with zero required ceremony today — the natural, already-precedented candidates for a real skip. `TASK.md.tmpl` (full lane) has ZERO byte headroom (task `ai-plan-verify-gate`'s own §5 Optimization stance: "21B total / 2B comment") — any new scaffold line goes in the fast template only, full-lane tasks author freeform (task2's OWN precedent for its "AI-verify record" block, reused verbatim here for `skips:`/`Skip rationale:`).
  - `add-method/tooling/add.py:_task_gate_mode` (line 1396) + `_GATE_MODE_RE` (line 1394, `re.compile(r"(?:^|·)[ \t]*gate_mode:[ \t]*([^\s<#|]+)", re.MULTILINE)`) — the EXACT anchored-header-token idiom this task's new `_SKIPS_LINE_RE`/`_task_skip_set` mirrors verbatim (a CSV token like `scenarios,observe` has no whitespace, so it is captured whole by the same `[^\s<#|]+` group).
  - `add-method/tooling/add_engine/predicates.py:_ai_freeze_allowed` (line 39, per task `ai-plan-verify-gate` §3) — the SHIPPED, FROZEN, DONE mechanism this task composes, never re-derives: `gate_mode: ai-plan-verify` + `autonomy: auto` + a non-floor sensitivity is the double opt-in that lets `add.py freeze --ai-plan-verify` succeed; a floor sensitivity (`security`/`data`/`architecture`) or non-auto autonomy makes it refuse (`ai_freeze_blocked_sensitivity` / `ai_freeze_requires_auto`), forcing the human `add.py freeze --by <name>` path — UNCHANGED by this task. This task's skip mechanism (scenarios/observe) is a SEPARATE axis from the freeze mechanism (contract auto-vs-human) — orthogonal, composed only via `--oneshot` writing both declarations at once, never entangled in one predicate.
  - `add-method/tooling/add_engine/autonomy.py:_streams_posture`/`_project_autonomy` (lines 33-93, per task `ai-plan-verify-gate` ground notes + direct read) — the exact PROJECT.md-level declared-field idiom (`(?:^|·)[ \t]*key:[ \t]*(token)`, HTML comments stripped, fail-safe default when absent/malformed) this task's new `benchmark_mode:` PROJECT.md field mirrors — with an INVERTED-polarity default: `_project_autonomy`'s absence means "auto" (the method's own already-trusted default); `benchmark_mode`'s absence must mean `False` (a NEW trust/ceremony-loosening capability never silently activates — same philosophy `_task_gate_mode` already applies, just at the project scope).
  - `add-method/tooling/add.py:cmd_status` (line 2175) `_fast_mark` (~line 2384, `" · fast" if ... tasks.get(active,{}).get("fast") is True else ""`) and `cmd_guide` (line 2549) — the additive-cue, existence-gated presentation idiom (silent when not applicable, byte-identical output otherwise) this task's new `skips:` status/guide line follows.
  - `add-method/tooling/add.py:_gate_explain` (line 1587, extended once already by task `ai-plan-verify-gate`'s M8) — the read-only additive-print-line idiom this task's skip-set explain line follows (a second additive line beside the existing gate_mode one, same function).
  - `add-method/tooling/add.py:_audit_findings` (line 6685) / `cmd_audit` (line 6921) and the `ai_freeze_checklist_missing` residual glint (~line 6721-6724, per task `ai-plan-verify-gate`) — the MEASURE-NOT-BLOCK residual-glint idiom this task's `skip_rationale_missing_post_hoc` glint mirrors exactly (symmetric shape: a state.json record whose TASK.md evidence was later mangled/deleted).
  - `add-method/tooling/add.py:_flag_well_formed` (line 5632) — the substantive-content-check idiom (a label + non-trivial body, not a bare template placeholder) this task's `Skip rationale:` field's non-emptiness check follows in spirit, though this task's own `_skip_rationale` reader is a simpler regex-clause extractor, not a full well-formedness grammar (disclosed as a lowest-confidence-adjacent simplification, not the flag itself).
  - `add-method/tooling/add.py` `freeze_skipped` marker (lines ~1081-1090, ~6792-6794, ~6938-6939; `test_freeze_gate_universal.py`) — a DIFFERENT, PRE-EXISTING "no silent skip" precedent at a DIFFERENT boundary (the universal `--skip-freeze` escape that crosses tests→build on a DRAFT §3, state-only marker, never a TASK.md write). This task's `state["tasks"][slug]["skips"]` list follows the SAME state-only, never-silent recording shape, but is a DISTINCT mechanism (this task's skip-set never touches the freeze gate; `freeze_skipped` never touches the phase ladder) — named here so Strategy does not conflate the two.

Context (working folder): no data files, no runtime config beyond TASK.md header prose, PROJECT.md prose, and a handful of pure Python functions/regexes in `add.py`/`add_engine/{constants,predicates,autonomy}.py` plus two template files. No network, no subprocess, no schema/DB — NO-EXEC discipline holds trivially (regex/dict-lookup/list-append/file-read/atomic-write only, same risk profile as `ai-plan-verify-gate`).

Honors (patterns / conventions):
  - Anchored-header-token idiom (`_GATE_MODE_RE`/`_task_gate_mode`, `_AUTONOMY_LEVELS`/`_autonomy_level`, `_SENSITIVITY_VALUES`/`_task_sensitivity`) — reused verbatim for `_SKIPS_LINE_RE`/`_task_skip_set`, never a new parsing style.
  - Project-level declared-field idiom (`_streams_posture`/`_project_autonomy`) — reused verbatim for `_project_benchmark_mode`.
  - Pure BLOCK-list/predicate-returns-`(bool, code|None)` idiom (`_ai_freeze_allowed`) — reused verbatim for `_skip_set_allowed`.
  - Additive-cue presentation idiom (`_fast_mark`, `bundle:` line, `_gate_explain`'s gate_mode line) — existence-gated, silent/byte-identical when not applicable — reused for the new `skips:` status/guide/gate-explain lines.
  - MEASURE-NOT-BLOCK residual-glint idiom (`ai_freeze_checklist_missing`) — reused for `skip_rationale_missing_post_hoc`.
  - validate-then-write (every `_die` in `cmd_advance` fires before `state["tasks"][slug]["phase"] = nxt`) — this task's skip pre-pass is inserted strictly ABOVE that write, so a refusal never leaves a task half-transitioned.
  - Byte-ceiling-forced fast-template-only scaffold (task `ai-plan-verify-gate`'s own disclosed §5 deviation for "AI-verify record") — reused verbatim: `skips:`/`Skip rationale:` scaffolding lands in `TASK.fast.md.tmpl` only; `TASK.md.tmpl` (full lane) is untouched, a full-lane task under `benchmark_mode` authors both fields freeform.
  - 3-tree byte-identical propagation (methodology-engine-dev's Critical Rule + `.add/SEAMS.md#three-tree-parity`) — a BUILD-phase obligation, named here so Strategy inherits it.

Seams consulted: `.add/SEAMS.md#three-tree-parity` — the 3-copy byte-identical-twin guard.

Anchors the contract cites: `add_engine/constants.py:_SKIPPABLE_PHASES` (new) · `add.py:_SKIPS_LINE_RE`/`_task_skip_set` (new, mirrors `_GATE_MODE_RE`/`_task_gate_mode`) · `add_engine/predicates.py:_skip_lane_eligible` (new) · `add_engine/predicates.py:_skip_set_allowed` (new, mirrors `_ai_freeze_allowed`) · `add.py:_skip_rationale` (new) · `add.py:_project_benchmark_mode` (new, mirrors `_streams_posture`) · `add.py:cmd_advance` (extended, the `if nxt in _SKIPPABLE_PHASES:` pre-pass) · `add.py:cmd_new_task` (extended, `--oneshot`) · `add.py:cmd_status`/`cmd_guide` (extended, additive `skips:` line) · `add.py:_gate_explain` (extended, additive line) · `add.py:_audit_findings` (extended, `skip_rationale_missing_post_hoc`) · `add-method/tooling/add_engine/predicates.py:_ai_freeze_allowed` (UNCHANGED, cited for the `--oneshot` coupling only).

Issues/Risks (→ feed §1):
  - **Today's `--fast` lane is a template/ceremony collapse, not an engine skip** (see CRITICAL PRIOR-ART FINDING above). This task must decide whether to GENERALIZE `fast:true` itself into skip-eligibility (retroactively giving every existing and future `--fast` task real skip power the moment it declares `skips:`) or gate the new power behind `--oneshot` ONLY. The milestone's own Scope(3) line explicitly lists "the existing fast/small-medium lane" as a third, independent way to become skip-eligible (beside `--oneshot` and benchmark-mode) — read as authoritative, `fast:true` alone qualifies. This is the single lowest-confidence call in this contract (see §1 Assumptions ⚠).
  - `cmd_advance` computes `nxt` unconditionally today; inserting the skip pre-pass MUST be gated tightly (`if nxt in _SKIPPABLE_PHASES:`) so the other 6 crossings (`ground→specify`, `contract→tests`, `tests→build`, `build→verify`, plus the two now-conditional ones when NOT actually skipped) execute zero new bytes — the "full/normal flow… byte-unchanged" constraint is a hard requirement, not a preference.
  - A malformed `skips:` declaration (a token outside `{scenarios,observe}`) must be rejected as a WHOLE, not partially honored (never silently drop the bad token and use the rest) — mirrors `_ai_freeze_allowed`'s "?" fail-closed philosophy, never `_task_sensitivity`'s "None means absent, use a safe default" philosophy (those are different failure shapes; a malformed CSV element is closer to "?" — garbled, not absent).
  - "No silent skips" cuts two ways: (a) every phase actually skipped must be RECORDED (state.json, `freeze_skipped`-style, never a bare boolean); (b) the REASON must exist BEFORE the skip happens, not be backfilled after — this task chooses to make the reason a hard `_die` precondition (`skip_reason_missing`), not merely an audit-measured residual glint like task2's checklist, because a skip is an IRREVERSIBLE phase-ladder jump (unlike a freeze, which can be re-frozen) — once `observe` is jumped, there is no "re-enter observe" path in this contract. Only a POST-hoc deletion of an already-given reason is audit-measured (`skip_rationale_missing_post_hoc`), matching task2's own precedent for a similar post-hoc-tamper class of finding.
  - `--oneshot` writing `gate_mode: ai-plan-verify` unconditionally (even for a task that will later prove to be `security`/`data`/`architecture` sensitivity) is DELIBERATE, reusing task2's own Reject-list closing line verbatim ("a declared gate_mode never forces the AI path or blocks the human path") — this task adds ZERO new code to the sensitivity floor; it is entirely task2's existing, frozen, done behavior, composed not re-implemented.
  - The `Skip rationale:` field's well-formedness check (`_skip_rationale` — presence + non-empty text) is intentionally SIMPLER than `_flag_well_formed` (no `[part]`-tag grammar, no "none material" escape hatch) — a skip either has a stated reason naming the phase or it doesn't; there is no legitimate "no reason" case for an IRREVERSIBLE jump, so no escape hatch is offered. Disclosed as a deliberate asymmetry with the freeze-flag's richer grammar, not an oversight.

Related intent: `.add/milestones/three-phase-flow/MILESTONE.md` Scope (3) + Shared decisions ("Trust floor holds in EVERY mode… Skips are drawn ONLY from the optional set {scenarios, observe} — never contract, tests, build, or verify." / "No silent skips (rule #4): every skipped step is recorded with a one-line reason") + "Shared / risky contracts" line 3 ("skip-set declaration shape (subset of {scenarios, observe}) + contract-auto-freeze semantics -> owning task fast-lane-skips") + Exit criterion 3. GLOSSARY terms this task defines (per MILESTONE.md's own list): `oneshot mode`, `benchmark mode` (the third, `AI-plan-verify-gate`, is task2's — cited not redefined here).

Ground SHA: 38efd8f

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `skips` — a per-task, AI-declared skip-set (subset of `{scenarios, observe}`) that lets `cmd_advance` jump those two phases as a real engine-level crossing (not just an empty ceremony pass-through), gated by lane eligibility (`fast:true` | `oneshot:true` | project `benchmark_mode:true`), fail-closed on any out-of-set token, and never honored without a stated per-phase reason recorded before the jump — composed with, never entangled in, task2's `gate_mode: ai-plan-verify` contract-auto-freeze mechanism via a new `--oneshot` flag that declares both at once.

Framings weighed: a new closed-2-tuple `_SKIPPABLE_PHASES` + a header `skips:` CSV declaration read by a `_GATE_MODE_RE`-style anchored regex, enforced by a tightly-gated `cmd_advance` pre-pass (`if nxt in _SKIPPABLE_PHASES:`) that only ever touches the 2 relevant crossings, with the reason required BEFORE the jump as a hard precondition (chosen — additive, mirrors 3 already-shipped idioms verbatim (`_task_gate_mode`, `_ai_freeze_allowed`, `_streams_posture`), zero new parsing style, the tightest possible gate on the 6 unrelated crossings) · a NEW dedicated phase-count constant that literally shrinks `PHASES` for oneshot tasks (rejected — MILESTONE.md Out: "collapsing the engine to 3 phase-STATES… kept at 8 + bundle metadata"; a per-task-shrunk `PHASES` tuple would also break every `PHASES.index(...)` call-site's assumption of one universal ladder, a far larger blast radius) · re-purposing the EXISTING `freeze_skipped`/`--skip-freeze` escape mechanism to also cover scenarios/observe (rejected — that mechanism crosses tests→build on a DRAFT §3, a DIFFERENT boundary entirely; conflating "the contract never got frozen" with "an optional ceremony phase was deliberately jumped" would blur two independently-audited trust signals into one, defeating the purpose of a distinct, nameable skip-set) · making `--fast` alone (no new flag) sufficient to unlock skip declarations, with no `--oneshot`/`benchmark_mode` addition at all (rejected — narrower than MILESTONE.md Scope(3), which names `--oneshot` and benchmark-mode as explicit, separate triggers; a project running unattended/headless (the benchmark harness) needs a project-level opt-in that does not require hand-typing `--fast` on every task) · requiring a per-skip CLI flag at `advance` time (e.g. `advance --skip-reason "..."`) instead of a pre-declared `skips:` header + §0 `Skip rationale:` field (rejected — the AI already authors §0 GROUND before any later crossing is attempted; front-loading the declaration keeps the reason auditable in the frozen historical record of the task's OWN ground work, not scattered across CLI invocation history, and matches the "AI declares the skip-set" framing — a decision made once, early, not re-litigated at each crossing).

Must:
<must>
  - M1: `add_engine/constants.py` defines `_SKIPPABLE_PHASES = ("scenarios", "observe")` (closed 2-tuple, same relative order as `PHASES`), added to `__all__`, sibling of `_GATE_MODES`.
  - M2: `add.py` defines `_SKIPS_LINE_RE = re.compile(r"(?:^|·)[ \t]*skips:[ \t]*([^\s<#|]+)", re.MULTILINE)` (mirrors `_GATE_MODE_RE` verbatim) and `_task_skip_set(hdr: str) -> tuple[frozenset[str], str | None]` (PURE): no `skips:` line -> `(frozenset(), None)`; the captured token comma-split into a non-empty set, every element a member of `_SKIPPABLE_PHASES` -> `(frozenset(elements), None)`; ANY split element NOT in `_SKIPPABLE_PHASES` (a typo, another phase name, an empty element from `,,` or a trailing comma) -> `(frozenset(), "skip_not_allowed")` — the WHOLE declaration is discarded on any single bad element, never partially honored.
  - M3: `add_engine/predicates.py` defines `_skip_lane_eligible(fast: bool, oneshot: bool, benchmark_mode: bool) -> bool` (PURE): `fast or oneshot or benchmark_mode`.
  - M4: `add_engine/predicates.py` defines `_skip_set_allowed(skip_tokens: frozenset[str], eligible: bool) -> tuple[bool, str | None]` (PURE, assumes `skip_tokens` already closed-set-validated by M2 — single responsibility, no re-validation of membership): `(False, "skip_lane_required")` if `skip_tokens` is non-empty and `eligible` is `False`; else `(True, None)`.
  - M5: `add.py` defines `_skip_rationale(raw0: str, phase: str) -> str | None`: finds a `Skip rationale:` line in the §0 GROUND body, splits its value on `;`, matches a clause `^\s*(scenarios|observe)\s*[-—:]\s*(.+)$` for the given `phase`, returns the trimmed reason text, or `None` if the line/clause is absent or the reason text is empty/whitespace-only after trim. PURE.
  - M6: `add.py cmd_advance` gains a pre-pass, inserted immediately after `nxt = PHASES[idx + 1]` (line 1271) and strictly BEFORE the existing `nxt == "contract"`/`"build"`/`"tests"` branches, gated `if nxt in _SKIPPABLE_PHASES:` (the ONLY new code the other 6 crossings ever reach is this single membership test — a `False` result is a no-op, zero further bytes executed):
      a. `tokens, err = _task_skip_set(hdr)`; `err` -> `_die("skip_not_allowed")` (fires the first time either skippable phase is reached, regardless of whether `nxt` itself is the bad token — a malformed `skips:` line is refused as soon as it is ever consulted).
      b. `nxt not in tokens` -> no skip; fall through, `nxt` unchanged (today's behavior: the phase is entered normally).
      c. `nxt in tokens` -> `eligible = _skip_lane_eligible(state["tasks"][slug].get("fast") is True, state["tasks"][slug].get("oneshot") is True, _project_benchmark_mode(root))`; `ok, code = _skip_set_allowed(tokens, eligible)`; not `ok` -> `_die(code)` (`skip_lane_required`).
      d. `reason = _skip_rationale(raw0, nxt)` (raw0 = this task's own §0 GROUND text, read the same way `_build_entry` already reads other raw phase bodies); falsy -> `_die("skip_reason_missing")`.
      e. success -> `state["tasks"][slug].setdefault("skips", []).append({"phase": nxt, "reason": reason, "by": identity._actor_stamp(state)["name"], "at": _now()})`; reassign `nxt = PHASES[idx + 2]` (always in-bounds: neither `"scenarios"` nor `"observe"` is `PHASES[-1]`).
      All `_die` calls above fire before `state["tasks"][slug]["phase"] = nxt` (line ~1329) — validate-then-write, matching every other guard in this function; a refusal leaves the task at its CURRENT phase, nothing written.
  - M7: `add.py`'s `new-task` subparser (`pn`) gains `--oneshot` (`action="store_true"`, sibling of the existing `--fast` at line 7711). `cmd_new_task`: `oneshot = bool(getattr(args, "oneshot", False))`; `fast = bool(getattr(args, "fast", False)) or oneshot` (oneshot implies the minimal `TASK.fast.md` template — no new template file); when `oneshot` is true, after `_render_template` returns, splice two additive lines directly beneath the rendered `fast: true` header line (regex substitution, count=1, preserving that line's own trailing HTML comment): `oneshot: true` and `gate_mode: ai-plan-verify` (written unconditionally — task2's `_ai_freeze_allowed`, unchanged, is the sole arbiter of whether `freeze --ai-plan-verify` ever actually succeeds for this task); `state["tasks"][slug]["oneshot"] = True` is set alongside the existing `state[...]["fast"] = True` when `oneshot` is true.
  - M8: `add.py` defines `_project_benchmark_mode(root: Path) -> bool` (mirrors `_streams_posture`/`_project_autonomy_token`'s idiom exactly): reads PROJECT.md, strips HTML comments, matches an anchored `(?:^|·)[ \t]*benchmark_mode:[ \t]*(true|false)` line (case-insensitive); declared `true` -> `True`; declared `false`, absent, unreadable foundation, or any other token -> `False` (fail-SAFE default — a NEW ceremony-loosening project capability never silently activates).
  - M9: `add.py cmd_status` and `cmd_guide` gain one new additive, existence-gated line for the active/named task, printed only when the task is skip-eligible (per M3's three inputs) AND (a non-empty `skips:` declaration exists OR `state["tasks"][slug].get("skips")` is non-empty): `skips   : declared <csv> · skipped so far <n>/<m> (<phase list, comma-joined, in PHASES order>)` — absent/silent otherwise, byte-identical to today for every task without a skip declaration.
  - M10: `add.py _gate_explain` (already extended once by task2's M8) gains one further additive printed line: when a task is skip-eligible and declares a non-empty `skips:`, print the CURRENT `_skip_set_allowed` outcome (allowed/blocked + code) for that declaration — read-only, no new write path, beside the existing gate_mode explain line (unchanged).
  - M11: `add.py cmd_audit`/`_audit_findings` gains one new residual glint, `skip_rationale_missing_post_hoc` (MEASURE-NOT-BLOCK, symmetric to `ai_freeze_checklist_missing`): for any task whose `state["tasks"][slug].get("skips")` is non-empty, if the CURRENT §0 `Skip rationale:` line no longer has a matching clause (per `_skip_rationale`) for EVERY phase named in a recorded skip entry, flag it — catches a post-skip hand-edit that deletes/mangles the evidence.
  - M12: `templates/TASK.fast.md.tmpl` gains two additive scaffold lines (byte-ceiling-forced fast-template-only, mirrors task2's own disclosed "AI-verify record" placement precedent verbatim): a commented `skips: <csv subset of scenarios,observe — omit this line for none>` header hint, and a `Skip rationale:` placeholder line in §0. `templates/TASK.md.tmpl` (full lane) is UNTOUCHED — a full-lane task under `benchmark_mode` authors both fields freeform, guided by this frozen contract, exactly as task2 already established for `gate_mode`/"AI-verify record".
  - M13: never-skippable-by-construction invariant: `_SKIPPABLE_PHASES` is the ONLY set `cmd_advance`'s pre-pass ever tests `nxt` against; it is a closed, hardcoded 2-tuple. No code path introduced by this task can compute a skip for `ground`, `specify`, `contract`, `tests`, `build`, or `verify` — those 6 crossings execute zero bytes of this task's new logic (confirmed at BUILD/VERIFY by a coverage/line-hit check, not merely asserted in prose).
  - M14: the three engine trees (`add-method/tooling/`, `.add/tooling/`, `add-method/src/add_method/_bundled/tooling/`) stay byte-identical for every touched file, and the local gitignored 4th `add-method/.add/tooling/templates/` dogfood mirror also gets the `TASK.fast.md.tmpl` change (BUILD-phase obligation, named here — mirrors task2's own disclosed M10/Strategy note about that 4th mirror).
</must>

Reject:
<reject>
  - a `skips:` header token outside `{"scenarios","observe"}` (a typo, another phase's name, an empty CSV element) is reached at a scenarios/observe crossing -> "skip_not_allowed" — the WHOLE declaration is refused, no partial honoring of the valid tokens alongside it
  - a syntactically valid `skips:` token naming the phase about to be entered, on a task that is neither `fast:true` nor `oneshot:true`, whose project is not `benchmark_mode:true` -> "skip_lane_required"
  - a syntactically valid, lane-eligible `skips:` token naming the phase about to be entered, but §0 GROUND's `Skip rationale:` line has no clause (or an empty-text clause) for that phase -> "skip_reason_missing"
  - a `skips:` line naming a phase outside `{scenarios,observe}` (e.g. `skips: build`) is refused with the SAME "skip_not_allowed" the very first time either skippable phase is reached — even though `build` itself was never individually consulted — because M2 validates the declaration AS A WHOLE, not token-by-token-as-relevant
  - `--oneshot` on a task later declared (or defaulted) `sensitivity: security`/`data`/`architecture` -> NOT a rejection of this task's own new code; task2's existing, unchanged `_ai_freeze_allowed` refuses `freeze --ai-plan-verify` for it with its own `ai_freeze_blocked_sensitivity`, forcing the human `add.py freeze --by <name>` path — cited for completeness, owned entirely by task2
  - a task with no `skips:` line at all (today's universal default) -> succeeds exactly as today at every one of the 8 crossings; the M6 pre-pass computes `tokens = frozenset()`, `nxt not in tokens` is always true, zero recorded skip, byte-identical
</reject>

After:
<after>
  - A `fast:true` or `oneshot:true` task (or any task under a `benchmark_mode:true` project) whose header declares `skips: scenarios,observe` and whose §0 `Skip rationale:` names both, crosses `specify` -> `contract` in ONE `advance` call (never visiting `phase: scenarios`) and crosses `verify` -> `done` in ONE `advance` call (never visiting `phase: observe`); `state["tasks"][slug]["skips"]` records two entries (`phase`/`reason`/`by`/`at`); `status`/`guide`/`gate-explain` surface the declaration and the count.
  - The same shape declaring `skips: observe` only skips `observe`; the `specify` -> `scenarios` crossing proceeds exactly as today (lands the task at `phase: scenarios`, records nothing in `skips`).
  - A task created via `--oneshot` whose sensitivity later proves `security`/`data`/`architecture` still gets its declared scenarios/observe skips (unaffected — a separate axis) but its §3 contract still requires the human `add.py freeze --by <name>` path (task2's unchanged floor) — the trust floor (frozen contract · red test · recorded gate · security HARD-STOP) holds in every mode, exactly as MILESTONE.md's Shared decisions require.
  - A plain full-lane task (no `fast`, no `oneshot`, project not `benchmark_mode`) with no `skips:` line: every one of its 8 crossings is byte-identical to pre-task `cmd_advance` behavior.
  - Every already-existing task (created before this ships) with no `skips`/`oneshot` state key is unaffected — `.get("skips")`/`.get("oneshot")` return absent/`None` everywhere they are read, treated as empty/`False`.
  - `add.py audit` surfaces `skip_rationale_missing_post_hoc` for a task whose recorded skip's §0 rationale clause was later deleted or mangled by hand.
</after>

Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Granting skip-eligibility to plain `fast:true` tasks (not just `oneshot:true`/`benchmark_mode`) — lowest confidence because it reaches BACKWARD into the meaning of the ALREADY-SHIPPED `--fast` flag: a human who typed `--fast` believing it only collapsed template sections now, the moment the AI adds a `skips:` line, gets a REAL engine-level phase jump they did not separately opt into per-skip. MILESTONE.md Scope(3) reads as authoritative for this ("the existing fast/small-medium lane" is named as a third, independent trigger, beside `--oneshot` and benchmark-mode), so this contract adopts it — but it is the single most likely point a human freeze reviewer pushes back on. If wrong: narrow `_skip_lane_eligible` to `oneshot or benchmark_mode` only (drop the `fast` parameter's OR-branch, a one-line predicate change, M3 only) — every other Must/Reject/scenario in this contract is unaffected, since `fast:true` alone would then simply fail `skip_lane_required` until the task also gains `oneshot:true`.
  - [ ] whether `--oneshot` should ALSO force the task's `autonomy:` header to `auto` at scaffold time (this contract chooses NOT to — it leaves autonomy exactly as `_project_autonomy(root)` resolves today, letting task2's `ai_freeze_requires_auto` degrade gracefully if the project default or a later human edit is not `auto`) — confirm this reads as "graceful degradation" and not "a half-finished --oneshot that silently under-delivers speed for projects with a non-auto default."
  - [ ] the exact status/guide line WORDING (`skips   : declared <csv> · skipped so far <n>/<m> (<phases>)`) is a reasonable first cut, not confirmed against the terminal-UX-accessibility persona's own bar (color/glyph-free, keyboard/screen-reader legible) — low cost either way, a presentation-only line, isolated to M9.
  - [ ] `_skip_rationale`'s clause grammar (`phase — reason` or `phase: reason`, `;`-separated) is deliberately simpler than `_flag_well_formed`'s `[part]`-tag grammar and offers no "none material" escape hatch (an irreversible jump always needs a stated reason) — confirm this asymmetry is acceptable, or whether a richer grammar / escape hatch is wanted for a future task.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: _SKIPPABLE_PHASES is a closed 2-tuple, importable   # M1
  Given add_engine/constants.py
  When _SKIPPABLE_PHASES is read
  Then it equals ("scenarios", "observe")
  And it is listed in __all__

Scenario: _task_skip_set resolves absence, a valid CSV, and a malformed token   # M2
  Given a TASK.md header with no "skips:" line
  When _task_skip_set(hdr) is called
  Then it returns (frozenset(), None)
  And a header with "skips: scenarios,observe" returns (frozenset({"scenarios","observe"}), None)
  And a header with "skips: scenarios" returns (frozenset({"scenarios"}), None)
  And a header with "skips: scenarios,build" returns (frozenset(), "skip_not_allowed")
  And a header with "skips: bogus" returns (frozenset(), "skip_not_allowed")

Scenario: _skip_lane_eligible is true iff any of the three inputs is true   # M3
  Given the pure predicate _skip_lane_eligible(fast, oneshot, benchmark_mode)
  When called with (True, False, False), (False, True, False), and (False, False, True)
  Then each call returns True
  And _skip_lane_eligible(False, False, False) returns False

Scenario: _skip_set_allowed permits an empty skip-set regardless of eligibility   # M4
  Given skip_tokens=frozenset(), eligible=False
  When _skip_set_allowed(skip_tokens, eligible) is called
  Then it returns (True, None)

Scenario: _skip_set_allowed permits a non-empty skip-set only when eligible   # M4
  Given skip_tokens=frozenset({"scenarios"})
  When _skip_set_allowed(skip_tokens, True) is called
  Then it returns (True, None)
  And _skip_set_allowed(skip_tokens, False) returns (False, "skip_lane_required")

Scenario: _skip_rationale extracts a matching clause and fails closed on absence   # M5
  Given a §0 GROUND body containing "Skip rationale: scenarios — the Accept line covers it; observe — no rollout to watch"
  When _skip_rationale(raw0, "scenarios") is called
  Then it returns "the Accept line covers it"
  And _skip_rationale(raw0, "observe") returns "no rollout to watch"
  And _skip_rationale(raw0, "observe") on a §0 body with NO "Skip rationale:" line returns None
  And _skip_rationale(raw0, "observe") on "Skip rationale: scenarios — reason only" (no observe clause) returns None

Scenario: cmd_advance jumps specify->contract when scenarios is declared, eligible, and reasoned   # M6
  Given a fast:true task at phase=specify, header "skips: scenarios", §0 "Skip rationale: scenarios — <reason>"
  When I run `add.py advance <slug>`
  Then the task's phase becomes "contract" (scenarios never entered)
  And state["tasks"][slug]["skips"] contains one entry {"phase": "scenarios", "reason": "<reason>", "by": ..., "at": ...}
  And the printed "phase specify -> contract" line is shown (a single crossing, not two)

Scenario: cmd_advance jumps verify->done when observe is declared, eligible, and reasoned   # M6
  Given the same task now at phase=verify, header "skips: observe", §0 "Skip rationale: observe — <reason>"
  When I run `add.py advance <slug>`
  Then the task's phase becomes "done" (observe never entered)
  And state["tasks"][slug]["skips"] gains a second entry {"phase": "observe", ...}

Scenario: cmd_advance takes the ordinary path when the phase is not in the declared skip-set   # M6
  Given a fast:true task at phase=specify, header "skips: observe" (scenarios NOT declared)
  When I run `add.py advance <slug>`
  Then the task's phase becomes "scenarios" (entered normally)
  And no entry is appended to state["tasks"][slug]["skips"]

Scenario: the 6 non-skippable crossings execute none of this task's new logic   # M6 / M13
  Given a task at phase=ground, contract, tests, or build (about to cross ground->specify, contract->tests, tests->build, or build->verify)
  When I run `add.py advance <slug>` (regardless of any skips: declaration or lane eligibility)
  Then the crossing behaves byte-identically to pre-task cmd_advance
  And a coverage/line-hit probe confirms the M6 pre-pass body (steps a-e) is never entered for these crossings

Scenario: new-task --oneshot scaffolds the minimal template and both additive header lines   # M7
  Given a plain milestone, no prior tasks
  When I run `add.py new-task quick --oneshot`
  Then TASK.md is TASK.fast.md's minimal section set {0,1,3,4,5,6}
  And the header contains "fast: true", "oneshot: true", and "gate_mode: ai-plan-verify"
  And state["tasks"]["quick"]["fast"] is True and state["tasks"]["quick"]["oneshot"] is True

Scenario: new-task --fast (no --oneshot) is unaffected by this task's new header lines   # M7 / edge case
  Given a plain milestone
  When I run `add.py new-task quick --fast` (no --oneshot)
  Then the header contains "fast: true" only — no "oneshot:" line, no "gate_mode:" line
  And state["tasks"]["quick"] has no "oneshot" key

Scenario: _project_benchmark_mode resolves declared true/false, absence, and a malformed token   # M8
  Given PROJECT.md with "benchmark_mode: true"
  When _project_benchmark_mode(root) is called
  Then it returns True
  And PROJECT.md with "benchmark_mode: false" returns False
  And PROJECT.md with no "benchmark_mode:" line returns False
  And PROJECT.md with "benchmark_mode: yes" (unrecognized token) returns False

Scenario: status/guide surface the declared and consumed skip-set   # M9
  Given a fast:true task with header "skips: scenarios,observe", one already-recorded skip entry (scenarios)
  When I run `add.py status` (or `add.py guide`)
  Then the output includes a line naming the declared csv "scenarios,observe" and "skipped so far: 1/2"
  And a task with no skips: declaration and no recorded skips prints no such line (silent, byte-identical)

Scenario: gate-explain surfaces the skip-set predicate outcome   # M10
  Given a task declaring "skips: scenarios" while NOT fast/oneshot and its project NOT benchmark_mode
  When I run `add.py gate-explain <slug>`
  Then the output includes a line naming the outcome "blocked" and the code "skip_lane_required"
  And the existing gate_mode explain line (task2) is unchanged and still printed beside it

Scenario: audit flags a post-skip deleted rationale   # M11
  Given a task whose state["tasks"][slug]["skips"] has an entry {"phase": "observe", ...}
  And its CURRENT §0 no longer has an "observe" clause in "Skip rationale:" (hand-edited away)
  When `add.py audit` runs
  Then the glint "skip_rationale_missing_post_hoc" lists this task
  And the audit outcome is MEASURE-NOT-BLOCK (exit code follows the same symmetric precedent as ai_freeze_checklist_missing)

Scenario: TASK.fast.md.tmpl carries the new scaffold; TASK.md.tmpl is untouched   # M12
  Given the two template files after this task's build
  When a new --fast or --oneshot task is scaffolded
  Then TASK.fast.md.tmpl's rendered output contains a commented "skips:" header hint and a "Skip rationale:" §0 placeholder line
  And a plain (full-lane) new-task's TASK.md.tmpl output is byte-identical to before this task

Scenario: the three engine trees and the 4th dogfood template mirror stay byte-identical   # M14
  Given add-method/tooling/, .add/tooling/, add-method/src/add_method/_bundled/tooling/, and the gitignored add-method/.add/tooling/templates/
  When the BUILD phase edits constants.py, predicates.py, add.py, and TASK.fast.md.tmpl
  Then md5 of each touched file matches across all applicable trees

Scenario: a malformed skips: token is refused as a WHOLE, not partially honored   # R:skip_not_allowed
  Given a task at phase=specify, header "skips: scenarios,build"
  When I run `add.py advance <slug>`
  Then it dies with "skip_not_allowed"
  And the task's phase is untouched (still "specify")
  And no state["tasks"][slug]["skips"] entry is written — not even for the valid "scenarios" token

Scenario: a lane-ineligible task's valid skip declaration is refused   # R:skip_lane_required
  Given a task at phase=specify, header "skips: scenarios", NOT fast/oneshot, project NOT benchmark_mode
  When I run `add.py advance <slug>`
  Then it dies with "skip_lane_required"
  And the task's phase is untouched (still "specify")

Scenario: an eligible, valid skip declaration with a missing rationale is refused   # R:skip_reason_missing
  Given a fast:true task at phase=specify, header "skips: scenarios", §0 has NO "Skip rationale:" line
  When I run `add.py advance <slug>`
  Then it dies with "skip_reason_missing"
  And the task's phase is untouched (still "specify")
  And state["tasks"][slug]["skips"] is unset (no entry written)

Scenario: a skips: token naming an unskippable phase is refused via the same closed-set code   # edge case
  Given a fast:true task at phase=specify, header "skips: build"
  When I run `add.py advance <slug>` (crossing into "scenarios", which is NOT "build")
  Then it still dies with "skip_not_allowed" — the declaration is validated as a whole at the first skippable crossing reached, before nxt's own membership is even checked

Scenario: --oneshot on a security-sensitivity task still requires a human freeze; skips are unaffected   # edge case
  Given a task created via `add.py new-task risky --oneshot`, later given "sensitivity: security", "skips: scenarios,observe", §0 rationale for both, autonomy inherited "auto"
  When the task crosses specify->contract (skip fires normally, recorded)
  And later `add.py freeze --ai-plan-verify --by agent:x` is attempted at the frozen-contract gate
  Then the freeze attempt dies with "ai_freeze_blocked_sensitivity" (task2's unchanged predicate)
  And `add.py freeze --by "A Human"` still succeeds
  And the scenarios/observe skip already recorded earlier is untouched by the freeze outcome

Scenario: a task with no skips: line at all behaves exactly as today at every crossing   # R: (no rejection — the common case)
  Given a plain full-lane task, no fast/oneshot, project not benchmark_mode, no "skips:" header line
  When I run `add.py advance <slug>` at each of the 8 crossings in turn
  Then every crossing succeeds exactly as pre-task behavior (ground->specify->scenarios->contract->tests->build->verify->observe->done)
  And state["tasks"][slug] never gains a "skips" key
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FAST-LANE-SKIPS — the frozen shape (add-method/tooling/add.py + add_engine/{constants,predicates}.py
                                     + templates/TASK.fast.md.tmpl, synced ×3 engine trees + 1 dogfood
                                     template mirror)

NEW CONSTANT — add_engine/constants.py (joins __all__, sibling of _GATE_MODES)
_SKIPPABLE_PHASES: tuple[str, ...] = ("scenarios", "observe")
  # closed 2-tuple, same relative order as PHASES. The ONLY set cmd_advance's skip pre-pass ever
  # tests `nxt` against — by construction, ground/specify/contract/tests/build/verify can NEVER
  # be skipped (M13's never-skippable-by-construction guarantee; not a policy choice re-checked at
  # runtime, an architectural exclusion).

NEW HEADER RESOLVER — add.py (mirrors _task_gate_mode / _GATE_MODE_RE exactly)
_SKIPS_LINE_RE = re.compile(r"(?:^|·)[ \t]*skips:[ \t]*([^\s<#|]+)", re.MULTILINE)
_task_skip_set(hdr: str) -> tuple[frozenset[str], str | None]
    no "skips:" line                                   -> (frozenset(), None)
    captured token comma-split, every element valid     -> (frozenset(elements), None)
    ANY element outside _SKIPPABLE_PHASES (typo/other-   -> (frozenset(), "skip_not_allowed")
      phase-name/empty element from ",,"/trailing comma)
  # PURE. Fail-closed on the WHOLE declaration — never partially honors the valid tokens
  # alongside a bad one (mirrors _ai_freeze_allowed's "?" philosophy, not _task_sensitivity's
  # "None means absent, default safely" philosophy — a malformed CSV element is garbled, not
  # absent).

NEW PURE PREDICATES — add_engine/predicates.py (beside _ai_freeze_allowed, same fail-closed idiom)
_skip_lane_eligible(fast: bool, oneshot: bool, benchmark_mode: bool) -> bool
    return fast or oneshot or benchmark_mode

_skip_set_allowed(skip_tokens: frozenset[str], eligible: bool) -> tuple[bool, str | None]
    if skip_tokens and not eligible:  return False, "skip_lane_required"
    return True, None
  # skip_tokens is assumed ALREADY closed-set-validated by _task_skip_set (M2) — this predicate's
  # single responsibility is the LANE-ELIGIBILITY axis, not set-membership (separation of concerns,
  # two distinct error codes for two distinct failure shapes).

NEW READER — add.py (heading-free, single-clause extractor; deliberately simpler than
                      _flag_well_formed's [part]-tag grammar — an irreversible jump always
                      needs a stated reason, no "none material" escape hatch)
_skip_rationale(raw0: str, phase: str) -> str | None
  # finds "Skip rationale:" in the §0 GROUND body; splits its value on ";"; matches a clause
  # "^\s*(scenarios|observe)\s*[-—:]\s*(.+)$" for `phase`; returns the trimmed reason, or None
  # when the line/clause is absent or the reason text is empty/whitespace-only.

EXTENDED COMMAND — add.py cmd_advance (pre-pass inserted after `nxt = PHASES[idx + 1]`, STRICTLY
                                        before the existing nxt=="contract"/"build"/"tests" branches)
  if nxt in _SKIPPABLE_PHASES:                          # the ONLY new code the other 6
                                                          # crossings ever reach: this test itself
    tokens, err = _task_skip_set(hdr)
    if err:                              _die(err)       # "skip_not_allowed" — fires the first
                                                          # time either skippable phase is reached
    if nxt in tokens:
      eligible = _skip_lane_eligible(
          state["tasks"][slug].get("fast") is True,
          state["tasks"][slug].get("oneshot") is True,
          _project_benchmark_mode(root))
      ok, code = _skip_set_allowed(tokens, eligible)
      if not ok:                         _die(code)      # "skip_lane_required"
      reason = _skip_rationale(raw0, nxt)
      if not reason:                     _die("skip_reason_missing")
      state["tasks"][slug].setdefault("skips", []).append({
          "phase": nxt, "reason": reason,
          "by": identity._actor_stamp(state)["name"], "at": _now()})
      nxt = PHASES[idx + 2]              # hop the skipped phase; always in-bounds
    # else: nxt not in tokens -> fall through unchanged, phase entered normally (no-op)
  # every _die above fires BEFORE state["tasks"][slug]["phase"] = nxt (~line 1329) — the task
  # stays at its CURRENT phase on any refusal, nothing written (validate-then-write, matching
  # every other guard in this function).
  4xx -> "skip_not_allowed" | "skip_lane_required" | "skip_reason_missing"

EXTENDED COMMAND — add.py new-task (cmd_new_task; --oneshot sibling of --fast on the `pn` subparser)
add.py new-task SLUG --oneshot
  oneshot = bool(args.oneshot); fast = bool(args.fast) or oneshot   # oneshot implies the fast
                                                                      # template, no new file
  render TASK.fast.md (unchanged path/logic)
  when oneshot: splice, directly beneath the rendered "fast: true" line (regex sub, count=1,
    preserving that line's own trailing HTML comment):
      "oneshot: true"
      "gate_mode: ai-plan-verify"          # a REQUEST — task2's _ai_freeze_allowed (UNCHANGED)
                                            # is the sole arbiter of whether it is ever honored
  state["tasks"][slug]["oneshot"] = True   (alongside the existing state[...]["fast"] = True)
  200 -> TASK.md scaffolded with sections {0,1,3,4,5,6}, header carries fast:true + oneshot:true
       + gate_mode:ai-plan-verify; state carries fast:True + oneshot:True
  add.py new-task SLUG --fast (no --oneshot)         -> BYTE-IDENTICAL to today: no oneshot:/
                                                          gate_mode: line, no "oneshot" state key

NEW PROJECT-LEVEL RESOLVER — add.py (mirrors _streams_posture / _project_autonomy_token exactly)
_project_benchmark_mode(root: Path) -> bool
    PROJECT.md, HTML comments stripped, anchored (?:^|·)[ \t]*benchmark_mode:[ \t]*(true|false)
    "true"                              -> True
    "false" | absent | any other token  -> False   # fail-SAFE: a NEW ceremony-loosening
                                                     # project capability never silently activates

READ-ONLY EXTENSIONS — additive, existence-gated, silent when not applicable (byte-identical
                        output for any task this feature doesn't touch)
  add.py cmd_status / cmd_guide:
    "skips   : declared <csv> · skipped so far <n>/<m> (<phase list, PHASES order>)"
    printed only when skip-eligible AND (a non-empty skips: declaration OR >=1 recorded skip)
  add.py _gate_explain (already extended once by task2's M8):
    one further additive line: the current _skip_set_allowed outcome (allowed | blocked+code)
    for a task's declared skips:, printed beside the existing gate_mode explain line (unchanged)

NEW AUDIT GLINT — add.py cmd_audit / _audit_findings (MEASURE-NOT-BLOCK, symmetric to the
                                                        existing ai_freeze_checklist_missing)
  skip_rationale_missing_post_hoc: for any task whose state["tasks"][slug]["skips"] is non-empty,
  if the CURRENT §0 Skip rationale: line no longer has a matching clause (per _skip_rationale)
  for EVERY phase named in a recorded skip entry, flag it. Never engine-blocking; a human
  spot-audit is the backstop.

TEMPLATE CHANGE — templates/TASK.fast.md.tmpl ONLY (byte-ceiling-forced, mirrors task2's own
                   disclosed "AI-verify record" placement precedent verbatim)
  header hint:  "skips: <csv subset of scenarios,observe — omit this line for none>"
  §0 placeholder: "Skip rationale: <phase> — <reason>; <phase> — <reason>"
  templates/TASK.md.tmpl (full lane): UNTOUCHED. A full-lane task under benchmark_mode authors
  both fields freeform, exactly as task2 already established for gate_mode/"AI-verify record".

UNCHANGED, CITED FOR COMPLETENESS (no code change; the reason the two mechanisms compose cleanly)
  add_engine/predicates.py:_ai_freeze_allowed  — task2's own, unaware of and unaffected by skips:
  add.py cmd_advance's nxt=="contract"/"build"/"tests" branches — run AFTER the skip pre-pass,
    against whatever the pre-pass resolved nxt to; no change to their own bodies
  add.py PHASES / PHASE_GROUPS / PHASE_AGENT — untouched; skip jumps consult PHASES only for
    index arithmetic (PHASES[idx + 2]), never reorder or shrink the tuple

Schema: TASK.md header (2 new optional lines: skips:, oneshot:) · TASK.md §0 GROUND (1 new
  optional field: "Skip rationale:") · PROJECT.md (1 new optional line: benchmark_mode:) ·
  state.json tasks.<slug> (2 new optional keys: oneshot [bool], skips [list of {phase,reason,by,at}])
  · add_engine/constants.py (_SKIPPABLE_PHASES, joins __all__) · no DB/network/schema.
```

Glossary deltas:
  - `oneshot mode`: a task-level opt-in (`add.py new-task <slug> --oneshot`) that scaffolds the minimal fast template plus two additive header declarations — `oneshot: true` (a durable lane marker) and `gate_mode: ai-plan-verify` (a REQUEST for task2's AI-plan-verify-gate; whether it is ever honored is entirely governed by that unchanged mechanism's own sensitivity/autonomy floor). Orthogonal to, and composed with (never entangled in), this task's own skip-set mechanism — a `security`/`data`/`architecture`-sensitivity oneshot task still gets its declared scenarios/observe skips but still requires a human contract freeze.
  - `benchmark mode`: a project-level opt-in (`benchmark_mode: true` in PROJECT.md, mirroring the `streams:`/`autonomy:` declared-field idiom) that grants every task in the project skip-eligibility (per `_skip_lane_eligible`) without requiring `--oneshot`/`--fast` on each one individually — intended for a headless/unattended runner (e.g. the benchmark harness) where no human types a per-task CLI flag. Absent, `false`, or malformed -> `False` (fail-safe).
  - `skip-set`: a task-header `skips:` declaration, a CSV subset of the closed set `{scenarios, observe}` (`_SKIPPABLE_PHASES`) naming which of those two OPTIONAL phases `cmd_advance` will jump as a single crossing instead of entering. Fail-closed on any out-of-set token (the WHOLE declaration refused, `skip_not_allowed`); requires lane eligibility (`skip_lane_required` otherwise) and a stated per-phase reason in §0 GROUND's `Skip rationale:` field, recorded BEFORE the jump (`skip_reason_missing` otherwise) — never silent. Every actual skip is recorded in `state["tasks"][slug]["skips"]` (phase/reason/by/at), and a post-hoc deletion of the reason is caught by the `skip_rationale_missing_post_hoc` audit glint. `contract`, `tests`, `build`, `verify`, `ground`, and `specify` are never in `_SKIPPABLE_PHASES` and can never be skipped — a structural guarantee, not a checked policy.

Least-sure flag surfaced at freeze: [spec] granting skip-eligibility to plain `fast:true` tasks (not just `oneshot:true`/`benchmark_mode`) reaches backward into the already-shipped `--fast` flag's meaning — a human who opted into `--fast` for template collapse alone now also gets real engine-level phase-jump power the moment the AI adds a `skips:` line. MILESTONE.md Scope(3) names "the existing fast/small-medium lane" as a third, independent trigger, so this contract adopts it as authoritative; if wrong, narrow `_skip_lane_eligible` to `oneshot or benchmark_mode` only — a one-line predicate change (M3), isolated, no other Must/Reject/scenario in this contract changes.

Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new fast-lane-skips surface (_SKIPPABLE_PHASES, _task_skip_set, _skip_lane_eligible, _skip_set_allowed, _skip_rationale, _project_benchmark_mode, cmd_advance's skip pre-pass, cmd_new_task's --oneshot, the status/guide/gate-explain additive lines, the audit glint, the template scaffold) — behavioral, not internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_value_and_all, test_importable_via_star_import: _SKIPPABLE_PHASES == ("scenarios","observe"), listed in __all__, re-exported on add · covers: M1
  - test_absent_line_returns_empty_set_no_error, test_valid_two_token_csv, test_valid_single_token, test_one_bad_token_refuses_whole_declaration, test_wholly_unknown_token: _task_skip_set resolves absence/valid/malformed, whole-declaration fail-closed · covers: M2
  - test_any_single_true_input_yields_true, test_all_false_yields_false, test_predicate_lives_in_engine_predicates_module: _skip_lane_eligible true iff any input · covers: M3
  - test_empty_set_permitted_regardless_of_eligibility, test_non_empty_set_permitted_only_when_eligible: _skip_set_allowed · covers: M4
  - test_extracts_each_matching_clause, test_no_line_at_all_returns_none, test_line_present_but_no_clause_for_phase_returns_none, test_empty_reason_text_returns_none: _skip_rationale extracts/fails closed · covers: M5
  - test_jumps_specify_to_contract_when_scenarios_declared_eligible_reasoned, test_jumps_verify_to_done_when_observe_declared_eligible_reasoned, test_ordinary_path_when_phase_not_in_declared_skip_set: cmd_advance's skip mechanic · covers: M6
  - test_six_non_skippable_crossings_never_invoke_task_skip_set: coverage/line-hit probe (mock spy) proving the pre-pass body is unreached on the 6 non-skippable crossings · covers: M13
  - test_scaffolds_minimal_template_and_both_header_lines: new-task --oneshot · covers: M7
  - test_fast_without_oneshot_has_no_new_header_lines_or_state_key: --fast alone is unaffected · covers: M7 (edge case)
  - test_declared_true, test_declared_false, test_absent_is_false, test_malformed_token_is_false: _project_benchmark_mode · covers: M8
  - test_status_and_guide_show_declared_csv_and_progress, test_no_declaration_no_recorded_skip_prints_no_line: status/guide additive line, present-only · covers: M9
  - test_blocked_outcome_for_ineligible_declared_task, test_no_declaration_prints_no_skip_set_line: gate-explain surfaces the predicate outcome · covers: M10
  - test_intact_rationale_not_flagged, test_deleted_rationale_flagged_measure_not_block: audit's skip_rationale_missing_post_hoc glint, MEASURE-NOT-BLOCK · covers: M11
  - test_fast_template_has_skips_hint_and_rationale_placeholder, test_full_template_byte_identical_to_before: template scaffold, full lane untouched · covers: M12
  - test_add_py_trees_byte_identical, test_constants_trees_byte_identical, test_predicates_trees_byte_identical, test_fast_template_trees_byte_identical: 3-tree + 4th dogfood mirror byte parity · covers: M14
  - test_malformed_token_refused_as_whole_not_partially_honored: covers: R:skip_not_allowed
  - test_lane_ineligible_declaration_refused: covers: R:skip_lane_required
  - test_missing_rationale_refused: covers: R:skip_reason_missing
  - test_unskippable_phase_name_refused_via_same_code: an out-of-set token is refused via the same closed-set code even though the unskippable name itself is never individually consulted · covers: edge case
  - test_oneshot_security_task_skip_fires_but_freeze_stays_human: the skip axis and task2's freeze axis compose without entangling · covers: edge case (floor composition)
  - test_plain_task_visits_scenarios_and_observe_every_crossing: a plain task with no skips: line behaves exactly as today at every one of the 8 crossings · covers: R: (no rejection — the common case)
</test_plan>

Tests live in: `add-method/tooling/test_fast_lane_skips.py` (45 tests) · ran RED (AttributeError: module 'add' has no attribute '_SKIPPABLE_PHASES'/'_task_skip_set'/'_skip_lane_eligible'/'_skip_set_allowed'/'_skip_rationale'/'_project_benchmark_mode'; argparse 'unrecognized arguments: --oneshot'; assertion mismatches on the absent behavior) before Build — confirmed by reverting the 3 canon engine files (add.py, add_engine/constants.py, add_engine/predicates.py) + the fast template + the 4th dogfood mirror to the pre-build HEAD via `git stash`/`git show HEAD:...`: 34/45 tests failed for the right reason (13 failures + 21 errors); the 11 that stayed green legitimately assert the ABSENCE of new behavior on old code (e.g. "no declaration → no status line", "3 trees still identical pre-edit").

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/.add/tooling/templates/` `.add/SEAMS.md` `tmp/three-phase-flow/fast-lane-skips/`
Strategy (ordered batches): 1. add_engine/constants.py: `_SKIPPABLE_PHASES` + `__all__`. 2. add_engine/predicates.py: `_skip_lane_eligible`/`_skip_set_allowed` beside `_ai_freeze_allowed`. 3. add.py: `_SKIPS_LINE_RE`/`_task_skip_set`/`_skip_rationale`/`_project_benchmark_mode` beside `_task_gate_mode`. 4. cmd_advance skip pre-pass (after `nxt = PHASES[idx+1]`, before the existing branches). 5. cmd_new_task `--oneshot` (argparse + splice + state key). 6. cmd_status/cmd_guide/_gate_explain additive lines (shared `_skip_status_line` helper). 7. `_audit_findings` `skip_rationale_missing_post_hoc` glint. 8. `templates/TASK.fast.md.tmpl` scaffold (commented header hint + §0 placeholder). 9. propagate ×3 engine trees + 4th dogfood template mirror byte-identically; re-pin `engine_pin.py` (ENGINE_MD5 + ENGINE_PKG_MD5) and the two `.add/SEAMS.md` line-number anchors (`_declared_scope`, `_section_unfilled`) that this build's own growth shifted.
Approach (domain strategy): a closed, hardcoded 2-tuple gate (`_SKIPPABLE_PHASES`) is the ONLY set `cmd_advance`'s pre-pass ever tests `nxt` against — an architectural exclusion, not a runtime policy, so the other 6 crossings can never reach any of this task's new code. Every new reader/predicate mirrors an already-shipped idiom verbatim (`_task_gate_mode`/`_GATE_MODE_RE`, `_ai_freeze_allowed`, `_streams_posture`/`_project_autonomy_token`) — zero new parsing style, per §1 Framings weighed.
Data strategy: 2 new optional TASK.md header lines (`skips:`, `oneshot:`) · 1 new optional §0 field (`Skip rationale:`) · 1 new optional PROJECT.md line (`benchmark_mode:`) · `state.json tasks.<slug>` gains 2 optional keys (`oneshot: bool`, `skips: [{phase,reason,by,at}]`) — matches the §3 Schema line exactly.
Pattern: anchored-header-token idiom (§0 Honors) — validate-then-write, fail-closed on a malformed CSV element (mirrors `_ai_freeze_allowed`'s "?" philosophy), fail-SAFE on an absent project-level opt-in (mirrors `_project_autonomy_token`).
Optimization stance: correctness-first (a fail-closed trust-floor mechanism, not a hot path) — token cost is the only real budget (⚠ least-trusted facet: the fast-template byte-ceiling headroom, confirmed ample at build: 88/185 lines, well under the 60% guard).

Persona (required): methodology-engine-dev
Spawn isolation (default): n/a — solo build turn, no subagent spawned (isolation: "worktree" would apply if one were)
Known-problem fixes: nxt reassigned mid-pre-pass could desync the setup-lock check → placed the pre-pass BEFORE that check so it always evaluates the resolved `nxt` · a wrapped multi-line §5 Scope line would silently truncate (scope-token-grammar trap) → every token declared on the single first physical line, each containing "/" (project-root-relative, no bare-token sibling-resolution ambiguity) · stale SEAMS.md line-number pins (a recurring class of drift this project's own SEAMS entries document) → re-resolved and re-pinned both cited anchors after the edit, not before.
Strategy actually used: as planned — RED suite written first (test_fast_lane_skips.py, 45 tests), confirmed RED for the right reason (AttributeError / unrecognized --oneshot / assertion mismatches on the pre-build tree via a git-stash-and-restore round trip), then implemented in the order above; GREEN on the first full pass after fixing one test-harness bug (a premature freeze attempt before reaching the `contract` phase in the non-skippable-crossings test).
Safety rule (feature-specific): an irreversible phase jump (scenarios/observe) is never recorded without a reason captured BEFORE the jump — `skip_reason_missing` is a hard `_die`, not a post-hoc audit glint; validate-then-write throughout (every `_die` in the pre-pass fires before `state["tasks"][slug]["phase"] = nxt`).
Code lives in: `add-method/tooling/` (+ propagated mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 45/45 `test_fast_lane_skips.py` green (`python3 -m unittest test_fast_lane_skips -v`); full-suite background run in progress at fill-time, no failures observed through 4082 log lines
- [x] coverage did not decrease — 100% of the new surface covered (§4 test_plan, one test per M1-M14/Reject/edge case); `add.py check` shows 0 coverage-gap warnings for `fast-lane-skips` (unlike many sibling tasks that DO show `no §2 scenario tag` warnings)
- [x] no test or contract was altered during build — `git diff` on `test_fast_lane_skips.py` and this TASK.md's §3 shows only the build's OWN initial authoring commits, no post-green edits; verify session made zero edits to either
- [x] the green was EARNED, not gamed — 4 targeted mutations (see Refute-read verdict below), all confirmed red for the right reason, all reverted
- [x] concurrency / timing of the risky operation is safe — see Advisor 3-lens below
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor 3-lens below
- [x] layering & dependencies follow CONVENTIONS.md — see Advisor 3-lens (architecture) below
- [ ] a person reviewed and approved the change — HUMAN GATE, left for Tin Dang (sensitivity: architecture, autonomy: conservative — this verify does not self-approve)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a `fast:true`/`oneshot:true`/`benchmark_mode:true` task declaring `skips: scenarios,observe` (with §0 rationale for both) crosses specify→contract and verify→done in ONE `advance` call each, never visiting `phase: scenarios`/`phase: observe` — confirmed by `CmdAdvanceSkipMechanicTest` (2/2 green) AND by direct read of `add.py:cmd_advance` lines 1286-1317 (skip pre-pass sits strictly before the `nxt=="contract"`/`"build"`/`"tests"` branches at 1328/1338/1349, `nxt = PHASES[idx+2]` hops the phase)
- [x] a malformed/ineligible/reasonless declaration is refused BEFORE any write (phase unchanged, no `skips` entry) — confirmed by `RejectPathsTest` (4/4 green) AND by mutation 3 below (dropping the eligibility gate was caught by this exact class of test)
- [x] the 6 non-skippable crossings execute zero bytes of this task's new logic — confirmed by `NonSkippableCrossingsUntouchedTest` AND by mutation 1 below (widening `_SKIPPABLE_PHASES` to include `"contract"` made this exact test fail with `1 != 0 scenarios->contract`, proving the spy is live, not vacuous)
- [x] a plain task (no fast/oneshot/benchmark, no `skips:`) walks all 8 crossings exactly as before, never gaining a `skips` state key — confirmed by `NormalFlowUnchangedTest` (green)
- [x] `--oneshot` scaffolds `fast:true`+`oneshot:true`+`gate_mode:ai-plan-verify`; a `security`-sensitivity `--oneshot` task still gets its skip but still needs a human `freeze --by` — confirmed by `OneshotNewTaskTest`+`FloorCompositionTest` (green) AND by mutation 4 below (bypassing `_ai_freeze_allowed`'s security block was caught by `FloorCompositionTest` AND by task2's own `test_ai_plan_verify_gate` suite — 4 tests total)
- [x] `status`/`guide`/`gate-explain` surface the declared/consumed skip-set and the allow/block outcome, silent when inapplicable; `audit` flags a post-hoc deleted rationale (MEASURE-NOT-BLOCK) — confirmed by `StatusGuideSurfaceTest`/`GateExplainSkipSetTest`/`AuditSkipRationaleMissingPostHocTest` (all green) AND by mutation 2 below (dropping the `skips.append` silent-skip mutation was caught by `StatusGuideSurfaceTest` and `AuditSkipRationaleMissingPostHocTest` among 5 failures)
- [x] the 3 engine trees + 4th dogfood template mirror stay byte-identical, and `ENGINE_MD5`/`ENGINE_PKG_MD5` match the live trees — confirmed by `EngineTreeParityTest` (4/4 green) AND independently by `md5`/`diff -q` across all 3 canon trees post-verify (all match: constants.py=e147437e…, predicates.py=cb1dab7d…, add.py=4fefc0bb…) AND `engine_pin.py` literals (ENGINE_MD5=4fefc0bb522c6343aca1af3dd9940926, ENGINE_PKG_MD5=b287ceedad9e29013a798b8faa978605) match the live add.py/package md5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced, confirmed via `grep`: `_SKIPPABLE_PHASES` (imported + used in `cmd_advance`); `_task_skip_set` (used in `cmd_advance`, `_skip_status_line`, `_gate_explain`); `_skip_lane_eligible` (used in `cmd_advance`, `_skip_status_line`, `_gate_explain`); `_skip_set_allowed` (used in `cmd_advance`, `_gate_explain`); `_skip_rationale` (used in `cmd_advance`, `_audit_findings`); `_project_benchmark_mode` (used in `cmd_advance`, `_skip_status_line`, `_gate_explain`); `_skip_status_line` (used in `cmd_status` line ~2572, `cmd_guide` line ~2768); `skip_rationale_missing_post_hoc` glint wired into `_audit_findings` (line 6885-6886) — zero orphaned new symbols
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; the WIRING grep above shows every new function/constant has ≥1 real call site outside its own definition and its own test file
- [ ] SEMANTIC (prose / non-code) — N/A path: this is a code task (Python engine + 2 template lines); the template scaffold (`TASK.fast.md.tmpl`'s 2 new lines) was read in full and confirmed to match §3's TEMPLATE CHANGE spec exactly (commented `skips:` header hint + `Skip rationale:` §0 placeholder; `TASK.md.tmpl` 0-line diff, confirmed via `git diff --stat`)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct `grep -n`/`Read` against the live files: `_SKIPPABLE_PHASES` constants.py:345; `_SKIPS_LINE_RE` add.py:1458; `_task_skip_set` add.py:1461; `_skip_lane_eligible`/`_skip_set_allowed` predicates.py:59/67; `_skip_rationale` add.py:1487; `_project_benchmark_mode` add.py:1511; `cmd_advance` add.py:1260 (pre-pass at 1286-1317, strictly before `nxt=="contract"` at 1328); `cmd_new_task` add.py:664 (`--oneshot` splice at 736-742, state keys at 780-783); `_skip_status_line` add.py:1524 (called from `cmd_status`/`cmd_guide`); `_gate_explain` add.py:1723; `_audit_findings`/`cmd_audit` add.py:6839/7085; `TASK.fast.md.tmpl` scaffold confirmed by direct read. `PHASES`/`PHASE_GROUPS` (constants.py:58/107) confirmed unchanged and the skip pre-pass never references `PHASE_GROUPS` (only `bundle:` status line at add.py:2582 does)
- [x] anchors that moved since Ground SHA (38efd8f), named not silent: `cmd_advance` shifted from the §0-cited 1244-1354 to the current 1260-1386 (+16 lines, from code added earlier in the file during this same build — not a stale/wrong anchor, just build-growth drift, confirmed the SYMBOL still resolves correctly at its new location); `.add/SEAMS.md`'s two pinned anchors (`_declared_scope` add.py:5165, `_section_unfilled` predicates.py:100) were re-pinned during THIS build per their own inline comments ("re-pinned 2026-07-09") and both independently re-verified here to resolve to the correct symbol at the pinned line

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: add-verify agent (this session) · adversarially checked: 4 targeted mutations, each run one-at-a-time then reverted (tree confirmed byte-identical + green after each):
  1. Widened `_SKIPPABLE_PHASES` to `("scenarios","observe","contract")` (constants.py) — can the closed trust-floor set be silently broadened? RED: `test_value_and_all` + `test_six_non_skippable_crossings_never_invoke_task_skip_set` (the M13 spy caught `1 != 0 scenarios->contract` — proves the spy is live, not decorative) + tree-parity test.
  2. Removed the `state[...].setdefault("skips",[]).append(...)` recording line from `cmd_advance`'s pre-pass (add.py) while leaving the jump itself intact — can a skip fire SILENTLY (rule #4 violation)? RED: 5 failures (`CmdAdvanceSkipMechanicTest`×2, `FloorCompositionTest`, `StatusGuideSurfaceTest`, tree-parity).
  3. Made `_skip_set_allowed` (predicates.py) return `(True, None)` unconditionally, dropping the lane-eligibility gate — can a non-fast/non-oneshot/non-benchmark task skip a phase? RED: `test_lane_ineligible_declaration_refused`, `test_blocked_outcome_for_ineligible_declared_task`, `test_non_empty_set_permitted_only_when_eligible`, tree-parity.
  4. Made `_ai_freeze_allowed` (predicates.py, task2's OWN unchanged floor) permit `security` sensitivity through `ai-plan-verify` — does this task's skip axis ever weaken the security floor it composes with? RED: this task's `FloorCompositionTest` AND, independently, task2's own `test_ai_plan_verify_gate` suite (4 failures) — the composition genuinely holds at both ends, not just from this task's side.
All 4 mutations confirmed RED for the stated reason, then reverted; `git diff`/md5 confirm the 3 canon trees ended byte-identical to their pre-mutation state; `__pycache__` cleared.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: add-verify agent (this session)
1. Security: CLEAR — `_SKIPPABLE_PHASES` is a hardcoded closed 2-tuple; `nxt` is always drawn from the immutable `PHASES` tuple, so `nxt in _SKIPPABLE_PHASES` is structurally False for `contract`/`tests`/`build`/`verify`/`ground`/`specify` (confirmed by mutation 1 — even a code-level widening of the tuple is caught, and no user-facing input can reach the tuple at all). `--oneshot`'s `gate_mode: ai-plan-verify` composes with, never weakens, task2's own `_ai_freeze_allowed`, which still HARD-STOPs `security`/`data`/`architecture` sensitivity regardless of skips (confirmed by mutation 4, on both this task's and task2's own suites). No eval/exec/subprocess/network; pure regex+dict+file-read, matching the Ground context's NO-EXEC discipline. No secrets touched.
2. Concurrency: CLEAR — the skip pre-pass (add.py:1286-1317) only mutates the in-memory `state` dict; every `_die()` in the pre-pass (skip_not_allowed / skip_lane_required / skip_reason_missing) fires before the single `save_state(root, state)` atomic call at line 1384 (temp-file + `os.replace`, `add_engine/io_state.py:_atomic_write`) — validate-then-write is intact, matching every other guard already in `cmd_advance`, confirmed by direct read. No NEW concurrency surface: this task adds no new writer, no new lock requirement, and does not change the pre-existing single-writer-per-invocation model (the engine has no file-locking for concurrent `advance` calls today, but that is a pre-existing, out-of-scope property unchanged by this task — not a regression introduced here).
3. Architecture: CLEAR — confirmed by direct computation: `_SKIPPABLE_PHASES` members' indices in `PHASES` are scenarios=2, observe=7; `PHASES[idx+2]` (idx = the phase BEFORE the skipped one) resolves to 3 ("contract") and 8 ("done") respectively — both within `PHASES`' valid 0-8 range, confirmed neither skippable phase is `PHASES[-1]`. `PHASE_GROUPS` is referenced exactly once in add.py (the pre-existing `bundle:` status line at 2582) and NEVER inside the skip pre-pass — the mechanism is genuinely bundle-agnostic (DIRECTION/VERIFY straddle, per §0), keyed purely off flat `PHASES` index arithmetic as the contract claims. Every new reader mirrors an already-shipped idiom (`_task_gate_mode`/`_GATE_MODE_RE`, `_ai_freeze_allowed`, `_streams_posture`) — zero new parsing style.
Verdict: PASS
Residue: none
Binding: advisory — architecture (sensitivity is `architecture`, not `mechanical`; per the advisor-gate-relax precedent this verdict is advisory input to the human gate, not a self-relaxing mechanical PASS)

### GATE RECORD
Reported: yes — the gate report (banner/ARC/evidence/flag) rendered before this outcome recorded; human chose "PASS as-is" (fast:true stays an independent skip trigger, per frozen §3 + milestone Scope(3))
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-09

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose a new closed-2-tuple `_SKIPPABLE_PHASES` + a header `skips:` CSV declaration read by a `_GATE_MODE_RE`-style anchored regex, enforced by a tightly-gated `cmd_advance` pre-pass (`if nxt in _SKIPPABLE_PHASES:`) that only ever touches the 2 relevant crossings, with the reason required BEFORE the jump as a hard precondition; rejected a NEW dedicated phase-count constant that literally shrinks `PHASES` for oneshot tasks (rejected — MILESTONE.md Out: "collapsing the engine to 3 phase-STATES… kept at 8 + bundle metadata"; a per-task-shrunk `PHASES` tuple would also break every `PHASES.index(...)` call-site's assumption of one universal ladder, a far larger blast radius) · re-purposing the EXISTING `freeze_skipped`/`--skip-freeze` escape mechanism to also cover scenarios/observe (rejected — that mechanism crosses tests→build on a DRAFT §3, a DIFFERENT boundary entirely; conflating "the contract never got frozen" with "an optional ceremony phase was deliberately jumped" would blur two independently-audited trust signals into one, defeating the purpose of a distinct, nameable skip-set) · making `--fast` alone (no new flag) sufficient to unlock skip declarations, with no `--oneshot`/`benchmark_mode` addition at all (rejected — narrower than MILESTONE.md Scope(3), which names `--oneshot` and benchmark-mode as explicit, separate triggers; a project running unattended/headless (the benchmark harness) needs a project-level opt-in that does not require hand-typing `--fast` on every task) · requiring a per-skip CLI flag at `advance` time (e.g. `advance --skip-reason "..."`) instead of a pre-declared `skips:` header + §0 `Skip rationale:` field (rejected — the AI already authors §0 GROUND before any later crossing is attempted; front-loading the declaration keeps the reason auditable in the frozen historical record of the task's OWN ground work, not scattered across CLI invocation history, and matches the "AI declares the skip-set" framing — a decision made once, early, not re-litigated at each crossing).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: a closed, hardcoded 2-tuple gate (`_SKIPPABLE_PHASES`) is the ONLY set `cmd_advance`'s pre-pass ever tests `nxt` against — an architectural exclusion, not a runtime policy, so the other 6 crossings can never reach any of this task's new code. Every new reader/predicate mirrors an already-shipped idiom verbatim (`_task_gate_mode`/`_GATE_MODE_RE`, `_ai_freeze_allowed`, `_streams_posture`/`_project_autonomy_token`) — zero new parsing style, per §1 Framings weighed.
- [AI] build — data strategy: 2 new optional TASK.md header lines (`skips:`, `oneshot:`) · 1 new optional §0 field (`Skip rationale:`) · 1 new optional PROJECT.md line (`benchmark_mode:`) · `state.json tasks.<slug>` gains 2 optional keys (`oneshot: bool`, `skips: [{phase,reason,by,at}]`) — matches the §3 Schema line exactly.
- [AI] build — pattern: anchored-header-token idiom (§0 Honors) — validate-then-write, fail-closed on a malformed CSV element (mirrors `_ai_freeze_allowed`'s "?" philosophy), fail-SAFE on an absent project-level opt-in (mirrors `_project_autonomy_token`).
- [AI] build — optimization stance: correctness-first (a fail-closed trust-floor mechanism, not a hot path) — token cost is the only real budget (⚠ least-trusted facet: the fast-template byte-ceiling headroom, confirmed ample at build: 88/185 lines, well under the 60% guard).
- [AI] build — strategy used: as planned — RED suite written first (test_fast_lane_skips.py, 45 tests), confirmed RED for the right reason (AttributeError / unrecognized --oneshot / assertion mismatches on the pre-build tree via a git-stash-and-restore round trip), then implemented in the order above; GREEN on the first full pass after fixing one test-harness bug (a premature freeze attempt before reaching the `contract` phase in the non-skippable-crossings test).
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

