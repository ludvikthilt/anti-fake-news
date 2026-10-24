import styles from "./ui.module.css";

type SpinnerProps = {
  size?: number;
  /** Texte lu par les lecteurs d'écran ; le visuel est décoratif. */
  label?: string;
  className?: string;
};

/**
 * Spinner InfoxVerify : deux arcs de balayage autour d'un noyau qui respire,
 * dans la couleur du texte courant (donc lisible sur bouton plein comme sur fond clair).
 */
export default function Spinner({ size = 20, label = "Chargement en cours", className }: SpinnerProps) {
  return (
    <span className={`${styles.spinner} ${className ?? ""}`} role="status">
      <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden>
        <circle cx="16" cy="16" r="12" stroke="currentColor" strokeOpacity="0.16" strokeWidth="3" />
        <g className={styles.spinnerArc}>
          <circle
            cx="16"
            cy="16"
            r="12"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="56 19.4"
            transform="rotate(-90 16 16)"
          />
        </g>
        <g className={styles.spinnerInner}>
          <circle
            cx="16"
            cy="16"
            r="7"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeDasharray="14 30"
            strokeOpacity="0.65"
            transform="rotate(60 16 16)"
          />
        </g>
        <circle className={styles.spinnerCore} cx="16" cy="16" r="2.4" fill="currentColor" />
      </svg>
      <span className="sr-only">{label}</span>
    </span>
  );
}
