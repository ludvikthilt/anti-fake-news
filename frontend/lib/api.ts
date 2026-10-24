const DEFAULT_API = "http://localhost:8000/api";

declare global {
  interface Window {
    __ANTIFAKE_API__?: string;
  }
}

/**
 * Adresse de l'API résolue à l'exécution.
 *
 * Dans le navigateur, `/runtime-config.js` injecte la valeur de la variable
 * `API_URL` du serveur : changer de domaine ne demande donc pas de reconstruire
 * l'image. Côté serveur (rendu SSR), la même variable est lue directement.
 * `NEXT_PUBLIC_API_URL` reste le repli figé au build (utile en local).
 */
export function apiBase(): string {
  if (typeof window !== "undefined") {
    return window.__ANTIFAKE_API__ || process.env.NEXT_PUBLIC_API_URL || DEFAULT_API;
  }
  return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || DEFAULT_API;
}

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "Plateforme anti-fake news";

const TOKEN_KEY = "antifake.access";
const REFRESH_KEY = "antifake.refresh";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh: string) {
  window.localStorage.setItem(TOKEN_KEY, access);
  window.localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function getStoredUser(): { email: string; name: string; role: string } | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("antifake.user");
  return raw ? JSON.parse(raw) : null;
}

export function setStoredUser(user: unknown) {
  window.localStorage.setItem("antifake.user", JSON.stringify(user));
}

export function clearUser() {
  window.localStorage.removeItem("antifake.user");
}

export async function api<T = unknown>(
  path: string,
  options: { method?: string; body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const { method = "GET", body, auth = true } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (auth && token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${apiBase()}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const detail =
      data && typeof data === "object"
        ? (data as { detail?: string; [k: string]: unknown }).detail ||
          Object.values(data as Record<string, unknown>)[0]
        : "Une erreur est survenue.";
    throw new ApiError(res.status, typeof detail === "string" ? detail : "Une erreur est survenue.");
  }
  return data as T;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}
