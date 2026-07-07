# TASK: Loop-adherence census artifact + add-arm loop wrapper; rerun add arm

slug: bench-adherence-census · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/score.py:score_record (artifacts writer) · benchmark/runner/core.py:_wrap_prompt (arm prompt wrapper) · benchmark/arms/add.toml:prompt_wrapper · benchmark/tests/ (new test module)
Context (working folder): benchmark/runs/<arm>/wm<k>/transcript.jsonl — census source; PROJECT.md invariants (frozen 5-metric set — census is an ARTIFACT, never a 6th metric)
Honors (patterns / conventions): judge_scores artifact precedent (bench-judge-median); plan-then-execute wrapper precedent (_wrap_prompt)
Anchors the contract cites: score_record · _wrap_prompt · artifacts["engine_calls"]
Ground SHA: 36fa689

---

## 1 · SPECIFY — the rules

Feature: loop-adherence census + add-arm loop wrapper
Must:
  - score_record writes artifacts["engine_calls"] = "<int>" — count of `add.py <subcommand>` invocations parsed from the run's transcript.jsonl (0 when transcript missing/empty; never a metric)
  - _wrap_prompt gains an "add-loop" wrapper: prefixes the workload prompt with the drive-the-ADD-loop instruction (status first · follow the phase flow · no app code before a frozen contract + red suite); add.toml switches prompt_wrapper to "add-loop"
  - existing 5 frozen metrics and all other arms' behavior byte-unchanged
Reject:
  - unknown wrapper string -> passes prompt through verbatim (existing behavior preserved)
Accept: Given an add-arm record with a transcript containing N `add.py` calls, When score_record runs, Then artifacts["engine_calls"] == str(N) and metrics keys are unchanged; Given wrapper "add-loop", When _wrap_prompt runs, Then output starts with the loop instruction and ends with the original prompt.
Assumptions: ⚠ regex `add\.py <word>` census may over/under-count (e.g. paths, docs mentions) — acceptable: it is a comparative artifact, not a metric; if wrong: census misleads adherence reads (mitigate: count only lines that look like command invocations is NOT required at this size)

---

## 3 · CONTRACT — freeze the shape

```
score_record(arm, wm, *, judge_cmd=None) -> RunRecord
  record.artifacts["engine_calls"]: str(int)   # census from transcript.jsonl; "0" fallback
_wrap_prompt(text, "add-loop") -> "Drive this repo's ADD loop..." + text
benchmark/arms/add.toml: prompt_wrapper = "add-loop"
frozen: metrics dict keys unchanged (5); other arms' toml untouched
```

`Least-sure flag surfaced at freeze:` [test] the census regex breadth — a transcript may mention add.py in prose/paths; counted anyway by design (comparative artifact); if wrong: adherence reads skew but no metric moves
Status: FROZEN @ v1 — approved by Tin Dang (guided-choice confirm 2026-07-08: "Rerun with adherence enforced — engine-call census as a recorded run artifact + strengthen the workspace prompt")

---

## 4 · TESTS — failing-first (red)

Suite: benchmark/tests/test_adherence_census.py — 7 tests (census count/missing/empty ·
add-loop wrapper prefix + verbatim fallback · add.toml switched · other arms untouched ·
census-is-artifact). RED confirmed: collection ImportError on `_engine_call_census`
(symbol not yet built) — red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `./src/`   <every file the build may write — declared before the §3 freeze>
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — benchmark suite 102 green (incl. 8 new); test fixture aligned to the frozen contract via re-cross (bare add.py path is not a subcommand invocation), no test weakened
- [x] green was EARNED — census counted against hand-built transcripts; wrapper asserted on prefix + verbatim fallback; other-arm tomls asserted untouched
- [x] no security surface — pure parsing/prompt-prefix change; no new deps

Build expectations (from §1 Accept + §3 CONTRACT): artifacts["engine_calls"] recorded per scored run; add arm prompts open with the drive-the-loop instruction — confirmed by benchmark/tests/test_adherence_census.py + the enforced rerun's records.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

