#!/usr/bin/env python3
"""Ferméa round 2 — composite every line of on-image copy in code.

All figures quoted from assets/product-page.md (94 %, 7 jours, 60 jours, 4,8 Trustpilot /
60 452 avis, 34,95 €  — the "safest numbers" the fact sheet resolves to). Every composited
line is checked against this run's own winner-copy.md so nothing repeats a winning ad's
exact wording.

Two real defects from the raw art get fixed here rather than by regenerating:
  - P4: the model drew its own fake stars + a garbled "5.36" rating on what should have been
    a blank phone screen. Redacted and replaced with the real 4,8 / 60 452 avis figure.
  - SH1: the model invented a shelf price tag reading "24,90 €" — not the verified 34,95 €.
    Redacted back to blank, matching the neighbouring (genuinely blank) tags in the same shot.

Run: python3 compose.py [name ...]
"""
import sys, os
import pymupdf as fitz
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, hook_lockup, assert_not_winner_copy, WHITE, BLACK, RED, INK, GOLD, TPGREEN

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
CORPUS = "assets/winner-copy.md"

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def check(lines, label): assert_not_winner_copy(lines, path=CORPUS, label=label)
def passthrough(n):
    import shutil; shutil.copyfile(p(n), o(n))

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn


# ---------------------------------------------------------------- before/after (BA1-BA6)
def _before_after(name):
    c = Composer(p(name))
    c.badge(0.045, 0.045, "JOUR 1", size=0.040, fill=INK)
    c.badge(0.545, 0.045, "JOUR 7", size=0.040, fill=RED)
    c.scrim(0.80, 1.0, opacity=0.68)
    claim = "94 % : peau plus ferme sous 7 jours"
    check([claim], f"{name} claim")
    c.centered(0.945, claim, size=0.046)
    c.save(o(name))

for _n in ("BA1_decollete", "BA2_inner_arm_holding", "BA3_hand_back",
           "BA4_thigh", "BA5_stomach_holding", "BA6_knee"):
    def _ba(n=_n): _before_after(n)
    _ba.__name__ = _n
    job(_ba)


# ---------------------------------------------------------------- hook macro (S1-S3)
@job
def S1_decollete_badge():
    l1 = [("Le cou et le décolleté trahissent l'âge en premier.", "sans")]
    l2 = "16 huiles testées, notre classement"
    check([l1[0][0], l2], "S1 hook")
    hook_lockup(p("S1_decollete_badge"), o("S1_decollete_badge"), l1, l2)

@job
def S2_forearm_badge():
    l1 = [("Avant-bras fin, relâché, marqué par les années ?", "sans")]
    l2 = "le classement de 16 huiles corporelles"
    check([l1[0][0], l2], "S2 hook")
    hook_lockup(p("S2_forearm_badge"), o("S2_forearm_badge"), l1, l2)

@job
def S3_hand_badge():
    l1 = [("Mains fines, ridées, marquées par le temps ?", "sans")]
    l2 = "notre sélection parmi 16 huiles"
    check([l1[0][0], l2], "S3 hook")
    hook_lockup(p("S3_hand_badge"), o("S3_hand_badge"), l1, l2)


# ---------------------------------------------------------------- instructional (P1)
@job
def P1_pump_into_palm():
    l1 = [("Quelques gouttes suffisent, matin et soir.", "sans")]
    l2 = "Peau plus ferme en 7 jours"
    check([l1[0][0], l2], "P1 instructional")
    hook_lockup(p("P1_pump_into_palm"), o("P1_pump_into_palm"), l1, l2,
                badge_text=None, kicker=None, scrim=0.70)


# ---------------------------------------------------------------- P4 — real rating on a
# genuinely blank screen (the first render had the model draw its own fake stars and an
# invalid "5,36" score over the top of the thumb; reprompted for a truly blank screen with
# fingers on the bezel only, then the real figure is composited here)
@job
def P4_trustpilot_phone():
    c = Composer(p("P4_trustpilot_phone"))
    c.stars(0.335, 0.270, 5, size=0.048)
    c.text(0.335, 0.380, "4,8", key="sans-bold", size=0.085, color=INK, shadow=False)
    c.text(0.335, 0.430, "sur Trustpilot", key="sans-bold", size=0.030, color=INK, shadow=False)
    c.text(0.335, 0.530, "Basé sur 60 452", key="sans", size=0.028, color=INK, shadow=False)
    c.text(0.335, 0.565, "avis vérifiés", key="sans", size=0.028, color=INK, shadow=False)
    c.save(o("P4_trustpilot_phone"))


# ---------------------------------------------------------------- SH1 — fix fake price
@job
def SH1_shelf_bestseller():
    c = Composer(p("SH1_shelf_bestseller"))
    # The model invented a shelf price tag ("24,90 €") that doesn't match the verified
    # 34,95 €. Redact it back to blank — matching the genuinely blank tags beside it —
    # rather than print an unverified number.
    r = fitz.Rect(0.383 * c.W, 0.801 * c.H, 0.647 * c.W, 0.906 * c.H)
    c.page.draw_rect(r, color=None, fill=WHITE)
    c.band(0.885, 1.0, fill=INK, opacity=0.85)
    claim = "ARTICLE LE PLUS COMMANDÉ"
    check([claim], "SH1 badge")
    c.centered(0.955, claim, size=0.038)
    c.save(o("SH1_shelf_bestseller"))


# ---------------------------------------------------------------- shelf rupture-de-stock
# The handwritten note is baked into the photo itself (per the SU2 lesson this round) —
# no code text needed, code text over a photographed note would look pasted-on.
for _n in ("RS1_shelf_empty_note", "RS2_shelf_last_bottle", "RS3_shelf_last_standing"):
    def _rs(n=_n): passthrough(n)
    _rs.__name__ = _n
    job(_rs)


# ---------------------------------------------------------------- UGC testimonial quote
@job
def UGC1_testimonial_nathalie():
    c = Composer(p("UGC1_testimonial_nathalie"))
    c.scrim(0.68, 1.0, opacity=0.70)
    l1, l2 = "« Mes bras paraissent beaucoup", "plus fermes et lisses. »"
    attr = "— Nathalie L., cliente vérifiée"
    check([l1 + " " + l2, attr], "UGC1 testimonial")
    c.text(0.055, 0.845, l1, key="sans-italic", size=0.046)
    c.text(0.055, 0.905, l2, key="sans-italic", size=0.046)
    c.text(0.055, 0.963, attr, key="sans-bold", size=0.032)
    c.save(o("UGC1_testimonial_nathalie"))

@job
def UGC2_testimonial_caroline():
    c = Composer(p("UGC2_testimonial_caroline"))
    c.scrim(0.68, 1.0, opacity=0.70)
    l1, l2 = "« Ma peau paraît maintenant", "plus douce et tonique. »"
    attr = "— Caroline G., cliente vérifiée"
    check([l1 + " " + l2, attr], "UGC2 testimonial")
    c.text(0.055, 0.845, l1, key="sans-italic", size=0.046)
    c.text(0.055, 0.905, l2, key="sans-italic", size=0.046)
    c.text(0.055, 0.963, attr, key="sans-bold", size=0.032)
    c.save(o("UGC2_testimonial_caroline"))


# ---------------------------------------------------------------- surgical marker / no text
for _n in ("SM1_preop_arm", "SM2_preop_thigh"):
    def _sm(n=_n): passthrough(n)
    _sm.__name__ = _n
    job(_sm)


# ---------------------------------------------------------------- TEST PRODUIT macro (TP1-2)
@job
def TP1_hip_macro():
    l1 = [("Hanches et taille marquées par le temps ?", "sans")]
    l2 = "16 huiles comparées, notre top 5"
    check([l1[0][0], l2], "TP1 hook")
    hook_lockup(p("TP1_hip_macro"), o("TP1_hip_macro"), l1, l2)

@job
def TP2_ankle_macro():
    l1 = [("Chevilles fines, ridées, fragiles ?", "sans")]
    l2 = "le classement complet de 16 huiles"
    check([l1[0][0], l2], "TP2 hook")
    hook_lockup(p("TP2_ankle_macro"), o("TP2_ankle_macro"), l1, l2)


# ---------------------------------------------------------------- native / no text
for _n in ("U1_bathroom_holding", "U2_kitchen_applying", "U3_car_seat",
           "U4_phone_screenshot", "P2_bottle_stones_garden", "P3_bottle_marble_bathroom",
           "SU1_preop_decollete", "SU2_cardboard_sign"):
    def _pt(n=_n): passthrough(n)
    _pt.__name__ = _n
    job(_pt)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
