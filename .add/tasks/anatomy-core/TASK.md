# TASK: token_anatomy(transcript) — attribute cache-read tokens by category (method-doc·engine·build·conversation)

slug: anatomy-core · created: 2026-07-15 · stage: mvp
milestone: token-anatomy
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: `token_anatomy(transcript)` — attribute a run transcript's cache-read cost to categories (method-doc · engine-output · build-work · conversation) by residency-weighting each message (`size × #later turns it stays resident`), so ceremony optimization targets the real drivers.
Must:
  - M1: `token_anatomy(path)` returns `{categories:{method_doc,engine_output,build_work,conversation}, total_cache_read, turns, attributed_pct, residual_pct}` — every message assigned to exactly one category.
  - M2: attribution is RESIDENCY-WEIGHTED — a message's weight = `est_size(msg) × (# assistant turns AFTER it)` (a doc read early costs more than one read late), and the category token split scales the ACTUAL summed `cache_read_input_tokens` by each category's weight share.
  - M3: DETERMINISTIC + fault-tolerant — identical transcript → identical dict; blank/malformed JSONL lines are skipped; a transcript with no usage yields all-zero categories (never raises mid-parse).
  - M4: categorization is TOOL-AWARE — a `tool_result` is classed by matching its `tool_use_id` to the assistant `tool_use` that made it: a Read/Grep of a method path (`PROJECT.md`,`SOUL.md`,`TASK.md`,`MILESTONE.md`,`CLAUDE.md`,`SKILL.md`,`.add/docs/`) → method_doc; a Bash whose command contains `add.py` → engine_output; other file/test/bash IO → build_work; bare text → conversation.
Reject:
  - R1: a transcript path that does not exist -> `BenchError("anatomy_no_transcript: <path>")` (fail-loud on a bad input; this is an analysis tool, not a renderer).
Accept: `token_anatomy` on `add-v2meter-r0/wm1` returns a dict whose four category tokens sum to ~`total_cache_read` (≥95% attributed / `residual_pct` <5%), with `method_doc` and `engine_output` both > 0 (ADD's ceremony surfaces are present), and re-running yields the identical dict.
Boundary: a well-formed assistant/tool_result transcript (real run) vs a degenerate one (empty file / lines with no `usage`) — the first attributes to categories, the second returns all-zeros without raising.
Assumptions: ⚠ `est_size = len(text)//4` (stdlib char heuristic, no tokenizer) is proportionally accurate enough that category SHARES are trustworthy even if absolute token calibration drifts — if the heuristic is biased per-category, shares skew; cost: the ranking of drivers could mis-order close categories, mitigated by reporting `residual_pct` so a large gap flags low trust.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `benchmark/anatomy.py` (NEW module) — `token_anatomy(transcript_path) -> dict` (the public attributor); helpers `_parse_lines` (JSONL → message dicts, skip blanks/malformed), `_est_size(text) -> int` (`len//4`), `_categorize(tool_use_by_id, msg) -> str` (the M4 tool-aware classifier), `_CATS = ("method_doc","engine_output","build_work","conversation")`, `_METHOD_PATHS` (the doc-name set). No engine import.
Context (working folder): `benchmark/runs/<arm>/wm<n>/transcript.jsonl` are the inputs (JSONL: `assistant` msgs carry `usage.cache_read_input_tokens` + `tool_use`; `user` msgs carry `tool_result` with `tool_use_id`); mirrors the ad-hoc probe already proven in this session (144 turns, 14.3M cache_read on add wm1).
Honors (patterns / conventions): `benchmark/` stdlib-only + fail-loud `BenchError` (score.py) for bad input · pure-function-over-a-file (report.py) · NO tokenizer dep (char heuristic) · NO `add-method/` engine touch (reads transcripts only — no ENGINE_MD5 repin).
Anchors the contract cites: `token_anatomy`, `_categorize`, `_est_size`, `_METHOD_PATHS`, `BenchError`.
Ground SHA: 507a916 — stamped by freeze

### Contract

```
token_anatomy(transcript_path: str | pathlib.Path) -> dict:
  returns {
    "categories": {"method_doc": int, "engine_output": int, "build_work": int, "conversation": int},
    "total_cache_read": int,     # actual Σ usage.cache_read_input_tokens over assistant turns
    "turns": int,                # count of assistant messages carrying usage
    "attributed_pct": float,     # named-category weight / total modeled weight (0..1)
    "residual_pct": float,       # 1 - attributed_pct
  }
  algorithm:
    - parse JSONL (skip blank/unparseable lines)
    - each message M -> _est_size(M) = len(text)//4 ; weight(M) = size(M) * (#assistant turns AFTER M)
    - _categorize(M): match tool_result.tool_use_id -> the assistant tool_use;
        Read/Grep/Glob of a _METHOD_PATHS name -> "method_doc"
        Bash cmd contains "add.py"            -> "engine_output"
        other Read/Edit/Write/Bash/tool IO    -> "build_work"
        bare assistant/user text (no tool)    -> "conversation"
    - categories[c] = round(total_cache_read * weight_share(c))   # scale ACTUAL cache_read by weight share
    - deterministic; no-usage transcript -> all zeros, turns 0 (no raise)

  path does not exist -> BenchError("anatomy_no_transcript: <path>")   # R1, fail-loud
```

`Least-sure flag surfaced at freeze:` [contract] residency weighting `size × #turns-after` MODELS cache_read growth (each resident message re-read every later turn) — it is an approximation of the real KV-cache prefix, not the billed number; if the model diverges from actual, `residual_pct` (modeled-total vs Σ cache_read) surfaces it — cost: category shares stay directionally right (which surface dominates) even when absolute calibration is loose.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `benchmark/anatomy.py` `benchmark/tests/`
Strategy & known-problem fixes: 1. RED tests first (benchmark/tests/test_token_anatomy.py) over a SYNTHETIC fixture transcript (hand-built JSONL: a PROJECT.md Read, an `add.py status` Bash, a source Edit, a test Bash, each with known sizes + usage) so attribution is exactly checkable: (a) M1/M4 — the PROJECT.md read lands in `method_doc`, the `add.py` bash in `engine_output`, the source/test IO in `build_work`; (b) M2 — an early doc read outweighs a late one (residency); (c) M3 — identical input → identical dict, and a no-usage transcript → all zeros without raising; (d) R1 — a missing path raises `anatomy_no_transcript`. 2. build `token_anatomy` + helpers. 3. sanity-run on the REAL add-v2meter-r0/wm1 transcript, assert ≥95% attributed + method_doc/engine_output > 0. Trap: match tool_use_id ACROSS messages (assistant tool_use precedes the user tool_result) — build the id→tool_use map in one forward pass. Trap: `#turns-after` counts ASSISTANT turns strictly after M's index (residency), not all messages.
Approach (domain strategy): "residency-weighted attribution"

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
Strategy actually used: as planned — RED suite (synthetic fixtures with known sizes + a real-transcript sanity pass) before build; `token_anatomy` + helpers; tool_use→tool_result matched via a one-pass forward id map; residency = assistant turns strictly after each message. Diverged: none in shape. Discovered at verify: `attributed_pct` is 1.0 by construction (every message maps to a named cat, so named/total weight ≡ 1) — faithful to the frozen §3 definition but a weak invariant, not a calibration residual; recorded as a §6 OBSERVE [SPEC·open], NOT patched into the frozen contract.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `token_anatomy('benchmark/runs/add-v2meter-r0/wm1/transcript.jsonl')` returns `turns=144`, `total_cache_read=14275240`, and `categories` summing to that total with `method_doc=896467` (6%) and `engine_output=5477937` (38%) both > 0 — re-running yields the identical dict. Confirmed live (the CLI probe above) + pinned by `test_real_add_transcript_attributes_ceremony` + the 8 synthetic-fixture tests (221 in `benchmark/tests/` green).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-15

OBSERVE:
- [SPEC · open] `attributed_pct` is 1.0 by construction (every message → a named category ⇒ named-weight/total-weight ≡ 1), so `>= 0.95` is a vacuous invariant, not a model-fidelity check. A genuinely informative residual would be a CALIBRATION residual: the modeled residency-weight total vs the ACTUAL Σ cache_read (surfacing the untracked prefix — system prompt + tool schemas — that transcript messages don't explain). Add in a follow-up (candidate for anatomy-report); do NOT retrofit the frozen contract. (evidence: live run attributed_pct==1.0 exactly on add-v2meter-r0/wm1)
- [SPEC · open] the anatomy REFRAMES the milestone's Why: cache-read is driven by engine_output (38%) + conversation (36%), NOT method_doc (6%, PROJECT.md). Ceremony optimization should target re-read `add.py` output before doc residency. (evidence: categories on add-v2meter-r0/wm1 = method_doc 896467 · engine_output 5477937 · build_work 2797911 · conversation 5102925)
