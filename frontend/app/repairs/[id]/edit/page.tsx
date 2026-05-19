import { AppShell } from "@/components/AppShell";
import { RepairEditLoader } from "@/components/RepairEditLoader";

export default function EditRepairPage({ params }: { params: { id: string } }) {
  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold text-ink">Editar reparacion</h1>
      </div>
      <RepairEditLoader id={Number(params.id)} />
    </AppShell>
  );
}

