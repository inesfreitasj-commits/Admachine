#!/usr/bin/env python3
"""
extract_pdf_images.py — extract every image from a PDF of winning static ads and
label each one by the nearest section heading above it.

The heading font is auto-detected: we score every (font, size, bold) style by the
number of DISTINCT PAGES on which it appears in short text spans, and pick the
winner. In a swipe-file PDF the framework headings ("US VS THEM", "BOLD CLAIM",
"Before & After", ...) are the one styled run that repeats page after page in
short lines, so this finds them without hardcoding anything.

Usage:
    python3 extract_pdf_images.py <input.pdf> <outdir> [--min-px 120] [--min-area 40000]
                                  [--render-fallback] [--dpi 200]

Writes:
    <outdir>/img_0001_US_VS_THEM.png          one file per extracted image
    <outdir>/manifest.json                    machine-readable index
    <outdir>/manifest.txt                     human-readable index

manifest.json schema:
    {
      "pdf": "...", "pages": 42,
      "heading_style": {"font": "...", "size": 18.0, "bold": true, "pages_seen": 31},
      "frameworks": {"US VS THEM": 12, "BOLD CLAIM": 8, ...},
      "images": [
        {"file": "img_0001_US_VS_THEM.png", "page": 3, "framework": "US VS THEM",
         "width": 1080, "height": 1350, "bbox": [x0,y0,x1,y1], "source": "embedded"},
        ...
      ]
    }
"""

import json
import os
import re
import sys
from collections import defaultdict

try:
    # PyMuPDF. Newer releases prefer `import pymupdf`; `import fitz` still works
    # but warns. Either way the API below is identical.
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
except ImportError:
    sys.exit(
        "PyMuPDF is not installed. Install it with:\n"
        "    pip install --user pymupdf\n"
        "(the module is imported as `fitz`)"
    )

# A heading is short. Anything longer is body copy / ad transcription.
SHORT_SPAN_MAX_CHARS = 60
# Ignore styles smaller than this — captions, footers, page numbers.
MIN_HEADING_SIZE = 9.0


def slug(text, maxlen=40):
    s = re.sub(r"[^A-Za-z0-9]+", "_", (text or "").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen].rstrip("_") or "UNLABELED").upper()


def span_style(span):
    """Style key for a text span: font family, rounded size, bold flag."""
    return (span["font"], round(span["size"], 1), bool(span["flags"] & 2 ** 4))


def collect_spans(doc):
    """[(page_no, y_top, text, style)] for every non-empty span in the document."""
    spans = []
    for pno, page in enumerate(doc):
        try:
            data = page.get_text("dict")
        except Exception:
            continue
        for block in data.get("blocks", []):
            if block.get("type") != 0:  # 0 = text
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    spans.append((pno, span["bbox"][1], text, span_style(span)))
    return spans


def detect_heading_style(spans):
    """Pick the style seen on the most distinct pages in short spans."""
    pages_by_style = defaultdict(set)
    for pno, _y, text, style in spans:
        if len(text) > SHORT_SPAN_MAX_CHARS:
            continue
        if style[1] < MIN_HEADING_SIZE:
            continue
        # Pure page numbers / bullets are not headings.
        if re.fullmatch(r"[\d\W_]+", text):
            continue
        pages_by_style[style].add(pno)

    if not pages_by_style:
        return None, 0

    # Most pages wins; ties broken by larger font size, then by bold.
    best = max(
        pages_by_style.items(),
        key=lambda kv: (len(kv[1]), kv[0][1], kv[0][2]),
    )
    return best[0], len(best[1])


def heading_runs(spans, style):
    """
    Headings in document order: [(page_no, y_top, text)].
    Consecutive spans of the heading style on the same line-ish y are merged so a
    heading split across spans ("US VS " + "THEM") comes back as one string.
    """
    if style is None:
        return []
    hits = sorted(
        [(p, y, t) for (p, y, t, s) in spans if s == style],
        key=lambda r: (r[0], r[1]),
    )
    runs = []
    for pno, y, text in hits:
        if runs and runs[-1][0] == pno and abs(runs[-1][1] - y) < 3.0:
            runs[-1][2] = (runs[-1][2] + " " + text).strip()
        else:
            runs.append([pno, y, text])
    return [(p, y, re.sub(r"\s+", " ", t).strip()) for p, y, t in runs]


def nearest_heading(headings, pno, y_top, carry):
    """
    Nearest heading ABOVE this position: the last heading on the same page whose
    y is above y_top; otherwise the last heading seen on any earlier page
    (`carry`), because a framework section runs until the next heading.
    """
    best = None
    for hp, hy, ht in headings:
        if hp > pno or (hp == pno and hy > y_top + 2.0):
            break
        best = ht
    return best or carry or "UNLABELED"


def extract(pdf_path, outdir, min_px, min_area, render_fallback, dpi):
    doc = fitz.open(pdf_path)
    os.makedirs(outdir, exist_ok=True)

    spans = collect_spans(doc)
    style, pages_seen = detect_heading_style(spans)
    headings = heading_runs(spans, style)

    images = []
    counters = defaultdict(int)
    seen_xrefs = set()
    carry = None
    n = 0

    for pno, page in enumerate(doc):
        page_headings = [h for h in headings if h[0] == pno]
        if page_headings:
            carry = page_headings[-1][2]

        placed = []
        for info in page.get_images(full=True):
            xref = info[0]
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                rects = []
            y_top = min([r.y0 for r in rects], default=0.0)
            bbox = list(rects[0]) if rects else [0.0, 0.0, 0.0, 0.0]
            placed.append((y_top, xref, bbox))
        placed.sort(key=lambda r: r[0])

        page_got_image = False
        for y_top, xref, bbox in placed:
            key = (pno, xref)
            if key in seen_xrefs:
                continue
            seen_xrefs.add(key)
            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception:
                continue
            if pix.width < min_px or pix.height < min_px:
                continue  # icon, bullet, logo
            if pix.width * pix.height < min_area:
                continue
            if pix.n - pix.alpha >= 4:  # CMYK -> RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)

            framework = nearest_heading(headings, pno, y_top, carry)
            n += 1
            counters[framework] += 1
            fname = "img_%04d_%s.png" % (n, slug(framework))
            pix.save(os.path.join(outdir, fname))
            images.append({
                "file": fname,
                "page": pno + 1,
                "framework": framework,
                "width": pix.width,
                "height": pix.height,
                "bbox": [round(v, 1) for v in bbox],
                "source": "embedded",
            })
            page_got_image = True

        # Some swipe files are flattened screenshots with no embedded XObjects.
        if render_fallback and not page_got_image:
            framework = nearest_heading(headings, pno, 1e9, carry)
            pix = page.get_pixmap(dpi=dpi)
            if pix.width >= min_px and pix.height >= min_px:
                n += 1
                counters[framework] += 1
                fname = "img_%04d_%s.png" % (n, slug(framework))
                pix.save(os.path.join(outdir, fname))
                images.append({
                    "file": fname,
                    "page": pno + 1,
                    "framework": framework,
                    "width": pix.width,
                    "height": pix.height,
                    "bbox": [0.0, 0.0, round(page.rect.width, 1), round(page.rect.height, 1)],
                    "source": "rendered_page",
                })

    manifest = {
        "pdf": os.path.abspath(pdf_path),
        "pages": doc.page_count,
        "heading_style": None if style is None else {
            "font": style[0], "size": style[1], "bold": style[2], "pages_seen": pages_seen,
        },
        "headings_found": [{"page": p + 1, "text": t} for p, _y, t in headings],
        "frameworks": dict(sorted(counters.items(), key=lambda kv: -kv[1])),
        "images": images,
    }

    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    lines = ["PDF: %s (%d pages)" % (manifest["pdf"], manifest["pages"])]
    if manifest["heading_style"]:
        hs = manifest["heading_style"]
        lines.append("Heading font auto-detected: %s @ %.1fpt%s — seen on %d pages"
                     % (hs["font"], hs["size"], " bold" if hs["bold"] else "", hs["pages_seen"]))
    else:
        lines.append("Heading font: NOT DETECTED (no text layer?) — images labelled UNLABELED")
    lines.append("")
    lines.append("Frameworks detected (%d images total):" % len(images))
    for name, count in manifest["frameworks"].items():
        lines.append("  %-32s %d images" % (name, count))
    lines.append("")
    for im in images:
        lines.append("  %-40s p%-4d %-28s %dx%d"
                     % (im["file"], im["page"], im["framework"], im["width"], im["height"]))
    with open(os.path.join(outdir, "manifest.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    return manifest


def main():
    args = [a for a in sys.argv[1:]]
    if len(args) < 2:
        sys.exit(__doc__)
    pdf_path, outdir = args[0], args[1]

    def flag_val(name, default, cast):
        if name in args:
            return cast(args[args.index(name) + 1])
        return default

    min_px = flag_val("--min-px", 120, int)
    min_area = flag_val("--min-area", 40000, int)
    dpi = flag_val("--dpi", 200, int)
    render_fallback = "--render-fallback" in args

    if not os.path.isfile(pdf_path):
        sys.exit("PDF not found: %s" % pdf_path)

    manifest = extract(pdf_path, outdir, min_px, min_area, render_fallback, dpi)
    if not manifest["images"]:
        sys.exit("\nNo images extracted. Re-run with --render-fallback to rasterise pages instead.")


if __name__ == "__main__":
    main()
