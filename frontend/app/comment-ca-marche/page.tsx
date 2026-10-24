import type { Metadata } from "next";

export const metadata: Metadata = { title: "Comment ça marche" };

const ROWS: [string, string, string][] = [
  ["Information", "Un fait que l'on peut vérifier.", "Peut-on le vérifier ? Oui."],
  ["Opinion", "Un jugement personnel, qui n'est ni vrai ni faux.", "Ce n'est pas un fait à vérifier."],
  ["Rumeur", "Une information non vérifiée qui circule.", "Peut-on le vérifier ? Pas encore."],
  ["Infox", "Une information fausse ou trompeuse.", "Vérifiée et contredite — reste l'intention."],
];

const DISORDER: [string, string][] = [
  ["Mésinformation", "Fausse information partagée sans intention de nuire."],
  ["Désinformation", "Fausse information créée avec l'intention de nuire."],
  ["Malinformation", "Information vraie sortie de son contexte pour nuire."],
];

export default function CommentCaMarche() {
  return (
    <div className="container" style={{ maxWidth: "46rem" }}>
      <h1>Comment ça marche</h1>
      <p>
        La plateforme ne dit jamais si une information est « vraie » ou « fausse ».
        Elle rassemble des traces — sources, dates, vérifications déjà publiées — puis propose un statut :
        c&apos;est une aide à la décision, pas un verdict.
      </p>

      <h2 className="sectionTitle">Les quatre statuts</h2>
      <ul>
        <li><strong>Corroborée</strong> : plusieurs sources indépendantes et fiables reprennent l&apos;information, sans contradiction trouvée.</li>
        <li><strong>Non corroborée</strong> : des traces existent, mais trop peu de sources fiables et indépendantes. Ce n&apos;est pas un « faux ».</li>
        <li><strong>Contredite</strong> : une vérification de faits publiée ou plusieurs sources fiables contredisent l&apos;information.</li>
        <li><strong>Indéterminée</strong> : pas assez d&apos;éléments, analyse partielle, ou désaccord entre insiders.</li>
      </ul>

      <h2 className="sectionTitle">Nature et désordre de l&apos;information</h2>
      <p>En plus du statut, deux étiquettes pédagogiques aident à raisonner.</p>
      <table className="card" style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--fs-sm)" }}>
        <thead>
          <tr><th style={{ textAlign: "left", padding: "var(--s-2)" }}>Nature</th><th style={{ textAlign: "left", padding: "var(--s-2)" }}>Définition</th></tr>
        </thead>
        <tbody>
          {ROWS.map(([n, d, q]) => (
            <tr key={n} style={{ borderTop: "1px solid var(--line)" }}>
              <td style={{ padding: "var(--s-2)", fontWeight: 600 }}>{n}</td>
              <td style={{ padding: "var(--s-2)" }}>{d} <em style={{ color: "var(--ink-muted)" }}>{q}</em></td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ marginTop: "var(--s-6)" }}>Les trois désordres de l&apos;information</h3>
      <ul>
        {DISORDER.map(([n, d]) => (
          <li key={n}><strong>{n}</strong> : {d}</li>
        ))}
      </ul>

      <h2 className="sectionTitle">Deux questions à se poser</h2>
      <p><strong>Peut-on le vérifier ?</strong> et <strong>y a-t-il une intention de nuire ?</strong></p>

      <p className="banner" style={{ marginTop: "var(--s-6)" }}>
        Ce site aide à vérifier : il ne prouve pas qu&apos;une information est vraie.
      </p>
    </div>
  );
}
