import json
import os
import time
import requests
import threading
from queue import Queue
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入 DockStatus 模型
from telemetry_app.models import DockStatus

# 🏭 机场名称全局映射字典
DOCK_NAME_MAPPING = {
    "8UUXN4900A052C": "工业大学机场",
    "8UUXN4R00A06Q6": "马贝机场",
}


def get_dock_display_name(dock_sn):
    """
    根据机场SN获取显示名称
    如果映射表中没有,返回 None (使用数据库中已有名称或SN)
    """
    return DOCK_NAME_MAPPING.get(dock_sn)


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
    # 保存机场状态到数据库
    # ======================================================
    def save_dock_status(self, data, gateway_sn):
        """
        解析机场 OSD 数据并保存到数据库
        🔧 修复: 只更新非空字段,避免用空值覆盖已有数据
        """
        try:
            # 提取机场数据
            dock_data = data.get("data", {})

            # 🏭 获取机场显示名称
            dock_display_name = get_dock_display_name(gateway_sn)

            # 📦 构建更新字典 - 只包含非空值
            defaults_dict = {
                'is_online': True,
                'last_update_time': timezone.now(),
            }

            # 🏭 如果映射表中有名称,则更新 dock_name
            if dock_display_name:
                defaults_dict['dock_name'] = dock_display_name

            # 🌡️ 环境数据 - 只在有值时更新
            if 'environment_temperature' in dock_data and dock_data['environment_temperature'] is not None:
                defaults_dict['environment_temperature'] = dock_data['environment_temperature']
            if 'temperature' in dock_data and dock_data['temperature'] is not None:
                defaults_dict['temperature'] = dock_data['temperature']
            if 'humidity' in dock_data and dock_data['humidity'] is not None:
                defaults_dict['humidity'] = dock_data['humidity']
            if 'wind_speed' in dock_data and dock_data['wind_speed'] is not None:
                defaults_dict['wind_speed'] = dock_data['wind_speed']
            if 'rainfall' in dock_data and dock_data['rainfall'] is not None:
                defaults_dict['rainfall'] = dock_data['rainfall']

            # ⚡ 电源数据
            if 'electric_supply_voltage' in dock_data and dock_data['electric_supply_voltage'] is not None:
                defaults_dict['electric_supply_voltage'] = dock_data['electric_supply_voltage']
            if 'working_voltage' in dock_data and dock_data['working_voltage'] is not None:
                defaults_dict['working_voltage'] = dock_data['working_voltage']
            if 'working_current' in dock_data and dock_data['working_current'] is not None:
                defaults_dict['working_current'] = dock_data['working_current']

            # 🔋 备用电池信息
            backup_battery = dock_data.get('backup_battery', {})
            if isinstance(backup_battery, dict):
                if 'voltage' in backup_battery and backup_battery['voltage'] is not None:
                    defaults_dict['backup_battery_voltage'] = backup_battery['voltage']
                if 'temperature' in backup_battery and backup_battery['temperature'] is not None:
                    defaults_dict['backup_battery_temperature'] = backup_battery['temperature']
                if 'switch' in backup_battery and backup_battery['switch'] is not None:
                    defaults_dict['backup_battery_switch'] = backup_battery['switch']

            # 🔧 硬件状态
            if 'cover_state' in dock_data and dock_data['cover_state'] is not None:
                defaults_dict['cover_state'] = dock_data['cover_state']
            if 'supplement_light_state' in dock_data and dock_data['supplement_light_state'] is not None:
                defaults_dict['supplement_light_state'] = dock_data['supplement_light_state']
            if 'emergency_stop_state' in dock_data and dock_data['emergency_stop_state'] is not None:
                defaults_dict['emergency_stop_state'] = dock_data['emergency_stop_state']
            if 'putter_state' in dock_data and dock_data['putter_state'] is not None:
                defaults_dict['putter_state'] = dock_data['putter_state']

            # 📊 模式和告警
            if 'mode_code' in dock_data and dock_data['mode_code'] is not None:
                defaults_dict['mode_code'] = dock_data['mode_code']
            if 'alarm_state' in dock_data and dock_data['alarm_state'] is not None:
                defaults_dict['alarm_state'] = dock_data['alarm_state']

            # 💾 存储信息
            storage_data = dock_data.get('storage', {})
            if isinstance(storage_data, dict):
                total_info = storage_data.get('total')
                used_info = storage_data.get('used')
                if total_info is not None:
                    defaults_dict['storage_total'] = total_info
                if used_info is not None:
                    defaults_dict['storage_used'] = used_info

            # 📈 任务统计
            if 'job_number' in dock_data and dock_data['job_number'] is not None:
                defaults_dict['job_number'] = dock_data['job_number']
            if 'acc_time' in dock_data and dock_data['acc_time'] is not None:
                defaults_dict['acc_time'] = dock_data['acc_time']
            if 'activation_time' in dock_data and dock_data['activation_time'] is not None:
                defaults_dict['activation_time'] = dock_data['activation_time']

            # 🚁 无人机信息
            sub_device = dock_data.get('sub_device', {})
            if isinstance(sub_device, dict) and 'device_sn' in sub_device and sub_device['device_sn']:
                defaults_dict['drone_sn'] = sub_device['device_sn']

            if 'drone_in_dock' in dock_data and dock_data['drone_in_dock'] is not None:
                defaults_dict['drone_in_dock'] = dock_data['drone_in_dock']

            drone_charge_state_data = dock_data.get('drone_charge_state', {})
            if isinstance(drone_charge_state_data, dict):
                if 'state' in drone_charge_state_data and drone_charge_state_data['state'] is not None:
                    defaults_dict['drone_charge_state'] = drone_charge_state_data['state']
                if 'capacity_percent' in drone_charge_state_data and drone_charge_state_data['capacity_percent'] is not None:
                    capacity = drone_charge_state_data['capacity_percent']
                    # 过滤掉无效值 32767
                    if capacity != 32767:
                        defaults_dict['drone_battery_percent'] = capacity

            # 📡 网络状态
            network_state = dock_data.get('network_state', {})
            if isinstance(network_state, dict):
                if 'type' in network_state and network_state['type'] is not None:
                    defaults_dict['network_state_type'] = network_state['type']
                if 'quality' in network_state and network_state['quality'] is not None:
                    defaults_dict['network_quality'] = network_state['quality']
                if 'rate' in network_state and network_state['rate'] is not None:
                    defaults_dict['network_rate'] = network_state['rate']

            # 💾 保存原始数据以便调试
            defaults_dict['raw_osd_data'] = dock_data

            # 🔄 更新或创建记录
            _, created = DockStatus.objects.update_or_create(
                dock_sn=gateway_sn,
                defaults=defaults_dict
            )

            action = "新建" if created else "更新"
            print(f"{'✅' if created else '🔄'} {action}机场记录: {gateway_sn}")

        except Exception as e:
            print(f"❌ 保存机场状态失败: {e}")
            import traceback
            traceback.print_exc()

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

                # ⭐ 保存机场状态到数据库
                self.save_dock_status(data, gateway_sn)
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
