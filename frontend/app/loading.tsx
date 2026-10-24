import BrandMark from "@/components/Logo";
import styles from "@/components/ui.module.css";

/**
 * Écran d'attente affiché le temps qu'une page se prépare.
 * Reprend le bouclier de la marque, un anneau de balayage et les quatre
 * couleurs de statut de la plateforme comme rythme visuel.
 */
export default function Loading() {
  const steps = [
    { color: "var(--ok-bd)", width: "78%" },
    { color: "var(--warn-bd)", width: "62%" },
    { color: "var(--unk-bd)", width: "44%" },
  ];

  return (
    <div className="container">
      <div className={styles.loadingScreen} role="status" aria-live="polite">
        <div className={styles.loadingOrb}>
          <span className={styles.loadingRing} aria-hidden />
          <BrandMark size={56} />
        </div>

        <p className="eyebrow" style={{ marginBottom: 0, justifyContent: "center" }}>
          Dossier de vérification
        </p>
        <h1 className={styles.loadingTitle}>Nous cherchons les traces…</h1>
        <p className={styles.loadingLead}>
          Sources publiées, dates de première apparition, vérifications déjà rendues publiques.
        </p>

        <div className={styles.loadingSteps} aria-hidden>
          {steps.map((s) => (
            <div key={s.color} className={styles.loadingStep}>
              <span className={styles.loadingDot} style={{ color: s.color }} />
              <span className={styles.loadingBars}>
                <span className={styles.loadingBar} style={{ width: s.width }} />
                <span className={styles.loadingBar} style={{ width: "92%" }} />
              </span>
            </div>
          ))}
        </div>

        <div className={styles.loadingStrip} aria-hidden />

        <p className={styles.loadingNote}>
          Le statut proposé ne juge jamais la personne qui a partagé le message.
        </p>
        <span className="sr-only">Chargement en cours</span>
      </div>
    </div>
  );
}
