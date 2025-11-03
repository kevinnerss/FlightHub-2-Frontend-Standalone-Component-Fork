# telemetry_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 1. 导入新的 ViewSet 名称
from .views import AlarmViewSet, AlarmCategoryViewSet

router = DefaultRouter()
router.register(r'alarms', AlarmViewSet)
# 2. 注册新的 ViewSet 名称
router.register(r'alarm-categories', AlarmCategoryViewSet, basename='alarmcategory')
# (推荐将 URL 也改为 'alarm-categories' 以保持一致)

urlpatterns = [
    path('', include(router.urls)),
]