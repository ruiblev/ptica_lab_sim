#!/bin/bash

# Diretorio do projeto
REPO_DIR="/Users/ruicampos/.gemini/antigravity/scratch/otica/ptica_lab_sim"
LOG_FILE="$REPO_DIR/daily_heartbeat.log"

cd "$REPO_DIR" || exit

# Adiciona um registo de atividade
echo "Daily heartbeat at $(date)" >> "$LOG_FILE"
# Mantem apenas as ultimas 100 linhas no log
tail -n 100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

# Git operations
/usr/bin/git add "$LOG_FILE"
/usr/bin/git commit -m "chore: automatic daily heartbeat [$(date)]"
/usr/bin/git push origin main
