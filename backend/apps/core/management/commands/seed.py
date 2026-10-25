"""Peuple la base locale de référence (MVP sans clés externes).

- Profils de sites (agences, médias, institutions, réseaux sociaux).
- Pages wiki publiées (pédagogie EMI, statuts, méthode).
- Fragments RAG pour la recherche « base propre ».
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.knowledge.models import KnowledgeChunk, SiteProfile, WikiPage

SITES = [
    ("afp.com", "AFP", "agency", 90, "Agence de presse internationale."),
    ("reuters.com", "Reuters", "agency", 90, "Agence de presse internationale."),
    ("apnews.com", "Associated Press", "agency", 90, "Agence de presse internationale."),
    ("who.int", "OMS", "institution", 85, "Organisation mondiale de la santé."),
    ("un.org", "Nations unies", "institution", 85, "Organisation des Nations unies."),
    ("prc.cm", "Présidence du Cameroun", "institution", 85, "Site officiel de la présidence."),
    ("minesec.gov.cm", "MINESEC", "institution", 85, "Ministère des Enseignements secondaires (Cameroun)."),
    ("mincom.gov.cm", "MINCOM", "institution", 85, "Ministère de la Communication (Cameroun)."),
    ("crtv.cm", "CRTV", "media", 80, "Média audiovisuel public camerounais."),
    ("cameroun-tribune.cm", "Cameroon Tribune", "media", 80, "Quotidien national camerounais."),
    ("lemonde.fr", "Le Monde", "media", 80, "Quotidien français."),
    ("rfi.fr", "RFI", "media", 80, "Radio France Internationale."),
    ("bbc.com", "BBC", "media", 80, "Média international."),
    ("facebook.com", "Facebook", "social", 30, "Réseau social."),
    ("x.com", "X (Twitter)", "social", 30, "Réseau social."),
    ("whatsapp.com", "WhatsApp", "social", 30, "Messagerie instantanée."),
    ("youtube.com", "YouTube", "social", 30, "Plateforme vidéo."),
    ("tiktok.com", "TikTok", "social", 30, "Réseau social vidéo."),
]

WIKI = [
    (
        "les-quatre-statuts",
        "Les quatre statuts d'une information",
        """La plateforme ne dit jamais si une information est « vraie » ou « fausse ». Elle classe le résultat d'une analyse selon quatre statuts :

- **Corroborée** : plusieurs sources indépendantes et fiables reprennent cette information, sans contradiction trouvée.
- **Non corroborée** : des traces existent, mais trop peu de sources fiables et indépendantes. Ce n'est pas un « faux ».
- **Contredite** : une vérification de faits publiée ou plusieurs sources fiables contredisent cette information.
- **Indéterminée** : pas assez d'éléments, analyse partielle, ou désaccord entre insiders.

Ce statut concerne l'information, jamais la personne qui l'a partagée. C'est une aide à la décision : c'est vous qui jugez, en ouvrant les sources.""",
    ),
    (
        "nature-et-desordre",
        "Nature de l'information et désordres de l'information",
        """En plus du statut, la plateforme affiche deux étiquettes pédagogiques distinctes :

**La nature de l'information**
- **Information** : un fait que l'on peut vérifier.
- **Opinion** : un jugement personnel, qui n'est ni vrai ni faux.
- **Rumeur** : une information non vérifiée qui circule.
- **Infox** : une information fausse ou trompeuse.

**Le désordre de l'information (pour une infox)**
- **Mésinformation** : fausse information partagée sans intention de nuire.
- **Désinformation** : fausse information créée avec l'intention de nuire.
- **Malinformation** : information vraie sortie de son contexte pour nuire.

Deux questions aident à raisonner : « Peut-on le vérifier ? » et « Y a-t-il une intention de nuire ? ».""",
    ),
    (
        "fiabilite-des-sources",
        "Comment évaluer la fiabilité d'une source",
        """La fiabilité d'une source dépend d'abord de sa nature :
- Agence de presse : 90
- Institution publique : 85
- Média d'information reconnu : 80
- Blog : 40
- Réseau social : 30
- Site inconnu : 20

Une information est d'autant mieux corroborée qu'elle est reprise par plusieurs sources **indépendantes** (une même dépêche reprise dix fois compte pour une seule source). La plateforme affiche la **plus ancienne trace trouvée**, jamais « la première apparition », car aucune API ne peut la garantir.""",
    ),
    (
        "comment-ca-marche",
        "Comment fonctionne la vérification",
        """1. Vous soumettez un texte, un lien ou une image.
2. La plateforme recherche des traces : recherche web, vérifications de faits déjà publiées, et sa base locale de sites déjà rencontrés.
3. Elle relève les dates et leur origine (déclarée, observée, métadonnée, indexation).
4. Elle calcule un statut à partir des sources trouvées, sans jamais trancher à votre place.

Ce site aide à vérifier : il ne prouve pas qu'une information est vraie.""",
    ),
]


class Command(BaseCommand):
    help = "Peuple la base locale de référence."

    def handle(self, *args, **options):
        for domain, name, nature, score, desc in SITES:
            SiteProfile.objects.update_or_create(
                domain=domain,
                defaults={"name": name, "nature": nature, "score": score, "description": desc},
            )
        self.stdout.write(f"{len(SITES)} profils de sites.")

        for slug, title, content in WIKI:
            page, _ = WikiPage.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "content": content,
                    "published": True,
                    # Pages de référence déjà validées : elles n'ont pas à apparaître
                    # dans la file « fiches à valider » de l'administration.
                    "review_status": WikiPage.ReviewStatus.APPROVED,
                    "reviewed_at": timezone.now(),
                },
            )
            KnowledgeChunk.objects.update_or_create(
                ref_type="wiki", ref_id=str(page.id),
                defaults={"url": "", "title": title, "content": content[:4000]},
            )
        self.stdout.write(f"{len(WIKI)} pages wiki + fragments RAG.")

        for domain, name, nature, score, desc in SITES:
            KnowledgeChunk.objects.get_or_create(
                ref_type="site", ref_id=domain,
                defaults={"url": f"https://{domain}", "title": name, "content": f"{name} ({domain}) — {desc}"},
            )
        self.stdout.write("Fragments RAG « site » créés.")
