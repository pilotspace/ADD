---
type: Milestone
title: The read costs what it is worth: a dereferenceable address, a bounded listing, and the trims underneath
status: done
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
---
## CARD
goal: an address a verb prints is an address a verb can read back, the carried inventory is windowed the way search already windows it, and the measured trims underneath are taken.
why: measured, not assumed. `add deltas` emits 26,162 bytes — about 90% of a task-intake session — and 51 of its 66 lines exceed the 300-character bound `add search` is HELD TO BY TEST, the longest at 830. The two verbs render the same records at 409 and 169 bytes each. But the listing cannot be windowed first: `add show /specs/method.md#M33` refuses and `add search M33` finds nothing, so today the only way to read one lesson in full is a 12,762-byte whole-spec read. The address every verb tells you to cite is not an address any verb can resolve. Underneath that, a full dead-code sweep of a 5,900-line engine found ~101 removable lines — 1.75% — which settles the shape of this work: the accumulated cost is in what one verb PRINTS, not in what the engine weighs.
next: add freeze read-cost

## SCOPE
In:  `#id` resolution in `show` and delta-head indexing in `search` · windowing `deltas` at the existing constant · `brief`'s false read-only claim · the measured `status`, `locate` and `brief` output trims · the ~101 dead and duplicated source lines.
Out: the 26-verb surface, the refusal grammar, law 1, law 3, the two-oracle split — none of them is negotiable. `show` on a whole spec is NOT windowed: it is the only full-text escape hatch, and its contract is to read one node whole.

## GROUND
touches: add-method/tooling/add.py and its three twins · add-method/tooling/cli.py and its three twins · add-method/FORMAT.md · add-method/tests
risks:
  - ORDER IS LOad-BEARING. Windowing the listing before the address resolves would strand full delta text behind a 12.7 KB read — a cut that makes the tool worse. Address first, window second, and the milestone fails if that order slips.
  - every trim removes something a reader might have relied on. Each one has to name what is lost and why that is acceptable, or it is not a trim, it is a regression.
  - `deltas` renders the inventory the planning loop reads. Over-window it and the loop plans from truncated lessons — the failure is silent and shows up as worse plans, not as a red check.
  - the engine has four byte-identical twins, so every source line removed is removed four times and both pins re-aim.

## EXIT
- [x] an address `deltas` and `search` print resolves: `show` reads a `#id` fragment, and `search` finds a delta by its own id   (address-dereferences)
      evidence: `show /specs/method.md#M33` renders the lesson (604 B) and `search M33` finds it by id; 9 checks, receipt 1
- [x] `deltas` is windowed at the constant `search` already uses, no line exceeds the bound `search` is tested against, and the malformed report is untouched   (bounded-delta-listing)
      evidence: windowed at SEARCH_SNIPPET; longest line 830 B -> under the 300-char bound; the malformed report untouched; 8 checks
- [x] `brief`'s read-only claim is either made true or corrected everywhere it is stated   (brief-is-not-read-only)
      evidence: the FUNCTION is pure, the VERB stamps — corrected in the docstring, the reference and the skill; 6 checks
- [x] `status`, `locate` and `brief` stop emitting what a reader cannot act on, each cut naming what is lost   (output-trims)
      evidence: status -49% · locate -97% · brief -3%, each collapse naming `--all`; 9 checks, 8 injections caught, receipt 3
- [x] the measured dead and duplicated source lines are gone from all four twins, with both pins re-aimed   (source-dead-code)
      evidence: RESERVED_FILES + delta_carried_on gone from all four twins, both pins re-aimed; 6 checks, 7 injections caught, receipt 1
- [x] a task-intake session is measured before and after, and the reduction is reported as data rather than claimed   (bounded-delta-listing)
      evidence: orient + locate + deltas + brief on the live 258-node bundle, measured against 904ee348:
      40,812 B -> 17,841 B (-56%) · status 615->315 · locate 3,723->106 · deltas 27,304->8,480 · brief 9,170->8,940

## CLOSE
evidence: one row per task
