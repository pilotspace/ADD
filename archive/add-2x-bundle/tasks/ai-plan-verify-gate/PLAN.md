# TASK: two-way DIRECTION gate: gate_mode=human|ai-plan-verify; AI verifies frozen direction bundle and auto-passes the contract freeze EXCEPT security/data/architecture (->human; security HARD-STOP)

slug: ai-plan-verify-gate · created: 2026-07-09 · stage: mvp · risk: high
milestone: three-phase-flow
sensitivity: architecture
autonomy: conservative
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_freeze` (line 926) — the §3 freeze-WRITE command; validate-then-write. Current checks in order: `already_frozen` -> `contract_not_drafted` -> `unflagged_freeze` -> `sensitivity_invalid` (via `_task_sensitivity`/`_project_sensitivity_values`), THEN writes `Status: FROZEN @ vN — approved by <who>` (who = `args.by` or `identity._actor_stamp(state)["name"]`) into the §3 span ONLY (regex-bounded between the `## 3 ·` heading and the next `##`/`---`), and records `state["tasks"][slug]["freeze"] = {"version","frozen_at","approved_by","actor"}`. This task's new AI-freeze path is an ADDITIVE branch inside this same function, gated behind a new `--ai-plan-verify` CLI flag — zero new code executes on the existing no-flag path.
  - `add-method/tooling/add.py:_contract_frozen` (line 5496) — `any(re.match(r"\s*Status:\s*FROZEN", ln) ...)`: artifact-observable, no engine flag, agnostic to WHO wrote FROZEN. This is why the tests->build gate (`_build_entry`, line ~1030-1094, the `contract_not_frozen` check at line 1043) needs **zero code change**: an AI-written `Status: FROZEN @ vN — approved by <agent-id>` satisfies it identically to a human-written one. The AI-freeze mechanism sits entirely upstream of the existing gate.
  - `add-method/tooling/add.py:_next_freeze_version` (line 918) — v1 first freeze, N+1 on re-freeze; reused unchanged by the AI path (no separate versioning scheme).
  - `add-method/tooling/add.py:_flag_well_formed` (line 5538) — the existing lowest-confidence-flag well-formedness check, already unconditionally required by `cmd_freeze` before ANY freeze (human or AI) — the AI path inherits this for free, no duplication needed.
  - `add-method/tooling/add.py:_task_sensitivity` (line 1334) + `add_engine/constants.py:_SENSITIVITY_VALUES` (line 326, `("security","data","architecture","mechanical")`) — the closed base enum; `_project_sensitivity_values` (add.py:1385) extends it with project GLOSSARY domain classes. `_task_sensitivity` returns a member, `None` (absent — grandfathered for the HUMAN path only), or `"?"` (real-but-unknown, rejected at freeze via `sensitivity_invalid`).
  - `add-method/tooling/add.py:_gate_explain` (line 1498) and the VERIFY-gate completion guard (line ~1560-1573, inside the function that also uses `_heal_or_escalate`/`_tamper_guard`) — **advisor-gate-relax**, the sibling mechanism at the OTHER trust boundary (VERIFY/completion, not FREEZE). `_relaxed = _task_sensitivity(hdr) == "mechanical" and _advisor_verdict_is_pass(body6) and _advisor_no_residue(body6)`: an ALLOW-LIST of exactly one literal token, `"mechanical"` — NOT "everything except security/data/architecture". The audit mirror at line ~6655 and the residue-mistier lint (`advisor_residue_on_mechanical_mis_tier`, line ~6798-6805) both key off the same literal check. This is the precedent this task's predicate must reconcile with (see Issues/Risks).
  - `add-method/tooling/add.py:_advisor_slice` (1422) / `_advisor_verdict_is_pass` (1433) / `_advisor_no_residue` (1442) — the exact idiom for extracting a named `### <Heading>` sub-block from a phase body and reading `Verdict:`/`Residue:` lines off it. This task's new "AI-verify record" §3 sub-block and its reader function follow the SAME idiom (heading-bounded slice, then line-anchored field reads), not a new parsing style.
  - `add-method/tooling/add_engine/autonomy.py:_autonomy_level` / `_effective_autonomy` / `_AUTONOMY_LEVELS` (constants.py) — `_effective_autonomy(root, state, slug)` resolves the task's declared rung, falling back to the project default; already the resolver `_driver_stop` uses at the VERIFY gate ("effective autonomy == auto"). This task reuses it unchanged for the FREEZE gate's autonomy check — no new autonomy machinery.
  - `add-method/tooling/add.py:identity._actor_stamp` — records the git/CLI actor running the command (distinct from the freeze's `approved_by` name). The AI path keeps `actor` as today (whoever's shell ran `add.py freeze`) and does NOT let it silently stand in for the required `--by <agent-id>` — an AI freeze must name its OWN agent id explicitly, never inherit the human's git identity as if it approved.
  - `add-method/tooling/add_engine/constants.py:__all__` (line 10) — any new public constant (`_GATE_MODES`) must be added here.
  - `add-method/tooling/add_engine/constants.py:_SENSITIVITY_VALUES` neighborhood (lines 300-330) — the sibling location for a new `_GATE_MODES = ("human", "ai-plan-verify")` closed-enum constant, same idiom as `_AUTONOMY_LEVELS`/`_STREAMS_POSTURES`/`_SENSITIVITY_VALUES`.
  - `phase-bundles` task (DONE, this milestone) — `PHASE_AGENT["contract"] == "add-design"`; confirms this task's own bundle/agent placement is already correct and needs no rework.

Context (working folder): no data files, no runtime config beyond TASK.md/state.json prose + a handful of pure Python functions in `add.py`/`add_engine/{constants,predicates,autonomy}.py`. No network, no subprocess, no schema/DB. NO-EXEC discipline trivially holds — everything here is regex/dict-lookup/file-read/atomic-write, matching the existing freeze machinery's own risk profile.

Honors (patterns / conventions):
  - Mirrors the closed-enum + anchored-line-read idiom used by `_AUTONOMY_LEVELS`/`_autonomy_level`, `_SENSITIVITY_VALUES`/`_task_sensitivity`, and `_STREAMS_POSTURES`/`_streams_posture`: a tuple constant in `constants.py` + a PURE resolver reading an anchored `key: value` header line, returning a member / `None` (absent) / `"?"` (unknown).
  - Mirrors `_advisor_slice`'s heading-bounded-sub-block idiom for the new "AI-verify record" §3 sub-block reader — never a new ad-hoc parsing style.
  - validate-then-write (cmd_freeze's own documented discipline, restated in its docstring): every new AI-path refusal fires BEFORE any write; TASK.md written before state.json (crash-safe, mirrors the existing freeze).
  - Additive-only: the new AI-path is reached ONLY via an explicit new CLI flag (`--ai-plan-verify`); the flagless path (today's default) is byte-identical — zero regression risk to the 45+ existing freeze/build-gate tests enumerated in the search above (test_freeze_command.py, test_unflagged_freeze.py, test_phase_build_guard.py, test_tamper_tripwire.py, etc.).
  - 3-tree byte-identical propagation (methodology-engine-dev's Critical Rule + `.add/SEAMS.md#three-tree-parity`) — a BUILD-phase obligation, named here so Strategy inherits it without re-deriving.

Seams consulted: `.add/SEAMS.md#three-tree-parity` — the 3-copy byte-identical-twin guard.

Anchors the contract cites: `add_engine/constants.py:_GATE_MODES` (new) · `add.py:_task_gate_mode` (new, mirrors `_task_sensitivity`) · `add_engine/predicates.py:_ai_freeze_allowed` (new, pure predicate) · `add.py:cmd_freeze` (extended) · `add.py:_ai_verify_slice` / `_ai_verify_checklist_complete` (new, mirrors `_advisor_slice`) · `add.py:_contract_frozen` (unchanged, already sufficient) · `add.py:_build_entry`'s `contract_not_frozen` check (unchanged) · `add.py:_gate_explain` / the VERIFY-gate `_relaxed` check (unchanged, cited for the reconciliation note only).

Issues/Risks (→ feed §1):
  - **RESOLVED (human freeze decision, 2026-07-09): the sensitivity floor is a BLOCK-list of exactly `{"security","data","architecture"}`, not an allow-list of `"mechanical"`.** The milestone doc's plain-English framing ("EXCEPT security/data/architecture... extends advisor-gate-relax") is the intake-authoritative reading. Consequence: UNDECLARED sensitivity (`None`), the literal `"mechanical"` token, and any project-GLOSSARY-declared class beyond the base four ALL qualify for AI-freeze (given gate_mode + autonomy also pass); only the 3 named floor classes and a genuinely MALFORMED (`"?"`) token are blocked — the malformed case gets its OWN new code, `ai_freeze_unknown_sensitivity` (distinct from the floor-class block, since "a real-but-garbled token" and "a real, recognized, human-floor token" are different failure shapes worth distinguishing in the audit trail). Rationale for undeclared qualifying (recorded, not silently inferred): the double opt-in — `gate_mode: ai-plan-verify` AND `autonomy: auto`, BOTH human-declared — IS the sign-off; the common oneshot/benchmark task carries no `sensitivity:` line at all, and that is exactly the case the milestone's speed goal needs to auto-freeze. This diverges from advisor-gate-relax's OWN choice (an allow-list of exactly `"mechanical"` at the VERIFY boundary) — the two gates are now explicitly DIFFERENT-SHAPED floors at two different boundaries, not one shared floor concept (see §3 reconciliation note).
  - (superseded — see RESOLVED above) The milestone's own Shared-decisions bullet describes this task as an "extension" of advisor-gate-relax's mechanical-only floor; that "extension" reading (broadening past mechanical-only) is the one now adopted.
  - `gate_mode` needs a fail-closed DEFAULT distinct from `autonomy`'s: `autonomy` defaults absent->`"auto"` (existing, permissive) because autonomy is an EXISTING, already-trusted dial; `gate_mode` is a brand-NEW trust-loosening capability, so absent must default to `"human"` (today's behavior, unchanged) — never silently default to the new capability.
  - `--by` must be a REQUIRED, explicit flag on the AI path (never fall back to `identity._actor_stamp`), else the audit trail would show a human's git identity as having "approved" a freeze an AI actually performed — a traceability regression the milestone's "no silent bypass" bar forbids.
  - The AI-verify checklist must be an ENGINE-ENFORCED precondition (regex-checked, mirroring `_flag_well_formed`), not merely advisory prose, or the "not a rubber stamp" requirement is unmet.
  - A tamper-symmetry gap: `unflagged_freeze`'s residual audit check (line ~6621-6624) re-verifies a `flag_verified` record's flag stays well-formed post-freeze. Without a symmetric residual check for `mode: "ai-plan-verify"` records, a human could hand-delete the "AI-verify record" block after the fact with zero detection — undermining the very audit trail this task exists to create. Proposed as a Must (parity with the existing pattern), not left for a later task.
  - Security is a HARD-STOP that ALREADY lives at the VERIFY gate (unaffected by this task); this task's allow-list additionally ensures `security` sensitivity can never even REACH an AI-frozen contract in the first place — defense in depth, not a new HARD-STOP mechanism.

Related intent: `.add/milestones/three-phase-flow/MILESTONE.md` Scope (2) + Shared decisions ("AI-plan-verify-gate NEVER auto-passes security/data/architecture... Mirrors and extends `advisor-gate-relax`") + Exit criterion 2. GLOSSARY terms: `AI-plan-verify-gate` (new, per Scope), `gate_mode` (new).

Ground SHA: 1af4c1e

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `gate_mode` — a two-way DIRECTION freeze gate (`human` | `ai-plan-verify`) letting a task under `autonomy:auto` whose sensitivity is NOT `security`/`data`/`architecture` (undeclared, `mechanical`, or any other valid class all qualify) have its §3 CONTRACT frozen by a recorded AI verifier instead of a human, with a fail-closed predicate and an engine-enforced verification checklist — never silently, and a genuinely malformed sensitivity token still fails closed.

Framings weighed: a new `--ai-plan-verify` flag on the EXISTING `cmd_freeze`, gated by a new task-header `gate_mode:` line + a pure BLOCK-list predicate over (gate_mode, sensitivity, autonomy) — human-required for exactly `{security,data,architecture}` plus a malformed `"?"` token, everything else (undeclared, `mechanical`, any other valid project class) qualifies — mirroring the `_AUTONOMY_LEVELS`/`_SENSITIVITY_VALUES` closed-enum idiom for the resolver shape (chosen — additive, reuses `_contract_frozen`'s artifact-observable signal with zero change to the tests->build gate; matches the intake-authoritative "all except security/data/architecture" framing) · a brand-new sibling command (`cmd_ai_freeze`) instead of extending `cmd_freeze` (rejected — duplicates the 4 existing validate-then-write preconditions (already_frozen/contract_not_drafted/unflagged_freeze/sensitivity_invalid), risking drift between two freeze paths; a flag on the same function keeps ONE freeze implementation, additive branch only) · an ALLOW-list of exactly `"mechanical"` mirroring advisor-gate-relax (considered, then rejected by the human freeze decision 2026-07-09 — see §0 Issues/Risks RESOLVED note: it is materially narrower than the milestone's own framing and would silently exclude the common sensitivity-undeclared oneshot/benchmark task the speed goal targets) · a project-level `gate_mode` default in PROJECT.md mirroring `_project_autonomy` (deferred — milestone Scope names only the task-header two-way state; a project default is a natural follow-on but not spec'd here, and defaulting a NEW trust-loosening capability at the project level before its task-level shape is proven is the wrong order).

Must:
<must>
  - M1: `add_engine/constants.py` defines `_GATE_MODES = ("human", "ai-plan-verify")` (closed 2-tuple), added to `__all__`, sibling of `_AUTONOMY_LEVELS`/`_SENSITIVITY_VALUES`/`_STREAMS_POSTURES`.
  - M2: `add.py` defines `_task_gate_mode(hdr: str) -> str | None` (PURE), reading an anchored `gate_mode:` header line (same `(?:^|·)[ \t]*gate_mode:[ \t]*([^\s<#|]+)` idiom as `_AUTONOMY_LINE_RE`): returns a member of `_GATE_MODES`, `None` when absent, `"?"` when a real-but-unrecognized token is written. Absent -> treated as `"human"` by every caller (fail-closed default; NEVER auto-upgrades to `"ai-plan-verify"`).
  - M3: `add_engine/predicates.py` defines `_ai_freeze_allowed(gate_mode: str | None, sensitivity: str | None, autonomy: str) -> tuple[bool, str | None]`, PURE: returns `(False, "ai_freeze_not_opted_in")` unless `gate_mode == "ai-plan-verify"`; else `(False, "ai_freeze_requires_auto")` unless `autonomy == "auto"`; else `(False, "ai_freeze_blocked_sensitivity")` if `sensitivity in ("security","data","architecture")`; else `(False, "ai_freeze_unknown_sensitivity")` if `sensitivity == "?"` (a real-but-malformed token — fails closed, distinct code from the floor-class block); else `(True, None)` — this LAST branch covers `sensitivity is None` (undeclared), `sensitivity == "mechanical"`, and any OTHER valid project-GLOSSARY-declared class: a BLOCK-list of the 3 named floor classes + malformed, not an allow-list of one.
  - M4: `add.py cmd_freeze` gains a new `--ai-plan-verify` boolean flag and a new required `--by AGENT_ID` value (the human path's `--by` stays optional, unchanged). When `--ai-plan-verify` is passed: (a) run already_frozen/contract_not_drafted/unflagged_freeze unchanged; the existing `sensitivity_invalid` `"?"`-guard is SKIPPED on this AI path (human path unchanged) so a malformed token routes to `_ai_freeze_allowed` -> `ai_freeze_unknown_sensitivity` (v2 amendment — makes that distinct code CLI-reachable); (b) `_die("ai_freeze_missing_actor")` if `--by` absent; (c) call `_ai_freeze_allowed(_task_gate_mode(hdr), _task_sensitivity(hdr, valid=_project_sensitivity_values(root)), _effective_autonomy(root,state,slug))`, dying with the returned code if not allowed; (d) `_die("ai_freeze_checklist_incomplete")` unless the §3 "AI-verify record" sub-block (M6) is present and every item checked; (e) on success, write `Status: FROZEN @ vN — approved by <agent_id>` (IDENTICAL format to the human path — `_contract_frozen`/`_freeze()` display need no change) PLUS one new additive line directly beneath it: `Freeze mode: ai-plan-verify — verified by <agent_id> at <ISO-8601 UTC timestamp>`; state.json's `freeze` dict gains `"mode": "ai-plan-verify"` and `"verified": {"anchors": true, "rules": true, "shape": true, "flag": true}` (all four, since (d) already required them all checked).
  - M5: the human path (`add.py freeze --by <name>`, no `--ai-plan-verify` flag) is BYTE-IDENTICAL to today — no new line, no new state key, no new check reached. `state["tasks"][slug]["freeze"]` on the human path has no `"mode"` key (its absence, not `"human"`, IS "human mode" — back-compat with every pre-existing frozen task's state record).
  - M6: §3's CONTRACT template gains a new optional-until-declared sub-block, "AI-verify record (required when gate_mode: ai-plan-verify)", with exactly 4 checklist lines mirroring this task's own success criteria: anchors resolve · Must+Reject present with error codes · contract shape concrete (no template placeholders) · lowest-confidence flag surfaced — plus a `Verified by: <agent-id> · at: <timestamp>` line. `add.py`'s `_ai_verify_slice(raw3)` (mirrors `_advisor_slice`'s heading-bounded-slice idiom) extracts this block; `_ai_verify_checklist_complete(raw3) -> bool` (mirrors `_flag_well_formed`'s style) is True iff all 4 items are `- [x]` and `Verified by:` is non-empty.
  - M7: `add.py audit` gains one new residual glint, `ai_freeze_checklist_missing`: for any task whose state.json `freeze.mode == "ai-plan-verify"`, if the CURRENT §3 no longer passes `_ai_verify_checklist_complete`, flag it — symmetric to the existing `unflagged_freeze` residual check (line ~6621-6624), catching a post-freeze hand-edit that deletes the AI-verify evidence. MEASURE-NOT-BLOCK (like every other audit glint) — never engine-blocking, a human spot-audit backstop.
  - M8: `add.py gate-explain` (the existing read-only `_gate_explain`, line 1498) gains one additional printed line when a task declares `gate_mode: ai-plan-verify`, naming whether the freeze-gate predicate currently allows or blocks an AI freeze and why (reuses `_ai_freeze_allowed`'s returned code) — read-only, no new write path, mirrors the existing `advisor-gate-relax` explain line already printed there.
  - M9: `.add/GLOSSARY.md` gains (via this task's §3 `Glossary deltas:` line, folded later by `add.py fold`) a `gate_mode` definition AND an explicit note reconciling it with `advisor-gate-relax`: the two are sibling gates at DIFFERENT trust boundaries (freeze vs. verify-completion) using DIFFERENT-SHAPED sensitivity floors — this gate BLOCK-lists `{security,data,architecture}` (+ malformed) and passes everything else (including undeclared and `mechanical`), while advisor-gate-relax ALLOW-lists only the literal `"mechanical"` token — related but not identical floors, never described as interchangeable.
  - M10: the three engine trees (`add-method/tooling/`, `.add/tooling/`, `add-method/src/add_method/_bundled/tooling/`) stay byte-identical for every `constants.py`/`predicates.py`/`add.py` edit (BUILD-phase obligation, declared here so Strategy inherits it).
</must>

Reject:
<reject>
  - `--ai-plan-verify` passed on a task whose `gate_mode:` header is absent or `"human"` -> "ai_freeze_not_opted_in"
  - `--ai-plan-verify` passed while the task's EFFECTIVE autonomy (declared, else project default) is not `"auto"` (e.g. `conservative`/`manual`, or a lowered dial) -> "ai_freeze_requires_auto"
  - `--ai-plan-verify` passed on a task whose sensitivity is `"security"`, `"data"`, or `"architecture"` (the human-floor set; security additionally remains a HARD-STOP at the unrelated, unaffected VERIFY gate) -> "ai_freeze_blocked_sensitivity"
  - `--ai-plan-verify` passed on a task whose sensitivity is a real-but-unrecognized, malformed token (`"?"` — not a member of the project's sensitivity vocabulary) -> "ai_freeze_unknown_sensitivity" (fails closed; distinct from the floor-class block above — a garbled declaration is not the same failure as a correctly-declared human-floor class)
  - `--ai-plan-verify` passed without `--by <agent_id>` (never silently falls back to the CLI-runner's git identity) -> "ai_freeze_missing_actor"
  - `--ai-plan-verify` passed but the §3 "AI-verify record" block is absent, has any unchecked item, or has no `Verified by:` value -> "ai_freeze_checklist_incomplete"
  - `--ai-plan-verify` passed on a task with UNDECLARED sensitivity, `"mechanical"` sensitivity, or any other project-GLOSSARY-declared class -> NOT a rejection; qualifies for AI-freeze (given gate_mode + autonomy also pass) — the double opt-in (`gate_mode: ai-plan-verify` + `autonomy: auto`, both human-declared) is the sign-off; a task author is never silently exempted since both declarations are visible, auditable, and required
  - the 4 pre-existing freeze checks (already_frozen/contract_not_drafted/unflagged_freeze/sensitivity_invalid) firing on the AI path -> the SAME existing error codes, unchanged, no new AI-specific text
  - `add.py freeze --by <human>` (no `--ai-plan-verify`) on any task, regardless of its `gate_mode:` declaration -> succeeds exactly as today; a declared `gate_mode: ai-plan-verify` never FORCES the AI path or blocks the human path — the human may always freeze by hand
</reject>

After:
<after>
  - A task declaring `gate_mode: ai-plan-verify` · `sensitivity: mechanical` · `autonomy: auto` (or inheriting an effective `auto`), with a complete "AI-verify record" and a well-formed lowest-confidence flag, can be frozen via `add.py freeze --ai-plan-verify --by agent:<id>` with NO human `--by`; the resulting §3 Status line + state.json freeze record name the agent id and `mode: ai-plan-verify`; `add.py status`/`gate-explain` surface this.
  - A task declaring `gate_mode: ai-plan-verify` · `autonomy: auto` with NO `sensitivity:` line at all (the common oneshot/benchmark case) qualifies identically — `_task_sensitivity` returns `None`, which is NOT in the block-list, so `_ai_freeze_allowed` returns `(True, None)`; the AI freeze proceeds on the same double opt-in sign-off, no `sensitivity:` declaration required.
  - The identical task with `sensitivity: security` (or `data`/`architecture`) refuses `--ai-plan-verify` with `ai_freeze_blocked_sensitivity`; a task with a genuinely malformed sensitivity token refuses with `ai_freeze_unknown_sensitivity`; both unchanged by any autonomy or gate_mode setting; the human `add.py freeze --by <name>` path still works for either.
  - `add.py status`/`guide`/`build`/`_build_entry`'s `contract_not_frozen` check need ZERO code change — an AI-frozen §3 is indistinguishable, at the tests->build gate, from a human-frozen one (`_contract_frozen` reads only the `Status:` line).
  - Every pre-existing frozen task (no `mode` key in its state.json freeze record) continues to display and gate exactly as before — this task never retrofits history.
  - `add.py audit` surfaces `ai_freeze_checklist_missing` for any AI-frozen task whose evidence block was later deleted/mangled.
</after>

Assumptions — lowest-confidence first:
<assumptions>
  - [x] RESOLVED (human freeze decision, 2026-07-09): the sensitivity floor is a BLOCK-list of exactly `{"security","data","architecture"}` (+ a malformed `"?"` token, new code `ai_freeze_unknown_sensitivity`) — NOT an allow-list of `"mechanical"`. Undeclared sensitivity, `"mechanical"`, and any other valid project-GLOSSARY class all qualify. No longer open.
  ⚠ [spec] Undeclared-sensitivity tasks qualify for AI-freeze — accepted because the `gate_mode: ai-plan-verify` + `autonomy: auto` double opt-in (both human-declared, both auditable) IS the sign-off, and the common oneshot/benchmark task carries no `sensitivity:` line at all — exactly the case the milestone's speed goal must auto-freeze. Lowest confidence because it is the one place this contract deliberately treats SILENCE (an absent declaration) as equivalent to an explicit safe declaration, a pattern this method otherwise avoids (`_task_sensitivity`'s own docstring: "the engine validates a human-declared token... it never infers it" — here, absence resolves to "not blocked" rather than to a neutral/unknown state); if wrong (a task author omits `sensitivity:` specifically to dodge scrutiny, rather than by oversight): cost is requiring an explicit `sensitivity:` line (any valid non-floor value, including `mechanical`) before ANY AI-freeze — a one-line predicate tightening (`sensitivity is not None` added as a fourth guard before the final `return True, None`), fully isolated, no other section of this contract changes.
  - [ ] `--by` accepts any non-empty string as the agent id with no format validation (e.g. no enforced `agent:` prefix or roster-slug check) — confirm: is a free-text agent identifier acceptable, or should it be validated against the roster (`add-design`/`add-build`/`add-verify`/etc. from `PHASE_AGENT`)? Low cost either way — a stricter validator is an additive follow-up, never a breaking change to this contract's shape.
  - [ ] `gate_mode` is task-header-only for this task (no PROJECT.md project-level default) — confirm this matches milestone Scope's silence on a project default; if the human wants one, it is additive (mirrors `_project_autonomy`) and does not reshape M1-M6.
  - [ ] the "AI-verify record" 4-item checklist is the RIGHT and SUFFICIENT set (anchors/rules/shape/flag) — confirm it does not also need a "no HARD-STOP-worthy content spotted" self-check; current design deliberately keeps the AI verifier's job scoped to DIRECTION-BUNDLE COHERENCE (spec/scenarios/contract shape), not a security review — security review is out of scope for a contract freeze and remains the VERIFY gate's job (unaffected, still HARD-STOP there).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: _GATE_MODES is a closed 2-tuple, importable   # M1
  Given add_engine/constants.py
  When _GATE_MODES is read
  Then it equals ("human", "ai-plan-verify")
  And it is listed in __all__

Scenario: _task_gate_mode resolves a declared token, absence, and an unknown token   # M2
  Given a TASK.md header with "gate_mode: ai-plan-verify"
  When _task_gate_mode(hdr) is called
  Then it returns "ai-plan-verify"
  And _task_gate_mode(hdr) on a header with no gate_mode line returns None
  And _task_gate_mode(hdr) on a header with "gate_mode: bogus" returns "?"

Scenario: _ai_freeze_allowed permits an undeclared sensitivity (the common oneshot/benchmark case)   # M3
  Given gate_mode="ai-plan-verify", sensitivity=None (no sensitivity: line at all), autonomy="auto"
  When _ai_freeze_allowed(gate_mode, sensitivity, autonomy) is called
  Then it returns (True, None)

Scenario: _ai_freeze_allowed permits the literal "mechanical" token   # M3
  Given gate_mode="ai-plan-verify", sensitivity="mechanical", autonomy="auto"
  When _ai_freeze_allowed(gate_mode, sensitivity, autonomy) is called
  Then it returns (True, None)

Scenario: _ai_freeze_allowed permits an other valid project-GLOSSARY class   # M3
  Given gate_mode="ai-plan-verify", sensitivity="compliance" (a recognized project-declared class, not one of the base four), autonomy="auto"
  When _ai_freeze_allowed(gate_mode, sensitivity, autonomy) is called
  Then it returns (True, None)

Scenario: _ai_freeze_allowed blocks a human-mode task   # M3 / R:ai_freeze_not_opted_in
  Given gate_mode=None (or "human")
  When _ai_freeze_allowed(gate_mode, "mechanical", "auto") is called
  Then it returns (False, "ai_freeze_not_opted_in")

Scenario: _ai_freeze_allowed blocks a non-auto autonomy   # M3 / R:ai_freeze_requires_auto
  Given gate_mode="ai-plan-verify", sensitivity=None, autonomy="conservative"
  When _ai_freeze_allowed(...) is called
  Then it returns (False, "ai_freeze_requires_auto")
  And this holds regardless of sensitivity — autonomy is checked before the sensitivity branch

Scenario: _ai_freeze_allowed blocks every human-floor sensitivity (outline)   # M3 / R:ai_freeze_blocked_sensitivity
  Given gate_mode="ai-plan-verify", autonomy="auto", sensitivity=<sens>
  When _ai_freeze_allowed(...) is called
  Then it returns (False, "ai_freeze_blocked_sensitivity")
  Examples: sens = "security" | "data" | "architecture"

Scenario: _ai_freeze_allowed fails closed on a malformed sensitivity token   # M3 / R:ai_freeze_unknown_sensitivity
  Given gate_mode="ai-plan-verify", autonomy="auto", sensitivity="?" (a real-but-unrecognized token — not in the project's sensitivity vocabulary)
  When _ai_freeze_allowed(...) is called
  Then it returns (False, "ai_freeze_unknown_sensitivity")
  And this is a DIFFERENT code from ai_freeze_blocked_sensitivity — a garbled declaration is distinguishable, in the audit trail, from a correctly-declared human-floor class

Scenario: cmd_freeze --ai-plan-verify writes the AI freeze record on a qualifying task   # M4
  Given a task at contract phase, gate_mode: ai-plan-verify, sensitivity: mechanical, autonomy: auto,
        a well-formed lowest-confidence flag, and a complete "AI-verify record" (all 4 items [x], Verified by: filled)
  When I run `add.py freeze --ai-plan-verify --by agent:add-design`
  Then §3's Status line reads "FROZEN @ v1 — approved by agent:add-design"
  And a new line directly beneath it reads "Freeze mode: ai-plan-verify — verified by agent:add-design at <timestamp>"
  And state.json's freeze record for the task has "mode": "ai-plan-verify" and "verified": {"anchors": true, "rules": true, "shape": true, "flag": true}
  And `_contract_frozen(raw3)` is True

Scenario: the human freeze path is untouched   # M5
  Given the same qualifying task as above, but before any --ai-plan-verify call
  When I run `add.py freeze --by "A Human"` (no --ai-plan-verify)
  Then §3's Status line reads "FROZEN @ v1 — approved by A Human"
  And no "Freeze mode:" line is added
  And state.json's freeze record has no "mode" key
  And this is byte-identical to pre-existing freeze behavior

Scenario: the AI-verify record block is read and validated like the advisor 3-lens slice   # M6
  Given a §3 with an "AI-verify record" sub-block where all 4 items are "- [x]" and "Verified by: agent:x · at: 2026-07-09T00:00:00Z"
  When _ai_verify_checklist_complete(raw3) is called
  Then it returns True
  And _ai_verify_slice(raw3) returns only that sub-block's text, matching _advisor_slice's heading-bounded-slice idiom

Scenario: audit flags a post-freeze deleted AI-verify record   # M7
  Given a task whose state.json freeze.mode == "ai-plan-verify"
  And its CURRENT §3 no longer has a complete "AI-verify record" block (hand-edited away)
  When `add.py audit` runs
  Then the glint "ai_freeze_checklist_missing" lists this task
  And the audit outcome is MEASURE-NOT-BLOCK (exit code unaffected, same as unflagged_freeze's residual glint)

Scenario: gate-explain surfaces the AI-plan-verify-gate predicate outcome   # M8
  Given a task declaring gate_mode: ai-plan-verify
  When I run `add.py gate-explain <slug>`
  Then the output includes a line naming whether an AI freeze is currently allowed or blocked, and the specific code if blocked
  And the existing advisor-gate-relax line is unchanged and still printed

Scenario: GLOSSARY gains the gate_mode term with the advisor-gate-relax reconciliation note   # M9
  Given this task's §3 "Glossary deltas:" line
  When the task reaches done and `add.py fold` runs
  Then .add/GLOSSARY.md gains a "gate_mode" entry
  And the entry states both AI-plan-verify-gate and advisor-gate-relax key off the literal "mechanical" token at two different trust boundaries (freeze vs. verify-completion)

Scenario: the three engine trees stay byte-identical after the constants/predicates/add.py edits   # M10
  Given add-method/tooling/, .add/tooling/, and add-method/src/add_method/_bundled/tooling/
  When the BUILD phase edits constants.py, predicates.py, and add.py
  Then md5(canonical add.py) == md5(dogfood add.py) == md5(bundled add.py)
  And the same holds for add_engine/constants.py and add_engine/predicates.py

Scenario: --ai-plan-verify without --by refuses before any write   # R:ai_freeze_missing_actor
  Given a qualifying task (gate_mode/sensitivity/autonomy all pass)
  When I run `add.py freeze --ai-plan-verify` (no --by)
  Then it dies with "ai_freeze_missing_actor"
  And §3's Status line is untouched (still DRAFT)
  And no state.json freeze record is written

Scenario: --ai-plan-verify with an incomplete AI-verify record refuses   # R:ai_freeze_checklist_incomplete
  Given a qualifying task whose "AI-verify record" has an unchecked item (e.g. "- [ ] §0 anchors resolve")
  When I run `add.py freeze --ai-plan-verify --by agent:x`
  Then it dies with "ai_freeze_checklist_incomplete"
  And §3's Status line is untouched (still DRAFT)

Scenario: the 4 pre-existing freeze checks still fire unchanged on the AI path   # edge case
  Given a task at contract phase whose §3 has NO well-formed lowest-confidence flag
  When I run `add.py freeze --ai-plan-verify --by agent:x` (otherwise qualifying)
  Then it dies with "unflagged_freeze" (the SAME code the human path uses)
  And no AI-specific check (opted-in/autonomy/sensitivity/checklist) is even reached — precondition ordering holds

Scenario: a declared gate_mode never forces the AI path or blocks the human path   # edge case
  Given a task declaring gate_mode: ai-plan-verify but sensitivity: architecture
  When I run `add.py freeze --by "A Human"` (no --ai-plan-verify flag)
  Then it succeeds exactly as the ordinary human freeze always has
  And the gate_mode declaration has no bearing on the human path

Scenario: security sensitivity is doubly blocked — freeze AND the unrelated verify gate   # edge case
  Given a task with sensitivity: security, gate_mode: ai-plan-verify, autonomy: auto
  When I run `add.py freeze --ai-plan-verify --by agent:x`
  Then it dies with "ai_freeze_blocked_sensitivity"
  And this is independent of and in addition to the existing VERIFY-gate HARD-STOP for security (unaffected by this task)

Scenario: a re-freeze (change request) via the AI path re-validates from scratch   # edge case
  Given a task previously AI-frozen at v1, now returned to SPECIFY via a change request and re-drafted to contract
  When I run `add.py freeze --ai-plan-verify --by agent:x` again
  Then _next_freeze_version returns "v2" (unchanged existing logic)
  And ALL AI-path checks (opted-in/autonomy/sensitivity/checklist) re-run against the CURRENT state — nothing is grandfathered from v1's approval
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
AI-PLAN-VERIFY-GATE — the frozen shape (add-method/tooling/add.py + add_engine/{constants,predicates}.py, synced ×3)

NEW CONSTANT — add_engine/constants.py (joins __all__, sibling of _AUTONOMY_LEVELS/_SENSITIVITY_VALUES/_STREAMS_POSTURES)
_GATE_MODES: tuple[str, ...] = ("human", "ai-plan-verify")
  # closed 2-way enum. Absent header line -> None from the resolver, treated as "human" by
  # every caller (fail-closed default — a NEW trust-loosening capability never silently activates,
  # unlike _AUTONOMY_LEVELS whose absent-default is the already-trusted "auto").

NEW HEADER RESOLVER — add.py (mirrors _task_sensitivity / _autonomy_level exactly)
_task_gate_mode(hdr: str) -> str | None
  # anchored regex (?:^|·)[ \t]*gate_mode:[ \t]*([^\s<#|]+), HTML comments already stripped by
  # _task_header. Returns a member of _GATE_MODES, None (absent), or "?" (real-but-unknown token).
  # PURE — validates a human-declared token, never infers one (mirrors every sibling resolver).

NEW PURE PREDICATE — add_engine/predicates.py (beside _phase_owner/_phase_bundle, same fail-closed idiom)
_ai_freeze_allowed(gate_mode: str | None, sensitivity: str | None, autonomy: str) -> tuple[bool, str | None]
    if gate_mode != "ai-plan-verify":                       return False, "ai_freeze_not_opted_in"
    if autonomy   != "auto":                                 return False, "ai_freeze_requires_auto"
    if sensitivity in ("security", "data", "architecture"):  return False, "ai_freeze_blocked_sensitivity"
    if sensitivity == "?":                                   return False, "ai_freeze_unknown_sensitivity"
    return True, None
  # BLOCK-LIST (human freeze decision, 2026-07-09): the human floor is the 3 NAMED classes
  # {security,data,architecture} plus a MALFORMED "?" token (its own code, fails closed on a
  # real-but-unrecognized declaration). UNDECLARED sensitivity (None), the literal "mechanical"
  # token, and any OTHER valid project-GLOSSARY-declared class ALL QUALIFY for AI-freeze — this
  # is deliberately NOT an allow-list of one. Rationale: matches the intake choice "all except
  # security/data/architecture"; undeclared qualifying is safe because it is never silent — the
  # DOUBLE opt-in (`gate_mode: ai-plan-verify` AND `autonomy: auto`, both human-declared) IS the
  # sign-off, and the common oneshot/benchmark task carries no sensitivity line at all, which is
  # exactly the case the speed goal must auto-freeze. Only a MALFORMED "?" fails closed.
  # RECONCILIATION WITH advisor-gate-relax (named explicitly, not left implicit):
  #   - advisor-gate-relax   = the VERIFY/COMPLETION boundary; requires a recorded, clean Advisor
  #                            3-lens verdict (§6); relaxes "a human must own a high-risk gate";
  #                            ALLOW-lists exactly the literal token "mechanical" (add.py ~1566).
  #   - ai-plan-verify-gate  = the CONTRACT-FREEZE boundary (this task); requires gate_mode
  #                            opt-in + autonomy:auto + a recorded AI-verify checklist (§3);
  #                            relaxes "a human must approve the frozen contract"; BLOCK-lists
  #                            {security,data,architecture} + malformed, passing everything else
  #                            (including undeclared and "mechanical").
  #   These are TWO RELATED BUT NOT IDENTICAL floors at two different boundaries — sibling
  #   gates, not one shared floor concept. advisor-gate-relax is the narrower of the two (opt-in
  #   only for "mechanical"); ai-plan-verify-gate is broader by design, per the intake decision.
  #   Security remains a HARD-STOP at the VERIFY boundary regardless (unaffected by this task);
  #   this predicate additionally ensures a security-sensitive contract can never even reach an
  #   AI-frozen state in the first place — defense in depth, not a new HARD-STOP mechanism.

EXTENDED COMMAND — add.py cmd_freeze (additive branch; the flagless path is BYTE-IDENTICAL to today)
add.py freeze --ai-plan-verify --by AGENT_ID [slug]
  Precondition order (validate-then-write; nothing is written until ALL pass):
    1. [runs for every freeze] already_frozen -> contract_not_drafted -> unflagged_freeze
    1b. sensitivity_invalid (the existing `_task_sensitivity(...) == "?"` guard) runs ONLY on the
       HUMAN path. On the --ai-plan-verify path it is SKIPPED, so a malformed "?" token flows to
       _ai_freeze_allowed and yields the DISTINCT `ai_freeze_unknown_sensitivity` (v2 amendment
       2026-07-09 — makes that code CLI-reachable; both paths still refuse a malformed token, so
       fail-safe is preserved and the human path stays byte-unchanged).
    2. [NEW, only when --ai-plan-verify given]
       a. --by present?                     else -> "ai_freeze_missing_actor"
       b. _ai_freeze_allowed(_task_gate_mode(hdr), _task_sensitivity(hdr, valid=_project_sensitivity_values(root)),
                             _effective_autonomy(root, state, slug))
                                             else -> the returned code (ai_freeze_not_opted_in |
                                                     ai_freeze_requires_auto | ai_freeze_blocked_sensitivity |
                                                     ai_freeze_unknown_sensitivity)
       c. _ai_verify_checklist_complete(raw3)  else -> "ai_freeze_checklist_incomplete"
  On success, writes (TASK.md first, then state — crash-safe, mirrors today):
    §3 Status line:  "Status: FROZEN @ vN — approved by <AGENT_ID>"        (IDENTICAL format/regex
                                                                             to the human path)
    NEW additive line directly beneath Status:
                     "Freeze mode: ai-plan-verify — verified by <AGENT_ID> at <ISO-8601 UTC ts>"
    state["tasks"][slug]["freeze"] = {"version": vN, "frozen_at": ts, "approved_by": AGENT_ID,
                                       "actor": <CLI-runner's actor stamp, unchanged>,
                                       "mode": "ai-plan-verify",
                                       "verified": {"anchors": true, "rules": true,
                                                    "shape": true, "flag": true}}
  4xx -> "ai_freeze_not_opted_in" | "ai_freeze_requires_auto" | "ai_freeze_blocked_sensitivity"
       | "ai_freeze_unknown_sensitivity" | "ai_freeze_missing_actor" | "ai_freeze_checklist_incomplete"
       | "already_frozen" | "contract_not_drafted" | "unflagged_freeze" | "sensitivity_invalid"

add.py freeze --by NAME [slug]      (no --ai-plan-verify — TODAY'S PATH, UNCHANGED)
  200 -> §3 Status: "FROZEN @ vN — approved by NAME"; state freeze record has NO "mode" key
       (absence of "mode", not "mode": "human", IS the human-mode signal — back-compat with
       every already-frozen task's existing state record)

NEW §3 SUB-BLOCK — task template addition (required only when gate_mode: ai-plan-verify)
  "### AI-verify record (required when gate_mode: ai-plan-verify)"
    - [ ] §0 GROUND anchors resolve in the current tree
    - [ ] §1 every Must + every Reject present, each Reject paired with an error code
    - [ ] §3 CONTRACT shape is concrete (no template placeholder text remains)
    - [ ] Least-sure flag surfaced and substantive (mirrors unflagged_freeze's own bar)
    Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>
  Readers (add.py, mirror _advisor_slice's heading-bounded-slice idiom):
    _ai_verify_slice(raw3) -> str            # the sub-block text, "" if absent (fail-safe)
    _ai_verify_checklist_complete(raw3) -> bool   # True iff all 4 items "- [x]" AND "Verified by:"
                                                   # has non-empty content

NEW AUDIT GLINT — add.py cmd_audit (MEASURE-NOT-BLOCK, symmetric to the existing unflagged_freeze
                                     residual check at ~line 6621-6624)
  ai_freeze_checklist_missing: for any task whose state.json freeze.mode == "ai-plan-verify", if the
  CURRENT §3 fails _ai_verify_checklist_complete, flag it — catches a post-freeze hand-edit that
  deletes the AI-verify evidence. Never engine-blocking; a human spot-audit is the backstop.

READ-ONLY EXTENSION — add.py _gate_explain (existing function, additive print line only)
  when the task declares gate_mode: ai-plan-verify, prints the _ai_freeze_allowed outcome + code,
  beside the existing advisor-gate-relax explain line (unchanged).

UNCHANGED, CITED FOR COMPLETENESS (no code change; the reason the tests->build gate needs none):
  _contract_frozen(raw3)          — reads only the Status: FROZEN line; agnostic to who wrote it
  add.py _build_entry's contract_not_frozen check (~line 1043) — sees an AI-frozen §3 identically
  _next_freeze_version            — reused unchanged (v1/N+1 versioning is freeze-mode-agnostic)
  the VERIFY-gate advisor-gate-relax check (~line 1566-1573) — a different boundary, untouched

Schema: TASK.md §3 (new sub-block, additive) · state.json tasks.<slug>.freeze (2 new optional keys:
  mode, verified) · add_engine/constants.py (_GATE_MODES, joins __all__) · no DB/network/schema.
```

Glossary deltas:
  - `gate_mode`: the two-way DIRECTION-freeze declaration on a task (`human` default | `ai-plan-verify`), read from a task-header `gate_mode:` line; when `ai-plan-verify` AND the task's effective autonomy is `auto` AND a recorded "AI-verify record" checklist is complete, an AI agent (not a human) may perform the §3 contract freeze via `add.py freeze --ai-plan-verify --by <agent-id>` — for any sensitivity EXCEPT `security`/`data`/`architecture` (the human floor) or a malformed token; undeclared sensitivity, `mechanical`, and any other valid project-GLOSSARY class all qualify. The human floor classes — and a malformed sensitivity declaration — always fall back to the human freeze path; security additionally remains a HARD-STOP at the unrelated VERIFY gate.
  - `AI-plan-verify-gate`: the mechanism (predicate + checklist + freeze-record extension) implementing `gate_mode: ai-plan-verify`. Sibling of `advisor-gate-relax` at a DIFFERENT trust boundary (contract-freeze vs. verify-completion) — related but NOT identical floors: this gate BLOCK-lists `{security,data,architecture}` (+ malformed) and passes everything else, while `advisor-gate-relax` ALLOW-lists only the literal `"mechanical"` token at the VERIFY boundary. Two sibling gates, two different-shaped floors — never described as interchangeable.

Least-sure flag surfaced at freeze: [spec] undeclared-sensitivity tasks qualify for AI-freeze — accepted because the gate_mode+auto double opt-in is the human sign-off; if wrong, require an explicit sensitivity: line before any AI-freeze.

Status: FROZEN @ v2 — approved by Tin Dang
Reported: no

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new ai-plan-verify-gate surface (_GATE_MODES, _task_gate_mode, _ai_freeze_allowed, cmd_freeze's --ai-plan-verify branch, _ai_verify_slice/_ai_verify_checklist_complete, the audit ai_freeze_checklist_missing glint, the gate-explain additive line) — behavioral, not internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_value_and_all, test_importable_via_star_import: _GATE_MODES == ("human","ai-plan-verify"), listed in __all__, re-exported on add · covers: M1
  - test_declared_token, test_absent_returns_none, test_unknown_token_returns_qmark, test_inline_slug_line_form: _task_gate_mode resolves declared/absent/unknown · covers: M2
  - test_permits_undeclared_sensitivity, test_permits_mechanical, test_permits_other_valid_project_class, test_blocks_human_mode, test_blocks_non_auto_autonomy_regardless_of_sensitivity, test_blocks_every_human_floor_sensitivity, test_fails_closed_on_malformed_sensitivity: the BLOCK-list predicate · covers: M3, R:ai_freeze_not_opted_in, R:ai_freeze_requires_auto, R:ai_freeze_blocked_sensitivity, R:ai_freeze_unknown_sensitivity
  - test_writes_status_and_freeze_mode_line_and_state, test_undeclared_sensitivity_qualifies: cmd_freeze --ai-plan-verify happy path, additive Status+state keys · covers: M4
  - test_human_path_unaffected_by_gate_mode_declaration, test_plain_freeze_no_flag_matches_pre_existing_behavior: the flagless human path is byte-identical, no mode key · covers: M5
  - test_complete_checklist_true, test_incomplete_checklist_false, test_absent_block_is_fail_safe_empty_and_false, test_empty_verified_by_is_incomplete: _ai_verify_slice/_ai_verify_checklist_complete mirror _advisor_slice's idiom · covers: M6
  - test_intact_record_not_flagged, test_mangled_record_flagged_measure_not_block, test_deleted_block_flagged, test_human_freeze_never_flagged, test_json_findings_carry_the_code: audit's ai_freeze_checklist_missing residual glint · covers: M7
  - test_allowed_outcome_printed, test_blocked_outcome_printed_with_code, test_human_mode_task_prints_no_ai_plan_verify_line, test_read_only: gate-explain surfaces the predicate outcome, read-only · covers: M8
  - test_add_py_trees_byte_identical, test_constants_trees_byte_identical, test_predicates_trees_byte_identical: 3-tree byte parity · covers: M10
  - test_missing_by_refuses_before_any_write: covers: R:ai_freeze_missing_actor
  - test_incomplete_checklist_refuses: covers: R:ai_freeze_checklist_incomplete
  - test_preexisting_checks_still_fire_unchanged_on_ai_path: unflagged_freeze fires first, no AI-specific check even reached · covers: edge case (precedence)
  - test_gate_mode_declared_never_forces_ai_path_or_blocks_human_path: a declared gate_mode never forces/blocks the human path · covers: edge case
  - test_security_sensitivity_doubly_blocked_at_freeze: the freeze-gate block is independent of the unrelated VERIFY-gate HARD-STOP · covers: edge case
  - test_refreeze_after_change_request_revalidates_from_scratch, test_refreeze_reevaluates_and_can_now_refuse: a re-freeze re-validates from scratch, nothing grandfathered from v1 · covers: edge case
</test_plan>
Tests live in: `add-method/tooling/test_ai_plan_verify_gate.py` (41 tests) · ran RED (AttributeError: module 'add' has no attribute '_task_gate_mode'/'_ai_freeze_allowed'/'_ai_verify_slice'/'_ai_verify_checklist_complete'; argparse 'unrecognized arguments: --ai-plan-verify') before Build — confirmed by reverting the 3 canon engine files (add.py, add_engine/constants.py, add_engine/predicates.py) via `git stash` while the dogfood/bundled trees kept the implementation: 38/41 tests failed for the right reason, plus the 3 tree-parity tests correctly failed on the deliberate 3-tree divergence (2 != 1).

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/.add/tooling/templates/` `.add/SEAMS.md` `tmp/` `.add/`
Strategy (ordered batches): 1. `add_engine/constants.py` — `_GATE_MODES` (joins `__all__`, sibling of `_SENSITIVITY_VALUES`). 2. `add_engine/predicates.py` — `_ai_freeze_allowed`, beside `_phase_owner`/`_phase_bundle`, same fail-closed idiom. 3. `add.py` — `_GATE_MODE_RE` + `_task_gate_mode` (mirrors `_task_sensitivity`, placed right after it); `_ai_verify_slice`/`_ai_verify_checklist_complete` (mirrors `_advisor_slice`/`_advisor_verdict_is_pass`, placed right after `_advisor_no_residue`); the `cmd_freeze` additive `--ai-plan-verify`/`--by`-required branch inserted between the existing 4 checks and the write block; the argparse `--ai-plan-verify` flag; the `_gate_explain` additive print line; the `cmd_audit`/`_audit_findings` `ai_freeze_checklist_missing` residual glint beside `unflagged_freeze`. 4. `templates/TASK.fast.md.tmpl` — the "### AI-verify record" sub-block (TASK.md.tmpl itself has zero byte-ceiling headroom — 21B total / 2B comment — so the literal scaffold lives in the fast lane only, mirroring the pre-existing "Least-sure flag surfaced at freeze:" precedent, which is ALSO fast-lane-only; the full lane keeps its existing single merged §3 comment untouched). 5. Propagate all 3 (+ the local gitignored 4th `add-method/.add/tooling/` dogfood copy, template file only) byte-identically; purge every tree's `__pycache__`. 6. Re-pin `ENGINE_MD5`/`ENGINE_PKG_MD5`; re-resolve + re-pin the 2 SEAMS.md line anchors the growth shifted (`_declared_scope` add.py 4918→5002, `_section_unfilled` predicates.py 60→80). 7. New red suite (`test_ai_plan_verify_gate.py`, 41 tests) confirmed RED for the right reason (missing implementation — proven by reverting only the 3 canon engine files via `git stash` while the dogfood/bundled trees kept the build, so the tree-parity tests also failed correctly on the deliberate divergence), then green. 8. Full tooling suite + `add.py check` green.
Approach (domain strategy): additive branch + closed-enum + anchored-header-resolver + heading-bounded-slice — three idioms already established in this codebase (`_AUTONOMY_LEVELS`/`_autonomy_level`, `_SENSITIVITY_VALUES`/`_task_sensitivity`, `_advisor_slice`), reused verbatim rather than inventing a 4th parsing style (methodology-engine-dev's "no hidden magic"); `cmd_freeze` keeps ONE implementation with a flag-gated branch rather than a sibling `cmd_ai_freeze`, so the 4 existing preconditions can never drift between two freeze paths (per §1 Framings weighed).
Data strategy: one new closed 2-tuple constant (`_GATE_MODES`), one new state.json freeze-record shape extension (2 optional keys: `mode`, `verified`) — additive, no existing key renamed/removed/retyped; no schema/DB; the §3 "AI-verify record" sub-block is read-only prose parsed by regex, never written by the engine except as literal copy-in-place of the human/AI-authored checklist.
Pattern: mirrors `_AUTONOMY_LEVELS`/`_SENSITIVITY_VALUES` (closed-enum + anchored-declaration-grammar resolver) and `_advisor_slice`/`_advisor_verdict_is_pass`/`_advisor_no_residue` (heading-bounded sub-block reader), both named in §0 Honors; validate-then-write discipline restated from `cmd_freeze`'s own docstring.
Optimization stance: correctness-first, no latency/memory budget — pure regex/dict-lookup/file-read/atomic-write, matching the existing freeze machinery's own risk profile (§0 Context). ⚠ least-trusted facet: the TASK.md.tmpl (full lane) byte ceiling had zero headroom (21B total, 2B comment) for the literal "AI-verify record" scaffold, so it was placed in TASK.fast.md.tmpl only, mirroring the pre-existing flag-line precedent (test_taskmd_lean.py's own note: "flag line lives in TASK.fast + agent-added §3, not here") — a full-lane task opting into gate_mode: ai-plan-verify authors the sub-block freeform in its own §3, guided by this task's own frozen contract + docs, not a template scaffold; disclosed as a build decision, not silently dropped.
Persona (required): methodology-engine-dev
Spawn isolation (default): n/a — no subagent spawned for this build; edits made directly by the build agent in the shared tree.
Known-problem fixes: stray bytecode in any of the 3 `__pycache__` dirs breaking parity guards → purge before/after every parity-sensitive run · SEAMS.md line-anchors drifting on add.py/predicates.py growth → re-resolve + re-pin after the edit (2 anchors moved) · a local gitignored 4th template mirror (`add-method/.add/tooling/templates/`) not covered by the 3 official engine trees but still asserted by `test_strategy_facets.py`/`test_facet_adr_harvest.py` → propagate there too, caught by running the FULL suite (not just the new module) before claiming green · fresh new-authored prose accidentally reusing a banned ubiquitous-language term ("least-sure" instead of "lowest-confidence") in the fast-lane template bullet → caught by `test_ubiquitous_language.py`'s extended-surface scan, reworded to the sanctioned replacement · a test-harness `(text, code)` vs `(code, text)` unpacking-order slip across a few `_run()` call sites in the new suite → caught immediately by the first green run (TypeError, not a silent pass), fixed before claiming green.
Strategy actually used: as planned (see Strategy above), with two disclosed deviations: (1) the AI-verify-record template scaffold went into TASK.fast.md.tmpl only, not TASK.md.tmpl (byte-ceiling headroom forced the choice, precedented by the existing flag-line split); (2) `cmd_audit`'s new `ai_freeze_checklist_missing` finding was verified to flip `add.py audit`'s own exit code to 1 (like its sibling `unflagged_freeze`) — MEASURE-NOT-BLOCK means the finding never refuses an ENGINE gate/write, not that the read-only `audit` command's CI-consumed exit code is untouched; the new suite's assertion was corrected to match the real, symmetric precedent rather than an assumed exit-0.
Safety rule (feature-specific): validate-then-write on the AI path — every new refusal (`ai_freeze_missing_actor` → the block-list predicate → `ai_freeze_checklist_incomplete`) fires strictly AFTER the 4 pre-existing checks and strictly BEFORE any write (TASK.md then state.json, crash-safe); the flagless human path executes zero new code (proven by `HumanFreezePathUnchangedTest` + the full pre-existing freeze suites staying green unmodified).
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 41/41 new (`test_ai_plan_verify_gate.py`) + 24/24 pre-existing freeze regression (`test_freeze_command.py`/`test_freeze_before_build_gate.py`/`test_freeze_gate_universal.py`), all green; re-run live during this verify (`python3 -m unittest test_ai_plan_verify_gate test_freeze_command test_freeze_before_build_gate test_freeze_gate_universal` → `Ran 65 tests ... OK`)
- [x] coverage did not decrease — 100% of the new surface exercised (constant/resolver/predicate/command-branch/slice/checklist/audit-glint/gate-explain-line), confirmed by mutation-probe (2 injected bugs, both caught — see Refute-read)
- [x] no test or contract was altered during build — `git diff --stat` on the 3 pre-existing freeze suites is empty (untouched); §3 CONTRACT text matches the implementation verbatim (verified read-for-read below); this task's own untracked TASK.md/state.json show a single frozen §3 (v1, human-approved) with no re-freeze history
- [x] the green was EARNED — see Refute-read verdict below: 2 live mutation-probes (security floor + checklist gate), both caught by the suite including CLI-integration-level tests, not just pure-function unit tests
- [x] concurrency / timing of the risky operation is safe — no new IO/locking/subprocess/threading surface; pure regex/dict-lookup + the pre-existing `_atomic_write`/`save_state` (unchanged, TASK.md-then-state write order preserved)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only (`re`, `hashlib`, `json`, `pathlib`), no new third-party import, no `--by` value ever eval'd/exec'd (plain string interpolation into text/dict only)
- [x] layering & dependencies follow CONVENTIONS.md — `_ai_freeze_allowed` lives in `add_engine/predicates.py` (engine-modularization discipline, confirmed: `add._ai_freeze_allowed is engine_predicates._ai_freeze_allowed`), `add.py` re-exports via star-import + owns the CLI/IO glue only
- [ ] a person reviewed and approved the change — PENDING: this §6 is the evidence bundle for that human review (sensitivity: architecture → human-owned gate; see GATE RECORD below)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a qualifying task (`gate_mode: ai-plan-verify` · `autonomy: auto` · sensitivity outside {security,data,architecture} · a complete "AI-verify record") freezes via `add.py freeze --ai-plan-verify --by agent:<id>` with NO human `--by`, writing `Status: FROZEN @ vN — approved by <id>` + a `Freeze mode: ai-plan-verify — verified by <id> at <ts>` line beneath it — confirmed by `test_ai_plan_verify_gate.py::CmdFreezeAiPathHappyTest` (green) + a live re-run in this verify (same output reproduced ad hoc)
- [x] `add.py freeze --by NAME` (no flag) on any task, regardless of its `gate_mode:` declaration, is byte-identical to pre-task behavior — no new §3 line, no `mode`/`verified` state keys — confirmed by `test_ai_plan_verify_gate.py::HumanFreezePathUnchangedTest` (green, asserts `assertNotIn("mode", rec)`/`assertNotIn("Freeze mode:", raw3)` — non-vacuous) + the full pre-existing `test_freeze_command.py`/`test_freeze_before_build_gate.py`/`test_freeze_gate_universal.py` suites (24/24) staying green, `git diff --stat`-confirmed UNMODIFIED by this build
- [x] every Reject fires its named code before any write (`ai_freeze_not_opted_in` · `ai_freeze_requires_auto` · `ai_freeze_blocked_sensitivity` · `ai_freeze_unknown_sensitivity` · `ai_freeze_missing_actor` · `ai_freeze_checklist_incomplete`), and the 4 pre-existing checks still fire unchanged and take precedence — confirmed by `AiFreezeAllowedPredicateTest` + `RejectPathsTest` (green) for 5 of 6 codes; **`ai_freeze_unknown_sensitivity` is asserted ONLY at the pure-predicate level, never end-to-end** — live CLI probe (`freeze --ai-plan-verify --by x` on a task with `sensitivity: bogus-token`) shows the PRE-EXISTING `sensitivity_invalid` check (line ~963, unconditional, runs before the AI branch) always intercepts a malformed token first — `ai_freeze_unknown_sensitivity` is dead code from `cmd_freeze`'s perspective (see Deep checks / Refute-read)
- [x] a post-freeze hand-edit that mangles/deletes the §3 "AI-verify record" is caught by `add.py audit`'s `ai_freeze_checklist_missing` glint (MEASURE-NOT-BLOCK) — confirmed by `test_ai_plan_verify_gate.py::AuditChecklistMissingTest` (5/5 green, incl. `--json` finding-code assertion) + live `add.py check` run shows 0 false-positive/false-negative on this task itself (human-frozen, correctly never flagged)
- [x] `add.py gate --explain <slug>` prints the `ai-plan-verify-gate:` line (allowed/blocked+code) for a `gate_mode: ai-plan-verify` task, silent for a human-mode task, and writes nothing — confirmed by `test_ai_plan_verify_gate.py::GateExplainAiPlanVerifyTest` (4/4 green, incl. a byte-identical-state-file read-only assertion)
- [x] the 3 engine trees (`add-method/tooling/`, `.add/tooling/`, `add-method/src/add_method/_bundled/tooling/`) stay byte-identical for `add.py`/`add_engine/constants.py`/`add_engine/predicates.py`, and `ENGINE_MD5`/`ENGINE_PKG_MD5` are re-pinned to the new digests — confirmed by `md5 -q` across the 3 trees live in this verify (`add.py`→`4b61de4f9dff69f2b8232b83bd763726`, `predicates.py`→`a76c353c0e66693d515878eb61062993`, all 3 trees matching) + `EngineTreeParityTest` (3/3 green) both before and after 2 mutation-probes (restored each time, re-confirmed identical)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — confirmed via `mcp__serena__find_referencing_symbols` on the canonical tree: `_ai_freeze_allowed` is imported into `add.py` (line 310, `from add_engine.predicates import (...)`) and called at `cmd_freeze` (add.py:975) + `_gate_explain` (add.py:1597); `_task_gate_mode` called at `cmd_freeze` (add.py:975, nested) + `_gate_explain` (add.py:1595); `_ai_verify_checklist_complete` called at `cmd_freeze` (add.py:980) + `_audit_findings` (add.py:6711, the `ai_freeze_checklist_missing` glint); `_ai_verify_slice` called inside `_ai_verify_checklist_complete` (add.py:1519); `_GATE_MODES` listed in `constants.__all__` (line 34) and re-exported into `add` (confirmed by `test_importable_via_star_import`). Every new symbol has >=1 real caller beyond its own definition/tests.
- [x] DEAD-CODE (code) — **one finding**: `_ai_freeze_allowed`'s `sensitivity == "?"` branch (returns `ai_freeze_unknown_sensitivity`) is UNREACHABLE via `cmd_freeze`. Live-probed: a task with `gate_mode: ai-plan-verify` · `sensitivity: bogus-token` · `autonomy: auto` · a complete AI-verify record, run through `add.py freeze --ai-plan-verify --by agent:x`, dies with `sensitivity_invalid` (the PRE-EXISTING, unconditional check at add.py:963, which runs BEFORE the `ai_plan_verify` branch and already treats any `_task_sensitivity(...) == "?"` as fatal for every freeze path, human or AI) — `_ai_freeze_allowed` is never even reached with `sensitivity="?"` in real use. The 41-test suite only exercises this branch via a direct pure-function call (`test_fails_closed_on_malformed_sensitivity`), never end-to-end, so the green suite never surfaced it. NOT a security bypass (both codes refuse the freeze — fails safe either way), but it contradicts §1's Reject-list / §2's scenario, which both promise `ai_freeze_unknown_sensitivity` as a DISTINCT, CLI-observable outcome ("a garbled declaration is distinguishable, in the audit trail, from a correctly-declared human-floor class") — that distinction does not actually surface in the audit trail today. Recommend a spec delta: either (a) document this as intentional defense-in-depth redundancy and correct the Reject-list wording, or (b) add an integration test asserting the REAL observed code so a future refactor of check-ordering doesn't silently change behavior either way.
- [ ] SEMANTIC (prose / non-code) — n/a, this task's surface is code (deferred to WIRING/DEAD-CODE above); one prose residue noted below (stale "NOT yet approved" sentence)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed via serena + direct read: `_GATE_MODES` (add_engine/constants.py:336, `__all__`:34) · `_task_gate_mode` (add.py:1388) · `_ai_freeze_allowed` (add_engine/predicates.py:39, imported add.py:310) · `cmd_freeze` (add.py:928, AI branch 967-984) · `_ai_verify_slice` (add.py:1504) · `_ai_verify_checklist_complete` (add.py:1515) · `_contract_frozen` (add.py:5580) · `_build_entry`'s `contract_not_frozen` check (add.py:1052 region / 1076,1158) · `_next_freeze_version` (add.py:920) · `_gate_explain`/the VERIFY-gate `_relaxed` check (add.py:1595 region / 1650)
- [x] anchors that moved: yes, several — `cmd_freeze` cited §0 line 926 now starts at 928; `_gate_explain`/`_relaxed` cited ~1498/1566 now sit at ~1595/1650; `_next_freeze_version` cited 918 now at 920; `_contract_frozen` cited 5496 now at 5580. All shifts are consistent with the DISCLOSED §5 growth (SEAMS.md re-pin: `_declared_scope` 4918→5002, `_section_unfilled` 60→80) — no silent/undisclosed drift found; every cited symbol still exists and still matches its described behavior.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (add-verify, personas tdd-verifier + security-gatekeeper) · adversarially checked:
  1. **Security-floor mutation-probe**: `add_engine/predicates.py` line `if sensitivity in ("security","data","architecture")` mutated to `if False and sensitivity in (...)` (bypass). Result: 6 tests failed, incl. the CLI-integration test `RejectPathsTest.test_security_sensitivity_doubly_blocked_at_freeze` which drives the real `freeze --ai-plan-verify` command end-to-end — proves the floor is caught at the integration level, not just the pure-function level. Mutation reverted; 3-tree md5 parity re-confirmed identical (`a76c353c0e66693d515878eb61062993` across all 3 trees, pre- and post-probe).
  2. **Checklist-gate mutation-probe**: `add.py`'s `if not _ai_verify_checklist_complete(raw3): _die(...)` in `cmd_freeze` mutated to `if False and not ...` (bypass). Result: 2 tests failed (`RejectPathsTest.test_incomplete_checklist_refuses` + tree-parity). Reverted; parity re-confirmed (`4b61de4f9dff69f2b8232b83bd763726` across all 3 trees).
  3. **Double-opt-in live CLI probes** (not just unit tests): (a) `gate_mode: ai-plan-verify` alone, task's template-scaffolded default `autonomy: auto` present → succeeds — this is the project/template default, not a bypass of a declared floor; (b) `autonomy: auto` alone with NO `gate_mode:` line → refused `ai_freeze_not_opted_in`; (c) `sensitivity: architecture` + `gate_mode: ai-plan-verify` + scaffolded-default `autonomy: auto` (no extra explicit autonomy line) → still refused `ai_freeze_blocked_sensitivity`. The security-relevant half of the floor (the sensitivity block-list) holds unconditionally regardless of how the autonomy half was declared — see Advisor Security lens for the one observation this surfaces.
  4. Read all 41 new tests line-by-line for overfit/vacuous asserts/stubbed logic: none found — every test drives either the pure predicate directly or the full `add.py` CLI via a real temp-dir project (`_Harness.setUp` does a real `init`/`lock`/`new-milestone`/`new-task`), asserting concrete regex/dict-equality/byte-parity outcomes (e.g. `assertEqual(rec["verified"], {...})`, `assertNotRegex(...FROZEN...)`, `assertEqual(self._state(), before)` for a refused write).
  5. `add.py check` (live run: 706 passed, 0 failed) shows zero `rule_coverage_gap` warnings for this task — every §1 Must/Reject traces to a §2 scenario tag or §4 `covers:` line.
  6. This task's OWN §3 was frozen via the HUMAN path (state.json `freeze` record has no `mode` key, `approved_by: "Tin Dang"`, actor stamp matches git identity) — the mechanism obeys its own reflexive floor (`sensitivity: architecture` → human freeze required), a live self-consistency check.
Residue disclosed (non-security, does not block EARNED): the `ai_freeze_unknown_sensitivity` dead-CLI-branch (Deep checks) and a stale prose sentence in this file's own §3 ("Reported: yes ... NOT yet approved" sitting directly beneath an already-`FROZEN`/human-approved Status line — leftover from the design-draft stage, not rewritten post-approval; cosmetic only).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (add-verify)
1. Security: CLEAR — the block-list floor was mutation-probed at both the pure-predicate and CLI-integration level with no bypass found (Refute-read #1); every human-floor sensitivity (security/data/architecture) plus a malformed token still refuses AI-freeze under every autonomy/gate_mode combination tried, including when the "autonomy" half of the double opt-in is only a template/project default rather than a freshly-authored line (Refute-read #3) — the actually-security-relevant half (the sensitivity block-list) is unconditional. One non-security residue: `ai_freeze_unknown_sensitivity` is unreachable via the real CLI (shadowed by the pre-existing `sensitivity_invalid` check) — a contract-fidelity gap, not a bypass, since both codes refuse the freeze.
2. Concurrency: CLEAR — no new IO/locking/subprocess/threading surface introduced; the AI branch is pure regex/dict-lookup, and the only file writes reuse the pre-existing, unchanged `_atomic_write`/`save_state` (TASK.md-then-state ordering preserved, matching the existing freeze machinery's own crash-safety discipline).
3. Architecture: RESIDUE (minor, non-blocking) — (a) the dead `ai_freeze_unknown_sensitivity` branch (Deep checks); (b) the stale "NOT yet approved" sentence in this task's own §3 prose, left over from the pre-approval draft and not rewritten after the human's actual freeze — confusing for a future reader cross-checking Status vs. the prose beneath it, purely cosmetic.
Verdict: PASS
Residue: 2 minor, both non-security, both disclosed above (dead CLI branch for a malformed-sensitivity code; stale approval-prose sentence). Neither weakens the human-floor guarantee this task exists to create.
Binding: advisory — architecture (not "mechanical"; advisor-gate-relax does not apply here — this task's own `autonomy: conservative` already routes its gate to a human)

### GATE RECORD
Reported: yes — this §6 evidence bundle is presented to the orchestrator/human as the verify record below; **no gate has been recorded** (`add.py gate` was deliberately NOT run — this task is `autonomy: conservative`/`sensitivity: architecture`, so a human records the outcome after reviewing this evidence).
RECOMMENDED outcome: PASS — see Refute-read + Advisor 3-lens above for the full evidentiary basis; 2 disclosed non-security residues (dead CLI branch, stale prose) are proposed as a spec delta / doc fix, not blockers.
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-09

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose a new `--ai-plan-verify` flag on the EXISTING `cmd_freeze`, gated by a new task-header `gate_mode:` line + a pure BLOCK-list predicate over (gate_mode, sensitivity, autonomy) — human-required for exactly `{security,data,architecture}` plus a malformed `"?"` token, everything else (undeclared, `mechanical`, any other valid project class) qualifies — mirroring the `_AUTONOMY_LEVELS`/`_SENSITIVITY_VALUES` closed-enum idiom for the resolver shape; rejected a brand-new sibling command (`cmd_ai_freeze`) instead of extending `cmd_freeze` (rejected — duplicates the 4 existing validate-then-write preconditions (already_frozen/contract_not_drafted/unflagged_freeze/sensitivity_invalid), risking drift between two freeze paths; a flag on the same function keeps ONE freeze implementation, additive branch only) · an ALLOW-list of exactly `"mechanical"` mirroring advisor-gate-relax (considered, then rejected by the human freeze decision 2026-07-09 — see §0 Issues/Risks RESOLVED note: it is materially narrower than the milestone's own framing and would silently exclude the common sensitivity-undeclared oneshot/benchmark task the speed goal targets) · a project-level `gate_mode` default in PROJECT.md mirroring `_project_autonomy` (deferred — milestone Scope names only the task-header two-way state; a project default is a natural follow-on but not spec'd here, and defaulting a NEW trust-loosening capability at the project level before its task-level shape is proven is the wrong order).
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — approach: additive branch + closed-enum + anchored-header-resolver + heading-bounded-slice — three idioms already established in this codebase (`_AUTONOMY_LEVELS`/`_autonomy_level`, `_SENSITIVITY_VALUES`/`_task_sensitivity`, `_advisor_slice`), reused verbatim rather than inventing a 4th parsing style (methodology-engine-dev's "no hidden magic"); `cmd_freeze` keeps ONE implementation with a flag-gated branch rather than a sibling `cmd_ai_freeze`, so the 4 existing preconditions can never drift between two freeze paths (per §1 Framings weighed).
- [AI] build — data strategy: one new closed 2-tuple constant (`_GATE_MODES`), one new state.json freeze-record shape extension (2 optional keys: `mode`, `verified`) — additive, no existing key renamed/removed/retyped; no schema/DB; the §3 "AI-verify record" sub-block is read-only prose parsed by regex, never written by the engine except as literal copy-in-place of the human/AI-authored checklist.
- [AI] build — pattern: mirrors `_AUTONOMY_LEVELS`/`_SENSITIVITY_VALUES` (closed-enum + anchored-declaration-grammar resolver) and `_advisor_slice`/`_advisor_verdict_is_pass`/`_advisor_no_residue` (heading-bounded sub-block reader), both named in §0 Honors; validate-then-write discipline restated from `cmd_freeze`'s own docstring.
- [AI] build — optimization stance: correctness-first, no latency/memory budget — pure regex/dict-lookup/file-read/atomic-write, matching the existing freeze machinery's own risk profile (§0 Context). ⚠ least-trusted facet: the TASK.md.tmpl (full lane) byte ceiling had zero headroom (21B total, 2B comment) for the literal "AI-verify record" scaffold, so it was placed in TASK.fast.md.tmpl only, mirroring the pre-existing flag-line precedent (test_taskmd_lean.py's own note: "flag line lives in TASK.fast + agent-added §3, not here") — a full-lane task opting into gate_mode: ai-plan-verify authors the sub-block freeform in its own §3, guided by this task's own frozen contract + docs, not a template scaffold; disclosed as a build decision, not silently dropped.
- [AI] build — strategy used: as planned (see Strategy above), with two disclosed deviations: (1) the AI-verify-record template scaffold went into TASK.fast.md.tmpl only, not TASK.md.tmpl (byte-ceiling headroom forced the choice, precedented by the existing flag-line split); (2) `cmd_audit`'s new `ai_freeze_checklist_missing` finding was verified to flip `add.py audit`'s own exit code to 1 (like its sibling `unflagged_freeze`) — MEASURE-NOT-BLOCK means the finding never refuses an ENGINE gate/write, not that the read-only `audit` command's CI-consumed exit code is untouched; the new suite's assertion was corrected to match the real, symmetric precedent rather than an assumed exit-0.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

