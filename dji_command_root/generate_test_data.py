import os
import django
import sys
# Python 内置模块和非Django依赖
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import random

# ====================================================================
# 1. Django 环境初始化 (必须在所有模型导入和使用之前完成)
# ====================================================================

# 1.1 设置 DJANGO_SETTINGS_MODULE 环境变量
# 这是告诉 Python 解释器去哪里找 settings.py 的关键步骤
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_center.settings')

# 1.2 执行 setup() 加载应用注册表和所有配置
django.setup()

# ====================================================================
# 2. 模型导入 (现在是安全的)
# ====================================================================

# 必须在 django.setup() 之后才能安全导入模型
from telemetry_app.models import Alarm, AlarmType


def generate_alarms():
    # --- 1. 确保 AlarmType 存在并获取 ---

    # 清空旧数据 (可选，测试时建议保留)
    # Alarm.objects.all().delete()
    # AlarmType.objects.all().delete()

    try:
        INSPECT_TYPE = AlarmType.objects.get(code='INSPECTION_FAIL')
        FAULT_TYPE = AlarmType.objects.get(code='DEVICE_FAULT')
    except AlarmType.DoesNotExist:
        # 如果类型不存在，手动创建它
        print("警告：告警类型不存在，正在为您创建...")
        AlarmType.objects.create(name='设备故障', code='DEVICE_FAULT', description='无人机/机场连接中断')
        AlarmType.objects.create(name='巡检异常', code='INSPECTION_FAIL', description='AI 算法识别到目标缺陷')
        INSPECT_TYPE = AlarmType.objects.get(code='INSPECTION_FAIL')
        FAULT_TYPE = AlarmType.objects.get(code='DEVICE_FAULT')
        print("告警类型创建完成。")


    # --- 2. 设置常量 ---
    STATUS_CHOICES = ['PENDING', 'PROCESSING', 'COMPLETED', 'IGNORED']
    HANDLER_CHOICES = ['AutoPilot', 'Operator A', 'Support Team', 'System']
    BASE_LAT = 22.55
    BASE_LON = 113.95
    IMAGE_BASE_URL = "http://10.94.98.17/img/alarm_pic_"

    # --- 3. 生成数据 ---
    new_alarms = []

    for i in range(1, 21):  # 生成 20 条数据，增加测试样本
        # 随机生成经纬度，让点分散在地图上
        lat = Decimal(BASE_LAT + random.uniform(-0.1, 0.1))
        lon = Decimal(BASE_LON + random.uniform(-0.1, 0.1))

        # 随机选择状态和类型
        status = random.choice(STATUS_CHOICES)
        handler = random.choice(HANDLER_CHOICES) if status != 'PENDING' else 'System'
        alarm_type = INSPECT_TYPE if i % 3 != 0 else FAULT_TYPE

        # 随机生成过去两周的时间
        past_date = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 14), hours=random.randint(0, 24))

        content_list = [
            "AI 识别到电塔绝缘子表面存在污损。",
            "无人机 GPS 信号丢失，飞行姿态异常。",
            "高风险：桥梁结构件发现严重锈蚀。",
            "机载摄像头模组过热，需强制降温。",
            "巡检发现区域内有未登记的施工活动。",
            "风速超限，已自动切换为定点悬停模式。",
        ]

        new_alarm = Alarm(
            type=alarm_type,
            latitude=lat,
            longitude=lon,
            content=random.choice(content_list),
            image_url=f"{IMAGE_BASE_URL}{i}.jpg" if i % 2 == 0 else "",
            status=status,
            handler=handler
        )
        new_alarm.created_at = past_date
        new_alarms.append(new_alarm)

    # 批量写入数据库 (效率更高)
    Alarm.objects.bulk_create(new_alarms)
    print(f"\n成功生成并写入 {Alarm.objects.count()} 条新的告警记录到数据库。")


if __name__ == '__main__':
    generate_alarms()