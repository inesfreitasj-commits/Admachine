#!/usr/bin/env python3
"""
label_boxes.py — find blank light-coloured label rectangles in a generated image, so text
can be composited INSIDE them instead of at guessed coordinates.

Written after prices composited at hardcoded x positions landed beside their price stickers
rather than on them. Measuring the render beats measuring by eye: the model places props
differently every generation, so any hardcoded coordinate is wrong the next time.

Usage:
    python3 label_boxes.py <image> --band <y0> <y1> [--min-w 0.04] [--thresh 215]

Pick the band tightly around the labels — including the darker shelf edge below them drops
the bright-row fraction and the detector finds nothing. When it returns 0 boxes, sample a
single row across the image first and read off the real threshold, rather than guessing.

Prints one "x0 y0 x1 y1" box per line, left to right, for use by a compositing step.
"""
import sys

try:
    try: import pymupdf as fitz
    except ImportError: import fitz
except ImportError:
    sys.exit("PyMuPDF required")


def find(path, y0f, y1f, min_w_frac=0.04, thresh=215, row_frac=0.45):
    pix = fitz.Pixmap(path)
    W, H, n, s = pix.width, pix.height, pix.n, pix.samples
    y0, y1 = int(y0f * H), int(y1f * H)

    # a column belongs to a label if most of the band's pixels there are bright and neutral
    cols = []
    for x in range(W):
        bright = 0
        rows = range(y0, y1, 2)
        for y in rows:
            i = (y * W + x) * n
            r, g, b = s[i], s[i + 1], s[i + 2]
            if r > thresh and g > thresh and b > thresh and max(r, g, b) - min(r, g, b) < 30:
                bright += 1
        cols.append(bright / max(1, len(list(rows))) > row_frac)

    # group contiguous bright columns into runs
    boxes, run = [], None
    for x, ok in enumerate(cols + [False]):
        if ok and run is None:
            run = x
        elif not ok and run is not None:
            if x - run >= min_w_frac * W:
                boxes.append((run, y0, x, y1))
            run = None

    # tighten each box vertically to the actual bright rows
    tight = []
    for bx0, _, bx1, _ in boxes:
        ys = []
        for y in range(y0, y1):
            cnt = 0
            for x in range(bx0, bx1, 3):
                i = (y * W + x) * n
                r, g, b = s[i], s[i + 1], s[i + 2]
                if r > thresh and g > thresh and b > thresh:
                    cnt += 1
            if cnt / max(1, len(range(bx0, bx1, 3))) > 0.6:
                ys.append(y)
        if ys:
            tight.append((bx0, min(ys), bx1, max(ys)))
    return tight, W, H


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    img = a[0]
    band = (float(a[a.index("--band") + 1]), float(a[a.index("--band") + 2])) if "--band" in a else (0.80, 0.98)
    thresh = int(a[a.index("--thresh") + 1]) if "--thresh" in a else 215
    minw = float(a[a.index("--min-w") + 1]) if "--min-w" in a else 0.04
    boxes, W, H = find(img, band[0], band[1], minw, thresh)
    print("# image %dx%d — %d label boxes found" % (W, H, len(boxes)), file=sys.stderr)
    for b in boxes:
        print("%d %d %d %d" % b)


if __name__ == "__main__":
    main()
