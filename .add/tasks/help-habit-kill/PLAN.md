# TASK: unknown subcommand → concise close-match + resume pointer, no 50-choice dump

slug: help-habit-kill · created: 2026-07-14 · stage: mvp
milestone: call-residuals
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: an unknown top-level subcommand self-corrects inline — instead of argparse dumping the full 50-choice usage (which the agent answers with a `--help` or a re-read, the measured 1/rep lever), a mistyped command prints a concise "unknown command 'X' — did you mean '<closest>'?" + a resume pointer to `add.py status`, so misuse is corrected in one glance without a --help round-trip.
Must:
  - an unknown TOP-LEVEL command (`add.py <bogus>`) prints to stderr `add.py: unknown command '<bogus>'`, a close-match suggestion `— did you mean '<near>'?` when difflib finds one, and a resume pointer `see where you are + all commands: add.py status`; exit 2
  - the full 50-choice usage dump is NOT printed for that case, and NO surface says "run --help"
  - subcommand-level errors (missing slug, a subcommand's own invalid choice like `stage <bad>`) keep argparse's default behavior (top-level-only interception, `prog == "add.py"`); every valid command is unaffected
Reject:
  - unknown top-level command -> "unknown command '<x>'" (exit 2)   (replaces the raw argparse choices dump for this one case)
Accept: Given a mistyped top-level command (e.g. `add.py statuss`), When it runs, Then stderr says "unknown command 'statuss' — did you mean 'status'?" and points to `add.py status`, without the 50-choice dump or any "--help" mention, exiting 2
Boundary: two variants the test must speak — a bogus command WITH a near match (`statuss`→`status`) and one with NO near match (`zzqq`, suggestion omitted, still points to status)
Assumptions: ⚠ the 50-choice dump is what triggers the --help/re-read, not the exit code — evidence: the dump is ~4 lines of 50 comma-separated names, unreadable at a glance; if wrong (agents --help for other reasons): no harm, the concise error is strictly more actionable

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add-method/tooling/add.py:build_parser` (make the top-level parser a subclass whose `error()` intercepts the unknown-command case) + a new `_AddArgParser(argparse.ArgumentParser)` class beside it; it READS `difflib.get_close_matches` (stdlib) — no engine symbol changed
Context (working folder): `add-method/tooling/` (canonical engine). The full write-set — canonical add.py, its 3 engine twins, engine_pin.py, the new test — is the §5 Scope below; ENGINE_MD5 + SEAMS re-aimed as part of any engine edit
Honors (patterns / conventions): fail-open + minimal-surface (intercept ONE case, delegate all else to `super().error()`); the top-level `prog == "add.py"` guard keeps subcommand-arg errors (test_graduate_guard's `stage <bad>` invalid-choice, test_argv_portability's unrecognized-arguments) on argparse defaults
Anchors the contract cites: `build_parser` (edited) · `_AddArgParser.error` (new) · `difflib.get_close_matches` (read) · `add.py status` (the resume pointer)
Ground SHA: aaee317 — stamped by freeze

### Contract

```
_AddArgParser(argparse.ArgumentParser).error(message), self.prog == "add.py" AND message matches "invalid choice: '<X>'":
  → stderr line 1: "add.py: unknown command '<X>'" + (" — did you mean '<near>'?" if difflib.get_close_matches(X, <subcommand names>, n=1) else "")
  → stderr line 2: "see where you are + all commands: add.py status"
  → exit 2; does NOT print the argparse usage dump; contains no "--help"
_AddArgParser.error, any OTHER message (or a subparser whose prog != "add.py"):
  → super().error(message)  (argparse default — unchanged)
build_parser: the top-level ArgumentParser is _AddArgParser; every subparser + all valid dispatch unchanged
```

`Least-sure flag surfaced at freeze:` [contract] the exact stderr wording — cosmetic; the hard edge is the `prog == "add.py"` + "invalid choice" match being NARROW enough to leave subcommand-arg errors (missing slug, `stage <bad>`) on the argparse default, so test_graduate_guard / test_argv_portability stay green.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/tooling/test_help_habit_kill.py`
Strategy & known-problem fixes: (1) RED first: new test_help_habit_kill asserts `add.py statuss` → stderr "unknown command 'statuss'" + "did you mean 'status'?" + "add.py status", NO "invalid choice"/no 50-choice dump/no "--help", exit 2; `add.py zzqq` → concise, no suggestion, still points to status; a valid command still runs. (2) add `_AddArgParser` overriding `error()`, gate on `self.prog == "add.py"` + a regex on "invalid choice: '(...)'", pull subcommand names from the `_SubParsersAction.choices`, difflib the closest; delegate every other error to `super().error()` (trap: keep the guard NARROW so subcommand invalid-choice / unrecognized-arguments tests stay green). (3) sync ×4 twins, re-pin ENGINE_MD5 + SEAMS.
Approach (domain strategy): narrow argparse error interception

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — no divergence. Added `_AddArgParser(argparse.ArgumentParser)` overriding `error()`; guards on `prog == "add.py"` + a `re.search` for "invalid choice: '(X)'", pulls choices from the `_SubParsersAction`, `difflib.get_close_matches` (lazy-imported) for the suggestion, else `super().error()`. `build_parser` now instantiates `_AddArgParser`. Synced ×4 twins, ENGINE_MD5→9267a41f. SEAMS unchanged (_declared_scope at 5688 is above the new class).
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full fence)
- [x] green was EARNED — the 3 intercept asserts RED first (suggestion · no-dump/no-help · no-near-match); valid-command invariant green throughout; GREEN only after the subclass
- [x] input dialect held — the test speaks the real CLI stderr + exit-code dialect
- [x] no exposed secrets, injection openings, or unexpected dependencies (stdlib difflib only; security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): `add.py statuss` prints to stderr `add.py: unknown command 'statuss' — did you mean 'status'?` then `see where you are + all commands: add.py status`, exit 2, with no "invalid choice"/50-choice dump/"--help"; `add.py zzqqxx` omits the suggestion but still points to status; `add.py stage <bad>` and missing-slug errors keep argparse defaults — confirmed by test_help_habit_kill (4 asserts) + the live `add.py statuss` output + green test_graduate_guard/test_argv_portability in the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

