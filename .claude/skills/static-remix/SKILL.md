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
2. **Get the actual product photo.** Prefer what the user supplies — a photo, a PDF,
   or a zip is more reliable than scraping and often the only route when the site is
   blocked. Extract a supplied PDF with the step-2 script (it applies PDF soft masks,
   so cut-out product shots come out on white instead of black). Otherwise scrape;
   for Shopify, `<product-url>.json` exposes image URLs:

```bash
curl -sSL "<product-url>.json" -o "$RUN/assets/product.json"
# image URLs live at product.images[].src
curl -sSL "<image-url>" -o "$RUN/assets/product.jpg"
```
   Not Shopify? Try `<url>/products/<handle>.json`, then the page's OpenGraph
   `og:image`, then the largest `<img>` on the page. If every route fails, **stop and
   ask the user to supply a product photo** — do not generate without one.

   **If the site is unreachable** (egress policy, login wall), do not guess and do not
   route around it: say which host is blocked and ask for full-page screenshots of the
   advertorial and sales page. Slice a tall screenshot into readable strips by opening
   the PNG with `fitz.open(file)` and calling `page.get_pixmap(clip=..., dpi=60)` per
   strip, then read the strips to pull pricing and claims verbatim.

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

**If the user supplies their own winning ads, tear those down FIRST and reproduce their
top repeated composition as a concept before reaching for any swipe-file framework.** A
format that already converts for this exact product outranks a stranger's ad every time.
Count how often each composition repeats across their winners — the most repeated one is
their proven format, and omitting it is the most expensive mistake available.

## Step 6 — Write one production brief per concept

One brief per concept in `$RUN/briefs/concept_NN.md`, tagged with its framework:

- **Scene description** — subject, setting, composition, lighting, camera angle,
  props, colour blocking. Concrete and visual.
- **Text overlays** — every on-image line, in exact quotes, with its position and
  relative size. Keep them short; long copy renders badly.
- **Headline** — the ad headline that runs with it
- **Caption** — the primary text / caption
- **Variation axis** — the ONE thing that changes between `var_01` and `var_02`.
  **It must be VISUAL: camera angle, composition, setting, crop, or model presence.**
  Everything else stays fixed — that is what makes the pair a clean test.

  **Never use overlay wording as the only axis.** Changing a few words while scene,
  lighting and product placement stay identical produces two images that look the
  same in a feed: half that concept's budget buys nothing. If you want to test copy,
  change the words *and* the composition.

- **Product scale** — every brief states how big the product sits in frame, with a
  physical size anchor and a cap on frame share (e.g. *"a small 20 ml bottle, about
  as tall as an adult hand is wide; no more than 15% of frame height; when held, the
  fingers wrap most of its height"*). Without this the model renders a palm-sized
  bottle as a 500 ml one. Expect to fight it: the instruction lands reliably when a
  hand or another object gives scale, and is often ignored in a bare product shot —
  check every image and regenerate the ones that came back oversized.

- **Angle** — see the aggressive-angle rule below.

### Native-market copy

**All copy must read as native to the target market, never as translated English.** For
non-English markets load `references/localization.md` before writing any overlay text,
headline or caption — it carries the user's copy persona and the register to write in.
Machine-translation-sounding copy is a defect on the same level as a garbled label.

### The concept bar — cut filler before it costs money

Three kinds of concept are rejected on sight and must not be proposed:
**not aggressive enough** (no number, no claim, no tension — could be any brand),
**generic** (stock lifestyle: smiling cyclist, sunset jog, couple laughing over coffee), and
**AI-looking** (bad hands, floating product, plastic skin, nonsense text).

Ten sharp concepts beat twenty with filler. Cut, don't pad.

`references/concept-library.md` carries the weekly 30-concept split, the concept types,
and the scene ideas the user has already validated.

### Put the timeframe in the copy

**Wherever an ad carries text, work the timeframe in** — "en 7 jours", "en 90 secondes",
"en 2 semaines". A deadline converts harder than a benefit alone. Standing user preference,
applies to every product.

### Always an aggressive angle

**Every concept carries an aggressive angle by default.** First-person, specific,
outcome-first, no hedging. Numbers and timings up front. The partner's or observer's
reaction as the proof. In DR, corporate wellness phrasing ("contribue à améliorer le
confort", "les résultats parlent d'eux-mêmes") is a defect, not a safe default — it is
the single most common way a generated batch underperforms the user's own winners.

Mine the aggression from what already converts for them: their winning ads' hooks are
the tone to match and, where the copy is theirs, to reuse verbatim.

**The guardrail that never moves:** aggressive *framing*, page-supported *facts*.
Invented prices, fabricated review counts, or medical outcome claims the page doesn't
make get the account banned rather than scaled. Aggression lives in the phrasing and
the imagery — never in a number you made up.

**Pricing and offer copy must be pulled verbatim from the product page. Never invent a
price, discount, guarantee, review count, or clinical claim.** If a framework needs a
number the page doesn't have, use a claim the page does support instead.

## Step 6.5 — Before spending: flag every shot you are not confident in

**Read `references/concept-library.md`, `references/native-realism.md` and
`references/rejected-patterns.md` first. Then, before a single API call, classify
every planned shot as high or low confidence, and raise the low-confidence ones with the
user BEFORE generating.**

The user pays $0.25 per image from their own key. An unasked question costs them money;
asking costs one message. Never gamble with someone else's credit to avoid a conversation.

Known-unreliable shots — do not propose these, or flag them explicitly if the user asks
for one:

| Shot type | Verdict |
|---|---|
| Product nearest the lens / on the front-most surface | **Will come back oversized.** Don't propose it. |
| Small product where the label must be readable | **Will come back garbled** at low reference resolution |
| Any scene wording with *dropper*, *serum*, *pipette* | **Will swap to amber glass.** Reword. |
| A pair differing only in wording | **Will come back as near-duplicates** |
| Product held in a hand | Medium — only reliable with the face anchor |
| Product resting at mid-distance | Reliable |
| Face-anchored held product | Reliable |

Raise a doubt as a concrete choice, not a vague check-in. *"This concept needs the label
readable, but your reference photo is too soft for that at this size. I can compose so the
label isn't the focal point, or you can send a sharper packshot and I'll do it properly.
Which?"*

**If the product photo is low-resolution, ask for a better one before generating a batch.**
It is the single highest-value input and costs the user nothing.

## Step 7 — Generate with Nano Banana Pro

Helper: `~/.claude/skills/static-remix/scripts/gemini-image-ref.sh`

**Never write the API key into a file.** Not into a batch script, not into a log, not
into a run folder — run folders get committed, and GitHub's secret scanner will block
the push after the work is done. Pass the key on the command line for a single call, and
for a batch script read it from the environment:

```bash
: "${GEMINI_API_KEY:?set GEMINI_API_KEY in the environment before running}"
```

If a key does reach a commit, fix the file and `git commit --amend` while it is still
unpushed — that drops it from history — and tell the user to rotate the key.

```bash
GEMINI_API_KEY=... \
  ~/.claude/skills/static-remix/scripts/gemini-image-ref.sh \
    "<full prompt>" 1:1 "$RUN/production/concept_01_var_01.png" "$RUN/assets/product.jpg"
```

It posts to `generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent`,
attaches the reference image as base64 `inline_data`, sets
`generationConfig.responseModalities=["IMAGE"]` and
`generationConfig.imageConfig.aspectRatio`, and decodes the returned base64 to
`output_path`. JSON encoding and base64 are done in perl, so it works on Git Bash for
Windows. Long prompts: use `--prompt-file <file>` to dodge shell quoting.

**Output format.** The model always returns JPEG — the API has no output-format
option. Ask for a `.png` path and the helper converts the bytes to real PNG with
PyMuPDF (already required for step 2) before saving. The file extension and the
actual bytes always agree, so ad-platform uploads don't reject the file.

Rules for this step:

- **Pass the product photo as the reference image on EVERY call.** This is what keeps
  the bottle, cap, label, and palette consistent across the whole batch.
- Each prompt = scene description + exact overlay text + the product visual
  description from step 4 + a line like *"the product must exactly match the attached
  reference photo — same bottle, cap, label, and colours."*
- **Localise the scene, not just the copy.** Buildings, signage, people, interiors, props,
  currency and — critically — **clothing matched to the current season in the target
  market**. Resolve the real date and season each run rather than assuming.
  `references/native-realism.md` has the checklist and the AI-tell fixes.

- **Ground the product in the scene.** Without this the bottle reads as a 2D cut-out
  pasted onto a photo. Require: a contact shadow where the base meets the surface; the
  same light direction and colour temperature as the rest of the frame; the same depth of
  field as its surroundings; a faint reflection on polished or wooden surfaces; and
  perspective matching the surface it stands on.

- **Never place the product in the extreme foreground.** This is the real cause of giant
  bottles — perspective enlarges anything near the lens, and no "no more than 12% of frame
  height" instruction overrides it. Put the product at the same depth as the person, on a
  nightstand or table beside them. The reliable alternative is having someone hold it with
  their fingers wrapped around it, which gives the model a scale anchor. A product standing
  alone in the foreground will come back oversized however you word the prompt.

- **If the reference photo is low-resolution, spell out the label copy in the prompt.**
  The model faithfully reproduces blur, so a fuzzy reference yields packaging covered in
  convincing gibberish. Quote the brand mark and every label line exactly, and say the
  reference is low-res and its text must be rendered crisply rather than copied. This
  is the single highest-value fix for brand fidelity.
- **Default aspect `1:1`, saved as `.png`.** Use `4:5` for vertical feed or `9:16`
  for stories/Reels only if the user asks. Confirm the placement if unsure.
- **Run sequentially**, not in parallel — the API rate-limits and parallel batches
  fail messily.
- Save as `production/concept_NN_var_MM.png`.
- `generationConfig.imageConfig.imageSize` accepts `"2K"` if the user wants larger
  files than the default 1024x1024; add it to the helper's JSON body if needed.
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

## Step 7.4 — Composite the copy in code, not in the image

**Generate the photograph. Draw the words yourself.** Nothing on an image model's
output can be trusted to be spelled correctly, and nothing it draws can be corrected
without paying for another generation. `scripts/compose_text.py` draws headlines,
badges, day labels, quotes, rating blocks and flag roundels onto a finished image for
free, exactly, and as many times as you like.

```python
import sys; sys.path.insert(0, "~/.claude/skills/static-remix/scripts")
from compose_text import Composer, hook_lockup, trim_uniform_border
```

Which copy goes where:

| Copy | Where it belongs |
|---|---|
| Headlines, kickers, badges, day labels, quotes, ratings, press strips | **Composited.** Flat overlay graphics — the model adds nothing |
| Price labels on a shelf rail, signage, a handwritten sign, label text on the pack | **Generated.** They live in the scene's perspective and lighting |

Everything in the module is specified in **fractions of the image size**, so a layout
measured once off the client's winner reproduces at any output resolution.

Three rules the module enforces so you cannot break them by accident:

- **It refuses to shrink type to fit.** `centered()`, `badge()` and `hook_lockup()`
  raise if a line would run off the frame. Shorten the copy instead — auto-fitting
  silently produced a headline nobody could read in the feed, and a centred line whose
  width exceeded the frame bled off *both* edges unnoticed.
- **Use `band()`, not `scrim()`, over a busy or white background.** A gradient over
  supermarket price labels leaves white copy unreadable. Check what is actually under
  the text before choosing.
- **`scrim()` is a real alpha ramp, not stacked translucent rectangles.** Overlapping
  rects double-darken at every seam and the banding is visible in the feed.

Also run `trim_uniform_border()` on every raw photo before compositing. The model
sometimes frames a shot with a flat white margin, which reads as a designed edge and
destroys the raw-phone-photo illusion the native ads depend on.

**Reference upgrade — build a two-panel reference when reproducing a scene.** The
helper takes one reference image, so when you are iterating on a client winner, paste
their high-resolution packshot beside the winning ad on one canvas and attach that.
The model then has both the pack and the scene. This is what makes shelf rail labels
and pack lettering come back clean at the same time.

## Step 7.5 — Quality gate: view EVERY image before showing the user anything

Run `python3 scripts/qc_batch.py <run>/final` to catch near-duplicate pairs and
product-colour drift mechanically, then **open every single image with the Read tool.**

`qc_batch.py` only pairs files named `*_var_NN`. When a batch uses concept names
instead, run the all-pairs check yourself — a batch of 20 has 190 pairs and the
duplicate can be anywhere:

```python
import sys, itertools, glob, os
sys.path.insert(0, "~/.claude/skills/static-remix/scripts")
import qc_batch as q
sigs = {os.path.basename(f): q.signature(f) for f in sorted(glob.glob("final/*.png"))}
worst = sorted((q.correlation(sigs[a], sigs[b]), a, b)
               for a, b in itertools.combinations(sigs, 2))[-8:]
```

Anything at r >= 0.60 is a duplicate to Meta.

**Run the duplicate check on `production/`, not `final/`.** When a batch shares one
composited lockup — the same kicker, the same bottom band in the same place on every
image — that template dominates a 16x16 greyscale signature and inflates every score.
Measured on a 36-image batch: 6 pairs cleared 0.60 after compositing, only 2 before,
and four of the six were plainly different creatives. Judge the photographs, then look
at the flagged pairs yourself before calling anything a duplicate.

### The review is NOT optional when the client is waiting

Twenty ads once shipped after three of them had been opened, because the client was asking
for speed. They came back with malformed legs and the wrong shoes — both of which were
obvious in the first image opened afterwards. **Time pressure is the exact condition under
which this step gets skipped, which makes it the exact condition under which it matters.**
Opening twenty images costs a couple of minutes. Shipping twenty unopened costs the batch,
the client's trust, and the money to redo it.

If there is genuinely no time to review all of them, send the ones you HAVE opened and say
the rest are still being checked. Never send an unopened image.

**Never judge a pair having viewed only one of its images.** A whole concept once shipped
with the wrong product — amber glass instead of the real bottle — because only `var_01`
was checked and `var_02` was assumed fine.

| Check | Fails if |
|---|---|
| Product identity | Not the real product: wrong material, wrong closure, wrong motif, wrong colour |
| Product scale | Taller than ~⅓ of the nearest face, or dominating the frame |
| Pair distinctness | The two variations read the same at a glance |
| Grip | Where held, fingers don't visibly contact and press the surface |
| Integration | No contact shadow, or light not matching the scene |
| Copy | Garbled, misspelled or invented words in the overlay |
| **Anatomy** | Feet: five toes with nails, ankle bone visible, Achilles hollow present, heel in contact. Hands: five fingers, real pressure. **Count the limbs** — orphan feet and third arms drift in |
| **Footwear** | Right sex, right style, straps and fastenings actually present |
| **Pack lettering** | **Crop the pack and read it at 100 %.** Below ~50 % of frame height the model's label micro-copy garbles, and it is invisible at review size — a client once had to hand-fix three boxes |
| Sequence direction | A timeline or before/after runs the wrong way — state what changes between first and last panel |
| **Dead frame** | **What fraction of the frame carries no information?** Four of five candid shots in one batch gave 18-36 % to a blank out-of-focus foreground. Crop it and rebuild the square — never ship a third of an ad as a smear |
| **Paper props** | Receipts, prescriptions, invoices, forms and price labels print gibberish. Crop and read them. Wall posters at genuine background blur are usually fine |
| **Squareness** | `trim_uniform_border` leaves ragged ratios — 876x1024, 1007x1007. Meta's feed wants 1:1 and letterboxes anything else, so `pad_square()` every delivered file |
| One scene per image | The image shows a split-screen of both variations |

**Ship shock and pattern-interrupt concepts text-free as well as composited.** Two clients
running, on two different products, have taken such an ad straight from `production/` or
stripped the overlay by hand. The clean file already exists, so delivering both costs
nothing and saves them the edit.

Report every failure **to the user as a failure, before they find it** — never ship quietly,
never call a batch finished while knowing it isn't. Regenerate within the approved count if
budget remains; otherwise say plainly which images failed and what fixing them would cost.

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
