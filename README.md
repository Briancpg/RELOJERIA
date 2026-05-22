# Relojeria Micro-SaaS

Sistema privado para gestionar reparaciones de relojes, ganancias por porcentaje e imagenes de sobres de reparacion.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT, Pydantic.
- Frontend: Next.js, TypeScript, TailwindCSS.
- Infraestructura: Docker Compose, Nginx, PostgreSQL, Cloudflare R2.

## Desarrollo Local

1. Copia variables:

```bash
cp .env.example .env
```

2. Ajusta credenciales locales en `.env`.

3. Levanta la app:

```bash
docker compose up --build -d
```

4. Abre:

```text
http://localhost
```

5. Verifica salud:

```bash
curl http://localhost/health
```

## Usuario Admin

El backend crea un admin inicial desde:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

En produccion cambia ambos valores antes del primer arranque.

## Imagenes

Las imagenes se guardan en Cloudflare R2. El servidor local no guarda archivos subidos en disco.

## Lectura Del Sobre Con Vision AI

La pantalla de nueva reparacion permite subir la foto del sobre y pedir una lectura automatica. El backend usa OpenAI Responses API con vision y salida JSON estructurada para sugerir campos; el usuario siempre revisa y corrige antes de guardar.

Variables necesarias:

- `OPENAI_API_KEY`
- `OPENAI_VISION_MODEL`, por defecto `gpt-5.4-mini`
- `OPENAI_VISION_TIMEOUT_SECONDS`, por defecto `45`

## Docker Hub

La aplicacion usa dos imagenes propias publicadas:

```text
brian2525/relojeria-backend:latest
brian2525/relojeria-frontend:latest
```

PostgreSQL y Nginx se mantienen como imagenes oficiales.

## Produccion

Para VPS Ubuntu usa el compose de produccion:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

El orden operativo completo esta en `docs/production-runbook.md`.

## Documentacion Operativa

- `docs/cloudflare-r2.md`
- `docs/deployment-vps.md`
- `docs/production-runbook.md`
- `docs/security-review.md`
- `docs/ux-flow.md`
