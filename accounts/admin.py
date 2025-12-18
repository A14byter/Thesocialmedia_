

from django.contrib import admin

from .models import Device,Page,Profile

class PageAdmin(admin.ModelAdmin):
    list_display = ['user_name','biography','avatar','is_private']
    list_filter=['user_name']
    search_fields=['user_name']

admin.site.register(Page,PageAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phone_number','location','device']
    list_filter = ['user']

admin.site.register(Profile,ProfileAdmin)