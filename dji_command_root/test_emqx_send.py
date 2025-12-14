import paho.mqtt.client as mqtt
import json
import time
import random
import socket
import sys

# ================= 配置 =================
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "sys/product/device/thing/event/fileupload_callback"

# ✅ 使用 Python 官网的 Logo
TEST_FILE_URL = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"


def check_port(ip, port):
    """【诊断步骤】检查 TCP 端口是否开放"""
    print(f"🔍 正在诊断网络: 尝试连接 {ip}:{port} ...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            print(f"✅ 网络通畅: {ip}:{port} 是开放的")
            s.close()
            return True
        else:
            print(f"❌ 网络不通: 无法连接到 {ip}:{port}")
            s.close()
            return False
    except Exception:
        return False


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ MQTT 连接成功!")
    else:
        print(f"❌ 连接失败，代码: {rc}")


def publish_test_data():
    if not check_port(BROKER, PORT):
        return

    # 生成一个显眼的 Client ID，方便你去后台搜
    my_client_id = f"Test_User_{random.randint(1000, 9999)}"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=my_client_id)
    client.on_connect = on_connect

    try:
        print(f"🔌 正在连接 (Client ID: {my_client_id})...")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        time.sleep(1)

        file_name = f"python_logo_ok_{int(time.time())}.png"

        payload = {
            "method": "fileupload_callback",
            "timestamp": int(time.time() * 1000),
            "data": {
                "file_id": "debug_file_003",
                "file_name": file_name,
                "object_key": "photos/debug/logo.png",
                "url": TEST_FILE_URL,
                "size": 50000
            }
        }

        json_payload = json.dumps(payload)

        print(f"📤 发送指令: 下载 {file_name}")
        info = client.publish(TOPIC, json_payload, qos=1)
        info.wait_for_publish()

        print("🎉 发送成功！请检查 Django 窗口。")

        # ==========================================
        # 🟢 调试模式：死循环保持在线，直到你按 Ctrl+C
        # ==========================================
        print("\n" + "=" * 50)
        print(f"⏳ 脚本正在保持在线 (ID: {my_client_id})")
        print(f"💓 每秒发送一次心跳，强制刷新 Dashboard...")
        print("👉 请不要看【概览】页！概览页有缓存！")
        print("👉 请点击左侧菜单的【客户端 (Clients)】，在列表里找这个 ID！")
        print("⌨️  查看完毕后，请按 [Ctrl + C] 停止脚本")
        print("=" * 50)

        try:
            while True:
                # 每秒发个空消息，刷存在感
                client.publish("sys/heartbeat", "ping")
                print(".", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 用户手动停止")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ 发生异常: {e}")


if __name__ == "__main__":
    publish_test_data()
