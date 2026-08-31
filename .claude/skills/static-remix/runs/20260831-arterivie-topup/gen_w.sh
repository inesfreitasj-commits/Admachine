#!/usr/bin/env bash
# ArtériVie topup — 3 replacements for F2/F3/F5 (flagged as not good: empty layout).
# W1 = win_06's partner-testimonial device, W2 = win_05's icon/graphic device (both
# previously untouched winning-ad devices), W3 = a redesigned newspaper native with a real
# composited body paragraph so the text fills the page instead of floating over blank paper.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

for name in W1_temoignage_epouse W2_icone_masculin W3_encart_temoignages; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  [ $? -ne 0 ] && echo "FAIL $name"
done
echo "W BATCH DONE"
