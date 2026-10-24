import type { Metadata } from "next";
import Link from "next/link";
import SubmitForm from "@/components/SubmitForm";
import StatusBadge from "@/components/StatusBadge";
import { ArrowRight, MapPin, ShieldCheck } from "@/components/Icon";
import { APP_NAME } from "@/lib/api";
import styles from "@/components/ui.module.css";

export const metadata: Metadata = {
  title: `Analyser une information · ${APP_NAME}`,
};

const NATURES = [
  {
    name: "Information factuelle",
    dot: "var(--ok-bd)",
    text: "Un fait vérifiable, contextualisé, attribuable à une source attestée, sans dramatisation volontaire.",
    example: "Communiqué signé d'un ministère",
  },
  {
    name: "Opinion / point de vue",
    dot: "var(--brand-500)",
    text: "Un jugement personnel ou une analyse éditoriale. Une opinion ne se déclare ni vraie ni fausse : elle se débat.",
    example: "« Les taxis de Mokolo conduisent trop vite »",
  },
  {
    name: "Rumeur non étayée",
    dot: "var(--warn-bd)",
    text: "Un propos colporté sans canal traçable, souvent introduit par « on dit que » ou « un cousin au ministère ».",
    example: "Fermeture d'un marché annoncée sans décret",
  },
  {
    name: "Infox (désinformation)",
    dot: "var(--bad-bd)",
    text: "Une falsification volontaire — faux arrêté, photo recyclée — conçue pour tromper et se propager.",
    example: "Faux timbre officiel sur une taxe inventée",
  },
];

const STEPS = [
  ["Vous soumettez", "Un texte, un lien ou une capture d'écran reçue par WhatsApp, SMS ou sur un réseau social."],
  ["Nous cherchons les traces", "Sources publiées, dates de première apparition, vérifications de faits déjà rendues publiques."],
  ["Un statut est proposé", "Corroborée, non corroborée, contredite ou indéterminée — jamais un verdict sur une personne."],
  ["Vous jugez", "Les sources, les dates et les critères restent ouverts : c'est vous qui concluez."],
];

const STATUTS: { key: "corroboree" | "non_corroboree" | "contredite" | "indeterminee"; text: string }[] = [
  { key: "corroboree", text: "Plusieurs sources indépendantes et fiables reprennent l'information, sans contradiction trouvée." },
  { key: "non_corroboree", text: "Des traces existent, mais trop peu de sources fiables et indépendantes : ce n'est pas un « faux »." },
  { key: "contredite", text: "Une vérification publiée ou plusieurs sources fiables contredisent l'information." },
  { key: "indeterminee", text: "Pas assez d'éléments, analyse partielle ou désaccord entre insiders." },
];

export default function Home() {
  return (
    <div className="container">
      <section className={styles.hero}>
        <span className={styles.heroPill}>
          <MapPin size={14} />
          Cameroun
        </span>
        <h1 className={styles.heroTitle}>Défions l&apos;infox, avec méthode.</h1>
        <p className={styles.heroLead}>
          Vérifiez un message reçu avant de le partager. La plateforme rassemble les sources,
          les dates et les vérifications déjà publiées — puis vous laisse juger.
        </p>
      </section>

      <aside className="banner" role="note">
        <ShieldCheck size={18} style={{ flex: "none", marginTop: 2, color: "var(--brand-700)" }} />
        <span>
          <strong>Ce site aide à vérifier :</strong> il ne prouve pas qu&apos;une information est vraie.
        </span>
      </aside>

      <section className={`${styles.console}`} aria-labelledby="soumission-titre">
        <div className="spread" style={{ marginBottom: "var(--s-4)" }}>
          <div>
            <p className="eyebrow" style={{ marginBottom: 2 }}>Console de vérification</p>
            <h2 id="soumission-titre" style={{ margin: 0, fontSize: "var(--fs-lg)" }}>
              Soumettre une information
            </h2>
          </div>
          <span className="pill">Gratuit · sans compte</span>
        </div>
        <SubmitForm />
      </section>

      <section className="section" aria-labelledby="autodefense-titre">
        <div className="spread" style={{ marginBottom: "var(--s-3)" }}>
          <h2 id="autodefense-titre" className="sectionTitle" style={{ margin: 0 }}>
            Auto-défense critique
          </h2>
          <span className="muted" style={{ fontSize: "var(--fs-xs)" }}>Méthode CEMAC</span>
        </div>
        <div className="grid2">
          <div className="card">
            <p className="eyebrow" style={{ marginBottom: "var(--s-2)" }}>Test 1</p>
            <h3 style={{ fontSize: "var(--fs-md)" }}>Peut-on vérifier les faits ?</h3>
            <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: 0 }}>
              Lieu daté, témoin identifiable, document officiel accessible.
            </p>
          </div>
          <div className="card">
            <p className="eyebrow" style={{ marginBottom: "var(--s-2)", color: "var(--bad-fg)" }}>Test 2</p>
            <h3 style={{ fontSize: "var(--fs-md)" }}>Y a-t-il une intention de nuire ?</h3>
            <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: 0 }}>
              Provocation de panique, ciblage communautaire, appât commercial.
            </p>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="natures-titre">
        <h2 id="natures-titre" className="sectionTitle">Les quatre natures d&apos;un message</h2>
        <p className="sectionLead">
          Avant de chercher des sources, identifiez ce que vous lisez. Toutes les phrases ne se
          vérifient pas de la même manière.
        </p>
        {NATURES.map((n) => (
          <details key={n.name} className="accordion">
            <summary>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "var(--s-2)" }}>
                <span
                  aria-hidden
                  style={{ width: 9, height: 9, borderRadius: 99, background: n.dot, flex: "none" }}
                />
                {n.name}
              </span>
            </summary>
            <div>
              <p style={{ margin: "0 0 var(--s-2)" }}>{n.text}</p>
              <span className="pill">{n.example}</span>
            </div>
          </details>
        ))}
      </section>

      <section className="section" aria-labelledby="etapes-titre">
        <h2 id="etapes-titre" className="sectionTitle">Comment la plateforme travaille</h2>
        <div className="grid4">
          {STEPS.map(([title, text], i) => (
            <article key={title} className="card card-flat">
              <span
                className="mono"
                style={{ color: "var(--brand-500)", fontWeight: 600, fontSize: "var(--fs-xs)" }}
              >
                0{i + 1}
              </span>
              <h3 style={{ fontSize: "var(--fs-md)", margin: "var(--s-2) 0" }}>{title}</h3>
              <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: 0 }}>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" aria-labelledby="statuts-titre">
        <h2 id="statuts-titre" className="sectionTitle">Les quatre statuts</h2>
        <p className="sectionLead">
          Un statut décrit ce que les sources permettent de dire aujourd&apos;hui. Il ne juge jamais
          la personne qui a partagé le message.
        </p>
        <div className="grid2">
          {STATUTS.map((s) => (
            <article key={s.key} className="card card-flat">
              <StatusBadge status={s.key} />
              <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: "var(--s-3) 0 0" }}>
                {s.text}
              </p>
            </article>
          ))}
        </div>
        <p style={{ marginTop: "var(--s-4)" }}>
          <Link href="/comment-ca-marche" className="btn btn-secondary">
            Comprendre la méthode <ArrowRight size={16} />
          </Link>
        </p>
      </section>

      <section className="section">
        <p className="banner">
          <span>
            <strong>Rappel :</strong> ce site aide à vérifier. Il ne prouve pas qu&apos;une
            information est vraie, et ne remplace pas une rédaction professionnelle.
          </span>
        </p>
      </section>
    </div>
  );
}
