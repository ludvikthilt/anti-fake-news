import Link from "next/link";
import { APP_NAME } from "@/lib/api";
import BrandMark from "./Logo";
import styles from "./ui.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className="container">
        <div className={styles.footerGrid}>
          <div>
            <div className={styles.footerBrand}>
              <BrandMark size={44} />
              <div>
                <div className={styles.footerName}>{APP_NAME}</div>
                <div className={styles.footerTag}>Vérification &amp; vigilance factuelle</div>
              </div>
            </div>
            <p className={styles.footerText}>
              Un outil éducatif d&apos;aide à la vérification de l&apos;information, réalisé pour
              le concours EDUK-MÉDIA, en partenariat avec l&apos;Union européenne, pour les
              élèves, étudiants et citoyens du Cameroun.
            </p>
            <div className={styles.footerBadges}>
              <span className={styles.footerBadge}>Concours EDUK-MÉDIA</span>
              <span className={styles.footerBadge}>En partenariat avec l&apos;Union européenne</span>
            </div>
          </div>

          <nav aria-label="La plateforme">
            <h2 className={styles.footerHeading}>La plateforme</h2>
            <div className={styles.footerLinks}>
              <Link href="/">Analyser une information</Link>
              <Link href="/comment-ca-marche">La méthode et les statuts</Link>
              <Link href="/wiki">Wiki des insiders</Link>
              <Link href="/historique">Mon historique</Link>
            </div>
          </nav>

          <nav aria-label="Informations et compte">
            <h2 className={styles.footerHeading}>Informations</h2>
            <div className={styles.footerLinks}>
              <Link href="/limites">Limites du service</Link>
              <Link href="/confidentialite">Confidentialité</Link>
              <Link href="/insider/demande">Devenir insider</Link>
              <Link href="/compte">Mon compte</Link>
            </div>
          </nav>
        </div>

        <div className={styles.footerBottom}>
          <span>© {new Date().getFullYear()} {APP_NAME} · Concours EDUK-MÉDIA · Yaoundé, Cameroun</span>
          <span>Ce site aide à vérifier : il ne prouve pas qu&apos;une information est vraie.</span>
        </div>
      </div>
    </footer>
  );
}
