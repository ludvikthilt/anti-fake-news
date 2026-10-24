export const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export function googleCallbackUri() {
  return `${window.location.origin}/compte/google/callback`;
}

export function startGoogleLogin() {
  const nonce = crypto.randomUUID();
  sessionStorage.setItem("google.nonce", nonce);
  const params = new URLSearchParams({
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: googleCallbackUri(),
    response_type: "code",
    scope: "openid email profile",
    nonce,
    prompt: "select_account",
  });
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}
