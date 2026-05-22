"use client";

import { FormEvent, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createRepair, extractEnvelope, updateRepair, uploadRepairImage } from "@/lib/api";
import type { ExtractedRepairFields, Repair, RepairPayload, RepairStatus } from "@/types/api";
import { statusLabels } from "@/components/StatusBadge";

const statuses = Object.keys(statusLabels) as RepairStatus[];
const MAX_WATCH_PHOTOS = 3;
const AUTO_FILL_CONFIDENCE = 0.8;
const SUGGESTION_CONFIDENCE = 0.5;

type ExtractionSuggestion = {
  key: keyof RepairPayload;
  label: string;
  value: string;
  confidence: number;
};

type ExtractionApplySummary = {
  autoFilled: number;
  suggestions: number;
  lowConfidence: number;
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

function RequiredMark() {
  return <span className="text-red-700">*</span>;
}

export function RepairForm({ repair }: { repair?: Repair }) {
  const router = useRouter();
  const watchInputRef = useRef<HTMLInputElement | null>(null);
  const envelopeInputRef = useRef<HTMLInputElement | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [createdRepairId, setCreatedRepairId] = useState<number | null>(null);
  const [watchPhotos, setWatchPhotos] = useState<File[]>([]);
  const [watchPhotosMessage, setWatchPhotosMessage] = useState("");
  const [showEnvelopeOption, setShowEnvelopeOption] = useState(false);
  const [envelopePhoto, setEnvelopePhoto] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [extractionMessage, setExtractionMessage] = useState("");
  const [extractionSuggestions, setExtractionSuggestions] = useState<ExtractionSuggestion[]>([]);
  const [form, setForm] = useState<RepairPayload>({
    repair_date: repair?.repair_date ?? today(),
    envelope_date: repair?.envelope_date ?? "",
    envelope_raw_transcription: repair?.envelope_raw_transcription ?? "",
    brand: repair?.brand ?? "",
    model: repair?.model ?? "",
    watch_color: repair?.watch_color ?? "",
    watch_specifications: repair?.watch_specifications ?? "",
    description: repair?.description ?? "",
    repair_cost: repair?.repair_cost ?? "",
    deposit_amount: repair?.deposit_amount ?? "",
    watchmaker_percentage: repair?.watchmaker_percentage ?? "50",
    status: repair?.status ?? "pending",
    customer_name: repair?.customer_name ?? "",
    customer_phone: repair?.customer_phone ?? "",
    customer_document_id: repair?.customer_document_id ?? "",
    invoice_number: repair?.invoice_number ?? "",
    notes: repair?.notes ?? ""
  });

  function resetNewRepairForm() {
    setForm({
      repair_date: today(),
      envelope_date: null,
      envelope_raw_transcription: "",
      brand: "",
      model: "",
      watch_color: "",
      watch_specifications: "",
      description: "",
      repair_cost: "",
      deposit_amount: "",
      watchmaker_percentage: "50",
      status: "pending",
      customer_name: "",
      customer_phone: "",
      customer_document_id: "",
      invoice_number: "",
      notes: ""
    });
    setCreatedRepairId(null);
    setWatchPhotos([]);
    setWatchPhotosMessage("");
    setShowEnvelopeOption(false);
    setEnvelopePhoto(null);
    setExtracting(false);
    setExtractionMessage("");
    setExtractionSuggestions([]);
    if (watchInputRef.current) watchInputRef.current.value = "";
    if (envelopeInputRef.current) envelopeInputRef.current.value = "";
  }

  function setField<K extends keyof RepairPayload>(key: K, value: RepairPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function removeWatchPhoto(index: number) {
    setWatchPhotos((current) => {
      const nextPhotos = current.filter((_, itemIndex) => itemIndex !== index);
      if (nextPhotos.length === 0 && watchInputRef.current) {
        watchInputRef.current.value = "";
      }
      return nextPhotos;
    });
    setWatchPhotosMessage("");
  }

  function addWatchPhotos(files: FileList | null) {
    const selectedFiles = Array.from(files ?? []);
    if (!selectedFiles.length) return;
    setWatchPhotos((current) => {
      const availableSlots = MAX_WATCH_PHOTOS - current.length;
      const acceptedFiles = selectedFiles.slice(0, Math.max(availableSlots, 0));
      const nextPhotos = [...current, ...acceptedFiles];
      setWatchPhotosMessage(
        selectedFiles.length > acceptedFiles.length
          ? `Solo puedes cargar maximo ${MAX_WATCH_PHOTOS} fotos del reloj.`
          : ""
      );
      return nextPhotos;
    });
    if (watchInputRef.current) {
      watchInputRef.current.value = "";
    }
  }

  function removeEnvelopePhoto() {
    setEnvelopePhoto(null);
    setExtractionMessage("");
    setExtractionSuggestions([]);
    if (envelopeInputRef.current) {
      envelopeInputRef.current.value = "";
    }
  }

  function toggleEnvelopeOption(enabled: boolean) {
    setShowEnvelopeOption(enabled);
    if (!enabled) {
      removeEnvelopePhoto();
      setField("envelope_raw_transcription", "");
    }
  }

  function applyExtractedFields(
    fields: ExtractedRepairFields,
    confidences: Record<string, number>,
    rawTranscription: string | null
  ): ExtractionApplySummary {
    const mappings: Array<{
      key: keyof RepairPayload;
      label: string;
      value: string | undefined;
      confidenceKey: string;
    }> = [
      { key: "brand", label: "Marca", value: fields.brand, confidenceKey: "watch_brand" },
      { key: "model", label: "Modelo", value: fields.model, confidenceKey: "watch_model" },
      { key: "watch_color", label: "Color del reloj", value: fields.watch_color, confidenceKey: "watch_color" },
      {
        key: "watch_specifications",
        label: "Especificaciones del reloj",
        value: fields.watch_specifications,
        confidenceKey: "watch_specifications"
      },
      {
        key: "description",
        label: "Descripcion de reparacion",
        value: fields.description,
        confidenceKey: "repair_description"
      },
      { key: "repair_cost", label: "Costo", value: fields.repair_cost, confidenceKey: "repair_cost" },
      { key: "deposit_amount", label: "Abono", value: fields.deposit_amount, confidenceKey: "deposit_amount" },
      { key: "customer_name", label: "Cliente", value: fields.customer_name, confidenceKey: "customer_name" },
      { key: "customer_phone", label: "Telefono", value: fields.customer_phone, confidenceKey: "customer_phone" },
      {
        key: "customer_document_id",
        label: "Cedula",
        value: fields.customer_document_id,
        confidenceKey: "customer_document_id"
      },
      {
        key: "invoice_number",
        label: "Numero de factura",
        value: fields.invoice_number,
        confidenceKey: "invoice_number"
      },
      { key: "notes", label: "Notas", value: fields.notes, confidenceKey: "notes" }
    ];

    const autoFill = mappings.filter(
      (item) => item.value && (confidences[item.confidenceKey] ?? 0) >= AUTO_FILL_CONFIDENCE
    );
    const suggestions = mappings
      .map((item) => ({
        key: item.key,
        label: item.label,
        value: item.value ?? "",
        confidence: confidences[item.confidenceKey] ?? 0
      }))
      .filter((item) => item.value && item.confidence >= SUGGESTION_CONFIDENCE && item.confidence < AUTO_FILL_CONFIDENCE);
    const lowConfidence = mappings.filter(
      (item) => item.value && (confidences[item.confidenceKey] ?? 0) < SUGGESTION_CONFIDENCE
    );

    setForm((current) => {
      const autoValues = Object.fromEntries(autoFill.map((item) => [item.key, item.value]));
      return {
        ...current,
        ...autoValues,
        envelope_raw_transcription: rawTranscription ?? current.envelope_raw_transcription
      };
    });
    setExtractionSuggestions(suggestions);
    return {
      autoFilled: autoFill.length,
      suggestions: suggestions.length,
      lowConfidence: lowConfidence.length
    };
  }

  function applySuggestion(suggestion: ExtractionSuggestion) {
    setField(suggestion.key, suggestion.value as never);
    setExtractionSuggestions((current) => current.filter((item) => item.key !== suggestion.key));
  }

  function dismissSuggestion(suggestion: ExtractionSuggestion) {
    setExtractionSuggestions((current) => current.filter((item) => item.key !== suggestion.key));
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
      const rawText = result.raw_transcription || result.raw_text;
      if (!result.extracted && !rawText && result.confidence === null && !result.raw_text_candidates.length) {
        setExtractionSuggestions([]);
        setExtractionMessage(result.message);
        return;
      }
      const applySummary = applyExtractedFields(result.fields, result.field_confidences, rawText);
      const confidence = result.confidence !== null ? ` Confianza: ${Math.round(result.confidence * 100)}%.` : "";
      const applied =
        ` Autollenados: ${applySummary.autoFilled}.` +
        ` Sugerencias: ${applySummary.suggestions}.` +
        ` Baja confianza: ${applySummary.lowConfidence}.`;
      const envelopeNumber = result.envelope_number ? ` Sobre: ${result.envelope_number}.` : "";
      const phones = result.phone_numbers.length ? ` Telefonos: ${result.phone_numbers.join(", ")}.` : "";
      const warnings = result.warnings.length ? ` Advertencias: ${result.warnings.join(" ")}` : "";
      const candidates = result.raw_text_candidates.length
        ? ` Posibles lecturas: ${result.raw_text_candidates.join(" | ")}.`
        : "";
      const transcription = rawText ? ` Transcripcion: ${rawText}` : "";
      setExtractionMessage(
        `${result.message} Solo se autollenan campos con confianza de 80% o mas.${applied}${confidence}${envelopeNumber}${phones}${warnings}${candidates}${transcription}`
      );
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
    setSuccess("");
    setCreatedRepairId(null);
    const payload: RepairPayload = {
      ...form,
      envelope_date: form.envelope_date || null,
      watch_color: form.watch_color || null,
      watch_specifications: form.watch_specifications || null,
      repair_cost: form.repair_cost || "0",
      deposit_amount: form.deposit_amount || null,
      customer_name: form.customer_name || "",
      customer_phone: form.customer_phone || "",
      customer_document_id: form.customer_document_id || null,
      invoice_number: form.invoice_number || null,
      notes: form.notes || null,
      envelope_raw_transcription: form.envelope_raw_transcription || null
    };
    try {
      const saved = repair ? await updateRepair(repair.id, payload) : await createRepair(payload);
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
        resetNewRepairForm();
        setSuccess("Reparacion guardada. El formulario quedo listo para registrar otra.");
        return;
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

      {success ? <div className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-800">{success}</div> : null}

      <p className="text-sm text-muted">
        <RequiredMark /> Campos requeridos para guardar: fecha actual, marca, modelo, descripcion, porcentaje, cliente y telefono.
      </p>

      {!repair ? (
        <section className="grid gap-3 lg:grid-cols-2">
          <div className="rounded-md border border-line bg-surface p-3">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-ink">Fotos del reloj</span>
              <input
                ref={watchInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                multiple
                disabled={watchPhotos.length >= MAX_WATCH_PHOTOS}
                onChange={(event) => addWatchPhotos(event.target.files)}
                className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-2 file:text-sm file:font-medium file:text-white disabled:opacity-60"
              />
            </label>
            <p className="mt-2 text-sm text-muted">
              {watchPhotos.length}/{MAX_WATCH_PHOTOS} foto(s) seleccionada(s)
            </p>
            {watchPhotosMessage ? <p className="mt-1 text-sm text-red-700">{watchPhotosMessage}</p> : null}
            {watchPhotos.length ? (
              <div className="mt-3 space-y-2">
                {watchPhotos.map((file, index) => (
                  <div
                    key={`${file.name}-${file.lastModified}-${index}`}
                    className="flex items-center justify-between gap-3 rounded-md bg-white px-3 py-2 text-sm"
                  >
                    <span className="min-w-0 truncate text-muted">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeWatchPhoto(index)}
                      className="focus-ring rounded-md border border-red-200 px-3 py-1 font-medium text-red-700"
                    >
                      Quitar
                    </button>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <div className="rounded-md border border-line bg-surface p-3">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-medium text-ink">Sobre de reparacion</p>
                <p className="mt-1 text-sm text-muted">
                  {showEnvelopeOption ? "Lectura con Vision AI activa" : "Lectura con Vision AI desactivada"}
                </p>
              </div>
              <button
                type="button"
                onClick={() => toggleEnvelopeOption(!showEnvelopeOption)}
                className={`focus-ring rounded-md px-4 py-2 text-sm font-medium ${
                  showEnvelopeOption ? "border border-line bg-white text-muted" : "bg-accent text-white"
                }`}
              >
                {showEnvelopeOption ? "Desactivar" : "Leer con IA"}
              </button>
            </div>

            {showEnvelopeOption ? (
              <div className="mt-4 space-y-3 border-t border-line pt-3">
                <div className="rounded-md border border-line bg-white p-3">
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-ink">Foto del sobre</span>
                    <input
                      ref={envelopeInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      capture="environment"
                      onChange={(event) => setEnvelopePhoto(event.target.files?.[0] ?? null)}
                      className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
                    />
                  </label>
                  {envelopePhoto ? (
                    <div className="mt-3 rounded-md bg-surface px-3 py-2">
                      <p className="truncate text-sm text-muted">{envelopePhoto.name}</p>
                    </div>
                  ) : null}
                </div>

                <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
                  <button
                    type="button"
                    disabled={!envelopePhoto || extracting}
                    onClick={readEnvelope}
                    className="focus-ring rounded-md bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {extracting ? "Leyendo..." : "Leer sobre"}
                  </button>
                  {envelopePhoto ? (
                    <button
                      type="button"
                      onClick={removeEnvelopePhoto}
                      className="focus-ring rounded-md border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-700"
                    >
                      Quitar imagen
                    </button>
                  ) : null}
                </div>

                {extractionMessage ? (
                  <div className="max-h-40 overflow-y-auto rounded-md border border-line bg-white p-3">
                    <p className="mb-1 text-sm font-medium text-ink">Resultado de Vision AI</p>
                    <p className="break-words text-sm leading-6 text-muted">{extractionMessage}</p>
                  </div>
                ) : null}

                {extractionSuggestions.length ? (
                  <div className="space-y-2 rounded-md border border-amber-200 bg-amber-50 p-3">
                    <p className="text-sm font-medium text-ink">Sugerencias para confirmar</p>
                    {extractionSuggestions.map((suggestion) => (
                      <div key={suggestion.key} className="grid gap-2 rounded-md bg-white p-2 text-sm sm:grid-cols-[1fr_auto]">
                        <div className="min-w-0">
                          <p className="font-medium text-ink">
                            {suggestion.label} ({Math.round(suggestion.confidence * 100)}%)
                          </p>
                          <p className="break-words text-muted">{suggestion.value}</p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => applySuggestion(suggestion)}
                            className="focus-ring rounded-md bg-accent px-3 py-2 font-medium text-white"
                          >
                            Usar
                          </button>
                          <button
                            type="button"
                            onClick={() => dismissSuggestion(suggestion)}
                            className="focus-ring rounded-md border border-line px-3 py-2 text-muted"
                          >
                            Ignorar
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">
            Fecha actual <RequiredMark />
          </span>
          <input
            type="date"
            required
            value={form.repair_date}
            onChange={(event) => setField("repair_date", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
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
        <div className="hidden sm:block" aria-hidden="true" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">
            Marca <RequiredMark />
          </span>
          <input
            required
            value={form.brand}
            onChange={(event) => setField("brand", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">
            Modelo <RequiredMark />
          </span>
          <input
            required
            value={form.model}
            onChange={(event) => setField("model", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
      </div>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">Color del reloj</span>
        <input
          value={form.watch_color ?? ""}
          onChange={(event) => setField("watch_color", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">Especificaciones del reloj</span>
        <textarea
          rows={3}
          value={form.watch_specifications ?? ""}
          onChange={(event) => setField("watch_specifications", event.target.value)}
          placeholder="Color, tamano, tipo de correa, cristal, movimiento u otros detalles visibles"
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink">
          Descripcion de reparacion <RequiredMark />
        </span>
        <textarea
          required
          rows={4}
          value={form.description}
          onChange={(event) => setField("description", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-3">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Costo</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.repair_cost}
            onChange={(event) => setField("repair_cost", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Abono</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.deposit_amount ?? ""}
            onChange={(event) => setField("deposit_amount", event.target.value || null)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">
            Porcentaje relojero <RequiredMark />
          </span>
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
        <span className="mb-1 block text-sm font-medium text-ink">
          Cliente <RequiredMark />
        </span>
        <input
          required
          value={form.customer_name ?? ""}
          onChange={(event) => setField("customer_name", event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-3">
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">
            Telefono <RequiredMark />
          </span>
          <input
            type="tel"
            inputMode="tel"
            required
            value={form.customer_phone ?? ""}
            onChange={(event) => setField("customer_phone", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Cedula</span>
          <input
            value={form.customer_document_id ?? ""}
            onChange={(event) => setField("customer_document_id", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-sm font-medium text-ink">Numero de factura</span>
          <input
            value={form.invoice_number ?? ""}
            onChange={(event) => setField("invoice_number", event.target.value)}
            className="focus-ring w-full rounded-md border border-line px-3 py-2"
          />
        </label>
      </div>

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
