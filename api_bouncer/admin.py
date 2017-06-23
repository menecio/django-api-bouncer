from django.contrib import admin

from .models import (
    Api,
    Consumer,
    ConsumerKey,
)


class ApiAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'upstream_url')


class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'username')


class ConsumerKeyAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'key')


admin.site.register(Api, ApiAdmin)
admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(ConsumerKey, ConsumerKeyAdmin)
