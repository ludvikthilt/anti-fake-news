"use client";

import { useEffect, useState } from "react";
import { api, getStoredUser } from "@/lib/api";
import type { CertificationRow, StatusKey } from "@/lib/types";
import { Scale, ShieldCheck, Trash2 } from "./Icon";
import Spinner from "./Spinner";

const STATUS_OPTIONS: { value: StatusKey; label: string }[] = [
  { value: "corroboree", label: "Corroborée" },
  { value: "non_corroboree", label: "Non corroborée" },
  { value: "contredite", label: "Contredite" },
  { value: "indeterminee", label: "Indéterminée" },
];

interface Props {
  targetType?: "analysis" | "site";
  targetId: string;
  readings: CertificationRow[];
  onChanged: () => void;
}

export default function InsiderReading({
  targetType = "analysis",
  targetId,
  readings,
  onChanged,
}: Props) {
  const [role, setRole] = useState<string | null>(null);
  const [identity, setIdentity] = useState<{ name?: string; email?: string } | null>(null);
  const [verdict, setVerdict] = useState<"certify" | "contest">("certify");
  const [proposed, setProposed] = useState<StatusKey | "">("");
  const [comment, setComment] = useState("");
  const [source, setSource] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    setRole(stored?.role ?? null);
    setIdentity(stored ? { name: stored.name, email: stored.email } : null);
  }, []);

  const mine = identity
    ? readings.find((r) => r.insider === identity.name || r.insider === identity.email)
    : undefined;

  useEffect(() => {
    if (!mine) return;
    setVerdict(mine.verdict === "contest" ? "contest" : "certify");
    setProposed((mine.proposed_status as StatusKey) || "");
    setComment(mine.comment || "");
    setSource(mine.source_url || "");
  }, [mine?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (role !== "insider" && role !== "admin") return null;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    if (!source.trim()) {
      setError("Une source est obligatoire : sans elle, la lecture n'est pas publiable.");
      return;
    }
    setBusy(true);
    try {
      await api("/certifications/", {
        method: "POST",
        body: {
          target_type: targetType,
          target_id: targetId,
          verdict,
          proposed_status: proposed,
          comment,
          source_url: source.trim(),
        },
      });
      setMessage(mine ? "Votre lecture est mise à jour." : "Votre lecture est enregistrée et signée.");
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "La lecture n'a pas pu être enregistrée.");
    } finally {
      setBusy(false);
    }
  }

  async function retract() {
    if (!mine?.id) return;
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api(`/certifications/${mine.id}/`, { method: "DELETE" });
      setMessage("Votre lecture est retirée.");
      setComment("");
      setSource("");
      setProposed("");
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Le retrait n'a pas abouti.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card stack" onSubmit={submit} aria-labelledby="lecture-insider-titre">
      <div className="cluster" style={{ gap: "var(--s-2)" }}>
        <Scale size={18} style={{ color: "var(--brand-700)", flex: "none" }} />
        <h2 id="lecture-insider-titre" className="sectionTitle" style={{ margin: 0 }}>
          {mine
            ? targetType === "site"
              ? "Votre lecture de ce site"
              : "Votre lecture de ce dossier"
            : targetType === "site"
              ? "Statuer sur ce site"
              : "Statuer sur cette information"}
        </h2>
      </div>
      <p className="hint" style={{ margin: 0 }}>
        {targetType === "site" ? (
          <>
            Une lecture seule ne suffit jamais à reconnaître un site : plusieurs insiders
            distincts doivent le certifier, en plus des corroborations constatées par le système.
            Une contestation annule une certification.
          </>
        ) : (
          <>
            En tant qu&apos;insider, vous signez une lecture datée. Elle est prise en compte dans le
            statut proposé — un désaccord entre insiders laisse le dossier « Indéterminée ».
          </>
        )}
      </p>

      <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
        <legend className="hint" style={{ marginBottom: "var(--s-2)" }}>
          Votre appréciation
        </legend>
        <div className="cluster" style={{ gap: "var(--s-2)", flexWrap: "wrap" }}>
          <button
            type="button"
            className={`btn ${verdict === "certify" ? "btn-primary" : "btn-secondary"}`}
            aria-pressed={verdict === "certify"}
            onClick={() => setVerdict("certify")}
          >
            <ShieldCheck size={16} /> Certifier
          </button>
          <button
            type="button"
            className={`btn ${verdict === "contest" ? "btn-primary" : "btn-secondary"}`}
            aria-pressed={verdict === "contest"}
            onClick={() => setVerdict("contest")}
          >
            Contester
          </button>
        </div>
      </fieldset>

      <div className="field">
        <label htmlFor="insider-statut">Statut que vous proposez (facultatif)</label>
        <select
          id="insider-statut"
          value={proposed}
          onChange={(e) => setProposed(e.target.value as StatusKey | "")}
        >
          <option value="">Ne se prononce pas</option>
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="insider-commentaire">Motif de votre lecture</label>
        <textarea
          id="insider-commentaire"
          rows={3}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Ce que vous avez vérifié, ce qui manque, ce qui vous fait douter…"
        />
      </div>

      <div className="field">
        <label htmlFor="insider-source">Source (obligatoire)</label>
        <input
          id="insider-source"
          type="url"
          required
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="https://…"
        />
      </div>

      {error && <p className="error-text" role="alert">{error}</p>}
      {message && <p className="success-text" role="status">{message}</p>}

      <div className="cluster" style={{ flexWrap: "wrap" }}>
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? <Spinner size={16} /> : <ShieldCheck size={16} />}
          {mine ? "Mettre à jour ma lecture" : "Signer ma lecture"}
        </button>
        {mine && (
          <button className="btn btn-secondary" type="button" onClick={retract} disabled={busy}>
            <Trash2 size={15} /> Retirer
          </button>
        )}
      </div>
    </form>
  );
}
