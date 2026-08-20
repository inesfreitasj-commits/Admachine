# Rejected patterns — read before writing any brief

Nine images the user rejected from a live ÉveilSens run, torn down. These are not nine
problems; they are five problems repeating. The frequency is the point.

## A. Oversized product — 5 of 9

Every one places the product **nearest the lens** — a counter front, a windowsill, a
foreground nightstand, a hand pushed toward camera.

Depth drives scale, not wording. "No more than 12% of frame height" loses to perspective
every time.

**Rule:** the product sits in the MIDDLE DISTANCE. Never the closest object in frame.
Don't even propose a foreground-product shot.

## B. Garbled label text — 6 of 9

`Augmentez votre plaiir. Profiloz do l'orgasmo.` The reference photo is low-resolution and
the model reproduces blur faithfully, as confident-looking nonsense words.

**Rule:** spell every label line out in the prompt, and say the reference is low-res and
must not be copied as blur. Where the product is small in frame the text degrades anyway —
so either keep it large enough to render or compose so the label isn't the focal point.
**Ask the user for a sharper packshot; it removes this defect entirely and costs nothing.**

## C. Wrong product — 3 of 9, the most damaging

- One pair rendered an **amber glass bottle with a black rubber pipette dropper**. Not the
  product. Its sibling in the same pair rendered the correct white squeeze bottle — so the
  product changed *within one concept*.
- One shot rendered the label motif as a **pink lotus flower** instead of the petal-and-
  droplet mark.
- One rendered the body **cream/ivory** and the carton pale pink instead of bright white
  and hot magenta.

**Root cause:** the words *dropper*, *serum*, *pipette*, *oil bottle* pull hard toward the
stock amber-glass-serum form that dominates training data for cosmetics. A blurry reference
does not outweigh that pull — the model treats a soft reference as loose inspiration, not
a spec.

**Rules:** never write *dropper*, *serum bottle*, *pipette* or *oil bottle* in a scene
description. Always write *squeeze bottle with a long tapered conical nozzle*. Carry an
explicit exclusion list in every prompt:
```
NEVER: amber or brown glass, a pipette or rubber-bulb dropper, a black cap, a lotus or
multi-petal flower, a cream or ivory body, a pump.
```

## D. Near-duplicate pairs — 2 of 9

Two doctor shots: same composition, same pose, same framing, same copy. One is wasted spend.

**Rule:** the variation axis must be visual. `scripts/qc_batch.py` catches this
mechanically before delivery.

## E. A grip that doesn't grip — 2 of 9

Fingers hover around the bottle without contacting it, so it reads as floating rather than
held.

**Rule:** require visible fingertip contact with slight indentation where the fingers press.
If a convincing grip can't be guaranteed, put the product at mid-distance instead.

## F. The variation rendered INSIDE one image

One brief said "same layout and text, but set on a bedside table". The model produced a
single split-screen frame containing *both* versions — an unusable ad.

**Rule:** each variation is a standalone prompt describing one complete scene. Never phrase
a variation as a diff against its sibling ("same as before but…"); the model may render the
comparison instead of the variant.

---

## The cause behind four of the five

**The reference photo is too low-resolution to function as a specification.** It is why the
label garbles, why the motif drifts to a lotus, why the body drifts to cream, and why the
form drifts to amber glass. Prompt wording is a workaround for a bad input, and workarounds
leak.

Ask for a sharp packshot early and plainly. It is worth more than any further prompt
engineering.

## The process failure that let these ship

The pair containing the amber-glass bottle was declared a keeper **after viewing only one
of its two images.** A pair is not checked until every image in it has been looked at.

---

# Worked example 2 — nine rejected ArtériVie ads

A second live batch, nine rejections, one dominant cause.

| Ad | Note from the client | Root cause |
|---|---|---|
| native feet | Feet should be **swollen** to show poor circulation | Symptom described as a category, not shown as evidence |
| x-ray | Should be **just a picture of an x-ray** — staged version looks fake | Artefact staged instead of shown |
| pharmacy shelf | Needs **competitor products with higher prices**; must look like a **real** shelf | "Generic unbranded" written into the prompt |
| doppler scan | Should be a **man** viewing his results | Audience mismatch on a men's product |
| comparison | **Too simple**, colours too simple | "Clean" read as "flat" |
| before/after | Artery good, **the people behind it make no sense** | Artefact staged instead of shown |
| pharmacy counter | Good, but **our product isn't in it** | Retail scene with no product and no absence line |
| doctor + model | Good, but **zoom to hands and model only** | Crop too wide |
| UGC man | **Wrong product** in his hands | Product drift in a person-scene |

## The one sentence that covers almost all of it

**The idea was described instead of the evidence.** A staged x-ray instead of the x-ray.
A clinical category instead of a swollen foot. "Generic boxes" instead of a real shelf.
"Clean" instead of a designed image. Every prompt was accurate and insufficiently specific.

**Specificity is what makes an image look real, and looking real is what makes it convert.**

## The cheapest correction available

**Crop tighter.** It removes the staging that caused the fakeness AND gives the product more
pixels so its label renders faithfully. Three of these nine are fixed by cropping in and
nothing else.
