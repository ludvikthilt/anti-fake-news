import type { Metadata, Viewport } from "next";
import "../styles/globals.css";
import { APP_NAME } from "@/lib/api";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import BottomNav from "@/components/BottomNav";
import ChatPanel from "@/components/ChatPanel";
import ServiceWorker from "@/components/ServiceWorker";

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — Aide à la vérification de l'information`,
    template: `%s · ${APP_NAME}`,
  },
  description:
    "Ce site aide à vérifier : il ne prouve pas qu'une information est vraie. Plateforme éducative d'aide à la vérification de l'information.",
  manifest: "/manifest.webmanifest",
  applicationName: APP_NAME,
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0B6A9E",
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        {/* Adresse de l'API fournie par le serveur au démarrage, pas au build. */}
        <script src="/runtime-config.js" />
      </head>
      <body>
        <a href="#contenu" className="skip-link">
          Aller au contenu
        </a>
        <Header />
        <main id="contenu" className="main">
          {children}
        </main>
        <Footer />
        <BottomNav />
        <ChatPanel />
        <ServiceWorker />
      </body>
    </html>
  );
}
