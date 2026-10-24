/**
 * Configuration lue à chaque requête : l'adresse de l'API peut changer
 * (prévisualisation Render, domaine personnalisé) sans reconstruire l'image.
 */
export const dynamic = "force-dynamic";

export function GET() {
  const api = process.env.API_URL || "";
  const body = `window.__ANTIFAKE_API__=${JSON.stringify(api)};`;
  return new Response(body, {
    headers: {
      "content-type": "application/javascript; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
