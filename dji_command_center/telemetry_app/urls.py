from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入您在 views.py 中定义的 ViewSets
from .views import AlarmViewSet, AlarmTypeViewSet

# 1. 实例化路由器
router = DefaultRouter()

# 2. 注册您的 ViewSets
router.register(r'alarms', AlarmViewSet, basename='alarm')
router.register(r'alarmtypes', AlarmTypeViewSet, basename='alarmtype')

urlpatterns = [
    # 3. 将路由器生成的所有路由包含进来
    path('', include(router.urls)),
]