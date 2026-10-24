import type { CertificationRow } from "@/lib/types";
import styles from "./ui.module.css";

export default function CertificationPair({ certifications }: { certifications: CertificationRow[] }) {
  if (!certifications.length) {
    return (
      <p style={{ color: "var(--ink-muted)" }}>
        Aucune certification d&apos;insider pour le moment.
      </p>
    );
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-3)" }}>
      {certifications.map((c, i) => (
        <article key={i} className="card">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--s-2)" }}>
            <span className={`pill ${c.verdict === "certify" ? "ok" : "warn"}`} style={{ fontSize: "var(--fs-xs)" }}>
              {c.verdict === "certify" ? "Information certifiée" : "Information contestée"}
            </span>
          </div>
          {c.comment && <p style={{ fontSize: "var(--fs-sm)", marginTop: "var(--s-2)" }}>{c.comment}</p>}
          <div style={{ display: "flex", gap: "var(--s-3)", flexWrap: "wrap", fontSize: "var(--fs-xs)", color: "var(--ink-muted)", marginTop: "var(--s-2)" }}>
            <span>Par {c.insider || "un insider"}</span>
            {c.created_at && (
              <time dateTime={c.created_at}>
                {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(c.created_at))}
              </time>
            )}
            {c.source_url && (
              <a href={c.source_url} target="_blank" rel="noopener noreferrer">
                Source de la certification
                <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
              </a>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
