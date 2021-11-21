from django.contrib import admin

from notifier.models import InviteCode, NotificationFact

admin.site.register(InviteCode)
admin.site.register(NotificationFact)

