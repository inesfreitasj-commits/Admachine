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

## When a generation gets refused (exit code 6)

Usually a health/medical claim or an implied before/after body result. Soften the
claim to what the product page actually supports, drop any implied medical outcome,
and retry once. If it refuses again, swap the concept rather than fighting it.
