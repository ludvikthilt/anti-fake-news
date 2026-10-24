import type { SourceRow } from "@/lib/types";
import DateOrigin from "./DateOrigin";
import { ExternalLink } from "./Icon";
import styles from "./ui.module.css";

const TYPE_LABELS: Record<string, string> = {
  agency: "Agence de presse",
  institution: "Institution publique",
  media: "Média reconnu",
  blog: "Blog",
  social: "Réseau social",
  unknown: "Site inconnu",
};

const SCORE_LEVEL = (score: number) =>
  score >= 80 ? "Fiabilité élevée" : score >= 70 ? "Fiabilité moyenne" : "Fiabilité faible";

function formatDate(iso: string | null) {
  if (!iso) return null;
  try {
    return new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export default function SourceTimeline({ sources }: { sources: SourceRow[] }) {
  if (!sources.length) {
    return (
      <p style={{ color: "var(--ink-muted)" }}>
        Aucune source trouvée. L&apos;analyse reste indéterminée, ce qui ne signifie ni « vrai » ni « faux ».
      </p>
    );
  }
  return (
    <ol className={styles.timeline}>
      {sources.map((s, i) => {
        const date = formatDate(s.date);
        return (
          <li key={i} className={styles.timelineItem}>
            <div className={styles.timelineDomain}>
              <span className="mono">{s.domain || "domaine inconnu"}</span>
              <span className="pill">{TYPE_LABELS[s.type] || "Site inconnu"}</span>
            </div>
            {s.title && <p className={styles.timelineTitle}>{s.title}</p>}
            <div className={styles.timelineMeta}>
              {date ? (
                <>
                  <time dateTime={s.date ?? undefined}>{date}</time>
                  <DateOrigin origin={s.date_origin} />
                </>
              ) : (
                <span>Date de première apparition indisponible</span>
              )}
              <span>{SCORE_LEVEL(s.score)}</span>
              {s.url && (
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  Ouvrir la source <ExternalLink size={14} />
                  <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
                </a>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
