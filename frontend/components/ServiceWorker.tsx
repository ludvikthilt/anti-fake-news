"use client";

import { useEffect } from "react";

export default function ServiceWorker() {
  useEffect(() => {
    // Localhost est un contexte sécurisé : on enregistre aussi en développement pour
    // pouvoir tester les notifications push avant la mise en ligne.
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
  }, []);
  return null;
}
