# Checklist De Entrega Al Cliente

## Estado Actual

- Backend FastAPI, PostgreSQL, Alembic, JWT, R2, OpenAI Vision y dashboard financiero implementados.
- Frontend Next.js con panel oscuro, reparaciones, clientes, inventario y reportes implementado.
- Flujo financiero actualizado: solo `Entregado` cuenta como ganancia real; estados activos cuentan como flotante; `Cancelado` no genera ganancia.
- Seguridad base revisada: `.env` ignorado, secretos fuera del repo, uploads validados y `python-multipart` actualizado a `0.0.29`.
- Cloudflare Pages puede hospedar el frontend. La API debe publicarse aparte en VPS o tunnel.

## Entrega Recomendada

- Staging: `https://staging.tutallerrelojero.com` y `https://api-staging.tutallerrelojero.com`.
- Frontend: Cloudflare Pages.
- API: VPS Ubuntu usando `docker-compose.vps.yml`.
- Base de datos: PostgreSQL en volumen Docker persistente.
- Imágenes: Cloudflare R2 privado.
- HTTPS: Cloudflare Proxy delante de `api.tutallerrelojero.com`.

## Variables Que Deben Quedar Reales

- En el VPS, crear `.env` desde `infra/env.production.example`.
- En Cloudflare Pages, configurar:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.tutallerrelojero.com/api/v1
```

- En backend, configurar:

```text
CORS_ORIGINS=https://tutallerrelojero.com,https://www.tutallerrelojero.com,https://taller-relojeria.pages.dev
```

## Pruebas De Aceptacion

Ejecutar primero en staging y repetir un smoke test final en produccion.

- Login con admin de produccion.
- Crear reparacion con cliente y telefono.
- Buscar por cliente, marca, cedula y numero de factura.
- Editar solo reparaciones en diagnostico.
- Cambiar estados desde la lista.
- Confirmar ganancia real solo en entregadas.
- Confirmar flotante en diagnostico, reparacion, espera piezas y listo.
- Subir foto del reloj y foto del sobre a R2.
- Leer 2 o 3 sobres reales con Vision AI.
- Confirmar dashboard, clientes, inventario y reportes.
- Probar celular, tablet y desktop.
- Reiniciar contenedores y confirmar persistencia.
- Crear backup y probar restore en entorno temporal.

## Go-Live

- No entregar hasta que `https://api.tutallerrelojero.com/health` responda OK.
- No entregar hasta que Pages use la URL real del API.
- No entregar hasta que R2 y OpenAI Vision funcionen con credenciales nuevas.
- Entregar al cliente URL, usuario admin, flujo basico de uso y procedimiento de backup.
