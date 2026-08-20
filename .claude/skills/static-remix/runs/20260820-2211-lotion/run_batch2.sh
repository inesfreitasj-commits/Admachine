#!/usr/bin/env bash
cd ~/.claude/skills/static-remix/runs/20260820-2211-lotion
: "${GEMINI_API_KEY:?set GEMINI_API_KEY in the environment before running}"
GEN=~/.claude/skills/static-remix/scripts/gemini-image-ref.sh
gen () {
  local n="$1" ref="$2"
  [ -s "production/$n.png" ] && { echo "SKIP $n"; return; }
  local args=(--prompt-file "prompts/$n.txt" 1:1 "production/$n.png")
  [ "$ref" != "-" ] && args+=("$ref")
  for a in 1 2 3; do
    "$GEN" "${args[@]}" >>logs/gen2.log 2>&1 && { echo "OK   $n"; return; }
    local rc=$?; echo "FAIL $n rc=$rc try=$a"; [ $rc -eq 5 ] || return; sleep $((a*4))
  done
}
S=assets/ref_shelf.png; P=assets/product.png
for spec in "$@"; do gen "${spec%%:*}" "${spec##*:}"; done
echo "BATCH2 DONE"
