# Despliegue En VPS Ubuntu

## Requisitos

- Ubuntu actualizado.
- Docker Engine y Docker Compose plugin.
- Dominio apuntando al VPS.
- Variables reales en `.env`.

## Archivos Necesarios

Copiar al VPS:

```text
docker-compose.yml
infra/nginx/default.conf
.env
```

Tambien puedes copiar todo el repo si vas a construir en el VPS.

## Despliegue Con Build Local En VPS

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f backend
```

## Despliegue Con Imagenes Publicadas

Si usas Docker Hub, cambia `build:` por `image:` en backend y frontend:

```yaml
backend:
  image: brian2525/relojeria-backend:latest

frontend:
  image: brian2525/relojeria-frontend:latest
```

Luego:

```bash
docker compose pull
docker compose up -d
```

## TLS

Para produccion, colocar TLS delante de Nginx con una de estas opciones:

- Nginx + Certbot en el host.
- Cloudflare proxy con certificado origin.
- Caddy/Traefik como reverse proxy externo.

## Checklist

- Cambiar `SECRET_KEY`.
- Cambiar `ADMIN_PASSWORD`.
- Cambiar `POSTGRES_PASSWORD`.
- Configurar `R2_*`.
- Restringir `CORS_ORIGINS` al dominio real.
- Probar login, CRUD, upload y dashboard.
