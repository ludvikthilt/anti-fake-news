"use client";

import Link from "next/link";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="container" style={{ textAlign: "center", paddingTop: "var(--s-12)" }}>
      <h1>Une erreur est survenue</h1>
      <p>Nous n&apos;avons pas pu afficher cette page. Vous pouvez réessayer.</p>
      <div style={{ display: "flex", gap: "var(--s-2)", justifyContent: "center" }}>
        <button className="btn btn-primary" onClick={reset}>Réessayer</button>
        <Link href="/" className="btn btn-secondary">Accueil</Link>
      </div>
    </div>
  );
}
