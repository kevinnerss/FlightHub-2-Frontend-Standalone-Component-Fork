"""
测试ZLM API连接和截图功能
用于诊断保护区检测无法截图的问题
"""

from django.core.management.base import BaseCommand
import requests
import json


class Command(BaseCommand):
    help = '测试ZLM API连接和截图功能'

    def handle(self, *args, **options):
        # 配置
        ZLM_API_HOST = "http://zlm:80"
        ZLM_SECRET = "123456"
        stream_id = "dock02"  # 你要测试的流ID

        self.stdout.write("=" * 60)
        self.stdout.write(f"🧪 ZLM API 测试工具")
        self.stdout.write(f"📡 ZLM地址: {ZLM_API_HOST}")
        self.stdout.write(f"🔑 密钥: {ZLM_SECRET}")
        self.stdout.write(f"📹 测试流: {stream_id}")
        self.stdout.write("=" * 60)

        # 测试1：检查ZLM是否可访问
        self.stdout.write("\n【测试1】检查ZLM服务器是否可访问...")
        try:
            resp = requests.get(f"{ZLM_API_HOST}/index/api/getServerStatus", timeout=5)
            self.stdout.write(f"✅ HTTP状态码: {resp.status_code}")
            self.stdout.write(f"📄 响应内容: {resp.text[:200]}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 无法连接到ZLM: {e}"))
            return

        # 测试2：获取在线流列表
        self.stdout.write("\n【测试2】获取在线流列表...")
        try:
            params = {"secret": ZLM_SECRET}
            resp = requests.get(f"{ZLM_API_HOST}/index/api/getMediaList", params=params, timeout=5)
            self.stdout.write(f"✅ HTTP状态码: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                self.stdout.write(f"📊 返回码: {data.get('code')}")
                self.stdout.write(f"📊 在线流数量: {len(data.get('data', []))}")

                if data.get('data'):
                    self.stdout.write("\n📹 在线流列表:")
                    for stream in data.get('data', []):
                        self.stdout.write(f"  - {stream.get('app')}/{stream.get('stream')}")
                else:
                    self.stdout.write(self.style.WARNING("⚠️ 当前没有在线流"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ HTTP错误: {resp.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 请求失败: {e}"))

        # 测试3：尝试截图
        self.stdout.write(f"\n【测试3】尝试对流 {stream_id} 截图...")
        try:
            snap_api = f"{ZLM_API_HOST}/index/api/getSnap"
            params = {
                "secret": ZLM_SECRET,
                "url": f"rtmp://127.0.0.1:1935/live/{stream_id}",
                "timeout_sec": 5,
                "expire_sec": 1
            }

            self.stdout.write(f"📡 请求URL: {snap_api}")
            self.stdout.write(f"📡 请求参数: {json.dumps(params, indent=2)}")

            resp = requests.get(snap_api, params=params, timeout=10)
            self.stdout.write(f"✅ HTTP状态码: {resp.status_code}")
            self.stdout.write(f"📄 响应头: {dict(resp.headers)}")
            self.stdout.write(f"📄 响应内容前500字符: {resp.text[:500]}")

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    self.stdout.write(f"📊 JSON返回码: {data.get('code')}")
                    self.stdout.write(f"📊 JSON消息: {data.get('msg')}")

                    if data.get('code') == 0:
                        self.stdout.write(self.style.SUCCESS(f"✅ 截图成功！"))
                        self.stdout.write(f"📸 截图URL: {data.get('data', '')}")
                    else:
                        self.stdout.write(self.style.ERROR(f"❌ ZLM返回错误码: {data.get('code')}"))
                        self.stdout.write(f"📄 错误消息: {data.get('msg')}")
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f"❌ 响应不是有效JSON: {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ HTTP错误: {resp.status_code}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 截图请求失败: {e}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🔍 如果看到错误，请检查：")
        self.stdout.write("1. ZLM容器是否正常运行：docker ps | grep zlm")
        self.stdout.write("2. 流是否正在推送：检查无人机是否在推流")
        self.stdout.write("3. 流ID是否正确：确认RTMP地址中的流ID")
        self.stdout.write("=" * 60)
