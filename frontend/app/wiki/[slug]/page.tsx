import Link from "next/link";
import { apiBase } from "@/lib/api";
import type { WikiDetail } from "@/lib/types";

export const dynamic = "force-dynamic";

async function getPage(slug: string): Promise<WikiDetail | null> {
  const res = await fetch(`${apiBase()}/wiki/pages/${slug}/`, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

function renderContent(md: string) {
  return md
    .split(/\n\n+/)
    .map((block, i) => {
      if (block.startsWith("## ")) return <h2 key={i} style={{ marginTop: "var(--s-6)" }}>{block.slice(3)}</h2>;
      if (block.startsWith("- ")) {
        const items = block.split("\n").filter((l) => l.startsWith("- "));
        return (
          <ul key={i}>
            {items.map((it, j) => (
              <li key={j} dangerouslySetInnerHTML={{ __html: it.slice(2).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") }} />
            ))}
          </ul>
        );
      }
      return (
        <p key={i} dangerouslySetInnerHTML={{ __html: block.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") }} />
      );
    });
}

export default async function WikiDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const page = await getPage(slug);
  if (!page) {
    return (
      <div className="container">
        <h1>Page introuvable</h1>
        <p>Cette page du wiki n&apos;existe pas ou n&apos;est pas publiée.</p>
        <p><Link href="/wiki">Revenir au wiki</Link></p>
      </div>
    );
  }
  return (
    <div className="container" style={{ maxWidth: "46rem" }}>
      <p><Link href="/wiki">← Wiki</Link></p>
      <h1>{page.title}</h1>
      <p style={{ fontSize: "var(--fs-xs)", color: "var(--ink-muted)" }}>
        Mis à jour le {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(page.updated_at))}
        {page.author_name ? ` · par ${page.author_name}` : ""}
      </p>
      <div style={{ maxWidth: "42rem" }}>{renderContent(page.content)}</div>
    </div>
  );
}
