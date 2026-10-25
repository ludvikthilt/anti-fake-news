"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Check, Send, ShieldCheck, Trash2, X } from "@/components/Icon";
import styles from "@/components/ui.module.css";

interface QuotaRow {
  account: string;
  label: string;
  period: string;
  used: number;
  limit: number;
  remaining: number | null;
  percent: number | null;
  alerted: boolean;
}

interface Stats {
  analyses_today: number;
  analyses_total: number;
  pending_insider_requests: number;
  pending_wiki: number;
  certifications: number;
  quotas: QuotaRow[];
}

interface Campaign {
  id: number;
  title: string;
  channel: string;
  status: string;
  created_at: string;
}

interface InsiderRequestRow {
  id: number;
  user: string;
  email: string;
  motivation: string;
  status: string;
  reason: string;
  created_at: string;
}

interface PendingWikiRow {
  slug: string;
  title: string;
  content: string;
  author: string;
  review_status: string;
  created_at: string;
}

interface ReadingRow {
  id: number;
  target_type: string;
  target_id: string;
  target_label: string;
  target_url: string;
  verdict: string;
  proposed_status: string;
  insider: string;
  source_url: string;
  created_at: string;
}

const CAMPAIGN_STATUS: Record<string, string> = {
  draft: "Brouillon",
  approved: "Approuvée",
  sent: "Envoyée",
};

const STATUS_CLASS: Record<string, string> = {
  draft: "warn",
  approved: "",
  sent: "ok",
};

const CHANNEL_LABELS: Record<string, string> = {
  email: "E-mail",
  telegram: "Telegram",
  push: "Notification push",
};

const PROPOSED_LABELS: Record<string, string> = {
  corroboree: "Corroborée",
  non_corroboree: "Non corroborée",
  contredite: "Contredite",
  indeterminee: "Indéterminée",
};

function quotaTone(q: QuotaRow): string {
  if (q.percent === null) return "unk";
  if (q.percent >= 100) return "bad";
  if (q.percent >= 80) return "warn";
  return "ok";
}

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [requests, setRequests] = useState<InsiderRequestRow[]>([]);
  const [pendingWiki, setPendingWiki] = useState<PendingWikiRow[]>([]);
  const [readings, setReadings] = useState<ReadingRow[]>([]);
  const [reviewNotes, setReviewNotes] = useState<Record<string, string>>({});
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [channel, setChannel] = useState("email");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const loadStats = useCallback(async () => {
    const data = await api<Stats>("/admin/stats/");
    setStats(data);
  }, []);

  const loadCampaigns = useCallback(async () => {
    setCampaigns(await api<Campaign[]>("/admin/campaigns/"));
  }, []);

  const loadRequests = useCallback(async () => {
    setRequests(await api<InsiderRequestRow[]>("/admin/insider-requests/?status=pending"));
  }, []);

  const loadPendingWiki = useCallback(async () => {
    setPendingWiki(await api<PendingWikiRow[]>("/admin/wiki/pending/"));
  }, []);

  const loadReadings = useCallback(async () => {
    setReadings(await api<ReadingRow[]>("/admin/certifications/"));
  }, []);

  const loadAll = useCallback(async () => {
    await Promise.all([loadStats(), loadRequests(), loadPendingWiki(), loadReadings()]);
  }, [loadStats, loadRequests, loadPendingWiki, loadReadings]);

  useEffect(() => {
    loadAll().catch((e) => setError(e instanceof Error ? e.message : "Accès réservé."));
    loadCampaigns().catch(() => {});
  }, [loadAll, loadCampaigns]);

  async function run(action: () => Promise<void>, success?: string) {
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await action();
      if (success) setMessage(success);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "L'action n'a pas abouti.");
    } finally {
      setBusy(false);
    }
  }

  function decideRequest(id: number, decision: "accepted" | "rejected") {
    run(async () => {
      await api(`/admin/insider-requests/${id}/`, {
        method: "PATCH",
        body: {
          status: decision,
          reason: decision === "rejected" ? window.prompt("Motif du refus (facultatif)") || "" : "",
        },
      });
    }, decision === "accepted" ? "Demande acceptée : la personne devient insider." : "Demande refusée.");
  }

  function decideWiki(slug: string, decision: "approve" | "reject") {
    run(async () => {
      await api(`/admin/wiki/${slug}/review/`, {
        method: "POST",
        body: { decision, note: reviewNotes[slug] || "" },
      });
      setReviewNotes((notes) => ({ ...notes, [slug]: "" }));
    }, decision === "approve" ? "Fiche publiée sur le wiki." : "Fiche refusée.");
  }

  function withdrawReading(id: number) {
    if (!window.confirm("Retirer cette lecture d'insider ?")) return;
    run(async () => {
      await api(`/admin/certifications/${id}/withdraw/`, {
        method: "POST",
        body: { reason: window.prompt("Motif du retrait (facultatif)") || "" },
      });
    }, "Lecture retirée.");
  }

  async function createCampaign(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api<Campaign>("/admin/campaigns/", { method: "POST", body: { title, body, channel } });
      setTitle("");
      setBody("");
      setMessage("Campagne créée. Elle reste en brouillon jusqu'à validation.");
      await loadCampaigns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Création impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function sendCampaign(id: number) {
    setError("");
    setMessage("");
    setBusy(true);
    try {
      const res = await api<{ status: string; sent: number }>(`/admin/campaigns/${id}/send/`, { method: "POST" });
      setMessage(`Campagne envoyée : ${res.sent} envoi(s).`);
      await loadCampaigns();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Envoi impossible.");
    } finally {
      setBusy(false);
    }
  }

  if (error && !stats) {
    return (
      <div className="container reading">
        <p className="eyebrow">Pilotage</p>
        <h1>Administration</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>Cette page est réservée aux administrateurs. <Link href="/compte">Se connecter.</Link></p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="container reading">
        <p className="eyebrow">Pilotage</p>
        <h1>Administration</h1>
        <p className="muted">Chargement…</p>
      </div>
    );
  }

  const cards: [string, number][] = [
    ["Analyses aujourd'hui", stats.analyses_today],
    ["Analyses au total", stats.analyses_total],
    ["Demandes insider en attente", stats.pending_insider_requests],
    ["Fiches à valider", stats.pending_wiki],
    ["Lectures d'insiders", stats.certifications],
  ];

  return (
    <div className="container">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Pilotage</p>
          <h1 style={{ margin: 0 }}>Administration</h1>
        </div>
        <span className="pill">Accès administrateur</span>
      </div>

      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <div className="grid4">
        {cards.map(([label, value]) => (
          <div key={label} className={styles.statCard}>
            <div className={styles.statLabel}>{label}</div>
            <div className={styles.statValue}>{value}</div>
          </div>
        ))}
      </div>

      <section className="section" aria-labelledby="demandes-insider">
        <h2 id="demandes-insider" className="sectionTitle">Demandes d&apos;insider</h2>
        {requests.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Aucune demande en attente.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {requests.map((r) => (
              <li key={r.id} className="card card-flat">
                <div className="spread">
                  <span style={{ minWidth: 0 }}>
                    <strong style={{ display: "block" }}>{r.user}</strong>
                    <span className="hint">
                      {r.email} ·{" "}
                      {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short" }).format(new Date(r.created_at))}
                    </span>
                  </span>
                  <span className="cluster">
                    <button className="btn btn-primary" onClick={() => decideRequest(r.id, "accepted")} disabled={busy}>
                      <Check size={15} /> Accepter
                    </button>
                    <button className="btn btn-secondary" onClick={() => decideRequest(r.id, "rejected")} disabled={busy}>
                      <X size={15} /> Refuser
                    </button>
                  </span>
                </div>
                <p style={{ margin: "var(--s-3) 0 0", fontSize: "var(--fs-sm)" }}>{r.motivation}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section" aria-labelledby="fiches-a-valider">
        <h2 id="fiches-a-valider" className="sectionTitle">Fiches du wiki à valider</h2>
        {pendingWiki.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Aucune fiche en attente.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {pendingWiki.map((page) => (
              <li key={page.slug} className="card card-flat">
                <div className="spread">
                  <span style={{ minWidth: 0 }}>
                    <strong style={{ display: "block", color: "var(--brand-900)" }}>{page.title}</strong>
                    <span className="hint">
                      Proposée par {page.author || "un insider"} le{" "}
                      {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short" }).format(new Date(page.created_at))}
                    </span>
                  </span>
                  <span className="cluster">
                    <button className="btn btn-primary" onClick={() => decideWiki(page.slug, "approve")} disabled={busy}>
                      <Check size={15} /> Publier
                    </button>
                    <button className="btn btn-secondary" onClick={() => decideWiki(page.slug, "reject")} disabled={busy}>
                      <X size={15} /> Refuser
                    </button>
                  </span>
                </div>
                <p
                  className="hint"
                  style={{ margin: "var(--s-3) 0 0", whiteSpace: "pre-wrap", maxHeight: 120, overflow: "hidden" }}
                >
                  {page.content}
                </p>
                <div className="field" style={{ marginTop: "var(--s-3)", marginBottom: 0 }}>
                  <label htmlFor={`note-${page.slug}`}>Motif de refus (facultatif)</label>
                  <input
                    id={`note-${page.slug}`}
                    value={reviewNotes[page.slug] || ""}
                    onChange={(e) => setReviewNotes((notes) => ({ ...notes, [page.slug]: e.target.value }))}
                    placeholder="Ce qui manque pour publier…"
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section" aria-labelledby="quotas-titre">
        <h2 id="quotas-titre" className="sectionTitle">Quotas des services</h2>
        <p className="hint" style={{ marginBottom: "var(--s-3)" }}>
          Mois en cours ({stats.quotas[0]?.period || "—"}). « — » signifie qu&apos;aucun plafond
          connu n&apos;est déclaré pour ce service.
        </p>
        <div className="tableWrap">
          <table className="table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Utilisé</th>
                <th>Plafond</th>
                <th>Restant</th>
                <th>Consommation</th>
              </tr>
            </thead>
            <tbody>
              {stats.quotas.map((q) => (
                <tr key={q.account}>
                  <td>{q.label}</td>
                  <td>{q.used}</td>
                  <td>{q.limit || "—"}</td>
                  <td>
                    {q.remaining === null ? "—" : q.remaining}
                  </td>
                  <td style={{ minWidth: 160 }}>
                    {q.percent === null ? (
                      <span className="muted" style={{ fontSize: "var(--fs-xs)" }}>Non plafonné</span>
                    ) : (
                      <span className="cluster" style={{ gap: "var(--s-2)", flexWrap: "nowrap" }}>
                        <span
                          aria-hidden
                          style={{
                            display: "inline-block",
                            width: 90,
                            height: 6,
                            borderRadius: 99,
                            background: "var(--brand-100)",
                            overflow: "hidden",
                            flex: "none",
                          }}
                        >
                          <span
                            style={{
                              display: "block",
                              height: "100%",
                              width: `${q.percent}%`,
                              borderRadius: 99,
                              background:
                                q.percent >= 100
                                  ? "var(--bad-fg)"
                                  : q.percent >= 80
                                    ? "var(--warn-fg)"
                                    : "var(--ok-fg)",
                            }}
                          />
                        </span>
                        <span className={`pill ${quotaTone(q)}`}>{q.percent} %</span>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="section" aria-labelledby="lectures-insiders">
        <h2 id="lectures-insiders" className="sectionTitle">Lectures récentes des insiders</h2>
        {readings.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>
              Aucune lecture déposée.
            </p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {readings.slice(0, 10).map((r) => (
              <li key={r.id} className="card card-flat spread">
                <span style={{ minWidth: 0 }}>
                  <span className="cluster" style={{ gap: "var(--s-2)" }}>
                    <span className={`pill ${r.verdict === "certify" ? "ok" : "warn"}`}>
                      <ShieldCheck size={12} /> {r.verdict === "certify" ? "Certifie" : "Conteste"}
                    </span>
                    {r.proposed_status && (
                      <span className="pill">{PROPOSED_LABELS[r.proposed_status] || r.proposed_status}</span>
                    )}
                  </span>
                  <strong style={{ display: "block", marginTop: "var(--s-2)" }}>
                    {r.target_url ? <Link href={r.target_url}>{r.target_label}</Link> : r.target_label}
                  </strong>
                  <span className="hint">
                    {r.insider} ·{" "}
                    {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short" }).format(new Date(r.created_at))}
                  </span>
                </span>
                <button className="btn btn-secondary" onClick={() => withdrawReading(r.id)} disabled={busy}>
                  <Trash2 size={14} /> Retirer
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section" aria-labelledby="campagnes-titre">
        <h2 id="campagnes-titre" className="sectionTitle">Campagnes de sensibilisation</h2>

        <form onSubmit={createCampaign} className="card" style={{ marginBottom: "var(--s-4)" }}>
          <h3 style={{ fontSize: "var(--fs-md)" }}>Créer une campagne</h3>
          <div className="field">
            <label htmlFor="campaign-title">Titre</label>
            <input id="campaign-title" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Titre du message" />
          </div>
          <div className="field">
            <label htmlFor="campaign-body">Message</label>
            <textarea id="campaign-body" rows={4} required value={body} onChange={(e) => setBody(e.target.value)} placeholder="Texte envoyé aux abonnés…" />
          </div>
          <div className="field">
            <label htmlFor="campaign-channel">Canal</label>
            <select id="campaign-channel" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="email">E-mail</option>
              <option value="telegram">Telegram</option>
              <option value="push">Notification push (PWA)</option>
            </select>
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>Créer la campagne</button>
        </form>

        {campaigns.length === 0 ? (
          <div className="card card-flat">
            <p className="muted" style={{ margin: 0, fontSize: "var(--fs-sm)" }}>Aucune campagne pour le moment.</p>
          </div>
        ) : (
          <ul className={`${styles.listReset} stack-sm`}>
            {campaigns.map((c) => (
              <li key={c.id} className="card card-flat spread">
                <span style={{ minWidth: 0 }}>
                  <strong style={{ display: "block", color: "var(--brand-900)" }}>{c.title}</strong>
                  <span className="hint">
                    {CHANNEL_LABELS[c.channel] || c.channel} ·{" "}
                    {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short" }).format(new Date(c.created_at))}
                  </span>
                </span>
                <span className="cluster">
                  <span className={`pill ${STATUS_CLASS[c.status] || ""}`}>
                    {CAMPAIGN_STATUS[c.status] || c.status}
                  </span>
                  {c.status === "approved" && (
                    <button className="btn btn-primary" onClick={() => sendCampaign(c.id)} disabled={busy}>
                      <Send size={15} /> Envoyer
                    </button>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="hint" style={{ marginTop: "var(--s-6)" }}>
        La suspension de comptes et les actions de modération lourdes restent disponibles via
        l&apos;admin Django (<span className="mono">/admin/</span>).
      </p>
    </div>
  );
}
