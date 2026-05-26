import { AppShell } from "@/components/AppShell";
import { InventoryList } from "@/components/InventoryList";

export default function InventoryPage() {
  return (
    <AppShell title="Inventario de piezas" subtitle="Control simple de repuestos y stock">
      <InventoryList />
    </AppShell>
  );
}
