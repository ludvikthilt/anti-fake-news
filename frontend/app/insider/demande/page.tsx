"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Request {
  id: number;
  motivation: string;
  status: string;
  reason: string;
  created_at: string;
}

const STATUS_LABELS: Record<string, string> = {
  pending: "En attente",
  accepted: "Acceptée",
  rejected: "Refusée",
};

export default function InsiderRequestPage() {
  const [motivation, setMotivation] = useState("");
  const [existing, setExisting] = useState<Request[] | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Request[]>("/auth/insider-requests/")
      .then(setExisting)
      .catch((e) => setError(e instanceof Error ? e.message : "Connexion requise."));
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api<Request>("/auth/insider-requests/", { method: "POST", body: { motivation } });
      setExisting((prev) => [...(prev || []), res]);
      setMotivation("");
      setMessage("Votre demande a été envoyée.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Envoi impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: "40rem" }}>
      <h1>Devenir insider</h1>
      <p>
        Les insiders sont des personnes de confiance (enseignants, journalistes, spécialistes) qui peuvent
        certifier ou contester une information, et rédiger le wiki. Aucune certification n&apos;est un verdict :
        c&apos;est une aide signée, datée et sourcée.
      </p>
      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <form onSubmit={submit} className="card">
        <label htmlFor="motivation">Pourquoi souhaitez-vous devenir insider ? (obligatoire)</label>
        <textarea id="motivation" rows={5} required value={motivation} onChange={(e) => setMotivation(e.target.value)} style={{ marginTop: "var(--s-2)" }} />
        <button className="btn btn-primary" type="submit" disabled={busy} style={{ marginTop: "var(--s-3)" }}>
          Envoyer ma demande
        </button>
      </form>

      {existing && existing.length > 0 && (
        <section style={{ marginTop: "var(--s-6)" }}>
          <h2>Mes demandes</h2>
          {existing.map((r) => (
            <div key={r.id} className="card" style={{ marginBottom: "var(--s-3)" }}>
              <strong>{STATUS_LABELS[r.status] || r.status}</strong>
              <p style={{ fontSize: "var(--fs-sm)", marginTop: "var(--s-2)" }}>{r.motivation}</p>
              {r.reason && <p style={{ fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>Motif : {r.reason}</p>}
            </div>
          ))}
        </section>
      )}

      <p style={{ marginTop: "var(--s-4)" }}>
        <Link href="/compte">Retour au compte</Link>
      </p>
    </div>
  );
}
