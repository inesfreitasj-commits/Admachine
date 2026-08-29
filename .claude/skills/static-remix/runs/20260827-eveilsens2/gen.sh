#!/usr/bin/env bash
# ÉveilSens round 2 — generate all 16 concepts on Nano Banana Pro.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

NAMES="LNG1_arched_back LNG2_side_profile_gasp LNG3_sheets_macro LNG4_morning_relaxed
LNG5_couple_embrace LNG6_hands_sheets LEG1_crossed_legs_bed LEG2_bathtub_edge
LEG3_nightstand_reach LEG4_thigh_closeup PRD1_pink_checklist PRD2_bundle_pricing
PRD3_ingredients_flatlay PRD4_hand_holding_bottle DR1_gynecologue DR2_hormones_comparison"

for name in $NAMES; do
  out="production/${name}.png"
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
echo "BATCH DONE"
