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

const scoreLabel = (score: number) =>
  score >= 80 ? "Fiabilité élevée" : score >= 70 ? "Fiabilité moyenne" : "Fiabilité à confirmer";

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
      <div className="card card-flat">
        <p style={{ margin: 0, color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
          Aucune source exploitable n&apos;a été trouvée. L&apos;analyse reste indéterminée :
          cela ne signifie ni « vrai » ni « faux ».
        </p>
      </div>
    );
  }
  return (
    <ol className={styles.timeline}>
      {sources.map((s, i) => {
        const date = formatDate(s.date);
        return (
          <li key={i} className={styles.timelineItem}>
            <div className={styles.timelineDomain}>
              <strong>{s.domain || "domaine inconnu"}</strong>
              <span className="pill">{TYPE_LABELS[s.type] || "Site inconnu"}</span>
              {s.certified && (
                <span className="pill ok" title="Site reconnu par les corroborations du système et plusieurs insiders">
                  Site certifié
                </span>
              )}
              <span className="pill" style={{ marginLeft: "auto" }}>{scoreLabel(s.score)}</span>
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
              {s.url && (
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  Ouvrir la source <ExternalLink size={13} />
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
