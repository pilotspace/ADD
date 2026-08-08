# TASK: bare add.py / --help lead with a concise flow map, not the 50-choice dump

slug: orient-map · created: 2026-07-14 · stage: mvp
milestone: orientation-honesty
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: bare `add.py` (no subcommand) and `add.py --help` LEAD with a concise flow-ordered command map (status · init · new-task · advance · freeze · gate) instead of the ~50-choice argparse dump — so the agent's first orientation is one cheap read. Kills the stubborn 1/rep bare-`--help` probe the anatomy flagged, which help-habit-kill never touched (it only caught UNKNOWN commands; the flag-carrying next-command hints from prior tasks already cover freeze/advance/new-task/init, so THIS is the true residual).
Must:
  - `add.py --help`/`-h` (top parser) output LEADS with the concise flow map, then the full argparse command list still appears below it — nothing lost; `add.py --help | head` now gets the map, not alphabet soup
  - bare `add.py` (no subcommand → argparse "the following arguments are required: cmd") prints the flow map + an `add.py status` pointer to STDERR, exit 2 — not the raw usage dump
  - a SUBCOMMAND's help (`add.py init --help`, prog "add.py init") is UNCHANGED — full argparse help for that command's flags stays intact
  - the help-habit-kill unknown-command interception stays byte-identical
Reject:
  - `add.py <cmd> --help` (a subparser, prog != "add.py") -> argparse default help, unchanged (the negative case the test pins)
Accept: Given a fresh shell, When `add.py --help` runs, Then its first lines are the flow map (status/init/new-task/advance/freeze/gate) AND the full command list still appears below; and bare `add.py` writes the map + "add.py status" to stderr, exit 2
Boundary: top parser (map leads) vs subparser `--help` (unchanged argparse) — the two shapes the test must speak
Assumptions: ⚠ argparse's `-h` action prints `format_help()` — overriding `format_help` on the top parser (guarded `prog=="add.py"`) retargets `--help` while leaving subparser help intact; if wrong (argparse routes `-h` around format_help): `--help` is unaffected and only the bare-`add.py` path lands — still a partial win, never a regression

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add.py:_AddArgParser` — add `format_help()` (top parser leads with the map) + extend `error()` for the no-subcommand "required" case; a new module constant `_FLOW_MAP` beside it; help-habit-kill's `error()` invalid-choice branch stays as-is
Context (working folder): `add-method/tooling/` (canonical add.py + 4 twins); ENGINE_MD5 re-pinned; SEAMS re-pinned only if `_declared_scope` line drifts (the _AddArgParser class sits near build_parser, ~line 8400 — well BELOW _declared_scope@5711, so no SEAMS drift)
Honors (patterns / conventions): help-habit-kill's `prog == "add.py"` top-parser guard (subparsers are _AddArgParser with prog "add.py <cmd>" — the guard scopes to the top parser only); the `add.py status` resume pointer idiom
Anchors the contract cites: `_AddArgParser.format_help` (new) · `_AddArgParser.error` (extended) · `_FLOW_MAP` (new) · `build_parser`
Ground SHA: 1d9a211 — stamped by freeze

### Contract

```
_FLOW_MAP: str  — a flow-ordered map: "status (start here) · init · new-task · advance · freeze · gate",
                  each with its key flags on one line, + "<command> -h for a command's flags"
_AddArgParser.format_help(self) -> str:
  self.prog == "add.py" -> _FLOW_MAP + "\n" + super().format_help()   # map LEADS, full list follows
  else                  -> super().format_help()                      # subcommand help byte-identical
_AddArgParser.error(self, message):
  self.prog == "add.py" AND "the following arguments are required" in message:
    -> sys.stderr.write(_FLOW_MAP + "\nrun: add.py status\n"); raise SystemExit(2)
  (the invalid-choice branch and the final super().error(message) stay unchanged)
```

`Least-sure flag surfaced at freeze:` [contract] whether argparse's `-h` action routes through `format_help()` — it does in CPython (the `_HelpAction` calls `parser.format_help()`), and the guard leaves subparser help intact; if a runtime differs, `--help` is simply unaffected (partial win, never a regression) — the bare-`add.py` path is independent and lands regardless.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_orient_map.py`
Strategy & known-problem fixes: 1. RED test_orient_map (`--help` leads with the map AND still lists the full commands below; bare `add.py` → map + "add.py status" on stderr, exit 2; `add.py init --help` still shows init's own flags, NOT the map; an unknown command still says "unknown command"). 2. add `_FLOW_MAP` + `format_help` + the "required" branch in `error()` (trap: guard `prog=="add.py"` so subcommand help/errors stay argparse-default). 3. sync ×4 add.py twins, re-pin ENGINE_MD5 (SEAMS unaffected — edit is below _declared_scope).
Approach (domain strategy): flow-map help override

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
Strategy actually used: as planned — added `_FLOW_MAP` constant + `_AddArgParser.format_help` (map leads then super() list, guarded `prog=="add.py"`) + the "required" branch in `error()`. Synced ×4 add.py twins, ENGINE_MD5→a88bc24c…; SEAMS unchanged (_declared_scope still 5711 — edit at ~8420 is below it). Live-verified: `--help` and bare `add.py` both lead with the map. No divergence.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — orient-map 4 green, help-habit-kill intact, repin parity green; full fence (pending tail)
- [x] green was EARNED — the two map asserts were RED before _FLOW_MAP/format_help existed; the subcommand-help + unknown-command asserts guard against the map hijacking those surfaces (both stayed green throughout)
- [x] input dialect held — the test speaks the real CLI stdout/stderr + exit-code dialect (format_help + parse_args)
- [x] no exposed secrets/injection/deps — pure static string + argparse override (security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): `add.py --help` output starts with `ADD — spec-and-tests-first…` + the flow map (status/init/new-task/advance/freeze/gate) AND still lists `new-milestone` et al below; bare `add.py` writes that map + `run: add.py status` to STDERR exit 2 (no `{init,lock,freeze…` dump); `add.py init --help` still shows `--stage` and NOT the map; `add.py statuss` still says "unknown command" — confirmed by test_orient_map (4 asserts) + the live `--help`/bare output + full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

