#!/usr/bin/env python3
"""VeinoVie batch — every line of on-image copy composited in code.

Every string is quoted from assets/product-page.md.
Numbers used: 97 % · 12 heures · 60 jours · 29,95 € · 4,8 · 9 148 avis.
NOT used: 92 %, 90 %, 4.9, 9 897, the Canadian press logos, the LipLyft table, and every
ingredient except Marronnier d'Inde (the only one all three funnel lists agree on).
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import Composer, trim_uniform_border, WHITE, RED, NEARBK

GREEN = (0.106, 0.478, 0.243)   # VeinoVie dark forest green
CREAM = (0.976, 0.965, 0.937)
SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
CTA = "Commandez VeinoVie™ maintenant →"

def native(n):
    """Winners 1, 4 and 5 carry no text at all. Three of five. Respect that."""
    trim_uniform_border(p(n)); shutil.copyfile(p(n), o(n))

def photo(n, l1, l2, bar=True, scrim=0.72):
    """Bar varies across the set on purpose — an identical bar on every ad manufactures
    duplicate scores out of pictures that share nothing (learned on the last product)."""
    trim_uniform_border(p(n))
    c = Composer(p(n))
    foot = 0.902 if bar else 1.0
    c.scrim(0.52, foot, opacity=scrim)
    if bar: c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
    dy = 0.0 if bar else 0.052
    c.text(0.055, 0.735 + dy, l1, key="sans", size=0.046)
    w = c.measure(l2, "sans-bold", 0.060)
    if w > 0.90: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.text(0.055, 0.822 + dy, l2, key="sans-bold", size=0.060)
    c.underline(0.055, 0.055 + w, 0.840 + dy)
    if bar: c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n))

def cream_head(n, l1, l2, top=0.098):
    """Winner 2's device: a dark-green question set on the empty cream top third."""
    trim_uniform_border(p(n))
    c = Composer(p(n))
    for t, y, k in ((l1, top, "sans-bold"), (l2, top + 0.082, "sans-bold")):
        if c.measure(t, k, 0.062) > 0.92:
            raise SystemExit(f'"{t}" too wide')
        c.centered(y, t, key=k, size=0.062, color=GREEN, shadow=False)
    c.save(o(n))

# ---------------- A — variations on the winners ----------------
@job
def A1_ugc_ba_kitchen(): native("A1_ugc_ba_kitchen")
@job
def A2_ugc_ba_evening(): native("A2_ugc_ba_evening")

@job
def A3_vector_ankle_question():
    cream_head("A3_vector_ankle_question",
               "Chevilles gonflées le soir ?", "Voici pourquoi elles gonflent.")
@job
def A4_vector_sock_groove():
    cream_head("A4_vector_sock_groove",
               "La marque des chaussettes ?", "C'est de la rétention d'eau.")

@job
def A5_pack_legs_arrows():
    trim_uniform_border(p("A5_pack_legs_arrows"))
    c = Composer(p("A5_pack_legs_arrows"))
    c.text(0.055, 0.105, "CHEVILLES GONFLÉES ?", key="sans-bold", size=0.072,
           color=GREEN, shadow=False)
    c.text(0.055, 0.192, "C'EST FINI.", key="sans-bold", size=0.072, color=NEARBK, shadow=False)
    c.badge(0, 0.905, "97 % DE GONFLEMENT EN MOINS EN 12 H",
            size=0.034, fill=GREEN, center_on=0.5)
    c.save(o("A5_pack_legs_arrows"))

@job
def A6_thermal_scanner(): native("A6_thermal_scanner")
@job
def A7_doppler_ankle(): native("A7_doppler_ankle")

# ---------------- B — native, no text, no product ----------------
for _n in ("B1_sock_groove_real","B2_shoe_wont_fit","B3_compression_stockings",
           "B4_feet_up_tv","B5_diuretics_table"):
    def _mk(n=_n): native(n)
    _mk.__name__ = _n; job(_mk)

# ---------------- C — new concepts carrying copy ----------------
@job
def C1_four_crossed_out():
    trim_uniform_border(p("C1_four_crossed_out"))
    c = Composer(p("C1_four_crossed_out"))
    for cx, cy in ((0.25, 0.25), (0.75, 0.25), (0.25, 0.72), (0.75, 0.72)):
        r = 0.085
        c.page.draw_circle(fitz.Point(cx * c.W, cy * c.H), r * c.H,
                           color=RED, width=0.011 * c.H, fill=None)
        for dx, dy in ((1, 1), (1, -1)):
            k = r * 0.62
            c.page.draw_line(fitz.Point((cx) * c.W - dx * k * c.H, cy * c.H - dy * k * c.H),
                             fitz.Point((cx) * c.W + dx * k * c.H, cy * c.H + dy * k * c.H),
                             color=RED, width=0.011 * c.H)
    c.band(0.90, 1.0, fill=GREEN, opacity=1.0)
    c.centered(0.958, "Aucune ne traite la vraie cause.", key="sans-bold",
               size=0.046, color=WHITE, shadow=False)
    c.save(o("C1_four_crossed_out"))

@job
def C2_pills_vs_stockings():
    trim_uniform_border(p("C2_pills_vs_stockings"))
    c = Composer(p("C2_pills_vs_stockings"))
    c.centered(0.108, "Les comprimés vident l'eau.", key="sans-bold", size=0.056,
               color=NEARBK, shadow=False)
    c.centered(0.178, "Les bas la déplacent.", key="sans-bold", size=0.056,
               color=NEARBK, shadow=False)
    c.badge(0, 0.885, "AUCUN NE TRAITE LA CAUSE", size=0.036, fill=GREEN, center_on=0.5)
    c.save(o("C2_pills_vs_stockings"))

@job
def C3_timeline_three_stages():
    trim_uniform_border(p("C3_timeline_three_stages"))
    c = Composer(p("C3_timeline_three_stages"))
    c.centered(0.115, "97 % de gonflement en moins", key="sans-bold", size=0.058,
               color=GREEN, shadow=False)
    for label, cx in (("JOUR 0", 0.185), ("12 H", 0.5), ("4 SEMAINES", 0.815)):
        c.badge(0, 0.845, label, size=0.036, fill=GREEN, center_on=cx)
    c.save(o("C3_timeline_three_stages"))

@job
def C4_authority_card():
    trim_uniform_border(p("C4_authority_card"))
    c = Composer(p("C4_authority_card"))
    x = 0.645
    c.text(x, 0.300, "4,8", key="sans-bold", size=0.150, color=NEARBK, shadow=False)
    c.stars(x, 0.330, 5, size=0.046)
    c.text(x, 0.468, "sur Trustpilot", key="sans-bold", size=0.038, color=NEARBK, shadow=False)
    c.text(x, 0.528, "Basé sur 9 148 avis", key="sans", size=0.031, color=NEARBK, shadow=False)
    c.text(x, 0.575, "vérifiés", key="sans", size=0.031, color=NEARBK, shadow=False)
    c.badge(x, 0.625, "GARANTIE 60 JOURS", size=0.028, fill=GREEN, padx=0.014)
    c.save(o("C4_authority_card"))

@job
def C5_suedoises_secret():
    trim_uniform_border(p("C5_suedoises_secret"))
    c = Composer(p("C5_suedoises_secret"))
    c.text(0.055, 0.150, "Les Suédoises", key="sans-bold", size=0.070, color=NEARBK, shadow=False)
    c.text(0.055, 0.235, "utilisent déjà ce", key="sans-bold", size=0.070, color=NEARBK, shadow=False)
    c.text(0.055, 0.325, "secret", key="sans-bold", size=0.070, color=NEARBK, shadow=False)
    c.text(0.055, 0.412, "CIRCULATOIRE", key="sans-bold", size=0.070, color=GREEN, shadow=False)
    c.badge(0.055, 0.860, "GARANTIE SATISFAIT OU REMBOURSÉ", size=0.032, fill=GREEN)
    c.save(o("C5_suedoises_secret"))

# ---------------- D ----------------
@job
def D1_ba_ankles_pair():
    trim_uniform_border(p("D1_ba_ankles_pair"))
    c = Composer(p("D1_ba_ankles_pair"))
    c.badge(0.045, 0.045, "JOUR 0", size=0.040, fill=NEARBK)
    c.badge(0.545, 0.045, "12 H", size=0.040, fill=GREEN)
    c.scrim(0.74, 0.902, opacity=0.70)
    c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
    c.centered(0.868, "97 % de gonflement en moins en 12 h", size=0.046)
    c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o("D1_ba_ankles_pair"))

@job
def D2_woman_holding_tube():
    trim_uniform_border(p("D2_woman_holding_tube"))
    c = Composer(p("D2_woman_holding_tube"))
    c.scrim(0.60, 1.0, opacity=0.74)
    c.text(0.055, 0.812, "« Après seulement deux jours, le", key="sans-italic", size=0.044)
    c.text(0.055, 0.872, "gonflement avait presque disparu. »", key="sans-italic", size=0.044)
    c.text(0.055, 0.940, "— Sylvie Moreou, cliente vérifiée", key="sans-bold", size=0.032)
    c.save(o("D2_woman_holding_tube"))

@job
def D3_applying_cream():
    photo("D3_applying_cream", "Une circulation lymphatique ralentie.",
          "C'est la vraie cause.", bar=False)


# ---------------- R / N — the anatomy fixes and new concepts ----------------
@job
def R1_ba_footstool_pov():
    trim_uniform_border(p("R1_ba_footstool_pov"))
    c = Composer(p("R1_ba_footstool_pov"))
    c.badge(0.045, 0.045, "JOUR 0", size=0.040, fill=NEARBK)
    c.badge(0.545, 0.045, "12 H", size=0.040, fill=GREEN)
    c.scrim(0.74, 0.902, opacity=0.70)
    c.band(0.902, 1.0, fill=GREEN, opacity=1.0)
    c.centered(0.868, "97 % de gonflement en moins en 12 h", size=0.046)
    c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o("R1_ba_footstool_pov"))

@job
def R2_sandal_wont_buckle():
    photo("R2_sandal_wont_buckle", "Elle ne se ferme plus.", "Ce n'est pas la sandale.")

@job
def R3_pack_real_leg():
    trim_uniform_border(p("R3_pack_real_leg"))
    c = Composer(p("R3_pack_real_leg"))
    c.text(0.055, 0.098, "CHEVILLES GONFLÉES ?", key="sans-bold", size=0.060,
           color=GREEN, shadow=False)
    c.text(0.055, 0.172, "C'EST FINI.", key="sans-bold", size=0.060, color=NEARBK, shadow=False)
    c.badge(0, 0.905, "97 % DE GONFLEMENT EN MOINS EN 12 H", size=0.034,
            fill=GREEN, center_on=0.5)
    c.save(o("R3_pack_real_leg"))

@job
def R4_vector_sock_groove():
    cream_head("R4_vector_sock_groove",
               "La marque des chaussettes ?", "C'est de la rétention d'eau.")

@job
def N1_pitting_test():
    photo("N1_pitting_test", "Appuyez sur votre cheville.", "Le creux reste ?", bar=False)

@job
def N2_prescription():
    photo("N2_prescription", "« Des diurétiques…", "et peut-être à vie. »")

@job
def N3_bench_shopping():
    photo("N3_bench_shopping", "S'asseoir toutes les quinze minutes.",
          "Ce n'est pas l'âge.", bar=False)

@job
def N4_stairs_pause():
    photo("N4_stairs_pause", "Monter l'escalier devient inconfortable.",
          "C'est la rétention d'eau.")

@job
def N5_thermal_legs(): native("N5_thermal_legs")
@job
def N6_strap_imprint(): native("N6_strap_imprint")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
