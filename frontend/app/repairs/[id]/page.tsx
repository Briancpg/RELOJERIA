import { AppShell } from "@/components/AppShell";
import { RepairDetail } from "@/components/RepairDetail";

export const runtime = "edge";

export default async function RepairDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <AppShell title="Detalle de reparacion" subtitle="Informacion completa del trabajo">
      <RepairDetail id={Number(id)} />
    </AppShell>
  );
}
