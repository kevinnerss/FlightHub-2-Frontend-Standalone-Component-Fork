from rest_framework import serializers
from .models import Alarm, AlarmCategory, Wayline, UserProfile  # 导入新的 AlarmCategory 和 Wayline
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


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


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
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
        # 添加createdAt字段以匹配前端期望
        ret['createdAt'] = instance.date_joined
        return ret

    def update(self, instance, validated_data):
        # 更新密码
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # 更新基本信息
        if 'username' in validated_data:
            instance.username = validated_data['username']
        
        instance.save()
        
        # 更新扩展信息
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
    """用户创建序列化器，包含密码设置"""
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
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password
        )
        
        # 创建用户扩展信息
        UserProfile.objects.create(
            user=user,
            name=name,
            role=role
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            
            if not user.is_active:
                raise serializers.ValidationError('用户已被禁用')
            
            data['user'] = user
            return data
        raise serializers.ValidationError('用户名或密码错误')


class TokenSerializer(serializers.ModelSerializer):
    """Token序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Token
        fields = ('key', 'user')