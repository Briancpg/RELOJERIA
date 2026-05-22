"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { deleteRepair, listRepairs, updateRepair, type RepairFilters } from "@/lib/api";
import type { Repair, RepairStatus } from "@/types/api";
import { StatusBadge, statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];

function profitLabel(status: RepairStatus) {
  if (status === "delivered") return "Ganancia";
  if (status === "cancelled") return "Sin ganancia";
  return "Flotante";
}

export function RepairList({ initialStatus = "" }: { initialStatus?: string }) {
  const [repairs, setRepairs] = useState<Repair[]>([]);
  const [filters, setFilters] = useState<RepairFilters>(
    statuses.includes(initialStatus as RepairStatus) ? { status: initialStatus as RepairStatus } : {}
  );
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingStatusId, setUpdatingStatusId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

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

  async function changeStatus(repair: Repair, status: RepairStatus) {
    if (repair.status === status) return;
    setUpdatingStatusId(repair.id);
    setError("");
    try {
      const updated = await updateRepair(repair.id, { status });
      setRepairs((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cambiar el estado");
    } finally {
      setUpdatingStatusId(null);
    }
  }

  async function removeCancelledRepair(repair: Repair) {
    if (repair.status !== "cancelled") return;
    if (!confirm("Eliminar esta reparacion cancelada del historial?")) return;
    setDeletingId(repair.id);
    setError("");
    try {
      await deleteRepair(repair.id);
      setRepairs((current) => current.filter((item) => item.id !== repair.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo eliminar la reparacion");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-line bg-white p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_260px]">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink">Buscar</span>
            <input
              value={search}
              onChange={(event) => {
                const value = event.target.value;
                setSearch(value);
                setFilters((current) => ({ ...current, search: value.trim() || undefined }));
              }}
              placeholder="Nombre, marca, cedula o factura"
              className="focus-ring w-full rounded-md border border-line px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink">Estado</span>
            <select
              value={filters.status ?? ""}
              onChange={(event) => {
                const status = event.target.value as RepairStatus | "";
                setFilters((current) => ({ ...current, status: status || undefined }));
              }}
              className="focus-ring w-full rounded-md border border-line px-3 py-2"
            >
              <option value="">Todos los estados</option>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {statusLabels[status]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading ? <p className="text-sm text-muted">Cargando reparaciones...</p> : null}
      {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="grid gap-3">
        {!loading && repairs.length === 0 ? (
          <div className="rounded-lg border border-line bg-white p-5 text-sm text-muted">No hay reparaciones.</div>
        ) : null}
        {repairs.map((repair) => (
          <article
            key={repair.id}
            className="rounded-lg border border-line bg-white p-4 shadow-sm transition hover:border-accent"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <Link href={`/repairs/${repair.id}`} className="min-w-0 flex-1">
                <p className="text-sm text-muted">Actual: {repair.repair_date}</p>
                <h2 className="text-lg font-semibold text-ink">
                  {repair.brand} {repair.model}
                </h2>
                <p className="mt-1 line-clamp-2 text-sm text-muted">{repair.description}</p>
              </Link>
              <div className="flex flex-col gap-3 sm:items-end">
                <div className="flex items-center justify-between gap-3 sm:justify-end">
                  <StatusBadge status={repair.status} />
                  <label className="sr-only" htmlFor={`status-${repair.id}`}>
                    Cambiar estado
                  </label>
                  <select
                    id={`status-${repair.id}`}
                    value={repair.status}
                    disabled={updatingStatusId === repair.id}
                    onChange={(event) => changeStatus(repair, event.target.value as RepairStatus)}
                    className="focus-ring rounded-md border border-line bg-white px-3 py-2 text-sm text-ink disabled:opacity-60"
                  >
                    {statuses.map((status) => (
                      <option key={status} value={status}>
                        {statusLabels[status]}
                      </option>
                    ))}
                  </select>
                </div>
                <span className="font-semibold text-ink">
                  {updatingStatusId === repair.id ? "Actualizando..." : `${profitLabel(repair.status)}: DOP ${repair.profit_amount}`}
                </span>
                {repair.status === "cancelled" ? (
                  <button
                    type="button"
                    disabled={deletingId === repair.id}
                    onClick={() => removeCancelledRepair(repair)}
                    className="focus-ring rounded-md border border-red-200 px-3 py-2 text-sm font-medium text-red-700 disabled:opacity-60"
                  >
                    {deletingId === repair.id ? "Eliminando..." : "Eliminar"}
                  </button>
                ) : null}
                {repair.status === "pending" ? (
                  <Link
                    href={`/repairs/${repair.id}/edit`}
                    className="focus-ring rounded-md bg-accent px-3 py-2 text-center text-sm font-medium text-white"
                  >
                    Editar
                  </Link>
                ) : null}
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

