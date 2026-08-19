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

## When a generation gets refused (exit code 6)

Usually a health/medical claim or an implied before/after body result. Soften the
claim to what the product page actually supports, drop any implied medical outcome,
and retry once. If it refuses again, swap the concept rather than fighting it.
