from django.contrib import admin

from .models import AwarenessCampaign, Notification

admin.site.register(Notification)
admin.site.register(AwarenessCampaign)
