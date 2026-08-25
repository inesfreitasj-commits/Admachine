#!/usr/bin/env python3
"""dupe_gate.py — perceptual duplicate check, including AGAINST THE CLIENT'S WINNERS.

    python3 dupe_gate.py final                       # my ads against each other
    python3 dupe_gate.py final assets/winning_ads    # ...and against the winners too

Why the second argument exists
------------------------------
For four products the gate only ever compared my own ads with each other. It passed a
batch in which three of seven "variations" were the client's winning ads re-rendered with
one number changed — same headline, same layout, same props, and in one case the winner's
handwritten line copied verbatim. Every pair scored clean, because a copy of a winner does
not resemble the OTHER ads in the batch.

A duplicate of theirs is worse than a duplicate of mine. Meta reads it as duplicate creative
against an ad already running, and the client paid for a variation, not a re-render.

Thresholds — and be honest about what each one is worth
-------------------------------------------------------
    r >= 0.60 against another of MY ads     -> A GATE. Fix it before delivery.
    r >= 0.45 against one of THEIR WINNERS  -> A REVIEW LIST. Not a verdict.

The first is a gate because it is measured: the client's own two Canident winners score
r = +0.031 against each other, so a shared brand format does not force a high score, and a
high score between two of my own ads is a real defect.

The second cannot be a gate, and pretending otherwise would be worse than not running it.
Measured against what the client actually said:

    A2 vs win_02   0.713   client: "completely the same"      correctly flagged
    A1 vs win_01   0.707   client: accepted it                FALSE POSITIVE
    A3 vs win_02   0.610   client: "very similar"             correctly flagged
    C2 vs win_08   0.446   client: accepted it                just under
    A7 vs win_04   0.370   client: "completely the same"      MISSED
    A6 vs win_05   0.359   client: "completely the same"      MISSED

There is no threshold that separates those. A 16x16 luminance signature sees "warm ground,
one central mass" and little else, so an ear diagram and a pack shot can score 0.58 while
looking nothing alike — and the two ads the client rejected hardest scored LOWEST of all,
because what they copied was the WORDS, not the picture.

So: treat the winner column as a shortlist to open side by side, nothing more. The check
that actually catches a copied ad is `assert_not_winner_copy` in compose_text.py, which is
exact, plus your own eyes on the closest winner.
"""
import glob
import math
import os
import sys

import pymupdf as fitz

MINE = 0.60
THEIRS = 0.45


def signature(path, n=16):
    """16x16 greyscale thumbnail, flattened. Small enough that wording and fine detail drop
    out and only the large shapes — the mass, the ground, the layout — survive."""
    doc = fitz.open()
    page = doc.new_page(width=n, height=n)
    page.insert_image(fitz.Rect(0, 0, n, n), filename=path)
    return list(fitz.Pixmap(fitz.csGRAY, page.get_pixmap()).samples)


def pearson(a, b):
    k = len(a)
    ma, mb = sum(a) / k, sum(b) / k
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da and db else 0.0


def load(folder):
    files = sorted(f for e in ("png", "jpg", "jpeg")
                   for f in glob.glob(os.path.join(folder, f"*.{e}")))
    return {f: signature(f) for f in files}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    mine = load(argv[0])
    if not mine:
        print(f"no images in {argv[0]}")
        return 2
    theirs = load(argv[1]) if len(argv) > 1 else {}
    fails = 0

    print(f"\n{'='*74}\nAGAINST EACH OTHER — {len(mine)} ads, "
          f"{len(mine)*(len(mine)-1)//2} pairs, gate r = {MINE}\n{'='*74}")
    rows = []
    names = list(mine)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            rows.append((pearson(mine[names[i]], mine[names[j]]),
                         os.path.basename(names[i]), os.path.basename(names[j])))
    rows.sort(reverse=True)
    over = [r for r in rows if r[0] >= MINE]
    fails += len(over)
    for v, a, b in (over or rows[:3]):
        print(f"  {'FAIL' if v >= MINE else '    '} {v:+.3f}  {a:<32} {b}")
    if not over:
        print(f"  clean — highest pair {rows[0][0]:+.3f}")

    if theirs:
        print(f"\n{'='*74}\nAGAINST THE CLIENT'S WINNERS — {len(theirs)} winners, "
              f"gate r = {THEIRS}\n{'='*74}")
        worst = {}
        for m, sm in mine.items():
            best = max(((pearson(sm, st), os.path.basename(t)) for t, st in theirs.items()))
            worst[os.path.basename(m)] = best
        for name, (v, win) in sorted(worst.items(), key=lambda kv: -kv[1][0]):
            flag = "OPEN THESE" if v >= THEIRS else "          "
            print(f"  {flag} {v:+.3f}  {name:<32} closest to {win}")
        print("\n  ADVISORY, NOT A GATE — see the module docstring. Open each flagged ad"
              "\n  beside the winner named and decide yourself. If it IS a re-render, the"
              "\n  fix is the LARGE shapes: dominant mass, ground colour, crop, where the"
              "\n  pack sits. Rewriting the headline will not move this number.")

    print(f"\n{'='*74}\n{'CLEAN' if not fails else str(fails) + ' PAIR(S) OVER THE GATE'}"
          f"\n{'='*74}\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
