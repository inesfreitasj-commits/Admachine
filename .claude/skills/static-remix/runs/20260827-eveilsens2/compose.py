#!/usr/bin/env python3
"""ÉveilSens round 2 — composite fixes in code.

The label's own script line ("Augmentez votre plaisir. Profitez de l'orgasme.") garbled on
essentially every one of the 16 raw renders — a different word broken each time, never
correct together, consistent with this being a genuinely hard piece of text for the model
on this label's cursive-script styling, not per-image bad luck. Rather than regenerate 12+
images with no guarantee of a clean roll, every image where that line is legible gets it
blurred with Composer.soften() and the correct two-line claim composited back in code
(sans-italic, the closest available face to the label's own script — correct and legible
matters more than a perfect font match). Images where the bottle is small or already
out-of-focus (LNG1, LNG2, LNG4) are left as pass-through — the text there is illegible at
normal viewing size regardless, same as a real photo's soft background label.

Run: python3 compose.py [name ...]
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
MAGENTA = (0.66, 0.04, 0.42)

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def passthrough(n):
    shutil.copyfile(p(n), o(n))

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn

CLAIM1 = "Augmentez votre plaisir."
CLAIM2 = "Profitez de l'orgasme."

def _fit_size(c, text, key, target_w, cap):
    """Largest size (up to cap) whose rendered width stays within target_w."""
    ref = 0.05
    w = c.measure(text, key, ref)
    fitted = target_w / w * ref if w > 0 else cap
    return min(fitted, cap)

def fix_label(name, rect, cap_size=0.05, radius=0.026, width_frac=0.88, feather=0.14):
    """Blur the garbled script line and composite the correct claim, auto-sized to fit
    inside the rect's own width (with a margin) so it can never spill outside the blur.
    feather is lowered from soften()'s 0.28 default because the rect is drawn tight around
    the text: a wide feather zone would leave the blur under-strength right where the
    garbled text actually sits, and it would show through."""
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


# ---------------------------------------------------------------- label-fix jobs
@job
def LNG3_sheets_macro():
    fix_label("LNG3_sheets_macro", (0.40, 0.48, 0.70, 0.76))

@job
def LNG6_hands_sheets():
    fix_label("LNG6_hands_sheets", (0.56, 0.63, 0.84, 0.87))

@job
def LEG1_crossed_legs_bed():
    fix_label("LEG1_crossed_legs_bed", (0.12, 0.68, 0.39, 0.85))

@job
def LEG2_bathtub_edge():
    fix_label("LEG2_bathtub_edge", (0.66, 0.62, 0.82, 0.78))

@job
def LEG3_nightstand_reach():
    fix_label("LEG3_nightstand_reach", (0.08, 0.51, 0.24, 0.65))

@job
def LEG4_thigh_closeup():
    fix_label("LEG4_thigh_closeup", (0.384, 0.422, 0.625, 0.640))

@job
def PRD1_pink_checklist():
    fix_label("PRD1_pink_checklist", (0.605, 0.565, 0.815, 0.690), radius=0.035)

@job
def PRD2_bundle_pricing():
    c = Composer(p("PRD2_bundle_pricing"))
    rects = [(0.29, 0.53, 0.42, 0.61), (0.44, 0.53, 0.57, 0.61)]
    for x0, y0, x1, y1 in rects:
        c.soften(x0, y0, x1, y1, radius=0.035, feather=0.14)
    for x0, y0, x1, y1 in rects:
        target_w = (x1 - x0) * 0.85
        s1 = _fit_size(c, CLAIM1, "sans-italic", target_w, 0.024)
        s2 = _fit_size(c, CLAIM2, "sans-italic", target_w, 0.024)
        size = min(s1, s2)
        gap = size * 1.5
        cy = (y0 + y1) / 2
        cx = (x0 + x1) / 2
        c.centered(cy - gap / 2, CLAIM1, key="sans-italic", size=size, color=MAGENTA,
                   shadow=False, center_on=cx)
        c.centered(cy + gap / 2, CLAIM2, key="sans-italic", size=size, color=MAGENTA,
                   shadow=False, center_on=cx)
    c.save(o("PRD2_bundle_pricing"))

@job
def PRD3_ingredients_flatlay():
    fix_label("PRD3_ingredients_flatlay", (0.406, 0.492, 0.599, 0.694), radius=0.035)

@job
def PRD4_hand_holding_bottle():
    fix_label("PRD4_hand_holding_bottle", (0.287, 0.410, 0.673, 0.627), radius=0.035)

@job
def DR1_gynecologue():
    fix_label("DR1_gynecologue", (0.16, 0.40, 0.42, 0.57))

@job
def DR2_hormones_comparison():
    fix_label("DR2_hormones_comparison", (0.645, 0.444, 0.898, 0.746), radius=0.035)


# ---------------------------------------------------------------- pass-through
for _n in ("LNG1_arched_back", "LNG2_side_profile_gasp", "LNG4_morning_relaxed",
           "LNG5_couple_embrace"):
    def _pt(n=_n): passthrough(n)
    _pt.__name__ = _n
    job(_pt)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
