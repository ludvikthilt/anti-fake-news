import type { Metadata } from "next";
import Link from "next/link";
import { Lock } from "@/components/Icon";

export const metadata: Metadata = { title: "Confidentialité" };

const ITEMS: [string, string][] = [
  ["Ne partagez rien de sensible", "Ne soumettez ni information personnelle, ni échange privé, ni document confidentiel."],
  ["Ce qui est transmis", "Le contenu soumis peut être envoyé à des services externes de recherche, d'analyse d'image ou d'IA, uniquement pour produire le résultat."],
  ["Ce qui est conservé", "Les originaux des images ne sont pas conservés après l'analyse. Le texte et les liens restent associés au dossier public."],
  ["Ce qui est public", "Un dossier d'analyse est accessible à toute personne qui possède son lien. Ne le partagez pas si le contenu est sensible."],
  ["Aucun profilage publicitaire", "La plateforme n'utilise aucun script de suivi publicitaire ni revendeur de données."],
  ["Vos droits", "Vous pouvez supprimer votre compte et vos analyses depuis votre espace personnel, à tout moment."],
];

export default function Confidentialite() {
  return (
    <div className="container reading">
      <p className="eyebrow">Vos données</p>
      <h1>Confidentialité</h1>
      <p className="hint" style={{ marginBottom: "var(--s-4)" }}>
        <Lock size={14} style={{ verticalAlign: "-2px", marginRight: 4 }} />
        Une plateforme d&apos;intérêt public doit dire clairement ce qu&apos;elle fait des contenus reçus.
      </p>

      <div className="stack-sm">
        {ITEMS.map(([title, text]) => (
          <section key={title} className="card card-flat">
            <h2 style={{ fontSize: "var(--fs-md)", marginBottom: 4 }}>{title}</h2>
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>{text}</p>
          </section>
        ))}
      </div>

      <p style={{ marginTop: "var(--s-6)" }}>
        Une question, une demande de suppression ? Utilisez le lien{" "}
        <Link href="/limites">« Signaler une erreur »</Link> disponible sur chaque résultat.
      </p>
    </div>
  );
}
