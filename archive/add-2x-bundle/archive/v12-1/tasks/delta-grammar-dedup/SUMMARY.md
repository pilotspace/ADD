# SUMMARY: delta-grammar-dedup

task: delta-grammar-dedup
outcome: PASS-PROPOSED
branch: worktree-agent-afadb0b14daf5dbb7
worktree: /Users/tindang/workspaces/tind-repo/AIDD-Book/.claude/worktrees/agent-afadb0b14daf5dbb7

## What collapsed

`_task_prose` had a local `_delta_start = re.compile(...)` at line 1205 that
was a byte-for-byte duplicate of the module-level `_DELTA_RE` (minus the
leading `\s*`). The module-level `_DELTA_RE` itself lacked the leading `\s*`
(so it was STRICT, not the permissive form required by the contract and needed
by `_task_prose` which feeds un-stripped lines).

Three edits to `add-method/tooling/add.py`:

1. Deleted `_delta_start` local variable (line 1205).
2. Replaced both `_delta_start.match(...)` usages (lines 1227, 1234) with
   `_DELTA_RE.match(...)`.
3. Made `_DELTA_RE` PERMISSIVE — added leading `\s*` to the pattern — and
   rewrote its comment to remove the reference to the now-deleted `_delta_start`
   and explain the permissive/strict caller split.

Note: the comment was also edited to strip the literal enumeration token
from the comment text itself, because the test counts lines containing
the enumeration across the entire source file.

## Why permissive

`_task_prose` matches against `lines[i]` which are raw (un-stripped) lines from
the section 7 OBSERVE block. An indented delta tag such as
`    - [DDD · open] text (evidence: e)` would not have matched the old strict
`_DELTA_RE`. Making `_DELTA_RE` permissive (leading `\s*`) preserves the
existing behavior of `_task_prose` while letting `_collect_open_deltas` and
`_lint_task_deltas` — which pre-strip their lines — continue to match correctly
(`\s*` matches zero on already-stripped input).

## Evidence

```
# Red driver: 3 tests, 1 fail -> 3 pass
cd add-method/tooling && python3 -m unittest test_delta_grammar_dedup -v
Ran 3 tests in 0.015s  OK

# Spec acceptance grep
grep -cE "\(DDD\|SDD\|UDD\|TDD\|ADD\)" add.py
1

# Regression net: 52 tests, all pass
python3 -m unittest test_deltas_report test_deltas_lint test_competency_deltas test_report test_fold_nudge -v
Ran 52 tests in 0.410s  OK
```

## Residue

security: none
concurrency: none (module-load-time regex compile; pure parse)
architecture: none

## Proposed competency deltas (status: open)

- [ADD · open] comment text must not repeat regex enumeration literals — a
  test counting source lines catches comments as phantom copies (evidence:
  delta-grammar-dedup build, grep hit on comment line requiring rewrite)
- [ADD · open] when deduplicating, the canonical form must absorb the deleted
  copy's intended semantics — the old _DELTA_RE was strict while _delta_start
  was permissive; the contract mandated permissive (evidence: delta-grammar-dedup
  section 3 CONTRACT v1)
