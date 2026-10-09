#!/usr/bin/env bash
# One-time environment for the report skill. Idempotent.
# Creates ~/.cache/report-skill/venv with faster-whisper, numpy, Pillow, markdown
# and checks the external tools the pipeline needs.
set -euo pipefail
HOME_DIR="${REPORT_SKILL_HOME:-$HOME/.cache/report-skill}"
mkdir -p "$HOME_DIR/models"

missing=0
for t in ffmpeg ffprobe python3; do
  if ! command -v "$t" >/dev/null 2>&1; then echo "missing: $t" >&2; missing=1; fi
done
[ "$missing" = 0 ] || { echo "install the missing tools and rerun" >&2; exit 1; }

PY="$HOME_DIR/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "creating venv at $HOME_DIR/venv"
  if command -v uv >/dev/null 2>&1; then
    uv venv --quiet "$HOME_DIR/venv"
    uv pip install --quiet --python "$PY" faster-whisper numpy Pillow markdown
  else
    python3 -m venv "$HOME_DIR/venv"
    "$HOME_DIR/venv/bin/pip" install --quiet faster-whisper numpy Pillow markdown
  fi
fi
"$PY" -c "import faster_whisper, numpy, PIL, markdown" && echo "venv ok: $HOME_DIR/venv"

# PDF rendering is optional; report what is available.
if command -v node >/dev/null 2>&1 && node "$(dirname "$0")/render_pdf.js" --check >/dev/null 2>&1; then
  echo "pdf: playwright ok"
else
  echo "pdf: playwright not found (needed only for PDFs: npm i -g playwright && npx playwright install chromium)"
fi
command -v pdfinfo >/dev/null 2>&1 && echo "pdf: poppler ok" || echo "pdf: poppler-utils missing (optional, used for page counts)"

if ls "$HOME_DIR/models" 2>/dev/null | grep -q .; then
  echo "models cached: $(ls "$HOME_DIR/models" | tr '\n' ' ')"
else
  echo "models cached: none yet (the first transcription downloads one)"
fi
