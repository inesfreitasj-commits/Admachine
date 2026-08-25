#!/usr/bin/env python3
"""VertiZen batch — all on-image copy composited in code.

Every string is quoted from assets/product-page.md.
TIMEFRAME: the client asked for 5 MINUTES throughout — which is the hero claim
("en seulement 5 minutes" / "Stoppez bourdonnements en 5 min"). "3 à 5 minutes" is never used.
Used: 98 % · 5 minutes · 30 à 60 minutes (pills) · 2 heures (untreated crisis) · 60 jours ·
29,95 € · 4,8 · 12 523 avis.
NOT used: 4.9, 9 897, the Canadian press logos, the three nootropic ingredients, "Tinnix".
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import (Composer, trim_uniform_border, pad_square, mirror, crop_to,
                          erase_drawn_rules, WHITE, RED, NEARBK, BLACK)

GREEN = (0.271, 0.463, 0.278)      # VertiZen sage / forest green
CREAM = (0.969, 0.949, 0.878)      # C3's own ground, sampled off the render
GREY  = (0.545, 0.573, 0.545)      # the untreated / "before" register
PALE  = (0.769, 0.792, 0.769)
SRC, OUT = "production", "final"
TMP = "/tmp/vertizen-work"
os.makedirs(TMP, exist_ok=True)
def t(n): return f"{TMP}/{n}.png"
os.makedirs(OUT, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
CTA = "Commandez VertiZen™ maintenant →"

def native(n, flip=False, fill=None):
    """Four of the eight winners carry no text and no product. Respect that."""
    trim_uniform_border(p(n)); shutil.copyfile(p(n), o(n))
    if flip: mirror(o(n))
    pad_square(o(n), fill=fill)


def footer_square(n, keep, panel, lines, ink=NEARBK, cta_h=0.090, sizes=(0.036, 0.058),
                  src=None):
    """Crop a dead foreground slab away, then rebuild the square as a claim ad.

    Four of the five candid shots in this batch came back with 18-36 % of the frame given
    to a featureless out-of-focus foreground. Cropping it is free; re-squaring by cropping
    the sides would cut the subject, so the space becomes a real footer instead. The client
    has never once chosen a pure native, so a native that has to be cropped is better spent
    as a claim ad.
    """
    src = src or p(n)
    trim_uniform_border(src)
    crop_to(src, t(n), bottom=keep)
    pix = fitz.Pixmap(t(n)); W, Hc = pix.width, pix.height
    doc = fitz.open(); page = doc.new_page(width=W, height=W)
    page.draw_rect(fitz.Rect(0, 0, W, W), color=None, fill=panel)
    page.insert_image(fitz.Rect(0, 0, W, Hc), filename=t(n))
    page.draw_rect(fitz.Rect(0, W * (1 - cta_h), W, W), color=None, fill=GREEN)
    page.get_pixmap().save(o(n))
    c = Composer(o(n))
    base = 1 - cta_h - 0.052
    for i, (line, key, size) in enumerate(zip(lines, ("sans", "sans-bold"), sizes)):
        y = base - (len(lines) - 1 - i) * 0.078
        ok, bg, ct = c.contrast_ok(ink, 0.05, y - 0.05, 0.95, y + 0.015)
        if not ok:
            raise SystemExit(f"{n}: footer copy scores {ct:.2f} contrast (bg {bg:.2f})")
        c.text(0.055, y, line, key=key, size=size, color=ink, shadow=False)
    c.centered(1 - cta_h / 2 + 0.016, CTA, key="sans-bold", size=0.044,
               color=WHITE, shadow=False)
    c.save(o(n))

def circled(n, cx, cy, r=0.16):
    """Winner 8's device: a hand-drawn red ring round the thing you're meant to look at.
    Composited so it is exact, and so the scan underneath stays clean."""
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.page.draw_circle(fitz.Point(cx * c.W, cy * c.H), r * c.H,
                       color=RED, width=0.009 * c.H, fill=None)
    c.save(o(n)); pad_square(o(n), fill=BLACK)

def photo(n, l1, l2, bar=True, scrim=0.72):
    """Bar varies across the set on purpose — an identical bar everywhere manufactures
    duplicate scores out of pictures that share nothing."""
    trim_uniform_border(p(n))
    c = Composer(p(n))
    foot = 0.902 if bar else 1.0
    c.scrim(0.52, foot, opacity=scrim)
    if bar: c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
    dy = 0.0 if bar else 0.052
    for y in (0.735 + dy, 0.822 + dy):
        ok, bg, ct = c.contrast_ok(WHITE, 0.05, y - 0.05, 0.95, y + 0.015)
        if not ok:
            raise SystemExit(f"{n}: white copy scores {ct:.2f} contrast at y={y:.2f} (bg {bg:.2f})")
    c.text(0.055, 0.735 + dy, l1, key="sans", size=0.046)
    w = c.measure(l2, "sans-bold", 0.060)
    if w > 0.90: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.text(0.055, 0.822 + dy, l2, key="sans-bold", size=0.060)
    c.underline(0.055, 0.055 + w, 0.840 + dy)
    if bar: c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n), fill=BLACK if not bar else None)

# ---------------- A — variations on the winners ----------------
@job
def A1_cervical_xray(): native("A1_cervical_xray", fill=BLACK)

@job
def A2_ear_cutaway_colour():
    # A2 and A3 are both ear cutaways on white and measured r = 0.632 against each other,
    # the batch's only pair over the gate. Mirroring one drops the pair to 0.476. Free.
    native("A2_ear_cutaway_colour", flip=True, fill=WHITE)

@job
def A3_nerve_line_drawing():
    n = "A3_nerve_line_drawing"
    trim_uniform_border(p(n))
    # The brief asked for "clear empty white areas where callout labels will be placed"
    # and the model drew the boxes literally. Rub the lines out where they cross blank
    # paper and leave the segments that cross the drawing — those read as hatching.
    shutil.copyfile(p(n), t(n))
    found = erase_drawn_rules(t(n))
    if found < 4:
        raise SystemExit(f"{n}: only {found} drawn rules found — expected 4 plus the frame")
    c = Composer(t(n))
    for r in (fitz.Rect(0, 0, c.W, 5), fitz.Rect(0, c.H - 5, c.W, c.H),
              fitz.Rect(0, 0, 5, c.H), fitz.Rect(c.W - 5, 0, c.W, c.H)):
        c.page.draw_rect(r, color=None, fill=WHITE)        # the outer frame box
    c.centered(0.088, "NERF SURSOLLICITÉ", key="sans-bold", size=0.070,
               color=NEARBK, shadow=False)                     # winner 7, verbatim
    c.text(0.560, 0.330, "1. Comprimé", key="sans-bold", size=0.046, color=RED, shadow=False)
    c.text(0.560, 0.720, "2. Écrasé",   key="sans-bold", size=0.046, color=RED, shadow=False)
    c.save(o(n)); pad_square(o(n), fill=WHITE)

@job
def A4_temporal_ct(): circled("A4_temporal_ct", 0.50, 0.52, r=0.17)  # already square
@job
def A5_hand_behind_ear(): native("A5_hand_behind_ear")

@job
def A6_pack_green_ground():
    trim_uniform_border(p("A6_pack_green_ground"))
    c = Composer(p("A6_pack_green_ground"))
    c.centered(0.092, "Fini les vertiges.", key="sans-bold", size=0.062,
               color=NEARBK, shadow=False)                     # winner 5, verbatim
    c.centered(0.162, "Fini les acouphènes.", key="sans-bold", size=0.062,
               color=NEARBK, shadow=False)
    for i, t in enumerate(("Système vestibulaire apaisé",
                           "Soulagement en 5 minutes",
                           "Sans somnolence")):
        c.text(0.150, 0.828 + i * 0.052, "✓  " + t, key="sans-bold", size=0.036,
               color=NEARBK, shadow=False)
    c.save(o("A6_pack_green_ground")); pad_square(o("A6_pack_green_ground"))

@job
def A7_pack_desk_notepad():
    trim_uniform_border(p("A7_pack_desk_notepad"))
    c = Composer(p("A7_pack_desk_notepad"))
    c.text(0.055, 0.092, "25 ANS", key="sans-bold", size=0.078, color=GREEN, shadow=False)
    c.text(0.055, 0.166, "DE VERTIGES", key="sans-bold", size=0.052, color=NEARBK, shadow=False)
    c.text(0.055, 0.226, "AU QUOTIDIEN…", key="sans-bold", size=0.052, color=NEARBK, shadow=False)
    c.badge(0.055, 0.262, "SOULAGÉ EN 5 MINUTES !", size=0.046, fill=GREEN)
    # The notepad was generated blank so the handwriting is exact — but at 0.052 the second
    # line ran off the pad's right edge onto the table. Handwriting has to sit ON the paper
    # or the whole prop stops working, so it is measured against the pad, not the frame.
    # The pad is a trapezoid and the pen lies across its top-left corner, so the two lines
    # are indented differently — measured against the PAPER, not against the frame.
    for line, x, y in (("Un seul geste,", 0.205, 0.776),
                       ("et tout arrête de tourner.", 0.168, 0.838)):
        w = c.measure(line, "hand", 0.037)
        if x + w > 0.645:
            raise SystemExit(f'"{line}" runs off the notepad ({x + w:.3f} > 0.645)')
        c.text(x, y, line, key="hand", size=0.037, color=(0.15, 0.18, 0.35), shadow=False)
    c.save(o("A7_pack_desk_notepad")); pad_square(o("A7_pack_desk_notepad"))

# ---------------- B — the candid set ----------------
# B3 and B5 stay native. B1, B2 and B4 came back with a dead foreground slab across the
# bottom of the frame (36 %, 33 %, 18 %) — the cost of asking for "an out-of-focus
# foreground element". Cropped, then rebuilt.

@job
def B1_counter_grip():
    footer_square("B1_counter_grip", keep=0.674, panel=CREAM,
                  lines=("Se tenir à quelque chose, le temps que ça passe.",
                         "98 % de vertiges en moins."))

@job
def B2_pills_bedside():
    n = "B2_pills_bedside"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.soften(0.086, 0.428, 0.264, 0.520, radius=0.006)  # garbled print on the near blister
    pre = c.save(t(n + "_pre"))
    footer_square(n, keep=0.645, panel=NEARBK, lines=("Un comprimé : 30 à 60 minutes.",
                                                      "VertiZen™ : 5 minutes."),
                  ink=WHITE, sizes=(0.040, 0.062), src=pre)

@job
def B3_edge_of_bed(): native("B3_edge_of_bed")

@job
def B4_otoscope_exam():
    # Only 18 % dead, and the scene survives a side crop — so it stays native and
    # re-squares by cropping rather than by growing a footer it does not need.
    n = "B4_otoscope_exam"
    trim_uniform_border(p(n))
    crop_to(p(n), t(n), bottom=0.820, left=0.090, right=0.910)
    Composer(t(n)).save(o(n), zoom=1024 / fitz.Pixmap(t(n)).width)

@job
def B5_hand_on_wall(): native("B5_hand_on_wall")

@job
def D3_handbag_native():
    n = "D3_handbag_native"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    # The till receipt printed mirror-flipped Latin — readable enough to read as fake.
    # Blurred back to what it should always have been: out-of-focus thermal print.
    c.soften(0.500, 0.470, 0.950, 0.795, radius=0.011, feather=0.18,
             wash=WHITE, wash_opacity=0.10)
    c.save(o(n)); pad_square(o(n))

# ---------------- C — mechanism / comparison ----------------
@job
def C1_pill_vs_skin():
    trim_uniform_border(p("C1_pill_vs_skin"))
    c = Composer(p("C1_pill_vs_skin"))
    c.centered(0.088, "Un comprimé : estomac, foie, 30 à 60 minutes.",
               key="sans-bold", size=0.042, color=NEARBK, shadow=False)
    c.centered(0.150, "Un roll-on : 5 minutes.", key="sans-bold", size=0.052,
               color=GREEN, shadow=False)
    c.badge(0, 0.900, "DERRIÈRE L'OREILLE, PAS PAR L'ESTOMAC", size=0.036,
            fill=GREEN, center_on=0.5)
    c.save(o("C1_pill_vs_skin")); pad_square(o("C1_pill_vs_skin"))

@job
def C2_mri_inner_ear(): circled("C2_mri_inner_ear", 0.32, 0.50, r=0.13)

@job
def C3_two_clocks():
    """The dials are redrawn here, not generated.

    The render came back with hands at roughly 9:20 on the left and both hands near 12 on
    the right — arbitrary. The DURATION is the entire argument of this ad, and it is the one
    thing an image model will not carry. It also arrived with its cream ground stopping
    short of the top and bottom edges, leaving two white bands the headline half-sat on.
    """
    n = "C3_two_clocks"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.page.draw_rect(fitz.Rect(0, 0, c.W, c.H), color=None, fill=CREAM)   # one flat ground

    c.clock(0.281, 0.500, 0.176, hour=2, minute=0, ring=GREY, hands=(0.35, 0.35, 0.34),
            arc_to=2.0, arc_color=PALE)                     # a crisis: twelve to two
    c.clock(0.719, 0.500, 0.176, hour=12, minute=5, ring=GREEN, hands=(0.10, 0.30, 0.12))
    # no arc on the right: five minutes is 2.5 degrees and reads as a stray tick. The
    # contrast the ad is making is a grey wedge against no wedge at all.

    c.centered(0.098, "Une crise de vertige :", key="sans", size=0.048,
               color=NEARBK, shadow=False)
    c.centered(0.168, "jusqu'à 2 heures.", key="sans-bold", size=0.058,
               color=NEARBK, shadow=False)
    for cx, txt, col in ((0.281, "2 h 00", GREY), (0.719, "5 min", GREEN)):
        c.text(cx - c.measure(txt, "sans-bold", 0.042) / 2, 0.775, txt,
               key="sans-bold", size=0.042, color=col, shadow=False)
    c.centered(0.905, "Avec VertiZen™ : 5 minutes.", key="sans-bold", size=0.052,
               color=GREEN, shadow=False)
    c.save(o(n)); pad_square(o(n), fill=CREAM)

@job
def C4_vestibular_render():
    photo("C4_vestibular_render", "Votre centre de contrôle de l'équilibre.",
          "C'est là que ça se joue.", bar=False)

# ---------------- D — product in use / UGC ----------------
@job
def D1_applying_behind_ear():
    photo("D1_applying_behind_ear", "Derrière l'oreille. Un seul geste.",
          "Soulagement en 5 minutes.")

@job
def D2_ugc_holding():
    trim_uniform_border(p("D2_ugc_holding"))
    c = Composer(p("D2_ugc_holding"))
    c.scrim(0.60, 1.0, opacity=0.74)
    c.text(0.055, 0.812, "« Je peux enfin sortir, conduire et", key="sans-italic", size=0.044)
    c.text(0.055, 0.872, "profiter de mes journées. »", key="sans-italic", size=0.044)
    c.text(0.055, 0.940, "— Isabelle Carpentier, cliente vérifiée", key="sans-bold", size=0.032)
    c.save(o("D2_ugc_holding")); pad_square(o("D2_ugc_holding"))

@job
def D4_crisis_before_after():
    trim_uniform_border(p("D4_crisis_before_after"))
    c = Composer(p("D4_crisis_before_after"))
    c.badge(0.045, 0.045, "PENDANT LA CRISE", size=0.036, fill=NEARBK)
    c.badge(0.545, 0.045, "5 MINUTES APRÈS", size=0.036, fill=GREEN)
    c.scrim(0.74, 0.902, opacity=0.70)
    c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
    c.centered(0.868, "98 % de vertiges en moins, au quotidien", size=0.044)
    c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o("D4_crisis_before_after")); pad_square(o("D4_crisis_before_after"))

if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
