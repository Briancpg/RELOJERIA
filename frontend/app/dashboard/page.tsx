import { AppShell } from "@/components/AppShell";
import { DashboardStats } from "@/components/DashboardStats";

export default function DashboardPage() {
  return (
    <AppShell>
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
          <p className="text-sm text-muted">Resumen financiero y operativo.</p>
        </div>
      </div>
      <DashboardStats />
    </AppShell>
  );
}

