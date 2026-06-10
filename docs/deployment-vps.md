# Despliegue En VPS Ubuntu

## Requisitos

- Ubuntu actualizado.
- Docker Engine y Docker Compose plugin.
- Dominio apuntando al VPS.
- Variables reales en `.env`.

## Archivos Necesarios

Copiar al VPS:

```text
docker-compose.api.yml
infra/nginx/api.conf
scripts/backup-postgres.sh
.env
```

Tambien puedes copiar todo el repo, pero en produccion se recomienda usar las imagenes ya publicadas en Docker Hub.

Usa `docker-compose.api.yml` cuando el frontend esta en Cloudflare Pages. Usa `docker-compose.prod.yml` solo si quieres servir frontend, backend, PostgreSQL y Nginx completos desde el VPS.

## Despliegue Recomendado: API En VPS Y Frontend En Pages

`docker-compose.api.yml` usa:

- `brian2525/relojeria-backend:latest`
- `postgres:16-alpine`
- `nginx:1.27-alpine`

Luego:

```bash
docker compose -f docker-compose.api.yml pull
docker compose -f docker-compose.api.yml up -d
docker compose -f docker-compose.api.yml ps
docker compose -f docker-compose.api.yml logs -f backend
```

Tambien puedes hacerlo desde tu maquina local con el script incluido. Crea primero `.env.production` local usando `infra/env.production.example` como base. Ese archivo esta ignorado por Git.

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu ENV_FILE=.env.production sh scripts/deploy-api-vps.sh
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

Si usas `docker-compose.prod.yml`, ejecuta:

```bash
COMPOSE_FILE=docker-compose.prod.yml sh scripts/backup-postgres.sh
```

## Checklist

- Cambiar `SECRET_KEY`.
- Cambiar `ADMIN_PASSWORD`.
- Cambiar `POSTGRES_PASSWORD`.
- Configurar `R2_*`.
- Restringir `CORS_ORIGINS` al dominio real.
- Probar login, CRUD, upload, Vision AI y dashboard.
- Crear y probar backup PostgreSQL antes del go-live.
