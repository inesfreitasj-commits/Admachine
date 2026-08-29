#!/usr/bin/env bash
# ÉveilSens — 6 testimonial-quote ads (scene photo + dramatized quote + checklist + tagline),
# following the client's own win_03/win_06 layout device with fresh scenes and fresh
# wording. No age-specific hook this round (per client's choice), no second person in frame.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product_v2.png

NAMES="TST1_sheets_grip TST2_pillow_press TST3_legs_tangled TST4_shoulder_glance TST5_back_curve TST6_toes_curl"

for name in $NAMES; do
  out="production_v2/${name}.png"
  if [ -f "$out" ]; then
    echo "SKIP $name (already exists)"
    continue
  fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out" "$REF"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL $name (exit $rc)"
  fi
done
echo "TST BATCH DONE"
