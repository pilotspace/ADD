# TASK: Freeze stamps the Ground SHA placeholder (derived data, never hand-typed)

slug: derived-stamps · created: 2026-07-13 · stage: mvp
milestone: ceremony-to-effort
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: freeze stamps the Ground SHA placeholder — derived data the agent hand-types today (weight audit 2026-07-13: 100% mechanically derivable). SCOPE-TRIMMED at ground: Status flip, GATE RECORD stamps (_stamp_gate_record), and fast-tmpl Ground SHA line ALREADY exist; Reported: is an honesty attestation, never auto-set.
Must:
  - `freeze` fills a §3 `Ground SHA:` line still carrying its `<...>` placeholder with the repo's real short HEAD, in the SAME atomic write as the Status flip (the tamper fingerprint hashes the stamped text)
  - both lanes (TASK.md + TASK.fast.md render the same line) get the stamp
Reject:
  - a hand-filled Ground SHA line -> byte-untouched (grandfather, mirrors _stamp_gate_record)
  - no git repo / git fails -> line untouched, freeze succeeds (fail-open)
Accept: Given a drafted §3 whose Ground SHA still holds the template placeholder in a git repo, When the human runs freeze --by, Then the frozen §3 carries the real short HEAD and the tamper check stays clean through gate.
Boundary: git-present vs git-absent project — both freeze successfully; only the former stamps
Assumptions: ⚠ the placeholder regex must not match a hand-filled SHA — why: grandfather is the safety; if wrong: a hand-typed value gets clobbered (cost: one wrong provenance line, caught by the test pinning grandfather)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add.py:cmd_freeze (~1030, Status-flip span substitution — the stamp joins the same new_text before _atomic_write) · add.py:~2249 (existing `git rev-parse --short HEAD` subprocess precedent, reuse its shape) · x4 engine twins + engine_pin re-pin
Context (working folder): templates x5 carry the Ground SHA line — comment text update optional, ceilings bind
Honors (patterns / conventions): _stamp_gate_record's grandfather rule (rewrite ONLY while `<...>` placeholder); fail-open subprocess (OSError/SubprocessError -> no stamp); validate-then-write order preserved
Anchors the contract cites: cmd_freeze · _stamp_gate_record (pattern) · the rev-parse precedent
Ground SHA: 260cdef — grounded live: gate stamps EXIST, Status flip EXISTS, fast tmpl HAS the line, Reported: = attestation (all dropped from scope)

### Contract

```
cmd_freeze, inside the existing §3 span substitution, BEFORE _atomic_write:
  a line matching ^Ground SHA:[ \t]*<[^>\n]*>.*$ (placeholder form only) becomes
    Ground SHA: <short-head> — stamped by freeze
  where <short-head> = `git rev-parse --short HEAD` run at the PROJECT root
  (root.parent), reusing the existing subprocess shape. Git absent or failing ->
  no substitution, freeze proceeds unchanged (fail-open). A non-placeholder line
  never matches (grandfather). The stamp lands in the same atomic TASK.md write
  as the Status flip, so freeze's contract_md5 fingerprints the STAMPED text.
```

`Least-sure flag surfaced at freeze:` [contract] the stamp text itself contains no `<...>` placeholder form — why: downstream placeholder-scanners (_section_unfilled, AI-verify) must not re-flag a stamped line; if wrong: a spurious unfilled warning at check (cost: one warn line, no gate impact)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy & known-problem fixes: 1) red tests (git + no-git tmp projects) in add-method/tooling/test_derived_stamps.py 2) cmd_freeze stamp in the span substitution 3) engine-only twin sync x4 + pin re-pin. Traps: the em-dash in the stamp is fine but keep the line free of `<...>`; tmp test projects need `git init`+commit for the git path; freeze tests elsewhere pin exact §3 text — stamp only fires on the PLACEHOLDER form so existing suites (hand-filled or no Ground SHA line) stay untouched.
Approach (domain strategy): grandfathered placeholder substitution, fail-open, one write

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (cmd_freeze ~1030 · rev-parse precedent ~2249 · _stamp_gate_record 385 — verified at 260cdef)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (stamp text must not re-trigger placeholder scanners)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T10:20:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_freeze_stamps_placeholder_ground_sha (git repo -> real short HEAD in frozen §3) · test_hand_filled_line_untouched (grandfather) · test_no_git_freeze_succeeds_line_untouched (fail-open) · test_stamp_inside_tamper_fingerprint (freeze -> advance x3 -> gate PASS clean, no contract_tampered).
Tests live in: `add-method/tooling/test_derived_stamps.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned; one fixture correction in TESTS (quality-floors Boundary: refusal — the floor caught my own fixture) and one SEAMS line-pin re-aim (5512→5526, 4th consecutive drift — todo #30). Live dogfood: THIS task's own freeze stamped Ground SHA into kickoff-truth-era placeholders? no — its §3 was hand-grounded at 260cdef before the feature existed; the NEXT task's freeze is the first live consumer.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (fixture fix was TESTS-phase, pre-crossing)
- [x] green was EARNED — M1 red-first for the feature's absence; grandfather/fail-open pinned by negative tests against the real CLI
- [x] input dialect held — tests assert the contract's own stamp text verbatim (`— stamped by freeze`)
- [x] no exposed secrets, injection openings, or unexpected dependencies — a git subprocess at the project root with a 10s timeout, output used only as a short hex string in prose; failure -> no stamp

Build expectations (from §1 Accept + §3 CONTRACT): a placeholder Ground SHA line freezes into the real short HEAD and the tamper check stays clean through gate; hand-filled/no-git lines byte-untouched — confirmed by test_derived_stamps 4/4 + full suite 3457 (sole failure = the known SEAMS line-pin drift, re-aimed) + check 738/0

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

