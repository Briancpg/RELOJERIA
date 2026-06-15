# Despliegue En VPS Ubuntu

## Requisitos

- Ubuntu actualizado.
- Docker Engine y Docker Compose plugin.
- Dominio apuntando al VPS.
- Variables reales en `.env`.

## Archivos Necesarios

Copiar al VPS:

```text
docker-compose.vps.yml
infra/nginx/relojeria-vps.conf
scripts/backup-postgres.sh
.env
```

Tambien puedes copiar todo el repo, pero en produccion se recomienda usar las imagenes ya publicadas en Docker Hub.

Usa `docker-compose.api.yml` cuando el frontend esta en Cloudflare Pages. Usa `docker-compose.prod.yml` solo si quieres servir frontend, backend, PostgreSQL y Nginx completos desde el VPS.

## Despliegue Recomendado: API En VPS Y Frontend En Pages

`docker-compose.vps.yml` usa:

- `brian2525/relojeria-backend:latest`
- `postgres:16-alpine`
- puerto local configurable con `BACKEND_HOST_PORT`

Nginx corre en el VPS y enruta:

```text
api.tutallerrelojero.com         -> 127.0.0.1:8001
api-staging.tutallerrelojero.com -> 127.0.0.1:8002
```

Luego:

```bash
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml pull
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml up -d
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml ps
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml logs -f backend
```

Tambien puedes hacerlo desde tu maquina local con el script incluido. Crea primero `.env.production` local usando `infra/env.production.example` como base. Ese archivo esta ignorado por Git.

```powershell
.\scripts\deploy-api-vps.ps1 -DeployHost 3.141.226.132 -DeployUser ubuntu -DeployEnv production -EnvFile .env.production
```

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu DEPLOY_ENV=production ENV_FILE=.env.production sh scripts/deploy-api-vps.sh
```

En Cloudflare Pages configura:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.tutallerrelojero.com/api/v1
```

## TLS

Para esta primera version, usar Cloudflare Proxy delante del VPS:

1. Crear registro `A` apuntando al VPS.
2. Activar proxy de Cloudflare.
3. Configurar SSL en modo `Full` o `Full (strict)` si usas certificado origin.
4. Ajustar `CORS_ORIGINS` al dominio final.

## Backup

Crear backup manual:

```bash
sh scripts/backup-postgres.sh
```

Los backups se guardan en `backups/postgres/`, fuera del volumen de PostgreSQL.

Para staging, ejecuta:

```bash
COMPOSE_PROJECT_NAME=relojeria-staging POSTGRES_DB=watch_staging sh scripts/backup-postgres.sh
```

## Checklist

- Cambiar `SECRET_KEY`.
- Cambiar `ADMIN_PASSWORD`.
- Cambiar `POSTGRES_PASSWORD`.
- Configurar `R2_*`.
- Restringir `CORS_ORIGINS` al dominio real.
- Probar login, CRUD, upload, Vision AI y dashboard.
- Crear y probar backup PostgreSQL antes del go-live.
