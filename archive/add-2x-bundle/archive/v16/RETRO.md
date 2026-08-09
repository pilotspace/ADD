════════════════════════════════════════════════════════════════════════
 v16 · xml-prompt-structure
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  0/5 met
 GATES     5 PASS             WAIVERS   none

 goal  XML-structure the agent-executable add-method prompt surface
       (Rule 5 idiom) without bloating lean prompts

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 xml-convention              done      PASS 17†   ●●●●●●●●
 phase-guides-xml            done      PASS 17†   ●●●●●●●●
 engine-docs-xml             done      PASS 17†   ●●●●●●●●
 appendix-templates-xml      done      PASS 17†   ●●●●●●●●
 mirror-greenstate           done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ○○○○○○○○○○ 0/5 met

 LEARNINGS (15 carried)
   • SDD · folded · a CLOSED notation needs a disambiguation rule when
     it collides with notation already in the prose — the convention
     tags `<x>…</x>` collided with existing `<name>`/`<why>`/`<cost>`
     prose placeholders; resolved by the PAIRED-tag rule (a convention
     tag is the intersection of open∩close). (evidence:
     test_vocab_in_set first flagged 3 placeholders before the rule was
     added.)
   • ADD · folded · tests-green ≠ faithful conversion: a content-shape
     guard cannot see over-tagging the spec never enumerated, so for
     non-uniform engine docs the sole-reviewer risk is real — the
     per-file narrative list must GROW with each task or the
     over-tagging guard is hollow. (evidence: advisor flagged this as
     the live risk for autonomous tasks 3–4.)
   • UDD · folded · a prompt file is dual-audience (agent + human);
     over-tagging hurts the human reader, so leanness is a UX
     constraint, not only a style one — the vocabulary was driven from a
     field-level scheme down to 5 block-level tags to keep the prose
     readable. (evidence: the chosen block-level core.)
   • TDD · folded · RED-before-build holds even for a doc refactor with
     no runtime: the guard was authored failing (pilot unconverted) then
     made green by the doc edit alone, no test weakened. (evidence:
     test_xml_convention RED→GREEN, suite 461/0, no existing test
     touched.)
   • SDD · folded · a per-file narrative-enumeration table is the only
     thing that makes an over-tagging guard real: without it a content
     test sees "tags present" but is blind to tags on prose. (evidence:
     test_phase_narrative_untagged enumerates each guide's narrative
     sections; the RED run had 0 tags so it trivially passed — the guard
     only bit once conversion added tags, exactly where the table
     pointed.)
   • TDD · folded · RED-before-build held across 7 files at once: 5 new
     tests authored failing (no blocks yet) → made green by the doc
     edits alone, no test weakened, suite 461→466. (evidence: the staged
     RED run showed 4 failures for the right reason.)
   • ADD · folded · applying a frozen contract is genuinely lower-risk
     than authoring it: task 1 was risk:high+conservative (defining the
     convention); task 2 is autonomy:auto (applying it), and the
     evidence-auto-gate resolved cleanly with no residue. The dial
     tracked the actual risk gradient. (evidence: this gate
     auto-resolved; task 1's did not.)
   • ADD · folded · the convention's fence-exemption clause is
     load-bearing, not decorative: every engine-doc output-shape is a
     code fence, so a "wrap output shapes in `<output_format>`" reading
     would have tagged fences and broken the leanness rule. Reading it
     as "fences are self-marking — never wrap them" kept the engine docs
     to exactly the 2 tags the first-use map reserved. (evidence:
     advisor-verified Position A this session; test_engine_vocab_subset
     strips fences then asserts ⊆ {constraints, reject_codes}.)
   • TDD · folded · a content guard needs BOTH its positive and negative
     half asserted: the worker-contract guard asserts the 7 tags are
     PRESENT in raw streams.md AND ABSENT after fence-strip —
     present-only would miss a fence deletion, absent-only would miss
     tags leaking outside the fence. (evidence:
     test_engine_worker_contract_preserved.)
   • TDD · folded · a freshly-authored assertion can fail for the WRONG
     reason and look like correct RED: the tags-present test used
     `assertRegex` (`re.search`, no DOTALL) against multi-line blocks,
     so it failed even on correctly-converted docs. RED must be triaged
     — "doc not converted" vs "assertion can't express its intent".
     (evidence: the first post-build run still failed tags-present until
     the DOTALL fix; the other 3 passed.)
   • ADD · folded · applying a markup convention to a RENDERED doc
     differs from a CONSUMED one: appendix-b is a published page, so the
     `<prompt>` tag must wrap the INTACT code fence (blank lines
     load-bearing) — removing the fence renders the body as live
     markdown and silently swallows `<…>` placeholders. Audience
     determines layout, not just whether-to-tag. (evidence: advisor
     caught the page-mangle before build; manual render check +
     test_appendix_render_safe.)
   • TDD · folded · a vocab/structure test is BLIND to rendering: "tags
     are valid" ≠ "the page renders". Guard the render failure
     structurally — assert no `<lowercase>` placeholder and no
     ≥4-space-indent line survives a fence-strip OUTSIDE a fence (the
     proxy for "fences were wrapped, not removed"). (evidence:
     test_appendix_render_safe; the vocab test alone would have passed a
     broken page.)
   • ADD · folded · a verbatim-reproduction doc transform should be done
     by a verifying SCRIPT, not hand-editing: the wrap transform
     asserted fence bodies byte-identical + tag/fence counts + no leak
     BEFORE writing, making "verbatim" provable rather than trusted.
     (evidence: tmp/wrap_appendix_b.py post-conditions; bodies
     md5-identical.)
   • TDD · folded · a multi-file convention needs a CENSUS guard, not
     just per-file subset checks: counting that all N expected tags
     appear (whole) AND no unexpected tag appears (closed) across the
     surface catches a tag that drifted off-vocabulary in a file the
     per-file table forgot to enumerate. (evidence: the 5-tag census
     this sweep; per-file tests only assert each listed file.)
   • ADD · folded · a milestone with several conversion tasks benefits
     from a dedicated green-state SWEEP task whose only job is to run
     the union of guards at once — per-task greens can each pass while a
     cross-file interaction is red. (evidence: this task; the
     composition was green, but it is the only run that proves it.)

 DECIDE NEXT  fold learnings + archive-milestone v16
════════════════════════════════════════════════════════════════════════