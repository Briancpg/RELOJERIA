# Estrategia De Entornos

## Entornos

### Development

- Corre en la maquina local.
- Usa `docker-compose.yml`.
- Usa `.env`.
- Puede tener datos falsos y cambios en progreso.

### Staging

- Corre en el VPS como stack separado.
- Frontend: `https://staging.tutallerrelojero.com`.
- API: `https://api-staging.tutallerrelojero.com`.
- Compose project: `relojeria-staging`.
- Backend local del VPS: `127.0.0.1:8002`.
- Env local antes de deploy: `.env.staging`.
- Bucket R2 sugerido: `watch-repair-images-staging`.

### Production

- Corre en el VPS como stack separado.
- Frontend: `https://tutallerrelojero.com`.
- API: `https://api.tutallerrelojero.com`.
- Compose project: `relojeria-prod`.
- Backend local del VPS: `127.0.0.1:8001`.
- Env local antes de deploy: `.env.production`.
- Bucket R2 sugerido: `watch-repair-images`.

## Flujo De Ramas

- `develop`: despliega a staging.
- `main`: despliega a produccion.
- Todo cambio se prueba primero en staging.
- Solo se promueve a `main` cuando staging pasa el checklist.

## Cloudflare Pages

Configurar variables por entorno:

```text
Production:
NEXT_PUBLIC_API_BASE_URL=https://api.tutallerrelojero.com/api/v1

Staging / Preview:
NEXT_PUBLIC_API_BASE_URL=https://api-staging.tutallerrelojero.com/api/v1
```

Configurar dominios:

```text
main    -> tutallerrelojero.com
develop -> staging.tutallerrelojero.com
```

## VPS

Instalar el router Nginx:

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu sh scripts/install-vps-nginx-router.sh
```

Desplegar production:

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu DEPLOY_ENV=production ENV_FILE=.env.production sh scripts/deploy-api-vps.sh
```

Desplegar staging:

```bash
DEPLOY_HOST=3.141.226.132 DEPLOY_USER=ubuntu DEPLOY_ENV=staging ENV_FILE=.env.staging sh scripts/deploy-api-vps.sh
```

## Checklist Antes De Promover A Produccion

- Login funciona.
- Crear reparacion funciona.
- Busqueda funciona.
- Cambio de estado funciona.
- Dashboard financiero calcula correctamente.
- R2 sube fotos en staging.
- Vision AI lee un sobre real en staging.
- No hay errores CORS.
- Backup de staging puede crearse.
