# Diagram pipeline (reusable)

The book's hand-drawn infographics are **generated**, not hand-edited, so they stay regenerable as
the method evolves. The source of truth is the book chapters; these prompts render a faithful
picture of them, and `CHECKLIST.md` is the acceptance gate.

| Diagram | Prompt | Renders to | Chapter |
|---------|--------|------------|---------|
| The loop | `prompt-flow.txt` | `add-flow.png` (not yet rendered for 4.0; ch02 uses a mermaid diagram) | ch02 |
| Five competencies | `prompt-competencies.txt` | `add-competencies.png` | ch14 |
| The loop on its foundation | `prompt-foundation.txt` | `add-foundation.png` | ch14 |
| Three tiers | `prompt-hierarchy.txt` | `add-hierarchy.png` (current render predates 4.0's flat file names) | ch14 |

## Render

Uses the `nanobanana-rest` skill (Google Gemini image API; key in `~/.nanobanana.env`):

```bash
SKILL=~/.claude/skills/nanobanana-rest/scripts/nanobanana_rest.py
python3 "$SKILL" \
  --prompt "$(cat add-method/diagrams/prompt-hierarchy.txt)" \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9 --image-size 2K \
  --output add-hierarchy.png
```

`gemini-3-pro-image-preview` for the final (highest label fidelity); a flash model is fine while
iterating. The diagrams are 16:9 landscape.

## Accept (the gate is text accuracy)

Image models garble small text — **this is the failure mode to watch.** After every render, check
**every glyph** against `CHECKLIST.md`. A misspelled, dropped, or duplicated label = reject and
re-render. Expect to render a few times before one passes.

## Propagate

A passing PNG is copied into the book (`add-method/docs/`) and, for the images the root README
shows, into the repo root:

```bash
cp add-hierarchy.png add-method/docs/add-hierarchy.png
```

The raster itself is a human visual gate; `tests/book/test_book.py` only checks that every image a
page links to exists.
