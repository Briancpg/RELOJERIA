"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { deleteRepair, getRepair } from "@/lib/api";
import type { Repair, RepairImage } from "@/types/api";
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

export function RepairDetail({ id }: { id: number }) {
  const router = useRouter();
  const [repair, setRepair] = useState<Repair | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
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
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Costo</dt>
            <dd className="font-semibold text-foreground">DOP {repair.repair_cost}</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Porcentaje</dt>
            <dd className="font-semibold text-foreground">{repair.watchmaker_percentage}%</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">{profitLabel(repair.status)}</dt>
            <dd className="font-semibold text-foreground">DOP {repair.profit_amount}</dd>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <dt className="text-sm text-muted">Abono</dt>
            <dd className="font-semibold text-foreground">DOP {repair.deposit_amount ?? "0.00"}</dd>
          </div>
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
        {repair.notes ? <p className="mt-3 whitespace-pre-line text-sm text-muted">{repair.notes}</p> : null}
        {repair.envelope_raw_transcription ? (
          <details className="mt-4 rounded-md border border-border bg-background/60 p-3 text-sm text-muted">
            <summary className="cursor-pointer font-medium text-foreground">Transcripcion del sobre</summary>
            <p className="mt-2 whitespace-pre-line break-words">{repair.envelope_raw_transcription}</p>
          </details>
        ) : null}
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          {repair.status === "diagnosis" ? (
            <Link
              href={`/repairs/${repair.id}/edit`}
              className="focus-ring rounded-md bg-gold px-4 py-2 text-center font-semibold text-background"
            >
              Editar
            </Link>
          ) : (
            <span className="rounded-md border border-border px-4 py-2 text-center text-sm text-muted">
              Solo se puede editar en diagnostico
            </span>
          )}
          <button type="button" onClick={remove} className="focus-ring rounded-md border border-border px-4 py-2 text-muted">
            Eliminar
          </button>
        </div>
      </div>

      <ImageUploader repairId={repair.id} onUploaded={addImage} />

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {repair.images.map((image) => (
          <a
            key={image.id}
            href={image.public_url ?? "#"}
            target="_blank"
            className="rounded-lg border border-border bg-card p-3 text-sm text-muted"
          >
            {image.public_url ? (
              <img src={image.public_url} alt={image.file_name} className="mb-2 aspect-video w-full rounded-md object-cover" />
            ) : null}
            <span className="block font-medium text-foreground">{imageTypeLabel(image)}</span>
            <span className="block truncate">{image.file_name}</span>
          </a>
        ))}
      </section>
    </div>
  );
}

