import { AppShell } from "@/components/AppShell";
import { DashboardStats } from "@/components/DashboardStats";

export default function DashboardPage() {
  return (
    <AppShell title="Panel principal" subtitle="Resumen financiero y operativo del taller">
      <DashboardStats />
    </AppShell>
  );
}
