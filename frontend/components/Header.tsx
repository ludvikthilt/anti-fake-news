"use client";

import { useState } from "react";
import Link from "next/link";
import { APP_NAME } from "@/lib/api";
import { Menu, X } from "./Icon";
import styles from "./ui.module.css";

export default function Header() {
  const [open, setOpen] = useState(false);
  const links = [
    { href: "/", label: "Analyser" },
    { href: "/wiki", label: "Wiki" },
    { href: "/comment-ca-marche", label: "Comment ça marche" },
    { href: "/compte", label: "Se connecter" },
  ];
  return (
    <header className={styles.header}>
      <div className={`container ${styles.headerBar}`}>
        <Link href="/" className={styles.brand}>
          <span className={styles.brandDot} aria-hidden />
          {APP_NAME}
        </Link>
        <nav className={styles.nav} aria-label="Navigation principale">
          {links.map((l) => (
            <Link key={l.href} href={l.href}>
              {l.label}
            </Link>
          ))}
        </nav>
        <button
          className={`btn btn-ghost ${styles.navToggle}`}
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={open ? "Fermer le menu" : "Ouvrir le menu"}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>
      {open && (
        <nav className={styles.mobileMenu} aria-label="Navigation mobile">
          {links.map((l) => (
            <Link key={l.href} href={l.href} onClick={() => setOpen(false)}>
              {l.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
