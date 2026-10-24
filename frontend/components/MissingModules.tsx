import type { MissingService } from "@/lib/types";
import { Info } from "./Icon";
import styles from "./ui.module.css";

/**
 * Analyse partielle : on informe sans exposer la mécanique interne
 * (fournisseurs, erreurs d'API, moteurs OCR). L'utilisateur n'a besoin
 * que de savoir ce qui reste fiable et ce qu'il peut faire.
 */
export default function MissingModules({ missing }: { missing: MissingService[] }) {
  if (!missing.length) return null;
  return (
    <div className={styles.missing} role="status">
      <Info size={20} className={styles.missingIcon} />
      <div>
        <strong className={styles.missingTitle}>Certains éléments n&apos;ont pas pu être vérifiés</strong>
        <p>
          Nous n&apos;avons pas pu réunir toutes les pièces pour cette information. Le résultat
          ci-dessous reste utilisable, mais il est incomplet : ouvrez les sources disponibles
          avant de vous faire un avis.
        </p>
      </div>
    </div>
  );
}
