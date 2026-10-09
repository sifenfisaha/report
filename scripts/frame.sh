#!/usr/bin/env bash
# usage: frame.sh <recording> <seconds> <out.png> [W:H:X:Y] [scale]
# Grabs one full-resolution frame at <seconds>. With a crop (ffmpeg crop syntax,
# width:height:x:y) the region is cut out and upscaled (default 2x, lanczos) so
# small on-screen text becomes legible when the image is read.
set -euo pipefail
IN="$1"; T="$2"; OUT="$3"; CROP="${4:-}"; SCALE="${5:-2}"
mkdir -p "$(dirname "$OUT")"
if [ -n "$CROP" ]; then
  ffmpeg -y -v error -ss "$T" -i "$IN" -frames:v 1 -vf "crop=$CROP,scale=iw*$SCALE:-1:flags=lanczos" "$OUT"
else
  ffmpeg -y -v error -ss "$T" -i "$IN" -frames:v 1 "$OUT"
fi
echo "$OUT"
