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


def get_minio_client():
    """
    统一创建一个 MinIO(S3) 客户端，方便复用。
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name=getattr(settings, "MINIO_REGION", "us-east-1"),
        config=Config(signature_version="s3v4"),
    )


class WaylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wayline
        fields = [
            "id",
            "wayline_id",
            "name",
            "description",
            "waypoints",
            "length",
            "estimated_duration",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            'detect_type',
        ]


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AlarmCategorySerializer(serializers.ModelSerializer):
    """
    告警类型序列化 (已更新：包含自动任务配置字段)
    """
    sub_categories = RecursiveField(many=True, read_only=True)
    # 方便前端显示绑定的航线名称
    wayline_name = serializers.CharField(source='wayline.name', read_only=True)

    class Meta:
        model = AlarmCategory
        fields = [
            "id",
            "name",
            "code",
            "description",
            "parent",
            "sub_categories",

            # ⭐ 新增配置字段 (用于前端配置自动任务)
            "wayline",
            "wayline_name",
            "match_keyword"
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
        """
        根据 image_url 存的 MinIO object key 生成一个临时可访问的 URL
        """
        if not obj.image_url:
            return None
        s3 = get_minio_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.MINIO_BUCKET_NAME, "Key": obj.image_url},
            ExpiresIn=3600,
        )

    class Meta:
        model = Alarm
        fields = [
            "id",
            "category",
            "category_details",
            "wayline",
            "wayline_details",
            "latitude",
            "longitude",
            "content",
            "specific_data",
            "image_url",
            "image_signed_url",
            "status",
            "handler",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "category": {"write_only": True, "required": True},
        }


class WaylineImageSerializer(serializers.ModelSerializer):
    wayline_details = WaylineSerializer(source="wayline", read_only=True)
    image_signed_url = serializers.SerializerMethodField(read_only=True)

    def get_image_signed_url(self, obj):
        if not obj.image_url:
            return None
        s3 = get_minio_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.MINIO_BUCKET_NAME, "Key": obj.image_url},
            ExpiresIn=3600,
        )

    class Meta:
        model = WaylineImage
        fields = [
            "id",
            "wayline",
            "wayline_details",
            "alarm",
            "image_url",
            "image_signed_url",
            "title",
            "description",
            "extra_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class UserSerializer(serializers.ModelSerializer):
    # 保留完整的用户逻辑
    name = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "role",
            "is_active",
            "date_joined",
            "password",
        )
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
            if name:
                profile.name = name
            if role:
                profile.role = role
            profile.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    # 保留完整的创建用户逻辑
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
        user = User.objects.create_user(
            username=validated_data["username"], password=password
        )
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
            "id",
            "serverUrl",
            "wssUrl",
            "hostUrl",
            "prjId",
            "projectToken",
            "userId",
            "workspaceId",
            "fh2_project_id",
            "extra_params",
            "created_at",
            "updated_at",
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
            "fh2_project_id": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
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

    # ⭐ 新增：展示检测类型关联对象的信息
    detect_category_name = serializers.CharField(source='detect_category.name', read_only=True)
    detect_category_code = serializers.CharField(source='detect_category.code', read_only=True)
    parent_task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = InspectTask
        fields = [
            'id',
            'wayline',
            'wayline_details',
            'external_task_id',
            'bucket',
            'prefix_list',
            'started_at',
            'finished_at',
            'expire_at',

            # ⭐ 变更为 detect_category
            'detect_category',  # 提交ID用
            'detect_category_name',  # 展示用
            'detect_category_code',  # 展示用

            'detect_status',
            'is_cleaned',
            'created_at',
            'parent_task',
        ]
        read_only_fields = ['id', 'detect_status', 'is_cleaned', 'created_at', 'parent_task']


class InspectImageSerializer(serializers.ModelSerializer):
    """
    巡检图片序列化：
    - 返回 MinIO 对象 key
    - 返回一个可直接访问的 signed_url（前端展示用）
    - 返回 result_signed_url（标注后的图片URL）
    - 返回一个简化的 status01 字段，供前端直接判断正常/异常
    - 返回 result_info（JSON字符串形式的检测结果）
    """
    signed_url = serializers.SerializerMethodField()
    result_signed_url = serializers.SerializerMethodField()
    inspect_task_details = InspectTaskSerializer(source="inspect_task", read_only=True)
    status01 = serializers.SerializerMethodField()
    result_info = serializers.SerializerMethodField()

    class Meta:
        model = InspectImage
        fields = [
            "id",
            "inspect_task",
            "inspect_task_details",
            "wayline",
            "object_key",
            "signed_url",
            "result_signed_url",
            "detect_status",
            "result",
            "result_info",
            "status01",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_signed_url(self, obj):
        if not obj.object_key:
            return None

        s3 = get_minio_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": obj.inspect_task.bucket,  # 用任务里的 bucket
                "Key": obj.object_key,
            },
            ExpiresIn=3600,
        )

    def get_result_signed_url(self, obj):
        """返回标注后图片的签名URL"""
        data = getattr(obj, "result", None) or {}
        if not isinstance(data, dict):
            return None
        
        result_object_key = data.get("result_object_key")
        if not result_object_key:
            return None
        
        s3 = get_minio_client()
        try:
            return s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": obj.inspect_task.bucket,
                    "Key": result_object_key,
                },
                ExpiresIn=3600,
            )
        except Exception as e:
            print(f"生成标注图片URL失败: {e}")
            return None

    def get_result_info(self, obj):
        """返回result字段的JSON字符串形式"""
        import json
        data = getattr(obj, "result", None)
        if data:
            return json.dumps(data, ensure_ascii=False)
        return None

    def get_status01(self, obj):
        """根据算法结果返回一个简单的状态位：0=正常，1=异常，None=未知/未完成"""
        data = getattr(obj, "result", None) or {}
        if not isinstance(data, dict):
            return None

        # 优先使用 detection_status 字段
        if "detection_status" in data:
            try:
                return int(data.get("detection_status"))
            except (TypeError, ValueError):
                pass

        # 兼容只返回 defects_description 列表的情况
        defects = data.get("defects_description")
        if isinstance(defects, (list, tuple)):
            return 1 if defects else 0

        return None