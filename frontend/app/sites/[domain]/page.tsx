"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { CertificationRow, SiteProfile } from "@/lib/types";
import CertificationPair from "@/components/CertificationPair";
import InsiderReading from "@/components/InsiderReading";
import Spinner from "@/components/Spinner";
import { ShieldCheck } from "@/components/Icon";
import styles from "@/components/ui.module.css";

const NATURE_LABELS: Record<string, string> = {
  agency: "Agence de presse",
  institution: "Institution publique",
  media: "Média d'information reconnu",
  blog: "Blog",
  social: "Réseau social",
  unknown: "Site inconnu",
};

function Progress({ label, value, total }: { label: string; value: number; total: number }) {
  const percent = total ? Math.min(Math.round((value / total) * 100), 100) : 0;
  return (
    <div style={{ minWidth: 0 }}>
      <div className="spread" style={{ gap: "var(--s-2)" }}>
        <span className="hint">{label}</span>
        <span className="hint mono">
          {value}/{total}
        </span>
      </div>
      <span
        aria-hidden
        style={{
          display: "block",
          height: 6,
          borderRadius: 99,
          background: "var(--brand-100)",
          overflow: "hidden",
          marginTop: 4,
        }}
      >
        <span
          style={{
            display: "block",
            height: "100%",
            width: `${percent}%`,
            borderRadius: 99,
            background: value >= total ? "var(--ok-fg)" : "var(--brand-500)",
          }}
        />
      </span>
    </div>
  );
}

export default function SiteDetailPage() {
  const { domain } = useParams<{ domain: string }>();
  const [site, setSite] = useState<SiteProfile | null>(null);
  const [readings, setReadings] = useState<CertificationRow[]>([]);
  const [error, setError] = useState("");
  const [readingError, setReadingError] = useState("");

  const load = useCallback(async () => {
    try {
      const [profile, rows] = await Promise.all([
        api<SiteProfile>(`/sites/${encodeURIComponent(domain)}/`, { auth: false }),
        api<CertificationRow[]>(
          `/certifications/?target_type=site&target_id=${encodeURIComponent(domain)}`,
          { auth: false },
        ),
      ]);
      setSite(profile);
      setReadings(rows);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Site introuvable.");
    }
  }, [domain]);

  useEffect(() => {
    load();
  }, [load]);

  async function retract(id: number) {
    if (!window.confirm("Retirer cette lecture ? Elle disparaîtra de la fiche du site.")) return;
    setReadingError("");
    try {
      await api(`/certifications/${id}/`, { method: "DELETE" });
      await load();
    } catch (err) {
      setReadingError(err instanceof Error ? err.message : "Le retrait n'a pas abouti.");
    }
  }

  if (error) {
    return (
      <div className="container reading">
        <p className="eyebrow">Base locale</p>
        <h1>Site introuvable</h1>
        <p className="error-text" role="alert">{error}</p>
        <p><Link href="/sites" className="btn btn-primary">Revenir aux sites</Link></p>
      </div>
    );
  }

  if (!site) {
    return (
      <div className="container reading">
        <p className="eyebrow">Base locale</p>
        <h1>Fiche du site</h1>
        <p className="muted cluster"><Spinner size={18} /> Chargement…</p>
      </div>
    );
  }

  return (
    <div className="container">
      <p className="hint" style={{ marginBottom: "var(--s-3)" }}>
        <Link href="/sites">← Sites de référence</Link>
      </p>

      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Fiche du site</p>
          <h1 style={{ margin: 0, wordBreak: "break-word" }}>{site.domain}</h1>
          {site.name && site.name !== site.domain && (
            <p className="muted" style={{ margin: "var(--s-2) 0 0" }}>{site.name}</p>
          )}
        </div>
        {site.certified ? (
          <span className="pill ok">
            <ShieldCheck size={13} /> Site certifié
          </span>
        ) : (
          <span className="pill warn">En observation</span>
        )}
      </div>

      <p className={styles.heroLead} style={{ maxWidth: "46rem" }}>
        {site.description ||
          `Fiche constituée automatiquement à partir des analyses qui ont rencontré ${site.domain}.`}
      </p>

      <div className="grid2" style={{ marginBottom: "var(--s-6)" }}>
        <div className="card card-flat">
          <p className="eyebrow" style={{ marginTop: 0 }}>Reconnaissance automatique</p>
          <p className="hint" style={{ marginTop: 0 }}>
            La certification est acquise quand les deux quotas sont atteints : corroborations
            constatées par le système et insiders distincts. Une lecture isolée ne suffit jamais ;
            chaque contestation annule une certification.
          </p>
          <div className="stack-sm">
            <Progress label="Corroborations constatées par le système" value={site.system_validations} total={site.system_quota} />
            <Progress label="Insiders certifiants (net des contestations)" value={site.insider_net} total={site.insider_quota} />
          </div>
          <p className="hint" style={{ marginBottom: 0 }}>
            {site.insider_certifications} certification(s) · {site.insider_contests} contestation(s)
            {site.certified && site.certified_at
              ? ` · reconnu le ${new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(site.certified_at))}`
              : ""}
          </p>
        </div>

        <div className="card card-flat">
          <p className="eyebrow" style={{ marginTop: 0 }}>Nature et score</p>
          <dl className="stack-sm" style={{ margin: 0 }}>
            <div>
              <dt className="hint">Nature</dt>
              <dd style={{ margin: 0, fontWeight: 600 }}>{NATURE_LABELS[site.nature] || site.nature}</dd>
            </div>
            <div>
              <dt className="hint">Score de fiabilité</dt>
              <dd style={{ margin: 0, fontWeight: 600 }}>{site.score}/100</dd>
            </div>
          </dl>
          <p className="hint" style={{ marginBottom: 0 }}>
            Un site certifié gagne un bonus de fiabilité dans les analyses à venir.
          </p>
        </div>
      </div>

      <section aria-labelledby="lectures-site" className="section" style={{ marginTop: 0 }}>
        <h2 id="lectures-site" className="sectionTitle">Lectures des insiders</h2>
        {readingError && (
          <p className="error-text" role="alert" style={{ marginBottom: "var(--s-3)" }}>{readingError}</p>
        )}
        <CertificationPair certifications={readings} onRetract={retract} />
        <div style={{ marginTop: "var(--s-4)" }}>
          <InsiderReading
            targetType="site"
            targetId={site.domain}
            readings={readings}
            onChanged={load}
          />
        </div>
      </section>
    </div>
  );
}
