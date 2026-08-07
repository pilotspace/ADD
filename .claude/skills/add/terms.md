# Terms — ADD / ABF-1 vocabulary (decode, don't guess)

The loop in `SKILL.md` uses a few coined terms. This is their plain-language key — load it once if a
phrase reads opaque; it names the flow, it does not add to it.

| Term | Plain meaning |
|------|---------------|
| **bundle** | the `.add/` ABF-1 state — the whole project memory. Files are the database; `graph.json` is a rebuildable cache. Resume from it (`add status`), never re-read the repo. |
| **node** | one atomic task = one node, a file at `.add/tasks/<slug>.md`. The unit the 3-beat loop drives. |
| **gives / needs** | contract edges. A task's frozen `gives:` is what it provides; `needs:` is what it depends on. The graph wires them, so a spec edit re-scopes downstream nodes with no manual edit. |
| **receipt** | a recorded, bound test result (`add run … --junitxml`). A build is trusted on its receipt — passing evidence — not on a diff that reads plausible. |
| **freeze** | the ONE approval carrying a task from direction into build — locks `## RULES · PLAN · CHECKS` (`add freeze`). A change to a frozen `gives:` is a change-request back to direction, never a silent edit. |
| **gate** | the recorded verify verdict, exactly one: `PASS` · `RISK-ACCEPTED` (signed, non-security) · `HARD-STOP` (`add gate`). |
| **residue** | the three lenses examined after build, at verify — **security · concurrency · architecture**. Security residue is always a HARD-STOP. |
| **lane** | the intake size that routes ceremony — **quick** (mechanical, no node) · **task** (one node) · **project** (a milestone). Security · data · architecture never go quick. |
| **delta** | one tagged lesson learned (`- [COMPETENCY · status] … (evidence: …)`) that folds into a living `.add/specs/` spec (`deltas.md`). |
| **wave** | a batch of independent tasks run together (parallel) under one milestone, rather than serially. |

Everything else in `SKILL.md` is plain method language; when in doubt, the phase guide that owns the
beat (`phases/direction.md · build.md · verify.md`) defines it in full.
