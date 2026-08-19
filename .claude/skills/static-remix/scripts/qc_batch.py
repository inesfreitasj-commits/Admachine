#!/usr/bin/env python3
"""
qc_batch.py — mechanical quality gate for a finished production/ directory.

Catches two defects that shipped to a real user and should never ship again:

  1. NEAR-DUPLICATE PAIRS. A var_01/var_02 whose only difference was overlay wording
     produced two images that read identically in a feed — half a concept's budget
     buying nothing.
Colour numbers are printed but NOTHING is gated on them, after two honest failures:

  - Gating on absolute warmth flagged 28 of 33 images, because warm lamplight makes
    every bright pixel warm: skin, wood, lampshades, blush backgrounds.
  - Gating on within-pair colour swing flagged five CORRECT pairs, because a pair whose
    variation axis is lighting is supposed to swing.

The lesson is that colour statistics cannot detect product identity in scene photography
— scene lighting dominates the signal entirely. A check that fires on correct work is
worse than no check, because it teaches you to ignore the output.

So product IDENTITY and SCALE are not automated here at all. They need a human eye, and
the amber-glass swap that shipped to a real user would not have been caught by any
statistic in this file. The script prints a per-image checklist instead, and SKILL.md
step 7.5 makes that review mandatory rather than optional.

Usage:
    python3 qc_batch.py <production_dir> [--dup-threshold 0.60] [--warm-threshold 14]

Threshold calibration (measured on a real 33-image run, not guessed):
    Pairs the user accepted            r = -0.47 .. 0.53
    Pairs the user called too similar  r =  0.65 .. 0.81
  0.60 sits in the gap. It flags every pair that was actually complained about and
  passes every pair that was not. Raise it if a legitimately similar format (two
  split-screens, say) keeps tripping it.

Exit codes:
    0  nothing flagged
    1  at least one pair or image flagged  (so it gates rather than merely informs)
    2  bad usage
"""

import os
import re
import sys
from collections import defaultdict

try:
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
except ImportError:
    sys.exit("PyMuPDF required: pip install --user pymupdf")

GRID = 16  # signature resolution


def signature(path):
    """Downscaled greyscale signature — coarse enough to ignore noise, fine enough
    to separate genuinely different compositions."""
    doc = fitz.open(path)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(GRID / doc[0].rect.width,
                                               GRID / doc[0].rect.height))
    s, n = pix.samples, pix.n
    out = []
    for i in range(pix.width * pix.height):
        r, g, b = s[i * n], s[i * n + 1], s[i * n + 2]
        out.append(0.299 * r + 0.587 * g + 0.114 * b)
    doc.close()
    return out


def correlation(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    num = sum(x * y for x, y in zip(da, db))
    den = (sum(x * x for x in da) ** 0.5) * (sum(y * y for y in db) ** 0.5)
    return num / den if den else 1.0


def bright_cast(path):
    """Mean RGB of the brightest pixels — the product body and lit surfaces.
    A warm cast means the white bottle has drifted to cream/ivory."""
    doc = fitz.open(path)
    pix = doc[0].get_pixmap(dpi=24)
    s, n = pix.samples, pix.n
    px = []
    for i in range(pix.width * pix.height):
        r, g, b = s[i * n], s[i * n + 1], s[i * n + 2]
        if r > 200 and g > 180 and b > 150:
            px.append((r, g, b))
    doc.close()
    if not px:
        return None
    return tuple(sum(c[k] for c in px) / len(px) for k in range(3))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    root = args[0]
    if not os.path.isdir(root):
        sys.exit("not a directory: %s" % root)

    def flag(name, default, cast):
        return cast(args[args.index(name) + 1]) if name in args else default

    dup_t = flag("--dup-threshold", 0.60, float)
    warm_t = flag("--warm-threshold", 14.0, float)

    files = sorted(f for f in os.listdir(root)
                   if f.lower().endswith((".png", ".jpg", ".jpeg")))
    if not files:
        sys.exit("no images in %s" % root)

    pairs = defaultdict(dict)
    for f in files:
        m = re.match(r"(.+?)_var_(\d+)\.", f)
        if m:
            pairs[m.group(1)][m.group(2)] = f

    problems = []
    casts = {}

    print("=" * 68)
    print("SCENE WARMTH  (advisory only - warm scenes read warm; NOT a pass/fail)")
    print("=" * 68)
    for f in files:
        c = bright_cast(os.path.join(root, f))
        if c is None:
            print("  %-28s no bright pixels sampled" % f[:28])
            continue
        warm = c[0] - c[2]
        casts[f] = warm
        print("  %-28s RGB %3.0f,%3.0f,%3.0f   warm%+5.1f" % (f[:28], c[0], c[1], c[2], warm))

    print()
    print("=" * 68)
    print("PAIR DISTINCTNESS  (variations must differ visually, not just in wording)")
    print("=" * 68)
    if not pairs:
        print("  no var_NN pairs found")
    for concept in sorted(pairs):
        vs = pairs[concept]
        if len(vs) < 2:
            continue
        keys = sorted(vs)
        for i in range(len(keys) - 1):
            a, b = vs[keys[i]], vs[keys[i + 1]]
            r = correlation(signature(os.path.join(root, a)),
                            signature(os.path.join(root, b)))
            bad = r > dup_t
            print("  %-34s r=%.3f  %s"
                  % ("%s %s/%s" % (concept, keys[i], keys[i + 1]), r,
                     "<-- TOO SIMILAR" if bad else "ok"))
            if bad:
                problems.append("near-duplicate: %s %s/%s" % (concept, keys[i], keys[i + 1]))

    print()
    print("=" * 68)
    print("WITHIN-PAIR COLOUR SWING  (advisory - a lighting-axis pair SHOULD swing)")
    print("=" * 68)
    for concept in sorted(pairs):
        vs = pairs[concept]
        keys = sorted(vs)
        vals = [casts.get(vs[k]) for k in keys if casts.get(vs[k]) is not None]
        if len(vals) < 2:
            continue
        swing = max(vals) - min(vals)
        print("  %-34s swing %5.1f" % (concept, swing))

    print()
    print("=" * 68)
    print("MANUAL CHECKS — open EVERY image with the Read tool. Never judge a pair")
    print("on one image; a whole concept once shipped with the wrong bottle that way.")
    print("No statistic below replaces this. Product IDENTITY (glass vs plastic, dropper")
    print("vs nozzle, lotus vs petal) and SCALE are only visible to a human eye.")
    print("=" * 68)
    for f in files:
        print("  [ ] %-30s identity - scale - grip - integration - copy" % f[:30])

    print()
    if problems:
        print("FLAGGED %d:" % len(problems))
        for p in problems:
            print("  - %s" % p)
        sys.exit(1)
    print("Nothing flagged mechanically. Manual checks above are still required.")
    sys.exit(0)


if __name__ == "__main__":
    main()
