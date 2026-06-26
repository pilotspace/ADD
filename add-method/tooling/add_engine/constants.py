"""add_engine.constants — engine constants (moved verbatim from add.py).

Pure module-level constants. add.py re-exports these so `import add; add.STAGES`
(and the 6 _-prefixed names) still resolve. `__all__` lists the public names so
`from add_engine.constants import *` brings exactly them (not the Path import).
"""
import re
from pathlib import Path

__all__ = [
    "ROOT_DIRNAME",
    "STATE_FILE",
    "MILESTONE_FILE",
    "GOAL_UNSET",
    "STAGES",
    "GRADUATION_CUE",
    "RELEASABLE_CUE",
    "RELEASES_FILE",
    "PHASES",
    "GATES",
    "HEAL_CAP",
    "PHASE_GUIDE",
    "PHASE_OWNER",
    "SETUP_FILES",
    "GUIDELINE_FILES",
    "RULES_FILE_REL",
    "WORKFLOW_HEADINGS",
]

ROOT_DIRNAME = ".add"
STATE_FILE = "state.json"
MILESTONE_FILE = "MILESTONE.md"
# The project GOAL (v20) is read live from PROJECT.md — never copied into state.json
# (single-source; the foundation is the truth). A missing/blank source degrades to
# this sentinel so the read-only orientation surfaces never blank or crash.
GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
STAGES = ("prototype", "poc", "mvp", "production")
# v22 stage-graduation: the read-only cue `status` shows when the MVP is covered.
# Worded as the ACTION (never a file) so it stands before graduate.md exists.
GRADUATION_CUE = "MVP covered → propose graduation"
# release-altitude: the read-only cue `status` shows when ≥1 closed milestone is
# unreleased. The 5th scope level (release.md). `{n}` is filled at print time; the
# wording matches SKILL.md's "Beyond the bundle" cross-ref byte-for-byte.
RELEASABLE_CUE = "releasable: {n} milestone(s) closed since last release"
# the append-only release ledger lives at the PROJECT ROOT (the dir containing .add/),
# a sibling of CHANGELOG.md — NOT inside .add/. The ledger IS the attribution source:
# a milestone is "released" iff its slug appears on a `milestones:` row.
RELEASES_FILE = "RELEASES.md"
PHASES = ("ground", "specify", "scenarios", "contract", "tests", "build", "verify", "observe", "done")
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")
# heal-then-escalate (verify-integrity): the bounded self-heal loop cap. A CONFIRMED cheat
# (mechanical tripwire divergence, or an agent-reported semantic refute-read finding) returns
# the task to BUILD for an honest redo; after HEAL_CAP such attempts the next confirmed cheat
# forces a HARD-STOP escalation to the human. MONOTONIC — attempts never auto-resets (a gamed
# green is never auto-passed; the loop is never unbounded).
HEAL_CAP = 3



# `add.py guide` copy: per-phase (concrete next action, book chapter to read).
# Keep the action wording aligned with each phase's EXIT line in the TASK template.
PHASE_GUIDE = {
    "ground":    ("gather the real codebase the task touches — files, symbols, signatures, conventions, and the anchor points the contract will cite; defer to PROJECT.md/CONVENTIONS.md and gather only the task delta",
                  "02-the-flow.md"),
    "specify":   ("state every rule — Must / Reject (+ named code) / After; rank assumptions lowest-confidence first and flag the biggest risk",
                  "03-step-1-specify.md"),
    "scenarios": ("write one Given/When/Then per Must AND per Reject; every result observable",
                  "04-step-2-scenarios.md"),
    "contract":  ("freeze the shape — signature, fields, error codes; names match the glossary",
                  "05-step-3-contract.md"),
    "tests":     ("write one failing test per scenario; run them RED for the right reason",
                  "06-step-4-tests.md"),
    "build":     ("write the minimum code to pass the tests; change no test and no contract",
                  "07-step-5-build.md"),
    "verify":    ("run the suite + non-functional checks, then record the gate",
                  "08-step-6-verify.md"),
    "observe":   ("note what to watch + the spec delta for the next loop",
                  "09-the-loop.md"),
    "done":      ("this task is done — pick the next feature",
                  "02-the-flow.md"),
}
# Phase -> who owns it, for the `--json` autonomy signal. An autonomous harness may run a
# phase only when owner=="ai" (stop is false); every other phase is a checkpoint. The map
# follows the book's who-does-what table (Verify is "human only"); `tests`/`build`/`observe`
# are AI-led. A phase missing here is `unmapped_phase` (fail closed) — never defaulted.
PHASE_OWNER = {
    "ground": "ai",
    "specify": "human", "scenarios": "human", "contract": "seam",
    "tests": "ai", "build": "ai", "verify": "human", "observe": "ai", "done": "human",
}
SETUP_FILES = ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist", "DESIGN.md", "SOUL.md")

# Scaffolded into .add/.gitignore at init so the engine's transient LOCAL artifacts
# never reach git. Bare-filename patterns match at any depth under .add/ (tasks/,
# milestones/, archive/). These are working state, not records: scope-snapshot.json
# is the tests->build touch baseline the verify scope-gate reads from disk (the
# durable scope declaration is the state.json anchor); pre-archive-state.bak.json is
# archive-milestone's pre-delete recovery net — needed on disk, never in history;
# pre-update-state.bak.json is the installer update's pre-write state backup (cli.js
# cmdUpdate / pip _installer.update) — same "on disk, never in git" need; .update-cache.json
# is the update-nudge's once-a-day registry throttle. All stay on disk; git-ignoring them
# is hygiene, never deletion. SINGLE-SOURCED: this constant is kept byte-identical to
# tooling/templates/gitignore.tmpl (test_gitignore_bak_seed parity) so the installers,
# which seed/refresh .add/.gitignore from that template on update, never drift from init.
_GITIGNORE_BODY = """\
# ADD engine transient artifacts — local working state, never committed.
# (Scaffolded by `add.py init`; refreshed additively by the installer on update.)
scope-snapshot.json
pre-archive-state.bak.json
pre-update-state.bak.json
.update-cache.json
"""

# Guideline-injection targets + version-stable markers. NEVER change these marker
# strings: a re-run finds the old block by exact match, so changing them would
# orphan every block written by a prior version (see TASK guideline-inject).
GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md")
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"

# Rule-file mode (ccsk-style projects): instead of inlining the block into CLAUDE.md,
# write it to a dedicated rule file under .claude/rules/ and leave a one-line reference
# in CLAUDE.md's Workflows section. .claude/rules/ is a CLAUDE-only convention, so this
# mode only ever relocates CLAUDE.md — AGENTS.md/.clinerules keep the inline block.
RULES_FILE_REL = Path(".claude") / "rules" / "add-workflows.md"
# Headings (most→least specific) a project may already use to group rule/workflow links.
# Match is case-insensitive on the heading TEXT, at any `#` level.
WORKFLOW_HEADINGS = ("Rules & Workflows", "Workflows", "Rules")
_RULE_REF_LINE = "- ADD (AI-Driven Development) Workflows rules: ./.claude/rules/add-workflows.md"

# Minimal embedded fallback so the tool still works if templates/ is missing
# (circuit breaker: never hard-fail just because a template file was deleted).
_FALLBACK_TASK = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
autonomy: auto
phase: ground

## 0 · GROUND
Touches (files · symbols · signatures):
Honors (patterns / conventions):
Anchors the contract cites:

## 1 · SPECIFY
Feature:
Framings weighed:
Must:
Reject:
After:
Assumptions — lowest-confidence first:
  ⚠ <most likely wrong> — lowest confidence because <why>; if wrong: <cost>

## 2 · SCENARIOS
## 3 · CONTRACT
Status: DRAFT
## 4 · TESTS
## 5 · BUILD
## 6 · VERIFY
### GATE RECORD
Outcome:
## 7 · OBSERVE
### Spec delta
### Competency deltas
"""


# Fast-lane fallback: the minimal TASK.md variant (sections {0,1,3,4,5,6}; §2 + §7 dropped).
# Mirrors templates/TASK.fast.md.tmpl's section set (circuit-breaker parity); a deleted
# templates/ never hard-fails the fast lane. Keeps the trust floor: §3 freeze-flag + Status,
# §6 GATE RECORD/Outcome, §0 Anchors, §4 red-before-build, §5 Scope.
_FALLBACK_TASK_FAST = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
autonomy: auto
phase: ground
fast: true

## 0 · GROUND
Touches (files · symbols):
Anchors the contract cites:

## 1 · SPECIFY
Feature:
Must:
Reject:
Accept:
Assumptions: ⚠ <most likely wrong> — why; if wrong: <cost>

## 3 · CONTRACT
Least-sure flag surfaced at freeze:
Status: DRAFT

## 4 · TESTS
Plan:
Tests live in: `./tests/` · MUST run red before Build.

## 5 · BUILD
Scope (may touch): `./src/`

## 6 · VERIFY
Build expectations (from §1 Accept + §3 CONTRACT):
### GATE RECORD
Outcome:
Reviewed by:
"""

_DEFAULT_WIDTH = 72       # fixed width for the persisted/canonical render (RETRO.md)


# --- shared delta-parsing regexes (used by taskdoc readers AND the deltas-web lint) ---
_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(DDD|SDD|UDD|TDD|ADD)\s*·\s*(open|folded|rejected)\s*\]\s*(.+)$"
)
_EVIDENCE_RE = re.compile(r"^(.*?)\s*\(evidence:\s*(.*?)\)\s*$")
_SPEC_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(SPEC)\s*·\s*(open|seeded|dropped)\s*\]\s*(.+)$"
)


# --- autonomy levels (shared: autonomy resolvers + _AUTONOMY_ORDER/cmd_autonomy) ---
_AUTONOMY_LEVELS = ("manual", "conservative", "auto")
