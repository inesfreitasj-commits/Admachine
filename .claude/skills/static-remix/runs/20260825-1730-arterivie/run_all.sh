#!/usr/bin/env bash
cd "$(dirname "$0")"
: "${GEMINI_API_KEY:?set GEMINI_API_KEY before running}"
R=assets/product.png
exec ./run_batch.sh \
  "S1_ct_gantry_feet:-" "S2_mri_control_glass:-" "S3_angio_suite:-" \
  "S4_man_entering_scanner:-" "S5_ultrasound_probe_groin:-" "S6_waiting_room_men:-" \
  "H1_artery_cutaway_jar:$R" "H2_two_arteries_compare:-" "H3_jar_orange_ground:$R" \
  "H4_couple_bed_relief:-" \
  "M1_penile_vs_coronary:-" "M2_plaque_timeline:-" "M3_pelvic_artery_map:-" \
  "M4_pill_vs_cleaning:-" \
  "P1_wife_holding_jar:$R" "P2_man_kitchen_jar:$R" "P3_bathroom_shelf_native:$R" \
  "N1_pharmacy_shelf:$R" "N2_cardboard_sign:-" "N3_doctor_artery_model:-"
