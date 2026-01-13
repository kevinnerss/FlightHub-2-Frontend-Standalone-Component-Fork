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
            # 🔥 修正：司空实际发送的 Topic 前缀是 thing/product
            topics = [
                ("thing/product/+/osd", 0),  # 实时位置信息（机场OSD）
                ("thing/product/+/events", 1),  # 告警与事件
                ("thing/product/+/services_reply", 1),  # 服务响应（含文件上传回调）
                ("thing/product/+/requests", 0),  # 下行指令（可选，用于调试）
                # 兼容旧格式（以防万一）
                ("sys/product/+/device/+/osd", 0),
                ("sys/product/+/device/+/events", 1),
                ("sys/product/+/device/+/services_reply", 1),
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

            # 🔥 调试：打印收到的所有消息（前100条）
            if not hasattr(self, 'message_count'):
                self.message_count = 0

            if self.message_count < 100 or self.debug_mode:
                self.message_count += 1
                print(f"\n📨 [消息 #{self.message_count}] Topic: {msg.topic}")
                print(f"   Payload (前500字符): {str(data)[:500]}...")

            # 1. 处理位置信息 (高频数据，同步快速处理)
            if self.is_position_data(msg.topic, data):
                print(f"   ✅ 识别为位置数据 ->")
                self.handle_position_data(data, msg.topic)
                return

            # 2. 判断是否为文件上传事件
            if self.is_upload_event(data):
                print(f"   ✅ 识别为上传事件 ->")
                # self.stdout.write(f"📨 收到潜在文件消息: {msg.topic}")

                # ⚠️ 关键修改：开启新线程进行下载，坚决不阻塞 MQTT 主循环
                # daemon=True 表示主程序退出时子线程自动结束
                t = threading.Thread(target=self._process_download_thread, args=(data, msg.topic), daemon=True)
                t.start()
            else:
                if self.message_count < 10 or self.debug_mode:
                    print(f"   ⚠️ 未识别的消息类型")

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"   原始数据: {msg.payload[:200]}")
        except Exception as e:
            if self.debug_mode:
                self.stdout.write(self.style.ERROR(f"处理消息异常: {e}"))
            else:
                print(f"❌ 消息处理异常: {e}")

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
        同时处理机场状态和无人机位置
        """
        # 避免未导入模型报错
        try:
            from telemetry_app.models import DronePosition, DockStatus
        except ImportError:
            # 如果没有这个 app，直接返回，避免报错
            print("❌ 模型导入失败：telemetry_app.models.DronePosition or DockStatus")
            return

        try:
            payload = data.get('data', data)
            if not isinstance(payload, dict):
                print(f"   ⚠️ payload不是dict: {type(payload)}")
                return

            print(f"   📦 解析payload:")
            print(f"      - payload keys: {list(payload.keys())}")

            lat = payload.get('latitude') or payload.get('lat')
            lon = payload.get('longitude') or payload.get('lon')
            alt = payload.get('height') or payload.get('altitude')

            print(f"      - 纬度: {lat}, 经度: {lon}, 高度: {alt}")

            # --- 增强的过滤逻辑 (User Request) ---
            # 1. 获取 SN 和 Gateway
            sn = data.get('sn')
            gateway_raw = data.get('gateway')

            print(f"   🔍 过滤检查:")
            print(f"      - SN: {sn}")
            print(f"      - Gateway: {gateway_raw}")

            # 2. 从 Topic 中提取设备 SN
            # Topic 格式: thing/product/设备SN/osd
            topic_sn = None
            if '/osd' in topic or '/events' in topic:
                parts = topic.split('/')
                if len(parts) >= 3:
                    topic_sn = parts[2]

            print(f"      - Topic中的设备SN: {topic_sn}")

            # 3. 过滤规则：
            #    规则A: 如果消息中没有 sn 字段,尝试从 Topic 提取
            #    规则B: 如果都没有，才是真正的无效消息 -> 忽略
            if not sn:
                if topic_sn:
                    sn = topic_sn
                    print(f"   ℹ️ 消息中无SN字段,使用Topic中的SN: {sn}")
                else:
                    print(f"   🚫 [规则A] 忽略无SN消息")
                    return

            # 4. 确认通过过滤，使用 SN
            device_sn = sn

            # 🔥 判断是机场还是无人机 (SN以8开头的是机场)
            if device_sn.startswith('8'):
                print(f"   🏭 识别为机场设备: {device_sn}")
                self.update_dock_status(device_sn, payload, topic, gateway_raw)
            else:
                print(f"   🚁 识别为无人机设备: {device_sn}")
                # 保存无人机位置
                if lat and lon:
                    DronePosition.objects.create(
                        device_sn=device_sn,
                        latitude=lat,
                        longitude=lon,
                        altitude=alt if alt else 0,
                        raw_data=data,
                        timestamp=timezone.now(),
                        mqtt_topic=topic
                    )
                    print(f"   ✅ 无人机位置写入成功！{device_sn} -> ({lat}, {lon}, {alt}m)")

        except Exception as e:
            # 数据库错误不应中断 MQTT 循环
            import traceback
            print(f"❌ 数据库错误: {e}")
            print(f"   详细错误:")
            traceback.print_exc()

    def update_dock_status(self, dock_sn, payload, topic, gateway):
        """
        更新机场状态到数据库
        """
        try:
            from telemetry_app.models import DockStatus
            from django.utils import timezone

            # 获取或创建机场状态记录
            dock, created = DockStatus.objects.get_or_create(
                dock_sn=dock_sn,
                defaults={'dock_name': f'机场-{dock_sn[-4:]}'}
            )

            # 更新位置信息
            if 'latitude' in payload:
                dock.latitude = payload['latitude']
            if 'longitude' in payload:
                dock.longitude = payload['longitude']
            if 'height' in payload:
                dock.height = payload['height']

            # 更新环境信息
            if 'environment_temperature' in payload:
                dock.environment_temperature = payload['environment_temperature']
            if 'temperature' in payload:
                dock.temperature = payload['temperature']
            if 'humidity' in payload:
                dock.humidity = payload['humidity']
            if 'wind_speed' in payload:
                dock.wind_speed = payload['wind_speed']
            if 'rainfall' in payload:
                dock.rainfall = payload['rainfall']

            # 更新硬件状态
            if 'mode_code' in payload:
                dock.mode_code = payload['mode_code']
            if 'cover_state' in payload:
                dock.cover_state = payload['cover_state']
            if 'putter_state' in payload:
                dock.putter_state = payload['putter_state']
            if 'supplement_light_state' in payload:
                dock.supplement_light_state = payload['supplement_light_state']
            if 'emergency_stop_state' in payload:
                dock.emergency_stop_state = payload['emergency_stop_state']

            # 更新电源信息
            if 'electric_supply_voltage' in payload:
                dock.electric_supply_voltage = payload['electric_supply_voltage']
            if 'working_voltage' in payload:
                dock.working_voltage = payload['working_voltage']
            if 'working_current' in payload:
                dock.working_current = payload['working_current']

            # 更新备用电池信息
            if 'backup_battery' in payload:
                battery = payload['backup_battery']
                if 'voltage' in battery:
                    dock.backup_battery_voltage = battery['voltage']
                if 'temperature' in battery:
                    dock.backup_battery_temperature = battery['temperature']
                if 'switch' in battery:
                    dock.backup_battery_switch = battery['switch']

            # 更新无人机状态
            if 'drone_in_dock' in payload:
                dock.drone_in_dock = payload['drone_in_dock']
            if 'drone_charge_state' in payload:
                charge = payload['drone_charge_state']
                if isinstance(charge, dict):
                    dock.drone_charge_state = charge.get('state', 0)
                    dock.drone_battery_percent = charge.get('capacity_percent', 0)
                else:
                    dock.drone_charge_state = charge

            # 更新子设备信息
            if 'sub_device' in payload:
                sub_dev = payload['sub_device']
                if 'device_sn' in sub_dev:
                    dock.drone_sn = sub_dev['device_sn']

            # 更新网络状态
            if 'network_state' in payload:
                net = payload['network_state']
                if 'type' in net:
                    dock.network_state_type = net['type']
                if 'quality' in net:
                    dock.network_quality = net['quality']
                if 'rate' in net:
                    dock.network_rate = net['rate']

            # 更新存储信息
            if 'storage' in payload:
                storage = payload['storage']
                if 'total' in storage:
                    dock.storage_total = storage['total']
                if 'used' in storage:
                    dock.storage_used = storage['used']

            # 更新任务统计
            if 'job_number' in payload:
                dock.job_number = payload['job_number']
            if 'acc_time' in payload:
                dock.acc_time = payload['acc_time']
            if 'activation_time' in payload:
                dock.activation_time = payload['activation_time']

            # 更新告警状态
            if 'alarm_state' in payload:
                dock.alarm_state = payload['alarm_state']

            # 保存原始数据
            dock.raw_osd_data = payload
            dock.last_update_time = timezone.now()
            dock.is_online = True

            dock.save()

            action = "创建" if created else "更新"
            print(f"   ✅ 机场状态{action}成功！{dock_sn}")

        except Exception as e:
            import traceback
            print(f"❌ 更新机场状态失败: {e}")
            traceback.print_exc()