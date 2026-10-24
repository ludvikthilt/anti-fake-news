import type { Metadata } from "next";
import Link from "next/link";
import Disclaimer from "@/components/Disclaimer";
import { Info } from "@/components/Icon";

export const metadata: Metadata = { title: "Limites du service" };

const LIMITES: [string, string][] = [
  ["Une aide, pas une preuve", "La plateforme ne prouve pas qu'une information est vraie. Elle montre ce que les sources permettent de dire à un instant donné."],
  ["La plus ancienne trace, pas « la première apparition »", "Aucun outil ne peut garantir la date exacte de la première diffusion d'un contenu. Nous affichons la trace la plus ancienne retrouvée, avec son origine."],
  ["Une analyse parfois partielle", "Certaines vérifications peuvent manquer. Quand cela arrive, le résultat reste affiché, mais il est signalé comme incomplet."],
  ["Des sources inégales", "Un média reconnu, une institution et un compte anonyme n'ont pas le même poids. La fiabilité affichée est indicative, jamais absolue."],
  ["Aucun jugement sur les personnes", "Un statut concerne une information, jamais la personne qui l'a partagée ni son intention supposée."],
  ["Images non conservées", "Les images soumises servent le temps de l'analyse ; elles ne sont pas conservées comme archive."],
];

export default function Limites() {
  return (
    <div className="container reading">
      <p className="eyebrow">Transparence</p>
      <h1>Limites du service</h1>
      <p className="hint" style={{ marginBottom: "var(--s-4)" }}>
        <Info size={14} style={{ verticalAlign: "-2px", marginRight: 4 }} />
        Ce que la plateforme peut faire, et ce qu&apos;elle ne peut pas promettre.
      </p>

      <div className="stack-sm">
        {LIMITES.map(([title, text]) => (
          <section key={title} className="card card-flat">
            <h2 style={{ fontSize: "var(--fs-md)", marginBottom: 4 }}>{title}</h2>
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>{text}</p>
          </section>
        ))}
      </div>

      <div style={{ marginTop: "var(--s-6)" }}>
        <Disclaimer />
      </div>

      <p style={{ marginTop: "var(--s-4)" }}>
        Pour signaler une erreur, ouvrez le dossier concerné et utilisez le lien{" "}
        <Link href="/">« Signaler une erreur »</Link>.
      </p>
    </div>
  );
}
