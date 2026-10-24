from django.contrib import admin

from .models import Analysis, Certification, FactCheck, MissingService, Source

admin.site.register(Analysis)
admin.site.register(Source)
admin.site.register(FactCheck)
admin.site.register(Certification)
admin.site.register(MissingService)
