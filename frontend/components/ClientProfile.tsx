"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listClients, listRepairs } from "@/lib/api";
import type { ClientSummary, Repair } from "@/types/api";
import { StatusBadge } from "@/components/StatusBadge";

function money(value: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency: "DOP" }).format(Number(value));
}

export function ClientProfile({ clientKey }: { clientKey: string }) {
  const decodedKey = decodeURIComponent(clientKey);
  const [client, setClient] = useState<ClientSummary | null>(null);
  const [repairs, setRepairs] = useState<Repair[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([listClients({ search: decodedKey, page_size: 1 }), listRepairs({ search: decodedKey, page_size: 20 })])
      .then(([clientsData, repairsData]) => {
        setClient(clientsData.items[0] ?? null);
        setRepairs(repairsData.items);
        setError("");
      })
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudo cargar el cliente"))
      .finally(() => setLoading(false));
  }, [decodedKey]);

  if (loading) return <p className="text-sm text-muted">Cargando cliente...</p>;
  if (error) return <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>;
  if (!client) {
    return (
      <div className="rounded-lg border border-border bg-card p-5 text-sm text-muted">
        No se encontro un cliente para esta busqueda.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <section className="rounded-lg border border-border bg-card p-4">
        <h2 className="text-xl font-semibold text-foreground">{client.customer_name}</h2>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
          {client.customer_phone ? <span>{client.customer_phone}</span> : null}
          {client.customer_document_id ? <span>Cedula: {client.customer_document_id}</span> : null}
          {client.last_repair_date ? <span>Ultima visita: {client.last_repair_date}</span> : null}
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-border bg-background/60 p-3">
            <p className="text-2xl font-semibold text-gold">{client.active_repairs}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Ordenes activas</p>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <p className="text-2xl font-semibold text-foreground">{client.total_repairs}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Ordenes totales</p>
          </div>
          <div className="rounded-md border border-border bg-background/60 p-3">
            <p className="text-2xl font-semibold text-gold">{money(client.total_spent)}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Gastado</p>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-3 font-semibold text-foreground">Historial de ordenes</h3>
        <div className="space-y-3">
          {repairs.map((repair) => (
            <Link
              key={repair.id}
              href={`/repairs/${repair.id}`}
              className="focus-ring block rounded-md border border-border bg-background/60 p-3 transition hover:border-gold/40"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm text-muted">{repair.repair_date}</p>
                  <p className="font-semibold text-foreground">
                    {repair.brand} {repair.model}
                  </p>
                  <p className="text-sm text-muted">{repair.description}</p>
                </div>
                <StatusBadge status={repair.status} />
              </div>
            </Link>
          ))}
          {repairs.length === 0 ? <p className="text-sm text-muted">Sin ordenes registradas.</p> : null}
        </div>
      </section>
    </div>
  );
}
