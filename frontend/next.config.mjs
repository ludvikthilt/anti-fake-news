/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Sortie autonome réservée à l'image Docker : sous Windows, la copie des liens
  // symboliques de `standalone` échoue sans privilège de création de liens.
  output: process.env.NEXT_OUTPUT === "standalone" ? "standalone" : undefined,
};

export default nextConfig;
