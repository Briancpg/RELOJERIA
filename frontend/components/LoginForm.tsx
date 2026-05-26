"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo iniciar sesion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border border-border bg-card p-5 shadow-glow">
      <div className="mb-5">
        <h1 className="text-xl font-semibold text-foreground">Acceso privado</h1>
        <p className="mt-1 text-sm text-muted">Gestion de reparaciones del taller.</p>
      </div>
      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium text-foreground">Email</span>
        <input
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="field-control w-full"
        />
      </label>
      <label className="mb-4 block">
        <span className="mb-1 block text-sm font-medium text-foreground">Password</span>
        <input
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="field-control w-full"
        />
      </label>
      {error ? <p className="mb-3 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="focus-ring w-full rounded-md bg-gold px-4 py-2.5 font-semibold text-background disabled:opacity-60"
      >
        {loading ? "Entrando..." : "Entrar"}
      </button>
    </form>
  );
}
