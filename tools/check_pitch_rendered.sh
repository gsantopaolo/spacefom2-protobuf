#!/usr/bin/env sh
# Fail if proposal/pitch.md changed without its rendered PDF and Word files.
# Reads the changed paths, one per line, on stdin:
#   git diff --name-only <base> <head> | sh tools/check_pitch_rendered.sh
set -eu

changed=$(cat)
has() { printf '%s\n' "$changed" | grep -qx "$1"; }

if ! has proposal/pitch.md; then
  echo "proposal/pitch.md unchanged; nothing to check."
  exit 0
fi

missing=""
for f in proposal/pitch.pdf proposal/pitch.docx; do
  has "$f" || missing="$missing $f"
done

if [ -n "$missing" ]; then
  echo "proposal/pitch.md changed, but these were not refreshed:$missing" >&2
  echo "Run: python tools/render_pdf.py proposal/pitch.md --out proposal && rm proposal/pitch.html" >&2
  exit 1
fi
echo "proposal/pitch.md, pitch.pdf and pitch.docx all changed."
