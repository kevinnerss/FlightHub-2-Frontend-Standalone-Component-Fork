import json
import os
import time
import requests
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.conf import settings
import urllib3

# 禁用 HTTPS 不安全警告 (因为司空私有化可能用自签名证书，内网下载必须忽略 SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    help = '启动 MQTT 监听服务，接收司空数据并自动下载媒体文件'

    def handle(self, *args, **options):
        # ================= 动态配置区域 =================
        # 优先读取环境变量 (Docker Compose 里设置的)，如果没读取到，则使用默认值 (本地测试用)

        # 1. Broker IP: 现场部署时会自动读取 docker-compose.yml 里的 DJI_BROKER_IP
        broker_ip = os.getenv('DJI_BROKER_IP', '127.0.0.1')

        # 2. Broker Port: 默认 1883
        broker_port = int(os.getenv('DJI_BROKER_PORT', 1883))

        # 3. 账号密码: 现场如果变了，可以在 yaml 里改，不用改代码
        username = os.getenv('DJI_BROKER_USER', 'dji_bridge')
        password = os.getenv('DJI_BROKER_PASSWORD', '123456')

        # 4. 下载目录: 确保保存到 Docker 挂载的 media 卷中
        # 默认保存到: /app/media/dji_downloads (Docker内) 或 项目根目录/media/dji_downloads (本地)
        download_dir = os.path.join(settings.MEDIA_ROOT, 'dji_downloads')

        # ==========================================================

        self.stdout.write(self.style.WARNING(f"⚙️  配置加载完毕:"))
        self.stdout.write(f"   - MQTT 服务器: {broker_ip}:{broker_port}")
        self.stdout.write(f"   - 用户名: {username}")
        self.stdout.write(f"   - 保存路径: {download_dir}")

        # 确保下载目录存在
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            self.stdout.write(f"   - 已自动创建下载目录")

        # 初始化 MQTT 客户端
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # 设置账号密码
        if username and password:
            client.username_pw_set(username, password)

        # 绑定回调函数
        # 注意：这里使用 lambda 或者 functools.partial 将 download_dir 传进去，
        # 或者直接存为 self.download_dir 供类方法使用
        self.download_dir = download_dir
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        self.stdout.write(self.style.SUCCESS(f"\n🚀 正在连接 MQTT 服务器..."))

        while True:
            try:
                client.connect(broker_ip, broker_port, 60)
                client.loop_forever()  # 阻塞运行
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\n🛑 用户停止了监听"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ 连接出错: {e}"))
                self.stdout.write(self.style.WARNING("🔄 5秒后尝试重连..."))
                time.sleep(5)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """连接成功回调"""
        if rc == 0:
            self.stdout.write(self.style.SUCCESS('✅ 成功连接到司空 MQTT! 正在监听所有消息 (#)...'))
            client.subscribe("#")
        else:
            self.stdout.write(self.style.ERROR(f'❌ 连接失败, 错误码: {rc}'))

    def on_message(self, client, userdata, msg):
        """收到消息回调"""
        try:
            payload = msg.payload.decode('utf-8')
            # 尝试解析 JSON
            data = json.loads(payload)

            # --- 调试日志 (生产环境可适当减少) ---
            # print(f"📩 [Topic: {msg.topic}] 收到数据...")

            # --- 核心业务逻辑 ---
            # 1. 检测是否为【文件上传回调】
            method = data.get('method', '')

            # 逻辑：判断是否包含文件上传的关键字段
            # 司空2通常会有 method: 'fileupload_callback'，或者直接带 file_id 和 url
            if method == 'fileupload_callback' or ('file_id' in str(data) and 'url' in str(data)):
                self.stdout.write(self.style.NOTICE(f"🔍 检测到文件上传事件!"))
                self.handle_file_upload(data)

        except json.JSONDecodeError:
            pass  # 忽略非 JSON 数据
        except Exception as e:
            print(f"❌ 数据处理异常: {e}")

    def handle_file_upload(self, data):
        """处理文件上传通知并下载文件"""
        try:
            # 这里的结构取决于司空实际发过来的 JSON，通常在 data 字段里
            # 如果 data 是由 {'data': {...}} 这种格式包裹
            file_data = data.get('data', data)  # 兼容两种格式

            # 获取文件名，如果没有就生成一个
            file_name = file_data.get('file_name')

            # 如果没有文件名，或者是路径形式，只取最后一部分
            if not file_name:
                object_key = file_data.get('object_key', '')
                if object_key:
                    file_name = os.path.basename(object_key)
                else:
                    file_name = f"unknown_{int(time.time())}.mp4"

            file_url = file_data.get('url')

            if not file_url:
                # 有些包可能只是进度通知，没有URL，直接忽略
                return

            local_path = os.path.join(self.download_dir, file_name)

            # 防止重复下载
            if os.path.exists(local_path):
                self.stdout.write(f"⚠️ 文件已存在，跳过: {file_name}")
                return

            self.stdout.write(f"⬇️ 开始下载: {file_name}")
            # self.stdout.write(f"🔗 链接: {file_url}") # 链接太长，调试时再打开

            # 开始下载
            self.download_file(file_url, local_path)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 处理文件逻辑出错: {e}"))

    def download_file(self, url, save_path):
        """流式下载文件"""
        try:
            # verify=False 忽略 SSL 证书错误
            # stream=True 防止内存溢出
            with requests.get(url, stream=True, verify=False, timeout=120) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            self.stdout.write(self.style.SUCCESS(f"✅ 文件下载成功: {save_path}"))

            # TODO: 可以在这里调用数据库保存逻辑
            # from telemetry_app.models import WaylineImage
            # WaylineImage.objects.create(path=save_path, ...)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 下载失败: {e}"))
            # 如果下载失败（例如文件只有0字节），删除它，以免影响后续重试
            if os.path.exists(save_path):
                os.remove(save_path)