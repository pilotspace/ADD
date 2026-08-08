════════════════════════════════════════════════════════════════════════
 ground-context · Ground context — gather the whole working folder, efficiently
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  2/2 met
 GATES     2 PASS             WAIVERS   none

 goal  A task's ground phase gathers the full task-relevant
       working-folder context — not only code symbols but docs/textbase,
       TODOs, config/manifests, and data/fixtures — and the
       `0-ground.md` guide directs the AI to gather it efficiently
       (prefer a small-model subagent / fast index / skim for the broad
       sweep) and task-specifically (deepen on what THIS task actually
       needs, never lock a code-only shallow first pass).

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 ground-context-sources      done      PASS 13†   ●●●●●●●●●
 ground-gather-hint          done      PASS 13†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (9 carried)
   • ADD · open · the FIRST lived ground run (a task created AT
     `ground`, not retrofitted) reached `grounded ✓` — closing the "zero
     lived runs starting at ground" ceiling folded at fv25 in real time
     (evidence: ground-context-sources created at phase ground; status
     showed `grounded ✓ — §0 cites the anchors §3 names` after §0 was
     filled, never retrofitted)
   • ADD · open · dogfooded the milestone's own technique on its own
     first task — a haiku subagent did the broad working-folder sweep
     (returned the ×3/×3 sync md5s + the guard list) while the main
     context deepened on the precise guard assertions; the split (cheap
     subagent for breadth · main context for the measure invariant)
     pre-mapped the `Anchors` line before the broaden touched it
     (evidence: the Explore/haiku sweep located the guards; the build
     preserved the `Anchors the contract cites:` line, measure stayed
     `grounded ✓`)
   • SDD · open · an additive §0 template LINE (inserted between
     existing fields) is byte-invisible to the existing guard surface —
     800→810 with zero scaffold/render test broken — because the
     template tests pin tokens/structure, not exact line-sets; the
     template twin of the additive-engine-surface-byte-invisible
     convention (evidence: full suite OK after the `Context (working
     folder):` line landed; only test_ground_context asserts it;
     test_ground_phase's `## 0`/`GROUND` asserts unaffected)
   • TDD · open · a prose/template task's RED suite splits into "the
     feature is missing" (red) + "the invariants still hold" (green) —
     triaging that split confirms the red is the new behavior, not a
     broken invariant (evidence: test_ground_context RED 3/3 on the
     category+Context-line asserts, GREEN from the first run on the
     ×3/×3 parity + engine-pin invariants)
   • ADD · open · (follow-up) the guide's intro/goal line ("gather the
     REAL current codebase — files, symbols, signatures, patterns,
     conventions") under-describes the broadened gather; align the
     framing in task 2 or a follow-up — recorded, not edited (the §3
     contract scoped only the `## Gather` bullet + the §0 line)
     (evidence: 0-ground.md intro lines 3-5 unchanged this task)
   • ADD · open · Ground has TWO axes — completeness (WHAT: the
     working-folder categories) and economics (HOW: sweep broad cheaply
     via a subagent/index/skim, then deepen task-specifically); naming
     the economics stops the agent from either skipping context or
     indexing the whole repo (evidence: this milestone needed BOTH a
     WHAT task and a HOW task — task 1's categories alone left "never
     lock a shallow first pass" unsaid).
   • ADD · open · A method hint can RECOMMEND a tool action (a
     small-model subagent) while the engine stays tool-agnostic — the
     guide prose carries the recommendation, add.py spawns nothing, so
     the engine pin holds across a capability addition (evidence: add.py
     == engine_pin through both ground-context tasks; the subagent is
     the orchestrator's choice, never the engine's).
   • TDD · open · A prose-economics hint is pinnable by token-presence
     guards the same way a structural hint is — assert
     "subagent"+("index"|"skim"), "deepen", and "working folder" in the
     intro; behavior pinned, phrasing free (evidence: GatherMethodHint's
     3 tests went RED→green on the guide edits alone, no test touched at
     build).
   • ADD · open · Dogfooding the very technique being shipped validates
     it in-flight — a haiku subagent ran the broad working-folder sweep
     (returned the ×3/×3 sync md5s + guard list) while the main context
     deepened on the guard assertions, exactly the
     sweep-cheap-then-deepen split this task added to the guide
     (evidence: the build used the method it documents).

 DECIDE NEXT  consolidate learnings + archive-milestone ground-context
════════════════════════════════════════════════════════════════════════