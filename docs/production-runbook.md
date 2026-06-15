# Runbook De Produccion

## Orden De Puesta En Marcha

1. Rotar secretos expuestos y generar valores nuevos para produccion.
2. Crear `.env` en el VPS usando `infra/env.production.example` como plantilla.
3. Configurar VPS Ubuntu con Docker Engine y Docker Compose plugin.
4. Levantar la API con `docker-compose.api.yml`.
5. Validar por IP antes de tocar DNS.
6. Configurar dominio en Cloudflare.
7. Validar por dominio con HTTPS.
8. Probar upload real en Cloudflare R2.
9. Probar lectura del sobre con OpenAI Vision.
10. Crear y probar backup PostgreSQL.
11. Hacer go-live.

Para trabajar con staging antes de produccion, seguir tambien `docs/environment-strategy.md`.

## Secretos De Produccion

Generar valores fuertes en el VPS:

```bash
openssl rand -hex 48
```

Usar valores distintos para:

- `SECRET_KEY`
- `ADMIN_PASSWORD`
- `POSTGRES_PASSWORD`

Rotar desde sus paneles:

- Cloudflare R2: crear nuevas credenciales `Object Read & Write` para `watch-repair-images`.
- OpenAI: crear o rotar `OPENAI_API_KEY` cuando la cuenta tenga billing/cuota activa.

Guardar estos valores solo en `.env` del VPS. No pegarlos en chat, GitHub ni documentos.

## Comandos Base En VPS

```bash
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml pull
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml up -d
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml ps
docker compose --env-file .env -p relojeria-prod -f docker-compose.vps.yml logs -f backend
```

Desde la maquina local, con acceso SSH al VPS, se puede automatizar la copia y arranque:

```powershell
.\scripts\deploy-api-vps.ps1 -DeployHost 3.141.226.132 -DeployUser ubuntu -DeployEnv production -EnvFile .env.production
```

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu DEPLOY_ENV=production ENV_FILE=.env.production sh scripts/deploy-api-vps.sh
```

## Validacion Por IP

```bash
curl http://IP_DEL_VPS/health
```

Luego abrir `http://IP_DEL_VPS`, iniciar sesion con el admin y crear una reparacion manual.

## Validacion Por Dominio

Despues de configurar Cloudflare, actualizar `CORS_ORIGINS` en `.env`:

```env
CORS_ORIGINS=https://tutallerrelojero.com,https://www.tutallerrelojero.com,https://taller-relojeria.pages.dev
```

Reiniciar backend:

```bash
docker compose -f docker-compose.api.yml up -d --force-recreate backend
docker compose -f docker-compose.api.yml restart nginx
```

Validar:

```bash
curl https://api.tutallerrelojero.com/health
```

En Cloudflare Pages, configurar:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.tutallerrelojero.com/api/v1
```

## Backup PostgreSQL

Crear backup manual:

```bash
sh scripts/backup-postgres.sh
```

Restaurar en un entorno temporal:

```bash
gzip -dc backups/postgres/ARCHIVO.sql.gz | docker compose -p relojeria-prod -f docker-compose.vps.yml exec -T postgres psql -U watch -d watch
```

## Checklist Go-Live

- HTTPS funciona por dominio.
- `.env` existe solo en el VPS y no esta commiteado.
- Secretos rotados.
- Login admin funciona.
- CRUD de reparaciones funciona.
- Cambio de estado funciona.
- R2 sube imagenes correctamente.
- OpenAI Vision devuelve sugerencias o errores controlados.
- Backup PostgreSQL creado y probado.
- Reinicio de contenedores no pierde datos.
