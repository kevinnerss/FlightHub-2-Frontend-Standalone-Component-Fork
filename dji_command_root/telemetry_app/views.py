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
import requests
import zipfile
import io
import re
from django.conf import settings  # 🔥 必须导入 settings
from .models import WaylineFingerprint, Wayline, AlarmCategory

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


# views.py 添加

def get_image_action_uuid_from_minio(s3_client, bucket, key):
    """
    [核心工具] 读取 MinIO 图片头部(前64KB)，提取 XMP 中的 FlightLineInfo (ActionUUID)
    """
    try:
        # 只读取前 64KB (Range Header)，避免下载几MB的大图
        resp = s3_client.get_object(Bucket=bucket, Key=key, Range='bytes=0-65535')
        head_data = resp['Body'].read()

        # 尝试解码 (XMP 是 ASCII/UTF-8 文本，混在二进制里)
        # 使用 latin-1 读取可以避免 decode 报错，且能保留英文字符
        try:
            text_data = head_data.decode('latin-1', errors='ignore')
        except:
            return None

        # 正则搜索 UUID
        # 格式通常是 drone-dji:FlightLineInfo="270f6508-..."
        # 或者 <drone-dji:FlightLineInfo>270f6508-...</drone-dji:FlightLineInfo>
        match = re.search(r'FlightLineInfo="([0-9a-fA-F-]{36})"', text_data)
        if not match:
            match = re.search(r'FlightLineInfo>([0-9a-fA-F-]{36})<', text_data)

        if match:
            return match.group(1)

    except Exception as e:
        # 只有在读不到或者不是图片时才会报错，属于正常现象
        # print(f"⚠️ 读取图片元数据失败: {key} - {e}")
        pass
    return None
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
                
                # 🔥 新增：跳过算法输出的结果图片（detected_ 开头的文件）
                filename = key.split('/')[-1]
                if filename.startswith("detected_"):
                    continue

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
    """自动检测全流程 (适配真实算法协议版 + 持续检测新图)"""
    # 🔥 修改：查询所有pending状态的图片，不管任务是什么时候开始的
    images = task.images.filter(detect_status="pending").order_by("id")
    if not images.exists():
        print(f"⏸️  [Detect] 任务 {task.id} 暂无待检测图片")
        return

    # 🔥 修改：只有第一次启动时才更新started_at
    if not task.started_at:
        task.started_at = django_timezone.now()
        task.save(update_fields=['started_at'])
    
    # 🔥 关键：不改变任务状态，保持scanning让轮询继续扫描新图

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

    # 🔥 修改：检测完这一批后，不立即结束任务，交给轮询线程判断
    print(f"✅ [Detect] 任务 {task.id} 本轮检测完成 ({len(images)}张)，等待轮询线程判断是否结束...")


# ======================================================================
# 2. 后台轮询 Worker (替代原来的 Webhook)
# ======================================================================
# views.py
# views.py 需要引入 timedelta 处理时区
from datetime import timedelta


def minio_poller_worker():
    """
    [最终命名优化版] 智能指纹扫描线程
    命名规则：
      - 父任务：yyyyMMdd巡检任务
      - 子任务：yyyyMMdd航线名检测类型
    """
    print("🕵️ [Poller] 智能命名扫描已启动...")
    time.sleep(5)

    # 启动指纹同步
    threading.Thread(target=WaylineFingerprintManager.sync_by_keywords).start()

    s3 = get_minio_client()
    bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

    while True:
        try:
            paginator = s3.get_paginator('list_objects_v2')

            # 存储结构变更为: { "子文件夹前缀": { "key": "采样图", "date": "yyyyMMdd" } }
            found_sub_folders = {}

            for page in paginator.paginate(Bucket=bucket_name, Prefix="fh_sync/"):
                if "Contents" not in page: continue
                for obj in page["Contents"]:
                    key = obj["Key"]
                    if not key.lower().endswith((".jpg", ".jpeg")): continue

                    parts = key.split('/')
                    if "media" in parts:
                        idx = parts.index("media")
                        if len(parts) > idx + 2:
                            folder_prefix = "/".join(parts[:idx + 2]) + "/"

                            # 如果这个文件夹还没记录，或者记录了但现在有了更新的日期，就更新它
                            if folder_prefix not in found_sub_folders:
                                # 获取文件时间 (UTC) 并转为北京时间 (UTC+8)
                                last_modified = obj['LastModified']
                                cn_time = last_modified + timedelta(hours=8)
                                date_str = cn_time.strftime("%Y%m%d")

                                found_sub_folders[folder_prefix] = {
                                    "key": key,
                                    "date": date_str
                                }

            # 处理发现的文件夹
            for folder_prefix, info in found_sub_folders.items():
                sample_key = info["key"]
                date_str = info["date"]

                # 原始的文件夹 UUID (2c8a...) 仍然需要用来判断是否处理过，防止重复读取指纹
                # 但不再用作 TaskID
                folder_native_uuid = folder_prefix.strip('/').split('/')[-1]

                # 暂时用 prefix_list 来判断是否处理过该物理路径
                # (注意：因为我们要改 ID 格式，所以不能简单用 external_task_id 查重了)
                # 我们可以查询 prefix_list 包含此路径的任务
                # JSONField 查询：prefix_list__contains=folder_prefix
                # ✅ 修正代码：使用 icontains 进行字符串匹配
                # 这会将数据库里的 JSON 视为字符串 "['path/to/a', 'path/to/b']"，然后查找子串
                if InspectTask.objects.filter(prefix_list__icontains=folder_prefix).exists():
                    continue

                print(f"🔍 [New Folder] 发现新上传: {folder_prefix} ({date_str})，正在识别...")

                uuid = get_image_action_uuid_from_minio(s3, bucket_name, sample_key)
                if not uuid: continue

                # 查指纹
                # ✅ SQLite 兼容版 (把 JSON 当字符串查)
                fingerprint = WaylineFingerprint.objects.filter(action_uuids__icontains=uuid).first()
                if not fingerprint:
                    # 兼容遍历
                    for fp in WaylineFingerprint.objects.all():
                        if uuid in fp.action_uuids:
                            fingerprint = fp
                            break

                if fingerprint:
                    # 获取名称信息
                    wayline_name = fingerprint.wayline.name
                    cat_name = fingerprint.detect_category.name if fingerprint.detect_category else "通用检测"

                    print(f"✅ [Match] 命中: {wayline_name} -> {cat_name}")

                    # =========================================================
                    # 1. 创建父任务 (虚拟任务)
                    # 命名格式: "20251221巡检任务"
                    # =========================================================
                    parent_task_id = f"{date_str}巡检任务"

                    parent_task, _ = InspectTask.objects.get_or_create(
                        external_task_id=parent_task_id,
                        defaults={
                            "detect_status": "done",
                            "bucket": bucket_name,
                            "prefix_list": []  # 父任务没有具体路径
                        }
                    )

                    # =========================================================
                    # 2. 创建子任务 (真实任务)
                    # 命名格式: "20251221工业大学桥梁检测"
                    # =========================================================
                    sub_task_id = f"{date_str}{wayline_name}{cat_name}"

                    # 创建任务（不自动检测，等待前端用户选择）
                    new_task = InspectTask.objects.create(
                        parent_task=parent_task,
                        external_task_id=sub_task_id,  # 🔥 这里变成了中文名称
                        bucket=bucket_name,
                        prefix_list=[folder_prefix],  # 🔥 真实的 MinIO 路径存在这里
                        wayline=fingerprint.wayline,
                        detect_category=fingerprint.detect_category,
                        detect_status="pending"  # 🔥 改为 pending，等待用户手动启动
                    )
                    print(f"🎉 任务创建: [{parent_task_id}] -> [{sub_task_id}] (等待用户启动)")

            # 常规图片同步逻辑（只同步 scanning 状态的任务）
            active_tasks = InspectTask.objects.filter(detect_status='scanning')
            for task in active_tasks:
                # 🔥 1. 先同步新图片
                new_cnt = sync_images_core(task)
                if new_cnt > 0:
                    print(f"📥 [Poller] 任务 {task.external_task_id} 同步了 {new_cnt} 张新图")
                
                # 🔥 2. 无论是否有新图，都检查是否有待检测的图片
                pending_cnt = InspectImage.objects.filter(
                    inspect_task=task,
                    detect_status='pending'
                ).count()
                
                if pending_cnt > 0:
                    print(f"🔄 [Poller] 任务 {task.external_task_id} 有 {pending_cnt} 张待检测图片，触发检测...")
                    threading.Thread(target=auto_trigger_detect, args=(task,)).start()
                else:
                    # 🔥 3. 没有pending图片，检查是否还有processing状态的图片
                    processing_cnt = InspectImage.objects.filter(
                        inspect_task=task,
                        detect_status='processing'
                    ).count()
                    
                    if processing_cnt == 0:
                        # 所有图片都处理完了，且没有新图
                        print(f"✅ [Poller] 任务 {task.external_task_id} 所有图片处理完毕，标记为完成")
                        task.detect_status = 'done'
                        task.finished_at = django_timezone.now()
                        task.save(update_fields=['detect_status', 'finished_at'])
                    else:
                        print(f"⏳ [Poller] 任务 {task.external_task_id} 还有 {processing_cnt} 张图片正在检测中...")

        except Exception as e:
            print(f"❌ Poller Loop Error: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(5)
def minio_poller_worker2():
    """
    [最终适配版] 智能指纹扫描线程
    逻辑：扫描 .../media/{SubFolder}/ 下的图片 -> 识别指纹 -> 创建父子任务
    结构：Job(父) -> SubFolder(子, 绑定类型)
    """
    print("🕵️ [Poller] 深度指纹扫描已启动...")
    time.sleep(5)

    # 1. 启动时同步一次指纹库 (确保本地指纹是最新的)
    threading.Thread(target=WaylineFingerprintManager.sync_by_keywords).start()

    s3 = get_minio_client()
    bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

    while True:
        try:
            # =========================================================
            # 第一步：发现 MinIO 里的所有“子任务文件夹” (2c..., 44...)
            # =========================================================
            # 我们直接列出 fh_sync 下的所有对象
            # 目标是找到包含 "/media/" 且在 media 下面还有一层文件夹的路径

            paginator = s3.get_paginator('list_objects_v2')

            # 临时存储发现的子文件夹: { "子文件夹完整路径/": "其中一张采样图的Key" }
            # 例如: { ".../media/2c8a.../": ".../media/2c8a.../DJI_001.jpg" }
            found_sub_folders = {}

            for page in paginator.paginate(Bucket=bucket_name, Prefix="dji/fh_sync/"):
                if "Contents" not in page: continue
                for obj in page["Contents"]:
                    key = obj["Key"]
                    if not key.lower().endswith((".jpg", ".jpeg")): continue

                    # 路径解析：dji/fh_sync/ProjID/JobID/media/SubFolder/img.jpg
                    parts = key.split('/')

                    if "media" in parts:
                        idx = parts.index("media")
                        # 确保 media 下面还有一层 (parts[idx+1]) 且不是文件名本身
                        if len(parts) > idx + 2:
                            # 构造该子文件夹的唯一标识路径 (Prefix)
                            # join 到 sub_folder_name 为止
                            folder_prefix = "/".join(parts[:idx + 2]) + "/"

                            if folder_prefix not in found_sub_folders:
                                found_sub_folders[folder_prefix] = key

            # =========================================================
            # 第二步：处理每一个发现的子文件夹
            # =========================================================
            for folder_prefix, sample_key in found_sub_folders.items():

                # 从路径中提取最后一段作为 external_task_id (即 2c8a... 或 44ed...)
                folder_uuid = folder_prefix.strip('/').split('/')[-1]

                # 1. 检查数据库：如果这个【子任务】已经建过了，跳过
                if InspectTask.objects.filter(external_task_id=folder_uuid).exists():
                    continue

                print(f"🔍 [New Sub-Task] 发现新文件夹: {folder_uuid}，正在采样识别...")

                # 2. 提取指纹 (读取采样图的 XMP)
                uuid = get_image_action_uuid_from_minio(s3, bucket_name, sample_key)

                if not uuid:
                    # 读不到指纹，可能是还没传完或不是航线图，暂跳过
                    continue

                # 3. 查库匹配
                # 查找包含此 UUID 的指纹记录
                fingerprint = WaylineFingerprint.objects.filter(action_uuids__contains=uuid).first()

                # 兼容性处理：如果 filter contains 不生效，尝试遍历
                if not fingerprint:
                    for fp in WaylineFingerprint.objects.all():
                        if uuid in fp.action_uuids:
                            fingerprint = fp
                            break

                if fingerprint:
                    # 获取分类名称 (如：轨道检测)
                    cat_name = fingerprint.detect_category.name if fingerprint.detect_category else "无类型"
                    print(f"✅ [Match] 命中航线: {fingerprint.wayline.name} -> 类型: {cat_name}")

                    # 4. 自动创建父任务 (Job层)
                    # sample_key: .../JobID/media/SubFolder/img.jpg
                    parts = sample_key.split('/')
                    media_idx = parts.index("media")
                    job_id = parts[media_idx - 1]  # media 的上一级就是 JobID (即父任务ID)

                    # 创建或获取父任务
                    # 父任务ID 就是你说的 "20251219巡检" (现在是 1361... UUID)
                    parent_task, _ = InspectTask.objects.get_or_create(
                        external_task_id=job_id,
                        defaults={
                            "detect_status": "done",  # 父任务本身不跑检测，只是个壳
                            "bucket": bucket_name
                        }
                    )

                    # 5. 创建子任务 (SubFolder层) - 这才是真正的检测任务
                    # 子任务ID 就是你说的 "20251219轨道" (现在是 44ed... UUID)
                    new_task = InspectTask.objects.create(
                        parent_task=parent_task,  # 👈 绑定父任务
                        external_task_id=folder_uuid,  # 用 2c8a... 做ID
                        bucket=bucket_name,
                        prefix_list=[folder_prefix],  # 扫描范围限定在这个子文件夹
                        wayline=fingerprint.wayline,
                        detect_category=fingerprint.detect_category,  # 🔥 自动绑定类型(轨道/桥梁)
                        detect_status="scanning"
                    )
                    print(f"🎉 任务创建成功: 子任务[{folder_uuid}] -> 父任务[{job_id}] (类型: {cat_name})")

                else:
                    # 指纹库里没找到，说明这条航线可能没在后台配置，或者没同步 KMZ
                    # print(f"⚪ 指纹 {uuid} 未匹配，跳过")
                    pass

            # =========================================================
            # 第三步：常规图片同步 (逻辑不变)
            # =========================================================
            active_tasks = InspectTask.objects.filter(detect_status='scanning')
            for task in active_tasks:
                new_cnt = sync_images_core(task)
                if new_cnt > 0:
                    print(f"📥 任务 {task.external_task_id} 同步了 {new_cnt} 张新图，触发检测...")
                    threading.Thread(target=auto_trigger_detect, args=(task,)).start()

                # 结束判断逻辑
                unfinished_cnt = InspectImage.objects.filter(
                    inspect_task=task,
                    detect_status__in=['pending', 'processing']
                ).count()

                # 如果没新图且没待处理图，可以视为完成 (根据需求开启)
                # if unfinished_cnt == 0 and new_cnt == 0:
                #      task.detect_status = 'done'
                #      task.save()

        except Exception as e:
            print(f"❌ Poller Loop Error: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(5)
def minio_poller_worker1():
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

    @action(detail=True, methods=["get"])
    def images(self, request, pk=None):
        """返回某个巡检任务下的所有图片及检测状态，按时间顺序排序"""
        task = self.get_object()
        queryset = InspectImage.objects.filter(inspect_task=task).order_by("created_at", "id")
        serializer = InspectImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def sub_tasks(self, request, pk=None):
        """返回某个父任务下面的所有子任务"""
        task = self.get_object()
        queryset = InspectTask.objects.filter(parent_task=task).order_by("created_at", "id")
        serializer = InspectTaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """启动巡检任务:将状态从pending改为scanning"""
        task = self.get_object()
        if task.detect_status not in ["pending"]:
            return Response({"detail": f"当前状态[{task.detect_status}]不可启动,仅pending状态可启动"}, status=400)
        task.detect_status = "scanning"
        task.started_at = django_timezone.now()
        task.save(update_fields=["detect_status", "started_at"])
        return Response(InspectTaskSerializer(task).data)


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


# views.py

class WaylineViewSet(viewsets.ModelViewSet):
    queryset = Wayline.objects.all()
    serializer_class = WaylineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['wayline_id', 'name', 'description', 'created_by']
    ordering_fields = ['created_at', 'updated_at', 'status', 'name']
    ordering = ['-created_at']

    # =========================================================
    # 🆕 新增接口: 同步航线数据 (POST /waylines/sync_data/)
    # =========================================================
    @action(detail=False, methods=['post'])
    def sync_data(self, request):
        """
        [硬编码配置版] 主动调用司空 API 同步航线列表到本地数据库
        """
        print("🔄 [Wayline Sync] 开始同步航线列表 (使用 Settings 配置)...")

        try:
            # 1. 从 settings 读取硬编码参数
            base_url = getattr(settings, "DJI_API_BASE_URL", "http://192.168.10.2").rstrip('/')

            headers = {
                "X-User-Token": getattr(settings, "DJI_X_USER_TOKEN", ""),
                "X-Project-Uuid": getattr(settings, "DJI_X_PROJECT_UUID", ""),
                "X-Request-Id": getattr(settings, "DJI_X_Request_ID", "uuid-123"),
                "X-Language": getattr(settings, "DJI_X_LANGUAGE", "zh"),
                "Content-Type": "application/json"
            }

            # 简单的参数校验
            if not headers["X-User-Token"] or not headers["X-Project-Uuid"]:
                return Response({"code": 500, "msg": "Settings 中缺少 DJI_X_USER_TOKEN 或 DJI_X_PROJECT_UUID"},
                                status=500)

            # 2. 发起请求
            # API 路径: /openapi/v0.1/wayline
            api_url = f"{base_url}/openapi/v0.1/wayline"

            # 假设你的接口支持分页，我们可以先传大一点的 page_size
            params = {
                "page": 1,
                "page_size": 100
            }

            print(f"   -> 请求接口: {api_url}")
            resp = requests.get(api_url, headers=headers, params=params, timeout=10)

            if resp.status_code != 200:
                print(f"❌ 同步失败: {resp.status_code} - {resp.text}")
                return Response({"code": 502, "msg": f"司空接口报错: {resp.status_code}"}, status=502)

            # 3. 解析数据
            resp_json = resp.json()

            # 根据你提供的 JSON 结构，数据可能在 data.list 里，或者 data 本身就是 list
            # 结构通常是: { "code": 0, "data": { "list": [...] } }
            raw_data = resp_json.get("data", {})
            wayline_list = []

            if isinstance(raw_data, dict):
                wayline_list = raw_data.get("list", [])
            elif isinstance(raw_data, list):
                wayline_list = raw_data

            print(f"   -> 获取到 {len(wayline_list)} 条航线数据")

            # 4. 入库更新
            updated_count = 0
            for item in wayline_list:
                w_id = item.get("id")
                w_name = item.get("name")

                # 你的 JSON 里有 "update_time": 1766109565421
                # 这是一个毫秒级时间戳，如果需要存，可以转一下，或者直接存到 description 里备注
                raw_update_time = item.get("update_time")

                if not w_id: continue

                # 执行 Update 或 Create
                Wayline.objects.update_or_create(
                    wayline_id=w_id,
                    defaults={
                        "name": w_name,
                        "description": f"Synced from API. UpdateTime: {raw_update_time}",
                        "status": "ACTIVE"
                    }
                )
                updated_count += 1

            print(f"✅ [Wayline Sync] 同步完成，已更新 {updated_count} 条记录")
            return Response({"code": 200, "msg": "同步成功", "count": updated_count})

        except Exception as e:
            print(f"❌ 同步异常: {e}")
            import traceback
            traceback.print_exc()
            return Response({"code": 500, "msg": str(e)}, status=500)


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


# ======================================================================
# 直播监听管理（保护区检测）
# ======================================================================

# 全局变量：存储正在运行的监听线程
live_monitor_threads = {}
# 格式: { "stream_id": { "thread": Thread对象, "stop_event": Event对象, "task": InspectTask对象 } }


class LiveMonitorViewSet(viewsets.ViewSet):
    """
    直播监听控制接口（保护区检测）
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='start')
    def start_monitor(self, request):
        """
        启动直播监听
        POST /api/v1/live-monitor/start/
        Body: { "stream_id": "drone01", "interval": 3.0 }
        """
        stream_id = request.data.get('stream_id', 'drone01')
        interval = float(request.data.get('interval', 3.0))

        # 检查是否已经在运行
        if stream_id in live_monitor_threads:
            return Response(
                {"status": "error", "message": f"流 {stream_id} 的监听已在运行中"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 创建停止事件
            stop_event = threading.Event()

            # 启动监听线程
            monitor_thread = threading.Thread(
                target=self._run_monitor,
                args=(stream_id, interval, stop_event),
                daemon=True
            )
            monitor_thread.start()

            # 等待一下确保任务创建完成
            time.sleep(0.5)

            # 查找刚创建的任务
            current_task = InspectTask.objects.filter(
                external_task_id__contains=f"直播_{stream_id}"
            ).order_by('-created_at').first()

            # 记录线程信息
            live_monitor_threads[stream_id] = {
                "thread": monitor_thread,
                "stop_event": stop_event,
                "task": current_task,
                "started_at": django_timezone.now().isoformat()
            }

            return Response({
                "status": "success",
                "message": f"直播监听已启动: {stream_id}",
                "stream_id": stream_id,
                "interval": interval,
                "task_id": current_task.id if current_task else None
            })

        except Exception as e:
            print(f"❌ 启动监听失败: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='stop')
    def stop_monitor(self, request):
        """
        停止直播监听
        POST /api/v1/live-monitor/stop/
        Body: { "stream_id": "drone01" }
        """
        stream_id = request.data.get('stream_id', 'drone01')

        if stream_id not in live_monitor_threads:
            return Response(
                {"status": "error", "message": f"流 {stream_id} 没有运行中的监听"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 发送停止信号
            monitor_info = live_monitor_threads[stream_id]
            monitor_info["stop_event"].set()

            # 等待线程结束（最多3秒）
            monitor_info["thread"].join(timeout=3)

            # 更新任务状态为完成
            if monitor_info["task"]:
                task = monitor_info["task"]
                task.detect_status = "done"
                task.finished_at = django_timezone.now()
                task.save(update_fields=['detect_status', 'finished_at'])

            # 移除记录
            del live_monitor_threads[stream_id]

            return Response({
                "status": "success",
                "message": f"直播监听已停止: {stream_id}"
            })

        except Exception as e:
            print(f"❌ 停止监听失败: {e}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='status')
    def get_status(self, request):
        """
        获取所有监听状态
        GET /api/v1/live-monitor/status/
        """
        stream_id = request.query_params.get('stream_id')

        if stream_id:
            # 查询单个流状态
            if stream_id in live_monitor_threads:
                info = live_monitor_threads[stream_id]
                return Response({
                    "stream_id": stream_id,
                    "is_running": True,
                    "started_at": info["started_at"],
                    "task_id": info["task"].id if info["task"] else None
                })
            else:
                return Response({
                    "stream_id": stream_id,
                    "is_running": False
                })
        else:
            # 查询所有流状态
            status_list = []
            for sid, info in live_monitor_threads.items():
                status_list.append({
                    "stream_id": sid,
                    "is_running": True,
                    "started_at": info["started_at"],
                    "task_id": info["task"].id if info["task"] else None
                })
            return Response({
                "monitors": status_list,
                "count": len(status_list)
            })

    def _run_monitor(self, stream_id, interval, stop_event):
        """
        监听主逻辑（在独立线程中运行）
        """
        # 配置区
        ZLM_API_HOST = "http://zlm:80"
        ZLM_SECRET = "035c73f7-bb6b-4889-a715-d9eb2d1925cc"
        bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

        print(f"🚀 [监听启动] Stream: {stream_id} | 等待首帧截图...")

        s3 = get_minio_client()
        frame_count = 0
        current_task = None  # ⭐ 延迟创建任务
        
        # 用于标记是否已成功截取第一帧
        first_frame_captured = False

        # 循环抽帧（直到收到停止信号）
        while not stop_event.is_set():
            try:
                snap_api = f"{ZLM_API_HOST}/index/api/getSnap"
                params = {
                    "secret": ZLM_SECRET,
                    "url": f"rtmp://127.0.0.1:1935/live/{stream_id}",
                    "timeout_sec": 5,
                    "expire_sec": 1
                }

                resp = requests.get(snap_api, params=params, timeout=5)
                res_json = resp.json()

                if res_json.get('code') == 0:
                    # ⭐ 第一次成功截图时，才创建任务
                    if not first_frame_captured:
                        print(f"✅ [首帧成功] 开始创建任务...")
                        
                        # 创建任务结构
                        today_str = datetime.now().strftime('%Y%m%d')
                        parent_task_name = f"{today_str}保护区直播汇总"

                        parent_task, _ = InspectTask.objects.get_or_create(
                            external_task_id=parent_task_name,
                            defaults={
                                "bucket": bucket_name,
                                "detect_status": "done",
                                "prefix_list": []
                            }
                        )

                        category, _ = AlarmCategory.objects.get_or_create(
                            code="protection_zone",
                            defaults={"name": "保护区实时检测", "match_keyword": "保护区"}
                        )

                        now_time = datetime.now().strftime('%H%M%S')
                        child_task_name = f"直播_{stream_id}_{now_time}"
                        virtual_prefix = f"fh_sync/live/{parent_task_name}/{child_task_name}/"

                        current_task = InspectTask.objects.create(
                            parent_task=parent_task,
                            external_task_id=child_task_name,
                            bucket=bucket_name,
                            prefix_list=[virtual_prefix],
                            detect_category=category,
                            detect_status="processing"
                        )
                        
                        # 更新全局线程记录（补充任务信息）
                        if stream_id in live_monitor_threads:
                            live_monitor_threads[stream_id]["task"] = current_task
                        
                        print(f"📂 [任务创建] {parent_task_name} -> {child_task_name}")
                        first_frame_captured = True
                    
                    # 下载截图
                    img_download_url = ZLM_API_HOST + res_json['data']
                    img_resp = requests.get(img_download_url, timeout=5)

                    if img_resp.status_code == 200:
                        file_bytes = io.BytesIO(img_resp.content)
                        file_size = file_bytes.getbuffer().nbytes
                        fname = f"frame_{datetime.now().strftime('%H%M%S_%f')}.jpg"
                        object_key = f"{current_task.prefix_list[0]}{fname}"

                        s3.put_object(
                            Bucket=bucket_name,
                            Key=object_key,
                            Body=file_bytes,
                            Length=file_size,
                            ContentType='image/jpeg'
                        )

                        InspectImage.objects.create(
                            inspect_task=current_task,
                            object_key=object_key,
                            detect_status='pending',
                            wayline=current_task.wayline
                        )
                        frame_count += 1
                        print(f"📸 [截图] {fname} (总计: {frame_count})")

                        # 异步触发检测
                        threading.Thread(target=auto_trigger_detect, args=(current_task,)).start()
                else:
                    # 流还没推上来，等待
                    if not first_frame_captured:
                        print(f"⏳ [等待推流] {stream_id}...")

            except Exception as e:
                if not stop_event.is_set():
                    print(f"❌ 截图异常: {e}")

            # 等待间隔（可被停止信号中断）
            stop_event.wait(interval)

        print(f"🛑 [监听停止] Stream: {stream_id} | 共截取 {frame_count} 帧")
        
        # 停止时更新任务状态
        if current_task:
            current_task.detect_status = "done"
            current_task.finished_at = django_timezone.now()
            current_task.save(update_fields=['detect_status', 'finished_at'])
            print(f"✅ [任务完成] {current_task.external_task_id}")


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
                
                # ⭐ 关键修改：根据图片实际检测进度判断任务状态
                total_images = task.images.count()
                if total_images > 0:
                    done_images = task.images.filter(detect_status='done').count()
                    processing_images = task.images.filter(detect_status='processing').count()
                    
                    # 如果有图片在检测中，显示"检测中"
                    if processing_images > 0:
                        status = "processing"
                    # 如果还有未检测的图片（pending），显示"检测中"
                    elif done_images < total_images:
                        status = "processing"
                    # 所有图片都检测完成，才显示"已完成"
                    else:
                        status = task.detect_status
                else:
                    # 没有图片，使用任务本身的状态
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


class WaylineFingerprintManager:

    @staticmethod
    def get_api_headers_and_host():
        """从 Settings 获取配置"""
        base_url = getattr(settings, "DJI_API_BASE_URL", "http://192.168.10.2").rstrip('/')
        headers = {
            "X-User-Token": getattr(settings, "DJI_X_USER_TOKEN", ""),
            "X-Project-Uuid": getattr(settings, "DJI_X_PROJECT_UUID", ""),
            "X-Request-Id": getattr(settings, "DJI_X_Request_ID", "uuid-123"),
            "X-Language": getattr(settings, "DJI_X_LANGUAGE", "zh"),
            "Content-Type": "application/json"
        }
        if not headers["X-User-Token"] or not headers["X-Project-Uuid"]:
            raise Exception("Settings 中缺少 DJI_X_USER_TOKEN 或 DJI_X_PROJECT_UUID 配置")
        return headers, base_url

    @staticmethod
    def sync_by_keywords():
        """
        🚀 [按需同步核心逻辑]
        1. 获取 API 所有航线列表。
        2. 遍历本地 AlarmCategory 获取匹配规则 (例如: 轨道, 桥梁)。
        3. 只有名字匹配上的航线，才下载 KMZ 并存入指纹表。
        """
        print("🔄 [Fingerprint] 开始按关键字匹配并同步...")

        try:
            # 1. 准备配置和规则
            headers, base_url = WaylineFingerprintManager.get_api_headers_and_host()

            # 获取所有配置了关键字的分类
            # 例如: [{"code": "rail", "match_keyword": "轨道"}, {"code": "bridge", "match_keyword": "桥梁"}]
            categories = AlarmCategory.objects.exclude(match_keyword__isnull=True).exclude(match_keyword__exact='')

            if not categories.exists():
                print("⚠️ [Stop] 本地 AlarmCategory 表未配置 match_keyword，无法进行匹配。")
                return

            print(f"   -> 加载匹配规则: {[c.name + ':' + c.match_keyword for c in categories]}")

            # 2. 调用 API 获取航线列表 (仅获取名字和ID)
            # API: GET /openapi/v0.1/wayline
            list_url = f"{base_url}/openapi/v0.1/wayline"

            # 分页获取所有航线 (这里简化写，假设一页够用，不够可加循环)
            res = requests.get(list_url, headers=headers, params={"page": 1, "page_size": 200}, timeout=10)
            if res.status_code != 200:
                print(f"❌ 获取航线列表失败: {res.status_code}")
                return

            res_json = res.json()
            raw_data = res_json.get('data', [])
            wayline_list = raw_data.get('list', []) if isinstance(raw_data, dict) else raw_data

            print(f"   -> API 返回 {len(wayline_list)} 条航线，开始筛选...")

            matched_count = 0

            # 3. 循环匹配
            for item in wayline_list:
                w_id = item.get('id')
                w_name = item.get('name')

                if not w_id or not w_name: continue

                # 🔥 核心匹配逻辑
                matched_category = None
                for cat in categories:
                    if cat.match_keyword in w_name:
                        matched_category = cat
                        break  # 匹配到一个就停止，避免重复

                # 只有匹配成功的才处理
                if matched_category:
                    print(f"   ✅ [Match] 航线 '{w_name}' 命中规则: {matched_category.name}")

                    # 4. 获取详情拿到 download_url
                    WaylineFingerprintManager.process_single_wayline(
                        base_url, headers, w_id, w_name, matched_category
                    )
                    matched_count += 1
                else:
                    # print(f"   ⚪ [Skip] 航线 '{w_name}' 未匹配任何关键字")
                    pass

            print(f"🏁 同步完成: API共 {len(wayline_list)} 条，匹配并入库 {matched_count} 条。")

        except Exception as e:
            print(f"❌ 同步流程异常: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def process_single_wayline(base_url, headers, wayline_id, wayline_name, category_obj):
        """
        处理单个命中的航线：入库 Wayline -> 获取 URL -> 下载 KMZ -> 入库 Fingerprint
        """
        try:
            # A. 确保存储了 Wayline 基本信息
            local_wayline, _ = Wayline.objects.update_or_create(
                wayline_id=wayline_id,
                defaults={
                    "name": wayline_name,
                    "detect_type": category_obj.code  # 顺便更新下冗余字段
                }
            )

            # B. 调用详情接口获取 download_url
            detail_url = f"{base_url}/openapi/v0.1/wayline/{wayline_id}"
            res = requests.get(detail_url, headers=headers, timeout=10)

            download_url = None
            if res.status_code == 200:
                data = res.json().get('data', {})
                download_url = data.get('download_url')

            if not download_url:
                print(f"      ⚠️ 未获取到 download_url，跳过下载")
                return

            # C. 下载并解析 KMZ
            print(f"      📥 下载 KMZ 解析指纹...")
            r = requests.get(download_url, timeout=30)
            if r.status_code != 200:
                return

            uuid_set = set()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                kml_files = [n for n in z.namelist() if n.endswith('template.kml')]
                if kml_files:
                    with z.open(kml_files[0]) as f:
                        content = f.read().decode('utf-8')
                        found = re.findall(r'<wpml:actionUUID>(.*?)</wpml:actionUUID>', content)
                        uuid_set.update(found)

            # D. 存入指纹表 (包含 detect_category)
            if uuid_set:
                fp, _ = WaylineFingerprint.objects.get_or_create(wayline=local_wayline)
                fp.detect_category = category_obj  # 🔥 关键：把匹配到的类型存进去
                fp.action_uuids = list(uuid_set)
                fp.source_url = download_url
                fp.save()
                print(f"      💾 指纹入库成功 (包含 {len(uuid_set)} 个 UUID)")

        except Exception as e:
            print(f"      ❌ 处理单条航线出错: {e}")
    @staticmethod
    def identify(image_uuid):
        """根据图片UUID反查航线"""
        all_fps = WaylineFingerprint.objects.all()
        for fp in all_fps:
            if image_uuid in fp.action_uuids:
                return fp.wayline
        return None