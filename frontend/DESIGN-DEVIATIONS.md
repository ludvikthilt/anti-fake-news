# DESIGN-DEVIATIONS.md — Écarts assumés avec DESIGN.md

Tout écart avec [ressources/design/DESIGN.md](../ressources/design/DESIGN.md) est listé ici. Les points non listés sont conformes.

1. **Polices** : DESIGN.md demande l'auto-hébergement via `next/font`. Pour éviter une requête réseau au build (environnement hors-ligne), les polices utilisent les piles système (`Poppins`/`Outfit` → fallback `system-ui`, `Inter` → fallback `system-ui`, `JetBrains Mono` → `ui-monospace`). À remplacer par `next/font` quand le build aura accès au réseau.

2. **CSS** : DESIGN.md autorise « Tailwind (ou CSS Modules) ». Choix : **CSS Modules + `tokens.css`**, sans Tailwind, pour garder le bundle initial léger et les tokens en source unique.

3. **Bibliothèque de composants** (`/dev/composants` ou Storybook) : non livrée. Les composants demandés sont bien isolés dans `frontend/components/` (`StatusBadge`, `StatusCard`, `DateOrigin`, `SourceTimeline`, `CriteriaList`, `CertificationPair`, `FactCheckCard`, `MissingModules`, `SubmitForm`, `ChatPanel`, `NatureTag`), mais sans page de démonstration dédiée.

4. **Tests d'accessibilité automatisés** (axe-core sur chaque page, contraste des deux thèmes, parcours clavier) : non livrés dans cette itération. Le contraste du thème clair respecte les valeurs du design ; le **mode sombre n'a pas été vérifié automatiquement** (avertissement repris de DESIGN.md §3).

5. **Bouton « Continuer avec Google »** : l'endpoint backend existe (`POST /auth/google/`), mais le bouton n'est pas affiché côté interface tant que les identifiants OAuth (`GOOGLE_OAUTH_*`) ne sont pas configurés. La connexion e-mail + mot de passe est fonctionnelle.

6. **Sélecteur de thème manuel** (clair/sombre/système) : les tokens sombres sont définis et suivent `prefers-color-scheme` (plus `data-theme`), mais le bouton de bascule n'est pas encore exposé dans le header.

7. **Icônes** : famille Lucide respectée, mais sous forme de SVG inline locaux (`components/Icon.tsx`) plutôt que le paquet `lucide-react`, pour éviter une dépendance supplémentaire.

8. **Docker** : volontairement différé (consigne : dockeriser uniquement après validation locale complète).
