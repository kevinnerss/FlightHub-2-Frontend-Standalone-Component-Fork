import os
import sys

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

def verify_data():
    """验证数据库中的测试数据"""
    print("开始验证数据库中的测试数据...")
    
    # 验证用户配置文件数据
    print("\n=== 用户配置文件(UserProfile) ===")
    user_profiles = UserProfile.objects.all()
    print(f"总记录数: {user_profiles.count()}")
    print("前2条记录:")
    for profile in user_profiles[:2]:
        print(f"  ID: {profile.id}, 用户名: {profile.user.username}, 真实姓名: {profile.name}, 角色: {profile.role}")
    
    # 验证告警类型数据
    print("\n=== 告警类型(AlarmCategory) ===")
    categories = AlarmCategory.objects.all()
    print(f"总记录数: {categories.count()}")
    print("所有告警类型:")
    for category in categories:
        parent_name = category.parent.name if category.parent else "无"
        print(f"  ID: {category.id}, 名称: {category.name}, 代码: {category.code}, 父类型: {parent_name}")
    
    # 验证航线数据
    print("\n=== 航线(Wayline) ===")
    waylines = Wayline.objects.all()
    print(f"总记录数: {waylines.count()}")
    print("所有航线:")
    for wayline in waylines:
        print(f"  ID: {wayline.id}, 航线ID: {wayline.wayline_id}, 名称: {wayline.name}, 状态: {wayline.status}")
        print(f"    长度: {wayline.length}米, 预计时间: {wayline.estimated_duration}秒")
        print(f"    航点数: {len(wayline.waypoints) if wayline.waypoints else 0}")
    
    # 验证告警数据
    print("\n=== 告警(Alarm) ===")
    alarms = Alarm.objects.all()
    print(f"总记录数: {alarms.count()}")
    print("前5条告警:")
    for alarm in alarms[:5]:
        wayline_name = alarm.wayline.name if alarm.wayline else "无"
        category_name = alarm.category.name if alarm.category else "无"
        print(f"  ID: {alarm.id}, 航线: {wayline_name}, 类型: {category_name}, 状态: {alarm.status}")
        print(f"    位置: ({alarm.latitude}, {alarm.longitude})")
        print(f"    创建时间: {alarm.created_at}")
    
    # 验证关系完整性
    print("\n=== 关系完整性验证 ===")
    # 检查每个告警是否有关联的航线和类型
    for alarm in alarms:
        if not alarm.wayline:
            print(f"警告: 告警ID {alarm.id} 没有关联的航线")
        if not alarm.category:
            print(f"警告: 告警ID {alarm.id} 没有关联的告警类型")
    
    print("\n数据验证完成！")

if __name__ == "__main__":
    verify_data()