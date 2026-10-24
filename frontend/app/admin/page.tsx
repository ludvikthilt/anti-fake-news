"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
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
      setMessage("Campagne créée (brouillon).");
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
      <div className="container">
        <h1>Administration</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>Cette page est réservée aux administrateurs. <Link href="/compte">Se connecter.</Link></p>
      </div>
    );
  }

  if (!stats) {
    return <div className="container"><h1>Administration</h1><p>Chargement…</p></div>;
  }

  return (
    <div className="container">
      <h1>Administration</h1>
      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <div className="grid2">
        <div className="card"><strong>Analyses aujourd&apos;hui</strong><div style={{ fontSize: "var(--fs-xl)" }}>{stats.analyses_today}</div></div>
        <div className="card"><strong>Analyses au total</strong><div style={{ fontSize: "var(--fs-xl)" }}>{stats.analyses_total}</div></div>
        <div className="card"><strong>Demandes insider en attente</strong><div style={{ fontSize: "var(--fs-xl)" }}>{stats.pending_insider_requests}</div></div>
        <div className="card"><strong>Certifications</strong><div style={{ fontSize: "var(--fs-xl)" }}>{stats.certifications}</div></div>
      </div>

      <h2 style={{ marginTop: "var(--s-8)" }}>Quotas des fournisseurs</h2>
      <div className="card" style={{ overflowX: "auto" }}>
        <table className={styles.table}>
          <thead>
            <tr><th>Compte</th><th>Utilisé</th><th>Limite</th></tr>
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

      <h2 style={{ marginTop: "var(--s-8)" }}>Campagnes de sensibilisation</h2>
      <form onSubmit={createCampaign} className="card" style={{ marginBottom: "var(--s-4)" }}>
        <label htmlFor="campaign-title">Titre</label>
        <input id="campaign-title" required value={title} onChange={(e) => setTitle(e.target.value)} style={{ marginBottom: "var(--s-3)" }} />
        <label htmlFor="campaign-body">Corps (HTML autorisé)</label>
        <textarea id="campaign-body" rows={4} required value={body} onChange={(e) => setBody(e.target.value)} style={{ marginBottom: "var(--s-3)" }} />
        <label htmlFor="campaign-channel">Canal</label>
        <select id="campaign-channel" value={channel} onChange={(e) => setChannel(e.target.value)} style={{ marginBottom: "var(--s-3)" }}>
          <option value="email">E-mail</option>
          <option value="telegram">Telegram</option>
          <option value="push">Notification push (PWA)</option>
        </select>
        <button className="btn btn-primary" type="submit" disabled={busy}>Créer la campagne</button>
      </form>

      {campaigns.length === 0 ? (
        <p>Aucune campagne pour le moment.</p>
      ) : (
        <div className="card" style={{ overflowX: "auto" }}>
          <table className={styles.table}>
            <thead>
              <tr><th>Titre</th><th>Canal</th><th>Statut</th><th>Action</th></tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <tr key={c.id}>
                  <td>{c.title}</td>
                  <td>{CHANNEL_LABELS[c.channel] || c.channel}</td>
                  <td>{CAMPAIGN_STATUS[c.status] || c.status}</td>
                  <td>
                    {c.status === "approved" && (
                      <button className="btn btn-secondary" onClick={() => sendCampaign(c.id)} disabled={busy}>
                        Envoyer
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p style={{ marginTop: "var(--s-4)" }}>
        La revue des demandes insider, le retrait de certifications et la suspension de comptes se font via l&apos;API ou l&apos;admin Django (<span className="mono">/admin/</span>).
      </p>
    </div>
  );
}
