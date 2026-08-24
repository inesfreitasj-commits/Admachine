# Writing Nano Banana Pro prompts for static ads

Read this before writing the generation prompts in step 7.

## Prompt skeleton

Every prompt has the same five blocks, in this order:

```
1. FORMAT     "A single flat static advertisement image, 1:1 square, designed for
               a paid social feed placement."
2. SCENE      Subject, setting, composition, lighting, camera angle, props.
3. PRODUCT    The visual description from assets/product-visual.md, verbatim, plus:
              "The product must exactly match the attached reference photo — same
               bottle shape, same cap colour, same label typography and layout, same
               brand colours. Do not redesign the packaging."
4. TEXT       Every overlay line in exact quotes, with position and relative size.
5. STYLE      Palette, mood, finish, and what to avoid.
```

## What actually moves the needle

- **Quote the overlay text exactly.** `Large bold white text across the top reading
  "THEIRS: 4 pills a day"` beats "add a headline about pill count". Unquoted text gets
  paraphrased or garbled.
- **Cap the on-image copy.** Two or three short lines render cleanly. A paragraph
  comes back as gibberish letterforms.
- **Name the camera.** "Shot on a phone, slightly overhead, natural window light"
  produces a very different ad from "studio product shot, seamless white sweep, soft
  box from the left". The variation axis usually lives here.
- **Say where the product sits.** "Bottle at lower right, front label fully visible,
  occupying about a quarter of the frame."
- **Anchor the palette** to the brand colours you pulled from the real photo, by name.
- **State the negatives.** "No watermark, no stock-photo logos, no extra text beyond
  what is specified, no distorted lettering, no duplicate bottles."

## Per-framework scene patterns

| Framework | Visual construction |
|---|---|
| **US VS THEM** | Hard vertical split. Their side desaturated/cluttered/grey; your side bright and clean with the product. Label both halves. Contrast does the persuading. |
| **BOLD CLAIM** | One product hero, one enormous claim in the top third, minimal everything else. Claim must be page-supported. |
| **Before & After** | Two panels, identical framing and lighting, one variable changed. Timestamp or day-label each panel. Never fake medical results. |
| **TESTIMONIAL** | Quote card or review-screenshot look. Short quote in quotation marks, name + descriptor underneath, product small in frame. Reads as a real person, not a brand. |
| **Comparison chart** | Checkmark/×  grid, your column highlighted. Rows are page-supported attributes only. |
| **Problem/Solution** | Top half tension (mess, fatigue, clutter), bottom half resolution with the product. Single arrow or divider between them. |

## Building the variation pair

`var_01` and `var_02` differ by **one axis only**. Pick one:

- **Camera angle** — flat-lay overhead vs. eye-level three-quarter
- **Overlay wording** — same claim, two phrasings ("4 pills a day" vs. "4x the pills")
- **Background** — bathroom counter vs. plain studio seamless
- **Model presence** — hand holding the product vs. product alone

Everything else — scene, product placement, palette, other text — stays byte-identical
between the two prompts. That is what makes the pair a clean A/B read; if two things
change, the test tells you nothing.

## Low-resolution reference photos

The model copies what it sees, blur included — a soft reference produces packaging
covered in plausible-looking nonsense words. Whenever label text matters, name it:

```
LABEL TEXT (the attached reference is low-resolution and its label text is blurred —
render these exact words crisply, do not copy the blur):
- brand mark in the oval near the top: "<Brand>"
- centred copy beneath it, two lines: "<line one>" then "<line two>"
- band at the bottom, small white text: "<strapline>"
All label lettering must be sharp and correctly spelled. No invented or garbled words.
```

Check the result: at hero size the label should be readable. Where the product sits
small in frame the text stays fuzzy, which is fine for feed but wrong under zoom.

## Two blocks worth pasting into every prompt

**Scale** — without it a palm-sized bottle renders as a 500 ml one:
```
SCALE: a small 20 ml bottle, roughly the size of a human palm — about as tall as an
adult hand is wide. No more than 15% of the frame height; never dominating the
composition. When held, it sits in one hand with the fingers wrapping most of its height.
```
Most reliable when a hand or a nearby object supplies scale; least reliable in a bare
product shot, so check every result.

**Colour lock** — stops the product drifting between images in a batch:
```
COLOUR (exact, no substitutions): body OPAQUE BRIGHT WHITE — not cream, not ivory, not
beige. Label gradient HOT MAGENTA (#D6006E) at the edges fading to near-white behind the
centre text. Solid HOT MAGENTA band at the bottom. Nozzle translucent natural polyethylene.
The motif is a SINGLE stylised line-drawn petal with a droplet — never a lotus, never a
multi-petal flower, never a leaf.
```
Colour holds well. The motif is stubborn — the model tends toward a generic lotus
whatever you say, so treat brand marks as something to check rather than trust.

## Products held in someone's hand

The most reliable way to get a giant product is to describe its size **relative to the
hand**: "fingers wrap around it", "no taller than her palm". The model satisfies those by
enlarging the HAND, because the product is the subject and subjects get drawn big. The
anchor becomes the thing that distorts.

Anchor to the FACE instead, name a small-object grip, and guard the hand:
```
The bottle is roughly ONE THIRD the height of the person's face, chin to hairline — about
the size of a cigarette lighter.
Held LIGHTLY BETWEEN THUMB AND FOREFINGER, the way you would hold a lighter or a pen — NOT
gripped in a closed fist. The fingertips visibly touch and press against its surface, so the
grip reads as a real grip.
THE HAND MUST BE NORMALLY PROPORTIONED to the head and body. Do NOT enlarge the hand.
```
Faces are rendered with dependable human proportions, so the model shrinks the prop rather
than distorting the face.

## Distance from the lens beats every size instruction

The real driver of product scale is not the wording, it is **where the product sits in
depth**. Anything near the camera gets enlarged by perspective, and no "no more than 12% of
frame height" overrides it — including a product resting on furniture, if that furniture is
the nearest thing to the lens.

- **Reliable:** product in the MIDDLE DISTANCE — a nightstand beside the subject, a
  windowsill, a counter behind them. Comes back correctly sized.
- **Unreliable:** product on the nearest surface to the camera, however emphatically you
  ask for it to be small.

Say where the product sits in depth, not just how big it should be.

## When the hero is an artefact, SHOW the artefact

A scan, an x-ray, a specimen, a diagram, an anatomical model, a document — these are
already compelling. Wrapping one in a staged scene makes it read as fake, because the
staging is the invented part.

- **Crop to the artefact.** Full frame, nothing else competing.
- Background must support it or be neutral. **Unrelated people are the fastest way to make
  a real-looking artefact look staged.**
- No lighting drama, no models admiring it, no room around it.

This is not a native-only rule. It applies to any concept built on a medical or documentary
object, in any bucket.

## Crop tighter — the first move when an image is failing

Tightening the crop fixes two different failures at once:

1. **Fakeness** — removes the irrelevant scene that made it look staged.
2. **Product and label fidelity** — the pack occupies more pixels, so its label renders
   better.

When an image is not working on either axis, crop in before adding anything. "Zoom in to
just the hands and the model" is almost always the right note.

## Product drift happens in person-scenes, not product-scenes

Sorting a real batch by whether the pack rendered correctly:

| Rendered correctly | Drifted to a different product |
|---|---|
| Studio product shot | Held in someone's hand in a kitchen |
| Overhead flat-lay | Prop inside an editorial scene |
| Hero on a shelf | |

When the pack is the **photographic subject** it renders faithfully. When it is a **prop
beside a person**, the model spends its attention on the person and rebuilds the pack from
memory. **An attached reference image does not prevent this.**

- Person-holding and person-scene shots carry the highest drift risk — verify every one.
- Crop tight so the pack is large in frame.
- Where label fidelity really matters, choose a product-hero composition instead.

## Never write "generic" or "unbranded"

Ask for "generic unbranded boxes" and the result is a shelf that looks like nothing, which
reads as fake. Describe the real thing instead: for a pharmacy shelf, dense boxes, printed
rail price labels, category signage, colour variety, slightly untidy facing.

For comparison ads, invented look-alike local brands with **visible prices higher than
yours** — the viewer doing that arithmetic is the entire mechanism of the concept.

## Detect where to composite — never hardcode coordinates

Text composited at positions measured by eye off one render lands wrong, because the model
places props differently every generation. Prices eyeballed onto a shelf came out floating
beside their price stickers rather than printed on them.

`scripts/label_boxes.py` finds blank light-coloured label rectangles — price stickers,
shelf talkers, blank cards — and returns their boxes so text can be centred inside each one
and auto-sized to fit.

- Generate the surface **blank** (blank stickers, blank cardboard), then composite onto it.
- Detect the target, don't guess it.
- If the detector returns 0 boxes, sample one row of pixels across the image and read the
  real threshold off the numbers rather than guessing again. A band that includes the
  darker shelf edge below the labels will find nothing.
- When a surface is too low-contrast to detect reliably, **rebuild it** — repaint the strip
  and draw clean labels on it. Faster than over-tuning a detector for one image.

## Sizing composited text for a feed, not for a screen

Text added in code is easy to make too small, because it looks fine at full size on a
desktop and is unreadable on a phone in-feed. An auto-fit routine makes this worse: it
happily shrinks type to whatever fits the box it was given.

- Size for the **thumbnail**, not the full-resolution file. If it isn't comfortably
  readable when the whole image is about 400px wide, it is too small.
- If the copy doesn't fit at a readable size, **cut the copy** — never shrink the type.
  Three short lines beat three long ones every time.
- Give the shortest, most important line the **largest** size. On a sign or a card the
  timeframe or the number should dominate.
- Map the usable area honestly: a held sign is only full-width where nobody's hands are.
  Give upper lines the full width and lower lines a narrower box.
- Always look at the result before delivering. Measured widths tell you it fits; only
  looking tells you it reads.

## When a generation gets refused (exit code 6)

Usually a health/medical claim or an implied before/after body result. Soften the
claim to what the product page actually supports, drop any implied medical outcome,
and retry once. If it refuses again, swap the concept rather than fighting it.


## Never say "both arms" without pinning the camera

A brief that said *"both arms are raised out to the sides at shoulder height"* produced
an image with **two people in it**. The phrasing only works from a frontal view; the
model placed the subject side-on, so both of her arms ran off the same edge of the
frame and the upper one read as a second person standing behind her. The client spotted
it before the QC pass did.

State the number of limbs allowed in the frame, not the pose of the body:

> ONLY ONE ARM APPEARS ANYWHERE IN THE FRAME — the arm nearest the camera. Her other
> arm hangs down behind her body and is COMPLETELY HIDDEN. There must be exactly ONE
> shoulder, ONE upper arm, ONE elbow and ONE forearm in the whole picture.
> CRITICAL — ONE PERSON ONLY: no second person, no arm entering the frame from any
> edge, nobody standing behind her.

The same trap applies to *both hands*, *both legs*, *both feet*, and to any second
figure implied but not described — a partner, a passer-by, a reflection. Count the body
parts you want and say the number.

## Match a supplied reference on its MATERIALS, not its subject

When the client sends a photo as a style reference, the thing to reproduce is the
material world in it, described concretely: iodine-stained skin, blue non-woven surgical
drapes filling the background, black marker with cross-hatched ladder edges and
handwritten centimetre annotations, hard overhead theatre light. Naming those got a
near-exact match first time. Writing "like a surgical photo" would not have.


## In a fixed-format series, the duplicate usually comes from YOUR overlay

A batch of eight ads in one client's pack format came back with 27 of its 28 pairs over
the duplicate gate. The obvious diagnosis — the artwork is too samey — was wrong, and
measuring the two stages separately is what proved it:

| | pairs over gate | median r |
|---|---|---|
| the raw generated art | **1 of 28** | 0.204 |
| the same art after compositing | **4 of 28**, max 0.746 | 0.009 |

Compositing pushed one pair from **r = 0.094 to r = 0.704** — it *added* 0.61 of
similarity. The cause was an identical navy CTA bar and an identical top-left headline
block on every single ad. On a 16×16 greyscale signature that shared furniture is a large
constant shape, and it swamps everything the artwork is doing.

**So measure both stages before blaming the pictures:**

```python
raw  = {n: q.signature(f"production/{n}.png") for n in names}
comp = {n: q.signature(f"final/{n}.png")      for n in names}
```

If `comp` is worse than `raw`, the overlay is the problem and the fix is free.

**Vary the furniture the way the client's own winners already do.** In that campaign
winner 1 carried the CTA bar with a left-set headline and winner 2 carried no bar with a
centred headline — which is part of why *their* two winners score r = 0.031. Putting the
bar on three of eight and centring the headline on two dropped the whole 20-ad batch to
**0 of 190 pairs over gate**, with no extra generation.

Design the lockup helper for this from the start: make the CTA bar, the wordmark, the
headline alignment, the type sizes and the copy column all optional parameters, not
constants baked into the function.

## Distinctness lives in the large shapes

The related trap, in the same batch: eight ads with the same pack, at the same size, in
the same place, on the same white ground, each with a different small illustration in the
lower-left corner. The detail changed; the picture did not.

What actually separates two ads in one format is the **dominant mass, the ground colour,
and the pack's position and scale** — an enormous element cropped by the frame edge, a
mirrored layout with the pack on the other side, a top-down flat lay, a photographic
subject where the others are vector, a band across the middle with the pack shrunk to the
bottom. Rebuilding on those axes took the same eight arguments from a 0.825 median to
0.204 in the raw art.

**Never brief a series as "same layout, different illustration".** Brief each one as a
different picture that happens to share a brand system.


## Check which way a sequence runs, not just its labels

A three-stage timeline shipped showing a tooth getting **steadily worse** — clean, then
filmed, then heavily encrusted — under the labels JOUR 0 / 24 H / 48 H, with the product
pack sitting at the end of the arrow. The literal message was *"48 hours with this product
and your dog's teeth look like this."* The client spotted it; the QC pass did not.

Every individual element checked out, which is exactly why it survived: the headline was
verbatim from the funnel (*"la plaque dentaire peut se transformer en tartre en seulement
48 heures"*), the stage labels were in the right order, the illustration was well drawn.
**The direction was the benefit reversed**, and nothing in the checklist looked at
direction.

Before shipping any timeline, before/after, or multi-panel sequence, say out loud what
changes between the first panel and the last, and confirm it is the outcome the product
sells. If the product removes something, the last panel has less of it.

## One number, one meaning per account

The same batch used **48 h** as the payoff in eight ads and as the speed of deterioration
in one. A number that means "improvement" and "decay" in the same ad account weakens the
claim the whole campaign rests on. Find the direction the funnel uses — here the hero, the
sidebar, the FAQ and both winning ads all used 48 h as the payoff — and hold it everywhere.

Problem-agitation ads are still fine; they just have to agitate with a *different* number,
or with no number at all.

## Swapping panels is free — regenerating is not

That timeline was fixed without spending anything, because flat-ground vector panels are
separable. Measure the groups by scanning for non-background columns, cut each to its own
file, blank the slots to the sampled background colour, and paste them back in the order
you want:

```python
cream = tuple(c/255 for c in pix.pixel(int(0.02*W), int(0.55*H)))   # sample, never guess
for a, b in GROUPS:                      # blank
    page.draw_rect(fitz.Rect(a*W-2, y0-2, b*W+2, y1+2), color=None, fill=cream)
for src_i, dst_i in ((2, 0), (1, 1), (0, 2)):   # paste back reordered, centred
    ...
```

Check the group widths first — if they are within a few pixels of each other, centring each
cut in its destination slot leaves no visible seam.


## Never brief a pack as "small" — the label garbles and the client has to fix it

A client had to hand-amend the product box on three delivered ads: "NETTOYANT DDNTAIRE",
"AKTY-TARTRE", "POUN CHIENS". The cause was purely mechanical and maps exactly onto how big
the pack was briefed:

| Pack height in frame | Label |
|---|---|
| **28–30 %** (briefed "SMALL and CENTRED along the bottom") | **garbled — every one** |
| 55–70 % | clean — every one |

It survived QC because the ads were reviewed whole, at reduced size, where garbling is
invisible. **It only shows at 100 %.**

Three rules follow:

1. **Floor the pack at 50 % of frame height** in any brief where the pack appears. If a
   layout seems to need a smaller pack, change the layout.
2. **Where a layout genuinely needs a small pack, composite the real packshot** rather than
   letting the model draw it. On a flat studio ground, pasting `assets/product.png` in is
   exact, free, and removes the entire class of error:

   ```python
   c = Composer(p(name))
   c.image(x0, y0, x1, y1, "assets/product.png")   # fractions, keeps the real lettering
   ```

3. **QC the pack at 100 %, as its own check.** Crop the pack region and read the label the
   way the duplicate gate is run separately — looking at the whole ad will not catch it:

   ```python
   # enlarge just the pack region and open it with Read
   pg.insert_image(fitz.Rect(-x0*Z, -y0*Z, (-x0+W)*Z, (-y0+H)*Z), filename=src)
   ```

The same applies to any small in-scene lettering the model draws — shelf labels, signage,
screens. Below roughly half the frame, assume it is wrong until you have read it enlarged.

## Circle the thing you want looked at

A client supplied, as a reference, a greyscale dog's mouth with the offending tooth ringed
in red marker. It is a cheap and very effective answer to "can you tell what this is in half
a second" — and it composites in code for nothing:

```python
c.page.draw_oval(fitz.Rect(...), color=RED, width=0.008 * c.H, fill=None)
```

Worth testing on any macro or clinical image where the subject needs finding.


## Never brief the ABSENCE of an anatomical landmark

A batch of swollen-leg ads came back with legs the client called "not normal". The cause was
not the model. It was this line, which I had put in a shared block on nearly every prompt:

> "the whole ankle reads as a **smooth continuous column with no visible hollow** beside the
> tendon"

That is an instruction to delete the medial malleolus and the Achilles hollow — the two
landmarks that make a leg read as a leg. The model obeyed exactly, and every ad the block
touched came back with smooth featureless tubes for legs.

**Describe a symptom by what it ADDS, never by what it removes.** Swelling is flesh spilling
over a sandal strap, a shiny stretched look on the tightest part, a sock groove indented with
the flesh bulging above and below it, a thumb-press dent that stays. The landmarks remain,
softened. The same applies to wasting, sagging, inflammation and every other deformity: name
what appears, never what disappears.

## A feet block, and it is stricter than the hands block

Feet are worse than hands. Use this wherever a bare foot is in frame:

> FEET AND ANKLES — RENDER THE ANATOMY, DO NOT REMOVE IT: exactly five toes, big toe clearly
> largest, each with a real toenail; the heel broad and in proper contact with the surface;
> the Achilles tendon visible as a cord up the back of the ankle; the ANKLE BONE ON THE INNER
> SIDE remains a visible rounded bump and the small hollows either side of the Achilles remain
> present even when puffy. Real skin: pores, freckles, sun spots, fine thread veins.

Also cap the limb count explicitly in the tail — "exactly the number of legs and feet
described, belonging to one person" — because orphan feet drifted into two ads in that batch.

## Barefoot shots are candid and environmental, never studio

In the same batch, four foot ads came out right and three came out wrong, and the split was
entirely about framing:

| Worked | Failed |
|---|---|
| One leg, side on, large in frame, resting on a real chair / footstool / coffee table, shot from the subject's own eyeline, real household clutter in shot | Front-on, standing, both feet together, small in frame, on a seamless studio ground |

The model has seen millions of real casual foot photographs and comparatively few clean
studio foot renders, so studio framing pulls it toward the idealised stock leg — which has no
ankle bone. **Shoot bare feet the way a person photographs their own.**

## Name footwear exactly: sex, style, strap, fastening

"A plain leather shoe" returned **men's brown lace-up Oxfords on a woman in a summer dress**.
The brief has to carry the whole specification:

> a WOMAN'S FLAT SUMMER SANDAL — tan leather sole, a wide band across the toes, and a proper
> ANKLE STRAP WITH A SMALL METAL BUCKLE at the side. Not a shoe, not a lace-up, not a men's
> brogue, not a slip-on, not a trainer.

The same batch proved the model renders that perfectly when asked — the failure was entirely
in the vagueness of the brief.
