"use client";

import { FormEvent, useState } from "react";
import { changePassword } from "@/lib/api";

export function AccountPasswordForm() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (newPassword.length < 8) {
      setError("La nueva clave debe tener al menos 8 caracteres.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("La confirmacion no coincide con la nueva clave.");
      return;
    }
    if (currentPassword === newPassword) {
      setError("La nueva clave debe ser diferente a la actual.");
      return;
    }

    setLoading(true);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSuccess("Clave actualizada correctamente.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cambiar la clave.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="max-w-xl space-y-4 rounded-lg border border-border bg-card p-4 sm:p-5">
      <div>
        <h2 className="text-lg font-semibold text-foreground">Cambiar clave</h2>
        <p className="mt-1 text-sm text-muted">Usa una clave privada y diferente a la temporal.</p>
      </div>

      {error ? <p className="rounded-md border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p> : null}
      {success ? (
        <p className="rounded-md border border-success/40 bg-success/10 px-3 py-2 text-sm text-success">{success}</p>
      ) : null}

      <label className="block text-sm font-semibold text-foreground">
        Clave actual
        <input
          type="password"
          autoComplete="current-password"
          value={currentPassword}
          onChange={(event) => setCurrentPassword(event.target.value)}
          required
          className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-foreground outline-none transition focus:border-gold"
        />
      </label>

      <label className="block text-sm font-semibold text-foreground">
        Nueva clave
        <input
          type="password"
          autoComplete="new-password"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          minLength={8}
          required
          className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-foreground outline-none transition focus:border-gold"
        />
      </label>

      <label className="block text-sm font-semibold text-foreground">
        Confirmar nueva clave
        <input
          type="password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          minLength={8}
          required
          className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-foreground outline-none transition focus:border-gold"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="focus-ring inline-flex w-full justify-center rounded-md bg-gold px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-gold/90 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
      >
        {loading ? "Guardando..." : "Actualizar clave"}
      </button>
    </form>
  );
}
