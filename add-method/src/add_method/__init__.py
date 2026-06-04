"""add_method — Python installer for the ADD (AI-Driven Development) method.

Published as `pilotspace-add` on PyPI. Installs the ADD skill, tooling, and
AIDD book into a target project, then runs `add.py init`.

Usage (CLI):
    pilotspace-add init [targetDir] [--force] [--stage STAGE] [--name NAME]

Usage (Python API):
    from add_method import install
    install("/path/to/project", stage="mvp", name="my-app")
"""
from add_method._installer import install

__all__ = ["install"]
__version__ = "1.1.0"
