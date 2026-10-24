"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, clearTokens, clearUser, getStoredUser, setStoredUser, setTokens } from "@/lib/api";
import { googleClientId, startGoogleLogin } from "@/lib/google";
import { disablePush, enablePush, pushSupported, type PushStatus } from "@/lib/push";
import type { UserInfo } from "@/lib/types";
import { Bell, Mail, ShieldCheck, Trash2 } from "@/components/Icon";
import styles from "@/components/ui.module.css";

const ROLE_LABELS: Record<string, string> = {
  user: "Inscrit",
  insider: "Insider",
  admin: "Administrateur",
};

interface InAppNotification {
  id: number;
  kind: string;
  title: string;
  body: string;
  read: boolean;
  created_at: string;
}

interface TelegramState {
  registered: boolean;
  available: boolean;
  opted_out?: boolean;
  username?: string;
  deep_link?: string;
}

export default function ComptePage() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [tg, setTg] = useState<TelegramState | null>(null);
  const [tgConsent, setTgConsent] = useState(false);
  const [tgMessage, setTgMessage] = useState("");
  const [tgError, setTgError] = useState("");
  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [pushStatus, setPushStatus] = useState<PushStatus | null>(null);
  const [pushOn, setPushOn] = useState(false);
  const [pushMessage, setPushMessage] = useState("");
  const [pushError, setPushError] = useState("");
  const [googleReady, setGoogleReady] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored as UserInfo);
    setGoogleReady(Boolean(googleClientId()));
  }, []);

  useEffect(() => {
    if (!user) return;
    api<TelegramState>("/auth/me/telegram/").then(setTg).catch(() => setTg(null));
    api<PushStatus>("/auth/me/push/").then(setPushStatus).catch(() => setPushStatus(null));
    api<InAppNotification[]>("/notifications/").then(setNotifications).catch(() => setNotifications([]));
    if (pushSupported()) {
      navigator.serviceWorker
        .getRegistration()
        .then((registration) => registration?.pushManager.getSubscription())
        .then((subscription) => setPushOn(Boolean(subscription)))
        .catch(() => setPushOn(false));
    }
  }, [user]);

  async function startTelegram() {
    setTgError("");
    setTgMessage("");
    try {
      const res = await api<{ deep_link: string }>("/auth/me/telegram/", {
        method: "POST",
        body: { consent: tgConsent },
      });
      window.open(res.deep_link, "_blank", "noopener");
      setTgMessage("Telegram s'ouvre : envoyez le message proposé, puis revenez sur cette page.");
      for (let i = 0; i < 20; i += 1) {
        await new Promise((resolve) => setTimeout(resolve, 3000));
        const status = await api<TelegramState>("/auth/me/telegram/");
        setTg(status);
        if (status?.registered) {
          setTgMessage("C'est fait : vous recevrez le résultat de vos analyses sur Telegram.");
          return;
        }
      }
    } catch (err) {
      setTgError(err instanceof Error ? err.message : "La liaison Telegram n'a pas abouti.");
    }
  }

  async function removeTelegram() {
    setTgError("");
    try {
      await api("/auth/me/telegram/", { method: "DELETE" });
      setTg({ registered: false, available: tg?.available ?? false, opted_out: true });
      setTgMessage("Vous ne recevrez plus de messages Telegram.");
    } catch (err) {
      setTgError(err instanceof Error ? err.message : "La désinscription n'a pas abouti.");
    }
  }

  async function markRead(id: number) {
    await api(`/notifications/${id}/read/`, { method: "POST" });
    setNotifications((rows) => rows.map((row) => (row.id === id ? { ...row, read: true } : row)));
  }

  async function markAllRead() {
    const unread = notifications.filter((row) => !row.read);
    await Promise.all(unread.map((row) => api(`/notifications/${row.id}/read/`, { method: "POST" })));
    setNotifications((rows) => rows.map((row) => ({ ...row, read: true })));
  }

  async function activatePush() {
    setPushError("");
    setPushMessage("");
    try {
      if (!pushStatus?.public_key) throw new Error("L'activation est momentanément indisponible.");
      await enablePush(pushStatus.public_key);
      setPushOn(true);
      setPushMessage("Notifications activées sur cet appareil.");
      setPushStatus(await api<PushStatus>("/auth/me/push/"));
    } catch (err) {
      setPushError(err instanceof Error ? err.message : "L'activation n'a pas abouti.");
    }
  }

  async function deactivatePush() {
    setPushError("");
    setPushMessage("");
    try {
      await disablePush();
      setPushOn(false);
      setPushMessage("Notifications désactivées sur cet appareil.");
      setPushStatus(await api<PushStatus>("/auth/me/push/"));
    } catch (err) {
      setPushError(err instanceof Error ? err.message : "La désactivation n'a pas abouti.");
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/register";
      const body = mode === "login" ? { email, password } : { email, password, name };
      const res = await api<{ access: string; refresh: string; user: UserInfo }>(path, { method: "POST", body, auth: false });
      setTokens(res.access, res.refresh);
      setStoredUser(res.user);
      setUser(res.user);
      setPassword("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connexion impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function deleteAccount() {
    setBusy(true);
    try {
      await api("/auth/me/", { method: "DELETE" });
      clearTokens();
      clearUser();
      setUser(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Suppression impossible.");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    clearTokens();
    clearUser();
    setUser(null);
  }

  if (user) {
    const initials = (user.name || user.email).slice(0, 2).toUpperCase();
    return (
      <div className="container reading">
        <div className={styles.pageHeader}>
          <div>
            <p className="eyebrow" style={{ marginBottom: 6 }}>Votre espace</p>
            <h1 style={{ margin: 0 }}>Mon compte</h1>
          </div>
          <span className={`pill ${user.role === "admin" ? "unk" : user.role === "insider" ? "ok" : ""}`}>
            {ROLE_LABELS[user.role] || user.role}
          </span>
        </div>

        <div className="card">
          <div className={styles.accountTop}>
            <div className={styles.profile}>
              <span className={styles.avatar} aria-hidden>{initials}</span>
              <span style={{ minWidth: 0 }}>
                <span className={styles.profileName}>{user.name || "Sans nom"}</span>
                <span className={styles.profileMail}>{user.email}</span>
              </span>
            </div>
            <span className="cluster">
              <Link href="/historique" className="btn btn-secondary">Mon historique</Link>
              {user.role === "user" && <Link href="/insider/demande" className="btn btn-secondary">Devenir insider</Link>}
              {user.role === "admin" && <Link href="/admin" className="btn btn-secondary">Administration</Link>}
              {user.role === "insider" && <Link href="/wiki" className="btn btn-secondary">Wiki</Link>}
            </span>
          </div>
          <div style={{ marginTop: "var(--s-4)", paddingTop: "var(--s-4)", borderTop: "1px solid var(--line)" }}>
            <button className="btn btn-ghost" type="button" onClick={logout}>Se déconnecter</button>
          </div>
        </div>

        {error && <p className="error-text" role="alert">{error}</p>}

        <section className="section" aria-labelledby="activite-titre">
          <div className="spread" style={{ marginBottom: "var(--s-3)" }}>
            <h2 id="activite-titre" className="sectionTitle" style={{ margin: 0 }}>Activité récente</h2>
            {notifications.some((n) => !n.read) && (
              <button className="btn btn-ghost" type="button" onClick={markAllRead}>Tout marquer comme lu</button>
            )}
          </div>
          <div className="card" style={{ padding: "var(--s-2) var(--s-4)" }}>
            {notifications.length === 0 ? (
              <p className="muted" style={{ margin: "var(--s-3) 0", fontSize: "var(--fs-sm)" }}>
                Aucune notification pour le moment. Vous serez prévenu ici et sur vos canaux
                activés dès qu&apos;une analyse est prête.
              </p>
            ) : (
              <ul className={styles.listReset}>
                {notifications.map((n) => (
                  <li
                    key={n.id}
                    style={{
                      padding: "var(--s-3) 0",
                      borderBottom: "1px solid var(--line)",
                      display: "flex",
                      gap: "var(--s-3)",
                      alignItems: "flex-start",
                    }}
                  >
                    <span
                      aria-hidden
                      style={{
                        width: 8, height: 8, borderRadius: 99, marginTop: 7, flex: "none",
                        background: n.read ? "var(--line-strong)" : "var(--brand-700)",
                      }}
                    />
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div className="spread" style={{ gap: "var(--s-2)" }}>
                        <strong style={{ fontSize: "var(--fs-sm)", color: "var(--brand-900)" }}>{n.title}</strong>
                        <span className="hint">
                          {new Intl.DateTimeFormat("fr-FR", { dateStyle: "short", timeStyle: "short" }).format(new Date(n.created_at))}
                        </span>
                      </div>
                      <p className="muted" style={{ margin: "2px 0 0", fontSize: "var(--fs-sm)" }}>{n.body}</p>
                      {!n.read && (
                        <button className="btn btn-ghost" type="button" onClick={() => markRead(n.id)} style={{ minHeight: 32, paddingLeft: 0 }}>
                          Marquer comme lu
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="section" aria-labelledby="telegram-titre">
          <h2 id="telegram-titre" className="sectionTitle">Alertes Telegram</h2>
          <div className="card">
            <div className="cluster" style={{ marginBottom: "var(--s-2)" }}>
              <span className={styles.avatar} aria-hidden style={{ width: 36, height: 36 }}><Mail size={17} /></span>
              {tg?.registered ? (
                <span>
                  Compte lié{tg.username ? <> : <strong className="mono">@{tg.username}</strong></> : null}{" "}
                  <span className="pill ok">Actif</span>
                </span>
              ) : (
                <strong style={{ fontSize: "var(--fs-sm)" }}>Recevoir le résultat sur Telegram</strong>
              )}
            </div>
            <p className="muted" style={{ fontSize: "var(--fs-sm)" }}>
              Facultatif et gratuit : un bot vous envoie le résultat de vos analyses et les campagnes
              de sensibilisation. Aucun numéro de téléphone n&apos;est demandé, rien n&apos;est publié.
              Envoyez /stop au bot pour tout arrêter.
            </p>

            {!tg?.registered && tg?.available !== false && (
              <>
                <label className="cluster" style={{ alignItems: "flex-start", gap: "var(--s-2)", fontSize: "var(--fs-sm)" }}>
                  <input type="checkbox" checked={tgConsent} onChange={(e) => setTgConsent(e.target.checked)} style={{ marginTop: 3 }} />
                  <span>
                    J&apos;accepte de recevoir des messages de la plateforme sur Telegram (résultats
                    d&apos;analyse et campagnes de sensibilisation).
                  </span>
                </label>
                <button className="btn btn-primary" type="button" onClick={startTelegram} disabled={!tgConsent || busy} style={{ marginTop: "var(--s-3)" }}>
                  Lier mon Telegram
                </button>
              </>
            )}

            {tg?.available === false && !tg?.registered && (
              <p className="banner" style={{ margin: 0 }}>
                <span>La liaison Telegram sera disponible très prochainement.</span>
              </p>
            )}

            {tg?.registered && (
              <button className="btn btn-ghost" type="button" onClick={removeTelegram} style={{ paddingLeft: 0 }}>
                Ne plus recevoir de Telegram
              </button>
            )}
            {tgMessage && <p className="success-text" role="status">{tgMessage}</p>}
            {tgError && <p className="error-text" role="alert">{tgError}</p>}
          </div>
        </section>

        <section className="section" aria-labelledby="push-titre">
          <h2 id="push-titre" className="sectionTitle">Alertes sur cet appareil</h2>
          <div className="card">
            <p className="muted" style={{ fontSize: "var(--fs-sm)" }}>
              Gratuit et illimité : la plateforme prévient cet appareil dès qu&apos;une analyse est
              prête, même quand l&apos;application est fermée. Fonctionne dans le raccourci installé
              (iPhone : iOS 16.4 ou plus récent).
            </p>
            {pushSupported() ? (
              <div className="cluster">
                {pushOn ? (
                  <button className="btn btn-secondary" type="button" onClick={deactivatePush}>
                    <Bell size={16} /> Désactiver sur cet appareil
                  </button>
                ) : (
                  <button className="btn btn-primary" type="button" onClick={activatePush} disabled={pushStatus?.available === false}>
                    <Bell size={16} /> Activer les notifications
                  </button>
                )}
                {pushStatus && pushStatus.count > 0 && (
                  <span className="pill">{pushStatus.count} appareil(s) abonné(s)</span>
                )}
              </div>
            ) : (
              <p className="hint" style={{ margin: 0 }}>
                Ce navigateur ne prend pas en charge les notifications. Sur iPhone, ajoutez
                d&apos;abord la plateforme à l&apos;écran d&apos;accueil.
              </p>
            )}
            {pushStatus?.available === false && pushSupported() && (
              <p className="hint" style={{ margin: "var(--s-2) 0 0" }}>
                L&apos;activation des notifications n&apos;est pas disponible pour le moment.
              </p>
            )}
            {pushMessage && <p className="success-text" role="status">{pushMessage}</p>}
            {pushError && <p className="error-text" role="alert">{pushError}</p>}
          </div>
        </section>

        <section className="section" aria-labelledby="suppression-titre">
          <h2 id="suppression-titre" className="sectionTitle">Supprimer mon compte</h2>
          <div className="card">
            {!confirmDelete ? (
              <>
                <p className="muted" style={{ fontSize: "var(--fs-sm)" }}>
                  Vous pouvez quitter la plateforme à tout moment : votre compte, vos analyses et
                  vos abonnements seront supprimés.
                </p>
                <button className="btn btn-danger" type="button" onClick={() => setConfirmDelete(true)}>
                  <Trash2 size={16} /> Supprimer mon compte
                </button>
              </>
            ) : (
              <>
                <p style={{ fontSize: "var(--fs-sm)" }}>
                  <strong>Cette action est définitive.</strong> Votre compte, votre historique et vos
                  notifications seront effacés.
                </p>
                <div className="cluster">
                  <button className="btn btn-danger" type="button" onClick={deleteAccount} disabled={busy}>
                    Confirmer la suppression
                  </button>
                  <button className="btn btn-ghost" type="button" onClick={() => setConfirmDelete(false)}>Annuler</button>
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="container">
      <div className={styles.authWrap}>
        <div className={`card card-accent ${styles.authCard}`} style={{ padding: "var(--s-5)", marginTop: "var(--s-4)" }}>
          <p className="eyebrow" style={{ marginBottom: 6 }}>Accès</p>
          <h1 className={styles.authTitle} style={{ fontSize: "var(--fs-2xl)" }}>
            {mode === "login" ? "Se connecter" : "Créer un compte"}
          </h1>
          <p className={styles.authLead}>
            {mode === "login"
              ? "Retrouvez votre historique et recevez le résultat de vos analyses."
              : "Un compte gratuit pour suivre vos dossiers et recevoir une alerte à la fin d'une analyse."}
          </p>

          {googleReady && (
            <>
              <button type="button" className={`btn btn-secondary ${styles.googleBtn}`} onClick={startGoogleLogin} disabled={busy}>
                <span aria-hidden style={{ fontWeight: 700, color: "#4285F4" }}>G</span>
                Continuer avec Google
              </button>
              <div className={styles.divider}>ou par e-mail</div>
            </>
          )}

          <form onSubmit={submit}>
            {mode === "register" && (
              <div className="field">
                <label htmlFor="name">Nom</label>
                <input id="name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" placeholder="Votre nom" />
              </div>
            )}
            <div className="field">
              <label htmlFor="email">Adresse e-mail</label>
              <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="vous@exemple.cm" />
            </div>
            <div className="field">
              <label htmlFor="password">Mot de passe</label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                placeholder="8 caractères minimum"
              />
            </div>
            {error && <p className="error-text" role="alert">{error}</p>}
            <button className="btn btn-primary btn-block" type="submit" disabled={busy} style={{ marginTop: "var(--s-2)" }}>
              {mode === "login" ? "Se connecter" : "Créer le compte"}
            </button>
          </form>

          <p className={styles.authSwitch}>
            {mode === "login" ? (
              <>Pas encore de compte ?{" "}
                <button type="button" onClick={() => { setMode("register"); setError(""); }}>Créer un compte</button>
              </>
            ) : (
              <>Déjà un compte ?{" "}
                <button type="button" onClick={() => { setMode("login"); setError(""); }}>Se connecter</button>
              </>
            )}
          </p>
        </div>

        <p className="hint" style={{ textAlign: "center", marginTop: "var(--s-4)" }}>
          <ShieldCheck size={13} style={{ verticalAlign: "-2px", marginRight: 4 }} />
          Aucune donnée revendue, aucun suivi publicitaire.
        </p>
      </div>
    </div>
  );
}
