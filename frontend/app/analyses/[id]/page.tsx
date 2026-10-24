"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { AnalysisDetail } from "@/lib/types";
import StatusCard from "@/components/StatusCard";
import NatureTag from "@/components/NatureTag";
import MissingModules from "@/components/MissingModules";
import SourceTimeline from "@/components/SourceTimeline";
import CriteriaList from "@/components/CriteriaList";
import FactCheckCard from "@/components/FactCheckCard";
import CertificationPair from "@/components/CertificationPair";
import Disclaimer from "@/components/Disclaimer";
import Spinner from "@/components/Spinner";
import { Calendar, ExternalLink, Info, Search } from "@/components/Icon";
import styles from "@/components/ui.module.css";

const STEPS = [
  ["Lecture", "Le contenu est lu et transcrit."],
  ["Recherche", "Les sources publiées sont rassemblées."],
  ["Dates", "L'ancienneté des traces est établie."],
  ["Statut", "Les critères sont comparés, puis le statut est proposé."],
];

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState("");
  const [slow, setSlow] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const polls = useRef(0);

  const load = useCallback(async () => {
    try {
      const res = await api<AnalysisDetail>(`/analyses/${id}/`, { auth: false });
      setData(res);
      const running = res.status === "pending" || res.status === "running";
      // La recherche inversée d'image arrive après le statut : on continue
      // de rafraîchir quelques minutes pour l'afficher sans rechargement.
      const enriching = Boolean(res.result?.extraction?.image_pending) && polls.current < 70;
      if (running || enriching) {
        polls.current += 1;
        timer.current = setTimeout(load, running ? 2000 : 3000);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analyse introuvable.");
    }
  }, [id]);

  useEffect(() => {
    load();
    const slowTimer = setTimeout(() => setSlow(true), 4000);
    return () => {
      clearTimeout(timer.current);
      clearTimeout(slowTimer);
    };
  }, [load]);

  if (error) {
    return (
      <div className="container reading">
        <p className="eyebrow">Dossier de vérification</p>
        <h1>Analyse indisponible</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>
          <Link href="/" className="btn btn-primary">Lancer une nouvelle analyse</Link>
        </p>
      </div>
    );
  }

  if (!data || data.status === "pending" || data.status === "running") {
    return (
      <div className="container reading">
        <div className={styles.pageHeader}>
          <div>
            <p className="eyebrow" style={{ marginBottom: 6 }}>Dossier de vérification</p>
            <h1 style={{ margin: 0 }}>Analyse en cours</h1>
          </div>
          <span className={styles.dossierId}>#{id}</span>
        </div>
        <div className="card card-accent">
          <div className="cluster" style={{ marginBottom: "var(--s-4)" }}>
            <Spinner size={20} label="Recherche des sources" />
            <strong style={{ fontSize: "var(--fs-sm)" }}>Recherche des sources et des antériorités…</strong>
          </div>
          <ol className="stack-sm" style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {STEPS.map(([title, text], i) => (
              <li key={title} className="cluster" style={{ alignItems: "flex-start", gap: "var(--s-3)" }}>
                <span
                  className="mono"
                  style={{
                    flex: "none",
                    width: 24,
                    height: 24,
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: 99,
                    background: "var(--brand-100)",
                    color: "var(--brand-700)",
                    fontSize: 11,
                    fontWeight: 600,
                  }}
                >
                  {i + 1}
                </span>
                <span>
                  <strong style={{ fontSize: "var(--fs-sm)" }}>{title}</strong>
                  <span className="muted" style={{ display: "block", fontSize: "var(--fs-xs)" }}>{text}</span>
                </span>
              </li>
            ))}
          </ol>
          <p className="hint" style={{ marginTop: "var(--s-4)" }}>
            Cette page se met à jour toute seule. Vous pouvez la fermer : le lien reste valable,
            et les inscrits sont prévenus à la fin.
          </p>
          {slow && (
            <p className="banner" role="status" style={{ marginTop: "var(--s-4)" }}>
              La préparation prend un peu plus de temps que d&apos;habitude. Merci de patienter.
            </p>
          )}
        </div>
      </div>
    );
  }

  const r = data.result;
  const created = new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(r.created_at));

  return (
    <div className="container">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Dossier de vérification</p>
          <h1 style={{ margin: 0 }}>Résultat de l&apos;analyse</h1>
        </div>
        <span className={styles.dossierId}>#{r.public_id}</span>
      </div>

      <MissingModules missing={r.missing} />

      <StatusCard result={r} />
      <NatureTag result={r} />

      <div className={styles.analysisGrid} style={{ marginTop: "var(--s-6)" }}>
        <div className="stack">
          {r.extraction?.image_pending && (
            <p className="banner banner-info" role="status">
              <Info size={17} style={{ flex: "none", marginTop: 2 }} />
              <span>La recherche de cette image sur le web se poursuit. Les correspondances apparaîtront ici automatiquement.</span>
            </p>
          )}

          {r.extraction?.ocr_text && (
            <section className="card" aria-labelledby="ocr-titre">
              <h2 id="ocr-titre" className="sectionTitle">Texte lu dans l&apos;image</h2>
              <p className="mono" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", margin: 0 }}>
                {r.extraction.ocr_text}
              </p>
            </section>
          )}

          {r.extraction &&
            (r.extraction.title ||
              r.extraction.author ||
              r.extraction.date ||
              (r.extraction.keywords && r.extraction.keywords.length > 0)) && (
              <section className="card" aria-labelledby="extraction-titre">
                <h2 id="extraction-titre" className="sectionTitle">Éléments identifiés</h2>
                <dl className="stack-sm" style={{ margin: 0 }}>
                  {r.extraction.title && (
                    <div>
                      <dt className="hint">Titre</dt>
                      <dd style={{ margin: 0, fontWeight: 600 }}>{r.extraction.title}</dd>
                    </div>
                  )}
                  {r.extraction.author && (
                    <div>
                      <dt className="hint">Auteur déclaré</dt>
                      <dd style={{ margin: 0 }}>{r.extraction.author}</dd>
                    </div>
                  )}
                  {r.extraction.date && (
                    <div>
                      <dt className="hint">Date annoncée</dt>
                      <dd style={{ margin: 0 }}>
                        <span className="cluster" style={{ gap: 6 }}>
                          <Calendar size={14} />
                          {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(r.extraction.date))}
                        </span>
                      </dd>
                    </div>
                  )}
                  {r.extraction.keywords && r.extraction.keywords.length > 0 && (
                    <div>
                      <dt className="hint">Mots-clés</dt>
                      <dd style={{ margin: 0, display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {r.extraction.keywords.map((k, i) => (
                          <span key={i} className="pill">{k}</span>
                        ))}
                      </dd>
                    </div>
                  )}
                </dl>
              </section>
            )}

          {r.extraction?.image_tools && r.extraction.image_tools.length > 0 && (
            <section className="card" aria-labelledby="outils-image-titre">
              <h2 id="outils-image-titre" className="sectionTitle">
                <Search size={18} /> Poursuivre la recherche d&apos;image
              </h2>
              <p className="hint" style={{ marginBottom: "var(--s-3)" }}>
                La date de première apparition n&apos;a pas pu être établie automatiquement.
                Vous pouvez lancer la recherche vous-même :
              </p>
              <div className="cluster">
                {r.extraction.image_tools.map((t, i) => (
                  <a key={i} className="btn btn-secondary" href={t.link} target="_blank" rel="noopener noreferrer">
                    {t.title} <ExternalLink size={14} />
                    <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
                  </a>
                ))}
              </div>
            </section>
          )}

          <section aria-labelledby="sources-titre">
            <h2 id="sources-titre" className="sectionTitle">Sources retrouvées</h2>
            <SourceTimeline sources={r.sources} />
          </section>

          <section aria-labelledby="factchecks-titre">
            <h2 id="factchecks-titre" className="sectionTitle">Vérifications déjà publiées</h2>
            <FactCheckCard items={r.factchecks} />
          </section>

          <section aria-labelledby="certifications-titre">
            <h2 id="certifications-titre" className="sectionTitle">Lectures des insiders</h2>
            <CertificationPair certifications={r.certifications} />
          </section>

          <CriteriaList criteria={r.criteria} />
        </div>

        <aside className={styles.analysisAside}>
          <div className="card card-flat stack-sm">
            <p className="eyebrow" style={{ margin: 0 }}>Repères</p>
            <p style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              <strong>Comment lire ce dossier</strong>
            </p>
            <ul style={{ margin: 0, paddingLeft: "1.1rem", fontSize: "var(--fs-xs)", color: "var(--ink-muted)" }}>
              <li>Le statut décrit l&apos;information, jamais une personne.</li>
              <li>Une source unique ne suffit pas à corroborer un fait.</li>
              <li>Une absence de source ne prouve pas qu&apos;un fait est faux.</li>
            </ul>
            <p className="hint" style={{ margin: 0 }}>Dossier ouvert le {created}.</p>
            <Link href="/comment-ca-marche" className="btn btn-secondary" style={{ marginTop: "var(--s-2)" }}>
              Comprendre la méthode
            </Link>
          </div>
          <div style={{ marginTop: "var(--s-3)" }}>
            <Disclaimer />
          </div>
          <p className="hint" style={{ marginTop: "var(--s-3)" }}>
            Ce lien est visible par toute personne qui le possède.{" "}
            <Link href="/limites">Signaler une erreur</Link>
          </p>
        </aside>
      </div>
    </div>
  );
}
