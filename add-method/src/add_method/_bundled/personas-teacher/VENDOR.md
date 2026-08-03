# Vendored teacher snapshot — pin record

- upstream: https://github.com/msitarzewski/agency-agents
- commit:   c89557f78509868c6d4cc08e5cbc79bc8625fe1c
- fetched:  2026-08-03

## Trim rules (what is vendored)

KEEP: the agent-definition domain folders (engineering, security, design, product, finance, marketing, testing, sales, support, strategy, project-management, academic, game-development, gis, spatial-computing, paid-media, specialized, examples), plus `README.md` and the `divisions.json`/`tools.json` roster manifests, plus `LICENSE`.

DROP: the upstream `.github/` CI, `scripts/`, other-tool `integrations/`, `CONTRIBUTING*`, `SECURITY.md`, and dotfiles.

Content is RAW + verbatim — regenerate with `python3 add-method/scripts/update_teacher.py`. Attribution: see the repo-root `THIRD_PARTY_NOTICES.md` and the retained `LICENSE` in this folder (MIT).
