"""Données de démonstration de `seed_demo`.

Adresses fictives réservées (RFC 2606 : `*.example.org`) : elles ne peuvent recevoir
aucun message réel. Aucun de ces comptes ne relie Telegram, l'application push ni
de numéro de téléphone : seuls les canaux e-mail et in-app sont représentés.

Les dossiers ci-dessous sont construits avec la vraie chaîne de statut
(`reliability.build_result`), donc les quatre statuts du dossier technique apparaissent
tels qu'une analyse réelle les produirait.
"""

# (email, nom, rôle)
DEMO_USERS = [
    ("amina.ngono@example.org", "Amina Nono", "insider"),
    ("blaise.ekani@example.org", "Blaise Ekani", "insider"),
    ("chantal.mvondo@example.org", "Chantal Mvondo", "insider"),
    ("yann.temguia@example.org", "Yann Temguia", "user"),
    ("flore.abega@example.org", "Flore Abéga", "user"),
    ("serge.ndongo@example.org", "Serge Ndongo", "user"),
]

# Demandes d'insider en attente (à traiter depuis l'espace administration).
DEMO_REQUESTS = [
    ("flore.abega@example.org", "Journaliste stagiaire, je vérifie quotidiennement des rumeurs "
     "circulant sur les groupes WhatsApp de mon quartier et je souhaite apporter mes sources."),
    ("serge.ndongo@example.org", "Étudiant en information-communication, je participe au club "
     "de fact-checking de mon université et je veux contribuer au wiki."),
]

# Fiches wiki proposées par des insiders, en attente de validation administrateur.
DEMO_WIKI_PENDING = [
    (
        "reconnaitre-un-deepfake",
        "Reconnaître une vidéo truquée (deepfake)",
        "Un deepfake est une vidéo modifiée par intelligence artificielle. Quatre réflexes :\n\n"
        "1. **Les lumières changeantes** : le visage clignote ou change de teinte là où la personne est remplacée.\n"
        "2. **La bouche et le son** : les lèvres ne suivent pas exactement les mots entendus.\n"
        "3. **Les Accessoires** : lunettes, bijoux ou dents artificielles peuvent fondre ou disparaître.\n"
        "4. **Le contexte** : cherchez d'abord la source originale de la vidéo, souvent plus ancienne.\n\n"
        "Une image truquée n'est pas « presque vraie » : elle ne peut pas servir de preuve.",
        "amina.ngono@example.org",
    ),
    (
        "desinformation-whatsapp",
        "Se protéger de la désinformation sur WhatsApp",
        "Les messages viral se propagent vite et sans source. Avant de relayer :\n\n"
        "- **Cherchez l'origine** : un message sans auteur, sans date et sans lien est un signal d'alerte.\n"
        "- **Comparez** : une information importante est reprise par plusieurs médias indépendants.\n"
        "- **Les chiffres ronds** : « 100 % », « tout le monde » méritent une vérification.\n\n"
        "En cas de doute, lancez une analyse sur la plateforme et partagez le lien du dossier "
        "plutôt que le message d'origine.",
        "blaise.ekani@example.org",
    ),
]

# Fiche wiki déjà publiée, écrite avant validation d'une première insider.
DEMO_WIKI_PUBLISHED = [
    (
        "lire-un-bulletin-meteorologique",
        "Lire un bulletin météorologique au Cameroun",
        "Les bulletins de la **Météo Cameroun** annoncent des pluies fortes par district. "
        "Deux précautions :\n\n"
        "- un bulletin porte sur **48 à 72 heures** : il ne confirme pas un événement passé ;\n"
        "- les alertes officielles passent par le **Ministère de la Communication** et les médias "
        "publics, jamais par une capture sans date.\n\n"
        "Pour vérifier une image d'inondation : cherchez la plus ancienne trace datée, puis "
        "ouvrez la source la plus fiable qui la reprend.",
        "chantal.mvondo@example.org",
    ),
]

# Fragments RAG supplémentaires (vérifications déjà publiées) : ils alimentent le chatbot.
DEMO_CHUNKS = [
    (
        "factcheck",
        "https://africacheck.org/fr/fact-checks",
        "Africa Check — vérifications publiées en français",
        "Africa Check publie des vérifications de faits sur l'Afrique : politique, santé, "
        "économie. Ses verdicts « Faux », « Trompeur » et « Exagéré » sont repris par la "
        "plateforme comme entrées du statut, jamais comme décision finale.",
    ),
    (
        "factcheck",
        "https://factuel.afp.com/",
        "AFP Fact Check — rubrique francophone",
        "L'AFP vérifie les affirmations qui circulent en ligne : images détournées de leur "
        "contexte, chiffres inventés, citations attribuées à de fausses personnes. Une "
        "vérification de l'AFP qui contredit une affirmation la classe « Contredite ».",
    ),
    (
        "factcheck",
        "https://www.who.int/fr/news-room/fact-sheets",
        "OMS — fiches d'information",
        "Les fiches de l'OMS servent de source institutionnelle (score 85) pour les questions "
        "de santé : épidémies, vaccins, nutrition. Elles datent et signent leurs mises à jour.",
    ),
    (
        "wiki",
        "",
        "Pourquoi une source unique ne suffit pas",
        "Une information reprise par dix sites qui recopient la même dépêche compte pour une "
        "seule source : l'indépendance se juge à la racine du domaine et à la rédaction, pas au "
        "nombre de liens. La plateforme affiche « Non corroborée » tant que deux sources "
        "indépendantes et fiables ne concordent pas.",
    ),
    (
        "wiki",
        "",
        "Distinguer opinion et information",
        "« Ce gouvernement est incompétent » est une opinion : elle n'est ni vraie ni fausse. "
        "« Le budget de l'éducation a augmenté de 12 % » est une information vérifiable. La "
        "plateforme classe la nature avant le statut, pour éviter de juger une opinion avec "
        "des outils de vérification de faits.",
    ),
    (
        "site",
        "https://www.crtv.cm",
        "CRTV — Média audiovisuel public camerounais",
        "crtv.cm (CRTV) — média d'information reconnu, score de base 80. Source utile pour les "
        "annonces officielles et les retransmissions ; à confronter toujours à une source "
        "indépendante.",
    ),
]

# Lecture d'insider sur un SITE : (domaine, email, verdict, statut proposé, commentaire, source)
SITE_READINGS = [
    # bbc.com : trois insiders certifient → avec 5 corroborations système, site certifié.
    ("bbc.com", "amina.ngono@example.org", "certify", "corroboree",
     "Média international, corrections publiées, sources citées dans chaque article.",
     "https://www.bbc.com/editorialguidelines"),
    ("bbc.com", "blaise.ekani@example.org", "certify", "corroboree",
     "Vérifications de faits régulières et signature des journalistes.",
     "https://www.bbc.com/news/reality_check"),
    ("bbc.com", "chantal.mvondo@example.org", "certify", "corroboree",
     "Régulièrement repris comme source indépendante dans nos dossiers.",
     "https://www.bbc.com/news/world-africa"),
    # crtV.cm : deux insiders certifient, un troisième reste nuancé → « en observation ».
    ("crtv.cm", "amina.ngono@example.org", "certify", "corroboree",
     "Source officielle pour les annonces publiques camerounaises.",
     "https://www.crtv.cm"),
    ("crtv.cm", "blaise.ekani@example.org", "certify", "corroboree",
     "Média public utile pour les communiqués, à recouper sur les sujets sensibles.",
     "https://www.crtv.cm"),
    ("crtv.cm", "chantal.mvondo@example.org", "certify", "non_corroboree",
     "Régulièrement juste sur les événements, mais peu de sources citées : je m'abstiens de corroborer.",
     "https://www.crtv.cm/info/contact"),
]

# Lecture d'insider sur un DOSSIER : (clé du dossier, email, verdict, statut proposé, commentaire, source)
ANALYSIS_READINGS = [
    ("gratuite-ecoles", "amina.ngono@example.org", "certify", "corroboree",
     "Circulaire officielle consultée et trois sources indépendantes concordantes.",
     "https://www.minesec.gov.cm"),
    ("gratuite-ecoles", "blaise.ekani@example.org", "certify", "corroboree",
     "Confirmé par la présidence et par un média international.",
     "https://www.prc.cm"),
    ("match-decede", "chantal.mvondo@example.org", "contest", "contredite",
     "Aucune source officielle ; la famille a démenti, la police a ouvert une enquête.",
     "https://africacheck.org/fr"),
    ("vaccin-particuliers", "amina.ngono@example.org", "certify", "non_corroboree",
     "Le post ne cite ni étude ni institution : on reste sur non corroboré, pas faux.",
     "https://www.who.int/fr/news-room/fact-sheets"),
    ("inondation-douala", "blaise.ekani@example.org", "certify", "indeterminee",
     "L'image est authentique mais ancienne : la date exacte reste à confirmer.",
     "https://www.crtv.cm"),
]

# Dossiers d'analyse de démonstration : sources, vérifications, modules manquants.
ANALYSES = [
    {
        "key": "gratuite-ecoles",
        "owner": "yann.temguia@example.org",
        "input_type": "text",
        "input_text": (
            "Le gouvernement du Cameroun annonce la gratuité totale des frais d'inscription "
            "dans les écoles publiques à partir de la rentrée de janvier."
        ),
        "days_ago": 6,
        "meta": {"source": "texte soumis", "keywords": ["gratuité", "inscription", "écoles"]},
        "missing": [],
        "sources": [
            {"url": "https://www.prc.cm/actualite/gratuite-inscription", "domain": "prc.cm",
             "title": "Gratuité de l'inscription confirmée pour la rentrée",
             "excerpt": "La présidence annonce la prise en charge des frais d'inscription dans les écoles publiques.",
             "type": "institution", "score": 85, "position": "corroborates",
             "date": "2026-10-18T09:00:00+00:00", "date_origin": "declared", "found_by": "Tavily"},
            {"url": "https://www.minesec.gov.cm/circulaire/inscription-2027", "domain": "minesec.gov.cm",
             "title": "Circulaire sur les frais d'inscription",
             "excerpt": "La circulaire ministérielle précise les écoles concernées et le calendrier.",
             "type": "institution", "score": 85, "position": "corroborates",
             "date": "2026-10-17T14:30:00+00:00", "date_origin": "declared", "found_by": "Serper"},
            {"url": "https://www.crtv.cm/info/gratuite-inscription-ecoles", "domain": "crtv.cm",
             "title": "La gratuité de l'inscription à la télévision publique",
             "excerpt": "Le CRTV reprend la circulaire et interroge des directeurs d'école.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-18T18:05:00+00:00", "date_origin": "observed", "found_by": "Serper"},
            {"url": "https://www.bbc.com/news/afrique-inscription-gratuite", "domain": "bbc.com",
             "title": "Cameroun : l'inscription rendue gratuite dans les écoles publiques",
             "excerpt": "Le média reprend l'annonce et demande le financement au ministère.",
             "type": "media", "score": 80, "position": "neutral",
             "date": "2026-10-19T07:12:00+00:00", "date_origin": "observed", "found_by": "Exa"},
        ],
        "factchecks": [],
    },
    {
        "key": "match-decede",
        "owner": "yann.temguia@example.org",
        "input_type": "text",
        "input_text": "Un stade rentrerait à pied après la finale de la coupe du Cameroun, mort à l'hôpital.",
        "days_ago": 3,
        "meta": {"source": "texte soumis", "keywords": ["stade", "finale", "décès"]},
        "missing": [],
        "sources": [
            {"url": "https://www.facebook.com/permalink.php?story_id=rumeur-stade", "domain": "facebook.com",
             "title": "Message viral sur un décès après la finale",
             "excerpt": "Partage sans source, sans date, circulant depuis plusieurs groupes.",
             "type": "social", "score": 30, "position": "neutral",
             "date": None, "date_origin": "", "found_by": "Tavily"},
            {"url": "https://sport-anonyme.blogspot.com/2026/10/finale", "domain": "sport-anonyme.blogspot.com",
             "title": "Blog sportif reprenant la rumeur",
             "excerpt": "Article sans auteur ni signature, copié d'un message de groupe.",
             "type": "blog", "score": 40, "position": "neutral",
             "date": "2026-10-22T21:40:00+00:00", "date_origin": "indexation", "found_by": "Tavily"},
        ],
        "factchecks": [
            {"organization": "Africa Check", "verdict": "Faux : aucune mort signalée, l'image est ancienne",
             "url": "https://africacheck.org/fr/fact-checks/match-finale", "published_date": "2026-10-23",
             "summary": "L'image d'un joueur allongé vient d'un match de 2019.",
             "contradicts": True},
            {"organization": "AFP Fact Check", "verdict": "Trompeur : photo détournée de son contexte",
             "url": "https://factuel.afp.com/photo-match-2019", "published_date": "2026-10-23",
             "summary": "La photo est authentique mais date de 2019.",
             "contradicts": True},
        ],
    },
    {
        "key": "vaccin-particuliers",
        "owner": "flore.abega@example.org",
        "input_type": "link",
        "input_url": "https://www.facebook.com/share/p/19mNQfz7Mh/",
        "days_ago": 2,
        "meta": {
            "source": "post social",
            "platform": "facebook",
            "author": "Compte sans identité vérifiée",
            "title": "Un vaccin vendu uniquement aux particuliers",
            "keywords": ["vaccin", "particuliers", "achat"],
        },
        "missing": [],
        "sources": [
            {"url": "https://sante-decouverte.blogspot.com/2026/10/vaccin", "domain": "sante-decouverte.blogspot.com",
             "title": "Blog santé reprenant l'affirmation",
             "excerpt": "Auteur anonyme, aucun lien vers une étude ou une institution.",
             "type": "blog", "score": 40, "position": "neutral",
             "date": "2026-10-23T11:00:00+00:00", "date_origin": "indexation", "found_by": "Tavily"},
            {"url": "https://x.com/status/1234567890", "domain": "x.com",
             "title": "Publication reprenant le même texte",
             "excerpt": "Message partagé 400 fois, sans source.",
             "type": "social", "score": 30, "position": "neutral",
             "date": None, "date_origin": "", "found_by": "Serper"},
        ],
        "factchecks": [],
    },
    {
        "key": "ligne-tramway",
        "owner": "serge.ndongo@example.org",
        "input_type": "text",
        "input_text": "La troisième ligne de tramway de Yaoundé ouvrirait avant fin 2026.",
        "days_ago": 1,
        "meta": {"source": "texte soumis", "keywords": ["tramway", "Yaoundé", "ouverture"]},
        "missing": [
            {"service": "recherche de texte", "reason": "Aucun moteur n'a répondu dans le budget."},
            {"service": "Google Fact Check Tools", "reason": "Vérifications de faits indisponibles."},
        ],
        "sources": [],
        "factchecks": [],
    },
    {
        "key": "inondation-douala",
        "owner": "yann.temguia@example.org",
        "input_type": "image",
        "input_thumb": "seed",
        "days_ago": 4,
        "meta": {
            "source": "image",
            "ocr_text": "DOUALA — les eaux montent dans le quartier Bonabéri, marché fermé",
            "ocr_engine": "OCR.space",
            "phash": "1184739205847392",
            "image_search": "Apify (Google Lens)",
            "keywords": ["Douala", "inondation", "Bonabéri"],
        },
        "missing": [],
        "sources": [
            {"url": "https://www.bbc.com/news/afrique-douala-inondation", "domain": "bbc.com",
             "title": "Inondations à Douala : le bilan des autorités",
             "excerpt": "Les pluies de la semaine ont fermé le marché de Bonabéri.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-21T16:20:00+00:00", "date_origin": "observed", "found_by": "Apify (Google Lens)"},
            {"url": "https://www.crtv.cm/info/inondation-bonaberi", "domain": "crtv.cm",
             "title": "Bonabéri : le marché fermé après les pluies",
             "excerpt": "Reportage sur place avec les commerçants.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-21T19:00:00+00:00", "date_origin": "observed", "found_by": "Serper"},
            {"url": "https://www.imprimerie-douala-cm.net/2026/10/photos-inondation", "domain": "imprimerie-douala-cm.net",
             "title": "Photos relayées d'un autre quartier",
             "excerpt": "La photo circule depuis 2023 : contexte à vérifier.",
             "type": "unknown", "score": 20, "position": "neutral",
             "date": "2026-10-22T08:00:00+00:00", "date_origin": "indexation", "found_by": "Recherche d'image"},
        ],
        "factchecks": [],
    },
    {
        "key": "securite-alimentaire",
        "owner": "flore.abega@example.org",
        "input_type": "link",
        "input_url": "https://www.rfi.fr/fr/afrique/securite-alimentaire-cameroun",
        "days_ago": 5,
        "meta": {
            "source": "article",
            "author": "RFI Afrique",
            "title": "Sécurité alimentaire : le Cameroun améliore son suivi des récoltes",
            "date": "2026-10-20",
            "date_origin": "metadata",
            "keywords": ["sécurité alimentaire", "récoltes", "Cameroun"],
        },
        "missing": [],
        "sources": [
            {"url": "https://www.rfi.fr/fr/afrique/securite-alimentaire-cameroun", "domain": "rfi.fr",
             "title": "Sécurité alimentaire : le Cameroun améliore son suivi des récoltes",
             "excerpt": "Le ministère de l'Agriculture présente un nouveau système de suivi.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-20T10:00:00+00:00", "date_origin": "metadata", "found_by": "Exa"},
            {"url": "https://www.afp.com/fr/actus/securite-alimentaire", "domain": "afp.com",
             "title": "Sécurité alimentaire en Afrique centrale",
             "excerpt": "L'agence publie les chiffres officiels de la FAO.",
             "type": "agency", "score": 90, "position": "corroborates",
             "date": "2026-10-19T22:15:00+00:00", "date_origin": "observed", "found_by": "Tavily"},
            {"url": "https://www.bbc.com/news/afrique-securite-alimentaire", "domain": "bbc.com",
             "title": "Les récoltes suivies de plus près au Cameroun",
             "excerpt": "Le média reprend les chiffres de la FAO et interroge des ONG.",
             "type": "media", "score": 80, "position": "neutral",
             "date": "2026-10-20T12:40:00+00:00", "date_origin": "observed", "found_by": "Serper"},
        ],
        "factchecks": [],
    },
    {
        "key": "elections-reportees",
        "owner": "serge.ndongo@example.org",
        "input_type": "text",
        "input_text": "Les élections municipales de 2027 sont confirmées pour mars 2027, selon le calendrier officiel.",
        "days_ago": 2,
        "meta": {"source": "texte soumis", "keywords": ["élections", "municipales", "calendrier"]},
        "missing": [],
        "sources": [
            {"url": "https://www.prc.cm/actualite/calendrier-electoral", "domain": "prc.cm",
             "title": "Le calendrier électoral reste inchangé",
             "excerpt": "La Commission électorale confirme le calendrier publié en 2026.",
             "type": "institution", "score": 85, "position": "corroborates",
             "date": "2026-10-23T10:00:00+00:00", "date_origin": "declared", "found_by": "Tavily"},
            {"url": "https://www.bbc.com/news/afrique-cameroun-elections", "domain": "bbc.com",
             "title": "Cameroun : le calendrier électoral contesté",
             "excerpt": "Le média rappelle la date officielle des municipales.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-23T15:30:00+00:00", "date_origin": "observed", "found_by": "Exa"},
            {"url": "https://www.lemonde.fr/afrique/article/cameroun-elections.html", "domain": "lemonde.fr",
             "title": "Au Cameroun, le calendrier électoral rassure les partis",
             "excerpt": "Les partis d'opposition saluent la publication du calendrier.",
             "type": "media", "score": 80, "position": "neutral",
             "date": "2026-10-23T20:10:00+00:00", "date_origin": "observed", "found_by": "Serper"},
            {"url": "https://www.crtv.cm/info/municipales-2027", "domain": "crtv.cm",
             "title": "Municipales 2027 : le calendrier publié",
             "excerpt": "Le média public retransmet la annonce de la Commission électorale.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-23T12:00:00+00:00", "date_origin": "observed", "found_by": "Serper"},
        ],
        "factchecks": [],
    },
    {
        "key": "paludisme-traitement",
        "owner": "serge.ndongo@example.org",
        "input_type": "text",
        "input_text": "Un nouveau traitement du paludisme grave serait disponible dans les hôpitaux camerounais depuis octobre.",
        "days_ago": 7,
        "meta": {"source": "texte soumis", "keywords": ["paludisme", "traitement", "hôpitaux"]},
        "missing": [],
        "sources": [
            {"url": "https://www.who.int/fr/news/item/traitement-paludisme-cameroun", "domain": "who.int",
             "title": "OMS : déploiement d'un traitement dans les hôpitaux",
             "excerpt": "La fiche officielle détaille les protocoles et les provinces concernées.",
             "type": "institution", "score": 85, "position": "corroborates",
             "date": "2026-10-17T08:00:00+00:00", "date_origin": "declared", "found_by": "Tavily"},
            {"url": "https://apnews.com/article/cameroun-paludisme", "domain": "apnews.com",
             "title": "Le Cameroun généralise un traitement antipaludique",
             "excerpt": "L'agence cite le ministère de la Santé et des médecins hospitaliers.",
             "type": "agency", "score": 90, "position": "corroborates",
             "date": "2026-10-17T13:45:00+00:00", "date_origin": "observed", "found_by": "Serper"},
            {"url": "https://www.bbc.com/news/afrique-paludisme-cameroun", "domain": "bbc.com",
             "title": "Cameroun : un traitement antipaludique étendu",
             "excerpt": "Le média reprend les chiffres de l'OMS et interroge des cliniciens.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-18T06:30:00+00:00", "date_origin": "observed", "found_by": "Exa"},
            {"url": "https://www.crtv.cm/info/traitement-paludisme", "domain": "crtv.cm",
             "title": "Le nouveau traitement arrive dans les hôpitaux",
             "excerpt": "Reportage dans un hôpital de Yaoundé avec le personnel soignant.",
             "type": "media", "score": 80, "position": "corroborates",
             "date": "2026-10-18T17:20:00+00:00", "date_origin": "observed", "found_by": "Serper"},
        ],
        "factchecks": [],
    },
    {
        "key": "prix-huile",
        "owner": "yann.temguia@example.org",
        "input_type": "text",
        "input_text": "Le prix de l'huile de palme a doublé en un mois sur les marchés du Sud-Ouest.",
        "days_ago": 1,
        "meta": {"source": "texte soumis", "keywords": ["huile de palme", "prix", "Sud-Ouest"]},
        "missing": [
            {"service": "Tavily — recherche web", "reason": "quota épuisé"},
            {"service": "SearchApi.io", "reason": "indisponible (coupe-circuit)"},
        ],
        "sources": [
            {"url": "https://marche-bafoussam-cm.blogspot.com/2026/10/huile", "domain": "marche-bafoussam-cm.blogspot.com",
             "title": "Commerçants parlent d'une hausse",
             "excerpt": "Témoignages sans chiffres ni date de relevé.",
             "type": "blog", "score": 40, "position": "neutral",
             "date": None, "date_origin": "", "found_by": "base propre"},
        ],
        "factchecks": [],
    },
]

# Consommation du mois en cours (compte fournisseur → utilisé). Sert à rendre la
# table des quotas de l'administration visible avant le premier appel réel.
QUOTA_USAGE = {
    "tavily": (42, 1000),
    "serper": (28, 2500),
    "serpapi": (6, 100),
    "searchapi": (3, 100),
    "exa": (11, 1000),
    "factcheck": (17, 0),
    "ocrspace": (9, 25000),
    "apify_lens": (2, 0),
    "groq": (64, 0),
    "gemini": (35, 0),
}

# Campagnes de sensibilisation (M13) : (titre, corps, canal, statut)
CAMPAIGNS = [
    ("Vérifier avant de partager : les cinq réflexes",
     "1. Lisez l'article entier avant de partager. 2. Vérifiez la date. 3. Cherchez la source "
     "originale. 4. Comparez avec deux médias indépendants. 5. En cas de doute, lancez une "
     "analyse sur InfoxVerify et partagez le lien du dossier.",
     "email", "approved"),
    ("Ateliers de vérification dans les lycées",
     "Inscriptions ouvertes pour les ateliers de vérification de l'information, chaque samedi "
     "de novembre, dans les lycées de Yaoundé et Douala.",
     "email", "draft"),
]

# Notifications in-app (cloche) : (email, titre, corps, non lu)
NOTIFICATIONS = [
    ("yann.temguia@example.org", "Analyse terminée",
     "Analyse gratuite-ecoles : Corroborée. Ouvrir le dossier pour voir les sources.", True),
    ("yann.temguia@example.org", "Analyse terminée",
     "Analyse match-decede : Contredite. Deux vérifications de faits contredisent l'information.", True),
    ("amina.ngono@example.org", "Proposition wiki en attente",
     "Votre fiche « Reconnaître une vidéo truquée (deepfake) » est en attente de validation.", True),
]
