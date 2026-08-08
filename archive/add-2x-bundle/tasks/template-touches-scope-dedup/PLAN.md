# TASK: templates dedup: §3 Touches names symbols, §5 Scope owns the file write-set

slug: template-touches-scope-dedup · created: 2026-07-14 · stage: mvp
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
Feature: templates de-duplicate the §3-Touches / §5-Scope file list — the two TASK templates (full + fast) nudge the agent to write the file write-set ONCE (§5 Scope owns it) and let §3 Touches name only symbols/anchors, killing the double file-list authoring the WM1 re-measure showed (the same duplication scope-first-draft's own Grounding had to fix by hand).
Must:
  - both templates' §3 `Touches (files · symbols…):` placeholder VALUE tells the agent to name symbols/anchors and NOT re-list the full file set, pointing to §5 Scope as the write-set owner
  - both templates' §5 `Scope (may touch):` placeholder VALUE declares itself the single source of truth for the file write-set, pointing back to §3 Touches as the symbol namer
  - the field LABELS are byte-unchanged (`Touches (files · symbols…):` · `Scope (may touch):`) — only the `<…>` placeholder guidance text changes; no engine/parser/gate behavior touched
  - canonical and bundle template trees stay byte-identical (test_bundle_parity)
Reject:
  - none — documentation-string change only; no code path, parser, or gate altered (milestone OUT-of-scope). The one label-integrity guard (test_seams_template_wiring pins the LABELS) must stay green unchanged
Accept: Given the full and fast TASK templates, When an agent reads §3 Grounding and §5 Build-strategy, Then the §3 Touches placeholder says "name symbols, not the full file list — §5 Scope owns the write-set" and the §5 Scope placeholder says "single source of truth for the file write-set", so the file list is authored once
Boundary: none — no external input shape; the change is static template text read by humans/agents, asserted by string-presence
Assumptions: ⚠ the duplicated file list (Touches listing files AND Scope listing the same files) is a real token/call cost, not just cosmetic — evidence: scope-first-draft's Grounding had to be hand-deduped this session on the user's "fix grounding and plan as duplicated scope, touch" instruction; if wrong (agents ignore the hint): no harm, pure guidance text

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): the §3 Touches + §5 Scope placeholder lines in both TASK templates (`TASK.md.tmpl:Touches`/`:Scope`, `TASK.fast.md.tmpl:Touches`/`:Scope`) — plus the one content-pinning test that migrates with the fast placeholder (`test_fastlane_ground_lite.py:_replace-target`)
Context (working folder): `add-method/tooling/templates/` (canonical). The full file write-set — both canonical templates, both bundle twins, the two gitignored dogfood twins, the new + migrated tests — is the §5 Scope below (not re-listed here)
Honors (patterns / conventions): LABELS are frozen (test_seams_template_wiring pins them) — reword only the `<…>` value; propose-not-impose in the templates themselves (the whole task is guidance text); test_bundle_parity holds canonical==bundle
Anchors the contract cites: the §3 `Touches (files · symbols…):` placeholder value · the §5 `Scope (may touch):` placeholder value · both LABELS (unchanged) · test_bundle_parity
Ground SHA: 5fe143b — stamped by freeze

### Contract

```
TASK.md.tmpl AND TASK.fast.md.tmpl, §3 Grounding `Touches (files · symbols…):` LINE:
  → LABEL byte-unchanged; placeholder <…> value now instructs: name the symbols/anchors
    you'll edit + how each is keyed, and "name symbols, not the full file list — §5 Scope
    owns the write-set"
TASK.md.tmpl AND TASK.fast.md.tmpl, §5 Build-strategy `Scope (may touch):` LINE:
  → LABEL + the `./src/` default token byte-unchanged; placeholder <…> value now declares
    "the single source of truth for the file write-set (§3 Touches names symbols, this
    names files); scope-lock source"
INVARIANTS (unchanged):
  → no engine/parser/gate/_declared_scope/_ground lint behavior changes — pure template text
  → canonical templates == bundle templates (byte) · both LABELS still present, original order
    (test_seams_template_wiring + test_bundle_parity stay green)
```

`Least-sure flag surfaced at freeze:` [contract] the exact placeholder wording — it is pure guidance text, so a reword is a cosmetic one-string change with no behavior shift; the only hard edge is keeping the LABELS + `./src/` token byte-identical so the two pin guards stay green.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/test_template_touches_scope_dedup.py` `add-method/tooling/test_fastlane_ground_lite.py`
Strategy & known-problem fixes: (1) RED first: new test_template_touches_scope_dedup asserts BOTH templates' §3 Touches value carries the "not the full file list / §5 Scope owns the write-set" phrase AND §5 Scope value carries the "single source of truth" phrase — RED now (absent). (2) reword the 4 placeholder values (2 templates × Touches+Scope), LABELS + `./src/` token byte-untouched (trap: test_seams_template_wiring pins the labels; test_bundle_parity pins canonical==bundle — sync both trees). (3) migrate the ripple: test_fastlane_ground_lite.py replaces the OLD fast Touches placeholder string in 2 spots — update those replace() targets to the new value (a content-pin migrating with its template, NOT a weakening), done in TESTS phase. (4) sync ×4 template twins (2 tracked + 2 gitignored dogfood). No ENGINE_MD5 / SEAMS change (no add.py edit).
Approach (domain strategy): documentation-layer only — 4 placeholder rewords + one content-pin migration; correctness-first, zero engine behavior change, dedup-by-guidance.

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
Strategy actually used: as planned — reworded the 4 placeholder VALUES (2 templates × Touches+Scope): §3 Touches now says "name symbols, not the full file list — §5 Scope owns the write-set"; §5 Scope now says "the file write-set, the single source of truth (§3 Touches names symbols, this names files)". LABELS + `./src/` token byte-untouched. The one ripple test (test_fastlane_ground_lite) was migrated in the TESTS phase to match the Touches line by label + `<…>` regex (robust to any future reword — greens against both old and new). Synced ×4 template twins (canonical + bundle tracked, 2 gitignored dogfood). No add.py edit → no ENGINE_MD5/SEAMS change.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full fence)
- [x] green was EARNED — target asserts (touches + scope) RED first for want of the reworded text; labels/parity green throughout; GREEN only after the reword
- [x] input dialect held — the test speaks the real template placeholder dialect (label + `<…>` value)
- [x] no exposed secrets, injection openings, or unexpected dependencies (pure documentation-string change; security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): both TASK templates' §3 Touches placeholder reads "name symbols, not the full file list — §5 Scope owns the write-set" and §5 Scope reads "the single source of truth for the file write-set"; labels + `./src/` token unchanged; canonical==bundle — confirmed by test_template_touches_scope_dedup (4 asserts) + test_seams_template_wiring (labels) + test_bundle_parity (twin bytes) + migrated test_fastlane_ground_lite, all green in the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

