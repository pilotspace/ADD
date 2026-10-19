# Vendored teacher snapshot — pin record

- upstream: https://github.com/msitarzewski/agency-agents
- commit:   652b2692f8d8ec2b1f1a38e559073e287dfdc469
- fetched:  2026-10-19

## Trim rules (what is vendored)

KEEP: the agent-definition domain folders (engineering, security, design, product, finance, marketing, testing, sales, support, strategy, project-management, academic, game-development, gis, spatial-computing, paid-media, specialized, examples), plus `README.md` and the `divisions.json`/`tools.json` roster manifests, plus `LICENSE`.

DROP: the upstream `.github/` CI, `scripts/`, other-tool `integrations/`, `CONTRIBUTING*`, `SECURITY.md`, and dotfiles.

Content is RAW + verbatim — regenerate with `python3 add-method/scripts/update_teacher.py`. Attribution: see the repo-root `THIRD_PARTY_NOTICES.md` and the retained `LICENSE` in this folder (MIT).
