import json
import os
import time
import random
import requests
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.conf import settings
import urllib3

# 禁用 HTTPS 不安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    help = '启动 MQTT 监听服务，连接本地 EMQX 并自动下载文件'

    def handle(self, *args, **options):
        # ================= 1. EMQX 连接配置 =================
        # 如果是本地电脑运行，默认就是 127.0.0.1
        # 如果是 Docker 运行，需填写宿主机 IP 或 emqx 容器名
        broker_ip = os.getenv('MQTT_BROKER_IP', '127.0.0.1')
        broker_port = int(os.getenv('MQTT_BROKER_PORT', 1883))

        # EMQX 默认允许匿名登录。如果你没在 EMQX Dashboard 设置密码，留空即可。
        # 如果设置了 password_file 或 MySQL 认证，请在这里填入
        username = os.getenv('MQTT_USER', 'dji_bridge')  # 默认为空
        password = os.getenv('MQTT_PASSWORD', '123456')

        # 客户端 ID (Client ID)
        # ⚠️ 重要：连接 EMQX 时，Client ID 必须唯一。
        # 如果写死一个字符串，当重启脚本或并发运行时，旧连接会被踢掉。
        client_id = f"django_listener_{random.randint(1000, 9999)}"

        # 下载保存路径
        download_dir = os.path.join(settings.MEDIA_ROOT, 'dji_downloads')

        # ==========================================================

        self.stdout.write(self.style.WARNING(f"⚙️  正在初始化 MQTT 客户端..."))
        self.stdout.write(f"   - 目标 Broker: {broker_ip}:{broker_port}")
        self.stdout.write(f"   - Client ID: {client_id}")
        self.stdout.write(f"   - 保存路径: {download_dir}")

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # 初始化客户端
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

        # 保持连接活跃的心跳时间 (秒)
        client.keepalive = 60

        # 如果有账号密码则设置，没有则匿名登录
        if username:
            client.username_pw_set(username, password)
            self.stdout.write(f"   - 使用用户: {username} 进行认证")
        else:
            self.stdout.write(f"   - 使用匿名模式登录 (如果 EMQX 禁止匿名，请配置环境变量)")

        # 绑定上下文变量
        self.download_dir = download_dir

        # 绑定回调
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        self.stdout.write(self.style.SUCCESS(f"\n🚀 开始连接 EMQX..."))

        while True:
            try:
                client.connect(broker_ip, broker_port, 60)
                client.loop_forever()
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\n🛑 用户手动停止"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ 连接异常: {e}"))
                self.stdout.write(self.style.WARNING("🔄 3秒后重连..."))
                time.sleep(3)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """连接成功回调"""
        if rc == 0:
            self.stdout.write(self.style.SUCCESS('✅ 已连接到 EMQX! 正在监听所有 topic (#)...'))
            # 订阅所有主题，或者指定特定主题如 'sys/product/+/thing/event/+'
            client.subscribe("#")
        else:
            # 常见错误码: 1-协议错, 2-ID非法, 3-服务不可用, 4-账号密码错, 5-无授权
            self.stdout.write(self.style.ERROR(f'❌ 连接被拒绝, 返回码: {rc}'))

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        if rc != 0:
            self.stdout.write(self.style.ERROR('⚠️  意外断开连接 (可能是网络波动或被踢下线)'))

    def on_message(self, client, userdata, msg):
        """收到消息回调"""
        try:
            payload = msg.payload.decode('utf-8')
            # 调试：打印一下 Topic，方便你知道是从哪发来的
            # self.stdout.write(f"📩 [{msg.topic}] {payload[:50]}...")

            data = json.loads(payload)

            # --- 核心判断逻辑 ---
            # 模拟司空的逻辑：method 为 fileupload_callback 或者包含文件信息的 JSON
            is_upload_event = False

            # 情况1: 标准司空回调
            if data.get('method') == 'fileupload_callback':
                is_upload_event = True

            # 情况2: 只要包含 URL 和 file_id/object_key 就认为是文件
            elif 'url' in data and ('file_id' in data or 'object_key' in data):
                is_upload_event = True

            if is_upload_event:
                self.stdout.write(self.style.NOTICE(f"🎯 捕获到文件上传消息 [Topic: {msg.topic}]"))
                self.handle_file_upload(data)

        except json.JSONDecodeError:
            # self.stdout.write(f"收到非JSON消息: {msg.payload}")
            pass
        except Exception as e:
            print(f"❌ 消息处理错误: {e}")

    def handle_file_upload(self, data):
        """下载逻辑"""
        try:
            # 兼容嵌套结构 {'data': {...}} 或 直接扁平结构
            file_data = data.get('data', data)

            url = file_data.get('url')
            if not url:
                return

            # 获取文件名
            name = file_data.get('file_name')
            if not name:
                # 尝试从 key 里取
                key = file_data.get('object_key', '')
                if key:
                    name = os.path.basename(key)
                else:
                    name = f"emqx_file_{int(time.time())}.jpg"  # 默认存为jpg或mp4

            save_path = os.path.join(self.download_dir, name)

            if os.path.exists(save_path):
                self.stdout.write(f"   ⚠️ 文件已存在，跳过: {name}")
                return

            self.stdout.write(f"   ⬇️ 正在下载: {name} ...")

            # 执行下载
            res = requests.get(url, stream=True, verify=False, timeout=60)
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1024):
                        f.write(chunk)
                self.stdout.write(self.style.SUCCESS(f"   ✅ 下载完成: {save_path}"))
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ 下载失败 HTTP {res.status_code}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ 下载过程出错: {e}"))