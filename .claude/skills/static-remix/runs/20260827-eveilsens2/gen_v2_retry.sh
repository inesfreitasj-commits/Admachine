#!/usr/bin/env bash
# Retry the 5 concepts that still had a garbled/off-brand label after the v2 (corrected
# reference) pass: LNG6, LEG2, LEG3, LEG4, DR1. LEG3 in particular reinvented the label
# design entirely, not just the text, so it gets a full regenerate too.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product_v2.png

NAMES="LNG6_hands_sheets LEG2_bathtub_edge LEG3_nightstand_reach LEG4_thigh_closeup DR1_gynecologue"

for name in $NAMES; do
  out="production_v2/${name}.png"
  if [ -f "$out" ]; then
    echo "SKIP $name (already exists)"
    continue
  fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL $name (exit $rc)"
  fi
done
echo "RETRY BATCH DONE"
