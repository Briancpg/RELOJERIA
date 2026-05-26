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
    <div className="rounded-lg border border-border bg-card p-4">
      <label className="mb-3 block">
        <span className="mb-2 block font-medium text-foreground">Tipo de imagen</span>
        <select
          value={imageType}
          onChange={(event) => setImageType(event.target.value as RepairImageType)}
          className="field-control w-full"
        >
          <option value="watch">Foto del reloj</option>
          <option value="envelope">Sobre de reparacion</option>
        </select>
      </label>
      <label className="block">
        <span className="mb-2 block font-medium text-foreground">Imagen</span>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={(event) => upload(event.target.files?.[0])}
          className="file-control"
        />
      </label>
      {loading ? <p className="mt-2 text-sm text-muted">Subiendo...</p> : null}
      {error ? <p className="mt-2 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}
    </div>
  );
}
