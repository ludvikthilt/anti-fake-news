"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Send } from "@/components/Icon";
import styles from "@/components/ui.module.css";

interface Stats {
  analyses_today: number;
  analyses_total: number;
  pending_insider_requests: number;
  certifications: number;
  quotas: { account: string; used: number; limit: number }[];
}

interface Campaign {
  id: number;
  title: string;
  channel: string;
  status: string;
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

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [channel, setChannel] = useState("email");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const loadCampaigns = useCallback(async () => {
    const rows = await api<Campaign[]>("/admin/campaigns/");
    setCampaigns(rows);
  }, []);

  useEffect(() => {
    api<Stats>("/admin/stats/")
      .then(setStats)
      .catch((e) => setError(e instanceof Error ? e.message : "Accès réservé."));
    loadCampaigns().catch(() => {});
  }, [loadCampaigns]);

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
    ["Certifications", stats.certifications],
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

      <section className="section" aria-labelledby="quotas-titre">
        <h2 id="quotas-titre" className="sectionTitle">Quotas des services</h2>
        <div className="tableWrap">
          <table className="table">
            <thead>
              <tr><th>Service</th><th>Utilisé</th><th>Limite</th></tr>
            </thead>
            <tbody>
              {stats.quotas.map((q) => (
                <tr key={q.account}>
                  <td className="mono">{q.account}</td>
                  <td>{q.used}</td>
                  <td>{q.limit || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
        La revue des demandes insider, le retrait de certifications et la suspension de comptes se font
        via l&apos;admin Django (<span className="mono">/admin/</span>).
      </p>
    </div>
  );
}
