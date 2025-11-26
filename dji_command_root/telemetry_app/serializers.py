from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Alarm, AlarmCategory, Wayline, UserProfile, ComponentConfig, WaylineImage


class WaylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wayline
        fields = [
            'id', 'wayline_id', 'name', 'description', 'waypoints',
            'length', 'estimated_duration', 'status', 'created_by',
            'created_at', 'updated_at'
        ]


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AlarmCategorySerializer(serializers.ModelSerializer):
    sub_categories = RecursiveField(many=True, read_only=True)

    class Meta:
        model = AlarmCategory
        fields = ['id', 'name', 'code', 'description', 'parent', 'sub_categories']


class AlarmSerializer(serializers.ModelSerializer):
    category_details = AlarmCategorySerializer(source='category', read_only=True)
    wayline = WaylineSerializer(read_only=True)
    wayline_details = serializers.SerializerMethodField(read_only=True)

    def get_wayline_details(self, obj):
        if obj.wayline:
            return WaylineSerializer(obj.wayline, context=self.context).data
        return None

    class Meta:
        model = Alarm
        fields = [
            'id', 'category', 'category_details', 'wayline', 'wayline_details',
            'latitude', 'longitude', 'content', 'specific_data', 'image_url',
            'status', 'handler', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'category': {'write_only': True, 'required': True}
        }


class WaylineImageSerializer(serializers.ModelSerializer):
    wayline_details = WaylineSerializer(source='wayline', read_only=True)

    class Meta:
        model = WaylineImage
        fields = [
            'id', 'wayline', 'wayline_details', 'alarm', 'image_url',
            'title', 'description', 'extra_data', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'role', 'is_active', 'date_joined', 'password')
        read_only_fields = ('date_joined',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if hasattr(instance, 'profile'):
            ret['name'] = instance.profile.name
            ret['role'] = instance.profile.role
        else:
            ret['name'] = instance.username
            ret['role'] = 'user'
        ret['createdAt'] = instance.date_joined
        return ret

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        if 'username' in validated_data:
            instance.username = validated_data['username']
        instance.save()

        name = validated_data.get('name')
        role = validated_data.get('role')
        if name or role:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            if name:
                profile.name = name
            if role:
                profile.role = role
            profile.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, default='user')

    class Meta:
        model = User
        fields = ('username', 'name', 'password', 'role')

    def create(self, validated_data):
        name = validated_data.pop('name')
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=validated_data['username'], password=password)
        UserProfile.objects.create(user=user, name=name, role=role)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        data['user'] = user
        return data


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')


class ComponentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentConfig
        fields = [
            'id', 'serverUrl', 'wssUrl', 'hostUrl', 'prjId', 'projectToken',
            'userId', 'workspaceId', 'fh2_project_id', 'extra_params',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'serverUrl': {'required': False, 'allow_blank': True, 'allow_null': True},
            'wssUrl': {'required': False, 'allow_blank': True, 'allow_null': True},
            'hostUrl': {'required': False, 'allow_blank': True, 'allow_null': True},
            'prjId': {'required': False, 'allow_blank': True, 'allow_null': True},
            'projectToken': {'required': False, 'allow_blank': True, 'allow_null': True},
            'userId': {'required': False, 'allow_blank': True, 'allow_null': True},
            'workspaceId': {'required': False, 'allow_blank': True, 'allow_null': True},
            'fh2_project_id': {'required': False, 'allow_blank': True, 'allow_null': True},
            'extra_params': {'required': False, 'allow_null': True}
        }
