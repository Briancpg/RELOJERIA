#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-}"
DEPLOY_USER="${DEPLOY_USER:-ubuntu}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/relojeria}"
DEPLOY_ENV="${DEPLOY_ENV:-production}"

case "$DEPLOY_ENV" in
  production)
    ENV_FILE="${ENV_FILE:-.env.production}"
    COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-relojeria-prod}"
    VERIFY_URL="https://api.tutallerrelojero.com/health"
    ;;
  staging)
    ENV_FILE="${ENV_FILE:-.env.staging}"
    COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-relojeria-staging}"
    VERIFY_URL="https://api-staging.tutallerrelojero.com/health"
    ;;
  *)
    echo "DEPLOY_ENV must be production or staging." >&2
    exit 1
    ;;
esac

if [ -z "$DEPLOY_HOST" ]; then
  echo "DEPLOY_HOST is required. Example: DEPLOY_HOST=3.141.226.132 $0" >&2
  exit 1
fi

if [[ "$DEPLOY_PATH" == *"'"* ]]; then
  echo "DEPLOY_PATH cannot contain single quotes." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing required file: $ENV_FILE" >&2
  exit 1
fi

BACKEND_HOST_PORT="$(grep -E '^BACKEND_HOST_PORT=' "$ENV_FILE" | head -n 1 | cut -d= -f2- | tr -d '\r' || true)"

if [ -z "$BACKEND_HOST_PORT" ]; then
  echo "BACKEND_HOST_PORT is required in $ENV_FILE." >&2
  exit 1
fi

required_files="
docker-compose.vps.yml
infra/nginx/relojeria-vps.conf
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
scp docker-compose.vps.yml "$target:${DEPLOY_PATH}/docker-compose.vps.yml"
scp infra/nginx/relojeria-vps.conf "$target:${DEPLOY_PATH}/infra/nginx/relojeria-vps.conf"
scp scripts/backup-postgres.sh "$target:${DEPLOY_PATH}/scripts/backup-postgres.sh"
scp "$ENV_FILE" "$target:${DEPLOY_PATH}/.env"

echo "Starting API stack"
ssh "$target" "cd '${DEPLOY_PATH}' && chmod +x scripts/backup-postgres.sh && docker compose --env-file .env -p '${COMPOSE_PROJECT_NAME}' -f docker-compose.vps.yml pull && docker compose --env-file .env -p '${COMPOSE_PROJECT_NAME}' -f docker-compose.vps.yml up -d && docker compose --env-file .env -p '${COMPOSE_PROJECT_NAME}' -f docker-compose.vps.yml ps"

echo "Checking local API health on VPS"
ssh "$target" "curl -fsS http://127.0.0.1:${BACKEND_HOST_PORT}/health"

echo "Deployment finished. Now verify: ${VERIFY_URL}"
echo "If Nginx is not configured yet, install infra/nginx/relojeria-vps.conf on the VPS under /etc/nginx/sites-available/."
