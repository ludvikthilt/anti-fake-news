from django.contrib import admin

from .models import KnowledgeChunk, SiteProfile, WikiPage, WikiRevision

admin.site.register(SiteProfile)
admin.site.register(KnowledgeChunk)
admin.site.register(WikiPage)
admin.site.register(WikiRevision)
