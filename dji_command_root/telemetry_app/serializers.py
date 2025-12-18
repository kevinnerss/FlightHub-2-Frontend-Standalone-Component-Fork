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
            "latitude", "longitude", "content", "specific_data", "image_url",
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

    class Meta:
        model = InspectTask
        fields = [
            'id', 'wayline', 'wayline_details', 'external_task_id', 'bucket', 'prefix_list',
            'started_at', 'finished_at', 'expire_at', 'detect_category', 'detect_category_name',
            'detect_category_code', 'category_details', 'detect_status', 'is_cleaned',
            'created_at', 'parent_task', 'parent_task_details',
        ]
        read_only_fields = ['id', 'detect_status', 'is_cleaned', 'created_at', 'parent_task']

    def get_parent_task_details(self, obj):
        if obj.parent_task:
            return {
                'id': obj.parent_task.id,
                'external_task_id': obj.parent_task.external_task_id,
            }
        return None


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