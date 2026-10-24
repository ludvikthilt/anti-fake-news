import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container" style={{ textAlign: "center", paddingTop: "var(--s-12)" }}>
      <h1>Page introuvable</h1>
      <p>Cette page n&apos;existe pas ou a été déplacée.</p>
      <p><Link href="/" className="btn btn-primary">Revenir à l&apos;accueil</Link></p>
    </div>
  );
}
