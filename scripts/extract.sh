#!/usr/bin/env bash
# usage: extract.sh <recording> [outdir]
# Probes the file, extracts 16 kHz mono audio, measures its level and, for video,
# builds timestamped contact sheets. Output defaults to <recording dir>/report/.
set -euo pipefail
IN="$1"
OUT="${2:-$(dirname "$(realpath "$IN")")/report}"
HOME_DIR="${REPORT_SKILL_HOME:-$HOME/.cache/report-skill}"
PY="$HOME_DIR/venv/bin/python"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"

ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels \
  -of json "$IN" > "$OUT/media.json"
DUR=$("$PY" -c "import json;print(int(float(json.load(open('$OUT/media.json'))['format']['duration'])))")
HASV=$("$PY" -c "import json;print('yes' if any(s['codec_type']=='video' for s in json.load(open('$OUT/media.json'))['streams']) else 'no')")
HASA=$("$PY" -c "import json;print('yes' if any(s['codec_type']=='audio' for s in json.load(open('$OUT/media.json'))['streams']) else 'no')")
printf 'duration: %dm%02ds  video: %s  audio: %s\n' $((DUR/60)) $((DUR%60)) "$HASV" "$HASA"

if [ "$HASA" = yes ]; then
  ffmpeg -y -v error -i "$IN" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/audio16k.wav"
  ffmpeg -i "$OUT/audio16k.wav" -af volumedetect -f null /dev/null 2>&1 \
    | grep -oE "(mean|max)_volume: [-0-9.]+ dB" > "$OUT/audio-levels.txt" || true
  echo "audio: $OUT/audio16k.wav ($(tr '\n' ' ' < "$OUT/audio-levels.txt"))"
else
  echo "no audio stream: nothing to transcribe" >&2
fi

if [ "$HASV" = yes ]; then
  "$PY" "$HERE/sheets.py" "$IN" "$OUT/sheets" "$DUR"
fi
echo "extracted to $OUT"
