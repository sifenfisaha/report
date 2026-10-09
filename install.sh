#!/usr/bin/env bash
# Links this checkout into Claude Code's skills folder and prepares the environment.
# usage: ./install.sh            (installs to ~/.claude/skills/report)
#        CLAUDE_SKILLS_DIR=/path ./install.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/report"
mkdir -p "$(dirname "$DEST")"
if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then
  echo "$DEST already exists and is not a symlink; move it aside and rerun" >&2
  exit 1
fi
ln -sfn "$HERE" "$DEST"
echo "linked $DEST -> $HERE"
chmod +x "$HERE"/scripts/*.sh "$HERE"/scripts/*.py "$HERE"/scripts/*.js
bash "$HERE/scripts/setup.sh"
echo "installed. Start a new Claude Code session and run: /report <recording>"
