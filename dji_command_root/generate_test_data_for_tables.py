import os
import sys
import random
import json
from datetime import datetime, timedelta

# 添加Django项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')

# 导入Django
import django
django.setup()

# 导入模型
from telemetry_app.models import Wayline, AlarmCategory, Alarm, UserProfile
from django.contrib.auth.models import User

def generate_test_data():
    """生成并插入测试数据到各个表中"""
    print("开始生成测试数据...")
    
    # 1. 生成用户和用户配置文件数据
    print("\n正在生成用户数据...")
    users_data = [
        {"username": "admin", "email": "admin@example.com", "password": "admin123", "name": "管理员", "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "password": "user123", "name": "操作员小王", "role": "user"},
        {"username": "user2", "email": "user2@example.com", "password": "user123", "name": "操作员小李", "role": "user"},
    ]
    
    created_users = []
    for user_data in users_data:
        try:
            # 检查用户是否已存在
            user = User.objects.filter(username=user_data['username']).first()
            if not user:
                # 创建新用户
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
                print(f"创建用户: {user_data['username']}")
            
            # 创建或更新用户配置文件
            profile, created = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'name': user_data['name'],
                    'role': user_data['role']
                }
            )
            if created:
                print(f"创建用户配置文件: {user_data['name']}")
            else:
                print(f"更新用户配置文件: {user_data['name']}")
            
            created_users.append(user)
        except Exception as e:
            print(f"创建用户 {user_data['username']} 时出错: {str(e)}")
    
    # 2. 生成告警类型数据
    print("\n正在生成告警类型数据...")
    alarm_categories_data = [
        {"name": "基础设施", "code": "INFRA", "parent": None},
        {"name": "接触网", "code": "OVERHEAD", "parent": None},
        {"name": "轨道", "code": "TRACK", "parent": None},
        
        # 基础设施子类型
        {"name": "电线杆", "code": "POLE", "parent": "INFRA"},
        {"name": "信号灯", "code": "SIGNAL", "parent": "INFRA"},
        
        # 接触网子类型
        {"name": "断线", "code": "BROKEN_LINE", "parent": "OVERHEAD"},
        {"name": "异物", "code": "FOREIGN_OBJECT", "parent": "OVERHEAD"},
        
        # 轨道子类型
        {"name": "障碍物", "code": "OBSTACLE", "parent": "TRACK"},
        {"name": "损坏", "code": "DAMAGE", "parent": "TRACK"},
    ]
    
    category_map = {}
    for category_data in alarm_categories_data:
        try:
            # 查找父类别
            parent = None
            if category_data['parent']:
                parent = category_map.get(category_data['parent'])
            
            # 创建或更新告警类型
            category, created = AlarmCategory.objects.update_or_create(
                code=category_data['code'],
                defaults={
                    'name': category_data['name'],
                    'parent': parent
                }
            )
            
            # 保存到映射中
            category_map[category.code] = category
            
            if created:
                print(f"创建告警类型: {category.name} ({category.code})")
            else:
                print(f"更新告警类型: {category.name} ({category.code})")
        except Exception as e:
            print(f"创建告警类型 {category_data['name']} 时出错: {str(e)}")
    
    # 3. 生成航线数据
    print("\n正在生成航线数据...")
    waylines_data = [
        {
            "wayline_id": "WL001",
            "name": "线路1巡检航线",
            "description": "用于电力线路1的例行巡检",
            "waypoints": [
                {"latitude": 31.2304, "longitude": 121.4737, "altitude": 50, "speed": 10},
                {"latitude": 31.2354, "longitude": 121.4787, "altitude": 50, "speed": 10},
                {"latitude": 31.2404, "longitude": 121.4837, "altitude": 50, "speed": 10},
            ],
            "length": 1500.5,
            "estimated_duration": 180,
            "status": "ACTIVE",
            "created_by": "admin"
        },
        {
            "wayline_id": "WL002",
            "name": "线路2巡检航线",
            "description": "用于电力线路2的例行巡检",
            "waypoints": [
                {"latitude": 31.2454, "longitude": 121.4887, "altitude": 60, "speed": 10},
                {"latitude": 31.2504, "longitude": 121.4937, "altitude": 60, "speed": 10},
                {"latitude": 31.2554, "longitude": 121.4987, "altitude": 60, "speed": 10},
            ],
            "length": 2000.7,
            "estimated_duration": 240,
            "status": "ACTIVE",
            "created_by": "admin"
        },
        {
            "wayline_id": "WL003",
            "name": "备用航线",
            "description": "紧急情况下使用的备用巡检航线",
            "waypoints": [
                {"latitude": 31.2604, "longitude": 121.5037, "altitude": 55, "speed": 10},
                {"latitude": 31.2654, "longitude": 121.5087, "altitude": 55, "speed": 10},
            ],
            "length": 1200.3,
            "estimated_duration": 144,
            "status": "DRAFT",
            "created_by": "user1"
        },
    ]
    
    created_waylines = []
    for wayline_data in waylines_data:
        try:
            # 创建或更新航线
            wayline, created = Wayline.objects.update_or_create(
                wayline_id=wayline_data['wayline_id'],
                defaults={
                    'name': wayline_data['name'],
                    'description': wayline_data['description'],
                    'waypoints': wayline_data['waypoints'],
                    'length': wayline_data['length'],
                    'estimated_duration': wayline_data['estimated_duration'],
                    'status': wayline_data['status'],
                    'created_by': wayline_data['created_by']
                }
            )
            
            if created:
                print(f"创建航线: {wayline.name} ({wayline.wayline_id})")
            else:
                print(f"更新航线: {wayline.name} ({wayline.wayline_id})")
            
            created_waylines.append(wayline)
        except Exception as e:
            print(f"创建航线 {wayline_data['name']} 时出错: {str(e)}")
    
    # 4. 生成告警数据
    print("\n正在生成告警数据...")
    
    # 告警状态选项
    status_choices = ['PENDING', 'PROCESSING', 'COMPLETED', 'IGNORED']
    
    # 处理人员选项
    handlers = ['admin', 'user1', 'user2', None]
    
    # 为每个航线生成多个告警
    for wayline in created_waylines:
        num_alarms = random.randint(2, 5)  # 每个航线生成2-5个告警
        
        for i in range(num_alarms):
            try:
                # 随机选择一个告警类型
                category_keys = list(category_map.keys())
                # 确保选择的是叶子节点类型（有父类的）
                leaf_categories = [key for key in category_keys if category_map[key].parent is not None]
                category_key = random.choice(leaf_categories)
                category = category_map[category_key]
                
                # 随机生成位置信息（在航线附近）
                base_lat = wayline.waypoints[0]['latitude']
                base_lng = wayline.waypoints[0]['longitude']
                
                # 生成随机偏移量（约100米范围内）
                lat_offset = random.uniform(-0.001, 0.001)
                lng_offset = random.uniform(-0.001, 0.001)
                
                # 根据告警类型生成特定数据
                specific_data = {}
                if category.code in ['POLE', 'BROKEN_LINE', 'FOREIGN_OBJECT']:
                    specific_data = {"pole_number": f"T{random.randint(1000, 9999)}", "voltage": "25kV"}
                elif category.code in ['OBSTACLE', 'DAMAGE']:
                    specific_data = {"track_id": f"G{random.randint(1, 20)}-S{random.randint(1, 10)}", "mileage": f"K{random.randint(1, 200)}+{random.randint(0, 999)}"}
                elif category.code == 'SIGNAL':
                    specific_data = {"signal_id": f"SG{random.randint(100, 999)}", "signal_type": random.choice(["红灯", "绿灯", "黄灯"])}
                
                # 创建告警
                alarm = Alarm.objects.create(
                    wayline=wayline,
                    category=category,
                    latitude=round(base_lat + lat_offset, 6),
                    longitude=round(base_lng + lng_offset, 6),
                    content=f"{category.name}告警 - {wayline.name}附近发现异常",
                    image_url=f"https://example.com/alarm_images/alarm_{wayline.wayline_id}_{i+1}.jpg" if random.random() > 0.3 else None,
                    specific_data=specific_data,
                    status=random.choice(status_choices),
                    handler=random.choice(handlers)
                )
                
                # 随机修改创建时间（过去7天内）
                days_ago = random.randint(0, 7)
                alarm.created_at = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                alarm.save()
                
                print(f"创建告警: {alarm.content} (ID: {alarm.id})")
            except Exception as e:
                print(f"创建告警时出错: {str(e)}")
    
    print("\n测试数据生成完成！")
    
    # 统计插入的数据
    print(f"\n插入数据统计:")
    print(f"- 用户配置文件: {UserProfile.objects.count()}条")
    print(f"- 告警类型: {AlarmCategory.objects.count()}条")
    print(f"- 航线: {Wayline.objects.count()}条")
    print(f"- 告警: {Alarm.objects.count()}条")

if __name__ == "__main__":
    generate_test_data()