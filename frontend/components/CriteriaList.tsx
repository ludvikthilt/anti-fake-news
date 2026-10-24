"use client";

import { useState } from "react";
import type { Criterion } from "@/lib/types";
import { Check, MinusCircle } from "./Icon";
import styles from "./ui.module.css";

export default function CriteriaList({ criteria }: { criteria: Criterion[] }) {
  const [open, setOpen] = useState(false);
  return (
    <section aria-labelledby="criteres-titre">
      <button
        className="btn btn-secondary"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="criteres-liste"
      >
        <span id="criteres-titre">Voir les critères</span>
      </button>
      {open && (
        <div id="criteres-liste" className={styles.criteria} style={{ marginTop: "var(--s-3)" }}>
          {criteria.map((c) => (
            <div key={c.key} className={styles.criteriaRow}>
              <span style={{ color: c.ok ? "var(--ok-fg)" : "var(--ink-muted)" }}>
                {c.ok ? <Check size={18} /> : <MinusCircle size={18} />}
              </span>
              <div>
                <div className={styles.criteriaValue}>{c.label}</div>
                <div>{c.value}</div>
                <div className={styles.criteriaExplanation}>{c.explanation}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
