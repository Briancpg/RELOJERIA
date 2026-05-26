"use client";

import { FormEvent, useEffect, useState } from "react";
import { createInventoryItem, deleteInventoryItem, getInventorySummary, listInventory } from "@/lib/api";
import type { InventoryItem, InventoryPayload, InventoryStatus, InventorySummary } from "@/types/api";

const statusLabels: Record<InventoryStatus, string> = {
  available: "Disponible",
  low_stock: "Stock bajo",
  exhausted: "Agotado"
};

const statusStyles: Record<InventoryStatus, string> = {
  available: "border-success/30 bg-success/10 text-success",
  low_stock: "border-warning/30 bg-warning/10 text-warning",
  exhausted: "border-danger/30 bg-danger/10 text-danger"
};

const emptyForm: InventoryPayload = {
  reference: "",
  name: "",
  category: "",
  brand: "",
  description: "",
  stock_quantity: 0,
  minimum_stock: 1,
  unit_price: "0",
  location: ""
};

function money(value: string) {
  return new Intl.NumberFormat("es-DO", { style: "currency", currency: "DOP" }).format(Number(value));
}

export function InventoryList() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [form, setForm] = useState<InventoryPayload>(emptyForm);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<InventoryStatus | "">("");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadInventory() {
    setLoading(true);
    try {
      const [listData, summaryData] = await Promise.all([
        listInventory({ search: search.trim() || undefined, status }),
        getInventorySummary()
      ]);
      setItems(listData.items);
      setSummary(summaryData);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar el inventario");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadInventory();
  }, [search, status]);

  function setField<K extends keyof InventoryPayload>(key: K, value: InventoryPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createInventoryItem({
        ...form,
        brand: form.brand || null,
        description: form.description || null,
        location: form.location || null,
        unit_price: form.unit_price || "0"
      });
      setForm(emptyForm);
      setShowForm(false);
      await loadInventory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar la pieza");
    } finally {
      setSaving(false);
    }
  }

  async function removeItem(item: InventoryItem) {
    if (!confirm(`Eliminar ${item.name} del inventario?`)) return;
    try {
      await deleteInventoryItem(item.id);
      await loadInventory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo eliminar la pieza");
    }
  }

  return (
    <div className="space-y-4">
      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Total piezas", summary?.total_items ?? 0],
          ["Disponibles", summary?.available_items ?? 0],
          ["Stock bajo", summary?.low_stock_items ?? 0],
          ["Agotadas", summary?.exhausted_items ?? 0]
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg border border-border bg-card p-4">
            <p className="text-sm uppercase tracking-[0.12em] text-muted">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-foreground">{value}</p>
          </div>
        ))}
      </section>

      <div className="rounded-lg border border-border bg-card p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_220px_auto]">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nombre, referencia, marca..."
            className="field-control"
          />
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as InventoryStatus | "")}
            className="field-control"
          >
            <option value="">Todos los estados</option>
            <option value="available">Disponible</option>
            <option value="low_stock">Stock bajo</option>
            <option value="exhausted">Agotado</option>
          </select>
          <button
            type="button"
            onClick={() => setShowForm((current) => !current)}
            className="focus-ring rounded-md bg-gold px-4 py-2 font-semibold text-background"
          >
            {showForm ? "Cerrar" : "Nueva pieza"}
          </button>
        </div>

        {showForm ? (
          <form onSubmit={onSubmit} className="mt-4 grid gap-3 border-t border-border pt-4 lg:grid-cols-3">
            <input required value={form.reference} onChange={(event) => setField("reference", event.target.value)} placeholder="Referencia" className="field-control" />
            <input required value={form.name} onChange={(event) => setField("name", event.target.value)} placeholder="Nombre" className="field-control" />
            <input required value={form.category} onChange={(event) => setField("category", event.target.value)} placeholder="Categoria" className="field-control" />
            <input value={form.brand ?? ""} onChange={(event) => setField("brand", event.target.value)} placeholder="Marca" className="field-control" />
            <input value={form.location ?? ""} onChange={(event) => setField("location", event.target.value)} placeholder="Ubicacion" className="field-control" />
            <input type="number" min="0" step="0.01" value={form.unit_price} onChange={(event) => setField("unit_price", event.target.value)} placeholder="Precio unitario" className="field-control" />
            <input type="number" min="0" value={form.stock_quantity} onChange={(event) => setField("stock_quantity", Number(event.target.value))} placeholder="Stock" className="field-control" />
            <input type="number" min="0" value={form.minimum_stock} onChange={(event) => setField("minimum_stock", Number(event.target.value))} placeholder="Minimo" className="field-control" />
            <button disabled={saving} className="focus-ring rounded-md bg-gold px-4 py-2 font-semibold text-background disabled:opacity-60">
              {saving ? "Guardando..." : "Guardar pieza"}
            </button>
          </form>
        ) : null}
      </div>

      {loading ? <p className="text-sm text-muted">Cargando inventario...</p> : null}
      {error ? <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}

      <div className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="hidden grid-cols-[130px_1fr_140px_140px_120px_120px_auto] gap-3 border-b border-border px-4 py-3 text-xs font-semibold uppercase tracking-[0.12em] text-muted lg:grid">
          <span>Referencia</span>
          <span>Nombre</span>
          <span>Categoria</span>
          <span>Marca</span>
          <span>Stock</span>
          <span>Precio</span>
          <span />
        </div>
        {items.length === 0 && !loading ? <p className="p-4 text-sm text-muted">No hay piezas registradas.</p> : null}
        {items.map((item) => (
          <article key={item.id} className="grid gap-3 border-b border-border px-4 py-4 last:border-0 lg:grid-cols-[130px_1fr_140px_140px_120px_120px_auto] lg:items-center">
            <p className="font-mono text-sm text-gold">{item.reference}</p>
            <div>
              <h2 className="font-semibold text-foreground">{item.name}</h2>
              {item.description ? <p className="text-sm text-muted">{item.description}</p> : null}
              {item.location ? <p className="text-xs text-muted">Ubicacion: {item.location}</p> : null}
            </div>
            <p className="text-sm text-muted">{item.category}</p>
            <p className="text-sm text-muted">{item.brand ?? "Generico"}</p>
            <div>
              <p className="font-semibold text-foreground">{item.stock_quantity} pcs</p>
              <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-semibold ${statusStyles[item.status]}`}>
                {statusLabels[item.status]}
              </span>
            </div>
            <p className="font-semibold text-gold">{money(item.unit_price)}</p>
            <button
              type="button"
              onClick={() => removeItem(item)}
              className="focus-ring rounded-md border border-danger/30 px-3 py-2 text-sm font-medium text-danger"
            >
              Eliminar
            </button>
          </article>
        ))}
      </div>
    </div>
  );
}
