"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Banknote, CalendarDays, Eye, Pencil, Trash2 } from "lucide-react";
import { deleteRepair, listRepairs, me, updateRepair, type RepairFilters } from "@/lib/api";
import type { Repair, RepairStatus, RepairStatusGroup, UserRole } from "@/types/api";
import { StatusBadge, statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];
const statusGroups: RepairStatusGroup[] = ["active", "in_process", "ready", "delivered", "cancelled"];

function profitLabel(status: RepairStatus) {
  if (status === "delivered") return "Ganancia";
  if (status === "cancelled") return "Sin ganancia";
  return "Flotante";
}

export function RepairList({
  initialStatus = "",
  initialStatusGroup = "",
  initialSearch = ""
}: {
  initialStatus?: string;
  initialStatusGroup?: string;
  initialSearch?: string;
}) {
  const [repairs, setRepairs] = useState<Repair[]>([]);
  const [totalRepairs, setTotalRepairs] = useState(0);
  const [filters, setFilters] = useState<RepairFilters>(
    {
      ...(statuses.includes(initialStatus as RepairStatus) ? { status: initialStatus as RepairStatus } : {}),
      ...(statusGroups.includes(initialStatusGroup as RepairStatusGroup) ? { status_group: initialStatusGroup } : {}),
      ...(initialSearch ? { search: initialSearch } : {})
    }
  );
  const [search, setSearch] = useState(initialSearch);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingStatusId, setUpdatingStatusId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const canManage = role === "admin" || role === "maestro";

  useEffect(() => {
    me()
      .then((user) => setRole(user.role))
      .catch(() => setRole(null));
  }, []);

  useEffect(() => {
    setLoading(true);
    listRepairs(filters)
      .then((data) => {
        setRepairs(data.items);
        setTotalRepairs(data.total);
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

  const visibleDelivered = repairs
    .filter((repair) => repair.status === "delivered")
    .reduce((total, repair) => total + Number(repair.profit_amount ?? 0), 0);
  const visibleSubmitted = repairs.filter((repair) => repair.status === "submitted").length;
  const visiblePending = repairs.filter((repair) => repair.status === "pending").length;
  const visibleInProcess = repairs.filter((repair) => repair.status === "in_process").length;
  const visibleReady = repairs.filter((repair) => repair.status === "ready").length;
  const visibleDeliveredCount = repairs.filter((repair) => repair.status === "delivered").length;

  const summaryCards = canManage
    ? [
        { label: "Nuevas joyerias", value: String(visibleSubmitted), helper: "Enviadas por joyeria" },
        { label: "Pendientes", value: String(visiblePending), helper: "Por recibir o aceptar" },
        { label: "En proceso", value: String(visibleInProcess), helper: "Trabajos activos" },
        { label: "Listas", value: String(visibleReady), helper: "Para entregar" },
        { label: "Entregadas", value: String(visibleDeliveredCount), helper: `DOP ${visibleDelivered.toFixed(2)}` }
      ]
    : [
        { label: "Enviadas", value: String(visibleSubmitted), helper: "Subidas al taller" },
        { label: "En proceso", value: String(visibleInProcess), helper: "Trabajos activos" },
        { label: "Listas", value: String(visibleReady), helper: "Pendientes de entrega" },
        { label: "Entregadas", value: String(visibleDeliveredCount), helper: "Historial propio" }
      ];

  function statusChipClass(status: RepairStatus | "") {
    const active = !filters.status_group && (filters.status ?? "") === status;
    return `focus-ring rounded-full border px-3 py-2 text-sm font-semibold transition ${
      active
        ? "border-gold/40 bg-gold/15 text-gold"
        : "border-border bg-card text-muted hover:border-gold/35 hover:text-foreground"
    }`;
  }

  function setStatusFilter(status: RepairStatus | "") {
    setFilters((current) => ({ ...current, status: status || undefined, status_group: undefined }));
  }

  function statusOptionsForRepair(repair: Repair) {
    return repair.status === "submitted" ? statuses : statuses.filter((status) => status !== "submitted");
  }

  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => (
          <div key={card.label} className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-muted">{card.label}</p>
            <p className="mt-2 text-2xl font-semibold text-foreground">{card.value}</p>
            <p className="mt-1 text-sm text-muted">{card.helper}</p>
          </div>
        ))}
      </section>

      <section className="rounded-lg border border-border bg-card p-4">
        <div className="space-y-3">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-foreground">Buscar orden</span>
            <input
              value={search}
              onChange={(event) => {
                const value = event.target.value;
                setSearch(value);
                setFilters((current) => ({ ...current, search: value.trim() || undefined }));
              }}
              placeholder="Cliente, telefono, marca, modelo, cedula, factura o estado"
              className="field-control h-11 w-full"
            />
          </label>
          <div className="flex flex-wrap gap-2 pt-1">
            <button type="button" onClick={() => setStatusFilter("")} className={statusChipClass("")}>
              Todas
            </button>
            {statuses.map((status) => (
              <button key={status} type="button" onClick={() => setStatusFilter(status)} className={statusChipClass(status)}>
                {statusLabels[status]}
              </button>
            ))}
          </div>
        </div>
      </section>

      {loading ? <p className="text-sm text-muted">Cargando ordenes...</p> : null}
      {error ? <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}

      <section className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="hidden grid-cols-[120px_1.2fr_1.4fr_150px_120px_150px_auto] gap-3 border-b border-border px-4 py-3 text-xs font-semibold uppercase tracking-[0.12em] text-muted lg:grid">
          <span># Orden</span>
          <span>Cliente</span>
          <span>Reloj / trabajo</span>
          <span>Estado</span>
          <span>Entrada</span>
          <span>{canManage ? "Ganancia" : "Salida"}</span>
          <span />
        </div>

        {!loading && repairs.length === 0 ? (
          <div className="p-6 text-sm text-muted">No hay ordenes con esos filtros.</div>
        ) : null}

        {repairs.map((repair) => (
          <article key={repair.id} className="border-b border-border p-4 last:border-0 lg:grid lg:grid-cols-[120px_1.2fr_1.4fr_150px_120px_150px_auto] lg:items-center lg:gap-3">
            <Link href={`/repairs/${repair.id}`} className="mb-3 block font-mono text-sm font-semibold text-gold lg:mb-0">
              ORD-{String(repair.id).padStart(4, "0")}
            </Link>

            <div className="mb-3 min-w-0 lg:mb-0">
              <p className="font-semibold text-foreground">{repair.customer_name || "Cliente sin nombre"}</p>
              <p className="truncate text-sm text-muted">{repair.customer_phone || repair.customer_document_id || "Sin contacto"}</p>
            </div>

            <Link href={`/repairs/${repair.id}`} className="mb-3 block min-w-0 lg:mb-0">
              <p className="font-semibold text-foreground">
                {repair.brand} {repair.model}
              </p>
              <p className="mt-1 line-clamp-2 text-sm text-muted">{repair.description}</p>
            </Link>

            <div className="mb-3 flex items-center gap-2 lg:mb-0 lg:block">
              <StatusBadge status={repair.status} />
              {canManage ? (
                <>
                  <label className="sr-only" htmlFor={`status-${repair.id}`}>
                    Cambiar estado
                  </label>
                  <select
                    id={`status-${repair.id}`}
                    value={repair.status}
                    disabled={updatingStatusId === repair.id}
                    onChange={(event) => changeStatus(repair, event.target.value as RepairStatus)}
                    className="focus-ring mt-0 rounded-md border border-border bg-background px-2 py-1.5 text-xs text-foreground disabled:opacity-60 lg:mt-2 lg:w-full"
                  >
                    {statusOptionsForRepair(repair).map((status) => (
                      <option key={status} value={status}>
                        {statusLabels[status]}
                      </option>
                    ))}
                  </select>
                </>
              ) : null}
            </div>

            <div className="mb-3 flex items-center gap-2 text-sm text-muted lg:mb-0">
              <CalendarDays className="h-4 w-4 text-gold" aria-hidden="true" />
              {repair.repair_date}
            </div>

            <div className="mb-3 flex items-center gap-2 font-semibold text-foreground lg:mb-0">
              {canManage ? (
                <>
                  <Banknote className="h-4 w-4 text-gold" aria-hidden="true" />
                  <span>
                    {updatingStatusId === repair.id
                      ? "Actualizando..."
                      : `${profitLabel(repair.status)}: DOP ${repair.profit_amount ?? "0.00"}`}
                  </span>
                </>
              ) : (
                <span className="text-sm text-muted">{repair.exit_date ?? "Pendiente"}</span>
              )}
            </div>

            <div className="flex flex-wrap gap-2 lg:justify-end">
              <Link
                href={`/repairs/${repair.id}`}
                className="focus-ring inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium text-muted transition hover:border-gold/40 hover:text-gold"
              >
                <Eye className="h-4 w-4" aria-hidden="true" />
                Ver
              </Link>
              {canManage ? (
                <Link
                  href={`/repairs/${repair.id}/edit`}
                  className="focus-ring inline-flex items-center gap-2 rounded-md bg-gold px-3 py-2 text-sm font-semibold text-background"
                >
                  <Pencil className="h-4 w-4" aria-hidden="true" />
                  Editar
                </Link>
              ) : null}
              {canManage && repair.status === "cancelled" ? (
                <button
                  type="button"
                  disabled={deletingId === repair.id}
                  onClick={() => removeCancelledRepair(repair)}
                  className="focus-ring inline-flex items-center gap-2 rounded-md border border-danger/30 px-3 py-2 text-sm font-medium text-danger disabled:opacity-60"
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                  {deletingId === repair.id ? "Eliminando..." : "Eliminar"}
                </button>
              ) : null}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

