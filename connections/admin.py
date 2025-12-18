from django.contrib import admin

from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['from_user','to_user','type','time','text']
    list_filter = ['from_user','to_user','type']
    search_fields = ['type']

admin.site.register(Notification,NotificationAdmin)

