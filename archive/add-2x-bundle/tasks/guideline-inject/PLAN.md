# TASK: Dynamic-by-reference guideline injection into AGENTS.md/CLAUDE.md

slug: guideline-inject · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Give any agent (Claude Code, or an AGENTS.md-aware tool) a stable pointer INTO the
ADD runtime, WITHOUT embedding live state in the guideline file. Anti-context-rot:
auto-updated context files measurably hurt (ETH-Zurich: ~3% lower success, 20%+ more
cost). Realizes Q7.

Must:
  - `sync-guidelines` writes one ADD "managed block" into BOTH `AGENTS.md` and
    `CLAUDE.md` at the PROJECT ROOT (not inside `.add/`).
  - The block is DYNAMIC-BY-REFERENCE: it tells the agent to run `add.py status` and
    read `.add/PROJECT.md` first. It MUST NOT embed live state (no task slug, phase,
    gate, or milestone names).
  - The block is delimited by VERSION-STABLE HTML markers so a re-run updates only the
    region between markers and never duplicates the block.
  - Idempotent: when the on-disk block already equals the desired block, do nothing —
    no write, no `.bak` (byte-identity no-op).
  - Backup-before-mutate: when an EXISTING file's content changes, write `<file>.bak`
    with the original before replacing (rollback path; design-for-failure).
  - Writes are atomic (`_atomic_write`); user content OUTSIDE the markers is preserved.
  - Symlink-dedup: if AGENTS.md and CLAUDE.md resolve to the same real path
    (`os.path.realpath`), inject once — and write the REAL file, never replace a symlink.
  - `init` runs the same injection automatically (zero-config) on the new project root.
Reject / fail-soft:
  - A target that cannot be written (permission/OS error) -> warn on stderr and SKIP
    that file; never crash `init` or abort the other target. (No new exit code.)
After:
  - AGENTS.md and CLAUDE.md each contain exactly one ADD block between the markers;
    re-running is a no-op; a pre-existing file keeps its other content + gains a `.bak`.
Assumptions (confirm before building):
  - [x] target BOTH AGENTS.md + CLAUDE.md at project root — user Q7 ("claude.md AND agents.md")
  - [x] create the file if absent (a new file gets the block as content, no `.bak`)
  - [x] dynamic-by-reference, never live state — user-picked (anti-context-rot)
  - [x] `npx @mrq/add sync-guidelines` wrapper deferred; core is `add.py sync-guidelines`

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: create the block in a fresh project
  Given a project with no AGENTS.md and no CLAUDE.md
  When I run sync-guidelines
  Then AGENTS.md and CLAUDE.md exist
  And each contains the ADD begin/end markers and the text "add.py status"

Scenario: idempotent re-run is a no-op
  Given sync-guidelines has already run once
  When I run it again
  Then both files are byte-identical to after the first run
  And no `.bak` file was created (nothing changed)

Scenario: preserve user content, overwrite only inside the markers
  Given an AGENTS.md with user text and a hand-tampered ADD block body
  When I run sync-guidelines
  Then the user text outside the markers is unchanged
  And the block body is restored to the canonical text

Scenario: backup before changing an existing file
  Given an AGENTS.md that has user text but no ADD block
  When I run sync-guidelines
  Then AGENTS.md.bak holds the original content (no block)
  And AGENTS.md now contains the user text AND the ADD block

Scenario: dynamic-by-reference — no live state leaks in
  Given an active task with a known slug
  When I run sync-guidelines
  Then the block contains "add.py status" and "PROJECT.md"
  And the block does NOT contain the active task slug

Scenario: symlink targets are de-duplicated
  Given CLAUDE.md is a symlink to AGENTS.md
  When I run sync-guidelines
  Then the single underlying file contains exactly one ADD begin marker

Scenario: init injects automatically
  Given a fresh directory
  When I run `add.py init`
  Then AGENTS.md and CLAUDE.md contain the ADD block

Scenario: an unwritable target is skipped, not fatal
  Given writing AGENTS.md raises an OS error
  When I run sync-guidelines
  Then the command does not crash
  And CLAUDE.md still receives the block
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
markers (module constants — NEVER change the strings, or old blocks orphan):
  _GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
  _GUIDE_END   = "<!-- ADD:END -->"

block body (dynamic-by-reference, NO live state): a short "how to work in this repo"
  pointing at `python3 .add/tooling/add.py status`, `.add/PROJECT.md`,
  `.add/tasks/<slug>/TASK.md` (+ phase/advance/gate), and `.add/docs/`.

targets: <project_root>/AGENTS.md and <project_root>/CLAUDE.md
  - present  -> replace region [BEGIN..END] if markers present, else append block
  - absent   -> create file with the block as content (no `.bak`)
  - realpath-dedup: collapse targets resolving to one inode; write the REAL file

api (functions in add.py):
  _guideline_block() -> str                       # BEGIN + body + END (no trailing \n)
  _inject_block(path: Path) -> "created"|"updated"|"unchanged"
      unchanged => no write, no `.bak`
      updated   => write `<path>.bak` (original), then atomic write
      created   => atomic write, no `.bak`
  _inject_guidelines(project_root: Path) -> list[(name, action)]
      per-target try/except OSError -> warn+skip (action "skipped")
  cmd_sync_guidelines(args)  -> prints "<action>  <file>" per target
  cmd_init(...)              -> calls _inject_guidelines(base) after save_state

cli:  add.py sync-guidelines        (new subcommand; requires a .add/ root)
pkg:  cli.js prunes ALL test_*.py (not just test_add.py) from installs
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 8 scenarios (new file add-method/tooling/test_guidelines.py).
Plan (one test per scenario, asserting BEHAVIOR — markers/content, not file existence alone):
  - test_sync_creates_block_fresh:        sync / both files + BEGIN+END markers + "add.py status"
  - test_sync_idempotent_no_bak:          sync x2 / BOTH halves: content byte-identical AND no `.bak`
  - test_preserve_outside_restore_inside: seed user text + tampered body / sync / kept + restored
  - test_backup_on_change:                seed user text no block / sync / `.bak` == original (no block)
  - test_block_no_live_state:             new-task slug / sync / slug NOT in block, "PROJECT.md" present
  - test_symlink_targets_dedup:           CLAUDE.md -> symlink AGENTS.md / sync / exactly one BEGIN marker
  - test_init_auto_syncs:                 init / BOTH files contain the BEGIN marker (not just exist)
  - test_unwritable_target_skips:         monkeypatch _atomic_write to raise for AGENTS.md / no crash + CLAUDE.md done

Tests live in: `add-method/tooling/test_guidelines.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): NEVER write a `.bak` or mutate a file on a no-op;
ALWAYS `.bak` before changing existing content; per-target failure is isolated
(warn+skip) so one bad target never aborts the run or `init`; resolve symlinks to the
real file before writing.
Code lives in: `add-method/tooling/add.py` (+ a carried-along packaging fix in
`add-method/bin/cli.js` so test_*.py never ships into installs). Constraints: stdlib
only; do NOT change tests/contract; keep `.add/tooling/add.py` byte-identical to source.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 46/46 green (`python3 -m unittest discover`); 10 new (8 + 2 from review)
- [x] coverage did not decrease — tests only ADDED, none removed or weakened
- [x] no test or contract was altered during build — contract FROZEN @ v1; review fixes added tests
- [x] concurrency / timing safe — `_atomic_write` (temp + os.replace); single-process CLI; no shared mutable state
- [x] no exposed secrets / injection / unexpected deps — stdlib only; block is 100% static text
      (no user input interpolated); markers are inert HTML comments
- [x] layering & deps follow CONVENTIONS.md — add.py stays flat stdlib; cli.js change is packaging-only
- [x] a person reviewed — adversarial python-expert review (verdict SHIP-WITH-FIXES); HIGH
      (UnicodeDecodeError escaping `except OSError` → crash on non-UTF-8 file) FIXED + tested;
      MEDIUM (begin-without-end silent edit) FIXED + tested; 2 LOW deferred to OBSERVE w/ rationale.
      Final author/PR sign-off requested from the user.

### GATE RECORD
Outcome: PASS
Reviewed by: adversarial subagent (python-expert) + executing agent · date: 2026-05-29
Human author (Tin) sign-off: PENDING (asked at PR/commit time)
Evidence: 46/46 tests green · dogfooded on this repo (created AGENTS.md + CLAUDE.md, re-run unchanged,
no .bak, no live slug leaked) · review HIGH+MEDIUM findings closed with tests.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do agents actually run `status` from the block?
do users complain about a second near-identical CLAUDE.md/AGENTS.md? `.bak` clutter?
Spec delta for the next loop: match markers on a stable token (`ADD:BEGIN`) instead of
the full string so the human-readable marker text can be reworded without orphaning old
blocks; an `npx @mrq/add sync-guidelines` convenience wrapper; a `--check` (dry-run) mode.
Deferred review findings (both LOW, both touch the SHARED `_atomic_write` primitive used by
every command — out of scope for this task, fix as a separate IO-hardening task to bound blast
radius): (1) `read_text`/`_atomic_write` normalize CRLF→LF, so a Windows-CRLF AGENTS.md is
silently denormalized on first inject (no content loss); (2) `mkstemp` makes the temp 0600, so
`os.replace` drops the original file's mode to owner-only — preserve the source mode before replace.
