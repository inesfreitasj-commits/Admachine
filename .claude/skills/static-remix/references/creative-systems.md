# Which creative system am I in?

Read this before writing a single concept. Two products in the same market can win on
opposite mechanics, and building one in the other's register kills it.

Diagnose it from the client's winners — not from the category, not from the last client.

| | **Claim-led** | **Editorial-test** |
|---|---|---|
| What persuades | The mechanism and the number | Third-party authority: it was tested and it won |
| Register | Dark, medical, high-contrast, urgent | Raw phone photos, plain type, magazine furniture |
| Product claims on the hook ad | Loud | **Often none at all** |
| Price | Proof it is cheaper | Context, and the product is happily mid-table |
| Typical hero | Diagram, cutaway, x-ray, organ, before/after | An unretouched close-up of an ordinary body |
| Who is talking | The brand | A named expert or a publication |
| Worked example | ArtériVie (FR cardiovascular) | Ferméa (FR body oil) |

## The trap

The same *format* means opposite things in each system. A pharmacy-shelf price
comparison in a claim-led system wins by being **cheapest** — your column beats theirs.
The identical shot in an editorial-test system wins by being **ranked**, and the product
sitting fourth of five on price is the whole point: it proves the ranking was not bought.

Reproducing a shelf ad without asking which of those it is produces a technically
competent ad that argues the wrong thing.

## Diagnosing it in two minutes

1. Read the hook ads' copy. Does it claim anything about the product? If not, you are in
   an editorial-test system and the persuasion is authority, not benefit.
2. Find where the campaign's furniture comes from. `VAINQUEUR DU TEST 2026`, a tricolore,
   a `TEST PRODUIT` badge, "we tested 16 and here are the 5 best" — all of that traces
   back to a line in the advertorial. Find that line; it is the campaign's spine.
3. Check the product's own price position on the shelf ad. Cheapest → claim-led.
   Mid-table → editorial-test.

## Reproducing an editorial-test lockup

Measure it off the client's own winner rather than eyeballing it. Crop the winner's
regions, enlarge 3x, and read the geometry off in source pixels, then express everything
as a fraction of the frame so it holds at any output size. The lockup for Ferméa's
campaign — flag roundel, two-line kicker, red badge, light line, bold underlined line —
is already implemented as `hook_lockup()` in `scripts/compose_text.py` with the
fractions measured off a real 742x742 winner.

Then generate the photograph **with no text at all** and composite the lockup on top.
The winners' text is a flat graphic overlay; asking the model to draw it produces
garbled French and costs money to retry.

## Read the whole funnel before writing anything

Every tile, not a sample. Ingredients were once invented into an ad because only two of
four sales-page tiles had been read. Reading all of them on the next product also turned
up a comparison table headed with a *different brand's name* and score bars in Swedish
inside a French article — both of which would have been repeated into ads as fact.

When two pages of the same funnel contradict each other, record both, pick the sales
page's version, and tell the client. Do not average them and do not pick the bigger
number.
