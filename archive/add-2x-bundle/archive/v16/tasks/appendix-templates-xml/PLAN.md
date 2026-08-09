# TASK: Apply the v16 XML convention to appendix-b prompts (+ assess templates)

slug: appendix-templates-xml · created: 2026-06-06 · stage: mvp
autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: apply the v16 XML convention (frozen by `xml-convention`) to the v16 tail —
`docs/appendix-b-prompts.md` (the prompt library) and `tooling/templates/*.tmpl`. This closes the
WIDEST scope: tasks 1–3 converted the agent-EXECUTABLE skill surface; this task handles the two
remaining targets after a close reading showed what each actually is.
Framings weighed: wrap-the-intact-fence (chosen) · replace-fence-with-`<prompt>` · leave-appendix-as-is

appendix-b reproduces the `playbook/` prompts VERBATIM as a published, copy-able BOOK PAGE (it is
RENDERED, unlike the skill/ files an agent consumes as text). The user's direction call (AskUserQuestion,
2026-06-06) was to convert it into a genuine `<prompt>` catalog. The HOW is the load-bearing decision:
each prompt is wrapped by tagging its INTACT code fence — `<prompt>` + blank line + the ```…``` fence +
blank line + `</prompt>` — NOT by removing the fence.

Must:
  - Wrap each of appendix-b's playbook prompts (6) + the master skeleton (1) in a block-level `<prompt>`
    pair, leaving the code fence INTACT inside it. The blank line after `<prompt>` and before `</prompt>`
    is load-bearing: it lets CommonMark still parse the fence as a code block; the wrap tags render as
    invisible HTML. Fence-strip then leaves the `<prompt>` pair, so the vocab check sees it.
  - Keep every prompt BODY byte-for-byte (the "verbatim reproduction" contract): Role:/Read first:/Task:/
    Steps:/Exit:/Never: stay PLAIN TEXT inside `<prompt>`, the `# why:` annotations kept, the `<name>`/
    `<assumption>`/`<why>`/`<cost>` placeholders kept (safely inside the fence).
  - Vocabulary here is EXACTLY {prompt}. appendix-b carries NO `<output_format>`/`<exit_gate>`/
    `<constraints>`/`<reject_codes>`: a self-contained playbook prompt is one atomic block; its Exit:/Never:
    are part of the prompt's own instruction text, not a separate document-level gate (this is the frozen
    convention's stated rule for the appendix-b labels).
  - Propagate the converted file through all 3 tracked copies byte-for-byte — canonical `docs/` →
    `_bundled/docs/` (parity-enforced) → root `./appendix-b-prompts.md` — plus the `.add/docs/` dogfood copy.
  - ASSESS `tooling/templates/*.tmpl` (all 7): they are pure fill-in FORMS with `{{placeholders}}` and
    `<prose markers>` — NO executable structure (grep-confirmed: no `<prompt>`/`<constraints>`/`<reject_codes>`/
    `<output_format>`/`<exit_gate>`/"Reject codes"/"Non-negotiable"/"Never:"). Nothing to tag → no edit.
Reject:
  - remove a prompt's code fence (render its body as live markdown, swallowing `<name>`/`<action>`
    placeholders + mangling indented `# why:` lines)                              -> "page_mangled"
  - introduce any non-`prompt` convention tag into appendix-b                       -> "vocab_offmidiom"
  - tag the intro paragraph (narrative, before the first prompt)                    -> "narrative_tagged"
  - alter a prompt body / drop a `# why:` annotation                               -> "verbatim_broken"
  - edit canonical `docs/` without re-syncing `_bundled/` + root                   -> "mirror_drift"
After:
  - appendix-b's 7 prompts are each a `<prompt>`-wrapped intact fence; vocab ⊆ {prompt}; the page renders
    unbroken (no placeholder/indent leaks outside a fence); templates carry no tags (assessed no-op);
    the extended `test_xml_convention.py` is GREEN; full suite + `add.py audit` + bundle parity pass.
Assumptions — least-sure first:
  ⚠ Wrapping the intact fence (vs. removing it) is the right realization of "convert appendix-b's prompts."
    Least sure because the literal first instinct was to replace the fence with a `<prompt>` block. If wrong:
    the page renders broken while the vocab test stays green — a silent regression the structural test can't
    see. Mitigation: advisor-caught this session; the page was manually inspected post-build AND a
    render-safety guard (`test_appendix_render_safe`) now asserts no `<…>` placeholder / no ≥4-space-indent
    leaks outside a fence — the structural proxy for "the fence was wrapped, not removed". Cost if wrong: a
    doc-only follow-up; no contract reopened.
  - [ ] Templates genuinely have nothing executable to convert — grounded: all 7 grepped NONE FOUND for every
        convention marker; they are fill-in forms, not agent prompts. Recorded against the milestone criterion.
  - [ ] The root `./appendix-b-prompts.md` (tracked but NOT parity-enforced by any test) stays in sync —
        kept byte-identical by the propagation step, md5-verified this build.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: every prompt is a wrapped intact fence      # Must: <prompt> wraps a kept fence
  Given appendix-b's 6 playbook prompts + the master skeleton
  When the convention is applied
  Then each is enclosed in a <prompt>…</prompt> block
  And each block STILL CONTAINS its ```…``` code fence (the fence was wrapped, not removed)

Scenario: vocabulary is the prompt catalog subset     # Reject: vocab_offmidiom
  Given appendix-b with code fences stripped
  When all paired tags are collected
  Then each tag ∈ {prompt} (no output_format/exit_gate/constraints/reject_codes)

Scenario: the published page renders unbroken          # Reject: page_mangled
  Given appendix-b with code fences stripped
  When the remaining (out-of-fence) text is scanned
  Then NO bare <lowercase> placeholder remains (a removed fence would expose <name>/<action>)
  And NO prose line is indented ≥4 spaces (markdown would render it as code)

Scenario: the intro stays prose                        # Reject: narrative_tagged
  Given the intro paragraph before the first prompt
  When it is scanned
  Then it carries NO paired convention tags

Scenario: templates are forms, untouched               # Must: assessed no-op
  Given the 7 tooling/templates/*.tmpl files
  When scanned for any executable/convention structure
  Then none is found and none is tagged

Scenario: three tracked copies agree                   # Reject: mirror_drift
  Given the converted appendix-b
  When test_bundle_parity (docs) runs and root ./appendix-b-prompts.md is hashed
  Then canonical, _bundled/docs, and root are byte-identical
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The contract is the per-file APPLICATION of the v16 convention frozen in `xml-convention` §3 (unchanged
here). This task adds NO new vocabulary — appendix-b uses `<prompt>`, which already debuted in task 1.
The one new idiom is the RENDER-SAFE wrap layout for a published page:

```
APPENDIX-B CONVERSION — v16 (applies xml-convention §3; vocab = {prompt} only)

  per prompt (×7: playbook 1_specify..6_observe + master skeleton):

      ### `playbook/N_*.md`
      <prompt>
                          ← blank line (load-bearing: closes the HTML block)
      ```
      …prompt body, VERBATIM (Role:/…/Exit:/Never:, `# why:` notes, <…> placeholders)…
      ```
                          ← blank line (load-bearing)
      </prompt>

  RULES: fence stays INTACT (wrapped, never removed) · body byte-identical · vocab ⊆ {prompt} ·
  intro paragraph stays prose · 3 tracked copies byte-identical.

TEMPLATES (*.tmpl ×7): assessed — pure fill-in forms, NO executable structure → no edit, no tag.
```

Status: FROZEN @ v16 — approved by Tin Dang, 2026-06-06 (explicit direction call via AskUserQuestion:
"Convert appendix-b's prompts"; templates left as forms)   <!-- one-approval front. Applies xml-convention §3;
changing THAT is a change request back to xml-convention. -->
<!-- Least-sure flag at the freeze: ⚠ [contract] the wrap-INTACT-fence layout (not fence removal) — the
     only realization that keeps the book page rendering while applying the tag. Advisor-caught and
     manually render-verified this session; a structural guard now backs it. Nothing else uncertain —
     vocab is {prompt}, already frozen in task 1. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 6 scenarios asserted (content-assertions on the doc files; no runtime to cover by %).
Plan — EXTEND `test_xml_convention.py` with `TestXmlConventionAppendixB` (reusing `_paired_tags`,
`_strip_code_fences`, `_FENCE`, `_OPEN`):
  - `APPENDIX_SUBSET = {prompt}` (STRICT — appendix-b is a prompt catalog only).
  - `test_appendix_prompts_wrapped`: `len(<prompt> blocks) == len(code fences)` AND every block contains a
    fence (guards "fence wrapped, not removed").
  - `test_appendix_vocab_subset`: every paired tag (fences stripped) ∈ {prompt}; non-empty (converted).
  - `test_appendix_render_safe`: with fences stripped, NO `<lowercase>` placeholder and NO ≥4-space-indent
    line leaks outside a fence — the structural proxy for an intact page that a vocab-only check cannot make.
  - `test_appendix_intro_untagged`: the intro (before the first prompt) carries no paired tags.
  - parity: `test_bundle_parity` (docs tree) reused; root copy md5-checked in build.
  - Templates: no test (nothing to assert — assessed no-op, recorded at the milestone gate).

Tests live in: `add-method/tooling/test_xml_convention.py` · MUST run red (appendix-b not yet converted) before Build.
<!-- RED reason: appendix-b has no <prompt> blocks yet -> prompts_wrapped + vocab_subset fail; render_safe +
     intro_untagged pass trivially (they bite on a WRONG conversion, not the unconverted state). -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): preserve every prompt body byte-for-byte (verbatim reproduction); keep the
load-bearing blank lines; keep all 3 tracked copies byte-identical.
Code lives in: `add-method/docs/appendix-b-prompts.md` + `_bundled/docs/` + root `./appendix-b-prompts.md`
(+ `.add/docs/` dogfood). Templates: `tooling/templates/*.tmpl` — assessed, unchanged.
Constraints: do NOT change any test or the frozen convention; only `<prompt>` wraps; markdown only.

What was built:
  - appendix-b: 7 prompts wrapped via a verifying transform (`tmp/wrap_appendix_b.py`) that asserts fence
    BODIES are byte-identical before/after, `#<prompt> == #</prompt> == #fences`, every block contains a
    fence, and no placeholder leaks — THEN writes. Page manually inspected post-build (layout clean).
  - Propagated to `_bundled/docs/` + root `./appendix-b-prompts.md` + `.add/docs/`; all 3 tracked copies
    md5-identical (b7bc635c…).
  - Templates: assessed — all 7 `*.tmpl` grep-clean of every convention/executable marker; left untouched.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **474 passed / 0 failed** (test_xml_convention now 17/17: +4 appendix-b tests; bundle-parity docs guard green)
- [x] coverage did not decrease — `test_xml_convention.py` extended (+4 tests, `TestXmlConventionAppendixB`); no existing test weakened
- [x] no test or contract was altered during build — the 4 appendix tests were authored RED pre-build (2 failing for the right reason: no `<prompt>` blocks yet; 2 guard tests pass trivially and bite on a wrong conversion). Made green by the doc wrap only. xml-convention §3 untouched.
- [x] concurrency / timing — N/A (static markdown docs; no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown-only edits; no security surface; no deps added
- [x] layering & dependencies follow CONVENTIONS — 3 tracked copies byte-identical (md5 b7bc635c…); only `<prompt>` used; every prompt body verbatim (transform-asserted)
- [x] RENDER integrity (the blind spot a structural test can't see) — page manually inspected; `test_appendix_render_safe` asserts no placeholder/indent leaks outside a fence; the wrap keeps each fence a real code block
- [x] auto-resolved (autonomy: auto, no residue) — recorded as the accountable run; the freeze itself carried an EXPLICIT human approval (the AskUserQuestion direction call)

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved on evidence — autonomy: auto, no residue · freeze human-approved (Tin Dang, AskUserQuestion direction call) · date: 2026-06-06
Note: ordinary doc-transform scope (applies the already-frozen xml-convention §3; vocab = {prompt}, no new
tag). The substantive risk — a vocab-clean but render-broken page — was advisor-caught before a line was
written, fixed by the wrap-intact-fence layout, and is now guarded structurally (`test_appendix_render_safe`)
AND was manually render-verified. Evidence-auto-gate: 474 tests green, no test weakened, no contract touched,
3 tracked copies md5-identical, templates assessed (nothing to tag), no security/concurrency/architecture
residue. Resolved under Tin Dang's standing authorization for the autonomous v16 run.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `test_appendix_render_safe` — the render-safety proxy. A future edit
that removes a fence or leaks a placeholder outside one trips it before the broken page ships.
Spec delta for the next loop: the v16 convention is now applied across the WHOLE prompt surface — the skill
files (tasks 1–3) AND the published prompt library (this task). Two audiences, one tag: skill/ files carry a
BARE `<prompt>` (consumed as text — rendering irrelevant), while appendix-b wraps an INTACT fence (a rendered
page — the fence must survive). Same `<prompt>` vocabulary, layout chosen by audience. Templates needed no
convention (forms, not prompts) — the WIDEST scope's two tail targets resolved to convert-one, assess-the-other.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] applying a markup convention to a RENDERED doc differs from a CONSUMED one: appendix-b is a
  published page, so the `<prompt>` tag must wrap the INTACT code fence (blank lines load-bearing) — removing
  the fence renders the body as live markdown and silently swallows `<…>` placeholders. Audience determines
  layout, not just whether-to-tag. (evidence: advisor caught the page-mangle before build; manual render check + test_appendix_render_safe.)
- [TDD · folded] a vocab/structure test is BLIND to rendering: "tags are valid" ≠ "the page renders". Guard the
  render failure structurally — assert no `<lowercase>` placeholder and no ≥4-space-indent line survives a
  fence-strip OUTSIDE a fence (the proxy for "fences were wrapped, not removed"). (evidence: test_appendix_render_safe; the vocab test alone would have passed a broken page.)
- [ADD · folded] a verbatim-reproduction doc transform should be done by a verifying SCRIPT, not hand-editing:
  the wrap transform asserted fence bodies byte-identical + tag/fence counts + no leak BEFORE writing, making
  "verbatim" provable rather than trusted. (evidence: tmp/wrap_appendix_b.py post-conditions; bodies md5-identical.)
