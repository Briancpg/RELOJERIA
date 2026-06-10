#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-}"
DEPLOY_USER="${DEPLOY_USER:-ubuntu}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/relojeria}"
ENV_FILE="${ENV_FILE:-.env.production}"

if [ -z "$DEPLOY_HOST" ]; then
  echo "DEPLOY_HOST is required. Example: DEPLOY_HOST=3.141.226.132 $0" >&2
  exit 1
fi

if [[ "$DEPLOY_PATH" == *"'"* ]]; then
  echo "DEPLOY_PATH cannot contain single quotes." >&2
  exit 1
fi

required_files="
docker-compose.api.yml
infra/nginx/api.conf
scripts/backup-postgres.sh
$ENV_FILE
"

for file in $required_files; do
  if [ ! -f "$file" ]; then
    echo "Missing required file: $file" >&2
    exit 1
  fi
done

target="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "Creating remote directories on ${target}:${DEPLOY_PATH}"
ssh "$target" "mkdir -p '${DEPLOY_PATH}/infra/nginx' '${DEPLOY_PATH}/scripts'"

echo "Copying deployment files"
scp docker-compose.api.yml "$target:${DEPLOY_PATH}/docker-compose.api.yml"
scp infra/nginx/api.conf "$target:${DEPLOY_PATH}/infra/nginx/api.conf"
scp scripts/backup-postgres.sh "$target:${DEPLOY_PATH}/scripts/backup-postgres.sh"
scp "$ENV_FILE" "$target:${DEPLOY_PATH}/.env"

echo "Starting API stack"
ssh "$target" "cd '${DEPLOY_PATH}' && chmod +x scripts/backup-postgres.sh && docker compose -f docker-compose.api.yml pull && docker compose -f docker-compose.api.yml up -d && docker compose -f docker-compose.api.yml ps"

echo "Checking local API health on VPS"
ssh "$target" "curl -fsS http://127.0.0.1/health"

echo "Deployment finished. Now verify: https://api.tutallerrelojero.com/health"
