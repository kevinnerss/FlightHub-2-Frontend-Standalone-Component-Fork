import time
import requests
import io
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from telemetry_app.models import InspectTask, InspectImage, AlarmCategory
from telemetry_app.views import get_minio_client


class Command(BaseCommand):
    help = '测试直播监听 - 调试版本（包含详细日志）'

    def add_arguments(self, parser):
        parser.add_argument('--stream_id', type=str, default='drone01', help='流ID')
        parser.add_argument('--interval', type=float, default=3.0, help='截图间隔(秒)')
        parser.add_argument('--max_frames', type=int, default=5, help='最大测试帧数（0=无限制）')

    def handle(self, *args, **options):
        stream_id = options['stream_id']
        interval = options['interval']
        max_frames = options['max_frames']

        # ================= 配置区 =================
        ZLM_API_HOST = "http://zlm:80"
        ZLM_SECRET = "035c73f7-bb6b-4889-a715-d9eb2d1925cc"
        bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")
        # =========================================

        self.stdout.write(self.style.WARNING(f"🧪 开始测试直播监听"))
        self.stdout.write(f"   - 流ID: {stream_id}")
        self.stdout.write(f"   - 间隔: {interval}秒")
        self.stdout.write(f"   - 最大帧数: {max_frames if max_frames > 0 else '无限制'}")
        self.stdout.write(f"   - ZLM: {ZLM_API_HOST}")
        self.stdout.write(f"   - MinIO桶: {bucket_name}")

        # 1. 测试ZLM连接
        self.stdout.write(f"\n📡 步骤1：测试ZLM流媒体服务器连接...")
        snap_api = f"{ZLM_API_HOST}/index/api/getSnap"
        params = {
            "secret": ZLM_SECRET,
            "url": f"rtmp://127.0.0.1:1935/live/{stream_id}",
            "timeout_sec": 5,
            "expire_sec": 1
        }

        try:
            resp = requests.get(snap_api, params=params, timeout=10)
            self.stdout.write(f"   - HTTP状态码: {resp.status_code}")

            if resp.status_code == 200:
                res_json = resp.json()
                self.stdout.write(f"   - 响应JSON: {res_json}")

                if res_json.get('code') == 0:
                    self.stdout.write(self.style.SUCCESS("   ✅ ZLM连接成功！流已在线"))
                else:
                    self.stdout.write(self.style.WARNING(f"   ⚠️ ZLM返回错误: {res_json.get('code')} - {res_json.get('msg')}"))
                    self.stdout.write(self.style.WARNING("   请确认推流已推送到服务器！"))
                    return
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ ZLM请求失败: {resp.status_code}"))
                self.stdout.write(f"   响应内容: {resp.text[:200]}")
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ ZLM连接异常: {e}"))
            self.stdout.write(self.style.ERROR("   请确认ZLM容器是否运行！"))
            return

        # 2. 测试MinIO连接
        self.stdout.write(f"\n📦 步骤2：测试MinIO连接...")
        try:
            s3 = get_minio_client()
            # 测试列出桶
            buckets = s3.list_buckets()
            self.stdout.write(self.style.SUCCESS(f"   ✅ MinIO连接成功！"))
            self.stdout.write(f"   - 桶列表: {[b['Name'] for b in buckets]}")

            if bucket_name not in [b['Name'] for b in buckets]:
                self.stdout.write(self.style.WARNING(f"   ⚠️ 桶 '{bucket_name}' 不存在，尝试创建..."))
                s3.create_bucket(Bucket=bucket_name)
                self.stdout.write(self.style.SUCCESS(f"   ✅ 桶 '{bucket_name}' 创建成功"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ MinIO连接失败: {e}"))
            return

        # 3. 创建测试任务
        self.stdout.write(f"\n📂 步骤3：创建测试任务...")
        try:
            today_str = datetime.datetime.now().strftime('%Y%m%d')
            # 🔥 修改：使用与其他检测类型统一的父任务命名规则
            parent_task_id = f"{today_str}巡检任务"

            parent_task, _ = InspectTask.objects.get_or_create(
                external_task_id=parent_task_id,
                defaults={
                    "bucket": bucket_name,
                    "detect_status": "pending",  # 🔥 改为pending，与其他任务一致
                    "prefix_list": []
                }
            )

            category, _ = AlarmCategory.objects.get_or_create(
                code="protected_area",
                defaults={"name": "保护区", "match_keyword": "保护区"}
            )

            now_time = datetime.datetime.now().strftime('%H%M%S')
            sub_task_id = f"{today_str}保护区检测直播_{stream_id}_{now_time}"
            virtual_prefix = f"fh_sync/live/{today_str}巡检任务/{sub_task_id}/"

            current_task = InspectTask.objects.create(
                parent_task=parent_task,
                external_task_id=sub_task_id,
                bucket=bucket_name,
                prefix_list=[virtual_prefix],
                detect_category=category,
                detect_status="processing"
            )

            self.stdout.write(self.style.SUCCESS(f"   ✅ 任务创建成功！ID: {current_task.id}"))
            self.stdout.write(f"   - 父任务: {parent_task_id}")
            self.stdout.write(f"   - 子任务: {sub_task_id}")
            self.stdout.write(f"   - 路径前缀: {virtual_prefix}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ 任务创建失败: {e}"))
            import traceback
            traceback.print_exc()
            return

        # 4. 开始循环截图测试
        self.stdout.write(f"\n📸 步骤4：开始循环截图...")
        frame_count = 0
        error_count = 0

        while True:
            if max_frames > 0 and frame_count >= max_frames:
                self.stdout.write(self.style.SUCCESS(f"\n✅ 达到最大帧数限制 ({max_frames})，测试结束"))
                break

            try:
                # 请求截图
                resp = requests.get(snap_api, params=params, timeout=10)

                # 🔥 修复：ZLM直接返回JPEG二进制数据
                if resp.status_code == 200:
                    # 检查是否是图片数据（JPEG魔数）
                    if resp.content[:4] == b'\xff\xd8\xff\xe0' or 'image' in resp.headers.get('Content-Type', ''):
                        # 直接使用resp.content
                        file_bytes = io.BytesIO(resp.content)
                        file_size = len(resp.content)
                        fname = f"test_frame_{datetime.datetime.now().strftime('%H%M%S_%f')}.jpg"
                        object_key = f"{virtual_prefix}{fname}"

                        # 上传到MinIO
                        s3.put_object(
                            Bucket=bucket_name,
                            Key=object_key,
                            Body=file_bytes,
                            ContentLength=file_size,
                            ContentType='image/jpeg'
                        )

                        # 入库
                        InspectImage.objects.create(
                            inspect_task=current_task,
                            object_key=object_key,
                            detect_status='pending',
                            wayline=current_task.wayline
                        )

                        frame_count += 1
                        file_size_kb = int(file_size / 1024)
                        self.stdout.write(self.style.SUCCESS(f"   ✅ 帧#{frame_count}: {fname} ({file_size_kb}KB)"))
                    else:
                        # 尝试JSON模式（备用）
                        try:
                            res_json = resp.json()
                            error_count += 1
                            self.stdout.write(self.style.WARNING(f"   ⚠️ ZLM返回JSON: code={res_json.get('code')}, msg={res_json.get('msg')}"))
                        except:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f"   ❌ 响应既不是图片也不是JSON"))
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"   ❌ HTTP错误: {resp.status_code}"))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"   ❌ 异常: {e}"))

            if error_count >= 5:
                self.stdout.write(self.style.ERROR(f"\n❌ 连续错误次数过多 ({error_count})，测试终止"))
                break

            self.stdout.write(f"   ⏱️ 等待 {interval} 秒...")
            time.sleep(interval)

        # 5. 测试总结
        self.stdout.write(f"\n📊 测试总结:")
        self.stdout.write(f"   - 成功截图: {frame_count} 帧")
        self.stdout.write(f"   - 错误次数: {error_count} 次")
        self.stdout.write(f"   - 任务ID: {current_task.id}")

        # 查询实际入库数量
        image_count = InspectImage.objects.filter(inspect_task=current_task).count()
        self.stdout.write(f"   - 入库图片: {image_count} 张")

        self.stdout.write(self.style.SUCCESS(f"\n✅ 测试完成！"))
