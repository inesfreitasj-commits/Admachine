#!/usr/bin/env bash
# Nano Banana returned 503 "high demand" on every call. That is Google's capacity, not the
# prompts — so this grinds with LONG backoff until the model frees up, and writes each image
# the moment it lands.
cd "$(dirname "$0")"
: "${GEMINI_API_KEY:?}"
GEN=~/.claude/skills/static-remix/scripts/gemini-image-ref.sh
L=assets/ref_pack_layout.png
SPECS=(A1_ugc_ba_kitchen:- A2_ugc_ba_evening:- A3_vector_ankle_question:- A4_vector_sock_groove:-
       "A5_pack_legs_arrows:$L" A6_thermal_scanner:- A7_doppler_ankle:-
       B1_sock_groove_real:- B2_shoe_wont_fit:- B3_compression_stockings:- B4_feet_up_tv:- B5_diuretics_table:-
       C1_four_crossed_out:- C2_pills_vs_stockings:- C3_timeline_three_stages:-
       "C4_authority_card:$L" "C5_suedoises_secret:$L"
       D1_ba_ankles_pair:- "D2_woman_holding_tube:$L" "D3_applying_cream:$L")
for round in 1 2 3 4 5 6 7 8 9 10 11 12; do
  left=0
  for spec in "${SPECS[@]}"; do
    n="${spec%%:*}"; ref="${spec##*:}"
    [ -s "production/$n.png" ] && continue
    args=(--prompt-file "prompts/$n.txt" 1:1 "production/$n.png")
    [ "$ref" != "-" ] && args+=("$ref")
    if "$GEN" "${args[@]}" >>logs/gen.log 2>&1; then echo "OK   $n"; else left=$((left+1)); fi
  done
  done_n=$(ls production/*.png 2>/dev/null | wc -l)
  echo "-- round $round: $done_n/20 done, $left still failing"
  [ "$done_n" -ge 20 ] && break
  sleep $((round < 4 ? 45 : 90))
done
echo "RETRY RUNNER FINISHED: $(ls production/*.png 2>/dev/null | wc -l)/20"
