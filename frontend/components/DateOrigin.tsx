import styles from "./ui.module.css";

const LABELS: Record<string, string> = {
  declared: "Déclarée",
  observed: "Observée",
  metadata: "Métadonnée",
  indexation: "Indexation",
};

export default function DateOrigin({ origin }: { origin: string }) {
  const label = LABELS[origin] || "Origine inconnue";
  return <span className={styles.dateOrigin}>{label}</span>;
}
