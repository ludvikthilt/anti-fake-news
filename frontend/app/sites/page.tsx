import type { Metadata } from "next";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import type { SiteProfile } from "@/lib/types";
import { Link as LinkIcon, Search, ShieldCheck } from "@/components/Icon";
import styles from "@/components/ui.module.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Sites de référence" };

const NATURE_LABELS: Record<string, string> = {
  agency: "Agence de presse",
  institution: "Institution publique",
  media: "Média d'information reconnu",
  blog: "Blog",
  social: "Réseau social",
  unknown: "Site inconnu",
};

async function getSites(q: string): Promise<SiteProfile[]> {
  const res = await fetch(`${API_URL}/sites/?q=${encodeURIComponent(q)}`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function SitesPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q: qParam } = await searchParams;
  const q = qParam || "";
  const sites = await getSites(q);
  const systemQuota = sites[0]?.system_quota ?? 5;
  const insiderQuota = sites[0]?.insider_quota ?? 3;

  return (
    <div className="container">
      <div className={styles.pageHeader}>
        <div>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Base locale</p>
          <h1 style={{ margin: 0 }}>Sites de référence</h1>
        </div>
        <span className="pill">{sites.length} fiche{sites.length > 1 ? "s" : ""}</span>
      </div>

      <p className={styles.heroLead} style={{ maxWidth: "46rem" }}>
        La plateforme garde la trace des sites rencontrés. Un site devient{" "}
        <strong>certifié automatiquement</strong> lorsque le système a constaté assez de
        corroborations et que plusieurs insiders distincts l&apos;ont certifié. Une lecture isolée
        ne suffit jamais, et une contestation annule une certification.
      </p>

      <p className="hint" style={{ marginBottom: "var(--s-4)" }}>
        Seuils actuels : {systemQuota} corroborations système et {insiderQuota} insiders
        certifiants. Ils sont réglables par l&apos;exploitant.
      </p>

      <form method="get" action="/sites" className="card card-flat" style={{ marginBottom: "var(--s-5)" }}>
        <label htmlFor="sites-q" className="field" style={{ marginBottom: 0 }}>
          <span className="hint">Rechercher un domaine</span>
          <span className="cluster" style={{ gap: "var(--s-2)", flexWrap: "nowrap" }}>
            <span style={{ position: "relative", flex: 1 }}>
              <Search
                size={16}
                style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--ink-muted)" }}
              />
              <input
                id="sites-q"
                type="search"
                name="q"
                defaultValue={q}
                placeholder="crtv.cm, bbc.com…"
                style={{ paddingLeft: 36 }}
              />
            </span>
            <button className="btn btn-primary" type="submit">Rechercher</button>
          </span>
        </label>
      </form>

      {sites.length === 0 ? (
        <div className="card card-flat center" style={{ padding: "var(--s-10) var(--s-4)" }}>
          <LinkIcon size={32} style={{ color: "var(--brand-500)" }} />
          <h2 style={{ fontSize: "var(--fs-lg)", marginTop: "var(--s-3)" }}>Aucun site trouvé</h2>
          <p className="muted" style={{ fontSize: "var(--fs-sm)", margin: 0 }}>
            {q
              ? "Essayez un autre domaine."
              : "Les sites apparaissent au fil des analyses, à mesure qu'ils sont rencontrés."}
          </p>
        </div>
      ) : (
        <ul className={`${styles.listReset} stack-sm`}>
          {sites.map((site) => (
            <li key={site.domain}>
              <Link href={`/sites/${encodeURIComponent(site.domain)}`} className={styles.linkCard}>
                <span style={{ minWidth: 0 }}>
                  <span className="cluster" style={{ gap: "var(--s-2)" }}>
                    <span className={styles.linkCardTitle}>{site.domain}</span>
                    {site.certified ? (
                      <span className="pill ok">
                        <ShieldCheck size={12} /> Site certifié
                      </span>
                    ) : (
                      <span className="pill warn">En observation</span>
                    )}
                  </span>
                  <span className="hint" style={{ display: "block", marginTop: 4 }}>
                    {NATURE_LABELS[site.nature] || site.nature}
                    {site.name && site.name !== site.domain ? ` · ${site.name}` : ""}
                  </span>
                  <span className="hint" style={{ display: "block" }}>
                    Corroborations système : {site.system_validations}/{site.system_quota}
                    {" · "}
                    Insiders certifiants : {site.insider_net}/{site.insider_quota}
                    {site.insider_contests > 0 ? ` (${site.insider_contests} contestation(s))` : ""}
                  </span>
                </span>
                <span aria-hidden style={{ color: "var(--brand-700)" }}>→</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
