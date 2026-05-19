"use client";

import { useEffect, useState } from "react";
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
  return <RepairForm repair={repair} />;
}

