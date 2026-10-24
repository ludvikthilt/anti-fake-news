import type { MissingService } from "@/lib/types";
import { Alert } from "./Icon";
import styles from "./ui.module.css";

export default function MissingModules({ missing }: { missing: MissingService[] }) {
  if (!missing.length) return null;
  return (
    <div className={styles.missing} role="status">
      <strong>
        <Alert size={16} style={{ verticalAlign: "-3px", marginRight: 6 }} />
        Analyse partielle — certains modules sont indisponibles.
      </strong>
      <ul className={styles.missingList}>
        {missing.map((m, i) => (
          <li key={i}>
            {m.service} : {m.reason || "service ne répond pas"}
          </li>
        ))}
      </ul>
      <p style={{ margin: "var(--s-2) 0 0", fontSize: "var(--fs-sm)" }}>
        Le résultat affiché ci-dessous reste valable avec les éléments disponibles.
      </p>
    </div>
  );
}
