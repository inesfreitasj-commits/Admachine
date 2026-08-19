#!/usr/bin/env bash
# gemini-image-ref.sh — generate one image with Nano Banana Pro
# (gemini-3-pro-image-preview), optionally conditioned on a reference image.
#
# Usage:
#   gemini-image-ref.sh "<prompt>" <aspect_ratio> <output_path> [reference_image_path]
#   gemini-image-ref.sh --prompt-file <file> <aspect_ratio> <output_path> [reference_image_path]
#
# Examples:
#   gemini-image-ref.sh "Split-screen US VS THEM ad ..." 4:5 production/concept_01_var_01.png assets/product.jpg
#   gemini-image-ref.sh --prompt-file briefs/c01.txt 1:1 production/c01.png assets/product.jpg
#
# Requires: GEMINI_API_KEY in the environment. curl and perl only — no jq, no
# base64 binary, so this runs unchanged on Git Bash for Windows.
#
# Exit codes:
#   0  image written
#   2  bad usage / missing file
#   3  GEMINI_API_KEY not set
#   4  HTTP 4xx (bad request, auth, quota) — do not retry blindly
#   5  HTTP 5xx (server error) — safe to retry later
#   6  HTTP 200 but no image in the response (often a safety block)
#
# Set GEMINI_DRY_RUN=1 to build and validate the request without calling the API
# (writes the request JSON to <output_path>.request.json and exits 0). Useful for
# checking prompt + reference-image wiring before spending money on a full batch.

set -uo pipefail

MODEL="gemini-3-pro-image-preview"
ENDPOINT="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent"

die() { echo "gemini-image-ref: $*" >&2; exit "${2:-2}"; }

# ---------- args ----------
if [ "${1:-}" = "--prompt-file" ]; then
  [ $# -ge 4 ] || die "usage: $0 --prompt-file <file> <aspect_ratio> <output_path> [reference_image]"
  PROMPT_FILE="$2"; ASPECT="$3"; OUT="$4"; REF="${5:-}"
  [ -f "$PROMPT_FILE" ] || die "prompt file not found: $PROMPT_FILE"
else
  [ $# -ge 3 ] || die "usage: $0 \"<prompt>\" <aspect_ratio> <output_path> [reference_image]"
  PROMPT_TEXT="$1"; ASPECT="$2"; OUT="$3"; REF="${4:-}"
  PROMPT_FILE=""
fi

if [ -z "${GEMINI_API_KEY:-}" ] && [ "${GEMINI_DRY_RUN:-}" != "1" ]; then
  die "GEMINI_API_KEY is not set in the environment" 3
fi
[ -n "$ASPECT" ] || die "aspect_ratio is required (e.g. 1:1, 4:5, 9:16, 16:9)"
[ -n "$OUT" ] || die "output_path is required"

mkdir -p "$(dirname "$OUT")" || die "cannot create output directory for $OUT"

TMPDIR_RUN="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_RUN"' EXIT
BODY="$TMPDIR_RUN/request.json"
RESP="$TMPDIR_RUN/response.json"

# ---------- JSON string encoding (perl, no deps) ----------
json_escape_file() {
  perl -0777 -pe '
    s/\\/\\\\/g; s/"/\\"/g;
    s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g;
    s/([\x00-\x1f])/sprintf("\\u%04x", ord($1))/ge;
  ' "$1"
}

if [ -n "$PROMPT_FILE" ]; then
  PROMPT_JSON="$(json_escape_file "$PROMPT_FILE")"
else
  printf '%s' "$PROMPT_TEXT" > "$TMPDIR_RUN/prompt.txt"
  PROMPT_JSON="$(json_escape_file "$TMPDIR_RUN/prompt.txt")"
fi
[ -n "$PROMPT_JSON" ] || die "prompt is empty"

# ---------- build contents.parts ----------
{
  printf '{"contents":[{"role":"user","parts":[{"text":"%s"}' "$PROMPT_JSON"

  if [ -n "$REF" ]; then
    [ -f "$REF" ] || die "reference image not found: $REF"
    case "$(printf '%s' "$REF" | tr 'A-Z' 'a-z')" in
      *.png)          MIME="image/png"  ;;
      *.jpg|*.jpeg)   MIME="image/jpeg" ;;
      *.webp)         MIME="image/webp" ;;
      *.gif)          MIME="image/gif"  ;;
      *)              MIME="image/jpeg" ;;
    esac
    printf ',{"inline_data":{"mime_type":"%s","data":"' "$MIME"
    perl -0777 -e 'use MIME::Base64; binmode STDIN; local $/; print encode_base64(<STDIN>, "");' < "$REF"
    printf '"}}'
  fi

  printf ']}],'
  printf '"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"%s"}}}' "$ASPECT"
} > "$BODY"

if [ "${GEMINI_DRY_RUN:-}" = "1" ]; then
  cp "$BODY" "${OUT}.request.json"
  echo "DRY-RUN  wrote ${OUT}.request.json  ($(perl -e 'print -s $ARGV[0]' "$BODY") bytes, aspect ${ASPECT}${REF:+, ref $(basename "$REF")})"
  exit 0
fi

# ---------- call ----------
HTTP="$(curl -sS -X POST \
  "${ENDPOINT}?key=${GEMINI_API_KEY}" \
  -H 'Content-Type: application/json' \
  --data-binary "@$BODY" \
  -o "$RESP" -w '%{http_code}')" || die "curl failed calling $ENDPOINT" 5

case "$HTTP" in
  200) ;;
  5*)  echo "gemini-image-ref: HTTP $HTTP (retryable) for $OUT" >&2
       head -c 600 "$RESP" >&2; echo >&2; exit 5 ;;
  *)   echo "gemini-image-ref: HTTP $HTTP for $OUT" >&2
       head -c 900 "$RESP" >&2; echo >&2; exit 4 ;;
esac

# ---------- decode the returned image ----------
# Pull the base64 payload out of the first inlineData / inline_data object.
# The object has no nested braces, so [^{}]* delimits it safely regardless of
# whether mimeType comes before or after data. Falls back to "first long base64
# blob" if the response shape ever changes.
perl -0777 -ne '
  if (/"inline_?[Dd]ata"\s*:\s*\{([^{}]*)\}/s) {
    my $obj = $1;
    if ($obj =~ /"data"\s*:\s*"([A-Za-z0-9+\/=\s]+)"/s) { print $1; exit 0 }
  }
  if (/"data"\s*:\s*"([A-Za-z0-9+\/=\s]{100,})"/s) { print $1; exit 0 }
  exit 1;
' "$RESP" > "$TMPDIR_RUN/b64" || {
  echo "gemini-image-ref: HTTP 200 but no image data returned for $OUT" >&2
  head -c 900 "$RESP" >&2; echo >&2; exit 6
}

perl -0777 -e '
  use MIME::Base64; binmode STDOUT; local $/;
  my $d = <STDIN>; $d =~ s/\s+//g; print decode_base64($d);
' < "$TMPDIR_RUN/b64" > "$OUT"

if [ ! -s "$OUT" ]; then
  rm -f "$OUT"
  die "decoded image was empty for $OUT" 6
fi

# The model always returns JPEG — the API has no output-format option (both
# outputMimeType and mimeType are rejected as unknown fields). So when the caller
# asks for a different extension, convert locally with PyMuPDF, which this skill
# already requires for PDF extraction. An ad platform will reject a JPEG named
# .png on upload, so the bytes and the extension must agree either way.
ACTUAL="$(perl -0777 -e '
  binmode STDIN; local $/; my $d = <STDIN>;
  print "jpg"  if substr($d,0,3) eq "\xff\xd8\xff";
  print "png"  if substr($d,0,8) eq "\x89PNG\r\n\x1a\n";
  print "webp" if substr($d,0,4) eq "RIFF" && substr($d,8,4) eq "WEBP";
' < "$OUT")"

WANT="$(printf '%s' "${OUT##*.}" | tr 'A-Z' 'a-z')"
[ "$WANT" = "jpeg" ] && WANT="jpg"

if [ -n "$ACTUAL" ] && [ "$ACTUAL" != "$WANT" ]; then
  CONVERTED=0
  if [ "$WANT" = "png" ] || [ "$WANT" = "jpg" ]; then
    mv -f "$OUT" "$TMPDIR_RUN/src.$ACTUAL"
    if python3 - "$TMPDIR_RUN/src.$ACTUAL" "$OUT" <<'PYCONV' 2>"$TMPDIR_RUN/conv.err"
import sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz
pix = fitz.Pixmap(sys.argv[1])
if pix.alpha:                      # JPEG has no alpha channel
    pix = fitz.Pixmap(pix, 0)
pix.save(sys.argv[2])
PYCONV
    then
      CONVERTED=1
    else
      mv -f "$TMPDIR_RUN/src.$ACTUAL" "$OUT"
      echo "gemini-image-ref: could not convert ${ACTUAL} -> ${WANT} ($(head -1 "$TMPDIR_RUN/conv.err"))" >&2
      echo "gemini-image-ref: install PyMuPDF (pip install --user pymupdf) for format conversion" >&2
    fi
  fi
  if [ "$CONVERTED" = "0" ]; then
    FIXED="${OUT%.*}.${ACTUAL}"
    [ "$FIXED" != "$OUT" ] && mv -f "$OUT" "$FIXED"
    echo "gemini-image-ref: model returned ${ACTUAL}; saved as $FIXED (not $OUT)" >&2
    OUT="$FIXED"
  fi
fi

BYTES="$(perl -e 'print -s $ARGV[0]' "$OUT")"
echo "OK  $OUT  (${BYTES} bytes, aspect ${ASPECT}${REF:+, ref $(basename "$REF")})"
