# Admachine

## `static-remix` skill

Turns a PDF of winning competitor static ads into on-brand recreations for your own
product, generated with Nano Banana Pro (`gemini-3-pro-image-preview`).

Source of truth lives in `.claude/skills/static-remix/`. Install it for personal use with:

```bash
cp -r .claude/skills/static-remix ~/.claude/skills/
```

Then run it in Claude Code with `/static-remix`.

### Requirements

- `pip install --user pymupdf` — PDF image extraction
- `GEMINI_API_KEY` in the environment — image generation
- `curl` + `perl` — the generation helper uses only these, so it runs on Git Bash for Windows

### Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | The 9-step pipeline Claude follows |
| `scripts/extract_pdf_images.py` | Extracts every image from the PDF, labels each by nearest framework heading (heading font auto-detected) |
| `scripts/gemini-image-ref.sh` | One image per call via Nano Banana Pro, with a reference image attached as base64 |
| `references/prompting.md` | Prompt skeleton, per-framework scene patterns, variation-axis rules |
| `runs/` | One dated output folder per run |

### Cost

$0.25 per image. The skill shows the estimate and asks for confirmation above $10.
