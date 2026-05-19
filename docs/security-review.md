# Security Review

## Alcance

Revision local del monolito FastAPI/Next.js, Docker Compose, Nginx, autenticacion JWT, upload de imagenes y configuracion.

## Hallazgos Y Acciones

### Resuelto En Baseline

- `.env` esta ignorado por git.
- Se agrego `.env.example` sin secretos reales.
- Los endpoints principales estan protegidos con JWT, excepto login/refresh/health.
- Dinero usa `Decimal` y `NUMERIC`, no `float`.
- Reparaciones e imagenes usan soft delete.
- Upload valida tipo MIME y limite de tamano.
- Upload valida firma basica del contenido para `jpeg`, `png` y `webp`.
- `DATABASE_URL` de Docker Compose apunta a `postgres`, no a `localhost`.
- `bcrypt` se fijo en `4.0.1` para compatibilidad limpia con `passlib`.
- Next.js se actualizo a `16.2.6`.
- `postcss` se fijo en `8.5.10` con override para cerrar el audit de produccion.
- `npm audit --omit=dev` reporta `0 vulnerabilities`.

### Pendiente Antes De Produccion

- Reemplazar `SECRET_KEY`, `ADMIN_PASSWORD` y `POSTGRES_PASSWORD`.
- Configurar `CORS_ORIGINS` solo con el dominio real.
- Usar HTTPS obligatorio en produccion.
- Configurar Cloudflare R2 real.
- Evaluar vulnerabilidades dev-only si se decide mantener toolchain local con ESLint 8.
- Considerar URL firmadas si las imagenes no deben ser publicas.

## Superficies Revisadas

- Autenticacion: JWT HS256, access/refresh tokens.
- Autorizacion: usuario actual requerido en routers protegidos.
- Datos: constraints SQL y soft delete.
- Uploads: R2, MIME allowlist, max size.
- Infra: Compose + Nginx reverse proxy.

## Riesgos Residuales

- El login no tiene rate limiting en v1.
- Los refresh tokens no tienen revocacion en servidor.
- `R2_PUBLIC_BASE_URL` puede exponer imagenes si se usa CDN publico.
- Las dependencias frontend reportan vulnerabilidades npm que requieren analisis separado para evitar upgrades rompientes.
