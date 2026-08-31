#!/usr/bin/env bash
# Ferméa round 3 topup — 20 ads, weighted toward rupture-de-stock (client's doubled-down
# device this round) with fresh body areas/settings across before/after, TEST PRODUIT
# macro, surgical-marker, UGC testimonial, and product-in-use.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# no product reference needed (no bottle visible in frame)
NO_REF="RS5_pharmacist_restocking RS6_customer_phone_photo RS8_note_macro
RS9_evening_golden_hour RS10_standing_sign_printed
BA7_upper_arm BA8_neck_jawline BA9_waist
TP3_knee_macro TP4_upperarm_macro TP5_neck_macro
SM3_preop_waist SM4_preop_neck SM5_preop_knee
UGC4_painpoint_mirror"

# product reference needed (bottle visible)
WITH_REF="RS7_almost_gone_two_left UGC3_testimonial_francoise
P5_bottle_bathtub_edge P6_neck_application P7_spa_flatlay"

for name in $NO_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out"
  code=$?
  [ $code -ne 0 ] && echo "FAIL $name (exit $code)"
done

for name in $WITH_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  code=$?
  [ $code -ne 0 ] && echo "FAIL $name (exit $code)"
done

echo "BATCH DONE"
