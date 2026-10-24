"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
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

const STEPS = ["Extraction", "Recherche", "Dates", "Statut"];

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
      // La recherche inversée d'image (Apify) arrive après le statut : on continue
      // de rafraîchir quelques minutes pour l'afficher sans rechargement manuel.
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
      <div className="container">
        <h1>Analyse indisponible</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>
          <a href="/">Revenir à l&apos;accueil pour lancer une analyse.</a>
        </p>
      </div>
    );
  }

  if (!data || data.status === "pending" || data.status === "running") {
    return (
      <div className="container">
        <h1>Analyse en cours</h1>
        <p className="mono">#{id}</p>
        <ol aria-label="Étapes de l'analyse" style={{ paddingLeft: "var(--s-4)" }}>
          {STEPS.map((s) => (
            <li key={s} style={{ marginBottom: "var(--s-2)" }}>{s}</li>
          ))}
        </ol>
        <p>
          <span className="pulse" aria-hidden /> Vous pouvez fermer cette page. Les inscrits sont prévenus à la fin.
        </p>
        {slow && (
          <p className="banner" role="status" style={{ marginTop: "var(--s-4)" }}>
            Réveil du serveur en cours, cela peut prendre environ une minute.
          </p>
        )}
      </div>
    );
  }

  const r = data.result;
  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", gap: "var(--s-4)", flexWrap: "wrap", alignItems: "baseline" }}>
        <h1>Résultat de l&apos;analyse</h1>
        <span className="mono" style={{ fontSize: "var(--fs-sm)" }}>#{r.public_id}</span>
      </div>

      <MissingModules missing={r.missing} />
      <div style={{ marginTop: "var(--s-4)" }}>
        <StatusCard result={r} />
        <NatureTag result={r} />
      </div>

      {r.extraction?.image_pending && (
        <p className="banner" role="status" style={{ marginTop: "var(--s-4)" }}>
          Recherche inversée d&apos;image en cours : les correspondances visuelles apparaîtront ici automatiquement.
        </p>
      )}

      {r.extraction?.ocr_text && (
        <section className="card" style={{ marginTop: "var(--s-4)" }} aria-labelledby="ocr-titre">
          <h3 id="ocr-titre" style={{ fontSize: "var(--fs-md)" }}>Texte lu dans l&apos;image</h3>
          <p className="mono" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            {r.extraction.ocr_text}
          </p>
          {r.extraction.ocr_engine && (
            <p style={{ marginTop: "var(--s-2)", fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
              Moteur de lecture : {r.extraction.ocr_engine}
            </p>
          )}
        </section>
      )}

      {r.extraction && (r.extraction.title || r.extraction.author || (r.extraction.keywords && r.extraction.keywords.length > 0)) && (
        <section className="card" style={{ marginTop: "var(--s-4)" }} aria-labelledby="extraction-titre">
          <h3 id="extraction-titre" style={{ fontSize: "var(--fs-md)" }}>Éléments extraits</h3>
          {r.extraction.title && <p style={{ marginBottom: "var(--s-2)" }}><strong>Titre :</strong> {r.extraction.title}</p>}
          {r.extraction.author && <p style={{ marginBottom: "var(--s-2)" }}><strong>Auteur :</strong> {r.extraction.author}</p>}
          {r.extraction.date && (
            <p style={{ marginBottom: "var(--s-2)" }}>
              <strong>Date déclarée :</strong>{" "}
              {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(r.extraction.date))}
            </p>
          )}
          {r.extraction.keywords && r.extraction.keywords.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s-2)" }}>
              {r.extraction.keywords.map((k, i) => (
                <span key={i} className="pill">{k}</span>
              ))}
            </div>
          )}
        </section>
      )}

      {r.extraction?.image_tools && r.extraction.image_tools.length > 0 && (
        <section aria-labelledby="outils-image-titre">
          <h2 id="outils-image-titre" className="sectionTitle">Recherche inversée d'image</h2>
          <p style={{ color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
            Date de première apparition indisponible. Vous pouvez lancer la recherche vous-même :
          </p>
          <div style={{ display: "flex", gap: "var(--s-2)", flexWrap: "wrap" }}>
            {r.extraction.image_tools.map((t, i) => (
              <a key={i} className="btn btn-secondary" href={t.link} target="_blank" rel="noopener noreferrer">
                {t.title}
                <span className="sr-only">(s&apos;ouvre dans un nouvel onglet)</span>
              </a>
            ))}
          </div>
        </section>
      )}

      <section aria-labelledby="sources-titre">
        <h2 id="sources-titre" className="sectionTitle">Sources</h2>
        <SourceTimeline sources={r.sources} />
      </section>

      <section aria-labelledby="factchecks-titre">
        <h2 id="factchecks-titre" className="sectionTitle">Vérifications de faits publiées</h2>
        <FactCheckCard items={r.factchecks} />
      </section>

      <section aria-labelledby="certifications-titre">
        <h2 id="certifications-titre" className="sectionTitle">Certifications des insiders</h2>
        <CertificationPair certifications={r.certifications} />
      </section>

      <section aria-labelledby="criteres-section">
        <h2 id="criteres-section" className="sectionTitle">Critères</h2>
        <CriteriaList criteria={r.criteria} />
      </section>

      <div style={{ marginTop: "var(--s-8)" }}>
        <Disclaimer />
      </div>

      <p style={{ marginTop: "var(--s-4)", fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
        Ce lien est visible par toute personne qui le possède.{" "}
        <a href="/limites">Signaler une erreur</a>
      </p>
    </div>
  );
}
