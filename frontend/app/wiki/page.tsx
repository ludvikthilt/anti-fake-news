import Link from "next/link";
import { apiBase } from "@/lib/api";
import type { WikiListItem } from "@/lib/types";

export const dynamic = "force-dynamic";

async function getPages(q: string): Promise<WikiListItem[]> {
  const res = await fetch(`${apiBase()}/wiki/pages/?q=${encodeURIComponent(q)}`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function WikiPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q: qParam } = await searchParams;
  const q = qParam || "";
  const pages = await getPages(q);
  return (
    <div className="container">
      <h1>Wiki des insiders</h1>
      <p style={{ color: "var(--ink-muted)" }}>
        Des pages pédagogiques, rédigées et vérifiées par les insiders, avec leurs sources.
      </p>
      <form method="get" action="/wiki" style={{ marginBottom: "var(--s-4)", display: "flex", gap: "var(--s-2)" }}>
        <input type="search" name="q" defaultValue={q} placeholder="Rechercher une page…" aria-label="Rechercher une page" />
        <button className="btn btn-primary" type="submit">Rechercher</button>
      </form>
      {pages.length === 0 ? (
        <p>Aucune page trouvée.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "var(--s-3)" }}>
          {pages.map((p) => (
            <li key={p.slug}>
              <Link href={`/wiki/${p.slug}`} className="card" style={{ display: "block", textDecoration: "none", color: "var(--ink)" }}>
                <strong>{p.title}</strong>
                <div style={{ fontSize: "var(--fs-xs)", color: "var(--ink-muted)", marginTop: "var(--s-1)" }}>
                  Mis à jour le {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(p.updated_at))}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
