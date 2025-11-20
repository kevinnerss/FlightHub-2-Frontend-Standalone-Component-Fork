import os
import sys
import subprocess

# 设置工作目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

def run_command(command):
    """运行命令并显示输出"""
    print(f'\n运行命令: {command}')
    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if stdout:
            print(stdout)
        if stderr:
            print(f'错误: {stderr}')
            
        return process.returncode
    except Exception as e:
        print(f'命令执行失败: {str(e)}')
        return 1

def main():
    print('开始初始化系统...')
    
    # 运行数据库迁移
    print('\n=== 运行数据库迁移 ===')
    
    # 先删除现有的迁移文件（排除__init__.py）
    migrations_dir = os.path.join(BASE_DIR, 'telemetry_app', 'migrations')
    if os.path.exists(migrations_dir):
        for file in os.listdir(migrations_dir):
            if file != '__init__.py' and file.endswith('.py'):
                try:
                    os.remove(os.path.join(migrations_dir, file))
                    print(f'已删除迁移文件: {file}')
                except Exception as e:
                    print(f'无法删除迁移文件 {file}: {str(e)}')
    
    # 重新生成迁移
    print('生成数据库迁移...')
    if run_command('python manage.py makemigrations telemetry_app') != 0:
        print('生成迁移失败，退出')
        sys.exit(1)
    
    # 运行迁移
    print('执行数据库迁移...')
    if run_command('python manage.py migrate') != 0:
        print('执行迁移失败，退出')
        sys.exit(1)
    
    # 初始化admin用户
    print('\n=== 初始化Admin用户 ===')
    run_command('python init_admin.py')
    
    print('\n=== 系统初始化完成 ===')
    print('可以使用以下命令启动后端服务:')
    print('python manage.py runserver')
    print('\n登录凭证:')
    print('用户名: admin')
    print('密码: admin123')

if __name__ == '__main__':
    main()