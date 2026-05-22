import { AppShell } from "@/components/AppShell";
import { RepairDetail } from "@/components/RepairDetail";

export default async function RepairDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <AppShell>
      <RepairDetail id={Number(id)} />
    </AppShell>
  );
}
