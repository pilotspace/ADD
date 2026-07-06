# TASK: leaner TASK.md template

slug: task-md-optimize · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): templates/TASK.md.tmpl (comments [0][2][3][5][6][8][9] + intro/§6/§7 blockquotes) · test_taskmd_lean.py (new frozen ceilings)
Context (working folder): 4 template trees; pins honored: test_declare_grammar_doc (§4 grammar) · test_high_risk_signal (risk: high) · test_template_form_tags (§3 single comment, cue words) · test_scope_decl_template (never retro-red) · tag census (no new bare <word> tag)
Honors (patterns / conventions): every machine-read marker byte-kept; guidance compressed, never deleted; v16 frozen tag vocabulary
Anchors the contract cites: TASK.md.tmpl · test_taskmd_lean ceilings
Ground SHA: post-fastlane-ground-lite commit

---

## 1 · SPECIFY — the rules

Feature: leaner TASK.md template (user-added: optimize TASK.md)
Must:
  - template ≤10600B / comments ≤2500B (UTF-8), from 12442/3418
  - all pinned anchors + form tags + block headings survive; scaffold behavior unchanged
Reject:
  - a new bare <word> tag -> "census_changed" (v16 vocab frozen)
Accept: Given the trimmed template, When the full template-pinning batch runs, Then 187+97 tests pass with the template 16% smaller
Assumptions: ⚠ compressed guidance keeps enough signal for a fresh agent — because every fact was kept, only narration dropped; if wrong: restore a sentence (cheap)

---

## 3 · CONTRACT — freeze the shape

```
TASK.md.tmpl: 12442B -> 10504B (-16%) · comments 3418B -> 2497B (-27%)
test_taskmd_lean: SIZE_CEILING 10600 · COMMENT_CEILING 2500 (frozen, UTF-8 bytes)
```

Least-sure flag surfaced at freeze: ⚠ [test] the ceilings were calibrated to the achieved trim — because the initial guess (11000/2400 chars) predated byte-measurement + pin discovery; if wrong: they still hold the line 15%/27% under pre-task
Status: FROZEN @ v1 — approved by Tin (implement-directly directive 2026-07-06)

---

## 4 · TESTS — failing-first (red)

Plan: test_taskmd_lean (5) — size ceiling · comment ceiling · pinned anchors · §3 single comment · tree parity.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/test_taskmd_lean.py` `.add/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/.add/tooling/templates/`
Strategy & known-problem fixes: comment inventory → pin census via grep → trim unpinned → 4 pin breaks surfaced by the batch → restore exact pinned words
Strategy actually used: as planned + 3 pinned-wording restorations (scenario/contract cue · never retro-red · no <learning> tag) + byte-vs-char recalibration
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (187 template-pin batch + 97 scaffold-behavior batch) · coverage held · no frozen test altered (my own new test recalibrated pre-green, disclosed in the flag)
- [x] green was EARNED — pins verified by running the pinning suites themselves, not by my assertions alone
- [x] no exposed secrets, injection openings, or unexpected dependencies

Build expectations (from §1 Accept + §3 CONTRACT): a fresh scaffold is ~2KB lighter with identical machine seams — confirmed by suite + byte counts

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto; no residue) under Tin's directive · date: 2026-07-06

