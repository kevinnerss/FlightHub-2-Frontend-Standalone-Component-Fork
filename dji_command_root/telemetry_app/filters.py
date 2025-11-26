# telemetry_app/filters.py
import django_filters
from .models import Alarm, AlarmCategory, WaylineImage


class AlarmFilter(django_filters.FilterSet):
    """告警信息过滤器"""

    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    category_code = django_filters.CharFilter(
        field_name='category__code',
        lookup_expr='exact'
    )
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Alarm.STATUS_CHOICES)
    wayline_id = django_filters.CharFilter(field_name='wayline__wayline_id', lookup_expr='icontains')
    wayline_name = django_filters.CharFilter(field_name='wayline__name', lookup_expr='icontains')
    wayline = django_filters.NumberFilter(field_name='wayline', lookup_expr='exact')

    class Meta:
        model = Alarm
        fields = [
            'status', 'handler', 'category', 'wayline', 'wayline_id', 'wayline_name',
            'start_date', 'end_date', 'category_name', 'category_code'
        ]


class WaylineImageFilter(django_filters.FilterSet):
    """航线图片过滤器"""

    wayline = django_filters.NumberFilter(field_name='wayline', lookup_expr='exact')
    wayline_id = django_filters.CharFilter(field_name='wayline__wayline_id', lookup_expr='exact')

    class Meta:
        model = WaylineImage
        fields = ['wayline', 'wayline_id']
