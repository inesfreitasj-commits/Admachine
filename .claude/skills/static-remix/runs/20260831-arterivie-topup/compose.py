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
import pymupdf as fitz

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

# per-concept text anchor (x, alignment) plus the VERTICAL ZONE (top, bottom) actually open
# in that column of the base photo. The first pass anchored every concept near the top and
# let the block's own height decide where it ended — on the 4 concepts with no badges row
# that left 40-50% of the frame empty below the text, floating with nothing to balance it
# against. Now the block is measured first and centred within its zone instead.
P_LAYOUT = {
    # (x, align, zone_top, zone_bottom, avail_override) — avail_override caps text width so
    # a line never stretches under the bottle even when the bottle sits low but wide; None
    # falls back to the full remaining-frame-width default.
    "P1_base": (0.055, "left", 0.08, 0.40, 0.46),   # bottle cap starts ~x0.55, widens fast below y0.4
    "P2_base": (0.50, "right", 0.08, 0.90, None),   # bottle lower-left only; right column clear full height
    "P3_base": (0.06, "left", 0.08, 0.58, None),    # bottle bottom-centre ~0.62-0.95; zone stops above it
    "P4_base": (0.055, "left", 0.08, 0.38, None),   # diagonal bottle spans nearly full width below y0.42
    "P5_base": (0.50, "right", 0.08, 0.36, None),   # diagonal bottle reaches into the right column below y0.4
    "P6_base": (0.045, "left", 0.16, 0.90, None),   # small bottle, upper-right corner only
    "P7_base": (0.50, "right", 0.08, 0.90, None),   # macro crop, hard left/right split full height
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

def _p_layout_pass(c, d, x, avail, headline_c, check_c, badge_fill, y0, draw):
    """Runs the P block's full layout math once. draw=False just measures (returns the
    final y with nothing rendered); draw=True actually paints at that same y0. Keeping one
    function for both means the measured height and the drawn height can never drift apart."""
    size = min(0.046, *(_fit(c, line, "sans-bold", avail, 0.046) for line in d["headline"]))
    gap = size * 1.3
    if draw:
        for i, line in enumerate(d["headline"]):
            c.text(x, y0 + i * gap, line, key="sans-bold", size=size, color=headline_c, shadow=False)
    y = y0 + len(d["headline"]) * gap + 0.035
    csize = min(0.026, _fit(c, "✓ " + d["good"], "sans-bold", avail, 0.026),
                _fit(c, "✗ " + d["bad"], "sans-bold", avail, 0.026))
    if draw:
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
            if draw:
                bx2, _ = c.badge(bx, by, b, key="sans-bold", size=badge_size, fill=badge_fill,
                                  color=WHITE, padx=padx, pady=0.012, radius=0.5)
                bx = bx2 + 0.014
            else:
                bx += w + 0.014
        by += 0.075
    else:
        by += 0.02
    tsize = _fit(c, d["tagline"], "sans-bold", avail, 0.024)
    if draw:
        c.text(x, by, d["tagline"], key="sans-bold", size=tsize, color=check_c, shadow=False)
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    psize = _fit(c, proof, "sans", avail, 0.017)
    end_y = by + tsize * 1.9
    if draw:
        c.text(x, end_y, proof, key="sans", size=psize, color=(0.4, 0.4, 0.4), shadow=False)
    return end_y


def make_p_job(name):
    def _job():
        d = P_DATA[name]
        lines_to_check = d["headline"] + [d["good"], d["bad"]] + (d["badges"] or []) + [d["tagline"], PRICE_LINE]
        assert_not_winner_copy(lines_to_check, label=name, path=WINNER_COPY)

        headline_c, check_c, badge_fill = (NAVY, ORANGE, NAVY) if d["scheme"] == "navy" else (ORANGE, NAVY, ORANGE)
        c = Composer(p(name))
        x, align, zone_top, zone_bottom, avail_override = P_LAYOUT[name]
        avail = avail_override if avail_override is not None else 0.97 - x
        # measure pass: how tall is this concept's own block, unaffected by where it starts?
        measured_end = _p_layout_pass(c, d, x, avail, headline_c, check_c, badge_fill,
                                       y0=0.0, draw=False)
        block_h = measured_end  # since y0=0.0, the returned end_y IS the height
        y0 = zone_top + max(0.0, (zone_bottom - zone_top - block_h) / 2)
        _p_layout_pass(c, d, x, avail, headline_c, check_c, badge_fill, y0=y0, draw=True)
        c.save(o(name))
    _job.__name__ = name
    return _job

for _n in P_DATA:
    job(make_p_job(_n))


# ---------------------------------------------------------------- F series: fake newspaper
F_DATA = {
    "F1_artery_diagram": dict(has_quote=True, y0=0.20,
        headline=["UNE FORMULE CIBLÉE", "POUR LES ARTÈRES DU PÉNIS"],
        teaser="Les spécialistes s'intéressent de plus près au rôle des artères dans la circulation masculine.",
        quote="« Je ne savais même pas que c'était lié aux artères. »"),
    "F2_heart_network": dict(has_quote=False, y0=0.32,
        headline=["POURQUOI LE VIAGRA", "NE SUFFIT PLUS APRÈS 50 ANS"],
        teaser="Ce qui bloque vraiment la circulation ne se voit pas à l'œil nu.",
        quote="« Mon médecin ne m'en avait jamais parlé. »"),
    "F3_stethoscope_desk": dict(has_quote=False, y0=0.145,
        headline=["CE QUE LES CHERCHEURS SAVENT", "SUR LES ARTÈRES ET L'ÉRECTION"],
        teaser="Une étude de 2005 a changé la manière dont les chercheurs voient le problème.",
        quote="« Ça a changé ma façon de voir le problème. »"),
    "F4_before_after_diagram": dict(has_quote=True, y0=0.19, tight=True,
        headline=["LA DIFFÉRENCE ENTRE UNE ARTÈRE", "SAINE ET UNE ARTÈRE OBSTRUÉE"],
        teaser="Une différence de 1 à 2 mm peut tout changer.",
        quote="« Une différence que j'ai sentie en quelques semaines. »"),
    "F5_doctor_desk_jar": dict(has_quote=False, y0=0.145,
        headline=["UNE ROUTINE SIMPLE POUR", "SOUTENIR LE CŒUR ET LES ARTÈRES"],
        teaser="Une prise quotidienne, sans bouleverser sa routine.",
        quote="« C'est devenu un réflexe, comme se brosser les dents. »"),
    "F6_pelvic_floor_diagram": dict(has_quote=True, y0=0.235, tight=True,
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
        # spacing below deliberately generous — the diagram baked into the photo sits wherever
        # it sits and can't be centred against, so instead of clustering everything at the top
        # (leaving 40-50% of the frame blank below, which read as a layout bug) the block
        # itself spreads out to use more of the vertical space. "tight" concepts (diagram
        # sitting higher up the page) keep closer to the original spacing so the quote
        # doesn't run down into it.
        tight = d.get("tight", False)
        y = y0 + len(d["headline"]) * gap + (0.035 if tight else 0.075)
        for i, line in enumerate(_wrap2(d["teaser"])):
            tsize = _fit(c, line, "sans", avail, 0.026)
            c.text(0.05, y + i * tsize * 1.5, line, key="sans", size=tsize,
                   color=(0.2, 0.2, 0.2), shadow=False)
        if d["has_quote"]:
            y += 0.085 if tight else 0.155
            c.page.draw_line((0.05 * c.W, y * c.H), (0.35 * c.W, y * c.H), color=NAVY, width=0.003 * c.H)
            y += 0.045 if tight else 0.075
            for i, line in enumerate(_wrap2(d["quote"])):
                qsize = _fit(c, line, "sans-italic", avail, 0.026)
                c.text(0.05, y + i * qsize * 1.5, line, key="sans-italic", size=qsize, color=NAVY,
                       shadow=False)
        c.save(o(name))
    _job.__name__ = name
    return _job

for _n in F_DATA:
    job(make_f_job(_n))


# ---------------------------------------------------------------- W series: replacements for
# F2/F3/F5 (flagged as not good — empty layout). Two previously-untouched winning-ad devices
# (W1 = win_06's partner-testimonial, W2 = win_05's icon/graphic) plus one newspaper redo
# with a genuine multi-line body paragraph composited in code, so the text itself fills the
# page instead of floating over blank paper with nothing to anchor it.
def _wrap_to_width(c, text, key, size, max_w):
    """Greedy word-wrap: as many words per line as fit at this size/width. Unlike _wrap2
    (always exactly 2 lines) this handles an arbitrary-length paragraph."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.measure(trial, key, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fix_w1_label(c):
    """W1's jar is small and secondary (~7% of frame width) — the whole garbled zone
    (subtitle, thin band, RENFORCE/LE CŒUR/ET LES ARTÈRES) has to be retyped at a scale
    proportional to that, not the label-copy scale used elsewhere in this run. First
    attempt here was a soften with nothing drawn back on top of it — that read as a flat
    blur smear sitting in an otherwise sharp, in-focus photo (nothing else in this shot is
    soft-focus, so a blurred patch reads as an edit, not depth of field) and it still left
    the bottom claim line garbled outside the softened rect. This retypes the whole zone
    instead, small enough to match the jar's real size in frame."""
    # rect measured off the raw render, then padded well beyond the actual glyph bounds —
    # the first version of this fix sized the rect tight to the text and a sliver of the
    # old garbled letters survived just inside its edge, because soften() ramps its own
    # blur down to zero at the outer `feather` of the patch (by design, so the patch has no
    # visible boundary) — a rect that ends where the text ends leaves that under-blurred
    # ring sitting right on top of the text it was supposed to erase.
    rect = (0.282, 0.494, 0.385, 0.556)
    x0, y0, x1, y1 = rect
    c.soften(x0, y0, x1, y1, radius=0.007, feather=0.16)
    cx = (x0 + x1) / 2
    avail = (x1 - x0) * 0.92

    s1, s2 = "Soutient naturellement", "votre système circulatoire"
    ssize = min(_fit(c, s1, "sans", avail, 0.0072), _fit(c, s2, "sans", avail, 0.0072))
    sy = y0 + (y1 - y0) * 0.16
    c.centered(sy, s1, key="sans", size=ssize, color=(0.35, 0.28, 0.22), shadow=False, center_on=cx)
    c.centered(sy + ssize * 1.5, s2, key="sans", size=ssize, color=(0.35, 0.28, 0.22),
               shadow=False, center_on=cx)

    msize = min(_fit(c, "RENFORCE", "sans-bold", avail, 0.0110),
                _fit(c, "LE CŒUR", "sans-bold", avail, 0.0110),
                _fit(c, "ET LES ARTÈRES", "sans-bold", avail, 0.0110))
    my = sy + ssize * 1.5 + msize * 2.3
    c.centered(my, "RENFORCE", key="sans-bold", size=msize, color=NAVY, shadow=False, center_on=cx)
    # this line sits right where the label's own background sweeps from white to orange —
    # ORANGE type there loses contrast against the orange half; a deeper red-brown reads
    # against both halves.
    c.centered(my + msize * 1.35, "LE CŒUR", key="sans-bold", size=msize, color=(0.62, 0.10, 0.03),
               shadow=False, center_on=cx)
    c.centered(my + msize * 2.7, "ET LES ARTÈRES", key="sans-bold", size=msize * 0.82,
               color=NAVY, shadow=False, center_on=cx)


def _fix_jar_label(c, rect, dark=NAVY):
    """Blur the garbled portion of the jar label and retype it — the label is small/angled
    in these two W concepts (a hand-held photo and a small graphic-composition jar), and it
    garbled on both first attempts, same failure mode already seen across every product
    label in this session's larger runs."""
    x0, y0, x1, y1 = rect
    c.soften(x0, y0, x1, y1, radius=0.030, feather=0.14)
    subtitle = "Soutient naturellement"
    subtitle2 = "votre système circulatoire"
    avail = (x1 - x0) * 0.92
    ssize = min(_fit(c, subtitle, "sans", avail, 0.020), _fit(c, subtitle2, "sans", avail, 0.020))
    cx = (x0 + x1) / 2
    sy = y0 + (y1 - y0) * 0.20
    c.centered(sy, subtitle, key="sans", size=ssize, color=(0.15, 0.15, 0.15), shadow=False,
               center_on=cx)
    c.centered(sy + ssize * 1.4, subtitle2, key="sans", size=ssize, color=(0.15, 0.15, 0.15),
               shadow=False, center_on=cx)
    msize = min(_fit(c, "RENFORCE", "sans-bold", avail, 0.032),
                _fit(c, "LE CŒUR", "sans-bold", avail, 0.032),
                _fit(c, "ET LES ARTÈRES", "sans-bold", avail, 0.032))
    my = sy + ssize * 1.4 + msize * 1.7
    c.centered(my, "RENFORCE", key="sans-bold", size=msize, color=dark, shadow=False, center_on=cx)
    c.centered(my + msize * 1.35, "LE CŒUR", key="sans-bold", size=msize, color=ORANGE,
               shadow=False, center_on=cx)
    c.centered(my + msize * 2.7, "ET LES ARTÈRES", key="sans-bold", size=msize * 0.85, color=dark,
               shadow=False, center_on=cx)


@job
def W1_temoignage_epouse():
    quote = ["« Je l'ai commandée sans lui en parler. »",
             "Trois semaines plus tard, il m'a posé la question."]
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    assert_not_winner_copy(quote, label="W1", path=WINNER_COPY)

    c = Composer(p("W1_temoignage_epouse"))
    _fix_w1_label(c)
    # her head/hair occupies roughly x0.42-0.62 up top, so the quote sits further right,
    # in the clear wall/window strip — narrow enough that each sentence needs its own wrap
    # rather than one long line.
    x, avail = 0.665, 0.30
    size = 0.026
    lines = []
    for sentence in quote:
        lines.extend(_wrap_to_width(c, sentence, "sans-italic", size, avail))
    gap = size * 1.5
    y0 = 0.08
    for i, line in enumerate(lines):
        c.text(x, y0 + i * gap, line, key="sans-italic", size=size, color=NAVY, shadow=True)
    proof_lines = _wrap_to_width(c, proof, "sans", 0.015, avail)
    py = y0 + len(lines) * gap + 0.03
    for i, line in enumerate(proof_lines):
        c.text(x, py + i * 0.022, line, key="sans", size=0.015, color=(0.35, 0.35, 0.35),
               shadow=True)
    c.save(o("W1_temoignage_epouse"))


@job
def W2_icone_masculin():
    headline = "Un symbole. Un résultat."
    tagline = "Soutenir le cœur, c'est soutenir tout le reste."
    badges = ["97 % EN MOINS", "DÈS 7 JOURS", "60 JOURS GARANTIE"]
    assert_not_winner_copy([headline, tagline] + badges, label="W2", path=WINNER_COPY)

    c = Composer(p("W2_icone_masculin"))
    # subtitle line garbled on the first render (RENFORCE/LE CŒUR/ET LES ARTÈRES came out
    # correct, only these two lines needed fixing)
    sub_rect = (0.715, 0.470, 0.845, 0.505)
    c.soften(*sub_rect, radius=0.026, feather=0.14)
    sub_cx = (sub_rect[0] + sub_rect[2]) / 2
    sub_avail = (sub_rect[2] - sub_rect[0]) * 0.94
    s1, s2 = "Soutient naturellement", "votre système circulatoire"
    ssize = min(_fit(c, s1, "sans", sub_avail, 0.013), _fit(c, s2, "sans", sub_avail, 0.013))
    sy = sub_rect[1] + (sub_rect[3] - sub_rect[1]) * 0.35
    c.centered(sy, s1, key="sans", size=ssize, color=(0.15, 0.15, 0.15), shadow=False, center_on=sub_cx)
    c.centered(sy + ssize * 1.4, s2, key="sans", size=ssize, color=(0.15, 0.15, 0.15),
               shadow=False, center_on=sub_cx)
    # orange "COMPLÉMENT ALIMENTAIRE" band text, also garbled
    band_rect = (0.715, 0.503, 0.845, 0.528)
    c.soften(*band_rect, radius=0.024, feather=0.14)
    band_cx = (band_rect[0] + band_rect[2]) / 2
    band_avail = (band_rect[2] - band_rect[0]) * 0.94
    band_text = "COMPLÉMENT ALIMENTAIRE"
    bsize = _fit(c, band_text, "sans-bold", band_avail, 0.013)
    c.centered((band_rect[1] + band_rect[3]) / 2 + bsize * 0.35, band_text, key="sans-bold",
               size=bsize, color=WHITE, shadow=False, center_on=band_cx)

    x, avail = 0.06, 0.88
    hsize = _fit(c, headline, "sans-bold", avail, 0.058)
    c.text(x, 0.75, headline, key="sans-bold", size=hsize, color=WHITE, shadow=False)
    tsize = _fit(c, tagline, "sans-bold", avail, 0.028)
    c.text(x, 0.80, tagline, key="sans-bold", size=tsize, color=ORANGE, shadow=False)
    bx, by = x, 0.865
    badge_size, padx = 0.020, 0.016
    for b in badges:
        w = c.measure(b, "sans-bold", badge_size) + 2 * padx
        if bx + w > 0.95:
            bx = x
            by += 0.052
        bx2, _ = c.badge(bx, by, b, key="sans-bold", size=badge_size, fill=ORANGE, color=NAVY,
                          padx=padx, pady=0.012, radius=0.5)
        bx = bx2 + 0.014
    c.save(o("W2_icone_masculin"))


@job
def W3_encart_temoignages():
    """Redone to match the client's own reference more closely: a real masthead line, body
    text confined to a left column beside a diagram baked into the right side of the photo
    (rather than a diagram-free full-width paragraph), and a bordered pull-quote box at the
    bottom instead of a bare quote line — the structure the client pointed at directly."""
    headline = ["CE QUE RÉVÈLENT VRAIMENT", "LES HOMMES DE PLUS DE 50 ANS"]
    body = ("Beaucoup d'hommes de plus de 50 ans remarquent une baisse progressive de leurs "
            "érections, sans toujours en comprendre la cause. Les recherches récentes pointent "
            "du doigt les artères, plus fines et plus fragiles que celles du cœur, plutôt qu'un "
            "simple manque de désir. Plusieurs témoignages évoquent un changement dès la "
            "première semaine avec ArtériVie™.")
    quote = "« Je pensais que c'était juste l'âge. En fait, tout venait de mes artères. »"
    masthead = ("VOL. 143 — N° 09", "31 AOÛT 2026", "2,80 €")
    see_more = "Voir ArtériVie™, page 5B"
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    assert_not_winner_copy(headline + [body, quote], label="W3", path=WINNER_COPY)

    c = Composer(p("W3_encart_temoignages"))

    # masthead — composited, not AI-baked. Every AI-rendered masthead elsewhere in this run
    # was left deliberately illegible on purpose (decorative furniture); the client's
    # reference shows a masthead that actually READS, so this one is typeset instead of
    # left to the image model, which is what keeps it legible.
    my = 0.048
    c.underline(0.05, 0.95, my - 0.020, weight=0.0020, color=(0.55, 0.55, 0.55))
    c.text(0.05, my, masthead[0], key="sans-bold", size=0.014, color=(0.3, 0.3, 0.3), shadow=False)
    c.centered(my, masthead[1], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False, center_on=0.5)
    mw = c.measure(masthead[2], "sans", 0.013)
    c.text(0.95 - mw, my, masthead[2], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False)
    c.underline(0.05, 0.95, my + 0.014, weight=0.0020, color=(0.55, 0.55, 0.55))

    # headline — full width, above the diagram
    x, avail = 0.05, 0.90
    hsize = min(0.048, *(_fit(c, l, "sans-bold", avail, 0.048) for l in headline))
    hgap = hsize * 1.25
    y0 = 0.135
    for i, line in enumerate(headline):
        c.text(x, y0 + i * hgap, line, key="sans-bold", size=hsize, color=(0.08, 0.08, 0.08),
               shadow=False)
    y = y0 + len(headline) * hgap + 0.030
    c.underline(x, x + 0.28, y, weight=0.0026, color=NAVY)

    # body — LEFT COLUMN ONLY, so it runs beside the diagram baked into the right side of
    # the photo instead of under it.
    body_avail = 0.46
    bsize = 0.0235
    y += 0.045
    for line in _wrap_to_width(c, body, "sans", bsize, body_avail):
        c.text(x, y, line, key="sans", size=bsize, color=(0.2, 0.2, 0.2), shadow=False)
        y += bsize * 1.55

    # pull-quote — bordered box spanning the full width near the bottom, echoing the
    # reference ad's boxed citation instead of a bare line of italic text.
    bx0, bx1 = 0.05, 0.95
    by0, by1 = 0.685, 0.895
    c.page.draw_rect(fitz.Rect(bx0 * c.W, by0 * c.H, bx1 * c.W, by1 * c.H),
                      color=NAVY, fill=None, width=0.0026 * c.H)
    pad = 0.035
    qx, qavail = bx0 + pad, (bx1 - bx0) - 2 * pad
    qsize = 0.026
    qy = by0 + 0.075
    qlines = _wrap_to_width(c, quote, "sans-italic", qsize, qavail)
    for i, line in enumerate(qlines):
        c.text(qx, qy + i * qsize * 1.5, line, key="sans-italic", size=qsize, color=NAVY, shadow=False)
    py = qy + len(qlines) * qsize * 1.5 + 0.030
    psize = _fit(c, proof, "sans", qavail, 0.016)
    c.text(qx, py, proof, key="sans", size=psize, color=(0.4, 0.4, 0.4), shadow=False)

    smsize = 0.013
    smw = c.measure(see_more, "sans-italic", smsize)
    c.text(bx1 - pad - smw, by1 - 0.028, see_more, key="sans-italic", size=smsize,
           color=(0.4, 0.4, 0.4), shadow=False)

    c.save(o("W3_encart_temoignages"))


@job
def E1_lifestyle_column():
    """Newspaper editorial — a reader-story column, portrait baked into the photo on the
    right, headline + body composited in code, real page-sourced testimonial as the boxed
    pull-quote (Michel Lavoie's own words from the sales page, not winner-ad copy, so it's
    safe to use verbatim — attributed by first name + initial the way the page itself does
    for privacy)."""
    headline = ["COMMENT UN HOMME DE 58 ANS", "A RETROUVÉ SES ÉRECTIONS SANS VIAGRA"]
    body = ("Plus de 70 % des troubles de l'érection après 50 ans seraient d'origine "
            "vasculaire, liés à des dépôts qui rétrécissent des artères de seulement 1 à 2 mm "
            "de diamètre. C'est ce mécanisme qu'ArtériVie™ cible directement, plutôt que de "
            "simplement masquer le symptôme comme le fait le Viagra.")
    quote = ("« J'ai remarqué une vraie différence. Des érections plus fermes et plus "
             "naturelles. Ma femme l'a remarqué elle aussi. Depuis la sixième semaine, je "
             "n'ai plus eu besoin de Viagra. » — Michel L.")
    masthead = ("VOL. 143 — N° 12", "31 AOÛT 2026", "2,80 €")
    see_more = "Voir ArtériVie™, page 5B"
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    assert_not_winner_copy(headline + [body, quote], label="E1", path=WINNER_COPY)

    c = Composer(p("E1_lifestyle_column"))

    my = 0.048
    c.underline(0.05, 0.95, my - 0.020, weight=0.0020, color=(0.55, 0.55, 0.55))
    c.text(0.05, my, masthead[0], key="sans-bold", size=0.014, color=(0.3, 0.3, 0.3), shadow=False)
    c.centered(my, masthead[1], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False, center_on=0.5)
    mw = c.measure(masthead[2], "sans", 0.013)
    c.text(0.95 - mw, my, masthead[2], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False)
    c.underline(0.05, 0.95, my + 0.014, weight=0.0020, color=(0.55, 0.55, 0.55))

    x, avail = 0.05, 0.90
    hsize = min(0.044, *(_fit(c, l, "sans-bold", avail, 0.044) for l in headline))
    hgap = hsize * 1.28
    y0 = 0.115
    for i, line in enumerate(headline):
        c.text(x, y0 + i * hgap, line, key="sans-bold", size=hsize, color=(0.08, 0.08, 0.08),
               shadow=False)
    y = y0 + len(headline) * hgap + 0.035
    c.underline(x, x + 0.28, y, weight=0.0026, color=NAVY)

    body_avail = 0.56
    bsize = 0.0225
    y += 0.04
    for line in _wrap_to_width(c, body, "sans", bsize, body_avail):
        c.text(x, y, line, key="sans", size=bsize, color=(0.2, 0.2, 0.2), shadow=False)
        y += bsize * 1.55

    bx0, bx1 = 0.05, 0.95
    by0, by1 = 0.805, 0.955
    c.page.draw_rect(fitz.Rect(bx0 * c.W, by0 * c.H, bx1 * c.W, by1 * c.H),
                      color=NAVY, fill=None, width=0.0024 * c.H)
    pad = 0.03
    qx, qavail = bx0 + pad, (bx1 - bx0) - 2 * pad
    qsize = 0.020
    qy = by0 + 0.045
    qlines = _wrap_to_width(c, quote, "sans-italic", qsize, qavail)
    for i, line in enumerate(qlines):
        c.text(qx, qy + i * qsize * 1.5, line, key="sans-italic", size=qsize, color=NAVY, shadow=False)

    smsize = 0.012
    smw = c.measure(see_more, "sans-italic", smsize)
    c.text(bx1 - pad - smw, by0 - 0.012, see_more, key="sans-italic", size=smsize,
           color=(0.4, 0.4, 0.4), shadow=False)
    psize = _fit(c, proof, "sans", body_avail, 0.015)
    c.text(x, by0 - 0.012, proof, key="sans", size=psize, color=(0.4, 0.4, 0.4), shadow=False)

    c.save(o("E1_lifestyle_column"))


@job
def E2_mechanism_sidebar():
    """Newspaper 'how it works' sidebar — the whole step graphic (circles, connecting line,
    numbers, captions) is drawn in code rather than relying on the image model to place
    AI-rendered circles precisely enough to composite onto; the base photo leaves that whole
    column genuinely blank, so there is zero alignment risk."""
    headline = ["LE MÉCANISME DERRIÈRE", "UNE CIRCULATION RÉTABLIE"]
    body = ("Contrairement au Viagra, qui dilate temporairement les artères sans agir sur la "
            "cause, ArtériVie™ cible directement les dépôts qui rétrécissent la circulation, "
            "pour un résultat qui s'installe plutôt qu'il ne se force.")
    steps = [
        "Les artères se resserrent avec les dépôts.",
        "Le Viagra dilate — sans rien nettoyer.",
        "ArtériVie™ cible directement les dépôts.",
        "La circulation reprend, progressivement.",
        "Le flux revient, naturellement.",
    ]
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    masthead = ("VOL. 143 — N° 13", "31 AOÛT 2026", "2,80 €")
    assert_not_winner_copy(headline + [body] + steps, label="E2", path=WINNER_COPY)

    c = Composer(p("E2_mechanism_sidebar"))

    my = 0.048
    c.underline(0.05, 0.95, my - 0.020, weight=0.0020, color=(0.6, 0.6, 0.6))
    c.text(0.05, my, masthead[0], key="sans-bold", size=0.014, color=(0.3, 0.3, 0.3), shadow=False)
    c.centered(my, masthead[1], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False, center_on=0.5)
    mw = c.measure(masthead[2], "sans", 0.013)
    c.text(0.95 - mw, my, masthead[2], key="sans", size=0.013, color=(0.3, 0.3, 0.3), shadow=False)
    c.underline(0.05, 0.95, my + 0.014, weight=0.0020, color=(0.6, 0.6, 0.6))

    x, avail = 0.05, 0.90
    hsize = min(0.044, *(_fit(c, l, "sans-bold", avail, 0.044) for l in headline))
    hgap = hsize * 1.28
    y0 = 0.115
    for i, line in enumerate(headline):
        c.text(x, y0 + i * hgap, line, key="sans-bold", size=hsize, color=(0.08, 0.08, 0.08),
               shadow=False)
    y = y0 + len(headline) * hgap + 0.035
    c.underline(x, x + 0.28, y, weight=0.0026, color=NAVY)

    body_avail = 0.48
    bsize = 0.0225
    y += 0.04
    for line in _wrap_to_width(c, body, "sans", bsize, body_avail):
        c.text(x, y, line, key="sans", size=bsize, color=(0.2, 0.2, 0.2), shadow=False)
        y += bsize * 1.55

    proof_y = 0.90
    psize = _fit(c, proof, "sans", body_avail, 0.015)
    c.text(x, proof_y, proof, key="sans", size=psize, color=(0.4, 0.4, 0.4), shadow=False)

    # step graphic — code-drawn, right column
    scx = 0.74
    stop, sbot = 0.16, 0.86
    n = len(steps)
    r = 0.022
    step_y = [stop + (sbot - stop) * i / (n - 1) for i in range(n)]
    c.page.draw_line(fitz.Point(scx * c.W, step_y[0] * c.H), fitz.Point(scx * c.W, step_y[-1] * c.H),
                      color=NAVY, width=0.0035 * c.H)
    cap_avail = 0.20
    for i, (sy, step) in enumerate(zip(step_y, steps), start=1):
        c.page.draw_circle(fitz.Point(scx * c.W, sy * c.H), r * c.H, color=NAVY, fill=ORANGE, width=0.003 * c.H)
        numsize = 0.020
        nw = c.measure(str(i), "sans-bold", numsize)
        c.text(scx - nw / 2, sy + numsize * 0.34, str(i), key="sans-bold", size=numsize, color=WHITE, shadow=False)
        capsize = min(0.0155, _fit(c, step, "sans", cap_avail, 0.0155))
        caplines = _wrap_to_width(c, step, "sans", capsize, cap_avail)
        cy = sy - (len(caplines) - 1) * capsize * 0.75
        for j, line in enumerate(caplines):
            c.text(scx + r + 0.025, cy + j * capsize * 1.5 + capsize * 0.34, line,
                   key="sans", size=capsize, color=(0.2, 0.2, 0.2), shadow=False)

    c.save(o("E2_mechanism_sidebar"))


@job
def U1_selfie_mirror():
    """UGC bathroom-mirror selfie — Denis Gauthier's real page-sourced testimonial, safe to
    use verbatim (not winner-ad copy)."""
    quote = ("« J'ai commencé parce que l'approche ciblant le nettoyage des artères "
              "m'avait intrigué, sans vraiment y croire. Puis, dès la quatrième semaine, tout "
              "a commencé à fonctionner de nouveau. Naturellement. Sans Viagra. »")
    attrib = "— Denis G."
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    assert_not_winner_copy([quote], label="U1", path=WINNER_COPY)

    c = Composer(p("U1_selfie_mirror"))
    scrim_y0 = 0.68
    c.scrim(scrim_y0, 1.0, opacity=0.62)
    x, avail = 0.06, 0.88
    qsize = 0.026
    qlines = _wrap_to_width(c, quote, "sans-italic", qsize, avail)
    y0 = 0.775
    for i, line in enumerate(qlines):
        c.text(x, y0 + i * qsize * 1.45, line, key="sans-italic", size=qsize, color=WHITE, shadow=True)
    y = y0 + len(qlines) * qsize * 1.45 + 0.012
    c.text(x, y, attrib, key="sans-bold", size=0.020, color=ORANGE, shadow=True)
    proof_lines = _wrap_to_width(c, proof, "sans", 0.015, avail)
    py = y + 0.038
    for i, line in enumerate(proof_lines):
        c.text(x, py + i * 0.022, line, key="sans", size=0.015, color=(0.85, 0.85, 0.85), shadow=True)
    c.save(o("U1_selfie_mirror"))


@job
def U2_nightstand_flatlay():
    """UGC nightstand flat-lay — the wife's candid caption, fresh wording (checked against
    W1's own quote too, not just the winner corpus, since both are her voice)."""
    quote = ["« Je l'ai glissée dans sa routine du matin,", "sans rien dire. »"]
    tagline = "Il n'a rien remarqué — jusqu'à ce qu'il remarque tout."
    proof = f"{PROOF_LINE}  ·  {PRICE_LINE}"
    assert_not_winner_copy(quote + [tagline], label="U2", path=WINNER_COPY)
    assert_not_winner_copy(quote, corpus=[
        "je l'ai commandée sans lui en parler.",
        "trois semaines plus tard, il m'a posé la question.",
    ], label="U2 vs W1", path=None)

    c = Composer(p("U2_nightstand_flatlay"))
    x, avail = 0.55, 0.40
    qsize = 0.026
    y0 = 0.10
    for i, line in enumerate(quote):
        c.text(x, y0 + i * qsize * 1.5, line, key="sans-italic", size=qsize, color=NAVY, shadow=False)
    y = y0 + len(quote) * qsize * 1.5 + 0.035
    tsize = _fit(c, tagline, "sans-bold", avail, 0.020)
    for line in _wrap_to_width(c, tagline, "sans-bold", tsize, avail):
        c.text(x, y, line, key="sans-bold", size=tsize, color=ORANGE, shadow=False)
        y += tsize * 1.5
    proof_lines = _wrap_to_width(c, proof, "sans", 0.015, avail)
    py = y + 0.03
    for i, line in enumerate(proof_lines):
        c.text(x, py + i * 0.022, line, key="sans", size=0.015, color=(0.35, 0.35, 0.35), shadow=False)
    c.save(o("U2_nightstand_flatlay"))


if __name__ == "__main__":
    want = sys.argv[1:] or list(jobs)
    for n in want:
        if not os.path.exists(p(n)):
            print(f"MISS {n} (no source image yet)"); continue
        jobs[n](); print(f"OK   {n}")
