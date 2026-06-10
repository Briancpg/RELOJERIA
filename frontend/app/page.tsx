"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function HomePage() {
  useEffect(() => {
    window.location.replace("/dashboard");
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 text-foreground">
      <section className="w-full max-w-sm rounded-lg border border-border bg-card p-6 text-center shadow-sm">
        <p className="text-sm text-muted">Abriendo el panel del taller...</p>
        <Link
          href="/dashboard"
          className="mt-4 inline-flex rounded-md bg-accent px-4 py-2 text-sm font-semibold text-black"
        >
          Ir al panel
        </Link>
      </section>
    </main>
  );
}
