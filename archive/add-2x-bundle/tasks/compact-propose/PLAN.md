# TASK: compact-foundation --propose read-only preview

slug: compact-propose · created: 2026-07-07 · stage: mvp
milestone: delta-drain
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py:_foundation_tail (the read-only folded-tail counter the compaction cue already uses) · add.py:main argparse subcommand table · add.py trio twins (.add/tooling + _bundled/tooling) · add-method/tooling/engine_pin.py:ENGINE_MD5 (re-pin honestly)
Context (working folder): .add/PROJECT.md + .add/CONVENTIONS.md (the two specs _foundation_tail reads) · add-method/skill/add/compact-foundation.md (the ritual: gather -> propose -> confirm -> write; this verb automates ONLY step 2)
Honors (patterns / conventions): cues COUNT, never judge (loop-surfacing-nudges) · engine verbs are NO-EXEC + fail-soft · never pre-stamp human seams — the WRITE stays the human-confirmed ritual
Anchors the contract cites: _foundation_tail · main subparser table · ENGINE_MD5
Ground SHA: a1cfd6a

---

## 1 · SPECIFY — the rules

Feature: a `compact-foundation --propose` read-only verb (render the per-spec settled line for the eligible tail) if the nudge alone doesn't drive the ritual (from loop-surfacing-nudges spec-delta)
Must:
  - `add.py compact-foundation --propose` prints, for EACH spec (PROJECT.md · CONVENTIONS.md) carrying >=1 live `[folded foundation-version N]` stamp, one propose line with the per-file count and fv range (grammar frozen in §3)
  - a success run always ends with the read-only footer naming the human ritual (compact-foundation.md)
  - the verb NEVER writes: every touched spec is byte-identical before/after in every path
  - zero folded stamps across both specs -> `nothing to propose — no folded tail above the settled line` (exit 0)
Reject:
  - `compact-foundation` without `--propose` -> "propose_only" (exit 2; stderr names the flag and the human ritual)
Accept: Given PROJECT.md carries >=2 live folded stamps, When `add.py compact-foundation --propose` runs, Then a PROJECT.md propose line with its fv range renders, the footer renders, and no file changed.
Assumptions: ⚠ the per-file fv range should come from the folded stamps themselves (min–max), not the settled line — if wrong: the proposed range mislabels and the human catches it at confirm (cheap re-freeze)

---

## 3 · CONTRACT — freeze the shape

```
add.py compact-foundation --propose            # READ-ONLY; the only supported mode
  per spec (PROJECT.md · CONVENTIONS.md) with >=1 live folded stamp, one line:
    "<name> : <N> folded line(s) (fv<LO>-fv<HI>) -> propose: settled fv<LO>-fv<HI> — <theme — draft at confirm> (see git)"
  always on success (last line):
    "read-only preview — the write stays the human-confirmed ritual (compact-foundation.md)"
  zero stamps across both specs -> "nothing to propose — no folded tail above the settled line"  (exit 0)
  without --propose -> exit 2, stderr: "compact-foundation: pass --propose — read-only preview only; the write is the human ritual (compact-foundation.md)"
  guarantee: zero filesystem writes on every path (propose_only reject included)
```

`Least-sure flag surfaced at freeze:` [contract] the propose-line grammar (colon-column, literal `<theme — draft at confirm>` placeholder) — chosen for grep-ability over prose; if wrong: cosmetic re-freeze, cheap
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: test_compact_propose.py — propose renders per-spec ranges + footer (Accept) · byte-identical specs before/after · zero-tail message · propose_only reject (exit 2, no writes) · add.py trio + ENGINE_MD5 honesty.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy & known-problem fixes: (1) red test_compact_propose.py first (2) per-file fv-range variant of _foundation_tail's parse (do NOT change _foundation_tail itself — the status cue pins its shape) (3) _cmd + subparser mirroring `deltas` (the read-only-report precedent) (4) sync trio + re-pin ENGINE_MD5
Approach (domain strategy): reuse the existing folded-stamp regex per file · min/max fv from stamps · read-only report-verb pattern (deltas/report precedent) · correctness-first, no budget
Strategy actually used: as planned (verb placed beside cmd_deltas, the read-only-report precedent; _foundation_tail untouched)
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): --propose renders per-spec fv-range propose lines + ritual footer, zero writes; bare verb exits 2 — confirmed by test_compact_propose (6 green) + live dogfood (PROJECT.md fv21-fv35 rendered, tree unchanged)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07

