import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container reading center" style={{ paddingTop: "var(--s-10)" }}>
      <p className="mono" style={{ color: "var(--brand-500)", fontWeight: 600 }}>404</p>
      <h1>Page introuvable</h1>
      <p className="muted">Cette page n&apos;existe pas ou a été déplacée.</p>
      <p style={{ marginTop: "var(--s-4)" }}>
        <Link href="/" className="btn btn-primary">Revenir à l&apos;accueil</Link>
      </p>
    </div>
  );
}
