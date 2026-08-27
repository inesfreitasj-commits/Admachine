#!/usr/bin/env bash
# Duréon batch — generate all 20 concepts on Nano Banana Pro.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# name : needs_ref(1/0)
JOBS="
BA1_avant_apres_couple:0
BA2_avant_apres_solo:0
BA3_avant_apres_office:0
BA4_avant_apres_outdoor:0
T1_testimonial_nicolas:1
T2_testimonial_philippe:1
T3_testimonial_alain:1
DR1_doctor_delorme:1
DR2_recommande_badge:1
CMP1_pills_vs_spray:1
CMP2_hand_choice:1
CMP3_clock_wait_time:1
SCI1_science_explained:1
SCI2_ingredients_macro:1
W1_hook_bold_claim:1
W2_hook_effect_duration:1
W3_hook_solo_confident:1
W4_hook_woman_outdoor:1
W5_hook_hands_intertwined:1
W6_shelf_rupture_stock:0
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
