# TASK: waiver field census matches case-insensitively

slug: waiver-field-case · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py:_audit_findings — the waiver_incomplete field census
Context (working folder): the two live RISK-ACCEPTED records (js-reclaim-lock-heartbeat · reclaim-ticket-race) write Owner:/Ticket:/Expires: capitalized
Honors (patterns / conventions): fix the checker when the record is right — never rewrite a human-signed §6
Anchors the contract cites: _audit_findings waiver block · test_gate_audit
Ground SHA: 6f2f21e

---

## 1 · SPECIFY — the rules

Feature: waiver_incomplete field census is case-insensitive
Must:
  - a RISK-ACCEPTED §6 carrying Owner:/Ticket:/Expires: (any casing, non-placeholder) raises no waiver_incomplete
  - a record missing any of the three still fires
Reject:
  - missing field -> "waiver_incomplete" (unchanged)
Accept: Given a waiver with capitalized fields, when audit runs, then no waiver_incomplete and Seam-audit CI exits 0
Assumptions: ⚠ case-insensitive match cannot over-accept — because (?!<)\S still rejects placeholders/blanks; if wrong: a lax waiver slips the census (human spot-audit backstop)

---

## 3 · CONTRACT — freeze the shape

```
re.search(rf"{k}:\s*(?!<)\S", s6, re.IGNORECASE) for k in (owner, ticket, expires)
records untouched; refusal text unchanged
```

`Least-sure flag surfaced at freeze:` ⚠ [contract] IGNORECASE is the full fix — because both live records differ only in casing; if wrong: the finding re-fires and CI stays honest
Status: FROZEN @ v1 — approved by Tin (AskUserQuestion: 'Fix the regex (Recommended)')

---

## 4 · TESTS — failing-first (red)

Plan: test_waiver_capitalized_fields_ok (in test_gate_audit) — capitalized fields raise no finding; the missing-field test stays.
Tests live in: `add-method/tooling/` · ran red (finding fired on capitalized fields) before the fix.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` · `.add/tooling/` · `add-method/src/add_method/_bundled/tooling/` · `add-method/.add/tooling/`
Strategy & known-problem fixes: red test → re.IGNORECASE → pin re-aim + 4-tree sync (trap: fixing the records instead would rewrite signed waivers)
Strategy actually used: as planned; local `add.py audit` exit 1→0
Code lives in: `add-method/tooling/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): local `add.py audit` exits 0 with both live waivers intact — confirmed by the run above + test_gate_audit 25/25

### GATE RECORD
Outcome: PASS
Reviewed by: Tin (option-approved) · date: 2026-07-06

