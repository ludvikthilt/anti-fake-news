"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, Clock, Search, User } from "./Icon";
import styles from "./ui.module.css";

export default function BottomNav() {
  const path = usePathname();
  const items = [
    { href: "/", label: "Analyser", Icon: Search, active: path === "/" },
    { href: "/wiki", label: "Wiki", Icon: BookOpen, active: path.startsWith("/wiki") },
    { href: "/historique", label: "Historique", Icon: Clock, active: path.startsWith("/historique") || path.startsWith("/analyses") },
    { href: "/compte", label: "Compte", Icon: User, active: path.startsWith("/compte") },
  ];
  return (
    <nav className={styles.bottomNav} aria-label="Navigation rapide">
      {items.map((it) => (
        <Link key={it.href} href={it.href} data-active={it.active} aria-current={it.active ? "page" : undefined}>
          <it.Icon size={21} />
          {it.label}
        </Link>
      ))}
    </nav>
  );
}
