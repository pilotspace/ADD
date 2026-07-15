# TASK: trim add.py --help top-level output to essentials + per-command pointer

slug: help-diet · created: 2026-07-15 · stage: mvp
milestone: engine-minimalism
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: `add.py --help` top-level output is trimmed from the ~120-line argparse dump (flow map + full per-command help for ~45 subcommands) to the flow map + a COMPACT command-NAME list + the `add.py <command> -h` pointer — cutting re-read cache-weight (17% of an ADD run's engine_output, from one early call) while keeping every command discoverable.
Must:
  - M1: `build_parser().format_help()` for the TOP parser (`prog == "add.py"`) leads with `_FLOW_MAP` (unchanged) then a COMPACT command list — every subcommand NAME present, but NOT the per-command help paragraph — total output ≤ 45 lines (baseline 121).
  - M2: DISCOVERABILITY held — every subcommand name argparse knows (init, new-task, advance, freeze, gate, status, milestone-done, new-milestone, release, federate, … all ~45) still appears in the output, and the per-command flags pointer (`add.py <command> -h`) is present.
  - M3: TOP-parser only — a subcommand's own `--help` (`prog == "add.py <cmd>"`, e.g. `add.py new-task -h`) stays BYTE-IDENTICAL to argparse default (full flags), and the bare-`add.py`/unknown-command error paths (help-habit-kill) are untouched.
Reject:
  - R1: `format_help()` for a NON-top parser (a subcommand) -> the trim MUST NOT apply (`no_top_trim`) — return argparse's full help verbatim (regression guard: the diet is scoped to `prog == "add.py"`).
Accept: `add.py --help` prints ≤45 lines, still names every subcommand (spot-check init·new-task·advance·freeze·gate·status·milestone-done·new-milestone·release·federate) + the `<command> -h` pointer, while `add.py new-task -h` is unchanged (shows `--title`/`--fast`).
Boundary: the TOP parser (`prog == "add.py"`, trimmed) vs a SUBCOMMAND parser (`prog == "add.py <cmd>"`, verbatim) — `format_help` dispatches on `self.prog`.
Assumptions: ⚠ `argparse._SubParsersAction.choices` reliably enumerates every subcommand name (private API) — it has since py3; if a future argparse renames it, the compact list could go empty; cost: `--help` loses the command list (caught by M2's presence assertions in CI), never a crash.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `add-method/tooling/add.py` — `_AddArgParser.format_help` (the top-parser branch: replace `super().format_help()` with a compact list); NEW module-level `_compact_commands(parser) -> str` (enumerate `_SubParsersAction.choices`, dedupe-in-order, textwrap into a names block + pointer). `_FLOW_MAP` unchanged; `error()` unchanged.
  - `add-method/tooling/test_orient_map.py` — forward-migrate the ONE sibling pin (`test_top_help_leads_with_map_then_full_list`) whose "the FULL argparse command list still appears" intent help-diet supersedes: assert the map leads + every NAME still present + the output is now COMPACT (no per-command help paragraph / ≤45 lines).
Context (working folder): baseline measured live — top `--help` 121 lines (`_FLOW_MAP` 10 + argparse dump 111); the dump is the trim target. help-habit-kill (`error()`) + subcommand `-h` are OUT of the change.
Honors (patterns / conventions): `_AddArgParser` already guards top-vs-subcommand on `self.prog == "add.py"` (orient-map/help-habit-kill pattern) — reuse it · SEAMS.md pins add.py line numbers → repin on shift · engine change → ENGINE_PKG_MD5 repin · no new deps (stdlib `textwrap`, `argparse`).
Anchors the contract cites: `_AddArgParser`, `format_help`, `_compact_commands`, `_FLOW_MAP`, `build_parser`, `argparse._SubParsersAction`.
Ground SHA: 98b5c49 — stamped by freeze

### Contract

```
_AddArgParser.format_help(self) -> str:
  if self.prog == "add.py":            # TOP parser only
      return _FLOW_MAP + "\n" + _compact_commands(self)   # map (unchanged) + compact names + pointer
  return super().format_help()         # R1: subcommand help verbatim (no_top_trim)

_compact_commands(parser) -> str:
  # enumerate the sole _SubParsersAction's choices (every subcommand name), dedupe preserving
  # order, textwrap into a names block; header names the per-command pointer `add.py <command> -h`.
  # contains EVERY subcommand name (M2 discoverability); NO per-command help paragraph.

  invariants:
    - top `add.py --help` output <= 45 lines, leads with _FLOW_MAP, names every subcommand + the pointer
    - `add.py <cmd> --help` (prog "add.py <cmd>") BYTE-IDENTICAL to today (argparse default)
    - bare add.py + unknown-command error() paths unchanged
```

`Least-sure flag surfaced at freeze:` [contract] the diet relies on `_SubParsersAction.choices` (argparse private API) to list commands — stable across py3 but unofficial; if it ever changes shape the compact list empties (M2's per-name presence assertions fail LOUD in CI) rather than crashing the CLI.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_help_diet.py` `add-method/tooling/test_orient_map.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py`
Strategy & known-problem fixes: 1. RED: `test_help_diet.py` — (M1) top `format_help()` ≤45 lines & leads with the map head; (M2) every sampled command name present + `<command> -h` pointer present; (M3/R1) `init --help` (subcommand) still shows `--stage` and is unchanged, i.e. the trim didn't leak. 2. forward-migrate `test_orient_map.py::test_top_help_leads_with_map_then_full_list` to the compact behavior (map leads · names present · compact/≤45 · no per-command help para) — a TESTS-phase sibling-pin migration (declared in scope), then `re-cross` if it lands after the freeze-cross. 3. build `_compact_commands` + the `format_help` top-branch swap. 4. LIVE: `add.py --help | wc -l` ≤45, `add.py new-task -h` unchanged. Trap: dedupe subparser aliases (choices dict may repeat a parser) preserving order. Trap: keep `_FLOW_MAP` verbatim (orient-map froze its head string `_MAP_HEAD`). Trap: don't touch `error()` (help-habit-kill pins it).
Approach (domain strategy): "compact names, verbatim subhelp"

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
Strategy actually used: as planned — `_compact_commands` enumerates the `_SubParsersAction.choices` and textwraps them; `format_help` top-branch swaps the argparse dump for map+compact. IMPROVED on strategy: added `break_on_hyphens=False, break_long_words=False` so hyphenated command names (carry-delta, re-cross, …) stay atomic — else textwrap split them across lines and broke discoverability grep. Sibling pin `test_orient_map::test_top_help_leads_with_map_then_compact_list` forward-migrated in the tests phase (in scope). ENGINE_MD5 re-pinned d7079f8d→1dd8c1b1 across all FOUR add.py twins (source · _bundled · repo .add/ · add-method/.add/); ENGINE_PKG_MD5 unchanged (add_engine/*.py untouched — only add.py).
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full engine suite 3630 green; sibling pin forward-migrated in tests phase, not build)
- [x] green was EARNED — asserts pin line-count ≤45 + per-command-help ABSENT + every sampled name present + subcommand help unchanged; live `--help` inspected (19 lines)
- [x] input dialect held — tests speak the real command names + prog forms (`add.py` vs `add.py <cmd>`)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib textwrap/argparse only, read-only formatting (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `python3 add-method/tooling/add.py --help | wc -l` = 19 (baseline 121); the output leads with `ADD — spec-and-tests-first`, ends with a `commands (flags: add.py <command> -h):` block listing all ~52 subcommands (each atomic — `carry-delta`, `re-cross`, `sync-guidelines` unbroken), and `add.py new-task -h` still prints `--title`/`--fast`. Confirmed live + pinned by `test_help_diet` (4) + migrated `test_orient_map` (4) + `test_help_habit_kill` (4); ENGINE_MD5 parity green (`test_engine_repin_parity`, `test_engine_twins_carry_the_echo`).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-15

OBSERVE:
- [SPEC · open] the engine has FOUR add.py twins (source · _bundled · repo `.add/` · add-method's own dogfood `.add/`), not the "three trees" the pin tests name; a partial re-pin sync passes the 3-copy EnginePinTest but trips `test_engine_twins_carry_the_echo` (4th twin) + `test_no_bytecode_or_os_junk_in_bundle` (import pollution). Lesson for orient-diet: sync ALL FOUR twins + run the suite with PYTHONDONTWRITEBYTECODE=1. (evidence: this task's 2 transient full-suite failures, both twin/pollution not logic)
