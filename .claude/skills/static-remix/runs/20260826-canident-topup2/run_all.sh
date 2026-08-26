#!/usr/bin/env bash
cd "$(dirname "$0")"
: "${GEMINI_API_KEY:?set GEMINI_API_KEY before running}"
exec ./run_batch.sh \
  "PK1_box_bottle_kitchen:assets/product.png" "PK2_hand_holding_bottle:assets/product.png" "PK3_flatlay_bathroom_shelf:assets/product.png" \
  "PK4_pack_pastel_pair:assets/product.png" "PK5_pump_foam_dispensing:assets/product.png" "PK6_pack_price_shelf:assets/product.png" \
  "D1_gumline_macro_new_dog:-" "D2_scaler_tool_removing:-" "D3_open_mouth_full_row:-" \
  "D4_vet_gloved_exam:-" "D5_tartre_in_bowl:-" \
  "BA1_heure_timeline_terrier:-" "BA2_heure_timeline_labrador:-" "BA3_side_profile_before_after:-" \
  "NA1_owner_dog_asleep:-" "NA2_dog_licking_hand_after:-" "NA3_flatlay_pastel_native:assets/product.png" \
  "X1_invoice_redacted:-" "X2_anesthesia_mask_dog:-" "X3_two_dogs_compare:-"
