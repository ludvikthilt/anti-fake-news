"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredUser } from "@/lib/api";
import type { InsiderReviewStatus, InsiderWorkspace } from "@/lib/types";
import { BookOpen, Clipboard, FileText, Scale, ShieldCheck, Trash2 } from "@/components/Icon";
import Spinner from "@/components/Spinner";
import styles from "@/components/ui.module.css";

const REVIEW_LABELS: Record<InsiderReviewStatus, string> = {
  pending: "En attente de validation",
  approved: "Publiée",
  rejected: "Refusée",
};

const REVIEW_CLASS: Record<InsiderReviewStatus, string> = {
  pending: "warn",
  approved: "ok",
  rejected: "bad",
};

const PROPOSED_LABELS: Record<string, string> = {
  corroboree: "Corroborée",
  non_corroboree: "Non corroborée",
  contredite: "Contredite",
  indeterminee: "Indéterminée",
};

export default function InsiderPage() {
  const [role, setRole] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<InsiderWorkspace | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setRole(getStoredUser()?.role ?? null);
  }, []);

  const load = useCallback(async () => {
    try {
      const data = await api<InsiderWorkspace>("/insider/workspace/");
      setWorkspace(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Espace indisponible.");
    }
  }, []);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored && (stored.role === "insider" || stored.role === "admin")) load();
  }, [load]);

  async function submitPage(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api("/wiki/pages/", { method: "POST", body: { title, content } });
      setTitle("");
      setContent("");
      setMessage("Fiche envoyée. Elle sera publiée après validation d'un administrateur.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "L'envoi n'a pas abouti.");
    } finally {
      setBusy(false);
    }
  }

  async function retract(id: number) {
    if (!window.confirm("Retirer cette lecture ? Elle disparaîtra du dossier.")) return;
    setError("");
    setMessage("");
    try {
      await api(`/certifications/${id}/`, { method: "DELETE" });
      setMessage("Lecture retirée.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Le retrait n'a pas abouti.");
    }
  }

  if (!role || (role !== "insider" && role !== "admin")) {
    return (
      <div className="container reading">
        <p className="eyebrow">Contributeurs</p>
        <h1>Espace insider</h1>
        <p className="muted">
          Cet espace est réservé aux contributeurs validés : ils statuent sur les informations
          et proposent des fiches de référence.
        </p>
        <p className="cluster">
          <Link href="/insider/demande" className="btn btn-primary">
            Demander à devenir insider
          </Link>
          <Link href="/compte" className="btn btn-secondary">
            Se connecter
          </Link>
        </p>
      </div>
    );
  }

  if (!workspace) {
    return (
      <div className="container reading">
        <p className="eyebrow">Contributeurs</p>
        <h1>Espace insider</h1>
        {error ? (
          <p className="error-text" role="alert">{error}</p>
        ) : (
          <p className="muted cluster"><Spinner size={18} /> Chargement…</p>
        )}
      </div>
    );
  }

  return (
    <div className="container">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Contributeurs</p>
          <h1 style={{ margin: 0 }}>Espace insider</h1>
        </div>
        <span className="pill">{role === "admin" ? "Administrateur" : "Insider"}</span>
      </div>

      <p className={styles.heroLead} style={{ maxWidth: "46rem" }}>
        Vous signez des lectures sourcées sur les dossiers, et vous proposez les fiches du wiki.
        Chaque proposition est relue par un administrateur avant publication.
      </p>

      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <div className="grid3">
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Lectures signées</div>
          <div className={styles.statValue}>{workspace.counts.readings}</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Fiches en attente</div>
          <div className={styles.statValue}>{workspace.counts.pending_wiki}</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Dossiers à statuer</div>
          <div className={styles.statValue}>{workspace.counts.to_review}</div>
        </div>
      </div>

      <section className="section" aria-labelledby="proposer-fiche">
        <h2 id="proposer-fiche" className="sectionTitle">
          <BookOpen size={18} /> Proposer une fiche du wiki
        </h2>
        <form className="card stack-sm" onSubmit={submitPage}>
          <div className="field">
            <label htmlFor="fiche-titre">Titre</label>
            <input
              id="fiche-titre"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Reconnaître une image sortie de son contexte"
            />
          </div>
          <div className="field">
            <label htmlFor="fiche-contenu">Contenu</label>
            <textarea
              id="fiche-contenu"
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={"## Ce qu'il faut savoir\n\n- …\n\n## Sources\n\n- https://…"}
            />
            <span className="hint">
              Les titres s&apos;écrivent avec <span className="mono">##</span> et l&apos;accent
              est mis sur <span className="mono">**ainsi**</span>. Citez vos sources avec leur date
              de consultation.
            </span>
          </div>
          <div className="cluster">
            <button className="btn btn-primary" type="submit" disabled={busy || !title.trim()}>
              {busy ? <Spinner size={16} /> : <FileText size={16} />} Envoyer pour validation
            </button>
          </div>
        </form>
      </section>

      <section className="section" aria-labelledby="mes-fiches">
        <h2 id="mes-fiches" className="sectionTitle">Mes fiches</h2>
        {workspace.wiki_pages.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Aucune fiche proposée pour le moment.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {workspace.wiki_pages.map((page) => (
              <li key={page.slug} className="card card-flat spread">
                <span style={{ minWidth: 0 }}>
                  <strong style={{ display: "block", color: "var(--brand-900)" }}>{page.title}</strong>
                  <span className="hint">
                    {page.updated_at
                      ? `Modifiée le ${new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(page.updated_at))}`
                      : ""}
                  </span>
                  {page.review_note && (
                    <span className="hint" style={{ display: "block" }}>
                      Note de l&apos;administrateur : {page.review_note}
                    </span>
                  )}
                </span>
                <span className="cluster">
                  <span className={`pill ${REVIEW_CLASS[page.review_status]}`}>
                    {REVIEW_LABELS[page.review_status]}
                  </span>
                  {page.published && (
                    <Link href={`/wiki/${page.slug}`} className="btn btn-secondary">
                      Lire
                    </Link>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section" aria-labelledby="a-statuer">
        <h2 id="a-statuer" className="sectionTitle">
          <Clipboard size={18} /> À statuer
        </h2>
        {workspace.to_review.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Tous les dossiers récents ont reçu votre lecture.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {workspace.to_review.map((item) => (
              <li key={item.public_id} className="card card-flat spread">
                <span style={{ minWidth: 0 }}>
                  <strong style={{ display: "block" }}>Dossier #{item.public_id}</strong>
                  <span className="hint">{item.excerpt}</span>
                </span>
                <Link href={`/analyses/${item.public_id}`} className="btn btn-secondary">
                  <Scale size={15} /> Statuer
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section" aria-labelledby="mes-lectures">
        <h2 id="mes-lectures" className="sectionTitle">
          <ShieldCheck size={18} /> Mes lectures
        </h2>
        {workspace.readings.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Aucune lecture signée pour le moment. Ouvrez un dossier pour statuer.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {workspace.readings.map((reading) => (
              <li key={reading.id} className="card card-flat">
                <div className="spread">
                  <span style={{ minWidth: 0 }}>
                    <span className="cluster" style={{ gap: "var(--s-2)" }}>
                      <span className={`pill ${reading.verdict === "certify" ? "ok" : "warn"}`}>
                        {reading.verdict === "certify" ? "Certifiée" : "Contestée"}
                      </span>
                      {reading.proposed_status && (
                        <span className="pill">
                          {PROPOSED_LABELS[reading.proposed_status] || reading.proposed_status}
                        </span>
                      )}
                    </span>
                    <strong style={{ display: "block", marginTop: "var(--s-2)" }}>
                      {reading.target_url ? (
                        <Link href={reading.target_url}>{reading.target_label}</Link>
                      ) : (
                        reading.target_label
                      )}
                    </strong>
                    {reading.comment && (
                      <span className="hint" style={{ display: "block" }}>{reading.comment}</span>
                    )}
                  </span>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => retract(reading.id)}
                  >
                    <Trash2 size={14} /> Retirer
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
