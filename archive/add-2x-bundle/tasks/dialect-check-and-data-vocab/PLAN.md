# TASK: §6 dialect check line + datetime/money/tz ⇒ data sensitivity vocabulary

slug: dialect-check-and-data-vocab · created: 2026-07-11 · stage: mvp
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

Touches (files · symbols): `add-method/tooling/templates/TASK.md.tmpl:127-129` (§6 checklist + `### Deep checks` block — the shallow audit already measures that block, so a dialect bullet there is audit-counted with ZERO new engine code) · `templates/TASK.fast.md.tmpl:79-80` (fast §6 checklist) · `templates/GLOSSARY.md.tmpl:5-15` (`## Sensitivity classes` — guidance must be PROSE, never a `- token:` bullet, or `_SENS_CLASS_LINE_RE` mints a new class) · `.add/GLOSSARY.md` (this project's own, section currently absent) · `sensitivity.md` skill guide ×3 twins · templates ×3 tooling twins; engine_manifest covers add_engine/*.py ONLY → no pin re-aim (add.py untouched)
Context (working folder): quality-floors MILESTONE.md items 3+4; evidence = benchmark/results/2026-07-wv1-rep0.md wm2 root cause
Honors (patterns / conventions): §6 already uses `<how / where>` placeholders (safe to mirror; the v16 tag census binds §1-§4 spans, not §6) · template/guide edits propagate to all twins before the gate · guidance-not-token (base `data` class, no new vocabulary)
Anchors the contract cites: `TASK.md.tmpl ### Deep checks` · `TASK.fast.md.tmpl §6` · `GLOSSARY.md.tmpl ## Sensitivity classes` · `_project_sensitivity_domain` (must stay ()-stable) · `sensitivity.md`
Ground SHA: `f9d2303`
Skip rationale: scenarios — two template lines + two prose entries, §1 Accept covers; observe — one optional delta line at the gate

---

## 1 · SPECIFY — the rules

Feature: quality-floors levers 3+4 — a §6 input-dialect check line in BOTH task templates (audit-counted via the existing Deep-checks/shallow machinery) + the datetime/money/timezone ⇒ `data` sensitivity guidance in the GLOSSARY template, this project's GLOSSARY, and the sensitivity skill guide (wm2 evidence named)
Must:
  - TASK.md.tmpl `### Deep checks` gains `- [ ] DIALECT — the tests speak the same value formats as the spec's own examples (spec-dialect floor): <what confirmed>` — inside the block the `shallow` audit already measures
  - TASK.fast.md.tmpl §6 checklist gains the condensed twin line
  - GLOSSARY.md.tmpl `## Sensitivity classes` gains PROSE guidance (not a bullet): datetime/money/timezone arithmetic ⇒ declare `data` (full lane), wm2 evidence in one clause; `.add/GLOSSARY.md` gains the same section content for THIS project
  - sensitivity.md skill guide names the rule + the wm2 evidence; all template/guide twins byte-identical
  - the guidance mints NO new sensitivity token — `_project_sensitivity_domain` over a fresh render stays ()
Reject:
  - guidance written as a `- token:` bullet -> "vocab_leak" (a new class token would silently widen freeze/status/check vocabulary)
  - a §1-§4 template span gaining a bare angle-tag -> "tag_census_collision" (v16 hazard; §6 only)
Accept: Given the templates render a fresh task, When §6 is read, Then both templates carry the dialect line (full inside Deep checks) AND the GLOSSARY template + project GLOSSARY + sensitivity guide carry the datetime/money/tz ⇒ data rule AND `_project_sensitivity_domain` of a fresh render is unchanged ()
Assumptions: ⚠ template guard suites may pin §6 line counts or exact Deep-checks content — if wrong: those pins red on the new line and each gets a TESTS-re-cross amendment in ITS owning suite (cost: one re-cross loop)

---

## 3 · CONTRACT — freeze the shape

```
TASK.md.tmpl / ### Deep checks (audit-counted via `shallow`):
  - [ ] DIALECT — the tests speak the same value formats as the spec's own examples
        (spec-dialect floor): <what confirmed>
TASK.fast.md.tmpl / §6 checklist:
  - [ ] input dialect held — tests speak the spec's example formats (spec-dialect floor)
GLOSSARY.md.tmpl + .add/GLOSSARY.md / ## Sensitivity classes (PROSE, no bullet):
  "Datetime, money, or timezone arithmetic ⇒ declare `data` …(wm2 evidence clause)"
sensitivity.md (×3 skill twins): the same rule + evidence, one short block.
success: fresh render carries the lines; _project_sensitivity_domain stays ().
rejections: vocab_leak (no `- token:` guidance) · tag_census_collision (§6 only).
```

`Least-sure flag surfaced at freeze:` [test] existing template-guard suites may pin §6/Deep-checks content or counts — the build may red THEIR pins, and each amendment must go through a TESTS re-cross in the owning suite, never a quiet edit; cost if many pin: several re-cross loops
Status: FROZEN @ v1 — approved by claude-fable-5
Freeze mode: ai-plan-verify — verified by claude-fable-5 at 2026-07-10T17:38:23+00:00

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §0 GROUND anchors resolve in the current tree — template line numbers, GLOSSARY tmpl section, sensitivity.md ×3, _SENS_CLASS_LINE_RE reader all grepped at f9d2303
- [x] §1 every Must + every Reject present, each Reject paired with an error code (vocab_leak · tag_census_collision)
- [x] §3 CONTRACT shape is concrete — exact line text per surface
- [x] Lowest-confidence flag surfaced and substantive — template-guard pin collisions with the re-cross cost
Verified by: claude-fable-5 (session ee9aef91, orchestrator inline) · at: 2026-07-10T21:30:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_dialect_vocab_lines.py — test_full_template_deep_checks_carries_dialect_line · test_fast_template_carries_dialect_line · test_glossary_template_carries_data_guidance_as_prose (+ regex proves no `- token:` bullet added) · test_project_glossary_carries_the_rule · test_sensitivity_guide_names_wm2_evidence · test_no_new_sensitivity_token (render a fresh project, _project_sensitivity_domain == ()).
Tests live in: `add-method/tooling/test_dialect_vocab_lines.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/` `.claude/` `.add/GLOSSARY.md` `tmp/`
Strategy & known-problem fixes: 1. red pins 2. canonical template/guide/glossary edits 3. cp to every twin 4. full tooling suite; traps: guidance as prose only (vocab_leak) · §6 only (tag census) · twins before the gate
Approach (domain strategy): book-technical-writer stance — the floor's prose surface: one checklist line a verifier can act on, one glossary rule a task author can route by
Strategy actually used: as planned, plus the byte-ceiling absorption the lean rule demands — the DIALECT line and sensitivity.md guidance were compressed (all §3-cited phrases held, pinned by the red suite) and ~183B of existing sensitivity.md prose trimmed so pool 51885/tree 145974 fences hold; 5 sibling pins amended via TESTS re-cross exactly as the least-sure flag predicted (4 Deep-checks fixtures now fill the DIALECT placeholder; fast-lane's task-local empty-git-diff guard re-pinned to its durable invariant: skip machinery stays fast-lane-only); a 4th gitignored dogfood twin (add-method/.add/tooling/templates/) joined the sync set.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full tooling suite 3374 passed + 162 subtests, 0 failed; test amendments (5) went through an explicit TESTS re-cross, never a quiet edit
- [x] green was EARNED — the 6 red pins assert rendered template/guide CONTENT (phrase + placement + no-bullet regex), not the build's own strings; `_project_sensitivity_domain` () proven over a fresh render
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose/template-only change; no new imports, no engine code touched (ENGINE_MD5/PKG unchanged)

Build expectations (from §1 Accept + §3 CONTRACT): a fresh render carries the DIALECT line inside `### Deep checks` (full) and the condensed §6 line (fast); GLOSSARY.md.tmpl + `.add/GLOSSARY.md` + sensitivity.md ×3 carry datetime/money/tz ⇒ `data` with the wm2 evidence; no new sensitivity token — confirmed by test_dialect_vocab_lines.py 6/6 + budget/parity/audit suites green (3374 total).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-11
[SPEC · open] lever-1 refinement: `_dialect_gaps` scans the §3 RAW body, which includes engine-written freeze metadata — this task's own tests→build crossing warned `aware-iso-timestamp` on its `Freeze mode: … 2026-07-10T17:38:23+00:00` stamp, a false positive of the v1 scan span; candidate fix: scan only §3 fenced blocks or strip the Status/Freeze-mode lines (evidence: crossing output at the phase-build re-cross, this task, 2026-07-11)

