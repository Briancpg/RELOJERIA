"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDashboardSummary, getProfitByWeek, getRepairsByStatus } from "@/lib/api";
import type { DashboardSummary, StatusCount, WeeklyProfit } from "@/types/api";

function money(value: string, currency: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency }).format(Number(value));
}

export function DashboardStats() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [statuses, setStatuses] = useState<StatusCount[]>([]);
  const [weeks, setWeeks] = useState<WeeklyProfit[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getDashboardSummary(), getRepairsByStatus(), getProfitByWeek()])
      .then(([summaryData, statusData, weekData]) => {
        setSummary(summaryData);
        setStatuses(statusData);
        setWeeks(weekData);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "No se pudo cargar el dashboard");
        if (err instanceof Error && err.message.includes("Authentication")) router.replace("/login");
      });
  }, [router]);

  if (error) return <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>;
  if (!summary) return <p className="text-sm text-muted">Cargando dashboard...</p>;

  const cards = [
    { label: "Ganancia semanal", value: money(summary.total_weekly, summary.currency) },
    { label: "Ganancia mensual", value: money(summary.total_monthly, summary.currency) },
    { label: "Flotante por entregar", value: money(summary.floating_profit, summary.currency) },
    { label: "Pendientes", value: String(summary.pending_repairs) },
    { label: "Entregadas", value: String(summary.delivered_repairs) },
    { label: "Acumulado entregado", value: money(summary.accumulated_profit, summary.currency) }
  ];

  return (
    <div className="space-y-5">
      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.label} className="rounded-lg border border-line bg-white p-4 shadow-sm">
            <p className="text-sm text-muted">{card.label}</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{card.value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-line bg-white p-4">
          <h2 className="mb-3 font-semibold text-ink">Estado de trabajos</h2>
          <div className="space-y-2">
            {statuses.length ? (
              statuses.map((item) => (
                <div key={item.status} className="flex items-center justify-between rounded-md bg-surface px-3 py-2">
                  <span className="text-sm text-muted">{item.status}</span>
                  <span className="font-semibold text-ink">{item.count}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">Sin reparaciones registradas.</p>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-line bg-white p-4">
          <h2 className="mb-3 font-semibold text-ink">Ultimas semanas</h2>
          <div className="space-y-2">
            {weeks.map((week) => (
              <div key={week.week_start} className="flex items-center justify-between rounded-md bg-surface px-3 py-2">
                <span className="text-sm text-muted">
                  {week.week_start} - {week.week_end}
                </span>
                <span className="font-semibold text-ink">{money(week.total_profit, summary.currency)}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
