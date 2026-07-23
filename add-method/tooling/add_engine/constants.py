"""add_engine.constants — engine constants (moved verbatim from add.py).

Pure module-level constants. add.py re-exports these so `import add; add.STAGES`
(and the 6 _-prefixed names) still resolve. `__all__` lists the public names so
`from add_engine.constants import *` brings exactly them.
"""
import re

__all__ = [
    "BOOK_URL",
    "book_url",
    "ROOT_DIRNAME",
    "STATE_FILE",
    "MILESTONE_FILE",
    "GOAL_UNSET",
    "STAGES",
    "PHASES",
    "LEGACY_PHASES",
    "GATES",
    "HEAL_CAP",
    "PHASE_GUIDE",
    "PHASE_OWNER",
    "PHASE_GROUPS",
    "PHASE_AGENT",
    "SETUP_FILES",
    "PERSONA_FRONTMATTER_KEYS",
    "PERSONA_REQUIRED_SECTIONS",
    "PERSONA_FLOW_VALUES",
    "TASK_KINDS",
    "SPEC_DDS",
    "PERSONA_HINT",
    "PERSONA_FIT_HINT_TEMPLATE",
    "GUIDELINE_FILES",
    "_GATE_MODES",
    "_SKIPPABLE_PHASES",
    "_DIALECT_CLASSES",
]

ROOT_DIRNAME = ".add"
STATE_FILE = "state.json"
MILESTONE_FILE = "MILESTONE.md"
# The project GOAL (v20) is read live from PROJECT.md — never copied into state.json
# (single-source; the foundation is the truth). A missing/blank source degrades to
# this sentinel so the read-only orientation surfaces never blank or crash.
GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
STAGES = ("prototype", "poc", "mvp", "production")
# kernel-trim (ADD 2.0 M5): GRADUATION_CUE / RELEASABLE_CUE / RELEASES_FILE died with the
# graduate/release verbs — the release-manager persona owns that judgment now.
PHASES = ("direction", "build", "verify", "done")
# phase-collapse-3 (thin-engine-loop W2): the 6-phase walk collapsed to 3 work phases.
# `direction` is the whole front span (the old specify+plan+tests — §1–§4 drafted
# top-to-bottom, ONE freeze approval crosses it into build). Legacy tokens normalize to
# their 3-phase home at READ time (load_state) — 473 pre-collapse task records are never
# bulk-rewritten; the map below is the single source both load_state and _phase_index use.
LEGACY_PHASES = {
    "ground": "direction", "specify": "direction", "scenarios": "direction",
    "contract": "direction", "plan": "direction", "tests": "direction",
    "observe": "verify",
}
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")
# heal-then-escalate (verify-integrity): the bounded self-heal loop cap. A CONFIRMED cheat
# (mechanical tripwire divergence, or an agent-reported semantic refute-read finding) returns
# the task to BUILD for an honest redo; after HEAL_CAP such attempts the next confirmed cheat
# forces a HARD-STOP escalation to the human. MONOTONIC — attempts never auto-resets (a gamed
# green is never auto-passed; the loop is never unbounded).
HEAL_CAP = 3



# The AIDD book's published home (book-stops-shipping, ADD 2.0 M6b): the book no
# longer installs into projects as .add/docs/ — every engine chapter pointer deep-
# links here instead. mkdocs pretty-URLs: docs/<stem>.md renders at <BOOK_URL>/<stem>/.
BOOK_URL = "https://pilotspace.github.io/ADD"


def book_url(chapter: str) -> str:
    """Deep link for a book chapter filename ('02-the-flow.md' -> …/02-the-flow/)."""
    stem = chapter[:-3] if chapter.endswith(".md") else chapter
    return f"{BOOK_URL}/{stem}/"


# `add.py guide` copy: per-phase (concrete next action, book chapter to read).
# Keep the action wording aligned with each phase's EXIT line in the TASK template.
PHASE_GUIDE = {
    "direction": ("draft the Direction bundle top-to-bottom — §1 rules (Must / Reject + named codes / After, assumptions ranked lowest-confidence first) · §2 one scenario per rule · §3 the change PLAN: ground the real code, draft the contract, and DESCRIBE what this task will do (scope · ordered batches · approach — the plan-of-action the freeze report shows the human) · §4 red suite failing for the right reason; then the ONE approval: freeze --by <name> --cross",
                  "03-step-1-specify.md"),
    "build":     ("write the minimum code to pass the tests; change no test and no contract",
                  "07-step-5-build.md"),
    "verify":    ("run the suite + non-functional checks, then record the gate; then note what to watch + the spec delta for the next loop (§7)",
                  "08-step-6-verify.md"),
    "done":      ("this task is done — pick the next feature",
                  "02-the-flow.md"),
}
# Phase -> who owns it, for the `--json` autonomy signal. An autonomous harness may run a
# phase only when owner=="ai" (stop is false); every other phase is a checkpoint. The map
# follows the book's who-does-what table (Verify is "human only"); `tests`/`build`
# are AI-led. A phase missing here is `unmapped_phase` (fail closed) — never defaulted.
PHASE_OWNER = {
    "direction": "seam",
    "build": "ai", "verify": "human", "done": "human",
}
# phase-bundles: the work phases (PHASES minus the terminal "done") group into 3
# agent-owned bundles surfaced at `status`/`guide` — DIRECTION fixes the shape (through
# the frozen change plan — grounding + contract + build-strategy — AND the red suite; the
# method thesis is "fix spec/scenarios/plan/failing-tests BEFORE the build"), BUILD makes
# it green, VERIFY earns trust and feeds the next loop. A grouping OVER PHASES, never a
# reorder; "done" (terminal, human-led) deliberately has no bundle — see PHASE_AGENT/
# _phase_bundle below. Union == set(PHASES) - {"done"}, pairwise disjoint (test_phase_bundles.py).
PHASE_GROUPS = {
    "DIRECTION": ("direction",),
    "BUILD": ("build",),
    "VERIFY": ("verify",),
}
# phase-bundles: the roster agent PREFERRED for each phase (per-PHASE, not per-bundle —
# advisor-split: `add-worker` is the execution shell for every phase; the spawn prompt names
# the mode (direction·build·verify·persona) and the agent loads that beat's guide + the fitting
# persona (personas carry the expertise, the agent carries the discipline). `add-advisor` is
# spawned on demand to propose/pressure-test/decide — it is not a per-phase default, so it is
# absent here. A phase missing here is a bug (PHASE_GROUPS' own union covers every key);
# `_phase_bundle` is the fail-closed resolver for an unmapped/corrupted phase token, not this map.
PHASE_AGENT = {
    "direction": "add-worker",
    "build": "add-worker",
    "verify": "add-worker",
}
SETUP_FILES = ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist", "DESIGN.md", "SOUL.md")

# persona-setup: a PERSONA living doc (`.add/personas/<slug>.md`) is a frozen-schema file
# distilled from the vendored teacher library to its critical-rules + default-requirement +
# measurable success-metrics. The schema is presence-based (these keys/sections must exist);
# content quality is the AI's authoring concern, not the engine gate. NO-EXEC: validation is pure.
PERSONA_FRONTMATTER_KEYS = ("name", "vibe")
PERSONA_REQUIRED_SECTIONS = ("## Identity", "## Critical Rules", "## Default Requirement", "## Success Metrics")
# persona-schema-hardening: the closed set of apply-surfaces a `flow:` value may name — the
# single source the quality predicate reads (a value outside this set is loaded by NO surface,
# so a typo would otherwise fail silently). Findings are WARN-only (measure-not-block).
PERSONA_FLOW_VALUES = ("design", "build", "advisor", "verify")
# persona-task-kinds (ADD 2.0 M1 persona-core): the closed task-kind taxonomy — the join key
# between a persona's routing claim (`task-kinds:` frontmatter) and a task's declared kind
# (`kind:` header line). Route-outcome traces record it, the persona scoreboard groups by it.
# Closed on purpose: a free-text kind can't be scored across tasks. Measure-not-block —
# an unknown kind is a named WARN (quality predicate Finding C), never a refusal.
TASK_KINDS = ("feature", "refactor", "test", "docs", "ui",
              "security", "data", "infra", "release", "integration")

# specs-5dd (ADD 2.0 M3): the closed 5-DD map — dd tag -> (spec file under .add/specs/,
# title, lens). init renders ONE template (templates/specs/SPEC.md.tmpl) five ways;
# `delta-append <dd>` routes a lesson to its file. Closed on purpose: the five lenses ARE
# the method's competency model (DDD·SDD·UDD·TDD·ADD) — an unknown dd is a refusal
# (delta_dd_unknown), because a delta filed under a sixth ad-hoc lens is a delta lost.
SPEC_DDS = {
    "ddd": ("domain.md", "Domain",
            "what the system IS: entities, rules, ubiquitous language (DDD)"),
    "sdd": ("system.md", "System",
            "how it is built: architecture, contracts, data shapes (SDD)"),
    "udd": ("experience.md", "Experience",
            "how it feels to use: flows, surfaces, the humans served (UDD)"),
    "tdd": ("quality.md", "Quality",
            "how we know it works: test strategy, floors, evidence (TDD)"),
    "add": ("method.md", "Method",
            "how we work: the loop, autonomy, ceremony budget (ADD)"),
}

# persona-seed-nudge v2: ONE hint, single-sourced — `new-milestone`/`check`/`status` all print
# THIS constant (not their own copy) so the wording can never drift across the three surfaces.
# Project-scoped (not "this milestone's domain") per the confirmed v2 amendment: the AI should
# catch up ALL of a project's missing personas, not draft a single milestone-fit one.
PERSONA_HINT = ("no project-fit persona seeded yet under .add/personas/ — use the persona-author "
                "skill (or read docs/18-personas.md) to author the project's persona(s) "
                "from PROJECT.md's domain")

# persona-fit-nudge: the OPPOSITE-branch, mutually-exclusive sibling of PERSONA_HINT — fires only
# when ≥1 real persona ALREADY exists, so a brand-new milestone doesn't silently assume one of
# them fits its domain. Existence-only (names the persona slugs already seeded); the AI still
# owns the actual fit judgment (add-worker's persona mode, guided by the persona-author skill) —
# the engine never scores content similarity. {slugs} is filled at call time from
# `.add/personas/*.md` (excluding any `_`-prefixed scaffold).
PERSONA_FIT_HINT_TEMPLATE = (
    "existing persona(s) seeded — {slugs} — confirm one fits this milestone's domain, or use the "
    "persona-author skill (or read docs/18-personas.md) to author a better-fit one"
)

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

# ADD-managed vendor trees: regenerable/vendored copies the installer drops in,
# never project-authored — mirrors the .add/docs/ rationale above, generalized
# to every consumer project (not just this repo). Patterns are BARE, not repo-
# root style: this file lives INSIDE .add/, so git resolves its patterns
# relative to .add/ itself — a ".add/"-prefixed pattern here would look for
# the non-existent .add/.add/tooling/ and never match anything. (one further
# managed tree is NOT listed here — the engine's own _GITIGNORE_BODY constant
# must stay hands-off of it by name; the installer twins seed that pattern
# themselves, also bare.)
tooling/
docs/
"""

# Guideline-injection targets + version-stable markers. NEVER change these marker
# strings: a re-run finds the old block by exact match, so changing them would
# orphan every block written by a prior version (see TASK guideline-inject).
GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md", ".clinerules")
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"

# PROJECT.md specs-pointer markers (foundation-specs-refs). PROJECT.md stays the thin
# read-first index; this managed, SPEC_DDS-driven block routes to the standing 5-DD picture
# in `.add/specs/`. `init` scaffolds it, `migrate` wires it into a pre-pointer PROJECT.md;
# both refresh it idempotently in place. Same never-change rule as the guideline markers:
# a re-run finds the old block by exact match, so changing these would orphan every block a
# prior version wrote.
_SPECS_BEGIN = "<!-- ADD:SPECS — the 5-DD standing picture; managed by add.py — do not edit inside -->"
_SPECS_END = "<!-- /ADD:SPECS -->"

# Minimal embedded fallback so the tool still works if templates/ is missing
# (circuit breaker: never hard-fail just because a template file was deleted).
_FALLBACK_TASK = """# PLAN: {title}

slug: {slug} · created: {date} · stage: {stage}
autonomy: auto
phase: direction

## 1 · SPECIFY
Feature:
Framings weighed:
Must:
Reject:
After:
Boundary:
<assumptions>
  ⚠ <the ONE assumption most likely to be wrong — if wrong: <cost>>
</assumptions>

## 3 · PLAN
### Contract
Status: DRAFT
### Build-strategy
Scope (may touch):
Regression floor:
## 4 · TESTS & SCENARIOS
## 5 · BUILD
## 6 · VERIFY
### GATE RECORD
Outcome:
## 7 · OBSERVE
### Spec delta
### Competency deltas
"""


# atomic-node: the ONE template IS the lean render — _FAST_SECTIONS retired with
# the lane scaffolds (the stripped blocks no longer exist in the template).


_DEFAULT_WIDTH = 72       # fixed width for the persisted/canonical render (RETRO.md)


# --- shared delta-parsing regexes (used by taskdoc readers AND the deltas-web lint) ---
# Groups stay (1) competency, (2) status, (3) text — every caller relies on that. A competency
# lesson MAY carry an OPTIONAL persona target + section hint between status and `]`
# (persona-self-improve): `[<comp> · <status> · persona:<slug> · <critical-rule|success-metric>] …`.
# That clause is NON-capturing here (group numbering unchanged); _PERSONA_TAG_RE below pulls the
# slug + hint out when a route needs them — permissively, so an unroutable hint still PARSES (and is
# rejected by code) rather than silently failing to match.
_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(DDD|SDD|UDD|TDD|ADD)\s*·\s*(open|folded|rejected)"
    r"(?:\s*·\s*persona:[^\s·\]]+\s*·\s*[^·\]]+?)?\s*\]\s*(.+)$"
)
# Pull the OPTIONAL persona target + section hint out of a delta tag line (persona-self-improve).
_PERSONA_TAG_RE = re.compile(r"persona:([^\s·\]]+)\s*·\s*([^·\]]+?)\s*\]")
_EVIDENCE_RE = re.compile(r"^(.*?)\s*\(evidence:\s*(.*?)\)\s*$")
_SPEC_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(SPEC)\s*·\s*(open|seeded|dropped|carried)\s*\]\s*(.+)$"
)

# delta-task-backlink: reads the `[→ <slug>]` seed stamp `_resolve_spec_delta` appends, so the
# delta→task lineage can be walked back (check WARNs when a seeded pointer no longer resolves).
_SEED_POINTER_RE = re.compile(r"\[→\s*([A-Za-z0-9_-]+)\s*\]")

# rule-id-coverage: §1 Must-ID / Reject-code lines, plus the §2 scenario tag and §4 `covers:`
# back-reference a task uses to claim coverage of a rule. A Reject's ID is its literal error_code
# string (from `-> "<error_code>"`), never a positional R1/R2 sequence number.
_MUST_ID_RE = re.compile(r"^\s*-\s*(M\d+)\s*:", re.MULTILINE)
_REJECT_CODE_RE = re.compile(r'^\s*-\s.*->\s*"([^"]+)"\s*$', re.MULTILINE)
_SCENARIO_TAG_RE = re.compile(r"^\s*Scenario:.*#\s*(.+?)\s*$", re.MULTILINE)
_COVERS_LINE_RE = re.compile(r"covers:\s*(.+?)\s*$", re.MULTILINE)
_TAG_TOKEN_RE = re.compile(r"(M\d+|R:[A-Za-z0-9_]+)")


# --- autonomy levels (shared: autonomy resolvers + _AUTONOMY_ORDER/cmd_autonomy) ---
_AUTONOMY_LEVELS = ("manual", "conservative", "auto")

# --- sensitivity taxonomy (shared: _task_sensitivity reader + cmd_freeze/status/audit) — the
#     risk-CLASS the human declares in the TASK header at freeze (risk-sensitivity-taxonomy). The
#     engine validates + surfaces a HUMAN-declared token; it NEVER classifies. A closed enum, sibling
#     of _AUTONOMY_LEVELS. Consumed downstream by advisor-gate-relax (mechanical). ---
_SENSITIVITY_VALUES = ("security", "data", "architecture", "mechanical")

# --- gate mode (shared: _task_gate_mode reader + cmd_freeze's --ai-plan-verify path) — the
#     two-way DIRECTION-freeze declaration (ai-plan-verify-gate): human (default) | ai-plan-verify.
#     A closed 2-tuple, sibling of _AUTONOMY_LEVELS/_SENSITIVITY_VALUES — but,
#     unlike them, listed in __all__: a NEW trust-loosening capability is deliberately surfaced via
#     `from add_engine.constants import *`, not tucked into the _-prefixed sibling import list.
#     Absent header line -> None from the resolver, treated as "human" by every caller (fail-closed
#     default — never silently upgrades to the loosened path). ---
_GATE_MODES = ("human", "ai-plan-verify")

# --- skippable phases (shared: _task_skip_set reader + cmd_advance's skip pre-pass) — the
#     fast-lane-skips closed tuple: the ONLY set cmd_advance's skip pre-pass ever tests `nxt`
#     against (scenarios left it at phase-merge-specify: merged into specify, the retired
#     header token is tolerated-and-ignored). specify/plan/tests/build/verify can NEVER be
#     skipped — a structural
#     exclusion (this tuple never names them), not a runtime-checked policy. Same relative order
#     as PHASES. Listed in __all__ (mirrors _GATE_MODES): a new trust-loosening capability is
#     deliberately surfaced via `from add_engine.constants import *`, not tucked away. ---
_SKIPPABLE_PHASES = ()

# --- format-dialect registry (shared: _dialect_gaps + the tests->build crossing warning +
#     cmd_check's dialect_gap lint) — quality-floors floor 1. Closed (name, regex) pairs: a
#     class matches only its FULL value shape, never prose fragments (a bare `2026-07-10`
#     date must not match — the aware class requires the T separator + a zone suffix). Born
#     from benchmark WV1 wm2: an arm's own suite stayed green on naive timestamps while the
#     spec's own examples were Z-suffixed; the aware/naive crash shipped green. Listed in
#     __all__ (mirrors _GATE_MODES): a new trust surface is deliberately surfaced. ---
_DIALECT_CLASSES = (
    ("aware-iso-timestamp",
     r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"),
)
