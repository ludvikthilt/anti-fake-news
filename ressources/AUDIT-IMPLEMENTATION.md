# Audit d'implémentation — dossier technique

> Établi le 24 octobre 2026, après nettoyage du code (retrait de WhatsApp Meta/Twilio et de Google Cloud Vision).
> Méthode : lecture du code, exécution des tests, appels HTTP réels aux endpoints et aux fournisseurs.

## Légende

| Marque | Sens |
|---|---|
| ✅ **Fait** | Implémenté et vérifié, conforme au dossier. |
| 🟡 **Fait mais différemment** | La contrainte technique ou matérielle interdisait la solution prévue ; une alternative fonctionnelle la remplace. |
| ⛔ **Non fait** | Absent, hors périmètre local, ou bloqué par une contrainte externe. |

## Synthèse

- **7 modules conformes** (M1, M2, M3, M7, M8, M10, M11), **6 conformes avec une variante assumée** (M4, M5, M6, M9, M12, M13), **0 module absent**.
- **54 tests automatisés verts**, `manage.py check` sans erreur, `check --deploy` sans aucun avertissement de sécurité, build Next.js réussi.
- Les deux retraits demandés (WhatsApp, Google Vision) sont complets : plus aucune référence dans le code, les modèles, les migrations ou les routes.

## Modules M1–M13

| Module | Exigence du dossier | État | Détail |
|---|---|---|---|
| **M1 Soumission** | Texte ≤ 5 000 car., image ≤ 5 Mo / 4 096 px, lien ; `202` immédiat ; cache SHA-256 / pHash | ✅ **Fait** | Texte borné à 5 000 car., réponse `202` avec identifiant public, cache texte (SHA-256 normalisé) et image (pHash). Les bornes **5 Mo et 4 096 px** sont contrôlées avant toute analyse (réponse `400` explicite). |
| **M2 Extraction** | Lien → titre, texte, auteur, date, mots-clés ; oEmbed Mastodon/Bluesky/TikTok ; Meta/X en saisie manuelle | ✅ **Fait** | trafilatura (titre, auteur, date) + repli BeautifulSoup ; YAKE pour les mots-clés ; oEmbed Mastodon, Bluesky, TikTok. Meta/X restent en collage manuel, comme prévu. |
| **M3 Recherche + fact-check** | Tavily → Serper → SerpApi → SearchAPI → Exa → base propre ; Fact Check Tools → base propre | ✅ **Fait** | Chaînes complètes dans `providers.py`, budget 25 s, Fact Check Tools testé (200, 5 vérifications). Une vérification n'est retenue que si elle porte sur **la même affirmation** (recouvrement ≥ 50 % des mots) : sans ce filtre, une vérification voisine déclarait « Contredite » une information sans rapport. `claims:imageSearch` n'est pas branché (seul `claims:search`). |
| **M4 Image** | pHash, recherche inversée, OCR, EXIF, hébergement éphémère | 🟡 **Fait mais différemment** | pHash, chaîne SerpApi Yandex → Lens → SearchAPI → Apify (asynchrone, fusionnée après le statut), URL éphémère à jeton (5 min). **OCR.space → saisie manuelle** (Vision retiré à la demande) ; pas d'EXIF, pas de Tesseract.js. |
| **M5 Dates** | DateResolver sur plusieurs pages + plus ancienne capture Internet Archive, avec origine | 🟡 **Fait mais différemment** | Dates **déclarées** (extraction) et **d'indexation** (résultats de recherche), plus la colonne `DateOrigin` à 4 valeurs (déclarée / observée / métadonnée / indexation). Pas de DateResolver multi-pages ni de CDX : sans clé d'archive, la date reste celle trouvée, toujours étiquetée. |
| **M6 Fiabilité** | 4 statuts + nature + désordre + grille de doutes | 🟡 **Fait mais différemment** | Les 4 statuts (Corroborée / Non corroborée / Contredite / Indéterminée) sont calculés sur sources, vérifications et certifications ; `nature` (Information / Opinion / Rumeur / Infox) et `disorder` (mésinformation / désinformation / malinformation) sont produits. La grille **« Paraît fiable / Prudence / Forte probabilité de manipulation »** n'est pas calculée. |
| **M7 Comptes** | E-mail + mot de passe, Google OIDC, rôles visiteur/inscrit/insider/admin | ✅ **Fait** | JWT, rôles, Google OIDC (code + ID token, `sub`, `email_verified`, nonce). Vérifié : URL d'autorisation acceptée, client/secret valides. |
| **M8 Certification** | Insiders, source obligatoire, retrait par l'admin | ✅ **Fait** | `POST /api/certifications/` réservé aux insiders, `source_url` obligatoire, retrait côté admin. |
| **M9 Chatbot / RAG** | pgvector + embeddings, tsvector, Gemini → Groq → stub | 🟡 **Fait mais différemment** | Embeddings Gemini stockés en **JSON** + similarité cosinus en Python (pgvector indisponible sous PostgreSQL 18/Windows sans compilateur), repli plein texte `fr_unaccent` + trigramme, puis mots-clés. Génération `gemini → groq → stub` testée. |
| **M10 Wiki** | Pages, versions, restauration | ✅ **Fait** | `WikiPage` + `WikiRevision`, restauration d'une révision par `POST`, pages non publiées réservées aux insiders. |
| **M11 Administration** | Stats, demandes insider, retrait de certification, suspension | ✅ **Fait** | `GET /api/admin/stats/`, validation/refus insider, retrait, `is_active=False`. |
| **M12 Notifications** | In-app + e-mail (Brevo) + WhatsApp | 🟡 **Fait mais différemment** | In-app à la fin d'analyse, e-mail Brevo (testé : `delivered`), **Telegram** et **Web Push** à la place de WhatsApp, consentements séparés, STOP/AIDE. WhatsApp retiré : Meta exige une vérification d'entreprise et Twilio reste payant. |
| **M13 Sensibilisation** | Campagnes, envoi, planificateur GitHub Actions | 🟡 **Fait mais différemment** | Modèle, API admin (création / envoi), endpoint interne à jeton, workflow `.github/workflows/send-campaigns.yml`. L'**approbation** n'a pas d'écran dédié : elle se fait par l'admin Django ou l'API ; les secrets GitHub restent à configurer. |

## Exigences transverses

| Exigence | État | Détail |
|---|---|---|
| Chaîne de repli ordonnée, repli ultime infaillible | ✅ **Fait** | `providers_run` parcourt la chaîne, borne chaque appel à 8 s et le total à 25 s. |
| Coupe-circuit 60 s | ✅ **Fait** | `CircuitBreaker` utilisé par la chaîne d'analyse ; une indisponibilité de configuration n'ouvre pas le circuit. |
| Quotas persistés | ✅ **Fait** | `QuotaUsage` par fournisseur et par mois, `can_call()` consulté avant chaque appel. |
| Alerte à 80 % du quota | ✅ **Fait** | `QuotaUsage.alerted_at` + journal + `AuditLog` une seule fois par période ; seuil réglable (`QUOTA_ALERT_RATIO`). |
| Résultat partiel + « modules indisponibles » | ✅ **Fait** | Chaque module manquant est listé avec sa raison ; l'analyse aboutit en `partial`. |
| Cache analyse | ✅ **Fait** | SHA-256 du texte normalisé / URL canonique, pHash pour l'image. |
| Expiration du cache (6 h / 24 h) | ✅ **Fait** | Le cache ne réutilise une analyse que si elle a moins de `CACHE_TTL_TEXT_HOURS` (texte) ou `CACHE_TTL_IMAGE_HOURS` (image). |
| Limitation de débit (visiteur / inscrit) | ✅ **Fait** | `DualRateThrottle` appliqué à toutes les vues API (60/min visiteur, 120/min inscrit), plus des scopes serrés : analyse 10/30, chatbot 20/60, connexion 10/min, inscription 5/h, jeton interne 10/min. Vérifié : la 61ᵉ requête anonyme renvoie `429`. |
| Résultat partageable | ✅ **Fait** | `public_id` court, page publique en lecture seule. |
| PWA / raccourci mobile | ✅ **Fait** | Manifeste, service worker, icônes, installation iOS/Android ; responsive vérifié. |
| Notifications push | ✅ **Fait** | VAPID + service worker, abonnement par appareil, nettoyage des abonnements morts. |
| Pages légales | ✅ **Fait** | `/confidentialite`, `/limites`, avertissement permanent. |
| Validation juridique des données | ⛔ **Non fait** | Hors code : à faire valider par une personne compétente. |
| Dockerisation | ✅ **Fait** | `backend/Dockerfile` (gunicorn, migrations + `collectstatic` + table de cache au démarrage), `frontend/Dockerfile` (sortie `standalone`), `docker-compose.yml` (PostgreSQL 16 + backend + front), `.dockerignore`, `HEALTHCHECK`. Non exécutée ici : Docker n'est pas installé sur cette machine. |
| Intégration continue | ✅ **Fait** | `.github/workflows/ci.yml` : tests backend sur PostgreSQL 16 et build front (types + `next build`). |
| Supervisabilité | ✅ **Fait** | `GET /api/health/` (base + cache, `503` si la base est indisponible), journaux sur la sortie standard, `check --deploy` sans avertissement. |

## Écarts assumés et leur raison

1. **Google Cloud Vision retiré** — l'API exige la facturation activée sur le projet. L'OCR repose sur **OCR.space**, puis la saisie manuelle. Le passage est invisible côté utilisateur.
2. **WhatsApp retiré** — depuis octobre 2026 Meta facture les messages de service, et la vérification d'entreprise n'est pas disponible. **Telegram** et **Web Push** couvrent le besoin gratuitement.
3. **pgvector indisponible** — l'extension `vector` n'est pas fournie avec PostgreSQL 18 sous Windows et aucun compilateur MSVC n'est présent. Embeddings en JSON + cosinus Python ; le jour où pgvector arrive, seule la colonne change.
4. **Pas d'Internet Archive / CDX** — aucune clé et pas de garantie de disponibilité ; les dates affichées portent toujours leur origine.
5. **Pas d'EXIF** — Pillow le permettrait, mais l'original n'est jamais conservé ; la miniature supprime les métadonnées.
6. **Grille de doutes non calculée** — le vocabulaire du document scanné est repris pour `nature` et `disorder`, pas pour les trois verdicts de la check-list.
7. **Approbation des campagnes** — statut `approved` présent, mais pas d'écran d'approbation ; envoi manuel possible depuis l'admin.

### Corrigé avant la mise en production (24 octobre)

- **Bornes d'image** : 5 Mo et 4 096 px contrôlés dans le sérialiseur, réponse `400` explicite, corps de requête autorisé à 12 Mo pour laisser passer le base64.
- **Limitation de débit** : `DualRateThrottle` branché globalement et scopes serrés sur les actions coûteuses.
- **Expiration du cache** : 6 h pour un texte, 24 h pour une image.
- **Alerte de quota** : journal + `AuditLog` à 80 % du plafond, une fois par période.
- **Vérifications de faits hors sujet** : une vérification n'est retenue que si elle porte réellement sur la même affirmation. Sans ce filtre, « La CAN 2025 se déroule au Maroc » était déclarée **Contredite** / **Infox** à cause d'une vérification sur le décès d'un stadier.
- **Configuration de production** : `check --deploy` sans avertissement (HSTS, cookies sécurisés, redirection HTTPS, en-tête proxy), garde-fous sur `SECRET_KEY` et `ALLOWED_HOSTS`, cache partagé optionnel, journaux sur la sortie standard, endpoint `/api/health/`.
- **Livraison** : Docker Compose, images backend/front, CI GitHub Actions, [DEPLOIEMENT.md](../DEPLOIEMENT.md).

## Vérifications exécutées

| Contrôle | Résultat |
|---|---|
| `pytest` (backend) | **54 tests verts** |
| `manage.py check` / migrations | OK, dont suppression de `WhatsAppContact` |
| `next build` + `tsc --noEmit` | OK |
| `check --deploy` en mode production | 0 avertissement de sécurité |
| 61 requêtes anonymes en une minute | `429` à la 61ᵉ, message en français |
| Image de 4 100 px | `400 Image trop grande : 4 096 px maximum par côté.` |
| Seconde soumission identique | `200` et même identifiant (cache), puis `202` après expiration |
| `GET /api/health/` | `200 {"database":"ok","cache":"ok"}` |
| `GET /api/webhooks/telegram/` | `200 {"available": false}` (jeton du bot à créer) |
| `GET /api/auth/me/{telegram,push}/` sans session | `401` |
| Anciens endpoints WhatsApp | `404` (`me/whatsapp`, `webhooks/whatsapp`, `webhooks/whatsapp/twilio`) |
| Envoi e-mail Brevo | `delivered` confirmé par le journal Brevo |
| Fact Check Tools | `200`, vérifications renvoyées |
| Interface compte | sections « Alertes Telegram » et « Notifications dans l'application » rendues ; aucune section WhatsApp |

## Reste à faire à la mise en ligne (hors code)

1. Créer le bot Telegram (@BotFather), poser le jeton et déclarer le webhook.
2. Servir l'application en **HTTPS** : sans cela, ni service worker ni notifications push.
3. Configurer les secrets GitHub (`BACKEND_URL`, `INTERNAL_TOKEN`) du planificateur.
4. Renseigner `GOOGLE_OAUTH_REDIRECT_URI` avec l'adresse réelle et l'ajouter dans la console Google.
5. Faire valider la politique de confidentialité et la conservation des données.
6. Exécuter `docker compose up -d --build` sur le serveur (Docker n'est pas installé sur le poste de développement) et dérouler la recette de [DEPLOIEMENT.md](../DEPLOIEMENT.md).
