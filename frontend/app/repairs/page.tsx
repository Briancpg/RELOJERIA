import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { RepairList } from "@/components/RepairList";

export default function RepairsPage({ searchParams }: { searchParams?: { status?: string; status_group?: string; search?: string } }) {
  return (
    <AppShell
      title="Ordenes de reparacion"
      subtitle="Historial, busqueda y estados"
      actions={
        <Link href="/repairs/new" className="focus-ring rounded-md bg-gold px-4 py-2 font-semibold text-background">
          Nueva orden
        </Link>
      }
    >
      <RepairList
        initialStatus={searchParams?.status ?? ""}
        initialStatusGroup={searchParams?.status_group ?? ""}
        initialSearch={searchParams?.search ?? ""}
      />
    </AppShell>
  );
}
