# telemetry_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlarmViewSet,
    AlarmCategoryViewSet,
    WaylineViewSet,
    WaylineImageViewSet,
    AuthViewSet,
    UserViewSet,
    ComponentConfigViewSet,
    MediaLibraryViewSet,
    InspectTaskViewSet,
)
from . import views
router = DefaultRouter()
router.register(r'alarms', AlarmViewSet)
router.register(r'alarm-categories', AlarmCategoryViewSet, basename='alarmcategory')
router.register(r'waylines', WaylineViewSet)
router.register(r'wayline-images', WaylineImageViewSet, basename='waylineimage')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'component-config', ComponentConfigViewSet, basename='componentconfig')
router.register(r'media-library', MediaLibraryViewSet, basename='media-library')
router.register(r'test/webhook', views.WebhookTestViewSet, basename='test-webhook')
router.register(r'inspect-tasks', InspectTaskViewSet, basename='inspect-task')
urlpatterns = [
    path('', include(router.urls)),
]
