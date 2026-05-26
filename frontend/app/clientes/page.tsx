import { AppShell } from "@/components/AppShell";
import { ClientList } from "@/components/ClientList";

export default function ClientsPage() {
  return (
    <AppShell title="Clientes" subtitle="Clientes derivados del historial de ordenes">
      <ClientList />
    </AppShell>
  );
}
