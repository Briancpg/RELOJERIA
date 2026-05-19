"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { listRepairs, type RepairFilters } from "@/lib/api";
import type { Repair, RepairStatus } from "@/types/api";
import { StatusBadge, statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];

export function RepairList() {
  const [repairs, setRepairs] = useState<Repair[]>([]);
  const [filters, setFilters] = useState<RepairFilters>({});
  const [draft, setDraft] = useState<RepairFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    listRepairs(filters)
      .then((data) => {
        setRepairs(data.items);
        setError("");
      })
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudo cargar"))
      .finally(() => setLoading(false));
  }, [filters]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters(draft);
  }

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="grid gap-3 rounded-lg border border-line bg-white p-4 sm:grid-cols-4">
        <input
          placeholder="Buscar marca, modelo o descripcion"
          value={draft.search ?? ""}
          onChange={(event) => setDraft((current) => ({ ...current, search: event.target.value }))}
          className="focus-ring rounded-md border border-line px-3 py-2 sm:col-span-2"
        />
        <select
          value={draft.status ?? ""}
          onChange={(event) => setDraft((current) => ({ ...current, status: event.target.value as RepairStatus | "" }))}
          className="focus-ring rounded-md border border-line px-3 py-2"
        >
          <option value="">Todos los estados</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {statusLabels[status]}
            </option>
          ))}
        </select>
        <button type="submit" className="focus-ring rounded-md bg-accent px-4 py-2 font-medium text-white">
          Filtrar
        </button>
      </form>

      {loading ? <p className="text-sm text-muted">Cargando reparaciones...</p> : null}
      {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="grid gap-3">
        {!loading && repairs.length === 0 ? (
          <div className="rounded-lg border border-line bg-white p-5 text-sm text-muted">No hay reparaciones.</div>
        ) : null}
        {repairs.map((repair) => (
          <Link
            href={`/repairs/${repair.id}`}
            key={repair.id}
            className="rounded-lg border border-line bg-white p-4 shadow-sm transition hover:border-accent"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-muted">{repair.repair_date}</p>
                <h2 className="text-lg font-semibold text-ink">
                  {repair.brand} {repair.model}
                </h2>
                <p className="mt-1 line-clamp-2 text-sm text-muted">{repair.description}</p>
              </div>
              <div className="flex items-center justify-between gap-3 sm:flex-col sm:items-end">
                <StatusBadge status={repair.status} />
                <span className="font-semibold text-ink">DOP {repair.profit_amount}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

