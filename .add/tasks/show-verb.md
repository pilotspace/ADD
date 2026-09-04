---
type: Task
title: add show reads one node whole, with its neighbourhood to three levels
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
depends_on:
  - /tasks/graph-neighborhood.md
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/README.md
  - README.md
  - add-method/docs/13-command-reference.md
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/engine
  - add-method/tests/skill
gives:
  - S1 add.resolve_ref(root, ref) — a bare slug or a cid to EXACTLY one cid; (cid, note) with cid None on a refusal. Zero matches refuses; several refuse and list the candidates. It never best-guesses
  - S2 add.show(root, ref, expand) — (view, note); view is None ONLY on a refusal. The view carries the node's cid, its frontmatter, its whole body, and its neighbourhood rows
  - S3 cli.py `add show REF [--expand N]` — the 26th verb, read-only; exit 0 on an answer, 1 on a refusal, and an --expand above the cap refuses rather than clamping
  - S4 the verb registries — the CLI WIRED set, the package README verb count, the CLI-surface count pin, the book command reference, and the cookbook in all three shipped skill trees
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:97b2e41549f8e8e8", binding: "sha256:bbab0c662dde5a9e" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:c510fe7e3c4db1c4" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/show-verb.d/runs/1.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/show-verb.d/runs/1.md, brief: "sha256:971f2649bc52b30b" }
---
## CARD
goal: `add show <slug>` returns a milestone or task whole — its full content and its relationships to three levels — as one bounded, read-only command.
why: nothing in the engine reads a node. `search` returns an address and a 96-character snippet; `brief` returns a phase-scoped prompt, not the node. An agent that wants a task's contract still `cat`s the file: outside the engine, unbounded, and with no relationships attached. `neighborhood()` now exists and has no caller, and `NEIGHBORHOOD_MAX` ships with no runtime reader — this verb is where both stop being dead surfaces.
beat: done · next: add status

## RULES
<must>
- M1 `add show <ref>` prints the node's FULL content — frontmatter and whole body — never a summary, a snippet, or a phase-scoped prompt
- M2 the neighbourhood is walked to `--expand` levels and defaults to 3 when the flag is absent
- M3 an `--expand` above `NEIGHBORHOOD_MAX` REFUSES and names the cap in the refusal; it never clamps to the cap and reports success
- M4 a ref that does not resolve to exactly one node refuses; several matches list the candidates and none is chosen
- M5 the verb is read-only — it writes nothing anywhere in the bundle, records no stamp, and leaves every file byte-identical
- M6 every registry that enumerates the verb set names `show`, and the CLI-surface count pin moves 25 to 26 in the same change
</must>
<reject>
- R:CLAMP an over-cap `--expand` must never be silently reduced to the cap — a clamp that reports success answers a question nobody asked -> "CLAMP"
- R:FALLBACK an unresolvable ref must never degrade into a substring search; a read that silently becomes a search answers a different question and reads as success -> "FALLBACK"
- R:GUESS a ref matching several nodes must refuse and list them, never pick one — `cli._resolve` best-guesses `/tasks/<ref>.md` today and that shape must not reach the new verb -> "GUESS"
- R:PHANTOM the verb must not be advertised anywhere it is not wired, nor wired without being advertised -> "PHANTOM"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 S4 · n/a · every surface here is read-only: no stamp, no verdict, no path to `done`, no authority floor consulted. There is no actor whose rights change, which is why this task's sensitivity is architecture and not security
- A2 [which] covers: S1 · the request does not say which nodes a bare slug may name; taking EVERY node type, not just Tasks — a milestone is the headline case in the request itself, and `cli._resolve`'s Task-shaped guess is the bug being removed · probe: `add show okf-graph-lookup` resolves a Milestone with no type hint -> if wrong, the verb reads tasks and refuses everything else
- A3 [which] covers: S2 · the request does not say which parts of a node count as content; taking frontmatter AND the whole body, because a task's contract lives in its body sections and a reader that got frontmatter alone would still have to open the file -> if wrong, the verb saves no `cat` and the whole task is decorative
- A4 [which] covers: S3 S4 · the request does not say which registries must learn a new verb; taking the set found by RUNNING THE SUITE rather than by grepping, because a verb-count pin names no verb and is invisible to any textual search (S5) · found: five sites — the WIRED set, the package README count, the CLI-surface count pin, the book command reference, and the cookbook in three skill trees -> if wrong, the verb ships advertised-but-unwired or wired-but-unadvertised and a phantom-verb fixture reds
- A5 [when] covers: S2 S3 · the request does not say where the depth boundary falls; taking `expand` as the DEEPEST level emitted so `--expand 1` is immediate neighbours, and the cap as INCLUSIVE so `--expand 5` succeeds and 6 refuses -> if wrong, every caller is off by one and the cap refuses a legal depth
- A6 [when] covers: S1 · the request does not say when a ref is a cid rather than a slug; taking the structural test `"/" in ref or ref.endswith(".md")`, the same one `cli._resolve` already uses, so the dispatch point is inherited and not invented -> if wrong, a slug containing a dot is read as a path
- A7 [when] covers: S4 · n/a · a registry entry has no runtime boundary; it either names the verb or does not
- A8 [absent] covers: S1 · the request does not say what an empty or missing ref means; taking a refusal — argparse requires the positional, and an empty string names no node -> if wrong, `add show` with no argument prints the whole bundle
- A9 [absent] covers: S2 · the request does not say what an absent neighbourhood means; taking the DISTINCTION `neighborhood()` already draws — a node with no edges shows its content and an empty relations block, and only an unresolvable ref refuses · found: `neighborhood()` returns `[]` for a real node and `None` only for a missing one -> if wrong, a lonely node reads as a missing one
- A10 [absent] covers: S3 S4 · the request does not say what an absent `--expand` means; taking `NEIGHBORHOOD_DEFAULT` (3), the value the primitive already documents, so the flag's default and the primitive's default are one number -> if wrong, the CLI and the engine disagree about the default walk
- A11 [order] covers: S2 S3 · the request does not say what orders the printed rows; taking `neighborhood()`'s total order unchanged and grouping the display by depth, so the output is diffable and the reader sees levels rather than a flat list -> if wrong, output churns between runs and no reader can diff two shows
- A12 [order] covers: S1 S4 · n/a · a single resolved cid has no ordering, and a registry is a set membership question rather than a sequence — except the candidate list on a `R:GUESS` refusal, which is sorted and is covered by A11's rule
- A13 [experience] covers: S2 S3 · the receiver is an agent spending context; what would make this hard is unbounded output, so the neighbourhood is capped and the node's own body is printed once rather than re-rendered per row -> if wrong, one `show` costs more context than the `cat` it replaces and nobody uses it
- A14 [experience] covers: S1 · the receiver is a human typing a slug from memory; what would make it hard is a refusal that does not say what IS available, so a zero-match refusal names the nearest verb (`add status`) and a many-match refusal lists the candidates -> if wrong, the refusal is a dead end
- A15 [experience] covers: S4 · the reader is the next author adding a verb; taking a cookbook line that shows the DEFAULT invocation rather than every flag, so the always-loaded budget pays for the common case -> if wrong, the SKILL byte pin is bumped to fund a flag nobody types

## PLAN
contract: `resolve_ref(root, ref)` returns `(cid, note)`; `cid is None` on a refusal. A ref carrying `/` or ending `.md` is taken as a cid and checked for existence; otherwise it is a slug matched against every node's basename. `show(root, ref, expand=NEIGHBORHOOD_DEFAULT)` returns `(view, note)`; `view is None` only when `resolve_ref` refused or `expand` exceeds `NEIGHBORHOOD_MAX`. The view is a dict carrying `cid`, `fm`, `body` and `rows`. `cli.py` adds the `show` subcommand with `ref`, `--expand`, prints the note, and exits 1 on a None view.
strategy: write the checks first including the over-cap refusal and the no-fallback case, land `resolve_ref` and `show`, wire the CLI, then run the FULL suite to find the registries — never a grep census.

## EDGES
- E1 a bare slug naming a Milestone resolves, with no type hint given
- E2 a full cid resolves to itself
- E3 a slug naming nothing refuses, and the refusal names a runnable next verb
- E4 a ref matching more than one node refuses and lists every candidate
- E5 `--expand 0` prints the node with an empty neighbourhood, and is an answer rather than a refusal
- E6 `--expand NEIGHBORHOOD_MAX` succeeds and `NEIGHBORHOOD_MAX + 1` refuses
- E7 a non-integer `--expand` is an argparse usage error (exit 2), not an engine refusal

## CHECKS
- test_show_prints_the_whole_body · covers: M1, A3 · every `## ` section heading of the node appears in the view's body
- test_show_walks_to_the_default_depth · covers: M2, A10 · with no flag the deepest row is 3, and the default equals `NEIGHBORHOOD_DEFAULT`
- test_over_cap_expand_refuses_and_names_the_cap · covers: M3, R:CLAMP, E6 · `NEIGHBORHOOD_MAX + 1` returns view None and a note naming the cap; the cap itself succeeds
- test_unresolvable_ref_refuses_without_searching · covers: M4, R:FALLBACK, E3 · a ref matching no node returns None and a note that is not a hit list
- test_ambiguous_ref_lists_candidates · covers: M4, R:GUESS, E4 · a ref matching two nodes returns None and names both
- test_slug_resolves_for_any_node_type · covers: A2, E1, E2 · a Milestone slug and a full cid both resolve; the probe A2 declares
- test_show_writes_nothing · covers: M5 · every file in the bundle is byte-identical before and after, and no receipt or stamp is added
- test_expand_zero_shows_the_node · covers: E5, A9 · the view exists with empty rows; a lonely node is not a missing one
- test_show_is_wired_and_advertised · covers: M6, R:PHANTOM · the CLI's advertised verb set equals the WIRED set and both contain `show`
- test_every_registry_learned_the_show_verb · covers: M6, A4 · the package README count, the CLI-surface count pin, the book command reference, and all three skill cookbooks name the verb
- test_non_integer_expand_is_a_usage_error · covers: E7 · argparse exits 2 rather than the engine refusing
- test_show_refusal_names_a_runnable_next · covers: A14 · every refusal note ends in a `next:` line naming a real verb
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
