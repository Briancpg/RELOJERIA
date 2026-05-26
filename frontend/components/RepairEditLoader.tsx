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

  if (error) return <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>;
  if (!repair) return <p className="text-sm text-muted">Cargando reparacion...</p>;
  if (repair.status !== "diagnosis") {
    return (
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-foreground">Edicion no disponible</h2>
        <p className="mt-2 text-sm text-muted">Solo se puede editar una reparacion cuando esta en diagnostico.</p>
        <Link
          href={`/repairs/${repair.id}`}
          className="focus-ring mt-4 inline-flex rounded-md bg-gold px-4 py-2 font-semibold text-background"
        >
          Volver al detalle
        </Link>
      </div>
    );
  }
  return <RepairForm repair={repair} />;
}
