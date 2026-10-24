"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Row {
  id: string;
  public_id: string;
  input_type: string;
  status: string;
  status_label: string;
  created_at: string;
}

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
      <div className="container">
        <h1>Historique</h1>
        <p className="error-text" role="alert">{error}</p>
        <p><Link href="/compte">Se connecter</Link> pour consulter l&apos;historique de vos analyses.</p>
      </div>
    );
  }

  if (!rows) {
    return <div className="container"><h1>Historique</h1><p>Chargement…</p></div>;
  }

  return (
    <div className="container">
      <h1>Mon historique</h1>
      {rows.length === 0 ? (
        <p>Aucune analyse pour le moment. <Link href="/">Lancer une analyse.</Link></p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "var(--s-3)" }}>
          {rows.map((r) => (
            <li key={r.id}>
              <Link href={`/analyses/${r.public_id}`} className="card" style={{ display: "flex", justifyContent: "space-between", gap: "var(--s-3)", textDecoration: "none", color: "var(--ink)" }}>
                <span className="mono">#{r.public_id}</span>
                <span>{r.status_label || r.status}</span>
                <span style={{ color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
                  {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short" }).format(new Date(r.created_at))}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
