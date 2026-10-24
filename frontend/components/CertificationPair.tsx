import type { CertificationRow } from "@/lib/types";
import { ShieldCheck } from "./Icon";
import styles from "./ui.module.css";

export default function CertificationPair({ certifications }: { certifications: CertificationRow[] }) {
  if (!certifications.length) {
    return (
      <div className="card card-flat">
        <p style={{ margin: 0, color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
          Aucune certification d&apos;insider pour le moment. Une certification est une lecture
          signée, datée et sourcée — pas un verdict.
        </p>
      </div>
    );
  }
  return (
    <div className="stack-sm">
      {certifications.map((c, i) => (
        <article key={i} className="card card-flat">
          <div className="cluster">
            <span className={`pill ${c.verdict === "certify" ? "ok" : "warn"}`}>
              <ShieldCheck size={13} />
              {c.verdict === "certify" ? "Information certifiée" : "Information contestée"}
            </span>
            <span className="muted" style={{ fontSize: "var(--fs-xs)" }}>
              Par {c.insider || "un insider"}
              {c.created_at
                ? ` · ${new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(c.created_at))}`
                : ""}
            </span>
          </div>
          {c.comment && (
            <p style={{ margin: "var(--s-3) 0 0", fontSize: "var(--fs-sm)" }}>{c.comment}</p>
          )}
          {c.source_url && (
            <p style={{ margin: "var(--s-2) 0 0", fontSize: "var(--fs-xs)" }}>
              <a href={c.source_url} target="_blank" rel="noopener noreferrer">
                Source de la certification
              </a>
            </p>
          )}
        </article>
      ))}
    </div>
  );
}
