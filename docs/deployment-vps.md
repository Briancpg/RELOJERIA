# Despliegue En VPS Ubuntu

## Requisitos

- Ubuntu actualizado.
- Docker Engine y Docker Compose plugin.
- Dominio apuntando al VPS.
- Variables reales en `.env`.

## Archivos Necesarios

Copiar al VPS:

```text
docker-compose.prod.yml
infra/nginx/default.conf
scripts/backup-postgres.sh
.env
```

Tambien puedes copiar todo el repo, pero en produccion se recomienda usar las imagenes ya publicadas en Docker Hub.

## Despliegue Con Imagenes Publicadas

`docker-compose.prod.yml` ya usa:

- `brian2525/relojeria-backend:latest`
- `brian2525/relojeria-frontend:latest`

Luego:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
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

## Checklist

- Cambiar `SECRET_KEY`.
- Cambiar `ADMIN_PASSWORD`.
- Cambiar `POSTGRES_PASSWORD`.
- Configurar `R2_*`.
- Restringir `CORS_ORIGINS` al dominio real.
- Probar login, CRUD, upload, Vision AI y dashboard.
- Crear y probar backup PostgreSQL antes del go-live.
