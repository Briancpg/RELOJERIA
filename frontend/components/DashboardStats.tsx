"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Banknote, CheckCircle2, Clock3, PackageCheck, TrendingUp, WalletCards } from "lucide-react";
import { getDashboardSummary, getMyDashboardSummary, getProfitByWeek, getRepairsByStatus, listRepairs, me } from "@/lib/api";
import type { DashboardSummary, JewelryDashboardSummary, RepairStatus, StatusCount, UserRole, WeeklyProfit } from "@/types/api";
import { statusLabels } from "@/components/StatusBadge";

function money(value: string, currency: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency }).format(Number(value));
}

export function DashboardStats() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [mySummary, setMySummary] = useState<JewelryDashboardSummary | null>(null);
  const [statuses, setStatuses] = useState<StatusCount[]>([]);
  const [weeks, setWeeks] = useState<WeeklyProfit[]>([]);
  const [error, setError] = useState("");
  const [openingStatus, setOpeningStatus] = useState<string | null>(null);

  useEffect(() => {
    me()
      .then((user) => {
        setRole(user.role);
        if (user.role === "joyeria") {
          return getMyDashboardSummary().then((data) => {
            setMySummary(data);
          });
        }
        return Promise.all([getDashboardSummary(), getRepairsByStatus(), getProfitByWeek()]).then(
          ([summaryData, statusData, weekData]) => {
            setSummary(summaryData);
            setStatuses(statusData);
            setWeeks(weekData);
          }
        );
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "No se pudo cargar el dashboard");
        if (err instanceof Error && err.message.includes("Authentication")) router.replace("/login");
      });
  }, [router]);

  if (error) return <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>;
  if (role === "joyeria") {
    if (!mySummary) return <p className="text-sm text-muted">Cargando dashboard...</p>;
    const jewelryCards = [
      { label: "Mis ordenes", value: String(mySummary.sent_repairs), icon: WalletCards, href: "/repairs" },
      { label: "En proceso", value: String(mySummary.in_process_repairs), icon: Clock3, href: "/repairs?status_group=in_process" },
      { label: "Listas", value: String(mySummary.ready_repairs), icon: PackageCheck, href: "/repairs?status_group=ready" },
      { label: "Entregadas", value: String(mySummary.delivered_repairs), icon: CheckCircle2, href: "/repairs?status_group=delivered" }
    ];
    return (
      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {jewelryCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.label}
              href={card.href}
              className="focus-ring rounded-lg border border-border bg-card p-4 text-left shadow-sm transition hover:border-gold/40 hover:bg-gold/10"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm uppercase tracking-[0.12em] text-muted">{card.label}</p>
                <span className="rounded-md bg-gold/10 p-2 text-gold">
                  <Icon className="h-4 w-4" aria-hidden="true" />
                </span>
              </div>
              <p className="mt-3 text-2xl font-semibold text-foreground">{card.value}</p>
            </Link>
          );
        })}
      </section>
    );
  }
  if (!summary) return <p className="text-sm text-muted">Cargando dashboard...</p>;

  const cards = [
    { label: "Activas", value: String(summary.active_repairs), icon: Clock3, href: "/repairs?status_group=active" },
    { label: "Listas para entregar", value: String(summary.ready_repairs), icon: PackageCheck, href: "/repairs?status_group=ready" },
    { label: "Entregadas esta semana", value: String(summary.delivered_weekly), icon: CheckCircle2, href: "/repairs?status_group=delivered" },
    { label: "Ganancia semanal", value: money(summary.total_weekly, summary.currency), icon: TrendingUp, href: "/repairs?status_group=delivered" },
    { label: "Flotante por entregar", value: money(summary.floating_profit, summary.currency), icon: WalletCards, href: "/repairs?status_group=active" },
    { label: "Ganancia mensual", value: money(summary.total_monthly, summary.currency), icon: Banknote, href: "/repairs?status_group=delivered" }
  ];

  async function openStatus(item: StatusCount) {
    const status = item.status as RepairStatus;
    setOpeningStatus(item.status);
    try {
      if (item.count === 1) {
        const repairs = await listRepairs({ status, page: 1, page_size: 1 });
        const repair = repairs.items[0];
        if (repair) {
          router.push(`/repairs/${repair.id}`);
          return;
        }
      }
      router.push(`/repairs?status=${encodeURIComponent(item.status)}`);
    } catch {
      router.push(`/repairs?status=${encodeURIComponent(item.status)}`);
    } finally {
      setOpeningStatus(null);
    }
  }

  return (
    <div className="space-y-5">
      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
          <Link
            key={card.label}
            href={card.href}
            className="focus-ring rounded-lg border border-border bg-card p-4 text-left shadow-sm transition hover:border-gold/40 hover:bg-gold/10"
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm uppercase tracking-[0.12em] text-muted">{card.label}</p>
              <span className="rounded-md bg-gold/10 p-2 text-gold">
                <Icon className="h-4 w-4" aria-hidden="true" />
              </span>
            </div>
            <p className="mt-3 text-2xl font-semibold text-foreground">{card.value}</p>
          </Link>
          );
        })}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-4">
          <h2 className="mb-3 font-semibold text-foreground">Estado de trabajos</h2>
          <div className="space-y-2">
            {statuses.length ? (
              statuses.map((item) => (
                <button
                  key={item.status}
                  type="button"
                  onClick={() => openStatus(item)}
                  className="focus-ring flex w-full items-center justify-between rounded-md border border-border bg-background/60 px-3 py-2 text-left transition hover:border-gold/40 hover:bg-gold/10"
                >
                  <span className="text-sm text-muted">
                    {statusLabels[item.status as RepairStatus] ?? item.status}
                  </span>
                  <span className="font-semibold text-foreground">{item.count}</span>
                  <span className="sr-only">
                    {openingStatus === item.status ? "Abriendo reparacion" : "Abrir reparaciones de este estado"}
                  </span>
                </button>
              ))
            ) : (
              <p className="text-sm text-muted">Sin reparaciones registradas.</p>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <h2 className="mb-3 font-semibold text-foreground">Ultimas semanas</h2>
          <div className="space-y-2">
            {weeks.map((week) => (
              <div key={week.week_start} className="flex items-center justify-between rounded-md border border-border bg-background/60 px-3 py-2">
                <span className="text-sm text-muted">
                  {week.week_start} - {week.week_end}
                </span>
                <span className="font-semibold text-foreground">{money(week.total_profit, summary.currency)}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
