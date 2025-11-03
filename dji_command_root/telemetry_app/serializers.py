from rest_framework import serializers
from .models import Alarm, AlarmCategory, Wayline  # 导入新的 AlarmCategory 和 Wayline


# --- 1. 航线序列化器 --- 移到前面以避免循环引用问题

class WaylineSerializer(serializers.ModelSerializer):
    """
    序列化航线信息
    """
    
    class Meta:
        model = Wayline
        fields = [
            'id',
            'wayline_id',
            'name',
            'description',
            'waypoints',
            'length',
            'estimated_duration',
            'status',
            'created_by',
            'created_at',
            'updated_at'
        ]


# --- 2. 告警类型序列化器 (层级结构) ---

class RecursiveField(serializers.Serializer):
    """用于显示无限层级的子分类 (sub_categories)"""

    def to_representation(self, value):
        # 使用父序列化器 (AlarmCategorySerializer) 来序列化子项
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AlarmCategorySerializer(serializers.ModelSerializer):
    """
    序列化告警类型 (层级结构)
    """
    # 动态地包含所有子类型
    sub_categories = RecursiveField(many=True, read_only=True)

    class Meta:
        model = AlarmCategory  # 对应新的 model
        fields = [
            'id', 'name', 'code', 'description',
            'parent',  # 父类型的 ID
            'sub_categories'  # 嵌套显示的子类型列表
        ]


# --- 3. 告警信息序列化器 ---

class AlarmSerializer(serializers.ModelSerializer):
    """
    序列化告警信息
    """

    # 优化：用于 "读" (GET)
    # 不再只是一个 'type_name'，而是显示完整的告警类型详细信息
    category_details = AlarmCategorySerializer(source='category', read_only=True)
    
    # 新增：直接在返回数据中包含wayline信息，方便前端使用
    wayline = WaylineSerializer(read_only=True)
    
    # 新增：兼容旧版API的字段名
    wayline_details = serializers.SerializerMethodField(read_only=True)
    
    def get_wayline_details(self, obj):
        # 为了向后兼容，保留wayline_details字段
        if obj.wayline:
            return WaylineSerializer(obj.wayline, context=self.context).data
        return None

    class Meta:
        model = Alarm
        fields = [
            'id',
            'category',  # 用于 "写" (POST/PUT)，期望一个 AlarmCategory 的 ID
            'category_details',  # 用于 "读" (GET)，显示上面定义的嵌套信息
            'wayline',  # 现在同时支持读写，读取时返回完整的wayline对象
            'wayline_details',  # 用于向后兼容旧版API
            'latitude',
            'longitude',
            'content',
            'specific_data',  # JSON 字段，用于存储特定数据
            'image_url',
            'status',
            'handler',
            'created_at',
            'updated_at'
        ]

        # 'category_details' 和 'wayline' 已经是 read_only=True
        read_only_fields = ['created_at', 'updated_at']

        # 关键优化：
        # 1. 'category' 字段是只写的 (write_only)。
        # 2. 这意味着当您 POST 或 PUT 数据时，您只需要提供 'category': 5 (ID)。
        # 3. 当您 GET 数据时，您会看到完整的 'wayline' 对象信息。
        extra_kwargs = {
            'category': {'write_only': True, 'required': True}  # 类别关联是必须的
            # wayline不再需要额外的write_only配置，DRF会处理好读写关系
        }