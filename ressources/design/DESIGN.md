# DESIGN.md — Direction artistique et UI/UX de la plateforme anti-fake news

Document de référence pour l'agent de code. À suivre à la lettre ; toute entorse doit être signalée dans la PR.
Stack cible : Next.js (TypeScript, SSR) sur Vercel. Interface 100 % en français.

> Hypothèses à valider : les teintes de marque ci-dessous sont estimées à l'œil depuis l'affiche et le logo EDUK-MÉDIA (pas de charte officielle fournie). Les remplacer par les valeurs officielles si elles existent (voir `tokens.css`). Le nom du projet est provisoire : ne jamais le coder en dur, utiliser `NEXT_PUBLIC_APP_NAME`.

---

## 1. Principes directeurs (par ordre de priorité)

1. **Aide à la vérification, jamais verdict.** Aucun élément visuel ne doit faire croire à une preuve : pas de tampon « VÉRIFIÉ », pas de gros « VRAI/FAUX », pas de jauge de 0 à 100 % mise en avant, pas de rouge criard plein écran.
2. **Tout est vérifiable en un clic.** Chaque statut, date ou score est accompagné de son critère, de son lien et de son origine. Si une donnée n'a pas d'origine, elle ne s'affiche pas.
3. **Honnêteté sur les limites.** Les modules indisponibles, quotas épuisés, analyses partielles, dates absentes sont affichés explicitement, jamais masqués ni remplacés par un spinner infini.
4. **Lisible par tous.** Jamais la couleur seule : symbole + mot + couleur. Public principal : élèves et étudiants du Mfoundi, souvent sur mobile, avec connexion limitée.
5. **Calme et pédagogique.** Ton posé, vocabulaire simple, pas d'alarmisme. Un statut concerne une information, jamais une personne.

## 2. Identité visuelle

Esprit : institutionnel-éducatif, jeune, lumineux, sobre. Héritage de l'affiche « Défions l'infox » (bleu ciel, point jaune, vert d'action, bandeau à motif géométrique) traité avec retenue.

- **Motif signature** : bandeau de losangs entrelacés (comme sur l'affiche), utilisé uniquement en liseré décoratif de 12 px en haut du header et dans le pied de page. `aria-hidden`, jamais derrière du texte.
- **Point jaune** : le « o » de « infox » est un point jaune. Reprendre ce point comme élément de marque (puce de titre, indicateur de chargement). Un seul par écran.
- **Logos** : logo EDUK-MÉDIA et mention « Projet financé par l'Union européenne » dans le pied de page de toutes les pages (obligation vraisemblable liée au financement : à confirmer auprès d'EDUK-MÉDIA). Ne pas déformer ni recolorer les logos.
- **Illustration** : style aplat vectoriel simple, personnages jeunes d'Afrique centrale, cohérents avec l'affiche. Pas d'illustrations d'IA photoréalistes. Usage limité : accueil, états vides, page d'erreur.
- **Iconographie** : une seule famille, Lucide (trait 1.75 px, coins arrondis). Pas d'emoji dans l'interface, sauf dans les messages de l'utilisateur.

## 3. Design tokens

Créer `styles/tokens.css` comme source unique. Aucune couleur ou taille en dur ailleurs.

```css
:root {
  /* Marque */
  --brand-500: #1CA7E0;   /* fonds, grands aplats, liseré. JAMAIS pour du texte sur blanc (contraste 2,74:1) */
  --brand-700: #0B6A9E;   /* texte de lien, boutons primaires (5,88:1 avec du blanc) */
  --brand-900: #0E2A3B;   /* pied de page, fonds sombres */
  --dot-yellow: #F5B700;  /* point de marque, accents ; texte dessus = --ink */
  --action-green: #1E8E5A;

  /* Neutres */
  --ink: #14202B;         /* texte principal (16,5:1 sur blanc) */
  --ink-muted: #4A5A68;   /* texte secondaire (7,1:1 sur blanc) */
  --line: #D5DEE5;
  --surface: #FFFFFF;
  --canvas: #F5F9FC;

  /* Statuts : fond / texte / bordure */
  --ok-bg: #E3F4EA;   --ok-fg: #0B5D38;   --ok-bd: #1E8E5A;
  --warn-bg: #FFF1D6; --warn-fg: #7A4B00; --warn-bd: #B26B00;
  --bad-bg: #FDE8E6;  --bad-fg: #9B1C14;  --bad-bd: #C0392B;
  --unk-bg: #ECEAFB;  --unk-fg: #4B3F9E;  --unk-bd: #6657C4;

  /* Typo */
  --font-display: "Poppins", system-ui, sans-serif;   /* titres (proche de l'affiche) */
  --font-body: "Inter", system-ui, sans-serif;        /* texte courant */
  --font-mono: ui-monospace, "JetBrains Mono", monospace; /* numéros d'analyse, URL */

  --fs-xs: 0.8125rem; --fs-sm: 0.9375rem; --fs-md: 1.0625rem;
  --fs-lg: 1.375rem; --fs-xl: 1.875rem; --fs-2xl: 2.5rem;
  --lh-body: 1.6;

  /* Espacement (base 4) */
  --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-6: 24px; --s-8: 32px; --s-12: 48px;

  --radius-sm: 8px; --radius-md: 14px; --radius-lg: 22px; --radius-pill: 999px;
  --shadow-1: 0 1px 2px rgba(20,32,43,.08), 0 2px 8px rgba(20,32,43,.06);
  --focus-ring: 0 0 0 3px #fff, 0 0 0 6px var(--brand-700);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ink: #E8F0F5; --ink-muted: #A9BAC7; --line: #2A3B48;
    --surface: #15232D; --canvas: #0F1A22; --brand-700: #5BC0EE;
    --ok-bg: #12301F; --ok-fg: #8FE0B2; --warn-bg: #3A2A08; --warn-fg: #F5C76B;
    --bad-bg: #3A1512; --bad-fg: #FFB1A8; --unk-bg: #231F45; --unk-fg: #B9B0FF;
  }
}
```

Contrastes vérifiés par calcul WCAG : texte courant ≥ 4,5:1 pour tous les couples texte/fond de statut (6,6 à 7,1), bordures de statut ≥ 3:1 sur blanc (4,1 à 5,6). **Le mode sombre n'a pas été calculé** (seul `--ink` sur `#0F1A22` l'a été : 15,3:1) : l'agent doit exécuter un contrôle de contraste automatisé sur toutes les paires sombres avant de livrer, et corriger celles sous 4,5:1.

Règle : `--brand-500` n'est jamais une couleur de texte sur fond clair. Sur `--brand-500`, le texte est `--ink` (6,0:1), pas blanc.

## 4. Typographie

- Titres : Poppins 600/700, interlignage 1,2. Texte : Inter 400/500, 1,6. Auto-héberger les polices via `next/font` (pas de requête à un CDN tiers : vie privée et performance).
- Corps ≥ 16 px sur mobile. Largeur de lecture ≤ 70 caractères.
- Numéros d'analyse, URL, hash : police mono, `overflow-wrap: anywhere`.
- Dates : format français long, `24 octobre 2026`, balise `<time datetime>`. Toujours suivie de la pastille d'origine (section 6.4).

## 5. Mise en page et navigation

- Mobile d'abord (base 360 px). Points de rupture : 640 / 960 / 1200 px. Contenu centré, max 1120 px.
- **Header** : logo + nom, liens `Analyser`, `Wiki`, `Comment ça marche`, bouton `Se connecter`. Sur mobile : barre de navigation basse à 3 entrées (Analyser, Historique/Wiki, Compte). Pas de menu burger caché pour l'action principale.
- **Pied de page** (fond `--brand-900`) : logos, liens `Confidentialité`, `Limites du service`, `Signaler une erreur`, et la phrase permanente : « Ce site aide à vérifier : il ne prouve pas qu'une information est vraie. » Cette phrase apparaît aussi, en plus petit, sous chaque résultat.
- Pages : `/` accueil+soumission · `/analyses/[id]` résultat (SSR, partageable) · `/historique` · `/wiki`, `/wiki/[slug]` · `/compte` · `/insider/demande` · `/admin` · `/comment-ca-marche` · `/limites` · pages d'erreur.

## 6. Composants clés

### 6.1 Formulaire de soumission (accueil)
- Un seul champ central, trois onglets : **Texte · Lien · Image**. L'onglet actif est annoncé (`role="tablist"`).
- Texte : zone ≤ 5 000 caractères avec compteur ; Image : glisser-déposer + bouton, JPEG/PNG/WebP, ≤ 5 Mo, ≤ 4 096 px ; erreurs en clair (« Image trop lourde : 5 Mo maximum »).
- Sous le champ, avertissement visible (pas dans une infobulle) : « Ne soumettez pas d'informations personnelles ou confidentielles. Le contenu peut être transmis à des services externes. » Lien vers la confidentialité.
- Message permanent pour les contenus non pris en charge : vidéo, audio, groupes fermés → proposer le collage manuel du texte/de l'image.
- Bouton primaire : `Analyser` (fond `--brand-700`, texte blanc). Après envoi : redirection immédiate vers `/analyses/[id]`.

### 6.2 Attente de l'analyse
- Page résultat en état « en cours » dès la réponse 202 : numéro d'analyse en mono, barre d'étapes (Extraction → Recherche → Dates → Statut) avec libellés texte, interrogation toutes les 2 s.
- Texte rassurant : « Vous pouvez fermer cette page. Les inscrits sont prévenus à la fin. » L'objectif de moins de 30 secondes est un objectif, ne pas le promettre en interface.
- **Réveil du serveur** (offre gratuite) : après 4 s sans réponse, bandeau `role="status"` : « Réveil du serveur en cours, cela peut prendre environ une minute. » Ne jamais afficher d'erreur générique pendant ce délai.
- `prefers-reduced-motion` : remplacer toute animation par un indicateur statique.

### 6.3 Bloc Statut (composant `StatusBadge` + `StatusCard`)

Quatre niveaux, toujours **icône + libellé + couleur + phrase explicative + lien « Voir les critères »**.

| Statut | Icône (Lucide) | Couleur | Phrase type |
|---|---|---|---|
| Corroborée | `check-circle-2` | ok | « Plusieurs sources indépendantes et fiables reprennent cette information, sans contradiction trouvée. » |
| Non corroborée | `minus-circle` | warn | « Des traces existent, mais trop peu de sources fiables et indépendantes. Ce n'est pas un « faux ». » |
| Contredite | `x-circle` | bad | « Une vérification de faits publiée ou plusieurs sources fiables contredisent cette information. » |
| Indéterminée | `help-circle` | unk | « Pas assez d'éléments, analyse partielle, ou désaccord entre insiders. » |

Règles :
- Taille d'une carte statut : visible sans scroll sur mobile, mais **jamais plus grande que le titre de la section « Sources »**. La mise en avant visuelle va aux sources et aux dates, pas au verdict.
- Sous chaque statut, une ligne fixe : « C'est une aide à la décision. C'est vous qui jugez, en ouvrant les sources. »
- Interdits : barre de progression, pourcentage de confiance, feu tricolore, mots « vrai » / « faux » seuls, animation de succès (confettis).
- La couleur bad est réservée au statut Contredite et aux erreurs de saisie. Ne pas l'utiliser pour des « avertissements » généraux.

### 6.4 Pastille d'origine de date (`DateOrigin`)
Quatre variantes, toujours collées à la date, jamais sans elle : **Déclarée**, **Observée**, **Métadonnée**, **Indexation**. Chaque pastille a une icône distincte, un libellé et une info-bulle accessible au clavier (et aussi au toucher : ouverture au clic, fermeture par Échap) expliquant l'origine. Pour une image sans date : bloc « Date de première apparition indisponible » + boutons pour ouvrir des moteurs d'image publics (Lens, TinEye, Yandex).

Libellé de la chronologie : « la plus ancienne trouvée », **jamais « la première »** (le dossier technique précise qu'aucune API ne garantit la première apparition).

### 6.5 Chronologie des sources (`SourceTimeline`)
- Liste verticale, de la plus ancienne à la plus récente. Chaque élément : domaine, titre, type (agence, média, institution, blog, réseau social, site inconnu), date + pastille d'origine, lien externe (`rel="noopener noreferrer"`, ouvert dans un nouvel onglet, avec icône « lien externe » et texte masqué « s'ouvre dans un nouvel onglet »).
- Le score de fiabilité numérique n'est pas affiché brut ; afficher le **type de source** et un niveau en mots. Le détail chiffré est disponible dans « Voir les critères ».
- Sur mobile : cartes empilées, pas de tableau horizontal.

### 6.6 Liste des critères (`CriteriaList`)
Accordéon ouvert par défaut sur desktop, fermé sur mobile. Cinq lignes : sources indépendantes, fiabilité des sources, vérification de faits, antériorité, certifications des insiders. Chaque ligne : icône d'état (rempli / vide / indisponible), libellé, valeur, explication d'une phrase.

### 6.7 Certifications (`CertificationPair`)
Deux mentions **visuellement séparées** : « Information certifiée » et « Site certifié ». Si les insiders sont en désaccord, afficher les deux positions côte à côte avec la source de chacun, signature et date. Ne jamais faire de moyenne ni choisir un camp.

### 6.8 Vérifications de faits publiées
Carte par vérification : organisme, verdict **tel que publié** (entre guillemets, sans le reformuler), date, lien. Message vide : « Aucune vérification de faits publiée trouvée. Cela ne signifie pas que l'information est vraie. »

### 6.9 Modules indisponibles (`MissingModules`)
Bandeau `warn` en haut du résultat si l'analyse est partielle : liste explicite (« Recherche d'image : quota mensuel atteint », « Vérifications de faits : service ne répond pas »), consigne de repli (liens manuels) et bouton `Relancer`. Le résultat reste affiché en dessous. Jamais de page d'erreur globale pour une analyse partielle.

### 6.10 Chatbot de redirection
- Panneau flottant ouvert par un bouton `Poser une question` (bas droite, au-dessus de la barre basse sur mobile).
- Réponses courtes (≤ 3 phrases) + cartes de liens issues de la base + bouton `Lancer une analyse`. Les liens sont affichés dans des cartes séparées du texte (ils sont construits par le serveur, pas par le modèle).
- Si le mode IA est indisponible (repli « stub »), afficher uniquement les liens, avec le même habillage. Ne pas annoncer de panne.
- Limite d'usage par IP atteinte : message calme avec invitation à créer un compte.
- Le chatbot ne dit jamais « vrai » ou « faux » : si la question demande un verdict, il redirige vers l'analyse.

### 6.11 Wiki des insiders
Lecture publique. Chaque affirmation porte une note de source numérotée : lien + date de consultation. Éditeur réservé aux insiders, historique des versions avec bouton `Restaurer`. Recherche par mot-clé en haut. Un paragraphe sans source est signalé par un bandeau « Source manquante » dans l'éditeur et empêche la publication.

### 6.12 Comptes, rôles, administration
- Rôles visibles par une étiquette sobre dans le compte (Visiteur n'a pas d'étiquette, Inscrit, Insider, Administrateur).
- Connexion : e-mail + mot de passe, et bouton `Continuer avec Google` (même importance visuelle, pas de mise en avant). Aucun jeton Google n'est affiché ni conservé côté interface.
- Formulaire de demande d'insider : motivation obligatoire, état de la demande (en attente / acceptée / refusée avec motif).
- Admin : tableau dense (desktop) avec actions confirmées par une boîte de dialogue ; tout retrait de certification exige un motif saisi.
- Suppression d'analyse et de compte : confirmation en deux temps, texte clair sur ce qui est supprimé.

## 7. Vocabulaire et micro-copie

Ton : tutoiement exclu, **vouvoiement**, phrases courtes, pas de jargon (« corroborée » est expliqué à chaque occurrence par sa phrase type).

- Statuts : Corroborée, Non corroborée, Contredite, Indéterminée (orthographe et accords exacts, partout).
- Mots interdits en interface : « vrai », « faux » (hors citation d'une vérification de faits publiée), « prouvé », « certifié par la plateforme ». Seuls les insiders certifient, jamais la plateforme.
- Phrases « jamais » : « Ce statut concerne l'information, jamais la personne qui l'a partagée. »
- Pédagogie EMI (issue du document scanné, correspondance à valider avec l'équipe avant implémentation) : afficher en **étiquettes secondaires distinctes du statut** la nature (Information, Opinion, Rumeur, Infox) et, pour une infox, le type de désordre (mésinformation, désinformation, malinformation). Ne pas les fusionner avec les quatre statuts. Page `/comment-ca-marche` avec le tableau pédagogique et les deux questions : « Peut-on le vérifier ? Y a-t-il une intention de nuire ? ».
- Messages d'erreur : dire ce qui s'est passé, ce que la personne peut faire, sans blâme (« Nous n'avons pas pu lire ce lien. Vous pouvez coller le texte à la main. »).
- Lien `Signaler une erreur` sur chaque résultat.

## 8. États à concevoir pour chaque écran

Chargement · vide · partiel · erreur réseau · quota/limite atteinte · hors ligne · serveur en réveil · succès. Chaque état a un texte, une icône et une action suivante. Aucun écran blanc.

## 9. Accessibilité (obligatoire, pas optionnelle)

- Cible WCAG 2.2 niveau AA. Contrastes selon la section 3.
- Navigation 100 % clavier ; `:focus-visible` avec `--focus-ring` ; lien d'évitement `Aller au contenu`.
- Zones tactiles ≥ 44×44 px.
- Un seul `h1` par page ; hiérarchie de titres sans saut ; régions `header`, `nav`, `main`, `footer`.
- Mise à jour du statut d'analyse annoncée via `aria-live="polite"` ; erreurs de formulaire reliées par `aria-describedby`.
- Aucun contenu transmis par la couleur seule ; icônes décoratives en `aria-hidden`, icônes informatives avec texte.
- Texte redimensionnable à 200 % sans perte ; pas de texte dans des images.
- Respect de `prefers-reduced-motion` et `prefers-color-scheme` ; sélecteur de thème manuel (clair/sombre/système).

## 10. Performance et réseau

Public sur mobile et connexion limitée, et front sur un hébergement gratuit :
- Pages publiques (accueil, wiki, résultat partagé) rendues côté serveur ; contenu utile sans JavaScript lourd.
- Budget visé : JS initial ≤ 150 Ko gzip sur l'accueil (objectif de conception, à mesurer avec Lighthouse CI).
- Images : `next/image`, formats modernes, miniatures seulement pour les images analysées (la plateforme ne conserve pas l'original).
- Pas de bibliothèque d'animation lourde ; transitions CSS de 150–200 ms.
- Aucun script de suivi publicitaire. Si une mesure d'audience est ajoutée, elle doit passer par la politique de confidentialité (à valider légalement, voir dossier technique).

## 11. Mouvement

Sobre, fonctionnel : apparition en fondu des résultats (150 ms), dépliage des critères (200 ms), pulsation douce du point jaune pendant l'attente. Interdit : animations de célébration, secousses sur erreur, compteurs qui défilent.

## 12. Conformité de contenu (garde-fous design)

- La phrase « Ce site aide à vérifier : il ne prouve pas qu'une information est vraie » est présente sur l'accueil, le résultat et le pied de page.
- Aucun partage social ne reprend le statut seul : l'aperçu de partage (Open Graph) affiche statut + phrase explicative + « voir les sources », jamais seulement une icône verte/rouge.
- Le lien de résultat est visible par toute personne qui le possède : afficher cet avertissement près du bouton `Copier le lien`.

## 13. Ce que l'agent de code livre

1. `styles/tokens.css` + configuration Tailwind (ou CSS Modules) lisant ces tokens.
2. Bibliothèque de composants isolés (Storybook ou page `/dev/composants`) : `StatusBadge`, `StatusCard`, `DateOrigin`, `SourceTimeline`, `CriteriaList`, `CertificationPair`, `FactCheckCard`, `MissingModules`, `SubmitForm`, `ChatPanel`, `NatureTag`.
3. Tous les états de la section 8 pour au moins : accueil, attente, résultat complet, résultat partiel, résultat Indéterminée.
4. Tests : axe-core automatisé sur chaque page, test de contraste sur les deux thèmes, test clavier du parcours soumission → résultat.
5. Un fichier `DESIGN-DEVIATIONS.md` listant tout écart assumé avec ce document.

## 14. Critères d'acceptation

- [ ] Aucun usage de `--brand-500` comme couleur de texte sur fond clair.
- [ ] Aucun statut sans icône, libellé, phrase explicative et lien vers les critères.
- [ ] Aucune date sans pastille d'origine.
- [ ] Aucune occurrence de « première apparition » présentée comme certaine (seulement « la plus ancienne trouvée »).
- [ ] Tous les cas d'échec externe produisent un résultat partiel lisible, pas une erreur globale.
- [ ] Parcours complet au clavier et au lecteur d'écran sur mobile.
- [ ] Aucun contraste inférieur à 4,5:1 (texte) ou 3:1 (composants) dans les deux thèmes.
- [ ] Liste des mots interdits (section 7) absente du code d'interface (vérifiée par grep dans la CI).
