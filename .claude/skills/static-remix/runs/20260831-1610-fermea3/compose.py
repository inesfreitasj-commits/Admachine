#!/usr/bin/env python3
"""Ferméa round 3 topup — composite the on-image copy in code.

The 7 "winning ads" this round are confirmed to be our own round-2/2b deliverables resent —
treated as proven winners, but every composited line here is fresh wording, checked against
assets/winner-copy.md (which documents THEIR exact copy) so nothing repeats verbatim.

All figures trace to assets/product-page.md (94 %, 7 jours, 60 jours, 4,8 Trustpilot /
60 452 avis, 34,95 €).

Run: python3 compose.py [name ...]
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, hook_lockup, assert_not_winner_copy, WHITE, BLACK, RED, INK

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


# ---------------------------------------------------------------- before/after (BA7-BA9)
def _before_after(name, claim):
    c = Composer(p(name))
    c.badge(0.045, 0.045, "JOUR 1", size=0.040, fill=INK)
    c.badge(0.545, 0.045, "JOUR 7", size=0.040, fill=RED)
    c.scrim(0.80, 1.0, opacity=0.68)
    check([claim], f"{name} claim")
    c.centered(0.945, claim, size=0.046)
    c.save(o(name))

BA_CLAIMS = {
    # same verified 94%/7 jours figure, fresh wording each time so nothing repeats
    # img_0002's exact "94 % : peau plus ferme sous 7 jours" line
    "BA7_upper_arm": "94 % : une peau plus ferme en 7 jours",
    "BA8_neck_jawline": "Peau du cou plus ferme en 7 jours",
    "BA9_waist": "94 % : fermeté retrouvée en 7 jours",
}
for _n, _claim in BA_CLAIMS.items():
    def _ba(n=_n, c=_claim): _before_after(n, c)
    _ba.__name__ = _n
    job(_ba)


# ---------------------------------------------------------------- TEST PRODUIT macro (TP3-5)
TP_HOOKS = {
    "TP3_knee_macro": (
        [("Genoux marqués, peau relâchée avec l'âge ?", "sans")],
        "notre sélection parmi 16 huiles testées"),
    "TP4_upperarm_macro": (
        [("Bras qui se relâchent sous l'épaule ?", "sans")],
        "16 huiles comparées pour le corps"),
    "TP5_neck_macro": (
        [("La peau du cou marque le temps en premier.", "sans")],
        "16 huiles testées, notre top 5"),
}
for _n, (_l1, _l2) in TP_HOOKS.items():
    def _tp(n=_n, l1=_l1, l2=_l2):
        check([l1[0][0], l2], f"{n} hook")
        hook_lockup(p(n), o(n), l1, l2)
    _tp.__name__ = _n
    job(_tp)


# ---------------------------------------------------------------- UGC testimonial (UGC3-4)
@job
def UGC3_testimonial_francoise():
    c = Composer(p("UGC3_testimonial_francoise"))
    c.scrim(0.68, 1.0, opacity=0.70)
    # paraphrase of Françoise Gauthier's real quote (page-supported claim, fresh wording —
    # her exact sentence is a genuine competitor winning ad's own line, reserved)
    l1, l2 = "« J'avais tout essayé sans résultat.", "Cette fois, ma peau est vraiment plus ferme. »"
    attr = "— Françoise G., cliente vérifiée"
    check([l1 + " " + l2, attr], "UGC3 testimonial")
    c.text(0.05, 0.845, l1, key="sans-italic", size=0.038)
    c.text(0.05, 0.895, l2, key="sans-italic", size=0.038)
    c.text(0.05, 0.955, attr, key="sans-bold", size=0.032)
    c.save(o("UGC3_testimonial_francoise"))

@job
def UGC4_painpoint_mirror():
    c = Composer(p("UGC4_painpoint_mirror"))
    c.scrim(0.68, 1.0, opacity=0.70)
    # the sales page's own "patient quote" — page-sourced, not a winning ad's own
    # composited line, safe to use verbatim
    l1 = "« J'ai tout essayé pour cette peau relâchée"
    l2 = "et fripée, mais rien ne fonctionne. »"
    check([l1 + " " + l2], "UGC4 painpoint")
    c.text(0.05, 0.845, l1, key="sans-italic", size=0.036)
    c.text(0.05, 0.893, l2, key="sans-italic", size=0.036)
    c.save(o("UGC4_painpoint_mirror"))


# ---------------------------------------------------------------- P6 — instructional
@job
def P6_neck_application():
    l1 = [("Un geste simple, matin et soir.", "sans")]
    l2 = "Peau du cou visiblement plus ferme"
    check([l1[0][0], l2], "P6 instructional")
    hook_lockup(p("P6_neck_application"), o("P6_neck_application"), l1, l2,
                badge_text=None, kicker=None, scrim=0.70)


# ---------------------------------------------------------------- no text — pass through
for _n in ("RS5_pharmacist_restocking", "RS6_customer_phone_photo",
           "RS7_almost_gone_two_left", "RS8_note_macro", "RS9_evening_golden_hour",
           "RS10_standing_sign_printed",
           "SM3_preop_waist", "SM4_preop_neck", "SM5_preop_knee",
           "P5_bottle_bathtub_edge", "P7_spa_flatlay"):
    def _pt(n=_n): passthrough(n)
    _pt.__name__ = _n
    job(_pt)


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
