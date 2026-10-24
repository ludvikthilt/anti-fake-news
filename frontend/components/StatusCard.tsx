import type { AnalysisResult } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import styles from "./ui.module.css";

export default function StatusCard({ result }: { result: AnalysisResult }) {
  return (
    <section className={styles.statusCard} aria-labelledby="statut-titre">
      <div className={styles.statusHead}>
        <StatusBadge status={result.status} />
        <h2 id="statut-titre" style={{ margin: 0, fontSize: "var(--fs-lg)" }}>
          Statut de l&apos;information
        </h2>
      </div>
      <p className={styles.statusPhrase}>{result.status_phrase}</p>
      <p className={styles.statusNote}>
        C&apos;est une aide à la décision. C&apos;est vous qui jugez, en ouvrant les sources.
        Ce statut concerne l&apos;information, jamais la personne qui l&apos;a partagée.
      </p>
    </section>
  );
}
