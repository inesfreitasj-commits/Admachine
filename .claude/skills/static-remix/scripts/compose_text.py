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


def trim_uniform_border(src, dst=None, min_var=90.0, max_frac=0.10):
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


if __name__ == "__main__":
    import sys
    print(__doc__)
    print("fonts:", ", ".join(FONTS))
