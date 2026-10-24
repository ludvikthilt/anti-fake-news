import type { Metadata } from "next";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import type { WikiDetail } from "@/lib/types";
import Disclaimer from "@/components/Disclaimer";
import styles from "@/components/ui.module.css";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const page = await getPage(slug);
  return { title: page ? page.title : "Page introuvable" };
}

async function getPage(slug: string): Promise<WikiDetail | null> {
  const res = await fetch(`${API_URL}/wiki/pages/${slug}/`, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

function renderContent(md: string) {
  return md.split(/\n\n+/).map((block, i) => {
    if (block.startsWith("## ")) {
      return <h2 key={i} style={{ fontSize: "var(--fs-xl)", marginTop: "var(--s-8)" }}>{block.slice(3)}</h2>;
    }
    if (block.startsWith("### ")) {
      return <h3 key={i} style={{ fontSize: "var(--fs-lg)", marginTop: "var(--s-6)" }}>{block.slice(4)}</h3>;
    }
    if (block.startsWith("- ")) {
      const items = block.split("\n").filter((l) => l.startsWith("- "));
      return (
        <ul key={i} style={{ color: "var(--ink-muted)", paddingLeft: "1.2rem" }}>
          {items.map((it, j) => (
            <li key={j} dangerouslySetInnerHTML={{ __html: it.slice(2).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") }} />
          ))}
        </ul>
      );
    }
    return (
      <p
        key={i}
        style={{ color: "var(--ink-muted)" }}
        dangerouslySetInnerHTML={{ __html: block.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>") }}
      />
    );
  });
}

export default async function WikiDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const page = await getPage(slug);

  if (!page) {
    return (
      <div className="container reading center" style={{ paddingTop: "var(--s-10)" }}>
        <h1>Page introuvable</h1>
        <p className="muted">Cette page n&apos;existe pas ou n&apos;est pas encore publiée.</p>
        <p><Link href="/wiki" className="btn btn-primary">Revenir au wiki</Link></p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="reading" style={{ margin: "0 auto" }}>
        <p className="hint" style={{ marginBottom: "var(--s-3)" }}>
          <Link href="/wiki">← Wiki des insiders</Link>
        </p>
        <p className="eyebrow" style={{ marginBottom: 6 }}>Fiche de référence</p>
        <h1>{page.title}</h1>
        <p className={styles.timelineMeta} style={{ marginBottom: "var(--s-5)" }}>
          <span>
            Mis à jour le{" "}
            {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(page.updated_at))}
          </span>
          {page.author_name && <span>· par {page.author_name}</span>}
        </p>

        <article className="card" style={{ padding: "var(--s-5)" }}>
          <div style={{ fontSize: "var(--fs-md)" }}>{renderContent(page.content)}</div>
        </article>

        <div style={{ marginTop: "var(--s-5)" }}>
          <Disclaimer />
        </div>
      </div>
    </div>
  );
}
