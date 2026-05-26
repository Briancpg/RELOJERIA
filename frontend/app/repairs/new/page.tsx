import { AppShell } from "@/components/AppShell";
import { RepairForm } from "@/components/RepairForm";

export default function NewRepairPage() {
  return (
    <AppShell title="Nueva orden" subtitle="Registro manual con calculo automatico de ganancia">
      <RepairForm />
    </AppShell>
  );
}
