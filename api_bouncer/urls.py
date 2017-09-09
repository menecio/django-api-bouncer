from django.conf.urls import include, url

from rest_framework.routers import SimpleRouter

from . import views


router = SimpleRouter()
router.register(r'apis', views.ApiViewSet)
router.register(r'acls', views.ConsumerACLViewSet)
router.register(r'consumers', views.ConsumerViewSet)
router.register(r'plugins', views.PluginViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', views.api_bouncer, name='api-bouncer'),
]
