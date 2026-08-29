#!/usr/bin/env bash
# ÉveilSens — 6 "native" clinical/medical mood shots, matching the register of the client's
# own win_05 (an unbranded medical-equipment close-up, no product, no text — a pattern-
# interrupt device). No product reference needed: nothing in these concepts shows the bottle.
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh

NAMES="CLN1_ultrasound_probe CLN2_vitals_monitor CLN3_instrument_tray CLN4_monitor_waveform CLN5_iv_drip CLN6_exam_light"

for name in $NAMES; do
  out="production_v2/${name}.png"
  if [ -f "$out" ]; then
    echo "SKIP $name (already exists)"
    continue
  fi
  "$SCRIPT" --prompt-file "prompts/${name}.txt" 1:1 "$out"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL $name (exit $rc)"
  fi
done
echo "CLN BATCH DONE"
