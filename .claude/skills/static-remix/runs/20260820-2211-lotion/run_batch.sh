#!/usr/bin/env bash
cd ~/.claude/skills/static-remix/runs/20260820-2211-lotion
# The key is READ FROM THE ENVIRONMENT and never written into this file.
# Run as:  GEMINI_API_KEY=... ./run_batch.sh
: "${GEMINI_API_KEY:?set GEMINI_API_KEY in the environment before running}"
GEN=~/.claude/skills/static-remix/scripts/gemini-image-ref.sh
gen () {  # $1 = name, $2 = ref (or "-")
  local n="$1" ref="$2"
  [ -s "production/$n.png" ] && { echo "SKIP $n (exists)"; return; }
  local args=(--prompt-file "prompts/$n.txt" 1:1 "production/$n.png")
  [ "$ref" != "-" ] && args+=("$ref")
  for attempt in 1 2 3; do
    "$GEN" "${args[@]}" >>logs/gen.log 2>&1 && { echo "OK   $n"; return; }
    local rc=$?
    echo "FAIL $n rc=$rc attempt=$attempt"
    [ $rc -eq 5 ] || return   # only retry 5xx
    sleep $((attempt*4))
  done
}
S=assets/ref_shelf.png
P=assets/product.png
gen A2_shelf_rupture_stock  "$S"
gen A3_shelf_hand_lifting   "$S"
gen A4_hook_decollete        -
gen A5_hook_inner_arm        -
gen A6_hook_hand_back        -
gen B1_ingredients          "$P"
gen B2_bathroom_native      "$P"
gen B3_hydration_not_enough "$P"
gen B4_trustpilot_authority "$P"
gen B5_test_winner_hero     "$P"
gen C1_papier_froisse        -
gen C2_upper_arm_bathroom    -
gen C3_pinch_test            -
gen C4_knees_garden          -
gen C5_pharmacy_aisle        -
gen D1_ba_forearm            -
gen D2_ba_decollete          -
gen D3_ugc_holding          "$P"
gen D4_pump_into_palm       "$P"
echo "BATCH DONE"
