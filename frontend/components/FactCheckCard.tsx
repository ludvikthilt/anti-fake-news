import type { FactCheckRow } from "@/lib/types";
import { ExternalLink } from "./Icon";
import styles from "./ui.module.css";

export default function FactCheckCard({ items }: { items: FactCheckRow[] }) {
  if (!items.length) {
    return (
      <div className="card card-flat">
        <p style={{ margin: 0, color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
          Aucune vérification de faits publiée n&apos;a été trouvée. Cela ne signifie pas que
          l&apos;information est vraie.
        </p>
      </div>
    );
  }
  return (
    <div>
      {items.map((fc, i) => (
        <article key={i} className={styles.fcCard}>
          <div className="spread" style={{ gap: "var(--s-2)" }}>
            <span className="pill unk">{fc.organization}</span>
            <span className={styles.fcVerdict}>«&nbsp;{fc.verdict}&nbsp;»</span>
          </div>
          {fc.summary && (
            <p style={{ margin: "var(--s-2) 0 0", fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
              {fc.summary}
            </p>
          )}
          <div className={styles.timelineMeta} style={{ marginTop: "var(--s-2)" }}>
            {fc.published_date && (
              <time dateTime={fc.published_date}>
                {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(fc.published_date))}
              </time>
            )}
            {fc.url && (
              <a href={fc.url} target="_blank" rel="noopener noreferrer">
                Lire la vérification <ExternalLink size={13} />
                <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
              </a>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
