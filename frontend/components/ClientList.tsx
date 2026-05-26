"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listClients } from "@/lib/api";
import type { ClientSummary } from "@/types/api";

function money(value: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency: "DOP" }).format(Number(value));
}

export function ClientList() {
  const [clients, setClients] = useState<ClientSummary[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    listClients({ search: search.trim() || undefined })
      .then((data) => {
        setClients(data.items);
        setError("");
      })
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudieron cargar los clientes"))
      .finally(() => setLoading(false));
  }, [search]);

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-border bg-card p-4">
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-foreground">Buscar cliente</span>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Nombre, telefono, cedula o factura"
            className="field-control w-full"
          />
        </label>
      </div>

      {loading ? <p className="text-sm text-muted">Cargando clientes...</p> : null}
      {error ? <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}

      <div className="grid gap-3">
        {!loading && clients.length === 0 ? (
          <div className="rounded-lg border border-border bg-card p-5 text-sm text-muted">
            Todavia no hay clientes con reparaciones registradas.
          </div>
        ) : null}
        {clients.map((client) => {
          const repairSearch = client.customer_phone || client.customer_document_id || client.customer_name;
          return (
            <article key={client.client_key} className="rounded-lg border border-border bg-card p-4">
              <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
                <div className="min-w-0">
                  <h2 className="text-lg font-semibold text-foreground">{client.customer_name}</h2>
                  <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
                    {client.customer_phone ? <span>{client.customer_phone}</span> : null}
                    {client.customer_document_id ? <span>Cedula: {client.customer_document_id}</span> : null}
                    {client.last_repair_date ? <span>Ultima visita: {client.last_repair_date}</span> : null}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-sm sm:min-w-[360px]">
                  <div className="rounded-md border border-border bg-background/60 p-2">
                    <p className="font-semibold text-gold">{client.active_repairs}</p>
                    <p className="text-xs uppercase tracking-[0.12em] text-muted">Activas</p>
                  </div>
                  <div className="rounded-md border border-border bg-background/60 p-2">
                    <p className="font-semibold text-foreground">{client.total_repairs}</p>
                    <p className="text-xs uppercase tracking-[0.12em] text-muted">Total</p>
                  </div>
                  <div className="rounded-md border border-border bg-background/60 p-2">
                    <p className="font-semibold text-gold">{money(client.total_spent)}</p>
                    <p className="text-xs uppercase tracking-[0.12em] text-muted">Gastado</p>
                  </div>
                </div>
              </div>
              <Link
                href={`/clientes/${encodeURIComponent(repairSearch)}`}
                className="focus-ring mt-3 inline-flex rounded-md border border-border px-3 py-2 text-sm font-medium text-muted transition hover:border-gold/40 hover:text-gold"
              >
                Ver perfil
              </Link>
            </article>
          );
        })}
      </div>
    </div>
  );
}
