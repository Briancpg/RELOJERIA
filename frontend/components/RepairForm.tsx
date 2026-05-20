"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createRepair, extractEnvelope, updateRepair, uploadRepairImage } from "@/lib/api";
import type { ExtractedRepairFields, Repair, RepairPayload, RepairStatus } from "@/types/api";
import { statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function RepairForm({ repair }: { repair?: Repair }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [createdRepairId, setCreatedRepairId] = useState<number | null>(null);
  const [watchPhotos, setWatchPhotos] = useState<File[]>([]);
  const [envelopePhoto, setEnvelopePhoto] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [extractionMessage, setExtractionMessage] = useState("");
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

  function applyExtractedFields(fields: ExtractedRepairFields) {
    setForm((current) => {
      const nextValue = (value: string | undefined, fallback: string | null | undefined) =>
        value !== undefined && value !== null && value !== "" ? value : fallback;

      return {
        ...current,
        repair_date: nextValue(fields.repair_date, current.repair_date) ?? current.repair_date,
        brand: nextValue(fields.brand, current.brand) ?? current.brand,
        model: nextValue(fields.model, current.model) ?? current.model,
        description: nextValue(fields.description, current.description) ?? current.description,
        repair_cost: nextValue(fields.repair_cost, current.repair_cost) ?? current.repair_cost,
        watchmaker_percentage:
          nextValue(fields.watchmaker_percentage, current.watchmaker_percentage) ?? current.watchmaker_percentage,
        customer_name: nextValue(fields.customer_name, current.customer_name),
        notes: nextValue(fields.notes, current.notes)
      };
    });
  }

  async function readEnvelope() {
    if (!envelopePhoto) {
      setExtractionMessage("Selecciona una foto del sobre primero.");
      return;
    }
    setExtracting(true);
    setExtractionMessage("");
    try {
      const result = await extractEnvelope(envelopePhoto);
      applyExtractedFields(result.fields);
      const confidence = result.confidence !== null ? ` Confianza: ${Math.round(result.confidence * 100)}%.` : "";
      const rawText = result.raw_text ? ` Texto leido: ${result.raw_text}` : "";
      setExtractionMessage(`${result.message}${confidence}${rawText}`);
    } catch (err) {
      setExtractionMessage(err instanceof Error ? err.message : "No se pudo leer el sobre");
    } finally {
      setExtracting(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setCreatedRepairId(null);
    try {
      const saved = repair ? await updateRepair(repair.id, form) : await createRepair(form);
      if (!repair) {
        const uploads = [
          ...watchPhotos.map((file) => uploadRepairImage(saved.id, file, "watch")),
          ...(envelopePhoto ? [uploadRepairImage(saved.id, envelopePhoto, "envelope")] : [])
        ];
        const results = await Promise.allSettled(uploads);
        const failedUploads = results.filter((result) => result.status === "rejected").length;
        if (failedUploads) {
          setCreatedRepairId(saved.id);
          setError(
            `La reparacion fue creada, pero ${failedUploads} imagen(es) no se pudieron subir. Revisa R2 e intentalo desde el detalle.`
          );
          return;
        }
      }
      router.replace(`/repairs/${saved.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-lg border border-line bg-white p-4 shadow-sm">
      {error ? (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          <p>{error}</p>
          {createdRepairId ? (
            <Link href={`/repairs/${createdRepairId}`} className="mt-2 inline-flex font-medium underline">
              Ver reparacion creada
            </Link>
          ) : null}
        </div>
      ) : null}

      {!repair ? (
        <section className="grid gap-3 lg:grid-cols-2">
          <div className="rounded-md border border-line bg-surface p-3">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-ink">Fotos del reloj</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                multiple
                onChange={(event) => setWatchPhotos(Array.from(event.target.files ?? []))}
                className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
              />
            </label>
            {watchPhotos.length ? (
              <p className="mt-2 text-sm text-muted">{watchPhotos.length} foto(s) seleccionada(s)</p>
            ) : null}
          </div>

          <div className="rounded-md border border-line bg-surface p-3">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-ink">Sobre de reparacion</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                onChange={(event) => setEnvelopePhoto(event.target.files?.[0] ?? null)}
                className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
              />
            </label>
            <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
              <button
                type="button"
                disabled={!envelopePhoto || extracting}
                onClick={readEnvelope}
                className="focus-ring rounded-md bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {extracting ? "Leyendo..." : "Leer sobre"}
              </button>
              {envelopePhoto ? <span className="text-sm text-muted">{envelopePhoto.name}</span> : null}
            </div>
            {extractionMessage ? <p className="mt-2 text-sm text-muted">{extractionMessage}</p> : null}
          </div>
        </section>
      ) : null}

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
