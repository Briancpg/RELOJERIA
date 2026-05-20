"use client";

import { useState } from "react";
import { uploadRepairImage } from "@/lib/api";
import type { RepairImage, RepairImageType } from "@/types/api";

export function ImageUploader({
  repairId,
  onUploaded
}: {
  repairId: number;
  onUploaded: (image: RepairImage) => void;
}) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageType, setImageType] = useState<RepairImageType>("watch");

  async function upload(file: File | undefined) {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const image = await uploadRepairImage(repairId, file, imageType);
      onUploaded(image);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo subir la imagen");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <label className="mb-3 block">
        <span className="mb-2 block font-medium text-ink">Tipo de imagen</span>
        <select
          value={imageType}
          onChange={(event) => setImageType(event.target.value as RepairImageType)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        >
          <option value="watch">Foto del reloj</option>
          <option value="envelope">Sobre de reparacion</option>
        </select>
      </label>
      <label className="block">
        <span className="mb-2 block font-medium text-ink">Imagen</span>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={(event) => upload(event.target.files?.[0])}
          className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
        />
      </label>
      {loading ? <p className="mt-2 text-sm text-muted">Subiendo...</p> : null}
      {error ? <p className="mt-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}
