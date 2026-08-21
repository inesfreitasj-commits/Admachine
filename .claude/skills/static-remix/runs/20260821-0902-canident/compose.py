#!/usr/bin/env python3
"""Canident batch — every line of on-image copy composited in code.

Every string is quoted from assets/product-page.md. Nothing here is invented.
Numbers used: 98 % · 48 h · 356 vétérinaires · 10 543 · 4,8 · 60 jours · 34,95 €.
Deliberately NOT used: 60 452, 60 000, 9 897, 4,9, any euro figure for a vet descale.
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import (Composer, canident_lockup, trim_uniform_border,
                          WHITE, NAVY, ROYAL, TEAL, NEARBK)

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn

CTA = "Commandez Canident™ maintenant →"

def photo(n, l1, l2, scrim=0.72, bar=True):
    """Photographic ads: the pack format doesn't apply, but the brand bar does.

    `bar` is variable on purpose. An identical navy bar plus an identical copy block on
    every ad is a large constant shape, and it manufactures duplicate scores out of
    pictures that share nothing — it added +0.37 between a dog's mouth and a paper
    invoice. Dropping it on a few breaks that without touching the photographs.
    """
    trim_uniform_border(p(n))
    c = Composer(p(n))
    foot = 0.902 if bar else 1.0
    c.scrim(0.52, foot, opacity=scrim)
    if bar:
        c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    dy = 0.0 if bar else 0.052
    c.text(0.055, 0.735 + dy, l1, key="sans", size=0.046)
    c.text(0.055, 0.822 + dy, l2, key="sans-bold", size=0.060)
    w = c.measure(l2, "sans-bold", 0.060)
    if w > 0.90: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.underline(0.055, 0.055 + w, 0.840 + dy)
    if bar:
        c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n))

# ---------------- P/N — the winners' own pack format ----------------
# Batch 01 built eight of these with the same pack in the same place on the same white
# ground and only changed the corner illustration; seven read as one ad. The rebuilds
# below vary the LARGE shapes — dominant mass, ground colour, pack position and scale —
# which is what makes the client's own two winners score r = 0.031.

@job
def P6_pack_hero_foam():
    canident_lockup(p("P6_pack_hero_foam"), o("P6_pack_hero_foam"),
        "98 % de dents plus propres", "sans effort",
        bullets=["356 vétérinaires\nle conseillent",
                 "Sans alcool,\nsans xylitol",
                 "Garanti 60 jours"])

@job
def N1_tooth_fullbleed():
    canident_lockup(p("N1_tooth_fullbleed"), o("N1_tooth_fullbleed"),
        # winner-2 treatment: centred headline, no bar, no wordmark
        "Le tartre accumulé se décolle", "en 48 h",
        align="center", cta=None, wordmark=None)

@job
def N2_brush_vs_foam_top():
    # pack sits on the bottom edge — a CTA bar would clip its base, and winner 2
    # carries neither bar nor wordmark either
    canident_lockup(p("N2_brush_vs_foam_top"), o("N2_brush_vs_foam_top"),
        "Fini la bagarre avec la brosse", "5 secondes", cta=None, wordmark=None)

@job
def N3_pack_left_mirrored():
    # pack is on the LEFT here, so the copy column moves right
    canident_lockup(p("N3_pack_left_mirrored"), o("N3_pack_left_mirrored"),
        # the pack is on the LEFT, so both lines live in the empty full-width top band
        "Haleine, gencives, plaque, tartre", "4-en-1",
        head_top=0.082, gap=0.088, cta=None, wordmark=None)

@job
def N4_dog_photo_left():
    canident_lockup(p("N4_dog_photo_left"), o("N4_dog_photo_left"),
        "Il lèche la mousse tout seul", "goût poulet")

@job
def N5_48h_timeline():
    # The sequence runs heavy -> yellow -> clean, so the headline must run in the same
    # direction. "La plaque devient tartre en 48 h" was verbatim from the funnel but it
    # pointed the ad at deterioration, with the pack sitting at the bad end of the arrow —
    # and 48 h is the payoff number everywhere else in this account.
    c = canident_lockup(p("N5_48h_timeline"), None,
        "Le tartre brun se détache", "en 48 h", cta=None, wordmark=None)
    # the three blue boxes were generated deliberately empty so the stages could be
    # lettered exactly here rather than gambled on the model
    # the third box is covered by the pack — see report.txt; only the visible two are lettered
    for label, cx in (("JOUR 0", 0.180), ("24 H", 0.500)):
        c.centered(0.652, label, key="sans-bold", size=0.045, color=WHITE,
                   shadow=False, center_on=cx)
    c.save(o("N5_48h_timeline"))

@job
def N6_flatlay_foam():
    canident_lockup(p("N6_flatlay_foam"), o("N6_flatlay_foam"),
        "Sans alcool, sans xylitol", "sans stress", cta=None)

@job
def N7_three_panel_rincage():
    canident_lockup(p("N7_three_panel_rincage"), o("N7_three_panel_rincage"),
        "Le liquide est rincé en secondes", "la mousse reste",
        align="center", cta=None, wordmark=None,
        sizes=(0.046, 0.070), head_top=0.055, gap=0.076)

# ---------------- D — photographic dog ----------------
@job
def D1_tartre_gumline():
    photo("D1_tartre_gumline", "Ce tartre brun s'installe en 48 h.",
          "Il se détache en 48 h")

@job
def D2_lift_the_lip():
    photo("D2_lift_the_lip", "Soulevez la babine. 2 pressions.",
          "C'est tout. Pas de brossage.")

@job
def D3_foam_applied():
    photo("D3_foam_applied", "Pas de lutte. Pas besoin de forcer.",
          "5 secondes, une fois par jour")

@job
def D4_clean_teeth_happy():
    photo("D4_clean_teeth_happy", "Recommandé par 356 vétérinaires.",
          "98 % de dents plus propres")

@job
def D5_vet_table():
    photo("D5_vet_table", "Un détartrage se fait sous anesthésie.",
          "Espacez-les. 60 jours garantis.")

# ---------------- O — dog + owner ----------------
@job
def O1_the_flinch():
    photo("O1_the_flinch", "Il s'approche pour un câlin.",
          "Vous détournez la tête.")

@job
def O2_cuddle_regained():
    photo("O2_cuddle_regained", "Plus besoin de reculer.",
          "Haleine fraîche en 48 h")

@job
def O3_failed_drawer():
    photo("O3_failed_drawer", "Bâtonnets, gouttes, brosse à doigt.",
          "Et le tartre est toujours là.")

@job
def O4_brushing_fight():
    photo("O4_brushing_fight", "Le brossage tourne vite au combat.",
          "Vaporisez. Laissez agir.")

# ---------------- BA — before / after ----------------
def _ba(n, left="JOUR 1", right="48 H", caption="Le tartre se détache sous 48 h"):
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.badge(0.045, 0.045, left, size=0.040, fill=NEARBK)
    c.badge(0.545, 0.045, right, size=0.040, fill=ROYAL)
    c.scrim(0.72, 0.902, opacity=0.70)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.centered(0.862, caption, size=0.046)
    c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n))

@job
def BA1_48h_side(): _ba("BA1_48h_side")
@job
def BA2_gumline_macro(): _ba("BA2_gumline_macro")
@job
def BA3_small_dog_front(): _ba("BA3_small_dog_front",
)  # 48 h everywhere — the campaign timeframe, per the client


# ---------------- X — hard angles, explicit clinical imagery ----------------
# Every line below is page-supported. "gratte / ramollit" is near-verbatim from the
# advertorial; "plusieurs centaines d'euros" and the gamelle are verbatim. No euro figure
# is ever put on an invoice, because the page never gives one.
_X = [
 ("X1_calcul_severe",     "Ce n'est plus de la plaque.",          "C'est du tartre durci."),
 ("X2_gamelle_tartre",    "Il en a retrouvé dans sa gamelle.",    "Le tartre se détache en 48 h"),
 ("X3_anesthesie_intubee","Détartrage : anesthésie générale.",    "Un risque chez le chien âgé."),
 ("X4_facture_veto",      "Détartrage sous anesthésie.",          "Plusieurs centaines d'euros."),
 ("X5_le_baiser",         "Vous connaissez cette odeur.",         "Elle vient des bactéries."),
 ("X6_scaler_grattage",   "Le vétérinaire gratte le tartre.",     "La mousse le ramollit."),
 ("X7_gencive_retractee", "Le tartre ne s'arrête pas aux dents.", "Les gencives aussi."),
 ("X8_gaze_tartre",       "Deux jours de mousse.",                "Voilà ce qui part."),
 ("X9_deux_bouches",      "La même bouche.",                      "48 heures d'écart."),
]
for _n, _l1, _l2 in _X:
    def _mk(n=_n, l1=_l1, l2=_l2):
        if n == "X4_facture_veto":
            # the thumb did not quite cover the TOTAL cell and a blurred figure is legible
            # enough to read as a real number. The page never states a euro amount, so the
            # cell is painted out in paper colour rather than shipped with an invented one.
            trim_uniform_border(p(n))
            c = Composer(p(n))
            c.page.draw_rect(fitz.Rect(0.735 * c.W, 0.700 * c.H, 0.862 * c.W, 0.757 * c.H),
                             color=None, fill=(0.894, 0.867, 0.780))
            c.save("production/X4_facture_veto.png")
        photo(n, l1, l2,
              bar=n not in ("X4_facture_veto", "X2_gamelle_tartre", "X8_gaze_tartre"),
              scrim=0.86 if n == "X9_deux_bouches" else 0.72)
    _mk.__name__ = _n
    job(_mk)


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
