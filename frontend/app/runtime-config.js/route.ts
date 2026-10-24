/**
 * Configuration lue à chaque requête : l'adresse de l'API peut changer
 * (prévisualisation Render, domaine personnalisé) sans reconstruire l'image.
 */
export const dynamic = "force-dynamic";

export function GET() {
  const api = process.env.API_URL || "";
  // Client OAuth public (aucun secret) : figé au build en local, fourni par
  // l'environnement en production.
  const googleClientId = process.env.GOOGLE_CLIENT_ID || process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
  const body = `window.__ANTIFAKE_API__=${JSON.stringify(api)};`
    + `window.__ANTIFAKE_GOOGLE_CLIENT_ID__=${JSON.stringify(googleClientId)};`;
  return new Response(body, {
    headers: {
      "content-type": "application/javascript; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
