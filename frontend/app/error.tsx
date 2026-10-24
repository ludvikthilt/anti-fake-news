"use client";

import Link from "next/link";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="container reading center" style={{ paddingTop: "var(--s-10)" }}>
      <p className="eyebrow" style={{ justifyContent: "center" }}>Incident</p>
      <h1>Une erreur est survenue</h1>
      <p className="muted">Nous n&apos;avons pas pu afficher cette page. Réessayez dans un instant.</p>
      <div className="cluster" style={{ justifyContent: "center", marginTop: "var(--s-4)" }}>
        <button className="btn btn-primary" onClick={reset}>Réessayer</button>
        <Link href="/" className="btn btn-secondary">Revenir à l&apos;accueil</Link>
      </div>
    </div>
  );
}
