import type { Metadata } from "next";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import type { WikiListItem } from "@/lib/types";
import { BookOpen, Search } from "@/components/Icon";
import styles from "@/components/ui.module.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Wiki des insiders" };

async function getPages(q: string): Promise<WikiListItem[]> {
  const res = await fetch(`${API_URL}/wiki/pages/?q=${encodeURIComponent(q)}`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function WikiPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q: qParam } = await searchParams;
  const q = qParam || "";
  const pages = await getPages(q);

  return (
    <div className="container">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Références vérifiées</p>
          <h1 style={{ margin: 0 }}>Wiki des insiders</h1>
        </div>
        <span className="pill">{pages.length} page{pages.length > 1 ? "s" : ""}</span>
      </div>

      <p className={styles.heroLead} style={{ maxWidth: "42rem" }}>
        Des pages pédagogiques rédigées et vérifiées par des insiders — enseignants, journalistes
        et spécialistes — avec leurs sources.
      </p>

      <form method="get" action="/wiki" className="card card-flat" style={{ marginBottom: "var(--s-5)" }}>
        <label htmlFor="wiki-q" className="field" style={{ marginBottom: 0 }}>
          <span className="hint">Rechercher une page</span>
          <span className="cluster" style={{ gap: "var(--s-2)", flexWrap: "nowrap" }}>
            <span style={{ position: "relative", flex: 1 }}>
              <Search
                size={16}
                style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--ink-muted)" }}
              />
              <input
                id="wiki-q"
                type="search"
                name="q"
                defaultValue={q}
                placeholder="Désinformation, image recyclée, sources…"
                style={{ paddingLeft: 36 }}
              />
            </span>
            <button className="btn btn-primary" type="submit">Rechercher</button>
          </span>
        </label>
      </form>

      {pages.length === 0 ? (
        <div className="card card-flat center" style={{ padding: "var(--s-10) var(--s-4)" }}>
          <BookOpen size={32} style={{ color: "var(--brand-500)" }} />
          <h2 style={{ fontSize: "var(--fs-lg)", marginTop: "var(--s-3)" }}>Aucune page trouvée</h2>
          <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: 0 }}>
            {q ? "Essayez un autre mot-clé." : "Le wiki s'enrichit progressivement avec les insiders certifiés."}
          </p>
        </div>
      ) : (
        <ul className={`${styles.listReset} stack-sm`}>
          {pages.map((p) => (
            <li key={p.slug}>
              <Link href={`/wiki/${p.slug}`} className={styles.linkCard}>
                <span style={{ minWidth: 0 }}>
                  <span className={styles.linkCardTitle}>{p.title}</span>
                  <span className="hint" style={{ display: "block", marginTop: 4 }}>
                    Mis à jour le{" "}
                    {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(p.updated_at))}
                  </span>
                </span>
                <span aria-hidden style={{ color: "var(--brand-700)" }}>→</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
