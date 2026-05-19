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
    <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border border-line bg-white p-5 shadow-sm">
      <div className="mb-5">
        <h1 className="text-xl font-semibold text-ink">Acceso privado</h1>
        <p className="mt-1 text-sm text-muted">Gestion de reparaciones del taller.</p>
      </div>
      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium text-ink">Email</span>
        <input
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>
      <label className="mb-4 block">
        <span className="mb-1 block text-sm font-medium text-ink">Password</span>
        <input
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="focus-ring w-full rounded-md border border-line px-3 py-2"
        />
      </label>
      {error ? <p className="mb-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="focus-ring w-full rounded-md bg-accent px-4 py-2.5 font-medium text-white disabled:opacity-60"
      >
        {loading ? "Entrando..." : "Entrar"}
      </button>
    </form>
  );
}

