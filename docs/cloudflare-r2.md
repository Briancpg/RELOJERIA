# Cloudflare R2

## Objetivo

Configurar almacenamiento externo para imagenes de sobres de reparacion sin guardar archivos en el servidor local.

## Pasos

1. Crear un bucket en Cloudflare R2, por ejemplo `watch-repair-images`.
2. Crear credenciales R2 con permisos de lectura/escritura para ese bucket.
3. Mantener el bucket privado para produccion inicial.
4. Actualizar `.env` en local o VPS:

```env
R2_ENDPOINT_URL=https://account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=watch-repair-images
R2_PUBLIC_BASE_URL=
```

## Validacion

1. Levantar la app con Docker Compose.
2. Crear una reparacion.
3. Abrir el detalle.
4. Subir una imagen `jpeg`, `png` o `webp`.
5. Confirmar que aparece en R2 y en la UI.

## Notas De Seguridad

- No commitear `.env`.
- Rotar keys si se comparten accidentalmente.
- Usar un bucket privado si las imagenes contienen datos sensibles.
- No activar `r2.dev` publico para fotos reales de clientes.
- Mantener `MAX_IMAGE_UPLOAD_MB` bajo, por defecto `10`.
