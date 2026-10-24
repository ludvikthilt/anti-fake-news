import type { Metadata } from "next";

export const metadata: Metadata = { title: "Confidentialité" };

export default function Confidentialite() {
  return (
    <div className="container" style={{ maxWidth: "46rem" }}>
      <h1>Confidentialité</h1>
      <ul>
        <li>Ne soumettez pas d&apos;informations personnelles ou confidentielles.</li>
        <li>Le contenu soumis peut être transmis à des services externes de recherche, d&apos;OCR ou d&apos;IA, uniquement dans le but de l&apos;analyse.</li>
        <li>Les originaux des images ne sont pas conservés après l&apos;analyse.</li>
        <li>Les analyses publiques restent accessibles à toute personne qui possède leur lien.</li>
        <li>Aucun script de suivi publicitaire n&apos;est utilisé.</li>
      </ul>
      <p>
        Pour toute question, utilisez le lien « Signaler une erreur » disponible sur les résultats,
        ou contactez l&apos;équipe EDUK-MÉDIA.
      </p>
    </div>
  );
}
