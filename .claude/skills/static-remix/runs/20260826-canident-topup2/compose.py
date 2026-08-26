#!/usr/bin/env python3
"""Canident topup 2 — every line composited in code, checked against the winners' copy.

Numbers used: 98 % · 48 h · 356 vétérinaires · 10 543 · 4,8 · 60 jours · 34,95 € (barré 70,00 €).
NOT used: 60 452, 60 000, 9 897, 4,9, any euro figure for a vet descale.
"""
import sys, os, shutil
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
import pymupdf as fitz
from compose_text import (Composer, canident_lockup, trim_uniform_border, pad_square,
                          assert_not_winner_copy, WHITE, NAVY, ROYAL, TEAL, NEARBK, RED)

SRC, OUT, TMP = "production", "final", "/tmp/canident2-work"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"
def t(n): return f"{TMP}/{n}.png"
jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
CTA = "Commandez Canident™ maintenant →"
WINCOPY = "assets/winner-copy.md"
def check(lines, n): assert_not_winner_copy(lines, path=WINCOPY, label=n)


def native(n):
    trim_uniform_border(p(n)); shutil.copyfile(p(n), o(n)); pad_square(o(n))


def photo(n, l1, l2, scrim=0.72, bar=True):
    """Bar varies on purpose — an identical bar on every ad manufactures duplicate scores
    out of pictures that share nothing (measured: +0.37 between a mouth and an invoice)."""
    check([l1, l2], n)
    trim_uniform_border(p(n))
    c = Composer(p(n))
    foot = 0.902 if bar else 1.0
    c.scrim(0.52, foot, opacity=scrim)
    if bar: c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    dy = 0.0 if bar else 0.052
    probe = Composer(c.save(t(n + "_probe")))
    for yy in (0.735 + dy, 0.822 + dy):
        ok, bg, ct = probe.contrast_ok(WHITE, 0.05, yy - 0.05, 0.95, yy + 0.015)
        if not ok:
            raise SystemExit(f"{n}: white copy scores {ct:.2f} contrast at y={yy:.2f} "
                             f"(bg {bg:.2f})")
    c.text(0.055, 0.735 + dy, l1, key="sans", size=0.046)
    w = c.measure(l2, "sans-bold", 0.060)
    if w > 0.90: raise SystemExit(f'"{l2}" is {w:.3f} wide — shorten it.')
    c.text(0.055, 0.822 + dy, l2, key="sans-bold", size=0.060)
    c.underline(0.055, 0.055 + w, 0.840 + dy)
    if bar: c.centered(0.962, CTA, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))


def timeline_badges(n, labels=("HEURE 1", "HEURE 24", "HEURE 48")):
    """Reproduce the winning device's own badges — a rounded pill, top of each panel."""
    trim_uniform_border(p(n))
    c = Composer(p(n))
    for i, lbl in enumerate(labels):
        cx = (i + 0.5) / len(labels)
        c.badge(cx - 0.075, 0.045, lbl, size=0.030, fill=NAVY, center_on=None)
    return c


# ---------------- PK — pack format, 8/8 chosen last round ----------------
@job
def PK1_box_bottle_kitchen():
    n = "PK1_box_bottle_kitchen"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    lines = ["98 % de dents plus propres,", "sans effort."]
    check(lines, n)
    c.scrim(0.74, 0.902, opacity=0.62)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.text(0.055, 0.798, lines[0], key="sans", size=0.040, color=NEARBK)
    c.text(0.055, 0.850, lines[1], key="sans-bold", size=0.050, color=ROYAL)
    c.centered(0.962, CTA, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def PK2_hand_holding_bottle():
    n = "PK2_hand_holding_bottle"
    canident_lockup(p(n), o(n), "Élimine le tartre jaune", "en 48 h",
        bullets=["Sans alcool,\nsans xylitol", "356 vétérinaires\nle conseillent"],
        align="center")
    pad_square(o(n))

@job
def PK3_flatlay_bathroom_shelf(): native("PK3_flatlay_bathroom_shelf")

@job
def PK4_pack_pastel_pair():
    n = "PK4_pack_pastel_pair"
    canident_lockup(p(n), o(n), "Convient aux chiens", "et les chats",
        bullets=["De toutes\ntailles", "Garanti\n60 jours"])
    pad_square(o(n))

@job
def PK5_pump_foam_dispensing():
    n = "PK5_pump_foam_dispensing"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    line = "Technologie mousse micro-adhérente."
    check([line], n)
    c.centered(0.088, line, key="sans-bold", size=0.044, color=NEARBK, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def PK6_pack_price_shelf():
    n = "PK6_pack_price_shelf"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    lines = ["Un seul de ces produits", "élimine vraiment le tartre."]
    check(lines, n)
    c.scrim(0.74, 0.902, opacity=0.70)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.text(0.055, 0.798, lines[0], key="sans", size=0.040, color=NEARBK)
    c.text(0.055, 0.850, lines[1], key="sans-bold", size=0.048, color=ROYAL)
    c.centered(0.962, CTA, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))

# ---------------- D — the sufferer's mouth, the mechanism ----------------
@job
def D1_gumline_macro_new_dog():
    photo("D1_gumline_macro_new_dog", "Le tartre se forme en 48 h.",
          "Sans que rien n'y paraisse.")

@job
def D2_scaler_tool_removing():
    photo("D2_scaler_tool_removing", "Ce que fait un détartrage vétérinaire.",
          "Canident™ agit avant.", bar=False)

@job
def D3_open_mouth_full_row():
    photo("D3_open_mouth_full_row", "Le tartre s'accumule dent après dent.",
          "98 % en moins avec Canident™.")

@job
def D4_vet_gloved_exam():
    photo("D4_vet_gloved_exam", "Un détartrage vétérinaire", "coûte très cher.", bar=False)

@job
def D5_tartre_in_bowl():
    photo("D5_tartre_in_bowl", "Ces flocons jaunes", "viennent de ses dents.")

# ---------------- BA — the winner's exact heure 1/24/48 device ----------------
@job
def BA1_heure_timeline_terrier():
    n = "BA1_heure_timeline_terrier"
    c = timeline_badges(n)
    line = "98 % du tartre, disparu en 48 h."
    check([line], n)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def BA2_heure_timeline_labrador():
    n = "BA2_heure_timeline_labrador"
    c = timeline_badges(n)
    line = "Sans brossage, sans stress."
    check([line], n)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def BA3_side_profile_before_after():
    n = "BA3_side_profile_before_after"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.badge(0.045, 0.045, "AVANT", size=0.032, fill=NAVY)
    c.badge(0.560, 0.045, "APRÈS", size=0.032, fill=ROYAL)
    line = "98 % du tartre éliminé en 48 h."
    check([line], n)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))

# ---------------- NA — native / UGC, matching the client's own new winner ----------------
@job
def NA1_owner_dog_asleep(): native("NA1_owner_dog_asleep")

@job
def NA2_dog_licking_hand_after(): native("NA2_dog_licking_hand_after")

@job
def NA3_flatlay_pastel_native(): native("NA3_flatlay_pastel_native")

# ---------------- X — new concepts ----------------
@job
def X1_invoice_redacted():
    n = "X1_invoice_redacted"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    lines = ["Un détartrage vétérinaire", "peut coûter très cher."]
    check(lines, n)
    c.text(0.055, 0.088, lines[0], key="sans", size=0.040, color=NEARBK, shadow=False)
    c.text(0.055, 0.140, lines[1], key="sans-bold", size=0.048, color=NEARBK, shadow=False)
    c.save(o(n)); pad_square(o(n))

@job
def X2_anesthesia_mask_dog():
    photo("X2_anesthesia_mask_dog", "Un détartrage nécessite souvent", "une anesthésie générale.")

@job
def X3_two_dogs_compare():
    n = "X3_two_dogs_compare"
    trim_uniform_border(p(n))
    c = Composer(p(n))
    c.badge(0.045, 0.045, "SANS CANIDENT™", size=0.030, fill=NAVY)
    c.badge(0.560, 0.045, "AVEC CANIDENT™", size=0.030, fill=ROYAL)
    line = "Même tartre. Résultat différent."
    check([line], n)
    c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
    c.centered(0.962, line, key="sans-bold", size=0.044, color=WHITE, shadow=False)
    c.save(o(n)); pad_square(o(n))


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(jobs)):
        if not os.path.exists(p(n)): print(f"MISS {n}"); continue
        jobs[n](); print(f"OK   {n}")
