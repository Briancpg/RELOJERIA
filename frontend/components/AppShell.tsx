"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, ClipboardList, LayoutDashboard, LogOut, Menu, Package, Plus, Users, Watch, X } from "lucide-react";
import { useState } from "react";
import { clearTokens } from "@/lib/auth";

const links = [
  { href: "/dashboard", label: "Panel", icon: LayoutDashboard },
  { href: "/repairs", label: "Ordenes", icon: ClipboardList },
  { href: "/clientes", label: "Clientes", icon: Users },
  { href: "/inventario", label: "Inventario", icon: Package },
  { href: "/reportes", label: "Reportes", icon: BarChart3 },
  { href: "/repairs/new", label: "Nueva orden", icon: Plus }
];

type AppShellProps = {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  maxWidth?: "lg" | "xl" | "2xl" | "full";
};

const maxWidthClasses: Record<NonNullable<AppShellProps["maxWidth"]>, string> = {
  lg: "max-w-5xl",
  xl: "max-w-6xl",
  "2xl": "max-w-7xl",
  full: "max-w-none"
};

export function AppShell({ children, title, subtitle, actions, maxWidth = "2xl" }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  function logout() {
    clearTokens();
    router.replace("/login");
  }

  const navigation = (
    <nav className="space-y-2">
      {links.map((link) => {
        const active =
          pathname === link.href ||
          (link.href === "/repairs" && pathname.startsWith("/repairs/") && pathname !== "/repairs/new");
        const Icon = link.icon;
        return (
          <Link
            key={link.href}
            href={link.href}
            onClick={() => setMobileOpen(false)}
            className={`flex items-center gap-3 rounded-md border px-3 py-2.5 text-sm font-semibold transition ${
              active
                ? "border-gold/35 bg-gold/15 text-gold"
                : "border-transparent text-muted hover:border-border hover:bg-card hover:text-foreground"
            }`}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {link.label}
          </Link>
        );
      })}
    </nav>
  );

  const sidebar = (
    <aside className="flex h-full flex-col border-r border-border bg-surface/95 px-3 py-5">
      <Link href="/dashboard" className="mb-8 flex items-center gap-3 px-1">
        <span className="grid h-10 w-10 place-items-center rounded-full border border-gold/35 bg-gold/10 text-gold">
          <Watch className="h-5 w-5" aria-hidden="true" />
        </span>
        <span>
          <span className="block font-semibold leading-tight text-foreground">Taller Relojero</span>
          <span className="block text-xs uppercase tracking-[0.2em] text-muted">Panel privado</span>
        </span>
      </Link>
      {navigation}
      <div className="mt-auto rounded-md border border-border bg-card px-3 py-2 text-sm text-muted">
        <span className="mr-2 inline-block h-2 w-2 rounded-full bg-success" />
        Taller abierto
      </div>
    </aside>
  );

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:block lg:w-64">{sidebar}</div>

      {mobileOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Cerrar menu"
            className="absolute inset-0 bg-black/70"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative h-full w-72 max-w-[85vw]">{sidebar}</div>
        </div>
      ) : null}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-border bg-background/92 backdrop-blur">
          <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                onClick={() => setMobileOpen(true)}
                className="focus-ring rounded-md border border-border bg-card p-2 text-muted lg:hidden"
                aria-label="Abrir menu"
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </button>
              <div className="min-w-0">
                {title ? <h1 className="truncate text-xl font-semibold text-foreground sm:text-2xl">{title}</h1> : null}
                {subtitle ? <p className="truncate text-sm text-muted">{subtitle}</p> : null}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {actions}
              <button
                type="button"
                onClick={logout}
                className="focus-ring inline-flex items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm font-medium text-muted transition hover:border-gold/40 hover:text-gold"
              >
                <LogOut className="hidden h-4 w-4 sm:block" aria-hidden="true" />
                Salir
              </button>
            </div>
          </div>
        </header>
        <main className={`mx-auto w-full ${maxWidthClasses[maxWidth]} px-4 py-5 sm:px-6 lg:py-7`}>{children}</main>
      </div>

      {mobileOpen ? (
        <button
          type="button"
          onClick={() => setMobileOpen(false)}
          className="focus-ring fixed right-4 top-4 z-50 rounded-md border border-border bg-card p-2 text-muted lg:hidden"
          aria-label="Cerrar menu"
        >
          <X className="h-5 w-5" aria-hidden="true" />
        </button>
      ) : null}
    </div>
  );
}
