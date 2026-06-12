#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-}"
DEPLOY_USER="${DEPLOY_USER:-ubuntu}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/relojeria}"

if [ -z "$DEPLOY_HOST" ]; then
  echo "DEPLOY_HOST is required. Example: DEPLOY_HOST=3.141.226.132 $0" >&2
  exit 1
fi

if [[ "$DEPLOY_PATH" == *"'"* ]]; then
  echo "DEPLOY_PATH cannot contain single quotes." >&2
  exit 1
fi

if [ ! -f "infra/nginx/relojeria-vps.conf" ]; then
  echo "Missing required file: infra/nginx/relojeria-vps.conf" >&2
  exit 1
fi

target="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "Copying Nginx router config to ${target}:${DEPLOY_PATH}"
ssh "$target" "mkdir -p '${DEPLOY_PATH}/infra/nginx'"
scp infra/nginx/relojeria-vps.conf "$target:${DEPLOY_PATH}/infra/nginx/relojeria-vps.conf"

echo "Installing Nginx router config"
ssh "$target" "sudo cp '${DEPLOY_PATH}/infra/nginx/relojeria-vps.conf' /etc/nginx/sites-available/relojeria-vps.conf && sudo ln -sf /etc/nginx/sites-available/relojeria-vps.conf /etc/nginx/sites-enabled/relojeria-vps.conf && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx"

echo "Nginx router installed. Verify:"
echo "  http://api.tutallerrelojero.com/health"
echo "  http://api-staging.tutallerrelojero.com/health"
