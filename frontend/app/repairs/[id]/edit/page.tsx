import { AppShell } from "@/components/AppShell";
import { RepairEditLoader } from "@/components/RepairEditLoader";

export default async function EditRepairPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold text-ink">Editar reparacion</h1>
      </div>
      <RepairEditLoader id={Number(id)} />
    </AppShell>
  );
}
