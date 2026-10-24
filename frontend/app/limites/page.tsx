import type { Metadata } from "next";

export const metadata: Metadata = { title: "Limites du service" };

export default function Limites() {
  return (
    <div className="container" style={{ maxWidth: "46rem" }}>
      <h1>Limites du service</h1>
      <ul>
        <li>La plateforme aide à vérifier : elle ne prouve pas qu&apos;une information est vraie.</li>
        <li>Elle affiche la <strong>plus ancienne trace trouvée</strong>, jamais « la première apparition » : aucune API ne peut la garantir.</li>
        <li>Certains modules (recherche d&apos;image, vérifications de faits, IA) dépendent de services externes et de quotas. Quand ils sont indisponibles, le résultat est affiché comme partiel.</li>
        <li>Un statut concerne une information, jamais la personne qui l&apos;a partagée.</li>
        <li>Les images analysées ne sont pas conservées : seule une miniature est utilisée le temps de l&apos;analyse.</li>
      </ul>
      <p className="banner">Ce site aide à vérifier : il ne prouve pas qu&apos;une information est vraie.</p>
    </div>
  );
}
