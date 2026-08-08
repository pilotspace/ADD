# TASK: switch SKILL orient call to status --brief; retain PROJECT.md+SOUL.md prose

slug: status-brief-adoption · created: 2026-07-15 · stage: mvp
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
Feature: the SKILL orient step calls `add.py status --brief` (resume essentials) instead of bare `status` (75-line/5.4k dump re-read every session), moving the "read PROJECT.md + SOUL.md" orient guidance into the skill PROSE — cutting status's re-read cache-weight (29.8% of engine_output) while the AI still gets the resume point + next command + orient files. DOC-only: the engine's bare-`status` output is untouched.
Must:
  - M1: the SKILL.md "Always start here (orient)" fenced command is `python3 .add/tooling/add.py status --brief` (not bare `status`) — in BOTH SKILL trees (source + `_bundled`), kept byte-identical (test_bundle_parity).
  - M2: the orient PROSE still instructs reading `.add/PROJECT.md` AND `.add/SOUL.md` as the two orient files — the load-bearing guidance survives the switch to `--brief` (which does not name them), reworded so the prose is the authority, not the command output.
  - M3: DOC-only — no `add.py`/`add_engine` edit (ENGINE_MD5 + ENGINE_PKG_MD5 UNCHANGED); the engine's bare-`status` and `status --brief` behavior are both unchanged; the full-status prose in loop/streams/report/release/graduate (which needs the roster/DAG/m-goal) stays bare `status`.
Reject:
  - R1: an edit that drops PROJECT.md or SOUL.md from the orient prose -> `orient_floor_lost` (the switch must PRESERVE the orient-files instruction; a diet that loses guidance is a defect).
Accept: SKILL.md (both trees) orient block reads `status --brief`, the orient prose still names PROJECT.md + SOUL.md, `git grep -c "md5(add.py)"`-pinned ENGINE_MD5 is unchanged, and the full engine suite stays green (no bare-status census/pin broken).
Boundary: the ORIENT call (switched to `--brief`) vs the advanced-flow prose calls in loop/streams/report/release/graduate (stay bare `status` — they read the roster/DAG/m-goal `--brief` omits) — the change is scoped to the orient block only.
Assumptions: ⚠ `status --brief` carries enough to orient (resume point + next + the no-project init signal) so the switch loses nothing the flow branches on — verified live (--brief prints the same `no .add/ project found` error and the `task:·phase:`+`next:` resume); if wrong, an orient branch mis-fires; cost: agent re-runs bare `status` (self-heals, no data loss).

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `add-method/skill/add/SKILL.md` — the "Always start here (orient)" fenced command (bare `status` → `status --brief`) + the following orient-files sentence (reworded so the prose instructs "read PROJECT.md + SOUL.md" directly, since `--brief` no longer names them).
  - `add-method/src/add_method/_bundled/skill/add/SKILL.md` — the same two edits (bundle twin; test_bundle_parity enforces byte-identity).
Context (working folder): live-verified — `status --brief` prints the same `no .add/ project found` init signal AND the `task:·phase:`+`next:` resume line; the full-status advanced flows (loop/streams/report-template/release/graduate) read roster/DAG/m-goal `--brief` omits → they STAY bare `status` (out of scope).
Honors (patterns / conventions): SKILL trees kept byte-identical (test_bundle_parity CANON vs BUNDLE) · load-bearing orient floor (resume + next + PROJECT.md/SOUL.md) · doc-only ⇒ NO ENGINE_MD5/ENGINE_PKG_MD5 re-pin (call-residuals lesson: doc/template edits don't repin).
Anchors the contract cites: `SKILL.md` orient block, `status --brief`, `.add/PROJECT.md`, `.add/SOUL.md`.
Ground SHA: 84f60ae — stamped by freeze

### Contract

```
SKILL.md "## Always start here (orient — do not skip)" block, BOTH trees:
  fenced command  ->  python3 .add/tooling/add.py status --brief     (was: bare `status`)
  orient prose     ->  still instructs reading .add/PROJECT.md AND .add/SOUL.md (the two orient files),
                       reworded so the PROSE is the authority (not "status names them")

  invariants:
    - the orient files PROJECT.md + SOUL.md remain named in the orient prose (R1 orient_floor_lost guard)
    - source SKILL.md == _bundled SKILL.md (byte-identical)
    - no add.py / add_engine edit -> ENGINE_MD5 + ENGINE_PKG_MD5 unchanged
    - bare `status` engine output + the advanced-flow prose calls unchanged
```

`Least-sure flag surfaced at freeze:` [test] the switch relies on the SKILL PROSE (not the command output) carrying the PROJECT.md/SOUL.md orient instruction — if a future edit trims that sentence thinking "status shows it", the orient floor silently drops; the R1 test pins both names in SKILL.md so CI catches it.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/skill/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/tooling/test_status_brief_orient.py`
Strategy & known-problem fixes: 1. RED: `test_status_brief_orient.py` — (M1) both SKILL trees' orient block contains `status --brief` and NOT a bare `add.py status\n` fenced line in that block; (M2/R1) both trees name `.add/PROJECT.md` and `.add/SOUL.md` in the orient prose. 2. edit both SKILL.md trees (command + prose rewording). 3. LIVE: `status --brief` orients (resume + next + no-project signal) — already verified. 4. run the FULL engine suite — a bare-`status` census/pin test may reference the old orient text; if one legitimately pins the OLD orient command, forward-migrate it (sanctioned) or confirm it targets a different surface. Trap: edit BOTH trees or test_bundle_parity fails. Trap: keep the advanced-flow bare-`status` prose (loop/streams/report/release/graduate) untouched — they need full status. Trap: DON'T re-pin ENGINE_MD5 (no add.py edit).
Approach (domain strategy): "orient-lean, prose-carried floor"

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
Strategy actually used: as planned — orient fenced command `status`→`status --brief`; the "`status` names two orient files" sentence reworded to "Then read the two orient files: PROJECT.md … and SOUL.md …" (prose now the authority). DIVERGED from the contract's "BOTH trees": there are THREE skill trees — canonical `add-method/skill/add/`, `_bundled`, AND the tracked dogfood `.claude/skills/add/` — the contract undercounted; all three synced (the x3 tree-parity suite enforces it). No add.py/add_engine edit → ENGINE_MD5/PKG unchanged.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full engine suite 3633 green)
- [x] green was EARNED — asserts pin the orient block's `--brief` command + PROJECT.md/SOUL.md prose across trees; x3 tree-parity enforces all trees carry it
- [x] input dialect held — the test speaks the real SKILL orient-block markdown + command strings
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure markdown doc edit (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): the SKILL.md orient block (all 3 trees byte-identical, md5 `44b41fee…`) reads```python3 .add/tooling/add.py status --brief``` with the following prose "Then read the two orient files: `.add/PROJECT.md` … and `.add/SOUL.md` …"; ENGINE_MD5 still `1dd8c1b1` (unchanged, no add.py edit). Confirmed live + pinned by `test_status_brief_orient` (3) + the x3 tree-parity suite (89 parity tests green).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-15

OBSERVE:
- [SPEC · open] the skill ships in THREE trees (canonical · `_bundled` · tracked dogfood `.claude/skills/add/`) — the contract said "both", undercounting; a SKILL.md edit that syncs only 2 trips 11 x3-parity tests. Pairs with help-diet's FOUR-add.py-twins lesson: the engine's twin/tree multiplicity is under-documented — a "sync all copies" preflight (glob every tracked SKILL.md / add.py) would prevent the mid-suite parity failures both tasks hit. (evidence: this task's 11 parity failures, all skill-tree byte-identity)
