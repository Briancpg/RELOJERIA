import { AppShell } from "@/components/AppShell";
import { ReportsView } from "@/components/ReportsView";

export default function ReportsPage() {
  return (
    <AppShell title="Reportes y estadisticas" subtitle="Resumen general del taller">
      <ReportsView />
    </AppShell>
  );
}
