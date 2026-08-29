#!/usr/bin/env python3
"""ÉveilSens round 2, v2 — composite pass against the CORRECTED reference.

v1's assets/product.png turned out to already have garbled label text baked in (traced back
to a straight page-slice of the client's own sales-page PDF), so every v1 render was
faithfully copying an already-broken reference. The client supplied a clean product photo
(assets/product_v2.png); regenerating against it fixed the label on most of the 16 concepts
outright — no blur/patch needed, which also removes the "visible blur with text on top of
it" look flagged on the v1 delivery.

A handful of concepts still needed 1-2 regeneration passes (production_v2/*.v2a.png,
*.v2b.png are the earlier failed attempts, kept for the record) before the label rendered
correctly and on-brand. Nothing in this v2 batch needed the blur+retype code fix at all.

Run: python3 compose_v2.py [name ...]
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer

SRC, OUT = "production_v2", "final_v2"
os.makedirs(OUT, exist_ok=True)
MAGENTA = (0.66, 0.04, 0.42)

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn

def passthrough(n):
    shutil.copyfile(p(n), o(n))

CLAIM1 = "Augmentez votre plaisir."
CLAIM2 = "Profitez de l'orgasme."

def _fit_size(c, text, key, target_w, cap):
    """Largest size (up to cap) whose rendered width stays within target_w."""
    ref = 0.05
    w = c.measure(text, key, ref)
    fitted = target_w / w * ref if w > 0 else cap
    return min(fitted, cap)

def fix_label(name, rect, cap_size=0.05, radius=0.035, width_frac=0.88, feather=0.14):
    """Blur the still-garbled claim line and composite the correct claim, auto-sized to fit
    inside the rect's own width. Only needed on the 2 of 16 concepts (LEG3, DR1) where even
    the corrected reference didn't produce clean text after two regeneration passes — the
    bottle shape and label layout are correct on both, only this one line needed a code fix."""
    c = Composer(p(name))
    x0, y0, x1, y1 = rect
    c.soften(x0, y0, x1, y1, radius=radius, feather=feather)
    target_w = (x1 - x0) * width_frac
    s1 = _fit_size(c, CLAIM1, "sans-italic", target_w, cap_size)
    s2 = _fit_size(c, CLAIM2, "sans-italic", target_w, cap_size)
    size = min(s1, s2)
    gap = size * 1.5
    cy = (y0 + y1) / 2
    ybase = cy - gap / 2
    cx = (x0 + x1) / 2
    c.centered(ybase, CLAIM1, key="sans-italic", size=size, color=MAGENTA,
               shadow=False, center_on=cx)
    c.centered(ybase + gap, CLAIM2, key="sans-italic", size=size, color=MAGENTA,
               shadow=False, center_on=cx)
    c.save(o(name))


@job
def LEG3_nightstand_reach():
    fix_label("LEG3_nightstand_reach", (0.697, 0.416, 0.783, 0.465))

@job
def DR1_gynecologue():
    fix_label("DR1_gynecologue", (0.249, 0.384, 0.347, 0.428))


# ---------------------------------------------------------------- pass-through (clean as generated)
for _n in ("LNG1_arched_back", "LNG2_side_profile_gasp", "LNG3_sheets_macro",
           "LNG4_morning_relaxed", "LNG5_couple_embrace",
           "LEG1_crossed_legs_bed", "LEG2_bathtub_edge", "LEG4_thigh_closeup",
           "PRD1_pink_checklist", "PRD2_bundle_pricing", "PRD3_ingredients_flatlay",
           "PRD4_hand_holding_bottle", "DR2_hormones_comparison", "LNG6_hands_sheets"):
    def _pt(n=_n): passthrough(n)
    _pt.__name__ = _n
    job(_pt)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
