declare global {
  interface Window {
    __ANTIFAKE_GOOGLE_CLIENT_ID__?: string;
  }
}

/**
 * Identifiant OAuth public, fourni à l'exécution par `/runtime-config.js`
 * (variable `GOOGLE_CLIENT_ID` du serveur). Repli sur la valeur figée au build
 * pour le développement local.
 */
export function googleClientId(): string {
  if (typeof window !== "undefined" && window.__ANTIFAKE_GOOGLE_CLIENT_ID__) {
    return window.__ANTIFAKE_GOOGLE_CLIENT_ID__;
  }
  return process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
}

export function googleCallbackUri() {
  return `${window.location.origin}/compte/google/callback`;
}

export function startGoogleLogin() {
  const clientId = googleClientId();
  if (!clientId) return;
  const nonce = crypto.randomUUID();
  sessionStorage.setItem("google.nonce", nonce);
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: googleCallbackUri(),
    response_type: "code",
    scope: "openid email profile",
    nonce,
    prompt: "select_account",
  });
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}
