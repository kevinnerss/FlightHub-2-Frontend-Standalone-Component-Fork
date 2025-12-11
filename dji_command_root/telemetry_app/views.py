import json
import mimetypes
import os
import time
import threading
import requests
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue
# views.py

# 1. 保持 Python 原生导入不变
from datetime import datetime, timezone

# 2. ⭐ 修改 Django 的导入，给它起个别名避免冲突
from django.utils import timezone as django_timezone
import boto3
from botocore.client import Config

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404
from django.utils._os import safe_join
from django.db import transaction

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.reverse import reverse

from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Alarm, AlarmCategory, Wayline, WaylineImage,
    ComponentConfig, MediaFolderConfig, InspectTask, InspectImage, UserProfile
)

from .serializers import (
    AlarmSerializer, AlarmCategorySerializer, WaylineSerializer,
    WaylineImageSerializer, UserSerializer, UserCreateSerializer,
    LoginSerializer, TokenSerializer, ComponentConfigSerializer,
    MediaFolderConfigSerializer, InspectTaskSerializer, InspectImageSerializer
)

from .filters import AlarmFilter, WaylineImageFilter
from .permissions import IsSystemAdmin


# ======================================================================
# 1. 核心业务逻辑 helper (新增/修改部分)
# ======================================================================

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name=getattr(settings, "MINIO_REGION", "us-east-1"),
        config=Config(signature_version="s3v4"),
    )


def sync_images_core(task):
    """MinIO 同步逻辑"""
    if not task.prefix_list: return 0
    folder_prefix = task.prefix_list[0]
    s3 = get_minio_client()
    created_count = 0
    try:
        paginator = s3.get_paginator('list_objects_v2')
        bucket_name = getattr(task, 'bucket', 'dji')

        for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix):
            if "Contents" not in page: continue
            for obj in page["Contents"]:
                key = obj["Key"]
                if not key.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")): continue

                if not InspectImage.objects.filter(inspect_task=task, object_key=key).exists():
                    InspectImage.objects.create(
                        inspect_task=task,
                        wayline=task.wayline,
                        object_key=key,
                        detect_status="pending"
                    )
                    created_count += 1
        return created_count
    except Exception as e:
        print(f"❌ [Sync] Error: {e}")
        return 0


# views.py

# views.py

def create_alarm_from_detection(task, img, result_data):
    try:
        # 1. 解析病害描述 (列表 -> 字符串)
        # 算法返回: "defects_description": ["绝缘子破损", "螺母松动"]
        defects_list = result_data.get("defects_description", [])

        # 将列表转为字符串: "绝缘子破损, 螺母松动"
        if defects_list:
            content_text = ", ".join([str(d) for d in defects_list])
            # 取第一个作为 code 去匹配数据库分类 (用于统计)
            primary_code = defects_list[0]
        else:
            content_text = "AI检测发现异常(未说明类型)"
            primary_code = "UNKNOWN"

        # 2. 匹配分类 (数据库 Category 外键)
        # 虽然 Content 直接写了描述，但 category_id 还是需要关联的，方便以后筛选
        sub_category = AlarmCategory.objects.filter(code=primary_code).first()
        if not sub_category:
            sub_category = task.detect_category

        # 3. 提取 GPS (硬性要求)
        gps = result_data.get("gps", {})
        lat = gps.get("lat", 0)
        lon = gps.get("lon", 0)

        # 4. 创建告警
        Alarm.objects.create(
            wayline=task.wayline,
            category=sub_category,
            source_image=img,
            image_url=result_data.get("result_object_key") or img.object_key,
            specific_data=result_data,

            # ⭐ 修改点：直接使用算法返回的描述文本
            content=f"AI检测发现: {content_text}",

            latitude=lat,
            longitude=lon,
            status="PENDING",
            handler="AI_ALGORITHM"
        )
        print(f"🚨 [Alarm] 告警创建成功！内容: {content_text}")

    except Exception as e:
        print(f"❌ [Alarm] 创建失败: {e}")
        import traceback
        traceback.print_exc()
# views.py 头部记得加这两个：
import time
import random

# views.py

import time
import random
from django.utils import timezone as django_timezone

# views.py

import time
import random
from django.utils import timezone as django_timezone


def auto_trigger_detect1(task):
    """
    自动检测全流程 (本地 Mock 版 - 适配 defects_description 列表协议)
    """
    images = task.images.filter(detect_status="pending").order_by("id")
    if not images.exists(): return

    task.detect_status = "processing"
    task.started_at = django_timezone.now()
    task.save(update_fields=['detect_status', 'started_at'])

    # 获取检测类型 (RAIL, BRIDGE...)
    algo_type = task.detect_category.code if task.detect_category else "unknown"

    for i, img in enumerate(images):
        img.detect_status = "processing"
        img.save(update_fields=['detect_status'])

        # =================================================================
        # 🛑 旧代码注释区 (这里保持不变，以后接真实算法时用)
        # =================================================================
        """
        # 注意：以后接真实算法时，payload 也要改成只发 3 个字段
        payload = {
            "bucket": task.bucket,
            "object_key": img.object_key,
            "detect_type": algo_type
        }
        try:
            detect_url = getattr(settings, "FASTAPI_DETECT_URL", "http://localhost:8001/detect")
            resp = requests.post(detect_url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json() # 直接拿根对象
                img.result = data
                img.detect_status = "done"
                img.save(update_fields=['detect_status', 'result'])

                # 判断列表是否有值
                if data.get("defects_description"): 
                    create_alarm_from_detection(task, img, data)
            else:
                img.detect_status = "failed"
                img.save(update_fields=['detect_status'])
        except Exception:
            img.detect_status = "failed"
            img.save(update_fields=['detect_status'])
        """
        # =================================================================

        # =================================================================
        # ✅ 新代码 (Mock 模拟逻辑 - 已更新为列表格式)
        # =================================================================
        try:
            # 1. 模拟耗时
            time.sleep(0.2)

            # 2. 制造假结果 (每 3 张图出 1 个异常)
            is_defect = (i % 3 == 0)

            # 构造异常列表：如果有病害，列表里放一个类型代码；否则为空列表
            mock_defects_list = [algo_type] if is_defect else []

            if is_defect:
                print(f"   ⚠️ [Mock] 图片 {img.id} -> 发现异常 ({mock_defects_list})")
            else:
                print(f"   ✅ [Mock] 图片 {img.id} -> 正常")

            # ⭐ 3. 构造完全符合新协议的 JSON
            data = {
                # 必须有的结果图路径 (假装原图就是结果图)
                "result_object_key": img.object_key,

                # 关键：用列表表达异常
                "defects_description": mock_defects_list,

                # 状态位 (可选，辅助参考)
                "detection_status": 1 if is_defect else 0,

                # 关键：必须带 GPS，否则数据库报错
                "gps": {"lat": 0, "lon": 0}
            }

            # 4. 保存结果到 InspectImage
            img.result = data
            img.detect_status = "done"
            img.save(update_fields=['detect_status', 'result'])

            # 5. 触发告警 (判断列表是否非空)
            if len(mock_defects_list) > 0:
                create_alarm_from_detection(task, img, data)

        except Exception as e:
            print(f"❌ [Mock] 模拟出错: {e}")
            import traceback
            traceback.print_exc()
            img.detect_status = "failed"
            img.save(update_fields=['detect_status'])
        # =================================================================

    task.finished_at = django_timezone.now()
    task.detect_status = "done"
    task.save(update_fields=['detect_status', 'finished_at'])
    print(f"🏁 [Detect] 任务 {task.id} 结束.")

def auto_trigger_detect(task):
    """自动检测全流程 (适配真实算法协议版)"""
    images = task.images.filter(detect_status="pending").order_by("id")
    if not images.exists(): return

    task.detect_status = "processing"
    task.started_at = django_timezone.now()
    task.save(update_fields=['detect_status', 'started_at'])

    detect_url = getattr(settings, "FASTAPI_DETECT_URL", "http://localhost:8001/detect")
    algo_type = task.detect_category.code if task.detect_category else "unknown"

    for img in images:
        img.detect_status = "processing"
        img.save(update_fields=['detect_status'])

        # 1. 构造极简请求 (符合之前确认的3字段协议)
        payload = {
            "bucket": task.bucket,
            "object_key": img.object_key,
            "detect_type": algo_type
        }

        try:
            # 发送请求
            resp = requests.post(detect_url, json=payload, timeout=30)

            if resp.status_code == 200:
                # ⭐ 改动点1：直接获取 JSON，不要 .get("data")
                # 因为算法返回的是扁平结构
                data = resp.json()

                img.result = data
                img.detect_status = "done"
                img.save(update_fields=['detect_status', 'result'])

                # ⭐ 改动点2：通过列表是否为空来判断是否异常
                # 算法返回: "defects_description": ["RAIL", ...]
                defects = data.get("defects_description", [])

                # 如果列表存在且不为空 (len > 0)，则视为有病害
                if defects:
                    create_alarm_from_detection(task, img, data)
            else:
                print(f"❌ [Detect] 算法返回错误: {resp.status_code} - {resp.text}")
                img.detect_status = "failed"
                img.save(update_fields=['detect_status'])

        except Exception as e:
            print(f"❌ [Detect] 请求异常: {e}")
            img.detect_status = "failed"
            img.save(update_fields=['detect_status'])

    task.finished_at = django_timezone.now()
    task.detect_status = "done"
    task.save(update_fields=['detect_status', 'finished_at'])
    print(f"🏁 [Detect] 任务 {task.id} 真实检测结束.")


# ======================================================================
# 2. 后台轮询 Worker (替代原来的 Webhook)
# ======================================================================

def minio_poller_worker():
    """MinIO 轮询线程 (调试 + SQLite兼容版)"""
    time.sleep(3)
    print("🕵️ [Debug] 轮询线程已启动 (Verbose Mode)...")

    s3 = get_minio_client()
    bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

    while True:
        try:
            # 1. 检查数据库配置
            configs = AlarmCategory.objects.filter(
                wayline__isnull=False, match_keyword__isnull=False
            ).select_related('wayline')

            if not configs.exists():
                print("⚠️ [Debug] 数据库无有效配置 (配置数: 0)，等待 60s...")
                time.sleep(60)
                continue

            # 2. 扫描 MinIO
            # print("   [Debug] 正在扫描 MinIO fh2/projects/ ...")
            paginator = s3.get_paginator('list_objects_v2')
            folder_stats = {}
            found_any_file = False

            for page in paginator.paginate(Bucket=bucket_name, Prefix="fh2/projects/"):
                if "Contents" not in page: continue
                found_any_file = True
                for obj in page['Contents']:
                    key = obj['Key']
                    parts = key.split('/')
                    if len(parts) < 3: continue
                    task_folder = '/'.join(parts[:-1]) + '/'

                    last_mod = obj['LastModified']
                    if task_folder not in folder_stats or last_mod > folder_stats[task_folder]:
                        folder_stats[task_folder] = last_mod

            if not found_any_file:
                print("⚠️ [Debug] MinIO 目录 fh2/projects/ 是空的，未扫描到文件")

            # 3. 分析结果
            now = django_timezone.now()

            for folder, last_mod in folder_stats.items():
                folder_name = folder.strip('/').split('/')[-1]

                # A. 时间检查 (调试时可以把 < 300 改成 < 0 来强制执行)
                time_diff = (now - last_mod).total_seconds()
                if time_diff < 300:
                    print(f"   -> ⏳ [Skip] {folder_name} 还在传输中 (距修改 {int(time_diff)}s)")
                    # continue # 🔴 调试时：如果想强制跑，就把这行注释掉

                # B. 去重检查 (使用 external_task_id 兼容 SQLite)
                if InspectTask.objects.filter(external_task_id=folder_name).exists():
                    # print(f"   -> 🔄 [Skip] {folder_name} 任务已存在")
                    continue

                # C. 匹配配置
                matched_cfg = None
                folder_lower = folder.lower()
                for cfg in configs:
                    if cfg.match_keyword.lower() in folder_lower:
                        matched_cfg = cfg
                        break

                if matched_cfg:
                    print(f"✨ [Success] 匹配成功！正在创建任务: {folder_name}")

                    # 1. 解析/创建父任务
                    parent_name = folder_name.split('_')[0] if '_' in folder_name else folder_name
                    parent_task, _ = InspectTask.objects.get_or_create(
                        external_task_id=parent_name,
                        parent_task__isnull=True,
                        defaults={"detect_status": "done", "bucket": "", "prefix_list": []}
                    )

                    # 2. 创建子任务
                    task = InspectTask.objects.create(
                        parent_task=parent_task,
                        wayline=matched_cfg.wayline,
                        detect_category=matched_cfg,
                        bucket=bucket_name,
                        prefix_list=[folder],
                        external_task_id=folder_name,
                        detect_status="pending"
                    )

                    # 3. 触发
                    sync_images_core(task)
                    threading.Thread(target=auto_trigger_detect, args=(task,)).start()
                else:
                    print(
                        f"   -> ❓ [Skip] {folder_name} 未匹配到关键字 (当前关键字: {[c.match_keyword for c in configs]})")

        except Exception as e:
            print(f"❌ [Monitor] 发生异常: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(10)  # 这里的 sleep 决定了轮询频

threading.Thread(target=minio_poller_worker, daemon=True).start()


# ======================================================================
# 3. ViewSets (融合了你的旧逻辑和我的新逻辑)
# ======================================================================

class AlarmCategoryViewSet(viewsets.ModelViewSet):
    """告警类型管理（兼配置中心）"""
    queryset = AlarmCategory.objects.all()
    serializer_class = AlarmCategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code', 'match_keyword']


class InspectTaskViewSet(viewsets.ModelViewSet):
    """巡检任务管理 (全自动)"""
    queryset = InspectTask.objects.all().order_by("-created_at")
    serializer_class = InspectTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["external_task_id", "wayline__name"]
    ordering_fields = ["created_at", "started_at", "finished_at"]

    @action(detail=True, methods=["post"])
    def sync_images(self, request, pk=None):
        task = self.get_object()
        cnt = sync_images_core(task)
        return Response({"detail": f"Synced {cnt} images."})

    @action(detail=True, methods=["post"])
    def trigger_detect(self, request, pk=None):
        task = self.get_object()
        if task.detect_status == "processing":
            return Response({"detail": "Processing..."}, status=400)
        threading.Thread(target=auto_trigger_detect, args=(task,)).start()
        return Response({"detail": "Detection started."})


class AlarmViewSet(viewsets.ModelViewSet):
    """保留你原本的 Search Fields"""
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
    queryset = Wayline.objects.all()
    serializer_class = WaylineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['wayline_id', 'name', 'description', 'created_by']
    ordering_fields = ['created_at', 'updated_at', 'status', 'name']
    ordering = ['-created_at']


class WaylineImageViewSet(viewsets.ModelViewSet):
    queryset = WaylineImage.objects.select_related('wayline', 'alarm').all()
    serializer_class = WaylineImageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WaylineImageFilter
    search_fields = ['title', 'description', 'wayline__name', 'wayline__wayline_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            token_serializer = TokenSerializer(token)
            return Response(token_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': '注销成功'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': '注销失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """保留你原本的 destroy 保护逻辑"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'profile__name']
    ordering_fields = ['id', 'username', 'date_joined']
    ordering = ['-date_joined']

    def get_permissions(self):
        if self.action in ['create', 'list', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSystemAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
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

    def partial_update(self, request, pk=None):
        obj = self.get_object()
        serializer = ComponentConfigSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MediaLibraryViewSet(viewsets.ViewSet):
    """保留你原本的 List 和 Serve 逻辑"""
    permission_classes = [AllowAny]
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.mpeg', '.mpg'}

    def get_permissions(self):
        if self.action == 'config' and getattr(self, 'request', None):
            if self.request.method in ['PUT', 'PATCH', 'POST']:
                return [permissions.IsAuthenticated(), IsSystemAdmin()]
        return [AllowAny()]

    def get_config(self):
        obj, _ = MediaFolderConfig.objects.get_or_create(id=1)
        return obj

    def list(self, request):
        config = self.get_config()
        folder_path = config.folder_path

        if not folder_path:
            return Response({'folder_path': folder_path, 'files': [], 'message': '媒体文件夹未配置'}, status=400)
        if not os.path.isdir(folder_path):
            return Response({'folder_path': folder_path, 'files': [], 'message': '路径不存在'}, status=400)

        files = []
        try:
            for entry in sorted(Path(folder_path).iterdir()):
                if not entry.is_file(): continue
                suffix = entry.suffix.lower()
                if suffix in self.image_extensions:
                    media_type = 'image'
                elif suffix in self.video_extensions:
                    media_type = 'video'
                else:
                    continue

                stat = entry.stat()
                rel_path = entry.relative_to(folder_path).as_posix()
                file_url = reverse('media-library-serve', kwargs={'path': rel_path}, request=request)
                files.append({
                    'name': entry.name,
                    'path': rel_path,
                    'type': media_type,
                    'url': file_url,
                    'size': stat.st_size,
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        except OSError:
            return Response({'folder_path': folder_path, 'files': [], 'message': '读取失败'}, status=400)
        return Response({'folder_path': folder_path, 'files': files})

    @action(detail=False, methods=['get', 'put'], url_path='config')
    def config(self, request):
        config = self.get_config()
        if request.method == 'GET':
            return Response(MediaFolderConfigSerializer(config).data)
        serializer = MediaFolderConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('folder_path') and not os.path.isdir(
                    serializer.validated_data['folder_path']):
                return Response({'folder_path': ['路径不存在']}, status=400)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'], url_path='serve/(?P<path>.+)', permission_classes=[permissions.AllowAny])
    def serve(self, request, path=None):
        config = self.get_config()
        if not config.folder_path: raise Http404("未配置")
        try:
            full_path = safe_join(config.folder_path, path)
        except (SuspiciousFileOperation, ValueError):
            raise Http404("非法路径")
        if not full_path or not os.path.isfile(full_path): raise Http404("文件不存在")

        response = FileResponse(open(full_path, 'rb'))
        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type: response["Content-Type"] = mime_type
        return response


# views.py

# ... (保留之前的 import 和 helper 函数) ...

# ======================================================================
# 恢复 Webhook 相关全局变量
# ======================================================================
webhook_queue = Queue()
processed_event_ids = set()


# ... (保留 minio_poller_worker 和其他代码) ...

# ======================================================================
# 恢复 WebhookTestViewSet
# ======================================================================

class WebhookTestViewSet(viewsets.ViewSet):
    """
    【生产级 Webhook 接口】(已恢复)
    - 用于接收司空或外部系统的 HTTP 推送
    - 数据仅存入队列，暂不干扰 MinIO 轮询逻辑
    """
    permission_classes = [AllowAny]  # 注意：需确保导入了 AllowAny

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

            print("🔥 [Webhook] 收到推送")

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

            # 为了防止集合无限增长，简单清理一下（可选）
            if len(processed_event_ids) > 1000:
                processed_event_ids.clear()

            data["_event_id"] = event_id

            # 放入队列 (如果你后续想处理它，可以再写一个 worker 来消费这个队列)
            webhook_queue.put(data)

            return Response({"msg": "接收成功", "event_id": event_id}, status=200)

        except Exception as e:
            print(f"❌ Webhook 处理异常: {e}")
            return Response({"msg": "解析失败"}, status=400)