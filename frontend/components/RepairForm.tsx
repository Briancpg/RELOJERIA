"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createRepair, updateRepair } from "@/lib/api";
import type { Repair, RepairPayload, RepairStatus } from "@/types/api";
import { statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function RepairForm({ repair }: { repair?: Repair }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<RepairPayload>({
    repair_date: repair?.repair_date ?? today(),
    brand: repair?.brand ?? "",
    model: repair?.model ?? "",
    description: repair?.description ?? "",
    repair_cost: repair?.repair_cost ?? "",
    watchmaker_percentage: repair?.watchmaker_percentage ?? "50",
    status: repair?.status ?? "pending",
    customer_name: repair?.customer_name ?? "",
    notes: repair?.notes ?? ""
  });

  function setField<K extends keyof RepairPayload>(key: K, value: RepairPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const saved = repair ? await updateRepair(repair.id, form) : await createRepair(form);
      router.replace(`/repairs/${saved.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-lg border border-line bg-white p-4 shadow-sm">
      {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Fecha</span>
          <input
            type="date"
            required
            value={form.repair_date}
            onChange={(event) => setField("repair_date", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Estado</span>
          <select
            value={form.status}
            onChange={(event) => setField("status", event.target.value as RepairStatus)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {statusLabels[status]}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Marca</span>
          <input
            required
            value={form.brand}
            onChange={(event) => setField("brand", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Modelo</span>
          <input
            required
            value={form.model}
            onChange={(event) => setField("model", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
      </div>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">Descripcion de reparacion</span>
        <textarea
          required
          rows={4}
          value={form.description}
          onChange={(event) => setField("description", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Costo</span>
          <input
            type="number"
            min="0"
            step="0.01"
            required
            value={form.repair_cost}
            onChange={(event) => setField("repair_cost", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Porcentaje relojero</span>
          <input
            type="number"
            min="0"
            max="100"
            step="0.01"
            required
            value={form.watchmaker_percentage}
            onChange={(event) => setField("watchmaker_percentage", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
      </div>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">Cliente</span>
        <input
          value={form.customer_name ?? ""}
          onChange={(event) => setField("customer_name", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">Notas</span>
        <textarea
          rows={3}
          value={form.notes ?? ""}
          onChange={(event) => setField("notes", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="focus-ring w-full rounded-md bg-accent px-4 py-3 font-medium text-white sm:w-auto"
      >
        {loading ? "Guardando..." : "Guardar reparacion"}
      </button>
    </form>
  );
}

