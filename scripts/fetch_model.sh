#!/usr/bin/env bash
# usage: fetch_model.sh <tiny|base|small|medium|large-v3|turbo|distil-large-v3|org/repo>
# Downloads a CTranslate2 whisper model into ~/.cache/report-skill/models/<name>
# with plain curl (resumable). Hugging Face's chunked downloader throttles itself
# on slow links; a single HTTP stream is usually several times faster.
set -euo pipefail
NAME="$1"
HOME_DIR="${REPORT_SKILL_HOME:-$HOME/.cache/report-skill}"
case "$NAME" in
  tiny) REPO=Systran/faster-whisper-tiny ;;
  base) REPO=Systran/faster-whisper-base ;;
  small) REPO=Systran/faster-whisper-small ;;
  medium) REPO=Systran/faster-whisper-medium ;;
  large-v3) REPO=Systran/faster-whisper-large-v3 ;;
  turbo|large-v3-turbo) REPO=mobiuslabsgmbh/faster-whisper-large-v3-turbo ;;
  distil-large-v3) REPO=Systran/faster-distil-whisper-large-v3 ;;
  */*) REPO="$NAME"; NAME="${NAME##*/}" ;;
  *) echo "unknown model: $NAME" >&2; exit 1 ;;
esac
DEST="$HOME_DIR/models/$NAME"
mkdir -p "$DEST"
FILES=$(curl -sL "https://huggingface.co/api/models/$REPO" | python3 -c "
import sys, json
for s in json.load(sys.stdin)['siblings']:
    n = s['rfilename']
    if not n.startswith(('.git', 'README')): print(n)")
for f in $FILES; do
  echo "[$(date +%T)] $NAME: fetching $f"
  ok=0
  for attempt in 1 2 3 4 5; do
    if curl -sL -C - --retry 5 --retry-all-errors -o "$DEST/$f" "https://huggingface.co/$REPO/resolve/main/$f"; then ok=1; break; fi
    echo "retry $attempt"; sleep 3
  done
  [ "$ok" = 1 ] || { echo "failed: $f" >&2; exit 1; }
done
SIZE=$(stat -c %s "$DEST/model.bin")
[ "$SIZE" -gt 1000000 ] || { echo "model.bin looks truncated ($SIZE bytes)" >&2; exit 1; }
echo "[$(date +%T)] $NAME ready in $DEST ($((SIZE/1048576)) MB)"
