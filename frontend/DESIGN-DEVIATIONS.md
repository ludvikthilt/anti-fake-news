# DESIGN-DEVIATIONS.md — écarts assumés avec le système de design

Référence : [ressources/design/DESIGN.md](../ressources/design/DESIGN.md) et les maquettes
`stitch_plateforme_anti_infox_eduk_media`.

## Conforme

- Palette complète : `#0E2A3B`, `#0B6A9E`, `#1CA7E0`, `#F5B700`, canvas `#F5F9FC`, encre `#14202B`,
  ligne `#D5DEE5`, statuts `ok / warn / bad / unk` avec leurs couples fond/texte/bordure.
- Typographie : Outfit pour les titres, Inter pour la lecture, JetBrains Mono pour les identifiants,
  dates, domaines et données forensiques.
- Grille : conteneur 1200 px, gouttières 24 px (16 px sur mobile), mise en page à une colonne
  sous 1024 px, barre latérale collante sur le dossier d'analyse.
- Formes : rayons 4 px (boutons, champs), 8 px (cartes), 12 px (console, modales, héros) ;
  pastilles en capsule.
- Élévation : bords 1 px et ombres très discrètes ; liseré de 3 px en `--brand-500` sur les
  cartes de premier niveau, barre de 4 px `--dot-yellow` pour l'avertissement méthodologique.
- Composants : boutons primaire/secondaire/fantôme, quatre badges de statut avec icône,
  pastilles d'origine de date, bandeau obligatoire, carte de dossier.
- Navigation mobile à quatre onglets, zone sûre (`env(safe-area-inset-bottom)`) respectée,
  cibles tactiles ≥ 44 px, installation en raccourci (manifeste + service worker).
- Le vocabulaire du dossier est conservé : corroborée, non corroborée, contredite, indéterminée,
  nature (information, opinion, rumeur, infox), mésinformation/désinformation/malinformation,
  origine de date (déclarée, observée, métadonnée, indexation).

## Écarts

1. **Polices** : chargées via `<link>` Google Fonts avec `display=swap` et repli système, plutôt
   que `next/font` auto-hébergé. Le build reste hors-ligne ; le rendu reste conforme.
2. **CSS** : CSS Modules + variables, sans Tailwind (le système autorise l'un ou l'autre).
3. **Thème** : le thème système s'applique par défaut ; un bouton permet de basculer manuellement
   entre clair et sombre, et le choix manuel est conservé sur l'appareil. Les contrastes du thème
   sombre ne sont pas encore couverts par un contrôle automatisé.
4. **Bibliothèque de composants** : pas de Storybook ni de route `/dev/composants` ; les
   composants sont isolés dans `frontend/components/`.
5. **Icônes** : SVG inline locaux (famille proche de Lucide), sans dépendance `lucide-react`.
6. **Tests d'accessibilité automatisés** (axe-core) : non branchés. Contrastes calculés à la
   main sur les couples du design (AAA pour le texte principal).
7. **Images des maquettes** : les photographies d'illustration et le logo du concours EDUK-MÉDIA
   ne sont pas repris ; la marque vectorielle InfoxVerify (bouclier + coche) est utilisée à la place.
8. **Docker** : différé, conformément à la consigne (validation locale complète d'abord).
9. **Relief des commandes** : les boutons, onglets, navigations et commandes de dépôt utilisent des
   reflets translucides, un relief tactile et de légères animations inspirés du liquid glass. Les
   cartes de contenu gardent les surfaces planes et les bordures discrètes prévues par le système ;
   le contraste reste piloté par les jetons de thème et les mouvements respectent `prefers-reduced-motion`.
10. **Motif de fond** : une trame répétée de losanges fins reprend le motif géométrique indiqué dans
    les ressources de design, avec une opacité basse et une couleur dérivée du thème.
