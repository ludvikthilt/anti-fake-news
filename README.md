# InfoxVerify — concours EDUK-MÉDIA

**InfoxVerify** est un outil éducatif d'**aide à la vérification de l'information**, réalisé pour le concours **EDUK-MÉDIA**, en partenariat avec l'**Union européenne**, et destiné aux élèves et étudiants du Mfoundi (Cameroun). InfoxVerify ne dit jamais « vrai » ni « faux » : l'outil rassemble des traces (sources, dates, vérifications déjà publiées) et propose un **statut** — c'est une aide à la décision, pas un verdict.

> **Ce site aide à vérifier : il ne prouve pas qu'une information est vraie.**

## Architecture

- **Backend** : Django 5 + Django REST Framework, PostgreSQL.
- **Frontend** : Next.js 15 (TypeScript, App Router), mobile-first, installable en PWA (raccourci sur l'écran d'accueil de n'importe quel appareil mobile).
- **Base de données** : PostgreSQL (natif en développement, conteneur en production).
- **Production** : Docker Compose (PostgreSQL + gunicorn + Next.js) — voir [DEPLOIEMENT.md](DEPLOIEMENT.md).

```
backend/   API REST + moteur d'analyse + admin Django (/admin)
frontend/  Next.js + PWA + design tokens
ressources/design/  Direction artistique de référence (DESIGN.md)
```

## Vocabulaire (issu du document scanné, conservé à l'implémentation)

Les **quatre statuts** d'une information (jamais « vrai/faux ») :

| Statut | Signification |
|---|---|
| **Corroborée** | Plusieurs sources indépendantes et fiables reprennent l'information, sans contradiction trouvée. |
| **Non corroborée** | Des traces existent, mais trop peu de sources fiables et indépendantes. Ce n'est pas un « faux ». |
| **Contredite** | Une vérification de faits publiée ou plusieurs sources fiables contredisent l'information. |
| **Indéterminée** | Pas assez d'éléments, analyse partielle, ou désaccord entre insiders. |

Étiquettes **pédagogiques EMI** secondaires (distinctes du statut) :

- **Nature** : Information · Opinion · Rumeur · Infox.
- **Désordre** (pour une infox) : Mésinformation · Désinformation · Malinformation.

Deux questions pour raisonner : « Peut-on le vérifier ? » et « Y a-t-il une intention de nuire ? »

## Prérequis

- Python 3.12, PostgreSQL 18 (service local), Node 24, pnpm 10.

## Démarrage du backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Windows (bash MSYS2)
# .venv/bin/pip install -r requirements.txt          # Linux/macOS

# 1. Créer la base (une fois)
createdb -U postgres antifake                        # ou via psql

# 2. Configurer .env (copier .env.example) avec :
#    DATABASE_URL=postgresql://postgres:MOT_DE_PASSE@localhost:5432/antifake

# 3. Migrer, peupler la base, créer l'admin
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py seed        # base de référence (sites, wiki, RAG)
.venv/Scripts/python manage.py seed_demo   # + données de démonstration complètes
.venv/Scripts/python manage.py createsuperuser

# 4. Lancer
.venv/Scripts/python manage.py runserver 127.0.0.1:8000
```

Compte de démonstration local (déjà créé via seed) :
- E-mail : `admin@antifake.local` — mot de passe : `admin12345` (rôle **Administrateur**).

`seed_demo` ajoute des données de démonstration : six comptes fictifs (`@example.org`, sans
compte Telegram), neuf dossiers d'analyse couvrant les quatre statuts, des lectures d'insiders,
un site certifié et un site « en observation », des fiches wiki en attente de validation, des
campagnes, des notifications et la consommation des quotas du mois. La commande est
idempotente (relançable sans doublon) ; définissez `DEMO_PASSWORD` si vous souhaitez connecter
les comptes fictifs, sinon ils n'ont aucun mot de passe utilisable.

> Sur Render, cette étape est **automatique** : `entrypoint.sh` lance `migrate`, `seed_demo` et
> `index_knowledge` à chaque démarrage (désactivable avec `SEED_DEMO=false`). Voir
> [DEPLOIEMENT.md](DEPLOIEMENT.md).

API : `http://127.0.0.1:8000/api/` · Schéma OpenAPI : `/api/schema/` · Swagger : `/api/docs/` · Admin Django : `/admin/`.

## Démarrage du frontend

```bash
cd frontend
pnpm install
pnpm dev          # http://localhost:3000
```

Build de production : `pnpm build` (First Load JS ≈ 109 Ko, sous l'objectif de 150 Ko gzip).

## Services externes et repli

Sans clé API, la plateforme fonctionne quand même : chaque fournisseur a une chaîne de repli et l'analyse part en **partiel** en affichant les « modules indisponibles ».

| Fonction | Fournisseurs (chaîne de repli) | Variable |
|---|---|---|
| Recherche texte | Tavily → Serper → SerpApi → SearchAPI → Exa → base propre | `SEARCH_PROVIDER` |
| OCR (image) | OCR.space → saisie manuelle | `OCRSPACE_API_KEY` |
| Recherche inversée d'image | SerpApi Yandex → SerpApi Lens → SearchAPI Lens → Apify Lens (asynchrone) → moteurs publics | `SERPAPI_API_KEY`, `SEARCHAPI_API_KEY`, `APIFY_API_KEY`, `APIFY_LENS_ACTOR` |
| Vérifications de faits | Fact Check Tools → base propre | `FACTCHECK_API_KEY` |
| Récupération RAG | Embeddings Gemini + cosinus → plein texte `fr_unaccent` → trigramme → mots-clés | `GEMINI_API_KEY`, `GEMINI_EMBED_MODEL` |
| Chatbot IA | Gemini → Groq → stub (liens seuls) | `AI_MODE`, `GEMINI_API_KEY`, `GROQ_API_KEY` |
| E-mail | Brevo (repli : console Django) | `BREVO_API_KEY`, `EMAIL_FROM` |
| Telegram | Bot API (gratuit) | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` |
| Web Push | VAPID + service worker (gratuit) | `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` |

Les clés se placent dans `backend/.env` (jamais dans git ni dans le code).

## Installation en PWA (mobile)

Depuis le navigateur mobile : « Ajouter à l'écran d'accueil » (Android/Chrome) ou « Partager → Sur l'écran d'accueil » (iOS/Safari). Le manifeste et le service worker sont dans `frontend/public/`.

## Dockerisation

L'application validée en local est dockerisée : `docker-compose.yml` réunit PostgreSQL, le backend
(gunicorn, migrations et fichiers statiques au démarrage) et le frontend (sortie Next.js
`standalone`).

```bash
cp backend/.env.example backend/.env    # renseigner DEBUG=false, clé, domaines, DATABASE_URL
cp .env.example .env                    # POSTGRES_*, NEXT_PUBLIC_API_URL (facultatif)
docker compose up -d --build
```

Détails, HTTPS, sauvegardes et recette : [DEPLOIEMENT.md](DEPLOIEMENT.md).

## État des modules du dossier technique (M1–M13)

| Module | État |
|---|---|
| M1 Soumission | ✅ texte / lien / image (bornes 5 Mo / 4 096 px), `202`, cache SHA-256/pHash expirant (6 h texte, 24 h image) |
| M2 Extraction | ✅ trafilatura (titre, auteur, date) + YAKE (mots-clés) + oEmbed Mastodon/Bluesky/TikTok |
| M3 Recherche texte + fact-check | ✅ chaînes de repli multiples |
| M4 Image | ✅ OCR.space (bascule silencieuse vers la saisie manuelle), pHash, recherche inversée Apify Lens lancée en parallèle puis fusionnée, hébergement éphémère |
| M5 Dates | ✅ DateResolver + pastille d'origine |
| M6 Fiabilité / statut | ✅ 4 statuts + nature/désordre EMI |
| M7 Comptes | ✅ e-mail/mot de passe + Google OIDC (endpoint, clés requises) |
| M8 Certification | ✅ insiders, source obligatoire |
| M9 Chatbot/RAG | ✅ embeddings Gemini (768 dim.) + cosinus → plein texte tsvector (`fr_unaccent`, GIN, pg_trgm) → mots-clés ; génération `gemini → groq → stub` ; `manage.py index_knowledge` |
| M10 Wiki | ✅ pages, versions, restauration |
| M11 Administration | ✅ stats, demandes insider, retrait de certification, suspension |
| M12 Notifications | ✅ in-app à la fin d'une analyse + e-mail Brevo (repli console) + Telegram + Web Push, consentements séparés, STOP/AIDE, `POST /api/auth/me/{telegram,push}/` |
| M13 Sensibilisation | ✅ campagnes (création, envoi) + endpoint interne à jeton + commande `send_campaigns` ; planificateur GitHub Actions à configurer en déploiement |

> **Vecteurs et pgvector** : l'extension `vector` n'est pas fournie par l'installation PostgreSQL 18 sous Windows utilisée en local (aucun outil de compilation MSVC disponible). Les embeddings Gemini sont donc stockés dans une colonne JSON native et la similarité cosinus est calculée en Python — le corpus reste petit, la recherche est exacte et sans dépendance supplémentaire. Le jour où pgvector est disponible, seule la colonne change : la chaîne de retrieval reste identique.
>

## Telegram — canal gratuit et illimité

Aucun coût, aucune vérification d'entreprise, aucun numéro de téléphone : le bot répond à
l'utilisateur qui ouvre la conversation. C'est le canal instantané gratuit de la plateforme.

1. Sur Telegram, ouvrir [@BotFather](https://t.me/BotFather) → `/newbot` → nom et identifiant.
   Il renvoie un jeton et le nom d'utilisateur du bot.
2. Renseigner `backend/.env` :
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_BOT_USERNAME=mon_antifake_bot
TELEGRAM_WEBHOOK_SECRET=<chaîne aléatoire, ex. openssl rand -hex 32>
```
3. Déclarer le webhook (une URL publique HTTPS ; en local `cloudflared tunnel --url http://localhost:8000`) :
```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://<tunnel>/api/webhooks/telegram/" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```
4. Dans l'application : **Mon compte → Alertes Telegram → Lier mon Telegram**. Un code de 30 minutes
   ouvre le bot ; le message `/start <code>` lie le compte. Le bouton surveille la liaison pendant
   une minute et confirme sans rechargement.
5. Commandes reconnues : `/start` (liaison), `/stop` (désinscription + retrait des consentements),
   `/aide`. Un chat ne peut être lié qu'à un seul compte.

Événements couverts : notification de fin d'analyse, campagnes de sensibilisation (canal `telegram`).

## Notifications Web Push — gratuit, dans la PWA

Le canal le plus économique : aucune passerelle tierce, aucune limite d'envoi. Il faut que la
plateforme soit ouverte au moins une fois depuis l'appareil (et installée en raccourci sur iPhone,
qui exige iOS 16.4 ou plus récent).

1. Les clés VAPID sont générées et posées dans `backend/.env`
   (`VAPID_PRIVATE_KEY` en base64url, 32 octets). Pour les régénérer :
```bash
python -c "import base64,os; from cryptography.hazmat.primitives.asymmetric import ec; k=ec.generate_private_key(ec.SECP256R1()); print(base64.urlsafe_b64encode(k.private_numbers().private_value.to_bytes(32,'big')).decode().rstrip('='))"
```
   `VAPID_SUBJECT` doit être un `mailto:` valide (contact technique exigé par la RFC 8292).
2. Dans l'application : **Mon compte → Notifications dans l'application → Activer les notifications**.
   Le navigateur demande l'autorisation, l'abonnement part vers `POST /api/auth/me/push/`.
3. L'envoi utilise `pywebpush` (`requirements.txt`) : le service worker `public/sw.js` affiche la
   notification et ouvre le lien de l'analyse au clic.
4. Un abonnement mort (410 Gone) est marqué `failed_at` et ignoré aux envois suivants.

Événements couverts : notification de fin d'analyse, campagnes (canal `push`).

## RAG : indexation du corpus

```bash
cd backend && .venv/Scripts/python.exe manage.py index_knowledge
```

À relancer après un import massif de pages wiki (les pages publiées sont sinon indexées à la première recherche).

## Documentation de référence

- Direction artistique : [ressources/design/DESIGN.md](ressources/design/DESIGN.md)
- Écarts assumés avec le design : [frontend/DESIGN-DEVIATIONS.md](frontend/DESIGN-DEVIATIONS.md)
