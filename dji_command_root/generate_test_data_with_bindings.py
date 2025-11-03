import os
import sys
import django
import random
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')
django.setup()

from telemetry_app.models import Wayline, Alarm, AlarmCategory

def create_alarm_categories():
    """创建告警类型"""
    categories = [
        {'name': '设备故障', 'code': 'EQUIP_FAIL'},
        {'name': '环境异常', 'code': 'ENV_ABNORMAL'},
        {'name': '安全警告', 'code': 'SECURITY_WARN'},
        {'name': '电量低', 'code': 'LOW_BATTERY'},
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = AlarmCategory.objects.get_or_create(
            code=cat_data['code'],
            defaults={'name': cat_data['name']}
        )
        created_categories.append(category)
    
    return created_categories

def create_waylines(count=5):
    """创建测试航线"""
    waylines = []
    
    for i in range(1, count + 1):
        wayline, created = Wayline.objects.get_or_create(
            wayline_id=f'WL{i:03d}',
            defaults={
                'name': f'测试航线{i}',
                'description': f'这是测试航线{i}的描述信息',
                'status': random.choice(['DRAFT', 'ACTIVE', 'ARCHIVED']),
                'length': round(random.uniform(1000, 10000), 2),
                'estimated_duration': random.randint(300, 1800),
                'created_by': f'user{i}',
                'waypoints': [
                    {'lat': 39.9 + random.uniform(-0.1, 0.1), 'lng': 116.3 + random.uniform(-0.1, 0.1), 'alt': 50},
                    {'lat': 39.9 + random.uniform(-0.1, 0.1), 'lng': 116.4 + random.uniform(-0.1, 0.1), 'alt': 60},
                ]
            }
        )
        waylines.append(wayline)
    
    return waylines

def create_alarms(waylines, categories, count_per_wayline=3):
    """为每个航线创建告警信息"""
    alarm_contents = [
        '设备温度过高',
        '信号强度不稳定',
        '电池电量低于30%',
        '检测到异常震动',
        'GPS信号弱',
        '风速超过安全阈值',
        '航向偏差过大',
        '高度异常波动',
        '避障系统警告',
        '遥测数据丢失'
    ]
    
    alarms_created = 0
    
    # 为每个航线创建告警
    for wayline in waylines:
        for _ in range(count_per_wayline):
            # 随机选择告警类型
            category = random.choice(categories)
            
            # 创建告警并关联到航线
            Alarm.objects.create(
                wayline=wayline,  # 这里使用外键关联
                category=category,
                latitude=round(random.uniform(39.8, 40.0), 6),
                longitude=round(random.uniform(116.2, 116.5), 6),
                content=random.choice(alarm_contents),
                status=random.choice(['PENDING', 'PROCESSING', 'COMPLETED', 'IGNORED']),
                specific_data={
                    'severity': random.choice(['low', 'medium', 'high']),
                    'detected_at': (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat()
                }
            )
            alarms_created += 1
    
    # 创建一些未关联航线的告警
    for _ in range(5):
        category = random.choice(categories)
        Alarm.objects.create(
            wayline=None,  # 不关联任何航线
            category=category,
            latitude=round(random.uniform(39.8, 40.0), 6),
            longitude=round(random.uniform(116.2, 116.5), 6),
            content=random.choice(alarm_contents),
            status=random.choice(['PENDING', 'PROCESSING', 'COMPLETED', 'IGNORED'])
        )
        alarms_created += 1
    
    return alarms_created

def main():
    print("开始生成测试数据...")
    
    # 创建告警类型
    print("1. 创建告警类型...")
    categories = create_alarm_categories()
    print(f"   成功创建 {len(categories)} 个告警类型")
    
    # 创建航线
    print("2. 创建测试航线...")
    waylines = create_waylines(5)
    print(f"   成功创建 {len(waylines)} 条航线")
    
    # 创建告警并关联到航线
    print("3. 创建告警并关联到航线...")
    alarms_created = create_alarms(waylines, categories, 3)
    print(f"   成功创建 {alarms_created} 条告警记录")
    
    print("\n数据生成完成！")
    print("\n验证数据:")
    print(f"- 航线总数: {Wayline.objects.count()}")
    print(f"- 告警类型总数: {AlarmCategory.objects.count()}")
    print(f"- 告警总数: {Alarm.objects.count()}")
    print(f"- 关联到航线的告警数: {Alarm.objects.filter(wayline__isnull=False).count()}")
    
    # 显示部分关联数据
    print("\n部分关联数据示例:")
    for wayline in Wayline.objects.all()[:3]:
        alarms = Alarm.objects.filter(wayline=wayline)[:2]
        print(f"航线: {wayline.name} (ID: {wayline.wayline_id})")
        for alarm in alarms:
            print(f"  - 告警: {alarm.content} (类型: {alarm.category.name})")

if __name__ == "__main__":
    main()