# Plateforme anti-fake news — Synthèse de compréhension

> Synthèse établie à partir de : `Presentation_Plateforme_anti-fake_news.pdf`, `Communiqué ralonge délai-fusionné (1).pdf`, `Scanned_20261024_111409.pdf`, `dossier-technique-v1.1.pdf`, `Dossier_technique_Plateforme_anti-fake_news-1.pdf`, `recapitulatif.pdf`.

## 1. Contexte et ambition

Le projet est porté par **EDUK-MEDIA**, Association camerounaise d'éducation aux médias (Yaoundé), avec le soutien de l'Union européenne, dans le cadre de la **Semaine mondiale de l'Éducation aux Médias et à l'Information (EMI) 2026** et du concours **« Défions l'infox »**.

- Cible : élèves et étudiants du département du Mfoundi (Yaoundé, Cameroun).
- Trois catégories de production : **Théâtre (sketch)**, **Dessin**, **Solution numérique**.
- La **plateforme anti-fake news est la « solution numérique »** du concours : un outil qui utilise/intègre l'IA pour lutter contre la désinformation.
- Principe pédagogique porté par le concours : *« comprendre l'information, apprendre à la vérifier, puis créer pour sensibiliser les autres »*.

## 2. La philosophie du projet

La promesse de la plateforme tient en une phrase : **« Savoir d'où vient une information, et quand elle est apparue en ligne. »**

Ce qu'elle est (et n'est pas) :

- Elle **ne prouve pas qu'une information est vraie** ; c'est une **aide à la vérification**.
- Elle montre des **sources**, des **dates** et des **critères** pour que l'utilisateur juge lui-même.
- Elle affiche un **statut en niveaux** (jamais « vrai » ou « faux » absolu), toujours accompagné de ses critères et de ses liens.
- Elle s'appuie sur des **humains** : des « insiders » (contributeurs validés) certifient ou contestent des informations et des sites, toujours avec une source obligatoire.
- Avertissement permanent : *« Ce site aide à vérifier : il ne prouve pas qu'une information est vraie. »*

Valeurs clés : transparence (chaque date porte son origine, chaque statut est explicable ligne par ligne), humilité (aide à la décision, pas preuve), fiabilité humaine (certifications tracées et signées).

## 3. Le produit (MVP)

**Entrées acceptées** : texte (≤ 5 000 caractères), image (≤ 5 Mo, JPEG/PNG/WebP, ≤ 4 096 px), lien de post ou d'article. Pas de vidéo ni d'audio, pas de contenus privés.

**Déroulé en 3 étapes** :
1. **Soumettre** → numéro d'analyse immédiat (réponse < 1 s).
2. **Patienter** → analyse en arrière-plan (objectif < 30 s) ; le résultat s'affiche immédiatement si déjà calculé.
3. **Lire le résultat** → statut, critères, chronologie des sources, vérifications de faits.

**Contenu d'un résultat** :
- statut + phrase de synthèse ;
- critères : nombre de sources indépendantes, fiabilité des sources, existence d'une vérification de faits, antériorité de la première apparition, certifications des insiders ;
- chronologie des sources (plus ancienne → plus récente), avec lien et **origine de la date** (déclarée / observée / métadonnée / indexation) ;
- vérifications de faits déjà publiées ;
- deux mentions séparées : **« information certifiée »** et **« site certifié »** ;
- **modules indisponibles** (service externe en échec ou quota épuisé) ;
- liens de résultat partageables.

**Rôles** :
- **Visiteur** : analyser, lire le résultat, wiki, chatbot (limite par IP).
- **Inscrit** : + historique, notifications, suppression des données.
- **Insider** : + certifier/contester une information ou un site (source obligatoire), écrire le wiki.
- **Administrateur** : valider les demandes d'insider, retirer une certification abusive, suspendre un compte.

**Autres composants** : un **chatbot de redirection** (réponse courte, liens issus de la base, invite à lancer une analyse) et un **wiki public des insiders** (chaque affirmation sourcée : URL + date de consultation, versions conservées).

**Notifications** : dans l'application, par e-mail (Brevo) et WhatsApp (API Cloud Meta — uniquement dans la fenêtre gratuite de 24 h ouverte par l'utilisateur).

**Limites assumées du MVP** : pas de vidéo/audio, contenus privés non analysés, lecture automatique refusée sur certains réseaux sociaux, recherche d'image plafonnée par quota, serveur gratuit qui s'endort après 15 minutes (« réveil du serveur en cours »).

## 4. Le vocabulaire des statuts (à partir du document scanné)

### 4.1 Statuts actuels du moteur (module M6 « Fiabilité »)

Le dossier technique propose 4 niveaux, calculés à partir des sources et des certifications :

| Statut | Symbole | Règle de calcul |
|---|---|---|
| **Corroborée** | ✓ | Aucune contradiction et ≥ 2 sources indépendantes de score ≥ 70 reprenant la phrase exacte, ou une vérification de faits « vrai ». |
| **Non corroborée** | - | Des sources existent, mais moins de 2 sources fiables indépendantes. |
| **Contredite** | ✗ | ≥ 1 vérification de faits « faux/trompeur », ou verdict net « contesté » des insiders sans désaccord. |
| **Indéterminée** | ? | Aucun résultat exploitable, analyse partielle sur un module essentiel, ou insiders en désaccord. |

Scores de fiabilité des sources (base 0–100) : agence de presse / institution publique 90/85, média reconnu 80, blog 40, réseau social 30, site inconnu 20.

### 4.2 Vocabulaire issu du document scanné (fiches EMI « Défions l'infox »)

Le document scanné contient trois grilles de vocabulaire que le projet souhaite réutiliser comme **statuts des informations après analyse** :

**A. Nature du contenu** (distinguer avant de juger) :

| Terme | Définition | Repérage |
|---|---|---|
| **Information** | Fait vérifié, source et daté, confirmé par d'autres sources fiables. | Auteur, date, lieu et sources identifiés. |
| **Opinion** | Point de vue personnel, ni vrai ni faux. | « je pense que », « à mon avis », adjectifs de jugement. |
| **Rumeur** | Information non vérifiée qui circule, source introuvable. | « on dit que », « il paraît ». |
| **Infox** | Information fausse ou trompeuse présentée comme vraie. | Preuve absente, émotion forte, image/chiffre sorti de son contexte. |

**B. Désordres informationnels** (croisement vrai/faux × intention de nuire) :

| Terme | Contenu | Intention de nuire |
|---|---|---|
| **Mésinformation** | Faux | Non (erreur de bonne foi) |
| **Désinformation** | Faux | Oui (inventée pour tromper) |
| **Malinformation** | Vrai | Oui (information privée dévoilée pour nuire) |

Deux questions pour s'y retrouver : **1. Peut-on le vérifier ? 2. Y a-t-il une intention de nuire ?**

**C. Verdict de la check-list** (par nombre de doutes sur 6 points de vérification) :

| Doutes | Verdict | Comportement |
|---|---|---|
| 0 doute | **Paraît fiable** | Utilisable. |
| 1 doute | **Prudence** | Vérifier avant d'utiliser ou de partager. |
| 2 doutes ou plus | **Forte probabilité de manipulation** | Ne pas partager, poursuivre les recherches. |

### 4.3 Correspondance proposée (à valider)

Lecture croisée entre le vocabulaire pédagogique du scanné et les 4 niveaux du moteur :

| Terme du scanné | Sens | Correspondance naturelle avec le moteur |
|---|---|---|
| Information | fait vérifié et sourcé | **Corroborée** |
| Rumeur | non vérifié, source introuvable | **Non corroborée** ou **Indéterminée** |
| Infox / Désinformation | faux, contredit | **Contredite** |
| Opinion | jugement subjectif | hors périmètre → à labelliser « Opinion » sans score |
| Paraît fiable | 0 doute | **Corroborée** |
| Prudence | 1 doute | **Non corroborée** / **Indéterminée** |
| Forte probabilité de manipulation | 2+ doutes | **Contredite** |

Piste d'articulation : conserver les 4 niveaux de **corroboration** (traces/sources), et y adjoindre une **nature** (Information / Opinion / Rumeur / Infox) ainsi que, lorsqu'une infox est détectée, son **type de désordre** (mésinformation / désinformation / malinformation) selon l'intention détectée. Ce point reste une proposition de lecture à valider.

## 5. Architecture technique

**Stack** :

| Couche | Technologie | Rôle |
|---|---|---|
| Front | Next.js (TypeScript), SSR pour les pages publiques, Vercel Hobby (non commercial) | Interface française, pages résultat partageables, wiki, espace utilisateur, admin |
| API | Django + Django REST Framework + Gunicorn, Render (offre gratuite) | Auth, rôles, limitation de débit, orchestration des analyses, cache |
| Tâches | Threads dans le processus web (2 analyses simultanées max, 512 Mo), file en mémoire | Exécuter les analyses sans bloquer la réponse initiale |
| Base | PostgreSQL sur Neon, extensions `vector` (pgvector) et `unaccent` | Données métier, recherche plein texte (tsvector), vecteurs, cache, quotas, journal |
| Services externes | Google Cloud Vision (remplacé en v1.2), Google Fact Check Tools, moteurs de recherche, Gemini, Groq, Brevo, WhatsApp Cloud API, Google OpenID Connect | Recherche d'image, vérifications de faits, recherche de texte, IA, e-mails, WhatsApp, connexion Google |
| Planificateur | Workflow GitHub Actions planifié | Déclenche les lots de sensibilisation via un endpoint interne à jeton |

**Modules M1–M13** : M1 Soumission · M2 Extraction (lien → texte/image/auteur/date/mots-clés) · M3 Recherche de texte + vérifications de faits · M4 Image (empreinte pHash, recherche inversée, OCR, EXIF) · M5 Dates · M6 Fiabilité et statut · M7 Comptes · M8 Certification (insiders) · M9 Chatbot (RAG) · M10 Wiki · M11 Administration · M12 Notifications multicanal · M13 Sensibilisation.

**Flux d'une analyse** : `POST /api/analyses/` → cache (SHA-256 du texte normalisé, URL canonique, ou empreinte image) → si absent, analyse `pending` + `202` (< 1 s) → file en mémoire → exécution en parallèle (recherche web, vérifications de faits, image/empreinte ; délai 8 s par fournisseur, budget total 25 s) → dates, fiabilité, statut → enregistrement → notifications. Le front sonde `GET /api/analyses/{id}/` toutes les 2 s. Un module en erreur ou hors quota produit un résultat `partial` (pas d'échec global).

**IA / RAG en 3 modes** (avec repli automatique) :
- **stub** : aucun modèle, liste de liens et extraits de la base ;
- **groq** : recherche plein texte PostgreSQL + Groq rédige ≤ 3 phrases (mode conseillé pour le MVP) ;
- **gemini** : recherche vectorielle pgvector + embeddings Gemini + rédaction Gemini.
Chaîne de repli : `gemini → groq → stub`. Le modèle ne rédige jamais les liens (construits par le serveur) et ne dit jamais « vrai/faux ».

**Authentification (v1.1)** : e-mail + mot de passe, et connexion Google (OpenID Connect). Clé de liaison = `sub` (jamais l'e-mail), `email_verified` exigé, pas de fusion automatique par e-mail, aucun jeton Google conservé. Insiders/admins : exigence Google encore à décider.

## 6. Problèmes identifiés et solutions proposées

### 6.1 Règle générale de repli (cœur du récapitulatif)

Chaque fonction suit une **chaîne ordonnée de fournisseurs**, du meilleur au moins bon, identique pour tous les profils, qui se termine par un **repli ultime infaillible** (base propre, liens manuels ou saisie par l'utilisateur).

Déclencheurs de passage au fournisseur suivant : délai de 8 s dépassé, HTTP 429/5xx, quota épuisé (`QuotaService.can_call()` faux), ou coupe-circuit ouvert (60 s après un échec). **Un résultat vide n'est pas une panne** : pas de repli. Budget total 25 s ; épuisé → résultat partiel + « Modules indisponibles » + bouton « Relancer ». Échecs journalisés et alertés à 80 % de quota.

### 6.2 Chaînes de repli par fonction

| Fonction | Chaîne (dans l'ordre) | Repli ultime |
|---|---|---|
| Image sur le web (M4) | SerpApi yandex_images → SerpApi google_lens → SearchAPI.io google_lens → Apify | pHash comparé à la base propre + liens manuels (Lens, TinEye, Yandex) |
| Texte sur le web (M3) | Tavily → Serper → SerpApi (Google) → SearchAPI.io (Google SERP) → Exa | Recherche plein texte dans la base propre + liens manuels |
| Vérifications de faits | Fact Check Tools (search + imageSearch) | Table propre des vérifications rencontrées + certifications des insiders |
| Texte dans une image (OCR) | OCR.space → Tesseract.js (navigateur) | Saisie manuelle |
| Post de réseau social (M2) | Mastodon → Bluesky → TikTok (oEmbed) | Saisie/collage du texte par l'utilisateur |
| Date d'apparition (M5) | DateResolver sur 5 pages candidates → plus ancienne capture de l'Internet Archive (CDX) | « Date inconnue » avec ce qui a été essayé |
| IA et chatbot (M9) | Gemini → Groq → stub | Stub : liens issus de la base, sans IA |
| E-mails | Brevo | Notification dans l'application |
| WhatsApp | Message libre dans la fenêtre de 24 h | Notification dans l'application ; envois reportés si plafond 300/jour atteint |
| Connexion | Google | E-mail et mot de passe |

### 6.3 Manques constatés et solutions

1. **Google Cloud Vision exige une carte** → remplacé par les chaînes image/OCR ci-dessus (sans carte).
2. **Quota d'image faible** (~250/mois ≈ 8/jour) → cache image 24 h allongé, plafond journalier, étalement du quota, chaîne de repli.
3. **Aucune API ne donne la date de première apparition** → DateResolver puis Internet Archive ; on affiche la « plus ancienne trouvée », jamais « la première », toujours avec son origine.
4. **Fact Check Tools : gratuité/carte inconnues** → si facturation exigée, le retirer ; « Contredite » vient alors de la table propre + insiders.
5. **Les moteurs d'image exigent une URL publique** → hébergement éphémère (URL à jeton aléatoire, quelques minutes, en mémoire, jamais en base).
6. **OCR non testé en français** → chaîne OCR.space → Tesseract.js → saisie manuelle ; réduction de l'image sous 1 Mo.
7. **Posts Meta et X non lisibles automatiquement** → saisie manuelle + affichage oEmbed ; extraction auto seulement pour Mastodon/Bluesky/TikTok ; X nécessite un avis juridique.
8. **Tavily : phrase exacte et dates** → deux requêtes par analyse ; dates par DateResolver.
9. **Google en production : domaine non vérifié** → mode Testing pour la bêta (100 testeurs, autorisations 7 jours) ; repli e-mail.
10. **Gemini : pays éligible ?** → chaîne Groq → stub déjà prévue.
11. **Cadre légal des données non confirmé** → validation par une personne compétente avant ouverture.
12. **Render se met en veille** → bandeau « réveil du serveur » ; pages publiques servies par le front.

### 6.4 Capacité estimée (calculs du récapitulatif, à vérifier)

Image ~8 recherches/jour (SerpApi) + réserve SearchAPI.io + ~1 000 images/mois (Apify) ; texte ~500 analyses/mois (Tavily, 2 requêtes/analyse) + ~1 250 (Serper) ; OCR 25 000/mois. **Le MVP tient pour un pilote de quelques dizaines d'analyses par jour au plus** — pas un service public à fort trafic.

## 7. Décisions en attente et risques majeurs

- Exiger ou non un **compte lié à Google** pour insiders et administrateurs.
- **Usage commercial ou non** (Vercel Hobby est non commercial).
- **Cadre légal** : politique de confidentialité et conservation des données à faire valider.
- Quotas/tarifs des fournisseurs à reconfirmer dans les consoles (ils changent souvent).
- WhatsApp : un moyen de paiement pourrait être exigé depuis octobre 2026 → sinon `WHATSAPP_ENABLED=false` et repli e-mail.
- **Faux sentiment de certitude** : risque qu'un statut soit pris pour une preuve → mitigation par les niveaux, critères, sources et l'avertissement permanent.

## 8. Conclusion en une page

La **plateforme anti-fake news** est la solution numérique du concours « Défions l'infox » d'EDUK-MEDIA : un **outil gratuit d'aide à la vérification** qui retrouve l'origine et la date d'apparition d'une information (texte, image, lien), croise les sources et les vérifications de faits, et affiche un **statut en niveaux** — jamais un verdict de vérité — appuyé sur des sources traçables et des certifications humaines (insiders).

Techniquement, c'est un MVP **Next.js (Vercel) + Django (Render) + PostgreSQL Neon**, découpé en 13 modules, avec une IA/RAG à 3 modes et repli automatique, et une contrainte forte : **tout doit fonctionner sans carte bancaire**, ce qui a conduit à remplacer Google Cloud Vision par des chaînes de fournisseurs de repli. La version 1.1 ajoute la connexion Google. Chaque fonctionnalité est conçue pour **toujours produire un résultat** (même partiel), grâce à une règle générale de repli qui se termine par la base propre ou la saisie manuelle.

Enfin, le vocabulaire de statut est en cours d'évolution : aux 4 niveaux techniques (Corroborée / Non corroborée / Contredite / Indéterminée) s'ajoute le vocabulaire pédagogique du document scanné (**Information / Opinion / Rumeur / Infox**, **mésinformation / désinformation / malinformation**, et l'échelle **Paraît fiable / Prudence / Forte probabilité de manipulation**), que le projet souhaite utiliser comme statuts des informations après analyse.
