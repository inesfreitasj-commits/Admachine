#!/usr/bin/env python3
"""ÉveilSens — checklist / strong-claim ad concepts (CKL1-4).

Follow-up on the client's own win_01/win_02 device (product + checkmark bullets + a short
punchy claim, sometimes a guarantee band) — client pointed at those two ads specifically and
asked for more in that register, pushed more aggressive. Every headline/bullet line below is
fresh wording, checked against assets/winner-copy.md via assert_not_winner_copy so nothing
reuses a winning ad's line verbatim (the claim is fine to reuse, proven by their own results;
the words have to move — see that module's docstring). Every fact used (2 gouttes, 90
secondes, sans hormones, sans ordonnance, sans abonnement, garantie 60 jours, 60 452 avis,
+60 000 clientes, livraison discrète, compatible préservatifs) traces to
assets/product-page.md.

Run: python3 compose_ckl.py [name ...]
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, assert_not_winner_copy

SRC, OUT = "production_v2", "final_v2"
os.makedirs(OUT, exist_ok=True)
MAGENTA = (0.66, 0.04, 0.42)
BAND_MAGENTA = (0.45, 0.02, 0.28)
WINNER_COPY = "assets/winner-copy.md"

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn


def checklist_line(c, x, baseline, text, size=0.032, color=MAGENTA):
    end_x = c.text(x, baseline, "✓", key="sym", size=size, color=color, shadow=False)
    c.text(end_x + 0.014, baseline, text, key="sans-bold", size=size, color=color, shadow=False)


def headline_block(c, x, top_baseline, lines, size=0.062, color=MAGENTA, line_gap=1.28,
                    center_on=None):
    """Left-aligned (or centred, if center_on is given) bold headline, one call per line."""
    gap = size * line_gap
    for i, line in enumerate(lines):
        b = top_baseline + i * gap
        if center_on is not None:
            c.centered(b, line, key="sans-bold", size=size, color=color, shadow=False,
                       center_on=center_on)
        else:
            c.text(x, b, line, key="sans-bold", size=size, color=color, shadow=False)
    return top_baseline + len(lines) * gap


def guarantee_band(c, text, y0=0.90, y1=0.965, size=0.032):
    c.band(y0, y1, fill=BAND_MAGENTA, opacity=1.0)
    cy = (y0 + y1) / 2 + size * 0.32
    c.centered(cy, text, key="sans-bold", size=size, color=(1, 1, 1), shadow=False)


@job
def CKL1_20ans_aggressive():
    # No bottom band, no left-text/right-bottle split — this concept's base photo is a
    # flat-lay with the bottle small at the very bottom, huge open ground above it, so the
    # whole "large shape" of the ad differs from win_02's left-text/right-bottle/bottom-band
    # layout (that first attempt scored 0.76 against win_02 and 0.64 against CKL2 — a
    # structural re-render, not just close wording; see report.txt for the full story).
    headline = ["REVIVEZ L'INTENSITÉ", "DE VOS 20 ANS.", "EN 90 SECONDES."]
    bullets = ["2 GOUTTES SUFFISENT", "FORMULE 100 % D'ORIGINE NATURELLE",
               "AUCUNE HORMONE AJOUTÉE", "60 JOURS POUR CHANGER D'AVIS"]
    assert_not_winner_copy(headline + bullets, label="CKL1", path=WINNER_COPY)

    c = Composer(p("CKL1_20ans_aggressive"))
    y = headline_block(c, None, 0.115, headline, size=0.062, center_on=0.5)
    y += 0.045
    bullet_size = 0.034
    widest = max(c.measure(b, "sans-bold", bullet_size) for b in bullets)
    tick_w = c.measure("✓", "sym", bullet_size)
    bx = 0.5 - (tick_w + 0.014 + widest) / 2
    for i, b in enumerate(bullets):
        checklist_line(c, bx, y + i * 0.052, b, size=bullet_size)
    c.save(o("CKL1_20ans_aggressive"))


@job
def CKL2_sans_ordonnance():
    headline = ["AUCUNE ORDONNANCE.", "AUCUNE ATTENTE.", "SEULEMENT 90 SECONDES."]
    bullets = ["AUCUNE HORMONE AJOUTÉE", "AUCUNE ORDONNANCE NÉCESSAIRE", "SANS ABONNEMENT"]
    footer = "+60 000 CLIENTES CONQUISES"
    assert_not_winner_copy(headline + bullets + [footer], label="CKL2", path=WINNER_COPY)

    c = Composer(p("CKL2_sans_ordonnance"))
    y = headline_block(c, 0.055, 0.115, headline, size=0.052)
    y += 0.03
    for i, b in enumerate(bullets):
        checklist_line(c, 0.058, y + i * 0.052, b, size=0.032)
    # a compact pill badge, not a full-width band — win_02's own device is a solid bar the
    # full width of the frame; a badge keeps the guarantee-90-cost proof point without
    # reproducing that same dominant shape.
    c.badge(0, 0.90, footer, key="sans-bold", size=0.030, fill=BAND_MAGENTA,
            color=(1, 1, 1), padx=0.026, pady=0.018, radius=0.5, center_on=0.5)
    c.save(o("CKL2_sans_ordonnance"))


@job
def CKL3_avis_proof():
    # Guarantee folded into the checklist as a 4th bullet rather than a bottom band — see
    # CKL1's comment: a full-width band is the single largest shape win_02 also carries, and
    # dropping it is what actually moves the duplicate-gate score, not the wording.
    headline = ["60 452 AVIS.", "UN SEUL VERDICT."]
    bullets = ["2 GOUTTES", "90 SECONDES", "SENSATIONS DÉCUPLÉES",
               "60 JOURS POUR CHANGER D'AVIS"]
    assert_not_winner_copy(headline + bullets, label="CKL3", path=WINNER_COPY)

    c = Composer(p("CKL3_avis_proof"))
    y = headline_block(c, None, 0.135, headline, size=0.072, center_on=0.5)
    y += 0.045
    # centre the checklist block as a whole: measure widest bullet incl. checkmark+gap
    bullet_size = 0.036
    widest = max(c.measure(b, "sans-bold", bullet_size) for b in bullets)
    tick_w = c.measure("✓", "sym", bullet_size)
    block_w = tick_w + 0.014 + widest
    bx = 0.5 - block_w / 2
    for i, b in enumerate(bullets):
        checklist_line(c, bx, y + i * 0.058, b, size=bullet_size)
    c.save(o("CKL3_avis_proof"))


@job
def CKL4_discreet_aggressive():
    headline = ["PERSONNE NE SAURA.", "VOUS, VOUS LE SAUREZ."]
    bullets = ["LIVRAISON DISCRÈTE", "100 % D'ORIGINE NATURELLE", "COMPATIBLE PRÉSERVATIFS"]
    footer = "60 JOURS POUR CHANGER D'AVIS. REMBOURSÉE."
    assert_not_winner_copy(headline + bullets + [footer], label="CKL4", path=WINNER_COPY)

    c = Composer(p("CKL4_discreet_aggressive"))
    y = headline_block(c, None, 0.145, headline, size=0.040, center_on=0.735)
    y += 0.035
    for i, b in enumerate(bullets):
        checklist_line(c, 0.503, y + i * 0.052, b, size=0.030)
    guarantee_band(c, footer)
    c.save(o("CKL4_discreet_aggressive"))


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
