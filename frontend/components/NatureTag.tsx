import type { AnalysisResult } from "@/lib/types";
import styles from "./ui.module.css";

const NATURE_LABELS: Record<string, string> = {
  Information: "Nature : Information",
  Opinion: "Nature : Opinion",
  Rumeur: "Nature : Rumeur",
  Infox: "Nature : Infox",
};

const DISORDER_LABELS: Record<string, string> = {
  Mésinformation: "Désordre : mésinformation",
  Désinformation: "Désordre : désinformation",
  Malinformation: "Désordre : malinformation",
};

export default function NatureTag({ result }: { result: AnalysisResult }) {
  const nature = result.nature ? NATURE_LABELS[result.nature] : null;
  const disorder = result.disorder ? DISORDER_LABELS[result.disorder] : null;
  if (!nature && !disorder) return null;
  return (
    <div className={styles.natureRow} aria-label="Étiquettes pédagogiques EMI">
      {nature && <span className={styles.natureTag}>{nature}</span>}
      {disorder && <span className={styles.natureTag}>{disorder}</span>}
    </div>
  );
}
