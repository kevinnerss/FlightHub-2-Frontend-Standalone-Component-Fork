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
    LiveMonitorViewSet,
    DronePositionViewSet,
    FlightTaskProxyViewSet,
    FlightTaskInfoViewSet,
    DockStatusViewSet,
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
router.register(r'live-monitor', LiveMonitorViewSet, basename='live-monitor')
router.register(r'drone-positions', DronePositionViewSet, basename='drone-position')
router.register(r'flight-task-proxy', FlightTaskProxyViewSet, basename='flight-task-proxy')
router.register(r'flight-task-info', FlightTaskInfoViewSet, basename='flight-task-info')
router.register(r'dock-status', DockStatusViewSet, basename='dock-status')

urlpatterns = [
    path('scan_candidate_folders', views.scan_candidate_folders),
    path('start_selected_tasks', views.start_selected_tasks),
    path('stop_detect', views.stop_detect),
    path('', include(router.urls)),
]
