import { AppShell } from "@/components/AppShell";
import { ClientProfile } from "@/components/ClientProfile";

export const runtime = "edge";

export default async function ClientProfilePage({ params }: { params: Promise<{ key: string }> }) {
  const { key } = await params;

  return (
    <AppShell title="Perfil de cliente" subtitle="Historial y resumen del cliente">
      <ClientProfile clientKey={key} />
    </AppShell>
  );
}
