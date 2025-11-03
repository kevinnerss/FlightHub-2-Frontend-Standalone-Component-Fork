from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Alarm, AlarmCategory, Wayline
from .serializers import AlarmSerializer, AlarmCategorySerializer, WaylineSerializer
from .filters import AlarmFilter  # 导入我们定义的过滤器


# 导入分页（如果您在 settings.py 中全局配置了，则此处非必需）
# from .pagination import StandardResultsSetPagination


class AlarmCategoryViewSet(viewsets.ModelViewSet):
    """
    告警类型管理（主要用于后台维护）
    - 已更新为层级的 AlarmCategory
    """
    queryset = AlarmCategory.objects.all()
    serializer_class = AlarmCategorySerializer
    # 备注：为了优化，对于层级结构，
    # 您可能希望只返回顶层类型 (parent=None)
    # queryset = AlarmCategory.objects.filter(parent__isnull=True)


class AlarmViewSet(viewsets.ModelViewSet):
    """
    告警信息管理（增删改查）
    - 支持分页 (在 settings.py 中配置)
    - 支持高级条件过滤 (查看 filters.py)
    - 支持 ?search= 模糊搜索
    - 支持 ?ordering= 排序
    """

    # 1. 优化 Queryset (非常重要)
    #    使用 select_related 预加载 'category' 和 'wayline'，防止 N+1 查询
    queryset = Alarm.objects.select_related('category', 'wayline').all()

    serializer_class = AlarmSerializer

    # pagination_class = StandardResultsSetPagination # (如果需要自定义分页, 在此指定)

    # 2. 挂载所有过滤器后端
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # --- 过滤器配置 ---

    # 3. (django-filter) 挂钩我们自定义的 AlarmFilter 类
    #    这会启用 ?status=PENDING, ?category_name=裂纹, ?start_date=... 等
    filterset_class = AlarmFilter

    # 4. (SearchFilter) 配置模糊搜索的字段
    #    这会启用 ?search=轨道 ...
    search_fields = [
        'content',  # 搜索告警内容
        'handler',  # 搜索处理人
        'category__name',  # 跨表搜索类型名称
        'category__code',  # 跨表搜索类型代码
        'wayline__wayline_id',  # 跨表搜索航线ID
        'wayline__name',  # 跨表搜索航线名称
        'specific_data'  # 搜索 JSON 字段 (取决于数据库支持)
    ]

    # 5. (OrderingFilter) 配置允许排序的字段
    #    这会启用 ?ordering=-created_at ...
    ordering_fields = ['created_at', 'updated_at', 'status']


class WaylineViewSet(viewsets.ModelViewSet):
    """
    航线信息管理（增删改查）
    - 支持分页
    - 支持搜索
    - 支持排序
    """
    queryset = Wayline.objects.all()
    serializer_class = WaylineSerializer
    
    # 挂载过滤器后端
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # 配置搜索字段
    search_fields = ['wayline_id', 'name', 'description', 'created_by']
    
    # 配置排序字段
    ordering_fields = ['created_at', 'updated_at', 'status', 'name']
    
    # 默认排序
    ordering = ['-created_at']

    # 6. get_queryset (可选)
    #    由于 django-filter 已经接管了过滤，这个函数现在可以保持简单，
    #    或者用于处理更复杂的、基于用户权限的过滤。
    #    您之前写的过滤逻辑 (按 status, category_id) 已被 filterset_class 替代。
    def get_queryset(self):
        # 过滤器会基于这个 super().get_queryset() 返回的结果进行筛选
        queryset = super().get_queryset()

        # 示例：如果需要，您可以在此添加 *额外* 逻辑，
        # 例如：只返回该用户相关的告警
        # if self.request.user.is_authenticated:
        #     queryset = queryset.filter(handler=self.request.user.username)

        return queryset