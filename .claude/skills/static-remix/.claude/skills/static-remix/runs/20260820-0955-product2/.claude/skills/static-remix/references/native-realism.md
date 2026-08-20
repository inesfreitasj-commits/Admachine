# Native realism — making generated ads look local, real and not AI

A generated ad fails the moment the viewer clocks it as generated or as foreign. This file
is about the details that give it away.

## Localise the SETTING, not just the language

Translated copy over a generic scene still reads as an import. The scene itself has to
belong to the market.

Work through this list for every scene with a location or a person:

| Element | Get it right by |
|---|---|
| **Buildings** | Name the country's actual architecture. A French hospital is not a US hospital: name the era and materials, not just "a hospital" |
| **Signage** | Any sign in frame must be in the local language and match local conventions |
| **People** | Name the nationality and let features, hair and grooming follow. Age the person to the actual buyer, not to a stock model |
| **Clothing** | Must match the LOCAL SEASON AND TEMPERATURE at the time of the run — see below |
| **Interiors** | Local retail and medical interiors differ markedly by country: fittings, layout, colour, branding conventions |
| **Documents & props** | Prescriptions, cards, receipts, packaging conventions are country-specific |
| **Money** | Local currency, local price formatting and decimal conventions |

## Season and temperature — check, do not assume

**Always resolve the current season in the target market before writing scenes**, and dress
people for it. Get today's date, work out the season in that hemisphere, and let clothing,
light and outdoor context follow.

A person in a heavy coat in an August ad for a Northern-Hemisphere market instantly reads as
stock or as AI. So does a summer terrace scene in January.

Also carry it into the light: summer gives long bright evenings and hard sun; winter gives
low flat light and early dark. State it in the prompt.

This is a rule to re-derive every run, never a fact to hardcode.

## The AI tells, and how to beat each one

| Tell | Fix in the prompt |
|---|---|
| **Hands** | The single biggest giveaway. Fingers must contact and press surfaces with visible indentation, correct count, normal proportion to the head. Check every held shot |
| **Plastic skin** | Ask for natural skin texture, visible pores, fine lines, slight asymmetry, real age. Never "flawless" or "perfect" |
| **Floating products** | Contact shadow, matching light direction and colour temperature, matching depth of field |
| **Impossible text** | Quote every on-image line exactly; keep it short; spell out label copy |
| **Too-perfect composition** | For UGC, ask for phone-camera imperfection: slight motion blur, uneven light, a cluttered real room, off-centre framing |
| **Uncanny teeth and eyes** | Prefer closed mouths or slight smiles over broad grins; avoid direct-to-lens stares in UGC |
| **Stock-photo energy** | Name a specific real moment rather than an emotion. "Reading the label at the kitchen table before dinner" beats "a happy man" |

## UGC specifically

UGC must look like it was taken by the person, not for them:
- Phone camera, natural room light, no studio setup
- Slightly off-centre, slightly imperfect framing
- Real domestic clutter in shot
- Ordinary clothing appropriate to the season
- The product held casually, not presented

If it looks art-directed, it is not UGC and will not perform as UGC.

## Native ads — what the client's 17 proven examples actually look like

Two sub-types, one shared DNA.

**Clinical / scientific, high production.** MRI scanner room. Thermal-imaging comparison.
False-colour anatomical scan. Striking, clean, science-looking.

**Raw phone-camera, deliberately unpolished.** Tweezers pulling something from an ear.
Two inhalers on a granite worktop. Feet wrapped in aluminium foil on beige carpet. Bad
light, amateur framing, domestic clutter, low resolution.

**Every single one shares this:**
- **No text overlay. None at all.**
- **No brand, and no shot of the product being sold.** Where a product appears it is the
  viewer's own existing medication, not the advertised item.
- **Curiosity is the whole mechanism** — why are her feet in foil, what is in his ear.
- Often mildly uncomfortable, taboo, or simply odd.

### Polish is the enemy

A premium style block — *"premium direct-response advertising, warm, cinematic,
thumb-stopping"* — GUARANTEES failure on a native concept, because it produces a glossy
ad, which is the one thing native must not be. Never apply it to a native brief.

Use the inverse:
```
STYLE — CRITICAL, THIS IS NOT AN ADVERTISEMENT:
Looks like a photo an ordinary person took on their phone and posted. Consumer smartphone
camera. Harsh on-camera flash or flat overhead domestic lighting. Slightly wrong white
balance. Mundane real surfaces and background clutter. Slightly off-centre framing. Mild
blur or softness is GOOD.
Do NOT make it beautiful. Do NOT art-direct it. Do NOT light it professionally.
ABSOLUTELY NO TEXT anywhere. NO logos, NO branding, NO packaging of the advertised brand.
```

Models resist making an image look bad — check the result and regenerate if it comes back
glossy. When it works the payoff is large: one brief asking for a thermal image produced it
displayed *on a phone screen held in a hand*, which is more native than what was asked for.

## Native editorial specifically

To read as an article rather than an ad:
- Match a real local publication's layout conventions
- Journalistic headline register, not ad copy
- A byline, a date, body text that behaves like body text
- **Generate the photograph, then composite the article furniture and text in code.** Image
  models turn dense small text into gibberish; code gives pixel-perfect local-language type
  at zero API cost. This is the difference between a native ad that works and one that
  is obviously fake.
