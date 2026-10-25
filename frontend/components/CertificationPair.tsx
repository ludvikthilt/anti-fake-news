import type { CertificationRow, StatusKey } from "@/lib/types";
import { ShieldCheck, Trash2 } from "./Icon";

const PROPOSED_LABELS: Record<StatusKey, string> = {
  corroboree: "Corroborée",
  non_corroboree: "Non corroborée",
  contredite: "Contredite",
  indeterminee: "Indéterminée",
};

const PROPOSED_CLASS: Record<StatusKey, string> = {
  corroboree: "ok",
  non_corroboree: "warn",
  contredite: "bad",
  indeterminee: "unk",
};

interface Props {
  certifications: CertificationRow[];
  onRetract?: (id: number) => void;
}

export default function CertificationPair({ certifications, onRetract }: Props) {
  if (!certifications.length) {
    return (
      <div className="card card-flat">
        <p style={{ margin: 0, color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
          Aucune lecture d&apos;insider pour le moment. Une lecture est signée, datée et sourcée —
          ce n&apos;est pas un verdict sur une personne.
        </p>
      </div>
    );
  }
  return (
    <div className="stack-sm">
      {certifications.map((c, i) => {
        const proposed = (c.proposed_status || "") as StatusKey;
        return (
          <article key={c.id ?? i} className="card card-flat">
            <div className="cluster" style={{ flexWrap: "wrap" }}>
              <span className={`pill ${c.verdict === "certify" ? "ok" : "warn"}`}>
                <ShieldCheck size={13} />
                {c.verdict === "certify" ? "Information certifiée" : "Information contestée"}
              </span>
              {proposed && PROPOSED_LABELS[proposed] && (
                <span className={`pill ${PROPOSED_CLASS[proposed]}`}>
                  Statut proposé : {PROPOSED_LABELS[proposed]}
                </span>
              )}
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
            <div className="cluster" style={{ marginTop: "var(--s-2)", flexWrap: "wrap" }}>
              {c.source_url && (
                <a
                  href={c.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: "var(--fs-xs)" }}
                >
                  Source de la lecture
                </a>
              )}
              {onRetract && c.id && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => onRetract(c.id as number)}
                  style={{ fontSize: "var(--fs-xs)", minHeight: 34 }}
                >
                  <Trash2 size={12} /> Retirer
                </button>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
