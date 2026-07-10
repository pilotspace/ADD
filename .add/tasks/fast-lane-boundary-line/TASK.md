# TASK: Fast-lane Boundary: line — the fast freeze refuses an undeclared input-format boundary

slug: fast-lane-boundary-line · created: 2026-07-11 · stage: mvp
milestone: quality-floors
autonomy: auto
phase: done
fast: true
oneshot: true
gate_mode: ai-plan-verify

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/add.py` cmd_freeze validate block (already_frozen → contract_not_drafted → unflagged_freeze precedence chain, ~:998-1003; the new guard slots directly after unflagged_freeze so BOTH the human and --ai-plan-verify paths hit it before any write) · `templates/TASK.fast.md.tmpl` §1 (directly after the Accept: line) · `add_engine/taskdoc.py` `_phase_spans` (§1 raw-body read, already imported by add.py) · `engine_pin.py` ENGINE_MD5 (add.py changes ⇒ re-aim; add_engine untouched ⇒ PKG stays) · `.add/SEAMS.md` scope-token-grammar line pin (the guard inserts far above :5324 ⇒ x18 drift re-pin) · add.py+templates ×3 tooling twins (+ the 4th gitignored dogfood template tree)
Context (working folder): quality-floors MILESTONE.md lever 2; evidence = benchmark/results/2026-07-wv1-rep0.md wm2 (the lean arm's red suite spoke naive timestamps — friendlier than the spec's own Z-examples — and shipped the crash green); levers 1+3+4 landed at f9d2303 + bb72452
Honors (patterns / conventions): validate-then-write (every freeze refusal fires before any byte lands) · absent-line grandfathering (legacy fast tasks + the full lane gain NO new refusal) · the unflagged_freeze error-code idiom (`<code>: <slug> ... <repair hint>`) · template/engine edits propagate to every twin before the gate · sibling-suite pins amend only via a TESTS re-cross (task-2 playbook)
Anchors the contract cites: `cmd_freeze` validate block · `_phase_spans(text).get(1)` · `TASK.fast.md.tmpl` §1 `Boundary:` · `boundary_unfilled` · ENGINE_MD5
Ground SHA: `bb72452`
Skip rationale: scenarios — one template line + one freeze guard, §1 Accept covers the three input variants; observe — one optional delta line at the gate

---

## 1 · SPECIFY — the rules

Feature: quality-floors lever 2 — the fast template's §1 gains a `Boundary:` line (≥1 format-variant per external input shape, or an explicit "none"), and freeze refuses a task whose Boundary value is still the bare template placeholder — the wm2 input-dialect floor applied at the fast lane's single approval seam
Must:
  - TASK.fast.md.tmpl §1 gains, directly after the Accept: line: `Boundary: <one format-variant per external input shape the tests must speak — e.g. aware vs naive timestamp · or "none — no external input">`
  - cmd_freeze refuses a task whose §1 carries a `Boundary:` line whose value is a bare unfenced `<...>` placeholder or empty — error code `boundary_unfilled`, fired in the validate block directly after unflagged_freeze, before any write, on BOTH freeze paths (human and --ai-plan-verify)
  - a real value passes · an explicit `none — ...` value passes · a task with NO `Boundary:` line is grandfathered (legacy fast + full lane behavior byte-identical)
  - ENGINE_MD5 re-aimed · SEAMS scope-token-grammar pin re-aimed (x18) · all twins byte-identical
Reject:
  - freeze with a placeholder or empty Boundary value -> "boundary_unfilled"
  - the guard firing on a task WITHOUT the line (full lane / legacy fast) -> "boundary_overreach" (design rejection: grandfathering IS the contract)
  - any TASK.md/state.json byte written before the refusal -> "validate_then_write_violated"
Accept: Given a fast task whose §1 `Boundary:` value is still the bare template placeholder, When `add.py freeze` runs (either path), Then it exits nonzero naming `boundary_unfilled` and §3 stays DRAFT with zero bytes written — while the same task with a real (or explicit "none") value freezes normally, and a line-less legacy task freezes exactly as before
Boundary: the Boundary value itself is the external input — the suite speaks all three variants: bare `<...>` placeholder · real text · explicit `none — ...`
Assumptions: ⚠ fast-template scaffold/byte/lockstep pins in existing suites (test_fast_lane_skips scaffold hints · taskmd-lean ceilings · twin md5s) may pin the §1 span — if wrong: each red pin gets a TESTS re-cross amendment in ITS owning suite; cost: one re-cross loop (the task-2 playbook)

---

## 3 · CONTRACT — freeze the shape

```
TASK.fast.md.tmpl / §1, directly after Accept::
  Boundary: <one format-variant per external input shape the tests must speak
            — e.g. aware vs naive timestamp · or "none — no external input">
cmd_freeze validate block (directly after unflagged_freeze, BOTH paths):
  §1 has a `Boundary:` line AND its value is empty or a bare unfenced <...>
    -> exit nonzero: "boundary_unfilled: <slug>'s §1 Boundary: line still
       carries the template placeholder — declare >=1 format-variant per
       external input shape (or an explicit "none — ..."), then re-freeze"
  no `Boundary:` line -> grandfathered, no new behavior (full lane / legacy fast)
  real value or explicit none -> freeze proceeds unchanged
success: refusal fires before ANY write (§3 stays DRAFT, state.json untouched).
rejections: boundary_unfilled · boundary_overreach (design) · validate_then_write_violated (design).
```

`Least-sure flag surfaced at freeze:` [test] the placeholder-detection rule (empty or bare unfenced `<...>`) may misjudge exotic real values that legitimately start with `<` — mitigated by mirroring `_section_unfilled`'s backtick-fence exemption; if wrong: a legit freeze is refused with a clear repair hint (annoying, never unsafe) — cost: one re-freeze after quoting the value
Status: FROZEN @ v1 — approved by claude-fable-5
Freeze mode: ai-plan-verify — verified by claude-fable-5 at 2026-07-10T18:09:30+00:00

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §0 GROUND anchors resolve in the current tree — cmd_freeze validate chain + unflagged_freeze grepped at :1001, _phase_spans import live, TASK.fast.md.tmpl §1 Accept: line present, SEAMS pin at :5324, all at the Ground SHA
- [x] §1 every Must + every Reject present, each Reject paired with an error code (boundary_unfilled · boundary_overreach · validate_then_write_violated)
- [x] §3 CONTRACT shape is concrete — exact template line text + the guard's exact refusal message and placement
- [x] Lowest-confidence flag surfaced and substantive — placeholder-detection edge (legit `<`-leading values) with the mitigation and its bounded cost
Verified by: claude-fable-5 (session ee9aef91, orchestrator inline) · at: 2026-07-11T04:55:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_fast_boundary_line.py — test_fast_template_carries_boundary_line (scaffold, after Accept:) · test_freeze_refuses_placeholder_boundary (exit nonzero, names boundary_unfilled, §3 stays DRAFT, state.json byte-identical) · test_ai_plan_verify_path_also_refuses · test_real_value_freezes · test_explicit_none_freezes · test_absent_line_grandfathered.
Tests live in: `add-method/tooling/test_fast_boundary_line.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/` `.add/SEAMS.md` `tmp/`
Strategy & known-problem fixes: 1. red suite 2. template line 3. cmd_freeze guard after unflagged_freeze 4. ENGINE_MD5 + SEAMS x18 re-aims 5. twins 6. full suite; traps: guard must read §1 via _phase_spans (never regex the whole file — a §3-fence mention of `Boundary:` must not trigger) · validate-then-write (refuse before the FROZEN stamp lands) · fast-template pins amend only via TESTS re-cross
Approach (domain strategy): methodology-engine-dev stance — a freeze-seam guard is a pure predicate over the §1 raw body + one precedence slot; obvious, correctness-first
Strategy actually used: as planned — guard in the shared validate block directly after unflagged_freeze (so it fires before the ai-path sensitivity check; two test_fast_lane_skips fixtures felt that precedence and were amended via TESTS re-cross to fill their Boundary lines); placeholder rule = empty or bare unfenced `<...>` with a backtick exemption, mirroring _section_unfilled; SEAMS x18 re-pin (:5337); twins ×3 + the 4th dogfood template tree synced.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full tooling suite 3383 passed + 162 subtests, 0 failed; the 2 fixture amendments (test_fast_lane_skips) went through an explicit TESTS re-cross
- [x] green was EARNED — the red suite pins behavior through the live CLI (exit codes, error text, byte-identical state.json/TASK.md on refusal), not the guard's internals; the 5 pre-passing tests pin grandfathering as no-regression
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor): the suite exercises all three Boundary variants the §1 Boundary line declares (bare placeholder · real value · explicit none), and carries an aware Z-timestamp
- [x] no exposed secrets, injection openings, or unexpected dependencies — one validate-only guard, no new imports, no state writes added; ENGINE_MD5 re-aimed 16cd7cca, PKG unchanged

Build expectations (from §1 Accept + §3 CONTRACT): a placeholder/empty §1 Boundary: value refuses BOTH freeze paths with `boundary_unfilled` and zero bytes written; real/none values and line-less legacy tasks freeze exactly as before; the fast template scaffolds the line after Accept: — confirmed by test_fast_boundary_line.py 9/9 + full suite 3383.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-11

