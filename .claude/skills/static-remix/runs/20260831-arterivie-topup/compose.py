#!/usr/bin/env python3
"""ArtériVie topup — composite the P (mechanism/proof-bar hero) and F (fake-newspaper
native) series. N series (silent scan-mystery natives) are pure passthrough — no text was
ever meant to be composited on them, the AI-rendered scan metadata is the whole point.

Every headline/checklist/badge/tagline line is fresh wording, checked against
assets/winner-copy.md via assert_not_winner_copy. Every fact traces to
assets/product-page.md — including the "60 452 avis" figure, which is flagged there as
client-confirmed rather than page-sourced (see that file's correction note).

Run: python3 compose.py [name ...]
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/static-remix/scripts")
from compose_text import Composer, assert_not_winner_copy

SRC, OUT = "production", "final"
os.makedirs(OUT, exist_ok=True)
ORANGE = (0.86, 0.42, 0.09)
NAVY = (0.09, 0.14, 0.24)
WHITE = (1, 1, 1)
WINNER_COPY = "assets/winner-copy.md"

def p(n): return f"{SRC}/{n}.png"
def o(n): return f"{OUT}/{n}.png"

jobs = {}
def job(fn): jobs[fn.__name__] = fn; return fn
def passthrough(n):
    import shutil; shutil.copyfile(p(n), o(n))


# ---------------------------------------------------------------- P series: mechanism hero
def check_line(c, x, baseline, mark, text, size, color):
    end_x = c.text(x, baseline, mark, key="sym", size=size, color=color, shadow=False)
    c.text(end_x + 0.013, baseline, text, key="sans-bold", size=size, color=color, shadow=False)

P_DATA = {
    # scheme "navy" = navy headline+badges, orange checkmarks. scheme "orange" swaps those
    # roles. badges=False drops the pill row entirely. Both vary deliberately across the 7 so
    # no two concepts share the same colour treatment AND text structure AND jar position —
    # the first pass gave all 7 an identical navy/orange scheme + badges row + full-width
    # bottom band, which is why 21 of the 21 P-P pairs hard-failed the duplicate gate: same
    # large shapes everywhere, different words. See report.txt.
    "P1_base": dict(
        headline=["70 % des troubles de l'érection", "sont d'origine vasculaire."],
        good="70 % des troubles sont vasculaires", bad="le Viagra ne cible pas les dépôts",
        badges=["70 % VASCULAIRE", "DOSE CLINIQUE", "60 JOURS GARANTIE"],
        tagline="Une circulation enfin débloquée.", scheme="navy"),
    "P2_base": dict(
        headline=["Ces artères sont deux fois plus", "fines que celles du cœur."],
        good="artères péniennes de 1 à 2 mm", bad="premières à s'obstruer avec l'âge",
        badges=["1 À 2 MM", "FORMULE CIBLÉE", "1 PRISE / JOUR"],
        tagline="La cause profonde, enfin ciblée.", scheme="orange"),
    "P3_base": dict(
        headline=["7 hommes sur 10 perdent leurs", "érections après 50 ans."],
        good="7 hommes sur 10 concernés après 50 ans", bad="personne ne leur explique pourquoi",
        badges=None,
        tagline="Tout commence dans les artères.", scheme="navy"),
    "P4_base": dict(
        headline=["3 à 5 fois plus de risque.", "Personne ne vous le dit."],
        good="risque cardiovasculaire 3 à 5x plus élevé", bad="un signal que le corps ne peut pas ignorer",
        badges=None,
        tagline="Le cœur et les artères, protégés ensemble.", scheme="orange"),
    "P5_base": dict(
        headline=["Le Viagra dilate.", "Il ne nettoie jamais les dépôts."],
        good="une formule qui cible les dépôts", bad="le Viagra dilate, il ne nettoie pas",
        badges=None,
        tagline="Une formule qui va à la racine du problème.", scheme="orange"),
    "P6_base": dict(
        headline=["97 % des dépôts artériels,", "disparus."],
        good="97 % des dépôts artériels éliminés", bad="les comprimés classiques n'y touchent pas",
        badges=["97 % EN MOINS", "DÈS 7 JOURS", "30 JOURS / FLACON"],
        tagline="Le flux sanguin, naturellement rétabli.", scheme="navy"),
    "P7_base": dict(
        headline=["24 heures. Jour 3. Jour 7.", "Voilà ce qui change."],
        good="érections plus fermes et réactives dès le jour 7", bad="le Viagra doit être repris à chaque fois",
        badges=["24 H", "JOUR 3", "JOUR 7"],
        tagline="Le changement, jour après jour.", scheme="navy"),
}
PRICE_LINE = "34,95 € au lieu de 70,00 € · Garantie 60 jours"
PROOF_LINE = "4,8 ★★★★★ — plus de 60 452 avis"

# per-concept text anchor (x, headline top-y, text alignment) matching each base photo's own
# open space — alignment also varies the proof/price line's position instead of a uniform
# full-width band, which was the single biggest shared shape in the first pass.
P_LAYOUT = {
    "P1_base": (0.055, 0.09, "left"),
    "P2_base": (0.50, 0.09, "right"),
    "P3_base": (0.06, 0.075, "left"),
    "P4_base": (0.055, 0.09, "left"),
    "P5_base": (0.50, 0.08, "right"),
    "P6_base": (0.045, 0.10, "left"),
    "P7_base": (0.50, 0.09, "right"),
}

def _wrap2(text):
    """Split into two roughly-even-length lines at a word boundary near the midpoint —
    used for teaser/quote sentences too long to fit as one line even at a small size."""
    words = text.split()
    if len(words) < 6:
        return [text]
    half = len(text) / 2
    best_i, best_diff = 1, abs(len(words[0]) - half)
    running = len(words[0])
    for i in range(1, len(words)):
        running += 1 + len(words[i])
        diff = abs(running - half)
        if diff < best_diff:
            best_diff, best_i = diff, i + 1
    return [" ".join(words[:best_i]), " ".join(words[best_i:])]

def _fit(c, text, key, avail, cap):
    """Largest size (up to cap) whose rendered width stays within avail — the auto-fit
    pattern from the ÉveilSens label fixes, applied here so no line is ever hand-tuned per
    concept only to overflow on the next edit."""
    ref = 0.05
    w = c.measure(text, key, ref)
    return min(avail / w * ref if w > 0 else cap, cap)

def make_p_job(name):
    def _job():
        d = P_DATA[name]
        lines_to_check = d["headline"] + [d["good"], d["bad"]] + (d["badges"] or []) + [d["tagline"], PRICE_LINE]
        assert_not_winner_copy(lines_to_check, label=name, path=WINNER_COPY)

        headline_c, check_c, badge_fill = (NAVY, ORANGE, NAVY) if d["scheme"] == "navy" else (ORANGE, NAVY, ORANGE)
        c = Composer(p(name))
        x, y0, align = P_LAYOUT[name]
        avail = 0.97 - x
        size = min(0.046, *(_fit(c, line, "sans-bold", avail, 0.046) for line in d["headline"]))
        gap = size * 1.3
        for i, line in enumerate(d["headline"]):
            c.text(x, y0 + i * gap, line, key="sans-bold", size=size, color=headline_c, shadow=False)
        y = y0 + len(d["headline"]) * gap + 0.035
        csize = min(0.026, _fit(c, "✓ " + d["good"], "sans-bold", avail, 0.026),
                    _fit(c, "✗ " + d["bad"], "sans-bold", avail, 0.026))
        check_line(c, x, y, "✓", d["good"], csize, check_c)
        check_line(c, x, y + csize * 1.55, "✗", d["bad"], csize, headline_c)
        by = y + csize * 1.55 + 0.055
        if d["badges"]:
            bx = x
            badge_size, padx = 0.020, 0.016
            for b in d["badges"]:
                w = c.measure(b, "sans-bold", badge_size) + 2 * padx
                if bx + w > 0.97:
                    bx = x
                    by += 0.052
                bx2, _ = c.badge(bx, by, b, key="sans-bold", size=badge_size, fill=badge_fill,
                                  color=WHITE, padx=padx, pady=0.012, radius=0.5)
                bx = bx2 + 0.014
            by += 0.075
        else:
            by += 0.02
        tsize = _fit(c, d["tagline"], "sans-bold", avail, 0.024)
        c.text(x, by, d["tagline"], key="sans-bold", size=tsize, color=check_c, shadow=False)
        # proof/price: plain small text right under the tagline, no solid band and no fixed
        # cross-image y — each concept's block simply ends wherever its own content ends.
        proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
        psize = _fit(c, proof, "sans", avail, 0.017)
        c.text(x, by + tsize * 1.9, proof, key="sans", size=psize, color=(0.4, 0.4, 0.4),
               shadow=False)
        c.save(o(name))
    _job.__name__ = name
    return _job

for _n in P_DATA:
    job(make_p_job(_n))


# ---------------------------------------------------------------- F series: fake newspaper
F_DATA = {
    "F1_artery_diagram": dict(has_quote=True, y0=0.145,
        headline=["UNE FORMULE CIBLÉE", "POUR LES ARTÈRES DU PÉNIS"],
        teaser="Les spécialistes s'intéressent de plus près au rôle des artères dans la circulation masculine.",
        quote="« Je ne savais même pas que c'était lié aux artères. »"),
    "F2_heart_network": dict(has_quote=False, y0=0.20,
        headline=["POURQUOI LE VIAGRA", "NE SUFFIT PLUS APRÈS 50 ANS"],
        teaser="Ce qui bloque vraiment la circulation ne se voit pas à l'œil nu.",
        quote="« Mon médecin ne m'en avait jamais parlé. »"),
    "F3_stethoscope_desk": dict(has_quote=False, y0=0.145,
        headline=["CE QUE LES CHERCHEURS SAVENT", "SUR LES ARTÈRES ET L'ÉRECTION"],
        teaser="Une étude de 2005 a changé la manière dont les chercheurs voient le problème.",
        quote="« Ça a changé ma façon de voir le problème. »"),
    "F4_before_after_diagram": dict(has_quote=True, y0=0.19,
        headline=["LA DIFFÉRENCE ENTRE UNE ARTÈRE", "SAINE ET UNE ARTÈRE OBSTRUÉE"],
        teaser="Une différence de 1 à 2 mm peut tout changer.",
        quote="« Une différence que j'ai sentie en quelques semaines. »"),
    "F5_doctor_desk_jar": dict(has_quote=False, y0=0.145,
        headline=["UNE ROUTINE SIMPLE POUR", "SOUTENIR LE CŒUR ET LES ARTÈRES"],
        teaser="Une prise quotidienne, sans bouleverser sa routine.",
        quote="« C'est devenu un réflexe, comme se brosser les dents. »"),
    "F6_pelvic_floor_diagram": dict(has_quote=True, y0=0.235,
        headline=["CE QUE PERSONNE N'EXPLIQUE SUR", "LES TROUBLES DE L'ÉRECTION APRÈS 50 ANS"],
        teaser="La cause est plus simple qu'on ne le pense.",
        quote="« J'aurais aimé le savoir dix ans plus tôt. »"),
}
SPONSORED = "CONTENU SPONSORISÉ — ArtériVie™"
# F5's base photo has the jar sitting in the upper-right, so its headline needs a narrower
# available width than the other 5 concepts (which have the whole top open).
F_AVAIL = {"F5_doctor_desk_jar": 0.73, "F4_before_after_diagram": 0.50,
           "F1_artery_diagram": 0.58}

def make_f_job(name):
    def _job():
        d = F_DATA[name]
        assert_not_winner_copy(d["headline"] + [d["teaser"], d["quote"]], label=name, path=WINNER_COPY)

        c = Composer(p(name))
        c.badge(0.05, 0.075, SPONSORED, key="sans-bold", size=0.020, fill=(0.85, 0.85, 0.82),
                color=NAVY, padx=0.016, pady=0.010, radius=0.15)
        avail = F_AVAIL.get(name, 0.90)
        size = min(0.052, *(_fit(c, line, "sans-bold", avail, 0.052) for line in d["headline"]))
        gap = size * 1.25
        y0 = d["y0"]
        for i, line in enumerate(d["headline"]):
            c.text(0.05, y0 + i * gap, line, key="sans-bold", size=size, color=(0.08, 0.08, 0.08),
                   shadow=False)
        y = y0 + len(d["headline"]) * gap + 0.035
        for i, line in enumerate(_wrap2(d["teaser"])):
            tsize = _fit(c, line, "sans", avail, 0.026)
            c.text(0.05, y + i * tsize * 1.5, line, key="sans", size=tsize,
                   color=(0.2, 0.2, 0.2), shadow=False)
        if d["has_quote"]:
            y += 0.085
            c.page.draw_line((0.05 * c.W, y * c.H), (0.35 * c.W, y * c.H), color=NAVY, width=0.003 * c.H)
            y += 0.045
            for i, line in enumerate(_wrap2(d["quote"])):
                qsize = _fit(c, line, "sans-italic", avail, 0.026)
                c.text(0.05, y + i * qsize * 1.5, line, key="sans-italic", size=qsize, color=NAVY,
                       shadow=False)
        c.save(o(name))
    _job.__name__ = name
    return _job

for _n in F_DATA:
    job(make_f_job(_n))


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
