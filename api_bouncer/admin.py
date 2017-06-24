from django.contrib import admin

from .models import (
    Api,
    Consumer,
    ConsumerKey,
    Plugin,
)


class ApiAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'upstream_url')


class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'username')


class ConsumerKeyAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'key')


class PluginAdmin(admin.ModelAdmin):
    list_display = ('api', 'name')


admin.site.register(Api, ApiAdmin)
admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(ConsumerKey, ConsumerKeyAdmin)
admin.site.register(Plugin, PluginAdmin)
