from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'apis', views.ApiViewSet)
router.register(r'consumers', views.ConsumerViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
