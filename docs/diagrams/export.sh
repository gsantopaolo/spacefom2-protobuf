#!/usr/bin/env bash
# Export every .drawio file in this folder to a GIF next to it.
# A diagram with one layer becomes a still GIF. A diagram with several layers
# becomes an animated GIF that adds one layer per frame (layer 1, then 1+2, ...).
#
# Needs: draw.io desktop (https://www.drawio.com) and ffmpeg.
# Usage: docs/diagrams/export.sh
set -euo pipefail

DRAWIO="${DRAWIO:-/Applications/draw.io.app/Contents/MacOS/draw.io}"
SCALE="${SCALE:-2}"
FRAME_SECONDS="${FRAME_SECONDS:-2.5}"
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

to_gif() {  # to_gif <input pattern or file> <output.gif> <frame rate>
  ffmpeg -loglevel error -y -framerate "$3" -i "$1" \
    -vf "split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=none" \
    -loop 0 "$2"
}

for src in "$HERE"/*.drawio; do
  name="$(basename "$src" .drawio)"
  # Layers are the cells whose parent is the root cell "0".
  layers=$(grep -o 'parent="0"' "$src" | wc -l | tr -d ' ')
  if [ "$layers" -le 1 ]; then
    "$DRAWIO" -x -f png -s "$SCALE" -b 20 -o "$TMP/$name.png" "$src" >/dev/null
    to_gif "$TMP/$name.png" "$HERE/$name.gif" 1
  else
    list="0"
    for ((i = 1; i <= layers; i++)); do
      "$DRAWIO" -x -f png -s "$SCALE" -b 20 -l "$list" -o "$TMP/$name-$(printf %02d "$i").png" "$src" >/dev/null
      list="$list,$i"
    done
    # Hold the last frame longer by repeating it.
    last="$TMP/$name-$(printf %02d "$layers").png"
    cp "$last" "$TMP/$name-$(printf %02d $((layers + 1))).png"
    cp "$last" "$TMP/$name-$(printf %02d $((layers + 2))).png"
    to_gif "$TMP/$name-%02d.png" "$HERE/$name.gif" "$(echo "1 / $FRAME_SECONDS" | bc -l)"
  fi
  echo "$name.gif"
done
