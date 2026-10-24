import Link from "next/link";
import { APP_NAME } from "@/lib/api";
import styles from "./ui.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className="container">
        <div className={styles.footerGrid}>
          <div>
            <strong>{APP_NAME}</strong>
            <p style={{ fontSize: "var(--fs-sm)", marginTop: "var(--s-2)", color: "#bcd9ec" }}>
              Un outil éducatif d&apos;aide à la vérification de l&apos;information, conçu pour les élèves et étudiants du Mfoundi.
            </p>
            <div className={styles.logoRow}>
              <span className={styles.logoBox}>EDUK-MÉDIA</span>
              <span className={styles.logoBox}>Projet financé par l&apos;Union européenne</span>
            </div>
          </div>
          <nav aria-label="Liens du pied de page">
            <Link href="/confidentialite">Confidentialité</Link>
            <br />
            <Link href="/limites">Limites du service</Link>
            <br />
            <Link href="/comment-ca-marche">Comment ça marche</Link>
            <br />
            <Link href="/wiki">Wiki des insiders</Link>
          </nav>
          <nav aria-label="Autres liens">
            <Link href="/historique">Historique</Link>
            <br />
            <Link href="/compte">Compte</Link>
            <br />
            <Link href="/insider/demande">Devenir insider</Link>
          </nav>
        </div>
        <p className={styles.footerPhrase}>
          Ce site aide à vérifier : il ne prouve pas qu&apos;une information est vraie.
        </p>
      </div>
    </footer>
  );
}
