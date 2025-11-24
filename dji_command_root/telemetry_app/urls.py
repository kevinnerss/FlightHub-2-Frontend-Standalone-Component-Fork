# telemetry_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入所�?ViewSet
from .views import AlarmViewSet, AlarmCategoryViewSet, WaylineViewSet, AuthViewSet, UserViewSet, ComponentConfigViewSet

router = DefaultRouter()
router.register(r'alarms', AlarmViewSet)
router.register(r'alarm-categories', AlarmCategoryViewSet, basename='alarmcategory')
router.register(r'waylines', WaylineViewSet)  # 注册航线视图�?
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'component-config', ComponentConfigViewSet, basename='componentconfig')

urlpatterns = [
    path('', include(router.urls)),
]
