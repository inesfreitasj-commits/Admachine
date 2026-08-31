#!/usr/bin/env bash
# ArtériVie topup — 5 more: 2 newspaper-editorial (E), 2 UGC-style (U), 1 native scan-mystery
# (N8), requested explicitly by the client after the W1/W3 fix round.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# no product reference needed
NO_REF="N8_bp_monitor_flag E1_lifestyle_column E2_mechanism_sidebar"

# product reference needed
WITH_REF="U1_selfie_mirror U2_nightstand_flatlay"

for name in $NO_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out"
  [ $? -ne 0 ] && echo "FAIL $name"
done

for name in $WITH_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  [ $? -ne 0 ] && echo "FAIL $name"
done

echo "GEN5 BATCH DONE"
