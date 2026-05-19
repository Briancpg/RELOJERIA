import type { RepairStatus } from "@/types/api";

const labels: Record<RepairStatus, string> = {
  pending: "Pendiente",
  in_progress: "En proceso",
  completed: "Completada",
  delivered: "Entregada",
  cancelled: "Cancelada"
};

const styles: Record<RepairStatus, string> = {
  pending: "bg-amber-50 text-amber-800 border-amber-200",
  in_progress: "bg-blue-50 text-blue-800 border-blue-200",
  completed: "bg-teal-50 text-teal-800 border-teal-200",
  delivered: "bg-emerald-50 text-emerald-800 border-emerald-200",
  cancelled: "bg-stone-100 text-stone-700 border-stone-200"
};

export function StatusBadge({ status }: { status: RepairStatus }) {
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

export { labels as statusLabels };

