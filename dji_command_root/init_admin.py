import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')
django.setup()

from django.contrib.auth.models import User
from telemetry_app.models import UserProfile
from django.db.utils import OperationalError

def create_admin_user():
    """创建admin用户"""
    try:
        # 检查admin用户是否已存在
        admin_user = User.objects.filter(username='admin').first()
        
        if not admin_user:
            # 创建admin用户
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            
            # 创建用户扩展信息
            UserProfile.objects.create(
                user=admin_user,
                name='系统管理员',
                role='admin'
            )
            print('Admin用户创建成功！')
        else:
            # 检查是否有扩展信息
            if not hasattr(admin_user, 'profile'):
                UserProfile.objects.create(
                    user=admin_user,
                    name='系统管理员',
                    role='admin'
                )
                print('Admin用户扩展信息创建成功！')
            else:
                print('Admin用户已存在')
            
        return admin_user
    except Exception as e:
        print(f'创建admin用户失败: {str(e)}')
        return None

def check_user_model():
    """检查用户模型是否正常工作"""
    try:
        # 尝试获取用户数量
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        print(f'用户模型正常，当前共有 {user_count} 个用户，{profile_count} 个用户扩展信息')
        return True
    except OperationalError as e:
        if 'no such table' in str(e):
            print('用户相关表不存在，请先运行数据库迁移')
        else:
            print(f'数据库操作错误: {str(e)}')
        return False
    except Exception as e:
        print(f'用户模型检查失败: {str(e)}')
        return False

if __name__ == '__main__':
    print('开始初始化admin用户...')
    
    # 先检查用户模型
    if check_user_model():
        # 创建admin用户
        create_admin_user()
    else:
        print('请先运行数据库迁移')
    
    print('初始化完成！')