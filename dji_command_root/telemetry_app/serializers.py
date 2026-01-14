import os
import json
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.conf import settings
from botocore.client import Config
import boto3

from .models import (
    Alarm,
    AlarmCategory,
    Wayline,
    UserProfile,
    ComponentConfig,
    WaylineImage,
    MediaFolderConfig,
    InspectTask,
    InspectImage,
    DronePosition,
    DockStatus,
    FlightTaskInfo,
)


# ======================================================================
# 🔥 [最终修正版] 解决 403 签名不匹配问题
# ======================================================================
def get_safe_presigned_url(bucket, key):
    """
    针对 Private 桶：使用外部 IP 初始化 Boto3 客户端进行签名，
    确保生成的签名与前端实际访问的 Host (公网IP) 一致。
    """
    if not key:
        return None

    try:
        # 1. 获取外部访问地址 (前端浏览器用的那个地址)
        # 例如: http://117.50.245.246:9000
        external_endpoint = os.getenv("MINIO_EXTERNAL_ENDPOINT", "http://127.0.0.1:9000")

        # 2. 专门创建一个客户端用于生成签名
        # 注意：这里 endpoint_url 直接填外部地址！
        # 虽然 Docker 内部连不上这个公网 IP，但 generate_presigned_url 是纯数学计算，不需要联网
        signer_client = boto3.client(
            "s3",
            endpoint_url=external_endpoint,  # 🔥 关键点：用公网 IP 签名
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name=getattr(settings, "MINIO_REGION", "us-east-1"),
            config=Config(signature_version="s3v4"),
        )

        # 3. 生成签名 URL
        # 此时生成的 URL 已经是 http://117.50.245.246:9000/... 且签名是匹配的
        url = signer_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=86400  # 1天有效
        )

        return url

    except Exception as e:
        print(f"❌ 生成签名 URL 失败: {e}")
        return None


# ======================================================================
# 👇 Serializers 定义
# ======================================================================

class WaylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wayline
        fields = [
            "id", "wayline_id", "name", "description", "waypoints",
            "length", "estimated_duration", "status", "created_by",
            "created_at", "updated_at", 'detect_type',
        ]


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AlarmCategorySerializer(serializers.ModelSerializer):
    sub_categories = RecursiveField(many=True, read_only=True)
    wayline_name = serializers.CharField(source='wayline.name', read_only=True)

    class Meta:
        model = AlarmCategory
        fields = [
            "id", "name", "code", "description", "parent",
            "sub_categories", "wayline", "wayline_name", "match_keyword"
        ]


class AlarmSerializer(serializers.ModelSerializer):
    category_details = AlarmCategorySerializer(source="category", read_only=True)
    wayline = WaylineSerializer(read_only=True)
    wayline_details = serializers.SerializerMethodField(read_only=True)
    image_signed_url = serializers.SerializerMethodField(read_only=True)

    def get_wayline_details(self, obj):
        if obj.wayline:
            return WaylineSerializer(obj.wayline, context=self.context).data
        return None

    def get_image_signed_url(self, obj):
        # 🔥 使用安全函数 (Bucket 默认为 dji)
        return get_safe_presigned_url(getattr(settings, "MINIO_BUCKET_NAME", "dji"), obj.image_url)

    class Meta:
        model = Alarm
        fields = [
            "id", "category", "category_details", "wayline", "wayline_details",
            "latitude", "longitude", "high", "content", "specific_data", "image_url",
            "image_signed_url", "status", "handler", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "category": {"write_only": True, "required": True},
        }


class WaylineImageSerializer(serializers.ModelSerializer):
    wayline_details = WaylineSerializer(source="wayline", read_only=True)
    image_signed_url = serializers.SerializerMethodField(read_only=True)

    def get_image_signed_url(self, obj):
        # 🔥 使用安全函数
        return get_safe_presigned_url(getattr(settings, "MINIO_BUCKET_NAME", "dji"), obj.image_url)

    class Meta:
        model = WaylineImage
        fields = [
            "id", "wayline", "wayline_details", "alarm", "image_url",
            "image_signed_url", "title", "description", "extra_data", "created_at",
        ]
        read_only_fields = ["created_at"]


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("id", "username", "name", "role", "is_active", "date_joined", "password")
        read_only_fields = ("date_joined",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if hasattr(instance, "profile"):
            ret["name"] = instance.profile.name
            ret["role"] = instance.profile.role
        else:
            ret["name"] = instance.username
            ret["role"] = "user"
        ret["createdAt"] = instance.date_joined
        return ret

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        if "username" in validated_data:
            instance.username = validated_data["username"]
        instance.save()

        name = validated_data.get("name")
        role = validated_data.get("role")
        if name or role:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            if name: profile.name = name
            if role: profile.role = role
            profile.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, default="user")

    class Meta:
        model = User
        fields = ("username", "name", "password", "role")

    def create(self, validated_data):
        name = validated_data.pop("name")
        role = validated_data.pop("role")
        password = validated_data.pop("password")
        user = User.objects.create_user(username=validated_data["username"], password=password)
        UserProfile.objects.create(user=user, name=name, role=role)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("用户名或密码错误")
        data["user"] = user
        return data


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ("key", "user")


class ComponentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentConfig
        fields = [
            "id", "serverUrl", "wssUrl", "hostUrl", "prjId", "projectToken",
            "userId", "workspaceId", "fh2_project_id", "extra_params",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "serverUrl": {"required": False, "allow_blank": True, "allow_null": True},
            "wssUrl": {"required": False, "allow_blank": True, "allow_null": True},
            "hostUrl": {"required": False, "allow_blank": True, "allow_null": True},
            "prjId": {"required": False, "allow_blank": True, "allow_null": True},
            "projectToken": {"required": False, "allow_blank": True, "allow_null": True},
            "userId": {"required": False, "allow_blank": True, "allow_null": True},
            "workspaceId": {"required": False, "allow_blank": True, "allow_null": True},
            "fh2_project_id": {"required": False, "allow_blank": True, "allow_null": True},
            "extra_params": {"required": False, "allow_null": True},
        }


class MediaFolderConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFolderConfig
        fields = ["id", "folder_path", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "folder_path": {"required": False, "allow_blank": True, "allow_null": True}
        }


class InspectTaskSerializer(serializers.ModelSerializer):
    wayline_details = WaylineSerializer(source='wayline', read_only=True)
    detect_category_name = serializers.CharField(source='detect_category.name', read_only=True)
    detect_category_code = serializers.CharField(source='detect_category.code', read_only=True)
    category_details = AlarmCategorySerializer(source='detect_category', read_only=True)
    parent_task_details = serializers.SerializerMethodField()
    sub_tasks_list = serializers.SerializerMethodField()  # 🔥 新增：子任务列表
    alarm_count = serializers.SerializerMethodField()
    total_images = serializers.SerializerMethodField()
    completed_images = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()  # 🔥 新增：统一显示名称
    is_parent_task = serializers.SerializerMethodField()  # 🔥 新增：是否为父任务

    class Meta:
        model = InspectTask
        fields = [
            'id', 'wayline', 'wayline_details', 'external_task_id', 'bucket', 'prefix_list',
            'started_at', 'finished_at', 'expire_at', 'detect_category', 'detect_category_name',
            'detect_category_code', 'category_details', 'detect_status', 'is_cleaned',
            'created_at', 'parent_task', 'parent_task_details', 'sub_tasks_list',
            'dji_task_uuid', 'dji_task_name', 'last_image_uploaded_at',
            'device_sn',
            'alarm_count',
            'total_images', 'completed_images',
            'display_name', 'is_parent_task',  # 🔥 新增字段
        ]
        read_only_fields = ['id', 'detect_status', 'is_cleaned', 'created_at', 'parent_task']

    def get_is_parent_task(self, obj):
        """判断是否为父任务（有子任务且没有真实路径）"""
        return obj.sub_tasks.exists() or (not obj.prefix_list or len(obj.prefix_list) == 0)

    def get_display_name(self, obj):
        """
        统一的显示名称
        - 父任务：显示 external_task_id (格式: 20250110巡检任务)
        - 子任务：优先显示 dji_task_name，其次 external_task_id
        """
        if self.get_is_parent_task(obj):
            # 父任务：显示日期+巡检任务
            return obj.external_task_id or f"{obj.created_at.strftime('%Y%m%d')}巡检任务"
        else:
            # 子任务：优先用户友好名称
            return obj.dji_task_name or obj.external_task_id or f"任务-{obj.id}"

    def get_parent_task_details(self, obj):
        if obj.parent_task:
            return {
                'id': obj.parent_task.id,
                'external_task_id': obj.parent_task.external_task_id,
                'display_name': self.get_display_name(obj.parent_task),
            }
        return None

    def get_sub_tasks_list(self, obj):
        """获取子任务列表（用于前端展示）"""
        if not obj.sub_tasks.exists():
            return []

        sub_tasks = obj.sub_tasks.all().order_by('-created_at')
        return [
            {
                'id': task.id,
                'external_task_id': task.external_task_id,
                'display_name': self.get_display_name(task),
                'detect_status': task.detect_status,
                'detect_category_name': task.detect_category.name if task.detect_category else None,
                'wayline_name': task.wayline.name if task.wayline else None,
                'device_sn': task.device_sn,
                'created_at': task.created_at,
            }
            for task in sub_tasks
        ]

    def get_alarm_count(self, obj):
        """
        统计任务的告警数量

        逻辑：
        1. 统计当前任务及其所有子任务的告警
        2. 只统计精确匹配的告警（通过 source_image__inspect_task_id）
        3. 不使用备用统计（避免重复计数）

        注意：
        - 一张图片可能产生多个告警（多种异常类型）
        - 所以 alarm_count 可能大于 total_images，这是正常的
        """
        # 获取任务ID列表（当前任务 + 所有子任务）
        ids = [obj.id] + list(obj.sub_tasks.values_list('id', flat=True))

        # 精确统计：只统计这些任务的告警
        cnt = Alarm.objects.filter(source_image__inspect_task_id__in=ids).count()

        return cnt

    def get_total_images(self, obj):
        # 父任务：统计所有子任务的图片
        if self.get_is_parent_task(obj):
            return InspectImage.objects.filter(inspect_task__in=obj.sub_tasks.all()).count()
        # 子任务：统计自己的图片
        return obj.images.count()

    def get_completed_images(self, obj):
        # 父任务：统计所有子任务的完成图片
        if self.get_is_parent_task(obj):
            return InspectImage.objects.filter(
                inspect_task__in=obj.sub_tasks.all(),
                detect_status='done'
            ).count()
        # 子任务：统计自己的完成图片
        return obj.images.filter(detect_status='done').count()


class InspectImageSerializer(serializers.ModelSerializer):
    """
    巡检图片序列化：返回带签名的安全 URL (Private Bucket 兼容)
    """
    signed_url = serializers.SerializerMethodField()
    result_signed_url = serializers.SerializerMethodField()
    inspect_task_details = InspectTaskSerializer(source="inspect_task", read_only=True)
    status01 = serializers.SerializerMethodField()
    result_info = serializers.SerializerMethodField()

    class Meta:
        model = InspectImage
        fields = [
            "id", "inspect_task", "inspect_task_details", "wayline", "object_key",
            "signed_url", "result_signed_url", "detect_status", "result",
            "result_info", "status01", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_signed_url(self, obj):
        # 🔥 使用安全函数
        return get_safe_presigned_url(obj.inspect_task.bucket, obj.object_key)

    def get_result_signed_url(self, obj):
        # 🔥 使用安全函数 (处理结果图)
        data = getattr(obj, "result", None) or {}
        result_key = data.get("result_object_key")
        return get_safe_presigned_url(obj.inspect_task.bucket, result_key)

    def get_result_info(self, obj):
        import json
        data = getattr(obj, "result", None)
        if data:
            return json.dumps(data, ensure_ascii=False)
        return None

    def get_status01(self, obj):
        """根据算法结果返回状态：None=未检测，0=正常，1=异常
        
        优先级：detection_status > defects_description
        原因：以算法明确给出的状态位为准
        """
        data = getattr(obj, "result", None)
        
        # ⭐ 关键修改：如果result为空或None，返回None表示未检测
        if not data or not isinstance(data, dict):
            return None
        
        # ⭐ 优先使用detection_status字段（算法明确给出的状态）
        if "detection_status" in data:
            try:
                return int(data.get("detection_status"))
            except:
                pass
        
        # 降级方案：检查defects_description
        defects = data.get("defects_description")
        if defects is None:
            return None  # 未检测
        
        # 有缺陷描述列表
        if isinstance(defects, (list, tuple)):
            return 1 if len(defects) > 0 else 0
        
        # 默认返回0（正常）
        return 0


class DronePositionSerializer(serializers.ModelSerializer):
    """
    无人机位置信息序列化器
    用于API返回和数据分析
    """
    class Meta:
        model = DronePosition
        fields = [
            "id", "device_sn", "device_model", "latitude", "longitude",
            "altitude", "relative_height", "heading", "speed_horizontal",
            "speed_vertical", "battery_percent", "signal_quality",
            "raw_data", "mqtt_topic", "timestamp", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


# ======================================================================
# 🏭 机场名称全局映射字典
# ======================================================================
class FlightTaskInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightTaskInfo
        fields = [
            "id", "task_uuid", "name", "sn", "wayline_id",
            "params", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


DOCK_NAME_MAPPING = {
    "8UUXN4900A052C": "工业大学机场",
    "8UUXN4R00A06Q6": "马贝机场",
}


def get_dock_display_name(dock_sn):
    """
    根据机场SN获取显示名称
    如果映射表中没有,返回 SN 本身
    """
    return DOCK_NAME_MAPPING.get(dock_sn, dock_sn)


class DockStatusSerializer(serializers.ModelSerializer):
    """
    机场状态序列化器
    用于API返回机场实时状态
    """
    storage_percent = serializers.SerializerMethodField()
    online_status = serializers.SerializerMethodField()
    power_status = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()  # 🔥 新增：统一显示名称

    class Meta:
        model = DockStatus
        fields = [
            "id", "dock_sn", "dock_name", "display_name", "latitude", "longitude", "height",
            "environment_temperature", "temperature", "humidity", "wind_speed", "rainfall",
            "mode_code", "cover_state", "putter_state", "supplement_light_state", "emergency_stop_state",
            "electric_supply_voltage", "working_voltage", "working_current",
            "backup_battery_voltage", "backup_battery_temperature", "backup_battery_switch",
            "drone_in_dock", "drone_charge_state", "drone_battery_percent", "drone_sn",
            "airport_push", "drone_push",
            "network_state_type", "network_quality", "network_rate",
            "storage_total", "storage_used", "storage_percent",
            "job_number", "acc_time", "activation_time",
            "alarm_state", "is_online", "online_status", "power_status",
            "last_update_time", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "storage_percent", "online_status", "power_status", "display_name"]

    def get_display_name(self, obj):
        """获取机场显示名称（优先使用映射表，其次使用 dock_name，最后使用 dock_sn）"""
        return get_dock_display_name(obj.dock_sn) if obj.dock_sn in DOCK_NAME_MAPPING else (obj.dock_name or obj.dock_sn)

    def get_storage_percent(self, obj):
        """计算存储使用百分比"""
        if obj.storage_total and obj.storage_total > 0:
            return round((obj.storage_used / obj.storage_total) * 100, 2)
        return 0

    def get_online_status(self, obj):
        """获取在线状态文本"""
        return "在线" if obj.is_online else "离线"

    def get_power_status(self, obj):
        """计算电源状态"""
        if obj.working_voltage and obj.working_current:
            power = (obj.working_voltage / 1000) * (obj.working_current / 1000)  # 转换为瓦特
            return round(power, 2)
        return 0
