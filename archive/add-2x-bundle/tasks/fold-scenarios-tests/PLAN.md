# PLAN: Retire §2, retitle §4 TESTS & SCENARIOS, primary-only rigor

slug: fold-scenarios-tests · created: 2026-07-23 · stage: mvp · risk: high
milestone: scenarios-into-tests
autonomy: conservative
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Retire the standalone §2 SCENARIOS section — fold its role into a retitled §4 "TESTS & SCENARIOS" — and make §4 rigor primary-only. Keep §3–§7 numbers, the freeze parser, and the ~380 §3–§7 references untouched (retire-in-place, not renumber).
Framings weighed: retire-in-place (chosen — §4 absorbs the scenario role, §2 heading deleted, §3–§7 numbers frozen; zero freeze/engine-parser risk, mirrors the phase-merge precedent) · contiguous-renumber §3→§2…§7→§6 (rejected — rewrites the freeze parser, ~380 refs, the whole test corpus, and every archived PLAN.md)
Must:
<must>
  - M1 A newly rendered PLAN.md (from templates/PLAN.md.tmpl) carries NO `## 2` SCENARIOS heading and NO scenarios form-tag.
  - M2 The tests section heading reads `## 4 · TESTS & SCENARIOS`.
  - M3 The closed form-tag vocab is exactly must, reject, after, assumptions, test_plan — the scenarios tag is retired; the template opens/closes each surviving tag exactly once and carries no tag outside that vocab.
  - M4 The constants _FALLBACK_TASK circuit-breaker stays in parity with the template on M1+M2 (no SCENARIOS heading, tests section retitled).
  - M5 rule-id-coverage passes when every §1 Must/Reject is covered by a §4 covers tag alone, on a doc with NO section-two present.
  - M6 freeze still targets §3 and stamps FROZEN on a section-two-less doc — the §3-is-the-frozen-core invariant is preserved.
  - M7 The §4 body states the rigor policy in prose: one red test per §1 Must/Reject (primary + primary edge cases); minor behaviors are prose build-guidance — no covers tag, no red test, not gated.
  - M8 A legacy PLAN.md that still carries a `## 2` SCENARIOS section keeps parsing and advancing (backward-compatible; old boards never break).
</must>
Reject:
<reject>
  - a template edit that drops a load-bearing engine anchor the parser greps (the §3 heading, `Tests live in:`, `Status: DRAFT`) -> "template_anchor_lost"
</reject>
After:
<after>
  - `add.py new-task` yields a lean 6-visible-section PLAN.md (§1,§3,§4,§5,§6,§7), the tests section owns the cases, and the whole tooling suite is green.
</after>
Boundary: two PLAN.md shapes the tests must speak — (a) the new section-two-less doc, and (b) a legacy section-two-bearing doc that must still parse.
<assumptions>
  ⚠ Riskiest: that NO engine path HARD-requires a `## 2` heading to exist (freeze targets §3, --fill for direction targets §1, rule-coverage tolerates an empty/absent §2). If some path dies on a missing §2 — cost: a folded task can't advance. Guarded by M6 + M8 (freeze + parse a §2-less doc end-to-end).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  (none — this task DOGFOODS its own change: every case is encoded in the §4 test_plan via covers tags. This §2 note demonstrates the target end-state where scenarios live with the tests.)
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
PLAN.md section schema — FROZEN SHAPE (post-change):
  ## 1 · SPECIFY                 (unchanged)
  ## 3 · PLAN                    (unchanged — still the frozen HARD core; freeze targets ^## 3 ·)
  ## 4 · TESTS & SCENARIOS       (RETITLED; absorbs the scenario role)
  ## 5 · BUILD  ## 6 · VERIFY  ## 7 · OBSERVE   (unchanged)
  — NO `## 2` SCENARIOS heading is rendered —
Closed form-tag vocab: { must, reject, after, assumptions, test_plan }   — scenarios RETIRED
§4 rigor line (prose, in the template body): one red test per §1 Must/Reject
  (primary + primary edge cases); minor behaviors = prose build-guidance, not gated.
Parity contract: templates/PLAN.md.tmpl  ==  add_engine/constants._FALLBACK_TASK  on the two shape changes.
Preserved invariants (NOT touched by this task):
  - freeze targets the literal `^## 3 ·` heading; §3 stays the tamper-guarded core.
  - rule-id-coverage gates on §1 Must/Reject IDs via §4 covers: (the gate is NOT loosened).
  - `scenarios` stays a RETIRED skip token (_RETIRED_SKIP_TOKENS) — legacy boards tolerated.
  - all ENGINE_ANCHORS in test_template_atomic survive (assertIn; `## 4 · TESTS` is a substring of the retitle).
Twin parity (build must mirror, not just source): add-method/tooling ⇄ .add/tooling ⇄ src/add_method/_bundled/tooling + engine_pin re-md5.
```

Target (measurable): `new-task` renders a §2-less, §4-retitled PLAN.md; the FULL add-method tooling suite is green (with the 2 schema-conformance tests migrated to the new vocab); 0 edits to the freeze parser and 0 to the ~380 §3–§7 references.
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
  ⚠ [contract] that NO engine path hard-requires a `## 2` heading — cost if wrong: a folded task can't advance. Mitigated by the 4 green guards (freeze + parse on §2-less AND legacy §2-bearing docs).
Reported: yes — the freeze report (SHAPE/SUMMARY/FLAGS/EVIDENCE) rendered before this froze

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/skill/add/` `add-method/docs/` `add-method/.add/tooling/` `.add/tooling/` `.claude/skills/add/` `add-method/src/add_method/_bundled/`

Regression floor: the full `add-method/tooling/test_*.py` suite (host repo's own tests) must stay green — run before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md`

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_template_has_no_scenarios_section: render/read PLAN.md.tmpl · assert no `## 2` SCENARIOS heading AND no scenarios form-tag · covers: M1
  - test_section_four_retitled: assert `## 4 · TESTS & SCENARIOS` present in the template · covers: M2
  - test_frozen_tag_vocab_drops_scenarios: paired form-tags in the template == {must,reject,after,assumptions,test_plan} · covers: M3
  - test_fallback_parity: constants._FALLBACK_TASK has no `## 2` heading and a retitled tests section · covers: M4
  - test_rule_coverage_passes_without_section_two: synth doc §1 Musts + §4 covers, NO §2 -> _rule_coverage_gaps() == [] · covers: M5
  - test_freeze_targets_section_three_on_folded_doc: freeze a §2-less PLAN.md -> §3 Status flips FROZEN, no error · covers: M6
  - test_section_four_states_primary_only_rigor: assert the primary-only rigor sentence is in the §4 template body · covers: M7
  - test_legacy_scenarios_doc_still_parses: a legacy §2-bearing doc -> _phase_spans returns §2 and §4, freeze/advance succeed · covers: M8
  - test_engine_anchors_survive: every test_template_atomic ENGINE_ANCHOR still assertIn the retitled template · covers: R:template_anchor_lost
</test_plan>

Primary vs minor (this task's OWN rigor floor): the nine tests above are the PRIMARY contract — each red-first. Minor/secondary polish (book prose wording in docs/, SKILL.md phrasing, the §2 removal comment style) is prose build-guidance below — NOT gated by a red test.

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned + a scope-widening signed re-cross. Retired §2 from PLAN.md.tmpl AND constants._FALLBACK_TASK, retitled §4 → "TESTS & SCENARIOS", added the primary-only rigor prose. Migrated the 2 named conformance tests (FROZEN_TAGS/FORM_TAGS drop `scenarios`) — AND 4 more §2-coupled suites the freeze under-declared (fast_boundary_line §2→§3 · tiny_plan §2→§4 marker · phase_bundles DIRECTION span drops §2 · rule_id_coverage `_set_section` synthesizes a legacy §2 so the still-supported §2 branch stays tested). Defolded add.py's 3 blurbs + the rule-coverage warning message (kept the tolerant sec2 read for legacy boards). Reframed direction.md + SKILL.md. 4-way engine twin sync + engine_pin double re-md5 (ENGINE_MD5 + ENGINE_PKG_MD5). Full 2236-test floor green.
Code lives in: `add-method/tooling/` + `add-method/skill/add/` (method engine + guides; twins mirrored)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite): full 2236-test tooling floor OK
- [x] coverage did not decrease — 9 NEW tests added (test_scenarios_folded); no test deleted
- [~] no test or contract was altered during build — the frozen §3 CONTRACT is UNTOUCHED. Tests WERE altered: 6 §2-coupled suites migrated to the new frozen vocab (2 named in §3 + 4 the freeze under-declared) — sanctioned via a SIGNED re-cross that re-armed the tripwire + scope snapshot; NOT a silent build-time test edit.
- [x] the green was EARNED, not gamed — the 5 net-new-behavior tests went RED first for the right reason; each of the 9 floor failures was verified a schema-coupling (fixture §-number relocation), not a masked regression; no vacuous assert or stubbed logic
- [x] concurrency / timing — n/a (pure template/engine-text change, no runtime IO or concurrency)
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new deps; stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — engine twins + pins kept in lockstep (test_tree_parity green)
- [ ] a person reviewed and approved the change — PENDING this gate

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) tried to find an engine path that HARD-requires §2 — freeze targets §3, --fill/direction targets §1, rule-coverage tolerates absent §2; the 4 green guards exercise freeze+parse on both §2-less and legacy §2-bearing docs. (2) confirmed each of the 9 full-suite failures was a fixture schema-coupling, not a real behavior regression, before touching it. (3) confirmed the migrated conformance/coupled tests still assert real behavior (rule_id_coverage now builds a legacy §2 doc rather than dropping the §2 branch). Residual: a cross-agent refute-read was not spawned (solo build) — flagged for the human.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose retire-in-place; rejected contiguous-renumber §3→§2…§7→§6 (rejected — rewrites the freeze parser, ~380 refs, the whole test corpus, and every archived PLAN.md)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned + a scope-widening signed re-cross. Retired §2 from PLAN.md.tmpl AND constants._FALLBACK_TASK, retitled §4 → "TESTS & SCENARIOS", added the primary-only rigor prose. Migrated the 2 named conformance tests (FROZEN_TAGS/FORM_TAGS drop `scenarios`) — AND 4 more §2-coupled suites the freeze under-declared (fast_boundary_line §2→§3 · tiny_plan §2→§4 marker · phase_bundles DIRECTION span drops §2 · rule_id_coverage `_set_section` synthesizes a legacy §2 so the still-supported §2 branch stays tested). Defolded add.py's 3 blurbs + the rule-coverage warning message (kept the tolerant sec2 read for legacy boards). Reframed direction.md + SKILL.md. 4-way engine twin sync + engine_pin double re-md5 (ENGINE_MD5 + ENGINE_PKG_MD5). Full 2236-test floor green.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] Book + engine §2 long-tail deferred (non-gated): fold `docs/04-step-2-scenarios.md` into the step-4 tests chapter + renumber the nav chain (7 cross-refs), and drop the inert `2` from `_PHASE_SECTIONS["direction"]` → `(1,3,4)` (+ its test pin at test_phase_merge_verify.py:194). (evidence: cross-agent refute-read residue list — all links resolve, engine consumers guarded, nothing broken)
- [SPEC · open] Build-strategy block trim: keep enforced `Scope` (relabel — it is HARD scope-lock, mislabeled SOFT), make `Regression floor` + `Persona` implicit/optional. (evidence: user question 2026-07-23 — Scope earns its keep, the other two lines are thin)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [ADD · open] Retire-in-place beats renumber for a number-keyed §-schema: delete §2 + retitle §4 = 1 task; the engine tolerates a non-contiguous §1→§3 doc because `_phase_spans` is dict-keyed, not ordinal. A contiguous renumber would have rewritten the freeze parser + ~380 refs + the whole test corpus. (evidence: freeze parser + 2236-floor untouched; task shipped in one bundle)
- [ADD · open] A schema change under-counts its coupled tests at freeze — beyond the 2 obvious conformance suites, 4 more fixtures encoded the old §2; the SIGNED re-cross is the sanctioned scope-widening, not a defect. (evidence: 6 suites migrated; re-cross re-armed tripwire+scope)
- [TDD · open] A "migrated" fixture can go vacuous — when a helper targets a retired section, make it SYNTHESIZE the legacy shape so the still-supported branch stays genuinely exercised. (evidence: rule_id_coverage._set_section builds a legacy §2; advisor confirmed non-vacuous)
