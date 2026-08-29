#!/usr/bin/env bash
# ÉveilSens round 2, v2 — regenerate all 16 concepts against the CORRECTED product
# reference (assets/product_v2.png). The original assets/product.png, inherited unmodified
# from the earlier incomplete run, turned out to already have garbled label text baked in —
# traced all the way back to a straight page-slice of the client's own sales-page PDF. Every
# v1 render was faithfully copying that already-broken reference, which is why blur+retype
# in code never fully disappeared: the photo behind the patch was never right to begin with.
# Output goes to production_v2/ so it can be reviewed against the delivered v1 set before
# anything is overwritten.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product_v2.png

mkdir -p production_v2

NAMES="LNG1_arched_back LNG2_side_profile_gasp LNG3_sheets_macro LNG4_morning_relaxed
LNG5_couple_embrace LNG6_hands_sheets LEG1_crossed_legs_bed LEG2_bathtub_edge
LEG3_nightstand_reach LEG4_thigh_closeup PRD1_pink_checklist PRD2_bundle_pricing
PRD3_ingredients_flatlay PRD4_hand_holding_bottle DR1_gynecologue DR2_hormones_comparison"

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
echo "BATCH DONE"
