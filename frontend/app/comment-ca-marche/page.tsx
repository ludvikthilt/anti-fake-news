import type { Metadata } from "next";
import Link from "next/link";
import Disclaimer from "@/components/Disclaimer";
import StatusBadge from "@/components/StatusBadge";
import { ArrowRight } from "@/components/Icon";
import styles from "@/components/ui.module.css";

export const metadata: Metadata = { title: "La méthode" };

const STATUTS = [
  {
    key: "corroboree" as const,
    def: "Plusieurs sources indépendantes et fiables reprennent l'information, sans contradiction trouvée.",
    caution: "Cela ne garantit pas que le fait soit exact : cela signifie que les traces convergent.",
  },
  {
    key: "non_corroboree" as const,
    def: "Des traces existent, mais trop peu de sources fiables et indépendantes les reprennent.",
    caution: "Ce n'est pas un « faux » : c'est une information que l'on ne peut pas encore étayer.",
  },
  {
    key: "contredite" as const,
    def: "Une vérification de faits publiée ou plusieurs sources fiables contredisent l'information.",
    caution: "On contredit l'information, pas la personne qui l'a relayée de bonne foi.",
  },
  {
    key: "indeterminee" as const,
    def: "Pas assez d'éléments, analyse partielle ou désaccord entre insiders.",
    caution: "L'indétermination est une réponse honnête, pas un échec de la plateforme.",
  },
];

const NATURES = [
  ["Information factuelle", "Un fait vérifiable, contextualisé, attribuable à une source attestée.", "Oui, on peut le vérifier."],
  ["Opinion", "Un jugement personnel, qui n'est ni vrai ni faux.", "Ce n'est pas un fait : cela se débat."],
  ["Rumeur", "Une information non vérifiée qui circule sans canal traçable.", "Pas encore : il manque des preuves."],
  ["Infox", "Une information fausse ou trompeuse, souvent fabriquée pour nuire.", "On vérifie les faits et l'intention."],
];

const DISORDRES = [
  ["Mésinformation", "Fausse information partagée sans intention de nuire."],
  ["Désinformation", "Fausse information créée avec l'intention de nuire."],
  ["Malinformation", "Information vraie sortie de son contexte pour nuire."],
];

export default function CommentCaMarche() {
  return (
    <div className="container reading">
      <p className="eyebrow">La méthode</p>
      <h1>Comment la plateforme raisonne</h1>
      <p className={styles.heroLead} style={{ marginBottom: "var(--s-4)" }}>
        La plateforme ne dit jamais si une information est « vraie » ou « fausse ». Elle rassemble
        des traces — sources, dates, vérifications déjà publiées — puis propose un statut. C&apos;est
        une aide à la décision, pas un verdict.
      </p>
      <Disclaimer />

      <section className="section" aria-labelledby="statuts">
        <h2 id="statuts" className="sectionTitle">Les quatre statuts</h2>
        <div className="grid2">
          {STATUTS.map((s) => (
            <article key={s.key} className="card card-flat">
              <StatusBadge status={s.key} />
              <p style={{ margin: "var(--s-3) 0 var(--s-2)", fontSize: "var(--fs-sm)" }}>{s.def}</p>
              <p className="hint" style={{ margin: 0 }}>{s.caution}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" aria-labelledby="natures">
        <h2 id="natures" className="sectionTitle">Nature et désordre de l&apos;information</h2>
        <p className="sectionLead">
          En plus du statut, deux étiquettes pédagogiques aident à raisonner : ce que le message
          <em> est</em>, et la manière dont il circule.
        </p>
        <div className="tableWrap">
          <table className="table" style={{ whiteSpace: "normal" }}>
            <thead>
              <tr><th>Nature</th><th>Définition</th><th>Peut-on vérifier ?</th></tr>
            </thead>
            <tbody>
              {NATURES.map(([n, d, q]) => (
                <tr key={n}>
                  <td style={{ fontWeight: 600, color: "var(--brand-900)" }}>{n}</td>
                  <td style={{ color: "var(--ink-muted)" }}>{d}</td>
                  <td className="hint">{q}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3 style={{ marginTop: "var(--s-6)" }}>Les trois désordres</h3>
        <div className="stack-sm">
          {DISORDRES.map(([n, d]) => (
            <div key={n} className="card card-flat">
              <strong style={{ fontSize: "var(--fs-sm)" }}>{n}</strong>
              <p className="muted" style={{ margin: "4px 0 0", fontSize: "var(--fs-sm)" }}>{d}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section" aria-labelledby="questions">
        <h2 id="questions" className="sectionTitle">Deux questions avant de partager</h2>
        <div className="grid2">
          <div className="card">
            <p className="eyebrow" style={{ marginBottom: 6 }}>Question 1</p>
            <h3 style={{ fontSize: "var(--fs-md)" }}>Peut-on vérifier ce qui est affirmé ?</h3>
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Un lieu, une date, un document, un témoin identifiable. Si rien de tout cela
              n&apos;existe, le message relève de la rumeur.
            </p>
          </div>
          <div className="card">
            <p className="eyebrow" style={{ marginBottom: 6, color: "var(--bad-fg)" }}>Question 2</p>
            <h3 style={{ fontSize: "var(--fs-md)" }}>Y a-t-il une intention de nuire ?</h3>
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Peur provoquée, groupe ciblé, gain commercial caché. L&apos;intention ne se devine
              pas : elle s&apos;argumente avec des preuves.
            </p>
          </div>
        </div>
      </section>

      <section className="section">
        <p className="banner banner-info">
          <span>
            <strong>Une limite assumée :</strong> la plateforme affiche la plus ancienne trace
            trouvée, jamais « la première apparition ». Aucune API ne peut la garantir.{" "}
            <Link href="/limites">Voir les limites du service</Link>.
          </span>
        </p>
        <p style={{ marginTop: "var(--s-4)" }}>
          <Link href="/" className="btn btn-primary">
            Vérifier une information <ArrowRight size={16} />
          </Link>
        </p>
      </section>
    </div>
  );
}
