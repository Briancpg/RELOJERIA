import type { RepairStatus } from "@/types/api";

const labels: Record<RepairStatus, string> = {
  submitted: "Enviado por joyeria",
  pending: "Pendiente",
  in_process: "En proceso",
  ready: "Listo para entregar",
  delivered: "Entregado",
  cancelled: "Cancelado"
};

const styles: Record<RepairStatus, string> = {
  submitted: "bg-purple-500/10 text-purple-300 border-purple-400/30",
  pending: "bg-warning/10 text-warning border-warning/30",
  in_process: "bg-blue-500/10 text-blue-300 border-blue-400/30",
  ready: "bg-emerald-500/10 text-emerald-300 border-emerald-400/30",
  delivered: "bg-success/10 text-success border-success/30",
  cancelled: "bg-danger/10 text-danger border-danger/30"
};

export function StatusBadge({ status }: { status: RepairStatus }) {
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

export { labels as statusLabels };
