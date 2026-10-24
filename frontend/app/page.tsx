import type { Metadata } from "next";
import SubmitForm from "@/components/SubmitForm";
import Disclaimer from "@/components/Disclaimer";

export const metadata: Metadata = {
  title: "Analyser une information",
};

export default function Home() {
  return (
    <div className="container">
      <section className="hero">
        <h1>Défions l&apos;infox, ensemble.</h1>
        <p style={{ maxWidth: "46rem" }}>
          Vérifiez une information que vous avez reçue : un texte, un lien ou une image.
          La plateforme rassemble les sources, les dates et les vérifications déjà publiées —
          puis vous laisse juger par vous-même.
        </p>
        <Disclaimer />
      </section>

      <section className="card card-accent" aria-labelledby="soumission-titre">
        <h2 id="soumission-titre" style={{ fontSize: "var(--fs-lg)" }}>
          Soumettre une information
        </h2>
        <SubmitForm />
      </section>

      <section aria-labelledby="etapes-titre">
        <h2 id="etapes-titre" className="sectionTitle">
          Comment ça marche
        </h2>
        <div className="grid2">
          {[
            ["1. Vous soumettez", "Un texte, un lien ou une image à vérifier."],
            ["2. La plateforme recherche", "Les traces, les dates et les vérifications de faits déjà publiées."],
            ["3. Un statut est proposé", "Corroborée, non corroborée, contredite ou indéterminée — jamais un verdict."],
            ["4. Vous jugez", "En ouvrant les sources, avec les critères affichés."],
          ].map(([t, d]) => (
            <div key={t} className="card">
              <h3 style={{ fontSize: "var(--fs-md)" }}>{t}</h3>
              <p style={{ color: "var(--ink-muted)" }}>{d}</p>
            </div>
          ))}
        </div>
        <p style={{ marginTop: "var(--s-4)" }}>
          <a href="/comment-ca-marche">En savoir plus sur la méthode</a>
        </p>
      </section>
    </div>
  );
}
