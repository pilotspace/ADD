════════════════════════════════════════════════════════════════════════
 udd-design-foundation · Udd Design Foundation
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  a UI project gets a render-ready UDD foundation the AI drafts
       from and into — DESIGN.md plus a JSON foundation (token layers +
       component catalog + prototype content trees) that a
       json-render-style renderer displays as a living design system and
       clickable prototype, and that add.py check lints

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 udd-token-schema            done      PASS 14†   ●●●●●●●●●
 udd-catalog-content-schema  done      PASS 19†   ●●●●●●●●●
 udd-design-template         done      PASS 13†   ●●●●●●●●●
 udd-check-lint              done      PASS 18†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (16 carried)
   • TDD · open · the verify-gate adversarial refute earns its keep on a
     TRAVERSAL validator — 10 behavior scenarios all passed yet missed a
     fail-OPEN gap (a `$value` node with non-`$` children skipped its
     whole subtree, so malformed nested tokens passed silently); a
     recursive validator's red suite needs a "never skip a subtree / no
     phantom children" probe FROM GROUND, not discovered at verify
     (evidence: the python-expert refute reproduced it on a nested
     malformed child; closed via reopen→tests→build→verify re-cross;
     `test_nested_token_children_are_validated` + `_index`/`_walk` now
     always descend; md5 8329cd4→c107344)
   • SDD · open · "a token = object with `$value`; a group = object
     without `$value`" left token LEAF-ness IMPLIED, not stated — the
     gap existed precisely because the frozen §1 never said "a token is
     a leaf (no child tokens)"; future schema tasks (catalog/tree)
     should state structural leaf/containment rules explicitly so the
     validator isn't the only place the invariant lives (evidence: the
     fail-open gap was an under-specified structural case, resolved by
     the fail-closed principle at verify, not by a frozen rule)
   • UDD · open · the compact dialect's value-form STRICTNESS is
     under-pinned in three spots the frozen contract did not nail:
     `fontWeight` accepts ANY string as a "keyword" (no enumerated set),
     weight FLOATS like `700.0` are rejected, and NEGATIVE dimensions
     like `"-16px"` pass — all defensible for MVP but a real renderer
     would reject some; tighten in a follow-up if real token files hit
     them (evidence: refute WEAKNESSES 1-3, classified non-blocking;
     deferred rather than change-requested against the frozen v1)
   • TDD · open · a traversal/validator task needs a TOTAL-FUNCTION
     (never-raises) probe + a wrong-JSON-type probe from ground — the 13
     scenarios all used well-formed dicts, so the adversarial refute,
     not the suite, caught the crash (evidence: refute Finding 1 —
     non-object component + children → AttributeError).
   • SDD · open · freeze-time check: every Reject must be SATISFIABLE by
     the frozen signature — non_semantic_ prop_token's $type-match
     needed tokens.json the `(catalog, tree)` signature never receives
     (evidence: v2 change-request raised while writing the red test for
     that scenario).
   • SDD · open · "lint shape only" left tree-element STRUCTURE (props
     is an object, children is an array) implied, not stated — the 9th
     code malformed_element had to be added at verify (evidence: v3
     refute Finding 2 — props:[…]/children:"x" silently passed).
   • UDD · open · identity VALUES are human-owned — surface design
     tokens (brand color, palette, type) at specify, never auto-pick
     from a menu (evidence: the "add branding color token" request → the
     identity-values guideline, committed 560442a; udd-tokens.md +
     phases/1-specify.md).
   • ADD · open · a same-task verify re-cross updates ENGINE_MD5
     (774e025 → 3cdfaab) WITHOUT changing the `re-aimed @ <slug>`
     annotation — the slug names the TASK, the md5 names the build
     (evidence: v3 re-pin).
   • UDD · open · DESIGN.md is the prose FRONT-DOOR that binds the
     named-set JSON (tokens·catalog·prototypes) the AI drafts UI from;
     design identity stays human-owned — the doc PROMPTS for
     brand/palette/type, never pre-fills (evidence: the shipped
     DESIGN.md.tmpl identity section is HTML-comment prompts + the
     identity_prefilled guard, both halves).
   • UDD · open · the human added a SCREENS section at the freeze
     ("Freeze + Screens section") — DESIGN.md doubles as the per-screen
     prototypes/<name>.json index, a shape worth defaulting into the
     template (evidence: the v1 §3 amendment).
   • TDD · open · string-PRESENCE asserts under-enforce a
     STRUCTURED-PROSE contract — `assertIn(anchor)` misses order, table
     form, and the OR-half of identity_prefilled (a non-hex literal); a
     prose contract needs STRUCTURE asserts (evidence: the verify refute
     found 4 such gaps a presence check passed; the 4 strengthened
     asserts each catch their counterexample).
   • ADD · open · strengthening a test at VERIFY (close-gap-before-gate)
     trips build_tampered — the honest path is reopen → tests →
     re-advance (re-snapshot), NEVER force the gate past the tripwire
     (evidence: build_tampered fired on the first `gate PASS` attempt;
     cleared by `phase tests` + re-advance, not by overriding — the §3
     contract stayed untouched).
   • TDD · open · a COMPOSING validator needs first-class
     "no-double-flag" boundary tests — proof that a sibling validator's
     codes are NOT re-emitted — not just per-code happy/sad tests
     (evidence: the build green missed 3 double-flag shapes; the verify
     refute caught them; +2 red boundary tests now guard them).
   • SDD · open · cross-check every §1 Reject code against a §4 test
     line at the contract freeze — an asymmetry here shipped 2 untested
     Reject codes (malformed_catalog_json · malformed_prototype_json)
     past a green build (evidence: refute #3/#4; +2 fail-closed tests
     closed them).
   • UDD · open · DTCG $type-inheritance means a resolved token's
     effective $type can be malformed/absent at the GROUP — a cross-file
     resolver must treat "resolved $type ∉ the valid set" as the
     UPSTREAM (task-1 unknown_type) validator's concern, never its own
     mismatch (evidence: the `got ∉ _TOKEN_TYPES` skip-guard).
   • ADD · open · the verify-gate adversarial refute surfaces
     contract-faithfulness gaps even when the build is green AND honest
     (no cheat) — close-gap-before-gate caught 5 here that the build's
     own green missed (evidence: 1 manual + 4 refute findings, all
     closed via an honest re-baseline through `phase tests`, never by
     forcing the gate).

 DECIDE NEXT  consolidate learnings + archive-milestone
              udd-design-foundation
════════════════════════════════════════════════════════════════════════