#!/usr/bin/env bash
# Ferméa round 2b — 8 more concepts on Nano Banana Pro.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product.png

# name : needs_ref(1/0)
JOBS="
RS1_shelf_empty_note:0
RS2_shelf_last_bottle:1
UGC1_testimonial_nathalie:1
UGC2_testimonial_caroline:1
SM1_preop_arm:0
SM2_preop_thigh:0
TP1_hip_macro:0
TP2_ankle_macro:0
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
echo "BATCH2 DONE"
