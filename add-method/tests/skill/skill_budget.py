"""The skill surface's budgets — one module, one literal each.

SKILL.md went ONE line over its pin and fourteen checks across seven files reported it. Fourteen
failures for one fact, and a re-pin that meant finding eight literals — so the number drifts the
first time someone finds only seven (R:SILENTPIN).

Every budget below is asserted by exactly ONE guard, named here. Other checks may READ these
constants to build a message; asserting one outside its owner is refused by
`test_one_budget_one_guard.py`.
"""

# Human-set, and re-pinned from 150 at 3.1.0 by a human call. SKILL.md is the only always-loaded
# cost in the whole skill, which is why it alone carries a hand-held number rather than a ratchet.
# Owner: tests/skill/test_surface.py::test_router_within_line_budget
LINE_BUDGET = 176

# A ratchet, pinned to the measured byte count of skill/add/SKILL.md at authoring time. Line count
# is a PROXY for the always-loaded cost, not the cost itself: a reflow — same content, fewer and
# longer lines — makes the line pin go greener while the real cost rises. That happened for real
# (176/176 lines held while the file grew 189 bytes). Never raise without funding it elsewhere.
# Owner: tests/skill/test_surface.py::test_skill_byte_budget_holds
BYTE_BUDGET = 13258

# The whole `add` skill tree, every .md the router can reach. 2.5 shipped 2031 lines; the budget
# is what holds the trim. `persona-author/` is a nested sub-skill with its own budget and is not
# counted against this one.
# Owner: tests/skill/test_surface.py::test_total_surface_within_budget
SURFACE_BUDGET = 1500

# --- Prose pins -------------------------------------------------------------------------------
# Same charge, different type. A skill-tree file's sha256 was a literal in `test_surface.py` while
# `test_skill_reads_the_graph.py` recovered it by REGEXING that file's source — three modules
# pinning each other's source text, which is the shape this module exists to end. A pin moves only
# when a human deliberately edits the prose, in the same commit, with the reason on its line.
# Owner: tests/skill/test_surface.py::test_skill_tree_prose_unedited_by_this_task
PROSE_PINS = {
    "SKILL.md": "51d076ad0bbc723734e445d5a19a1b2974bbca68d11c88191462a05aa1b11081",   # aimed @ evidence-over-tests C1: CHECKS sized as ≥1 discriminating check per referent, never a quota
    "intake.md": "ee78c0816e09eba20be82535b7e8729c42a715589743508c2dcd5f4155e95e41",   # aimed @ skill-reads-the-graph: the loop reads the graph before it plans. prior: db288507…
}
