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

# ================= 配置区域 (请根据现场修改) =================
# 1. MQTT Broker 配置 (连接 EMQX)
# 如果是 Docker 部署且在同一网络，可以用宿主机 IP 或 service name
# 本地测试填 "127.0.0.1"
BROKER_IP = "127.0.0.1"
BROKER_PORT = 1883
USERNAME = "dji_bridge"
PASSWORD = "123456"

# 2. 文件存储配置
# 下载的文件将保存在项目根目录下的 media/dji_downloads 文件夹
# 确保你的 settings.py 里配置了 MEDIA_ROOT
DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'media', 'dji_downloads')


# ==========================================================

class Command(BaseCommand):
    help = '启动 MQTT 监听服务，接收司空数据并自动下载媒体文件'

    def handle(self, *args, **options):
        # 确保下载目录存在
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            self.stdout.write(f"创建下载目录: {DOWNLOAD_DIR}")

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # 设置账号密码
        if USERNAME and PASSWORD:
            client.username_pw_set(USERNAME, PASSWORD)

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        self.stdout.write(self.style.SUCCESS(f"正在连接 MQTT 服务器: {BROKER_IP}..."))

        try:
            client.connect(BROKER_IP, BROKER_PORT, 60)
            # 阻塞运行，保持长连接
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\n用户停止了监听"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"连接出错: {e}"))

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """连接成功回调"""
        if rc == 0:
            self.stdout.write(self.style.SUCCESS('✅ Django 已成功连接到 EMQX! 正在监听数据...'))
            # 订阅所有主题
            client.subscribe("#")
        else:
            self.stdout.write(self.style.ERROR(f'连接失败, 错误码: {rc}'))

    def on_message(self, client, userdata, msg):
        """收到消息回调"""
        try:
            payload = msg.payload.decode('utf-8')
            # 尝试解析 JSON
            data = json.loads(payload)
            print(f"📩 [RAW] 收到原始数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            # --- 核心业务逻辑 ---

            # 1. 检测是否为【文件上传回调】
            # 不同版本司空 key 可能略有不同，通常包含 fileupload_callback
            # 或者直接判断有没有 'file_id' 和 'url'
            method = data.get('method', '')

            # 逻辑：如果是文件上传回调，或者数据里包含了文件 ID 和 URL，就触发下载
            if method == 'fileupload_callback' or ('file_id' in str(data) and 'url' in str(data)):
                self.handle_file_upload(data)

            # 2. (可选) 处理设备状态，例如存入数据库
            # if 'status' in data:
            #     pass

            # ------------------

        except json.JSONDecodeError:
            # 忽略非 JSON 数据
            pass
        except Exception as e:
            print(f"❌ 数据处理异常: {e}")

    def handle_file_upload(self, data):
        """处理文件上传通知并下载文件"""
        try:
            # 这里的结构取决于司空实际发过来的 JSON，通常在 data 字段里
            file_data = data.get('data', {})

            # 获取文件名，如果没有就生成一个
            file_name = file_data.get('file_name')
            if not file_name:
                file_name = f"unknown_{int(time.time())}.mp4"

            file_url = file_data.get('url')

            if not file_url:
                print(f"⚠️ 收到文件通知但没有 URL: {file_name}")
                return

            print(f"⬇️ 发现新文件: {file_name}")
            print(f"🔗 下载链接: {file_url}")

            local_path = os.path.join(DOWNLOAD_DIR, file_name)

            # 开始下载
            self.download_file(file_url, local_path)

        except Exception as e:
            print(f"处理文件下载逻辑出错: {e}")

    def download_file(self, url, save_path):
        """流式下载文件"""
        try:
            # verify=False 忽略 SSL 证书错误（内网环境常见）
            # stream=True 必须开启，防止大视频撑爆内存
            with requests.get(url, stream=True, verify=False, timeout=120) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            print(f"✅ 文件下载成功: {save_path}")

            # TODO: 在这里可以触发你的 AI 识别函数
            # from my_ai_module import detect_anomaly
            # detect_anomaly(save_path)

        except Exception as e:
            print(f"❌ 下载失败: {e}")