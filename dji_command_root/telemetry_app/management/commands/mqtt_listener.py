import json
import os
import time
import random
import threading
import requests
import paho.mqtt.client as mqtt
from urllib.parse import urlparse, urlunparse
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import urllib3

# 禁用 HTTPS 不安全警告 (针对私有化部署自签名证书)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    help = '启动 MQTT 监听服务，连接司空 EMQX 并异步下载文件'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='开启详细调试日志')

    def handle(self, *args, **options):
        self.debug_mode = options['debug']

        # ================= 1. 配置区域 =================
        # MQTT 连接信息
        self.broker_ip = os.getenv('MQTT_BROKER_IP', '127.0.0.1')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', 1883))
        self.username = os.getenv('MQTT_USER', '')
        self.password = os.getenv('MQTT_PASSWORD', '')

        # 修正 MinIO 地址 (关键配置)
        # 如果司空返回的是内网 Docker IP (如 172.x.x.x)，这里填宿主机的公网/局域网 IP
        # 如果不需要替换，保持为空
        self.minio_external_host = os.getenv('MINIO_EXTERNAL_HOST', '')
        # 例如: '192.168.1.100:9000'

        # 文件保存路径
        self.download_dir = os.path.join(settings.MEDIA_ROOT, 'dji_downloads')
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # Client ID 必须唯一
        client_id = f"django_backend_{random.randint(10000, 99999)}"

        # ==============================================

        self.stdout.write(self.style.WARNING(f"⚙️  正在启动司空数据监听器..."))
        self.stdout.write(f"   - Broker: {self.broker_ip}:{self.broker_port}")
        self.stdout.write(f"   - 保存路径: {self.download_dir}")

        # 初始化 MQTT 客户端
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        client.keepalive = 60  # 心跳间隔

        if self.username:
            client.username_pw_set(self.username, self.password)

        # 绑定回调函数
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        # 开始连接循环
        while True:
            try:
                self.stdout.write(f"🚀 尝试连接到 EMQX...")
                client.connect(self.broker_ip, self.broker_port, 60)
                # 阻塞运行，自动处理重连
                client.loop_forever()
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\n🛑 服务已手动停止"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ 连接异常: {e}"))
                time.sleep(5)  # 等待5秒后重连

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """连接成功后的订阅逻辑"""
        if rc == 0:
            self.stdout.write(self.style.SUCCESS('✅ 连接成功! 正在订阅主题...'))

            # 优化：只订阅必要的 Topic，减少无用消息处理压力
            topics = [
                ("sys/product/+/device/+/osd", 0),  # 实时位置信息
                ("sys/product/+/device/+/events", 1),  # 告警与事件
                ("sys/product/+/device/+/services_reply", 1),  # 服务响应（含文件上传回调）
                ("sys/product/+/device/+/requests", 0)  # 下行指令（可选，用于调试）
            ]
            client.subscribe(topics)
            self.stdout.write(f"   - 已订阅 {len(topics)} 类核心主题")
        else:
            self.stdout.write(self.style.ERROR(f'❌ 连接拒绝，返回码: {rc}'))

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        if rc != 0:
            self.stdout.write(self.style.WARNING('⚠️  连接意外断开，正在尝试重连...'))

    def on_message(self, client, userdata, msg):
        """
        消息处理入口
        注意：此函数必须快速执行完毕，不能包含耗时操作（如大文件下载）
        """
        try:
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)

            # 1. 处理位置信息 (高频数据，同步快速处理)
            if self.is_position_data(msg.topic, data):
                self.handle_position_data(data, msg.topic)
                return

            # 2. 判断是否为文件上传事件
            if self.is_upload_event(data):
                # self.stdout.write(f"📨 收到潜在文件消息: {msg.topic}")

                # ⚠️ 关键修改：开启新线程进行下载，坚决不阻塞 MQTT 主循环
                # daemon=True 表示主程序退出时子线程自动结束
                t = threading.Thread(target=self._process_download_thread, args=(data, msg.topic), daemon=True)
                t.start()

        except json.JSONDecodeError:
            pass
        except Exception as e:
            if self.debug_mode:
                self.stdout.write(self.style.ERROR(f"处理消息异常: {e}"))

    # ================= 业务逻辑区 =================

    def is_upload_event(self, data):
        """判断消息是否包含文件上传信息"""
        # 逻辑1: 标准回调
        if data.get('method') == 'fileupload_callback':
            return True
        # 逻辑2: 包含 URL 的数据包
        payload = data.get('data', data)
        if isinstance(payload, dict) and 'url' in payload:
            # 简单的 URL 校验
            if payload['url'].startswith('http'):
                return True
        return False

    def _process_download_thread(self, data, topic):
        """
        [子线程] 执行下载任务
        这里可以执行耗时操作，不会影响 MQTT 心跳
        """
        try:
            file_info = data.get('data', data)
            original_url = file_info.get('url')

            if not original_url:
                return

            # --- 地址修正逻辑 (针对私有化部署) ---
            final_url = original_url
            if self.minio_external_host:
                # 解析原始 URL
                parsed = urlparse(original_url)
                # 替换 netloc (域名:端口)
                new_parsed = parsed._replace(netloc=self.minio_external_host)
                final_url = urlunparse(new_parsed)
                # 如果从 http 变成 https 或反之，需在这里额外处理 scheme

            # --- 生成文件名 ---
            file_name = file_info.get('object_key')  # 优先使用 key
            if not file_name:
                file_name = file_info.get('file_name')
            if not file_name:
                file_name = os.path.basename(urlparse(final_url).path)
            if not file_name:
                file_name = f"unknown_{int(time.time())}.dat"

            # 清理文件名中的路径分隔符，防止存错目录
            file_name = os.path.basename(file_name)
            save_path = os.path.join(self.download_dir, file_name)

            if os.path.exists(save_path):
                self.stdout.write(f"   ⚠️ 文件已存在，跳过: {file_name}")
                return

            # --- 开始下载 ---
            self.stdout.write(self.style.NOTICE(f"⬇️ [线程启动] 开始下载: {file_name}"))

            # 使用 requests 的 stream 模式
            start_time = time.time()
            response = requests.get(final_url, stream=True, verify=False, timeout=120)

            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                duration = time.time() - start_time
                file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ 下载完成: {file_name} ({file_size_mb:.2f}MB, 耗时 {duration:.1f}s)"
                ))
            else:
                self.stdout.write(self.style.ERROR(f"❌ 下载失败 HTTP {response.status_code}: {final_url}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 下载线程出错: {e}"))

    def is_position_data(self, topic, data):
        """判断是否为 OSD 数据"""
        return 'osd' in topic or ('latitude' in str(data))

    def handle_position_data(self, data, topic):
        """
        处理位置数据入库
        注意：此处需要 import 你的 DronePosition 模型
        """
        # 避免未导入模型报错
        try:
            from telemetry_app.models import DronePosition
        except ImportError:
            # 如果没有这个 app，直接返回，避免报错
            return

        try:
            payload = data.get('data', data)
            if not isinstance(payload, dict):
                return

            lat = payload.get('latitude') or payload.get('lat')
            lon = payload.get('longitude') or payload.get('lon')
            alt = payload.get('height') or payload.get('altitude')

            if lat and lon:
                # --- 增强的过滤逻辑 (User Request) ---
                # 1. 获取 SN 和 Gateway
                sn = data.get('sn')
                gateway_raw = data.get('gateway')

                # 2. 解析 Gateway SN (可能是 dict 也可能是 str)
                gateway_sn = None
                if isinstance(gateway_raw, dict):
                    gateway_sn = gateway_raw.get('sn')
                elif isinstance(gateway_raw, str):
                    gateway_sn = gateway_raw

                # 3. 过滤规则：
                #    规则A: 如果没有 SN，通常是机场心跳包 -> 忽略
                #    规则B: 如果 SN == Gateway，是机场自身位置 -> 忽略
                if not sn:
                    # if self.debug_mode:
                    #     print(f"🚫 [OSD] 忽略无SN消息 (Gateway: {gateway_sn})")
                    return

                if gateway_sn and sn == gateway_sn:
                    # if self.debug_mode:
                    #     print(f"🚫 [OSD] 忽略机场自身位置 (SN: {sn})")
                    return

                # 4. 确认通过过滤，使用 SN
                device_sn = sn

                DronePosition.objects.create(
                    device_sn=device_sn,
                    latitude=lat,
                    longitude=lon,
                    altitude=alt if alt else 0,
                    raw_data=data,
                    timestamp=timezone.now()
                )
                # 只有在 debug 模式下才打印 OSD 日志，防止刷屏
                if self.debug_mode:
                    print(f"📍 OSD: {device_sn} -> {lat}, {lon}")

        except Exception as e:
            # 数据库错误不应中断 MQTT 循环
            print(f"DB Error: {e}")