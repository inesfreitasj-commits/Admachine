---
name: static-remix
description: "Turn a PDF of winning competitor static ads into on-brand recreations for the user's own product, generated with Nano Banana Pro (gemini-3-pro-image-preview). Use when the user runs /static-remix, or asks to remix, recreate, swipe, or adapt static ads from a PDF/swipe file into their own branded creative — 'make these ads for my product', 'remix this swipe file', 'recreate these statics on-brand', 'turn this PDF of ads into my ads', 'static ad batch from this PDF'. Extracts every image from the PDF, labels each by its framework heading (US VS THEM, BOLD CLAIM, Before & After, TESTIMONIAL...), tears them down, and regenerates them with the user's real product photo as a visual reference on every call."
---

# Static Remix — PDF swipe file → on-brand static ads

Input: a PDF of winning competitor static ads, grouped under framework headings.
Output: a dated run folder of production-ready statics for the user's product, each
one generated with their real product photo attached as a visual reference.

**The one rule that makes or breaks this skill:** the user's actual product photo is
downloaded, *viewed with the Read tool*, described concretely, and passed as the
reference image on **every single** generation call. Skip any part of that and the
output drifts off-brand — wrong bottle, wrong cap, invented label. Never describe the
product from page text alone.

---

## Step 1 — Locate the PDF and open the run folder

Find the PDF the user named. If the path is a placeholder, ambiguous, or missing, ask
for it before doing anything else — do not guess.

Create the run folder with a real timestamp:

```bash
RUN=~/.claude/skills/static-remix/runs/$(date +%Y%m%d-%H%M)
mkdir -p "$RUN"/{source,assets,briefs,production,logs}
echo "$RUN"
```

Everything for this run lives under `$RUN`. Never write into a previous run folder.

## Step 2 — Extract and label every image in the PDF

```bash
python3 ~/.claude/skills/static-remix/scripts/extract_pdf_images.py \
  "<pdf-path>" "$RUN/source" | tee "$RUN/logs/extract.log"
```

The script auto-detects the heading font by scoring every (font, size, bold) style by
the number of **distinct pages** it appears on in short text spans (≤60 chars), then
labels each image with the nearest heading above it — carrying the current section
across pages that have no heading of their own. It filters out logos and bullets
(<120px per side) and writes `source/manifest.json` + `source/manifest.txt`.

If PyMuPDF is missing: `pip install --user pymupdf`.

Check the log before continuing:
- **"No images extracted"** → the PDF is flattened/vector. Re-run with
  `--render-fallback --dpi 200` to rasterise whole pages instead.
- **"Heading font: NOT DETECTED"** → the PDF has no text layer (pure scan). Tell the
  user, then open a sample of images with Read and label the frameworks by eye.
- **Headings that look wrong** (page numbers, body copy) → the detected style is off.
  Read `manifest.json` → `headings_found`, pick the real heading style yourself, and
  relabel; do not proceed with garbage framework names.

Read `manifest.json` to get the framework list and per-framework image counts. You
need these for the next step.

## Step 3 — Ask the user (all four questions, every run)

**These four questions are REQUIRED on every run. Never skip one, never silently
default one, never infer an answer from context or from a previous run.** Ask them in
a single `AskUserQuestion` call (it takes up to 4 questions).

**a. Product URL** — required, no default. There is no sensible guess here.
   Options: any product URL already given in this conversation, plus
   `"Enter a different URL"`. If no URL is in context, give two options that both
   route to free text (e.g. `"Paste the product URL"` / `"I'll paste it in chat"`)
   and take the answer from the user's typed "Other" text. If the answer comes back
   empty or is not a URL, ask again — do not proceed.

**b. Total images** — how many finished images they want (10 / 50 / 100 / custom).

**c. Variations per concept** — usually 2. Same framework, **one axis changes** per
   variation (camera angle, overlay wording, background, model). Offer 2 / 3 / 4.

**d. Per-framework split** — show the frameworks you actually detected in step 2 with
   their source-image counts, and let the user assign a count to each. Options:
   `"Even split across all frameworks"`, a weighted suggestion based on what the PDF
   is heaviest in, and `"Custom split"` (they type e.g.
   `"20 US VS THEM, 10 BOLD CLAIM, 10 Before & After, 10 TESTIMONIAL"`).
   List the detected framework names verbatim in the question text so the user can
   name them back to you.

### Then validate the arithmetic — before generating anything

```
concepts = total_images / variations
sum(per_framework_counts) == total_images
```

- `total_images` must divide evenly by `variations`. If not, show the remainder and
  ask the user to adjust.
- The per-framework counts **must sum to `total_images`**. "Even split" means you
  compute it: divide evenly, then distribute the remainder to the frameworks with the
  most source examples.
- If the numbers don't add up, show the mismatch concretely — the numbers they gave,
  what they sum to, the target, and the gap — and **ask them to fix it before
  continuing**. Do not silently round, pad, or drop a framework.

Per-framework concept counts are `framework_images / variations`; if that isn't a
whole number for some framework, adjust the split with the user rather than guessing.

### Cost

Estimate at **$0.25 per image**: `total_images × $0.25`. Show it. **If the estimate
exceeds $10, confirm with the user before generating** (an `AskUserQuestion` with the
dollar figure and a proceed / change-the-number choice).

Write the confirmed settings to `$RUN/logs/run-config.json` so the run is reproducible.

## Step 4 — Fetch the product page AND download the real product photo

1. `WebFetch` the product URL. Pull out: product name, exact price, any offer or
   bundle copy, guarantee, shipping claim, key ingredients/benefits, and review count
   or rating. Save to `$RUN/assets/product-page.md`.
2. **Download the actual product photo.** For Shopify, `<product-url>.json` exposes
   image URLs:

```bash
curl -sSL "<product-url>.json" -o "$RUN/assets/product.json"
# image URLs live at product.images[].src
curl -sSL "<image-url>" -o "$RUN/assets/product.jpg"
```
   Not Shopify? Try `<url>/products/<handle>.json`, then the page's OpenGraph
   `og:image`, then the largest `<img>` on the page. If every route fails, **stop and
   ask the user to supply a product photo** — do not generate without one.

3. **Open `$RUN/assets/product.jpg` with the Read tool and look at it.** Then write
   `$RUN/assets/product-visual.md` describing what you actually see:
   - container type, shape, material, and **exact colour**
   - **cap colour** and finish
   - label: background colour, typography style, logo placement, accent colours
   - the product itself: capsule/softgel/powder/cream — colour, shape, count
   - brand palette: 2–4 dominant colours, named concretely ("deep navy", "warm cream")
   - any text visible on the label, quoted exactly

   Grab 2–3 images if the page has multiple angles; pick the cleanest front-facing
   shot as the reference image for generation.

   This description gets pasted into every generation prompt. Vague description →
   off-brand images. Do not skip the Read step and write this from the page text.

## Step 5 — Tear down the selected source examples

Select source images from `source/` per the agreed per-framework split (prefer the
largest/cleanest examples of each framework). **View each selected image with the Read
tool**, then write a short teardown into `$RUN/briefs/teardowns.md`:

- **Framework** — which one, and how it's constructed visually
- **Why it works** — the psychological mechanism (contrast, loss aversion, social
  proof, specificity, pattern interrupt), one or two sentences
- **Keep** — the structural parts that carry the persuasion: layout, split, arrow,
  badge, colour-blocking, text hierarchy
- **Swap** — what becomes the user's brand: product, palette, claim, price, proof

## Step 6 — Write one production brief per concept

One brief per concept in `$RUN/briefs/concept_NN.md`, tagged with its framework:

- **Scene description** — subject, setting, composition, lighting, camera angle,
  props, colour blocking. Concrete and visual.
- **Text overlays** — every on-image line, in exact quotes, with its position and
  relative size. Keep them short; long copy renders badly.
- **Headline** — the ad headline that runs with it
- **Caption** — the primary text / caption
- **Variation axis** — the ONE thing that changes between `var_01` and `var_02`
  (camera angle, overlay wording, background, model). Everything else stays fixed —
  that is what makes the pair a clean test.

**Pricing and offer copy must be pulled verbatim from the product page. Never invent a
price, discount, guarantee, review count, or clinical claim.** If a framework needs a
number the page doesn't have, use a claim the page does support instead.

## Step 7 — Generate with Nano Banana Pro

Helper: `~/.claude/skills/static-remix/scripts/gemini-image-ref.sh`

```bash
GEMINI_API_KEY=... \
  ~/.claude/skills/static-remix/scripts/gemini-image-ref.sh \
    "<full prompt>" 4:5 "$RUN/production/concept_01_var_01.png" "$RUN/assets/product.jpg"
```

It posts to `generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent`,
attaches the reference image as base64 `inline_data`, sets
`generationConfig.responseModalities=["IMAGE"]` and
`generationConfig.imageConfig.aspectRatio`, and decodes the returned base64 to
`output_path`. JSON encoding and base64 are done in perl, so it works on Git Bash for
Windows. Long prompts: use `--prompt-file <file>` to dodge shell quoting.

Rules for this step:

- **Pass the product photo as the reference image on EVERY call.** This is what keeps
  the bottle, cap, label, and palette consistent across the whole batch.
- Each prompt = scene description + exact overlay text + the product visual
  description from step 4 + a line like *"the product must exactly match the attached
  reference photo — same bottle, cap, label, and colours."*
- Default aspect `4:5` (feed). Use `1:1` for square placements, `9:16` for
  stories/Reels. Ask if the user has a placement preference.
- **Run sequentially**, not in parallel — the API rate-limits and parallel batches
  fail messily.
- Save as `production/concept_NN_var_MM.png`.
- Log every call's exit status to `$RUN/logs/generation.log`.

### Exit codes and retries

| code | meaning | action |
|---|---|---|
| 0 | image written | continue |
| 3 | `GEMINI_API_KEY` not set | stop, ask the user for the key |
| 4 | HTTP 4xx (bad request / auth / quota) | stop and report — retrying won't help |
| 5 | HTTP 5xx | **collect it, retry at the end of the run** |
| 6 | HTTP 200, no image (usually a safety block) | soften the prompt, retry once |

Collect every code-5 failure during the pass and **retry them once at the end**, after
the full batch is through. Report anything still missing rather than quietly shipping
a short batch.

Set `GEMINI_DRY_RUN=1` to build and inspect the request JSON without calling the API —
worth doing once on the first concept of a large batch to check the wiring.

## Step 8 — Write the report

`$RUN/report.txt`:

1. **Images produced** — count, and the per-framework breakdown; list any failures.
2. **Top 3 concepts to test first** — one line of reasoning each (why this one is
   most likely to win for this product and audience).
3. **Testing playbook** — budget per creative, how long to run before judging, kill
   criteria (e.g. spend threshold with no purchase, CTR/CPC/CPA floors), and what to
   do with a winner (scale, then iterate on the winning variation axis).
4. **Per-concept detail** — for each concept: framework, headline, caption, overlay
   text, variation axis, and its file names.

## Step 9 — Report back in chat, briefly

End with a short message only:

- the run folder path
- how many images were produced (and how many failed, if any)
- the top 3 concepts to test first

**Do not dump the report into chat.** Point at `report.txt`.

---

## Guardrails

- Never invent pricing, discounts, guarantees, review counts, or health claims — pull
  them verbatim from the product page.
- Never generate without having viewed the real product photo.
- Never skip or auto-answer any of the four questions in step 3.
- Never proceed past a per-framework/total mismatch without the user fixing it.
- Never overwrite a previous run folder.
