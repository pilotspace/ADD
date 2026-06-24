════════════════════════════════════════════════════════════════════════
 docs-site · Docs site — ship the AIDD book to GitHub Pages
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  4/4 met
 GATES     2 PASS             WAIVERS   none

 goal  a reader can browse and search the full AIDD book at a public
       GitHub Pages URL, built with MkDocs Material from the canonical
       add-method/docs/ and deployed automatically by CI
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 site-scaffold               done      PASS 7     ●●●●●●●●●
 pages-deploy                done      PASS 7     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   site-scaffold            PASS Tin Dang <tindang.ht97@gmail.com>
   pages-deploy             PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (6 carried)
   • ADD · open · repo-root files in §5 Scope MUST use the
     `add-method/../<file>` climb — a bare token (`mkdocs.yml`) resolves
     to the TASK dir, not project root, tripping a false
     `scope_violation` at the gate; re-cross tests→build to re-anchor
     after fixing the declaration (evidence: gate returned-to-build
     attempt 1/3, healed by re-declaring + re-snapshot — reaffirms the
     close-book-align convention).
   • UDD · open · keeping the site home OUT of the book
     (README→index.html via MkDocs default) is the lean choice for a
     book whose source is mirror-guarded — it adds zero new file, zero
     bundle/parity work, and the existing README already carries an
     intro + linked TOC that makes a good landing (evidence: human chose
     it over a new index.md; strict build confirmed README is the site
     root).
   • TDD · open · a docs/config task with no Python src is still
     red/green-testable by asserting the declarative config shape +
     running the REAL `mkdocs build --strict` in a tmp dir
     (skip-with-reason if the tool is absent) — the strict build is the
     behavior seam, not a mock (evidence: 7 stdlib-unittest tests, RED
     before config existed → GREEN after).
   • ADD · open · a deploy task whose final step is inherently
     human-and-remote (enable Pages, merge, live publish) is honestly
     verified by asserting the ARTIFACT shape (workflow YAML keys + a
     real local strict build) + DISCLOSING the un-local-verifiable
     deploy in the freeze flag — not by faking a green; the residual
     ship-step belongs to the human (release-altitude's "engine records,
     human ships") (evidence: gate PASS auto-resolved with the
     live-deploy residual surfaced, not hidden).
   • SDD · open · YAML 1.1 parses a bare `on:` key as the boolean True —
     a workflow-shape test must read `cfg.get("on", cfg.get(True))` or
     it silently asserts against a missing key (evidence: the trigger
     test needed the True-key fallback to see the `on:` block).
   • TDD · open · for a deploy task, the invariant guards (versions
     unchanged · book/bundle clean) are GREEN at red-time by design —
     they assert preservation; only the artifact-shape tests are red
     pre-build, and that mix is honest red (evidence: 4 behavior tests
     red + 3 invariant tests green before build → all 7 green after).

 SPEC DELTAS    43 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone docs-site
════════════════════════════════════════════════════════════════════════