"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { deleteRepair, getRepair, getRepairImageBlob, me } from "@/lib/api";
import type { Repair, RepairImage, UserRole } from "@/types/api";
import { ImageUploader } from "@/components/ImageUploader";
import { StatusBadge } from "@/components/StatusBadge";

function profitLabel(status: Repair["status"]) {
  if (status === "delivered") return "Ganancia";
  if (status === "cancelled") return "Sin ganancia";
  return "Flotante";
}

function imageTypeLabel(image: RepairImage) {
  return image.image_type === "envelope" ? "Sobre de reparacion" : "Foto del reloj";
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function RepairImageCard({ image }: { image: RepairImage }) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(image.public_url);
  const [loadingPreview, setLoadingPreview] = useState(!image.public_url);
  const [previewError, setPreviewError] = useState("");

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;

    if (image.public_url) {
      setPreviewUrl(image.public_url);
      setLoadingPreview(false);
      setPreviewError("");
      return;
    }

    setLoadingPreview(true);
    setPreviewError("");
    getRepairImageBlob(image.repair_id, image.id)
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch((err) => {
        if (cancelled) return;
        setPreviewError(err instanceof Error ? err.message : "No se pudo mostrar la imagen");
      })
      .finally(() => {
        if (!cancelled) setLoadingPreview(false);
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [image.id, image.public_url, image.repair_id]);

  return (
    <article className="overflow-hidden rounded-lg border border-border bg-card text-sm text-muted shadow-sm">
      {previewUrl ? (
        <a href={previewUrl} target="_blank" rel="noreferrer" className="block">
          <img src={previewUrl} alt={image.file_name} className="aspect-video w-full bg-background/60 object-cover" />
        </a>
      ) : (
        <div className="flex aspect-video items-center justify-center bg-background/60 px-4 text-center text-sm text-muted">
          {loadingPreview ? "Cargando imagen..." : previewError || "Imagen no disponible para previsualizar"}
        </div>
      )}
      <div className="space-y-1 p-3">
        <p className="font-semibold text-foreground">{imageTypeLabel(image)}</p>
        <p className="truncate">{image.file_name}</p>
        <p className="text-xs text-muted">
          {image.content_type} · {formatFileSize(image.file_size)}
        </p>
      </div>
    </article>
  );
}

export function RepairDetail({ id }: { id: number }) {
  const router = useRouter();
  const [repair, setRepair] = useState<Repair | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [error, setError] = useState("");
  const canManage = role === "admin" || role === "maestro";

  useEffect(() => {
    me()
      .then((user) => setRole(user.role))
      .catch(() => setRole(null));
    getRepair(id)
      .then(setRepair)
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudo cargar"));
  }, [id]);

  async function remove() {
    if (!confirm("Marcar esta reparacion como eliminada?")) return;
    await deleteRepair(id);
    router.replace("/repairs");
  }

  function addImage(image: RepairImage) {
    setRepair((current) => (current ? { ...current, images: [...current.images, image] } : current));
  }

  if (error) {
    return (
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <h1 className="text-lg font-semibold text-foreground">No se pudo cargar la reparacion</h1>
        <p className="mt-2 text-sm text-muted">{error}</p>
        <Link
          href="/repairs"
          className="focus-ring mt-4 inline-flex rounded-md bg-gold px-4 py-2 font-semibold text-background"
        >
          Volver a reparaciones
        </Link>
      </div>
    );
  }
  if (!repair) return <p className="text-sm text-muted">Cargando reparacion...</p>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-muted">Fecha actual: {repair.repair_date}</p>
            <h1 className="text-2xl font-semibold text-foreground">
              {repair.brand} {repair.model}
            </h1>
          </div>
          <StatusBadge status={repair.status} />
        </div>
        <dl className="mt-4 grid gap-3 sm:grid-cols-3">
          {canManage ? (
            <>
              <div className="rounded-md border border-border bg-background/60 p-3">
                <dt className="text-sm text-muted">Precio cobrado</dt>
                <dd className="font-semibold text-foreground">DOP {repair.repair_cost}</dd>
              </div>
              <div className="rounded-md border border-border bg-background/60 p-3">
                <dt className="text-sm text-muted">Costo interno</dt>
                <dd className="font-semibold text-foreground">DOP {repair.internal_cost ?? "0.00"}</dd>
              </div>
              <div className="rounded-md border border-border bg-background/60 p-3">
                <dt className="text-sm text-muted">Porcentaje</dt>
                <dd className="font-semibold text-foreground">{repair.watchmaker_percentage ?? "0"}%</dd>
              </div>
              <div className="rounded-md border border-border bg-background/60 p-3">
                <dt className="text-sm text-muted">{profitLabel(repair.status)}</dt>
                <dd className="font-semibold text-foreground">DOP {repair.profit_amount ?? "0.00"}</dd>
              </div>
            </>
          ) : null}
          {canManage ? (
            <div className="rounded-md border border-border bg-background/60 p-3">
              <dt className="text-sm text-muted">Abono</dt>
              <dd className="font-semibold text-foreground">DOP {repair.deposit_amount ?? "0.00"}</dd>
            </div>
          ) : null}
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Factura</dt>
            <dd className="font-semibold text-foreground">{repair.invoice_number ?? "Sin factura"}</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Cedula</dt>
            <dd className="font-semibold text-foreground">{repair.customer_document_id ?? "Sin cedula"}</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Telefono</dt>
            <dd className="font-semibold text-foreground">{repair.customer_phone ?? "Sin telefono"}</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Salida</dt>
            <dd className="font-semibold text-foreground">{repair.exit_date ?? "Pendiente"}</dd>
          </div>
        </dl>
        {repair.customer_name ? <p className="mt-4 text-sm text-muted">Cliente: {repair.customer_name}</p> : null}
        {repair.watch_color ? <p className="mt-2 text-sm text-muted">Color del reloj: {repair.watch_color}</p> : null}
        {repair.watch_specifications ? (
          <div className="mt-4 rounded-md border border-border bg-background/60 p-3">
            <p className="text-sm font-medium text-foreground">Especificaciones del reloj</p>
            <p className="mt-2 whitespace-pre-line text-sm text-muted">{repair.watch_specifications}</p>
          </div>
        ) : null}
        <p className="mt-4 whitespace-pre-line text-sm text-foreground">{repair.description}</p>
        {canManage && repair.notes ? <p className="mt-3 whitespace-pre-line text-sm text-muted">{repair.notes}</p> : null}
        {canManage && repair.envelope_raw_transcription ? (
          <details className="mt-4 rounded-md border border-border bg-background/60 p-3 text-sm text-muted">
            <summary className="cursor-pointer font-medium text-foreground">Transcripcion del sobre</summary>
            <p className="mt-2 whitespace-pre-line break-words">{repair.envelope_raw_transcription}</p>
          </details>
        ) : null}
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          {canManage ? (
            <Link
              href={`/repairs/${repair.id}/edit`}
              className="focus-ring rounded-md bg-gold px-4 py-2 text-center font-semibold text-background"
            >
              Editar
            </Link>
          ) : null}
          {canManage ? (
            <button type="button" onClick={remove} className="focus-ring rounded-md border border-border px-4 py-2 text-muted">
              Eliminar
            </button>
          ) : null}
        </div>
      </div>

      <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold text-foreground">Imagenes de la reparacion</h2>
            <p className="text-sm text-muted">Fotos del reloj y sobre guardadas para este trabajo.</p>
          </div>
          <span className="text-sm text-muted">{repair.images.length} imagen(es)</span>
        </div>
        {repair.images.length ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {repair.images.map((image) => (
              <RepairImageCard key={image.id} image={image} />
            ))}
          </div>
        ) : (
          <p className="mt-4 rounded-md border border-border bg-background/60 px-3 py-4 text-sm text-muted">
            Esta reparacion todavia no tiene imagenes guardadas.
          </p>
        )}
      </section>

      <ImageUploader repairId={repair.id} onUploaded={addImage} />
    </div>
  );
}

