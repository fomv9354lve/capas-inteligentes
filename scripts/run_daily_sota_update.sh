#!/bin/zsh
set -euo pipefail

ROOT="/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES"
cd "$ROOT"

mkdir -p outputs/logs outputs/sota_watch

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CAPAS daily SOTA watch started"
python3 scripts/update_sota_watch.py

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CAPAS validation started"
python3 capas.py validate

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CAPAS daily SOTA watch finished"
