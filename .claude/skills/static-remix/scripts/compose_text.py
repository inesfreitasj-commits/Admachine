#!/usr/bin/env python3
"""compose_text.py — composite exact text and flat graphics onto a generated image.

Image models garble long copy. Anything that MUST be spelled correctly — headlines,
badges, day labels, price stickers, quotes — is drawn here instead, in code, so it is
pixel-exact and free to redo.

Everything is specified in FRACTIONS of the image size, so a layout written once works
at any output resolution. Import `Composer` and call the primitives, or use the
`hook_lockup` helper which reproduces the consumer-test editorial lockup.

Sizing rule (learned the hard way): size type for the THUMBNAIL, not the file. A
headline below ~0.040 of the frame height is unreadable in a Meta feed. This module
REFUSES to auto-shrink text to fit — if a line is too long it raises, so you shorten the
copy instead of shipping type nobody can read.
"""
import math
import pymupdf as fitz

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
FONTS = {
    "sans":        f"{FONT_DIR}/InstrumentSans-Regular.ttf",
    "sans-bold":   f"{FONT_DIR}/InstrumentSans-Bold.ttf",
    "sans-italic": f"{FONT_DIR}/InstrumentSans-Italic.ttf",
    "serif":       f"{FONT_DIR}/Lora-Regular.ttf",
    "serif-bold":  f"{FONT_DIR}/Lora-Bold.ttf",
    "hand":        f"{FONT_DIR}/NothingYouCouldDo-Regular.ttf",
    "sym":         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # ★ ✓ ✗ €
}
WHITE, BLACK = (1, 1, 1), (0, 0, 0)
RED    = (0.898, 0.180, 0.180)   # the red of the winning ads' TEST PRODUIT badge
BLEU   = (0.000, 0.129, 0.588)   # tricolore blue
ROUGE  = (0.929, 0.161, 0.224)   # tricolore red
GOLD   = (0.788, 0.541, 0.294)
ROYAL  = (0.106, 0.373, 0.682)   # Canident headline blue
NAVY   = (0.071, 0.227, 0.388)   # Canident CTA bar
TEAL   = (0.122, 0.420, 0.369)   # Canident wordmark
NEARBK = (0.102, 0.102, 0.180)   # the winners' headline black
INK    = (0.106, 0.086, 0.070)   # near-black brown, for type on the cream ground
TPGREEN= (0.000, 0.714, 0.478)   # Trustpilot green

MIN_HEADLINE_FRAC = 0.040        # of image height — below this, nobody reads it


class Composer:
    def __init__(self, src):
        self.src = src
        pix = fitz.Pixmap(src)
        self.W, self.H = pix.width, pix.height
        self.doc = fitz.open()
        self.page = self.doc.new_page(width=self.W, height=self.H)
        self.page.insert_image(fitz.Rect(0, 0, self.W, self.H), filename=src)
        self._fonts = {}

    # ---- helpers -------------------------------------------------------
    def font(self, key):
        if key not in self._fonts:
            self._fonts[key] = fitz.Font(fontfile=FONTS[key])
        return self._fonts[key]

    def px(self, fx, fy=None):
        return (fx * self.W) if fy is None else (fx * self.W, fy * self.H)

    def measure(self, text, key, size_frac):
        return self.font(key).text_length(text, self.H * size_frac) / self.W

    # ---- primitives ----------------------------------------------------
    def scrim(self, y0, y1, opacity=0.55, top_down=False, gamma=1.6):
        """Soft dark gradient so white type survives a bright photo.

        Built as a real alpha ramp in a Pixmap — stacked translucent rects band
        badly where they overlap, and that banding is visible in the feed.
        """
        h = max(2, int(round((y1 - y0) * self.H)))
        pm = fitz.Pixmap(fitz.csGRAY, fitz.IRect(0, 0, 1, h), True)   # +alpha
        buf = bytearray(pm.samples)
        for i in range(h):
            t = (i / (h - 1)) if not top_down else (1 - i / (h - 1))
            buf[2 * i] = 0                                   # black
            buf[2 * i + 1] = int(255 * opacity * (t ** gamma))
        pm.samples_mv[:] = bytes(buf)
        self.page.insert_image(fitz.Rect(0, y0 * self.H, self.W, y1 * self.H),
                               pixmap=pm, keep_proportion=False)

    def band(self, y0, y1, fill=BLACK, opacity=0.88):
        """Solid bar. Use instead of a scrim when the photo underneath is busy or
        white — a gradient over supermarket price labels leaves the copy unreadable."""
        self.page.draw_rect(fitz.Rect(0, y0 * self.H, self.W, y1 * self.H),
                            color=None, fill=fill, fill_opacity=opacity)

    def text(self, x, baseline, text, key="sans-bold", size=0.05, color=WHITE,
             shadow=True, letter_spacing=0.0):
        """Draw one line. x/baseline/size are fractions. Returns the end x fraction."""
        f, s = self.font(key), self.H * size
        tw = fitz.TextWriter(self.page.rect)
        if shadow:
            sh = fitz.TextWriter(self.page.rect)
            off = s * 0.045
            for dx, dy in ((off, off), (-off * .4, off), (off, -off * .4)):
                sh.append((x * self.W + dx, baseline * self.H + dy), text, font=f, fontsize=s)
            sh.write_text(self.page, color=BLACK, opacity=0.45)
        tw.append((x * self.W, baseline * self.H), text, font=f, fontsize=s)
        tw.write_text(self.page, color=color)
        return x + f.text_length(text, s) / self.W

    def rich(self, x, baseline, spans, size=0.05, color=WHITE, shadow=True):
        """spans = [(text, font_key), ...] drawn on one baseline. Returns end x."""
        for t, k in spans:
            x = self.text(x, baseline, t, key=k, size=size, color=color, shadow=shadow)
        return x

    def centered(self, baseline, text, key="sans-bold", size=0.05, color=WHITE,
                 shadow=True, max_frac=0.94, center_on=0.5):
        """Centre one line and REFUSE to draw it if it would run off the frame.

        Centring by hand with (1 - w) / 2 silently produces negative x when the copy
        is too long, and the line bleeds off both edges. This raises instead."""
        w = self.measure(text, key, size)
        if w > max_frac:
            raise SystemExit(
                f'"{text}" is {w:.3f} of the frame width at size {size} — it would '
                f'run off both edges. Shorten the copy; do NOT shrink the type.')
        self.text(center_on - w / 2, baseline, text, key=key, size=size,
                  color=color, shadow=shadow)
        return w

    def underline(self, x0, x1, y, weight=0.006, color=WHITE):
        self.page.draw_line(fitz.Point(x0 * self.W, y * self.H),
                            fitz.Point(x1 * self.W, y * self.H),
                            color=color, width=weight * self.H)

    def badge(self, x, y, text, key="sans-bold", size=0.042, fill=RED, color=WHITE,
              padx=0.020, pady=0.016, radius=0.28, center_on=None):
        """Rounded label with the text vertically centred. y is the badge TOP.

        center_on: horizontal fraction to centre the badge on, instead of x.
        Raises rather than shrinking if the badge would run off the frame."""
        f, s = self.font(key), self.H * size
        tw_ = f.text_length(text, s) / self.W
        if center_on is not None:
            x = center_on - (tw_ + 2 * padx) / 2
        w, h = tw_ + 2 * padx, size * 1.02 + 2 * pady * self.W / self.H
        if x + w > 0.985 or x < 0.005:
            raise SystemExit(
                f'badge "{text}" spans {x:.3f}..{x + w:.3f} of the frame width and runs '
                f'off the edge. Shorten the copy or move it — do NOT shrink the type.')
        r = fitz.Rect(x * self.W, y * self.H, (x + w) * self.W, (y + h) * self.H)
        self.page.draw_rect(r, color=None, fill=fill, radius=radius)
        base = y + h - pady * self.W / self.H - size * 0.16
        self.text(x + padx, base, text, key=key, size=size, color=color, shadow=False)
        return x + w, y + h

    def tricolore(self, cx, cy, r):
        """The circular French flag roundel used in the winners' lockup."""
        R, cxp, cyp = r * self.H, cx * self.W, cy * self.H
        shape = self.page.new_shape()
        shape.draw_oval(fitz.Rect(cxp - R, cyp - R, cxp + R, cyp + R))
        shape.finish(color=None, fill=WHITE)
        shape.commit()
        # blue and red bands, drawn as vertical slices clipped to the circle
        for frac0, frac1, col in ((0.0, 1/3, BLEU), (2/3, 1.0, ROUGE)):
            x0, x1, steps = cxp - R + 2*R*frac0, cxp - R + 2*R*frac1, 80
            for i in range(steps):
                sx0 = x0 + (x1 - x0) * i / steps
                sx1 = x0 + (x1 - x0) * (i + 1) / steps
                mx = sx1 if col is BLEU else sx0          # outer edge of the slice
                dy = max(0.0, R*R - (mx - cxp) ** 2) ** 0.5
                self.page.draw_rect(fitz.Rect(sx0, cyp - dy, sx1 + 0.7, cyp + dy),
                                    color=None, fill=col)

    def stars(self, x, y, n=5, size=0.045, color=TPGREEN, box=True):
        """Trustpilot-style star row. y is the row TOP. Returns the end x fraction."""
        f, s = self.font("sym"), self.H * size
        side = size * 1.34
        gap = side * 0.10
        for i in range(n):
            bx = x + i * (side * self.H / self.W + gap * self.H / self.W)
            if box:
                self.page.draw_rect(fitz.Rect(bx * self.W, y * self.H,
                                              bx * self.W + side * self.H,
                                              y * self.H + side * self.H),
                                    color=None, fill=color)
            tw = fitz.TextWriter(self.page.rect)
            glyph_w = f.text_length("\u2605", s) / self.W
            tw.append((bx * self.W + (side * self.H - glyph_w * self.W) / 2,
                       (y + side * 0.80) * self.H), "\u2605", font=f, fontsize=s)
            tw.write_text(self.page, color=WHITE if box else color)
        return x + n * (side * self.H / self.W + gap * self.H / self.W)

    def image(self, x0, y0, x1, y1, path):
        self.page.insert_image(fitz.Rect(x0*self.W, y0*self.H, x1*self.W, y1*self.H),
                               filename=path)

    def paw(self, cx, cy, r, color=ROYAL):
        """The paw-print bullet glyph from the Canident winners. r = pad radius."""
        R = r * self.H
        cxp, cyp = cx * self.W, cy * self.H
        pad = fitz.Rect(cxp - R, cyp - R * 0.72, cxp + R, cyp + R * 0.95)
        sh = self.page.new_shape(); sh.draw_oval(pad); sh.finish(color=None, fill=color); sh.commit()
        for dx, dy, rr in ((-1.05, -1.28, 0.40), (-0.36, -1.62, 0.40),
                           (0.36, -1.62, 0.40), (1.05, -1.28, 0.40)):
            t = fitz.Rect(cxp + dx * R - rr * R, cyp + dy * R - rr * R * 1.15,
                          cxp + dx * R + rr * R, cyp + dy * R + rr * R * 1.15)
            sh = self.page.new_shape(); sh.draw_oval(t); sh.finish(color=None, fill=color); sh.commit()


    def luminance_under(self, x0, y0, x1, y1, step=6):
        """Mean perceived luminance (0-1) of the picture under a rectangle."""
        px0, py0 = int(x0 * self.W), int(y0 * self.H)
        px1, py1 = int(x1 * self.W), int(y1 * self.H)
        px0, py0 = max(0, px0), max(0, py0)
        px1, py1 = min(self.W - 1, px1), min(self.H - 1, py1)
        vals = []
        pix = fitz.Pixmap(self.src)
        sx, sy = pix.width / self.W, pix.height / self.H
        for y in range(py0, py1, step):
            for x in range(px0, px1, step):
                r, g, b = pix.pixel(min(pix.width - 1, int(x * sx)),
                                    min(pix.height - 1, int(y * sy)))
                vals.append((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255)
        return sum(vals) / len(vals) if vals else 0.5

    def contrast_ok(self, color, x0, y0, x1, y1, minimum=0.33):
        """Will `color` actually read against the picture here?

        Copy has shipped in dark green over a sunlit bookshelf, invisible at thumbnail size.
        Measure before drawing rather than eyeballing it afterwards. Returns
        (ok, background_luminance, contrast)."""
        bg = self.luminance_under(x0, y0, x1, y1)
        fg = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
        return abs(fg - bg) >= minimum, bg, abs(fg - bg)

    def text_panel(self, x, baseline, lines, key="sans-bold", size=0.060, color=NEARBK,
                   fill=WHITE, pad=0.018, lead=None, radius=0.10, opacity=0.94):
        """Draw copy on its own solid panel — the reliable answer when the picture behind is
        busy or its brightness is close to the type colour. Returns the panel rect."""
        lead = lead or size * 1.28
        w = max(self.measure(t, key, size) for t in lines)
        top = baseline - size * 0.82 - pad
        bot = baseline + lead * (len(lines) - 1) + size * 0.28 + pad
        self.page.draw_rect(fitz.Rect((x - pad) * self.W, top * self.H,
                                      (x + w + pad) * self.W, bot * self.H),
                            color=None, fill=fill, fill_opacity=opacity,
                            radius=radius)
        for i, t in enumerate(lines):
            self.text(x, baseline + i * lead, t, key=key, size=size, color=color, shadow=False)
        return (x - pad, top, x + w + pad, bot)

    def soften(self, x0, y0, x1, y1, radius=0.010, feather=0.28, wash=None,
               wash_opacity=0.0):
        """Blur a rectangle with a real box blur, faded out at its own edges.

        The fix for a paper prop the image model has printed gibberish on — a receipt, a
        prescription, an invoice, a foil blister. Blurring turns readable nonsense back into
        what it should have been: out-of-focus print.

        Do NOT do this by downsampling and re-inserting. That was the first attempt and it
        produced a mosaic of hard square blocks with a razor edge around the rectangle — far
        more obviously wrong than the gibberish it was hiding. A patch is only a fix if it
        disappears: blur properly, and ramp the blur to nothing over the outer `feather` of
        the patch so there is no boundary to see.

        radius is a fraction of the image WIDTH. feather is a fraction of the patch.
        """
        r = fitz.Rect(x0 * self.W, y0 * self.H, x1 * self.W, y1 * self.H)
        pm = fitz.Pixmap(fitz.csRGB, self.page.get_pixmap(clip=r))
        w, h, n = pm.width, pm.height, 3
        src = list(pm.samples)
        rad = max(1, int(radius * self.W))

        def box(buf, W, H, horizontal):
            out = [0] * len(buf)
            for a in range(H if horizontal else W):
                line = []
                for b in range(W if horizontal else H):
                    idx = ((a * W + b) if horizontal else (b * W + a)) * n
                    line.append(buf[idx:idx + n])
                acc = [sum(p[c] for p in line[:rad + 1]) for c in range(n)]
                cnt = rad + 1
                L = len(line)
                for b in range(L):
                    idx = ((a * W + b) if horizontal else (b * W + a)) * n
                    for c in range(n):
                        out[idx + c] = acc[c] // cnt
                    if b + rad + 1 < L:
                        for c in range(n): acc[c] += line[b + rad + 1][c]
                        cnt += 1
                    if b - rad >= 0:
                        for c in range(n): acc[c] -= line[b - rad][c]
                        cnt -= 1
            return out

        blur = box(box(src, w, h, True), w, h, False)

        fx, fy = max(1, int(w * feather)), max(1, int(h * feather))
        for y in range(h):
            wy = min(1.0, min(y, h - 1 - y) / fy)
            for x in range(w):
                k = min(wy, min(1.0, min(x, w - 1 - x) / fx))
                if k >= 1.0:
                    continue
                i0 = (y * w + x) * n
                for c in range(n):
                    blur[i0 + c] = int(blur[i0 + c] * k + src[i0 + c] * (1 - k))

        self.page.insert_image(r, pixmap=fitz.Pixmap(fitz.csRGB, w, h, bytes(bytearray(blur)), False))
        if wash and wash_opacity:
            self.page.draw_rect(r, color=None, fill=wash, fill_opacity=wash_opacity)
        return r

    def clock(self, cx, cy, r, hour, minute, ring=NEARBK, face=WHITE, hands=NEARBK,
              arc_to=None, arc_color=None, arc_r=0.62, arc_width=0.10, ring_width=0.09):
        """Draw an analogue dial in code.

        A clock face cannot be briefed. Ask an image model for "two hours" and it draws
        hands at whatever angle it likes — the duration is the whole point of the ad and it
        is the one thing the picture will not carry. So the dial is drawn here, like every
        other exact thing.

        cx, cy, r are fractions of the frame (r of the height). `arc_to` is the elapsed
        sweep in HOURS from 12 o'clock — 2.0 draws a two-hour wedge outline, 5/60 draws
        five minutes.
        """
        R = r * self.H
        C = fitz.Point(cx * self.W, cy * self.H)

        def at(hours, rad):
            a = hours / 12.0 * 2 * math.pi
            return fitz.Point(C.x + rad * math.sin(a), C.y - rad * math.cos(a))

        self.page.draw_circle(C, R, color=None, fill=ring)
        self.page.draw_circle(C, R * (1 - ring_width), color=None, fill=face)
        for i in range(12):
            long = (i % 3 == 0)
            p0 = at(i, R * (0.80 if long else 0.84))
            p1 = at(i, R * 0.92)
            self.page.draw_line(p0, p1, color=ring, width=R * (0.030 if long else 0.018))
        if arc_to:
            col = arc_color or ring
            steps = max(8, int(abs(arc_to) * 24))
            pts = [at(arc_to * i / steps, R * arc_r) for i in range(steps + 1)]
            for a, b in zip(pts, pts[1:]):
                self.page.draw_line(a, b, color=col, width=R * arc_width)
        # minute hand long, hour hand short — the reader checks this without knowing it
        self.page.draw_line(C, at(minute / 5.0, R * 0.78), color=hands, width=R * 0.045)
        self.page.draw_line(C, at(hour + minute / 60.0, R * 0.52),
                            color=hands, width=R * 0.062)
        self.page.draw_circle(C, R * 0.05, color=None, fill=hands)
        return C

    def save(self, out, zoom=1):
        self.page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(out)
        return out


# ------------------------------------------------------------------ lockup
def hook_lockup(src, out, line1_spans, line2, badge_text="TEST PRODUIT",
                kicker=("VAINQUEUR DU TEST", "2026"), scrim=0.6):
    """Reproduce the winning hook ads' editorial lockup on a raw photo.

    Geometry measured directly off the client's 742x742 winners, expressed as
    fractions so it holds at any output size.
      line1_spans : [(text, "sans"|"sans-bold"), ...] — the light line, bold on the number
      line2       : the bold underlined payoff line
    """
    c = Composer(src)
    c.scrim(0.68, 1.0, opacity=scrim)
    if kicker:
        c.scrim(0.0, 0.20, opacity=scrim * 0.65, top_down=True)
        c.tricolore(cx=0.0741, cy=0.0970, r=0.0404)
        c.text(0.1253, 0.0966, kicker[0], size=0.0377)
        c.text(0.1253, 0.1415, kicker[1], size=0.0377)

    if badge_text:
        c.badge(0.0445, 0.7116, badge_text, size=0.0404)

    L1, L2 = 0.0418, 0.0526
    w1 = sum(c.measure(t, k, L1) for t, k in line1_spans)
    w2 = c.measure(line2, "sans-bold", L2)
    for w, label in ((w1, "line 1"), (w2, "line 2")):
        if w > 0.94:
            raise SystemExit(
                f"{label} is {w:.3f} of the frame width at the winner's type size — "
                f"too long. Shorten the copy; do NOT shrink the type.")
    c.rich(0.0445, 0.8518, line1_spans, size=L1)
    c.text(0.0445, 0.9340, line2, key="sans-bold", size=L2)
    c.underline(0.0445, 0.0445 + w2, 0.9470)
    return c.save(out) if out else c



def canident_lockup(src, out, line1, line2, bullets=(), cta="Commandez Canident\u2122 maintenant \u2192",
                    wordmark="Canident\u2122", line1_color=NEARBK, line2_color=ROYAL,
                    head_top=0.108, bullet_cap=0.40, x=0.053, gap=0.111, align="left", sizes=(0.060, 0.100)):
    """Reproduce the Canident winners' pack-forward lockup on a generated pack ad.

    Geometry measured off the client's 743x738 winner and expressed as fractions, so one
    measurement holds at any output size. `bullets` may contain "\n" for a second line.
    Pass bullets=() for the ads that carry a headline only.
    """
    c = Composer(src)
    L1, L2 = sizes
    X = x
    # Line 1 sits ABOVE the pack and may run nearly full width, exactly as it does in the
    # client's winner. Line 2 sits BESIDE the pack, so it has to stay in the left half —
    # in the winner it is a single word.
    for txt, size, cap, label in ((line1, L1, 0.93 - X + 0.053, "line 1"),
                                  (line2, L2, 0.58 - X + 0.053, "line 2")):
        w = c.measure(txt, "sans-bold", size)
        if w > cap:
            raise SystemExit(
                f'{label} "{txt}" is {w:.3f} of the frame width (cap {cap}) — it would run '
                f'into the pack. Shorten it; do NOT shrink the type.')
    # Winner 1 sets its headline left and carries a CTA bar; winner 2 centres its headline
    # and carries no bar. Reproducing only one of those on every ad in a series makes the
    # shared furniture dominate the frame — which is what turns distinct artwork into
    # near-duplicates. Vary it the way the client's own two winners do.
    if align == "center":
        c.centered(head_top, line1, key="sans-bold", size=L1, color=line1_color, shadow=False)
        c.centered(head_top + gap, line2, key="sans-bold", size=L2, color=line2_color, shadow=False)
    else:
        c.text(X, head_top, line1, key="sans-bold", size=L1, color=line1_color, shadow=False)
        c.text(X, head_top + gap, line2, key="sans-bold", size=L2, color=line2_color, shadow=False)

    if bullets:
        y, size, lead = 0.314, 0.035, 0.047
        # Bullets sit BESIDE the pack, so every row has to stop before it. Same guard as
        # the headline, for the same reason: a bullet running under the box is unreadable.
        for b in bullets:
            for row in b.split("\n"):
                w = X + 0.071 + c.measure(row, "sans", size)
                if w > bullet_cap:
                    raise SystemExit(
                        f'bullet row "{row}" ends at {w:.3f} of the frame width (cap '
                        f'{bullet_cap}) — it would run under the pack. Shorten it.')
        for b in bullets:
            rows = b.split("\n")
            c.paw(X + 0.024, y - size * 0.34, 0.017)
            for i, row in enumerate(rows):
                c.text(X + 0.071, y + i * lead, row, key="sans" if i else "sans",
                       size=size, color=NEARBK, shadow=False)
            y += lead * len(rows) + 0.038

    if wordmark:
        c.text(X, 0.831, wordmark, key="sans-bold", size=0.042, color=TEAL, shadow=False)
    if cta:
        c.band(0.902, 1.0, fill=NAVY, opacity=1.0)
        c.centered(0.962, cta, key="sans-bold", size=0.046, color=WHITE, shadow=False)
    return c.save(out) if out else c


def slide(src, dx, dst=None, sample=(0.02, 0.02), scale=1.0):
    """Slide the picture sideways on its own flat background, and extend that background
    into the strip left behind. dx is a fraction of the width, positive = move right.

    Use when a generated pack or subject sits where the headline has to go. On a flat
    studio ground this is invisible and free — far better than paying to regenerate, and
    it also breaks the layout similarity that makes a fixed-format series read as
    duplicates."""
    pix = fitz.Pixmap(src)
    W, H = pix.width, pix.height
    r, g, b = pix.pixel(int(W * sample[0]), int(H * sample[1]))
    doc = fitz.open()
    page = doc.new_page(width=W, height=H)
    page.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=(r / 255, g / 255, b / 255))
    sw, sh = W * scale, H * scale
    off = dx * W
    top = H - sh                      # keep the subject standing on the same baseline
    page.insert_image(fitz.Rect(off, top, off + sw, top + sh), filename=src)
    out = dst or src
    page.get_pixmap().save(out)
    return out


def trim_uniform_border(src, dst=None, min_var=90.0, max_frac=0.10, _rounds=4):
    """Crop to a FIXED POINT, so calling this twice is a no-op.

    A single pass can leave a second, slightly different flat margin behind, and the next
    run of the script then crops again. That silently moved A3's frame from 922x927 to
    886x923 between two runs and broke a repair that had been measured against the first
    size. Converge here instead, once."""
    prev = None
    for _ in range(_rounds):
        out = _trim_once(src if prev is None else prev, dst or src,
                         min_var=min_var, max_frac=max_frac)
        if out == (prev if prev is not None else src):
            break
        prev = out
    return prev or src


def _trim_once(src, dst=None, min_var=90.0, max_frac=0.10):
    """Crop the flat white/grey margin the image model sometimes frames a photo with.

    Such a border reads as a "designed" edge in the feed and breaks the raw-phone-photo
    illusion the native ads depend on. Returns the path written (dst, or src in place).
    """
    pix = fitz.Pixmap(src)
    W, H = pix.width, pix.height

    def var_row(y):
        px = [pix.pixel(x, y) for x in range(2, W - 2, max(1, W // 60))]
        g = [sum(c) / 3 for c in px]
        m = sum(g) / len(g)
        return sum((v - m) ** 2 for v in g) / len(g)

    def var_col(x):
        px = [pix.pixel(x, y) for y in range(2, H - 2, max(1, H // 60))]
        g = [sum(c) / 3 for c in px]
        m = sum(g) / len(g)
        return sum((v - m) ** 2 for v in g) / len(g)

    lim_v, lim_h = int(H * max_frac), int(W * max_frac)
    top = next((y for y in range(lim_v) if var_row(y) > min_var), 0)
    bot = next((y for y in range(lim_v) if var_row(H - 1 - y) > min_var), 0)
    left = next((x for x in range(lim_h) if var_col(x) > min_var), 0)
    right = next((x for x in range(lim_h) if var_col(W - 1 - x) > min_var), 0)
    if not (top or bot or left or right):
        return src
    out = dst or src
    doc = fitz.open()
    pw, ph = W - left - right, H - top - bot
    page = doc.new_page(width=pw, height=ph)
    page.insert_image(fitz.Rect(-left, -top, W - left, H - top), filename=src)
    page.get_pixmap().save(out)
    return out



def pad_square(src, dst=None, fill=None, sample=(0.5, 0.02)):
    """Pad the short axis so the frame is exactly 1:1.

    `trim_uniform_border` leaves ragged ratios — 876x1024, 1007x1007, 938x1024 — and the
    Meta feed wants a square. Letterboxing in the placement crops the ad unpredictably, so
    square it here where the fill colour can be chosen. `fill` defaults to the pixel at
    `sample`, which is the right answer for the flat-ground and black-scan frames.
    """
    pix = fitz.Pixmap(src)
    W, H = pix.width, pix.height
    if W == H:
        return src
    S = max(W, H)
    if fill is None:
        r, g, b = pix.pixel(int(W * sample[0]), int(H * sample[1]))[:3]
        fill = (r / 255, g / 255, b / 255)
    doc = fitz.open()
    page = doc.new_page(width=S, height=S)
    page.draw_rect(fitz.Rect(0, 0, S, S), color=None, fill=fill)
    ox, oy = (S - W) / 2, (S - H) / 2
    page.insert_image(fitz.Rect(ox, oy, ox + W, oy + H), filename=src)
    out = dst or src
    page.get_pixmap().save(out)
    return out


def mirror(src, dst=None):
    """Flip left-for-right.

    The cheapest way to break a duplicate score between two images that share a subject.
    Two ear cutaways on white measured r = 0.632 against each other; mirroring one dropped
    the pair to 0.476 with no other change and no regeneration. Check the subject first —
    anatomy and scenery mirror fine, lettering and clock faces do not.
    """
    pix = fitz.Pixmap(fitz.csRGB, fitz.Pixmap(src)) if fitz.Pixmap(src).n > 3 \
        else fitz.Pixmap(src)
    W, H, n = pix.width, pix.height, pix.n
    row = W * n
    buf = bytearray(pix.samples)
    out_b = bytearray(len(buf))
    for y in range(H):
        b0 = y * row
        rev = bytearray(buf[b0:b0 + row])[::-1]
        if n == 3:                    # reversing bytes also reverses R,G,B within a pixel
            rev[0::3], rev[2::3] = rev[2::3], rev[0::3]
        out_b[b0:b0 + row] = rev
    new = fitz.Pixmap(pix.colorspace, W, H, bytes(out_b), False)
    out = dst or src
    new.save(out)
    return out


def crop_to(src, dst=None, top=0.0, bottom=1.0, left=0.0, right=1.0):
    """Crop by fractions of the frame. Returns the path written."""
    pix = fitz.Pixmap(src)
    W, H = pix.width, pix.height
    x0, x1 = int(left * W), int(right * W)
    y0, y1 = int(top * H), int(bottom * H)
    doc = fitz.open()
    page = doc.new_page(width=x1 - x0, height=y1 - y0)
    page.insert_image(fitz.Rect(-x0, -y0, W - x0, H - y0), filename=src)
    out = dst or src
    page.get_pixmap().save(out)
    return out


def erase_drawn_rules(src, dst=None, min_run=0.22, ink=150, blank=205,
                      margin=5, thickness=3, fill=(255, 255, 255), passes=3):
    """Rub out the straight rules an image model drew into a diagram — and nothing else.

    Asking for "a clear empty area where the callout labels will go" gets you literal drawn
    rectangles. They are erasable, but only where they run across blank paper, so each pixel
    goes only if the paper `margin` either side of the rule is blank. Where a rule crosses
    the drawing it is left alone and reads as part of the hatching.

    The rules are FOUND here, not passed in. Hard-coded pixel positions were the first
    attempt and they silently missed after `trim_uniform_border` changed the frame size by
    36 px — a repair that reports success and does nothing is worse than no repair.
    """
    # Run more than once: each pass whitens the clear stretches, which turns the pixels
    # that were blocked by their neighbours into erasable ones. One pass leaves the rule as
    # a dotted trace, which still reads as a drawn line.
    lines = None
    for _ in range(passes):
        lines = _erase_rules_once(src, dst, min_run, ink, blank, margin, thickness,
                                  fill, lines)
        src = dst or src
        if not lines:
            break
    return len(lines or ())


def _erase_rules_once(src, dst, min_run, ink, blank, margin, thickness, fill, lines=None):
    pix = fitz.Pixmap(fitz.csRGB, fitz.Pixmap(src))
    W, H = pix.width, pix.height
    g = pix.samples

    def dark(x, y):
        i = (y * W + x) * 3
        return min(g[i], g[i + 1], g[i + 2]) < ink

    def light(x, y):
        if not (0 <= x < W and 0 <= y < H):
            return False
        i = (y * W + x) * 3
        return min(g[i], g[i + 1], g[i + 2]) > blank

    # Detect the rules on the first pass only. Once a pass has whitened most of a rule the
    # surviving dashes are too short to be re-detected, so the positions carry forward and
    # each pass rubs out a little more of what the previous one unblocked.
    if lines is not None:
        found = list(lines)
    else:
        found = []
        for axis, N, M in (("v", W, H), ("h", H, W)):
            for a in range(N):
                run = best = 0
                for b in range(M):
                    on = dark(a, b) if axis == "v" else dark(b, a)
                    run = run + 1 if on else 0
                    if run > best:
                        best = run
                if best < min_run * M:
                    continue
                clear = 0
                for b in range(0, M, 3):
                    if axis == "v":
                        if light(a - margin, b) and light(a + margin, b):
                            clear += 1
                    elif light(b, a - margin) and light(b, a + margin):
                        clear += 1
                if clear / (M / 3.0) > 0.45:
                    found.append((axis, a))

    doc = fitz.open()
    page = doc.new_page(width=W, height=H)
    page.insert_image(fitz.Rect(0, 0, W, H), filename=src)
    col = tuple(c / 255 for c in fill)
    for axis, a in found:
        M = H if axis == "v" else W
        run_start = None
        for b in range(M):
            ok = (light(a - margin - thickness, b) and light(a + margin + thickness, b)) \
                if axis == "v" else \
                (light(b, a - margin - thickness) and light(b, a + margin + thickness))
            if ok and run_start is None:
                run_start = b
            elif not ok and run_start is not None:
                _paint(page, axis, a, run_start, b, thickness, col); run_start = None
        if run_start is not None:
            _paint(page, axis, a, run_start, M, thickness, col)
    out = dst or src
    page.get_pixmap().save(out)
    return found


def _paint(page, axis, a, b0, b1, thickness, col):
    r = fitz.Rect(a - thickness, b0, a + thickness + 1, b1) if axis == "v" \
        else fitz.Rect(b0, a - thickness, b1, a + thickness + 1)
    page.draw_rect(r, color=None, fill=col)


if __name__ == "__main__":
    import sys
    print(__doc__)
    print("fonts:", ", ".join(FONTS))
