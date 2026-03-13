#!/usr/bin/env bash
# Skrypt do uruchomienia eksportu (np. z crona).
# Skopiuj, ustaw zmienne i dodaj do crontab.

set -e

# === Dostosuj poniższe ===
export MISP_URL="${MISP_URL:-https://misp.example.com}"
export MISP_API_KEY="${MISP_API_KEY:-}"
export MISP_VERIFY_SSL="${MISP_VERIFY_SSL:-true}"
export MISP_TAGS="${MISP_TAGS:-tlp:white,osint}"
export OUTPUT_FORMAT="${OUTPUT_FORMAT:-json}"

DATA_DIR="${DATA_DIR:-$(dirname "$0")/data}"
IMAGE_NAME="${IMAGE_NAME:-misp-ioc-exporter}"
DOCKER="${DOCKER:-docker}"

mkdir -p "$DATA_DIR"

$DOCKER run --rm \
  -e MISP_URL \
  -e MISP_API_KEY \
  -e MISP_VERIFY_SSL \
  -e MISP_TAGS \
  -e OUTPUT_FORMAT \
  -v "${DATA_DIR}:/data" \
  "$IMAGE_NAME"
