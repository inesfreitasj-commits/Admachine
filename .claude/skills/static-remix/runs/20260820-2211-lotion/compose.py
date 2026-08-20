#!/usr/bin/env python3
"""Ferméa batch — composite every line of on-image copy in code.

Every string below is quoted from assets/product-page.md. Nothing here is invented.
Run: python3 compose.py [name ...]
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, hook_lockup, WHITE, BLACK, RED, INK, GOLD, TPGREEN

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
KICK = ("VAINQUEUR DU TEST", "2026")

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn


# ---------------------------------------------------------------- A
@job
def A1_shelf_test_winner():
    """No overlay — the client's own shelf winner carries no text either."""
    import shutil; shutil.copyfile(p("A1_shelf_test_winner"), o("A1_shelf_test_winner"))

@job
def A2_shelf_rupture_stock():
    # The copy goes on the empty grey shelf-back panel, NOT over the bottom of the
    # frame — a gradient there would sit on the white rail price labels and the
    # headline would be unreadable, which is the whole point of this ad.
    c = Composer(p("A2_shelf_rupture_stock"))
    c.scrim(0.0, 0.20, opacity=0.45, top_down=True)
    c.tricolore(cx=0.0741, cy=0.0970, r=0.0404)
    c.text(0.1253, 0.0966, KICK[0], size=0.0377)
    c.text(0.1253, 0.1415, KICK[1], size=0.0377)
    c.rich(0.150, 0.300, [("Ferméa", "sans-bold"), ("™ n'est plus", "sans")], size=0.052)
    c.text(0.150, 0.368, "en rayon.", key="sans", size=0.052)
    c.text(0.150, 0.462, "Disponible uniquement", key="sans-bold", size=0.052)
    c.text(0.150, 0.530, "en ligne", key="sans-bold", size=0.052)
    w = c.measure("en ligne", "sans-bold", 0.052)
    c.underline(0.150, 0.150 + w, 0.546)
    c.save(o("A2_shelf_rupture_stock"))

@job
def A3_shelf_hand_lifting():
    # Solid bar, not a gradient — the bottom of this frame is white price labels.
    c = Composer(p("A3_shelf_hand_lifting"))
    c.scrim(0.0, 0.20, opacity=0.45, top_down=True)
    c.tricolore(cx=0.0741, cy=0.0970, r=0.0404)
    c.text(0.1253, 0.0966, KICK[0], size=0.0377)
    c.text(0.1253, 0.1415, KICK[1], size=0.0377)
    c.band(0.786, 1.0, opacity=0.90)
    c.text(0.0445, 0.868, "16 huiles testées par une dermatologue.", key="sans",
           size=0.0418, shadow=False)
    c.text(0.0445, 0.950, "94 % : peau plus ferme sous 7 jours", key="sans-bold",
           size=0.0526, shadow=False)
    w = c.measure("94 % : peau plus ferme sous 7 jours", "sans-bold", 0.0526)
    c.underline(0.0445, 0.0445 + w, 0.966)
    c.save(o("A3_shelf_hand_lifting"))

@job
def A4_hook_decollete():
    hook_lockup(p("A4_hook_decollete"), o("A4_hook_decollete"),
                [("Peau du cou et du décolleté ", "sans"), ("relâchée", "sans-bold"), (" ?", "sans")],
                "les 5 huiles les plus efficaces")

@job
def A5_hook_inner_arm():
    hook_lockup(p("A5_hook_inner_arm"), o("A5_hook_inner_arm"),
                [("Une dermatologue a testé ", "sans"), ("16", "sans-bold"), (" huiles :", "sans")],
                "voici son classement")

@job
def A6_hook_hand_back():
    hook_lockup(p("A6_hook_hand_back"), o("A6_hook_hand_back"),
                [("Peau fine, relâchée, « papier froissé » ?", "sans")],
                "les 5 huiles les mieux notées")


# ---------------------------------------------------------------- B
@job
def B1_ingredients():
    c = Composer(p("B1_ingredients"))
    c.text(0.062, 0.088, "94 % ont constaté une peau", key="sans-bold", size=0.058,
           color=INK, shadow=False)
    c.text(0.062, 0.158, "plus ferme sous 7 jours", key="sans-bold", size=0.058,
           color=INK, shadow=False)
    for line, y in (("BAKUCHIOL · ROSE MUSQUÉE · PÉPINS DE RAISIN", 0.930),
                    ("GRENADE · ONAGRE · VITAMINE E · SQUALANE", 0.978)):
        c.centered(y, line, size=0.033, color=GOLD, shadow=False)
    c.save(o("B1_ingredients"))

@job
def B2_bathroom_native():
    """No text — this one only works if nobody can tell it is an ad."""
    import shutil; shutil.copyfile(p("B2_bathroom_native"), o("B2_bathroom_native"))

@job
def B3_hydration_not_enough():
    c = Composer(p("B3_hydration_not_enough"))
    l1, l2 = "Une simple hydratation", "ne suffit pas"
    c.text(0.055, 0.098, l1, key="sans-bold", size=0.062, color=INK, shadow=False)
    c.text(0.055, 0.172, l2, key="sans-bold", size=0.062, color=INK, shadow=False)
    c.centered(0.848, "UNE CRÈME ORDINAIRE", size=0.030, color=INK, shadow=False,
               center_on=0.25)   # the right column needs no label — the pack says it
    c.badge(0, 0.888, "94 % ONT UNE PEAU PLUS FERME SOUS 7 JOURS", size=0.032,
            fill=RED, center_on=0.5)
    c.save(o("B3_hydration_not_enough"))

@job
def B4_trustpilot_authority():
    c = Composer(p("B4_trustpilot_authority"))
    x = 0.520
    c.text(x, 0.300, "4,8", key="sans-bold", size=0.150, color=INK, shadow=False)
    c.stars(x, 0.330, 5, size=0.048)
    c.text(x, 0.470, "sur Trustpilot", key="sans-bold", size=0.040, color=INK, shadow=False)
    c.text(x, 0.535, "Basé sur 60 452 avis vérifiés", key="sans", size=0.032, color=INK, shadow=False)
    c.text(x, 0.585, "Plus de 60 000 clients vérifiés", key="sans", size=0.032, color=INK, shadow=False)
    c.badge(x, 0.640, "GARANTIE 60 JOURS", size=0.032, fill=INK)
    c.save(o("B4_trustpilot_authority"))

@job
def B5_test_winner_hero():
    c = Composer(p("B5_test_winner_hero"))
    c.tricolore(cx=0.0741, cy=0.0970, r=0.0404)
    c.text(0.1253, 0.0966, KICK[0], size=0.0377, color=INK, shadow=False)
    c.text(0.1253, 0.1415, KICK[1], size=0.0377, color=INK, shadow=False)
    c.badge(0.0445, 0.860, "#1 CHOIX DE LA DERMATOLOGUE", size=0.036, fill=RED)
    c.save(o("B5_test_winner_hero"))


# ---------------------------------------------------------------- C
for _n in ("C1_papier_froisse", "C2_upper_arm_bathroom", "C3_pinch_test"):
    def _passthrough(n=_n):
        """No text, no brand — pure curiosity native."""
        import shutil; shutil.copyfile(p(n), o(n))
    _passthrough.__name__ = _n
    job(_passthrough)

@job
def C4_knees_garden():
    hook_lockup(p("C4_knees_garden"), o("C4_knees_garden"),
                [("Cuisses et genoux qui se ", "sans"), ("relâchent", "sans-bold"), (" ?", "sans")],
                "Une dermatologue a testé 16 huiles")

@job
def C5_pharmacy_aisle():
    hook_lockup(p("C5_pharmacy_aisle"), o("C5_pharmacy_aisle"),
                [("La plupart n'ont jamais été formulées pour ça.", "sans")],
                "16 huiles testées : le classement")


# ---------------------------------------------------------------- D
def _before_after(name):
    c = Composer(p(name))
    c.badge(0.045, 0.045, "JOUR 1", size=0.040, fill=INK)
    c.badge(0.545, 0.045, "JOUR 7", size=0.040, fill=RED)
    c.scrim(0.80, 1.0, opacity=0.68)
    c.centered(0.945, "94 % : peau plus ferme sous 7 jours", size=0.046)
    c.save(o(name))

@job
def D1_ba_forearm(): _before_after("D1_ba_forearm")

@job
def D2_ba_decollete(): _before_after("D2_ba_decollete")

@job
def D3_ugc_holding():
    c = Composer(p("D3_ugc_holding"))
    c.scrim(0.68, 1.0, opacity=0.70)
    c.text(0.055, 0.845, "« Après tant de crèmes essayées,", key="sans-italic", size=0.046)
    c.text(0.055, 0.905, "je suis impressionnée. »", key="sans-italic", size=0.046)
    c.text(0.055, 0.963, "— Françoise G., cliente vérifiée", key="sans-bold", size=0.032)
    c.save(o("D3_ugc_holding"))

@job
def D4_pump_into_palm():
    hook_lockup(p("D4_pump_into_palm"), o("D4_pump_into_palm"),
                [("Sur peau légèrement humide, matin et soir.", "sans")],
                "Peau plus ferme sous 7 jours",
                badge_text=None, kicker=None, scrim=0.70)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
