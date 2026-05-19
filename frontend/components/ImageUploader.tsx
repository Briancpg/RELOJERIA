"use client";

import { useState } from "react";
import { uploadRepairImage } from "@/lib/api";
import type { RepairImage } from "@/types/api";

export function ImageUploader({
  repairId,
  onUploaded
}: {
  repairId: number;
  onUploaded: (image: RepairImage) => void;
}) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function upload(file: File | undefined) {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const image = await uploadRepairImage(repairId, file);
      onUploaded(image);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo subir la imagen");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <label className="block">
        <span className="mb-2 block font-medium text-ink">Imagen del sobre</span>
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

