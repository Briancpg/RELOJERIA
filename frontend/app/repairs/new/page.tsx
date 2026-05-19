import { AppShell } from "@/components/AppShell";
import { RepairForm } from "@/components/RepairForm";

export default function NewRepairPage() {
  return (
    <AppShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold text-ink">Nueva reparacion</h1>
        <p className="text-sm text-muted">Registro manual con calculo automatico de ganancia.</p>
      </div>
      <RepairForm />
    </AppShell>
  );
}

