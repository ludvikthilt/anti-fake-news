"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Clock } from "@/components/Icon";
import styles from "@/components/ui.module.css";

interface Row {
  id: string;
  public_id: string;
  input_type: string;
  status: string;
  status_label: string;
  created_at: string;
}

const TYPE_LABELS: Record<string, string> = {
  text: "Texte",
  link: "Lien",
  image: "Image",
};

export default function HistoriquePage() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Row[]>("/analyses/")
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : "Connexion requise."));
  }, []);

  if (error) {
    return (
      <div className="container reading">
        <p className="eyebrow">Votre espace</p>
        <h1>Historique</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>
          <Link href="/compte" className="btn btn-primary">Se connecter</Link>{" "}
          pour retrouver vos analyses.
        </p>
      </div>
    );
  }

  if (!rows) {
    return (
      <div className="container reading">
        <p className="eyebrow">Votre espace</p>
        <h1>Historique</h1>
        <p className="muted">Chargement de vos dossiers…</p>
      </div>
    );
  }

  return (
    <div className="container reading">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Votre espace</p>
          <h1 style={{ margin: 0 }}>Mon historique</h1>
        </div>
        <span className="pill">{rows.length} dossier{rows.length > 1 ? "s" : ""}</span>
      </div>

      {rows.length === 0 ? (
        <div className="card card-flat center" style={{ padding: "var(--s-10) var(--s-4)" }}>
          <Clock size={30} style={{ color: "var(--brand-500)" }} />
          <h2 style={{ fontSize: "var(--fs-lg)", marginTop: "var(--s-3)" }}>Aucune analyse pour le moment</h2>
          <p className="muted" style={{ fontSize: "var(--fs-sm)" }}>
            Vos prochaines vérifications apparaîtront ici, avec leur statut.
          </p>
          <Link href="/" className="btn btn-primary" style={{ marginTop: "var(--s-2)" }}>
            Lancer une analyse
          </Link>
        </div>
      ) : (
        <ul className={`${styles.listReset} stack-sm`}>
          {rows.map((r) => (
            <li key={r.id}>
              <Link href={`/analyses/${r.public_id}`} className={styles.linkCard}>
                <span style={{ minWidth: 0 }}>
                  <span className="mono" style={{ fontSize: "var(--fs-xs)", color: "var(--ink-muted)" }}>
                    #{r.public_id}
                  </span>
                  <span className={styles.linkCardTitle} style={{ display: "block", marginTop: 2 }}>
                    {r.status_label || r.status}
                  </span>
                  <span className="hint" style={{ display: "block", marginTop: 2 }}>
                    {TYPE_LABELS[r.input_type] || r.input_type} ·{" "}
                    {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long", timeStyle: "short" }).format(new Date(r.created_at))}
                  </span>
                </span>
                <span aria-hidden style={{ color: "var(--brand-700)", fontSize: "var(--fs-lg)" }}>→</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
