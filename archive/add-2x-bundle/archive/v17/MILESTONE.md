# MILESTONE: prompt-clarity

goal: Rewrite the agent-facing prompt surface to be literal, direct, and positively-framed — with semantics provably preserved — without breaking the method's defined vocabulary
stage: mvp · status: active · created: 2026-06-06

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> Research-grounded (2026 synthesis, primary sources). The two asks are evidence-backed:
> idioms parse inconsistently across calls (DICE: GPT-4o ~49% literal/figurative consistency);
> negation is structurally under-followed (NeQA inverse scaling; "Prohibitions→Permissions":
> negative framing 77% vs positive 24% endorsement of prohibited acts). Anthropic states it
> directly: "Tell Claude what to do instead of what not to do." The governing CAUTION shapes the
> measurement design: brittleness is SYMMETRIC — even meaning-preserving rewordings cause 18–62%
> compliance swings, and the SAME prompt varies run-to-run (IFEval++ reliable@10). So the BLOCKING
> gate is DETERMINISTIC semantic-preservation (no rule dropped or changed in meaning); a behavioral
> eval of agent judgment is model-in-loop and noisy, kept INDICATIVE (prose≠enforcement), never a gate.

## Scope
In:  A wording rewrite of the agent-executable prompt surface — `skill/add/` (18 files) +
     `docs/appendix-b-prompts.md` — to: (1) replace idioms/figurative/ambiguous phrasing with
     literal operational language; (2) convert negative framing to positive imperatives WHERE a
     clean positive exists; (3) dial back aggressive emphasis (CAPS/NON-NEGOTIABLE/NEVER walls)
     to plain imperative, reserving strong emphasis for ≤3 true hard-stops; (4) add explicit SCOPE
     qualifiers to phase-wide rules. PLUS two structural wins: trim the ~290 words of always-loaded
     summary out of `SKILL.md`, and move `run.md`'s auto-gate + high-risk rules from prose INTO
     existing `<constraints>` blocks. All behind a FROZEN rubric, enforced by a `wording-lint`, and
     GATED by a DETERMINISTIC semantic-preservation inventory (every reject code · Must/Reject ·
     gate outcome · numeric threshold · scope qualifier survives the rewrite, unchanged in meaning).
Out: Method SEMANTICS (flow, gates, autonomy, CLI behavior) — UNCHANGED; this is phrasing, not rules.
     A RIGOROUS behavioral eval harness (model-in-loop, N-sampled, graded across agents) — DEFERRED
     to its own milestone; v17 includes only a NON-GATING behavioral spot-check at close. Splitting
     `<constraints>` into a finer tag taxonomy — DEFERRED (reopens v16's frozen 5-tag closed
     vocabulary). Authoring new `<example>` few-shot blocks — DEFERRED (its own content milestone).
     Harness-ENFORCED hard-stops (a deterministic security/contract gate in code) — DEFERRED. Release/
     version bump — deferred.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **The wording rubric** (frozen by `wording-rubric`): the idiom→direct map · the KEEP-LIST of
  load-bearing method terms · the NEGATIVE-KEEP-LIST · the emphasis policy · the scope-qualifier
  rule. The frozen spec lives in `wording-rubric` §3 CONTRACT.
- **Semantics-preserving is the prime invariant** (glossary delta): a rewrite changes PHRASING, never
  the RULE. No reject code, gate, autonomy dial, touch-boundary, or contract may change MEANING. A
  reword that alters semantics is reject `semantics_changed` — route it as a change-request, not a
  wording edit.
- **Gate on semantic preservation; behavioral eval is INDICATIVE, not a gate.** The blocking proof a
  rewrite is safe is the DETERMINISTIC inventory diff (every semantic unit still present, unchanged) —
  this is CI-able and gates each rewrite task. A behavioral eval (does a real agent escalate/ask/
  classify correctly?) tests JUDGMENT, is non-deterministic + model-specific, and is recorded as an
  indicative confidence signal only — never a blocking before/after diff. Honors `words-exist≠method-works`.
- **"Provably preserved" is operationally NECESSARY-not-SUFFICIENT** (ratified at the `semantic-inventory`
  contract freeze, 2026-06-06): the deterministic gate proves preservation is NECESSARY-true — nothing
  dropped/renamed/relocated, every safety invariant's anchors intact in a tight window, no listed exception
  introduced. It does NOT prove SUFFICIENT preservation: an INVERSION around surviving anchors (an added
  "unless…"/negation/scope-narrowing that keeps every anchor word) is model-judgment and is CEDED, by name,
  to human review + the indicative behavioral eval. So the goal's "semantics provably preserved" = the gate
  (necessary) + review + indicative eval (the rest), never the gate alone. `clarity-greenstate` must record
  "preserved: PASS" against THIS definition (gate + review + eval), not claim the gate alone proves it.
- **The keep-list is sacred**: load-bearing vocabulary (`one-approval front` · `touch-boundary` ·
  `fold` · `competency delta` · `least-sure flag` · `the trust layer` · `HARD-STOP`/`RISK-ACCEPTED`/
  `PASS` · `evidence auto-gate` · the v16 XML tag names) is NOT reworded — renaming breaks GLOSSARY,
  cross-refs, and tests (`test_declare_grammar_doc` et al.). Reword AROUND these terms, never them.
- **Keep negatives where they are the right tool** (research caveat): a negative STAYS for a hard
  floor/ceiling, a security/safety boundary, or a prohibition with no clean positive form — each
  carrying a `# why:` rationale (Anthropic: constraint+reason beats bare constraint). Positivize the
  REST.
- **The run.md structural win needs a ratified guard update**: moving `## The evidence auto-gate` /
  `## The autonomy dial` prose into `<constraints>` adds paired tags to sections `test_xml_convention`
  (`ENGINE_FILES`) lists as run.md's NARRATIVE-UNTAGGED. Per the frozen-guard convention (fix the
  build output, never the matcher silently), `rewrite-core`'s contract carries that ENGINE_FILES edit
  as a human-ratified change-request — not a silent inline change.
- **v16 convention honored**: the XML 5-tag closed vocabulary stays frozen. The structural win moves
  prose INTO an existing `<constraints>` block — it does NOT add or split tags.
- **Mirror parity**: every `skill/add/` edit → `_bundled/` → `.claude/skills/add` byte-identical
  (`test_bundle_parity` + `test_tree_parity` backstop); appendix-b → its 3 tracked copies.

- **Surface-wide idiom promotion, BOTH FORMS** (held at the rewrite-core freeze 2026-06-06; RATIFIED at
  the rewrite-guides freeze, 2026-06-07, Tin Dang): an idiom flips `[mapped]`→`[enforced]` in the SAME
  commit that removes its LAST occurrence from the WHOLE lint surface, clearing BOTH written forms
  (hyphen + space — F1's matcher is form-strict, so the space/hyphen twin must be cleared by hand); a
  both-forms escape on an ALREADY-enforced idiom is cleared by whichever rewrite task owns the file.
  Live proof that motivated the both-forms clause: `blast-radius` survived in `phases/7-observe.md`
  with the lint green after `blast radius` was enforced. Binds `rewrite-guides` + `clarity-greenstate`
  (whose exit asserts `enforced_banned == full idiom_map`) + any future wording task. The §4
  both-forms regex test (`test_rewrite_guides.py`) is the standing fence for the form-escape class.

## Shared / risky contracts (freeze these first)
- The wording RUBRIC (idiom map · keep-list · negative-keep-list · emphasis/scope policy · reject codes) -> owning task `wording-rubric`
- The semantic-preservation INVENTORY (the frozen set of semantic units every rewrite must keep) + its diff test -> owning task `semantic-inventory`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] wording-rubric     depends-on: none                              — freeze the rubric + keep-lists + emphasis/scope policy; ship the `wording-lint` (red/green)
- [x] semantic-inventory depends-on: none                              — extract the per-file semantic-unit inventory (reject codes · Must/Reject · gate outcomes · thresholds · scope qualifiers); ship the deterministic preservation-diff test (the blocking gate)
- [x] rewrite-core       depends-on: wording-rubric,semantic-inventory — rewrite SKILL.md + 9 engine docs to the rubric + the 2 structural wins; semantic-inventory green; carry the run.md ENGINE_FILES change-request
- [x] rewrite-guides     depends-on: wording-rubric,semantic-inventory — rewrite the 8 phase guides + appendix-b to the rubric; semantic-inventory green
- [x] clarity-greenstate depends-on: rewrite-core,rewrite-guides       — full suite + wording-lint + semantic-inventory + 3-mirror parity + audit; assert `enforced_banned == every idiom in idiom_map` (the promotion protocol actually ran — no idiom left `[mapped]` and un-retired, which would keep the lint trivially green); PLUS a NON-GATING behavioral spot-check (a few hard-stop scenarios via a real agent, recorded as indicative); close

## Exit criteria (observable; map each to the task that delivers it)
- [x] The wording rubric is frozen + `wording-lint` is green over the surface          (← wording-rubric)
- [x] The semantic-preservation inventory is captured + its diff test is green          (← semantic-inventory)
- [x] SKILL.md + engine docs carry the rubric; ~290 W always-loaded summary trimmed; run.md auto-gate/high-risk in `<constraints>` (ENGINE_FILES change-request ratified); inventory unchanged  (← rewrite-core)
      ↳ met-WITH-deviation, ruled at the close 2026-06-07 (Tin Dang): the actual safe trim was 180 W — the deliberate stop that kept load-bearing prose; ~290 W was an estimate, not an obligation.
- [x] The 8 phase guides + appendix-b carry the rubric; inventory unchanged             (← rewrite-guides)
- [x] Whole suite + wording-lint + semantic-inventory + 3-mirror parity + `add.py audit` green; `enforced_banned == full idiom_map` (every mapped idiom was promoted, not left un-retired); the non-gating behavioral spot-check is run + recorded as indicative  (← clarity-greenstate)
