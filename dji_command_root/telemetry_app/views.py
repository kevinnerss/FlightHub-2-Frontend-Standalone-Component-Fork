from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
import threading
from queue import Queue
from .models import Alarm, AlarmCategory, Wayline, UserProfile, ComponentConfig, WaylineImage
from .serializers import (
    AlarmSerializer, AlarmCategorySerializer, WaylineSerializer,
    UserSerializer, UserCreateSerializer, LoginSerializer, TokenSerializer,
    ComponentConfigSerializer, WaylineImageSerializer
)
from .filters import AlarmFilter, WaylineImageFilter
from .permissions import IsSystemAdmin

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

import json
import threading
import time
from queue import Queue

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


# ------------------------------
# Webhook 后台事件队列
# ------------------------------
webhook_queue = Queue()
processed_event_ids = set()


def webhook_worker():
    """后台线程：异步处理司空推送，防止阻塞 Django worker"""
    while True:
        try:
            event = webhook_queue.get()
            event_id = event.get("_event_id")
            print(f"📥 [Webhook Worker] 正在处理 event_id={event_id}")

            # TODO: 在这里处理司空事件，例如存库、触发业务逻辑
            # save_event_to_db(event)

            time.sleep(0.1)  # 模拟处理耗时

        except Exception as e:
            print(f"❌ Webhook Worker 异常: {e}")


# 启动后台 worker（只启动一次）
threading.Thread(target=webhook_worker, daemon=True).start()



class WebhookTestViewSet(viewsets.ViewSet):
    """
    【生产级 Webhook 接口】
    - 不阻塞 Django worker
    - 自动兼容 challenge / JSON / nested payload
    - 防止重复事件
    - 后台异步处理
    """

    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post', 'get'], url_path='receive')
    def receive_data(self, request):

        if request.method == 'GET':
            return Response(
                {'msg': 'Webhook OK（请以 POST 方式发送正式数据）'},
                status=status.HTTP_200_OK
            )

        try:
            # 尝试解析 JSON
            try:
                data = request.data
            except:
                data = {}

            # 少打印日志（避免 worker timeout）
            print("🔥 [Webhook] 收到推送（精简日志）")

            # 处理 challenge，用于司空验证
            if isinstance(data, dict) and "challenge" in data:
                return Response({"challenge": data["challenge"]})

            # 生成事件 ID（用于去重）
            event_id = (
                data.get("id")
                or data.get("event_id")
                or f"{time.time()}-{request.META.get('REMOTE_ADDR')}"
            )

            if event_id in processed_event_ids:
                return Response({"msg": "重复事件，已忽略"}, status=200)

            processed_event_ids.add(event_id)
            data["_event_id"] = event_id  # 放入事件

            # 异步放入队列
            webhook_queue.put(data)

            return Response({"msg": "接收成功", "event_id": event_id}, status=200)

        except Exception as e:
            print(f"❌ Webhook 处理异常: {e}")
            return Response({"msg": "解析失败"}, status=400)
    def partial_update(self, request, pk=None):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

