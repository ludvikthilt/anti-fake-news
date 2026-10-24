import type { Criterion } from "@/lib/types";
import { Check, MinusCircle } from "./Icon";
import styles from "./ui.module.css";

export default function CriteriaList({ criteria }: { criteria: Criterion[] }) {
  if (!criteria.length) return null;
  return (
    <details className="accordion">
      <summary>Critères pris en compte ({criteria.length})</summary>
      <div>
        <div className={styles.criteria}>
          {criteria.map((c) => (
            <div key={c.key} className={styles.criteriaRow}>
              <span
                aria-hidden
                style={{ color: c.ok ? "var(--ok-fg)" : "var(--ink-muted)", marginTop: 2 }}
              >
                {c.ok ? <Check size={17} /> : <MinusCircle size={17} />}
              </span>
              <div>
                <div className={styles.criteriaValue}>{c.label}</div>
                <div style={{ fontSize: "var(--fs-sm)" }}>{c.value}</div>
                <div className={styles.criteriaExplanation}>{c.explanation}</div>
                <span className="sr-only">{c.ok ? "Critère rempli." : "Critère non rempli."}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </details>
  );
}
