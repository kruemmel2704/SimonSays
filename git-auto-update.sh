#!/bin/bash
set -euo pipefail

# =========================
# Einstellungen
# =========================
REPO_URL="https://github.com/kruemmel2704/SimonSays"
SRC_DIR="/opt/simonsays-src"          # Git-Clone liegt hier
LIVE_DIR="/opt/simonsays-live"        # Hier laufen die Dateien
BRANCH="main"                         # ggf. "master"
INTERVAL=10                           # Sekunden

# Optional: Service/Command nach Update (leer lassen wenn nicht nötig)
# Beispiele:
# RESTART_CMD="systemctl restart simonsays"
# RESTART_CMD="pm2 restart simonsays"
# RESTART_CMD="docker compose -f /opt/simonsays-live/docker-compose.yml up -d --build"
RESTART_CMD=""

# Ordner/Dateien die NICHT überschrieben werden sollen (z.B. config, env, uploads)
# Mehrere --exclude möglich
RSYNC_EXCLUDES=(
  "--exclude=.env"
  "--exclude=config.ini"
  "--exclude=uploads/"
  "--exclude=data/"
  "--exclude=.git/"
)

# =========================
# Setup: Clone falls fehlt
# =========================
mkdir -p "$SRC_DIR" "$LIVE_DIR"

if [ ! -d "$SRC_DIR/.git" ]; then
  echo "[$(date '+%F %T')] Kein Git-Clone gefunden, klone Repository..."
  rm -rf "$SRC_DIR"
  git clone "$REPO_URL" "$SRC_DIR"
fi

cd "$SRC_DIR"

# Branch sicher auschecken
git fetch --all --prune
git checkout -B "$BRANCH" "origin/$BRANCH" >/dev/null 2>&1 || git checkout "$BRANCH"

echo "[$(date '+%F %T')] Auto-Deploy gestartet."
echo "  SRC : $SRC_DIR"
echo "  LIVE: $LIVE_DIR"
echo "  BR  : $BRANCH"
echo "----------------------------------------"

# =========================
# Loop
# =========================
while true; do
  git fetch --quiet

  LOCAL="$(git rev-parse HEAD)"
  REMOTE="$(git rev-parse "origin/$BRANCH")"

  if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date '+%F %T')] Update erkannt -> pull + deploy..."
    git pull --rebase --autostash --quiet

    echo "[$(date '+%F %T')] Deploy via rsync..."
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$SRC_DIR"/ "$LIVE_DIR"/

    echo "[$(date '+%F %T')] Deploy fertig: $(git rev-parse HEAD)"

    if [ -n "$RESTART_CMD" ]; then
      echo "[$(date '+%F %T')] Restart: $RESTART_CMD"
      bash -lc "$RESTART_CMD" || true
    fi

    echo "----------------------------------------"
  fi

  sleep "$INTERVAL"
done
