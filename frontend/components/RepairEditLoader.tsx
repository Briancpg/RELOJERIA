"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getRepair } from "@/lib/api";
import type { Repair } from "@/types/api";
import { RepairForm } from "@/components/RepairForm";

export function RepairEditLoader({ id }: { id: number }) {
  const [repair, setRepair] = useState<Repair | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getRepair(id)
      .then(setRepair)
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudo cargar"));
  }, [id]);

  if (error) return <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>;
  if (!repair) return <p className="text-sm text-muted">Cargando reparacion...</p>;
  if (repair.status !== "pending") {
    return (
      <div className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">Edicion no disponible</h2>
        <p className="mt-2 text-sm text-muted">Solo se puede editar una reparacion cuando esta pendiente.</p>
        <Link
          href={`/repairs/${repair.id}`}
          className="focus-ring mt-4 inline-flex rounded-md bg-accent px-4 py-2 font-medium text-white"
        >
          Volver al detalle
        </Link>
      </div>
    );
  }
  return <RepairForm repair={repair} />;
}
