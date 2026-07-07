# Vendored teacher snapshot — pin record

- upstream: https://github.com/msitarzewski/agency-agents
- commit:   24485830cd4b3c63a4a357b0664d9dedbab9653a
- fetched:  2026-06-30

## Trim rules (what is vendored)

KEEP: the agent-definition domain folders (engineering, security, design, product, finance, marketing, testing, sales, support, strategy, project-management, academic, game-development, gis, spatial-computing, paid-media, specialized, examples), plus `README.md` and the `divisions.json`/`tools.json` roster manifests, plus `LICENSE`.

DROP: the upstream `.github/` CI, `scripts/`, other-tool `integrations/`, `CONTRIBUTING*`, `SECURITY.md`, and dotfiles.

Content is RAW + verbatim — regenerate with `python3 add-method/scripts/update_teacher.py`. Attribution: see the repo-root `THIRD_PARTY_NOTICES.md` and the retained `LICENSE` in this folder (MIT).

## Refresh-drift check (run on every refresh PR)

Distilled personas keep `source:` provenance pointing into this snapshot. In the refresh PR
description, list every `.add/personas/*.md` whose `source:` file(s) changed or moved in the
diff — those personas are candidates for re-distillation, otherwise their provenance rots silently.
