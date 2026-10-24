"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, clearTokens, clearUser, getStoredUser, setStoredUser, setTokens } from "@/lib/api";
import { googleClientId, startGoogleLogin } from "@/lib/google";
import { disablePush, enablePush, pushSupported, type PushStatus } from "@/lib/push";
import type { UserInfo } from "@/lib/types";
import styles from "@/components/ui.module.css";

const ROLE_LABELS: Record<string, string> = {
  user: "Inscrit",
  insider: "Insider",
  admin: "Administrateur",
};

export default function ComptePage() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [tg, setTg] = useState<{ registered: boolean; available: boolean; opted_out?: boolean; username?: string; deep_link?: string } | null>(null);
  const [tgConsent, setTgConsent] = useState(false);
  const [tgMessage, setTgMessage] = useState("");
  const [tgError, setTgError] = useState("");
  interface InAppNotification { id: number; kind: string; title: string; body: string; read: boolean; created_at: string }
  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [pushStatus, setPushStatus] = useState<PushStatus | null>(null);
  const [pushOn, setPushOn] = useState(false);
  const [pushMessage, setPushMessage] = useState("");
  const [pushError, setPushError] = useState("");
  const [googleReady, setGoogleReady] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored as UserInfo);
    // Le client OAuth est fourni par /runtime-config.js : on ne l'affiche
    // qu'une fois la page hydratée, pour éviter tout écart de rendu.
    setGoogleReady(Boolean(googleClientId()));
  }, []);

  useEffect(() => {
    if (!user) return;
    api<typeof tg>("/auth/me/telegram/")
      .then(setTg)
      .catch(() => setTg(null));
    api<PushStatus>("/auth/me/push/")
      .then(setPushStatus)
      .catch(() => setPushStatus(null));
    api<InAppNotification[]>("/notifications/")
      .then(setNotifications)
      .catch(() => setNotifications([]));
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
      setTgMessage("Ouverture de Telegram… envoyez le message /start proposé, puis revenez ici.");
      // le webhook lie le compte en arrière-plan : on vérifie pendant une minute
      for (let i = 0; i < 20; i += 1) {
        await new Promise((resolve) => setTimeout(resolve, 3000));
        const status = await api<typeof tg>("/auth/me/telegram/");
        setTg(status);
        if (status?.registered) {
          setTgMessage("Telegram lié : vous recevrez le résultat de vos analyses.");
          return;
        }
      }
    } catch (err) {
      setTgError(err instanceof Error ? err.message : "Liaison Telegram impossible.");
    }
  }

  async function removeTelegram() {
    setTgError("");
    try {
      await api("/auth/me/telegram/", { method: "DELETE" });
      setTg({ registered: false, available: tg?.available ?? false, opted_out: true });
      setTgMessage("Vous ne recevrez plus de messages Telegram.");
    } catch (err) {
      setTgError(err instanceof Error ? err.message : "Désinscription impossible.");
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
      if (!pushStatus?.public_key) throw new Error("Notifications push non configurées côté serveur.");
      await enablePush(pushStatus.public_key);
      setPushOn(true);
      setPushMessage("Notifications activées pour cet appareil.");
      setPushStatus(await api<PushStatus>("/auth/me/push/"));
    } catch (err) {
      setPushError(err instanceof Error ? err.message : "Activation impossible.");
    }
  }

  async function deactivatePush() {
    setPushError("");
    setPushMessage("");
    try {
      await disablePush();
      setPushOn(false);
      setPushMessage("Notifications désactivées pour cet appareil.");
      setPushStatus(await api<PushStatus>("/auth/me/push/"));
    } catch (err) {
      setPushError(err instanceof Error ? err.message : "Désactivation impossible.");
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

  if (user) {
    return (
      <div className="container" style={{ maxWidth: "40rem" }}>
        <h1>Mon compte</h1>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "var(--s-3)", flexWrap: "wrap" }}>
            <div>
              <strong>{user.name || user.email}</strong>
              <div className="mono" style={{ fontSize: "var(--fs-sm)" }}>{user.email}</div>
            </div>
            {user.role !== "user" && (
              <span className="pill ok">{ROLE_LABELS[user.role] || user.role}</span>
            )}
          </div>
          <div style={{ marginTop: "var(--s-4)", display: "flex", gap: "var(--s-2)", flexWrap: "wrap" }}>
            <Link href="/historique" className="btn btn-secondary">Mon historique</Link>
            {user.role === "user" && <Link href="/insider/demande" className="btn btn-secondary">Devenir insider</Link>}
            {user.role === "admin" && <Link href="/admin" className="btn btn-secondary">Administration</Link>}
            {user.role === "insider" && <Link href="/wiki" className="btn btn-secondary">Wiki</Link>}
            <button
              className="btn btn-ghost"
              onClick={() => {
                clearTokens();
                clearUser();
                setUser(null);
              }}
            >
              Se déconnecter
            </button>
          </div>
        </div>

        <h2 style={{ marginTop: "var(--s-8)" }}>Notifications</h2>
        <div className="card">
          {notifications.length === 0 ? (
            <p style={{ margin: 0, color: "var(--ink-muted)" }}>Aucune notification pour le moment.</p>
          ) : (
            <>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "var(--s-3)" }}>
                {notifications.map((n) => (
                  <li
                    key={n.id}
                    style={{
                      borderLeft: n.read ? "3px solid transparent" : "3px solid var(--brand-700)",
                      paddingLeft: "var(--s-3)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: "var(--s-2)", flexWrap: "wrap" }}>
                      <strong>{n.title}</strong>
                      {!n.read && <span className="pill">nouveau</span>}
                    </div>
                    <p style={{ margin: "var(--s-1) 0", fontSize: "var(--fs-sm)" }}>{n.body}</p>
                    {!n.read && (
                      <button className="btn btn-ghost" type="button" onClick={() => markRead(n.id)}>
                        Marquer comme lu
                      </button>
                    )}
                  </li>
                ))}
              </ul>
              {notifications.some((n) => !n.read) && (
                <button className="btn btn-secondary" type="button" onClick={markAllRead} style={{ marginTop: "var(--s-3)" }}>
                  Tout marquer comme lu
                </button>
              )}
            </>
          )}
        </div>

        <h2 style={{ marginTop: "var(--s-8)" }}>Alertes Telegram</h2>
        <div className="card">
          {tg?.registered && (
            <p style={{ marginTop: 0 }}>
              Compte lié{tg.username ? <> : <strong className="mono">@{tg.username}</strong></> : null}{" "}
              <span className="pill ok">actif</span>
            </p>
          )}
          <p style={{ color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
            Facultatif et gratuit : un bot vous envoie le résultat de vos analyses et les campagnes.
            Aucun numéro de téléphone n&apos;est demandé, rien n&apos;est publié. Envoyez /stop au bot
            pour tout arrêter.
          </p>
          {!tg?.registered && (
            <>
              <label style={{ display: "flex", gap: "var(--s-2)", alignItems: "flex-start", fontSize: "var(--fs-sm)" }}>
                <input
                  type="checkbox"
                  checked={tgConsent}
                  onChange={(e) => setTgConsent(e.target.checked)}
                  style={{ width: "auto", marginTop: 2 }}
                />
                <span>
                  J&apos;accepte de recevoir des messages de la plateforme sur Telegram (résultats d&apos;analyse et
                  campagnes de sensibilisation).
                </span>
              </label>
              <div style={{ display: "flex", gap: "var(--s-2)", flexWrap: "wrap", marginTop: "var(--s-3)" }}>
                <button className="btn btn-primary" type="button" onClick={startTelegram} disabled={!tgConsent || busy || tg?.available === false}>
                  Lier mon Telegram
                </button>
              </div>
              {tg?.available === false && (
                <p style={{ fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
                  Le bot Telegram n&apos;est pas encore configuré côté serveur.
                </p>
              )}
            </>
          )}
          {tg?.registered && (
            <button className="btn btn-ghost" type="button" onClick={removeTelegram}>
              Ne plus recevoir de Telegram
            </button>
          )}
          {tgMessage && <p className="banner" role="status">{tgMessage}</p>}
          {tgError && <p className="error-text" role="alert">{tgError}</p>}
        </div>

        <h2 style={{ marginTop: "var(--s-8)" }}>Notifications dans l&apos;application</h2>
        <div className="card">
          <p style={{ marginTop: 0, color: "var(--ink-muted)", fontSize: "var(--fs-sm)" }}>
            Gratuit et illimité : la plateforme prévient cet appareil dès qu&apos;une analyse est prête,
            même quand l&apos;application est fermée. Fonctionne dans le raccourci installé
            (iPhone : iOS 16.4 ou plus récent).
          </p>
          {pushSupported() ? (
            <div style={{ display: "flex", gap: "var(--s-2)", flexWrap: "wrap" }}>
              {pushOn ? (
                <button className="btn btn-ghost" type="button" onClick={deactivatePush}>
                  Désactiver sur cet appareil
                </button>
              ) : (
                <button className="btn btn-primary" type="button" onClick={activatePush} disabled={pushStatus?.available === false}>
                  Activer les notifications
                </button>
              )}
              {pushStatus && pushStatus.count > 0 && (
                <span className="pill">{pushStatus.count} appareil(s) abonné(s)</span>
              )}
            </div>
          ) : (
            <p style={{ fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
              Ce navigateur ne prend pas en charge les notifications push. Sur iPhone, ajoutez d&apos;abord
              la plateforme à l&apos;écran d&apos;accueil.
            </p>
          )}
          {pushStatus?.available === false && (
            <p style={{ fontSize: "var(--fs-sm)", color: "var(--ink-muted)" }}>
              Les clés VAPID ne sont pas configurées côté serveur.
            </p>
          )}
          {pushMessage && <p className="banner" role="status">{pushMessage}</p>}
          {pushError && <p className="error-text" role="alert">{pushError}</p>}
        </div>

        <h2 style={{ marginTop: "var(--s-8)" }}>Supprimer mon compte</h2>
        <div className="card">
          {!confirmDelete ? (
            <button className="btn btn-secondary" onClick={() => setConfirmDelete(true)}>Supprimer mon compte</button>
          ) : (
            <>
              <p>Cette action supprime votre compte et vos analyses. Elle est définitive.</p>
              <div style={{ display: "flex", gap: "var(--s-2)" }}>
                <button className="btn btn-primary" onClick={deleteAccount} disabled={busy}>Confirmer la suppression</button>
                <button className="btn btn-ghost" onClick={() => setConfirmDelete(false)}>Annuler</button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: "30rem" }}>
      <h1>{mode === "login" ? "Se connecter" : "Créer un compte"}</h1>
      <form onSubmit={submit} className="card">
        {mode === "register" && (
          <>
            <label htmlFor="name">Nom</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" style={{ marginBottom: "var(--s-3)" }} />
          </>
        )}
        <label htmlFor="email">Adresse e-mail</label>
        <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" style={{ marginBottom: "var(--s-3)" }} />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={mode === "login" ? "current-password" : "new-password"} style={{ marginBottom: "var(--s-3)" }} />
        {error && <p className="error-text" role="alert">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: "100%" }}>
          {mode === "login" ? "Se connecter" : "Créer le compte"}
        </button>
        {googleReady && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={startGoogleLogin}
            disabled={busy}
            style={{ width: "100%", marginTop: "var(--s-2)" }}
          >
            Continuer avec Google
          </button>
        )}
        <p style={{ textAlign: "center", marginTop: "var(--s-3)", fontSize: "var(--fs-sm)" }}>
          {mode === "login" ? (
            <>Pas encore de compte ? <button type="button" className="btn-ghost" style={{ border: "none", background: "transparent", color: "var(--brand-700)" }} onClick={() => setMode("register")}>Créer un compte</button></>
          ) : (
            <>Déjà un compte ? <button type="button" className="btn-ghost" style={{ border: "none", background: "transparent", color: "var(--brand-700)" }} onClick={() => setMode("login")}>Se connecter</button></>
          )}
        </p>
      </form>
    </div>
  );
}
