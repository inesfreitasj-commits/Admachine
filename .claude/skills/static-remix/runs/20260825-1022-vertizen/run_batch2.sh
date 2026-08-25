#!/usr/bin/env bash
# Second VertiZen batch — 20 ads, after the client's teardown of batch 1.
cd "$(dirname "$0")"
: "${GEMINI_API_KEY:?set GEMINI_API_KEY before running}"
REF=assets/ref_pack_layout.png
exec ./run_batch.sh \
  "E1_inner_ear_cream:-"        "E2_two_ears_split:-"       "E3_absorption_path:-" \
  "E4_application_zones:-"      "E5_cause_vs_symptom:-" \
  "U1_mirror_selfie:$REF"       "U2_worktop_clutter:$REF"   "U3_behind_ear_daylight:-" \
  "U4_car_door_pocket:$REF"     "U5_kitchen_table_holding:$REF" \
  "U6_bedside_flash:$REF"       "U7_trolley_handle:-"       "U8_arms_length_wall:$REF" \
  "R1_applying_correct:$REF"    "R2_ugc_holding_correct:$REF" "R3_pack_hand_wall:$REF" \
  "N1_pharmacy_shelf:$REF"      "N2_cardboard_sign:-"       "N3_doctor_ear_model:-" \
  "N4_boxes_vs_rollon:$REF"
