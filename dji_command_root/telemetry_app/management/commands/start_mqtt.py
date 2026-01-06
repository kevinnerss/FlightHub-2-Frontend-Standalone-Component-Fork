import json
import os
import time
import requests
import threading
from queue import Queue
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.conf import settings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ------------------------------
# 🔍 强健的文件事件解析器（关键）
# ------------------------------
def extract_file_info(data):
    """
    自动识别司空可能推送的所有文件格式变化
    返回: (file_name, url) 或 (None, None)
    """

    if not isinstance(data, dict):
        return None, None

    # --- 1. 标准结构 method=fileupload_callback ---
    if data.get("method") == "fileupload_callback":
        inner = data.get("data", {})
        return inner.get("file_name"), inner.get("url")

    # --- 2. file_id + url 格式 ---
    if "file_id" in data and "url" in data:
        name = data.get("file_name") or f"{data['file_id']}.bin"
        return name, data["url"]

    # --- 3. object_key 附带路径 ---
    if "object_key" in data:
        fname = os.path.basename(data["object_key"])
        return fname, data.get("url")

    # --- 4. 可能包裹在 data/payload/file 等字段 ---
    for key in ["data", "payload", "file"]:
        if isinstance(data.get(key), dict):
            name, url = extract_file_info(data[key])
            if name and url:
                return name, url

    # --- 5. 深层递归搜索 ---
    for v in data.values():
        if isinstance(v, dict):
            name, url = extract_file_info(v)
            if name and url:
                return name, url

    return None, None


# ======================================================================
# ⭐ 主类：MQTT 监听
# ======================================================================
class Command(BaseCommand):
    help = "MQTT Worker：监听司空并下载媒体文件（增强稳定版）"

    def __init__(self):
        super().__init__()
        self.download_queue = Queue()
        self.processed_message_ids = set()  # 防重复消息处理
        self.max_log_len = int(os.getenv("MQTT_LOG_PAYLOAD_MAXLEN", "4000"))

    # ======================================================
    # 启动 Worker线程
    # ======================================================
    def start_worker_thread(self):
        def worker():
            while True:
                try:
                    file_name, file_url = self.download_queue.get()
                    self.safe_download(file_name, file_url)
                except Exception as e:
                    print(f"❌ Worker线程异常: {e}")

        threading.Thread(target=worker, daemon=True).start()

    # ======================================================
    # 下载函数（带重试）
    # ======================================================
    def safe_download(self, file_name, file_url):
        save_path = os.path.join(self.download_dir, file_name)

        # 已存在则跳过
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            print(f"⚠️ 已存在文件，跳过下载: {file_name}")
            return

        print(f"⬇️ 准备下载: {file_name}")
        print(f"🔗 URL: {file_url}")

        for attempt in range(3):  # 至多3次
            try:
                with requests.get(file_url, stream=True, verify=False, timeout=15) as r:
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                print(f"✅ 下载成功: {save_path}")
                return
            except Exception as e:
                print(f"❌ 下载失败（第 {attempt+1} 次）: {e}")
                time.sleep(2)

        print(f"🚨 彻底失败，放弃下载: {file_name}")

        if os.path.exists(save_path):
            os.remove(save_path)

    # ======================================================
    # 回调：连接成功
    # ======================================================
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ MQTT 连接成功！订阅所有主题 #")
            client.subscribe("#", qos=1)  # ⭐ 强烈建议使用 QoS=1，避免丢消息
        else:
            print(f"❌ 连接失败 rc={rc}")

    # ======================================================
    # 回调：收到消息
    # ======================================================
    def on_message(self, client, userdata, msg):
        try:
            payload_bytes = msg.payload or b""
            print(f"📩 收到 MQTT 消息：topic={msg.topic}, bytes={len(payload_bytes)}")
        except Exception:
            print(f"📩 收到 MQTT 消息：topic={msg.topic}")
        try:
            payload = msg.payload.decode("utf-8", errors="ignore")

            data = json.loads(payload)

            # 去重：避免重复触发
            msg_id = data.get("id") or f"{msg.topic}-{time.time()}"
            if msg_id in self.processed_message_ids:
                return
            self.processed_message_ids.add(msg_id)

            # --- 智能日志过滤 (User Request) ---
            # 识别机场心跳包 (Dock Heartbeat)，避免刷屏
            sn = data.get("sn")
            gateway = data.get("gateway")
            gateway_sn = gateway.get("sn") if isinstance(gateway, dict) else gateway
            
            is_dock_heartbeat = False
            if (not sn and gateway_sn) or (sn and gateway_sn and sn == gateway_sn):
                is_dock_heartbeat = True

            if is_dock_heartbeat and "osd" in msg.topic:
                # 简化显示机场心跳
                print(f"💓 [Dock OSD] Gateway: {gateway_sn} (Status OK) - 隐藏详细 JSON")
            else:
                # 显示完整/截断的 JSON
                try:
                    preview = json.dumps(data, ensure_ascii=False, indent=2)
                    if len(preview) > self.max_log_len:
                        print(preview[:self.max_log_len] + "...(truncated)")
                    else:
                        print(preview)
                except Exception:
                    s = payload
                    if len(s) > self.max_log_len:
                        print(s[:self.max_log_len] + "...(truncated)")
                    else:
                        print(s)

            # 提取文件信息
            file_name, file_url = extract_file_info(data)

            if file_name and file_url:
                print("\n🔥🔥🔥🔥🔥 侦测到文件事件 🔥🔥🔥🔥🔥")
                print(json.dumps(data, indent=4, ensure_ascii=False))

                # 放入下载队列而不是直接下载（避免阻塞 MQTT）
                self.download_queue.put((file_name, file_url))
                return

        except Exception as e:
            print(f"❌ 解析消息失败: {e}")

    # ======================================================
    # 主循环
    # ======================================================
    def handle(self, *args, **options):

        # 读取配置
        broker_ip = os.getenv("DJI_BROKER_IP", "emqx")
        broker_port = int(os.getenv("DJI_BROKER_PORT", 1883))
        username = os.getenv("DJI_BROKER_USER", "")
        password = os.getenv("DJI_BROKER_PASSWORD", "")

        self.download_dir = os.path.join(settings.MEDIA_ROOT, "dji_downloads")
        os.makedirs(self.download_dir, exist_ok=True)

        print("⚙️ 配置：")
        print(f"  MQTT: {broker_ip}:{broker_port}")
        print(f"  保存目录: {self.download_dir}")

        # 启动后台下载线程
        self.start_worker_thread()

        # 创建客户端
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if username:
            client.username_pw_set(username, password)

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # 自动重连循环
        while True:
            try:
                print("🚀 正在连接 MQTT ...")
                client.connect(broker_ip, broker_port, keepalive=60)
                client.loop_forever()
            except Exception as e:
                print(f"❌ MQTT 连接异常: {e}")
                print("🔄 5秒后重试...")
                time.sleep(5)
