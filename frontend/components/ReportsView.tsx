"use client";

import { useEffect, useState } from "react";
import { BarChart3, CheckCircle2, Clock3, Users, WalletCards } from "lucide-react";
import { getReportsSummary } from "@/lib/api";
import type { NameCount, ReportsSummary } from "@/types/api";
import { statusLabels } from "@/components/StatusBadge";

function money(value: string, currency: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency }).format(Number(value));
}

function ProgressList({ title, items }: { title: string; items: NameCount[] }) {
  const max = Math.max(...items.map((item) => item.count), 1);
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h2 className="mb-4 font-semibold text-foreground">{title}</h2>
      <div className="space-y-3">
        {items.length === 0 ? <p className="text-sm text-muted">Sin datos suficientes.</p> : null}
        {items.map((item) => (
          <div key={item.name}>
            <div className="mb-1 flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-foreground">
                {statusLabels[item.name as keyof typeof statusLabels] ?? item.name}
              </span>
              <span className="font-semibold text-gold">{item.count}</span>
            </div>
            <div className="h-1.5 rounded-full bg-background">
              <div className="h-1.5 rounded-full bg-gold" style={{ width: `${Math.max((item.count / max) * 100, 8)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ReportsView() {
  const [summary, setSummary] = useState<ReportsSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getReportsSummary()
      .then(setSummary)
      .catch((err) => setError(err instanceof Error ? err.message : "No se pudieron cargar los reportes"));
  }, []);

  if (error) return <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>;
  if (!summary) return <p className="text-sm text-muted">Cargando reportes...</p>;

  const cards = [
    {
      label: "Ingresos totales",
      value: money(summary.total_estimated_revenue, summary.currency),
      helper: "Ordenes con precio asignado",
      icon: WalletCards
    },
    {
      label: "Ingresos cobrados",
      value: money(summary.collected_revenue, summary.currency),
      helper: "Ordenes entregadas",
      icon: CheckCircle2
    },
    {
      label: "Ingresos por entregar",
      value: money(summary.pending_revenue, summary.currency),
      helper: "Ordenes activas sin entregar",
      icon: Clock3
    },
    {
      label: "Clientes registrados",
      value: String(summary.registered_clients),
      helper: `${summary.total_repairs} ordenes en total`,
      icon: Users
    }
  ];

  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="rounded-lg border border-border bg-card p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm uppercase tracking-[0.12em] text-muted">{card.label}</p>
                <span className="rounded-md bg-gold/10 p-2 text-gold">
                  <Icon className="h-4 w-4" aria-hidden="true" />
                </span>
              </div>
              <p className="mt-3 text-2xl font-semibold text-foreground">{card.value}</p>
              <p className="mt-1 text-sm text-muted">{card.helper}</p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <ProgressList title="Ordenes por estado" items={summary.status_counts} />
        <ProgressList title="Ordenes por marca" items={summary.brand_counts} />
      </section>

      <section className="rounded-lg border border-border bg-card p-4">
        <div className="mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-gold" aria-hidden="true" />
          <h2 className="font-semibold text-foreground">Estado del inventario</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-border bg-background/60 p-4 text-center">
            <p className="text-2xl font-semibold text-foreground">{summary.inventory.total_items}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Total piezas</p>
          </div>
          <div className="rounded-md border border-warning/30 bg-warning/10 p-4 text-center">
            <p className="text-2xl font-semibold text-warning">{summary.inventory.low_stock_items}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Stock bajo</p>
          </div>
          <div className="rounded-md border border-danger/30 bg-danger/10 p-4 text-center">
            <p className="text-2xl font-semibold text-danger">{summary.inventory.exhausted_items}</p>
            <p className="text-xs uppercase tracking-[0.12em] text-muted">Agotadas</p>
          </div>
        </div>
      </section>
    </div>
  );
}
