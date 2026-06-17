import { AccountPasswordForm } from "@/components/AccountPasswordForm";
import { AppShell } from "@/components/AppShell";

export default function AccountPage() {
  return (
    <AppShell title="Mi cuenta" subtitle="Gestion de acceso y seguridad">
      <AccountPasswordForm />
    </AppShell>
  );
}
