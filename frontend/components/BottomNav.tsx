"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Search, User } from "./Icon";
import styles from "./ui.module.css";

export default function BottomNav() {
  const path = usePathname();
  const items = [
    { href: "/", label: "Analyser", Icon: Search, active: path === "/" },
    { href: "/wiki", label: "Wiki", Icon: FileText, active: path.startsWith("/wiki") },
    { href: "/compte", label: "Compte", Icon: User, active: path.startsWith("/compte") },
  ];
  return (
    <nav className={styles.bottomNav} aria-label="Navigation mobile">
      {items.map((it) => (
        <Link key={it.href} href={it.href} data-active={it.active}>
          <it.Icon size={20} />
          {it.label}
        </Link>
      ))}
    </nav>
  );
}
