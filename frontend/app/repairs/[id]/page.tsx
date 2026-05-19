import { AppShell } from "@/components/AppShell";
import { RepairDetail } from "@/components/RepairDetail";

export default function RepairDetailPage({ params }: { params: { id: string } }) {
  return (
    <AppShell>
      <RepairDetail id={Number(params.id)} />
    </AppShell>
  );
}

