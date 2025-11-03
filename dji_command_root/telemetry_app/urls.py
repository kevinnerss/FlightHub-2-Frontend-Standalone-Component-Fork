# telemetry_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入所有 ViewSet
from .views import AlarmViewSet, AlarmCategoryViewSet, WaylineViewSet

router = DefaultRouter()
router.register(r'alarms', AlarmViewSet)
router.register(r'alarm-categories', AlarmCategoryViewSet, basename='alarmcategory')
router.register(r'waylines', WaylineViewSet)  # 注册航线视图集

urlpatterns = [
    path('', include(router.urls)),
]