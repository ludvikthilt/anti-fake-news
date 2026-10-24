"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { APP_NAME } from "@/lib/api";
import { THEME_STORAGE_KEY, type Theme } from "@/lib/theme";
import { Download, MessageCircle, Moon, MoreHorizontal, Scale, Shield, Sun, User, X } from "./Icon";
import BrandMark from "./Logo";
import styles from "./ui.module.css";

const LINKS = [
  { href: "/", label: "Analyser" },
  { href: "/wiki", label: "Wiki des insiders" },
  { href: "/comment-ca-marche", label: "La méthode" },
  { href: "/historique", label: "Mon historique" },
];

const SHORTCUTS = [
  { href: "/comment-ca-marche", label: "La méthode et les statuts", Icon: Scale },
  { href: "/limites", label: "Limites & transparence", Icon: Shield },
  { href: "/insider/demande", label: "Devenir insider", Icon: User },
];

type InstallPrompt = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

export default function Header() {
  const [open, setOpen] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<InstallPrompt | null>(null);
  const [installed, setInstalled] = useState(false);
  const [installHint, setInstallHint] = useState("");
  const [darkTheme, setDarkTheme] = useState(false);
  const [themeError, setThemeError] = useState("");
  const manualTheme = useRef(false);
  const path = usePathname();

  const isActive = (href: string) =>
    href === "/" ? path === "/" : path.startsWith(href);

  // Le menu se referme dès qu'on change de page.
  useEffect(() => {
    setOpen(false);
  }, [path]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    let savedTheme: string | null = null;
    try {
      savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    } catch {
      setThemeError("Le thème système sera utilisé, car les préférences ne sont pas accessibles.");
    }
    const hasSavedTheme = savedTheme === "dark" || savedTheme === "light";
    manualTheme.current = hasSavedTheme;

    const applyTheme = (theme: Theme) => {
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
      document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#08131b" : "#f5f9fc");
      setDarkTheme(theme === "dark");
    };
    const initialTheme: Theme = savedTheme === "dark" ? "dark" : savedTheme === "light" ? "light" : media.matches ? "dark" : "light";
    applyTheme(initialTheme);

    const followSystemTheme = (event: MediaQueryListEvent) => {
      if (!manualTheme.current) applyTheme(event.matches ? "dark" : "light");
    };
    media.addEventListener("change", followSystemTheme);
    return () => media.removeEventListener("change", followSystemTheme);
  }, []);

  // Échap ferme le menu.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    setInstalled(window.matchMedia("(display-mode: standalone)").matches);
    const capture = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as InstallPrompt);
    };
    const onInstalled = () => {
      setInstalled(true);
      setInstallPrompt(null);
    };
    window.addEventListener("beforeinstallprompt", capture);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", capture);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  async function install() {
    if (installPrompt) {
      await installPrompt.prompt();
      const choice = await installPrompt.userChoice;
      if (choice.outcome === "accepted") setInstalled(true);
      setInstallPrompt(null);
      return;
    }
    setInstallHint(
      "Sur iPhone : bouton Partager, puis « Sur l'écran d'accueil ». Sur Android : menu ⋮ puis « Installer l'application ».",
    );
  }

  function toggleTheme() {
    const nextTheme: Theme = darkTheme ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    document.documentElement.style.colorScheme = nextTheme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", nextTheme === "dark" ? "#08131b" : "#f5f9fc");
    setDarkTheme(nextTheme === "dark");
    manualTheme.current = true;
    setThemeError("");
    try {
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    } catch {
      setThemeError("Le thème est appliqué, mais ne peut pas être mémorisé sur cet appareil.");
    }
  }

  const themeAction = darkTheme ? "Activer le mode clair" : "Activer le mode sombre";
  const ThemeIcon = darkTheme ? Sun : Moon;

  return (
    <header className={styles.header}>
      <div className={styles.topStrip} aria-hidden />
      <div className={`container ${styles.headerBar}`}>
        <Link href="/" className={styles.brand} aria-label={`${APP_NAME} — accueil`}>
          <BrandMark size={34} className={styles.brandMark} />
          <span className={styles.brandText}>
            <span className={styles.brandName}>{APP_NAME}</span>
            <span className={styles.brandTag}>Vérification &amp; vigilance</span>
          </span>
        </Link>

        <nav className={styles.nav} aria-label="Navigation principale">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={styles.navLink}
              data-active={isActive(l.href)}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className={styles.headerActions}>
          <button
            type="button"
            className={`${styles.iconBtn} ${styles.themeHeaderBtn}`}
            onClick={toggleTheme}
            aria-label={themeAction}
            aria-pressed={darkTheme}
            title={themeAction}
          >
            <ThemeIcon size={18} />
          </button>
          <button
            type="button"
            className={`${styles.iconBtn} ${styles.chatHeaderBtn}`}
            aria-label="Ouvrir l'assistant de vérification"
            title="Poser une question"
            onClick={() => window.dispatchEvent(new Event("antifake:chat"))}
          >
            <MessageCircle size={18} />
          </button>
          <Link
            href="/compte"
            className={`${styles.iconBtn} ${styles.accountBtn}`}
            aria-label="Mon compte"
            title="Mon compte"
          >
            <User size={18} />
          </Link>
          <button
            type="button"
            className={styles.navToggle}
            onClick={() => {
              setOpen((v) => !v);
              setInstallHint("");
            }}
            aria-expanded={open}
            aria-controls="menu-mobile"
            aria-haspopup="true"
            aria-label={open ? "Fermer le menu" : "Plus d'options"}
            title={open ? "Fermer" : "Plus d'options"}
          >
            {open ? <X size={17} /> : <MoreHorizontal size={20} />}
          </button>
        </div>
      </div>

      {open && (
        <>
          <div className={styles.menuBackdrop} onClick={() => setOpen(false)} aria-hidden />
          <div id="menu-mobile" className={styles.mobileMenu} role="group" aria-label="Plus d'options">
            <p className={styles.menuTitle}>Plus d&apos;options</p>

            <button
              type="button"
              className={styles.menuItem}
              onClick={() => {
                setOpen(false);
                window.dispatchEvent(new Event("antifake:chat"));
              }}
            >
              <span className={styles.menuItemIcon} aria-hidden>
                <MessageCircle size={16} />
              </span>
              Poser une question
            </button>

            <button
              type="button"
              className={styles.menuItem}
              onClick={toggleTheme}
              aria-label={themeAction}
              aria-pressed={darkTheme}
            >
              <span className={styles.menuItemIcon} aria-hidden>
                <ThemeIcon size={16} />
              </span>
              {themeAction}
            </button>

            {SHORTCUTS.map(({ href, label, Icon }) => (
              <Link key={href} href={href} className={styles.menuItem} data-active={isActive(href)}>
                <span className={styles.menuItemIcon} aria-hidden>
                  <Icon size={16} />
                </span>
                {label}
              </Link>
            ))}

            {!installed && (
              <>
                <div className={styles.menuDivider} />
                <button type="button" className={styles.menuItem} onClick={install}>
                  <span className={styles.menuItemIcon} aria-hidden>
                    <Download size={16} />
                  </span>
                  Installer l&apos;application
                </button>
              </>
            )}

            {installHint && <p className={styles.menuHint}>{installHint}</p>}
            {themeError && <p className={styles.menuHint} role="status">{themeError}</p>}
          </div>
        </>
      )}
    </header>
  );
}
