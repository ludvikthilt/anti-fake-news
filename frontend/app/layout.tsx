import type { Metadata, Viewport } from "next";
import "../styles/globals.css";
import { APP_NAME } from "@/lib/api";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import BottomNav from "@/components/BottomNav";
import ChatPanel from "@/components/ChatPanel";
import ServiceWorker from "@/components/ServiceWorker";
import { THEME_STORAGE_KEY } from "@/lib/theme";

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — Aide à la vérification de l'information`,
    template: `%s · ${APP_NAME}`,
  },
  description:
    "Ce site aide à vérifier : il ne prouve pas qu'une information est vraie. Plateforme éducative d'aide à la vérification de l'information.",
  manifest: "/manifest.webmanifest",
  applicationName: APP_NAME,
  appleWebApp: {
    capable: true,
    title: APP_NAME,
    statusBarStyle: "default",
  },
  icons: {
    icon: [{ url: "/brand/mark.svg", type: "image/svg+xml" }],
    apple: [{ url: "/icons/icon-192.png" }],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#f5f9fc",
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var saved=localStorage.getItem(${JSON.stringify(THEME_STORAGE_KEY)});var theme=saved==="dark"||saved==="light"?saved:(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;var color=document.querySelector('meta[name="theme-color"]');if(color)color.content=theme==="dark"?"#08131b":"#f5f9fc";}catch(_){var theme=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;}})();`,
          }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
        />
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
