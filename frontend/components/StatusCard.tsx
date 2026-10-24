import type { AnalysisResult } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import styles from "./ui.module.css";

export default function StatusCard({ result }: { result: AnalysisResult }) {
  return (
    <section className={styles.statusCard} aria-labelledby="statut-titre">
      <div className={styles.statusHead}>
        <StatusBadge status={result.status} />
        <p className={styles.statusEyebrow} id="statut-titre">Statut proposé</p>
      </div>
      <p className={styles.statusPhrase}>{result.status_phrase}</p>
      <p className={styles.statusNote}>
        C&apos;est une aide à la décision, pas un verdict : c&apos;est vous qui jugez, en ouvrant
        les sources. Ce statut porte sur l&apos;information, jamais sur la personne qui l&apos;a
        partagée.
      </p>
    </section>
  );
}
