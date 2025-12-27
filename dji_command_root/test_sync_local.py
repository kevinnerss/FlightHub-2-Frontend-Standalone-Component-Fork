import os
import django
import json
import zipfile
import io
from unittest.mock import MagicMock, patch

# 1. 初始化 Django 环境 (必须在最前面)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')  # ⚠️ 请把 'dj_backend' 换成你实际的项目文件夹名
django.setup()

from telemetry_app.models import Wayline, AlarmCategory, WaylineFingerprint
from telemetry_app.views import WaylineFingerprintManager
# ==============================================================================
# 1. 准备“真实”数据 (Mock Data)
# ==============================================================================

# 模拟 API 返回的航线列表 (参考你的截图数据)
MOCK_WAYLINE_LIST_DATA = {
    "code": 0,
    "data": {
        "list": [
            {
                "id": "f5f5e1fe-7b23-459a-9ced-73a743992529",
                "name": "工业大学至宁官站左侧桥梁",  # 这个名字包含 "桥梁"，应该被匹配到
                "update_time": 1766127033
            },
            {
                "id": "ignore-me-123",
                "name": "无关航线-不应被同步",
                "update_time": 1766127033
            }
        ]
    }
}

# 模拟 API 返回的单条详情 (包含 download_url)
MOCK_WAYLINE_DETAIL_DATA = {
    "code": 0,
    "data": {
        "id": "f5f5e1fe-7b23-459a-9ced-73a743992529",
        "name": "工业大学至宁官站左侧桥梁",
        "download_url": "http://mock-dji-api.com/download/test.kmz"
    }
}


# 模拟 KMZ 文件内容 (构造一个真实的 Zip 包，里面放 template.kml)
def create_mock_kmz_bytes():
    # KML 内容，包含你截图里的那个 UUID
    kml_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document>
        <wpml:missionConfig>
            <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
        </wpml:missionConfig>
        <Folder>
          <wpml:actionGroup>
            <wpml:actionGroupId>0</wpml:actionGroupId>
            <wpml:actionGroupStartIndex>0</wpml:actionGroupStartIndex>
            <wpml:actionGroupEndIndex>0</wpml:actionGroupEndIndex>
            <wpml:actionGroupMode>sequence</wpml:actionGroupMode>
            <wpml:actionTrigger>
              <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
            </wpml:actionTrigger>

            <wpml:actionUUID>270f6508-4ec0-442d-8583-686fc09987f2</wpml:actionUUID>

            <wpml:actionActuatorFuncParam>...</wpml:actionActuatorFuncParam>
          </wpml:actionGroup>
        </Folder>
      </Document>
    </kml>
    """

    # 在内存中创建一个 Zip 文件
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 必须叫 template.kml，因为你的代码里是按这个名字找的
        zf.writestr("template.kml", kml_content)

    buffer.seek(0)
    return buffer.read()


# ==============================================================================
# 2. 编写 Mock 逻辑 (拦截网络请求)
# ==============================================================================

def mock_requests_get(url, *args, **kwargs):
    """拦截 requests.get，根据 URL 返回我们伪造的数据"""
    print(f"🔍 [Mock Request] 正在请求: {url}")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    # 1. 拦截列表请求
    if "openapi/v0.1/wayline" in url and "wayline/" not in url:
        mock_resp.json.return_value = MOCK_WAYLINE_LIST_DATA
        return mock_resp

    # 2. 拦截详情请求 (注意 URL 结尾是 UUID)
    if "f5f5e1fe-7b23-459a-9ced-73a743992529" in url:
        mock_resp.json.return_value = MOCK_WAYLINE_DETAIL_DATA
        return mock_resp

    # 3. 拦截 KMZ 下载请求
    if "test.kmz" in url:
        mock_resp.content = create_mock_kmz_bytes()
        return mock_resp

    # 其他请求返回空
    mock_resp.status_code = 404
    return mock_resp


# ==============================================================================
# 3. 执行测试主流程
# ==============================================================================

def run_test():
    print("🚀 开始本地同步测试...\n")

    # --- 步骤 A: 准备数据库环境 ---
    print("1️⃣  正在准备基础数据 (AlarmCategory)...")
    # 清理旧数据，防止干扰
    Wayline.objects.all().delete()
    WaylineFingerprint.objects.all().delete()

    # 创建一个匹配规则：名字里带 "桥梁" 的，归类为 "桥梁检测"
    bridge_cat, _ = AlarmCategory.objects.get_or_create(
        code="bridge",
        defaults={
            "name": "桥梁检测",
            "match_keyword": "桥梁"  # 🔥 关键：只要航线名带这个词，就会被同步
        }
    )
    print(f"   已创建分类: {bridge_cat.name} (关键字: {bridge_cat.match_keyword})")

    # --- 步骤 B: 运行同步逻辑 (Mock 网络请求) ---
    print("\n2️⃣  正在执行 sync_by_keywords (Mock模式)...")

    # 使用 patch 装饰器，把 requests.get 替换成我们的 mock_requests_get
    with patch('requests.get', side_effect=mock_requests_get):
        # 🔥 调用你的核心业务逻辑
        WaylineFingerprintManager.sync_by_keywords()

    # --- 步骤 C: 验证结果 ---
    print("\n3️⃣  正在验证结果...")

    # 验证 1: Wayline 表是否创建了？
    wayline = Wayline.objects.filter(wayline_id="f5f5e1fe-7b23-459a-9ced-73a743992529").first()
    if wayline:
        print(f"   ✅ [Wayline] 航线创建成功: {wayline.name}")
    else:
        print("   ❌ [Wayline] 航线未创建！")
        return

    # 验证 2: WaylineFingerprint 表是否创建了？
    fingerprint = WaylineFingerprint.objects.filter(wayline=wayline).first()
    if fingerprint:
        print(f"   ✅ [Fingerprint] 指纹记录创建成功!")
        print(f"      - 关联分类: {fingerprint.detect_category.name}")
        print(f"      - UUID 数量: {len(fingerprint.action_uuids)}")
        print(f"      - UUID 列表: {fingerprint.action_uuids}")

        # 验证 3: UUID 是否对得上？
        target_uuid = "270f6508-4ec0-442d-8583-686fc09987f2"
        if target_uuid in fingerprint.action_uuids:
            print(f"   🎉 [Success] 成功提取到目标 UUID: {target_uuid}")
        else:
            print(f"   ❌ [Fail] 未找到目标 UUID，解析逻辑可能有误。")
    else:
        print("   ❌ [Fingerprint] 指纹记录未创建！")


if __name__ == "__main__":
    run_test()