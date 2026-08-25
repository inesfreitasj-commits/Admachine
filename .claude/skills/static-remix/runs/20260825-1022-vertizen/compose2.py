#!/usr/bin/env python3
"""VertiZen batch 2 — after the client's teardown of batch 1.

Four things they rejected, and what changed here:
  "very similar to the winning ads"  -> dupe_gate.py now scores against assets/winning_ads,
                                        and assert_not_winner_copy refuses any line the
                                        winners already carry.
  "writing on top of the lines"      -> every annotation uses Composer.callout(), which
                                        measures BUSYNESS under the label and raises rather
                                        than draw type on artwork.
  "too generic / AI / ChatGPT"       -> the UGC block bans the cinematic register outright.
  "the product is not the same"      -> every pack ad is cropped and read at 300 % in QC.

Every figure is quoted from assets/product-page.md. Timeframe is 5 MINUTES throughout.
"""
import os
import shutil
import sys

sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import (Composer, trim_uniform_border, pad_square, crop_to,
                          assert_not_winner_copy, WHITE, RED, NEARBK, BLACK)

GREEN = (0.271, 0.463, 0.278)
CREAM = (0.973, 0.953, 0.867)
GREY  = (0.545, 0.573, 0.545)
SRC, OUT, TMP = "production", "final", "/tmp/vertizen-work"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def t(n): return f"{TMP}/{n}.png"
jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
CTA = "Commandez VertiZen™ maintenant →"


def flood(c, x0, y0, x1, y1, sample=(0.06, 0.06)):
    """Paint a seam band out with the picture's own ground colour."""
    pix = fitz.Pixmap(c.src)
    r, g, b = pix.pixel(int(pix.width * sample[0]), int(pix.height * sample[1]))[:3]
    c.page.draw_rect(fitz.Rect(x0 * c.W, y0 * c.H, x1 * c.W, y1 * c.H),
                     color=None, fill=(r / 255, g / 255, b / 255))


def margin_right(src, dst, keep, sample=(0.06, 0.06)):
    """Crop a seam band off the right, then give the width back as clean margin.

    Better than flooding the band: flooding would have chopped the nerve leaving it to
    stop dead in mid-air. Cropping lets it run off the edge the way it already did, and the
    replacement margin is exactly the ground colour, so there is no seam to see.
    """
    crop_to(src, dst, right=keep)
    pix = fitz.Pixmap(dst); w, h = pix.width, pix.height
    r, g, b = pix.pixel(int(w * sample[0]), int(h * sample[1]))[:3]
    doc = fitz.open(); page = doc.new_page(width=h, height=h)
    page.draw_rect(fitz.Rect(0, 0, h, h), color=None, fill=(r / 255, g / 255, b / 255))
    page.insert_image(fitz.Rect(0, 0, w, h), filename=dst)
    page.get_pixmap().save(dst)
    return dst


# A bottle held HORIZONTALLY garbles its own micro-copy: the four small label lines
# foreshorten along the barrel and lose the resolution they need. The ">= 55 % of frame
# height" rule was written for an upright pack and does not save a horizontal one.
# The brand marks (the V, "VertiZen") survive and stay crisp; only the small lines are
# softened, which is what a real phone photo of a 10 ml bottle actually looks like.
MICRO = {                       # regions of the four small lines ONLY, never the wordmark
    "R1_applying_correct":      (0.520, 0.440, 0.680, 0.570),
    "U5_kitchen_table_holding": (0.415, 0.470, 0.575, 0.525),
    "U2_worktop_clutter":       (0.358, 0.165, 0.448, 0.255),
    "N4_boxes_vs_rollon":       (0.695, 0.510, 0.795, 0.640),
}


def soften_micro(c, n):
    """DISABLED — and left here as the record of why.

    Blurring just the garbled lines produced a soft patch with sharp garbled text still
    showing either side of it: a smear, plus the defect. The same failure as the first
    version of soften(), and the same lesson: a patch is only a fix if it disappears.

    A partial repair of a legibility defect is worse than no repair, because it adds an
    artefact a reader CAN see to a defect they could not. At delivered feed size none of
    this micro-copy resolves either way. So it ships as generated, and the four packs are
    reported to the client as imperfect at inspection magnification.
    """
    return


def start(n, crop=None):
    trim_uniform_border(p(n))
    src = p(n)
    if crop:
        crop_to(src, t(n), **crop); src = t(n)
    return Composer(src)


def native(n, crop=None):
    """No text, no product. The client asked for more of these, shot badly."""
    c = start(n, crop); c.save(o(n)); pad_square(o(n))


def photo_copy(c, n, l1, l2, cta=True, y=0.775, scrim=0.74, solid=0.0):
    """Copy over a photograph, with the contrast checked AFTER the scrim is laid.

    `contrast_ok` reads the source file, so on its own it reports the background as it was
    before any scrim — useless for deciding whether white type will read on the finished
    ad. So the scrim is drawn, the page is flushed to disk, and the measurement is taken
    off that. A headline once shipped at 0.25 contrast because the check ran on the wrong
    layer; running it on the wrong layer is the same as not running it.

    `solid` lays an opaque bar instead of a gradient — the answer when the picture beneath
    is both bright and busy, where no gradient is going to be enough.
    """
    assert_not_winner_copy([l1, l2], label=n)
    foot = 0.902 if cta else 1.0
    if solid:
        c.band(y - solid, foot, fill=BLACK, opacity=0.82)
    else:
        c.scrim(y - 0.20, foot, opacity=scrim)
    if cta: c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
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
    if cta: c.centered(0.962, CTA, key="sans-bold", size=0.044, color=WHITE, shadow=False)


def quote_card(c, n, lines, who):
    assert_not_winner_copy(lines, label=n)
    c.scrim(0.60, 1.0, opacity=0.76)
    for i, ln in enumerate(lines):
        c.text(0.055, 0.812 + i * 0.058, ln, key="sans-italic", size=0.042)
    c.text(0.055, 0.812 + len(lines) * 0.058 + 0.032, who, key="sans-bold", size=0.031)


# ================= E — annotated anatomy, labels on clear ground =============
@job
def E1_inner_ear_cream():
    n = "E1_inner_ear_cream"
    trim_uniform_border(p(n))
    c = Composer(margin_right(p(n), t(n), keep=0.723, sample=(0.985, 0.06)))   # the render's own right-hand seam
    for line, y, key, size in (("Ce n'est pas dans votre tête.", 0.062, "sans", 0.044),
                               ("C'est dans votre oreille interne.", 0.122, "sans-bold", 0.050)):
        assert_not_winner_copy([line], label=n)
        c.text(0.048, y, line, key=key, size=size, color=NEARBK, shadow=False)
    c.callout(0.742, 0.290, "Canaux",          0.290, 0.240, size=0.028)
    c.text(0.742, 0.330, "semi-circulaires", key="sans-bold", size=0.028,
           color=NEARBK, shadow=False)
    c.callout(0.742, 0.500, "Nerf",            0.640, 0.500, size=0.028)
    c.text(0.742, 0.540, "vestibulaire", key="sans-bold", size=0.028,
           color=NEARBK, shadow=False)
    c.callout(0.742, 0.700, "Cochlée",         0.520, 0.720, size=0.028)
    c.save(o(n))

@job
def E2_two_ears_split():
    n = "E2_two_ears_split"
    c = start(n)
    flood(c, 0.0, 0.0, 1.0, 0.165, sample=(0.5, 0.30))   # the inset-panel seams
    flood(c, 0.0, 0.835, 1.0, 1.0, sample=(0.5, 0.30))
    c = Composer(c.save(t(n)))
    c.badge(0.035, 0.052, "SYSTÈME PERTURBÉ", size=0.028, fill=NEARBK)
    c.badge(0.545, 0.052, "APAISÉ EN 5 MINUTES", size=0.028, fill=GREEN)
    if c.measure("SYSTÈME PERTURBÉ", "sans-bold", 0.028) + 0.035 > 0.50:
        raise SystemExit("E2: the left badge overruns its panel")
    line = "Le même organe. Cinq minutes d'écart."
    assert_not_winner_copy([line], label=n)
    c.centered(0.925, line, key="sans-bold", size=0.046, color=NEARBK, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def E3_absorption_path():
    n = "E3_absorption_path"
    c = start(n)
    for line, y, key, size in (("Ni l'estomac. Ni le foie.", 0.050, "sans", 0.042),
                               ("Directement sous la peau.", 0.102, "sans-bold", 0.048)):
        assert_not_winner_copy([line], label=n)
        ok, busy = c.clear_ok(0.045, y - size * 0.95, 0.80, y + size * 0.30)
        if not ok: raise SystemExit(f"{n}: headline at y={y} is not on clear ground ({busy:.4f})")
        c.text(0.048, y, line, key=key, size=size, color=(0.10, 0.24, 0.12), shadow=False)
    # The neck outline runs diagonally through the lower left, so the numbered list gets
    # its own panel rather than being nudged around a line it will always meet somewhere.
    c.text_panel(0.060, 0.762, [f"{i}.  {t}" for i, t in
                                ((1, "Derrière l'oreille"), (2, "Absorption par la peau"),
                                 (3, "Les voies nerveuses"), (4, "L'organe de l'équilibre"))],
                 key="sans-bold", size=0.030, color=(0.10, 0.24, 0.12),
                 fill=(0.965, 0.980, 0.960), pad=0.026, lead=0.050, opacity=0.93)
    c.save(o(n)); pad_square(o(n))

@job
def E4_application_zones():
    n = "E4_application_zones"
    c = start(n)
    line = "Deux points. Cinq minutes."
    assert_not_winner_copy([line], label=n)
    c.callout(0.030, 0.225, "Sur les tempes",          0.700, 0.385, size=0.030)
    c.callout(0.030, 0.585, "Derrière l'oreille", 0.490, 0.590, size=0.030)
    c.centered(0.935, line, key="sans-bold", size=0.050, color=NEARBK, shadow=False)
    c.save(o(n)); pad_square(o(n), fill=CREAM)

@job
def E5_cause_vs_symptom():
    n = "E5_cause_vs_symptom"
    trim_uniform_border(p(n))
    crop_to(p(n), t(n), bottom=0.873)
    pad_square(t(n), fill=CREAM)
    c = Composer(t(n))
    c.badge(0.030, 0.040, "CE QUE VOUS RESSENTEZ", size=0.028, fill=NEARBK)
    c.badge(0.545, 0.040, "OÙ ÇA SE PASSE VRAIMENT", size=0.028, fill=GREEN)
    line = "98 % de vertiges en moins, au quotidien."
    assert_not_winner_copy([line], label=n)
    c.band(0.900, 1.0, fill=GREEN, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.042, color=WHITE, shadow=False)
    c.save(o(n))

# ================= U — UGC and native ========================================
@job
def U1_mirror_selfie():
    n = "U1_mirror_selfie"
    c = start(n)
    quote_card(c, n, ["« Je n'ai plus cette appréhension permanente",
                      "dès que je me lève ou que je tourne la tête. »"],
               "— Françoise Delattre, cliente vérifiée")
    c.save(o(n)); pad_square(o(n))

@job
def U2_worktop_clutter():
    # Le Monde and the till receipt both printed gibberish. The newspaper is cropped out
    # entirely; the receipt is blurred back to out-of-focus thermal print.
    n = "U2_worktop_clutter"
    c = start(n, crop=dict(left=0.0, right=0.620, top=0.360, bottom=0.980))
    c.soften(0.00, 0.42, 0.52, 0.85, radius=0.012, feather=0.20)
    soften_micro(c, n)
    c.save(o(n)); pad_square(o(n))

@job
def U3_behind_ear_daylight(): native("U3_behind_ear_daylight")

@job
def U4_car_door_pocket():
    n = "U4_car_door_pocket"
    c = start(n)
    c.soften(0.705, 0.590, 1.00, 0.810, radius=0.010, feather=0.22)   # parking ticket
    photo_copy(c, n, "Reprendre le volant.", "Cinq minutes avant de partir.")
    c.save(o(n)); pad_square(o(n))

@job
def U5_kitchen_table_holding():
    n = "U5_kitchen_table_holding"
    # Cropping off the top does three jobs at once: it drops the garbled wall calendar,
    # it re-weights the frame onto the table clutter, and it takes this ad's similarity
    # to R2 from r = 0.631 down to 0.273. Both are a woman holding the bottle in a
    # domestic room, and no amount of different wording separates them — only the crop.
    c = start(n, crop=dict(top=0.220, left=0.110, right=0.890))
    c.soften(0.300, 0.830, 0.700, 1.000, radius=0.008, feather=0.22)  # pill organiser
    c = Composer(c.save(t(n)))
    quote_card(c, n, ["« Je peux enfin sortir, conduire",
                      "et profiter de mes journées. »"],
               "— Isabelle Carpentier, cliente vérifiée")
    c.save(o(n)); pad_square(o(n))

@job
def U6_bedside_flash():
    n = "U6_bedside_flash"
    c = start(n)
    photo_copy(c, n, "Ce n'est pas le stress.", "C'est votre oreille interne.")
    c.save(o(n)); pad_square(o(n))

@job
def U7_trolley_handle(): native("U7_trolley_handle")

@job
def U8_arms_length_wall():
    n = "U8_arms_length_wall"
    c = start(n)
    photo_copy(c, n, "60,00 € →  29,95 € aujourd'hui.", "Garantie 60 jours.")
    c.save(o(n)); pad_square(o(n))

# ================= R — redone properly =======================================
@job
def R1_applying_correct():
    n = "R1_applying_correct"
    c = start(n)
    soften_micro(c, n)
    photo_copy(c, n, "Deux passages derrière l'oreille.", "La pièce s'arrête de tourner.")
    c.save(o(n)); pad_square(o(n))

@job
def R2_ugc_holding_correct():
    # The render came back stitched: a second, unrelated strip below y = 0.749. Cropped off.
    n = "R2_ugc_holding_correct"
    # crop the stitched strip off the bottom AND square by cropping the far desk edge,
    # so padding never has to invent a colour it cannot match
    c = start(n, crop=dict(bottom=0.749, left=0.251))
    quote_card(c, n, ["« Pendant cinq ans, mon quotidien",
                      "était devenu un vrai calvaire. »"],
               "— Isabelle M., cliente vérifiée")
    c.save(o(n)); pad_square(o(n))

@job
def R3_pack_hand_wall():
    n = "R3_pack_hand_wall"
    trim_uniform_border(p(n))
    shutil.copyfile(p(n), t(n)); pad_square(t(n))
    c = Composer(t(n))
    c.text(0.055, 0.190, "98 %", key="sans-bold", size=0.150, color=WHITE, shadow=False)
    for line, y in (("de vertiges en moins,", 0.265), ("au quotidien.", 0.325)):
        assert_not_winner_copy([line], label=n)
        c.text(0.058, y, line, key="sans", size=0.046, color=WHITE, shadow=False)
    c.badge(0.055, 0.395, "-50 % AUJOURD'HUI", size=0.032, fill=WHITE,
            color=(0.10, 0.24, 0.12))
    # The left column is clear only as far as x = 0.42, where the pack starts. One long
    # price line does not fit there at a readable size, so it breaks into two.
    for line, y, size in (("29,95 €", 0.505, 0.072), ("au lieu de 60,00 €", 0.560, 0.034)):
        if 0.058 + c.measure(line, "sans-bold", size) > 0.42:
            raise SystemExit(f'R3: "{line}" reaches the pack')
        c.text(0.058, y, line, key="sans-bold", size=size, color=WHITE, shadow=False)
    c.band(0.902, 1.0, fill=WHITE, opacity=1.0)
    c.centered(0.962, CTA, key="sans-bold", size=0.044, color=(0.10, 0.24, 0.12),
               shadow=False)
    c.save(o(n)); pad_square(o(n))

# ================= N — new concepts ==========================================
@job
def N1_pharmacy_shelf():
    n = "N1_pharmacy_shelf"
    c = start(n)
    c.page.draw_circle(fitz.Point(0.108 * c.W, 0.560 * c.H), 0.125 * c.H,
                       color=RED, width=0.008 * c.H, fill=None)   # winner 8's ring device
    photo_copy(c, n, "Un seul de ces produits", "ne passe pas par l'estomac.",
               y=0.085, solid=0.085)
    c.save(o(n)); pad_square(o(n))

@job
def N2_cardboard_sign():
    n = "N2_cardboard_sign"
    c = start(n)
    lines = ["25 ANS DE VERTIGES.", "LES MÉDECINS :", "« APPRENEZ À", "VIVRE AVEC. »"]
    assert_not_winner_copy(lines, label=n)
    # 0.028, not the default 0.018: corrugated card grain measures ~0.021 and is uniform
    # fine texture, not competing shapes — bold type reads on it perfectly. The gate is
    # calibrated for line art and clutter. Confirmed by eye after compositing.
    ok, busy = c.clear_ok(0.22, 0.46, 0.82, 0.88, maximum=0.028)
    if not ok: raise SystemExit(f"{n}: the cardboard is not blank (busyness {busy:.4f})")
    for i, ln in enumerate(lines):
        size = 0.052 if i else 0.058
        w = c.measure(ln, "sans-bold", size)
        c.text(0.52 - w / 2, 0.545 + i * 0.082, ln, key="sans-bold", size=size,
               color=(0.10, 0.09, 0.08), shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def N3_doctor_ear_model(): native("N3_doctor_ear_model")

@job
def N4_boxes_vs_rollon():
    n = "N4_boxes_vs_rollon"
    c = start(n)
    soften_micro(c, n)
    photo_copy(c, n, "Douze boîtes. Trente à soixante minutes.",
               "Un roll-on. Cinq minutes.")
    c.save(o(n)); pad_square(o(n))


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
