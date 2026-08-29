#!/usr/bin/env bash
# ÉveilSens — 4 checklist/strong-claim ad bases, following up on win_01/win_02's own
# device (client pointed at those two as the angle to do more of, pushed more aggressive).
# Each is a clean product-on-pink shot with generous open space for a code-composited
# checklist + headline + guarantee band (see compose_ckl.py).
set -uo pipefail
cd "$(dirname "$0")"
source /tmp/claude-0/-home-user-Admachine/bf0cd556-3b67-5206-a435-cab5cfef6902/scratchpad/gemini.env
SCRIPT=/root/.claude/skills/static-remix/scripts/gemini-image-ref.sh
REF=assets/product_v2.png

NAMES="CKL1_20ans_aggressive CKL2_sans_ordonnance CKL3_avis_proof CKL4_discreet_aggressive"

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
echo "CKL BATCH DONE"
