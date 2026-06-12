#!/usr/bin/env sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.vps.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-relojeria-prod}"
BACKUP_DIR="${BACKUP_DIR:-./backups/postgres}"
POSTGRES_DB="${POSTGRES_DB:-watch}"
POSTGRES_USER="${POSTGRES_USER:-watch}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

output_file="$BACKUP_DIR/${POSTGRES_DB}_${timestamp}.sql.gz"

docker compose -p "$COMPOSE_PROJECT_NAME" -f "$COMPOSE_FILE" exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip > "$output_file"

echo "Backup created: $output_file"
