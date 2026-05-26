import { AppShell } from "@/components/AppShell";
import { RepairEditLoader } from "@/components/RepairEditLoader";

export default async function EditRepairPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <AppShell title="Editar reparacion" subtitle="Solo disponible mientras el trabajo esta en diagnostico">
      <RepairEditLoader id={Number(id)} />
    </AppShell>
  );
}
