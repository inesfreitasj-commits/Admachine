#!/usr/bin/env python3
"""Duréon batch — composite every line of on-image copy in code.

Every claim quoted from assets/product-page.md. Nothing here is invented. Ingredient
callouts use ONLY the label's three ingredients (fenugrec, riz, L-arginine) — the sales
page's "algues marines" mechanism claim is deliberately excluded, see product-page.md.

Four raw renders (DR1, DR2, CMP2, CMP3) kept garbling their own small ingredient-block text
after 4-5 regenerations each — a different word broken each time, never all correct
together. Rather than keep gambling, that block is blurred with Composer.soften() (the
established fix this session for "readable nonsense" on a photographed prop) and the
correct ingredient line is composited fresh in code where the layout allows it.

Run: python3 compose.py [name ...]
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, assert_not_winner_copy, WHITE, BLACK, RED, INK, crop_to, pad_square

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
CORPUS = "assets/winner-copy.md"
NAVY = (0.09, 0.20, 0.36)

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def check(lines, label): assert_not_winner_copy(lines, path=CORPUS, label=label)
def passthrough(n):
    import shutil; shutil.copyfile(p(n), o(n))

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn


# ---------------------------------------------------------------- before/after (BA1-BA4)
def _before_after(name):
    c = Composer(p(name))
    c.badge(0.045, 0.045, "AVANT", size=0.038, fill=INK)
    c.badge(0.545, 0.045, "APRÈS", size=0.038, fill=RED)
    c.scrim(0.82, 1.0, opacity=0.68)
    claim = "Érections 98 % plus fermes en 43 secondes"
    check([claim], f"{name} claim")
    c.centered(0.945, claim, size=0.042)
    c.save(o(name))

for _n in ("BA1_avant_apres_couple", "BA2_avant_apres_solo",
           "BA3_avant_apres_office", "BA4_avant_apres_outdoor"):
    def _ba(n=_n): _before_after(n)
    _ba.__name__ = _n
    job(_ba)


# ---------------------------------------------------------------- testimonials (T1-T3)
@job
def T1_testimonial_nicolas():
    c = Composer(p("T1_testimonial_nicolas"))
    c.scrim(0.68, 1.0, opacity=0.72)
    l1 = "« Dès la première utilisation,"
    l2 = "j'ai eu l'impression que mon corps se réveillait. »"
    attr = "— Nicolas D., client vérifié"
    check([l1 + " " + l2, attr], "T1 testimonial")
    c.text(0.050, 0.845, l1, key="sans-italic", size=0.040)
    c.text(0.050, 0.895, l2, key="sans-italic", size=0.034)
    c.text(0.050, 0.958, attr, key="sans-bold", size=0.030)
    c.save(o("T1_testimonial_nicolas"))

@job
def T2_testimonial_philippe():
    c = Composer(p("T2_testimonial_philippe"))
    c.scrim(0.68, 1.0, opacity=0.72)
    l1 = "« J'ai eu l'impression d'avoir"
    l2 = "à nouveau 25 ans pendant quatre heures. »"
    attr = "— Philippe, 60 ans, client vérifié"
    check([l1 + " " + l2, attr], "T2 testimonial")
    c.text(0.050, 0.845, l1, key="sans-italic", size=0.040)
    c.text(0.050, 0.895, l2, key="sans-italic", size=0.034)
    c.text(0.050, 0.958, attr, key="sans-bold", size=0.030)
    c.save(o("T2_testimonial_philippe"))

@job
def T3_testimonial_alain():
    # Structurally distinct from T1/T2: a top band, not a bottom scrim.
    c = Composer(p("T3_testimonial_alain"))
    c.band(0.0, 0.24, fill=INK, opacity=0.80)
    l1 = "« C'était comme si mon corps se"
    l2 = "réveillait après des années de silence. »"
    attr = "— Alain D., client vérifié"
    check([l1 + " " + l2, attr], "T3 testimonial")
    c.text(0.050, 0.075, l1, key="sans-italic", size=0.036, shadow=False)
    c.text(0.050, 0.120, l2, key="sans-italic", size=0.032, shadow=False)
    c.text(0.050, 0.180, attr, key="sans-bold", size=0.028, shadow=False)
    c.save(o("T3_testimonial_alain"))


# ---------------------------------------------------------------- doctor authority (DR1-2)
@job
def DR1_doctor_delorme():
    c = Composer(p("DR1_doctor_delorme"))
    c.soften(0.435, 0.585, 0.580, 0.735, radius=0.022)  # blur the garbled ingredient block
    quote1 = "« La circulation sanguine joue un rôle"
    quote2 = "essentiel dans la réponse érectile. »"
    attr = "— Dr Claire Delorme, sexologue"
    check([quote1 + " " + quote2, attr], "DR1 quote")
    c.scrim(0.0, 0.22, opacity=0.55, top_down=True)
    c.text(0.045, 0.075, quote1, size=0.036)
    c.text(0.045, 0.120, quote2, size=0.036)
    c.text(0.045, 0.170, attr, key="sans-bold", size=0.028)
    c.save(o("DR1_doctor_delorme"))

@job
def DR2_recommande_badge():
    c = Composer(p("DR2_recommande_badge"))
    c.soften(0.375, 0.460, 0.595, 0.750, radius=0.024)  # blur the garbled ingredient block
    claim = "RECOMMANDÉ PAR 569 SEXOLOGUES FRANÇAIS"
    check([claim], "DR2 badge")
    c.badge(0.045, 0.045, claim, size=0.030, fill=RED, center_on=None)
    c.save(o("DR2_recommande_badge"))


# ---------------------------------------------------------------- comparison (CMP1-3)
@job
def CMP1_pills_vs_spray():
    c = Composer(p("CMP1_pills_vs_spray"))
    c.badge(0.045, 0.045, "AVANT : COMPRIMÉ", size=0.032, fill=INK)
    c.badge(0.545, 0.045, "DURÉON : SPRAY", size=0.032, fill=RED)
    c.band(0.86, 1.0, fill=WHITE, opacity=0.92)
    l = "30 à 45 min d'attente"
    r = "30 à 43 secondes"
    check([l, r], "CMP1 labels")
    c.text(0.045, 0.925, l, key="sans-bold", size=0.038, color=INK, shadow=False)
    c.text(0.545, 0.925, r, key="sans-bold", size=0.038, color=INK, shadow=False)
    c.save(o("CMP1_pills_vs_spray"))

@job
def CMP2_hand_choice():
    c = Composer(p("CMP2_hand_choice"))
    c.soften(0.545, 0.340, 0.870, 0.850, radius=0.030)  # blur the whole label (tilted bottle
    # kept missing edges with a tight rect; the wordmark stays soft-focus, which reads as a
    # normal shallow depth of field rather than a defect)
    c.soften(0.535, 0.575, 0.660, 0.635, radius=0.030, feather=0.10)  # second, tight pass —
    # the wide feather on the big rect above was diluting mid-patch strength right where the
    # "30 ml / spray" line sits; a small rect with a small feather guarantees full strength
    l1 = "Pourquoi choisir un comprimé"
    l2 = "quand une pulvérisation suffit ?"
    check([l1 + " " + l2], "CMP2 claim")
    c.scrim(0.0, 0.24, opacity=0.55, top_down=True)
    c.centered(0.075, l1, size=0.036)
    c.centered(0.135, l2, size=0.036)
    c.save(o("CMP2_hand_choice"))

@job
def CMP3_clock_wait_time():
    c = Composer(p("CMP3_clock_wait_time"))
    c.soften(0.790, 0.660, 0.935, 0.805, radius=0.022)  # blur the garbled ingredient sub-line
    c.badge(0.045, 0.045, "AVANT", size=0.036, fill=INK)
    c.badge(0.545, 0.045, "DURÉON", size=0.036, fill=RED)
    c.save(o("CMP3_clock_wait_time"))


# ---------------------------------------------------------------- science / ingredients
@job
def SCI1_science_explained():
    c = Composer(p("SCI1_science_explained"))
    c.scrim(0.72, 1.0, opacity=0.68)
    lines = ["favorise la microcirculation", "soutient la souplesse vasculaire",
             "favorise l'oxygénation locale"]
    check(lines, "SCI1 checklist")
    y = 0.825
    for line in lines:
        c.text(0.055, y, f"✓ {line}", key="sans-bold", size=0.036)
        y += 0.060
    c.save(o("SCI1_science_explained"))

@job
def SCI2_ingredients_macro():
    c = Composer(p("SCI2_ingredients_macro"))
    line = "Extrait de fenugrec · Extrait de riz · L-Arginine"
    check([line], "SCI2 ingredients")
    c.badge(0.045, 0.045, line, size=0.028, fill=INK, center_on=None)
    c.save(o("SCI2_ingredients_macro"))


# ---------------------------------------------------------------- winning-ad device (W1-6)
def _hook(name, claim, footer):
    c = Composer(p(name))
    check([claim, footer], f"{name} hook")
    c.scrim(0.0, 0.24, opacity=0.55, top_down=True)
    c.text(0.045, 0.075, claim.split(" / ")[0], key="sans-bold", size=0.044, color=RED)
    if " / " in claim:
        c.text(0.045, 0.135, claim.split(" / ")[1], key="sans-bold", size=0.044, color=RED)
    c.band(0.90, 1.0, fill=WHITE, opacity=0.94)
    c.centered(0.955, footer, size=0.032, color=INK, shadow=False)
    c.save(o(name))

@job
def W1_hook_bold_claim():
    _hook("W1_hook_bold_claim", "ÉRECTIONS 98 % PLUS / FERMES EN 43 SECONDES",
          "Stock limité — commandez en ligne dès maintenant.")

@job
def W2_hook_effect_duration():
    # Structurally distinct from W1/W3/W5: a full-width top band (not a scrim + corner
    # claim) and the footer is a small centred badge instead of a full-width white bar.
    c = Composer(p("W2_hook_effect_duration"))
    claim = "4 heures d'effet & un maximum de plaisir"
    footer = "Satisfait ou remboursé pendant 60 jours."
    check([claim, footer], "W2 hook")
    c.band(0.0, 0.16, fill=RED, opacity=0.92)
    c.centered(0.10, claim, size=0.038)
    c.badge(0, 0.905, footer, size=0.028, fill=INK, center_on=0.5)
    c.save(o("W2_hook_effect_duration"))

@job
def W3_hook_solo_confident():
    # Crop away the right-side product panel so this stops sharing W1's baked-in
    # split-photo composition — the compositing above already dropped the shared banner,
    # but the raw photo itself still had the same photographic split as W1/W2/W4/W5.
    tmp = "/tmp/w3_cropped.png"
    crop_to(p("W3_hook_solo_confident"), tmp, right=0.66)
    crop_to(tmp, tmp, top=0.17, bottom=0.83)  # center-crop height to match the
    # narrowed width instead of padding — padding picked up an ugly dark bar colour
    c = Composer(tmp)
    claim = "Recommandé par 569 sexologues français"
    check([claim], "W3 hook")
    c.badge(0.045, 0.045, claim, size=0.030, fill=RED, center_on=None)
    c.save(o("W3_hook_solo_confident"))

@job
def W4_hook_woman_outdoor():
    _hook("W4_hook_woman_outdoor", "FINI LA GÊNE AU LIT, / RETROUVEZ CONFIANCE",
          "Plus de 60 000 clients vérifiés.")

@job
def W5_hook_hands_intertwined():
    # Bottom scrim + centred claim only — no top banner, no split, no white bar.
    c = Composer(p("W5_hook_hands_intertwined"))
    l1 = "Érections 98 % plus fermes"
    l2 = "en 43 secondes"
    footer = "Plus de 60 000 clients vérifiés."
    check([l1 + " " + l2, footer], "W5 hook")
    c.scrim(0.68, 1.0, opacity=0.72)
    c.centered(0.845, l1, size=0.044)
    c.centered(0.905, l2, size=0.044)
    c.centered(0.965, footer, size=0.028, color=(0.85, 0.85, 0.85))
    c.save(o("W5_hook_hands_intertwined"))


# ---------------------------------------------------------------- higher-intensity (AGR1-3)
@job
def AGR1_intense_closeup():
    # Corner badge only — distinct from AGR2/AGR3's treatments below.
    c = Composer(p("AGR1_intense_closeup"))
    claim = "Fini la gêne au lit, retrouvez confiance"
    check([claim], "AGR1 claim")
    c.badge(0.045, 0.045, claim, size=0.032, fill=RED, center_on=None)
    c.save(o("AGR1_intense_closeup"))

@job
def AGR2_intense_bedroom():
    # Bottom scrim + centred claim.
    c = Composer(p("AGR2_intense_bedroom"))
    l1 = "Érections 98 % plus fermes"
    l2 = "en 43 secondes"
    check([l1 + " " + l2], "AGR2 claim")
    c.scrim(0.70, 1.0, opacity=0.70)
    c.centered(0.870, l1, size=0.046)
    c.centered(0.935, l2, size=0.046)
    c.save(o("AGR2_intense_bedroom"))

@job
def AGR3_intense_outdoor():
    # Full-width top band + centred claim.
    c = Composer(p("AGR3_intense_outdoor"))
    claim = "Recommandé par 569 sexologues français"
    check([claim], "AGR3 claim")
    c.band(0.0, 0.15, fill=INK, opacity=0.85)
    c.centered(0.095, claim, size=0.034)
    c.save(o("AGR3_intense_outdoor"))


# ---------------------------------------------------------------- native / no text
for _n in ("W6_shelf_rupture_stock",):
    def _pt(n=_n): passthrough(n)
    _pt.__name__ = _n
    job(_pt)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
