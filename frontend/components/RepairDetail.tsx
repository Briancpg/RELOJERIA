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
      <div className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <h1 className="text-lg font-semibold text-ink">No se pudo cargar la reparacion</h1>
        <p className="mt-2 text-sm text-muted">{error}</p>
        <Link
          href="/repairs"
          className="focus-ring mt-4 inline-flex rounded-md bg-accent px-4 py-2 font-medium text-white"
        >
          Volver a reparaciones
        </Link>
      </div>
    );
  }
  if (!repair) return <p className="text-sm text-muted">Cargando reparacion...</p>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-muted">{repair.repair_date}</p>
            <h1 className="text-2xl font-semibold text-ink">
              {repair.brand} {repair.model}
            </h1>
          </div>
          <StatusBadge status={repair.status} />
        </div>
        <dl className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md bg-surface p-3">
            <dt className="text-sm text-muted">Costo</dt>
            <dd className="font-semibold text-ink">DOP {repair.repair_cost}</dd>
          </div>
          <div className="rounded-md bg-surface p-3">
            <dt className="text-sm text-muted">Porcentaje</dt>
            <dd className="font-semibold text-ink">{repair.watchmaker_percentage}%</dd>
          </div>
          <div className="rounded-md bg-surface p-3">
            <dt className="text-sm text-muted">{profitLabel(repair.status)}</dt>
            <dd className="font-semibold text-ink">DOP {repair.profit_amount}</dd>
          </div>
        </dl>
        <p className="mt-4 whitespace-pre-line text-sm text-ink">{repair.description}</p>
        {repair.notes ? <p className="mt-3 whitespace-pre-line text-sm text-muted">{repair.notes}</p> : null}
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Link href={`/repairs/${repair.id}/edit`} className="focus-ring rounded-md bg-accent px-4 py-2 text-center font-medium text-white">
            Editar
          </Link>
          <button type="button" onClick={remove} className="focus-ring rounded-md border border-line px-4 py-2 text-muted">
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
            className="rounded-lg border border-line bg-white p-3 text-sm text-muted"
          >
            {image.public_url ? (
              <img src={image.public_url} alt={image.file_name} className="mb-2 aspect-video w-full rounded-md object-cover" />
            ) : null}
            {image.file_name}
          </a>
        ))}
      </section>
    </div>
  );
}

