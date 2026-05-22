# Runbook De Produccion

## Orden De Puesta En Marcha

1. Rotar secretos expuestos y generar valores nuevos para produccion.
2. Crear `.env` en el VPS usando `.env.example` como plantilla.
3. Configurar VPS Ubuntu con Docker Engine y Docker Compose plugin.
4. Levantar la app con `docker-compose.prod.yml`.
5. Validar por IP antes de tocar DNS.
6. Configurar dominio en Cloudflare.
7. Validar por dominio con HTTPS.
8. Probar upload real en Cloudflare R2.
9. Probar lectura del sobre con OpenAI Vision.
10. Crear y probar backup PostgreSQL.
11. Hacer go-live.

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
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
```

## Validacion Por IP

```bash
curl http://IP_DEL_VPS/health
```

Luego abrir `http://IP_DEL_VPS`, iniciar sesion con el admin y crear una reparacion manual.

## Validacion Por Dominio

Despues de configurar Cloudflare, actualizar `CORS_ORIGINS` en `.env`:

```env
CORS_ORIGINS=https://tudominio.com
```

Reiniciar backend:

```bash
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
docker compose -f docker-compose.prod.yml restart nginx
```

Validar:

```bash
curl https://tudominio.com/health
```

## Backup PostgreSQL

Crear backup manual:

```bash
sh scripts/backup-postgres.sh
```

Restaurar en un entorno temporal:

```bash
gzip -dc backups/postgres/ARCHIVO.sql.gz | docker compose -f docker-compose.prod.yml exec -T postgres psql -U watch -d watch
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
