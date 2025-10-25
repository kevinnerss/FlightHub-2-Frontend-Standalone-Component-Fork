from rest_framework import viewsets
from .models import Alarm, AlarmType
from .serializers import AlarmSerializer, AlarmTypeSerializer

class AlarmTypeViewSet(viewsets.ModelViewSet):
    """告警类型管理（主要用于后台维护）"""
    queryset = AlarmType.objects.all()
    serializer_class = AlarmTypeSerializer
    # 通常不需要删除和修改，只读即可，根据需求调整权限

class AlarmViewSet(viewsets.ModelViewSet):
    """告警信息管理（增删改查）"""
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer

    # 如果需要过滤，可以在这里重写 get_queryset 方法
    # def get_queryset(self):
    #     queryset = Alarm.objects.all()
    #     status = self.request.query_params.get('status', None)
    #     if status is not None:
    #         queryset = queryset.filter(status=status)
    #     return queryset