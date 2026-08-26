#!/usr/bin/env bash
# Ferméa round 2 — generate all 20 concepts on Nano Banana Pro.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# name : needs_ref(1/0)
JOBS="
BA1_decollete:0
BA2_inner_arm_holding:1
BA3_hand_back:0
BA4_thigh:0
BA5_stomach_holding:1
BA6_knee:0
U1_bathroom_holding:1
U2_kitchen_applying:1
U3_car_seat:1
U4_phone_screenshot:0
P1_pump_into_palm:1
P2_bottle_stones_garden:1
P3_bottle_marble_bathroom:1
P4_trustpilot_phone:1
S1_decollete_badge:0
S2_forearm_badge:0
S3_hand_badge:0
SH1_shelf_bestseller:1
SU1_preop_decollete:0
SU2_cardboard_sign:0
"

for line in $JOBS; do
  name="${line%%:*}"
  needs_ref="${line##*:}"
  out="production/${name}.png"
  if [ -f "$out" ]; then
    echo "SKIP $name (already exists)"
    continue
  fi
  if [ "$needs_ref" = "1" ]; then
    "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  else
    "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out"
  fi
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL $name (exit $rc)"
  fi
done
echo "BATCH DONE"
