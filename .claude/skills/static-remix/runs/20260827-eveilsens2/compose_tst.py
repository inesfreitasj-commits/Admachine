#!/usr/bin/env python3
"""ÉveilSens — testimonial-quote ads (TST1-6).

Follow-up on the client's own win_03/win_06/win_07 device: a dramatized customer quote over
a scene photo, a short checklist, and a closing tagline. Every quote/bullet/tagline here is
fresh wording (checked against assets/winner-copy.md via assert_not_winner_copy — the claim
is fine to reuse, the wording has to move) and every fact traces to assets/product-page.md.
No second person in any of these six — client's own more explicit reference (two people,
implied sexual act) was declined; everything here stays within the single-subject ceiling
already established this run (win_06's own "partial back/hip exposure", never full nudity or
a depicted act).

Run: python3 compose_tst.py [name ...]
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, assert_not_winner_copy

SRC, OUT = "production_v2", "final_v2"
os.makedirs(OUT, exist_ok=True)
WHITE = (1, 1, 1)
PINK = (0.95, 0.20, 0.55)
WINNER_COPY = "assets/winner-copy.md"

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn


def partial_scrim(c, x0, y0, x1, y1, opacity=0.42):
    """A soft dark rect behind a text block that only covers part of the frame width —
    Composer.scrim()/band() are always full-width, which would darken photo area this run
    doesn't need darkened."""
    c.page.draw_rect(fitz_rect(c, x0, y0, x1, y1), color=None, fill=(0, 0, 0),
                      fill_opacity=opacity)


def fitz_rect(c, x0, y0, x1, y1):
    import pymupdf as fitz
    return fitz.Rect(x0 * c.W, y0 * c.H, x1 * c.W, y1 * c.H)


def checklist_line(c, x, baseline, text, size=0.030, color=WHITE):
    end_x = c.text(x, baseline, "✓", key="sym", size=size, color=PINK, shadow=True)
    c.text(end_x + 0.013, baseline, text, key="sans-bold", size=size, color=color, shadow=True)


def quote_block(c, x, y0, quote_lines, size=0.048, align_center=None):
    """quote_lines = [(text, color), ...]. Returns the baseline just after the block."""
    gap = size * 1.35
    for i, (text, color) in enumerate(quote_lines):
        b = y0 + i * gap
        if align_center is not None:
            c.centered(b, text, key="sans-bold", size=size, color=color, shadow=True,
                       center_on=align_center)
        else:
            c.text(x, b, text, key="sans-bold", size=size, color=color, shadow=True)
    return y0 + len(quote_lines) * gap


@job
def TST1_sheets_grip():
    quote = [("« Je ne savais plus si je devais", WHITE),
             ("respirer ou crier son prénom. »", PINK)]
    bullets = ["1 À 2 GOUTTES SUFFISENT", "USAGE EXTERNE, DISCRET",
               "SANS PARABÈNES NI SULFATES"]
    tagline = "SON CORPS N'A PAS MENTI."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST1", path=WINNER_COPY)

    c = Composer(p("TST1_sheets_grip"))
    partial_scrim(c, 0.0, 0.60, 1.0, 1.0, opacity=0.48)
    y = quote_block(c, None, 0.665, quote, size=0.038, align_center=0.5)
    y += 0.028
    bullet_size = 0.023
    for i, b in enumerate(bullets):
        w = c.measure(b, "sans-bold", bullet_size) + c.measure("✓", "sym", bullet_size) + 0.013
        checklist_line(c, 0.5 - w / 2, y + i * 0.033, b, size=bullet_size)
    tagline_y = y + len(bullets) * 0.033 + 0.028
    c.centered(tagline_y, tagline, key="sans-bold", size=0.026, color=PINK, shadow=True,
               center_on=0.5)
    c.save(o("TST1_sheets_grip"))


@job
def TST2_pillow_press():
    quote = [("« Mon oreiller pourrait", WHITE), ("tout raconter. »", PINK)]
    bullets = ["MASSAGE DE 90 SECONDES", "COMPATIBLE PRÉSERVATIFS", "VÉGAN & SANS TEST ANIMAL"]
    tagline = "ELLE N'A RIEN VU VENIR."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST2", path=WINNER_COPY)

    c = Composer(p("TST2_pillow_press"))
    partial_scrim(c, 0.585, 0.03, 1.0, 0.62, opacity=0.40)
    y = quote_block(c, 0.615, 0.115, quote, size=0.030)
    y += 0.05
    bullet_size = 0.019
    for i, b in enumerate(bullets):
        checklist_line(c, 0.615, y + i * 0.048, b, size=bullet_size)
    c.text(0.615, 0.575, tagline, key="sans-bold", size=0.023, color=PINK, shadow=True)
    c.save(o("TST2_pillow_press"))


@job
def TST3_legs_tangled():
    quote = [("Elle a fini par ne plus démêler", WHITE), ("ni les draps, ni ses jambes.", PINK)]
    bullets = ["2 GOUTTES, 90 SECONDES", "60 452 AVIS VÉRIFIÉS", "GARANTIE 60 JOURS"]
    tagline = "CE SOIR-LÀ, ELLE N'A PAS COMPTÉ LES MINUTES."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST3", path=WINNER_COPY)

    c = Composer(p("TST3_legs_tangled"))
    partial_scrim(c, 0.0, 0.0, 1.0, 0.36, opacity=0.40)
    y = quote_block(c, None, 0.075, quote, size=0.040, align_center=0.5)
    y += 0.032
    bullet_size = 0.026
    for i, b in enumerate(bullets):
        w = c.measure(b, "sans-bold", bullet_size) + c.measure("✓", "sym", bullet_size) + 0.013
        checklist_line(c, 0.5 - w / 2, y + i * 0.038, b, size=bullet_size)
    c.band(0.93, 0.985, fill=(0.45, 0.02, 0.28), opacity=1.0)
    c.centered(0.965, tagline, key="sans-bold", size=0.026, color=WHITE, shadow=False,
               center_on=0.5)
    c.save(o("TST3_legs_tangled"))


@job
def TST4_shoulder_glance():
    quote = [("« Il a fallu qu'il me redemande", WHITE), ("deux fois si j'allais bien. »", PINK)]
    bullets = ["ORIGINE 100 % VÉGÉTALE", "AUCUNE HORMONE", "AUCUNE ORDONNANCE NÉCESSAIRE"]
    tagline = "+60 000 CLIENTES ONT DIT OUI."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST4", path=WINNER_COPY)

    c = Composer(p("TST4_shoulder_glance"))
    y = quote_block(c, 0.045, 0.115, quote, size=0.033)
    y += 0.05
    bullet_size = 0.024
    for i, b in enumerate(bullets):
        checklist_line(c, 0.045, y + i * 0.050, b, size=bullet_size)
    c.text(0.045, 0.565, tagline, key="sans-bold", size=0.026, color=PINK, shadow=True)
    c.save(o("TST4_shoulder_glance"))


@job
def TST5_back_curve():
    quote = [("Elle a arrêté de compter les minutes", WHITE), ("après la première.", PINK)]
    bullets = ["1 À 2 GOUTTES", "MASSAGE DE 90 SECONDES", "LIVRAISON DISCRÈTE"]
    tagline = "CE QU'ELLE A RESSENTI L'A SURPRISE ELLE-MÊME."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST5", path=WINNER_COPY)

    c = Composer(p("TST5_back_curve"))
    partial_scrim(c, 0.40, 0.0, 1.0, 0.46, opacity=0.40)
    y = quote_block(c, 0.43, 0.075, quote, size=0.030)
    y += 0.045
    bullet_size = 0.023
    for i, b in enumerate(bullets):
        checklist_line(c, 0.43, y + i * 0.046, b, size=bullet_size)
    c.text(0.43, 0.415, tagline, key="sans-bold", size=0.021, color=PINK, shadow=True)
    c.save(o("TST5_back_curve"))


@job
def TST6_toes_curl():
    quote = [("Ses orteils se sont", WHITE), ("recroquevillés en une minute.", PINK)]
    bullets = ["SANS ABONNEMENT", "ORIGINE VÉGÉTALE", "60 JOURS D'ESSAI, SANS RISQUE"]
    tagline = "ELLE NE S'Y ATTENDAIT PAS."
    assert_not_winner_copy([t for t, _ in quote] + bullets + [tagline],
                           label="TST6", path=WINNER_COPY)

    c = Composer(p("TST6_toes_curl"))
    partial_scrim(c, 0.0, 0.0, 1.0, 0.42, opacity=0.35)
    y = quote_block(c, None, 0.075, quote, size=0.042, align_center=0.5)
    y += 0.035
    bullet_size = 0.026
    for i, b in enumerate(bullets):
        w = c.measure(b, "sans-bold", bullet_size) + c.measure("✓", "sym", bullet_size) + 0.013
        checklist_line(c, 0.5 - w / 2, y + i * 0.038, b, size=bullet_size)
    c.band(0.93, 0.985, fill=(0.45, 0.02, 0.28), opacity=1.0)
    c.centered(0.965, tagline, key="sans-bold", size=0.026, color=WHITE, shadow=False,
               center_on=0.5)
    c.save(o("TST6_toes_curl"))


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
