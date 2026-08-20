#!/usr/bin/env python3
"""Ferméa batch 2 — every line composited in code. All copy quoted from the funnel."""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import (Composer, hook_lockup, trim_uniform_border,
                          WHITE, BLACK, RED, INK, GOLD)

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
KICK = ("VAINQUEUR DU TEST", "2026")
p = lambda n: f"{SRC}/{n}.png"
o = lambda n: f"{OUT}/{n}.png"
jobs = {}
def job(f): jobs[f.__name__] = f; return f

def kicker(c, color=WHITE, shadow=True, scrim=0.45):
    if scrim: c.scrim(0.0, 0.20, opacity=scrim, top_down=True)
    c.tricolore(cx=0.0741, cy=0.0970, r=0.0404)
    c.text(0.1253, 0.0966, KICK[0], size=0.0377, color=color, shadow=shadow)
    c.text(0.1253, 0.1415, KICK[1], size=0.0377, color=color, shadow=shadow)

def bottom_band(c, l1, l2, top=0.786):
    """Solid bar + light line + bold underlined line. For busy or white backgrounds."""
    c.band(top, 1.0, opacity=0.90)
    c.text(0.0445, top + 0.082, l1, key="sans", size=0.0418, shadow=False)
    c.text(0.0445, top + 0.164, l2, key="sans-bold", size=0.0526, shadow=False)
    w = c.measure(l2, "sans-bold", 0.0526)
    if w > 0.94: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.underline(0.0445, 0.0445 + w, top + 0.180)

def passthrough(*names):
    for n in names:
        def f(n=n):
            trim_uniform_border(p(n)); shutil.copyfile(p(n), o(n))
        f.__name__ = n; job(f)

# ---------------- shelves ----------------
@job
def S1_last_bottle():
    c = Composer(p("S1_last_bottle")); kicker(c)
    bottom_band(c, "Il ne reste que 4 flacons.", "Disponible uniquement en ligne")
    c.save(o("S1_last_bottle"))

# S2's handwritten note IS the message — an overlay would only make it look like an ad.
passthrough("S2_handwritten_note")

# ---------------- UGC ----------------
@job
def U1_ugc_kitchen():
    trim_uniform_border(p("U1_ugc_kitchen"))
    c = Composer(p("U1_ugc_kitchen")); c.scrim(0.68, 1.0, opacity=0.72)
    c.text(0.055, 0.845, "« Mes bras paraissent beaucoup", key="sans-italic", size=0.044)
    c.text(0.055, 0.902, "plus fermes et lisses. »", key="sans-italic", size=0.044)
    c.text(0.055, 0.962, "— Nathalie L., cliente vérifiée", key="sans-bold", size=0.032)
    c.save(o("U1_ugc_kitchen"))

@job
def U2_ugc_arm_show():
    trim_uniform_border(p("U2_ugc_arm_show"))
    c = Composer(p("U2_ugc_arm_show"))
    c.badge(0, 0.055, "94 % ONT UNE PEAU PLUS FERME SOUS 7 JOURS", size=0.034,
            fill=RED, center_on=0.5)
    c.scrim(0.72, 1.0, opacity=0.72)
    c.text(0.055, 0.888, "« Ma peau paraît maintenant plus", key="sans-italic", size=0.044)
    c.text(0.055, 0.945, "douce et tonique. »", key="sans-italic", size=0.044)
    c.save(o("U2_ugc_arm_show"))

passthrough("U3_ugc_car", "N1_parcel_doormat", "N2_bedside", "N3_oiled_arm")

# ---------------- aggressive ----------------
@job
def X1_tout_essaye():
    trim_uniform_border(p("X1_tout_essaye"))
    hook_lockup(p("X1_tout_essaye"), o("X1_tout_essaye"),
                [("« J'ai tout essayé… rien ne fonctionne. »", "sans")],
                "Une dermatologue a testé 16 huiles", scrim=0.72)

@job
def X2_lotion_fails():
    trim_uniform_border(p("X2_lotion_fails"))
    hook_lockup(p("X2_lotion_fails"), o("X2_lotion_fails"),
                [("Une simple hydratation ", "sans"), ("ne suffit pas", "sans-bold")],
                "94 % : peau plus ferme sous 7 jours", scrim=0.72)

# ---------------- new concepts ----------------
@job
def Y1_derm_exam():
    trim_uniform_border(p("Y1_derm_exam"))
    hook_lockup(p("Y1_derm_exam"), o("Y1_derm_exam"),
                [("Elle a passé en revue ", "sans"), ("16", "sans-bold"), (" huiles pour le corps.", "sans")],
                "Une seule cible la fermeté", scrim=0.70)

@job
def Y2_three_ages():
    trim_uniform_border(p("Y2_three_ages"))
    c = Composer(p("Y2_three_ages"))
    for label, cx in (("40 ANS", 1/6), ("55 ANS", 3/6), ("70 ANS", 5/6)):
        c.badge(0, 0.042, label, size=0.038, fill=INK, center_on=cx)
    c.band(0.845, 1.0, opacity=0.90)
    c.centered(0.905, "Bras, cuisses, genoux, décolleté.", key="sans", size=0.040,
               shadow=False)
    w = c.centered(0.968, "16 huiles testées : le classement", size=0.049, shadow=False)
    c.underline(0.5 - w / 2, 0.5 + w / 2, 0.982)
    c.save(o("Y2_three_ages"))

@job
def Y3_cardboard_sign():
    trim_uniform_border(p("Y3_cardboard_sign"))
    c = Composer(p("Y3_cardboard_sign")); kicker(c)
    c.save(o("Y3_cardboard_sign"))   # the sign carries the message

passthrough("Y4_phone_article")

@job
def Y5_five_oils_table():
    trim_uniform_border(p("Y5_five_oils_table"))
    c = Composer(p("Y5_five_oils_table"))
    c.centered(0.088, "16 huiles testées.", key="sans", size=0.048, color=INK, shadow=False)
    c.centered(0.152, "Voici les 5 finalistes.", key="sans-bold", size=0.048, color=INK,
               shadow=False)
    c.badge(0.045, 0.865, "#1 CHOIX DE LA DERMATOLOGUE", size=0.036, fill=RED)
    c.save(o("Y5_five_oils_table"))

@job
def Y6_macro_texture():
    trim_uniform_border(p("Y6_macro_texture"))
    hook_lockup(p("Y6_macro_texture"), o("Y6_macro_texture"),
                [("C'est ça, la peau « papier froissé ».", "sans")],
                "16 huiles testées : le classement", scrim=0.72)

if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
