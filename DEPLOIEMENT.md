# Mise en production

Ce guide décrit tout ce qui est nécessaire pour faire tourner la plateforme hors du poste de
développement : préparation, variables, deux chemins d'installation (Docker Compose ou serveur
classique), puis la liste des réglages à faire une fois l'application en ligne.

Le fonctionnement local reste inchangé : `manage.py runserver` et `next dev`.

---

## 1. Ce que la production exige

| Élément | Pourquoi |
|---|---|
| PostgreSQL 16 ou plus | Base applicative (l'extension `vector` n'est pas nécessaire). |
| HTTPS | Obligatoire pour le service worker, les notifications push et les cookies sécurisés. |
| Une clé secrète forte | `DJANGO_SECRET_KEY` : sans elle, `check` en mode production refuse de démarrer. |
| `ALLOWED_HOSTS` explicite | Idem : `*` est refusé quand `DEBUG=false`. |
| 2 processus ou plus | Gunicorn lance 3 workers par défaut ; le cache passe alors en base (`CACHE_BACKEND=db`). |

---

## 2. Variables d'environnement

À placer dans `backend/.env` (Docker) ou dans l'unité systemd (serveur classique).
`backend/.env.example` sert de modèle.

### Obligatoires en production

| Variable | Exemple | Rôle |
|---|---|---|
| `DEBUG` | `false` | Désactive le mode développement. |
| `DJANGO_SECRET_KEY` | 50+ caractères aléatoires | Signature des sessions et jetons. |
| `ALLOWED_HOSTS` | `antifake.exemple.com` | Domaines servis. |
| `DATABASE_URL` | `postgresql://user:pass@db:5432/antifake` | Connexion PostgreSQL. |
| `FRONTEND_URL` | `https://antifake.exemple.com` | Liens et redirections. |
| `CORS_ALLOWED_ORIGINS` | `https://antifake.exemple.com` | Origines autorisées. |
| `CSRF_TRUSTED_ORIGINS` | `https://antifake.exemple.com` | Formulaires et admin Django. |

### Recommandées

| Variable | Défaut | Rôle |
|---|---|---|
| `CACHE_BACKEND` | `locmem` | Mettre `db` dès qu'il y a plusieurs workers. |
| `SECURE_SSL_REDIRECT` | `true` hors DEBUG | Redirige HTTP vers HTTPS. |
| `BACKEND_BASE_URL` | `http://127.0.0.1:8000` | URL publique du backend (images éphémères des moteurs de recherche). |
| `LOG_LEVEL` | `INFO` | Verbosité des journaux. |
| `GUNICORN_WORKERS` | `3` | Nombre de workers. |
| `MAX_REQUEST_BYTES` | `12582912` | Taille maximale d'une requête (image 5 Mo en base64). |
| `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` | — | Création automatique du compte admin au premier démarrage. |

### Fournisseurs (aucune n'est obligatoire, les chaînes de repli prennent le relais)

`TAVILY_API_KEY`, `SERPER_API_KEY`, `SERPAPI_API_KEY`, `SEARCHAPI_API_KEY`, `EXA_API_KEY`,
`FACTCHECK_API_KEY`, `OCRSPACE_API_KEY`, `APIFY_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`,
`BREVO_API_KEY`, `TELEGRAM_BOT_TOKEN`, `VAPID_PRIVATE_KEY`, `GOOGLE_OAUTH_CLIENT_ID`,
`GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`, `INTERNAL_TOKEN`.

---

## 3. Chemin A — Docker Compose (recommandé)

```bash
# 1. Variables
cp backend/.env.example backend/.env
#    → renseigner DEBUG=false, DJANGO_SECRET_KEY, ALLOWED_HOSTS, FRONTEND_URL,
#      CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS, DATABASE_URL placeholders et les clés.

# 2. Variables de l'orchestration (facultatives, valeurs par défaut prévues)
#    POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, NEXT_PUBLIC_API_URL

# 3. Lancement
docker compose up -d --build

# 4. Vérification
docker compose ps                       # backend « healthy », db « healthy »
curl -s http://localhost:8000/api/health/
```

- Front : `http://localhost:3000`, API : `http://localhost:8000/api/`.
- `NEXT_PUBLIC_API_URL` est **figé au build** : c'est l'adresse appelée par le navigateur du
  visiteur. Sur un vrai domaine, mettre `https://api.exemple.com/api` (ou `/api` si un
  reverse proxy sert les deux sur la même origine) puis reconstruire l'image front.
- Le conteneur backend exécute automatiquement `migrate`, `collectstatic`, la table de cache
  et, si les variables le permettent, le compte administrateur.
- `docker compose logs -f backend` pour suivre les analyses.

### HTTPS devant la pile

Le plus simple est un reverse proxy sur la même machine (Caddy) :

```
antifake.exemple.com {
    handle_path /api/* {
        reverse_proxy backend:8000
    }
    reverse_proxy frontend:3000
}
```

Avec nginx, ajouter `proxy_set_header X-Forwarded-Proto $scheme;` — Django lit cet en-tête
(`SECURE_PROXY_SSL_HEADER`) pour savoir que la requête est arrivée en HTTPS.

---

## 3 bis. Render (PaaS, sans serveur à gérer)

Le fichier [render.yaml](render.yaml) décrit la base PostgreSQL, l'API et le front. Render construit
les deux images Docker à partir du dépôt et fournit HTTPS automatiquement.

1. Pousser le dépôt sur GitHub (voir section 5 bis).
2. Render → **New +** → **Blueprint** → sélectionner le dépôt. Render lit `render.yaml` et propose
trois ressources : `antifake-db`, `antifake-api`, `antifake-web`.
3. Cliquer **Apply**. Le premier build prend quelques minutes ; `antifake-api` reste rouge tant que
   la base n'est pas prête, puis /api/health/ passe au vert.
4. Renseigner les variables marquées `sync: false` sur `antifake-api` (clés Tavily, Gemini, Brevo,
   Google, Telegram…). Render redéploie automatiquement à chaque enregistrement.
5. Vérifier les adresses : si Render a suffixé un nom (déjà pris), mettre à jour `ALLOWED_HOSTS`,
   `FRONTEND_URL`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `BACKEND_BASE_URL` et `API_URL`
   du front. `API_URL` est lue à l'exécution : un simple redémarrage suffit, sans rebuild.
6. Ajouter `https://<front>.onrender.com` (origine) et
   `https://<front>.onrender.com/compte/google/callback` dans la console Google. Le front lit
   `GOOGLE_CLIENT_ID` et `API_URL` à l'exécution via `/runtime-config.js` : le blueprint fournit
   déjà le client OAuth, et ces valeurs se changent sans reconstruire l'image.
7. Redéclarer le webhook Telegram sur `https://<api>.onrender.com/api/webhooks/telegram/`.

> **Offre gratuite** : les services s'endorment après une période d'inactivité (le premier appel
> après réveil prend quelques dizaines de secondes) et le service PostgreSQL gratuit est limité
> dans le temps. Une analyse lancée juste avant l'endormissement peut rester en `pending` :
> relancer l'analyse. Pour un usage continu (notifications, campagnes), le plan payant évite ces
> coupures.

## 4. Chemin B — serveur classique (sans Docker)

```bash
# Backend
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createcachetable          # si CACHE_BACKEND=db
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120

# Frontend (autre service)
cd frontend
corepack enable && pnpm install --frozen-lockfile
NEXT_PUBLIC_API_URL=https://api.exemple.com/api pnpm build
pnpm start                                  # écoute sur :3000
```

Unité systemd minimale pour le backend :

```ini
[Unit]
Description=Antifake backend
After=network.target postgresql.service

[Service]
WorkingDirectory=/srv/antifake/backend
EnvironmentFile=/srv/antifake/backend/.env
ExecStart=/srv/antifake/backend/.venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 5. Réglages à faire une fois en ligne

1. **Google** : dans la console Google Cloud, ajouter
   `https://<domaine>/compte/google/callback` aux URI de redirection autorisées, puis mettre
   cette valeur dans `GOOGLE_OAUTH_REDIRECT_URI` et reconstruire le front (la valeur doit être
   identique côté navigateur).
2. **Telegram** : créer le bot (@BotFather), renseigner `TELEGRAM_BOT_TOKEN`,
   `TELEGRAM_BOT_USERNAME`, `TELEGRAM_WEBHOOK_SECRET`, puis déclarer le webhook :
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -d "url=https://<domaine>/api/webhooks/telegram/" \
     -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
   ```
3. **Web Push** : générer la clé VAPID (`python -m py_vapid` ou l'utilitaire de votre choix),
   la placer dans `VAPID_PRIVATE_KEY` et `VAPID_SUBJECT` (adresse de contact).
4. **Planificateur des campagnes** : dans GitHub → *Settings → Secrets and variables → Actions*,
   créer `BACKEND_URL` (ex. `https://api.exemple.com`) et `INTERNAL_TOKEN` (même valeur que
   dans `.env`). Le workflow `.github/workflows/send-campaigns.yml` s'exécute chaque jour.
5. **RAG** : peupler la base du wiki puis calculer les embeddings :
   ```bash
   python manage.py seed
   python manage.py index_knowledge
   ```
6. **Compte administrateur** : `python manage.py createsuperuser` (ou les variables
   `DJANGO_SUPERUSER_*`), puis `https://<domaine>/admin/`.
7. **Sauvegardes** :
   ```bash
   docker compose exec db pg_dump -U antifake antifake | gzip > antifake-$(date +%F).sql.gz
   ```
   À planifier (cron) et à stocker hors de la machine.

---

## 5 bis. Dépôt GitHub

Le dépôt se crée depuis l'interface GitHub (*New repository*, sans README ni .gitignore), puis :
```bash
git remote add origin https://github.com/<compte>/<depot>.git
git push -u origin main
```
Git Credential Manager ouvre le navigateur pour l'authentification. La CI (`.github/workflows/ci.yml`)
s'exécute ensuite à chaque push : tests backend sur PostgreSQL et build du front.

Les fichiers `.env` ne sont pas suivis (voir `.gitignore`) ; seuls les modèles `.env.example` le sont.

## 6. Recette après déploiement

| # | Contrôle | Attendu |
|---|---|---|
| 1 | `GET /api/health/` | `{"status":"ok","database":"ok","cache":"ok"}` |
| 2 | Soumission texte depuis le téléphone | `202`, page d'analyse, statut final |
| 3 | Soumission d'un lien social | extraction + statue, éventuellement `partial` |
| 4 | Image > 5 Mo | refus immédiat « Image trop lourde » |
| 5 | 61 requêtes anonymes en une minute | la 61ᵉ renvoie `429` |
| 6 | Connexion Google | retour sur `/compte`, session active |
| 7 | Notification in-app | pastille dans « Mon compte » après une analyse |
| 8 | E-mail Brevo | expéditeur vérifié, message reçu |
| 9 | Installation PWA | icône sur l'écran d'accueil, ouverture plein écran |
| 10 | `/admin/` | accès réservé au rôle admin |

---

## 7. Ce qui reste hors du code

- **Validation juridique** de la politique de confidentialité et des durées de conservation :
  à faire par une personne compétente.
- **Google Cloud Vision** reste retiré : l'OCR passe par OCR.space puis la saisie manuelle.
- **WhatsApp** reste retiré ; l'instantané est assuré par Telegram et Web Push.
- **pgvector** n'est pas utilisé : les embeddings sont stockés en JSON et comparés en Python.
  Le jour où l'extension est disponible, seule la colonne change.
