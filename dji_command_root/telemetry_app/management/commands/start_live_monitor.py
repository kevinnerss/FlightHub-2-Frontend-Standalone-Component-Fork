import time
import requests
import io
import datetime
import threading
from django.core.management.base import BaseCommand
from django.conf import settings
from telemetry_app.models import InspectTask, InspectImage, AlarmCategory
# 引入你在 views.py 里定义好的工具函数
from telemetry_app.views import get_minio_client, auto_trigger_detect


class Command(BaseCommand):
    help = '启动保护区直播异常检测监听 (IP: 192.168.10.10)'

    def add_arguments(self, parser):
        parser.add_argument('--stream_id', type=str, required=True, help='流ID (例如 drone01)')
        parser.add_argument('--interval', type=float, default=3.0, help='截图间隔(秒)')

    def handle(self, *args, **options):
        stream_id = options['stream_id']
        interval = options['interval']

        # ================= 配置区 =================
        # Django (backend) 访问 ZLM 的内部地址
        ZLM_API_HOST = "http://zlm:80"

        # ZLM 默认 Secret (如果你没挂载配置文件改过的话)
        # 如果你改了 zlm_config.ini，这里要换成你改的密码
        ZLM_SECRET = "QIlf1WwTa1phKL6cTxWcCm0YhIlQFGGl"
        # =========================================

        # 1. 准备任务结构 (自动归档到当天)
        today_str = datetime.datetime.now().strftime('%Y%m%d')
        parent_task_name = f"{today_str}保护区直播汇总"
        bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "dji")

        # A. 创建/获取父任务
        parent_task, _ = InspectTask.objects.get_or_create(
            external_task_id=parent_task_name,
            defaults={
                "bucket": bucket_name,
                "detect_status": "done",
                "prefix_list": []
            }
        )

        # B. 确保有“保护区检测”这个分类
        category, _ = AlarmCategory.objects.get_or_create(
            code="protection_zone",
            defaults={"name": "保护区实时检测", "match_keyword": "保护区"}
        )

        # C. 创建本次直播的子任务
        now_time = datetime.datetime.now().strftime('%H%M%S')
        child_task_name = f"直播_{stream_id}_{now_time}"
        # 构造一个虚拟路径，防止 Poller 扫描冲突
        virtual_prefix = f"fh_sync/live/{parent_task_name}/{child_task_name}/"

        current_task = InspectTask.objects.create(
            parent_task=parent_task,
            external_task_id=child_task_name,
            bucket=bucket_name,
            prefix_list=[virtual_prefix],
            detect_category=category,
            detect_status="processing"
        )

        print(f"🚀 [监听启动] Server: 192.168.10.10 | Stream: {stream_id}")
        print(f"📂 [任务创建] {parent_task_name} -> {child_task_name}")

        s3 = get_minio_client()

        # 2. 循环抽帧
        while True:
            try:
                # 构造 ZLM 截图请求
                # url 参数解释：告诉 ZLM 去截取 "rtmp://127.0.0.1..." 这个流
                # 因为 ZLM 自己就在本机，所以填 127.0.0.1 它是能找到自己的
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
                    # 获取图片下载地址 (注意：ZLM 返回的可能是相对路径或内部IP)
                    # res_json['data'] 类似 "/index/api/getSnap/..."
                    # 我们需要拼上 ZLM 的内部地址去下载
                    img_download_url = ZLM_API_HOST + res_json['data']

                    img_resp = requests.get(img_download_url, timeout=5)

                    if img_resp.status_code == 200:
                        # --- 上传 MinIO ---
                        file_bytes = io.BytesIO(img_resp.content)
                        file_size = file_bytes.getbuffer().nbytes
                        fname = f"frame_{datetime.datetime.now().strftime('%H%M%S_%f')}.jpg"
                        object_key = f"{virtual_prefix}{fname}"

                        s3.put_object(
                            Bucket=bucket_name,
                            Key=object_key,
                            Body=file_bytes,
                            Length=file_size,
                            ContentType='image/jpeg'
                        )

                        # --- 入库 & 触发检测 ---
                        InspectImage.objects.create(
                            inspect_task=current_task,
                            object_key=object_key,
                            detect_status='pending',
                            wayline=current_task.wayline
                        )
                        print(f"📸 [截图] {fname} -> AI检测中...")

                        # 异步触发 AI (复用 views.py 的逻辑)
                        threading.Thread(target=auto_trigger_detect, args=(current_task,)).start()
                else:
                    # code != 0 通常意味着流还没推上来
                    # print(f"等待推流... {res_json.get('msg')}")
                    pass

            except Exception as e:
                print(f"❌ 异常: {e}")

            time.sleep(interval)