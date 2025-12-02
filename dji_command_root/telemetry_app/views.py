from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
from .models import Alarm, AlarmCategory, Wayline, UserProfile, ComponentConfig, WaylineImage
from .serializers import (
    AlarmSerializer, AlarmCategorySerializer, WaylineSerializer,
    UserSerializer, UserCreateSerializer, LoginSerializer, TokenSerializer,
    ComponentConfigSerializer, WaylineImageSerializer
)
from .filters import AlarmFilter, WaylineImageFilter
from .permissions import IsSystemAdmin


class AlarmCategoryViewSet(viewsets.ModelViewSet):
    """
    告警类型管理（主要用于后台维护）
    """
    queryset = AlarmCategory.objects.all()
    serializer_class = AlarmCategorySerializer


class AlarmViewSet(viewsets.ModelViewSet):
    """
    告警信息管理（增删改查）
    """
    queryset = Alarm.objects.select_related('category', 'wayline').all()
    serializer_class = AlarmSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AlarmFilter
    search_fields = [
        'content', 'handler', 'category__name', 'category__code',
        'wayline__wayline_id', 'wayline__name', 'specific_data'
    ]
    ordering_fields = ['created_at', 'updated_at', 'status']


class WaylineViewSet(viewsets.ModelViewSet):
    """
    航线信息管理（增删改查）
    """
    queryset = Wayline.objects.all()
    serializer_class = WaylineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['wayline_id', 'name', 'description', 'created_by']
    ordering_fields = ['created_at', 'updated_at', 'status', 'name']
    ordering = ['-created_at']


class WaylineImageViewSet(viewsets.ModelViewSet):
    """
    航线图片管理
    """
    queryset = WaylineImage.objects.select_related('wayline', 'alarm').all()
    serializer_class = WaylineImageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WaylineImageFilter
    search_fields = ['title', 'description', 'wayline__name', 'wayline__wayline_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AuthViewSet(viewsets.ViewSet):
    """
    用户认证视图集
    """
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            token_serializer = TokenSerializer(token)
            return Response(token_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """用户注销"""
        try:
            request.user.auth_token.delete()
            return Response({'message': '注销成功'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': '注销失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'profile__name']
    ordering_fields = ['id', 'username', 'date_joined']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """根据不同操作设置不同的权限"""
        if self.action in ['create', 'list', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSystemAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        """根据不同操作使用不同的序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def destroy(self, request, *args, **kwargs):
        """防止删除admin用户"""
        user = self.get_object()
        if user.username == 'admin':
            return Response({'message': '不能删除管理员账户'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ComponentConfigViewSet(viewsets.ViewSet):
    """
    Component config for FH2 public params (single record storage)
    """
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]

    def get_object(self):
        obj, _ = ComponentConfig.objects.get_or_create(id=1)
        return obj

    def list(self, request):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj)
        return Response(serializer.data)

    def update(self, request, pk=None):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ... (上面是你原本的代码)

class WebhookTestViewSet(viewsets.ViewSet):
    """
    【测试专用】用于接收 EMQX 或 司空2 推送的 Webhook 数据
    配置填写的 URL: http://<服务器IP>/api/test/webhook/receive/
    """
    # 允许任何 IP 调用 (司空服务器可能没有 Token)
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post', 'get'], url_path='receive')
    def receive_data(self, request):
        """
        接收司空2 Webhook 推送
        """
        # 1. 如果是 GET 请求，通常是浏览器访问测试
        if request.method == 'GET':
            return Response({'msg': 'Webhook 接口正常运行中，请在司空配置 POST 请求。'}, status=status.HTTP_200_OK)

        # 2. 处理 POST 请求
        try:
            # 获取原始数据
            data = request.data

            # --- 打印日志，方便现场调试 ---
            print("\n" + "🔥" * 10 + " [Django Webhook] 收到数据 " + "🔥" * 10)
            print(json.dumps(data, indent=4, ensure_ascii=False))
            print("🔥" * 30 + "\n")

            # 3. (可选) 司空握手验证
            # 如果收到含有 challenge 的包，原样返回即可通过验证
            if 'challenge' in data:
                return Response({'challenge': data['challenge']}, status=status.HTTP_200_OK)

            # 4. 你的业务逻辑 (例如设备上线存库)
            # if data.get('type') == 'device_online':
            #     save_device_status(data)

            return Response({'code': 200, 'msg': '接收成功'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Webhook 处理异常: {str(e)}")
            return Response({'code': 500, 'msg': '数据解析失败'}, status=status.HTTP_400_BAD_REQUEST)
    def partial_update(self, request, pk=None):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

