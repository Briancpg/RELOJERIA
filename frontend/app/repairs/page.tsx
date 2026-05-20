import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { RepairList } from "@/components/RepairList";

export default function RepairsPage({ searchParams }: { searchParams?: { status?: string } }) {
  return (
    <AppShell>
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Reparaciones</h1>
          <p className="text-sm text-muted">Historial, busqueda y estados.</p>
        </div>
        <Link href="/repairs/new" className="focus-ring rounded-md bg-accent px-4 py-2 font-medium text-white">
          Nueva
        </Link>
      </div>
      <RepairList initialStatus={searchParams?.status ?? ""} />
    </AppShell>
  );
}
