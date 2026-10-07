"""add_method — the pip installer for ADD (AI-Driven Development).

Published as `pilotspace-add` on PyPI. Copies the ADD skill into a project (or, with
`--global`, into ~/.claude/skills/add) and scaffolds the `.add/` bundle. ADD 4.0 has no
engine: the method is the skill, and its tools are git and the project's own test command.

Usage (CLI):
    pilotspace-add [init|update] [dir] [--name NAME]
    pilotspace-add --global

Usage (Python API):
    from add_method import install
    install("/path/to/project", name="my-app")   # 0 ok · 1 failed
"""
from add_method._installer import install

__all__ = ["install"]
__version__ = "4.1.0"
