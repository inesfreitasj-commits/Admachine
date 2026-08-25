#!/usr/bin/env python3
"""ArtériVie batch — all on-image copy composited in code.

Every figure is quoted from assets/product-page.md. Every line is checked against
assets/winner-copy.md before it is drawn — half the winning set carries no text at all, and
the two that do must not be reused word for word.

TIMEFRAME: 7 jours, as the client briefed. The funnel's own FAQ says two-to-three weeks and
its testimonials say three, four and six weeks — so "7 jours" and a multi-week testimonial
never appear in the same frame.
NOT used: VIVA / alive / Chatelaine / Best Health (the same four Canadian outlets for the
fifth product running). No ingredient outside aubépine, ail, feuille d'olivier, valériane.
"""
import os
import shutil
import sys

sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import (Composer, trim_uniform_border, pad_square, crop_to,
                          erase_drawn_rules, assert_not_winner_copy,
                          WHITE, RED, NEARBK, BLACK)

ORANGE = (0.945, 0.376, 0.118)     # the funnel's CTA orange
CREAM  = (0.992, 0.933, 0.910)     # the funnel's section ground
INK    = (0.13, 0.13, 0.15)
WINCOPY = "assets/winner-copy.md"
SRC, OUT, TMP = "production", "final", "/tmp/arterivie-work"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def t(n): return f"{TMP}/{n}.png"
jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
CTA = "Commandez ArtériVie™ maintenant →"


def check(lines, n):
    assert_not_winner_copy(lines, path=WINCOPY, label=n)


def start(n, crop=None, derule=False, square=None):
    trim_uniform_border(p(n))
    src = p(n)
    if derule:
        # "The top fifth of the frame is flat empty white" was phrased positively and the
        # model STILL drew the boxes. Describing an empty zone at all invites a rectangle;
        # the only reliable answer is to rub them out afterwards.
        shutil.copyfile(src, t(n + "_dr")); erase_drawn_rules(t(n + "_dr")); src = t(n + "_dr")
    if crop:
        crop_to(src, t(n), **crop); src = t(n)
        if square is not None:
            # "sample" pads in the render's OWN ground colour. A hardcoded cream never
            # quite matches what the model drew, and the mismatch reads as a band.
            pad_square(src, fill=None if square == "sample" else square,
                       sample=(0.5, 0.06))
    return Composer(src)


BRAND = {   # real manufacturer marks the render put on the equipment
    "S1_ct_gantry_feet":  [(0.44, 0.03, 0.56, 0.10), (0.86, 0.00, 1.00, 0.06)],
    "S3_angio_suite":     [(0.33, 0.27, 0.47, 0.33), (0.34, 0.40, 0.50, 0.45)],
    "S4_man_entering_scanner": [(0.29, 0.12, 0.44, 0.19), (0.54, 0.24, 0.68, 0.30),
                                (0.89, 0.21, 1.00, 0.34)],
    "S2_mri_control_glass": [(0.55, 0.66, 0.79, 0.75)],   # garbled text on the centre monitor
}


NATIVE_CROP = {  # S2 came back with a drawn border frame around the whole picture
    "S2_mri_control_glass": dict(left=0.034, right=0.968, top=0.030, bottom=0.958),
}


def native(n):
    """Three of the six winners are silent hospital photographs. Respect that."""
    c = start(n, crop=NATIVE_CROP.get(n))
    for box in BRAND.get(n, ()):
        c.soften(*box, radius=0.006, feather=0.28)
    c.save(o(n)); pad_square(o(n))


def photo_copy(c, n, l1, l2, cta=True, y=0.775, scrim=0.74, solid=0.0, bar=ORANGE):
    """Contrast is measured AFTER the scrim is laid, on the flushed page — measuring the
    source would report the background as it was before the scrim, which is useless."""
    check([l1, l2], n)
    foot = 0.902 if cta else 1.0
    if solid:
        c.band(y - solid, foot, fill=BLACK, opacity=0.82)
    else:
        c.scrim(y - 0.20, foot, opacity=scrim)
    if cta: c.band(0.902, 1.0, fill=bar, opacity=1.0)
    probe = Composer(c.save(t(n + "_probe")))
    for yy in (y, y + 0.078):
        ok, bg, ct = probe.contrast_ok(WHITE, 0.05, yy - 0.05, 0.95, yy + 0.015)
        if not ok:
            raise SystemExit(f"{n}: white copy scores {ct:.2f} contrast at y={yy:.3f} "
                             f"(background {bg:.2f}) — needs a solid bar, not a gradient.")
    c.text(0.055, y, l1, key="sans", size=0.042)
    w = c.measure(l2, "sans-bold", 0.058)
    if w > 0.90: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.text(0.055, y + 0.078, l2, key="sans-bold", size=0.058)
    c.underline(0.055, 0.055 + w, y + 0.096)
    if cta: c.centered(0.962, CTA, key="sans-bold", size=0.042, color=WHITE, shadow=False)


# ================= S — silent hospital natives (the dominant winning format) =========
for _n in ("S1_ct_gantry_feet", "S2_mri_control_glass", "S3_angio_suite",
           "S4_man_entering_scanner", "S5_ultrasound_probe_groin", "S6_waiting_room_men",
           "P3_bathroom_shelf_native", "N3_doctor_artery_model"):
    def _mk(n=_n): native(n)
    _mk.__name__ = _n; job(_mk)

# ================= H — claim heroes, win_01's lockup, new words ======================
@job
def H1_artery_cutaway_jar():
    n = "H1_artery_cutaway_jar"
    c = start(n)
    lines = ["97 % de plaque en moins.", "Et tout recommence à circuler."]
    check(lines, n)
    c.text(0.055, 0.098, lines[0], key="sans-bold", size=0.072, color=RED, shadow=False)
    c.text(0.055, 0.176, lines[1], key="sans-bold", size=0.048, color=NEARBK, shadow=False)
    c.badge(0.055, 0.900, "DES ÉRECTIONS NATURELLES, SANS VIAGRA", size=0.032, fill=ORANGE)
    c.save(o(n)); pad_square(o(n), fill=WHITE)

@job
def H2_two_arteries_compare():
    n = "H2_two_arteries_compare"
    c = start(n, derule=True)
    for r in (fitz.Rect(0, 0, c.W, 6), fitz.Rect(0, c.H - 6, c.W, c.H),
              fitz.Rect(0, 0, 6, c.H), fitz.Rect(c.W - 6, 0, c.W, c.H)):
        c.page.draw_rect(r, color=None, fill=WHITE)     # the drawn frame's own edges
    c.badge(0.045, 0.055, "BOUCHÉE", size=0.034, fill=NEARBK)
    c.badge(0.560, 0.055, "DÉBOUCHÉE", size=0.034, fill=ORANGE)
    line = "97 % des dépôts artériels éliminés."
    check([line], n)
    c.band(0.900, 1.0, fill=ORANGE, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n), fill=WHITE)

@job
def H3_jar_orange_ground():
    n = "H3_jar_orange_ground"
    trim_uniform_border(p(n))
    shutil.copyfile(p(n), t(n)); pad_square(t(n))
    c = Composer(t(n))
    # The jar's lid begins at x = 0.40. Everything on the left must finish before that,
    # and the clear column runs the full height, so the block sits low instead of high.
    LIMIT = 0.375
    c.text(0.055, 0.560, "34,95 €", key="sans-bold", size=0.105, color=WHITE, shadow=False)
    for line, y, size in (("au lieu de 70,00 €", 0.615, 0.034),
                          ("Garantie 60 jours.", 0.668, 0.034)):
        check([line], n)
        if 0.058 + c.measure(line, "sans-bold", size) > LIMIT:
            raise SystemExit(f'H3: "{line}" reaches the jar')
        c.text(0.058, y, line, key="sans-bold", size=size, color=WHITE, shadow=False)
    c.band(0.902, 1.0, fill=WHITE, opacity=1.0)
    c.centered(0.962, CTA, key="sans-bold", size=0.042, color=ORANGE, shadow=False)
    c.save(o(n))

@job
def H4_couple_bed_relief():
    n = "H4_couple_bed_relief"
    c = start(n)
    lines = ["« Depuis la sixième semaine,", "je n'ai plus eu besoin de Viagra. »"]
    check(lines, n)
    c.scrim(0.58, 1.0, opacity=0.76)
    for i, ln in enumerate(lines):
        c.text(0.055, 0.808 + i * 0.058, ln, key="sans-italic", size=0.042)
    c.text(0.055, 0.940, "— Michel Lavoie, client vérifié", key="sans-bold", size=0.031)
    c.save(o(n)); pad_square(o(n))

# ================= M — mechanism diagrams, labels on clear ground ====================
@job
def M1_penile_vs_coronary():
    # Cropping the foot does two jobs: it drops the render's own ground seam, and it takes
    # this ad's similarity to H2 from r = 0.657 to 0.51. Three artery diagrams in one batch
    # will always converge unless their LARGE shapes are pulled apart.
    n = "M1_penile_vs_coronary"
    c = start(n, crop=dict(bottom=0.860), square="sample")
    lines = ["Deux fois plus fines que celles du cœur.", "Elles se bouchent les premières."]
    check(lines, n)
    c.text(0.048, 0.072, lines[0], key="sans", size=0.042, color=INK, shadow=False)
    c.text(0.048, 0.126, lines[1], key="sans-bold", size=0.048, color=INK, shadow=False)
    # Short leaders to the near edge of each vessel — a leader that crosses the drawing to
    # reach its centre is the thing the client objected to on the last product.
    c.callout(0.048, 0.870, "Artère coronaire", 0.250, 0.775, size=0.030)
    c.callout(0.560, 0.870, "Artère du pénis — 1 à 2 mm", 0.700, 0.718, size=0.030)
    c.save(o(n))

@job
def M2_plaque_timeline():
    n = "M2_plaque_timeline"
    trim_uniform_border(p(n))
    shutil.copyfile(p(n), t(n)); pad_square(t(n), sample=(0.5, 0.06))
    c = Composer(t(n))
    lines = ["7 hommes sur 10 perdent leurs érections.",
             "Tout commence dans les artères."]
    check(lines, n)
    for line, y, key, size in ((lines[0], 0.078, "sans", 0.036),
                               (lines[1], 0.134, "sans-bold", 0.044)):
        if 0.045 + c.measure(line, key, size) > 0.95:
            raise SystemExit(f'M2: "{line}" runs off the frame')
        c.text(0.045, y, line, key=key, size=size, color=INK, shadow=False)
    c.band(0.900, 1.0, fill=ORANGE, opacity=1.0)
    c.centered(0.962, CTA, key="sans-bold", size=0.042, color=WHITE, shadow=False)
    c.save(o(n))

@job
def M3_pelvic_artery_map():
    n = "M3_pelvic_artery_map"
    c = start(n)
    lines = ["70 % des troubles de l'érection", "après 50 ans sont vasculaires."]
    check(lines, n)
    c.text(0.045, 0.080, lines[0], key="sans", size=0.040, color=INK, shadow=False)
    c.text(0.045, 0.136, lines[1], key="sans-bold", size=0.046, color=INK, shadow=False)
    c.callout(0.045, 0.640, "1 à 2 mm de diamètre", 0.560, 0.600, size=0.030)
    c.save(o(n)); pad_square(o(n), fill=CREAM)

@job
def M4_pill_vs_cleaning():
    n = "M4_pill_vs_cleaning"
    c = start(n, crop=dict(left=0.100, right=0.900, top=0.120, bottom=0.920), square=CREAM)
    c.badge(0.035, 0.052, "LE VIAGRA DILATE", size=0.030, fill=NEARBK)
    c.badge(0.545, 0.052, "ARTÉRIVIE NETTOIE", size=0.030, fill=ORANGE)
    line = "Les dépôts continuent de s'accumuler."
    check([line], n)
    c.centered(0.930, line, key="sans-bold", size=0.042, color=INK, shadow=False)
    c.save(o(n))

# ================= P / N — partner POV, UGC, new concepts ============================
@job
def P1_wife_holding_jar():
    n = "P1_wife_holding_jar"
    c = start(n)
    photo_copy(c, n, "Commandé par sa femme.", "Sans qu'il ait rien demandé.")
    c.save(o(n)); pad_square(o(n))

@job
def P2_man_kitchen_jar():
    n = "P2_man_kitchen_jar"
    c = start(n)
    photo_copy(c, n, "2 gélules par jour, au repas.", "Un flacon = 30 jours.")
    c.save(o(n)); pad_square(o(n))

@job
def N1_pharmacy_shelf():
    n = "N1_pharmacy_shelf"
    c = start(n, crop=dict(right=0.840, top=0.082, bottom=0.918))
    # ring the jar without clipping the frame: the crop moved it to x ~ 0.25
    c.page.draw_circle(fitz.Point(0.270 * c.W, 0.540 * c.H), 0.255 * c.H,
                       color=RED, width=0.008 * c.H, fill=None)
    photo_copy(c, n, "Un seul de ces produits", "s'attaque aux dépôts.",
               y=0.085, solid=0.085)
    c.save(o(n)); pad_square(o(n))

@job
def N2_cardboard_sign():
    n = "N2_cardboard_sign"
    c = start(n)
    lines = ["70 % DES TROUBLES", "DE L'ÉRECTION SONT", "VASCULAIRES.",
             "PERSONNE NE ME", "L'AVAIT DIT."]
    check(lines, n)
    ok, busy = c.clear_ok(0.25, 0.50, 0.79, 0.87, maximum=0.034)  # card face only — his
    # fingers curl over the top corners, so the probe stops short of them
    if not ok:
        raise SystemExit(f"{n}: the cardboard is not blank (busyness {busy:.4f})")
    for i, ln in enumerate(lines):
        w = c.measure(ln, "sans-bold", 0.044)
        c.text(0.52 - w / 2, 0.520 + i * 0.068, ln, key="sans-bold", size=0.044,
               color=(0.10, 0.09, 0.08), shadow=False)
    c.save(o(n)); pad_square(o(n))


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
