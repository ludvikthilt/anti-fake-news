"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ShieldCheck } from "@/components/Icon";
import styles from "@/components/ui.module.css";

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

const STATUS_CLASS: Record<string, string> = {
  pending: "warn",
  accepted: "ok",
  rejected: "bad",
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
      setMessage("Votre demande a bien été envoyée.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Envoi impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container reading">
      <p className="eyebrow">Communauté de vérification</p>
      <h1>Devenir insider</h1>
      <p className={styles.heroLead} style={{ maxWidth: "42rem" }}>
        Les insiders sont des personnes de confiance — enseignants, journalistes, spécialistes —
        qui peuvent certifier ou contester une information, et rédiger le wiki. Une certification
        n&apos;est jamais un verdict : c&apos;est une lecture signée, datée et sourcée.
      </p>

      <div className="banner banner-info" style={{ marginBottom: "var(--s-5)" }}>
        <ShieldCheck size={17} style={{ flex: "none", marginTop: 2 }} />
        <span>
          Les candidatures sont examinées par l&apos;équipe éditoriale. Vous pouvez suivre leur
          état ci-dessous.
        </span>
      </div>

      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <form onSubmit={submit} className="card">
        <div className="field">
          <label htmlFor="motivation">Pourquoi souhaitez-vous devenir insider ?</label>
          <textarea
            id="motivation"
            rows={5}
            required
            value={motivation}
            onChange={(e) => setMotivation(e.target.value)}
            placeholder="Votre parcours, vos domaines de compétence, les sources auxquelles vous avez accès…"
          />
          <span className="hint">Cette motivation est lue par l&apos;équipe, elle n&apos;est pas publiée.</span>
        </div>
        <button className="btn btn-primary" type="submit" disabled={busy}>
          Envoyer ma demande
        </button>
      </form>

      {existing && existing.length > 0 && (
        <section className="section" aria-labelledby="demandes-titre">
          <h2 id="demandes-titre" className="sectionTitle">Mes demandes</h2>
          <div className="stack-sm">
            {existing.map((r) => (
              <article key={r.id} className="card card-flat">
                <div className="spread">
                  <span className={`pill ${STATUS_CLASS[r.status] || ""}`}>
                    {STATUS_LABELS[r.status] || r.status}
                  </span>
                  <span className="hint">
                    {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(r.created_at))}
                  </span>
                </div>
                <p style={{ fontSize: "var(--fs-sm)", margin: "var(--s-3) 0 0" }}>{r.motivation}</p>
                {r.reason && (
                  <p className="hint" style={{ margin: "var(--s-2) 0 0" }}>Motif : {r.reason}</p>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      <p style={{ marginTop: "var(--s-6)" }}>
        <Link href="/compte" className="btn btn-secondary">Retour à mon compte</Link>
      </p>
    </div>
  );
}
