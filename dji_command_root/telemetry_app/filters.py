# telemetry_app/filters.py
import django_filters
from .models import Alarm, AlarmCategory


class AlarmFilter(django_filters.FilterSet):
    """
    自定义告警信息的过滤器
    """

    # --- 多表筛选 (核心) ---
    # 1. 允许通过 告警类型的名称 模糊查询
    category_name = django_filters.CharFilter(
        field_name='category__name',  # 使用 'category__name' 进行跨表查询
        lookup_expr='icontains',  # 'icontains' = 忽略大小写的模糊匹配
        label='告警类型名称 (模糊)'
    )

    # 2. 允许通过 告警类型的代码 精确查询
    category_code = django_filters.CharFilter(
        field_name='category__code',  # 跨表
        lookup_expr='exact',  # 'exact' = 精确匹配
        label='告警类型代码 (精确)'
    )

    # --- 条件查询 (日期范围) ---
    # 3. 允许查询 "某个时间点之后" 创建的告警
    start_date = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',  # 'gte' = greater than or equal (大于等于)
        label='创建时间 (晚于等于)'
    )

    # 4. 允许查询 "某个时间点之前" 创建的告警
    end_date = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',  # 'lte' = less than or equal (小于等于)
        label='创建时间 (早于等于)'
    )

    # --- 条件查询 (状态) ---
    # 5. 允许通过 状态 字段精确查询
    status = django_filters.ChoiceFilter(
        choices=Alarm.STATUS_CHOICES,
        label='告警状态'
    )

    # 6. 允许通过 航线ID 模糊查询 (使用外键关系)
    wayline_id = django_filters.CharFilter(
        field_name='wayline__wayline_id',
        lookup_expr='icontains',  # 忽略大小写的模糊匹配
        label='航线ID (模糊)'
    )
    
    # 7. 允许通过 航线名称 模糊查询
    wayline_name = django_filters.CharFilter(
        field_name='wayline__name',
        lookup_expr='icontains',
        label='航线名称 (模糊)'
    )
    
    # 8. 允许通过 航线 对象ID 精确查询
    wayline = django_filters.NumberFilter(
        field_name='wayline',
        lookup_expr='exact',
        label='航线ID (精确)'
    )

    class Meta:
        model = Alarm
        # 'fields' 列表包含最简单的过滤器 (DRF 会自动推断类型)
        fields = [
            'status',  # 我们在上面自定义了, 但在这里声明更清晰
            'handler',  # 允许 ?handler=张三 (精确匹配)
            'category',  # 允许 ?category=5 (按 告警类型ID 精确匹配)
            'wayline',  # 允许 ?wayline=1 (按航线对象ID精确匹配)
            'wayline_id',  # 允许 ?wayline_id=WL001 (按航线ID模糊匹配)
            'wayline_name',  # 允许 ?wayline_name=测试航线 (按航线名称模糊匹配)
            'start_date',
            'end_date',
            'category_name',
            'category_code',
        ]