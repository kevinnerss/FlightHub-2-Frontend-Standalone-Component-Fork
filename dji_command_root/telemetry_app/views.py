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
import uuid
# 1. 保持 Python 原生导入不变
from datetime import datetime, timezone
# --- 请确保 views.py 顶部包含这些引用 ---
import json
import re
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# --- 补充 MinIO 客户端配置 (解决 'client' 报错) ---
# 如果你之前是在某个函数里定义的 client，现在需要把它放到外面变成全局变量，
# 这样新的 scan_candidate_folders 函数才能用它。
# 请确保这段代码在 views.py 的所有函数之前：


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
        gps = result_data.get("gps") or {}
        lat = gps.get("lat", 0)  # 如果没 GPS，默认经纬度 0
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

    detect_url = getattr(settings, "FASTAPI_DETECT_URL", "http://localhost:8088/detect")
    algo_type = task.detect_category.code if task.detect_category else "unknown"

    for img in images:
        img.detect_status = "processing"
        img.save(update_fields=['detect_status'])

        # 1. 构造极简请求 (符合之前确认的3字段协议)
        """payload = {
            "bucket": task.bucket,
            "object_key": img.object_key,
            "detect_type": algo_type
        }"""
        payload = {
            # 1. 必填字段 (算法要的)
            "req_id": f"req_{uuid.uuid4().hex[:8]}",  # 随机生成一个ID
            "image_id": img.id,  # 真实的图片ID
            "wayline_id": str(task.wayline_id) if task.wayline_id else "0",  # 转字符串
            "timestamp": int(time.time()),  # 当前时间戳

            # 2. 核心字段 (业务要的)
            "bucket": task.bucket,
            "object_key": img.object_key,
            "detect_type": algo_type
        }

        try:
            # 发送请求
            resp = requests.post(detect_url, json=payload, timeout=300)

            if resp.status_code == 200:
                # ⭐ 改动点1：直接获取 JSON，不要 .get("data")
                # 因为算法返回的是扁平结构
                data = resp.json()

                img.result = data
                img.detect_status = "done"
                img.save(update_fields=['detect_status', 'result'])

                algo_status = data.get("detection_status", 0)

                if algo_status == 1:
                    # 只有真的是异常 (1)，才创建 Alarm 记录
                    print(f"⚠️ [Detect] 图片 {img.id} 确认为异常 (Status=1)，生成告警...")
                    create_alarm_from_detection(task, img, data)
                else:
                    # 正常 (0)，只打印日志，不往 Alarm 表里写垃圾数据
                    print(f"✅ [Detect] 图片 {img.id} 检测通过 (Status=0).")
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

def minio_poller_worker1():
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


def minio_poller_worker():
    """
    [新版] 智能扫描线程 (含自动结束逻辑)
    """
    print("🕵️ [Poller] 智能扫描线程已启动，等待指令...")
    time.sleep(3)

    s3 = get_minio_client()

    while True:
        try:
            # 只查询状态为 'scanning' 的任务
            active_tasks = InspectTask.objects.filter(detect_status='scanning')

            if not active_tasks.exists():
                time.sleep(2)
                continue

            for task in active_tasks:
                # 1. 确定扫描路径
                if task.prefix_list and len(task.prefix_list) > 0:
                    prefix = task.prefix_list[0]
                else:
                    # 如果没有 prefix_list，回退到 external_task_id
                    # 注意：如果你的 MinIO 是根目录结构，这里可能是 folder_name + "/"
                    prefix = f"{task.external_task_id}/"

                bucket_name = getattr(task, 'bucket', 'dji')

                # 2. 扫描 MinIO
                paginator = s3.get_paginator('list_objects_v2')
                new_images_count = 0

                # 加上异常捕获，防止某个任务路径不对卡死整个线程
                try:
                    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                        if "Contents" not in page: continue

                        for obj in page["Contents"]:
                            key = obj["Key"]
                            if not key.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")): continue
                            filename = key.split('/')[-1]
                            if filename.startswith("detected_"): continue

                            # 检查去重
                            if not InspectImage.objects.filter(inspect_task=task, object_key=key).exists():
                                InspectImage.objects.create(
                                    inspect_task=task,
                                    wayline=task.wayline,
                                    object_key=key,
                                    detect_status="pending"
                                )
                                print(f"✨ [New Image] 发现新图片: {filename}")
                                new_images_count += 1
                except Exception as s3_err:
                    print(f"⚠️ 扫描任务 {task.id} 路径异常: {s3_err}")

                # 3. 分支判断
                if new_images_count > 0:
                    # A. 有新图 -> 触发检测 -> 检测函数会在跑完后把状态改为 done
                    print(f"🚀 [Poller] 任务 {task.external_task_id} 发现 {new_images_count} 张新图，触发检测...")
                    threading.Thread(target=auto_trigger_detect, args=(task,)).start()
                else:
                    # B. 无新图 -> 检查是否还有残留的 pending/processing 图片
                    # 如果所有图片都跑完了，且刚才没扫到新图，说明任务彻底结束了
                    unfinished_cnt = InspectImage.objects.filter(
                        inspect_task=task,
                        detect_status__in=['pending', 'processing']
                    ).count()

                    if unfinished_cnt == 0:
                        print(f"✅ [Poller] 任务 {task.external_task_id} 已无新图且处理完毕，自动结束扫描。")
                        task.detect_status = 'done'
                        task.save(update_fields=['detect_status'])

            time.sleep(3)

        except Exception as e:
            print(f"❌ [Poller Error] 轮询出错: {e}")
            time.sleep(5)
#threading.Thread(target=minio_poller_worker, daemon=True).start()
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


@csrf_exempt
def scan_candidate_folders(request):
    """
    [API] 预扫描 MinIO 目录 (Boto3 版本)
    利用 Delimiter='/' 模拟文件夹列表，只看 fh2/projects/ 下的一级目录
    """
    if request.method != 'GET':
        return JsonResponse({"code": 405, "msg": "Method Not Allowed"})

    try:
        # 1. 获取 Boto3 客户端 (复用你 views.py 第 85 行定义的工具函数)
        s3 = get_minio_client()
        bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")
        #prefix = "fh2/projects/"
        prefix = ""
        # 2. 调用 list_objects_v2 (Boto3 的标准写法)
        # Delimiter='/' 意思是以 / 为界限，这样 API 就会把“子文件夹”聚合在 CommonPrefixes 里
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            Delimiter='/'
        )

        candidates = {}

        # Boto3 返回的文件夹列表在 'CommonPrefixes' 字段里
        # 结构如: [{'Prefix': 'fh2/projects/李达轨道 2025-12-12/'}, ...]
        common_prefixes = response.get('CommonPrefixes', [])

        for item in common_prefixes:
            full_path = item['Prefix']  # 例如 "fh2/projects/李达轨道 2025-12-12/"

            # 提取文件夹名：去掉前缀 "fh2/projects/" 和末尾的 "/"
            # split('/') 会得到 ['', 'projects', '李达轨道...', '']
            folder_name = full_path.strip('/').split('/')[-1]

            # 跳过空名
            if not folder_name:
                continue

            # --- 解析日期逻辑 (调用你下方定义的 parse_folder_name) ---
            date_group, type_name = parse_folder_name(folder_name)

            if date_group not in candidates:
                candidates[date_group] = []

            # 检查数据库状态
            exists = InspectTask.objects.filter(external_task_id=folder_name).exists()
            status = "new"
            if exists:
                task = InspectTask.objects.get(external_task_id=folder_name)
                status = task.detect_status

            candidates[date_group].append({
                "folder_name": folder_name,
                "full_path": full_path,
                "detect_type": type_name,
                "db_status": status
            })

        # 排序并返回
        sorted_keys = sorted(candidates.keys(), reverse=True)
        result_list = [
            {"date": k, "tasks": candidates[k]} for k in sorted_keys
        ]

        return JsonResponse({"code": 200, "data": result_list})

    except Exception as e:
        print(f"❌ [Scan Error] 扫描失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"code": 500, "msg": f"MinIO 扫描失败: {str(e)}"})
import re
from datetime import datetime


def parse_folder_name(folder_name):
    """
    解析文件夹名称，提取日期和类型
    支持格式: "李达轨道 2025-12-12" 或 "20251211_rail_test"
    返回: (date_str, type_str)
    """
    # 移除末尾的斜杠
    folder_name = folder_name.strip('/')

    # 1. 尝试匹配 YYYY-MM-DD 格式
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', folder_name)
    if date_match:
        date_str = date_match.group(1)
        # 类型 = 原名去掉日期和空格
        type_str = folder_name.replace(date_str, '').strip(' _-')
        return date_str, type_str or "未知类型"

    # 2. 尝试匹配 YYYYMMDD 格式
    date_match_compact = re.search(r'(\d{8})', folder_name)
    if date_match_compact:
        raw_date = date_match_compact.group(1)
        # 格式化为 YYYY-MM-DD 以便前端统一展示
        try:
            date_obj = datetime.strptime(raw_date, "%Y%m%d")
            date_str = date_obj.strftime("%Y-%m-%d")
            type_str = folder_name.replace(raw_date, '').strip(' _-')
            return date_str, type_str or "未知类型"
        except ValueError:
            pass

    # 3. 实在解析不出来，就默认“今天”
    return datetime.now().strftime("%Y-%m-%d"), folder_name


@csrf_exempt
def start_selected_tasks(request):
    """
    [API] 批量启动任务
    修复：自动将 AlarmCategory 绑定的航线 (wayline) 继承给 InspectTask
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            selected_folders = body.get("folders", [])

            if not selected_folders:
                return JsonResponse({"code": 400, "msg": "未选择任何任务"})

            started_list = []
            bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

            for folder_name in selected_folders:
                date_str, type_name = parse_folder_name(folder_name)

                # 1. 映射 Code (rail, insulator...)
                algo_code = "unknown"
                type_name_lower = type_name.lower()
                if "轨道" in type_name_lower or "rail" in type_name_lower:
                    algo_code = "rail"
                elif "绝缘子" in type_name_lower or "insulator" in type_name_lower:
                    algo_code = "insulator"
                elif "桥" in type_name_lower or "bridge" in type_name_lower:
                    algo_code = "bridge"
                elif "glm" in type_name_lower:
                    algo_code = "glm"

                # 2. 获取分类对象
                category_obj = AlarmCategory.objects.filter(code=algo_code).first()
                if not category_obj and algo_code != "unknown":
                    category_obj = AlarmCategory.objects.create(name=f"{algo_code}检测(自动)", code=algo_code)

                # -------------------------------------------------------
                # 🔥 关键修复：从配置中提取绑定的航线
                # -------------------------------------------------------
                # 你的 CSV 里 rail 绑定了 wayline_id=1，这里就会取出来
                target_wayline = category_obj.wayline if category_obj else None

                # 3. 确保父任务存在
                parent_task_id = f"{date_str}_检测任务"
                parent_task, _ = InspectTask.objects.get_or_create(
                    external_task_id=parent_task_id,
                    defaults={"detect_status": "done", "bucket": bucket_name, "prefix_list": []}
                )

                # 4. 创建子任务 (带上航线)
                prefix_path = f"{folder_name}/"
                task, created = InspectTask.objects.get_or_create(
                    external_task_id=folder_name,
                    defaults={
                        "parent_task": parent_task,
                        "wayline": target_wayline,  # 🔥 赋值：把配置里的航线给任务
                        "bucket": bucket_name,
                        "detect_category": category_obj,
                        "prefix_list": [prefix_path],
                        "detect_status": "scanning"
                    }
                )

                # 5. 如果任务已存在，同步更新航线 (Fix现有数据)
                if not created:
                    task.parent_task = parent_task
                    task.detect_category = category_obj

                    # 🔥 如果配置里有航线，强制同步给任务
                    if target_wayline:
                        task.wayline = target_wayline

                    if not task.prefix_list:
                        task.prefix_list = [prefix_path]

                    if task.detect_status != 'scanning':
                        task.detect_status = 'scanning'
                    task.save()

                    # 6. 复活失败图片并重测
                    reset_count = task.images.filter(detect_status='failed').update(detect_status='pending')
                    if reset_count > 0:
                        print(f"🔄 [Restart] 任务 {folder_name} 重启，航线ID已修正为: {task.wayline_id}")
                        threading.Thread(target=auto_trigger_detect, args=(task,)).start()

                started_list.append(folder_name)

            return JsonResponse({"code": 200, "msg": f"成功启动 {len(started_list)} 个任务", "started": started_list})

        except Exception as e:
            print(f"❌ [Start Task Error]: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"code": 500, "msg": str(e)})

    return JsonResponse({"code": 405, "msg": "Method Not Allowed"})
@csrf_exempt
def stop_detect(request):
    """
    [API] 强制停止/结束检测任务
    前端点击 [结束检测] 按钮时调用
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 允许传 task_id (数据库ID) 或者 external_id (文件夹名)
            task_id = data.get('task_id')
            folder_name = data.get('folder_name')

            tasks = InspectTask.objects.none()

            if task_id:
                tasks = InspectTask.objects.filter(id=task_id)
            elif folder_name:
                tasks = InspectTask.objects.filter(external_task_id=folder_name)

            if not tasks.exists():
                return JsonResponse({"code": 404, "msg": "未找到指定任务"})

            # 强制更新为 done
            rows = tasks.update(detect_status="done")

            return JsonResponse({"code": 200, "msg": f"已停止 {rows} 个任务"})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": str(e)})

    return JsonResponse({"code": 405, "msg": "Method Not Allowed"})