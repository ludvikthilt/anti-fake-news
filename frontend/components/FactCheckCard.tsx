import type { FactCheckRow } from "@/lib/types";
import { ExternalLink } from "./Icon";
import styles from "./ui.module.css";

export default function FactCheckCard({ items }: { items: FactCheckRow[] }) {
  if (!items.length) {
    return (
      <p style={{ color: "var(--ink-muted)" }}>
        Aucune vérification de faits publiée trouvée. Cela ne signifie pas que l&apos;information est vraie.
      </p>
    );
  }
  return (
    <div>
      {items.map((fc, i) => (
        <article key={i} className={styles.fcCard}>
          <div className={styles.fcVerdict}>
            {fc.organization} : «&nbsp;{fc.verdict}&nbsp;»
          </div>
          {fc.summary && <p style={{ marginTop: "var(--s-2)", fontSize: "var(--fs-sm)" }}>{fc.summary}</p>}
          <div style={{ display: "flex", gap: "var(--s-3)", flexWrap: "wrap", marginTop: "var(--s-2)", fontSize: "var(--fs-xs)", color: "var(--ink-muted)" }}>
            {fc.published_date && (
              <time dateTime={fc.published_date}>
                {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(fc.published_date))}
              </time>
            )}
            {fc.url && (
              <a href={fc.url} target="_blank" rel="noopener noreferrer">
                Lien vers la vérification <ExternalLink size={14} />
                <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
              </a>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
