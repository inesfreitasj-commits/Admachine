#!/usr/bin/env bash
# ArtériVie topup — 20 ads across 3 new devices spotted in the client's latest winning ads:
# N (silent MRI/scan-mystery natives), P (dense mechanism/proof-bar heroes, composited text),
# F (fake-newspaper natives, composited headline/pull-quote).
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# no product reference needed
NO_REF="N1_mri_pelvis_scan N2_ct_angiogram_scan N3_doppler_scan N4_angiography_live
N5_xray_pelvis N6_echocardiogram N7_vascular_ultrasound
F1_artery_diagram F2_heart_network F3_stethoscope_desk F4_before_after_diagram F6_pelvic_floor_diagram"

# product reference needed
WITH_REF="P1_base P2_base P3_base P4_base P5_base P6_base P7_base F5_doctor_desk_jar"

for name in $NO_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out"
  [ $? -ne 0 ] && echo "FAIL $name"
done

for name in $WITH_REF; do
  out="production/${name}.png"
  if [ -f "$out" ]; then echo "SKIP $name"; continue; fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  [ $? -ne 0 ] && echo "FAIL $name"
done

echo "BATCH DONE"
